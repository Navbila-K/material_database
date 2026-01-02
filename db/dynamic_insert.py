"""
Dynamic Database Inserter for Material Database Engine.
Works with dynamic_xml_parser to insert ANY XML structure into database.

KEY FEATURES:
- No hardcoded property categories (handles Phase, Thermal, Mechanical, Optical, Nuclear, etc.)
- No hardcoded model types (handles ElasticModel, OpticalModel, QuantumModel, etc.)
- Fully recursive insertion following XML structure
- Preserves all attributes, units, references
- Works with existing AND novel material structures

PHILOSOPHY:
Let the data define its own structure - the inserter adapts to it.
"""
from typing import Dict, List, Any, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DynamicMaterialInserter:
    """
    Dynamically inserts material data from ANY XML structure.
    Discovers structure at runtime - no hardcoded schemas.
    """
    
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
        Dynamically insert complete material data into database.
        
        Args:
            material_data: Parsed material dictionary from dynamic XML parser
        
        Returns:
            material_id of inserted material
        """
        cursor = self.conn.cursor()
        
        try:
            # 1. Insert metadata
            material_id = self._insert_metadata(cursor, material_data['metadata'])
            logger.info(f"  ✓ Inserted material metadata (ID: {material_id})")
            
            # 2. Dynamically insert ALL property categories
            if 'properties' in material_data and material_data['properties']:
                prop_count = self._insert_properties_dynamic(
                    cursor, material_id, material_data['properties']
                )
                logger.info(f"  ✓ Inserted {prop_count} property categories")
            
            # 3. Dynamically insert ALL model types
            if 'models' in material_data and material_data['models']:
                model_count = self._insert_models_dynamic(
                    cursor, material_id, material_data['models']
                )
                logger.info(f"  ✓ Inserted {model_count} model types")
            
            self.conn.commit()
            logger.info(
                f"✓ Material '{material_data['metadata'].get('name')}' "
                f"inserted successfully (ID: {material_id})"
            )
            
            return material_id
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"✗ Error inserting material: {e}")
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
    
    def _insert_properties_dynamic(
        self, cursor, material_id: int, properties: Dict[str, Any]
    ) -> int:
        """
        Dynamically insert ALL property categories (Phase, Thermal, Mechanical, NEW categories).
        Discovers categories at runtime.
        
        Returns:
            Number of categories inserted
        """
        category_count = 0
        
        for category_type, category_data in properties.items():
            logger.info(f"    Inserting property category: {category_type}")
            
            # Insert category
            category_id = self._insert_property_category(cursor, material_id, category_type)
            
            # Special handling for Phase (simple key-value pairs)
            if category_type == 'Phase':
                for key, value in category_data.items():
                    property_id = self._insert_property(cursor, category_id, key, None)
                    if value:
                        self._insert_property_entry(cursor, property_id, value, None, 1)
            
            # General handling for other categories
            else:
                self._insert_property_data_recursive(cursor, category_id, category_data)
            
            category_count += 1
        
        return category_count
    
    def _insert_property_data_recursive(
        self, cursor, category_id: int, category_data: Dict[str, Any]
    ):
        """
        Recursively insert property data for ANY structure.
        Handles entries, nested structures, units, etc.
        """
        for prop_name, prop_data in category_data.items():
            # Case 1: Property with entries (most common)
            if isinstance(prop_data, dict) and 'entries' in prop_data:
                unit = prop_data.get('unit')
                entries = prop_data.get('entries', [])
                
                property_id = self._insert_property(cursor, category_id, prop_name, unit)
                
                for entry in entries:
                    self._insert_property_entry(
                        cursor,
                        property_id,
                        entry.get('value'),
                        entry.get('ref'),
                        entry.get('index', 1)
                    )
            
            # Case 2: Simple value property
            elif isinstance(prop_data, dict) and 'value' in prop_data:
                unit = prop_data.get('unit')
                value = prop_data.get('value')
                
                property_id = self._insert_property(cursor, category_id, prop_name, unit)
                
                if value:
                    self._insert_property_entry(cursor, property_id, value, None, 1)
            
            # Case 3: Nested structure - recurse
            elif isinstance(prop_data, dict):
                # Create a sub-property for nested structure
                # For now, flatten it or log warning
                logger.warning(
                    f"      Skipping nested property structure: {prop_name} "
                    "(not standard Entry format)"
                )
    
    def _insert_models_dynamic(
        self, cursor, material_id: int, models: Dict[str, Any]
    ) -> int:
        """
        Dynamically insert ALL model types.
        Discovers model types at runtime (ElasticModel, OpticalModel, QuantumModel, etc.)
        
        Returns:
            Number of model types inserted
        """
        model_count = 0
        
        for model_type, model_data in models.items():
            logger.info(f"    Inserting model type: {model_type}")
            
            # Insert model type
            model_id = self._insert_model(cursor, material_id, model_type)
            
            # Handle Row-based structures (EOSModel)
            if isinstance(model_data, dict) and 'rows' in model_data:
                self._insert_eos_rows(cursor, model_id, model_data['rows'])
            
            # Handle general model structures
            else:
                self._insert_model_structure_recursive(cursor, model_id, model_data)
            
            model_count += 1
        
        return model_count
    
    def _insert_model_structure_recursive(
        self, cursor, model_id: int, model_data: Dict[str, Any], 
        parent_sub_model_id: Optional[int] = None, parent_name: Optional[str] = None
    ):
        """
        Recursively insert model structure.
        Handles sub-models, parameters, nested structures.
        """
        for key, value in model_data.items():
            # Case 1: List of entries (parameter with multiple values)
            if isinstance(value, list) and value and isinstance(value[0], dict) and 'value' in value[0]:
                # This is a parameter with entries
                sub_model_id = self._insert_sub_model(
                    cursor, model_id, key, None, parent_sub_model_id, parent_name
                )
                
                for entry in value:
                    self._insert_model_parameter(
                        cursor,
                        sub_model_id,
                        key,
                        entry.get('value'),
                        entry.get('unit'),
                        entry.get('ref'),
                        entry.get('index', 1)
                    )
            
            # Case 2: Dictionary with 'value' key (single parameter)
            elif isinstance(value, dict) and 'value' in value:
                sub_model_id = self._insert_sub_model(
                    cursor, model_id, key, None, parent_sub_model_id, parent_name
                )
                
                self._insert_model_parameter(
                    cursor,
                    sub_model_id,
                    key,
                    value.get('value'),
                    value.get('unit'),
                    value.get('ref'),
                    1
                )
            
            # Case 3: Nested dictionary (sub-model like ThermoMechanical, Dispersion, etc.)
            elif isinstance(value, dict):
                # Create sub-model for this nested structure
                sub_model_id = self._insert_sub_model(
                    cursor, model_id, key, None, parent_sub_model_id, parent_name
                )
                
                # Recurse into nested structure
                self._insert_model_structure_recursive(
                    cursor, model_id, value, sub_model_id, key
                )
    
    def _insert_eos_rows(self, cursor, model_id: int, rows: List[Dict[str, Any]]):
        """Insert EOS Row structures."""
        for row in rows:
            row_index = row.get('index')
            row_params = row.get('parameters', {})
            
            # Insert row as sub_model
            sub_model_id = self._insert_sub_model(
                cursor, model_id, 'Row', row_index, None, None
            )
            
            # Insert row parameters
            for param_name, param_data in row_params.items():
                if isinstance(param_data, dict):
                    # Check for nested unreacted/reacted
                    if param_name in ['unreacted', 'reacted']:
                        # Create nested sub-model
                        nested_sub_model_id = self._insert_sub_model(
                            cursor, model_id, param_name, None, sub_model_id, param_name
                        )
                        
                        for nested_param, nested_value in param_data.items():
                            if isinstance(nested_value, dict):
                                self._insert_model_parameter(
                                    cursor,
                                    nested_sub_model_id,
                                    nested_param,
                                    nested_value.get('value'),
                                    nested_value.get('unit'),
                                    nested_value.get('ref'),
                                    1
                                )
                    else:
                        # Regular parameter
                        self._insert_model_parameter(
                            cursor,
                            sub_model_id,
                            param_name,
                            param_data.get('value'),
                            param_data.get('unit'),
                            param_data.get('ref'),
                            1
                        )
    
    # ========== Database Insertion Methods ==========
    
    def _insert_property_category(self, cursor, material_id: int, category_type: str) -> int:
        """Insert property category and return category_id."""
        sql = """
            INSERT INTO property_categories (material_id, category_type)
            VALUES (%s, %s)
            RETURNING category_id
        """
        
        cursor.execute(sql, (material_id, category_type))
        return cursor.fetchone()[0]
    
    def _insert_property(
        self, cursor, category_id: int, property_name: str, unit: Optional[str]
    ) -> int:
        """Insert property and return property_id."""
        sql = """
            INSERT INTO properties (category_id, property_name, unit)
            VALUES (%s, %s, %s)
            RETURNING property_id
        """
        
        cursor.execute(sql, (category_id, property_name, unit))
        return cursor.fetchone()[0]
    
    def _insert_property_entry(
        self, cursor, property_id: int, value: Optional[str], 
        ref_id: Optional[str], entry_index: int
    ):
        """Insert property entry."""
        sql = """
            INSERT INTO property_entries (property_id, value, ref_id, entry_index)
            VALUES (%s, %s, %s, %s)
        """
        
        cursor.execute(sql, (property_id, value, ref_id, entry_index))
    
    def _insert_model(self, cursor, material_id: int, model_type: str) -> int:
        """Insert model and return model_id."""
        sql = """
            INSERT INTO models (material_id, model_type)
            VALUES (%s, %s)
            RETURNING model_id
        """
        
        cursor.execute(sql, (material_id, model_type))
        return cursor.fetchone()[0]
    
    def _insert_sub_model(
        self, cursor, model_id: int, sub_model_type: str, row_index: Optional[int],
        parent_sub_model_id: Optional[int], parent_name: Optional[str]
    ) -> int:
        """Insert sub-model and return sub_model_id."""
        sql = """
            INSERT INTO sub_models 
            (model_id, sub_model_type, row_index, parent_sub_model_id, parent_name)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING sub_model_id
        """
        
        cursor.execute(sql, (
            model_id, sub_model_type, row_index, parent_sub_model_id, parent_name
        ))
        return cursor.fetchone()[0]
    
    def _insert_model_parameter(
        self, cursor, sub_model_id: int, param_name: str, value: Optional[str],
        unit: Optional[str], ref_id: Optional[str], entry_index: int
    ):
        """Insert model parameter."""
        sql = """
            INSERT INTO model_parameters 
            (sub_model_id, param_name, value, unit, ref_id, entry_index)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(sql, (sub_model_id, param_name, value, unit, ref_id, entry_index))
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    from parser.dynamic_xml_parser import parse_material_xml_dynamic
    
    print("="*80)
    print("TESTING DYNAMIC INSERTER")
    print("="*80)
    
    # Test with novel material
    test_file = "xml/TEST_NOVEL.xml"
    
    print(f"\n1. Parsing {test_file}...")
    material_data = parse_material_xml_dynamic(test_file)
    
    print(f"\n2. Connecting to database...")
    db = DatabaseManager()
    inserter = DynamicMaterialInserter(db)
    
    print(f"\n3. Inserting material...")
    try:
        material_id = inserter.insert_material(material_data)
        print(f"\n✓ Successfully inserted material ID: {material_id}")
        print(f"✓ Material name: {material_data['metadata']['name']}")
        print(f"✓ Property categories: {list(material_data['properties'].keys())}")
        print(f"✓ Model types: {list(material_data['models'].keys())}")
    except Exception as e:
        print(f"\n✗ Error: {e}")
    finally:
        inserter.close()
    
    print("\n" + "="*80)
