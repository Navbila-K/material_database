"""
XML Parser for Material Database Engine.
Parses material XML files into structured Python dictionaries.

CORE PRINCIPLE: Structure is fixed, data is flexible.
This parser preserves:
- Empty tags (stored as None)
- Units and references
- Index attributes
- Exact hierarchy
"""
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional


class MaterialXMLParser:
    """
    Parses material XML files into structured dictionaries.
    Designed to work with ANY material (metal, explosive, etc.) 
    without modification.
    """
    
    def __init__(self, xml_file_path: str):
        """
        Initialize parser with XML file path.
        
        Args:
            xml_file_path: Path to material XML file
        """
        self.xml_file_path = xml_file_path
        self.tree = None
        self.root = None
    
    def parse(self) -> Dict[str, Any]:
        """
        Parse XML file into structured dictionary.
        
        Returns:
            Dictionary containing complete material data structure
        """
        self.tree = ET.parse(self.xml_file_path)
        self.root = self.tree.getroot()
        
        material_data = {
            'metadata': self._parse_metadata(),
            'properties': self._parse_properties(),
            'models': self._parse_models()
        }
        
        return material_data
    
    def _parse_metadata(self) -> Dict[str, str]:
        """
        Parse <Metadata> section.
        
        Returns:
            Dictionary with metadata fields
        """
        metadata_elem = self.root.find('Metadata')
        if metadata_elem is None:
            return {}
        
        metadata = {}
        
        # Parse standard fields
        for field in ['Id', 'Name', 'Author', 'Date']:
            elem = metadata_elem.find(field)
            metadata[field.lower()] = elem.text if elem is not None and elem.text else None
        
        # Parse Version with meaning attribute
        version_elem = metadata_elem.find('Version')
        if version_elem is not None:
            metadata['version'] = version_elem.text if version_elem.text else None
            metadata['version_meaning'] = version_elem.get('meaning', None)
        else:
            metadata['version'] = None
            metadata['version_meaning'] = None
        
        return metadata
    
    def _parse_properties(self) -> Dict[str, Any]:
        """
        Parse <Property> section containing Phase, Thermal, Mechanical.
        
        Returns:
            Dictionary with property categories and their data
        """
        category_elem = self.root.find('Category')
        if category_elem is None:
            return {}
        
        property_elem = category_elem.find('Property')
        if property_elem is None:
            return {}
        
        properties = {}
        
        # Parse Phase
        phase_elem = property_elem.find('Phase')
        if phase_elem is not None:
            properties['Phase'] = self._parse_phase(phase_elem)
        
        # Parse Thermal
        thermal_elem = property_elem.find('Thermal')
        if thermal_elem is not None:
            properties['Thermal'] = self._parse_property_category(thermal_elem)
        
        # Parse Mechanical
        mechanical_elem = property_elem.find('Mechanical')
        if mechanical_elem is not None:
            properties['Mechanical'] = self._parse_property_category(mechanical_elem)
        
        return properties
    
    def _parse_phase(self, phase_elem: ET.Element) -> Dict[str, Any]:
        """Parse Phase information."""
        state_elem = phase_elem.find('State')
        return {
            'State': state_elem.text if state_elem is not None and state_elem.text else None
        }
    
    def _parse_property_category(self, category_elem: ET.Element) -> Dict[str, Any]:
        """
        Parse a property category (Thermal or Mechanical).
        
        Returns:
            Dictionary mapping property names to their entries
        """
        properties = {}
        
        for prop_elem in category_elem:
            prop_name = prop_elem.tag
            unit = prop_elem.get('unit', None)
            entries = self._parse_entries(prop_elem)
            
            properties[prop_name] = {
                'unit': unit,
                'entries': entries
            }
        
        return properties
    
    def _parse_entries(self, parent_elem: ET.Element) -> List[Dict[str, Any]]:
        """
        Parse <Entry> elements within a property.
        
        Returns:
            List of entry dictionaries with value, ref, index
        """
        entries = []
        
        for idx, entry_elem in enumerate(parent_elem.findall('Entry')):
            entry_data = {
                'value': entry_elem.text if entry_elem.text and entry_elem.text.strip() else None,
                'ref': entry_elem.get('ref', None),
                'index': idx + 1  # 1-based indexing
            }
            entries.append(entry_data)
        
        return entries
    
    def _parse_models(self) -> Dict[str, Any]:
        """
        Parse <Model> section containing all model types.
        
        Returns:
            Dictionary with all model data
        """
        category_elem = self.root.find('Category')
        if category_elem is None:
            return {}
        
        model_elem = category_elem.find('Model')
        if model_elem is None:
            return {}
        
        models = {}
        
        # Parse ElasticModel
        elastic_elem = model_elem.find('ElasticModel')
        if elastic_elem is not None:
            models['ElasticModel'] = self._parse_elastic_model(elastic_elem)
        
        # Parse ElastoPlastic
        elastoplastic_elem = model_elem.find('ElastoPlastic')
        if elastoplastic_elem is not None:
            models['ElastoPlastic'] = self._parse_elastoplastic_model(elastoplastic_elem)
        
        # Parse ReactionModel
        reaction_elem = model_elem.find('ReactionModel')
        if reaction_elem is not None:
            models['ReactionModel'] = self._parse_reaction_model(reaction_elem)
        
        # Parse EOSModel
        eos_elem = model_elem.find('EOSModel')
        if eos_elem is not None:
            models['EOSModel'] = self._parse_eos_model(eos_elem)
        
        return models
    
    def _parse_elastic_model(self, elastic_elem: ET.Element) -> Dict[str, Any]:
        """Parse ElasticModel (contains ThermoMechanical)."""
        model_data = {}
        
        thermo_elem = elastic_elem.find('ThermoMechanical')
        if thermo_elem is not None:
            model_data['ThermoMechanical'] = self._parse_thermomechanical(thermo_elem)
        
        return model_data
    
    def _parse_thermomechanical(self, thermo_elem: ET.Element) -> Dict[str, Any]:
        """Parse ThermoMechanical sub-model."""
        parameters = {}
        
        for param_elem in thermo_elem:
            param_name = param_elem.tag
            
            # Check if it contains Entry elements (not just any children)
            entry_elements = param_elem.findall('Entry')
            
            if entry_elements:
                # Parse as list of entries
                unit = param_elem.get('unit', None)
                entries = []
                
                for idx, entry_elem in enumerate(entry_elements):
                    entry_data = {
                        'value': entry_elem.text if entry_elem.text and entry_elem.text.strip() else None,
                        'unit': entry_elem.get('unit', None) or unit,
                        'ref': entry_elem.get('ref', None),
                        'index': idx + 1
                    }
                    entries.append(entry_data)
                
                parameters[param_name] = entries
            elif list(param_elem):  # Has child elements (like SpecificHeatConstants)
                # Parse as nested structure
                param_data = {}
                for child in param_elem:
                    param_data[child.tag] = {
                        'value': child.text if child.text and child.text.strip() else None,
                        'unit': child.get('unit', None),
                        'ref': child.get('ref', None)
                    }
                parameters[param_name] = param_data
            else:
                # Empty or single value element (shouldn't happen in this schema)
                parameters[param_name] = []
        
        return parameters
    
    def _parse_elastoplastic_model(self, elastoplastic_elem: ET.Element) -> Dict[str, Any]:
        """Parse ElastoPlastic model."""
        model_data = {}
        
        for param_elem in elastoplastic_elem:
            param_name = param_elem.tag
            
            # Check if it contains Entry elements first
            entry_elements = param_elem.findall('Entry')
            
            if entry_elements:
                # Parse as list of entries
                unit = param_elem.get('unit', None)
                entries = []
                
                for idx, entry_elem in enumerate(entry_elements):
                    entry_data = {
                        'value': entry_elem.text if entry_elem.text and entry_elem.text.strip() else None,
                        'unit': entry_elem.get('unit', None) or unit,
                        'ref': entry_elem.get('ref', None),
                        'index': idx + 1
                    }
                    entries.append(entry_data)
                
                model_data[param_name] = entries
            elif list(param_elem):
                # Has child elements (like JohnsonCookModelConstants)
                param_data = {}
                for child in param_elem:
                    param_data[child.tag] = {
                        'value': child.text if child.text and child.text.strip() else None,
                        'unit': child.get('unit', None),
                        'ref': child.get('ref', None)
                    }
                model_data[param_name] = param_data
            else:
                # Empty element
                model_data[param_name] = []
        
        return model_data
    
    def _parse_reaction_model(self, reaction_elem: ET.Element) -> Dict[str, Any]:
        """Parse ReactionModel."""
        model_data = {}
        
        # Parse Kind
        kind_elem = reaction_elem.find('Kind')
        model_data['Kind'] = kind_elem.text if kind_elem is not None and kind_elem.text else None
        
        # Parse indexed entries (LnZ, ActivationEnergy, HeatRelease)
        for param_name in ['LnZ', 'ActivationEnergy', 'HeatRelease']:
            param_elem = reaction_elem.find(param_name)
            if param_elem is not None:
                unit = param_elem.get('unit', None)
                entries = []
                
                for entry_elem in param_elem.findall('Entry'):
                    entry_data = {
                        'value': entry_elem.text if entry_elem.text and entry_elem.text.strip() else None,
                        'unit': unit,
                        'index': entry_elem.get('index', None),
                        'ref': entry_elem.get('ref', None)
                    }
                    entries.append(entry_data)
                
                model_data[param_name] = entries
        
        # Parse ReactionModelParameter
        param_elem = reaction_elem.find('ReactionModelParameter')
        if param_elem is not None:
            param_data = {}
            for child in param_elem:
                param_data[child.tag] = {
                    'value': child.text if child.text and child.text.strip() else None,
                    'unit': child.get('unit', None),
                    'ref': child.get('ref', None)
                }
            model_data['ReactionModelParameter'] = param_data
        
        return model_data
    
    def _parse_eos_model(self, eos_elem: ET.Element) -> Dict[str, Any]:
        """Parse EOSModel with Row structures."""
        model_data = {'rows': []}
        
        for row_elem in eos_elem.findall('Row'):
            row_index = row_elem.get('index', None)
            row_data = {
                'index': row_index,
                'parameters': {}
            }
            
            for param_elem in row_elem:
                param_name = param_elem.tag
                
                # Check for nested structures (unreacted/reacted)
                if param_name in ['unreacted', 'reacted']:
                    nested_params = {}
                    for child in param_elem:
                        nested_params[child.tag] = {
                            'value': child.text if child.text and child.text.strip() else None,
                            'unit': child.get('unit', None),
                            'ref': child.get('ref', None)
                        }
                    row_data['parameters'][param_name] = nested_params
                else:
                    # Simple parameter
                    row_data['parameters'][param_name] = {
                        'value': param_elem.text if param_elem.text and param_elem.text.strip() else None,
                        'unit': param_elem.get('unit', None),
                        'ref': param_elem.get('ref', None)
                    }
            
            model_data['rows'].append(row_data)
        
        return model_data


def parse_material_xml(xml_file_path: str) -> Dict[str, Any]:
    """
    Convenience function to parse a material XML file.
    
    Args:
        xml_file_path: Path to material XML file
    
    Returns:
        Dictionary containing complete material data structure
    """
    parser = MaterialXMLParser(xml_file_path)
    return parser.parse()


if __name__ == "__main__":
    # Test parser with Copper.xml
    import sys
    import os
    import json
    
    # Test file
    test_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                             "xml", "Copper.xml")
    
    if os.path.exists(test_file):
        print(f"Parsing {test_file}...")
        data = parse_material_xml(test_file)
        
        print("\n=== METADATA ===")
        print(json.dumps(data['metadata'], indent=2))
        
        print("\n=== PROPERTIES ===")
        print(f"Categories: {list(data['properties'].keys())}")
        
        print("\n=== MODELS ===")
        print(f"Model types: {list(data['models'].keys())}")
        
        print("\n✓ Parse successful!")
    else:
        print(f"✗ Test file not found: {test_file}")
