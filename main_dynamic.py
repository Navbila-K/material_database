"""
Dynamic Material Import System - User-Friendly Interface
Automatically parses and stores ANY XML material structure.

USAGE:
    python main_dynamic.py import xml/MaterialName.xml
    python main_dynamic.py import-all
    python main_dynamic.py reset
    python main_dynamic.py status

FEATURES:
- ✅ Automatically discovers new property categories (Optical, Nuclear, Electrical, etc.)
- ✅ Automatically discovers new model types (QuantumModel, OpticalModel, etc.)
- ✅ No code changes needed for new XML structures
- ✅ Fully backward compatible with existing materials
- ✅ Validates data integrity
"""
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parser.dynamic_xml_parser import parse_material_xml_dynamic
from db.database import DatabaseManager
from db.dynamic_insert import DynamicMaterialInserter
from db.query import MaterialQuerier


def query_material(material_name: str) -> bool:
    """
    Query and display material data from database.
    
    Args:
        material_name: Name of material to query
    
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"\n{'='*70}")
        print(f"QUERYING MATERIAL: {material_name}")
        print('='*70)
        
        # Connect to database
        db = DatabaseManager()
        querier = MaterialQuerier(db)
        
        # Get material data
        material_data = querier.get_material_by_name(material_name, apply_overrides=False)
        
        if not material_data:
            print(f"\n❌ Material '{material_name}' not found in database")
            print(f"{'='*70}\n")
            return False
        
        # Display metadata
        print(f"\n📋 MATERIAL: {material_data['metadata']['name']}")
        print(f"{'='*70}")
        print(f"ID: {material_data['metadata']['id']}")
        if material_data['metadata'].get('version'):
            print(f"Version: {material_data['metadata']['version']}")
        if material_data['metadata'].get('author'):
            print(f"Author: {material_data['metadata']['author']}")
        if material_data['metadata'].get('date'):
            print(f"Date: {material_data['metadata']['date']}")
        
        # Display properties
        if material_data.get('properties'):
            print(f"\n📊 PROPERTIES:")
            print('='*70)
            for category_name, category_data in material_data['properties'].items():
                print(f"\n  [{category_name}]")
                
                if category_name == 'Phase':
                    for key, value in category_data.items():
                        if value:
                            print(f"    {key}: {value}")
                else:
                    for prop_name, prop_data in category_data.items():
                        if isinstance(prop_data, dict) and 'entries' in prop_data:
                            unit_str = f" ({prop_data['unit']})" if prop_data.get('unit') else ""
                            print(f"    {prop_name}{unit_str}:")
                            for entry in prop_data['entries']:
                                ref_str = f" [ref: {entry['ref']}]" if entry.get('ref') else ""
                                print(f"      • {entry['value']}{ref_str}")
        
        # Display models
        if material_data.get('models'):
            print(f"\n🔧 MODELS:")
            print('='*70)
            for model_type, model_data in material_data['models'].items():
                print(f"\n  [{model_type}]")
                _display_model_structure(model_data, indent=4)
        
        print(f"\n{'='*70}\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Error querying material: {e}")
        print(f"{'='*70}\n")
        return False


def _display_model_structure(model_data: dict, indent: int = 0):
    """Recursively display model structure."""
    indent_str = " " * indent
    
    if isinstance(model_data, dict):
        # Handle rows (EOS models)
        if 'rows' in model_data:
            for row in model_data['rows']:
                row_idx = row.get('index', '?')
                print(f"{indent_str}[Row {row_idx}]")
                _display_model_structure(row.get('parameters', {}), indent + 2)
        else:
            # Handle regular nested structure
            for key, value in model_data.items():
                if isinstance(value, list) and value and isinstance(value[0], dict) and 'value' in value[0]:
                    # Parameter with entries
                    print(f"{indent_str}{key}:")
                    for entry in value:
                        unit_str = f" ({entry['unit']})" if entry.get('unit') else ""
                        ref_str = f" [ref: {entry['ref']}]" if entry.get('ref') else ""
                        print(f"{indent_str}  • {entry['value']}{unit_str}{ref_str}")
                elif isinstance(value, dict) and 'value' in value:
                    # Single value parameter
                    unit_str = f" ({value['unit']})" if value.get('unit') else ""
                    ref_str = f" [ref: {value['ref']}]" if value.get('ref') else ""
                    print(f"{indent_str}{key}: {value['value']}{unit_str}{ref_str}")
                elif isinstance(value, dict):
                    # Nested structure
                    print(f"{indent_str}<{key}>")
                    _display_model_structure(value, indent + 2)


def import_material(xml_file: str) -> bool:
    """
    Import a single material using dynamic parser and inserter.
    
    Args:
        xml_file: Path to XML file
    
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"\n{'='*70}")
        print(f"Importing: {Path(xml_file).name}")
        print('='*70)
        
        # 1. Parse XML dynamically
        material_data = parse_material_xml_dynamic(xml_file)
        
        # 2. Connect to database
        db = DatabaseManager()
        inserter = DynamicMaterialInserter(db)
        
        # 3. Insert material
        material_id = inserter.insert_material(material_data)
        
        # 4. Close connection
        inserter.close()
        
        print(f"{'='*70}")
        print(f"✅ SUCCESS: {material_data['metadata']['name']} (ID: {material_id})")
        print(f"{'='*70}\n")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}\n")
        return False


