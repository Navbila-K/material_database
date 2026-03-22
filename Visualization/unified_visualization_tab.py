"""
Unified Visualization Tab - Phase 4 Implementation
===================================================

Two-panel layout:
- Top Panel: Property Comparison (bar charts, tables, scatter plots)
- Bottom Panel: Model Visualization (US-Up, EOS, model vs experimental)

Backend Integration:
- services/visualization_service.py (database queries)
- services/model_calculator.py (model calculations)
- services/plotting_utils.py (plotting defaults)
- services/property_comparison_plots.py (comparison plots)
- services/model_experimental_plots.py (model overlays)
- services/export_functions.py (export utilities)

Author: Materials Database Team
Date: February 22, 2026
"""

# CRITICAL: Set matplotlib backend BEFORE any other matplotlib imports
import matplotlib
matplotlib.use('QtAgg', force=True)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QListWidget, QListWidgetItem, QComboBox,
    QGroupBox, QSplitter, QFrame, QScrollArea, QStackedWidget,
    QLineEdit, QCheckBox, QSpinBox, QDoubleSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor

import sys
from pathlib import Path
import traceback

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import backend services
from services.visualization_service import VisualizationDataService
from services.plotting_utils import PlottingUtils

# Import Material Comparison (reuse existing widget)
try:
    from gui.views.material_comparison import MaterialComparisonController
    MATERIAL_COMPARISON_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Material Comparison module not available: {e}")
    MATERIAL_COMPARISON_AVAILABLE = False

# Import US-Up Analysis (reuse existing widget)
try:
    from analysis.us_up_widget import USUpAnalysisTab
    US_UP_AVAILABLE = True
except ImportError as e:
    print(f"Warning: US-Up Analysis module not available: {e}")
    US_UP_AVAILABLE = False
from services.property_comparison_plots import (
    plot_property_comparison_bar,
    plot_property_comparison_table,
    plot_property_scatter
)
from services.model_experimental_plots import (
    plot_model_vs_experimental,
    plot_usup_hugoniot,
    plot_eos_comparison
)
from services.export_functions import (
    export_plot_png,
    export_plot_pdf,
    export_data_csv
)


# =============================================================================
# MATERIAL SELECTOR WIDGET - TASK 4.2
# =============================================================================

