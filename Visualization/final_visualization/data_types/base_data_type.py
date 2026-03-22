"""
Base Data Type - Abstract base class for all data types

This provides the plugin interface for extensibility.
All new data types (experimental, models) should inherit from this.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from PyQt6.QtWidgets import QWidget


class BaseDataType(ABC):
    """
    Abstract base class for data types (experimental, models, etc.)
    
    All data types must implement these methods to be compatible
    with the visualization system.
    """
    
    def __init__(self, name: str, category: str):
        """
        Initialize data type
        
        Args:
            name: Display name (e.g., "Us-Up Experiment")
            category: Category ("experimental", "model", etc.)
        """
        self.name = name
        self.category = category
        self.data_cache = {}
    
    @abstractmethod
    def can_load(self, material_name: str) -> bool:
        """
        Check if this data type is available for given material
        
        Args:
            material_name: Material to check
            
        Returns:
            True if data exists, False otherwise
        """
        pass
    
    @abstractmethod
    def load_data(self, material_name: str) -> Dict[str, Any]:
        """
        Load data for given material
        
        Args:
            material_name: Material name
            
        Returns:
            Dictionary with data (structure varies by type)
        """
        pass
    
    @abstractmethod
    def get_plot_data(self, material_name: str) -> Dict[str, Any]:
        """
        Get data formatted for plotting
        
        Args:
            material_name: Material name
            
        Returns:
            Dictionary with x, y, labels, etc. for plotting
        """
        pass
    
    @abstractmethod
    def get_display_widget(self, material_name: str) -> Optional[QWidget]:
        """
        Get widget to display this data in data panel
        
        Args:
            material_name: Material name
            
        Returns:
            QWidget to display, or None
        """
        pass
    
    def get_summary(self, material_name: str) -> str:
        """
        Get text summary of data
        
        Args:
            material_name: Material name
            
        Returns:
            Human-readable summary
        """
        return f"{self.name} data for {material_name}"
    
    def clear_cache(self):
        """Clear cached data"""
        self.data_cache.clear()
