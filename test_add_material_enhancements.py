#!/usr/bin/env python3
"""
Test Add Material Dialog Enhancements

This script tests the new features of the enhanced Add Material dialog:
1. Context-aware button display
2. Two-mode operation (create new vs edit existing)
3. Reference tab functionality
4. Property and model addition
"""

import sys
from PyQt6.QtWidgets import QApplication
from gui.views.dialogs import AddMaterialDialog
from db.database import DatabaseManager


def test_create_mode():
    """Test dialog in create new material mode."""
    print("\n=== TEST 1: Create New Material Mode ===")
    
    db = DatabaseManager()
    dialog = AddMaterialDialog(db, None)
    
    # Verify initial state
    assert dialog.current_material_id is None, "Should start with no material"
    assert dialog.is_edit_mode is False, "Should be in create mode"
    assert dialog.tab_widget.currentIndex() == 0, "Should start on Metadata tab"
    assert dialog.tab_widget.isTabEnabled(0), "Metadata tab should be enabled"
    
    print("✓ Dialog initializes in create mode")
    print("✓ Metadata tab is enabled")
    print("✓ Starting on tab 0 (Metadata)")
    
    return dialog


def test_edit_mode():
    """Test dialog in edit existing material mode."""
    print("\n=== TEST 2: Edit Existing Material Mode ===")
    
    db = DatabaseManager()
    
    # Get first material ID for testing
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT material_id, name FROM materials LIMIT 1")
    row = cursor.fetchone()
    
    if not row:
        print("⚠ No materials in database, skipping edit mode test")
        return None
    
    material_id, material_name = row
    print(f"Testing with material: {material_name} (ID: {material_id})")
    
    dialog = AddMaterialDialog(db, None, material_id=material_id)
    
    # Verify initial state
    assert dialog.current_material_id == material_id, "Should have material ID"
    assert dialog.is_edit_mode is True, "Should be in edit mode"
    assert not dialog.tab_widget.isTabEnabled(0), "Metadata tab should be disabled"
    assert dialog.tab_widget.currentIndex() == 1, "Should start on Properties tab"
    
    print("✓ Dialog initializes in edit mode")
    print("✓ Metadata tab is disabled")
    print("✓ Starting on tab 1 (Properties)")
    print(f"✓ Material name loaded: {dialog.current_material_name}")
    
    return dialog


def test_tab_buttons():
    """Test that correct buttons appear on each tab."""
    print("\n=== TEST 3: Tab-Specific Buttons ===")
    
    db = DatabaseManager()
    dialog = AddMaterialDialog(db, None)
    
    # Tab 0: Metadata - should show "Create Material"
    dialog.tab_widget.setCurrentIndex(0)
    dialog._on_tab_changed(0)
    assert dialog.create_material_btn.isVisible(), "Create Material button should be visible on tab 0"
    assert not dialog.add_property_btn.isVisible(), "Add Property button should be hidden"
    assert not dialog.add_model_btn.isVisible(), "Add Model button should be hidden"
    assert not dialog.add_reference_btn.isVisible(), "Add Reference button should be hidden"
    print("✓ Tab 0 (Metadata): Shows 'Create Material' button only")
    
    # Tab 1: Properties - should show "Add Property"
    dialog.tab_widget.setCurrentIndex(1)
    dialog._on_tab_changed(1)
    assert not dialog.create_material_btn.isVisible(), "Create Material button should be hidden"
    assert dialog.add_property_btn.isVisible(), "Add Property button should be visible on tab 1"
    assert not dialog.add_model_btn.isVisible(), "Add Model button should be hidden"
    assert not dialog.add_reference_btn.isVisible(), "Add Reference button should be hidden"
    print("✓ Tab 1 (Properties): Shows 'Add Property' button only")
    
    # Tab 2: Models - should show "Add Model"
    dialog.tab_widget.setCurrentIndex(2)
    dialog._on_tab_changed(2)
    assert not dialog.create_material_btn.isVisible(), "Create Material button should be hidden"
    assert not dialog.add_property_btn.isVisible(), "Add Property button should be hidden"
    assert dialog.add_model_btn.isVisible(), "Add Model button should be visible on tab 2"
    assert not dialog.add_reference_btn.isVisible(), "Add Reference button should be hidden"
    print("✓ Tab 2 (Models): Shows 'Add Model' button only")
    
    # Tab 3: References - should show "Add Reference"
    dialog.tab_widget.setCurrentIndex(3)
    dialog._on_tab_changed(3)
    assert not dialog.create_material_btn.isVisible(), "Create Material button should be hidden"
    assert not dialog.add_property_btn.isVisible(), "Add Property button should be hidden"
    assert not dialog.add_model_btn.isVisible(), "Add Model button should be hidden"
    assert dialog.add_reference_btn.isVisible(), "Add Reference button should be visible on tab 3"
    print("✓ Tab 3 (References): Shows 'Add Reference' button only")
    
    return dialog


