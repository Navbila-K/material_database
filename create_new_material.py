#!/usr/bin/env python3
"""
XML Material File Generator
Creates new material XML files following the existing schema format
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import hashlib

def fnv1a_32(data: str) -> str:
    """Calculate FNV-1a 32-bit hash for version checksum"""
    FNV_32_PRIME = 0x01000193
    FNV_32_INIT = 0x811c9dc5
    
    hash_value = FNV_32_INIT
    for byte in data.encode('utf-8'):
        hash_value ^= byte
        hash_value = (hash_value * FNV_32_PRIME) & 0xffffffff
    
    return format(hash_value, '08X')

def create_material_xml(material_data):
    """
    Generate XML file for a new material
    
    Args:
        material_data: Dictionary with material information
        {
            'name': 'Material Name',
            'description': 'Material description',
            'properties': {
                'Phase': {
                    'Density': [{'value': '1.8', 'unit': 'g/cm^3', 'ref': '1', 'note': ''}],
                },
                'Thermal': {
                    'Thermal Conductivity': [{'value': '0.5', 'unit': 'W/m-K', 'ref': '1'}],
                }
            },
            'models': {
                'ElasticModel': {
                    'Elastic': {
                        'Bulk Modulus': {'value': '10', 'unit': 'GPa', 'ref': '1'}
                    }
                }
            }
        }
    """
    
    # Create root element
    root = ET.Element('Material')
    
    # Add Metadata
    metadata = ET.SubElement(root, 'Metadata')
    
    # Generate ID from material name
    material_id = material_data['name'].upper().replace(' ', '_').replace('-', '_')
    ET.SubElement(metadata, 'Id').text = material_id
    ET.SubElement(metadata, 'Name').text = material_data['name']
    
    # Generate version with checksum
    version_str = "0.0.0"
    checksum = fnv1a_32(material_id)
    ET.SubElement(metadata, 'Version').text = f"{version_str}-{checksum}"
    
    # Add description if provided
    if material_data.get('description'):
        ET.SubElement(metadata, 'Description').text = material_data['description']
    
    ET.SubElement(metadata, 'VersionMeaning').text = "Major.Minor.Patch"
    
    # Add Category section
    category = ET.SubElement(root, 'Category')
    
    # Add Properties
    property_section = ET.SubElement(category, 'Property')
    
    for category_name, properties in material_data.get('properties', {}).items():
        cat_elem = ET.SubElement(property_section, category_name)
        
        for prop_name, entries in properties.items():
            prop_elem = ET.SubElement(cat_elem, prop_name.replace(' ', ''))
            
            # Add entries
            for entry in entries:
                entry_elem = ET.SubElement(prop_elem, 'entry')
                entry_elem.set('value', str(entry['value']))
                entry_elem.set('ref', str(entry.get('ref', '1')))
                
                if entry.get('unit'):
                    entry_elem.set('unit', entry['unit'])
                if entry.get('note'):
                    entry_elem.set('note', entry['note'])
    
    # Add Models
    model_section = ET.SubElement(category, 'Model')
    
    for model_name, submodels in material_data.get('models', {}).items():
        model_elem = ET.SubElement(model_section, model_name)
        
        for submodel_name, parameters in submodels.items():
            submodel_elem = ET.SubElement(model_elem, submodel_name)
            
            for param_name, param_data in parameters.items():
                param_elem = ET.SubElement(submodel_elem, param_name.replace(' ', ''))
                param_elem.set('value', str(param_data['value']))
                param_elem.set('ref', str(param_data.get('ref', '1')))
                
                if param_data.get('unit'):
                    param_elem.set('unit', param_data['unit'])
    
    # Pretty print
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    
    # Remove extra blank lines
    xml_lines = [line for line in xml_str.split('\n') if line.strip()]
    xml_str = '\n'.join(xml_lines)
    
    return xml_str

def save_material_xml(material_data, output_dir='xml'):
    """Save material XML to file"""
    xml_content = create_material_xml(material_data)
    
    filename = f"{output_dir}/{material_data['name'].replace(' ', '_')}.xml"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    print(f"✅ Created: {filename}")
    return filename


# Example usage - Template for LASL materials
if __name__ == "__main__":
    
    # TEMPLATE - Fill in data from LASL PDF
    example_material = {
        'name': 'COMP-B',  # Change this
        'description': 'Composition B explosive - 60% RDX, 40% TNT',  # From PDF
        
        'properties': {
            'Phase': {
                'Density': [
                    {'value': '1.717', 'unit': 'g/cm^3', 'ref': '1', 'note': 'at 25°C'}
                ],
                'Melting Point': [
                    {'value': '79', 'unit': '°C', 'ref': '1'}
                ]
            },
            'Thermal': {
                'Thermal Conductivity': [
                    {'value': '0.23', 'unit': 'W/m-K', 'ref': '1', 'note': 'at 20°C'}
                ],
                'Specific Heat': [
                    {'value': '1050', 'unit': 'J/kg-K', 'ref': '1'}
                ]
            },
            'Detonation': {
                'Detonation Velocity': [
                    {'value': '7980', 'unit': 'm/s', 'ref': '1', 'note': 'at density 1.717 g/cm³'}
                ],
                'Detonation Pressure': [
                    {'value': '29.5', 'unit': 'GPa', 'ref': '1'}
                ]
            }
        },
        
        'models': {
            'ElasticModel': {
                'Elastic': {
                    'Bulk Modulus': {'value': '12.0', 'unit': 'GPa', 'ref': '1'}
                }
            },
            'EOSModel': {
                'JWL': {
                    'A': {'value': '524.2', 'unit': 'GPa', 'ref': '1'},
                    'B': {'value': '7.678', 'unit': 'GPa', 'ref': '1'},
                    'R1': {'value': '4.2', 'unit': '--', 'ref': '1'},
                    'R2': {'value': '1.1', 'unit': '--', 'ref': '1'},
                    'omega': {'value': '0.34', 'unit': '--', 'ref': '1'}
                }
            }
        }
    }
    
    # Generate XML
    save_material_xml(example_material)
    
    print("\n" + "="*60)
    print("XML file created successfully!")
    print("="*60)
    print("\nNext steps:")
    print("1. Edit the material_data dictionary with data from LASL PDF")
    print("2. Run this script to generate XML")
    print("3. Import: python main.py import xml/YourMaterial.xml")
    print("4. Or import all: python main.py import-all")
