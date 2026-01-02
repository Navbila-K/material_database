#!/usr/bin/env python3
"""
Run database migration to add 10-category structure support.

This script:
1. Connects to the database
2. Executes the migration SQL
3. Verifies the migration was successful
4. Shows summary of categories created

Usage:
    python run_migration.py
"""

import sys
from db.database import DatabaseManager
from db.migration_10_categories import get_migration_sql, get_rollback_sql


def run_migration():
    """Execute the database migration."""
    print("=" * 60)
    print("DATABASE MIGRATION: 10-Category Structure")
    print("=" * 60)
    
    db = DatabaseManager()
    
    try:
        # Connect to database
        print("\n[1/5] Connecting to database...")
        conn = db.connect()
        cursor = conn.cursor()
        print("✓ Connected successfully")
        
        # Execute migration
        print("\n[2/5] Executing migration SQL...")
        migration_sql = get_migration_sql()
        cursor.execute(migration_sql)
        conn.commit()
        print("✓ Migration executed successfully")
        
        # Verify categories were created
        print("\n[3/5] Verifying categories...")
        cursor.execute("""
            SELECT category_name, display_order, description 
            FROM category_master 
            ORDER BY display_order
        """)
        categories = cursor.fetchall()
        
        if len(categories) == 10:
            print(f"✓ All 10 categories created successfully")
        else:
            print(f"⚠ Warning: Expected 10 categories, found {len(categories)}")
        
        # Show categories
        print("\n[4/5] Category Summary:")
        print("-" * 60)
        for cat in categories:
            print(f"  {cat[1]:2d}. {cat[0]:30s}")
        print("-" * 60)
        
        # Check existing properties
        print("\n[5/5] Checking existing data migration...")
        cursor.execute("""
            SELECT 
                COUNT(*) as total_properties,
                COUNT(standard_category_id) as mapped_properties
            FROM properties
        """)
        result = cursor.fetchone()
        
        if result:
            total = result[0]
            mapped = result[1]
            print(f"✓ Total properties in database: {total}")
            print(f"✓ Properties mapped to new categories: {mapped}")
            
            if total > 0 and mapped == total:
                print("✓ All existing properties successfully migrated!")
            elif total > 0 and mapped < total:
                print(f"⚠ {total - mapped} properties need manual category assignment")
        
        cursor.close()
        
        print("\n" + "=" * 60)
        print("MIGRATION COMPLETED SUCCESSFULLY! ✓")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Update GUI dialogs to show category dropdowns")
        print("  2. Update XML parser to read new category structure")
        print("  3. Update XML exporter to write new category structure")
        print("  4. Test with PBX-9404.xml")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        print("\nAttempting rollback...")
        try:
            rollback_cursor = conn.cursor()
            rollback_cursor.execute(get_rollback_sql())
            conn.commit()
            rollback_cursor.close()
            print("✓ Rollback successful")
        except Exception as rollback_error:
            print(f"✗ Rollback failed: {rollback_error}")
        return False
    
    finally:
        db.close()


def check_migration_status():
    """Check if migration has already been run."""
    db = DatabaseManager()
    
    try:
        conn = db.connect()
        cursor = conn.cursor()
        
        # Check if category_master table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'category_master'
            )
        """)
        exists = cursor.fetchone()[0]
        
        cursor.close()
        return exists
        
    except Exception as e:
        print(f"Error checking migration status: {e}")
        return False
    finally:
        db.close()


def main():
    """Main entry point."""
    print("\n🔧 Database Migration Tool\n")
    
    # Check if already migrated
    if check_migration_status():
        print("⚠ Migration appears to have already been run.")
        print("  The 'category_master' table already exists.")
        response = input("\nRun migration again? (y/N): ").strip().lower()
        if response != 'y':
            print("Migration cancelled.")
            return
    
    # Run migration
    success = run_migration()
    
    if success:
        print("\n✅ Database is ready for 10-category structure!")
        sys.exit(0)
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
