"""
Database insertion module for Material Database Engine.
Inserts parsed material data into PostgreSQL tables.

CORE PRINCIPLES:
- Preserve NULL values (empty XML tags)
- Store numeric values as TEXT to preserve scientific notation
- Maintain exact hierarchy from XML
- Material-agnostic insertion logic
"""
from typing import Dict, List, Any, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import DatabaseManager


class MaterialInserter:
    """Handles insertion of parsed material data into database."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize inserter with database manager.
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager
        self.conn = db_manager.connect()
    
    def insert_material(self, material_data: Dict[str, Any]) -> int:
        """
        Insert complete material data into database.
        
        Args:
            material_data: Parsed material dictionary from XML parser
        
        Returns:
            material_id of inserted material
        """
        cursor = self.conn.cursor()
        
        try:
            # 1. Insert metadata
            material_id = self._insert_metadata(cursor, material_data['metadata'])
            print(f"  ✓ Inserted material metadata (ID: {material_id})")
            
            # 2. Insert properties
            if 'properties' in material_data:
                self._insert_properties(cursor, material_id, material_data['properties'])
                print(f"  ✓ Inserted properties")
            
            # 3. Insert models
            if 'models' in material_data:
                self._insert_models(cursor, material_id, material_data['models'])
                print(f"  ✓ Inserted models")
            
            self.conn.commit()
            print(f"✓ Material '{material_data['metadata'].get('name')}' inserted successfully")
            
            return material_id
            
        except Exception as e:
            self.conn.rollback()
            print(f"✗ Error inserting material: {e}")
            raise
        finally:
            cursor.close()
    
    def _insert_metadata(self, cursor, metadata: Dict[str, str]) -> int:
        """Insert material metadata and return material_id."""
        sql = """
            INSERT INTO materials (xml_id, name, author, date, version, version_meaning)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING material_id
        """
        
        cursor.execute(sql, (
            metadata.get('id'),
            metadata.get('name'),
            metadata.get('author'),
            metadata.get('date'),
            metadata.get('version'),
            metadata.get('version_meaning')
        ))
        
        material_id = cursor.fetchone()[0]
        return material_id
    
    def _insert_properties(self, cursor, material_id: int, properties: Dict[str, Any]):
        """Insert property categories and their data."""
        
        for category_type, category_data in properties.items():
            if category_type == 'Phase':
                # Phase is special - just store the state
                category_id = self._insert_property_category(cursor, material_id, category_type)
                
                property_id = self._insert_property(cursor, category_id, 'State', None)
                
                state_value = category_data.get('State')
                if state_value:
                    self._insert_property_entry(cursor, property_id, state_value, None, 1)
            else:
                # Thermal, Mechanical
                category_id = self._insert_property_category(cursor, material_id, category_type)
                
                for prop_name, prop_data in category_data.items():
                    unit = prop_data.get('unit')
                    entries = prop_data.get('entries', [])
                    
                    property_id = self._insert_property(cursor, category_id, prop_name, unit)
                    
                    for entry in entries:
                        self._insert_property_entry(
                            cursor,
                            property_id,
                            entry.get('value'),
                            entry.get('ref'),
                            entry.get('index')
                        )
    
    def _insert_property_category(self, cursor, material_id: int, category_type: str) -> int:
        """Insert property category and return category_id."""
        sql = """
            INSERT INTO property_categories (material_id, category_type)
            VALUES (%s, %s)
            RETURNING category_id
        """
        
        cursor.execute(sql, (material_id, category_type))
        return cursor.fetchone()[0]
    
    def _insert_property(self, cursor, category_id: int, property_name: str, unit: Optional[str]) -> int:
        """Insert property and return property_id."""
        sql = """
            INSERT INTO properties (category_id, property_name, unit)
            VALUES (%s, %s, %s)
            RETURNING property_id
        """
        
        cursor.execute(sql, (category_id, property_name, unit))
        return cursor.fetchone()[0]
    
    def _insert_property_entry(self, cursor, property_id: int, value: Optional[str], 
                               ref_id: Optional[str], entry_index: int):
        """Insert property entry."""
        sql = """
            INSERT INTO property_entries (property_id, value, ref_id, entry_index)
            VALUES (%s, %s, %s, %s)
        """
        
        cursor.execute(sql, (property_id, value, ref_id, entry_index))
    
    def _insert_models(self, cursor, material_id: int, models: Dict[str, Any]):
        """Insert all model data."""
        
        for model_type, model_data in models.items():
            model_id = self._insert_model(cursor, material_id, model_type)
            
            if model_type == 'ElasticModel':
                self._insert_elastic_model(cursor, model_id, model_data)
            elif model_type == 'ElastoPlastic':
                self._insert_elastoplastic_model(cursor, model_id, model_data)
            elif model_type == 'ReactionModel':
                self._insert_reaction_model(cursor, model_id, model_data)
            elif model_type == 'EOSModel':
                self._insert_eos_model(cursor, model_id, model_data)
    
    def _insert_model(self, cursor, material_id: int, model_type: str) -> int:
        """Insert model and return model_id."""
        sql = """
            INSERT INTO models (material_id, model_type)
            VALUES (%s, %s)
            RETURNING model_id
        """
        
        cursor.execute(sql, (material_id, model_type))
        return cursor.fetchone()[0]
    
    def _insert_elastic_model(self, cursor, model_id: int, model_data: Dict[str, Any]):
        """Insert ElasticModel data."""
        
        thermo_data = model_data.get('ThermoMechanical', {})
        
        # Create ThermoMechanical sub-model
        sub_model_id = self._insert_sub_model(cursor, model_id, 'ThermoMechanical', None, None, None)
        
        # Insert parameters
        for param_name, param_value in thermo_data.items():
            if isinstance(param_value, list):
                # List of entries
                for entry in param_value:
                    self._insert_model_parameter(
                        cursor,
                        sub_model_id,
                        param_name,
                        entry.get('value'),
                        entry.get('unit'),
                        entry.get('ref'),
                        entry.get('index')
                    )
            elif isinstance(param_value, dict):
                # Complex structure like SpecificHeatConstants
                for sub_param_name, sub_param_data in param_value.items():
                    self._insert_model_parameter(
                        cursor,
                        sub_model_id,
                        f"{param_name}.{sub_param_name}",
                        sub_param_data.get('value'),
                        sub_param_data.get('unit'),
                        sub_param_data.get('ref'),
                        None
                    )
    
    def _insert_elastoplastic_model(self, cursor, model_id: int, model_data: Dict[str, Any]):
        """Insert ElastoPlastic model data."""
        
        for param_name, param_value in model_data.items():
            if 'Constants' in param_name or 'Model' in param_name:
                # Complex structure (e.g., JohnsonCookModelConstants)
                sub_model_id = self._insert_sub_model(cursor, model_id, param_name, None, None, None)
                
                for sub_param_name, sub_param_data in param_value.items():
                    if isinstance(sub_param_data, dict):
                        self._insert_model_parameter(
                            cursor,
                            sub_model_id,
                            sub_param_name,
                            sub_param_data.get('value'),
                            sub_param_data.get('unit'),
                            sub_param_data.get('ref'),
                            None
                        )
            else:
                # Simple entries (ShearModulus, YieldStrength)
                sub_model_id = self._insert_sub_model(cursor, model_id, param_name, None, None, None)
                
                # param_value should be a list
                if isinstance(param_value, list):
                    for entry in param_value:
                        self._insert_model_parameter(
                            cursor,
                            sub_model_id,
                            param_name,
                            entry.get('value'),
                            entry.get('unit'),
                            entry.get('ref'),
                            entry.get('index')
                        )
                elif isinstance(param_value, dict):
                    # Single entry as dict
                    self._insert_model_parameter(
                        cursor,
                        sub_model_id,
                        param_name,
                        param_value.get('value'),
                        param_value.get('unit'),
                        param_value.get('ref'),
                        None
                    )
    
    def _insert_reaction_model(self, cursor, model_id: int, model_data: Dict[str, Any]):
        """Insert ReactionModel data."""
        
        # Create main sub-model
        sub_model_id = self._insert_sub_model(cursor, model_id, 'ReactionModel', None, None, None)
        
        # Insert Kind
        if 'Kind' in model_data:
            self._insert_model_parameter(cursor, sub_model_id, 'Kind', 
                                         model_data['Kind'], None, None, None)
        
        # Insert indexed entries
        for param_name in ['LnZ', 'ActivationEnergy', 'HeatRelease']:
            if param_name in model_data:
                for entry in model_data[param_name]:
                    self._insert_model_parameter(
                        cursor,
                        sub_model_id,
                        param_name,
                        entry.get('value'),
                        entry.get('unit'),
                        entry.get('ref'),
                        entry.get('index')
                    )
        
        # Insert ReactionModelParameter
        if 'ReactionModelParameter' in model_data:
            param_sub_model_id = self._insert_sub_model(
                cursor, model_id, 'ReactionModelParameter', None, None, None
            )
            
            for sub_param_name, sub_param_data in model_data['ReactionModelParameter'].items():
                self._insert_model_parameter(
                    cursor,
                    param_sub_model_id,
                    sub_param_name,
                    sub_param_data.get('value'),
                    sub_param_data.get('unit'),
                    sub_param_data.get('ref'),
                    None
                )
    
    def _insert_eos_model(self, cursor, model_id: int, model_data: Dict[str, Any]):
        """Insert EOSModel data with Row structures."""
        
        rows = model_data.get('rows', [])
        
        for row in rows:
            row_index = row.get('index')
            parameters = row.get('parameters', {})
            
            # Create Row sub-model
            row_sub_model_id = self._insert_sub_model(
                cursor, model_id, 'Row', row_index, None, None
            )
            
            for param_name, param_data in parameters.items():
                if isinstance(param_data, dict) and 'value' in param_data:
                    # Simple parameter
                    self._insert_model_parameter(
                        cursor,
                        row_sub_model_id,
                        param_name,
                        param_data.get('value'),
                        param_data.get('unit'),
                        param_data.get('ref'),
                        None
                    )
                else:
                    # Nested structure (unreacted/reacted)
                    nested_sub_model_id = self._insert_sub_model(
                        cursor, model_id, 'Row', row_index, row_sub_model_id, param_name
                    )
                    
                    for sub_param_name, sub_param_data in param_data.items():
                        self._insert_model_parameter(
                            cursor,
                            nested_sub_model_id,
                            sub_param_name,
                            sub_param_data.get('value'),
                            sub_param_data.get('unit'),
                            sub_param_data.get('ref'),
                            None
                        )
    
    def _insert_sub_model(self, cursor, model_id: int, sub_model_type: str, 
                         row_index: Optional[int], parent_sub_model_id: Optional[int],
                         parent_name: Optional[str]) -> int:
        """Insert sub-model and return sub_model_id."""
        sql = """
            INSERT INTO sub_models (model_id, sub_model_type, row_index, parent_sub_model_id, parent_name)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING sub_model_id
        """
        
        cursor.execute(sql, (model_id, sub_model_type, row_index, parent_sub_model_id, parent_name))
        return cursor.fetchone()[0]
    
    def _insert_model_parameter(self, cursor, sub_model_id: int, param_name: str,
                                value: Optional[str], unit: Optional[str],
                                ref_id: Optional[str], entry_index: Optional[int]):
        """Insert model parameter."""
        sql = """
            INSERT INTO model_parameters (sub_model_id, param_name, value, unit, ref_id, entry_index)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(sql, (sub_model_id, param_name, value, unit, ref_id, entry_index))