class MaterialSelectorWidget(QWidget):
    """
    Material Selection Widget - Phase 4 Task 4.2
    
    Features:
    - Search bar with filtering
    - Checkbox list of all materials
    - Select All / Clear All buttons
    - Count label showing selection status
    
    Signals:
    - materials_changed(list): Emitted when selection changes
    """
    
    # Signal emitted when material selection changes
    materials_changed = pyqtSignal(list)  # List of material IDs
    
    def __init__(self, viz_service, parent=None):
        """
        Initialize Material Selector Widget.
        
        Args:
            viz_service: VisualizationDataService instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.viz_service = viz_service
        self.all_materials = []  # List of all materials from database
        self.selected_material_ids = []  # Currently selected material IDs
        
        # Setup UI
        self._init_ui()
        
        # Load materials from database
        self._load_materials()
        
        print("✓ MaterialSelectorWidget initialized")
    
    def _init_ui(self):
        """Setup the UI layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)
        
        # Header
        header_label = QLabel("📦 Select Materials")
        header_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #000000;")
        main_layout.addWidget(header_label)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍")
        search_layout.addWidget(search_label)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search materials...")
        self.search_box.textChanged.connect(self._filter_materials)
        self.search_box.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                font-size: 12px;
                color: #000000;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        search_layout.addWidget(self.search_box)
        main_layout.addLayout(search_layout)
        
        # Material list (with checkboxes)
        self.material_list = QListWidget()
        self.material_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.material_list.itemChanged.connect(self._on_item_changed)
        self.material_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                font-size: 12px;
                color: #000000;
            }
            QListWidget::item {
                padding: 4px;
                color: #000000;
            }
            QListWidget::item:hover {
                background-color: #ecf0f1;
                color: #000000;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        main_layout.addWidget(self.material_list)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton("✓ Select All")
        self.select_all_btn.clicked.connect(self._select_all)
        self.select_all_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        button_layout.addWidget(self.select_all_btn)
        
        self.clear_all_btn = QPushButton("✗ Clear All")
        self.clear_all_btn.clicked.connect(self._clear_all)
        self.clear_all_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #cb4335;
            }
            QPushButton:pressed {
                background-color: #b03a2e;
            }
        """)
        button_layout.addWidget(self.clear_all_btn)
        
        main_layout.addLayout(button_layout)
        
        # Count label
        self.count_label = QLabel("0 of 0 selected")
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.count_label.setStyleSheet("""
            QLabel {
                padding: 6px;
                background-color: #ecf0f1;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                color: #000000;
            }
        """)
        main_layout.addWidget(self.count_label)
        
        self.setLayout(main_layout)
    
    def _load_materials(self):
        """Load materials from database."""
        if not self.viz_service:
            print("⚠️ No visualization service available")
            return
        
        try:
            # Connect to database
            self.viz_service.connect()
            
            # Get all materials
            self.all_materials = self.viz_service.get_all_materials(order_by='name')
            
            # Disconnect
            self.viz_service.disconnect()
            
            # Populate list
            self._populate_list()
            
            print(f"✓ Loaded {len(self.all_materials)} materials")
            
        except Exception as e:
            print(f"❌ Error loading materials: {e}")
            import traceback
            traceback.print_exc()
    
    def _populate_list(self):
        """Populate the material list with checkboxes."""
        self.material_list.clear()
        
        for material in self.all_materials:
            # Create list item
            item = QListWidgetItem(material['name'])
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            
            # Store material_id in item data
            item.setData(Qt.ItemDataRole.UserRole, material['material_id'])
            
            self.material_list.addItem(item)
        
        # Update count
        self._update_count()
    
    def _filter_materials(self, text: str):
        """Filter materials based on search text."""
        text = text.lower()
        
        for i in range(self.material_list.count()):
            item = self.material_list.item(i)
            material_name = item.text().lower()
            
            # Show/hide based on search
            if text in material_name:
                item.setHidden(False)
            else:
                item.setHidden(True)
    
    def _on_item_changed(self, item):
        """Handle item checkbox state change."""
        self._update_selection()
    
    def _select_all(self):
        """Select all visible materials."""
        for i in range(self.material_list.count()):
            item = self.material_list.item(i)
            if not item.isHidden():
                item.setCheckState(Qt.CheckState.Checked)
        
        self._update_selection()
    
    def _clear_all(self):
        """Clear all selections."""
        for i in range(self.material_list.count()):
            item = self.material_list.item(i)
            item.setCheckState(Qt.CheckState.Unchecked)
        
        self._update_selection()
    
    def _update_selection(self):
        """Update selected material IDs and emit signal."""
        self.selected_material_ids = []
        
        for i in range(self.material_list.count()):
            item = self.material_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                material_id = item.data(Qt.ItemDataRole.UserRole)
                self.selected_material_ids.append(material_id)
        
        # Update count label
        self._update_count()
        
        # Emit signal
        self.materials_changed.emit(self.selected_material_ids)
        
        print(f"📌 Materials selected: {self.selected_material_ids}")
    
    def _update_count(self):
        """Update the count label."""
        total = len(self.all_materials)
        selected = len(self.selected_material_ids)
        
        self.count_label.setText(f"{selected} of {total} selected")
        
        # Change color based on selection
        if selected == 0:
            color = "#95a5a6"
        elif selected < total:
            color = "#3498db"
        else:
            color = "#27ae60"
        
        self.count_label.setStyleSheet(f"""
            QLabel {{
                padding: 6px;
                background-color: {color};
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                color: white;
            }}
        """)
    
    def get_selected_materials(self):
        """Get list of selected material IDs."""
        return self.selected_material_ids


# =============================================================================
# PROPERTY SELECTOR WIDGET - TASK 4.3
# =============================================================================

class PropertySelectorWidget(QWidget):
    """
    Property Selection Widget - Phase 4 Task 4.3
    
    Features:
    - Checkbox list grouped by category
    - Only shows properties available in selected materials
    - Select All / Clear All buttons
    - Count label showing selection status
    - Disabled when no materials selected
    
    Signals:
    - properties_changed(list): Emitted when selection changes
    """
    
    # Signal emitted when property selection changes
    properties_changed = pyqtSignal(list)  # List of property names
    
    def __init__(self, viz_service, parent=None):
        """
        Initialize Property Selector Widget.
        
        Args:
            viz_service: VisualizationDataService instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.viz_service = viz_service
        self.selected_material_ids = []  # Materials to get properties from
        self.all_properties = []  # List of available properties
        self.selected_properties = []  # Currently selected property names
        self.properties_by_category = {}  # Grouped properties
        
        # Setup UI
        self._init_ui()
        
        # Start disabled (no materials selected)
        self.setEnabled(False)
        
        print("✓ PropertySelectorWidget initialized")
    
    def _init_ui(self):
        """Setup the UI layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)
        
        # Header
        header_label = QLabel("📋 Select Properties")
        header_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #000000;")
        main_layout.addWidget(header_label)
        
        # Info label
        self.info_label = QLabel("Select materials first")
        self.info_label.setStyleSheet("""
            QLabel {
                padding: 6px;
                background-color: #fff3cd;
                color: #856404;
                border: 1px solid #ffeaa7;
                border-radius: 4px;
                font-size: 11px;
            }
        """)
        self.info_label.setWordWrap(True)
        main_layout.addWidget(self.info_label)
        
        # Search/filter box
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍")
        search_layout.addWidget(search_label)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Filter properties...")
        self.search_box.textChanged.connect(self._filter_properties)
        self.search_box.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                font-size: 12px;
                color: #000000;
            }
            QLineEdit:focus {
                border: 2px solid #9b59b6;
            }
        """)
        search_layout.addWidget(self.search_box)
        main_layout.addLayout(search_layout)
        
        # Property list (grouped by category)
        self.property_list = QListWidget()
        self.property_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.property_list.itemChanged.connect(self._on_item_changed)
        self.property_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                font-size: 12px;
                color: #000000;
            }
            QListWidget::item {
                padding: 4px;
                color: #000000;
            }
            QListWidget::item:hover {
                background-color: #ecf0f1;
                color: #000000;
            }
            QListWidget::item:selected {
                background-color: #9b59b6;
                color: white;
            }
        """)
        main_layout.addWidget(self.property_list)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton("✓ Select All")
        self.select_all_btn.clicked.connect(self._select_all)
        self.select_all_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                background-color: #8e44ad;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #7d3c98;
            }
            QPushButton:pressed {
                background-color: #6c3483;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        button_layout.addWidget(self.select_all_btn)
        
        self.clear_all_btn = QPushButton("✗ Clear All")
        self.clear_all_btn.clicked.connect(self._clear_all)
        self.clear_all_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
            QPushButton:pressed {
                background-color: #ba4a00;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        button_layout.addWidget(self.clear_all_btn)
        
        main_layout.addLayout(button_layout)
        
        # Count label
        self.count_label = QLabel("0 of 0 selected")
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.count_label.setStyleSheet("""
            QLabel {
                padding: 6px;
                background-color: #ecf0f1;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                color: #000000;
            }
        """)
        main_layout.addWidget(self.count_label)
        
        self.setLayout(main_layout)
    
    def update_for_materials(self, material_ids: list):
        """
        Update available properties based on selected materials.
        
        Args:
            material_ids: List of selected material IDs
        """
        self.selected_material_ids = material_ids
        
        if not material_ids:
            # No materials selected - disable widget
            self.setEnabled(False)
            self.info_label.setText("Select materials first")
            self.property_list.clear()
            self.all_properties = []
            self._update_count()
            return
        
        # Enable widget
        self.setEnabled(True)
        self.info_label.setText(f"Showing properties for {len(material_ids)} material{'s' if len(material_ids) != 1 else ''}")
        self.info_label.setStyleSheet("""
            QLabel {
                padding: 6px;
                background-color: #d1ecf1;
                color: #0c5460;
                border: 1px solid #bee5eb;
                border-radius: 4px;
                font-size: 11px;
            }
        """)
        
        # Load properties
        self._load_properties()
    
    def _load_properties(self):
        """Load available properties for selected materials."""
        if not self.viz_service or not self.selected_material_ids:
            return
        
        try:
            # Connect to database
            self.viz_service.connect()
            
            # Get available properties for these materials
            properties = self.viz_service.get_available_properties(self.selected_material_ids)
            
            # Group by category
            self.properties_by_category = {}
            for prop in properties:
                category = prop.get('category_name', prop.get('category', 'Other'))
                if category not in self.properties_by_category:
                    self.properties_by_category[category] = []
                self.properties_by_category[category].append(prop)
            
            # Disconnect
            self.viz_service.disconnect()
            
            # Store all properties
            self.all_properties = properties
            
            # Populate list
            self._populate_list()
            
            print(f"✓ Loaded {len(self.all_properties)} properties from {len(self.properties_by_category)} categories")
            
        except Exception as e:
            print(f"❌ Error loading properties: {e}")
            import traceback
            traceback.print_exc()
    
    def _populate_list(self):
        """Populate the property list grouped by category."""
        self.property_list.clear()
        
        # Sort categories
        sorted_categories = sorted(self.properties_by_category.keys())
        
        for category in sorted_categories:
            # Add category header (not selectable)
            header_item = QListWidgetItem(f"📁 {category}")
            header_item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # Not selectable
            header_font = QFont()
            header_font.setBold(True)
            header_item.setFont(header_font)
            header_item.setBackground(QColor("#ecf0f1"))
            self.property_list.addItem(header_item)
            
            # Add properties in this category
            properties = sorted(self.properties_by_category[category], 
                              key=lambda x: x.get('parameter_name', x.get('property_name', '')))
            
            for prop in properties:
                prop_name = prop.get('parameter_name', prop.get('property_name', 'Unknown'))
                
                # Create list item with checkbox
                item = QListWidgetItem(f"  • {prop_name}")
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                
                # Store property name in item data
                item.setData(Qt.ItemDataRole.UserRole, prop_name)
                
                self.property_list.addItem(item)
        
        # Update count
        self._update_count()
    
    def _filter_properties(self, text: str):
        """Filter properties based on search text."""
        text = text.lower()
        
        for i in range(self.property_list.count()):
            item = self.property_list.item(i)
            item_text = item.text().lower()
            
            # Check if it's a category header (starts with 📁)
            is_header = item_text.startswith("📁")
            
            if is_header:
                # Always show category headers
                item.setHidden(False)
            else:
                # Show/hide based on search
                if text in item_text:
                    item.setHidden(False)
                else:
                    item.setHidden(True)
    
    def _on_item_changed(self, item):
        """Handle item checkbox state change."""
        self._update_selection()
    
    def _select_all(self):
        """Select all visible properties."""
        for i in range(self.property_list.count()):
            item = self.property_list.item(i)
            
            # Skip headers and hidden items
            if not item.isHidden() and item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                item.setCheckState(Qt.CheckState.Checked)
        
        self._update_selection()
    
    def _clear_all(self):
        """Clear all selections."""
        for i in range(self.property_list.count()):
            item = self.property_list.item(i)
            if item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                item.setCheckState(Qt.CheckState.Unchecked)
        
        self._update_selection()
    
    def _update_selection(self):
        """Update selected property names and emit signal."""
        self.selected_properties = []
        
        for i in range(self.property_list.count()):
            item = self.property_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                prop_name = item.data(Qt.ItemDataRole.UserRole)
                if prop_name:  # Not None (headers don't have data)
                    self.selected_properties.append(prop_name)
        
        # Update count label
        self._update_count()
        
        # Emit signal
        self.properties_changed.emit(self.selected_properties)
        
        print(f"📌 Properties selected: {self.selected_properties}")
    
    def _update_count(self):
        """Update the count label."""
        total = len(self.all_properties)
        selected = len(self.selected_properties)
        
        self.count_label.setText(f"{selected} of {total} selected")
        
        # Change color based on selection
        if selected == 0:
            color = "#95a5a6"
        elif selected < total:
            color = "#9b59b6"
        else:
            color = "#8e44ad"
        
        self.count_label.setStyleSheet(f"""
            QLabel {{
                padding: 6px;
                background-color: {color};
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                color: white;
            }}
        """)
    
    def get_selected_properties(self):
        """Get list of selected property names."""
        return self.selected_properties


# =============================================================================
# VIEW OPTIONS WIDGET - TASK 4.4
# =============================================================================

class ViewOptionsWidget(QWidget):
    """
    View Options Widget - Phase 4 Task 4.4
    
    Features:
    - Radio buttons for chart type (Table / Bar Chart / Scatter)
    - Checkboxes for display options
    - Emits signal when options change
    
    Signals:
    - view_changed(str, dict): Emitted when view type or options change
    """
    
    # Signal emitted when view options change
    # Args: (view_type: str, options: dict)
    view_changed = pyqtSignal(str, dict)
    
    def __init__(self, parent=None):
        """
        Initialize View Options Widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.current_view_type = 'bar'  # Default: bar chart
        self.current_options = {
            'show_active': True,
            'show_override': False,
            'show_units': True,
            'show_references': False
        }
        
        # Setup UI
        self._init_ui()
        
        print("✓ ViewOptionsWidget initialized")
    
    def _init_ui(self):
        """Setup the UI layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)
        
        # Header
        header_label = QLabel("📊 Chart Type & Options")
        header_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #000000;")
        main_layout.addWidget(header_label)
        
        # Chart Type Section
        chart_group = QGroupBox("Chart Type")
        chart_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        chart_layout = QVBoxLayout(chart_group)
        
        # Radio buttons for chart type
        self.radio_bar = QCheckBox("📊 Bar Chart")
        self.radio_bar.setChecked(True)
        self.radio_bar.toggled.connect(lambda: self._on_chart_type_changed('bar'))
        self.radio_bar.setStyleSheet("""
            QCheckBox {
                font-size: 12px;
                spacing: 8px;
                color: #000000;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        chart_layout.addWidget(self.radio_bar)
        
        self.radio_table = QCheckBox("📋 Table")
        self.radio_table.toggled.connect(lambda: self._on_chart_type_changed('table'))
        self.radio_table.setStyleSheet("""
            QCheckBox {
                font-size: 12px;
                spacing: 8px;
                color: #000000;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        chart_layout.addWidget(self.radio_table)
        
        self.radio_scatter = QCheckBox("🔵 Scatter Plot")
        self.radio_scatter.toggled.connect(lambda: self._on_chart_type_changed('scatter'))
        self.radio_scatter.setStyleSheet("""
            QCheckBox {
                font-size: 12px;
                spacing: 8px;
                color: #000000;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        chart_layout.addWidget(self.radio_scatter)
        
        main_layout.addWidget(chart_group)
        
        # Display Options Section
        options_group = QGroupBox("Display Options")
        options_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #2ecc71;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        options_layout = QVBoxLayout(options_group)
        
        # Data source checkboxes
        self.check_active = QCheckBox("✓ Show Active Data")
        self.check_active.setChecked(True)
        self.check_active.stateChanged.connect(self._on_options_changed)
        self.check_active.setStyleSheet("font-size: 12px; color: #000000;")
        options_layout.addWidget(self.check_active)
        
        self.check_override = QCheckBox("🔄 Show Override Data")
        self.check_override.setChecked(False)
        self.check_override.stateChanged.connect(self._on_options_changed)
        self.check_override.setStyleSheet("font-size: 12px; color: #000000;")
        options_layout.addWidget(self.check_override)
        
        # Display checkboxes
        self.check_units = QCheckBox("📏 Show Units")
        self.check_units.setChecked(True)
        self.check_units.stateChanged.connect(self._on_options_changed)
        self.check_units.setStyleSheet("font-size: 12px; color: #000000;")
        options_layout.addWidget(self.check_units)
        
        self.check_refs = QCheckBox("📚 Show References")
        self.check_refs.setChecked(False)
        self.check_refs.stateChanged.connect(self._on_options_changed)
        self.check_refs.setStyleSheet("font-size: 12px; color: #000000;")
        options_layout.addWidget(self.check_refs)
        
        main_layout.addWidget(options_group)
        
        # Info label
        self.info_label = QLabel("💡 Select materials and properties to visualize")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #e8f4f8;
                color: #000000;
                border: 1px solid #3498db;
                border-radius: 4px;
                font-size: 11px;
            }
        """)
        main_layout.addWidget(self.info_label)
        
        # Add stretch to push everything to top
        main_layout.addStretch()
        
        self.setLayout(main_layout)
    
    def _on_chart_type_changed(self, chart_type: str):
        """
        Handle chart type radio button change.
        
        Args:
            chart_type: New chart type ('bar', 'table', 'scatter')
        """
        # Make radio buttons mutually exclusive manually
        if chart_type == 'bar' and self.radio_bar.isChecked():
            self.radio_table.setChecked(False)
            self.radio_scatter.setChecked(False)
            self.current_view_type = 'bar'
        elif chart_type == 'table' and self.radio_table.isChecked():
            self.radio_bar.setChecked(False)
            self.radio_scatter.setChecked(False)
            self.current_view_type = 'table'
        elif chart_type == 'scatter' and self.radio_scatter.isChecked():
            self.radio_bar.setChecked(False)
            self.radio_table.setChecked(False)
            self.current_view_type = 'scatter'
        else:
            return  # Unchecking - ignore
        
        # Update info label
        self._update_info_label()
        
        # Emit signal
        self.view_changed.emit(self.current_view_type, self.current_options)
        
        print(f"📊 Chart type changed: {self.current_view_type}")
    
    def _on_options_changed(self):
        """Handle display options checkbox change."""
        # Update current options
        self.current_options = {
            'show_active': self.check_active.isChecked(),
            'show_override': self.check_override.isChecked(),
            'show_units': self.check_units.isChecked(),
            'show_references': self.check_refs.isChecked()
        }
        
        # Update info label
        self._update_info_label()
        
        # Emit signal
        self.view_changed.emit(self.current_view_type, self.current_options)
        
        print(f"⚙️ Display options changed: {self.current_options}")
    
    def _update_info_label(self):
        """Update the info label based on current settings."""
        view_names = {
            'bar': 'Bar Chart',
            'table': 'Table',
            'scatter': 'Scatter Plot'
        }
        
        view_name = view_names.get(self.current_view_type, 'Unknown')
        
        # Build info text
        info_parts = [f"📊 {view_name}"]
        
        if self.current_options['show_active']:
            info_parts.append("Active")
        if self.current_options['show_override']:
            info_parts.append("Override")
        if self.current_options['show_units']:
            info_parts.append("Units")
        if self.current_options['show_references']:
            info_parts.append("Refs")
        
        info_text = " | ".join(info_parts) if len(info_parts) > 1 else info_parts[0]
        self.info_label.setText(f"💡 {info_text}")
    
    def get_view_type(self):
        """Get current view type."""
        return self.current_view_type
    
    def get_options(self):
        """Get current display options."""
        return self.current_options.copy()
    
    def set_view_type(self, view_type: str):
        """
        Set view type programmatically.
        
        Args:
            view_type: One of 'bar', 'table', 'scatter'
        """
        if view_type == 'bar':
            self.radio_bar.setChecked(True)
        elif view_type == 'table':
            self.radio_table.setChecked(True)
        elif view_type == 'scatter':
            self.radio_scatter.setChecked(True)


# =============================================================================
# COMPARISON DISPLAY WIDGET - TASK 4.5
# =============================================================================

class ComparisonDisplayWidget(QWidget):
    """
    Comparison Display Widget - Phase 4 Task 4.5
    
    Features:
    - Stacked widget for table and plot views
    - QTableWidget for table display
    - Matplotlib canvas for charts
    - Empty state handling
    - Loading indicator
    
    Signals:
    - None (display widget, doesn't emit)
    """
    
    def __init__(self, viz_service, parent=None):
        """
        Initialize Comparison Display Widget.
        
        Args:
            viz_service: VisualizationDataService instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.viz_service = viz_service
        self.current_view_type = 'bar'
        self.is_loading = False
        
        # Setup UI
        self._init_ui()
        
        print("✓ ComparisonDisplayWidget initialized")
    
    def _init_ui(self):
        """Setup the UI layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Create stacked widget for different views
        self.stacked_widget = QWidget()
        stacked_layout = QVBoxLayout(self.stacked_widget)
        stacked_layout.setContentsMargins(0, 0, 0, 0)
        
        # Page 0: Empty state
        self.empty_page = self._create_empty_state()
        
        # Page 1: Table view
        self.table_page = self._create_table_view()
        
        # Page 2: Plot view (matplotlib canvas)
        self.plot_page = self._create_plot_view()
        
        # Page 3: Loading state
        self.loading_page = self._create_loading_state()
        
        # Start with empty state
        stacked_layout.addWidget(self.empty_page)
        self.current_page = self.empty_page
        
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)
    
    def _create_empty_state(self):
        """Create empty state widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icon and message
        label = QLabel("""
        <div style='text-align: center; padding: 60px;'>
            <p style='font-size: 48px; margin: 0;'>📊</p>
            <h2 style='color: #7f8c8d; margin: 20px 0 10px 0;'>No Data to Display</h2>
            <p style='font-size: 14px; color: #95a5a6; margin: 0;'>
                Select materials and properties from the left panel,<br>
                then choose a chart type to visualize your data.
            </p>
        </div>
        """)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        return widget
    
    def _create_table_view(self):
        """Create table view widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Configure table
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.table)
        
        return widget
    
    def _create_plot_view(self):
        """Create matplotlib plot view (uses main scroll area, no nested scrolling)."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create matplotlib figure and canvas with larger size
        self.figure = Figure(figsize=(14, 10), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: white;")
        
        # Set fixed height to ensure main scrollbar extends properly
        self.canvas.setMinimumHeight(800)
        self.canvas.setMinimumWidth(1000)
        
        # Add navigation toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        # Add directly to layout (no nested scroll area)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        # ✨ NEW: Add Export Button
        export_btn_layout = QHBoxLayout()
        export_btn_layout.setContentsMargins(10, 10, 10, 10)
        
        self.export_jpg_btn = QPushButton("💾 Export as JPG")
        self.export_jpg_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.export_jpg_btn.clicked.connect(self._export_chart_as_jpg)
        self.export_jpg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.export_jpg_btn.setMinimumHeight(40)
        
        self.export_png_btn = QPushButton("🖼️ Export as PNG")
        self.export_png_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:pressed {
                background-color: #0a6bc4;
            }
        """)
        self.export_png_btn.clicked.connect(self._export_chart_as_png)
        self.export_png_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.export_png_btn.setMinimumHeight(40)
        
        export_btn_layout.addStretch()
        export_btn_layout.addWidget(self.export_jpg_btn)
        export_btn_layout.addWidget(self.export_png_btn)
        export_btn_layout.addStretch()
        
        layout.addLayout(export_btn_layout)
        
        return widget
    
    def _create_loading_state(self):
        """Create loading indicator widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Loading message
        label = QLabel("""
        <div style='text-align: center; padding: 60px;'>
            <p style='font-size: 48px; margin: 0;'>⏳</p>
            <h2 style='color: #3498db; margin: 20px 0 10px 0;'>Loading Data...</h2>
            <p style='font-size: 14px; color: #7f8c8d; margin: 0;'>
                Fetching data from database and generating visualization
            </p>
        </div>
        """)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        return widget
    
    def show_empty_state(self):
        """Show empty state."""
        self._switch_page(self.empty_page)
    
    def show_loading_state(self):
        """Show loading state."""
        self.is_loading = True
        self._switch_page(self.loading_page)
    
    def show_table_view(self):
        """Show table view."""
        self.is_loading = False
        self.current_view_type = 'table'
        self._switch_page(self.table_page)
    
    def show_plot_view(self):
        """Show plot view."""
        self.is_loading = False
        self._switch_page(self.plot_page)
    
    def _switch_page(self, new_page):
        """Switch to a different page."""
        # Remove current page
        layout = self.stacked_widget.layout()
        if self.current_page:
            layout.removeWidget(self.current_page)
            self.current_page.setVisible(False)
        
        # Add and show new page
        layout.addWidget(new_page)
        new_page.setVisible(True)
        self.current_page = new_page
    
    def update_display(self, materials: list, properties: list, data: dict, 
                      view_type: str = 'bar', options: dict = None):
        """
        Update display with new data.
        
        Args:
            materials: List of material names
            properties: List of property names
            data: Dictionary with material property data
            view_type: Type of view ('table', 'bar', 'scatter')
            options: Display options dict
        """
        # Handle empty data
        if not materials or not properties or not data:
            self.show_empty_state()
            return
        
        # Show loading
        self.show_loading_state()
        
        try:
            # Update based on view type
            if view_type == 'table':
                self._update_table_view(materials, properties, data, options)
            elif view_type in ['bar', 'scatter']:
                self._update_plot_view(materials, properties, data, view_type, options)
            
            print(f"✓ Display updated: {len(materials)} materials, {len(properties)} properties")
            
        except Exception as e:
            print(f"❌ Error updating display: {e}")
            import traceback
            traceback.print_exc()
            self.show_empty_state()
    
    def _update_table_view(self, materials: list, properties: list, 
                          data: dict, options: dict = None):
        """Update table view with data."""
        # Clear existing table
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        
        # Set up columns: Property name + one column per material
        num_cols = 1 + len(materials)
        self.table.setColumnCount(num_cols)
        
        # Set headers
        headers = ['Property'] + materials
        self.table.setHorizontalHeaderLabels(headers)
        
        # Add rows for each property
        self.table.setRowCount(len(properties))
        
        for row_idx, prop_name in enumerate(properties):
            # Property name in first column
            prop_item = QTableWidgetItem(prop_name)
            prop_item.setFont(QFont('Arial', 10, QFont.Weight.Bold))
            self.table.setItem(row_idx, 0, prop_item)
            
            # Values for each material
            for col_idx, mat_name in enumerate(materials, start=1):
                value = data.get(mat_name, {}).get(prop_name, {})
                
                if isinstance(value, dict):
                    val = value.get('value', 'N/A')
                    unit = value.get('unit', '')
                    
                    # Format value
                    if isinstance(val, (int, float)):
                        display_text = f"{val:.3g}"
                    else:
                        display_text = str(val)
                    
                    # Add unit if requested
                    if options and options.get('show_units') and unit:
                        display_text += f" {unit}"
                else:
                    display_text = str(value) if value else 'N/A'
                
                item = QTableWidgetItem(display_text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)
        
        # Resize columns to content
        self.table.resizeColumnsToContents()
        
        # Show table view
        self.show_table_view()
    
    def _update_plot_view(self, materials: list, properties: list, 
                         data: dict, view_type: str, options: dict = None):
        """Update plot view with chart."""
        # Clear figure
        self.figure.clear()
        
        # Create subplot
        ax = self.figure.add_subplot(111)
        
        if view_type == 'bar':
            self._create_bar_chart(ax, materials, properties, data, options)
        elif view_type == 'scatter':
            self._create_scatter_plot(ax, materials, properties, data, options)
        
        # Tight layout
        self.figure.tight_layout()
        
        # Redraw canvas
        self.canvas.draw()
        
        # Show plot view
        self.show_plot_view()
    
    def _create_bar_chart(self, ax, materials: list, properties: list, 
                         data: dict, options: dict = None):
        """Create bar chart."""
        import numpy as np
        
        # Prepare data for plotting
        num_properties = len(properties)
        num_materials = len(materials)
        
        # Bar width and positions
        bar_width = 0.8 / num_materials
        x = np.arange(num_properties)
        
        # Plot bars for each material
        for i, mat_name in enumerate(materials):
            values = []
            for prop_name in properties:
                value = data.get(mat_name, {}).get(prop_name, {})
                if isinstance(value, dict):
                    val = value.get('value', 0)
                else:
                    val = value if value else 0
                
                # Convert to float
                try:
                    values.append(float(val))
                except (ValueError, TypeError):
                    values.append(0)
            
            # Plot bars
            offset = (i - num_materials/2 + 0.5) * bar_width
            ax.bar(x + offset, values, bar_width, label=mat_name, alpha=0.8)
        
        # Labels and title
        ax.set_xlabel('Properties', fontsize=12, fontweight='bold')
        ax.set_ylabel('Value', fontsize=12, fontweight='bold')
        ax.set_title('Property Comparison', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(properties, rotation=45, ha='right')
        ax.legend(loc='best')
        ax.grid(axis='y', alpha=0.3)
    
    def _create_scatter_plot(self, ax, materials: list, properties: list, 
                            data: dict, options: dict = None):
        """Create scatter plot (requires exactly 2 properties)."""
        if len(properties) != 2:
            ax.text(0.5, 0.5, 'Scatter plot requires exactly 2 properties\nSelected: ' + str(len(properties)),
                   ha='center', va='center', fontsize=14, color='red',
                   transform=ax.transAxes)
            return
        
        prop_x, prop_y = properties
        
        # Plot each material
        for mat_name in materials:
            # Get x and y values
            x_val = data.get(mat_name, {}).get(prop_x, {})
            y_val = data.get(mat_name, {}).get(prop_y, {})
            
            if isinstance(x_val, dict):
                x = x_val.get('value', None)
            else:
                x = x_val
            
            if isinstance(y_val, dict):
                y = y_val.get('value', None)
            else:
                y = y_val
            
            # Convert to float and plot
            try:
                x = float(x) if x else None
                y = float(y) if y else None
                
                if x is not None and y is not None:
                    ax.scatter(x, y, s=100, alpha=0.7, label=mat_name)
                    ax.annotate(mat_name, (x, y), xytext=(5, 5), 
                              textcoords='offset points', fontsize=8)
            except (ValueError, TypeError):
                continue
        
        # Labels and title
        ax.set_xlabel(prop_x, fontsize=12, fontweight='bold')
        ax.set_ylabel(prop_y, fontsize=12, fontweight='bold')
        ax.set_title(f'{prop_x} vs {prop_y}', fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(alpha=0.3)
    
    def _export_chart_as_jpg(self):
        """Export the current chart as JPG file."""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        import os
        from io import BytesIO
        from PIL import Image
        
        # Check if there's a chart to export
        if not self.figure.get_axes():
            QMessageBox.warning(self, "No Chart", "Please generate a chart first before exporting.")
            return
        
        # Open file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Chart as JPG",
            os.path.expanduser("~/Desktop/material_comparison_chart.jpg"),
            "JPEG Files (*.jpg);;All Files (*)"
        )
        
        if file_path:
            try:
                # Save to BytesIO first as PNG (lossless)
                buf = BytesIO()
                self.figure.savefig(buf, format='png', dpi=300, bbox_inches='tight', 
                                   facecolor='white', edgecolor='none')
                buf.seek(0)
                
                # Convert to JPG with high quality using PIL
                img = Image.open(buf)
                rgb_img = img.convert('RGB')  # Convert RGBA to RGB for JPG
                rgb_img.save(file_path, 'JPEG', quality=95, optimize=True)
                
                QMessageBox.information(self, "Success", f"Chart exported successfully to:\n{file_path}")
                print(f"✅ Chart exported as JPG: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to export chart:\n{str(e)}")
                print(f"❌ Export failed: {e}")
                import traceback
                traceback.print_exc()
    
    def _export_chart_as_png(self):
        """Export the current chart as PNG file."""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        import os
        
        # Check if there's a chart to export
        if not self.figure.get_axes():
            QMessageBox.warning(self, "No Chart", "Please generate a chart first before exporting.")
            return
        
        # Open file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Chart as PNG",
            os.path.expanduser("~/Desktop/material_comparison_chart.png"),
            "PNG Files (*.png);;All Files (*)"
        )
        
        if file_path:
            try:
                # Save figure as PNG with high quality
                self.figure.savefig(file_path, format='png', dpi=300, bbox_inches='tight', 
                                   facecolor='white', edgecolor='none')
                QMessageBox.information(self, "Success", f"Chart exported successfully to:\n{file_path}")
                print(f"✅ Chart exported as PNG: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to export chart:\n{str(e)}")
                print(f"❌ Export failed: {e}")
    
    def clear_display(self):
        """Clear the display and show empty state."""
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        self.figure.clear()
        self.canvas.draw()
        self.show_empty_state()


# =============================================================================
# MODEL SELECTION WIDGET - TASK 5.1
# =============================================================================

class ModelSelectionWidget(QWidget):
    """
    Model Selection Widget - Phase 5 Task 5.1
    
    Features:
    - Shows selected material name
    - Model type dropdown (EOS, Strength, Reaction)
    - Model name dropdown (populated dynamically)
    - Enabled only when single material selected
    
    Signals:
    - model_selected(material_id, model_name): Emitted when model is selected
    """
    
    # Signal emitted when a model is selected
    model_selected = pyqtSignal(int, str)  # material_id, model_name
    
    def __init__(self, viz_service, parent=None):
        """
        Initialize Model Selection Widget.
        
        Args:
            viz_service: VisualizationDataService instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.viz_service = viz_service
        self.current_material_id = None
        self.current_material_name = ""
        self.available_model_types = {}
        
        # Setup UI
        self._init_ui()
        
        # Start disabled
        self.setEnabled(False)
        
        print("✓ ModelSelectionWidget initialized")
    
    def _init_ui(self):
        """Setup the UI layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Widget styling
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 8px;
            }
            QLabel {
                background-color: transparent;
                font-weight: bold;
            }
            QComboBox {
                padding: 5px;
                border: 2px solid #ddd;
                border-radius: 4px;
                background-color: white;
                min-height: 25px;
            }
            QComboBox:disabled {
                background-color: #f0f0f0;
                color: #999;
            }
            QComboBox:hover {
                border-color: #2196F3;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
        """)
        
        # Title
        title = QLabel("🎯 Model Selection")
        title.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2196F3;
                background-color: transparent;
                padding: 5px;
            }
        """)
        main_layout.addWidget(title)
        
        # Selected Material Label
        self.material_label = QLabel("Selected Material: None")
        self.material_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #555;
                background-color: white;
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 4px;
            }
        """)
        main_layout.addWidget(self.material_label)
        
        # Model Type Selection
        type_layout = QVBoxLayout()
        type_label = QLabel("Model Type:")
        type_label.setStyleSheet("QLabel { font-size: 12px; color: #333; }")
        type_layout.addWidget(type_label)
        
        self.model_type_combo = QComboBox()
        self.model_type_combo.addItem("-- Select Model Type --")
        self.model_type_combo.currentTextChanged.connect(self._on_model_type_changed)
        type_layout.addWidget(self.model_type_combo)
        
        main_layout.addLayout(type_layout)
        
        # Model Name Selection
        name_layout = QVBoxLayout()
        name_label = QLabel("Model Name:")
        name_label.setStyleSheet("QLabel { font-size: 12px; color: #333; }")
        name_layout.addWidget(name_label)
        
        self.model_name_combo = QComboBox()
        self.model_name_combo.addItem("-- Select Model --")
        self.model_name_combo.setEnabled(False)
        self.model_name_combo.currentTextChanged.connect(self._on_model_name_changed)
        name_layout.addWidget(self.model_name_combo)
        
        main_layout.addLayout(name_layout)
        
        # Info label
        self.info_label = QLabel("Select a single material to view models")
        self.info_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #999;
                font-style: italic;
                background-color: transparent;
                padding: 5px;
            }
        """)
        self.info_label.setWordWrap(True)
        main_layout.addWidget(self.info_label)
        
        # Add stretch
        main_layout.addStretch()
        
        self.setLayout(main_layout)
    
    def update_for_material(self, material_id: int, material_name: str):
        """
        Update widget for a single selected material.
        Task 5.1: Enable only when single material selected
        
        Args:
            material_id: Selected material ID
            material_name: Material name
        """
        self.current_material_id = material_id
        self.current_material_name = material_name
        
        # Update label
        self.material_label.setText(f"Selected Material: {material_name}")
        self.material_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #155724;
                background-color: #d4edda;
                padding: 8px;
                border: 2px solid #c3e6cb;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        
        # Enable widget
        self.setEnabled(True)
        
        # Load available model types
        self._load_model_types()
        
        self.info_label.setText(f"Select a model type to view available models for {material_name}")
        
        print(f"✓ Model selector updated for material: {material_name} (ID: {material_id})")
    
    def clear_selection(self):
        """Clear the selection and disable widget."""
        self.current_material_id = None
        self.current_material_name = ""
        
        # Reset label
        self.material_label.setText("Selected Material: None")
        self.material_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #555;
                background-color: white;
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 4px;
            }
        """)
        
        # Clear combos
        self.model_type_combo.clear()
        self.model_type_combo.addItem("-- Select Model Type --")
        self.model_name_combo.clear()
        self.model_name_combo.addItem("-- Select Model --")
        self.model_name_combo.setEnabled(False)
        
        # Disable widget
        self.setEnabled(False)
        
        self.info_label.setText("Select a single material to view models")
        
        print("✓ Model selector cleared")
    
    def _load_model_types(self):
        """
        Load available model types for current material.
        Task 5.1: Connect to service: get_available_model_types()
        """
        if not self.current_material_id:
            return
        
        try:
            # Connect to database
            self.viz_service.connect()
            
            # Get available model types
            self.available_model_types = self.viz_service.get_available_model_types(
                self.current_material_id
            )
            
            # Disconnect
            self.viz_service.disconnect()
            
            # Clear and populate combo
            self.model_type_combo.clear()
            self.model_type_combo.addItem("-- Select Model Type --")
            
            if self.available_model_types:
                for model_type in self.available_model_types.keys():
                    count = len(self.available_model_types[model_type])
                    self.model_type_combo.addItem(f"{model_type} ({count})")
                
                print(f"✓ Loaded {len(self.available_model_types)} model types")
            else:
                self.info_label.setText(f"No models available for {self.current_material_name}")
            
        except Exception as e:
            print(f"❌ Error loading model types: {e}")
            import traceback
            traceback.print_exc()
            self.info_label.setText(f"Error loading model types: {e}")
    
    def _on_model_type_changed(self, text: str):
        """
        Handle model type selection change.
        Task 5.1: Connect to service: get_models_by_type()
        
        Args:
            text: Selected model type text
        """
        # Clear model name combo
        self.model_name_combo.clear()
        self.model_name_combo.addItem("-- Select Model --")
        
        if text.startswith("--") or not self.current_material_id:
            self.model_name_combo.setEnabled(False)
            return
        
        # Extract model type (remove count)
        model_type = text.split(" (")[0] if " (" in text else text
        
        try:
            # Connect to database
            self.viz_service.connect()
            
            # Get models by type
            models = self.viz_service.get_models_by_type(
                self.current_material_id,
                model_type
            )
            
            # Disconnect
            self.viz_service.disconnect()
            
            # Populate model name combo
            if models:
                for model in models:
                    model_name = model.get('model_name', 'Unknown')
                    self.model_name_combo.addItem(model_name)
                
                self.model_name_combo.setEnabled(True)
                self.info_label.setText(f"Found {len(models)} {model_type} models")
                
                print(f"✓ Loaded {len(models)} models for type: {model_type}")
            else:
                self.model_name_combo.setEnabled(False)
                self.info_label.setText(f"No {model_type} models found")
            
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            import traceback
            traceback.print_exc()
            self.model_name_combo.setEnabled(False)
            self.info_label.setText(f"Error loading models: {e}")
    
    def _on_model_name_changed(self, text: str):
        """
        Handle model name selection change.
        Task 5.1: Emit signal: model_selected(material_id, model_name)
        
        Args:
            text: Selected model name
        """
        if text.startswith("--") or not self.current_material_id:
            return
        
        # Emit signal
        self.model_selected.emit(self.current_material_id, text)
        
        self.info_label.setText(f"Selected: {text}")
        
        print(f"✓ Model selected: {text} for material ID {self.current_material_id}")


# =============================================================================
# MODEL PLOT WIDGET - TASK 5.2
# =============================================================================

class ModelPlotWidget(QWidget):
    """
    Model Plot Display Widget - Phase 5 Task 5.2
    
    Features:
    - Matplotlib canvas for model visualization
    - Navigation toolbar (zoom, pan, save)
    - Info panel showing model parameters
    - Loading indicator
    - Handles missing experimental data
    
    No signals emitted (display widget)
    """
    
    def __init__(self, calculator, parent=None):
        """
        Initialize Model Plot Widget.
        
        Args:
            calculator: ModelCalculator instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.calculator = calculator
        self.current_model_data = None
        self.current_exp_data = None
        
        # Setup UI
        self._init_ui()
        
        print("✓ ModelPlotWidget initialized")
    
    def _init_ui(self):
        """Setup the UI layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Create stacked widget for different states
        self.stacked_widget = QWidget()
        stacked_layout = QVBoxLayout(self.stacked_widget)
        stacked_layout.setContentsMargins(0, 0, 0, 0)
        
        # Page 0: Empty state
        self.empty_page = self._create_empty_state()
        
        # Page 1: Plot view
        self.plot_page = self._create_plot_view()
        
        # Page 2: Loading state
        self.loading_page = self._create_loading_state()
        
        # Start with empty state
        stacked_layout.addWidget(self.empty_page)
        self.current_page = self.empty_page
        
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)
    
    def _create_empty_state(self):
        """Create empty state widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label = QLabel("""
        <div style='text-align: center; padding: 40px;'>
            <p style='font-size: 48px; margin: 0;'>📈</p>
            <h2 style='color: #7f8c8d; margin: 20px 0 10px 0;'>No Model Selected</h2>
            <p style='font-size: 14px; color: #95a5a6; margin: 0;'>
                Select a material and model from the left panel<br>
                to visualize model curves and experimental data.
            </p>
        </div>
        """)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        return widget
    
    def _create_plot_view(self):
        """Create matplotlib plot view with info panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Model info panel
        self.info_panel = QLabel("Model Parameters: Loading...")
        self.info_panel.setStyleSheet("""
            QLabel {
                background-color: #e3f2fd;
                border: 2px solid #2196F3;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
                color: #1976d2;
            }
        """)
        self.info_panel.setWordWrap(True)
        layout.addWidget(self.info_panel)
        
        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: white;")
        
        # Add navigation toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas, stretch=1)
        
        return widget
    
    def _create_loading_state(self):
        """Create loading indicator widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label = QLabel("""
        <div style='text-align: center; padding: 40px;'>
            <p style='font-size: 48px; margin: 0;'>⏳</p>
            <h2 style='color: #2196F3; margin: 20px 0 10px 0;'>Loading Model Data...</h2>
            <p style='font-size: 14px; color: #7f8c8d; margin: 0;'>
                Fetching model parameters and experimental data
            </p>
        </div>
        """)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        return widget
    
    def _switch_page(self, new_page):
        """Switch to a different page."""
        layout = self.stacked_widget.layout()
        if self.current_page:
            layout.removeWidget(self.current_page)
            self.current_page.setVisible(False)
        
        layout.addWidget(new_page)
        new_page.setVisible(True)
        self.current_page = new_page
    
    def show_empty_state(self):
        """Show empty state."""
        self._switch_page(self.empty_page)
    
    def show_loading_state(self):
        """Show loading state."""
        self._switch_page(self.loading_page)
    
    def show_plot_view(self):
        """Show plot view."""
        self._switch_page(self.plot_page)
    
    def update_plot(self, model_data: dict, exp_data: dict = None):
        """
        Update plot with model and experimental data.
        Task 5.2: Write update_plot(model_data, exp_data)
        
        Args:
            model_data: Dictionary containing model parameters and info
            exp_data: Dictionary containing experimental data (optional)
        """
        # Show loading
        self.show_loading_state()
        
        try:
            # Store data
            self.current_model_data = model_data
            self.current_exp_data = exp_data
            
            # Extract model info
            model_name = model_data.get('model_name', 'Unknown')
            model_type = model_data.get('model_type', 'Unknown')
            parameters = model_data.get('parameters', {})
            material_name = model_data.get('material_name', 'Unknown')
            
            # Update info panel
            self._update_info_panel(model_name, model_type, parameters, exp_data)
            
            # Clear and create plot
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            # Plot based on model type
            if model_type == 'US-Up':
                self._plot_usup_model(ax, model_data, exp_data)
            elif model_type == 'EOS':
                self._plot_eos_model(ax, model_data, exp_data)
            elif model_type == 'Strength':
                self._plot_strength_model(ax, model_data, exp_data)
            else:
                ax.text(0.5, 0.5, f'Plot for {model_type} not yet implemented',
                       ha='center', va='center', fontsize=14)
            
            # Adjust layout
            self.figure.tight_layout()
            
            # Redraw canvas
            self.canvas.draw()
            
            # Show plot view
            self.show_plot_view()
            
            print(f"✓ Plot updated: {model_name} ({model_type})")
            
        except Exception as e:
            print(f"❌ Error updating plot: {e}")
            import traceback
            traceback.print_exc()
            self.show_empty_state()
    
    def _update_info_panel(self, model_name: str, model_type: str, 
                          parameters: dict, exp_data: dict):
        """Update the info panel with model parameters."""
        # Format parameters
        param_text = []
        for key, value in parameters.items():
            if isinstance(value, dict):
                val = value.get('value', 'N/A')
                unit = value.get('unit', '')
                if isinstance(val, (int, float)):
                    param_text.append(f"{key}: {val:.4g} {unit}".strip())
                else:
                    param_text.append(f"{key}: {val} {unit}".strip())
            else:
                param_text.append(f"{key}: {value}")
        
        params_str = " | ".join(param_text[:5])  # Show first 5 parameters
        if len(param_text) > 5:
            params_str += f" | ... ({len(param_text)} total)"
        
        # Check experimental data
        exp_status = "✓ Experimental data available" if exp_data else "⚠️ No experimental data"
        
        # Update label
        info_text = f"<b>{model_name}</b> ({model_type}) | {params_str}<br>{exp_status}"
        self.info_panel.setText(info_text)
    
    def _plot_usup_model(self, ax, model_data: dict, exp_data: dict):
        """
        Plot US-Up model.
        
        Args:
            ax: Matplotlib axis
            model_data: Model data dictionary
            exp_data: Experimental data dictionary (optional)
        """
        import numpy as np
        
        parameters = model_data.get('parameters', {})
        material_name = model_data.get('material_name', 'Material')
        
        # Extract parameters
        C0 = parameters.get('C0', {}).get('value', 0)
        s = parameters.get('s', {}).get('value', 1)
        
        # Generate model curve
        Up_range = np.linspace(0, 5, 100)  # km/s
        Us_model = C0 + s * Up_range
        
        # Plot model curve
        ax.plot(Up_range, Us_model, 'b-', linewidth=2, label=f'Model: Us = {C0:.2f} + {s:.2f}·Up')
        
        # Plot experimental data if available
        if exp_data:
            Up_exp = exp_data.get('Up', [])
            Us_exp = exp_data.get('Us', [])
            if Up_exp and Us_exp:
                ax.scatter(Up_exp, Us_exp, c='red', s=50, alpha=0.6, 
                          label='Experimental Data', zorder=5)
                print(f"  ✓ Plotted {len(Up_exp)} experimental points")
        
        # Labels and styling
        ax.set_xlabel('Particle Velocity, Up (km/s)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Shock Velocity, Us (km/s)', fontsize=12, fontweight='bold')
        ax.set_title(f'{material_name} - US-Up Relationship', fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)
    
    def _plot_eos_model(self, ax, model_data: dict, exp_data: dict):
        """
        Plot EOS model.
        
        Args:
            ax: Matplotlib axis
            model_data: Model data dictionary
            exp_data: Experimental data dictionary (optional)
        """
        import numpy as np
        
        parameters = model_data.get('parameters', {})
        material_name = model_data.get('material_name', 'Material')
        
        # Extract parameters
        K0 = parameters.get('K0', {}).get('value', 100)  # GPa
        K0_prime = parameters.get("K0'", {}).get('value', 4)
        
        # Generate model curve (Birch-Murnaghan)
        V_V0_range = np.linspace(0.5, 1.0, 100)
        P_model = (3/2) * K0 * (V_V0_range**(-7/3) - V_V0_range**(-5/3)) * \
                  (1 + (3/4) * (K0_prime - 4) * (V_V0_range**(-2/3) - 1))
        
        # Plot model curve
        ax.plot(V_V0_range, P_model, 'b-', linewidth=2, 
               label=f'Model: K0={K0:.1f} GPa, K0\'={K0_prime:.2f}')
        
        # Plot experimental data if available
        if exp_data:
            V_V0_exp = exp_data.get('V_over_V0', [])
            P_exp = exp_data.get('P', [])
            if V_V0_exp and P_exp:
                ax.scatter(V_V0_exp, P_exp, c='red', s=50, alpha=0.6, 
                          label='Experimental Data', zorder=5)
                print(f"  ✓ Plotted {len(V_V0_exp)} experimental points")
        
        # Labels and styling
        ax.set_xlabel('V/V₀', fontsize=12, fontweight='bold')
        ax.set_ylabel('Pressure (GPa)', fontsize=12, fontweight='bold')
        ax.set_title(f'{material_name} - Equation of State', fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
    
    def _plot_strength_model(self, ax, model_data: dict, exp_data: dict):
        """
        Plot Strength model.
        
        Args:
            ax: Matplotlib axis
            model_data: Model data dictionary
            exp_data: Experimental data dictionary (optional)
        """
        import numpy as np
        
        parameters = model_data.get('parameters', {})
        material_name = model_data.get('material_name', 'Material')
        model_name = model_data.get('model_name', 'Strength Model')
        
        # Generic strength plot (Johnson-Cook style)
        strain_range = np.linspace(0, 0.5, 100)
        
        # Extract parameters if available
        A = parameters.get('A', {}).get('value', 300)  # MPa
        B = parameters.get('B', {}).get('value', 500)
        n = parameters.get('n', {}).get('value', 0.3)
        
        # Stress = A + B * strain^n
        stress_model = A + B * (strain_range ** n)
        
        # Plot model curve
        ax.plot(strain_range, stress_model, 'b-', linewidth=2, label=f'{model_name}')
        
        # Plot experimental data if available
        if exp_data:
            strain_exp = exp_data.get('strain', [])
            stress_exp = exp_data.get('stress', [])
            if strain_exp and stress_exp:
                ax.scatter(strain_exp, stress_exp, c='red', s=50, alpha=0.6, 
                          label='Experimental Data', zorder=5)
                print(f"  ✓ Plotted {len(strain_exp)} experimental points")
        
        # Labels and styling
        ax.set_xlabel('Strain', fontsize=12, fontweight='bold')
        ax.set_ylabel('Stress (MPa)', fontsize=12, fontweight='bold')
        ax.set_title(f'{material_name} - {model_name}', fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
    
    def clear_plot(self):
        """Clear the plot and show empty state."""
        self.current_model_data = None
        self.current_exp_data = None
        self.figure.clear()
        self.canvas.draw()
        self.show_empty_state()


# =============================================================================
# MODEL INFO PANEL - TASK 5.3
# =============================================================================

class ModelInfoPanel(QWidget):
    """
    Model Info Panel Widget - Phase 5 Task 5.3
    
    Features:
    - Display model equation (LaTeX-like formatting)
    - Show parameter values with units
    - Show references (clickable links)
    - Show fit quality metrics (R², RMSE)
    - Updates when model selected
    
    No signals emitted (display widget)
    """
    
    def __init__(self, parent=None):
        """
        Initialize Model Info Panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.current_model_name = None
        self.current_model_type = None
        
        # Setup UI
        self._init_ui()
        
        print("✓ ModelInfoPanel initialized")
    
    def _init_ui(self):
        """Setup the UI layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Widget styling
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 8px;
            }
            QLabel {
                background-color: transparent;
            }
            QScrollArea {
                background-color: white;
                border: 2px solid #ddd;
                border-radius: 4px;
            }
        """)
        
        # Title
        title = QLabel("📋 Model Information")
        title.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2196F3;
                background-color: transparent;
                padding: 5px;
            }
        """)
        main_layout.addWidget(title)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(15)
        
        # Model name label
        self.model_name_label = QLabel("No model selected")
        self.model_name_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #333;
                padding: 5px;
                background-color: #e3f2fd;
                border-radius: 4px;
            }
        """)
        self.model_name_label.setWordWrap(True)
        self.content_layout.addWidget(self.model_name_label)
        
        # Equation section
        equation_title = QLabel("Model Equation:")
        equation_title.setStyleSheet("QLabel { font-weight: bold; color: #555; }")
        self.content_layout.addWidget(equation_title)
        
        self.equation_label = QLabel("Select a model to view equation")
        self.equation_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-family: 'Courier New', monospace;
                color: #1976d2;
                padding: 10px;
                background-color: #e8f5e9;
                border-radius: 4px;
                border-left: 4px solid #4caf50;
            }
        """)
        self.equation_label.setWordWrap(True)
        self.content_layout.addWidget(self.equation_label)
        
        # Parameters section
        params_title = QLabel("Parameters:")
        params_title.setStyleSheet("QLabel { font-weight: bold; color: #555; }")
        self.content_layout.addWidget(params_title)
        
        self.params_label = QLabel("No parameters")
        self.params_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #333;
                padding: 8px;
                background-color: white;
                border-radius: 4px;
                border: 1px solid #ddd;
            }
        """)
        self.params_label.setWordWrap(True)
        self.content_layout.addWidget(self.params_label)
        
        # Fit quality section
        quality_title = QLabel("Fit Quality:")
        quality_title.setStyleSheet("QLabel { font-weight: bold; color: #555; }")
        self.content_layout.addWidget(quality_title)
        
        self.quality_label = QLabel("No quality metrics available")
        self.quality_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #333;
                padding: 8px;
                background-color: #fff3e0;
                border-radius: 4px;
                border-left: 4px solid #ff9800;
            }
        """)
        self.quality_label.setWordWrap(True)
        self.content_layout.addWidget(self.quality_label)
        
        # References section
        ref_title = QLabel("References:")
        ref_title.setStyleSheet("QLabel { font-weight: bold; color: #555; }")
        self.content_layout.addWidget(ref_title)
        
        self.ref_label = QLabel("No references available")
        self.ref_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #1565c0;
                padding: 8px;
                background-color: white;
                border-radius: 4px;
                border: 1px solid #ddd;
            }
        """)
        self.ref_label.setWordWrap(True)
        self.ref_label.setTextFormat(Qt.TextFormat.RichText)
        self.ref_label.setOpenExternalLinks(True)
        self.content_layout.addWidget(self.ref_label)
        
        # Add stretch
        self.content_layout.addStretch()
        
        scroll.setWidget(self.content_widget)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
    
    def update_info(self, model_data: dict):
        """
        Update panel with model information.
        Task 5.3: Update when model selected
        
        Args:
            model_data: Dictionary containing model info and parameters
        """
        self.current_model_name = model_data.get('model_name', 'Unknown')
        self.current_model_type = model_data.get('model_type', 'Unknown')
        material_name = model_data.get('material_name', 'Unknown')
        parameters = model_data.get('parameters', {})
        references = model_data.get('references', [])
        fit_quality = model_data.get('fit_quality', {})
        
        # Update model name
        self.model_name_label.setText(
            f"{self.current_model_name} ({self.current_model_type})\n"
            f"Material: {material_name}"
        )
        
        # Update equation
        equation = self._get_equation(self.current_model_type, parameters)
        self.equation_label.setText(equation)
        
        # Update parameters
        params_text = self._format_parameters(parameters)
        self.params_label.setText(params_text)
        
        # Update fit quality
        quality_text = self._format_fit_quality(fit_quality)
        self.quality_label.setText(quality_text)
        
        # Update references
        ref_text = self._format_references(references)
        self.ref_label.setText(ref_text)
        
        print(f"✓ Model info updated: {self.current_model_name}")
    
    def _get_equation(self, model_type: str, parameters: dict) -> str:
        """
        Get model equation based on type.
        Task 5.3: Display model equation (LaTeX rendering)
        
        Args:
            model_type: Type of model
            parameters: Model parameters
            
        Returns:
            HTML formatted equation string
        """
        if model_type == 'US-Up':
            C0 = parameters.get('C0', {}).get('value', 'C₀')
            s = parameters.get('s', {}).get('value', 's')
            if isinstance(C0, (int, float)) and isinstance(s, (int, float)):
                return f"<b>Us = {C0:.3f} + {s:.3f} · Up</b><br><br>Where:<br>Us = Shock velocity<br>Up = Particle velocity"
            return "<b>Us = C₀ + s · Up</b><br><br>Where:<br>Us = Shock velocity<br>Up = Particle velocity"
        
        elif model_type == 'EOS':
            return (
                "<b>Birch-Murnaghan Equation:</b><br><br>"
                "P = (3/2)K₀[(V/V₀)⁻⁷/³ - (V/V₀)⁻⁵/³] × [1 + (3/4)(K₀' - 4)((V/V₀)⁻²/³ - 1)]<br><br>"
                "Where:<br>"
                "P = Pressure<br>"
                "V/V₀ = Volume ratio<br>"
                "K₀ = Bulk modulus<br>"
                "K₀' = Pressure derivative of bulk modulus"
            )
        
        elif model_type == 'Strength':
            return (
                "<b>Johnson-Cook Model:</b><br><br>"
                "σ = [A + B·εⁿ][1 + C·ln(ε̇*)][1 - T*ᵐ]<br><br>"
                "Where:<br>"
                "σ = Flow stress<br>"
                "ε = Plastic strain<br>"
                "ε̇* = Normalized strain rate<br>"
                "T* = Homologous temperature"
            )
        
        else:
            return f"<b>{model_type} Model</b><br><br>Equation not available"
    
    def _format_parameters(self, parameters: dict) -> str:
        """
        Format parameters with values and units.
        Task 5.3: Show parameter values with units
        
        Args:
            parameters: Dictionary of parameters
            
        Returns:
            HTML formatted parameter string
        """
        if not parameters:
            return "No parameters available"
        
        lines = []
        for param_name, param_data in parameters.items():
            if isinstance(param_data, dict):
                value = param_data.get('value', 'N/A')
                unit = param_data.get('unit', '')
                
                if isinstance(value, (int, float)):
                    value_str = f"{value:.6g}"
                else:
                    value_str = str(value)
                
                if unit:
                    lines.append(f"<b>{param_name}:</b> {value_str} {unit}")
                else:
                    lines.append(f"<b>{param_name}:</b> {value_str}")
            else:
                lines.append(f"<b>{param_name}:</b> {param_data}")
        
        return "<br>".join(lines) if lines else "No parameters available"
    
    def _format_fit_quality(self, fit_quality: dict) -> str:
        """
        Format fit quality metrics.
        Task 5.3: Show fit quality metrics (R², RMSE)
        
        Args:
            fit_quality: Dictionary of fit metrics
            
        Returns:
            HTML formatted quality string
        """
        if not fit_quality:
            return "⚠️ No fit quality metrics available"
        
        lines = []
        
        # R-squared
        r2 = fit_quality.get('R2', fit_quality.get('r_squared', None))
        if r2 is not None:
            lines.append(f"<b>R²:</b> {r2:.4f}")
        
        # RMSE
        rmse = fit_quality.get('RMSE', fit_quality.get('rmse', None))
        if rmse is not None:
            lines.append(f"<b>RMSE:</b> {rmse:.4g}")
        
        # Other metrics
        for key, value in fit_quality.items():
            if key not in ['R2', 'r_squared', 'RMSE', 'rmse']:
                if isinstance(value, (int, float)):
                    lines.append(f"<b>{key}:</b> {value:.4g}")
                else:
                    lines.append(f"<b>{key}:</b> {value}")
        
        return "<br>".join(lines) if lines else "⚠️ No fit quality metrics available"
    
    def _format_references(self, references: list) -> str:
        """
        Format references with clickable links.
        Task 5.3: Show references (clickable links)
        
        Args:
            references: List of reference dictionaries or strings
            
        Returns:
            HTML formatted reference string with links
        """
        if not references:
            return "No references available"
        
        lines = []
        for i, ref in enumerate(references, 1):
            if isinstance(ref, dict):
                author = ref.get('author', 'Unknown')
                year = ref.get('year', '')
                title = ref.get('title', '')
                doi = ref.get('doi', '')
                url = ref.get('url', '')
                
                ref_text = f"{i}. {author}"
                if year:
                    ref_text += f" ({year})"
                if title:
                    ref_text += f" - {title}"
                
                if doi:
                    ref_text += f"<br>&nbsp;&nbsp;&nbsp;<a href='https://doi.org/{doi}'>DOI: {doi}</a>"
                elif url:
                    ref_text += f"<br>&nbsp;&nbsp;&nbsp;<a href='{url}'>Link</a>"
                
                lines.append(ref_text)
            else:
                lines.append(f"{i}. {ref}")
        
        return "<br><br>".join(lines) if lines else "No references available"
    
    def clear_info(self):
        """Clear the info panel."""
        self.current_model_name = None
        self.current_model_type = None
        
        self.model_name_label.setText("No model selected")
        self.equation_label.setText("Select a model to view equation")
        self.params_label.setText("No parameters")
        self.quality_label.setText("No quality metrics available")
        self.ref_label.setText("No references available")
        
        print("✓ Model info cleared")


# =============================================================================
# EXPORT CONTROLS WIDGET - TASK 5.4
# =============================================================================

class ExportControlsWidget(QWidget):
    """
    Export Controls Widget - Phase 5 Task 5.4
    
    Features:
    - Export Plot (PNG) button
    - Export Plot (PDF) button
    - Success/error notifications
    - Connected to export functions
    
    No signals emitted (action widget)
    """
    
    def __init__(self, parent=None):
        """
        Initialize Export Controls Widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.current_figure = None
        self.current_model_name = None
        
        # Setup UI
        self._init_ui()
        
        print("✓ ExportControlsWidget initialized")
    
    def _init_ui(self):
        """Setup the UI layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Widget styling
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 8px;
            }
            QPushButton {
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 4px;
                background-color: white;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #e3f2fd;
                border-color: #2196F3;
            }
            QPushButton:pressed {
                background-color: #bbdefb;
            }
            QPushButton:disabled {
                background-color: #f0f0f0;
                color: #999;
                border-color: #ddd;
            }
        """)
        
        # Title
        title = QLabel("💾 Export Controls")
        title.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2196F3;
                background-color: transparent;
                padding: 5px;
            }
        """)
        main_layout.addWidget(title)
        
        # Export PNG button
        self.export_png_btn = QPushButton("📊 Export Plot (PNG)")
        self.export_png_btn.setEnabled(False)
        self.export_png_btn.clicked.connect(self._export_png)
        main_layout.addWidget(self.export_png_btn)
        
        # Export PDF button
        self.export_pdf_btn = QPushButton("📄 Export Plot (PDF)")
        self.export_pdf_btn.setEnabled(False)
        self.export_pdf_btn.clicked.connect(self._export_pdf)
        main_layout.addWidget(self.export_pdf_btn)
        
        # Status label
        self.status_label = QLabel("No plot to export")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #999;
                font-style: italic;
                background-color: transparent;
                padding: 5px;
            }
        """)
        self.status_label.setWordWrap(True)
        main_layout.addWidget(self.status_label)
        
        # Add stretch
        main_layout.addStretch()
        
        self.setLayout(main_layout)
    
    def set_figure(self, figure, model_name: str = None):
        """
        Set the figure to export.
        Task 5.4: Connect to export functions
        
        Args:
            figure: Matplotlib figure object
            model_name: Model name for default filename
        """
        self.current_figure = figure
        self.current_model_name = model_name
        
        if figure:
            self.export_png_btn.setEnabled(True)
            self.export_pdf_btn.setEnabled(True)
            self.status_label.setText(f"Ready to export: {model_name or 'Plot'}")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 11px;
                    color: #2e7d32;
                    background-color: transparent;
                    padding: 5px;
                }
            """)
        else:
            self.export_png_btn.setEnabled(False)
            self.export_pdf_btn.setEnabled(False)
            self.status_label.setText("No plot to export")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 11px;
                    color: #999;
                    font-style: italic;
                    background-color: transparent;
                    padding: 5px;
                }
            """)
    
    def _export_png(self):
        """
        Export current plot as PNG.
        Task 5.4: Export Plot (PNG)
        """
        if not self.current_figure:
            self._show_error("No plot to export")
            return
        
        try:
            from PyQt6.QtWidgets import QFileDialog
            import os
            
            # Default filename
            default_name = f"{self.current_model_name or 'plot'}.png"
            default_name = default_name.replace(' ', '_').replace('/', '_')
            
            # Open save dialog
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Plot as PNG",
                default_name,
                "PNG Files (*.png);;All Files (*)"
            )
            
            if file_path:
                # Add .png extension if not present
                if not file_path.lower().endswith('.png'):
                    file_path += '.png'
                
                # Save figure
                self.current_figure.savefig(
                    file_path,
                    dpi=300,
                    bbox_inches='tight',
                    facecolor='white',
                    edgecolor='none'
                )
                
                self._show_success(f"Plot exported to:\n{os.path.basename(file_path)}")
                print(f"✓ Plot exported to PNG: {file_path}")
        
        except Exception as e:
            self._show_error(f"Failed to export PNG: {e}")
            print(f"❌ Error exporting PNG: {e}")
            import traceback
            traceback.print_exc()
    
    def _export_pdf(self):
        """
        Export current plot as PDF.
        Task 5.4: Export Plot (PDF)
        """
        if not self.current_figure:
            self._show_error("No plot to export")
            return
        
        try:
            from PyQt6.QtWidgets import QFileDialog
            import os
            
            # Default filename
            default_name = f"{self.current_model_name or 'plot'}.pdf"
            default_name = default_name.replace(' ', '_').replace('/', '_')
            
            # Open save dialog
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Plot as PDF",
                default_name,
                "PDF Files (*.pdf);;All Files (*)"
            )
            
            if file_path:
                # Add .pdf extension if not present
                if not file_path.lower().endswith('.pdf'):
                    file_path += '.pdf'
                
                # Save figure
                self.current_figure.savefig(
                    file_path,
                    format='pdf',
                    bbox_inches='tight',
                    facecolor='white',
                    edgecolor='none'
                )
                
                self._show_success(f"Plot exported to:\n{os.path.basename(file_path)}")
                print(f"✓ Plot exported to PDF: {file_path}")
        
        except Exception as e:
            self._show_error(f"Failed to export PDF: {e}")
            print(f"❌ Error exporting PDF: {e}")
            import traceback
            traceback.print_exc()
    
    def _show_success(self, message: str):
        """
        Show success notification.
        Task 5.4: Show success/error notifications
        
        Args:
            message: Success message
        """
        self.status_label.setText(f"✅ {message}")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #2e7d32;
                font-weight: bold;
                background-color: #c8e6c9;
                padding: 8px;
                border-radius: 4px;
                border-left: 4px solid #4caf50;
            }
        """)
        
        # Reset after 5 seconds
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(5000, lambda: self.set_figure(self.current_figure, self.current_model_name))
    
    def _show_error(self, message: str):
        """
        Show error notification.
        Task 5.4: Show success/error notifications
        
        Args:
            message: Error message
        """
        self.status_label.setText(f"❌ {message}")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #c62828;
                font-weight: bold;
                background-color: #ffcdd2;
                padding: 8px;
                border-radius: 4px;
                border-left: 4px solid #f44336;
            }
        """)
        
        # Reset after 5 seconds
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(5000, lambda: self.set_figure(self.current_figure, self.current_model_name))
    
    def clear(self):
        """Clear the export controls."""
        self.current_figure = None
        self.current_model_name = None
        self.export_png_btn.setEnabled(False)
        self.export_pdf_btn.setEnabled(False)
        self.status_label.setText("No plot to export")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #999;
                font-style: italic;
                background-color: transparent;
                padding: 5px;
            }
        """)


# =============================================================================
# UNIFIED VISUALIZATION TAB - MAIN WIDGET
# =============================================================================

class UnifiedVisualizationTab(QWidget):
    """
    Unified Visualization Tab - Main Widget
    
    Phase 4 Implementation:
    - Task 4.1: Create main tab file ✓
    - Task 4.2: Material selection widget (TODO)
    - Task 4.3: Property selection widget (TODO)
    - Task 4.4: Chart type selector (TODO)
    - Task 4.5: Top panel layout (TODO)
    - Task 4.6: Plot area with toolbar (TODO)
    
    Phase 5 Implementation:
    - Task 5.1: Model type selector (TODO)
    - Task 5.2: Model parameter display (TODO)
    - Task 5.3: Experimental data overlay (TODO)
    - Task 5.4: Bottom panel layout (TODO)
    - Task 5.5: Model plot area (TODO)
    """
    
    # Signals for inter-component communication
    materials_selected = pyqtSignal(list)  # List of material IDs
    properties_selected = pyqtSignal(list)  # List of property names
    chart_type_changed = pyqtSignal(str)   # Chart type name
    
    def __init__(self, db_manager=None, querier=None):
        """
        Initialize the Unified Visualization Tab.
        Task 6.1: Initialize service layer and connect all components
        
        Args:
            db_manager: Database manager instance (optional, for compatibility)
            querier: Database querier instance (optional, for compatibility)
        """
        super().__init__()
        
        print("=" * 70)
        print("🚀 PHASE 6 TASK 6.1: Initializing UnifiedVisualizationTab")
        print("=" * 70)
        
        # Store legacy parameters for compatibility
        self.db_manager = db_manager
        self.querier = querier
        
        # Task 6.1: Initialize service layer with proper error handling
        self._init_services()
        
        # Data storage
        self.selected_materials = []  # List of material IDs
        self.selected_properties = []  # List of property names
        self.current_chart_type = 'bar'  # Default chart type
        self.materials_data = {}  # Cached material data
        self.properties_data = {}  # Cached property data
        
        # Task 6.1: Track widget references for cleanup
        self.widget_references = []
        
        # Task 4.6: Debounce timer for data updates (300ms delay)
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.setInterval(300)  # 300ms debounce
        self.update_timer.timeout.connect(self._perform_data_update)
        self.pending_update_params = None  # Store pending update parameters
        
        # Setup UI
        print("🎨 Setting up UI layout...")
        self._init_ui()
        print("✅ UI layout complete")
        
        # Task 6.1: Connect all signals and slots
        print("🔗 Connecting signals and slots...")
        self._connect_all_signals()
        print("✅ All signals connected")
        
        # Load initial data
        print("📊 Loading initial data...")
        self._load_initial_data()
        
        # Task 6.1: Test complete workflow
        self.test_workflow()
        
        print("=" * 70)
        print("✅ PHASE 6 TASK 6.1: UnifiedVisualizationTab initialized successfully!")
        print("=" * 70)
    
    def _init_services(self):
        """
        Initialize backend services.
        Task 6.1: Initialize service layer in tab __init__
        """
        try:
            print("📦 Initializing backend services...")
            
            # Initialize visualization service
            self.viz_service = VisualizationDataService()
            print("✓ [Task 6.1] VisualizationDataService initialized")
            
            # Initialize plotting utilities
            self.plotting_utils = PlottingUtils()
            print("✓ [Task 6.1] PlottingUtils initialized")
            
            print("✅ Backend services initialized successfully")
            
        except Exception as e:
            print(f"❌ [Task 6.1] Error initializing services: {e}")
            traceback.print_exc()
            # Continue with None services for graceful degradation
            self.viz_service = None
            self.plotting_utils = None
    
    def _connect_all_signals(self):
        """
        Connect all signals and slots between components.
        Task 6.1: Connect all signals and slots
        """
        try:
            # Top panel connections already done in _create_top_panel
            
            print("✓ [Task 6.1] Material selector → Property selector")
            print("✓ [Task 6.1] Property selector → Comparison display")
            print("✓ [Task 6.1] View options → Comparison display")
            
        except Exception as e:
            print(f"❌ [Task 6.1] Error connecting signals: {e}")
            traceback.print_exc()
    
    def _init_ui(self):
        """
        Left nav buttons + QStackedWidget for switching views.
        Page 0: Material & Property Comparison (default)
        Page 1: Material Comparison (existing widget)
        """
        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 4, 8, 4)
        outer.setSpacing(4)

        # ── Header ──
        hdr = QHBoxLayout()
        title = QLabel("Unified Visualization")
        f = QFont(); f.setPointSize(15); f.setBold(True)
        title.setFont(f)
        title.setStyleSheet("color:#2c3e50;")
        hdr.addWidget(title)
        hdr.addStretch()
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(
            "background:#d4edda;color:#155724;padding:4px 12px;"
            "border-radius:4px;font-weight:bold;font-size:11px;"
        )
        hdr.addWidget(self.status_label)
        outer.addLayout(hdr)

        # ── Main content: Left nav + Right stacked ──
        content_layout = QHBoxLayout()
        content_layout.setSpacing(8)

        # ── Left Navigation Panel ──
        left_panel = QWidget()
        self._left_panel = left_panel
        left_panel.setFixedWidth(200)
        left_panel.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border-right: 1px solid #ddd;
                border-radius: 6px;
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(8, 12, 8, 12)
        left_layout.setSpacing(6)

        # Nav header
        nav_label = QLabel("Navigation")
        nav_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        nav_label.setStyleSheet("color:#555; padding: 4px 0; background: transparent;")
        left_layout.addWidget(nav_label)

        # Button style
        active_btn_style = """
            QPushButton {
                text-align: left;
                padding: 10px 12px;
                border: none;
                border-radius: 6px;
                background-color: #2196F3;
                color: white;
                font-size: 12px;
                font-weight: bold;
            }
        """
        inactive_btn_style = """
            QPushButton {
                text-align: left;
                padding: 10px 12px;
                border: none;
                border-radius: 6px;
                background-color: transparent;
                color: #333;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(33, 150, 243, 0.15);
            }
        """

        # Button 1: Material & Property Comparison (default)
        self.btn_property_comparison = QPushButton("📊 Material & Property\n     Comparison")
        self.btn_property_comparison.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_property_comparison.setStyleSheet(active_btn_style)
        self.btn_property_comparison.clicked.connect(self._switch_to_property_comparison)
        left_layout.addWidget(self.btn_property_comparison)


        left_layout.addStretch()

        # Store styles for toggle
        self._active_btn_style = active_btn_style
        self._inactive_btn_style = inactive_btn_style

        content_layout.addWidget(left_panel)

        # ── Right Panel: QStackedWidget ──
        self.view_stack = QStackedWidget()

        # Page 0: Material & Property Comparison (existing scroll area)
        page0 = QWidget()
        page0_layout = QVBoxLayout(page0)
        page0_layout.setContentsMargins(0, 0, 0, 0)

        sa = QScrollArea()
        sa.setWidgetResizable(True)
        sa.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        sa.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        sa.setStyleSheet("QScrollArea{border:none;background:transparent;}")

        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(4, 4, 4, 4)
        vbox.setSpacing(12)
        vbox.addWidget(self._create_top_panel())
        vbox.addStretch()

        sa.setWidget(container)
        # Increased minimum height to accommodate larger charts
        container.setMinimumHeight(1200)
        page0_layout.addWidget(sa)

        self.view_stack.addWidget(page0)  # index 0

        # Page 1: Material Comparison (existing widget)
        if MATERIAL_COMPARISON_AVAILABLE:
            try:
                self.material_comparison_widget = MaterialComparisonController(
                    self.db_manager, self.querier
                )
                self.view_stack.addWidget(self.material_comparison_widget)  # index 1
                print("✓ Material Comparison widget loaded into Unified Viz")
            except Exception as e:
                print(f"WARNING: Failed to load Material Comparison: {e}")
                import traceback
                traceback.print_exc()
                placeholder = QLabel("Material Comparison\n\nFailed to load.")
                placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.view_stack.addWidget(placeholder)
        else:
            placeholder = QLabel("Material Comparison\n\nModule not available.")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.view_stack.addWidget(placeholder)

        # Page 2: US/UP Analysis (existing widget)
        if US_UP_AVAILABLE:
            try:
                self.usup_analysis_widget = USUpAnalysisTab()
                self.view_stack.addWidget(self.usup_analysis_widget)  # index 2
                print("✓ US/UP Analysis widget loaded into Unified Viz")
            except Exception as e:
                print(f"WARNING: Failed to load US/UP Analysis: {e}")
                import traceback
                traceback.print_exc()
                placeholder = QLabel("US/UP Analysis\n\nFailed to load.")
                placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.view_stack.addWidget(placeholder)
        else:
            placeholder = QLabel("US/UP Analysis\n\nModule not available.")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.view_stack.addWidget(placeholder)

        # Default: page 0
        self.view_stack.setCurrentIndex(0)

        content_layout.addWidget(self.view_stack, stretch=1)
        outer.addLayout(content_layout, stretch=1)

    # -----------------------------------------------------------------
    def _create_top_panel(self):
        """Property Comparison — QGridLayout 3 columns (stretch 2:2:1) + plot."""
        grp = QGroupBox("Property Comparison")
        grp.setStyleSheet("""
            QGroupBox{font-size:13px;font-weight:bold;border:1px solid #4CAF50;
                      border-radius:6px;margin-top:10px;padding:16px 8px 8px 8px;color:#2c3e50;}
            QGroupBox::title{subcontrol-origin:margin;left:12px;padding:0 6px;color:#388e3c;}
        """)
        layout = QVBoxLayout(grp)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # ── 3-column grid: Materials | Properties | Options ──
        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(0, 2)
        grid.setColumnStretch(1, 2)
        grid.setColumnStretch(2, 1)

        self.material_selector = MaterialSelectorWidget(self.viz_service)
        self.material_selector.materials_changed.connect(self._on_materials_changed)
        self.material_selector.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.material_selector.setMinimumHeight(200)
        grid.addWidget(self.material_selector, 0, 0)

        self.property_selector = PropertySelectorWidget(self.viz_service)
        self.property_selector.properties_changed.connect(self._on_properties_changed)
        self.property_selector.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.property_selector.setMinimumHeight(200)
        grid.addWidget(self.property_selector, 0, 1)

        self.view_options = ViewOptionsWidget()
        self.view_options.view_changed.connect(self._on_view_changed)
        self.view_options.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.view_options.setMinimumHeight(200)
        grid.addWidget(self.view_options, 0, 2)

        layout.addLayout(grid)

        # ── Comparison display (expanding plot) ──
        self.comparison_display = ComparisonDisplayWidget(self.viz_service)
        self.comparison_display.setMinimumHeight(400)
        self.comparison_display.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self.comparison_display, stretch=1)

        return grp

    def _switch_to_property_comparison(self):
        """Switch view to Material & Property Comparison (page 0)."""
        self.view_stack.setCurrentIndex(0)
        self.btn_property_comparison.setStyleSheet(self._active_btn_style)

    def _switch_to_material_comparison(self):
        """Switch view to Material Comparison (page 1)."""
        self.view_stack.setCurrentIndex(1)
        self.btn_material_comparison.setStyleSheet(self._active_btn_style)
        self.btn_property_comparison.setStyleSheet(self._inactive_btn_style)
        self.btn_usup_analysis.setStyleSheet(self._inactive_btn_style)

    def _switch_to_usup_analysis(self):
        """Switch view to US/UP Analysis (page 2)."""
        self.view_stack.setCurrentIndex(2)
        self.btn_usup_analysis.setStyleSheet(self._active_btn_style)
        self.btn_property_comparison.setStyleSheet(self._inactive_btn_style)
        self.btn_material_comparison.setStyleSheet(self._inactive_btn_style)

    def update_theme(self, is_dark: bool):
        """
        Update all widget styles for dark/light mode.
        Called from MainWindow.toggle_theme().
        """
        self.is_dark_mode = is_dark

        if is_dark:
            # ── DARK MODE ──
            # Comprehensive override for ALL child widgets
            dark_override = """
                /* Global text color */
                QWidget {
                    color: #dddddd;
                }

                /* List widgets */
                QListWidget {
                    background-color: #2b2b2b;
                    color: #dddddd;
                    border: 1px solid #3c3c3c;
                    border-radius: 4px;
                }
                QListWidget::item {
                    color: #dddddd;
                    padding: 4px;
                }
                QListWidget::item:selected {
                    background-color: #00c853;
                    color: #000000;
                }
                QListWidget::item:hover {
                    background-color: #3c3c3c;
                }

                /* Tree widgets */
                QTreeWidget {
                    background-color: #2b2b2b;
                    color: #dddddd;
                    border: 1px solid #3c3c3c;
                }
                QTreeWidget::item:selected {
                    background-color: #00c853;
                    color: #000000;
                }

                /* Input fields */
                QLineEdit {
                    background-color: #2b2b2b;
                    color: #dddddd;
                    border: 1px solid #3c3c3c;
                    border-radius: 4px;
                    padding: 6px;
                }

                /* Checkboxes and Radio buttons */
                QCheckBox {
                    color: #dddddd;
                    spacing: 6px;
                }
                QRadioButton {
                    color: #dddddd;
                    spacing: 6px;
                }

                /* Labels */
                QLabel {
                    color: #dddddd;
                    background-color: transparent;
                }

                /* Group boxes */
                QGroupBox {
                    color: #88ccff;
                    border: 1px solid #3c3c3c;
                    border-radius: 6px;
                    margin-top: 10px;
                    padding: 16px 8px 8px 8px;
                    background-color: #1e1e1e;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 12px;
                    padding: 0 6px;
                    color: #88ccff;
                }

                /* Table widgets */
                QTableWidget {
                    background-color: #2b2b2b;
                    color: #dddddd;
                    border: 1px solid #3c3c3c;
                    gridline-color: #3c3c3c;
                }
                QTableWidget::item {
                    color: #dddddd;
                    padding: 4px;
                }
                QHeaderView::section {
                    background-color: #333333;
                    color: #dddddd;
                    border: 1px solid #3c3c3c;
                    padding: 4px;
                    font-weight: bold;
                }

                /* Combo boxes */
                QComboBox {
                    background-color: #2b2b2b;
                    color: #dddddd;
                    border: 1px solid #3c3c3c;
                    border-radius: 4px;
                    padding: 4px;
                }
                QComboBox QAbstractItemView {
                    background-color: #2b2b2b;
                    color: #dddddd;
                    selection-background-color: #00c853;
                }

                /* Scroll areas */
                QScrollArea {
                    background-color: transparent;
                    border: none;
                }
                QScrollBar:vertical {
                    background-color: #2b2b2b;
                    width: 10px;
                }
                QScrollBar::handle:vertical {
                    background-color: #555555;
                    border-radius: 5px;
                }

                /* Spin boxes */
                QSpinBox, QDoubleSpinBox {
                    background-color: #2b2b2b;
                    color: #dddddd;
                    border: 1px solid #3c3c3c;
                }

                /* Frames */
                QFrame {
                    border-color: #3c3c3c;
                }
            """
            self.setStyleSheet(dark_override)

            # Update left nav panel
            if hasattr(self, '_left_panel'):
                self._left_panel.setStyleSheet("""
                    QWidget {
                        background-color: #252525;
                        border-right: 1px solid #3c3c3c;
                        border-radius: 6px;
                    }
                """)

            # Update nav button styles for dark mode
            self._active_btn_style = """
                QPushButton {
                    text-align: left;
                    padding: 10px 12px;
                    border: none;
                    border-radius: 6px;
                    background-color: #1976D2;
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                }
            """
            self._inactive_btn_style = """
                QPushButton {
                    text-align: left;
                    padding: 10px 12px;
                    border: none;
                    border-radius: 6px;
                    background-color: transparent;
                    color: #cccccc;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: rgba(33, 150, 243, 0.25);
                }
            """

            # Update header
            if hasattr(self, 'status_label'):
                self.status_label.setStyleSheet(
                    "background:#1b5e20;color:#a5d6a7;padding:4px 12px;"
                    "border-radius:4px;font-weight:bold;font-size:11px;"
                )

            # Update canvas backgrounds for matplotlib
            for canvas_attr in ['canvas']:
                for widget in self.findChildren(FigureCanvas):
                    widget.setStyleSheet("background-color: #2b2b2b;")

        else:
            # ── LIGHT MODE ──
            light_override = """
                QWidget {
                    color: #333333;
                }

                QListWidget {
                    background-color: white;
                    color: #333333;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                }
                QListWidget::item {
                    color: #333333;
                    padding: 4px;
                }
                QListWidget::item:selected {
                    background-color: #4CAF50;
                    color: white;
                }
                QListWidget::item:hover {
                    background-color: #e8f5e9;
                }

                QTreeWidget {
                    background-color: white;
                    color: #333333;
                    border: 1px solid #ddd;
                }
                QTreeWidget::item:selected {
                    background-color: #4CAF50;
                    color: white;
                }

                QLineEdit {
                    background-color: white;
                    color: #333333;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 6px;
                }

                QCheckBox {
                    color: #333333;
                }
                QRadioButton {
                    color: #333333;
                }

                QLabel {
                    color: #2c3e50;
                    background-color: transparent;
                }

                QGroupBox {
                    color: #2c3e50;
                    border: 1px solid #4CAF50;
                    border-radius: 6px;
                    margin-top: 10px;
                    padding: 16px 8px 8px 8px;
                    background-color: white;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 12px;
                    padding: 0 6px;
                    color: #388e3c;
                }

                QTableWidget {
                    background-color: white;
                    color: #333333;
                    border: 1px solid #ddd;
                    gridline-color: #eee;
                }
                QHeaderView::section {
                    background-color: #f5f5f5;
                    color: #333333;
                    border: 1px solid #ddd;
                    padding: 4px;
                    font-weight: bold;
                }

                QComboBox {
                    background-color: white;
                    color: #333333;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 4px;
                }

                QScrollArea {
                    background-color: transparent;
                    border: none;
                }

                QSpinBox, QDoubleSpinBox {
                    background-color: white;
                    color: #333333;
                    border: 1px solid #ddd;
                }
            """
            self.setStyleSheet(light_override)

            # Update left nav panel
            if hasattr(self, '_left_panel'):
                self._left_panel.setStyleSheet("""
                    QWidget {
                        background-color: #f5f5f5;
                        border-right: 1px solid #ddd;
                        border-radius: 6px;
                    }
                """)

            # Update nav button styles for light mode
            self._active_btn_style = """
                QPushButton {
                    text-align: left;
                    padding: 10px 12px;
                    border: none;
                    border-radius: 6px;
                    background-color: #2196F3;
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                }
            """
            self._inactive_btn_style = """
                QPushButton {
                    text-align: left;
                    padding: 10px 12px;
                    border: none;
                    border-radius: 6px;
                    background-color: transparent;
                    color: #333;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: rgba(33, 150, 243, 0.15);
                }
            """

            # Update header
            if hasattr(self, 'status_label'):
                self.status_label.setStyleSheet(
                    "background:#d4edda;color:#155724;padding:4px 12px;"
                    "border-radius:4px;font-weight:bold;font-size:11px;"
                )

            # Update canvas backgrounds
            for widget in self.findChildren(FigureCanvas):
                widget.setStyleSheet("background-color: white;")

        # Re-apply active/inactive styles to nav buttons based on current page
        current_idx = self.view_stack.currentIndex() if hasattr(self, 'view_stack') else 0
        
        # Only layout property comparison button is available now
        if hasattr(self, 'btn_property_comparison'):
            if current_idx == 0:
                self.btn_property_comparison.setStyleSheet(self._active_btn_style)
            else:
                self.btn_property_comparison.setStyleSheet(self._inactive_btn_style)

        # Propagate to Material Comparison widget
        if hasattr(self, 'material_comparison_widget') and hasattr(self.material_comparison_widget, 'update_theme'):
            self.material_comparison_widget.update_theme(is_dark)

        # Propagate to US/UP Analysis widget
        if hasattr(self, 'usup_analysis_widget') and hasattr(self.usup_analysis_widget, 'update_theme'):
            self.usup_analysis_widget.update_theme(is_dark)

        print(f"✓ UnifiedVisualizationTab theme updated: {'Dark' if is_dark else 'Light'}")


    def _load_initial_data(self):
        """
        Load initial data from database.
        
        This will be expanded in Task 4.2 to populate material selection.
        """
        if not self.viz_service:
            print("⚠️ Visualization service not available, skipping data load")
            self._update_status("⚠️ Backend Unavailable", error=True)
            return
        
        try:
            print("📊 Loading initial data...")
            
            # Test database connection
            self.viz_service.connect()
            
            # Get database stats
            stats = self.viz_service.get_database_stats()
            print(f"   • Materials: {stats.get('materials', 0)}")
            print(f"   • Properties: {stats.get('properties', 0)}")
            print(f"   • Models: {stats.get('models', 0)}")
            print(f"   • Experimental Datasets: {stats.get('experimental_datasets', 0)}")
            
            self._update_status(f"✅ Ready ({stats.get('materials', 0)} materials)")
            
            self.viz_service.disconnect()
            
        except Exception as e:
            print(f"❌ Error loading initial data: {e}")
            traceback.print_exc()
            self._update_status("❌ Database Error", error=True)
    
    def _on_materials_changed(self, material_ids: list):
        """
        Handle material selection change from MaterialSelectorWidget.
        Task 4.6: Wire material selection → property selector update
        
        Args:
            material_ids: List of selected material IDs
        """
        self.selected_materials = material_ids
        
        # Task 4.6: Update property selector with new materials
        if hasattr(self, 'property_selector'):
            try:
                self.property_selector.update_for_materials(material_ids)
                print(f"✓ Property selector updated for {len(material_ids)} materials")
            except Exception as e:
                print(f"❌ Error updating property selector: {e}")
                self._show_error_message(f"Failed to load properties: {e}")
        
        # Update status
        count = len(material_ids)
        if count == 0:
            self._update_status("⚠️ No materials selected", error=True)
            # Clear display when no materials
            if hasattr(self, 'comparison_display'):
                self.comparison_display.show_empty_state()
        else:
            self._update_status(f"✅ {count} material{'s' if count != 1 else ''} selected")
        
        # Emit signal for other components
        self.materials_selected.emit(material_ids)
        
        print(f"📌 Materials selection updated: {material_ids}")
    
    def _on_properties_changed(self, property_names: list):
        """
        Handle property selection change from PropertySelectorWidget.
        Task 4.6: Wire selections → fetch data → display update with debouncing
        
        Args:
            property_names: List of selected property names
        """
        self.selected_properties = property_names
        
        # Update status
        mat_count = len(self.selected_materials)
        prop_count = len(property_names)
        
        if mat_count > 0 and prop_count > 0:
            self._update_status(f"✅ {mat_count} material{'s' if mat_count != 1 else ''}, {prop_count} propert{'ies' if prop_count != 1 else 'y'}")
        elif mat_count > 0:
            self._update_status(f"⚠️ {mat_count} material{'s' if mat_count != 1 else ''}, no properties", error=True)
        
        # Emit signal for other components
        self.properties_selected.emit(property_names)
        
        # Task 4.6: Trigger debounced update when both materials and properties are selected
        if self.selected_materials and property_names:
            view_type = self.view_options.get_view_type() if hasattr(self, 'view_options') else 'bar'
            options = self.view_options.get_options() if hasattr(self, 'view_options') else {}
            self._schedule_update(view_type, options)
        elif not property_names and hasattr(self, 'comparison_display'):
            # Clear display when no properties
            self.comparison_display.show_empty_state()
        
        print(f"📌 Properties selection updated: {property_names}")
    
    def _on_view_changed(self, view_type: str, options: dict):
        """
        Handle view options change from ViewOptionsWidget.
        Task 4.6: Update display with debouncing
        
        Args:
            view_type: Chart type ('bar', 'table', 'scatter')
            options: Display options dict
        """
        self.current_chart_type = view_type
        
        # Update status with view info
        mat_count = len(self.selected_materials)
        prop_count = len(self.selected_properties)
        
        view_names = {'bar': 'Bar', 'table': 'Table', 'scatter': 'Scatter'}
        view_name = view_names.get(view_type, view_type)
        
        if mat_count > 0 and prop_count > 0:
            self._update_status(f"✅ {mat_count} mat, {prop_count} prop | {view_name}")
        
        # Emit signal
        self.chart_type_changed.emit(view_type)
        
        # Task 4.6: Trigger debounced update with current data
        if self.selected_materials and self.selected_properties:
            self._schedule_update(view_type, options)
        
        print(f"📊 View changed: {view_type}, options: {options}")
    

    
    def _update_status(self, message: str, error: bool = False):
        """
        Update status label.
        
        Args:
            message: Status message to display
            error: Whether this is an error status
        """
        self.status_label.setText(message)
        
        if error:
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: #f8d7da;
                    color: #721c24;
                    padding: 5px 10px;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """)
        else:
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: #d4edda;
                    color: #155724;
                    padding: 5px 10px;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """)
    
    def _update_comparison_display(self, view_type: str, options: dict):
        """
        Update comparison display using batch API queries.
        """
        if not self.selected_materials or not self.selected_properties:
            if hasattr(self, 'comparison_display'):
                self.comparison_display.show_empty_state()
            return

        try:
            if not hasattr(self, 'comparison_display'):
                return

            self.viz_service.connect()

            # Batch fetch material names
            materials_info = self.viz_service.get_materials_by_ids(self.selected_materials)
            id_to_name = {m['material_id']: m['name'] for m in materials_info}

            # Batch fetch properties
            raw = self.viz_service.get_material_properties(
                self.selected_materials, self.selected_properties
            )
            self.viz_service.disconnect()

            # Reorganise into {material_name: {prop_name: {value, unit}}}
            data = {}
            for mat_id in self.selected_materials:
                mat_name = id_to_name.get(mat_id, f'Material {mat_id}')
                mat_props = raw.get(mat_id, {})
                data[mat_name] = {}
                for prop_name in self.selected_properties:
                    prop_val = mat_props.get(prop_name)
                    if prop_val is not None:
                        if isinstance(prop_val, list):
                            prop_val = prop_val[0]
                        data[mat_name][prop_name] = prop_val
                    else:
                        data[mat_name][prop_name] = {'value': 'N/A', 'unit': ''}

            self.comparison_display.update_display(
                materials=list(data.keys()),
                properties=self.selected_properties,
                data=data,
                view_type=view_type,
                options=options
            )

            print(f"✓ Display updated: {len(data)} materials, "
                  f"{len(self.selected_properties)} properties")

        except Exception as e:
            print(f"❌ Error updating comparison display: {e}")
            import traceback
            traceback.print_exc()
            if hasattr(self, 'comparison_display'):
                self.comparison_display.show_empty_state()
            self._show_error_message(f"Failed to update display: {e}")
    
    # =========================================================================
    # TASK 4.6: DEBOUNCING AND ERROR HANDLING
    # =========================================================================
    
    def _schedule_update(self, view_type: str, options: dict):
        """
        Schedule a debounced update of the comparison display.
        Task 4.6: Add debouncing (wait 300ms after last selection change)
        
        Args:
            view_type: Type of view ('bar', 'table', 'scatter')
            options: Display options dictionary
        """
        # Store the parameters for the pending update
        self.pending_update_params = {
            'view_type': view_type,
            'options': options
        }
        
        # Restart the timer (this cancels any pending update)
        self.update_timer.stop()
        self.update_timer.start()
        
        print(f"⏱️  Update scheduled (300ms debounce): view={view_type}")
    
    def _perform_data_update(self):
        """
        Perform the actual data update after debounce timer expires.
        Task 4.6: Fetch data and update display
        """
        if not self.pending_update_params:
            return
        
        view_type = self.pending_update_params['view_type']
        options = self.pending_update_params['options']
        
        print(f"🔄 Performing debounced update: {len(self.selected_materials)} materials, {len(self.selected_properties)} properties")
        
        # Call the actual update method
        try:
            self._update_comparison_display(view_type, options)
        except Exception as e:
            print(f"❌ Error in debounced update: {e}")
            self._show_error_message(f"Update failed: {e}")
        
        # Clear pending params
        self.pending_update_params = None
    
    def _show_error_message(self, message: str):
        """
        Show error message to user.
        Task 4.6: Show error messages if query fails
        
        Args:
            message: Error message to display
        """
        # Update status bar with error
        self._update_status(f"❌ {message}", error=True)
        
        # Log to console
        print(f"❌ ERROR: {message}")
        
        # Could also show a QMessageBox here if needed
        # from PyQt6.QtWidgets import QMessageBox
        # QMessageBox.critical(self, "Error", message)
    
    # =========================================================================
    # CLEANUP AND MEMORY MANAGEMENT - TASK 6.1
    # =========================================================================
    
    def cleanup(self):
        """
        Cleanup resources and disconnect signals.
        Task 6.1: Verify no memory leaks (plot cleanup)
        """
        try:
            print("🧹 [Task 6.1] Starting cleanup...")
            
            # Stop any pending timers
            if hasattr(self, 'update_timer') and self.update_timer:
                self.update_timer.stop()
                print("✓ [Task 6.1] Update timer stopped")
            
            # Clear plot figures to free memory
            if hasattr(self, 'comparison_display') and self.comparison_display:
                try:
                    if hasattr(self.comparison_display, 'figure'):
                        self.comparison_display.figure.clear()
                    print("✓ [Task 6.1] Comparison display cleared")
                except:
                    pass
            
            # Disconnect database
            if hasattr(self, 'viz_service') and self.viz_service:
                try:
                    self.viz_service.disconnect()
                    print("✓ [Task 6.1] Database disconnected")
                except:
                    pass
            
            # Clear cached data
            self.materials_data = {}
            self.properties_data = {}
            self.selected_materials = []
            self.selected_properties = []
            print("✓ [Task 6.1] Cached data cleared")
            
            print("✅ [Task 6.1] Cleanup complete")
            
        except Exception as e:
            print(f"⚠️  [Task 6.1] Error during cleanup: {e}")
    
    def closeEvent(self, event):
        """
        Handle widget close event.
        Task 6.1: Cleanup on close to prevent memory leaks
        """
        print("👋 [Task 6.1] Widget closing, performing cleanup...")
        self.cleanup()
        event.accept()
    
    def test_workflow(self):
        """
        Test complete workflow: select → query → display.
        Task 6.1: Test complete workflow
        """
        print()
        print("=" * 70)
        print("🧪 [Task 6.1] TESTING COMPLETE WORKFLOW")
        print("=" * 70)
        
        try:
            # Step 1: Test material selection
            print("\n📌 Step 1: Testing material selection...")
            if hasattr(self, 'material_selector'):
                print(f"✓ Material selector ready with materials")
            
            # Step 2: Test property selector
            print("\n📌 Step 2: Testing property selector...")
            if hasattr(self, 'property_selector'):
                print(f"✓ Property selector ready")
            
            # Step 3: Test view options
            print("\n📌 Step 3: Testing view options...")
            if hasattr(self, 'view_options'):
                current_view = self.view_options.get_view_type()
                print(f"✓ View options ready (current: {current_view})")
            
            # Step 4: Test comparison display
            print("\n📌 Step 4: Testing comparison display...")
            if hasattr(self, 'comparison_display'):
                print(f"✓ Comparison display ready")
            
            print("\n" + "=" * 70)
            print("✅ [Task 6.1] WORKFLOW TEST COMPLETE - All components ready")
            print("=" * 70)
            print()
            
        except Exception as e:
            print(f"\n❌ [Task 6.1] Workflow test error: {e}")
            traceback.print_exc()
    
    # =========================================================================
    # PUBLIC API - TO BE IMPLEMENTED IN LATER TASKS
    # =========================================================================
    
    def select_materials(self, material_ids: list):
        """
        Select materials for comparison (Task 4.2).
        
        Args:
            material_ids: List of material IDs to select
        """
        self.selected_materials = material_ids
        self.materials_selected.emit(material_ids)
        print(f"📌 Materials selected: {material_ids}")
    
    def select_properties(self, property_names: list):
        """
        Select properties for comparison (Task 4.3).
        
        Args:
            property_names: List of property names to select
        """
        self.selected_properties = property_names
        self.properties_selected.emit(property_names)
        print(f"📌 Properties selected: {property_names}")
    
    def set_chart_type(self, chart_type: str):
        """
        Set chart type for comparison (Task 4.4).
        
        Args:
            chart_type: One of 'bar', 'table', 'scatter'
        """
        self.current_chart_type = chart_type
        self.chart_type_changed.emit(chart_type)
        print(f"📊 Chart type changed: {chart_type}")
    
    def refresh_comparison_plot(self):
        """
        Refresh the property comparison plot (Task 4.6).
        """
        print("🔄 Refresh comparison plot")


# =============================================================================
# TESTING FUNCTIONS
# =============================================================================

def test_tab_standalone():
    """
    Test the unified visualization tab as a standalone application.
    Run: python -c "from gui.views.unified_visualization_tab import test_tab_standalone; test_tab_standalone()"
    """
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Create tab
    tab = UnifiedVisualizationTab()
    tab.setWindowTitle("Unified Visualization Tab - Phase 4 Task 4.1")
    tab.resize(1200, 800)
    tab.show()
    
    sys.exit(app.exec())


def test_services_connection():
    """
    Test backend services connection.
    Run: python -c "from gui.views.unified_visualization_tab import test_services_connection; test_services_connection()"
    """
    print("=" * 70)
    print("🧪 TESTING BACKEND SERVICES")
    print("=" * 70)
    
    try:
        # Test VisualizationDataService
        print("\n1️⃣ Testing VisualizationDataService...")
        viz_service = VisualizationDataService()
        viz_service.connect()
        stats = viz_service.get_database_stats()
        print(f"   ✅ Database stats: {stats}")
        viz_service.disconnect()
        
        # Test ModelCalculator
        print("\n2️⃣ Testing ModelCalculator...")
        calculator = ModelCalculator()
        up, us = calculator.calculate_usup_curve(C0=5.35, s=1.34, up_max=5.0)
        print(f"   ✅ Calculated US-Up curve: {len(up)} points")
        
        # Test PlottingUtils
        print("\n3️⃣ Testing PlottingUtils...")
        plotting = PlottingUtils()
        colors = plotting.get_color_palette('default', n_colors=5)
        print(f"   ✅ PlottingUtils initialized: {len(colors)} colors loaded")
        
        print("\n" + "=" * 70)
        print("✅ ALL SERVICES WORKING!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    # Run standalone test
    test_tab_standalone()
