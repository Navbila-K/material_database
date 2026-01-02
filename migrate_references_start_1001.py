#!/usr/bin/env python3
"""
Migration Script: Set Reference ID Auto-Increment to Start from 1001

PURPOSE:
========
Prevents conflicts between:
- XML-imported references (IDs 1-1000)
- GUI-created references (IDs 1001+)

ISSUE ADDRESSED:
================
When references are created via GUI, they auto-increment from 1, 2, 3...
If materials were imported from XML with ref="3" pointing to "Wescott, B.L.",
but the database only has 3 references (not imported from XML), then creating
a NEW reference gets ID=3, causing it to INCORRECTLY appear as "Used by" those
materials that reference the OLD ref="3".

SOLUTION:
=========
1. Set reference_id sequence to start from 1001
2. New GUI-created references will be 1001, 1002, 1003...
3. XML references (when imported) will use IDs 1-1000
4. No conflicts, no false "Used by" linkages!

SAFETY:
=======
- Checks current max reference_id before migrating
- Only sets sequence if current max < 1001
- Does NOT modify existing reference IDs
- Does NOT break existing linkages

USAGE:
======
    python migrate_references_start_1001.py
"""

import sys
from db.database import DatabaseManager


def migrate_reference_sequence():
    """Set reference_id sequence to start from 1001."""
    
    print("\n" + "="*70)
    print("Reference ID Auto-Increment Migration")
    print("Setting sequence to start from 1001 (avoiding XML conflicts)")
    print("="*70 + "\n")
    
    # Connect to database
    db = DatabaseManager()
    try:
        conn = db.connect()
        cursor = conn.cursor()
        
        # Step 1: Check current state
        print("Step 1: Checking current reference_id state...")
        cursor.execute('SELECT MAX(reference_id) FROM "references"')
        max_id = cursor.fetchone()[0]
        max_id = max_id if max_id is not None else 0
        print(f"  ✓ Current max reference_id: {max_id}")
        
        cursor.execute('SELECT COUNT(*) FROM "references"')
        total_refs = cursor.fetchone()[0]
        print(f"  ✓ Total references: {total_refs}")
        
        # Step 2: Check if migration needed
        if max_id >= 1001:
            print(f"\n⚠️  Migration not needed!")
            print(f"   Max reference_id ({max_id}) is already >= 1001")
            cursor.close()
            db.close()
            return
        
        # Step 3: Set sequence to start from 1001
        print("\nStep 2: Setting sequence start value to 1001...")
        
        # Check if sequence exists
        cursor.execute("""
            SELECT sequence_name 
            FROM information_schema.sequences 
            WHERE sequence_name = 'references_reference_id_seq'
        """)
        
        if cursor.fetchone():
            # Sequence exists, set it to 1001
            cursor.execute("""
                SELECT setval('references_reference_id_seq', 1001, false)
            """)
            # false = next value will be 1001 (not 1002)
            print("  ✓ Sequence set to start from 1001")
        else:
            print("  ⚠️  Sequence not found. Creating new sequence...")
            cursor.execute("""
                CREATE SEQUENCE IF NOT EXISTS references_reference_id_seq START WITH 1001;
            """)
            cursor.execute("""
                ALTER TABLE "references" 
                ALTER COLUMN reference_id 
                SET DEFAULT nextval('references_reference_id_seq');
            """)
            print("  ✓ New sequence created starting from 1001")
        
        # Step 4: Verify the change
        print("\nStep 3: Verifying sequence configuration...")
        cursor.execute("""
            SELECT last_value, is_called 
            FROM references_reference_id_seq
        """)
        last_value, is_called = cursor.fetchone()
        next_value = last_value + 1 if is_called else last_value
        print(f"  ✓ Next reference_id will be: {next_value}")
        
        # Step 5: Check for orphaned references
        print("\nStep 4: Checking for orphaned reference linkages...")
        
        # Check property_entries
        cursor.execute("""
            SELECT COUNT(DISTINCT pe.ref_id)
            FROM property_entries pe
            WHERE pe.ref_id IS NOT NULL
            AND pe.ref_id NOT IN (
                SELECT CAST(reference_id AS TEXT) FROM "references"
            )
        """)
        orphaned_props = cursor.fetchone()[0]
        
        # Check model_parameters
        cursor.execute("""
            SELECT COUNT(DISTINCT mp.ref_id)
            FROM model_parameters mp
            WHERE mp.ref_id IS NOT NULL
            AND mp.ref_id NOT IN (
                SELECT CAST(reference_id AS TEXT) FROM "references"
            )
        """)
        orphaned_models = cursor.fetchone()[0]
        
        if orphaned_props > 0 or orphaned_models > 0:
            print(f"  ⚠️  Found orphaned reference linkages:")
            print(f"     - Property entries: {orphaned_props} distinct ref_id(s)")
            print(f"     - Model parameters: {orphaned_models} distinct ref_id(s)")
            print(f"\n  💡 These are from XML imports where references weren't imported.")
            print(f"     They will show as 'Used by' materials but reference doesn't exist.")
            print(f"     Recommendation: Import References.xml to populate missing references.")
        else:
            print("  ✓ No orphaned reference linkages found")
        
        # Commit changes
        conn.commit()
        print("\n" + "="*70)
        print("✅ Migration completed successfully!")
        print("="*70)
        print("\nRESULT:")
        print(f"  • Next GUI-created reference will have ID: {next_value}")
        print(f"  • XML-imported references can use IDs: 1-1000")
        print(f"  • No more conflicts between GUI and XML references!")
        print("\n")
        
        cursor.close()
        db.close()
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
        sys.exit(1)


if __name__ == "__main__":
    migrate_reference_sequence()