def insert_material_from_dict(db_manager: DatabaseManager, material_data: Dict[str, Any]) -> int:
    """
    Convenience function to insert material data.
    
    Args:
        db_manager: DatabaseManager instance
        material_data: Parsed material dictionary
    
    Returns:
        material_id of inserted material
    """
    inserter = MaterialInserter(db_manager)
    return inserter.insert_material(material_data)


if __name__ == "__main__":
    # Test insertion
    from db.database import DatabaseManager
    from parser.xml_parser import parse_material_xml
    import os
    
    db = DatabaseManager()
    db.connect()
    
    # Test with Copper.xml
    test_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                             "xml", "Copper.xml")
    
    if os.path.exists(test_file):
        print(f"Parsing {test_file}...")
        material_data = parse_material_xml(test_file)
        
        print(f"\nInserting material into database...")
        material_id = insert_material_from_dict(db, material_data)
        
        print(f"\n✓ Material inserted with ID: {material_id}")
    else:
        print(f"✗ Test file not found: {test_file}")
    
    db.close()


def insert_references(db_manager: DatabaseManager, references: List[Dict[str, Any]]) -> int:
    """
    Insert references from References.xml into database.
    
    CRITICAL: Inserts ALL reference data - no fields omitted!
    
    Args:
        db_manager: DatabaseManager instance
        references: List of reference dictionaries from references_parser
    
    Returns:
        Number of references inserted
    """
    conn = db_manager.connect()
    cursor = conn.cursor()
    
    inserted_count = 0
    
    try:
        for ref in references:
            # Insert reference (with UPSERT to handle re-imports)
            cursor.execute("""
                INSERT INTO "references" (
                    reference_id, ref_type, author, title, 
                    journal, year, volume, pages
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (reference_id) DO UPDATE SET
                    ref_type = EXCLUDED.ref_type,
                    author = EXCLUDED.author,
                    title = EXCLUDED.title,
                    journal = EXCLUDED.journal,
                    year = EXCLUDED.year,
                    volume = EXCLUDED.volume,
                    pages = EXCLUDED.pages
            """, (
                ref['reference_id'],
                ref['ref_type'],
                ref['author'],
                ref['title'],
                ref['journal'],
                ref['year'],
                ref['volume'],
                ref['pages']
            ))
            
            inserted_count += 1
        
        conn.commit()
        print(f"✓ Inserted/updated {inserted_count} references")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Error inserting references: {e}")
        raise
    finally:
        cursor.close()
    
    return inserted_count
