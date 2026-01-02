#!/usr/bin/env python3
"""
Test script for AddPropertyDialog
Tests that the dialog opens without errors
"""

import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from gui.views.dialogs.add_property_dialog import AddPropertyDialog
from db.database import DatabaseManager

def test_add_property_dialog():
    """Test opening the AddPropertyDialog"""
    app = QApplication(sys.argv)
    
    try:
        # Initialize database manager
        db_manager = DatabaseManager()
        
        # Test dialog creation
        print("Creating AddPropertyDialog...")
        dialog = AddPropertyDialog(db_manager=db_manager)
        
        print("✓ Dialog created successfully!")
        print(f"  - Material data loaded: {len(dialog.material_data)} materials")
        print(f"  - Reference data loaded: {len(dialog.reference_data)} references")
        
        # Show the dialog
        print("\nOpening dialog window...")
        result = dialog.exec()
        
        if result:
            print("✓ Dialog accepted (property saved)")
        else:
            print("✓ Dialog cancelled")
            
        return 0
        
    except AttributeError as e:
        print(f"✗ AttributeError: {e}")
        QMessageBox.critical(None, "Error", f"AttributeError: {e}")
        return 1
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        QMessageBox.critical(None, "Error", f"Failed to open dialog: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(test_add_property_dialog())
