"""
Visualization Tab - Offline Material Data Visualization

Creates interactive charts and dashboards for material property comparison.
Fully offline using matplotlib embedded in PyQt6.
"""

# CRITICAL: Set matplotlib backend BEFORE any other matplotlib imports
import matplotlib
matplotlib.use('QtAgg', force=True)  # Force QtAgg backend for PyQt6 compatibility

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
# DO NOT import pyplot - we use Figure directly for better control
import numpy as np

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QListWidget, QComboBox,
    QGroupBox, QSplitter, QFrame, QFileDialog,
    QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor


class VisualizationTab(QWidget):
    """
    Visualization tab for material property comparison.
    
    Layout:
    - Left: Control panel (material/property selection, chart type)
    - Center: Matplotlib plot area
    - Right: Dashboard with statistics
    """
    
    def __init__(self, db_manager, querier):
        super().__init__()
        
        print("[VizTab] Initializing Visualization Tab...")
        
        self.db_manager = db_manager
        self.querier = querier
        
        # Data storage
        self.materials_data = {}  # {material_name: property_data_dict}
        self.selected_materials = []
        self.selected_properties = []
        
        # Matplotlib setup
        self.figure = None
        self.canvas = None
        self.ax = None
        self.toolbar = None  # Store toolbar reference for theme updates
        
        print("[VizTab] Setting up UI...")
        self.setup_ui()
        print("[VizTab] Loading materials...")
        self.load_available_materials()
        print("[VizTab] Initialization complete!")
        
    def setup_ui(self):
        """Initialize the user interface."""
        print("[VizTab] setup_ui() called")
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create three panels
        control_panel = self.create_control_panel()
        plot_panel = self.create_plot_panel()
        dashboard_panel = self.create_dashboard_panel()
        
        # Add panels with proportions: 25% control, 50% plot, 25% dashboard
        main_layout.addWidget(control_panel, stretch=2)
        main_layout.addWidget(plot_panel, stretch=4)
        main_layout.addWidget(dashboard_panel, stretch=2)
        
    def create_control_panel(self):
        """Create left control panel with material/property selection."""
        panel = QFrame()
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("Control Panel")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Info label about linkage
        info_label = QLabel("💡 Linked with Material Browser\nSelect a material there to auto-populate here")
        info_label.setProperty("class", "info-label")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Material selection
        mat_group = QGroupBox("Select Materials")
        mat_layout = QVBoxLayout(mat_group)
        
        self.material_list = QListWidget()
        self.material_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        mat_layout.addWidget(self.material_list)
        
        layout.addWidget(mat_group)
        
        # Property selection
        prop_group = QGroupBox("Select Properties")
        prop_layout = QVBoxLayout(prop_group)
        
        self.property_list = QListWidget()
        self.property_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        
        # Common properties (normalized names matching database)
        common_properties = [
            "density",
            "cp",  # Specific heat (constant pressure)
            "cv",  # Specific heat (constant volume)
            "viscosity",
            "thermal_conductivity",
            "thermal_expansion",
            "youngs_modulus",
            "shear_modulus",
            "bulk_modulus",
            "poissons_ratio",
            "yield_strength",
            "electrical_conductivity"
        ]
        
        for prop in common_properties:
            self.property_list.addItem(prop)
            self.property_list.addItem(prop)
        
        prop_layout.addWidget(self.property_list)
        layout.addWidget(prop_group)
        
        # Data view mode selection
        view_group = QGroupBox("Data View Mode")
        view_layout = QVBoxLayout(view_group)
        
        self.view_mode_combo = QComboBox()
        self.view_mode_combo.addItems(["Active View (with Overrides)", "Original Data (no Overrides)"])
        self.view_mode_combo.setToolTip("Match the data view from Material Browser tabs")
        view_layout.addWidget(self.view_mode_combo)
        
        layout.addWidget(view_group)
        
        # Chart type selection
        chart_group = QGroupBox("Chart Type")
        chart_layout = QVBoxLayout(chart_group)
        
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems([
            "Line", 
            "Bar", 
            "Scatter", 
            "Area", 
            "Pie",
            "Histogram"
        ])
        chart_layout.addWidget(self.chart_type_combo)
        
        layout.addWidget(chart_group)
        
        # Action buttons
        self.generate_btn = QPushButton("Generate Plot")
        self.generate_btn.clicked.connect(self.generate_plot)
        print("[VizTab] Generate Plot button created and connected")
        layout.addWidget(self.generate_btn)
        
        self.export_btn = QPushButton("Export Plot (PNG/PDF)")
        self.export_btn.clicked.connect(self.export_plot)
        layout.addWidget(self.export_btn)
        
        layout.addStretch()
        
        return panel
        
    def create_plot_panel(self):
        """Create center panel with matplotlib canvas."""
        panel = QFrame()
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        title = QLabel("Plot Area")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Matplotlib figure and canvas
        print("[VizTab] Creating matplotlib Figure...")
        try:
            self.figure = Figure(figsize=(8, 6), dpi=100)
            print("[VizTab] Figure created successfully")
            
            print("[VizTab] Creating FigureCanvas...")
            self.canvas = FigureCanvas(self.figure)
            print("[VizTab] FigureCanvas created successfully")
            
            print("[VizTab] Adding subplot...")
            self.ax = self.figure.add_subplot(111)
            print("[VizTab] Subplot added successfully")
            
            # Initial empty plot
            self.ax.text(0.5, 0.5, 'Select materials and properties,\nthen click "Generate Plot"',
                        ha='center', va='center', fontsize=12, color='gray')
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            
            # Navigation toolbar
            print("[VizTab] Creating NavigationToolbar...")
            self.toolbar = NavigationToolbar(self.canvas, panel)
            print("[VizTab] NavigationToolbar created successfully")
            
            layout.addWidget(self.toolbar)
            layout.addWidget(self.canvas)
            print("[VizTab] Plot panel created successfully!")
            
        except Exception as e:
            print(f"[VizTab] ERROR creating plot panel: {e}")
            import traceback
            traceback.print_exc()
        
        return panel
        
    def create_dashboard_panel(self):
        """Create right panel with statistics cards."""
        panel = QFrame()
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("Dashboard")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Statistics cards
        self.stats_layout = QGridLayout()
        
        # Card: Selected Materials
        self.mat_count_label = self.create_stat_card("Materials\nSelected", "0", "#2196F3")
        self.stats_layout.addWidget(self.mat_count_label, 0, 0)
        
        # Card: Selected Properties
        self.prop_count_label = self.create_stat_card("Properties\nSelected", "0", "#4CAF50")
        self.stats_layout.addWidget(self.prop_count_label, 0, 1)
        
        # Card: Data Points
        self.data_points_label = self.create_stat_card("Data\nPoints", "0", "#FF9800")
        self.stats_layout.addWidget(self.data_points_label, 1, 0)
        
        # Card: Missing Values
        self.missing_label = self.create_stat_card("Missing\nValues", "0", "#F44336")
        self.stats_layout.addWidget(self.missing_label, 1, 1)
        
        layout.addLayout(self.stats_layout)
        
        # Detail text area
        detail_group = QGroupBox("Details")
        detail_layout = QVBoxLayout(detail_group)
        
        self.detail_text = QLabel("No data loaded")
        self.detail_text.setProperty("class", "detail-text")
        self.detail_text.setWordWrap(True)
        self.detail_text.setAlignment(Qt.AlignmentFlag.AlignTop)
        detail_layout.addWidget(self.detail_text)
        
        layout.addWidget(detail_group)
        layout.addStretch()
        
        return panel
        
    def create_stat_card(self, title, value, color):
        """Create a colored statistics card."""
        card = QFrame()
        card.setFrameShape(QFrame.Shape.Box)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 5px;
                padding: 10px;
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setProperty("class", "stat-card-title")
        
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setProperty("class", "stat-card-value")
        value_label.setObjectName(f"{title.replace(chr(10), '_')}_value")
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)
        
        return card
        
    def load_available_materials(self):
        """Load materials from database."""
        try:
            cursor = self.db_manager.connect().cursor()
            cursor.execute("SELECT name FROM materials ORDER BY name")
            materials = cursor.fetchall()
            cursor.close()
            
            self.material_list.clear()
            for (name,) in materials:
                self.material_list.addItem(name)
                
        except Exception as e:
            print(f"Error loading materials: {e}")
            
    def select_material(self, material_name):
        """
        Programmatically select a material in the list.
        Called when material is selected in Material Browser.
        """
        print(f"[VizTab] Selecting material: {material_name}")
        
        # Find and select the material in the list
        for i in range(self.material_list.count()):
            item = self.material_list.item(i)
            if item.text() == material_name:
                item.setSelected(True)
                self.material_list.scrollToItem(item)
                print(f"[VizTab] Material '{material_name}' selected in visualization tab")
                return
        
        print(f"[VizTab] Material '{material_name}' not found in list")
    
    def update_theme(self, is_dark_mode):
        """
        Update matplotlib toolbar colors based on theme.
        Called by main window when theme changes.
        """
        if self.toolbar:
            if is_dark_mode:
                # Dark mode: light icons on dark background
                self.toolbar.setStyleSheet("""
                    QToolBar {
                        background-color: #3c3c3c;
                        border: none;
                        spacing: 5px;
                        padding: 5px;
                    }
                    QToolButton {
                        background-color: transparent;
                        color: #ffffff;
                        border: none;
                        padding: 5px;
                        border-radius: 3px;
                    }
                    QToolButton:hover {
                        background-color: #555555;
                    }
                    QToolButton:pressed {
                        background-color: #0078d4;
                    }
                """)
                # Restore original icons for dark mode
                self._restore_toolbar_icons()
            else:
                # Light mode: dark icons on light background
                self.toolbar.setStyleSheet("""
                    QToolBar {
                        background-color: #ffffff;
                        border: none;
                        border-bottom: 1px solid #d0d0d0;
                        spacing: 5px;
                        padding: 5px;
                    }
                    QToolButton {
                        background-color: #f5f5f5;
                        color: #000000;
                        border: 1px solid #d0d0d0;
                        padding: 5px;
                        border-radius: 3px;
                    }
                    QToolButton:hover {
                        background-color: #e0e0e0;
                        border: 1px solid #0078d4;
                    }
                    QToolButton:pressed {
                        background-color: #0078d4;
                        color: #ffffff;
                        border: 1px solid #0078d4;
                    }
                """)
                # Invert toolbar icons for light mode
                self._invert_toolbar_icons()
            print(f"[VizTab] Toolbar theme updated to {'dark' if is_dark_mode else 'light'} mode")
        
        # Also update matplotlib plot background colors
        if self.figure and self.ax:
            if is_dark_mode:
                self.figure.patch.set_facecolor('#2b2b2b')
                self.ax.set_facecolor('#252525')
                self.ax.tick_params(colors='white', which='both')
                self.ax.spines['bottom'].set_color('white')
                self.ax.spines['top'].set_color('white')
                self.ax.spines['left'].set_color('white')
                self.ax.spines['right'].set_color('white')
                self.ax.xaxis.label.set_color('white')
                self.ax.yaxis.label.set_color('white')
                self.ax.title.set_color('white')
            else:
                self.figure.patch.set_facecolor('#ffffff')
                self.ax.set_facecolor('#ffffff')
                self.ax.tick_params(colors='black', which='both')
                self.ax.spines['bottom'].set_color('black')
                self.ax.spines['top'].set_color('black')
                self.ax.spines['left'].set_color('black')
                self.ax.spines['right'].set_color('black')
                self.ax.xaxis.label.set_color('black')
                self.ax.yaxis.label.set_color('black')
                self.ax.title.set_color('black')
            
            self.canvas.draw()
            print(f"[VizTab] Plot colors updated to {'dark' if is_dark_mode else 'light'} mode")
    
    def _invert_toolbar_icons(self):
        """Invert toolbar icon colors for light mode visibility."""
        if not self.toolbar:
            return
        
        # Store original icons if not already stored
        if not hasattr(self, '_original_icons'):
            self._original_icons = {}
        
        # Iterate through all actions in the toolbar
        for action in self.toolbar.actions():
            if action.icon() and not action.icon().isNull():
                # Store original icon if not already stored
                action_name = action.text() or action.objectName()
                if action_name not in self._original_icons:
                    self._original_icons[action_name] = action.icon()
                
                # Get the icon and invert its colors
                original_icon = self._original_icons[action_name]
                inverted_icon = self._create_inverted_icon(original_icon)
                action.setIcon(inverted_icon)
        
        print("[VizTab] Toolbar icons inverted for light mode")
    
    def _restore_toolbar_icons(self):
        """Restore original toolbar icons for dark mode."""
        if not self.toolbar or not hasattr(self, '_original_icons'):
            return
        
        # Restore original icons
        for action in self.toolbar.actions():
            action_name = action.text() or action.objectName()
            if action_name in self._original_icons:
                action.setIcon(self._original_icons[action_name])
        
        print("[VizTab] Toolbar icons restored for dark mode")
    
    def _create_inverted_icon(self, icon):
        """Create an inverted version of an icon."""
        # Get the pixmap from the icon
        pixmap = icon.pixmap(24, 24)  # Standard toolbar icon size
        
        # Create a new image to draw the inverted version
        inverted_pixmap = QPixmap(pixmap.size())
        inverted_pixmap.fill(Qt.GlobalColor.transparent)
        
        # Create painter
        painter = QPainter(inverted_pixmap)
        
        # Draw the original pixmap
        painter.drawPixmap(0, 0, pixmap)
        
        # Apply composition mode to invert colors
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Difference)
        painter.fillRect(inverted_pixmap.rect(), QColor(255, 255, 255))
        
        painter.end()
        
        return QIcon(inverted_pixmap)
        
    def auto_select_common_properties(self):
        """Auto-select common properties for quick visualization."""
        common_props = ['density', 'specific_heat_capacity', 'thermal_conductivity']
        
        for i in range(self.property_list.count()):
            item = self.property_list.item(i)
            if item.text() in common_props:
                item.setSelected(True)
                
    def fetch_material_data(self, material_name):
        """
        Fetch material property data from database.
        
        Returns dict: {property_name: [{value, unit, ref}]}
        """
        try:
            # Determine whether to apply overrides based on view mode
            view_mode = self.view_mode_combo.currentText()
            apply_overrides = "Active View" in view_mode
            
            print(f"[VizTab] Fetching {material_name} with overrides={apply_overrides}")
            
            # Get material data
            material_data = self.querier.get_material_by_name(material_name, apply_overrides=apply_overrides)
            
            if not material_data:
                print(f"[VizTab] No material_data returned for {material_name}")
                return {}
            
            # Extract properties - NEW STRUCTURE
            property_dict = {}
            
            # The actual structure is: material_data['properties'][Category][PropertyName]
            properties_section = material_data.get('properties', {})
            
            print(f"[VizTab] Properties section has categories: {list(properties_section.keys())}")
            
            # Iterate through categories (Thermal, Mechanical, etc.)
            for category_name, category_data in properties_section.items():
                if not isinstance(category_data, dict):
                    continue
                
                print(f"[VizTab]   Category '{category_name}' has {len(category_data)} properties")
                
                # Iterate through properties in this category
                for prop_name, prop_data in category_data.items():
                    # Skip non-dict values (like Phase.State = "solid")
                    if not isinstance(prop_data, dict):
                        continue
                    
                    # Get unit and entries
                    unit = prop_data.get('unit', '')
                    entries = prop_data.get('entries', [])
                    
                    if not entries:
                        continue
                    
                    # Normalize property name to lowercase with underscores
                    normalized_name = prop_name.lower().replace(' ', '_')
                    
                    if normalized_name not in property_dict:
                        property_dict[normalized_name] = []
                    
                    # Extract values from entries
                    for entry in entries:
                        value_str = entry.get('value')
                        if value_str and value_str.lower() != 'null':
                            try:
                                value_float = float(value_str)
                                property_dict[normalized_name].append({
                                    'value': value_float,
                                    'unit': unit,
                                    'ref': entry.get('ref', '')
                                })
                            except (ValueError, TypeError):
                                pass
            
            print(f"[VizTab] Extracted properties: {list(property_dict.keys())}")
            for prop_name, values in property_dict.items():
                print(f"[VizTab]   {prop_name}: {len(values)} values")
                        
            return property_dict
            
        except Exception as e:
            print(f"[VizTab] Error fetching data for {material_name}: {e}")
            import traceback
            traceback.print_exc()
            return {}
            
    def generate_plot(self):
        """Generate plot based on selections."""
        print("\n=== GENERATE PLOT CALLED ===")
        
        # Get selected materials
        self.selected_materials = [item.text() for item in self.material_list.selectedItems()]
        print(f"Selected materials: {self.selected_materials}")
        
        # Get selected properties
        self.selected_properties = [item.text() for item in self.property_list.selectedItems()]
        print(f"Selected properties: {self.selected_properties}")
        
        if not self.selected_materials:
            self.ax.clear()
            self.ax.text(0.5, 0.5, 'Please select at least one material',
                        ha='center', va='center', fontsize=12, color='red')
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            self.canvas.draw()
            print("ERROR: No materials selected")
            return
            
        if not self.selected_properties:
            self.ax.clear()
            self.ax.text(0.5, 0.5, 'Please select at least one property',
                        ha='center', va='center', fontsize=12, color='red')
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            self.canvas.draw()
            print("ERROR: No properties selected")
            return
        
        # Fetch data for all selected materials
        self.materials_data = {}
        for material in self.selected_materials:
            print(f"\nFetching data for: {material}")
            mat_data = self.fetch_material_data(material)
            print(f"  Properties found: {list(mat_data.keys())}")
            for prop in self.selected_properties:
                if prop in mat_data:
                    print(f"    {prop}: {len(mat_data[prop])} data points - Values: {[v['value'] for v in mat_data[prop][:3]]}")
                else:
                    print(f"    {prop}: NOT FOUND in material data")
            self.materials_data[material] = mat_data
        
        # Plot based on chart type
        chart_type = self.chart_type_combo.currentText()
        print(f"\nGenerating {chart_type} chart...")
        
        try:
            if chart_type == "Line":
                self.plot_line_chart()
            elif chart_type == "Bar":
                self.plot_bar_chart()
            elif chart_type == "Scatter":
                self.plot_scatter_chart()
            elif chart_type == "Area":
                self.plot_area_chart()
            elif chart_type == "Pie":
                self.plot_pie_chart()
            elif chart_type == "Histogram":
                self.plot_histogram_chart()
            print("Plot generated successfully!")
        except Exception as e:
            print(f"ERROR in plotting: {e}")
            import traceback
            traceback.print_exc()
            
            # Show error on plot
            self.ax.clear()
            self.ax.text(0.5, 0.5, f'Error generating plot:\n{str(e)}',
                        ha='center', va='center', fontsize=10, color='red', 
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            self.canvas.draw()
            
        # Update dashboard
        self.update_dashboard()
        print("=== PLOT GENERATION COMPLETE ===\n")
        
    def plot_line_chart(self):
        """Generate line chart."""
        self.ax.clear()
        
        # Color palette
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', 
                 '#1abc9c', '#e67e22', '#34495e']
        
        plot_count = 0
        
        for mat_idx, material in enumerate(self.selected_materials):
            mat_data = self.materials_data.get(material, {})
            color = colors[mat_idx % len(colors)]
            
            for prop in self.selected_properties:
                if prop in mat_data:
                    values = mat_data[prop]
                    
                    if values:
                        y_vals = [v['value'] for v in values]
                        x_vals = list(range(len(y_vals)))
                        
                        label = f"{material} - {prop.replace('_', ' ').title()}"
                        self.ax.plot(x_vals, y_vals, marker='o', label=label, 
                                   color=color, linewidth=2, markersize=6)
                        plot_count += 1
        
        if plot_count > 0:
            self.ax.set_xlabel('Data Point Index', fontsize=11)
            self.ax.set_ylabel('Property Value', fontsize=11)
            self.ax.set_title('Material Property Comparison', fontsize=13, fontweight='bold')
            self.ax.legend(loc='best', fontsize=9)
            self.ax.grid(True, alpha=0.3, linestyle='--')
        else:
            self.ax.text(0.5, 0.5, 'No data available for selected properties',
                        ha='center', va='center', fontsize=12, color='orange')
            self.ax.set_xticks([])
            self.ax.set_yticks([])
        
        self.canvas.draw()
        
    def plot_bar_chart(self):
        """Generate bar chart."""
        self.ax.clear()
        
        import numpy as np
        
        # Color palette
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
        
        # Prepare data: average values per property per material
        bar_data = {}  # {material: {property: avg_value}}
        
        for material in self.selected_materials:
            mat_data = self.materials_data.get(material, {})
            bar_data[material] = {}
            
            for prop in self.selected_properties:
                if prop in mat_data and mat_data[prop]:
                    values = [v['value'] for v in mat_data[prop]]
                    bar_data[material][prop] = np.mean(values)
                else:
                    bar_data[material][prop] = 0
        
        # Plot grouped bars
        x = np.arange(len(self.selected_properties))
        width = 0.8 / len(self.selected_materials) if self.selected_materials else 0.8
        
        for idx, material in enumerate(self.selected_materials):
            values = [bar_data[material].get(prop, 0) for prop in self.selected_properties]
            offset = (idx - len(self.selected_materials)/2 + 0.5) * width
            
            self.ax.bar(x + offset, values, width, label=material, 
                       color=colors[idx % len(colors)], alpha=0.8)
        
        self.ax.set_xlabel('Properties', fontsize=11)
        self.ax.set_ylabel('Average Value', fontsize=11)
        self.ax.set_title('Material Property Comparison', fontsize=13, fontweight='bold')
        self.ax.set_xticks(x)
        self.ax.set_xticklabels([p.replace('_', ' ').title() for p in self.selected_properties], 
                                rotation=45, ha='right')
        self.ax.legend(loc='best', fontsize=9)
        self.ax.grid(True, axis='y', alpha=0.3, linestyle='--')
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_scatter_chart(self):
        """Generate scatter plot."""
        self.ax.clear()
        
        # Color palette
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', 
                 '#1abc9c', '#e67e22', '#34495e']
        
        plot_count = 0
        
        for mat_idx, material in enumerate(self.selected_materials):
            mat_data = self.materials_data.get(material, {})
            color = colors[mat_idx % len(colors)]
            
            for prop_idx, prop in enumerate(self.selected_properties):
                if prop in mat_data and mat_data[prop]:
                    values = mat_data[prop]
                    y_vals = [v['value'] for v in values]
                    x_vals = list(range(len(y_vals)))
                    
                    label = f"{material} - {prop.replace('_', ' ').title()}"
                    self.ax.scatter(x_vals, y_vals, s=100, alpha=0.7, 
                                  c=color, edgecolors='white', linewidth=1.5,
                                  label=label, marker='o')
                    plot_count += 1
        
        if plot_count > 0:
            self.ax.set_xlabel('Data Point Index', fontsize=11)
            self.ax.set_ylabel('Property Value', fontsize=11)
            self.ax.set_title('Material Property Scatter Plot', fontsize=13, fontweight='bold')
            self.ax.legend(loc='best', fontsize=9)
            self.ax.grid(True, alpha=0.3, linestyle='--')
        else:
            self.ax.text(0.5, 0.5, 'No data available for scatter plot',
                        ha='center', va='center', fontsize=12, color='orange')
            self.ax.set_xticks([])
            self.ax.set_yticks([])
        
        self.canvas.draw()
    
    def plot_area_chart(self):
        """Generate area/filled chart."""
        self.ax.clear()
        
        import numpy as np
        
        # Color palette
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', 
                 '#1abc9c', '#e67e22', '#34495e']
        
        plot_count = 0
        
        for mat_idx, material in enumerate(self.selected_materials):
            mat_data = self.materials_data.get(material, {})
            color = colors[mat_idx % len(colors)]
            
            for prop in self.selected_properties:
                if prop in mat_data and mat_data[prop]:
                    values = mat_data[prop]
                    y_vals = [v['value'] for v in values]
                    x_vals = list(range(len(y_vals)))
                    
                    label = f"{material} - {prop.replace('_', ' ').title()}"
                    self.ax.fill_between(x_vals, y_vals, alpha=0.4, color=color, label=label)
                    self.ax.plot(x_vals, y_vals, color=color, linewidth=2, alpha=0.8)
                    plot_count += 1
        
        if plot_count > 0:
            self.ax.set_xlabel('Data Point Index', fontsize=11)
            self.ax.set_ylabel('Property Value', fontsize=11)
            self.ax.set_title('Material Property Area Chart', fontsize=13, fontweight='bold')
            self.ax.legend(loc='best', fontsize=9)
            self.ax.grid(True, alpha=0.3, linestyle='--')
        else:
            self.ax.text(0.5, 0.5, 'No data available for area chart',
                        ha='center', va='center', fontsize=12, color='orange')
            self.ax.set_xticks([])
            self.ax.set_yticks([])
        
        self.canvas.draw()
    
    def plot_pie_chart(self):
        """Generate pie chart for property comparison."""
        self.ax.clear()
        
        import numpy as np
        
        # For pie chart, show average property values for first selected material
        if not self.selected_materials:
            self.ax.text(0.5, 0.5, 'No material selected',
                        ha='center', va='center', fontsize=12, color='red')
            self.canvas.draw()
            return
        
        material = self.selected_materials[0]
        mat_data = self.materials_data.get(material, {})
        
        # Collect average values for each property
        labels = []
        values = []
        
        for prop in self.selected_properties:
            if prop in mat_data and mat_data[prop]:
                prop_values = [v['value'] for v in mat_data[prop]]
                avg_value = np.mean(prop_values)
                labels.append(prop.replace('_', ' ').title())
                values.append(abs(avg_value))  # Use absolute values for pie chart
        
        if values:
            # Color palette
            colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', 
                     '#1abc9c', '#e67e22', '#34495e']
            
            # Create pie chart
            wedges, texts, autotexts = self.ax.pie(
                values, 
                labels=labels, 
                colors=colors[:len(values)],
                autopct='%1.1f%%',
                startangle=90,
                textprops={'fontsize': 9}
            )
            
            # Make percentage text bold and white
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            self.ax.set_title(f'{material} - Property Distribution', 
                            fontsize=13, fontweight='bold', pad=20)
            
            # Equal aspect ratio ensures circular pie
            self.ax.axis('equal')
        else:
            self.ax.text(0.5, 0.5, f'No data for {material}',
                        ha='center', va='center', fontsize=12, color='orange')
        
        self.canvas.draw()
    
    def plot_histogram_chart(self):
        """Generate histogram for value distribution."""
        self.ax.clear()
        
        import numpy as np
        
        # Color palette
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
        
        plot_count = 0
        all_data = []
        
        for mat_idx, material in enumerate(self.selected_materials):
            mat_data = self.materials_data.get(material, {})
            
            for prop in self.selected_properties:
                if prop in mat_data and mat_data[prop]:
                    values = [v['value'] for v in mat_data[prop]]
                    all_data.extend(values)
                    
                    label = f"{material} - {prop.replace('_', ' ').title()}"
                    self.ax.hist(values, bins=10, alpha=0.6, 
                               color=colors[mat_idx % len(colors)],
                               label=label, edgecolor='black')
                    plot_count += 1
        
        if plot_count > 0:
            self.ax.set_xlabel('Property Value', fontsize=11)
            self.ax.set_ylabel('Frequency', fontsize=11)
            self.ax.set_title('Property Value Distribution', fontsize=13, fontweight='bold')
            self.ax.legend(loc='best', fontsize=9)
            self.ax.grid(True, axis='y', alpha=0.3, linestyle='--')
        else:
            self.ax.text(0.5, 0.5, 'No data available for histogram',
                        ha='center', va='center', fontsize=12, color='orange')
            self.ax.set_xticks([])
            self.ax.set_yticks([])
        
        self.canvas.draw()
        
    def update_dashboard(self):
        """Update dashboard statistics."""
        # Count selected materials and properties
        mat_count = len(self.selected_materials)
        prop_count = len(self.selected_properties)
        
        # Count total data points, missing values, and references
        total_points = 0
        missing_count = 0
        references_set = set()
        
        for material in self.selected_materials:
            mat_data = self.materials_data.get(material, {})
            for prop in self.selected_properties:
                if prop in mat_data and mat_data[prop]:
                    total_points += len(mat_data[prop])
                    # Collect unique reference IDs
                    for data_point in mat_data[prop]:
                        ref = data_point.get('ref', '')
                        if ref:
                            references_set.add(ref)
                else:
                    missing_count += 1
        
        # Update stat cards
        self.update_stat_card("Materials_Selected_value", str(mat_count))
        self.update_stat_card("Properties_Selected_value", str(prop_count))
        self.update_stat_card("Data_Points_value", str(total_points))
        self.update_stat_card("Missing_Values_value", str(missing_count))
        
        # Update detail text with references
        detail_text = f"Materials: {', '.join(self.selected_materials)}\n\n"
        detail_text += f"Properties: {', '.join([p.replace('_', ' ').title() for p in self.selected_properties])}\n\n"
        detail_text += f"Data View: {self.view_mode_combo.currentText()}\n\n"
        detail_text += f"Total data points: {total_points}\n"
        detail_text += f"Missing values: {missing_count}\n"
        detail_text += f"Unique references: {len(references_set)}\n"
        if references_set:
            detail_text += f"Ref IDs: {', '.join(sorted(references_set))}"
        
        self.detail_text.setText(detail_text)
        
    def update_stat_card(self, object_name, value):
        """Update a statistic card value."""
        for i in range(self.stats_layout.count()):
            widget = self.stats_layout.itemAt(i).widget()
            if widget:
                value_label = widget.findChild(QLabel, object_name)
                if value_label:
                    value_label.setText(value)
                    return
                    
    def export_plot(self):
        """Export current plot to file."""
        if not hasattr(self, 'figure') or self.figure is None:
            return
        
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Plot",
            "material_plot.png",
            "PNG Image (*.png);;PDF Document (*.pdf)"
        )
        
        if file_path:
            try:
                self.figure.savefig(file_path, dpi=300, bbox_inches='tight')
                print(f"Plot exported to: {file_path}")
            except Exception as e:
                print(f"Export failed: {e}")
