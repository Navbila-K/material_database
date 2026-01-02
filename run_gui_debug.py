#!/usr/bin/env python3
"""
Debug script to check if Data menu is created in GUI
Run this instead of run_gui.py to see debug output
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("DEBUG: Starting GUI with menu debugging...")
print("=" * 70)

from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

app = QApplication(sys.argv)

print("\n1. Creating MainWindow...")
window = MainWindow()

print("\n2. Checking menu bar...")
menubar = window.menuBar()
menus = []
for action in menubar.actions():
    menu_text = action.text()
    menus.append(menu_text)
    print(f"   Found menu: '{menu_text}'")

print(f"\n3. Total menus found: {len(menus)}")
print(f"   Menu list: {menus}")

if "&Data" in menus:
    print("\n✅ SUCCESS: Data menu IS present!")
    print("\n4. Checking Data menu items...")
    for action in menubar.actions():
        if action.text() == "&Data":
            data_menu = action.menu()
            print(f"   Data menu has {len(data_menu.actions())} items:")
            for item in data_menu.actions():
                if not item.isSeparator():
                    shortcut = item.shortcut().toString()
                    print(f"      - {item.text()} ({shortcut})")
else:
    print("\n❌ ERROR: Data menu NOT found!")
    print("   This is a problem - the menu should be there.")

print("\n" + "=" * 70)
print("Opening GUI now...")
print("Try pressing Ctrl+M to open Add Material dialog")
print("=" * 70 + "\n")

window.show()
sys.exit(app.exec())
