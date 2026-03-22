"""
Unified Visualization Workspace - Main workspace combining all components

This is the central workspace that combines:
- Material selection panel (top)
- Experimental data section (left)
- Model data section (left)
- Unified plot widget (center/right)

Author: Materials Database Team
Date: February 2026
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QFrame, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal

from gui.components_new.material_selection_panel import MaterialSelectionPanel
from gui.components_new.experimental_section import ExperimentalDataSection
from gui.components_new.model_section import ModelDataSection
from gui.components_new.unified_plot_widget import UnifiedPlotWidget

from gui.data.material_data_manager import MaterialDataManager
from gui.data.calibration_manager import CalibrationRangeManager
from gui.state.selection_state import get_selection_state


class UnifiedVisualizationWorkspace(QWidget):
    """
    Complete visualization workspace with integrated components
    
    Layout:
    ┌─────────────────────────────────────────────────────────┐
    │  Material Selection Panel (Search + Chips)              │
    ├─────────────────┬───────────────────────────────────────┤
    │                 │                                       │
    │  Experimental   │                                       │
    │  Data Section   │      Unified Plot Widget              │
    │                 │      (Matplotlib Canvas)              │
    │─────────────────│                                       │
    │                 │                                       │
    │  Model Data     │                                       │
    │  Section        │                                       │
    │                 │                                       │
    └─────────────────┴───────────────────────────────────────┘
    """
    
    def __init__(self, db_manager, parent=None):
        """
        Initialize UnifiedVisualizationWorkspace
        
        Args:
            db_manager: Database manager instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Initialize managers
        self.data_manager = MaterialDataManager(db_manager)
        self.calibration_manager = CalibrationRangeManager(db_manager)
        self.selection_state = get_selection_state()
        
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Setup the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)
        
        # ============ TOP: Material Selection Panel ============
        self.selection_panel = MaterialSelectionPanel(self.data_manager)
        main_layout.addWidget(self.selection_panel)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)
        
        # ============ BOTTOM: Split view (Data sections | Plot) ============
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # LEFT: Data sections (stacked vertically)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        # Experimental data section
        self.experimental_section = ExperimentalDataSection(self.data_manager)
        left_layout.addWidget(self.experimental_section)
        
        # Model data section
        self.model_section = ModelDataSection(self.data_manager)
        left_layout.addWidget(self.model_section)
        
        # Make sections scrollable
        scroll_area = QScrollArea()
        scroll_area.setWidget(left_panel)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setMinimumWidth(350)
        
        splitter.addWidget(scroll_area)
        
        # RIGHT: Unified plot widget
        self.plot_widget = UnifiedPlotWidget(self.calibration_manager)
        splitter.addWidget(self.plot_widget)
        
        # Set initial splitter sizes (30% left, 70% right)
        splitter.setSizes([300, 700])
        splitter.setStretchFactor(0, 0)  # Left panel fixed-ish
        splitter.setStretchFactor(1, 1)  # Plot expands
        
        main_layout.addWidget(splitter, stretch=1)
        
        # Size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
    def _connect_signals(self):
        """Connect signals and slots"""
        # Material selection changes
        self.selection_panel.selection_changed.connect(self._on_materials_changed)
        
        # Experimental data selection
        self.experimental_section.parameter_selected.connect(self._on_experimental_selected)
        
        # Model data selection
        self.model_section.parameter_selected.connect(self._on_model_selected)
        
    def _on_materials_changed(self, materials: list):
        """Handle material selection changes"""
        print(f"[UnifiedViz] Materials changed: {materials}")
        
        # Update data sections
        print(f"[UnifiedViz] Updating experimental section with {len(materials)} materials")
        self.experimental_section.update_materials(materials)
        
        print(f"[UnifiedViz] Updating model section with {len(materials)} materials")
        self.model_section.update_materials(materials)
        
        # Clear plot if no materials selected
        if not materials:
            self.plot_widget.clear_plot()
            print(f"[UnifiedViz] Plot cleared (no materials)")
        else:
            print(f"[UnifiedViz] Materials updated, waiting for parameter selection")
            
    def _on_experimental_selected(self, material: str, parameter: str):
        """
        Handle experimental data selection
        
        Args:
            material: Material name
            parameter: Parameter name
        """
        print(f"[VizNew] Experimental selected: {material} - {parameter}")
        
        try:
            # Load experimental data
            exp_data_list = self.data_manager.get_experimental_data(material)
            print(f"[VizNew] Found {len(exp_data_list)} datasets for {material}")
            
            # Find matching parameter
            exp_data = None
            for data in exp_data_list:
                print(f"[VizNew] Checking parameter: {data.parameter}")
                if data.parameter == parameter:
                    exp_data = data
                    break
                    
            if exp_data:
                print(f"[VizNew] Plotting {len(exp_data.x_values)} points")
                
                # Get material color
                materials = self.selection_state.get_materials()
                material_index = materials.index(material) if material in materials else 0
                from gui.data.plot_config import PlotColors
                color = PlotColors.get_material_color(material_index)
                
                # Plot experimental data
                self.plot_widget.plot_experimental(exp_data, color=color)
                print(f"[VizNew] Plot complete!")
            else:
                print(f"[VizNew] ERROR: No experimental data found for {material} - {parameter}")
                print(f"[VizNew] Available parameters: {[d.parameter for d in exp_data_list]}")
                
        except Exception as e:
            print(f"[VizNew] ERROR plotting experimental data: {e}")
            import traceback
            traceback.print_exc()
            
    def _on_model_selected(self, material: str, model_type: str, parameter: str):
        """
        Handle model data selection
        
        Args:
            material: Material name
            model_type: Model type
            parameter: Parameter name
        """
        try:
            # Load model data
            model_data_list = self.data_manager.get_model_data(material)
            
            # Find matching model and parameter
            model_data = None
            for data in model_data_list:
                if data.model_type == model_type and data.parameter == parameter:
                    model_data = data
                    break
                    
            if model_data:
                # Get material color
                materials = self.selection_state.get_materials()
                material_index = materials.index(material) if material in materials else 0
                from gui.data.plot_config import PlotColors
                color = PlotColors.get_material_color(material_index)
                
                # Plot model data
                self.plot_widget.plot_model(model_data, color=color)
            else:
                print(f"No model data found for {material} - {model_type} - {parameter}")
                
        except Exception as e:
            print(f"Error plotting model data: {e}")
            
    def refresh(self):
        """Refresh all components"""
        materials = self.selection_state.get_materials()
        self._on_materials_changed(materials)
