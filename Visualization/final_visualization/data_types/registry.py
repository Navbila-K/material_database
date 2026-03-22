"""
Data Type Registry - Plugin system for extensible data types

This registry allows automatic discovery and management of all data types.
New data types can be added without modifying core code.
"""

from typing import Dict, List, Type, Optional
from .base_data_type import BaseDataType


class DataTypeRegistry:
    """
    Central registry for all data types
    
    Usage:
        # Register a new type
        DataTypeRegistry.register(UsUpExperimental())
        
        # Get all types
        types = DataTypeRegistry.get_all()
        
        # Get types by category
        exp_types = DataTypeRegistry.get_by_category("experimental")
    """
    
    _registry: Dict[str, BaseDataType] = {}
    
    @classmethod
    def register(cls, data_type: BaseDataType):
        """
        Register a new data type
        
        Args:
            data_type: Instance of BaseDataType subclass
        """
        key = f"{data_type.category}:{data_type.name}"
        cls._registry[key] = data_type
        print(f"[Registry] ✓ Registered: {key}")
    
    @classmethod
    def unregister(cls, category: str, name: str):
        """Unregister a data type"""
        key = f"{category}:{name}"
        if key in cls._registry:
            del cls._registry[key]
            print(f"[Registry] ✓ Unregistered: {key}")
    
    @classmethod
    def get_all(cls) -> List[BaseDataType]:
        """Get all registered data types"""
        return list(cls._registry.values())
    
    @classmethod
    def get_by_category(cls, category: str) -> List[BaseDataType]:
        """
        Get all data types in a category
        
        Args:
            category: Category name ("experimental", "model", etc.)
            
        Returns:
            List of data types in that category
        """
        return [dt for dt in cls._registry.values() if dt.category == category]
    
    @classmethod
    def get_by_name(cls, category: str, name: str) -> Optional[BaseDataType]:
        """Get specific data type"""
        key = f"{category}:{name}"
        return cls._registry.get(key)
    
    @classmethod
    def get_categories(cls) -> List[str]:
        """Get all unique categories"""
        return list(set(dt.category for dt in cls._registry.values()))
    
    @classmethod
    def get_available_for_material(cls, material_name: str) -> Dict[str, List[BaseDataType]]:
        """
        Get all available data types for a material, grouped by category
        
        Args:
            material_name: Material to check
            
        Returns:
            Dictionary: {category: [data_types]}
        """
        result = {}
        for data_type in cls._registry.values():
            if data_type.can_load(material_name):
                category = data_type.category
                if category not in result:
                    result[category] = []
                result[category].append(data_type)
        return result
    
    @classmethod
    def clear(cls):
        """Clear all registered types (useful for testing)"""
        cls._registry.clear()
        print("[Registry] ✓ Cleared")
    
    @classmethod
    def summary(cls) -> str:
        """Get summary of registered types"""
        categories = cls.get_categories()
        lines = ["Data Type Registry:"]
        for category in sorted(categories):
            types = cls.get_by_category(category)
            lines.append(f"  {category}: {len(types)} types")
            for dt in types:
                lines.append(f"    - {dt.name}")
        return "\n".join(lines)


# Convenience functions
def register_data_type(data_type: BaseDataType):
    """Convenience function to register a data type"""
    DataTypeRegistry.register(data_type)


def get_available_data(material_name: str) -> Dict[str, List[BaseDataType]]:
    """Convenience function to get available data for material"""
    return DataTypeRegistry.get_available_for_material(material_name)
