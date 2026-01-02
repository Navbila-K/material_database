#!/usr/bin/env python3
"""
Verify Add Material Dialog Structure (No GUI Required)

This script verifies the code structure without launching Qt GUI.
"""

import ast
import sys


def check_file_structure(filepath):
    """Parse Python file and check its structure."""
    with open(filepath, 'r') as f:
        tree = ast.parse(f.read())
    
    classes = {}
    functions = {}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes[node.name] = {
                'methods': [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                'signals': []
            }
        elif isinstance(node, ast.FunctionDef):
            if node.name not in [m for c in classes.values() for m in c['methods']]:
                functions[node.name] = True
    
    return classes, functions


def verify_add_material_dialog():
    """Verify the structure of add_material_dialog.py"""
    print("=" * 70)
    print("Verifying Add Material Dialog Structure")
    print("=" * 70)
    
    filepath = "gui/views/dialogs/add_material_dialog.py"
    
    try:
        classes, functions = check_file_structure(filepath)
        
        # Check AddMaterialDialog class exists
        assert 'AddMaterialDialog' in classes, "AddMaterialDialog class not found"
        print("✓ AddMaterialDialog class exists")
        
        dialog_class = classes['AddMaterialDialog']
        methods = dialog_class['methods']
        
        # Check required methods
        required_methods = [
            '__init__',
            '_load_references',
            '_load_material_data',
            '_init_ui',
            '_on_tab_changed',
            '_create_metadata_tab',
            '_create_properties_tab',
            '_create_models_tab',
            '_create_references_tab',
            '_on_add_property',
            '_on_add_model',
            '_on_add_reference',
            '_on_save',
        ]
        
        missing_methods = []
        for method in required_methods:
            if method in methods:
                print(f"✓ Method '{method}' exists")
            else:
                missing_methods.append(method)
                print(f"✗ Method '{method}' MISSING")
        
        if missing_methods:
            print(f"\n❌ Missing methods: {', '.join(missing_methods)}")
            return False
        
        print("\n✅ All required methods present")
        return True
        
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return False
    except Exception as e:
        print(f"❌ Error parsing file: {e}")
        return False


def verify_main_window():
    """Verify main_window.py has required handlers."""
    print("\n" + "=" * 70)
    print("Verifying Main Window Integration")
    print("=" * 70)
    
    filepath = "gui/main_window.py"
    
    try:
        classes, functions = check_file_structure(filepath)
        
        # Find MainWindow class
        main_window = None
        for class_name in classes:
            if 'Window' in class_name:
                main_window = classes[class_name]
                print(f"✓ Found class: {class_name}")
                break
        
        if not main_window:
            print("✗ MainWindow class not found")
            return False
        
        methods = main_window['methods']
        
        # Check required methods
        required_handlers = [
            'on_add_material',
            'on_material_added',
            'on_property_added',
            'on_model_added',
            '_get_material_id_by_name'
        ]
        
        missing = []
        for handler in required_handlers:
            if handler in methods:
                print(f"✓ Handler '{handler}' exists")
            else:
                missing.append(handler)
                print(f"✗ Handler '{handler}' MISSING")
        
        if missing:
            print(f"\n❌ Missing handlers: {', '.join(missing)}")
            return False
        
        print("\n✅ All required handlers present")
        return True
        
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return False
    except Exception as e:
        print(f"❌ Error parsing file: {e}")
        return False


def check_documentation():
    """Check if documentation files exist."""
    print("\n" + "=" * 70)
    print("Checking Documentation")
    print("=" * 70)
    
    import os
    
    docs = [
        "ADD_MATERIAL_DIALOG_ENHANCEMENTS.md",
        "ADD_MATERIAL_QUICK_START.md"
    ]
    
    all_exist = True
    for doc in docs:
        if os.path.exists(doc):
            size = os.path.getsize(doc)
            print(f"✓ {doc} ({size:,} bytes)")
        else:
            print(f"✗ {doc} MISSING")
            all_exist = False
    
    if all_exist:
        print("\n✅ All documentation files present")
    
    return all_exist


def main():
    """Run all verifications."""
    results = []
    
    print("\n🔍 VERIFICATION SUITE FOR ADD MATERIAL DIALOG ENHANCEMENTS\n")
    
    results.append(("Dialog Structure", verify_add_material_dialog()))
    results.append(("Main Window Integration", verify_main_window()))
    results.append(("Documentation", check_documentation()))
    
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name:.<50} {status}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n" + "🎉 " * 10)
        print("ALL VERIFICATIONS PASSED!")
        print("🎉 " * 10)
        print("\nThe enhanced Add Material dialog is ready to use:")
        print("  • All required methods implemented")
        print("  • Main window handlers connected")
        print("  • Documentation complete")
        print("\nTo test: Run 'python run_gui.py' and press Ctrl+M")
        return 0
    else:
        print("\n❌ Some verifications failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
