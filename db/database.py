"""
Database connection and management module.
Handles PostgreSQL connections and schema initialization.
"""
import psycopg2
from psycopg2.extensions import connection as Connection
from psycopg2 import sql
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_CONFIG
from db.schema import get_create_schema_sql, get_drop_schema_sql


class DatabaseManager:
    """Manages database connections and schema operations."""
    
    def __init__(self):
        """Initialize database manager with configuration."""
        self.config = DB_CONFIG
        self._connection = None
    
    def connect(self) -> Connection:
        """
        Establish connection to PostgreSQL database.
        
        Returns:
            psycopg2 connection object
        
        Raises:
            psycopg2.Error: If connection fails
        """
        if self._connection is None or self._connection.closed:
            try:
                self._connection = psycopg2.connect(
                    host=self.config['host'],
                    port=self.config['port'],
                    database=self.config['database'],
                    user=self.config['user'],
                    password=self.config['password']
                )
                print(f"✓ Connected to database: {self.config['database']}")
            except psycopg2.Error as e:
                print(f"✗ Database connection failed: {e}")
                raise
        
        return self._connection
    
    def close(self):
        """Close database connection."""
        if self._connection and not self._connection.closed:
            self._connection.close()
            print("✓ Database connection closed")
    
    def create_schema(self):
        """
        Create database schema (all tables, indexes).
        Safe to call multiple times (uses IF NOT EXISTS).
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            schema_sql = get_create_schema_sql()
            cursor.execute(schema_sql)
            conn.commit()
            print("✓ Database schema created successfully")
        except psycopg2.Error as e:
            conn.rollback()
            print(f"✗ Schema creation failed: {e}")
            raise
        finally:
            cursor.close()
    
    def drop_schema(self):
        """
        Drop all database tables.
        WARNING: This deletes all data!
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            drop_sql = get_drop_schema_sql()
            cursor.execute(drop_sql)
            conn.commit()
            print("✓ Database schema dropped successfully")
        except psycopg2.Error as e:
            conn.rollback()
            print(f"✗ Schema drop failed: {e}")
            raise
        finally:
            cursor.close()
    
    def reset_schema(self):
        """Drop and recreate schema (fresh start)."""
        print("Resetting database schema...")
        self.drop_schema()
        self.create_schema()
        print("✓ Schema reset complete")
    
    def test_connection(self) -> bool:
        """
        Test database connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✓ PostgreSQL version: {version[0]}")
            cursor.close()
            return True
        except Exception as e:
            print(f"✗ Connection test failed: {e}")
            return False
    
    def get_cursor(self):
        """
        Get a cursor for executing queries.
        Caller is responsible for closing cursor.
        
        Returns:
            psycopg2 cursor object
        """
        conn = self.connect()
        return conn.cursor()
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = False):
        """
        Execute a SQL query.
        
        Args:
            query: SQL query string
            params: Query parameters (for parameterized queries)
            fetch: If True, return results
        
        Returns:
            Query results if fetch=True, None otherwise
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                results = cursor.fetchall()
                cursor.close()
                return results
            else:
                conn.commit()
                cursor.close()
        except psycopg2.Error as e:
            conn.rollback()
            cursor.close()
            raise


def get_db_manager() -> DatabaseManager:
    """Factory function to get DatabaseManager instance."""
    return DatabaseManager()


if __name__ == "__main__":
    # Test database connection and schema creation
    print("Testing database connection...")
    db = DatabaseManager()
    
    if db.test_connection():
        print("\nCreating schema...")
        db.create_schema()
        print("\nDatabase setup complete!")
    
    db.close()
