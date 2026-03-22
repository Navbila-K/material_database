"""
Visualization Data Service
Provides database access for the unified visualization tab.

This service layer separates database queries from GUI logic,
making the code more maintainable and testable.

Data Sources:
- xml_finalized_materials: Material metadata
- xml_finalized_parameters: Properties (Categories 1-10)
- xml_finalized_models: Models (Category 11)
- experimental_datasets: YAML experimental data
- experimental_points: Experimental data points

Author: Materials Database Team
Date: 2026-02-22
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Optional, Any, Tuple
from functools import wraps
import traceback
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DB_CONFIG


class DatabaseError(Exception):
    """Custom exception for database errors"""
    pass


class DataNotFoundError(Exception):
    """Custom exception when requested data is not found"""
    pass


def handle_db_errors(func):
    """
    Decorator to handle database errors gracefully.
    Wraps database operations with try-except and provides meaningful error messages.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except psycopg2.Error as e:
            error_msg = f"Database error in {func.__name__}: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            raise DatabaseError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error in {func.__name__}: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            raise
    return wrapper


class VisualizationDataService:
    """
    Service class for querying visualization data from PostgreSQL.
    
    This class provides a clean interface for fetching:
    - Material lists and metadata
    - Material properties (Categories 1-10)
    - Model parameters (Category 11)
    - Experimental datasets and points
    
    All methods are decorated with error handling for robustness.
    """
    
    def __init__(self, db_config: Optional[Dict] = None):
        """
        Initialize the service with database configuration.
        
        Args:
            db_config: Database configuration dict. Uses config.py if None.
        """
        self.db_config = db_config or DB_CONFIG
        self._connection = None
        self._cursor = None
        
        print("✓ VisualizationDataService initialized")
    
    def connect(self) -> psycopg2.extensions.connection:
        """
        Establish database connection.
        Creates a new connection if one doesn't exist or is closed.
        
        Returns:
            psycopg2 connection object
            
        Raises:
            DatabaseError: If connection fails
        """
        if self._connection is None or self._connection.closed:
            try:
                self._connection = psycopg2.connect(
                    host=self.db_config['host'],
                    port=self.db_config['port'],
                    database=self.db_config['database'],
                    user=self.db_config['user'],
                    password=self.db_config['password'],
                    cursor_factory=RealDictCursor  # Returns dict instead of tuple
                )
                print(f"✓ Connected to database: {self.db_config['database']}")
            except psycopg2.Error as e:
                error_msg = f"Failed to connect to database: {str(e)}"
                print(f"❌ {error_msg}")
                raise DatabaseError(error_msg) from e
        
        return self._connection
    
    def disconnect(self):
        """Close database connection."""
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None
            self._cursor = None
            print("✓ Database connection closed")
    
    def _get_cursor(self):
        """
        Get a database cursor. Creates new cursor if needed.
        
        Returns:
            psycopg2 cursor object with RealDictCursor factory
        """
        if self._cursor is None or self._cursor.closed:
            conn = self.connect()
            self._cursor = conn.cursor()
        return self._cursor
    
    def _execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Dict]:
        """
        Execute a SQL query and return results as list of dictionaries.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            
        Returns:
            List of dictionaries (one per row)
            
        Raises:
            DatabaseError: If query execution fails
        """
        cursor = self._get_cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def _execute_query_one(self, query: str, params: Optional[Tuple] = None) -> Optional[Dict]:
        """
        Execute a SQL query and return single result as dictionary.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            
        Returns:
            Dictionary or None if no results
            
        Raises:
            DatabaseError: If query execution fails
        """
        cursor = self._get_cursor()
        cursor.execute(query, params)
        return cursor.fetchone()
    
    @handle_db_errors
    def test_connection(self) -> bool:
        """
        Test database connection and verify tables exist.
        
        Returns:
            True if connection successful and tables exist
            
        Raises:
            DatabaseError: If connection or table verification fails
        """
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
          AND table_name IN (
              'xml_finalized_materials',
              'xml_finalized_parameters',
              'xml_finalized_models',
              'experimental_datasets',
              'experimental_points'
          )
        ORDER BY table_name;
        """
        
        results = self._execute_query(query)
        table_names = [row['table_name'] for row in results]
        
        required_tables = [
            'xml_finalized_materials',
            'xml_finalized_parameters',
            'xml_finalized_models',
            'experimental_datasets',
            'experimental_points'
        ]
        
        missing_tables = set(required_tables) - set(table_names)
        
        if missing_tables:
            raise DatabaseError(f"Missing required tables: {missing_tables}")
        
        print(f"✓ All required tables exist: {len(table_names)} tables found")
        return True
    
    @handle_db_errors
    def get_database_stats(self) -> Dict[str, int]:
        """
        Get summary statistics about the database.
        
        Returns:
            Dictionary with counts for materials, parameters, models, etc.
            
        Example:
            {
                'materials': 17,
                'parameters': 1022,
                'models': 215,
                'experimental_datasets': 95,
                'experimental_points': 2139
            }
        """
        stats = {}
        
        # Count materials
        query = "SELECT COUNT(*) as count FROM xml_finalized_materials;"
        result = self._execute_query_one(query)
        stats['materials'] = result['count'] if result else 0
        
        # Count parameters
        query = "SELECT COUNT(*) as count FROM xml_finalized_parameters;"
        result = self._execute_query_one(query)
        stats['parameters'] = result['count'] if result else 0
        
        # Count models
        query = "SELECT COUNT(*) as count FROM xml_finalized_models;"
        result = self._execute_query_one(query)
        stats['models'] = result['count'] if result else 0
        
        # Count experimental datasets
        query = "SELECT COUNT(*) as count FROM experimental_datasets;"
        result = self._execute_query_one(query)
        stats['experimental_datasets'] = result['count'] if result else 0
        
        # Count experimental points
        query = "SELECT COUNT(*) as count FROM experimental_points;"
        result = self._execute_query_one(query)
        stats['experimental_points'] = result['count'] if result else 0
        
        return stats
    
    def __enter__(self):
        """Context manager entry - establish connection"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection"""
        self.disconnect()
    
    def __del__(self):
        """Destructor - ensure connection is closed"""
        self.disconnect()
    
    # ========================================================================
    # TASK 1.2: MATERIAL QUERY FUNCTIONS
    # ========================================================================
    
    @handle_db_errors
    def get_all_materials(self, order_by: str = 'name') -> List[Dict]:
        """
        Get list of all materials from database.
        
        Args:
            order_by: Field to order results by ('name', 'material_id', 'material_class')
        
        Returns:
            List of material dictionaries with fields:
            - material_id: int
            - xml_id: str
            - name: str
            - common_name: str
            - material_class: str
            - author: str
            - version: str
            - status: str
        
        Example:
            >>> service.get_all_materials()
            [
                {'material_id': 1, 'name': 'Aluminum', 'material_class': 'Metal', ...},
                {'material_id': 3, 'name': 'Copper', 'material_class': 'Metal', ...},
                ...
            ]
        """
        valid_order_fields = ['name', 'material_id', 'material_class', 'xml_id']
        if order_by not in valid_order_fields:
            order_by = 'name'
        
        query = f"""
        SELECT 
            material_id,
            xml_id,
            name,
            common_name,
            author,
            date,
            version,
            last_modified,
            status,
            material_class,
            xml_file_path
        FROM xml_finalized_materials
        ORDER BY {order_by};
        """
        
        results = self._execute_query(query)
        print(f"✓ Retrieved {len(results)} materials")
        return results
    
    @handle_db_errors
    def get_material_by_id(self, material_id: int) -> Optional[Dict]:
        """
        Get single material by material_id.
        
        Args:
            material_id: Material ID to fetch
        
        Returns:
            Material dictionary or None if not found
        
        Raises:
            DataNotFoundError: If material_id doesn't exist
        
        Example:
            >>> service.get_material_by_id(3)
            {'material_id': 3, 'name': 'Copper', ...}
        """
        query = """
        SELECT 
            material_id,
            xml_id,
            name,
            common_name,
            author,
            date,
            version,
            last_modified,
            status,
            material_class,
            xml_file_path
        FROM xml_finalized_materials
        WHERE material_id = %s;
        """
        
        result = self._execute_query_one(query, (material_id,))
        
        if result is None:
            raise DataNotFoundError(f"Material with ID {material_id} not found")
        
        print(f"✓ Retrieved material: {result['name']}")
        return result
    
    @handle_db_errors
    def get_material_by_name(self, name: str, exact_match: bool = True) -> Optional[Dict]:
        """
        Get single material by name.
        
        Args:
            name: Material name to search for
            exact_match: If True, require exact match. If False, use ILIKE search.
        
        Returns:
            Material dictionary or None if not found
        
        Example:
            >>> service.get_material_by_name('Copper')
            {'material_id': 3, 'name': 'Copper', ...}
            
            >>> service.get_material_by_name('copp', exact_match=False)
            {'material_id': 3, 'name': 'Copper', ...}
        """
        if exact_match:
            query = """
            SELECT 
                material_id,
                xml_id,
                name,
                common_name,
                author,
                date,
                version,
                last_modified,
                status,
                material_class,
                xml_file_path
            FROM xml_finalized_materials
            WHERE name = %s;
            """
            result = self._execute_query_one(query, (name,))
        else:
            query = """
            SELECT 
                material_id,
                xml_id,
                name,
                common_name,
                author,
                date,
                version,
                last_modified,
                status,
                material_class,
                xml_file_path
            FROM xml_finalized_materials
            WHERE name ILIKE %s;
            """
            result = self._execute_query_one(query, (f'%{name}%',))
        
        if result:
            print(f"✓ Found material: {result['name']}")
        else:
            print(f"✗ Material '{name}' not found")
        
        return result
    
    @handle_db_errors
    def search_materials(self, search_term: str) -> List[Dict]:
        """
        Search for materials by name (fuzzy search).
        Case-insensitive partial match on name or common_name.
        
        Args:
            search_term: Search string (partial match allowed)
        
        Returns:
            List of matching materials
        
        Example:
            >>> service.search_materials('copper')
            [{'material_id': 3, 'name': 'Copper', ...}]
            
            >>> service.search_materials('mag')
            [{'material_id': 7, 'name': 'MAGNESIUM', ...}]
        """
        query = """
        SELECT 
            material_id,
            xml_id,
            name,
            common_name,
            material_class,
            status
        FROM xml_finalized_materials
        WHERE 
            name ILIKE %s 
            OR common_name ILIKE %s
            OR xml_id ILIKE %s
        ORDER BY name;
        """
        
        search_pattern = f'%{search_term}%'
        results = self._execute_query(query, (search_pattern, search_pattern, search_pattern))
        
        print(f"✓ Found {len(results)} materials matching '{search_term}'")
        return results
    
    @handle_db_errors
    def get_materials_by_class(self, material_class: str) -> List[Dict]:
        """
        Get all materials of a specific class.
        
        Args:
            material_class: Material class to filter by (e.g., 'Metal', 'Explosive', 'Polymer')
        
        Returns:
            List of materials with matching class
        
        Example:
            >>> service.get_materials_by_class('Metal')
            [{'material_id': 1, 'name': 'Aluminum', ...}, ...]
        """
        query = """
        SELECT 
            material_id,
            xml_id,
            name,
            common_name,
            material_class,
            status
        FROM xml_finalized_materials
        WHERE material_class = %s
        ORDER BY name;
        """
        
        results = self._execute_query(query, (material_class,))
        print(f"✓ Found {len(results)} materials with class '{material_class}'")
        return results
    
    @handle_db_errors
    def get_material_classes(self) -> List[str]:
        """
        Get list of unique material classes in database.
        
        Returns:
            List of unique material class names
        
        Example:
            >>> service.get_material_classes()
            ['Metal', 'Explosive', 'Polymer', 'Gas']
        """
        query = """
        SELECT DISTINCT material_class
        FROM xml_finalized_materials
        WHERE material_class IS NOT NULL
        ORDER BY material_class;
        """
        
        results = self._execute_query(query)
        classes = [row['material_class'] for row in results]
        
        print(f"✓ Found {len(classes)} unique material classes")
        return classes
    
    @handle_db_errors
    def get_materials_by_ids(self, material_ids: List[int]) -> List[Dict]:
        """
        Get multiple materials by their IDs.
        
        Args:
            material_ids: List of material IDs to fetch
        
        Returns:
            List of material dictionaries
        
        Example:
            >>> service.get_materials_by_ids([1, 3, 8])
            [
                {'material_id': 1, 'name': 'Aluminum', ...},
                {'material_id': 3, 'name': 'Copper', ...},
                {'material_id': 8, 'name': 'Nickel', ...}
            ]
        """
        if not material_ids:
            return []
        
        # Create placeholders for SQL IN clause
        placeholders = ','.join(['%s'] * len(material_ids))
        
        query = f"""
        SELECT 
            material_id,
            xml_id,
            name,
            common_name,
            material_class,
            author,
            version,
            status
        FROM xml_finalized_materials
        WHERE material_id IN ({placeholders})
        ORDER BY name;
        """
        
        results = self._execute_query(query, tuple(material_ids))
        print(f"✓ Retrieved {len(results)} materials")
        return results
    
    # ========================================================================
    # TASK 1.3: PROPERTY QUERY FUNCTIONS
    # ========================================================================
    
    @handle_db_errors
    def get_available_properties(self, material_ids: Optional[List[int]] = None) -> List[Dict]:
        """
        Get list of available properties, optionally filtered by materials.
        Returns unique property names across selected materials.
        
        Args:
            material_ids: Optional list of material IDs to filter by.
                         If None, returns all properties from all materials.
        
        Returns:
            List of dictionaries with:
            - parameter_name: str
            - category_name: str
            - category_number: int
            - count: int (number of materials with this property)
        
        Example:
            >>> service.get_available_properties([1, 3, 8])
            [
                {'parameter_name': 'Density', 'category_name': 'PhysicalProperties', ...},
                {'parameter_name': 'Melting Point', 'category_name': 'ThermalProperties', ...},
                ...
            ]
        """
        if material_ids:
            placeholders = ','.join(['%s'] * len(material_ids))
            query = f"""
            SELECT DISTINCT
                parameter_name,
                category_name,
                category_number,
                COUNT(DISTINCT material_id) as material_count
            FROM xml_finalized_parameters
            WHERE material_id IN ({placeholders})
              AND is_empty_value = FALSE
              AND parameter_value IS NOT NULL
            GROUP BY parameter_name, category_name, category_number
            ORDER BY category_number, parameter_name;
            """
            results = self._execute_query(query, tuple(material_ids))
        else:
            query = """
            SELECT DISTINCT
                parameter_name,
                category_name,
                category_number,
                COUNT(DISTINCT material_id) as material_count
            FROM xml_finalized_parameters
            WHERE is_empty_value = FALSE
              AND parameter_value IS NOT NULL
            GROUP BY parameter_name, category_name, category_number
            ORDER BY category_number, parameter_name;
            """
            results = self._execute_query(query)
        
        print(f"✓ Found {len(results)} available properties")
        return results
    
    @handle_db_errors
    def get_properties_by_category(self, category_name: str, material_ids: Optional[List[int]] = None) -> List[str]:
        """
        Get property names for a specific category.
        
        Args:
            category_name: Category to filter by (e.g., 'ThermalProperties', 'MechanicalProperties')
            material_ids: Optional list of material IDs to filter by
        
        Returns:
            List of property names in that category
        
        Example:
            >>> service.get_properties_by_category('ThermalProperties')
            ['Ambient Temperature', 'Melting Temperature', 'Specific Heat', ...]
        """
        if material_ids:
            placeholders = ','.join(['%s'] * len(material_ids))
            query = f"""
            SELECT DISTINCT parameter_name
            FROM xml_finalized_parameters
            WHERE category_name = %s
              AND material_id IN ({placeholders})
              AND is_empty_value = FALSE
              AND parameter_value IS NOT NULL
            ORDER BY parameter_name;
            """
            params = (category_name,) + tuple(material_ids)
            results = self._execute_query(query, params)
        else:
            query = """
            SELECT DISTINCT parameter_name
            FROM xml_finalized_parameters
            WHERE category_name = %s
              AND is_empty_value = FALSE
              AND parameter_value IS NOT NULL
            ORDER BY parameter_name;
            """
            results = self._execute_query(query, (category_name,))
        
        properties = [row['parameter_name'] for row in results]
        print(f"✓ Found {len(properties)} properties in category '{category_name}'")
        return properties
    
    @handle_db_errors
    def get_material_properties(self, material_ids: List[int], property_names: List[str]) -> Dict[int, Dict[str, Dict]]:
        """
        Get property values for multiple materials and properties.
        This is the core function for property comparison.
        
        Args:
            material_ids: List of material IDs to fetch
            property_names: List of property names to fetch
        
        Returns:
            Nested dictionary: {material_id: {property_name: {value, unit, ref, symbol}}}
        
        Example:
            >>> service.get_material_properties([1, 3], ['Density', 'Melting Temperature'])
            {
                1: {
                    'Density': {'value': '2700', 'unit': 'kg/m³', 'ref': '101', 'symbol': 'ρ₀'},
                    'Melting Temperature': {'value': '933', 'unit': 'K', 'ref': '101', 'symbol': 'Tm'}
                },
                3: {
                    'Density': {'value': '8960', 'unit': 'kg/m³', 'ref': '103', 'symbol': 'ρ₀'},
                    'Melting Temperature': {'value': '1358', 'unit': 'K', 'ref': '103', 'symbol': 'Tm'}
                }
            }
        """
        if not material_ids or not property_names:
            return {}
        
        mat_placeholders = ','.join(['%s'] * len(material_ids))
        prop_placeholders = ','.join(['%s'] * len(property_names))
        
        query = f"""
        SELECT 
            p.material_id,
            m.name as material_name,
            p.parameter_name,
            p.parameter_symbol,
            p.parameter_value,
            p.parameter_unit,
            p.value_ref,
            p.value_id,
            p.entry_index,
            p.category_name
        FROM xml_finalized_parameters p
        JOIN xml_finalized_materials m ON p.material_id = m.material_id
        WHERE p.material_id IN ({mat_placeholders})
          AND p.parameter_name IN ({prop_placeholders})
          AND p.is_empty_value = FALSE
          AND p.parameter_value IS NOT NULL
        ORDER BY p.material_id, p.parameter_name, p.entry_index;
        """
        
        params = tuple(material_ids) + tuple(property_names)
        results = self._execute_query(query, params)
        
        # Organize results into nested dictionary
        data = {}
        for row in results:
            mat_id = row['material_id']
            prop_name = row['parameter_name']
            
            if mat_id not in data:
                data[mat_id] = {'_material_name': row['material_name']}
            
            # If property already exists and this is another entry, aggregate
            if prop_name in data[mat_id]:
                # Handle multiple entries (e.g., multiple density values from different refs)
                if isinstance(data[mat_id][prop_name], list):
                    data[mat_id][prop_name].append({
                        'value': row['parameter_value'],
                        'unit': row['parameter_unit'],
                        'ref': row['value_ref'],
                        'symbol': row['parameter_symbol'],
                        'value_id': row['value_id'],
                        'category': row['category_name']
                    })
                else:
                    # Convert to list of entries
                    existing = data[mat_id][prop_name]
                    data[mat_id][prop_name] = [
                        existing,
                        {
                            'value': row['parameter_value'],
                            'unit': row['parameter_unit'],
                            'ref': row['value_ref'],
                            'symbol': row['parameter_symbol'],
                            'value_id': row['value_id'],
                            'category': row['category_name']
                        }
                    ]
            else:
                data[mat_id][prop_name] = {
                    'value': row['parameter_value'],
                    'unit': row['parameter_unit'],
                    'ref': row['value_ref'],
                    'symbol': row['parameter_symbol'],
                    'value_id': row['value_id'],
                    'category': row['category_name']
                }
        
        print(f"✓ Retrieved properties for {len(data)} materials, {len(property_names)} properties")
        return data
    
    @handle_db_errors
    def get_property_details(self, material_id: int, property_name: str) -> List[Dict]:
        """
        Get detailed information about a specific property for a material.
        Returns all entries if multiple values exist (e.g., from different references).
        
        Args:
            material_id: Material ID
            property_name: Property name to fetch
        
        Returns:
            List of property entries with full details
        
        Example:
            >>> service.get_property_details(3, 'Density')
            [
                {
                    'value': '8960',
                    'unit': 'kg/m³',
                    'ref': '103',
                    'symbol': 'ρ₀',
                    'category': 'PhysicalProperties',
                    'entry_index': 0
                },
                {
                    'value': '8940',
                    'unit': 'kg/m³',
                    'ref': '104',
                    'symbol': 'ρ₀',
                    'category': 'PhysicalProperties',
                    'entry_index': 1
                }
            ]
        """
        query = """
        SELECT 
            parameter_name,
            parameter_symbol,
            parameter_value,
            parameter_unit,
            value_ref,
            value_id,
            value_usup_ref,
            entry_index,
            category_name,
            category_number,
            is_empty_value
        FROM xml_finalized_parameters
        WHERE material_id = %s
          AND parameter_name = %s
        ORDER BY entry_index;
        """
        
        results = self._execute_query(query, (material_id, property_name))
        
        print(f"✓ Found {len(results)} entries for property '{property_name}'")
        return results
    
    @handle_db_errors
    def get_all_properties_for_material(self, material_id: int, include_empty: bool = False) -> Dict[str, List[Dict]]:
        """
        Get ALL properties for a single material, grouped by category.
        
        Args:
            material_id: Material ID to fetch
            include_empty: If True, include properties with empty values
        
        Returns:
            Dictionary grouped by category: {category_name: [properties]}
        
        Example:
            >>> service.get_all_properties_for_material(3)
            {
                'PhysicalProperties': [
                    {'name': 'Density', 'value': '8960', 'unit': 'kg/m³', ...},
                    {'name': 'Color', 'value': 'reddish', ...}
                ],
                'ThermalProperties': [
                    {'name': 'Melting Temperature', 'value': '1358', ...}
                ],
                ...
            }
        """
        if include_empty:
            query = """
            SELECT 
                parameter_name,
                parameter_symbol,
                parameter_value,
                parameter_unit,
                value_ref,
                value_id,
                entry_index,
                category_name,
                category_number,
                is_empty_value
            FROM xml_finalized_parameters
            WHERE material_id = %s
            ORDER BY category_number, parameter_name, entry_index;
            """
        else:
            query = """
            SELECT 
                parameter_name,
                parameter_symbol,
                parameter_value,
                parameter_unit,
                value_ref,
                value_id,
                entry_index,
                category_name,
                category_number,
                is_empty_value
            FROM xml_finalized_parameters
            WHERE material_id = %s
              AND is_empty_value = FALSE
              AND parameter_value IS NOT NULL
            ORDER BY category_number, parameter_name, entry_index;
            """
        
        results = self._execute_query(query, (material_id,))
        
        # Group by category
        grouped = {}
        for row in results:
            category = row['category_name']
            if category not in grouped:
                grouped[category] = []
            
            grouped[category].append({
                'name': row['parameter_name'],
                'symbol': row['parameter_symbol'],
                'value': row['parameter_value'],
                'unit': row['parameter_unit'],
                'ref': row['value_ref'],
                'value_id': row['value_id'],
                'entry_index': row['entry_index'],
                'is_empty': row['is_empty_value']
            })
        
        print(f"✓ Retrieved {len(results)} properties across {len(grouped)} categories")
        return grouped
    
    @handle_db_errors
    def get_categories_with_counts(self, material_id: Optional[int] = None) -> List[Dict]:
        """
        Get all categories with property counts.
        
        Args:
            material_id: Optional material ID to filter by
        
        Returns:
            List of categories with property counts
        
        Example:
            >>> service.get_categories_with_counts(3)
            [
                {'category_number': 1, 'category_name': 'StructureAndFormulation', 'count': 4},
                {'category_number': 2, 'category_name': 'PhysicalProperties', 'count': 3},
                ...
            ]
        """
        if material_id:
            query = """
            SELECT 
                category_number,
                category_name,
                COUNT(*) as property_count,
                COUNT(CASE WHEN is_empty_value = FALSE AND parameter_value IS NOT NULL THEN 1 END) as filled_count
            FROM xml_finalized_parameters
            WHERE material_id = %s
            GROUP BY category_number, category_name
            ORDER BY category_number;
            """
            results = self._execute_query(query, (material_id,))
        else:
            query = """
            SELECT 
                category_number,
                category_name,
                COUNT(DISTINCT parameter_name) as property_count,
                COUNT(DISTINCT material_id) as material_count
            FROM xml_finalized_parameters
            GROUP BY category_number, category_name
            ORDER BY category_number;
            """
            results = self._execute_query(query)
        
        print(f"✓ Found {len(results)} categories")
        return results
    
    # ========================================================================
    # TASK 1.4: MODEL QUERY FUNCTIONS
    # ========================================================================
    
    @handle_db_errors
    def get_available_model_types(self, material_id: int) -> Dict[str, List[str]]:
        """
        Get available model types for a material (EOS, Strength, Reaction).
        Returns models grouped by type.
        
        Args:
            material_id: Material ID to query
        
        Returns:
            Dictionary grouped by model type:
            {
                'EOS': ['Mie-Gruneisen', 'USUP', ...],
                'Strength': ['Johnson-Cook', 'Steinberg-Guinan', ...],
                'Reaction': ['JWL', ...]
            }
        
        Example:
            >>> service.get_available_model_types(3)
            {
                'EOS': ['Mie-Gruneisen', 'USUP'],
                'Strength': ['Johnson-Cook'],
                'Reaction': []
            }
        """
        query = """
        SELECT DISTINCT
            model_type,
            model_name
        FROM xml_finalized_models
        WHERE material_id = %s
        ORDER BY model_type, model_name;
        """
        
        results = self._execute_query(query, (material_id,))
        
        # Group by model type
        grouped = {'EOS': [], 'Strength': [], 'Reaction': []}
        for row in results:
            model_type = row['model_type']
            model_name = row['model_name']
            if model_type in grouped:
                grouped[model_type].append(model_name)
        
        total_models = sum(len(models) for models in grouped.values())
        print(f"✓ Found {total_models} models for material {material_id}")
        return grouped
    
    @handle_db_errors
    def get_models_by_type(self, material_id: int, model_type: str) -> List[Dict]:
        """
        Get all models of a specific type for a material.
        
        Args:
            material_id: Material ID to query
            model_type: Model type ('EOS', 'Strength', 'Reaction')
        
        Returns:
            List of model dictionaries with basic info
        
        Example:
            >>> service.get_models_by_type(3, 'EOS')
            [
                {'model_name': 'Mie-Gruneisen', 'model_type': 'EOS', 'parameter_count': 15},
                {'model_name': 'USUP', 'model_type': 'EOS', 'parameter_count': 8}
            ]
        """
        query = """
        SELECT 
            model_name,
            model_type,
            COUNT(*) as parameter_count
        FROM xml_finalized_models
        WHERE material_id = %s
          AND model_type = %s
        GROUP BY model_name, model_type
        ORDER BY model_name;
        """
        
        results = self._execute_query(query, (material_id, model_type))
        print(f"✓ Found {len(results)} {model_type} models")
        return results
    
    @handle_db_errors
    def get_model_parameters(self, material_id: int, model_name: str) -> List[Dict]:
        """
        Get all parameters for a specific model.
        This is the core function for US-Up visualization and model display.
        
        Args:
            material_id: Material ID
            model_name: Model name (e.g., 'USUP', 'Johnson-Cook', 'Mie-Gruneisen')
        
        Returns:
            List of parameter dictionaries with all details
        
        Example:
            >>> service.get_model_parameters(3, 'USUP')
            [
                {
                    'parameter_name': 'C0',
                    'parameter_symbol': 'C₀',
                    'parameter_value': '3940',
                    'parameter_unit': 'm/s',
                    'value_ref': '107',
                    'value_usup_ref': 'LASL',
                    'model_type': 'EOS'
                },
                {
                    'parameter_name': 's',
                    'parameter_symbol': 's',
                    'parameter_value': '1.489',
                    'parameter_unit': '',
                    'value_ref': '107',
                    'value_usup_ref': 'LASL',
                    'model_type': 'EOS'
                },
                ...
            ]
        """
        query = """
        SELECT 
            model_name,
            model_type,
            parameter_name,
            parameter_symbol,
            parameter_value,
            parameter_unit,
            value_ref,
            value_usup_ref,
            entry_index
        FROM xml_finalized_models
        WHERE material_id = %s
          AND model_name = %s
        ORDER BY entry_index;
        """
        
        results = self._execute_query(query, (material_id, model_name))
        print(f"✓ Retrieved {len(results)} parameters for model '{model_name}'")
        return results
    
    @handle_db_errors
    def get_usup_parameters(self, material_id: int) -> Dict[str, any]:
        """
        Get US-Up (shock velocity) parameters specifically for plotting.
        Extracts C0, s, and Gamma from USUP or Mie-Gruneisen models.
        
        Args:
            material_id: Material ID
        
        Returns:
            Dictionary with US-Up parameters:
            {
                'model_name': 'USUP',
                'C0': {'value': '3940', 'unit': 'm/s', 'ref': '107'},
                's': {'value': '1.489', 'unit': '', 'ref': '107'},
                'Gamma': {'value': '2.0', 'unit': '', 'ref': '107'},
                'rho0': {'value': '8940', 'unit': 'kg/m³', 'ref': '107'}
            }
        
        Example:
            >>> params = service.get_usup_parameters(3)
            >>> c0 = float(params['C0']['value'])
            >>> s = float(params['s']['value'])
            >>> # Now can plot: Us = C0 + s * Up
        """
        # Try USUP model first
        query = """
        SELECT 
            model_name,
            parameter_name,
            parameter_symbol,
            parameter_value,
            parameter_unit,
            value_ref,
            value_usup_ref
        FROM xml_finalized_models
        WHERE material_id = %s
          AND (model_name = 'USUP' OR model_name = 'Mie-Gruneisen' OR model_name LIKE '%%US-Up%%')
          AND (parameter_name IN ('C0', 's', 'Gamma', 'Reference Density', 'Cs', 'Rho'))
        ORDER BY 
            CASE 
                WHEN model_name LIKE '%%US-Up%%' THEN 1
                WHEN model_name = 'USUP' THEN 2 
                WHEN model_name = 'Mie-Gruneisen' THEN 3
            END,
            parameter_name;
        """
        
        results = self._execute_query(query, (material_id,))
        
        if not results:
            print(f"✓ No US-Up parameters found for material {material_id}")
            return {}
        
        # Build parameter dictionary
        usup_data = {
            'model_name': results[0]['model_name'],
            'material_id': material_id
        }
        
        for row in results:
            param_name = row['parameter_name']
            
            # Normalize parameter names (handle different naming conventions)
            if param_name in ['C0', 'Cs']:
                usup_data['C0'] = {
                    'value': row['parameter_value'],
                    'unit': row['parameter_unit'],
                    'ref': row['value_ref'],
                    'usup_ref': row['value_usup_ref'],
                    'symbol': row['parameter_symbol']
                }
            elif param_name == 's':
                usup_data['s'] = {
                    'value': row['parameter_value'],
                    'unit': row['parameter_unit'],
                    'ref': row['value_ref'],
                    'usup_ref': row['value_usup_ref'],
                    'symbol': row['parameter_symbol']
                }
            elif param_name == 'Gamma':
                usup_data['Gamma'] = {
                    'value': row['parameter_value'],
                    'unit': row['parameter_unit'],
                    'ref': row['value_ref'],
                    'usup_ref': row['value_usup_ref'],
                    'symbol': row['parameter_symbol']
                }
            elif param_name in ['Reference Density', 'Rho']:
                usup_data['rho0'] = {
                    'value': row['parameter_value'],
                    'unit': row['parameter_unit'],
                    'ref': row['value_ref'],
                    'symbol': row['parameter_symbol']
                }
        
        print(f"✓ Retrieved US-Up parameters from '{usup_data['model_name']}' model")
        return usup_data
    
    @handle_db_errors
    def get_all_models_for_material(self, material_id: int) -> Dict[str, List[Dict]]:
        """
        Get ALL models for a material, grouped by type.
        Comprehensive view of all EOS, Strength, and Reaction models.
        
        Args:
            material_id: Material ID
        
        Returns:
            Dictionary grouped by model type with full parameter details:
            {
                'EOS': [
                    {
                        'model_name': 'USUP',
                        'parameters': [{'name': 'C0', 'value': '3940', ...}, ...]
                    },
                    ...
                ],
                'Strength': [...],
                'Reaction': [...]
            }
        
        Example:
            >>> all_models = service.get_all_models_for_material(3)
            >>> eos_models = all_models['EOS']
            >>> print(f"Found {len(eos_models)} EOS models")
        """
        query = """
        SELECT 
            model_name,
            model_type,
            parameter_name,
            parameter_symbol,
            parameter_value,
            parameter_unit,
            value_ref,
            value_usup_ref,
            entry_index
        FROM xml_finalized_models
        WHERE material_id = %s
        ORDER BY model_type, model_name, entry_index;
        """
        
        results = self._execute_query(query, (material_id,))
        
        # Group by model type and model name
        grouped = {'EOS': [], 'Strength': [], 'Reaction': []}
        current_model = None
        current_params = []
        
        for row in results:
            model_type = row['model_type']
            model_name = row['model_name']
            
            # Check if we're starting a new model
            if current_model != model_name:
                # Save previous model
                if current_model and current_params:
                    model_type_prev = current_params[0].get('model_type', 'EOS')
                    if model_type_prev in grouped:
                        grouped[model_type_prev].append({
                            'model_name': current_model,
                            'parameters': current_params
                        })
                
                # Start new model
                current_model = model_name
                current_params = []
            
            # Add parameter to current model
            current_params.append({
                'name': row['parameter_name'],
                'symbol': row['parameter_symbol'],
                'value': row['parameter_value'],
                'unit': row['parameter_unit'],
                'ref': row['value_ref'],
                'usup_ref': row['value_usup_ref'],
                'model_type': row['model_type']
            })
        
        # Don't forget the last model
        if current_model and current_params:
            model_type_last = current_params[0].get('model_type', 'EOS')
            if model_type_last in grouped:
                grouped[model_type_last].append({
                    'model_name': current_model,
                    'parameters': current_params
                })
        
        total_models = sum(len(models) for models in grouped.values())
        print(f"✓ Retrieved {total_models} models across {len([k for k, v in grouped.items() if v])} model types")
        return grouped
    
    @handle_db_errors
    def get_model_count(self, material_id: Optional[int] = None) -> Dict[str, int]:
        """
        Get count of models by type, optionally filtered by material.
        
        Args:
            material_id: Optional material ID to filter by
        
        Returns:
            Dictionary with counts: {'EOS': 2, 'Strength': 1, 'Reaction': 0, 'total': 3}
        
        Example:
            >>> service.get_model_count(3)
            {'EOS': 2, 'Strength': 1, 'Reaction': 0, 'total': 3}
        """
        if material_id:
            query = """
            SELECT 
                model_type,
                COUNT(DISTINCT model_name) as model_count
            FROM xml_finalized_models
            WHERE material_id = %s
            GROUP BY model_type;
            """
            results = self._execute_query(query, (material_id,))
        else:
            query = """
            SELECT 
                model_type,
                COUNT(DISTINCT CONCAT(material_id, '-', model_name)) as model_count
            FROM xml_finalized_models
            GROUP BY model_type;
            """
            results = self._execute_query(query)
        
        # Initialize counts
        counts = {'EOS': 0, 'Strength': 0, 'Reaction': 0, 'total': 0}
        
        for row in results:
            model_type = row['model_type']
            count = row['model_count']
            if model_type in counts:
                counts[model_type] = count
                counts['total'] += count
        
        print(f"✓ Model counts: EOS={counts['EOS']}, Strength={counts['Strength']}, Reaction={counts['Reaction']}")
        return counts
    
    # ========================================================================
    # TASK 1.5: EXPERIMENTAL DATA QUERY FUNCTIONS
    # ========================================================================
    
    @handle_db_errors
    def get_experimental_datasets(self, material_name: Optional[str] = None) -> List[Dict]:
        """
        Get available experimental datasets, optionally filtered by material name.
        
        Args:
            material_name: Optional material name to filter by (case-insensitive, fuzzy match)
        
        Returns:
            List of dataset dictionaries with metadata
        
        Example:
            >>> service.get_experimental_datasets('Copper')
            [
                {
                    'dataset_id': 15,
                    'material_name': 'Copper',
                    'experiment_type': 'Shock Hugoniot',
                    'source': 'LASL Shock Hugoniot Data',
                    'point_count': 45,
                    'filename': 'copper_shock.yaml'
                },
                ...
            ]
        """
        if material_name:
            # Fuzzy search on material name
            query = """
            SELECT 
                d.dataset_id,
                d.material_name,
                d.experiment_type,
                d.source_file,
                d.yaml_filename,
                d.description,
                d.notes,
                d.created_at,
                COUNT(p.point_id) as point_count
            FROM experimental_datasets d
            LEFT JOIN experimental_points p ON d.dataset_id = p.dataset_id
            WHERE LOWER(d.material_name) LIKE LOWER(%s)
            GROUP BY d.dataset_id, d.material_name, d.experiment_type, d.source_file, 
                     d.yaml_filename, d.description, d.notes, d.created_at
            ORDER BY d.material_name, d.experiment_type;
            """
            search_pattern = f"%{material_name}%"
            results = self._execute_query(query, (search_pattern,))
        else:
            query = """
            SELECT 
                d.dataset_id,
                d.material_name,
                d.experiment_type,
                d.source_file,
                d.yaml_filename,
                d.description,
                d.notes,
                d.created_at,
                COUNT(p.point_id) as point_count
            FROM experimental_datasets d
            LEFT JOIN experimental_points p ON d.dataset_id = p.dataset_id
            GROUP BY d.dataset_id, d.material_name, d.experiment_type, d.source_file, 
                     d.yaml_filename, d.description, d.notes, d.created_at
            ORDER BY d.material_name, d.experiment_type;
            """
            results = self._execute_query(query)
        
        print(f"✓ Found {len(results)} experimental datasets")
        return results
    
    @handle_db_errors
    def get_experimental_datasets_by_type(self, experiment_type: str, material_name: Optional[str] = None) -> List[Dict]:
        """
        Get experimental datasets filtered by experiment type.
        
        Args:
            experiment_type: Type of experiment (e.g., 'Shock Hugoniot', 'Sound Speed', 'Tension')
            material_name: Optional material name to further filter
        
        Returns:
            List of dataset dictionaries
        
        Example:
            >>> service.get_experimental_datasets_by_type('Shock Hugoniot', 'Copper')
            [
                {'dataset_id': 15, 'material_name': 'Copper', 'point_count': 45, ...},
                ...
            ]
        """
        if material_name:
            query = """
            SELECT 
                d.dataset_id,
                d.material_name,
                d.experiment_type,
                d.source_file,
                d.yaml_filename,
                d.description,
                d.notes,
                COUNT(p.point_id) as point_count
            FROM experimental_datasets d
            LEFT JOIN experimental_points p ON d.dataset_id = p.dataset_id
            WHERE d.experiment_type = %s
              AND LOWER(d.material_name) LIKE LOWER(%s)
            GROUP BY d.dataset_id, d.material_name, d.experiment_type, d.source_file, 
                     d.yaml_filename, d.description, d.notes
            ORDER BY d.material_name;
            """
            search_pattern = f"%{material_name}%"
            results = self._execute_query(query, (experiment_type, search_pattern))
        else:
            query = """
            SELECT 
                d.dataset_id,
                d.material_name,
                d.experiment_type,
                d.source_file,
                d.yaml_filename,
                d.description,
                d.notes,
                COUNT(p.point_id) as point_count
            FROM experimental_datasets d
            LEFT JOIN experimental_points p ON d.dataset_id = p.dataset_id
            WHERE d.experiment_type = %s
            GROUP BY d.dataset_id, d.material_name, d.experiment_type, d.source_file, 
                     d.yaml_filename, d.description, d.notes
            ORDER BY d.material_name;
            """
            results = self._execute_query(query, (experiment_type,))
        
        print(f"✓ Found {len(results)} datasets of type '{experiment_type}'")
        return results
    
    @handle_db_errors
    def get_experiment_types(self, material_name: Optional[str] = None) -> List[str]:
        """
        Get list of unique experiment types available.
        
        Args:
            material_name: Optional material name to filter by
        
        Returns:
            List of experiment type names
        
        Example:
            >>> service.get_experiment_types()
            ['Shock Hugoniot', 'Sound Speed', 'Tension', 'Compression', ...]
        """
        if material_name:
            query = """
            SELECT DISTINCT experiment_type
            FROM experimental_datasets
            WHERE LOWER(material_name) LIKE LOWER(%s)
            ORDER BY experiment_type;
            """
            search_pattern = f"%{material_name}%"
            results = self._execute_query(query, (search_pattern,))
        else:
            query = """
            SELECT DISTINCT experiment_type
            FROM experimental_datasets
            ORDER BY experiment_type;
            """
            results = self._execute_query(query)
        
        types = [row['experiment_type'] for row in results]
        print(f"✓ Found {len(types)} experiment types")
        return types
    
    @handle_db_errors
    def get_experimental_points(self, dataset_id: int) -> List[Dict]:
        """
        Get all data points for a specific experimental dataset.
        This is the core function for plotting experimental data (US-Up).
        
        Args:
            dataset_id: Dataset ID to fetch points from
        
        Returns:
            List of data point dictionaries with US-Up values
        
        Example:
            >>> points = service.get_experimental_points(15)
            [
                {
                    'point_id': 1,
                    'us': 4500.2,  # Shock velocity
                    'up': 1000.5,  # Particle velocity
                    'p': 12.5,     # Pressure
                    'rho': 8960.0, # Density
                    'v': 0.112,    # Specific volume
                    'rho0': 8940.0, # Initial density
                    'v_over_v0': 1.002,
                    'experiment_label': 'Shot 1'
                },
                ...
            ]
        """
        query = """
        SELECT 
            point_id,
            dataset_id,
            point_order,
            rho0,
            us,
            up,
            p,
            v,
            rho,
            v_over_v0,
            experiment_label,
            symbol,
            additional_properties
        FROM experimental_points
        WHERE dataset_id = %s
        ORDER BY point_order;
        """
        
        results = self._execute_query(query, (dataset_id,))
        print(f"✓ Retrieved {len(results)} data points for dataset {dataset_id}")
        return results
    
    @handle_db_errors
    def get_experimental_data_with_points(self, material_name: str) -> Dict[str, List[Dict]]:
        """
        Get experimental datasets with their data points for a material.
        Returns complete data ready for plotting.
        
        Args:
            material_name: Material name to fetch data for
        
        Returns:
            Dictionary grouped by experiment type:
            {
                'Shock Hugoniot': [
                    {
                        'dataset_info': {...},
                        'points': [{x_value, y_value, ...}, ...]
                    },
                    ...
                ],
                'Sound Speed': [...],
                ...
            }
        
        Example:
            >>> data = service.get_experimental_data_with_points('Copper')
            >>> hugoniot_datasets = data['Shock Hugoniot']
            >>> first_dataset = hugoniot_datasets[0]
            >>> x_vals = [p['x_value'] for p in first_dataset['points']]
            >>> y_vals = [p['y_value'] for p in first_dataset['points']]
            >>> plt.plot(x_vals, y_vals)
        """
        # Get all datasets for the material
        datasets = self.get_experimental_datasets(material_name)
        
        if not datasets:
            print(f"✓ No experimental data found for '{material_name}'")
            return {}
        
        # Group by experiment type and fetch points
        grouped = {}
        
        for dataset in datasets:
            exp_type = dataset['experiment_type']
            dataset_id = dataset['dataset_id']
            
            # Get points for this dataset
            points = self.get_experimental_points(dataset_id)
            
            if exp_type not in grouped:
                grouped[exp_type] = []
            
            grouped[exp_type].append({
                'dataset_info': dataset,
                'points': points
            })
        
        total_datasets = len(datasets)
        total_points = sum(d['point_count'] for d in datasets)
        print(f"✓ Retrieved {total_datasets} datasets with {total_points} total points")
        return grouped
    
    @handle_db_errors
    def get_dataset_statistics(self, dataset_id: int) -> Dict:
        """
        Get statistical summary of a dataset's data points (US-Up data).
        
        Args:
            dataset_id: Dataset ID to analyze
        
        Returns:
            Dictionary with statistics:
            {
                'dataset_id': 15,
                'point_count': 45,
                'us_min': 3500.0,
                'us_max': 8000.5,
                'us_mean': 5500.2,
                'up_min': 500.1,
                'up_max': 2500.3,
                'up_mean': 1500.4
            }
        
        Example:
            >>> stats = service.get_dataset_statistics(15)
            >>> print(f"Us range: {stats['us_min']} to {stats['us_max']}")
        """
        query = """
        SELECT 
            dataset_id,
            COUNT(*) as point_count,
            MIN(us) as us_min,
            MAX(us) as us_max,
            AVG(us) as us_mean,
            MIN(up) as up_min,
            MAX(up) as up_max,
            AVG(up) as up_mean,
            MIN(p) as p_min,
            MAX(p) as p_max,
            AVG(p) as p_mean,
            MIN(rho) as rho_min,
            MAX(rho) as rho_max,
            AVG(rho) as rho_mean
        FROM experimental_points
        WHERE dataset_id = %s
        GROUP BY dataset_id;
        """
        
        result = self._execute_query_one(query, (dataset_id,))
        
        if not result:
            raise DataNotFoundError(f"No data points found for dataset {dataset_id}")
        
        print(f"✓ Retrieved statistics for dataset {dataset_id}: {result['point_count']} points")
        return result
    
    @handle_db_errors
    def get_all_experimental_materials(self) -> List[Dict]:
        """
        Get list of materials that have experimental data.
        
        Returns:
            List of dictionaries with material names and dataset counts
        
        Example:
            >>> materials = service.get_all_experimental_materials()
            [
                {'material_name': 'Copper', 'dataset_count': 3, 'total_points': 125},
                {'material_name': 'Aluminum', 'dataset_count': 2, 'total_points': 80},
                ...
            ]
        """
        query = """
        SELECT 
            d.material_name,
            COUNT(DISTINCT d.dataset_id) as dataset_count,
            COUNT(p.point_id) as total_points
        FROM experimental_datasets d
        LEFT JOIN experimental_points p ON d.dataset_id = p.dataset_id
        GROUP BY d.material_name
        ORDER BY d.material_name;
        """
        
        results = self._execute_query(query)
        print(f"✓ Found {len(results)} materials with experimental data")
        return results