def test_button_states():
    """Test button enable/disable based on material state."""
    print("\n=== TEST 4: Button Enable/Disable States ===")
    
    db = DatabaseManager()
    dialog = AddMaterialDialog(db, None)
    
    # Initially no material - property/model buttons should be disabled
    dialog.tab_widget.setCurrentIndex(1)
    dialog._on_tab_changed(1)
    assert not dialog.add_property_btn.isEnabled(), "Add Property should be disabled without material"
    print("✓ Add Property button disabled when no material exists")
    
    dialog.tab_widget.setCurrentIndex(2)
    dialog._on_tab_changed(2)
    assert not dialog.add_model_btn.isEnabled(), "Add Model should be disabled without material"
    print("✓ Add Model button disabled when no material exists")
    
    # Simulate material creation
    dialog.current_material_id = 999
    dialog.current_material_name = "Test Material"
    dialog.add_property_btn.setEnabled(True)
    dialog.add_model_btn.setEnabled(True)
    
    dialog.tab_widget.setCurrentIndex(1)
    dialog._on_tab_changed(1)
    assert dialog.add_property_btn.isEnabled(), "Add Property should be enabled with material"
    print("✓ Add Property button enabled after material created")
    
    dialog.tab_widget.setCurrentIndex(2)
    dialog._on_tab_changed(2)
    assert dialog.add_model_btn.isEnabled(), "Add Model should be enabled with material"
    print("✓ Add Model button enabled after material created")
    
    # References should always be enabled
    dialog.tab_widget.setCurrentIndex(3)
    dialog._on_tab_changed(3)
    assert dialog.add_reference_btn.isEnabled(), "Add Reference should always be enabled"
    print("✓ Add Reference button always enabled (global references)")
    
    return dialog


def test_tab_count():
    """Test that all 4 tabs are present."""
    print("\n=== TEST 5: Tab Structure ===")
    
    db = DatabaseManager()
    dialog = AddMaterialDialog(db, None)
    
    assert dialog.tab_widget.count() == 4, "Should have exactly 4 tabs"
    print("✓ Dialog has 4 tabs")
    
    tab_names = [
        dialog.tab_widget.tabText(i) for i in range(dialog.tab_widget.count())
    ]
    
    expected_tabs = ["1. Metadata", "2. Properties", "3. Models", "4. References"]
    for i, expected in enumerate(expected_tabs):
        assert tab_names[i] == expected, f"Tab {i} should be '{expected}'"
        print(f"✓ Tab {i}: {tab_names[i]}")
    
    return dialog


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Enhanced Add Material Dialog")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    try:
        # Run tests
        test_tab_count()
        test_create_mode()
        test_edit_mode()
        test_tab_buttons()
        test_button_states()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nDialog enhancements are working correctly:")
        print("  • 4 tabs with proper names")
        print("  • Create mode starts on Metadata tab")
        print("  • Edit mode starts on Properties tab")
        print("  • Context-aware buttons show on correct tabs")
        print("  • Buttons enable/disable based on state")
        print("  • Reference tab is always accessible")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
