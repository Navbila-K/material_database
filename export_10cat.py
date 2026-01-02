"""
Quick XML Exporter for 10-Category Format
Exports materials in the new standardized structure
"""
import xml.etree.ElementTree as ET
from xml.dom import minidom
from db.database import DatabaseManager


def export_material_10cat(material_id, output_path):
    """Export material using 10-category structure."""
    db = DatabaseManager()
    conn = db.connect()
    cursor = conn.cursor()
    
    # Get material metadata
    cursor.execute("SELECT * FROM materials WHERE material_id = %s", (material_id,))
    mat = cursor.fetchone()
    cols = [desc[0] for desc in cursor.description]
    material = dict(zip(cols, mat))
    
    # Create XML
    root = ET.Element('Material')
    
    # Metadata
    meta = ET.SubElement(root, 'Metadata')
    ET.SubElement(meta, 'Id').text = material['xml_id']
    ET.SubElement(meta, 'Name').text = material['name']
    ET.SubElement(meta, 'Author').text = material.get('author') or ''
    ET.SubElement(meta, 'Date').text = material.get('date') or ''
    version_elem = ET.SubElement(meta, 'Version')
    version_elem.set('meaning', 'schema_version')
    version_elem.text = material.get('version') or '2.0.0'
    
    # Get all 10 categories in order
    cursor.execute("""
        SELECT category_id, category_name, display_order 
        FROM category_master 
        ORDER BY display_order
    """)
    categories = cursor.fetchall()
    
    for cat_id, cat_name, _ in categories:
        # Get properties for this category
        cursor.execute("""
            SELECT p.property_name, p.unit, p.subcategory_name,
                   pe.value, pe.ref_id, pe.entry_index
            FROM properties p
            JOIN property_categories pc ON p.category_id = pc.category_id
            LEFT JOIN property_entries pe ON p.property_id = pe.property_id
            WHERE pc.material_id = %s AND p.standard_category_id = %s
            ORDER BY p.subcategory_name, p.property_name, pe.entry_index
        """, (material_id, cat_id))
        
        props = cursor.fetchall()
        
        if props:
            cat_elem = ET.SubElement(root, 'Category')
            cat_elem.set('name', cat_name)
            
            # Group by subcategory
            current_subcat = None
            subcat_elem = None
            
            for prop_name, unit, subcat, value, ref_id, _ in props:
                if subcat and subcat != current_subcat:
                    current_subcat = subcat
                    subcat_elem = ET.SubElement(cat_elem, 'Subcategory')
                    subcat_elem.set('name', subcat)
                
                parent = subcat_elem if subcat_elem else cat_elem
                prop_elem = ET.SubElement(parent, 'Property')
                prop_elem.set('name', prop_name)
                if value:
                    prop_elem.set('value', value)
                if unit:
                    prop_elem.set('unit', unit)
                if ref_id:
                    prop_elem.set('ref', str(ref_id))
    
    # Pretty print
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    
    with open(output_path, 'w') as f:
        f.write(xml_str)
    
    print(f"✓ Exported: {output_path}")
    
    cursor.close()
    db.close()


if __name__ == "__main__":
    # Test export
    export_material_10cat(1, "export/output/Aluminum_10cat.xml")
