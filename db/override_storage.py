"""
Override Storage for Material Database Engine.
Stores user overrides SEPARATELY from reference data.

CRITICAL: This module does NOT modify core tables.
Overrides are stored in a dedicated table for persistence.
"""
import psycopg2
from typing import Dict, List, Any, Optional
import json


class OverrideStorage:
    """
    Manages persistent storage of overrides in a separate table.
    Does NOT touch core material tables.
    """
    
    def __init__(self, connection):
        """
        Initialize override storage.
        
        Args:
            connection: psycopg2 connection object
        """
        self.conn = connection
        self._ensure_override_table()
    
    def _ensure_override_table(self):
        """Create override table if it doesn't exist."""
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS material_overrides (
                    override_id SERIAL PRIMARY KEY,
                    material_id INTEGER NOT NULL REFERENCES materials(material_id) ON DELETE CASCADE,
                    property_path TEXT NOT NULL,
                    override_type TEXT NOT NULL CHECK (override_type IN ('reference_preference', 'value_override')),
                    override_data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(material_id, property_path, override_type)
                );
                
                CREATE INDEX IF NOT EXISTS idx_overrides_material 
                ON material_overrides(material_id);
            """)
            self.conn.commit()
    
    def save_reference_preference(self, material_id: int, property_path: str, 
                                   preferred_ref: str):
        """
        Save preferred reference selection.
        
        Args:
            material_id: Material ID
            property_path: Path to property (e.g., 'properties.Thermal.Density')
            preferred_ref: Preferred reference ID
        """
        override_data = {'preferred_ref': preferred_ref}
        
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO material_overrides 
                (material_id, property_path, override_type, override_data)
                VALUES (%s, %s, 'reference_preference', %s)
                ON CONFLICT (material_id, property_path, override_type)
                DO UPDATE SET override_data = EXCLUDED.override_data,
                             created_at = CURRENT_TIMESTAMP
            """, (material_id, property_path, json.dumps(override_data)))
            self.conn.commit()
    
    def save_value_override(self, material_id: int, property_path: str, 
                           override_value: str, unit: Optional[str] = None,
                           reason: Optional[str] = None):
        """
        Save user-defined value override.
        
        Args:
            material_id: Material ID
            property_path: Path to property
            override_value: Override value
            unit: Unit (optional)
            reason: Reason for override (optional)
        """
        override_data = {
            'value': override_value,
            'unit': unit,
            'reason': reason
        }
        
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO material_overrides 
                (material_id, property_path, override_type, override_data)
                VALUES (%s, %s, 'value_override', %s)
                ON CONFLICT (material_id, property_path, override_type)
                DO UPDATE SET override_data = EXCLUDED.override_data,
                             created_at = CURRENT_TIMESTAMP
            """, (material_id, property_path, json.dumps(override_data)))
            self.conn.commit()
    
    def load_overrides(self, material_id: int) -> Dict[str, Any]:
        """
        Load all overrides for a material.
        
        Args:
            material_id: Material ID
        
        Returns:
            Dictionary with reference_preferences and value_overrides
        """
        result = {
            'reference_preferences': {},
            'value_overrides': {}
        }
        
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT property_path, override_type, override_data
                FROM material_overrides
                WHERE material_id = %s
            """, (material_id,))
            
            for row in cur.fetchall():
                property_path, override_type, override_data = row
                data = json.loads(override_data) if isinstance(override_data, str) else override_data
                
                if override_type == 'reference_preference':
                    result['reference_preferences'][property_path] = data['preferred_ref']
                elif override_type == 'value_override':
                    result['value_overrides'][property_path] = data
        
        return result
    
    def delete_override(self, material_id: int, property_path: str, 
                        override_type: Optional[str] = None):
        """
        Delete specific override or all overrides for a property path.
        
        Args:
            material_id: Material ID
            property_path: Path to property
            override_type: Specific override type or None for all
        """
        with self.conn.cursor() as cur:
            if override_type:
                cur.execute("""
                    DELETE FROM material_overrides
                    WHERE material_id = %s AND property_path = %s AND override_type = %s
                """, (material_id, property_path, override_type))
            else:
                cur.execute("""
                    DELETE FROM material_overrides
                    WHERE material_id = %s AND property_path = %s
                """, (material_id, property_path))
            self.conn.commit()
    
    def delete_all_overrides(self, material_id: int):
        """
        Delete all overrides for a material.
        
        Args:
            material_id: Material ID
        """
        with self.conn.cursor() as cur:
            cur.execute("""
                DELETE FROM material_overrides
                WHERE material_id = %s
            """, (material_id,))
            self.conn.commit()
    
    def list_overrides(self, material_id: int) -> List[Dict[str, Any]]:
        """
        List all overrides for a material with full details.
        
        Args:
            material_id: Material ID
        
        Returns:
            List of override dictionaries
        """
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT property_path, override_type, override_data, created_at
                FROM material_overrides
                WHERE material_id = %s
                ORDER BY created_at DESC
            """, (material_id,))
            
            results = []
            for row in cur.fetchall():
                property_path, override_type, override_data, created_at = row
                data = json.loads(override_data) if isinstance(override_data, str) else override_data
                
                results.append({
                    'property_path': property_path,
                    'override_type': override_type,
                    'override_data': data,
                    'created_at': created_at
                })
            
            return results
    
    def has_overrides(self, material_id: int) -> bool:
        """
        Check if material has any overrides.
        
        Args:
            material_id: Material ID
        
        Returns:
            True if material has overrides
        """
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) FROM material_overrides
                WHERE material_id = %s
            """, (material_id,))
            count = cur.fetchone()[0]
            return count > 0


def create_override_storage(connection) -> OverrideStorage:
    """
    Factory function to create OverrideStorage instance.
    
    Args:
        connection: psycopg2 connection object
    
    Returns:
        OverrideStorage instance
    """
    return OverrideStorage(connection)
