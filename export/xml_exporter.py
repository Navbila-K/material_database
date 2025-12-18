"""
XML Export module for Material Database Engine.
Exports database data back to solver-compatible XML format.

CORE PRINCIPLE: Output must EXACTLY match original XML structure.
- Preserve tag order and hierarchy
- Include empty tags
- Maintain units and references
- Output must be solver-ready
"""
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import Dict, List, Any, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MaterialXMLExporter:
    """Exports material data from database back to XML format."""
    
    def __init__(self, material_data: Dict[str, Any]):
        """
        Initialize exporter with material data.
        
        Args:
            material_data: Material data dictionary from database query
        """
        self.material_data = material_data
        self.root = None
    
    def export_to_xml(self) -> ET.ElementTree:
        """
        Export material data to XML ElementTree.
        
        Returns:
            ElementTree object
        """
        # Create root element
        self.root = ET.Element('Material')
        
        # Add metadata
        self._add_metadata()
        
        # Add Category wrapper
        category = ET.SubElement(self.root, 'Category')
        
        # Add Property section
        self._add_properties(category)
        
        # Add Model section
        self._add_models(category)
        
        return ET.ElementTree(self.root)
    
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
        
        print(f"✓ Exported to: {output_path}")
    
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
        comment = '''<!--
=========================================================
                MATERIAL DESCRIPTION FILE
=========================================================
This XML defines a single material along with:
- metadata (id, name, author, date, version)
- categories of physical models (thermal, mechanical, plasticity, reaction, EOS)
- data stored as entries with units separated into attributes
- fully explicit structure, future-proof and backward compatible
=========================================================
-->
'''
        
        pretty_xml = reparsed.toprettyxml(indent='  ', encoding='utf-8').decode('utf-8')
        
        # Remove extra blank lines
        lines = [line for line in pretty_xml.split('\n') if line.strip()]
        
        # Remove XML declaration from minidom (we'll add our own)
        if lines and lines[0].startswith('<?xml'):
            lines = lines[1:]
        
        return xml_declaration + comment + '\n'.join(lines)
    
    def _add_metadata(self):
        """Add Metadata section."""
        metadata = self.material_data.get('metadata', {})
        
        metadata_elem = ET.SubElement(self.root, 'Metadata')
        
        # Add fields
        self._add_element(metadata_elem, 'Id', metadata.get('id'))
        self._add_element(metadata_elem, 'Name', metadata.get('name'))
        self._add_element(metadata_elem, 'Author', metadata.get('author'))
        self._add_element(metadata_elem, 'Date', metadata.get('date'))
        
        # Version with meaning attribute
        version_elem = ET.SubElement(metadata_elem, 'Version')
        if metadata.get('version_meaning'):
            version_elem.set('meaning', metadata.get('version_meaning'))
        version_elem.text = metadata.get('version') or ''
    
    def _add_properties(self, category: ET.Element):
        """Add Property section."""
        property_elem = ET.SubElement(category, 'Property')
        
        properties = self.material_data.get('properties', {})
        
        # Add Phase
        if 'Phase' in properties:
            self._add_phase(property_elem, properties['Phase'])
        
        # Add Thermal
        if 'Thermal' in properties:
            self._add_property_category(property_elem, 'Thermal', properties['Thermal'])
        
        # Add Mechanical
        if 'Mechanical' in properties:
            self._add_property_category(property_elem, 'Mechanical', properties['Mechanical'])
    
    def _add_phase(self, parent: ET.Element, phase_data: Dict[str, Any]):
        """Add Phase section."""
        phase_elem = ET.SubElement(parent, 'Phase')
        state_elem = ET.SubElement(phase_elem, 'State')
        state_elem.text = phase_data.get('State') or ''
    
    def _add_property_category(self, parent: ET.Element, category_name: str, 
                                category_data: Dict[str, Any]):
        """Add Thermal or Mechanical section."""
        category_elem = ET.SubElement(parent, category_name)
        
        for prop_name, prop_data in category_data.items():
            prop_elem = ET.SubElement(category_elem, prop_name)
            
            unit = prop_data.get('unit')
            if unit:
                prop_elem.set('unit', unit)
            
            entries = prop_data.get('entries', [])
            for entry in entries:
                entry_elem = ET.SubElement(prop_elem, 'Entry')
                
                ref = entry.get('ref')
                if ref:
                    entry_elem.set('ref', ref)
                
                value = entry.get('value')
                entry_elem.text = value if value is not None else ''
    
    def _add_models(self, category: ET.Element):
        """Add Model section."""
        model_elem = ET.SubElement(category, 'Model')
        
        models = self.material_data.get('models', {})
        
        # Add ElasticModel
        if 'ElasticModel' in models:
            self._add_elastic_model(model_elem, models['ElasticModel'])
        
        # Add ElastoPlastic
        if 'ElastoPlastic' in models:
            self._add_elastoplastic_model(model_elem, models['ElastoPlastic'])
        
        # Add ReactionModel
        if 'ReactionModel' in models:
            self._add_reaction_model(model_elem, models['ReactionModel'])
        
        # Add EOSModel
        if 'EOSModel' in models:
            self._add_eos_model(model_elem, models['EOSModel'])
    
    def _add_elastic_model(self, parent: ET.Element, model_data: Dict[str, Any]):
        """Add ElasticModel section."""
        elastic_elem = ET.SubElement(parent, 'ElasticModel')
        
        thermo_data = model_data.get('ThermoMechanical', {})
        if thermo_data:
            thermo_elem = ET.SubElement(elastic_elem, 'ThermoMechanical')
            
            for param_name, param_value in thermo_data.items():
                if isinstance(param_value, dict) and not isinstance(param_value, list):
                    # Complex structure (e.g., SpecificHeatConstants)
                    param_elem = ET.SubElement(thermo_elem, param_name)
                    for sub_name, sub_data in param_value.items():
                        sub_elem = ET.SubElement(param_elem, sub_name)
                        if isinstance(sub_data, dict):
                            unit = sub_data.get('unit')
                            if unit:
                                sub_elem.set('unit', unit)
                            value = sub_data.get('value')
                            sub_elem.text = value if value is not None else ''
                else:
                    # List of entries
                    param_elem = ET.SubElement(thermo_elem, param_name)
                    
                    # Get unit from first entry if available
                    if param_value and isinstance(param_value, list) and param_value[0].get('unit'):
                        # Check if all entries have same unit
                        first_unit = param_value[0].get('unit')
                        if all(e.get('unit') == first_unit for e in param_value):
                            param_elem.set('unit', first_unit)
                    
                    for entry in param_value:
                        entry_elem = ET.SubElement(param_elem, 'Entry')
                        
                        unit = entry.get('unit')
                        if unit and not param_elem.get('unit'):
                            entry_elem.set('unit', unit)
                        
                        ref = entry.get('ref')
                        if ref:
                            entry_elem.set('ref', ref)
                        
                        value = entry.get('value')
                        entry_elem.text = value if value is not None else ''
    
    def _add_elastoplastic_model(self, parent: ET.Element, model_data: Dict[str, Any]):
        """Add ElastoPlastic section."""
        elastoplastic_elem = ET.SubElement(parent, 'ElastoPlastic')
        
        for param_name, param_value in model_data.items():
            if isinstance(param_value, dict) and 'value' not in param_value:
                # Complex structure (e.g., JohnsonCookModelConstants)
                param_elem = ET.SubElement(elastoplastic_elem, param_name)
                
                for sub_name, sub_data in param_value.items():
                    sub_elem = ET.SubElement(param_elem, sub_name)
                    
                    if isinstance(sub_data, dict):
                        unit = sub_data.get('unit')
                        if unit:
                            sub_elem.set('unit', unit)
                        
                        ref = sub_data.get('ref')
                        if ref:
                            sub_elem.set('ref', ref)
                        
                        value = sub_data.get('value')
                        sub_elem.text = value if value is not None else ''
            else:
                # Simple entries (ShearModulus, YieldStrength)
                param_elem = ET.SubElement(elastoplastic_elem, param_name)
                
                entries = param_value if isinstance(param_value, list) else [param_value]
                
                for entry in entries:
                    entry_elem = ET.SubElement(param_elem, 'Entry')
                    
                    unit = entry.get('unit')
                    if unit:
                        entry_elem.set('unit', unit)
                    
                    ref = entry.get('ref')
                    if ref:
                        entry_elem.set('ref', ref)
                    
                    value = entry.get('value')
                    entry_elem.text = value if value is not None else ''
    
    def _add_reaction_model(self, parent: ET.Element, model_data: Dict[str, Any]):
        """Add ReactionModel section."""
        reaction_elem = ET.SubElement(parent, 'ReactionModel')
        
        # Add Kind
        kind_elem = ET.SubElement(reaction_elem, 'Kind')
        kind_elem.text = model_data.get('Kind') or ''
        
        # Add indexed parameters
        for param_name in ['LnZ', 'ActivationEnergy', 'HeatRelease']:
            if param_name in model_data:
                entries = model_data[param_name]
                if entries:
                    param_elem = ET.SubElement(reaction_elem, param_name)
                    
                    # Get unit from first entry
                    unit = entries[0].get('unit')
                    if unit:
                        param_elem.set('unit', unit)
                    
                    for entry in entries:
                        entry_elem = ET.SubElement(param_elem, 'Entry')
                        
                        index = entry.get('index')
                        if index:
                            entry_elem.set('index', str(index))
                        
                        ref = entry.get('ref')
                        if ref:
                            entry_elem.set('ref', ref)
                        
                        value = entry.get('value')
                        entry_elem.text = value if value is not None else ''
        
        # Add ReactionModelParameter
        if 'ReactionModelParameter' in model_data:
            param_elem = ET.SubElement(reaction_elem, 'ReactionModelParameter')
            
            for sub_name, sub_data in model_data['ReactionModelParameter'].items():
                sub_elem = ET.SubElement(param_elem, sub_name)
                
                if isinstance(sub_data, dict):
                    unit = sub_data.get('unit')
                    if unit:
                        sub_elem.set('unit', unit)
                    
                    ref = sub_data.get('ref')
                    if ref:
                        sub_elem.set('ref', ref)
                    
                    value = sub_data.get('value')
                    sub_elem.text = value if value is not None else ''
    
    def _add_eos_model(self, parent: ET.Element, model_data: Dict[str, Any]):
        """Add EOSModel section with Row structures."""
        eos_elem = ET.SubElement(parent, 'EOSModel')
        
        rows = model_data.get('rows', [])
        
        for row in rows:
            row_elem = ET.SubElement(eos_elem, 'Row')
            
            index = row.get('index')
            if index:
                row_elem.set('index', str(index))
            
            parameters = row.get('parameters', {})
            
            for param_name, param_data in parameters.items():
                if isinstance(param_data, dict) and 'value' not in param_data:
                    # Nested structure (unreacted/reacted)
                    nested_elem = ET.SubElement(row_elem, param_name)
                    
                    for sub_name, sub_data in param_data.items():
                        sub_elem = ET.SubElement(nested_elem, sub_name)
                        
                        if isinstance(sub_data, dict):
                            unit = sub_data.get('unit')
                            if unit:
                                sub_elem.set('unit', unit)
                            
                            ref = sub_data.get('ref')
                            if ref:
                                sub_elem.set('ref', ref)
                            
                            value = sub_data.get('value')
                            sub_elem.text = value if value is not None else ''
                else:
                    # Simple parameter
                    param_elem = ET.SubElement(row_elem, param_name)
                    
                    if isinstance(param_data, dict):
                        unit = param_data.get('unit')
                        if unit:
                            param_elem.set('unit', unit)
                        
                        ref = param_data.get('ref')
                        if ref:
                            param_elem.set('ref', ref)
                        
                        value = param_data.get('value')
                        param_elem.text = value if value is not None else ''
    
    def _add_element(self, parent: ET.Element, tag: str, text: Optional[str]):
        """Helper to add element with text."""
        elem = ET.SubElement(parent, tag)
        elem.text = text if text is not None else ''


def export_material_to_xml(material_data: Dict[str, Any], output_path: str):
    """
    Convenience function to export material to XML file.
    
    Args:
        material_data: Material data dictionary
        output_path: Path to output XML file
    """
    exporter = MaterialXMLExporter(material_data)
    exporter.export_to_file(output_path)


if __name__ == "__main__":
    # Test export
    import os
    from db.database import DatabaseManager
    from db.query import MaterialQuerier
    from config import EXPORT_DIR
    
    db = DatabaseManager()
    db.connect()
    
    querier = MaterialQuerier(db)
    materials = querier.list_materials()
    
    if materials:
        material = materials[0]
        print(f"Exporting: {material['name']}")
        
        material_data = querier.get_material_by_id(material['material_id'])
        
        output_path = os.path.join(EXPORT_DIR, f"{material['name']}_exported.xml")
        export_material_to_xml(material_data, output_path)
    else:
        print("No materials found in database")
    
    db.close()
