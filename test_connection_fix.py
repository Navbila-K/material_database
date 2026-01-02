#!/usr/bin/env python3
"""
Quick verification that database connection fix is working
"""

import sys
from db.database import DatabaseManager

def test_connection_persistence():
    """Test that connection stays open across multiple calls."""
    
    print("="*60)
    print("DATABASE CONNECTION PERSISTENCE TEST")
    print("="*60)
    
    db = DatabaseManager()
    
    # First connect
    print("\n1. First connect()...")
    conn1 = db.connect()
    print(f"   Connection: {conn1}")
    print(f"   Closed? {conn1.closed}")
    
    # Second connect (should return same connection)
    print("\n2. Second connect() (should be same connection)...")
    conn2 = db.connect()
    print(f"   Connection: {conn2}")
    print(f"   Closed? {conn2.closed}")
    print(f"   Same object? {conn1 is conn2}")
    
    # Test a query
    print("\n3. Testing query...")
    try:
        cursor = conn1.cursor()
        cursor.execute("SELECT COUNT(*) FROM materials")
        count = cursor.fetchone()[0]
        print(f"   ✓ Query successful: {count} materials found")
    except Exception as e:
        print(f"   ✗ Query failed: {e}")
        return False
    
    # Check connection still open
    print("\n4. Checking connection still open...")
    print(f"   Closed? {conn1.closed}")
    
    if conn1.closed:
        print("\n✗ TEST FAILED: Connection was closed!")
        return False
    else:
        print("\n✓ TEST PASSED: Connection remains open!")
        return True

if __name__ == "__main__":
    success = test_connection_persistence()
    sys.exit(0 if success else 1)
