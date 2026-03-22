"""
Material Intelligence Hub - Ultimate Unified Visualization & Comparison

COMBINES:
1. Material Comparison (search, multi-select, side-by-side)
2. Visualization New (unified plots, calibration ranges)

INTO ONE POWERFUL INTERFACE:
- Search & multi-select materials
- Toggle between Single/Compare/Overlay modes
- Experimental data + Models + Calibration ranges
- Export to multiple formats

Author: Materials Database Team
Date: February 20, 2026
"""

from pathlib import Path
from typing import Dict, List, Optional, Any

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTabWidget, QLabel, QComboBox, QPushButton,
    QFrame, QScrollArea, QButtonGroup, QRadioButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

# Import from Material Comparison
from gui.widgets.material_search_widget import MaterialSearchWidget
from gui.helpers.experimental_data_reader import ExperimentalDataReader
from gui.helpers.xml_model_reader import XMLModelReader

# Import from Visualization New
from gui.components_new.unified_plot_widget import UnifiedPlotWidget
from gui.data.material_data_manager import MaterialDataManager
from gui.data.calibration_manager import CalibrationRangeManager
from gui.state.selection_state import get_selection_state


class MaterialIntelligenceHub(QWidget):
    """
    Ultimate Material Intelligence Hub
    
    Architecture:
    ┌───────────────────────────────────────────────────────────┐
    │  🔍 Material Search + Selection                           │
    │  [Search...] [+ Add] | Selected: [Al ×] [Cu ×] [Steel ×] │
    ├───────────────────────────────────────────────────────────┤
    │  Mode: ○ Single  ● Compare  ○ Overlay  | Chart: [Us-Up▼]│
    ├─────────────────┬─────────────────────────────────────────┤
    │                 │                                         │
    │  📊 Data Panel  │       📈 Visualization Area             │
    │                 │                                         │
    │  Experimental   │    (Matplotlib/Interactive Plots)       │
    │  • Material 1   │                                         │
    │  • Material 2   │    • Experimental data points           │
    │                 │    • Model curves                       │
    │  Models         │    • Calibration ranges (shaded)       │
    │  • EOS          │    • Legend (interactive)               │
    │  • Strength     │                                         │
    │                 │    [Export PNG] [Export PDF] [Excel]    │
    └─────────────────┴─────────────────────────────────────────┘
    
    Features:
    - Search & multi-select materials (from Comparison)
    - Unified visualization (from Viz_New)
    - Three modes: Single, Compare, Overlay
    - Calibration range awareness
    - Export to multiple formats
    """
    
    material_added = pyqtSignal(str)  # Emitted when material is added
    material_removed = pyqtSignal(str)  # Emitted when material is removed
    
    def __init__(self, db_manager, querier, parent=None):
        super().__init__(parent)
        
        self.db_manager = db_manager
        self.querier = querier
        
        # Initialize data managers
        self.data_manager = MaterialDataManager(db_manager)
        self.calibration_manager = CalibrationRangeManager(db_manager)
        self.selection_state = get_selection_state()
        
        # Initialize readers (from Material Comparison)
        self.experimental_data_path = Path(__file__).parent.parent.parent / "Experimental_data"
        self.xml_models_path = Path(__file__).parent.parent.parent / "XML_Finalized_Structure"
        
        self.exp_reader = None
        self.xml_model_reader = None
        self._init_readers()
        
        # Track selected materials
        self.selected_materials: List[str] = []
        self.material_colors: Dict[str, str] = {}
        
        # Current mode
        self.current_mode = "compare"  # single, compare, overlay
        
        # Initialize and register data types
        self._init_data_types()
        
        self._setup_ui()
        self._connect_signals()
    
    def _init_data_types(self):
        """Initialize and register all data types"""
        from .data_types import DataTypeRegistry, UsUpExperimentalType, UsUpModelType
        
        # Clear any existing registrations
        DataTypeRegistry.clear()
        
        # Register Us-Up data types
        us_up_exp = UsUpExperimentalType(self.experimental_data_path)
        us_up_model = UsUpModelType(self.xml_models_path)
        
        DataTypeRegistry.register(us_up_exp)
        DataTypeRegistry.register(us_up_model)
        
        print("[Intelligence Hub] ✓ Data types registered:")
        print(DataTypeRegistry.summary())
        
    def _init_readers(self):
        """Initialize data readers"""
        try:
            self.exp_reader = ExperimentalDataReader(self.experimental_data_path)
            print(f"[Intelligence Hub] ✓ Loaded {len(self.exp_reader.datasets)} experimental datasets")
        except Exception as e:
            print(f"[Intelligence Hub] ⚠ Experimental reader failed: {e}")
        
        try:
            self.xml_model_reader = XMLModelReader(self.xml_models_path)
            print(f"[Intelligence Hub] ✓ XML model reader initialized")
        except Exception as e:
            print(f"[Intelligence Hub] ⚠ XML reader failed: {e}")
    
    def _setup_ui(self):
        """Setup the unified interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # ============ HEADER ============
        header = self._create_header()
        layout.addWidget(header)
        
        # ============ MATERIAL SELECTION BAR ============
        selection_bar = self._create_selection_bar()
        layout.addWidget(selection_bar)
        
        # ============ CONTROL PANEL ============
        control_panel = self._create_control_panel()
        layout.addWidget(control_panel)
        
        # ============ MAIN WORKSPACE ============
        workspace = self._create_workspace()
        layout.addWidget(workspace, stretch=1)
    
    def _create_header(self) -> QWidget:
        """Create header with title"""
        header = QWidget()
        header.setStyleSheet("background-color: #f0f4f8; border-radius: 5px;")
        
        layout = QVBoxLayout(header)
        layout.setContentsMargins(15, 10, 15, 10)
        
        title = QLabel("🎯 Material Intelligence Hub")
        title.setFont(QFont('Arial', 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        subtitle = QLabel("Unified Visualization & Comparison Platform - Search, Compare, Analyze")
        subtitle.setFont(QFont('Arial', 10))
        subtitle.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(subtitle)
        
        return header
    
    def _create_selection_bar(self) -> QWidget:
        """Create material selection bar (search + chips)"""
        bar = QWidget()
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Search widget (from Material Comparison)
        search_label = QLabel("🔍 Search Material:")
        layout.addWidget(search_label)
        
        self.search_widget = MaterialSearchWidget()
        self.search_widget.setMaximumWidth(300)
        layout.addWidget(self.search_widget)
        
        add_btn = QPushButton("➕ Add")
        add_btn.setMaximumWidth(80)
        add_btn.clicked.connect(self._on_add_material)
        layout.addWidget(add_btn)
        
        # Separator
        layout.addWidget(QLabel(" | "))
        
        # Selected materials display
        selected_label = QLabel("Selected:")
        layout.addWidget(selected_label)
        
        self.chips_container = QWidget()
        self.chips_layout = QHBoxLayout(self.chips_container)
        self.chips_layout.setContentsMargins(0, 0, 0, 0)
        self.chips_layout.setSpacing(5)
        layout.addWidget(self.chips_container)
        
        layout.addStretch()
        
        return bar
    
    def _create_control_panel(self) -> QWidget:
        """Create control panel (mode selection + chart type)"""
        panel = QWidget()
        panel.setStyleSheet("background-color: #ecf0f1; border-radius: 5px; padding: 10px;")
        
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # ===== VIEW MODE =====
        mode_label = QLabel("View Mode:")
        mode_label.setFont(QFont('Arial', 10, QFont.Weight.Bold))
        layout.addWidget(mode_label)
        
        self.mode_group = QButtonGroup()
        
        self.single_radio = QRadioButton("Single Material")
        self.compare_radio = QRadioButton("Side-by-Side")
        self.overlay_radio = QRadioButton("Overlay")
        
        # Add tooltips
        self.single_radio.setToolTip("View one material in detail")
        self.compare_radio.setToolTip("Compare materials side-by-side in grid")
        self.overlay_radio.setToolTip("Overlay all materials on one plot")
        
        self.mode_group.addButton(self.single_radio, 0)
        self.mode_group.addButton(self.compare_radio, 1)
        self.mode_group.addButton(self.overlay_radio, 2)
        
        self.compare_radio.setChecked(True)  # Default
        
        layout.addWidget(self.single_radio)
        layout.addWidget(self.compare_radio)
        layout.addWidget(self.overlay_radio)
        
        layout.addWidget(QLabel(" | "))
        
        # ===== CHART TYPE =====
        chart_label = QLabel("Chart Type:")
        chart_label.setFont(QFont('Arial', 10, QFont.Weight.Bold))
        layout.addWidget(chart_label)
        
        self.chart_combo = QComboBox()
        self.chart_combo.setToolTip("Select type of plot to display")
        self.chart_combo.addItems([
            "Us-Up (Shock Physics)",
            "Stress-Strain",
            "Pressure-Volume",
            "Temperature-Pressure",
            "Property Table"
        ])
        layout.addWidget(self.chart_combo)
        
        layout.addWidget(QLabel(" | "))
        
        # ===== EXPORT =====
        export_label = QLabel("Export:")
        export_label.setFont(QFont('Arial', 10, QFont.Weight.Bold))
        layout.addWidget(export_label)
        
        self.png_btn = QPushButton("📄 PNG")
        self.pdf_btn = QPushButton("📕 PDF")
        self.excel_btn = QPushButton("📊 Excel")
        
        # Connect export buttons
        self.png_btn.clicked.connect(self._export_png)
        self.pdf_btn.clicked.connect(self._export_pdf)
        self.excel_btn.clicked.connect(self._export_excel)
        
        for btn in [self.png_btn, self.pdf_btn, self.excel_btn]:
            btn.setMaximumWidth(80)
            btn.setToolTip(f"Export current plot as {btn.text().split()[1]}")
            layout.addWidget(btn)
        
        layout.addStretch()
        
        return panel
    
    def _create_workspace(self) -> QWidget:
        """Create main workspace (splitter with data panel + plot)"""
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # ===== LEFT: DATA PANEL =====
        data_panel = self._create_data_panel()
        splitter.addWidget(data_panel)
        
        # ===== RIGHT: PLOT AREA =====
        plot_area = self._create_plot_area()
        splitter.addWidget(plot_area)
        
        # Set initial sizes (30% left, 70% right)
        splitter.setSizes([300, 700])
        
        return splitter
    
    def _create_data_panel(self) -> QWidget:
        """Create data panel (experimental + models)"""
        from .dynamic_data_panel import DynamicDataPanel
        
        # Create dynamic data panel
        self.data_panel = DynamicDataPanel()
        
        # Connect signals
        self.data_panel.data_selected.connect(self._on_data_selected)
        
        return self.data_panel
    
    def _create_plot_area(self) -> QWidget:
        """Create plot area (use PlotManager)"""
        from .plot_manager import PlotManager
        
        # Create plot manager
        self.plot_manager = PlotManager()
        
        return self.plot_manager
    
    def _connect_signals(self):
        """Connect all signals"""
        # Search widget
        self.search_widget.material_selected.connect(self._on_material_searched)
        
        # Mode radio buttons
        self.mode_group.buttonClicked.connect(self._on_mode_changed)
        
        # Chart type
        self.chart_combo.currentTextChanged.connect(self._on_chart_type_changed)
    
    # ========== EVENT HANDLERS ==========
    
    def _on_add_material(self):
        """Add material from search"""
        # Get selected material from search widget
        selected = self.search_widget.get_selected_material()
        if selected and selected not in self.selected_materials:
            self.add_material(selected)
    
    def _on_material_searched(self, material_name: str):
        """Material selected from search widget"""
        if material_name not in self.selected_materials:
            self.add_material(material_name)
    
    def add_material(self, material_name: str):
        """Add material to selection"""
        if material_name in self.selected_materials:
            return
        
        self.selected_materials.append(material_name)
        
        # Assign color
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        color = colors[len(self.selected_materials) % len(colors)]
        self.material_colors[material_name] = color
        
        # Create chip
        self._add_chip(material_name, color)
        
        # Emit signal
        self.material_added.emit(material_name)
        
        # Update plot
        self._update_visualization()
        
        print(f"[Intelligence Hub] ✓ Added material: {material_name}")
    
    def _add_chip(self, material_name: str, color: str):
        """Add material chip to selection bar"""
        chip = QWidget()
        chip.setStyleSheet(f"""
            background-color: {color};
            color: white;
            border-radius: 12px;
            padding: 5px 10px;
        """)
        
        chip_layout = QHBoxLayout(chip)
        chip_layout.setContentsMargins(5, 2, 5, 2)
        chip_layout.setSpacing(5)
        
        label = QLabel(material_name)
        label.setFont(QFont('Arial', 9, QFont.Weight.Bold))
        chip_layout.addWidget(label)
        
        remove_btn = QPushButton("×")
        remove_btn.setMaximumSize(20, 20)
        remove_btn.setStyleSheet("background: transparent; color: white; border: none; font-size: 16px;")
        remove_btn.clicked.connect(lambda: self.remove_material(material_name))
        chip_layout.addWidget(remove_btn)
        
        self.chips_layout.addWidget(chip)
        chip.setProperty('material_name', material_name)
    
    def remove_material(self, material_name: str):
        """Remove material from selection"""
        if material_name not in self.selected_materials:
            return
        
        self.selected_materials.remove(material_name)
        del self.material_colors[material_name]
        
        # Remove chip
        for i in range(self.chips_layout.count()):
            widget = self.chips_layout.itemAt(i).widget()
            if widget and widget.property('material_name') == material_name:
                widget.deleteLater()
                break
        
        # Emit signal
        self.material_removed.emit(material_name)
        
        # Remove from plot manager
        if hasattr(self, 'plot_manager'):
            self.plot_manager.remove_material_data(material_name)
        
        # Update data panel
        if hasattr(self, 'data_panel'):
            self.data_panel.set_materials(self.selected_materials)
        
        print(f"[Intelligence Hub] ✓ Removed material: {material_name}")
    
    def _on_mode_changed(self):
        """Handle mode change"""
        if self.single_radio.isChecked():
            self.current_mode = "single"
        elif self.compare_radio.isChecked():
            self.current_mode = "compare"
        else:
            self.current_mode = "overlay"
        
        print(f"[Intelligence Hub] Mode changed to: {self.current_mode}")
        
        # Update plot manager
        if hasattr(self, 'plot_manager'):
            self.plot_manager.set_mode(self.current_mode)
    
    def _on_chart_type_changed(self, chart_type: str):
        """Handle chart type change"""
        print(f"[Intelligence Hub] Chart type changed to: {chart_type}")
        
        # Update plot manager
        if hasattr(self, 'plot_manager'):
            self.plot_manager.set_chart_type(chart_type)
    
    def _on_data_selected(self, material: str, category: str, data_type: str):
        """Handle data item selection in data panel"""
        print(f"[Intelligence Hub] Data selected: {material}/{category}/{data_type}")
        # TODO: Highlight in plot or show details
    
    def _update_visualization(self):
        """Update the visualization based on current state"""
        if not self.selected_materials:
            print("[Intelligence Hub] No materials selected")
            if hasattr(self, 'data_panel'):
                self.data_panel.clear()
            if hasattr(self, 'plot_manager'):
                self.plot_manager.clear_plot()
            return
        
        print(f"[Intelligence Hub] Updating visualization:")
        print(f"  Materials: {self.selected_materials}")
        print(f"  Mode: {self.current_mode}")
        print(f"  Chart: {self.chart_combo.currentText()}")
        
        # Update data panel with selected materials
        if hasattr(self, 'data_panel'):
            self.data_panel.set_materials(self.selected_materials)
        
        # Load and plot data for each material
        if hasattr(self, 'plot_manager'):
            for material_name in self.selected_materials:
                self._load_and_plot_material(material_name)
    
    def _load_and_plot_material(self, material_name: str):
        """Load data for material and add to plot"""
        from .data_types import DataTypeRegistry
        
        # Get experimental data
        exp_data = None
        exp_type = DataTypeRegistry.get_by_name("experimental", "Us-Up Experiment")
        if exp_type and exp_type.can_load(material_name):
            exp_data = exp_type.load_data(material_name)
            print(f"  ✓ Loaded experimental data for {material_name}")
        
        # Get model data
        model_data = None
        model_type = DataTypeRegistry.get_by_name("model", "Us-Up Model")
        if model_type and model_type.can_load(material_name):
            model_data = model_type.load_data(material_name)
            print(f"  ✓ Loaded model data for {material_name}")
        
        # Get color for this material
        color = self.material_colors.get(material_name)
        
        # Add to plot manager
        if hasattr(self, 'plot_manager'):
            self.plot_manager.add_material_data(
                material_name,
                exp_data=exp_data,
                model_data=model_data,
                color=color
            )
    
    def refresh(self):
        """Refresh the hub"""
        self._update_visualization()
    
    # ===== EXPORT METHODS =====
    
    def _export_png(self):
        """Export current plot as PNG"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        
        if not hasattr(self, 'plot_manager') or not self.selected_materials:
            QMessageBox.warning(self, "Export Error", "No plot to export. Please add materials first.")
            return
        
        # Open file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Plot as PNG",
            f"plot_{self.current_mode}_{len(self.selected_materials)}_materials.png",
            "PNG Files (*.png);;All Files (*)"
        )
        
        if file_path:
            try:
                # Export from plot manager
                self.plot_manager.figure.savefig(
                    file_path,
                    dpi=300,
                    bbox_inches='tight',
                    facecolor='white'
                )
                QMessageBox.information(self, "Export Success", f"Plot saved to:\n{file_path}")
                print(f"[Intelligence Hub] ✓ Exported PNG: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export PNG:\n{str(e)}")
                print(f"[Intelligence Hub] ✗ PNG export failed: {e}")
    
    def _export_pdf(self):
        """Export current plot as PDF"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        
        if not hasattr(self, 'plot_manager') or not self.selected_materials:
            QMessageBox.warning(self, "Export Error", "No plot to export. Please add materials first.")
            return
        
        # Open file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Plot as PDF",
            f"plot_{self.current_mode}_{len(self.selected_materials)}_materials.pdf",
            "PDF Files (*.pdf);;All Files (*)"
        )
        
        if file_path:
            try:
                # Export from plot manager
                self.plot_manager.figure.savefig(
                    file_path,
                    format='pdf',
                    bbox_inches='tight'
                )
                QMessageBox.information(self, "Export Success", f"Plot saved to:\n{file_path}")
                print(f"[Intelligence Hub] ✓ Exported PDF: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export PDF:\n{str(e)}")
                print(f"[Intelligence Hub] ✗ PDF export failed: {e}")
    
    def _export_excel(self):
        """Export current data as Excel"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        import pandas as pd
        
        if not self.selected_materials:
            QMessageBox.warning(self, "Export Error", "No data to export. Please add materials first.")
            return
        
        # Open file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Data as Excel",
            f"data_{len(self.selected_materials)}_materials.xlsx",
            "Excel Files (*.xlsx);;All Files (*)"
        )
        
        if file_path:
            try:
                from .data_types import DataTypeRegistry
                
                # Create Excel writer
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    for material_name in self.selected_materials:
                        # Get experimental data
                        exp_type = DataTypeRegistry.get_by_name("experimental", "Us-Up Experiment")
                        if exp_type and exp_type.can_load(material_name):
                            exp_data = exp_type.load_data(material_name)
                            if exp_data and exp_data.get('datasets'):
                                # Combine all datasets for this material
                                all_up = []
                                all_us = []
                                all_source = []
                                
                                for i, dataset in enumerate(exp_data['datasets']):
                                    up_vals = dataset['Up']
                                    us_vals = dataset['Us']
                                    source = dataset['file']
                                    
                                    all_up.extend(up_vals)
                                    all_us.extend(us_vals)
                                    all_source.extend([source] * len(up_vals))
                                
                                # Create DataFrame
                                df = pd.DataFrame({
                                    'Up (km/s)': all_up,
                                    'Us (km/s)': all_us,
                                    'Source': all_source
                                })
                                
                                # Safe sheet name (Excel limits to 31 chars)
                                sheet_name = material_name[:31]
                                df.to_excel(writer, sheet_name=sheet_name, index=False)
                        
                        # Get model data
                        model_type = DataTypeRegistry.get_by_name("model", "Us-Up Model")
                        if model_type and model_type.can_load(material_name):
                            model_data = model_type.load_data(material_name)
                            if model_data and 'C0' in model_data:
                                # Create model DataFrame
                                df_model = pd.DataFrame({
                                    'Parameter': ['C0 (km/s)', 'S (dimensionless)'],
                                    'Value': [model_data['C0'], model_data['S']]
                                })
                                sheet_name = f"{material_name}_model"[:31]
                                df_model.to_excel(writer, sheet_name=sheet_name, index=False)
                
                QMessageBox.information(self, "Export Success", f"Data saved to:\n{file_path}")
                print(f"[Intelligence Hub] ✓ Exported Excel: {file_path}")
            except ImportError:
                QMessageBox.critical(
                    self, 
                    "Export Error", 
                    "Excel export requires 'openpyxl' and 'pandas' packages.\n"
                    "Install with: pip install pandas openpyxl"
                )
                print("[Intelligence Hub] ✗ Excel export requires pandas and openpyxl")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export Excel:\n{str(e)}")
                print(f"[Intelligence Hub] ✗ Excel export failed: {e}")
    
    def cleanup(self):
        """Cleanup resources"""
        self.selected_materials.clear()
        self.material_colors.clear()
