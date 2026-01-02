"""
Test GUI Integration - Add Reference Dialog

Quick test to verify:
1. GUI launches without errors
2. Data menu appears
3. Add Reference dialog opens
4. Reference can be added successfully
5. Auto-refresh works

Run this to test TODO #4.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("="*70)
print("TESTING GUI INTEGRATION - Add Reference Dialog")
print("="*70)

print("\n1. Testing imports...")
try:
    from PyQt6.QtWidgets import QApplication
    from gui.main_window import MainWindow
    from gui.views.dialogs import AddReferenceDialog
    print("   ✓ All imports successful")
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    sys.exit(1)

print("\n2. Creating QApplication...")
app = QApplication(sys.argv)
print("   ✓ QApplication created")

print("\n3. Testing database connection...")
try:
    from db.database import DatabaseManager
    db = DatabaseManager()
    conn = db.connect()
    print("   ✓ Database connected")
except Exception as e:
    print(f"   ✗ Database connection failed: {e}")
    sys.exit(1)

print("\n4. Creating main window...")
try:
    window = MainWindow()
    print("   ✓ Main window created")
except Exception as e:
    print(f"   ✗ Main window creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n5. Checking Data menu...")
menubar = window.menuBar()
menus = [menubar.actions()[i].text() for i in range(menubar.actions().__len__())]
print(f"   Available menus: {menus}")
if "&Data" in menus:
    print("   ✓ Data menu exists")
else:
    print("   ✗ Data menu not found")

print("\n6. Showing main window...")
window.show()
print("   ✓ Main window displayed")

print("\n" + "="*70)
print("GUI TEST COMPLETE")
print("="*70)
print("\nManual Test Steps:")
print("1. Check that 'Data' menu appears in menu bar")
print("2. Click Data → Add Reference")
print("3. Fill in reference details:")
print("   - Reference ID: (auto-filled)")
print("   - Type: Article")
print("   - Author: Test Author")
print("   - Title: Test Reference")
print("4. Click Save")
print("5. Verify success message appears")
print("6. Check status bar shows: '✓ Reference X added successfully'")
print("\nClose the window when done testing.")
print("="*70)

# Run application
sys.exit(app.exec())
