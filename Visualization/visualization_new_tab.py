"""
Visualization New Tab - Complete new visualization interface

This is the main tab that integrates the entire new visualization system.
It replaces the old workflow with a modern, intuitive interface.

Author: Materials Database Team
Date: February 2026
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from gui.components_new.unified_visualization import UnifiedVisualizationWorkspace


class VisualizationNewTab(QWidget):
    """
    Complete new visualization tab
    
    This tab provides:
    - Material selection at top level
    - Unified experimental + model visualization
    - Calibration range awareness
    - Multi-material comparison
    - Professional engineering UI
    """
    
    def __init__(self, db_manager, parent=None):
        """
        Initialize VisualizationNewTab
        
        Args:
            db_manager: Database manager instance (from main application)
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.db_manager = db_manager
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # ============ HEADER (Optional) ============
        header = self._create_header()
        layout.addWidget(header)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # ============ MAIN WORKSPACE ============
        self.workspace = UnifiedVisualizationWorkspace(self.db_manager)
        layout.addWidget(self.workspace, stretch=1)
        
    def _create_header(self) -> QWidget:
        """Create header with title and info"""
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(15, 10, 15, 10)
        header_layout.setSpacing(5)
        
        # Title
        title_label = QLabel("Material Intelligence Platform")
        title_label.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1f77b4;")
        header_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel(
            "Unified visualization with experimental data, model predictions, "
            "and calibration range awareness"
        )
        subtitle_label.setFont(QFont('Arial', 10))
        subtitle_label.setStyleSheet("color: #666;")
        subtitle_label.setWordWrap(True)
        header_layout.addWidget(subtitle_label)
        
        # Set background
        header.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
            }
        """)
        
        return header
        
    def refresh(self):
        """Refresh the tab (called when tab becomes active)"""
        self.workspace.refresh()
        
    def cleanup(self):
        """Cleanup resources when tab is closed"""
        # Clear any cached data
        if hasattr(self.workspace, 'data_manager'):
            self.workspace.data_manager.clear_cache()
