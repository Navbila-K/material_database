"""
Data Types Package - Extensible plugin system

This package contains all data type implementations.
Each data type knows how to load, display, and plot itself.
"""

from .base_data_type import BaseDataType
from .registry import DataTypeRegistry, register_data_type, get_available_data
from .us_up_experimental import UsUpExperimentalType
from .us_up_model import UsUpModelType

__all__ = [
    'BaseDataType',
    'DataTypeRegistry',
    'register_data_type',
    'get_available_data',
    'UsUpExperimentalType',
    'UsUpModelType',
]
