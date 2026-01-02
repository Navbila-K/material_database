"""
Quick Parser for 10-Category XML Format
Imports PBX-9404.xml and other new-format materials
"""
import xml.etree.ElementTree as ET
from db.database import DatabaseManager


def import_10cat_xml(xml_path):
    """Import material from 10-category XML format."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    db = DatabaseManager()
    conn = db.connect()
    cursor = conn.cursor()
    
    # Parse metadata
    meta = root.find('Metadata')
    xml_id = meta.find('Id').text
    name = meta.find('Name').text
    author = meta.find('Author').text if meta.find('Author') is not None else None
    date = meta.find('Date').text if meta.find('Date') is not None else None
    version = meta.find('Version').text if meta.find('Version') is not None else '2.0.0'
    
    # Insert material
    cursor.execute("""
        INSERT INTO materials (xml_id, name, author, date, version)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (xml_id) DO UPDATE 
        SET name = EXCLUDED.name, author = EXCLUDED.author, 
            date = EXCLUDED.date, version = EXCLUDED.version
        RETURNING material_id
    """, (xml_id, name, author, date, version))
    
    material_id = cursor.fetchone()[0]
    print(f"✓ Material imported: {name} (ID: {material_id})")
    
    # Parse categories
    for category in root.findall('Category'):
        cat_name = category.get('name')
        
        # Get category_id from category_master
        cursor.execute("SELECT category_id FROM category_master WHERE category_name = %s", (cat_name,))
        result = cursor.fetchone()
        if not result:
            print(f"⚠ Category not found: {cat_name}, skipping...")
            continue
        
        standard_category_id = result[0]
        
        # Create property_categories entry
        cursor.execute("""
            INSERT INTO property_categories (material_id, category_type, standard_category_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (material_id, category_type) DO NOTHING
            RETURNING category_id
        """, (material_id, cat_name, standard_category_id))
        
        result = cursor.fetchone()
        if result:
            property_category_id = result[0]
        else:
            cursor.execute("""
                SELECT category_id FROM property_categories 
                WHERE material_id = %s AND category_type = %s
            """, (material_id, cat_name))
            property_category_id = cursor.fetchone()[0]
        
        # Parse properties (both direct and in subcategories)
        for elem in category:
            if elem.tag == 'Subcategory':
                subcat_name = elem.get('name')
                for prop in elem.findall('Property'):
                    _insert_property(cursor, property_category_id, standard_category_id, 
                                   prop, subcat_name)
            elif elem.tag == 'Property':
                _insert_property(cursor, property_category_id, standard_category_id, 
                               elem, None)
    
    conn.commit()
    print(f"✓ Import complete: {name}")
    
    cursor.close()
    db.close()


def _insert_property(cursor, property_category_id, standard_category_id, prop_elem, subcategory):
    """Helper to insert a property."""
    prop_name = prop_elem.get('name')
    value = prop_elem.get('value', '')
    unit = prop_elem.get('unit')
    ref_id = prop_elem.get('ref')
    
    # Insert or get property
    cursor.execute("""
        INSERT INTO properties (category_id, property_name, unit, standard_category_id, subcategory_name)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (category_id, property_name) DO NOTHING
        RETURNING property_id
    """, (property_category_id, prop_name, unit, standard_category_id, subcategory))
    
    result = cursor.fetchone()
    if result:
        property_id = result[0]
    else:
        cursor.execute("""
            SELECT property_id FROM properties 
            WHERE category_id = %s AND property_name = %s
        """, (property_category_id, prop_name))
        property_id = cursor.fetchone()[0]
    
    # Insert entry if value exists
    if value:
        cursor.execute("""
            INSERT INTO property_entries (property_id, value, ref_id, entry_index)
            VALUES (%s, %s, %s, 0)
        """, (property_id, value, ref_id))


if __name__ == "__main__":
    import sys
    xml_file = sys.argv[1] if len(sys.argv) > 1 else "xml/PBX-9404.xml"
    import_10cat_xml(xml_file)
