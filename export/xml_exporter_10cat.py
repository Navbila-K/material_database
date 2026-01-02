"""
XML Export module for Material Database Engine - Version 2.0
Exports database data to 10-category XML format.

NEW STRUCTURE:
- 10 standardized categories
- Optional subcategories
- Backward compatible with old format
"""
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import Dict, List, Any, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.database import DatabaseManager


class Material10CategoryExporter:
    """Exports material data using 10-category structure."""
    
    # 10 Standard Categories in order
    CATEGORIES = [
        'Structure_and_Formulation',
        'Physical_Properties',
        'Chemical_Properties',
        'Thermal_Properties',
        'Mechanical_Properties',
        'Detonation_Properties',
        'Sensitivity',
        'Electrical_Properties',
        'Toxicity',
        'Additional_Properties'
    ]
    
    CATEGORY_DESCRIPTIONS = {
        'Structure_and_Formulation': 'Chemical composition and formulation details',
        'Physical_Properties': 'Physical state, appearance, and density information',
        'Chemical_Properties': 'Thermochemical and reactivity properties',
        'Thermal_Properties': 'Thermal conductivity, heat capacity, and thermal stability',
        'Mechanical_Properties': 'Mechanical strength, creep, and stress-strain behavior',
        'Detonation_Properties': 'Detonation velocity, pressure, energy, and performance metrics',
        'Sensitivity': 'Impact, friction, shock, and initiation sensitivity',
        'Electrical_Properties': 'Electrical conductivity and dielectric properties',
        'Toxicity': 'Toxicological and safety information',
        'Additional_Properties': 'Other properties and miscellaneous data'
    }
    
    def __init__(self, db_manager: DatabaseManager, material_id: int):
        """
        Initialize exporter.
        
        Args:
            db_manager: Database manager instance
            material_id: ID of material to export
        """
        self.db = db_manager
        self.material_id = material_id
        self.material_data = None
        self.properties_by_category = {}
        self.root = None
    
    def load_material_data(self):
        """Load all material data from database."""
        conn = self.db.connect()
        cursor = conn.cursor()
        
        # Load material metadata
        cursor.execute('''
            SELECT material_id, xml_id, name, author, date, version, version_meaning
            FROM materials
            WHERE material_id = %s
        ''', (self.material_id,))
        
        result = cursor.fetchone()
        if not result:
            raise ValueError(f"Material with ID {self.material_id} not found")
        
        self.material_data = {
            'material_id': result[0],
            'xml_id': result[1],
            'name': result[2],
            'author': result[3],
            'date': result[4],
            'version': result[5],
            'version_meaning': result[6]
        }
        
        # Load properties grouped by category
        cursor.execute('''
            SELECT 
                cm.category_name,
                cm.display_order,
                p.subcategory_name,
                p.property_name,
                p.unit,
                pe.value,
                pe.ref_id,
                pe.entry_index
            FROM properties p
            JOIN property_categories pc ON p.category_id = pc.category_id
            LEFT JOIN category_master cm ON p.standard_category_id = cm.category_id
            LEFT JOIN property_entries pe ON p.property_id = pe.property_id
            WHERE pc.material_id = %s
            ORDER BY cm.display_order, p.subcategory_name, p.property_name, pe.entry_index
        ''', (self.material_id,))
        
        properties = cursor.fetchall()
        
        # Group properties by category and subcategory
        for prop in properties:
            category = prop[0] or 'Additional_Properties'
            subcategory = prop[2]
            property_name = prop[3]
            unit = prop[4]
            value = prop[5]
            ref_id = prop[6]
            
            if category not in self.properties_by_category:
                self.properties_by_category[category] = {}
            
            if subcategory not in self.properties_by_category[category]:
                self.properties_by_category[category][subcategory] = {}
            
            if property_name not in self.properties_by_category[category][subcategory]:
                self.properties_by_category[category][subcategory][property_name] = {
                    'unit': unit,
                    'values': []
                }
            
            if value:  # Only add if value exists
                self.properties_by_category[category][subcategory][property_name]['values'].append({
                    'value': value,
                    'ref': ref_id
                })
        
        cursor.close()
    
    def export_to_xml(self) -> ET.ElementTree:
        """
        Export material data to XML ElementTree using 10-category structure.
        
        Returns:
            ElementTree object
        """
        # Load data first
        self.load_material_data()
        
        # Create root element
        self.root = ET.Element('Material')
        
        # Add metadata
        self._add_metadata()
        
        # Add each of the 10 categories
        for category_name in self.CATEGORIES:
            if category_name in self.properties_by_category:
                self._add_category(category_name)
        
        return ET.ElementTree(self.root)
    
    def _add_metadata(self):
        """Add metadata section."""
        metadata = ET.SubElement(self.root, 'Metadata')
        
        # Add metadata fields
        ET.SubElement(metadata, 'Id').text = self.material_data['xml_id'] or ''
        ET.SubElement(metadata, 'Name').text = self.material_data['name'] or ''
        ET.SubElement(metadata, 'Author').text = self.material_data['author'] or ''
        ET.SubElement(metadata, 'Date').text = self.material_data['date'] or ''
        
        version = ET.SubElement(metadata, 'Version')
        version.text = self.material_data['version'] or '2.0.0'
        if self.material_data.get('version_meaning'):
            version.set('meaning', self.material_data['version_meaning'])
        else:
            version.set('meaning', 'schema_version')
    
    def _add_category(self, category_name: str):
        """
        Add a category section with all its properties.
        
        Args:
            category_name: Name of category (e.g., 'Physical_Properties')
        """
        category = ET.SubElement(self.root, 'Category')
        category.set('name', category_name)
        
        # Add description
        description = ET.SubElement(category, 'Description')
        description.text = self.CATEGORY_DESCRIPTIONS.get(category_name, '')
        
        # Get properties for this category
        category_data = self.properties_by_category.get(category_name, {})
        
        # Group by subcategory
        for subcategory_name, properties in sorted(category_data.items()):
            if subcategory_name:  # Has subcategory
                subcategory = ET.SubElement(category, 'Subcategory')
                subcategory.set('name', subcategory_name)
                parent = subcategory
            else:  # No subcategory
                parent = category
            
            # Add properties
            for prop_name, prop_data in sorted(properties.items()):
                self._add_property(parent, prop_name, prop_data)
    
    def _add_property(self, parent: ET.Element, property_name: str, property_data: Dict):
        """
        Add a property element.
        
        Args:
            parent: Parent element (Category or Subcategory)
            property_name: Name of property
            property_data: Property data dict with 'unit' and 'values'
        """
        prop_elem = ET.SubElement(parent, 'Property')
        prop_elem.set('name', property_name)
        
        # Add unit if present
        if property_data['unit']:
            prop_elem.set('unit', property_data['unit'])
        
        # Add values
        values = property_data['values']
        if len(values) == 1:
            # Single value - set as attribute
            prop_elem.set('value', values[0]['value'])
            if values[0]['ref']:
                prop_elem.set('ref', str(values[0]['ref']))
        else:
            # Multiple values - use Entry elements
            for entry in values:
                entry_elem = ET.SubElement(prop_elem, 'Entry')
                entry_elem.text = entry['value']
                if entry['ref']:
                    entry_elem.set('ref', str(entry['ref']))
    
    def export_to_file(self, output_path: str):
        """
        Export material data to XML file.
        
        Args:
            output_path: Path to output XML file
        """
        tree = self.export_to_xml()
        
        # Pretty print
        xml_str = self._prettify(self.root)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_str)
        
        print(f"✓ Exported '{self.material_data['name']}' to: {output_path}")
    
    def _prettify(self, elem: ET.Element) -> str:
        """
        Return pretty-printed XML string.
        
        Args:
            elem: Root element
        
        Returns:
            Formatted XML string
        """
        rough_string = ET.tostring(elem, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        
        # Add XML declaration and comment
        xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n\n'
        comment = f'''<!--
=========================================================
              MATERIAL DESCRIPTION FILE
              {self.material_data['name']}
=========================================================
This XML uses the 10-category standardized structure:
1. Structure and Formulation
2. Physical Properties
3. Chemical Properties
4. Thermal Properties
5. Mechanical Properties
6. Detonation Properties
7. Sensitivity
8. Electrical Properties
9. Toxicity
10. Additional Properties

Schema version: 2.0.0
Exported from Materials Database
=========================================================
-->
'''
        
        # Get pretty XML (remove first line which is minidom's declaration)
        pretty_xml = '\n'.join(reparsed.toprettyxml(indent='  ').split('\n')[1:])
        
        return xml_declaration + comment + pretty_xml


def export_material(material_id: int, output_dir: str = 'export/output') -> str:
    """
    Convenience function to export a material.
    
    Args:
        material_id: ID of material to export
        output_dir: Output directory
    
    Returns:
        Path to exported file
    """
    db = DatabaseManager()
    exporter = Material10CategoryExporter(db, material_id)
    exporter.load_material_data()
    
    # Create output directory if needed
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename
    material_name = exporter.material_data['name'].replace(' ', '_')
    output_path = os.path.join(output_dir, f"{material_name}_10cat.xml")
    
    exporter.export_to_file(output_path)
    db.close()
    
    return output_path


if __name__ == '__main__':
    """Test exporter with Aluminum."""
    print("Testing 10-Category XML Exporter...")
    
    # Export Aluminum (material_id = 1)
    output_file = export_material(1)
    print(f"\n✓ Test complete! Check: {output_file}")
