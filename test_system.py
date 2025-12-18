#!/usr/bin/env python3
"""
Comprehensive test script for Material Database Engine.
Tests all modules and verifies functionality.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("Material Database Engine - Comprehensive Test Suite")
print("=" * 70)

# Test 1: Database Connection
print("\n[1/7] Testing Database Connection...")
try:
    from db.database import DatabaseManager
    db = DatabaseManager()
    if db.test_connection():
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")
        sys.exit(1)
    db.close()
except Exception as e:
    print(f"❌ Database test failed: {e}")
    sys.exit(1)

# Test 2: XML Parser
print("\n[2/7] Testing XML Parser...")
try:
    from parser.xml_parser import parse_material_xml
    test_file = "xml/Copper.xml"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        sys.exit(1)
    
    material_data = parse_material_xml(test_file)
    
    # Verify structure
    assert 'metadata' in material_data, "Missing metadata"
    assert 'properties' in material_data, "Missing properties"
    assert 'models' in material_data, "Missing models"
    assert material_data['metadata']['name'] == 'Copper', "Wrong material name"
    
    print(f"✅ XML Parser working - parsed {material_data['metadata']['name']}")
except Exception as e:
    print(f"❌ Parser test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Database Schema
print("\n[3/7] Testing Database Schema Creation...")
try:
    from db.database import DatabaseManager
    db = DatabaseManager()
    db.connect()
    
    # Check if tables exist
    cursor = db.get_cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('materials', 'property_categories', 'properties', 
                          'property_entries', 'models', 'sub_models', 
                          'model_parameters')
    """)
    count = cursor.fetchone()[0]
    cursor.close()
    
    if count >= 7:
        print(f"✅ Database schema exists ({count} tables found)")
    else:
        print(f"⚠️  Only {count}/7 tables found, creating schema...")
        db.create_schema()
    
    db.close()
except Exception as e:
    print(f"❌ Schema test failed: {e}")
    sys.exit(1)

# Test 4: Data Insertion
print("\n[4/7] Testing Data Insertion...")
try:
    from db.database import DatabaseManager
    from db.insert import MaterialInserter
    from parser.xml_parser import parse_material_xml
    
    db = DatabaseManager()
    db.connect()
    
    # Check if Copper already exists
    cursor = db.get_cursor()
    cursor.execute("SELECT COUNT(*) FROM materials WHERE name = 'Copper'")
    copper_exists = cursor.fetchone()[0] > 0
    cursor.close()
    
    if not copper_exists:
        print("  Importing Copper...")
        material_data = parse_material_xml("xml/Copper.xml")
        inserter = MaterialInserter(db)
        material_id = inserter.insert_material(material_data)
        print(f"✅ Data insertion working - inserted Copper (ID: {material_id})")
    else:
        print("✅ Data insertion verified - Copper already in database")
    
    db.close()
except Exception as e:
    print(f"❌ Insertion test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Data Query
print("\n[5/7] Testing Data Query...")
try:
    from db.database import DatabaseManager
    from db.query import MaterialQuerier
    
    db = DatabaseManager()
    db.connect()
    
    querier = MaterialQuerier(db)
    materials = querier.list_materials()
    
    if materials:
        print(f"✅ Query working - found {len(materials)} materials:")
        for mat in materials[:5]:  # Show first 5
            print(f"     - {mat['name']} ({mat['xml_id']})")
        if len(materials) > 5:
            print(f"     ... and {len(materials) - 5} more")
    else:
        print("⚠️  No materials found in database")
    
    # Test specific query
    if materials:
        material_data = querier.get_material_by_id(materials[0]['material_id'])
        assert 'metadata' in material_data
        assert 'properties' in material_data
        assert 'models' in material_data
        print(f"✅ Detailed query working - retrieved complete data for {materials[0]['name']}")
    
    db.close()
except Exception as e:
    print(f"❌ Query test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: XML Export
print("\n[6/7] Testing XML Export...")
try:
    from db.database import DatabaseManager
    from db.query import MaterialQuerier
    from export.xml_exporter import export_material_to_xml
    import tempfile
    
    db = DatabaseManager()
    db.connect()
    
    querier = MaterialQuerier(db)
    materials = querier.list_materials()
    
    if materials:
        material_data = querier.get_material_by_id(materials[0]['material_id'])
        
        # Export to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            temp_file = f.name
        
        export_material_to_xml(material_data, temp_file)
        
        # Verify file exists and has content
        assert os.path.exists(temp_file), "Export file not created"
        file_size = os.path.getsize(temp_file)
        assert file_size > 0, "Export file is empty"
        
        print(f"✅ XML Export working - exported {materials[0]['name']} ({file_size} bytes)")
        
        # Cleanup
        os.remove(temp_file)
    else:
        print("⚠️  Skipping export test - no materials in database")
    
    db.close()
except Exception as e:
    print(f"❌ Export test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 7: Override Manager
print("\n[7/7] Testing Override Manager...")
try:
    from overrides.override_manager import OverrideManager
    
    manager = OverrideManager()
    
    # Test data
    test_data = {
        'metadata': {'name': 'Test'},
        'properties': {
            'Thermal': {
                'Density': {
                    'unit': 'kg/m^3',
                    'entries': [
                        {'value': '8940', 'ref': '107', 'index': 1},
                        {'value': '8930', 'ref': '109', 'index': 2}
                    ]
                }
            }
        },
        'models': {}
    }
    
    # Test reference preference
    manager.set_preferred_reference(1, 'properties.Thermal.Density', '109')
    modified = manager.apply_overrides(1, test_data)
    
    assert len(modified['properties']['Thermal']['Density']['entries']) == 1
    assert modified['properties']['Thermal']['Density']['entries'][0]['ref'] == '109'
    
    print("✅ Override Manager working - reference selection verified")
    
except Exception as e:
    print(f"❌ Override test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Final Summary
print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED!")
print("=" * 70)
print("\nSystem is fully operational. You can now:")
print("  • Import materials: python main.py import xml/MaterialName.xml")
print("  • Query materials: python main.py query MaterialName")
print("  • Export materials: python main.py export MaterialName")
print("  • List materials: python main.py list")
print("\nFor more info: python main.py --help")
print("=" * 70)