# ============================================================================
# MODULE-LEVEL TEST FUNCTION
# ============================================================================

def test_service():
    """
    Test function to verify service is working correctly.
    Can be run standalone: python services/visualization_service.py
    """
    print("\n" + "="*70)
    print("TESTING VISUALIZATION DATA SERVICE")
    print("="*70 + "\n")
    
    try:
        # Test 1: Create service
        print("Test 1: Creating service instance...")
        service = VisualizationDataService()
        print("✓ Service created\n")
        
        # Test 2: Test connection
        print("Test 2: Testing database connection...")
        service.test_connection()
        print("✓ Connection successful\n")
        
        # Test 3: Get database stats
        print("Test 3: Getting database statistics...")
        stats = service.get_database_stats()
        print("✓ Database Statistics:")
        for key, value in stats.items():
            print(f"  • {key:.<30} {value:>10,}")
        print()
        
        # Test 4: Context manager
        print("Test 4: Testing context manager...")
        with VisualizationDataService() as svc:
            stats2 = svc.get_database_stats()
            print(f"✓ Context manager works: {stats2['materials']} materials found\n")
        
        # Test 5: Cleanup
        print("Test 5: Cleaning up...")
        service.disconnect()
        print("✓ Service disconnected\n")
        
        print("="*70)
        print("✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run tests when script is executed directly
    success = test_service()
    sys.exit(0 if success else 1)
