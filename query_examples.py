#!/usr/bin/env python3
"""
Advanced query examples for Materials Database.
Demonstrates various ways to query and analyze material data.
"""
from db.database import DatabaseManager
from db.query import MaterialQuerier
import psycopg2

def query_by_property(property_name):
    """Get all materials with a specific property."""
    db = DatabaseManager()
    conn = db.connect()
    cursor = conn.cursor()
    
    sql = """
        SELECT m.name, p.property_name, pe.value, pe.ref_id, p.unit
        FROM materials m
        JOIN property_categories pc ON m.material_id = pc.material_id
        JOIN properties p ON pc.category_id = p.category_id
        JOIN property_entries pe ON p.property_id = pe.property_id
        WHERE p.property_name = %s
        ORDER BY m.name, pe.entry_index;
    """
    
    cursor.execute(sql, (property_name,))
    results = cursor.fetchall()
    
    print(f"\n{'='*80}")
    print(f"Property: {property_name}")
    print(f"{'='*80}")
    
    for row in results:
        name, prop, value, ref, unit = row
        ref_str = f" [ref: {ref}]" if ref else ""
        print(f"{name:20} {value or '(empty)':15} {unit or '':10}{ref_str}")
    
    cursor.close()
    conn.close()

def compare_materials(material_names):
    """Compare properties across multiple materials."""
    db = DatabaseManager()
    conn = db.connect()
    cursor = conn.cursor()
    
    placeholders = ','.join(['%s'] * len(material_names))
    
    sql = f"""
        SELECT m.name, pc.category_type, p.property_name, 
               COUNT(pe.entry_id) as entry_count,
               STRING_AGG(pe.value, ', ' ORDER BY pe.entry_index) as values
        FROM materials m
        JOIN property_categories pc ON m.material_id = pc.material_id
        JOIN properties p ON pc.category_id = p.category_id
        LEFT JOIN property_entries pe ON p.property_id = pe.property_id
        WHERE m.name IN ({placeholders})
        GROUP BY m.name, pc.category_type, p.property_name, p.unit
        ORDER BY m.name, pc.category_type, p.property_name;
    """
    
    cursor.execute(sql, tuple(material_names))
    results = cursor.fetchall()
    
    print(f"\n{'='*80}")
    print(f"Material Comparison: {', '.join(material_names)}")
    print(f"{'='*80}")
    
    current_material = None
    for row in results:
        name, category, prop, count, values = row
        if name != current_material:
            print(f"\n{name}:")
            current_material = name
        print(f"  {category}/{prop}: {values or '(empty)'}")
    
    cursor.close()
    conn.close()

def find_materials_by_model(model_type):
    """Find all materials with a specific model type."""
    db = DatabaseManager()
    conn = db.connect()
    cursor = conn.cursor()
    
    sql = """
        SELECT DISTINCT m.name, m.xml_id
        FROM materials m
        JOIN models mo ON m.material_id = mo.material_id
        WHERE mo.model_type = %s
        ORDER BY m.name;
    """
    
    cursor.execute(sql, (model_type,))
    results = cursor.fetchall()
    
    print(f"\n{'='*80}")
    print(f"Materials with {model_type}")
    print(f"{'='*80}")
    
    for name, xml_id in results:
        print(f"  {name:20} ({xml_id})")
    
    print(f"\nTotal: {len(results)} materials")
    
    cursor.close()
    conn.close()

def get_material_statistics():
    """Get overall database statistics."""
    db = DatabaseManager()
    conn = db.connect()
    cursor = conn.cursor()
    
    print(f"\n{'='*80}")
    print("DATABASE STATISTICS")
    print(f"{'='*80}")
    
    # Total materials
    cursor.execute("SELECT COUNT(*) FROM materials;")
    total_materials = cursor.fetchone()[0]
    print(f"\nTotal Materials: {total_materials}")
    
    # Total properties
    cursor.execute("SELECT COUNT(*) FROM properties;")
    total_properties = cursor.fetchone()[0]
    print(f"Total Properties: {total_properties}")
    
    # Total property entries
    cursor.execute("SELECT COUNT(*) FROM property_entries;")
    total_entries = cursor.fetchone()[0]
    print(f"Total Property Entries: {total_entries}")
    
    # Total models
    cursor.execute("SELECT COUNT(*) FROM models;")
    total_models = cursor.fetchone()[0]
    print(f"Total Models: {total_models}")
    
    # Total model parameters
    cursor.execute("SELECT COUNT(*) FROM model_parameters;")
    total_params = cursor.fetchone()[0]
    print(f"Total Model Parameters: {total_params}")
    
    # Materials by type (based on state)
    cursor.execute("""
        SELECT pe.value, COUNT(DISTINCT m.material_id)
        FROM materials m
        JOIN property_categories pc ON m.material_id = pc.material_id
        JOIN properties p ON pc.category_id = p.category_id
        JOIN property_entries pe ON p.property_id = pe.property_id
        WHERE p.property_name = 'State'
        GROUP BY pe.value;
    """)
    
    print(f"\nMaterials by State:")
    for state, count in cursor.fetchall():
        print(f"  {state}: {count}")
    
    cursor.close()
    conn.close()

def search_materials(search_term):
    """Search materials by name."""
    db = DatabaseManager()
    querier = MaterialQuerier(db)
    
    materials = querier.list_materials()
    
    results = [m for m in materials if search_term.lower() in m['name'].lower()]
    
    print(f"\n{'='*80}")
    print(f"Search results for: '{search_term}'")
    print(f"{'='*80}\n")
    
    if results:
        for mat in results:
            print(f"  {mat['name']:20} {mat['xml_id']:20} v{mat['version']}")
    else:
        print("  No materials found.")
    
    querier.conn.close()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python query_examples.py property <PropertyName>")
        print("  python query_examples.py compare <Material1> <Material2> ...")
        print("  python query_examples.py model <ModelType>")
        print("  python query_examples.py stats")
        print("  python query_examples.py search <SearchTerm>")
        print("\nExamples:")
        print("  python query_examples.py property Density")
        print("  python query_examples.py compare Aluminum Copper Nickel")
        print("  python query_examples.py model ElasticModel")
        print("  python query_examples.py stats")
        print("  python query_examples.py search um")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'property' and len(sys.argv) >= 3:
        query_by_property(sys.argv[2])
    elif command == 'compare' and len(sys.argv) >= 4:
        compare_materials(sys.argv[3:])
    elif command == 'model' and len(sys.argv) >= 3:
        find_materials_by_model(sys.argv[2])
    elif command == 'stats':
        get_material_statistics()
    elif command == 'search' and len(sys.argv) >= 3:
        search_materials(sys.argv[2])
    else:
        print("Invalid command or missing arguments!")
        sys.exit(1)
