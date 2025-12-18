"""
Database query module for Material Database Engine.
Retrieves material data from PostgreSQL database.

Returns data in a structure that mirrors the original XML.
"""
from typing import Dict, List, Any, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import DatabaseManager
from overrides.override_manager import OverrideManager
from db.override_storage import OverrideStorage


class MaterialQuerier:
    """Handles querying of material data from database."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize querier with database manager.
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager
        self.conn = db_manager.connect()
        self.override_manager = OverrideManager()
        self.override_storage = OverrideStorage(self.conn)
    
    def get_material_by_name(self, name: str, apply_overrides: bool = True) -> Optional[Dict[str, Any]]:
        """
        Retrieve material by name.
        
        Args:
            name: Material name
            apply_overrides: Whether to apply stored overrides
        
        Returns:
            Material data dictionary or None if not found
        """
        cursor = self.conn.cursor()
        
        sql = "SELECT material_id FROM materials WHERE name = %s"
        cursor.execute(sql, (name,))
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return self.get_material_by_id(result[0], apply_overrides)
        return None
    
    def get_material_by_id(self, material_id: int, apply_overrides: bool = True) -> Dict[str, Any]:
        """
        Retrieve complete material data by ID.
        
        Args:
            material_id: Material ID
            apply_overrides: Whether to apply stored overrides
        
        Returns:
            Material data dictionary
        """
        material_data = {
            'metadata': self._get_metadata(material_id),
            'properties': self._get_properties(material_id),
            'models': self._get_models(material_id)
        }
        
        # Apply overrides if requested
        if apply_overrides:
            # Load stored overrides from database
            stored_overrides = self.override_storage.load_overrides(material_id)
            
            # Apply reference preferences
            for property_path, preferred_ref in stored_overrides['reference_preferences'].items():
                self.override_manager.set_preferred_reference(material_id, property_path, preferred_ref)
            
            # Apply value overrides
            for property_path, override_data in stored_overrides['value_overrides'].items():
                self.override_manager.set_value_override(
                    material_id, property_path, 
                    override_data['value'], 
                    override_data.get('unit')
                )
            
            # Apply all overrides to material data
            material_data = self.override_manager.apply_overrides(material_id, material_data)
        
        return material_data
    
    def list_materials(self) -> List[Dict[str, Any]]:
        """
        Get list of all materials.
        
        Returns:
            List of material summaries
        """
        cursor = self.conn.cursor()
        
        sql = """
            SELECT material_id, xml_id, name, author, date, version, created_at
            FROM materials
            ORDER BY name
        """
        
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        
        materials = []
        for row in results:
            materials.append({
                'material_id': row[0],
                'xml_id': row[1],
                'name': row[2],
                'author': row[3],
                'date': row[4],
                'version': row[5],
                'created_at': row[6]
            })
        
        return materials
    
    def _get_metadata(self, material_id: int) -> Dict[str, Any]:
        """Retrieve material metadata."""
        cursor = self.conn.cursor()
        
        sql = """
            SELECT xml_id, name, author, date, version, version_meaning
            FROM materials
            WHERE material_id = %s
        """
        
        cursor.execute(sql, (material_id,))
        row = cursor.fetchone()
        cursor.close()
        
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'author': row[2],
                'date': row[3],
                'version': row[4],
                'version_meaning': row[5]
            }
        return {}
    
    def _get_properties(self, material_id: int) -> Dict[str, Any]:
        """Retrieve all property data."""
        cursor = self.conn.cursor()
        
        # Get property categories
        sql = """
            SELECT category_id, category_type
            FROM property_categories
            WHERE material_id = %s
        """
        
        cursor.execute(sql, (material_id,))
        categories = cursor.fetchall()
        
        properties = {}
        
        for category_id, category_type in categories:
            if category_type == 'Phase':
                properties['Phase'] = self._get_phase_property(cursor, category_id)
            else:
                properties[category_type] = self._get_category_properties(cursor, category_id)
        
        cursor.close()
        return properties
    
    def _get_phase_property(self, cursor, category_id: int) -> Dict[str, Any]:
        """Get Phase property."""
        sql = """
            SELECT pe.value
            FROM properties p
            JOIN property_entries pe ON p.property_id = pe.property_id
            WHERE p.category_id = %s AND p.property_name = 'State'
        """
        
        cursor.execute(sql, (category_id,))
        result = cursor.fetchone()
        
        return {'State': result[0] if result else None}
    
    def _get_category_properties(self, cursor, category_id: int) -> Dict[str, Any]:
        """Get properties for a category (Thermal, Mechanical)."""
        sql = """
            SELECT property_id, property_name, unit
            FROM properties
            WHERE category_id = %s
        """
        
        cursor.execute(sql, (category_id,))
        props = cursor.fetchall()
        
        category_data = {}
        
        for property_id, property_name, unit in props:
            entries = self._get_property_entries(cursor, property_id)
            category_data[property_name] = {
                'unit': unit,
                'entries': entries
            }
        
        return category_data
    
    def _get_property_entries(self, cursor, property_id: int) -> List[Dict[str, Any]]:
        """Get all entries for a property."""
        sql = """
            SELECT value, ref_id, entry_index
            FROM property_entries
            WHERE property_id = %s
            ORDER BY entry_index
        """
        
        cursor.execute(sql, (property_id,))
        rows = cursor.fetchall()
        
        entries = []
        for value, ref_id, entry_index in rows:
            entries.append({
                'value': value,
                'ref': ref_id,
                'index': entry_index
            })
        
        return entries
    
    def _get_models(self, material_id: int) -> Dict[str, Any]:
        """Retrieve all model data."""
        cursor = self.conn.cursor()
        
        sql = """
            SELECT model_id, model_type
            FROM models
            WHERE material_id = %s
        """
        
        cursor.execute(sql, (material_id,))
        models_data = cursor.fetchall()
        
        models = {}
        
        for model_id, model_type in models_data:
            if model_type == 'ElasticModel':
                models[model_type] = self._get_elastic_model(cursor, model_id)
            elif model_type == 'ElastoPlastic':
                models[model_type] = self._get_elastoplastic_model(cursor, model_id)
            elif model_type == 'ReactionModel':
                models[model_type] = self._get_reaction_model(cursor, model_id)
            elif model_type == 'EOSModel':
                models[model_type] = self._get_eos_model(cursor, model_id)
        
        cursor.close()
        return models
    
    def _get_elastic_model(self, cursor, model_id: int) -> Dict[str, Any]:
        """Get ElasticModel data."""
        # Get ThermoMechanical sub-model
        sql = """
            SELECT sub_model_id
            FROM sub_models
            WHERE model_id = %s AND sub_model_type = 'ThermoMechanical'
        """
        
        cursor.execute(sql, (model_id,))
        result = cursor.fetchone()
        
        if result:
            sub_model_id = result[0]
            thermo_data = self._get_sub_model_parameters(cursor, sub_model_id)
            return {'ThermoMechanical': thermo_data}
        
        return {}
    
    def _get_sub_model_parameters(self, cursor, sub_model_id: int) -> Dict[str, Any]:
        """Get parameters for a sub-model."""
        sql = """
            SELECT param_name, value, unit, ref_id, entry_index
            FROM model_parameters
            WHERE sub_model_id = %s
            ORDER BY param_name, entry_index
        """
        
        cursor.execute(sql, (sub_model_id,))
        rows = cursor.fetchall()
        
        # Group by parameter name
        params_dict = {}
        
        for param_name, value, unit, ref_id, entry_index in rows:
            # Check if it's a nested parameter (e.g., SpecificHeatConstants.c0)
            if '.' in param_name:
                parent_name, child_name = param_name.split('.', 1)
                if parent_name not in params_dict:
                    params_dict[parent_name] = {}
                params_dict[parent_name][child_name] = {
                    'value': value,
                    'unit': unit,
                    'ref': ref_id
                }
            else:
                # Regular parameter
                if param_name not in params_dict:
                    params_dict[param_name] = []
                
                params_dict[param_name].append({
                    'value': value,
                    'unit': unit,
                    'ref': ref_id,
                    'index': entry_index
                })
        
        return params_dict
    
    def _get_elastoplastic_model(self, cursor, model_id: int) -> Dict[str, Any]:
        """Get ElastoPlastic model data."""
        sql = """
            SELECT sub_model_id, sub_model_type
            FROM sub_models
            WHERE model_id = %s
        """
        
        cursor.execute(sql, (model_id,))
        sub_models = cursor.fetchall()
        
        model_data = {}
        
        for sub_model_id, sub_model_type in sub_models:
            if 'Constants' in sub_model_type or 'Model' in sub_model_type:
                # Complex structure
                params = self._get_sub_model_parameters(cursor, sub_model_id)
                # Flatten single-entry lists to dict
                flat_params = {}
                for key, value in params.items():
                    if isinstance(value, list) and len(value) == 1:
                        flat_params[key] = value[0]
                    else:
                        flat_params[key] = value
                model_data[sub_model_type] = flat_params
            else:
                # Simple parameters
                params = self._get_sub_model_parameters(cursor, sub_model_id)
                if sub_model_type in params:
                    model_data[sub_model_type] = params[sub_model_type]
        
        return model_data
    
    def _get_reaction_model(self, cursor, model_id: int) -> Dict[str, Any]:
        """Get ReactionModel data."""
        model_data = {}
        
        # Get main ReactionModel sub-model
        sql = """
            SELECT sub_model_id, sub_model_type
            FROM sub_models
            WHERE model_id = %s
        """
        
        cursor.execute(sql, (model_id,))
        sub_models = cursor.fetchall()
        
        for sub_model_id, sub_model_type in sub_models:
            if sub_model_type == 'ReactionModel':
                # Get Kind parameter
                sql_kind = """
                    SELECT value
                    FROM model_parameters
                    WHERE sub_model_id = %s AND param_name = 'Kind'
                """
                cursor.execute(sql_kind, (sub_model_id,))
                kind_result = cursor.fetchone()
                model_data['Kind'] = kind_result[0] if kind_result else None
                
                # Get indexed parameters
                for param_name in ['LnZ', 'ActivationEnergy', 'HeatRelease']:
                    sql_param = """
                        SELECT value, unit, ref_id, entry_index
                        FROM model_parameters
                        WHERE sub_model_id = %s AND param_name = %s
                        ORDER BY entry_index
                    """
                    cursor.execute(sql_param, (sub_model_id, param_name))
                    entries = []
                    for value, unit, ref_id, entry_index in cursor.fetchall():
                        entries.append({
                            'value': value,
                            'unit': unit,
                            'ref': ref_id,
                            'index': entry_index
                        })
                    if entries:
                        model_data[param_name] = entries
            
            elif sub_model_type == 'ReactionModelParameter':
                params = self._get_sub_model_parameters(cursor, sub_model_id)
                # Flatten to dict
                flat_params = {}
                for key, value in params.items():
                    if isinstance(value, list) and len(value) == 1:
                        flat_params[key] = value[0]
                    else:
                        flat_params[key] = value
                model_data['ReactionModelParameter'] = flat_params
        
        return model_data
    
    def _get_eos_model(self, cursor, model_id: int) -> Dict[str, Any]:
        """Get EOSModel data with Row structures."""
        sql = """
            SELECT sub_model_id, row_index, parent_sub_model_id, parent_name
            FROM sub_models
            WHERE model_id = %s AND sub_model_type = 'Row'
            ORDER BY row_index
        """
        
        cursor.execute(sql, (model_id,))
        rows_data = cursor.fetchall()
        
        # Group by row_index
        rows_dict = {}
        
        for sub_model_id, row_index, parent_sub_model_id, parent_name in rows_data:
            if row_index not in rows_dict:
                rows_dict[row_index] = {
                    'index': str(row_index) if row_index else None,
                    'parameters': {}
                }
            
            if parent_sub_model_id is None:
                # Main row parameters
                params = self._get_sub_model_parameters(cursor, sub_model_id)
                for param_name, param_values in params.items():
                    if isinstance(param_values, list) and len(param_values) == 1:
                        rows_dict[row_index]['parameters'][param_name] = param_values[0]
                    else:
                        rows_dict[row_index]['parameters'][param_name] = param_values
            else:
                # Nested parameters (unreacted/reacted)
                if parent_name:
                    nested_params = self._get_sub_model_parameters(cursor, sub_model_id)
                    flat_nested = {}
                    for key, value in nested_params.items():
                        if isinstance(value, list) and len(value) == 1:
                            flat_nested[key] = value[0]
                        else:
                            flat_nested[key] = value
                    rows_dict[row_index]['parameters'][parent_name] = flat_nested
        
        # Convert to list
        rows_list = [rows_dict[idx] for idx in sorted(rows_dict.keys())]
        
        return {'rows': rows_list}


def get_material(db_manager: DatabaseManager, name: str) -> Optional[Dict[str, Any]]:
    """
    Convenience function to get material by name.
    
    Args:
        db_manager: DatabaseManager instance
        name: Material name
    
    Returns:
        Material data dictionary or None
    """
    querier = MaterialQuerier(db_manager)
    return querier.get_material_by_name(name)


if __name__ == "__main__":
    # Test query
    import json
    from db.database import DatabaseManager
    
    db = DatabaseManager()
    db.connect()
    
    querier = MaterialQuerier(db)
    
    print("=== ALL MATERIALS ===")
    materials = querier.list_materials()
    for mat in materials:
        print(f"  - {mat['name']} (ID: {mat['material_id']})")
    
    if materials:
        print(f"\n=== QUERYING: {materials[0]['name']} ===")
        material_data = querier.get_material_by_id(materials[0]['material_id'])
        
        print("\nMetadata:")
        print(json.dumps(material_data['metadata'], indent=2))
        
        print("\nProperties:")
        print(f"Categories: {list(material_data['properties'].keys())}")
        
        print("\nModels:")
        print(f"Model types: {list(material_data['models'].keys())}")
    
    db.close()
