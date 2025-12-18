#!/usr/bin/env python3
"""
Verification script to query all materials and confirm complete data retrieval.
"""
import sys
from db.database import DatabaseManager
from db.query import MaterialQuerier
from config import DB_CONFIG

def verify_material(querier, material_name):
    """Verify a single material has complete data."""
    print(f"\n{'='*80}")
    print(f"Verifying: {material_name}")
    print(f"{'='*80}")
    
    material_data = querier.get_material_by_name(material_name)
    
    if not material_data:
        print(f"❌ FAILED: Material '{material_name}' not found!")
        return False
    
    # Check metadata
    metadata = material_data.get('metadata', {})
    print(f"✓ Metadata: ID={metadata.get('id')}, Version={metadata.get('version')}")
    
    # Check properties
    properties = material_data.get('properties', {})
    prop_count = sum(len(props) for props in properties.values())
    print(f"✓ Properties: {len(properties)} categories, {prop_count} total properties")
    
    # Check models
    models = material_data.get('models', {})
    print(f"✓ Models: {list(models.keys())}")
    
    # Count entries
    total_entries = 0
    for category, props in properties.items():
        if category == 'Phase':
            continue
        for prop_name, prop_data in props.items():
            entries = prop_data.get('entries', [])
            total_entries += len(entries)
    
    print(f"✓ Total property entries: {total_entries}")
    
    return True

def main():
    """Verify all materials in database."""
    print(f"\n{'='*80}")
    print("MATERIAL DATABASE VERIFICATION")
    print(f"{'='*80}")
    
    db = DatabaseManager()
    db.connect()
    
    querier = MaterialQuerier(db)
    
    # Get all materials
    materials = querier.list_materials()
    print(f"\nTotal materials in database: {len(materials)}")
    
    # Verify each material
    results = {}
    for material in materials:
        name = material['name']
        success = verify_material(querier, name)
        results[name] = success
    
    # Summary
    print(f"\n{'='*80}")
    print("VERIFICATION SUMMARY")
    print(f"{'='*80}")
    
    passed = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)
    
    print(f"\n✓ Passed: {passed}/{len(results)}")
    if failed > 0:
        print(f"❌ Failed: {failed}/{len(results)}")
        print("\nFailed materials:")
        for name, success in results.items():
            if not success:
                print(f"  - {name}")
    else:
        print("✅ ALL MATERIALS VERIFIED SUCCESSFULLY!")
    
    querier.conn.close()
    print(f"\n{'='*80}\n")
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
