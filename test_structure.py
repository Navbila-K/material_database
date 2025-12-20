#!/usr/bin/env python3
"""
Test what structure get_material_by_name actually returns
"""

import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from db.database import DatabaseManager
from db.query import MaterialQuerier

def test_structure():
    """Test the actual structure returned"""
    print("=" * 60)
    print("Testing MaterialQuerier.get_material_by_name() structure")
    print("=" * 60)
    
    try:
        db = DatabaseManager()
        querier = MaterialQuerier(db)
        
        # Get material data
        print("\nFetching Copper...")
        material_data = querier.get_material_by_name("Copper", apply_overrides=False)
        
        if not material_data:
            print("No data returned!")
            return
        
        print("\nTop-level keys:")
        for key in material_data.keys():
            print(f"  - {key}")
        
        # Check metadata
        if 'metadata' in material_data:
            print("\nMetadata:")
            for k, v in material_data['metadata'].items():
                print(f"  {k}: {v}")
        
        # Check properties structure
        if 'properties' in material_data:
            print("\nProperties structure:")
            props = material_data['properties']
            print(f"  Type: {type(props)}")
            print(f"  Keys: {list(props.keys()) if isinstance(props, dict) else 'Not a dict'}")
            
            # Look deeper
            if isinstance(props, dict):
                for category_key in props.keys():
                    category_data = props[category_key]
                    print(f"\n  Category: {category_key}")
                    print(f"    Type: {type(category_data)}")
                    if isinstance(category_data, list):
                        print(f"    Items: {len(category_data)}")
                        if len(category_data) > 0:
                            print(f"    First item: {category_data[0]}")
                    elif isinstance(category_data, dict):
                        print(f"    Keys: {list(category_data.keys())}")
        
        # Show full structure (limited)
        print("\n" + "=" * 60)
        print("Full structure (limited):")
        print(json.dumps(material_data, indent=2, default=str)[:2000])
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_structure()
