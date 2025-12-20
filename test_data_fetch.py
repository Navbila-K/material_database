#!/usr/bin/env python3
"""
Diagnostic script to test if data is being fetched correctly
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from db.database import DatabaseManager
from db.query import MaterialQuerier

def test_data_fetch():
    """Test if we can fetch material data"""
    print("=" * 60)
    print("DIAGNOSTIC: Testing Material Data Fetch")
    print("=" * 60)
    
    try:
        # Connect to database
        print("\n1. Connecting to database...")
        db = DatabaseManager()
        querier = MaterialQuerier(db)
        print("   ✓ Connected successfully")
        
        # Get Copper data
        print("\n2. Fetching Copper material data...")
        material_data = querier.get_material_by_name("Copper", apply_overrides=True)
        
        if not material_data:
            print("   ✗ No data returned for Copper!")
            return
        
        print(f"   ✓ Material data retrieved")
        print(f"   Material ID: {material_data.get('id')}")
        print(f"   Material Name: {material_data.get('name')}")
        
        # Check thermal properties
        print("\n3. Checking thermal properties...")
        thermal_props = material_data.get('thermal_properties', [])
        print(f"   Found {len(thermal_props)} thermal properties")
        
        for prop in thermal_props[:5]:  # Show first 5
            prop_name = prop.get('name', 'unknown')
            if 'value' in prop:
                print(f"   - {prop_name}: {prop['value']} {prop.get('unit', '')}")
            elif 'table' in prop:
                print(f"   - {prop_name}: TABLE with {len(prop['table'])} rows")
        
        # Check if density exists
        print("\n4. Looking for 'density' property...")
        found_density = False
        
        categories = ['thermal_properties', 'mechanical_properties', 
                     'electrical_properties', 'optical_properties', 'eos_properties']
        
        for category in categories:
            if category in material_data:
                for prop in material_data[category]:
                    if prop.get('name') == 'density':
                        found_density = True
                        print(f"   ✓ Found density in {category}")
                        if 'value' in prop:
                            print(f"     Value: {prop['value']} {prop.get('unit', '')}")
                        elif 'table' in prop:
                            print(f"     Table with {len(prop['table'])} rows")
                            # Show first few values
                            for i, row in enumerate(prop['table'][:3]):
                                print(f"       Row {i}: {row}")
        
        if not found_density:
            print("   ✗ Density property NOT FOUND")
            print("\n5. All available properties:")
            for category in categories:
                if category in material_data:
                    props = [p.get('name', 'unknown') for p in material_data[category]]
                    print(f"   {category}: {props}")
        
        # Test the visualization tab's data fetch logic
        print("\n6. Testing visualization tab data extraction logic...")
        property_dict = {}
        
        for category in categories:
            if category in material_data:
                for prop in material_data[category]:
                    prop_name = prop.get('name', '')
                    
                    # Handle scalar values
                    if 'value' in prop:
                        if prop_name not in property_dict:
                            property_dict[prop_name] = []
                        property_dict[prop_name].append({
                            'value': float(prop['value']),
                            'unit': prop.get('unit', ''),
                            'ref': prop.get('reference_id', '')
                        })
                    
                    # Handle table values
                    elif 'table' in prop:
                        if prop_name not in property_dict:
                            property_dict[prop_name] = []
                        # Extract Y values from table
                        for row in prop['table'][:20]:
                            if len(row) >= 2:
                                try:
                                    property_dict[prop_name].append({
                                        'value': float(row[1]),
                                        'unit': prop.get('unit', ''),
                                        'ref': prop.get('reference_id', '')
                                    })
                                except (ValueError, IndexError):
                                    pass
        
        print(f"   Extracted {len(property_dict)} properties")
        print(f"   Properties: {list(property_dict.keys())}")
        
        if 'density' in property_dict:
            print(f"\n   ✓ Density extracted: {len(property_dict['density'])} data points")
            print(f"     First value: {property_dict['density'][0]['value']}")
        else:
            print(f"\n   ✗ Density NOT in extracted properties")
        
        print("\n" + "=" * 60)
        print("DIAGNOSTIC COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_data_fetch()
