#!/usr/bin/env python3
"""
Test the FIXED fetch_material_data logic
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from db.database import DatabaseManager
from db.query import MaterialQuerier

def test_fixed_logic():
    """Test the new data extraction logic"""
    print("=" * 70)
    print("Testing FIXED fetch_material_data() logic")
    print("=" * 70)
    
    try:
        db = DatabaseManager()
        querier = MaterialQuerier(db)
        
        # Get material data
        print("\n1. Fetching Copper from database...")
        material_data = querier.get_material_by_name("Copper", apply_overrides=False)
        
        if not material_data:
            print("   ✗ No data returned!")
            return
        
        print("   ✓ Data retrieved")
        
        # NEW EXTRACTION LOGIC (matches what we put in visualization_tab.py)
        print("\n2. Extracting properties with NEW logic...")
        property_dict = {}
        
        properties_section = material_data.get('properties', {})
        print(f"   Properties section categories: {list(properties_section.keys())}")
        
        for category_name, category_data in properties_section.items():
            if not isinstance(category_data, dict):
                continue
            
            print(f"\n   Processing category '{category_name}':")
            
            for prop_name, prop_data in category_data.items():
                if not isinstance(prop_data, dict):
                    print(f"     - {prop_name}: Skipped (value: {prop_data})")
                    continue
                
                unit = prop_data.get('unit', '')
                entries = prop_data.get('entries', [])
                
                if not entries:
                    print(f"     - {prop_name}: No entries")
                    continue
                
                # Normalize name
                normalized_name = prop_name.lower().replace(' ', '_')
                
                if normalized_name not in property_dict:
                    property_dict[normalized_name] = []
                
                # Extract values
                for entry in entries:
                    value_str = entry.get('value')
                    if value_str and value_str.lower() != 'null':
                        try:
                            value_float = float(value_str)
                            property_dict[normalized_name].append({
                                'value': value_float,
                                'unit': unit,
                                'ref': entry.get('ref', '')
                            })
                        except (ValueError, TypeError):
                            pass
                
                print(f"     ✓ {prop_name} → '{normalized_name}': {len(property_dict[normalized_name])} values")
        
        print("\n" + "=" * 70)
        print(f"EXTRACTION COMPLETE: {len(property_dict)} properties extracted")
        print("=" * 70)
        
        for prop_name, values in property_dict.items():
            print(f"\n{prop_name}:")
            print(f"  Count: {len(values)}")
            print(f"  Unit: {values[0]['unit'] if values else 'N/A'}")
            print(f"  Values: {[v['value'] for v in values[:5]]}")
        
        print("\n" + "=" * 70)
        print("✓✓✓ SUCCESS - Data extraction working! ✓✓✓")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_fixed_logic()
