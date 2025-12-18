"""
Override Manager for Material Database Engine.
Handles query-time overrides and reference selection.

CORE PRINCIPLE: Never modify original database values.
All overrides are applied at query/export time only.
"""
from typing import Dict, List, Any, Optional
import copy


class OverrideManager:
    """
    Manages material data overrides without modifying database.
    
    Supports:
    - Preferred reference selection
    - User-defined value overrides
    - Query-time application
    """
    
    def __init__(self):
        """Initialize override manager."""
        self.overrides = {
            'reference_preferences': {},  # {material_id: {property_path: preferred_ref}}
            'value_overrides': {}  # {material_id: {property_path: override_value}}
        }
    
    def set_preferred_reference(self, material_id: int, property_path: str, 
                                preferred_ref: str):
        """
        Set preferred reference for a property.
        
        Args:
            material_id: Material ID
            property_path: Path to property (e.g., 'properties.Thermal.Density')
            preferred_ref: Preferred reference ID
        """
        if material_id not in self.overrides['reference_preferences']:
            self.overrides['reference_preferences'][material_id] = {}
        
        self.overrides['reference_preferences'][material_id][property_path] = preferred_ref
    
    def set_value_override(self, material_id: int, property_path: str, 
                          override_value: str, unit: Optional[str] = None):
        """
        Set user-defined value override for a property.
        
        Args:
            material_id: Material ID
            property_path: Path to property
            override_value: Override value
            unit: Unit (optional)
        """
        if material_id not in self.overrides['value_overrides']:
            self.overrides['value_overrides'][material_id] = {}
        
        self.overrides['value_overrides'][material_id][property_path] = {
            'value': override_value,
            'unit': unit
        }
    
    def apply_overrides(self, material_id: int, material_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply all overrides to material data.
        Returns a modified copy without changing original.
        
        Args:
            material_id: Material ID
            material_data: Original material data
        
        Returns:
            Modified copy of material data with overrides applied
        """
        # Create deep copy to avoid modifying original
        modified_data = copy.deepcopy(material_data)
        
        # Apply reference preferences
        if material_id in self.overrides['reference_preferences']:
            modified_data = self._apply_reference_preferences(
                material_id, modified_data
            )
        
        # Apply value overrides
        if material_id in self.overrides['value_overrides']:
            modified_data = self._apply_value_overrides(
                material_id, modified_data
            )
        
        return modified_data
    
    def _apply_reference_preferences(self, material_id: int, 
                                     material_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply reference preferences to material data.
        Selects preferred reference when multiple entries exist.
        """
        prefs = self.overrides['reference_preferences'][material_id]
        
        for property_path, preferred_ref in prefs.items():
            # Parse path (e.g., 'properties.Thermal.Density')
            parts = property_path.split('.')
            
            if parts[0] == 'properties' and len(parts) >= 3:
                category = parts[1]
                prop_name = parts[2]
                
                if category in material_data['properties']:
                    if prop_name in material_data['properties'][category]:
                        prop_data = material_data['properties'][category][prop_name]
                        entries = prop_data.get('entries', [])
                        
                        # Find entry with preferred reference
                        selected_entry = None
                        for entry in entries:
                            if entry.get('ref') == preferred_ref:
                                selected_entry = entry
                                break
                        
                        # Replace entries with selected one
                        if selected_entry:
                            prop_data['entries'] = [selected_entry]
            
            elif parts[0] == 'models' and len(parts) >= 4:
                # Handle model paths: models.ElasticModel.ThermoMechanical.Density
                model_type = parts[1]
                sub_model_type = parts[2]
                param_name = parts[3]
                
                if model_type in material_data['models']:
                    model_data = material_data['models'][model_type]
                    
                    # Check if sub_model exists
                    if sub_model_type in model_data:
                        sub_model = model_data[sub_model_type]
                        
                        if param_name in sub_model:
                            param_data = sub_model[param_name]
                            
                            # Handle both single values and entry lists
                            if isinstance(param_data, dict) and 'entries' in param_data:
                                entries = param_data['entries']
                                
                                # Find entry with preferred reference
                                selected_entry = None
                                for entry in entries:
                                    if entry.get('ref') == preferred_ref:
                                        selected_entry = entry
                                        break
                                
                                # Replace entries with selected one
                                if selected_entry:
                                    param_data['entries'] = [selected_entry]
        
        return material_data
    
    def _apply_value_overrides(self, material_id: int, 
                               material_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply user-defined value overrides to material data.
        Replaces all entries with override value.
        """
        overrides = self.overrides['value_overrides'][material_id]
        
        for property_path, override_data in overrides.items():
            # Parse path
            parts = property_path.split('.')
            
            if parts[0] == 'properties' and len(parts) >= 3:
                category = parts[1]
                prop_name = parts[2]
                
                if category in material_data['properties']:
                    if prop_name in material_data['properties'][category]:
                        prop_data = material_data['properties'][category][prop_name]
                        
                        # Create override entry
                        override_entry = {
                            'value': override_data['value'],
                            'unit': override_data.get('unit') or prop_data.get('unit'),
                            'ref': 'USER_OVERRIDE',
                            'index': 1
                        }
                        
                        # Replace all entries with override
                        prop_data['entries'] = [override_entry]
            
            elif parts[0] == 'models' and len(parts) >= 3:
                # Handle model paths:
                # 3-part: models.ElastoPlastic.ShearModulus (direct parameter)
                # 4-part: models.ElasticModel.ThermoMechanical.Density (nested sub-model)
                model_type = parts[1]
                
                if model_type in material_data['models']:
                    model_data = material_data['models'][model_type]
                    
                    if len(parts) == 3:
                        # Direct model parameter (e.g., ElastoPlastic.ShearModulus)
                        param_name = parts[2]
                        
                        if param_name in model_data:
                            param_data = model_data[param_name]
                            
                            # Create override entry
                            override_entry = {
                                'value': override_data['value'],
                                'unit': override_data.get('unit') or (
                                    param_data[0].get('unit') if isinstance(param_data, list) and len(param_data) > 0
                                    else param_data.get('unit') if isinstance(param_data, dict)
                                    else None
                                ),
                                'ref': 'USER_OVERRIDE',
                                'index': 1
                            }
                            
                            # Replace with override (handle array format for ElastoPlastic)
                            if isinstance(param_data, list):
                                model_data[param_name] = [override_entry]
                            elif isinstance(param_data, dict) and 'entries' in param_data:
                                param_data['entries'] = [override_entry]
                            else:
                                model_data[param_name] = override_entry
                    
                    elif len(parts) >= 4:
                        # Nested sub-model parameter (e.g., ElasticModel.ThermoMechanical.Density)
                        sub_model_type = parts[2]
                        param_name = parts[3]
                        
                        if sub_model_type in model_data:
                            sub_model = model_data[sub_model_type]
                            
                            if param_name in sub_model:
                                param_data = sub_model[param_name]
                                
                                # Get unit from existing data
                                unit = override_data.get('unit')
                                if not unit:
                                    if isinstance(param_data, list) and len(param_data) > 0:
                                        unit = param_data[0].get('unit')
                                    elif isinstance(param_data, dict):
                                        unit = param_data.get('unit')
                                
                                # Create override entry
                                override_entry = {
                                    'value': override_data['value'],
                                    'unit': unit,
                                    'ref': 'USER_OVERRIDE',
                                    'index': 1
                                }
                                
                                # Replace with override (handle different data structures)
                                if isinstance(param_data, list):
                                    # Array format (e.g., ThermoMechanical parameters)
                                    sub_model[param_name] = [override_entry]
                                elif isinstance(param_data, dict) and 'entries' in param_data:
                                    # Entries format
                                    param_data['entries'] = [override_entry]
                                else:
                                    # Single value format
                                    sub_model[param_name] = override_entry

        
        return material_data
    
    def get_single_value(self, material_data: Dict[str, Any], 
                        property_path: str) -> Optional[Dict[str, Any]]:
        """
        Get a single value for a property, applying selection logic.
        
        Selection priority:
        1. User override
        2. Preferred reference
        3. First entry
        
        Args:
            material_data: Material data (with overrides already applied)
            property_path: Path to property
        
        Returns:
            Single entry dictionary or None
        """
        parts = property_path.split('.')
        
        if parts[0] == 'properties' and len(parts) >= 3:
            category = parts[1]
            prop_name = parts[2]
            
            if category in material_data['properties']:
                if prop_name in material_data['properties'][category]:
                    prop_data = material_data['properties'][category][prop_name]
                    entries = prop_data.get('entries', [])
                    
                    if entries:
                        # Return first entry (overrides already applied)
                        return entries[0]
        
        elif parts[0] == 'models' and len(parts) >= 4:
            # Handle model parameters
            model_type = parts[1]
            sub_model_type = parts[2]
            param_name = parts[3]
            
            if model_type in material_data['models']:
                model_data = material_data['models'][model_type]
                
                if sub_model_type in model_data:
                    sub_model = model_data[sub_model_type]
                    
                    if param_name in sub_model:
                        param_data = sub_model[param_name]
                        
                        # Handle entry lists
                        if isinstance(param_data, dict) and 'entries' in param_data:
                            entries = param_data['entries']
                            if entries:
                                return entries[0]
                        else:
                            # Return single value
                            return param_data
        
        return None
    
    def clear_overrides(self, material_id: Optional[int] = None):
        """
        Clear overrides for a specific material or all materials.
        
        Args:
            material_id: Material ID to clear, or None for all
        """
        if material_id is None:
            # Clear all
            self.overrides = {
                'reference_preferences': {},
                'value_overrides': {}
            }
        else:
            # Clear specific material
            if material_id in self.overrides['reference_preferences']:
                del self.overrides['reference_preferences'][material_id]
            if material_id in self.overrides['value_overrides']:
                del self.overrides['value_overrides'][material_id]
    
    def list_overrides(self, material_id: int) -> Dict[str, Any]:
        """
        List all overrides for a material.
        
        Args:
            material_id: Material ID
        
        Returns:
            Dictionary with reference preferences and value overrides
        """
        return {
            'reference_preferences': self.overrides['reference_preferences'].get(material_id, {}),
            'value_overrides': self.overrides['value_overrides'].get(material_id, {})
        }
    
    def has_overrides(self, material_id: int) -> bool:
        """
        Check if material has any overrides.
        
        Args:
            material_id: Material ID
        
        Returns:
            True if material has overrides
        """
        has_ref_prefs = material_id in self.overrides['reference_preferences'] and \
                       len(self.overrides['reference_preferences'][material_id]) > 0
        has_value_overrides = material_id in self.overrides['value_overrides'] and \
                             len(self.overrides['value_overrides'][material_id]) > 0
        return has_ref_prefs or has_value_overrides


def create_override_manager() -> OverrideManager:
    """Factory function to create OverrideManager instance."""
    return OverrideManager()


if __name__ == "__main__":
    # Test override manager
    import json
    
    # Sample material data
    sample_data = {
        'metadata': {'name': 'TestMaterial'},
        'properties': {
            'Thermal': {
                'Density': {
                    'unit': 'kg/m^3',
                    'entries': [
                        {'value': '8940', 'ref': '107', 'index': 1},
                        {'value': '8930', 'ref': '109', 'index': 2},
                        {'value': '8960', 'ref': '121', 'index': 3}
                    ]
                }
            }
        },
        'models': {}
    }
    
    manager = OverrideManager()
    
    print("=== ORIGINAL DATA ===")
    print(json.dumps(sample_data['properties']['Thermal']['Density']['entries'], indent=2))
    
    # Test reference preference
    print("\n=== APPLYING REFERENCE PREFERENCE (ref=109) ===")
    manager.set_preferred_reference(1, 'properties.Thermal.Density', '109')
    modified = manager.apply_overrides(1, sample_data)
    print(json.dumps(modified['properties']['Thermal']['Density']['entries'], indent=2))
    
    # Test value override
    print("\n=== APPLYING VALUE OVERRIDE ===")
    manager.clear_overrides(1)
    manager.set_value_override(1, 'properties.Thermal.Density', '9000', 'kg/m^3')
    modified = manager.apply_overrides(1, sample_data)
    print(json.dumps(modified['properties']['Thermal']['Density']['entries'], indent=2))
    
    print("\n✓ Override tests complete")
