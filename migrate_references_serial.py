#!/usr/bin/env python3
"""
Migration: Fix references.reference_id to use SERIAL auto-increment

Problem: reference_id is INTEGER PRIMARY KEY (not auto-generating)
Solution: Change to SERIAL PRIMARY KEY (auto-generates 1, 2, 3, ...)
"""

import psycopg2
from config import DB_CONFIG

def migrate_references_id():
    """Convert reference_id from INTEGER to SERIAL."""
    
    print("="*60)
    print("MIGRATION: Fix references.reference_id to SERIAL")
    print("="*60)
    
    conn = psycopg2.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        database=DB_CONFIG['database'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )
    
    cursor = conn.cursor()
    
    try:
        # Step 1: Check current max reference_id
        print("\n1. Checking current max reference_id...")
        cursor.execute('SELECT MAX(reference_id) FROM "references"')
        max_id = cursor.fetchone()[0]
        print(f"   Current max reference_id: {max_id if max_id else 'None (table empty)'}")
        
        # Step 2: Create sequence
        print("\n2. Creating sequence for reference_id...")
        start_value = (max_id + 1) if max_id else 1
        
        # Drop sequence if exists
        cursor.execute("DROP SEQUENCE IF EXISTS references_reference_id_seq CASCADE")
        
        # Create new sequence
        cursor.execute(f"""
            CREATE SEQUENCE references_reference_id_seq
            START WITH {start_value}
            INCREMENT BY 1
            NO MINVALUE
            NO MAXVALUE
            CACHE 1
        """)
        print(f"   ✓ Sequence created, starting at {start_value}")
        
        # Step 3: Alter column to use sequence
        print("\n3. Altering reference_id column to use sequence...")
        cursor.execute("""
            ALTER TABLE "references" 
            ALTER COLUMN reference_id 
            SET DEFAULT nextval('references_reference_id_seq')
        """)
        print("   ✓ Column altered to use sequence")
        
        # Step 4: Set sequence ownership
        print("\n4. Setting sequence ownership...")
        cursor.execute("""
            ALTER SEQUENCE references_reference_id_seq 
            OWNED BY "references".reference_id
        """)
        print("   ✓ Sequence ownership set")
        
        # Step 5: Verify setup
        print("\n5. Verifying setup...")
        cursor.execute("""
            SELECT column_name, column_default, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'references' AND column_name = 'reference_id'
        """)
        result = cursor.fetchone()
        print(f"   Column: {result[0]}")
        print(f"   Default: {result[1]}")
        print(f"   Nullable: {result[2]}")
        
        # Commit changes
        conn.commit()
        
        print("\n" + "="*60)
        print("✓ MIGRATION COMPLETE!")
        print("="*60)
        print(f"\nNext reference ID will be: {start_value}")
        print("\nNew references will auto-generate IDs starting from this number.")
        print("\nTest by adding a reference through the GUI - no ID needed!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ MIGRATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        cursor.close()
        conn.close()
    
    return True

if __name__ == "__main__":
    import sys
    success = migrate_references_id()
    sys.exit(0 if success else 1)
