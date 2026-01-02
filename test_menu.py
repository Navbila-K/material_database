"""
Quick test to verify Data menu exists in GUI
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("Testing GUI Menu Structure...")
print("="*70)

from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

app = QApplication(sys.argv)
window = MainWindow()

# Get all menus
menubar = window.menuBar()
menus = []
for action in menubar.actions():
    menu_text = action.text()
    menus.append(menu_text)
    print(f"✓ Menu: {menu_text}")

print("\n" + "="*70)

if "&Data" in menus:
    print("✅ SUCCESS: Data menu exists!")
    print("\nGetting Data menu actions...")
    
    # Find Data menu
    for action in menubar.actions():
        if action.text() == "&Data":
            data_menu = action.menu()
            print(f"\nData menu items:")
            for item_action in data_menu.actions():
                if item_action.isSeparator():
                    print("  ─────────")
                else:
                    shortcut = item_action.shortcut().toString() if item_action.shortcut() else "None"
                    print(f"  • {item_action.text()} (Shortcut: {shortcut})")
            break
else:
    print("❌ FAILED: Data menu NOT found!")
    print(f"Available menus: {menus}")

print("="*70)
print("\nTo see the GUI with Data menu:")
print("  python run_gui.py")
print("\nThen click: Data → Add Material / Add Property / Add Reference")
