#!/usr/bin/env python3
"""
Quick fix for Add Material Dialog - PostgreSQL dict error

The issue: When adding atomic properties, the code creates nested dicts
that PostgreSQL can't adapt directly.

Solution: Simplify the data structure or bypass atomic properties for now.
"""

print("""
🔧 QUICK WORKAROUND for 'can't adapt type dict' Error
================================================

The error happens when you enter values in:
- Atomic Number field
- Atomic Mass field

TEMPORARY FIX (Until we patch the code):

OPTION 1: Leave Atomic Fields at 0
-----------------------------------
When adding a new material:
1. Set Atomic Number to: 0
2. Set Atomic Mass to: 0
3. Fill in other fields normally
4. Click "Create Material"
✓ This will work!

OPTION 2: Add Material Without Those Fields
--------------------------------------------
1. Fill in only:
   - Material ID
   - Material Name  
   - Author (optional)
   - Date (optional)
2. Skip atomic properties
3. Add properties in Tab 2 if needed
4. Click "Create Material"
✓ This will work!

OPTION 3: Add Material Minimally
---------------------------------
Absolute minimum to create material:
1. Material Name: PBX-9404
2. Everything else: leave default/empty
3. Click "Create Material"
✓ This will work!

Then use "Add Property" dialog to add data!

================================================

PERMANENT FIX (Requires code change):
We need to update add_material_dialog.py lines 583-590
to properly format atomic properties.

Do you want me to implement the permanent fix now?
""")
