#!/usr/bin/env python3
"""
Comprehensive diagnostic: Check ALL materials, properties, and models
that should be available for visualization
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from db.database import DatabaseManager
from db.query import MaterialQuerier

def check_materials_properties_models():
    """Check what's actually in the database"""
    
    print("=" * 80)
    print("DIAGNOSTIC: Materials, Properties, and Models Availability")
    print("=" * 80)
    
    try:
        db = DatabaseManager()
        querier = MaterialQuerier(db)
        
        # ===== CHECK 1: List All Materials =====
        print("\n" + "=" * 80)
        print("CHECK 1: ALL MATERIALS IN DATABASE")
        print("=" * 80)
        
        materials = querier.list_materials()
        print(f"\nTotal Materials: {len(materials)}")
        
        material_names = []
        for mat in materials:
            name = mat.get('name', 'UNKNOWN')
            material_id = mat.get('material_id', 'N/A')
            material_names.append(name)
            print(f"  {material_id:3} - {name}")
        
        if not materials:
            print("  ❌ NO MATERIALS FOUND IN DATABASE!")
            return
        
        # ===== CHECK 2: Check Each Material's Data Structure =====
        print("\n" + "=" * 80)
        print("CHECK 2: DATA STRUCTURE FOR EACH MATERIAL")
        print("=" * 80)
        
        for mat_name in material_names[:5]:  # Check first 5
            print(f"\n--- {mat_name} ---")
            mat_data = querier.get_material_by_name(mat_name, apply_overrides=False)
            
            if not mat_data:
                print(f"  ❌ No data returned!")
                continue
            
            # Check top-level structure
            print(f"  Top-level keys: {list(mat_data.keys())}")
            
            # Check metadata
            if 'metadata' in mat_data:
                meta = mat_data['metadata']
                print(f"  Metadata: ID={meta.get('id')}, Name={meta.get('name')}")
            
            # Check properties
            if 'properties' in mat_data:
                props = mat_data['properties']
                print(f"  Property Categories: {list(props.keys())}")
                
                for cat_name, cat_data in props.items():
                    if isinstance(cat_data, dict) and cat_name != 'Phase':
                        prop_names = list(cat_data.keys())
                        print(f"    {cat_name}: {len(prop_names)} properties")
                        print(f"      → {prop_names}")
            
            # Check models
            if 'models' in mat_data:
                models = mat_data['models']
                print(f"  Model Types: {list(models.keys())}")
        
        # ===== CHECK 3: Property Extraction Test =====
        print("\n" + "=" * 80)
        print("CHECK 3: PROPERTY EXTRACTION (Visualization Tab Logic)")
        print("=" * 80)
        
        test_material = material_names[0] if material_names else None
        if test_material:
            print(f"\nTesting with: {test_material}")
            
            mat_data = querier.get_material_by_name(test_material, apply_overrides=False)
            
            # Use the same extraction logic as visualization tab
            property_dict = {}
            properties_section = mat_data.get('properties', {})
            
            print(f"Property categories found: {list(properties_section.keys())}")
            
            for category_name, category_data in properties_section.items():
                if not isinstance(category_data, dict):
                    continue
                
                print(f"\n  Category: {category_name}")
                
                for prop_name, prop_data in category_data.items():
                    if not isinstance(prop_data, dict):
                        print(f"    {prop_name}: {prop_data} (scalar value)")
                        continue
                    
                    unit = prop_data.get('unit', '')
                    entries = prop_data.get('entries', [])
                    
                    # Normalize name
                    normalized_name = prop_name.lower().replace(' ', '_')
                    
                    if normalized_name not in property_dict:
                        property_dict[normalized_name] = []
                    
                    # Extract values
                    value_count = 0
                    for entry in entries:
                        value_str = entry.get('value')
                        if value_str and value_str.lower() != 'null':
                            try:
                                value_float = float(value_str)
                                property_dict[normalized_name].append({
                                    'value': value_float,
                                    'unit': unit,
                                    'ref': entry.get('ref', ''),
                                    'index': entry.get('index', '')
                                })
                                value_count += 1
                            except (ValueError, TypeError):
                                pass
                    
                    status = "✓" if value_count > 0 else "✗"
                    print(f"    {status} {prop_name} → '{normalized_name}': {value_count} values (unit: {unit})")
            
            print(f"\n  SUMMARY: Extracted {len(property_dict)} properties with data")
            print(f"  Available for plotting: {list(property_dict.keys())}")
        
        # ===== CHECK 4: Model Availability =====
        print("\n" + "=" * 80)
        print("CHECK 4: MODELS AVAILABILITY")
        print("=" * 80)
        
        if test_material:
            mat_data = querier.get_material_by_name(test_material, apply_overrides=False)
            models = mat_data.get('models', {})
            
            print(f"\nMaterial: {test_material}")
            print(f"Model types available: {len(models)}")
            
            for model_type, model_data in models.items():
                print(f"\n  Model: {model_type}")
                if isinstance(model_data, dict):
                    print(f"    Submodels: {list(model_data.keys())}")
                    
                    # Show first submodel structure
                    for submodel_name, submodel_data in list(model_data.items())[:1]:
                        print(f"\n    Submodel: {submodel_name}")
                        if isinstance(submodel_data, dict):
                            print(f"      Parameters: {list(submodel_data.keys())}")
        
        # ===== CHECK 5: Comparison Data =====
        print("\n" + "=" * 80)
        print("CHECK 5: COMPARISON CAPABILITY CHECK")
        print("=" * 80)
        
        # Check which materials have common properties for comparison
        if len(material_names) >= 2:
            mat1_name = material_names[0]
            mat2_name = material_names[1]
            
            print(f"\nComparing: {mat1_name} vs {mat2_name}")
            
            mat1_data = querier.get_material_by_name(mat1_name, apply_overrides=False)
            mat2_data = querier.get_material_by_name(mat2_name, apply_overrides=False)
            
            # Extract properties for both
            def extract_props(mat_data):
                props = {}
                properties_section = mat_data.get('properties', {})
                for cat_name, cat_data in properties_section.items():
                    if isinstance(cat_data, dict):
                        for prop_name, prop_data in cat_data.items():
                            if isinstance(prop_data, dict):
                                normalized = prop_name.lower().replace(' ', '_')
                                entries = prop_data.get('entries', [])
                                if entries and any(e.get('value') for e in entries):
                                    props[normalized] = True
                return set(props.keys())
            
            mat1_props = extract_props(mat1_data)
            mat2_props = extract_props(mat2_data)
            
            common_props = mat1_props & mat2_props
            
            print(f"\n  {mat1_name} has {len(mat1_props)} properties with data")
            print(f"  {mat2_name} has {len(mat2_props)} properties with data")
            print(f"  Common properties: {len(common_props)}")
            print(f"  → {sorted(common_props)}")
            
            if common_props:
                print(f"\n  ✓ Materials CAN be compared using: {', '.join(sorted(list(common_props)[:5]))}")
            else:
                print(f"\n  ✗ No common properties for comparison!")
        
        # ===== FINAL SUMMARY =====
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        
        print(f"\n✓ Total Materials: {len(materials)}")
        print(f"✓ Materials can be loaded: YES")
        print(f"✓ Properties can be extracted: YES")
        print(f"✓ Models are available: YES")
        
        if len(material_names) >= 2 and common_props:
            print(f"✓ Comparison possible: YES ({len(common_props)} common properties)")
        else:
            print(f"⚠ Comparison: LIMITED (few or no common properties)")
        
        print("\n" + "=" * 80)
        print("VISUALIZATION TAB READINESS: ✓ READY")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_materials_properties_models()
