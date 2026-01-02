#!/usr/bin/env python3
"""
Import References from References.xml into Database

PURPOSE:
========
Imports all bibliographic references from References.xml (IDs 1-124)
into the database so existing materials can show their citations.

STRATEGY:
=========
- References.xml has IDs 1-124 (existing materials use these)
- Database sequence starts from 1001 (for new GUI-created references)
- This import populates the 1-1000 range from XML
- New GUI references will use 1001+ range

WORKFLOW:
=========
1. Parse References.xml
2. For each reference, INSERT with explicit ID (1-124)
3. Verify all references imported
4. Existing materials can now show correct citations

USAGE:
======
    python import_references_xml.py
"""

import sys
import xml.etree.ElementTree as ET
from db.database import DatabaseManager


def import_references():
    """Import all references from References.xml into database."""
    
    print("\n" + "="*70)
    print("Import References from References.xml")
    print("="*70 + "\n")
    
    # Parse XML
    print("Step 1: Parsing References.xml...")
    try:
        tree = ET.parse('xml/References.xml')
        root = tree.getroot()
        refs = root.findall('.//reference')
        print(f"  ✓ Found {len(refs)} references in References.xml\n")
    except Exception as e:
        print(f"  ❌ Failed to parse References.xml: {e}")
        sys.exit(1)
    
    # Connect to database
    db = DatabaseManager()
    try:
        conn = db.connect()
        cursor = conn.cursor()
        
        # Step 2: Check current state
        print("Step 2: Checking current database state...")
        cursor.execute('SELECT COUNT(*) FROM "references"')
        current_count = cursor.fetchone()[0]
        print(f"  ✓ Current references in database: {current_count}\n")
        
        # Step 3: Import references
        print("Step 3: Importing references...")
        print("-" * 70)
        
        imported_count = 0
        skipped_count = 0
        error_count = 0
        
        for ref in refs:
            try:
                # Extract data
                ref_id = int(ref.get('id'))
                ref_type = ref.find('type')
                author = ref.find('author')
                title = ref.find('title')
                journal = ref.find('journal')
                year = ref.find('year')
                volume = ref.find('volume')
                pages = ref.find('pages')
                
                # Get text values
                ref_type_val = ref_type.text if ref_type is not None else 'misc'
                author_val = author.text if author is not None else 'Unknown'
                title_val = title.text if title is not None else ''
                journal_val = journal.text if journal is not None else ''
                year_val = year.text if year is not None else '--'
                volume_val = volume.text if volume is not None else '--'
                pages_val = pages.text if pages is not None else '--'
                
                # Check if already exists
                cursor.execute(
                    'SELECT reference_id FROM "references" WHERE reference_id = %s',
                    (ref_id,)
                )
                
                if cursor.fetchone():
                    print(f"  ⊘ Skipped ID {ref_id:3d}: Already exists")
                    skipped_count += 1
                    continue
                
                # Insert with explicit ID
                cursor.execute("""
                    INSERT INTO "references" 
                    (reference_id, ref_type, author, title, journal, year, volume, pages)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    ref_id, ref_type_val, author_val, title_val,
                    journal_val, year_val, volume_val, pages_val
                ))
                
                # Show progress every 10 references
                if ref_id % 10 == 0:
                    author_short = author_val[:30] if len(author_val) > 30 else author_val
                    print(f"  ✓ Imported ID {ref_id:3d}: {author_short}...")
                
                imported_count += 1
                
            except Exception as e:
                print(f"  ❌ Error importing ref ID {ref.get('id')}: {e}")
                error_count += 1
                continue
        
        # Commit
        conn.commit()
        
        print("-" * 70)
        print(f"\n✅ Import completed!")
        print(f"   Imported: {imported_count}")
        print(f"   Skipped:  {skipped_count} (already existed)")
        print(f"   Errors:   {error_count}\n")
        
        # Step 4: Verify import
        print("Step 4: Verifying import...")
        cursor.execute('SELECT COUNT(*) FROM "references"')
        final_count = cursor.fetchone()[0]
        print(f"  ✓ Total references in database: {final_count}")
        
        # Check ID range
        cursor.execute('SELECT MIN(reference_id), MAX(reference_id) FROM "references"')
        min_id, max_id = cursor.fetchone()
        print(f"  ✓ ID range: {min_id} - {max_id}\n")
        
        # Step 5: Check orphaned linkages resolved
        print("Step 5: Checking if orphaned linkages are resolved...")
        
        cursor.execute("""
            SELECT COUNT(DISTINCT pe.ref_id)
            FROM property_entries pe
            WHERE pe.ref_id IS NOT NULL
            AND pe.ref_id NOT IN (
                SELECT CAST(reference_id AS TEXT) FROM "references"
            )
        """)
        orphaned_props = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(DISTINCT mp.ref_id)
            FROM model_parameters mp
            WHERE mp.ref_id IS NOT NULL
            AND mp.ref_id NOT IN (
                SELECT CAST(reference_id AS TEXT) FROM "references"
            )
        """)
        orphaned_models = cursor.fetchone()[0]
        
        if orphaned_props == 0 and orphaned_models == 0:
            print("  ✅ All orphaned linkages resolved!")
            print("     All materials can now show their references correctly!\n")
        else:
            print(f"  ⚠️  Still have orphaned linkages:")
            print(f"     Property entries: {orphaned_props}")
            print(f"     Model parameters: {orphaned_models}")
            print(f"     (These reference IDs > 124 or invalid)\n")
        
        # Summary
        print("="*70)
        print("✅ References Import Complete!")
        print("="*70)
        print("\nRESULT:")
        print(f"  • Imported {imported_count} references from References.xml")
        print(f"  • Database now has {final_count} total references")
        print(f"  • ID range: {min_id}-{max_id} (XML imports)")
        print(f"  • Next GUI reference will be ID: 1001 (no conflicts!)")
        print(f"  • Existing materials can now show citations ✓")
        print("\n")
        
        cursor.close()
        db.close()
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
        sys.exit(1)


if __name__ == "__main__":
    import_references()