def import_all_materials(xml_dir: str = "xml") -> tuple:
    """
    Import all XML materials from directory.
    
    Args:
        xml_dir: Directory containing XML files
    
    Returns:
        Tuple of (succeeded, failed) counts
    """
    xml_path = Path(xml_dir)
    xml_files = sorted(xml_path.glob("*.xml"))
    
    # Exclude References.xml
    xml_files = [f for f in xml_files if f.name != "References.xml"]
    
    print(f"\n{'='*70}")
    print(f"DYNAMIC IMPORT - Found {len(xml_files)} material files")
    print(f"{'='*70}\n")
    
    succeeded = 0
    failed = 0
    failed_files = []
    
    for xml_file in xml_files:
        if import_material(str(xml_file)):
            succeeded += 1
        else:
            failed += 1
            failed_files.append(xml_file.name)
    
    print(f"\n{'='*70}")
    print(f"IMPORT COMPLETE")
    print(f"{'='*70}")
    print(f"✅ Succeeded: {succeeded}")
    print(f"❌ Failed: {failed}")
    
    if failed_files:
        print(f"\nFailed files:")
        for fname in failed_files:
            print(f"  • {fname}")
    
    print(f"{'='*70}\n")
    
    return succeeded, failed


def reset_database():
    """Reset database schema (drop and recreate all tables)."""
    print(f"\n{'='*70}")
    print("RESETTING DATABASE")
    print(f"{'='*70}\n")
    
    db = DatabaseManager()
    
    confirm = input("⚠️  This will delete ALL data. Continue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Reset cancelled\n")
        return
    
    try:
        db.reset_schema()
        print("✅ Database reset complete\n")
    except Exception as e:
        print(f"❌ Reset failed: {e}\n")


def show_status():
    """Show database statistics."""
    print(f"\n{'='*70}")
    print("DATABASE STATUS")
    print(f"{'='*70}\n")
    
    try:
        db = DatabaseManager()
        conn = db.connect()
        cursor = conn.cursor()
        
        # Count materials
        cursor.execute("SELECT COUNT(*) FROM materials")
        material_count = cursor.fetchone()[0]
        
        # Count property categories
        cursor.execute("SELECT COUNT(DISTINCT category_type) FROM property_categories")
        category_count = cursor.fetchone()[0]
        
        # Count model types
        cursor.execute("SELECT COUNT(DISTINCT model_type) FROM models")
        model_count = cursor.fetchone()[0]
        
        # Get unique property categories
        cursor.execute("""
            SELECT DISTINCT category_type 
            FROM property_categories 
            ORDER BY category_type
        """)
        categories = [row[0] for row in cursor.fetchall()]
        
        # Get unique model types
        cursor.execute("""
            SELECT DISTINCT model_type 
            FROM models 
            ORDER BY model_type
        """)
        models = [row[0] for row in cursor.fetchall()]
        
        print(f"📊 Materials: {material_count}")
        print(f"📊 Unique property categories: {category_count}")
        print(f"📊 Unique model types: {model_count}")
        
        print(f"\n📁 Property Categories:")
        for cat in categories:
            print(f"  • {cat}")
        
        print(f"\n🔧 Model Types:")
        for model in models:
            print(f"  • {model}")
        
        cursor.close()
        conn.close()
        
        print(f"\n{'='*70}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}\n")


def show_help():
    """Show usage information."""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║              DYNAMIC MATERIAL IMPORT SYSTEM                          ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

📖 USAGE:

  Import single material:
    python main_dynamic.py import xml/MaterialName.xml
  
  Import all materials:
    python main_dynamic.py import-all
  
  Query material data:
    python main_dynamic.py query MaterialName
  
  Reset database:
    python main_dynamic.py reset
  
  Show statistics:
    python main_dynamic.py status
  
  Show this help:
    python main_dynamic.py help

✨ FEATURES:

  ✅ Automatically discovers new property categories
     (Optical, Nuclear, Electrical, Magnetic, etc.)
  
  ✅ Automatically discovers new model types
     (QuantumModel, OpticalModel, FluidModel, etc.)
  
  ✅ No code changes needed for new XML structures
  
  ✅ Fully backward compatible with existing materials
  
  ✅ Validates data integrity

📊 EXAMPLES:

  # Import novel material with new properties
  python main_dynamic.py import xml/TEST_NOVEL.xml
  
  # Import standard material (backward compatible)
  python main_dynamic.py import xml/COMP-B.xml
  
  # Query material to see its data
  python main_dynamic.py query "Novel Test Material"
  
  # Query LASL material
  python main_dynamic.py query COMP-B
  
  # Import all materials at once
  python main_dynamic.py import-all
  
  # Check what's in the database
  python main_dynamic.py status

╚══════════════════════════════════════════════════════════════════════╝
""")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "import":
        if len(sys.argv) < 3:
            print("❌ Error: Please specify XML file")
            print("Usage: python main_dynamic.py import xml/MaterialName.xml")
            return
        
        xml_file = sys.argv[2]
        if not os.path.exists(xml_file):
            print(f"❌ Error: File not found: {xml_file}")
            return
        
        import_material(xml_file)
    
    elif command == "import-all":
        import_all_materials()
    
    elif command == "query":
        if len(sys.argv) < 3:
            print("❌ Error: Please specify material name")
            print("Usage: python main_dynamic.py query MaterialName")
            print('       python main_dynamic.py query "Material Name"')
            return
        
        material_name = sys.argv[2]
        query_material(material_name)
    
    elif command == "reset":
        reset_database()
    
    elif command == "status":
        show_status()
    
    elif command == "help" or command == "--help" or command == "-h":
        show_help()
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python main_dynamic.py help' for usage information")


if __name__ == "__main__":
    main()
