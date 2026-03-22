"""
Final Visualization Tab - Wrapper for Material Intelligence Hub

This provides a clean tab interface for the main window.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from .material_intelligence_hub import MaterialIntelligenceHub


class FinalVisualizationTab(QWidget):
    """
    Final visualization tab for main window
    
    This is a simple wrapper around MaterialIntelligenceHub
    to provide a clean interface for tab integration.
    """
    
    def __init__(self, db_manager, querier, parent=None):
        super().__init__(parent)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Add intelligence hub
        self.hub = MaterialIntelligenceHub(db_manager, querier, self)
        layout.addWidget(self.hub)
    
    def refresh(self):
        """Refresh the tab (called when tab becomes active)"""
        if hasattr(self.hub, 'refresh'):
            self.hub.refresh()
    
    def cleanup(self):
        """Cleanup resources when tab is closed"""
        if hasattr(self.hub, 'cleanup'):
            self.hub.cleanup()
