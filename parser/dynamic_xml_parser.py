"""
Dynamic XML Parser for Material Database Engine.
Automatically discovers and parses ANY XML structure without hardcoded schemas.

KEY FEATURES:
- Discovers property categories dynamically (Phase, Thermal, Mechanical, NEW categories)
- Discovers model types dynamically (ElasticModel, NEW model types)
- Recursively parses nested structures
- Preserves all attributes, units, references
- NO hardcoded property or model names
- Works with existing materials AND new structures

PHILOSOPHY: 
Let the XML define its own structure - the parser adapts to it.
"""
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Union
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DynamicMaterialParser:
    """
    Dynamic parser that discovers XML structure at runtime.
    Can handle ANY material XML schema without modification.
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
        Automatically discovers all structures.
        
        Returns:
            Dictionary containing complete material data structure
        """
        try:
            self.tree = ET.parse(self.xml_file_path)
            self.root = self.tree.getroot()
            
            logger.info(f"Parsing {self.xml_file_path}...")
            
            material_data = {
                'metadata': self._parse_metadata(),
                'properties': self._parse_properties(),
                'models': self._parse_models()
            }
            
            logger.info(f"✓ Successfully parsed material: {material_data['metadata'].get('name', 'Unknown')}")
            logger.info(f"  Property categories: {list(material_data['properties'].keys())}")
            logger.info(f"  Model types: {list(material_data['models'].keys())}")
            
            return material_data
            
        except ET.ParseError as e:
            logger.error(f"✗ XML parsing error: {e}")
            raise
        except Exception as e:
            logger.error(f"✗ Unexpected error: {e}")
            raise
    
    def _parse_metadata(self) -> Dict[str, str]:
        """
        Parse <Metadata> section.
        Dynamically discovers all metadata fields.
        
        Returns:
            Dictionary with all metadata fields found
        """
        metadata_elem = self.root.find('Metadata')
        if metadata_elem is None:
            logger.warning("No <Metadata> section found")
            return {}
        
        metadata = {}
        
        # Dynamically parse ALL child elements
        for child in metadata_elem:
            field_name = child.tag.lower()
            
            # Store text content
            metadata[field_name] = child.text if child.text and child.text.strip() else None
            
            # Store attributes (like meaning="schema_version")
            for attr_name, attr_value in child.attrib.items():
                metadata[f"{field_name}_{attr_name}"] = attr_value
        
        # Validate required fields
        if 'id' not in metadata or 'name' not in metadata:
            logger.warning("Missing required metadata: Id or Name")
        
        return metadata
    
    def _parse_properties(self) -> Dict[str, Any]:
        """
        Parse <Property> section - DYNAMICALLY discovers all categories.
        No hardcoded category names (Phase, Thermal, Mechanical, etc.)
        
        Returns:
            Dictionary with ALL property categories found
        """
        category_elem = self.root.find('Category')
        if category_elem is None:
            logger.warning("No <Category> section found")
            return {}
        
        property_elem = category_elem.find('Property')
        if property_elem is None:
            logger.warning("No <Property> section found")
            return {}
        
        properties = {}
        
        # DYNAMICALLY discover ALL property categories
        for category in property_elem:
            category_name = category.tag
            logger.info(f"  Discovered property category: {category_name}")
            
            # Special handling for Phase (simple State element)
            if category_name == 'Phase':
                properties[category_name] = self._parse_phase(category)
            else:
                # Generic category parsing
                properties[category_name] = self._parse_property_category(category)
        
        return properties
    
    def _parse_phase(self, phase_elem: ET.Element) -> Dict[str, Any]:
        """
        Parse Phase information.
        Can handle State and any other Phase-related elements.
        """
        phase_data = {}
        
        # Dynamically parse all child elements
        for child in phase_elem:
            phase_data[child.tag] = child.text if child.text and child.text.strip() else None
        
        return phase_data
    
    def _parse_property_category(self, category_elem: ET.Element) -> Dict[str, Any]:
        """
        Parse a property category (Thermal, Mechanical, OR ANY NEW CATEGORY).
        Dynamically discovers all properties within the category.
        
        Returns:
            Dictionary mapping property names to their entries
        """
        properties = {}
        
        for prop_elem in category_elem:
            prop_name = prop_elem.tag
            
            # Check if it contains Entry elements
            entry_elements = prop_elem.findall('Entry')
            
            if entry_elements:
                # Has Entry children - parse as property with entries
                unit = prop_elem.get('unit', None)
                entries = self._parse_entries(prop_elem)
                
                properties[prop_name] = {
                    'unit': unit,
                    'entries': entries
                }
            elif list(prop_elem):
                # Has other child elements - recursive parsing
                properties[prop_name] = self._parse_generic_structure(prop_elem)
            else:
                # Simple text element
                properties[prop_name] = {
                    'value': prop_elem.text if prop_elem.text and prop_elem.text.strip() else None,
                    'unit': prop_elem.get('unit', None)
                }
        
        return properties
    
    def _parse_entries(self, parent_elem: ET.Element) -> List[Dict[str, Any]]:
        """
        Parse <Entry> elements within a property.
        
        Returns:
            List of entry dictionaries with value, ref, index, and any other attributes
        """
        entries = []
        
        for idx, entry_elem in enumerate(parent_elem.findall('Entry')):
            entry_data = {
                'value': entry_elem.text if entry_elem.text and entry_elem.text.strip() else None,
                'index': idx + 1  # 1-based indexing
            }
            
            # Dynamically capture ALL attributes (ref, unit, index, etc.)
            for attr_name, attr_value in entry_elem.attrib.items():
                entry_data[attr_name] = attr_value
            
            entries.append(entry_data)
        
        return entries
    
    def _parse_models(self) -> Dict[str, Any]:
        """
        Parse <Model> section - DYNAMICALLY discovers all model types.
        No hardcoded model names (ElasticModel, EOSModel, etc.)
        
        Returns:
            Dictionary with ALL model types found
        """
        category_elem = self.root.find('Category')
        if category_elem is None:
            return {}
        
        model_elem = category_elem.find('Model')
        if model_elem is None:
            logger.info("  No <Model> section found")
            return {}
        
        models = {}
        
        # DYNAMICALLY discover ALL model types
        for model_type_elem in model_elem:
            model_type = model_type_elem.tag
            logger.info(f"  Discovered model type: {model_type}")
            
            # Parse model structure generically
            models[model_type] = self._parse_model_structure(model_type_elem)
        
        return models
    
    def _parse_model_structure(self, model_elem: ET.Element) -> Dict[str, Any]:
        """
        Recursively parse any model structure.
        Handles sub-models, parameters, rows, nested structures.
        
        Args:
            model_elem: XML element representing a model
        
        Returns:
            Dictionary with complete model structure
        """
        model_data = {}
        
        # Check for Row elements (EOS models)
        rows = model_elem.findall('Row')
        if rows:
            model_data['rows'] = []
            for row_elem in rows:
                row_data = {
                    'index': row_elem.get('index', None),
                    'parameters': self._parse_generic_structure(row_elem)
                }
                model_data['rows'].append(row_data)
            return model_data
        
        # Otherwise, parse all children
        for child in model_elem:
            child_name = child.tag
            
            # Check if child contains Entry elements
            entry_elements = child.findall('Entry')
            
            if entry_elements:
                # Has Entry children
                unit = child.get('unit', None)
                entries = []
                
                for idx, entry_elem in enumerate(entry_elements):
                    entry_data = {
                        'value': entry_elem.text if entry_elem.text and entry_elem.text.strip() else None,
                        'index': idx + 1
                    }
                    
                    # Capture all attributes
                    for attr_name, attr_value in entry_elem.attrib.items():
                        entry_data[attr_name] = attr_value
                    
                    # If no unit on entry, use parent's unit
                    if 'unit' not in entry_data and unit:
                        entry_data['unit'] = unit
                    
                    entries.append(entry_data)
                
                model_data[child_name] = entries
            
            elif list(child):
                # Has child elements - recursive parsing
                model_data[child_name] = self._parse_generic_structure(child)
            
            else:
                # Simple text element
                value = child.text if child.text and child.text.strip() else None
                model_data[child_name] = {
                    'value': value,
                    'unit': child.get('unit', None),
                    'ref': child.get('ref', None)
                }
        
        return model_data
    
    def _parse_generic_structure(self, elem: ET.Element) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Generic recursive parser for any XML structure.
        Handles nested elements, entries, attributes.
        
        Args:
            elem: XML element to parse
        
        Returns:
            Dictionary or list representing the structure
        """
        result = {}
        
        for child in elem:
            child_name = child.tag
            
            # Check for Entry elements
            entry_elements = child.findall('Entry')
            
            if entry_elements:
                # Has Entry children
                unit = child.get('unit', None)
                entries = []
                
                for idx, entry_elem in enumerate(entry_elements):
                    entry_data = {
                        'value': entry_elem.text if entry_elem.text and entry_elem.text.strip() else None,
                        'index': idx + 1
                    }
                    
                    # Capture all attributes
                    for attr_name, attr_value in entry_elem.attrib.items():
                        entry_data[attr_name] = attr_value
                    
                    if 'unit' not in entry_data and unit:
                        entry_data['unit'] = unit
                    
                    entries.append(entry_data)
                
                result[child_name] = {
                    'unit': unit,
                    'entries': entries
                }
            
            elif list(child):
                # Has child elements - recurse
                result[child_name] = self._parse_generic_structure(child)
            
            else:
                # Leaf node - text content
                result[child_name] = {
                    'value': child.text if child.text and child.text.strip() else None
                }
                
                # Capture attributes
                for attr_name, attr_value in child.attrib.items():
                    result[child_name][attr_name] = attr_value
        
        return result


def parse_material_xml_dynamic(xml_file_path: str) -> Dict[str, Any]:
    """
    Convenience function to parse a material XML file dynamically.
    
    Args:
        xml_file_path: Path to material XML file
    
    Returns:
        Dictionary containing complete material data structure
    """
    parser = DynamicMaterialParser(xml_file_path)
    return parser.parse()


if __name__ == "__main__":
    import sys
    import os
    import json
    
    # Test with multiple materials
    test_files = [
        "Copper.xml",
        "TNT.xml", 
        "COMP-B.xml",
        "COMP-C4.xml"
    ]
    
    xml_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "xml")
    
    for test_file in test_files:
        file_path = os.path.join(xml_dir, test_file)
        
        if os.path.exists(file_path):
            print(f"\n{'='*70}")
            print(f"Testing: {test_file}")
            print('='*70)
            
            try:
                data = parse_material_xml_dynamic(file_path)
                
                print(f"\n✓ Material: {data['metadata'].get('name', 'Unknown')}")
                print(f"✓ Property categories: {', '.join(data['properties'].keys())}")
                print(f"✓ Model types: {', '.join(data['models'].keys())}")
                
            except Exception as e:
                print(f"✗ Error: {e}")
        else:
            print(f"\n✗ Not found: {test_file}")
    
    print("\n" + "="*70)
    print("✓ Dynamic parsing test complete!")
    print("="*70)
