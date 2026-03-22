"""
Final Visualization Package - Ultimate Material Intelligence Hub

This package provides a unified, scalable visualization system that combines:
- Material Comparison (search, multi-select)
- Visualization_New (unified plots, calibration)
- Extensible plugin system for future data types

Structure:
- material_intelligence_hub.py: Main controller
- final_visualization_tab.py: Tab wrapper for main window
- dynamic_data_panel.py: Auto-generating data tree
- data_types/: Plugin system for extensible data types
- components/: Reusable UI components
- managers/: Data and plot managers

Author: Materials Database Team
Date: February 20, 2026
"""

from .material_intelligence_hub import MaterialIntelligenceHub
from .final_visualization_tab import FinalVisualizationTab
from .dynamic_data_panel import DynamicDataPanel

__all__ = ['MaterialIntelligenceHub', 'FinalVisualizationTab', 'DynamicDataPanel']
__version__ = '1.0.0'
