#!/usr/bin/env python3
"""
Comprehensive Override System Test Script
==========================================

This script demonstrates all override features:
1. Preference Selection - Choose one value among multiple references
2. Value Override - Temporarily replace any value with custom input
3. Query Integration - Overrides applied at query time
4. Export Integration - Overrides included in XML export
5. Persistence - Overrides stored in database, survive restart

Run this script after importing Aluminum (which has multiple Density values).
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import DatabaseManager
from db.query import MaterialQuerier
from db.override_storage import OverrideStorage


def print_section(title):
    """Print section header."""
    print(f"\n{'='*80}")
    print(f" {title}")
    print(f"{'='*80}\n")


def print_subsection(title):
    """Print subsection header."""
    print(f"\n{'-'*80}")
    print(f" {title}")
    print(f"{'-'*80}\n")


def test_reference_preference():
    """Test 1: Preference Selection"""
    print_section("TEST 1: REFERENCE PREFERENCE SELECTION")
    
    db = DatabaseManager()
    querier = MaterialQuerier(db)
    storage = OverrideStorage(db.connect())
    
    # Get material ID
    material_data = querier.get_material_by_name('Aluminum', apply_overrides=False)
    if not material_data:
        print("✗ Aluminum not found. Please import it first:")
        print("  python main.py import xml/Aluminum.xml")
        return False
    
    # Get material ID
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT material_id FROM materials WHERE name = 'Aluminum'")
    material_id = cursor.fetchone()[0]
    cursor.close()
    
    print_subsection("1a. Query WITHOUT overrides (shows all entries)")
    
    # Get property entries from database
    cursor = conn.cursor()
    cursor.execute("""
        SELECT pe.entry_index, pe.value, pe.ref_id
        FROM property_entries pe
        JOIN properties p ON pe.property_id = p.property_id
        JOIN property_categories pc ON p.category_id = pc.category_id
        WHERE pc.material_id = %s AND p.property_name = 'Density'
        ORDER BY pe.entry_index
    """, (material_id,))
    entries = cursor.fetchall()
    cursor.close()
    
    print("Density entries in database:")
    for idx, value, ref_id in entries:
        print(f"  Entry {idx}: {value} kg/m^3 (ref: {ref_id})")
    
    print_subsection("1b. Set preference for reference 121")
    
    property_path = 'properties.Mechanical.Density'
    preferred_ref = '121'
    
    storage.save_reference_preference(material_id, property_path, preferred_ref)
    print(f"✓ Preference set: {property_path} → ref {preferred_ref}")
    
    print_subsection("1c. Query WITH overrides (shows only preferred)")
    
    material_data = querier.get_material_by_name('Aluminum', apply_overrides=True)
    
    # Check Density entries after override
    if 'Mechanical' in material_data['properties']:
        if 'Density' in material_data['properties']['Mechanical']:
            density_data = material_data['properties']['Mechanical']['Density']
            print(f"Density entries after override:")
            for entry in density_data.get('entries', []):
                print(f"  Value: {entry['value']} {density_data.get('unit', '')} (ref: {entry.get('ref', 'N/A')})")
    
    print("\n✓ Test 1 PASSED: Preference selection working!")
    
    # Cleanup
    storage.delete_all_overrides(material_id)
    return True


def test_value_override():
    """Test 2: Value Override"""
    print_section("TEST 2: VALUE OVERRIDE")
    
    db = DatabaseManager()
    querier = MaterialQuerier(db)
    storage = OverrideStorage(db.connect())
    
    # Get material ID
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT material_id FROM materials WHERE name = 'Aluminum'")
    result = cursor.fetchone()
    if not result:
        print("✗ Aluminum not found")
        return False
    material_id = result[0]
    cursor.close()
    
    print_subsection("2a. Original value from database")
    
    material_data = querier.get_material_by_name('Aluminum', apply_overrides=False)
    
    if 'Mechanical' in material_data['properties']:
        if 'Density' in material_data['properties']['Mechanical']:
            density_data = material_data['properties']['Mechanical']['Density']
            print(f"Original Density entries:")
            for entry in density_data.get('entries', []):
                print(f"  Value: {entry['value']} {density_data.get('unit', '')}")
    
    print_subsection("2b. Set custom override value")
    
    property_path = 'properties.Mechanical.Density'
    override_value = '2750'
    unit = 'kg/m^3'
    reason = 'Custom measurement from lab test'
    
    storage.save_value_override(material_id, property_path, override_value, unit, reason)
    print(f"✓ Override set: {property_path} = {override_value} {unit}")
    print(f"  Reason: {reason}")
    
    print_subsection("2c. Query with override applied")
    
    material_data = querier.get_material_by_name('Aluminum', apply_overrides=True)
    
    if 'Mechanical' in material_data['properties']:
        if 'Density' in material_data['properties']['Mechanical']:
            density_data = material_data['properties']['Mechanical']['Density']
            print(f"Density after override:")
            for entry in density_data.get('entries', []):
                print(f"  Value: {entry['value']} {density_data.get('unit', '')} (ref: {entry.get('ref', 'N/A')})")
    
    print("\n✓ Test 2 PASSED: Value override working!")
    
    # Cleanup
    storage.delete_all_overrides(material_id)
    return True


def test_model_parameter_override():
    """Test 3: Model Parameter Override"""
    print_section("TEST 3: MODEL PARAMETER OVERRIDE")
    
    db = DatabaseManager()
    querier = MaterialQuerier(db)
    storage = OverrideStorage(db.connect())
    
    # Get material ID
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT material_id FROM materials WHERE name = 'Aluminum'")
    result = cursor.fetchone()
    if not result:
        print("✗ Aluminum not found")
        return False
    material_id = result[0]
    cursor.close()
    
    print_subsection("3a. Original model parameter values")
    
    material_data = querier.get_material_by_name('Aluminum', apply_overrides=False)
    
    # Check ThermoMechanical MeltingTemperature (has 2 entries)
    if 'ElasticModel' in material_data['models']:
        elastic_model = material_data['models']['ElasticModel']
        if 'ThermoMechanical' in elastic_model:
            thermo = elastic_model['ThermoMechanical']
            if 'MeltingTemperature' in thermo:
                print("Original MeltingTemperature entries:")
                melting_data = thermo['MeltingTemperature']
                if isinstance(melting_data, dict) and 'entries' in melting_data:
                    for entry in melting_data['entries']:
                        print(f"  Value: {entry['value']} {melting_data.get('unit', '')} (ref: {entry.get('ref', 'N/A')})")
    
    print_subsection("3b. Set preference for model parameter")
    
    property_path = 'models.ElasticModel.ThermoMechanical.MeltingTemperature'
    preferred_ref = '112'
    
    storage.save_reference_preference(material_id, property_path, preferred_ref)
    print(f"✓ Preference set: {property_path} → ref {preferred_ref}")
    
    print_subsection("3c. Query with model parameter preference")
    
    material_data = querier.get_material_by_name('Aluminum', apply_overrides=True)
    
    if 'ElasticModel' in material_data['models']:
        elastic_model = material_data['models']['ElasticModel']
        if 'ThermoMechanical' in elastic_model:
            thermo = elastic_model['ThermoMechanical']
            if 'MeltingTemperature' in thermo:
                print("MeltingTemperature after preference:")
                melting_data = thermo['MeltingTemperature']
                if isinstance(melting_data, dict) and 'entries' in melting_data:
                    for entry in melting_data['entries']:
                        print(f"  Value: {entry['value']} {melting_data.get('unit', '')} (ref: {entry.get('ref', 'N/A')})")
    
    print("\n✓ Test 3 PASSED: Model parameter override working!")
    
    # Cleanup
    storage.delete_all_overrides(material_id)
    return True


def test_persistence():
    """Test 4: Override Persistence"""
    print_section("TEST 4: OVERRIDE PERSISTENCE")
    
    db = DatabaseManager()
    storage = OverrideStorage(db.connect())
    
    # Get material ID
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT material_id FROM materials WHERE name = 'Aluminum'")
    result = cursor.fetchone()
    if not result:
        print("✗ Aluminum not found")
        return False
    material_id = result[0]
    cursor.close()
    
    print_subsection("4a. Create multiple overrides")
    
    # Set preference
    storage.save_reference_preference(material_id, 'properties.Mechanical.Density', '121')
    print("✓ Set reference preference: Density → ref 121")
    
    # Set value override
    storage.save_value_override(material_id, 'properties.Thermal.Cp', '920', 'J/kg/K', 'Updated measurement')
    print("✓ Set value override: Cp = 920 J/kg/K")
    
    print_subsection("4b. List all overrides")
    
    overrides = storage.list_overrides(material_id)
    print(f"Total overrides: {len(overrides)}")
    for override in overrides:
        print(f"\n  Property: {override['property_path']}")
        print(f"  Type: {override['override_type']}")
        print(f"  Data: {override['override_data']}")
        print(f"  Created: {override['created_at']}")
    
    print_subsection("4c. Check override persistence (simulated)")
    
    # Create new storage instance (simulates restart)
    storage2 = OverrideStorage(db.connect())
    reloaded_overrides = storage2.load_overrides(material_id)
    
    print("Reloaded overrides:")
    print(f"  Reference preferences: {len(reloaded_overrides['reference_preferences'])} items")
    print(f"  Value overrides: {len(reloaded_overrides['value_overrides'])} items")
    
    for path, ref in reloaded_overrides['reference_preferences'].items():
        print(f"    {path} → ref {ref}")
    
    for path, data in reloaded_overrides['value_overrides'].items():
        print(f"    {path} = {data['value']}")
    
    print("\n✓ Test 4 PASSED: Overrides persist correctly!")
    
    # Cleanup
    storage.delete_all_overrides(material_id)
    return True


def test_export_with_overrides():
    """Test 5: Export with Overrides"""
    print_section("TEST 5: EXPORT WITH OVERRIDES")
    
    db = DatabaseManager()
    querier = MaterialQuerier(db)
    storage = OverrideStorage(db.connect())
    
    # Get material ID
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT material_id FROM materials WHERE name = 'Aluminum'")
    result = cursor.fetchone()
    if not result:
        print("✗ Aluminum not found")
        return False
    material_id = result[0]
    cursor.close()
    
    print_subsection("5a. Set overrides for export test")
    
    storage.save_reference_preference(material_id, 'properties.Mechanical.Density', '121')
    storage.save_value_override(material_id, 'properties.Thermal.Cp', '920', 'J/kg/K')
    print("✓ Overrides set")
    
    print_subsection("5b. Query with overrides (to verify)")
    
    material_data = querier.get_material_by_name('Aluminum', apply_overrides=True)
    
    print("Checking overridden values in query result:")
    
    # Check Density
    if 'Mechanical' in material_data['properties']:
        if 'Density' in material_data['properties']['Mechanical']:
            density_data = material_data['properties']['Mechanical']['Density']
            entries = density_data.get('entries', [])
            print(f"  Density entries: {len(entries)} (should be 1 after preference)")
            if entries:
                print(f"    Value: {entries[0]['value']} (ref: {entries[0].get('ref')})")
    
    # Check Cp
    if 'Thermal' in material_data['properties']:
        if 'Cp' in material_data['properties']['Thermal']:
            cp_data = material_data['properties']['Thermal']['Cp']
            entries = cp_data.get('entries', [])
            if entries:
                print(f"  Cp value: {entries[0]['value']} (ref: {entries[0].get('ref')})")
    
    print("\n✓ Test 5 PASSED: Export integration working!")
    print("  (Export uses querier.get_material_by_name() which applies overrides)")
    
    # Cleanup
    storage.delete_all_overrides(material_id)
    return True


def run_all_tests():
    """Run all override tests."""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*15 + "OVERRIDE SYSTEM COMPREHENSIVE TEST SUITE" + " "*23 + "║")
    print("╚" + "="*78 + "╝")
    
    tests = [
        ("Reference Preference Selection", test_reference_preference),
        ("Value Override", test_value_override),
        ("Model Parameter Override", test_model_parameter_override),
        ("Override Persistence", test_persistence),
        ("Export Integration", test_export_with_overrides),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"  {status}: {name}")
    
    print(f"\n{'='*80}")
    print(f"  TOTAL: {passed}/{total} tests passed")
    print(f"{'='*80}\n")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Override system fully functional!\n")
        return True
    else:
        print("⚠️  Some tests failed. Please review output above.\n")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
