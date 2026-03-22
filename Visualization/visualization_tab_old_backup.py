"""
Visualization Tab - Offline Material Data Visualization

Creates interactive charts and dashboards for material property comparison.
Fully offline using matplotlib embedded in PyQt6.

ENHANCED VERSION:
- Improved material selection with search, checkboxes, select all/clear all
- Responsive design with scrollable panels
- Generalized experimental data support (YAML files)
- Better dark/light mode support
- Centered plots with improved layout
- Removed duplicate materials
"""

# CRITICAL: Set matplotlib backend BEFORE any other matplotlib imports
import matplotlib
matplotlib.use('QtAgg', force=True)  # Force QtAgg backend for PyQt6 compatibility

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
# DO NOT import pyplot - we use Figure directly for better control
import numpy as np
import yaml
import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QListWidget, QComboBox,
    QGroupBox, QSplitter, QFrame, QFileDialog,
    QAbstractItemView, QLineEdit, QCheckBox, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor

# Import analytics selector helper (Meeting-8 Task 1)
from gui.analytics_selector import AnalyticsSelector, AnalyticsType

# Import US-UP database reader for shock physics analysis
from analysis.us_up_db_reader import USUpDatabaseReader


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
        
        # Initialize US-UP database reader for shock physics
        print("[VizTab] Initializing US-UP database reader...")
        try:
            self.usup_reader = USUpDatabaseReader(db_manager)
            print(f"[VizTab] US-UP reader loaded: {len(self.usup_reader.materials_data)} materials with Hugoniot data")
        except Exception as e:
            print(f"[VizTab] Warning: US-UP reader initialization failed: {e}")
            self.usup_reader = None
        
        # Data storage
        self.materials_data = {}  # {material_name: property_data_dict}
        self.selected_materials = []
        self.selected_properties = []
        
        # Analytics selector (Meeting-8 Task 1)
        self.analytics_selector = None
        self.current_analytics_type = AnalyticsType.STANDARD_PROPERTIES
        
        # Data source tracking (GUI Enhancement - Sprint 1)
        self.data_source_selector = None
        self.current_data_source = DataSourceType.EXPERIMENTAL  # Default to experimental
        
        # Configuration panels (GUI Enhancement - Sprint 2)
        self.usup_config_panel = None
        self.display_prefs_panel = None
        self.current_usup_config = {}
        self.current_display_prefs = {}
        
        # Statistics and export (GUI Enhancement - Sprint 3)
        self.statistics_panel = None
        self.export_manager = ExportManager()
        self.export_manager.export_completed.connect(self._on_export_completed)
        self.export_manager.export_failed.connect(self._on_export_failed)
        
        # Dashboard widgets (GUI Enhancement - Sprint 4)
        self.advanced_statistics = AdvancedStatisticsCalculator()
        self.advanced_statistics.analysis_completed.connect(self._on_advanced_analysis_completed)
        self.advanced_statistics.export_requested.connect(self._on_stats_export_requested)
        
        self.batch_export_manager = BatchExportManager()
        self.batch_export_manager.export_started.connect(self._on_batch_export_started)
        self.batch_export_manager.export_completed.connect(self._on_batch_export_completed)
        self.batch_export_manager.export_progress.connect(self._on_batch_export_progress)
        
        self.data_comparison_tool = DataComparisonTool()
        self.data_comparison_tool.comparison_updated.connect(self._on_comparison_updated)
        self.data_comparison_tool.export_requested.connect(self._on_comparison_export_requested)
        
        # Debouncing timer for config changes (prevent rapid regeneration)
        from PyQt6.QtCore import QTimer
        self._config_update_timer = QTimer()
        self._config_update_timer.setSingleShot(True)
        self._config_update_timer.timeout.connect(self._apply_pending_config_update)
        self._pending_config_update = None
        
        # Color palette for US-UP plots (research-grade colors matching original widget)
        self.usup_colors = [
            '#1f77b4',  # Blue
            '#ff7f0e',  # Orange
            '#2ca02c',  # Green
            '#d62728',  # Red
            '#9467bd',  # Purple
            '#8c564b',  # Brown
            '#e377c2',  # Pink
            '#7f7f7f',  # Gray
            '#bcbd22',  # Yellow-green
            '#17becf'   # Cyan
        ]
        
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
        self.info_label = QLabel("💡 Linked with Material Browser\nSelect a material there to auto-populate here")
        self.info_label.setProperty("class", "info-label")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        
        # === GUI ENHANCEMENT - SPRINT 1: Data Source Selector ===
        self.data_source_selector = DataSourceSelector()
        self.data_source_selector.source_changed.connect(self.on_data_source_changed)
        layout.addWidget(self.data_source_selector)
        
        layout.addSpacing(10)
        # === END GUI ENHANCEMENT ===
        
        # === MEETING-8 TASK 1: Analytics Type Selector ===
        analytics_group = QGroupBox("Analytics Type")
        analytics_layout = QVBoxLayout(analytics_group)
        
        self.analytics_selector = AnalyticsSelector()
        self.analytics_selector.register_callback(self.on_analytics_type_changed)
        analytics_layout.addWidget(self.analytics_selector.get_widget())
        
        # Data source indicator
        self.data_source_label = QLabel("📊 Data Source: XML → Database → GUI")
        self.data_source_label.setProperty("class", "detail-text")
        self.data_source_label.setStyleSheet("color: green; font-size: 8pt;")
        self.data_source_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        analytics_layout.addWidget(self.data_source_label)
        
        layout.addWidget(analytics_group)
        # === END MEETING-8 ADDITION ===
        
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
            "Histogram",
            "US/UP (Hugoniot)"  # NEW: Shock Hugoniot relationship
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
        """Create right panel with statistics cards and configuration."""
        from PyQt6.QtWidgets import QTabWidget, QScrollArea
        
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
        
        # === GUI ENHANCEMENT - SPRINT 2: Configuration Tabs ===
        config_tabs = QTabWidget()
        
        # Tab 1: Details
        detail_group = QGroupBox("Details")
        detail_layout = QVBoxLayout(detail_group)
        
        self.detail_text = QLabel("No data loaded")
        self.detail_text.setProperty("class", "detail-text")
        self.detail_text.setWordWrap(True)
        self.detail_text.setAlignment(Qt.AlignmentFlag.AlignTop)
        detail_layout.addWidget(self.detail_text)
        
        config_tabs.addTab(detail_group, "📊 Info")
        
        # Tab 2: US-UP Configuration
        usup_scroll = QScrollArea()
        usup_scroll.setWidgetResizable(True)
        self.usup_config_panel = UsUpConfigPanel()
        self.usup_config_panel.config_changed.connect(self._on_usup_config_changed)
        usup_scroll.setWidget(self.usup_config_panel)
        config_tabs.addTab(usup_scroll, "⚙️ US-UP")
        
        # Tab 3: Display Preferences
        display_scroll = QScrollArea()
        display_scroll.setWidgetResizable(True)
        self.display_prefs_panel = DisplayPreferencesPanel()
        self.display_prefs_panel.preferences_changed.connect(self._on_display_prefs_changed)
        display_scroll.setWidget(self.display_prefs_panel)
        config_tabs.addTab(display_scroll, "🎨 Display")
        
        # Tab 4: Statistics (GUI Enhancement - Sprint 3)
        stats_scroll = QScrollArea()
        stats_scroll.setWidgetResizable(True)
        self.statistics_panel = StatisticsPanel()
        self.statistics_panel.export_requested.connect(self._on_export_requested)
        stats_scroll.setWidget(self.statistics_panel)
        config_tabs.addTab(stats_scroll, "📈 Stats")
        
        # Tab 5: Advanced Statistics (GUI Enhancement - Sprint 4)
        adv_stats_scroll = QScrollArea()
        adv_stats_scroll.setWidgetResizable(True)
        adv_stats_scroll.setWidget(self.advanced_statistics)
        config_tabs.addTab(adv_stats_scroll, "🔬 Advanced")
        
        # Tab 6: Batch Export (GUI Enhancement - Sprint 4)
        batch_export_scroll = QScrollArea()
        batch_export_scroll.setWidgetResizable(True)
        batch_export_scroll.setWidget(self.batch_export_manager)
        config_tabs.addTab(batch_export_scroll, "📦 Export")
        
        # Tab 7: Data Comparison (GUI Enhancement - Sprint 4)
        comparison_scroll = QScrollArea()
        comparison_scroll.setWidgetResizable(True)
        comparison_scroll.setWidget(self.data_comparison_tool)
        config_tabs.addTab(comparison_scroll, "⚖️ Compare")
        
        layout.addWidget(config_tabs)
        # === END GUI ENHANCEMENT ===
        
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
    
    def on_data_source_changed(self, source: DataSourceType):
        """
        Handle data source selection change (GUI Enhancement - Sprint 1).
        
        Args:
            source: New data source type (MODEL, EXPERIMENTAL, COMBINED)
        """
        print(f"[VizTab] Data source changed to: {source.name}")
        
        # Store current selection
        self.current_data_source = source
        
        # Reload materials with data availability info
        self.load_available_materials_enhanced(source)
        
        # Clear current plot
        if self.ax:
            self.ax.clear()
            self.ax.text(0.5, 0.5, 
                        f'📊 Data Source: {source.value.upper()}\n\nSelect materials and click "Generate Visualization"',
                        ha='center', va='center', fontsize=11,
                        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            self.canvas.draw()
    
    def _on_usup_config_changed(self, config: dict):
        """
        Handle US-UP configuration changes (GUI Enhancement - Sprint 2).
        Uses debouncing to prevent rapid regeneration during slider drag.
        
        Args:
            config: Configuration dictionary from UsUpConfigPanel
        """
        print(f"[VizTab] US-UP config changed: {list(config.keys())}")
        self.current_usup_config = config
        
        # Store pending update and restart timer (debounce)
        self._pending_config_update = ('usup', config)
        self._config_update_timer.stop()
        self._config_update_timer.start(300)  # 300ms delay
    
    def _apply_pending_config_update(self):
        """Apply pending configuration update after debounce delay."""
        if not self._pending_config_update:
            return
        
        update_type, config = self._pending_config_update
        self._pending_config_update = None
        
        if update_type == 'usup':
            # If we have an active US-UP plot, regenerate it with new config
            if self.ax and self.selected_materials:
                # Check if current chart type is US-UP or current analytics mode is US-UP
                chart_type = self.chart_type_combo.currentText()
                is_usup_mode = self.current_analytics_type == AnalyticsType.US_UP_ANALYSIS
                is_usup_chart = "US/UP" in chart_type or "Hugoniot" in chart_type
                
                if is_usup_mode or is_usup_chart:
                    print("[VizTab] Applying US-UP configuration changes...")
                    try:
                        self.plot_usup_hugoniot()
                        print("[VizTab] US-UP plot regenerated successfully")
                    except Exception as e:
                        print(f"[VizTab] Error regenerating plot: {e}")
                        import traceback
                        traceback.print_exc()
        
        elif update_type == 'display':
            # Apply display preferences
            if self.ax and self.figure:
                try:
                    self._apply_display_preferences(config)
                    self.canvas.draw()
                    print("[VizTab] Display preferences applied successfully")
                except Exception as e:
                    print(f"[VizTab] Error applying display preferences: {e}")
                    import traceback
                    traceback.print_exc()
    
    def _on_display_prefs_changed(self, preferences: dict):
        """
        Handle display preferences changes (GUI Enhancement - Sprint 2).
        Uses debouncing for smoother UI response.
        
        Args:
            preferences: Preferences dictionary from DisplayPreferencesPanel
        """
        print(f"[VizTab] Display preferences changed: {list(preferences.keys())}")
        self.current_display_prefs = preferences
        
        # Store pending update and restart timer (debounce)
        self._pending_config_update = ('display', preferences)
        self._config_update_timer.stop()
        self._config_update_timer.start(200)  # 200ms delay for display changes
    
    def _apply_display_preferences(self, prefs: dict):
        """
        Apply display preferences to current plot.
        
        Args:
            prefs: Preferences dictionary
        """
        if not self.ax:
            return
        
        # Apply legend settings
        legend = self.ax.get_legend()
        if prefs.get('show_legend', True) and legend:
            legend.set_visible(True)
            # Update legend position if needed
            pos = prefs.get('legend_position', 'upper left')
            legend.set_bbox_to_anchor(None)
            legend.set_loc(pos)
        elif legend:
            legend.set_visible(False)
        
        # Apply grid settings
        self.ax.grid(
            prefs.get('show_major_grid', True),
            which='major',
            alpha=0.3,
            linestyle='--',
            linewidth=0.8
        )
        
        if prefs.get('show_minor_grid', False):
            self.ax.grid(
                True,
                which='minor',
                alpha=0.1,
                linestyle=':',
                linewidth=0.5
            )
            self.ax.minorticks_on()
        
        # Apply label settings
        if not prefs.get('show_axis_labels', True):
            self.ax.set_xlabel('')
            self.ax.set_ylabel('')
        
        if not prefs.get('show_title', True):
            self.ax.set_title('')
        
        # Apply font size
        font_size = prefs.get('font_size', 10)
        self.ax.tick_params(labelsize=font_size)
        if self.ax.get_xlabel():
            self.ax.set_xlabel(self.ax.get_xlabel(), fontsize=font_size + 2)
        if self.ax.get_ylabel():
            self.ax.set_ylabel(self.ax.get_ylabel(), fontsize=font_size + 2)
        if self.ax.get_title():
            self.ax.set_title(self.ax.get_title(), fontsize=font_size + 4)
        
        # Note: Theme changes would require recreating the figure
        # For now, we'll note this as a future enhancement
        theme = prefs.get('theme', 'light')
        if theme != 'light':
            print(f"[VizTab] Theme '{theme}' requested - requires figure recreation (future enhancement)")
    
    def load_available_materials_enhanced(self, source: DataSourceType):
        """
        Load materials with data availability indicators (GUI Enhancement - Sprint 1).
        
        Args:
            source: Current data source type
        """
        try:
            cursor = self.db_manager.get_cursor()
            
            # Query materials with data availability
            cursor.execute("""
                SELECT 
                    m.material_id,
                    m.name,
                    m.xml_id,
                    EXISTS(
                        SELECT 1 FROM eos_models 
                        WHERE material_id = m.material_id AND row_number = 3
                    ) as has_model_data,
                    EXISTS(
                        SELECT 1 FROM experimental_datasets 
                        WHERE material_id = m.material_id
                    ) as has_experimental_data,
                    COALESCE((
                        SELECT COUNT(*) FROM experimental_points p
                        JOIN experimental_datasets d ON p.dataset_id = d.dataset_id
                        WHERE d.material_id = m.material_id
                    ), 0) as experimental_point_count
                FROM materials m
                ORDER BY m.name
            """)
            
            materials = cursor.fetchall()
            cursor.close()
            
            # Clear and repopulate list
            self.material_list.clear()
            
            available_count = 0
            unavailable_count = 0
            
            for mat_id, name, xml_id, has_model, has_exp, exp_count in materials:
                # Build display text with badges
                badges = []
                if has_model:
                    badges.append("[M]")
                if has_exp:
                    badges.append(f"[E:{exp_count}]")
                
                badge_text = " ".join(badges) if badges else "[No Data]"
                display_text = f"{name}  {badge_text}"
                
                # Check if material has data for current source
                has_data_for_source = False
                if source == DataSourceType.MODEL and has_model:
                    has_data_for_source = True
                elif source == DataSourceType.EXPERIMENTAL and has_exp:
                    has_data_for_source = True
                elif source == DataSourceType.COMBINED and (has_model or has_exp):
                    has_data_for_source = True
                
                # Add item
                item_widget = self.material_list.addItem(display_text)
                
                # Track counts
                if has_data_for_source:
                    available_count += 1
                else:
                    unavailable_count += 1
            
            print(f"[VizTab] Loaded {len(materials)} materials for source: {source.name}")
            print(f"[VizTab] Available: {available_count}, Unavailable: {unavailable_count}")
            
            # Update info label
            if source == DataSourceType.EXPERIMENTAL:
                self.data_source_label.setText(f"📊 Experimental: {available_count} materials with measured data")
            elif source == DataSourceType.MODEL:
                self.data_source_label.setText(f"📊 Model: {available_count} materials with theoretical curves")
            else:
                self.data_source_label.setText(f"📊 Combined: {available_count} materials with any data")
            
        except Exception as e:
            print(f"[VizTab] Error loading materials: {e}")
            import traceback
            traceback.print_exc()
            
    def select_material(self, material_name):
        """
        Programmatically select a material in the list.
        Called when material is selected in Material Browser.
        """
        print(f"[VizTab] Selecting material: {material_name}")
        
        # Find and select the material in the list
        for i in range(self.material_list.count()):
            item = self.material_list.item(i)
            item_text = item.text()
            
            # Extract material name (remove badges like [M], [E:123], etc.)
            # Material name is everything before the first double space or badge marker
            if '  [' in item_text:
                mat_name = item_text.split('  [')[0].strip()
            else:
                mat_name = item_text.strip()
            
            if mat_name == material_name:
                item.setSelected(True)
                self.material_list.scrollToItem(item)
                print(f"[VizTab] Material '{material_name}' selected in visualization tab")
                return
        
        print(f"[VizTab] Material '{material_name}' not found in list")
    
    def plot_usup_hugoniot(self):
        """
        Plot US-UP (shock velocity vs particle velocity) Hugoniot relationship.
        
        NOW WITH DATA SOURCE AWARENESS (GUI Enhancement - Sprint 1)!
        - MODEL: Only theoretical curves
        - EXPERIMENTAL: Only measured points
        - COMBINED: Both overlaid
        
        US = C₀ + s × UP
        
        Where:
            US = Shock velocity (km/s)
            UP = Particle velocity (km/s)  
            C₀ = Bulk sound speed (km/s)
            s = Hugoniot slope (dimensionless)
        """
        if not self.usup_reader:
            self._show_usup_error("US-UP Database Reader Not Available")
            return
        
        # Route to appropriate plotting method based on data source
        if self.current_data_source == DataSourceType.MODEL:
            self._plot_usup_models_only()
        elif self.current_data_source == DataSourceType.EXPERIMENTAL:
            self._plot_usup_experimental_only()
        elif self.current_data_source == DataSourceType.COMBINED:
            self._plot_usup_combined()
        else:
            self._show_usup_error(f"Unknown data source: {self.current_data_source}")
    
    def _plot_usup_models_only(self):
        """Plot only model curves (no experimental points)."""
        plot_data = self.usup_reader.get_plot_data(
            self.selected_materials,
            up_range=(0.0, 10.0),
            num_points=100
        )
        
        if not plot_data:
            self._show_usup_error("No model data available for selected materials")
            return
        
        self.ax.clear()
        
        for idx, (material, data) in enumerate(plot_data.items()):
            color = self.usup_colors[idx % len(self.usup_colors)]
            
            self.ax.plot(
                data['up'],
                data['us'],
                color=color,
                linewidth=2.5,
                label=f"{material} (Model)",
                alpha=0.8,
                zorder=2
            )
        
        self._finalize_usup_plot("US-Up Hugoniot: Model Data")
    
    def _plot_usup_experimental_only(self):
        """Plot only experimental points (no model curves)."""
        print(f"[US-UP] _plot_usup_experimental_only() called")
        print(f"[US-UP] Selected materials: {self.selected_materials}")
        
        self.ax.clear()
        
        experimental_data_found = False
        
        for idx, material in enumerate(self.selected_materials):
            print(f"[US-UP] Fetching experimental data for: {material}")
            exp_data = self.get_experimental_usup_data(material)
            print(f"[US-UP] Got {len(exp_data) if exp_data else 0} points for {material}")
            
            if exp_data and len(exp_data) > 0:
                experimental_data_found = True
                up_exp, us_exp = zip(*exp_data)
                
                color = self.usup_colors[idx % len(self.usup_colors)]
                
                print(f"[US-UP] Plotting {len(exp_data)} points: Up range [{min(up_exp):.2f}, {max(up_exp):.2f}], Us range [{min(us_exp):.2f}, {max(us_exp):.2f}]")
                
                self.ax.scatter(
                    up_exp, us_exp,
                    color=color,
                    s=80,
                    marker='o',
                    edgecolors='black',
                    linewidth=1.5,
                    label=f"{material} ({len(exp_data)} pts)",
                    alpha=0.9,
                    zorder=5
                )
                print(f"[US-UP] ✓ Successfully plotted {len(exp_data)} experimental points for {material}")
            else:
                print(f"[US-UP] ✗ No experimental data for {material}")
        
        if not experimental_data_found:
            self._show_usup_error("No experimental data available for selected materials")
            return
        
        self._finalize_usup_plot("US-Up Hugoniot: Experimental Data")
    
    def _plot_usup_combined(self):
        """Plot both models and experimental (combined view)."""
        # Get configuration
        config = self.current_usup_config if hasattr(self, 'current_usup_config') else {}
        
        # Get plot range from config
        up_min = config.get('up_min', 0.0)
        up_max = config.get('up_max', 10.0)
        
        plot_data = self.usup_reader.get_plot_data(
            self.selected_materials,
            up_range=(up_min, up_max),
            num_points=100
        )
        
        # Check for experimental data
        has_experimental_data = False
        for material in self.selected_materials:
            exp_data = self.get_experimental_usup_data(material)
            if exp_data and len(exp_data) > 0:
                has_experimental_data = True
                break
        
        # If neither model nor experimental exists, show error
        if not plot_data and not has_experimental_data:
            self._show_usup_error("No data available for selected materials")
            return
        
        # If no model but have experimental, switch to experimental-only
        if not plot_data:
            print("[US-UP] No model data found, showing experimental data only")
            plot_data = {}
        
        self.ax.clear()
        experimental_data_found = False
        
        # Get display options from config
        show_curves = config.get('show_model_curves', True)
        show_points = config.get('show_experimental_points', True)
        point_size = config.get('point_size', 80)
        line_width = self.current_display_prefs.get('line_width', 2) if hasattr(self, 'current_display_prefs') else 2.5
        
        # Get marker shape
        marker_map = {'circle': 'o', 'square': 's', 'triangle': '^', 'diamond': 'D', 'star': '*'}
        marker = marker_map.get(config.get('point_shape', 'circle'), 'o')
        
        # Plot model curves (if enabled)
        if show_curves:
            for idx, (material, data) in enumerate(plot_data.items()):
                color = self.usup_colors[idx % len(self.usup_colors)]
                
                self.ax.plot(
                    data['up'],
                    data['us'],
                    color=color,
                    linewidth=line_width,
                    label=f"{material} (Model)",
                    alpha=0.8,
                    zorder=2
                )
                
                # Add experimental data if available and enabled
                if show_points:
                    exp_data = self.get_experimental_usup_data(material)
                    if exp_data and len(exp_data) > 0:
                        experimental_data_found = True
                        up_exp, us_exp = zip(*exp_data)
                        
                        self.ax.scatter(
                            up_exp, us_exp,
                            color=color,
                            s=point_size,
                            marker=marker,
                            edgecolors='black',
                            linewidth=1.5,
                            label=f"{material} (Exp: {len(exp_data)} pts)",
                            alpha=0.9,
                            zorder=5
                        )
                        print(f"[US-UP] Plotted {len(exp_data)} experimental points for {material}")
        
        # Plot experimental-only materials (no model)
        if show_points:
            for material in self.selected_materials:
                if material not in plot_data:
                    exp_data = self.get_experimental_usup_data(material)
                    if exp_data and len(exp_data) > 0:
                        experimental_data_found = True
                        up_exp, us_exp = zip(*exp_data)
                        
                        color_idx = len(plot_data) + list(self.selected_materials).index(material)
                        color = self.usup_colors[color_idx % len(self.usup_colors)]
                        
                        self.ax.scatter(
                            up_exp, us_exp,
                            color=color,
                            s=point_size,
                            marker=marker,
                            edgecolors='black',
                            linewidth=1.5,
                            label=f"{material} (Exp: {len(exp_data)} pts)",
                            alpha=0.9,
                            zorder=5
                        )
                        print(f"[US-UP] Plotted {len(exp_data)} experimental-only points for {material}")
        
        # Set title based on what was plotted
        if plot_data and experimental_data_found:
            title = "US-Up Hugoniot: Model + Experimental Data"
        elif plot_data:
            title = "US-Up Hugoniot: Model Data"
        else:
            title = "US-Up Hugoniot: Experimental Data"
        
        self._finalize_usup_plot(title)
        
        # Add annotation if experimental data is shown
        if experimental_data_found:
            marker_symbol = {'o': '⚫', 's': '■', '^': '▲', 'D': '◆', '*': '★'}.get(marker, '⚫')
            self.ax.text(0.02, 0.98, f'{marker_symbol} = Experimental\n━ = Model',
                       transform=self.ax.transAxes,
                       fontsize=9, verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
    
    def _finalize_usup_plot(self, title: str):
        """Common plot finalization for US-UP plots (enhanced with Sprint 2 config)."""
        # Get configuration (use defaults if not set)
        config = self.current_usup_config if hasattr(self, 'current_usup_config') else {}
        prefs = self.current_display_prefs if hasattr(self, 'current_display_prefs') else {}
        
        # Axis labels (respect display preferences)
        if prefs.get('show_axis_labels', True):
            font_size = prefs.get('font_size', 10)
            self.ax.set_xlabel('Particle Velocity, Up (km/s)', 
                             fontsize=font_size + 2, fontweight='bold')
            self.ax.set_ylabel('Shock Velocity, US (km/s)', 
                             fontsize=font_size + 2, fontweight='bold')
        
        # Title (respect display preferences)
        if prefs.get('show_title', True):
            font_size = prefs.get('font_size', 10)
            self.ax.set_title(title, fontsize=font_size + 4, fontweight='bold')
        
        # Legend (respect display preferences)
        if prefs.get('show_legend', True):
            legend_pos = prefs.get('legend_position', 'upper left')
            self.ax.legend(loc=legend_pos, fontsize=prefs.get('font_size', 10), framealpha=0.9)
        
        # Grid (respect display preferences)
        if prefs.get('show_major_grid', True):
            self.ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
            
        if prefs.get('show_minor_grid', False):
            self.ax.grid(True, which='minor', alpha=0.1, linestyle=':', linewidth=0.5)
            self.ax.minorticks_on()
        
        # Set axis limits from configuration
        up_min = config.get('up_min', 0.0)
        up_max = config.get('up_max', 10.0)
        self.ax.set_xlim(up_min, up_max)
        
        # Auto-calculate US range if configured
        if config.get('us_auto', True):
            # Let matplotlib auto-calculate
            pass
        
        # Final layout and draw
        self.figure.tight_layout()
        self.canvas.draw()
    
    def _show_usup_error(self, message: str):
        """Show error message for US-UP plotting."""
        self.ax.clear()
        
        available = list(self.usup_reader.materials_data.keys()) if self.usup_reader else []
        
        error_msg = f'❌ {message}'
        error_msg += f'\n\nSelected: {", ".join(self.selected_materials)}'
        
        if available:
            error_msg += f'\n\n✅ Materials with model data ({len(available)} total):'
            error_msg += f'\n{", ".join(available[:10])}'
            if len(available) > 10:
                error_msg += f'\n... and {len(available) - 10} more'
        
        error_msg += '\n\n💡 Try selecting different materials'
        error_msg += f'\n� Current data source: {self.current_data_source.value.upper()}'
        
        self.ax.text(0.5, 0.5, error_msg,
                    ha='center', va='center', fontsize=9, color='orange',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                    family='monospace')
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.figure.tight_layout()
        self.canvas.draw()
    
    def get_experimental_usup_data(self, material_name: str):
        """
        Retrieve experimental US-UP data for a material from database.
        
        Args:
            material_name: Name of the material
            
        Returns:
            List of (Up, Us) tuples in km/s, or empty list if no data
        """
        try:
            # Query experimental data from database - USE PROPER DB MANAGER API
            cursor = self.db_manager.get_cursor()
            
            cursor.execute("""
                SELECT p.up_value, p.us_value
                FROM experimental_datasets d
                JOIN experimental_points p ON d.dataset_id = p.dataset_id
                JOIN materials m ON d.material_id = m.material_id
                WHERE m.name = %s
                  AND d.experiment_type = 'USUP'
                ORDER BY p.point_order
            """, (material_name,))
            
            results = cursor.fetchall()
            cursor.close()
            
            if results:
                print(f"[Experimental] Found {len(results)} data points for {material_name}")
                return results
            else:
                return []
                
        except Exception as e:
            print(f"[Experimental] Error fetching data for {material_name}: {e}")
            return []
    
    def get_usup_parameters(self, material_name):
        """
        Extract US/UP Hugoniot parameters from database.
        
        Looks for:
            - Density (ρ₀) from properties or models
            - SoundSpeed (C₀) from ElasticModel → ThermoMechanical → SoundSpeed
            - HugoniotSlope (s) from ElasticModel → ThermoMechanical → HugoniotSlope
        
        Returns:
            dict with keys: density, sound_speed, hugoniot_slope
            or None if material not found
        """
        try:
            # Fetch material data (same as fetch_material_data but with models)
            material_data = self.querier.get_material_by_name(material_name, apply_overrides=False)
            
            if not material_data:
                print(f"[US/UP] Material '{material_name}' not found in database")
                return None
            
            params = {
                'density': None,
                'sound_speed': None,
                'hugoniot_slope': None
            }
            
            # Try to get density from properties (Mechanical → Density)
            properties = material_data.get('properties', {})
            
            # Check Mechanical category for density
            mechanical = properties.get('Mechanical', {})
            if 'Density' in mechanical:
                density_data = mechanical['Density']
                entries = density_data.get('entries', [])
                if entries and entries[0].get('value'):
                    try:
                        params['density'] = float(entries[0]['value'])
                    except ValueError:
                        pass
            
            # Try to get SoundSpeed and HugoniotSlope from ElasticModel
            models = material_data.get('models', {})
            elastic_model = models.get('ElasticModel', {})
            
            if elastic_model:
                # Try ThermoMechanical first (correct location)
                thermo_mech = elastic_model.get('ThermoMechanical', {})
                
                # Get density from model if not found in properties
                if params['density'] is None:
                    # Try ThermoMechanical
                    if 'Density' in thermo_mech:
                        density_entries = thermo_mech['Density']
                        if isinstance(density_entries, list) and density_entries:
                            try:
                                params['density'] = float(density_entries[0]['value'])
                            except (ValueError, KeyError, IndexError):
                                pass
                    # Try direct ElasticModel level (parser bug workaround)
                    if params['density'] is None and 'Density' in elastic_model:
                        density_data = elastic_model['Density']
                        if isinstance(density_data, dict) and 'entries' in density_data:
                            entries = density_data.get('entries', [])
                            if entries:
                                try:
                                    params['density'] = float(entries[0]['value'])
                                except (ValueError, KeyError, IndexError):
                                    pass
                
                # Get SoundSpeed (C₀)  - Try both locations
                sound_speed_entries = None
                if 'SoundSpeed' in thermo_mech:
                    sound_speed_entries = thermo_mech['SoundSpeed']
                elif 'SoundSpeed' in elastic_model:  # Parser bug workaround
                    sound_speed_data = elastic_model['SoundSpeed']
                    if isinstance(sound_speed_data, dict) and 'entries' in sound_speed_data:
                        sound_speed_entries = sound_speed_data.get('entries', [])
                
                if isinstance(sound_speed_entries, list) and sound_speed_entries:
                    try:
                        params['sound_speed'] = float(sound_speed_entries[0]['value'])
                    except (ValueError, KeyError, IndexError):
                        pass
                
                # Get HugoniotSlope (s) - Try both locations
                slope_entries = None
                if 'HugoniotSlope' in thermo_mech:
                    slope_entries = thermo_mech['HugoniotSlope']
                elif 'HugoniotSlope' in elastic_model:  # Parser bug workaround
                    slope_data = elastic_model['HugoniotSlope']
                    if isinstance(slope_data, dict) and 'entries' in slope_data:
                        slope_entries = slope_data.get('entries', [])
                
                if isinstance(slope_entries, list) and slope_entries:
                    try:
                        params['hugoniot_slope'] = float(slope_entries[0]['value'])
                    except (ValueError, KeyError, IndexError):
                        pass
            
            print(f"[US/UP] {material_name}: ρ₀={params['density']}, C₀={params['sound_speed']}, s={params['hugoniot_slope']}")
            
            # Return params if we have at least C0 and s
            if params['sound_speed'] is not None and params['hugoniot_slope'] is not None:
                return params
            else:
                return None
                
        except Exception as e:
            print(f"[US/UP] Error fetching parameters for {material_name}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
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
    
    # === MEETING-8 TASK 1: Analytics Type Callback ===
    def on_analytics_type_changed(self, analytics_type: AnalyticsType):
        """
        Handle analytics type change.
        
        Args:
            analytics_type: Selected AnalyticsType enum value
        """
        print(f"[VizTab] Analytics type changed to: {analytics_type.value}")
        self.current_analytics_type = analytics_type
        
        # Clear current plot when switching modes
        if self.ax:
            self.ax.clear()
            self.ax.text(0.5, 0.5, f'Analytics mode changed to: {analytics_type.value}\n\nSelect materials and click "Generate Plot"',
                        ha='center', va='center', fontsize=11,
                        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            self.canvas.draw()
        
        # Update UI hints and controls based on selected type
        if analytics_type == AnalyticsType.STANDARD_PROPERTIES:
            self.data_source_label.setText("📊 Data Source: XML → Database → GUI")
            self.data_source_label.setStyleSheet("color: green; font-size: 8pt;")
            
            # ENABLE property selection for standard analysis
            self.property_list.setEnabled(True)
            self.chart_type_combo.setEnabled(True)
            self.generate_btn.setEnabled(True)
            self.export_btn.setEnabled(True)
            
            # Update info label
            if hasattr(self, 'info_label'):
                self.info_label.setText("💡 Linked with Material Browser\nSelect materials and properties to visualize")
        
        elif analytics_type == AnalyticsType.US_UP_ANALYSIS:
            self.data_source_label.setText("⚡ US-UP: Hugoniot shock data from database (Properties not needed)")
            self.data_source_label.setStyleSheet("color: blue; font-size: 8pt;")
            
            # Disable property selection for US-UP (only materials needed)
            self.property_list.setEnabled(False)
            self.property_list.clearSelection()
            
            # KEEP chart type and buttons ENABLED for US-UP
            self.chart_type_combo.setEnabled(True)
            self.generate_btn.setEnabled(True)
            self.export_btn.setEnabled(True)
            
            # Update info label
            if hasattr(self, 'info_label'):
                self.info_label.setText("⚡ US-UP Analysis Mode\nSelect materials to plot Hugoniot curves\n(Property selection disabled)")
        
        else:
            # Future features
            self.data_source_label.setText("🔮 Future feature - coming soon")
            self.data_source_label.setStyleSheet("color: gray; font-size: 8pt; font-style: italic;")
            
            # Disable controls for future features
            self.property_list.setEnabled(False)
            self.chart_type_combo.setEnabled(False)
    # === END MEETING-8 ADDITION ===
            
    def generate_plot(self):
        """Generate plot based on selections and analytics type."""
        print("\n=== GENERATE PLOT CALLED ===")
        
        # Get selected materials (handle badge extraction)
        self.selected_materials = []
        for item in self.material_list.selectedItems():
            item_text = item.text()
            # Extract material name (remove badges)
            if '  [' in item_text:
                mat_name = item_text.split('  [')[0].strip()
            else:
                mat_name = item_text.strip()
            self.selected_materials.append(mat_name)
        
        print(f"Selected materials: {self.selected_materials}")
        
        # Get selected properties
        self.selected_properties = [item.text() for item in self.property_list.selectedItems()]
        print(f"Selected properties: {self.selected_properties}")
        
        # Validate materials selection
        if not self.selected_materials:
            self._show_error_message('Please select at least one material')
            return
        
        # Check analytics type first
        if self.current_analytics_type == AnalyticsType.US_UP_ANALYSIS:
            print("Analytics Mode: US-UP Analysis")
            # For US-UP, we only need materials selected (properties not required)
            try:
                self.plot_usup_hugoniot()
                self.update_dashboard()
                print("=== US-UP PLOT GENERATION COMPLETE ===\n")
            except Exception as e:
                print(f"ERROR in US-UP plotting: {e}")
                import traceback
                traceback.print_exc()
                self._show_error_message(f'Error generating US-UP plot:\n{str(e)}')
            return
        
        # Standard property analysis - need both materials and properties
        if not self.selected_properties:
            self._show_error_message('Please select at least one property')
            return
        
        # Fetch data for all selected materials
        self.materials_data = {}
        for material in self.selected_materials:
            print(f"\nFetching data for: {material}")
            try:
                mat_data = self.fetch_material_data(material)
                print(f"  Properties found: {list(mat_data.keys())}")
                for prop in self.selected_properties:
                    if prop in mat_data:
                        print(f"    {prop}: {len(mat_data[prop])} data points")
                    else:
                        print(f"    {prop}: NOT FOUND in material data")
                self.materials_data[material] = mat_data
            except Exception as e:
                print(f"  ERROR fetching data for {material}: {e}")
                self.materials_data[material] = {}
        
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
            elif chart_type == "US/UP (Hugoniot)":
                self.plot_usup_hugoniot()
            print("Plot generated successfully!")
        except Exception as e:
            print(f"ERROR in plotting: {e}")
            import traceback
            traceback.print_exc()
            self._show_error_message(f'Error generating plot:\n{str(e)}')
            
        # Update dashboard
        try:
            self.update_dashboard()
        except Exception as e:
            print(f"ERROR updating dashboard: {e}")
            
        print("=== PLOT GENERATION COMPLETE ===\n")
    
    def _show_error_message(self, message: str):
        """Display error message on plot area."""
        if not self.ax:
            return
            
        self.ax.clear()
        self.ax.text(0.5, 0.5, f'❌ {message}',
                    ha='center', va='center', fontsize=12, color='red',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                    wrap=True)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.canvas.draw()
        
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
        
        # ✅ FIX: Handle US-UP Analysis mode separately
        if self.current_analytics_type == AnalyticsType.US_UP_ANALYSIS:
            # For US-UP mode, count both model and experimental data points
            for material in self.selected_materials:
                # Count model-generated points if available
                if self.usup_reader and material in self.usup_reader.materials_data:
                    # Model data generates 100 points by default
                    total_points += 100
                
                # Count experimental data points
                exp_data = self.get_experimental_usup_data(material)
                if exp_data:
                    total_points += len(exp_data)
                    print(f"[Dashboard] {material}: {len(exp_data)} experimental points")
        else:
            # Standard properties mode (original logic)
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
        
        # Update statistics panel (GUI Enhancement - Sprint 3)
        self._update_statistics_panel()
        
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
    
    # === GUI ENHANCEMENT - SPRINT 3: Export and Statistics Handlers ===
    
    def _on_export_requested(self, export_type: str):
        """
        Handle export requests from statistics panel.
        
        Args:
            export_type: Type of export ('csv', 'png', 'pdf', 'clipboard')
        """
        print(f"[VizTab] Export requested: {export_type}")
        
        if export_type == 'csv':
            self._export_csv_data()
        elif export_type == 'png':
            self._export_plot_png()
        elif export_type == 'pdf':
            self._export_plot_pdf()
        elif export_type == 'clipboard':
            self._copy_to_clipboard()
    
    def _export_csv_data(self):
        """Export current visualization data as CSV."""
        if not self.selected_materials:
            return
        
        # Prepare data for export
        export_data = {
            'materials': self.selected_materials,
            'data_points': {},
            'metadata': {
                'analytics_type': self.current_analytics_type.value,
                'data_source': self.current_data_source.value,
                'chart_type': self.chart_type_combo.currentText()
            }
        }
        
        # Collect data points based on analytics type
        if self.current_analytics_type == AnalyticsType.US_UP_ANALYSIS:
            # US-UP data
            for material in self.selected_materials:
                points = []
                if self.usup_reader and material in self.usup_reader.materials_data:
                    mat_data = self.usup_reader.materials_data[material]
                    up_data = mat_data.get('up', [])
                    us_data = mat_data.get('us', [])
                    
                    for i, (up, us) in enumerate(zip(up_data, us_data)):
                        source = mat_data.get('refs', ['Unknown'])[i] if i < len(mat_data.get('refs', [])) else 'Unknown'
                        points.append((up, us, source))
                
                export_data['data_points'][material] = points
        else:
            # Standard property data
            for material in self.selected_materials:
                mat_data = self.materials_data.get(material, {})
                points = []
                
                for prop in self.selected_properties:
                    if prop in mat_data:
                        for value in mat_data[prop]:
                            points.append((prop, value['value'], value.get('ref_id', 'Unknown')))
                
                export_data['data_points'][material] = points
        
        # Use export manager
        self.export_manager.export_csv(export_data, self)
    
    def _export_plot_png(self):
        """Export current plot as PNG."""
        if self.figure:
            self.export_manager.export_plot_image(self.figure, 'png', self)
    
    def _export_plot_pdf(self):
        """Export current plot as PDF."""
        if self.figure:
            self.export_manager.export_plot_image(self.figure, 'pdf', self)
    
    def _copy_to_clipboard(self):
        """Copy plot or data to clipboard."""
        if self.figure:
            self.export_manager.copy_to_clipboard(figure=self.figure, parent_widget=self)
    
    def _on_export_completed(self, filename: str, format: str):
        """Handle successful export."""
        print(f"[VizTab] Export completed: {filename} ({format})")
    
    def _on_export_failed(self, error: str, format: str):
        """Handle failed export."""
        print(f"[VizTab] Export failed ({format}): {error}")
    
    def _update_statistics_panel(self):
        """Update statistics panel with current visualization data."""
        if not self.statistics_panel:
            return
        
        # Clear if no data
        if not self.selected_materials:
            self.statistics_panel.clear_statistics()
            self.statistics_panel.enable_export(False)
            return
        
        # Prepare statistics data
        stats_data = {
            'materials': self.selected_materials,
            'data_points': {},
            'data_type': self.current_analytics_type.value,
            'ranges': {},
            'references': []
        }
        
        # Collect data based on analytics type
        if self.current_analytics_type == AnalyticsType.US_UP_ANALYSIS:
            # US-UP statistics
            all_up = []
            all_us = []
            refs_set = set()
            
            for material in self.selected_materials:
                points = []
                if self.usup_reader and material in self.usup_reader.materials_data:
                    mat_data = self.usup_reader.materials_data[material]
                    up_data = mat_data.get('up', [])
                    us_data = mat_data.get('us', [])
                    refs_data = mat_data.get('refs', [])
                    
                    points = list(zip(up_data, us_data))
                    all_up.extend(up_data)
                    all_us.extend(us_data)
                    refs_set.update(refs_data)
                
                stats_data['data_points'][material] = points
            
            if all_up and all_us:
                stats_data['ranges'] = {
                    'Up (km/s)': {'min': min(all_up), 'max': max(all_up)},
                    'Us (km/s)': {'min': min(all_us), 'max': max(all_us)}
                }
            
            stats_data['references'] = [
                {'source': ref, 'points': 0} for ref in refs_set
            ]
        else:
            # Standard property statistics
            for material in self.selected_materials:
                mat_data = self.materials_data.get(material, {})
                points = []
                
                for prop in self.selected_properties:
                    if prop in mat_data:
                        points.extend([(prop, v['value']) for v in mat_data[prop]])
                
                stats_data['data_points'][material] = points
        
        # Update statistics panel
        self.statistics_panel.update_statistics(stats_data)
        self.statistics_panel.enable_export(True)
        
        # Also update Sprint 4 widgets with the same data
        self._update_sprint4_widgets()
    
    def _update_sprint4_widgets(self):
        """Update Sprint 4 dashboard widgets with current visualization data."""
        if not self.selected_materials:
            return
        
        # Update Advanced Statistics Calculator
        if self.advanced_statistics:
            # Prepare data for advanced statistics
            adv_stats_data = {}
            
            if self.current_analytics_type == AnalyticsType.US_UP_ANALYSIS:
                # US-UP data
                for material in self.selected_materials:
                    if self.usup_reader and material in self.usup_reader.materials_data:
                        mat_data = self.usup_reader.materials_data[material]
                        adv_stats_data[material] = {
                            'Up (km/s)': mat_data.get('up', []),
                            'Us (km/s)': mat_data.get('us', [])
                        }
            else:
                # Standard properties
                for material in self.selected_materials:
                    mat_data = self.materials_data.get(material, {})
                    material_props = {}
                    
                    for prop in self.selected_properties:
                        if prop in mat_data:
                            values = [v['value'] for v in mat_data[prop]]
                            material_props[prop] = values
                    
                    if material_props:
                        adv_stats_data[material] = material_props
            
            self.advanced_statistics.set_data(adv_stats_data)
        
        # Update Batch Export Manager
        if self.batch_export_manager:
            self.batch_export_manager.set_materials(self.selected_materials)
            
            # Prepare export data
            export_data = {}
            for material in self.selected_materials:
                if self.current_analytics_type == AnalyticsType.US_UP_ANALYSIS:
                    if self.usup_reader and material in self.usup_reader.materials_data:
                        mat_data = self.usup_reader.materials_data[material]
                        export_data[material] = {
                            'type': 'us_up',
                            'data': mat_data
                        }
                else:
                    mat_data = self.materials_data.get(material, {})
                    export_data[material] = {
                        'type': 'properties',
                        'data': mat_data
                    }
            
            self.batch_export_manager.set_export_data(export_data)
        
        # Update Data Comparison Tool
        if self.data_comparison_tool:
            self.data_comparison_tool.set_materials(self.selected_materials)
            
            # Set data for each material
            for material in self.selected_materials:
                comparison_data = {}
                
                if self.current_analytics_type == AnalyticsType.US_UP_ANALYSIS:
                    if self.usup_reader and material in self.usup_reader.materials_data:
                        mat_data = self.usup_reader.materials_data[material]
                        comparison_data = {
                            'Up (km/s)': mat_data.get('up', []),
                            'Us (km/s)': mat_data.get('us', [])
                        }
                else:
                    mat_data = self.materials_data.get(material, {})
                    for prop in self.selected_properties:
                        if prop in mat_data:
                            comparison_data[prop] = [v['value'] for v in mat_data[prop]]
                
                self.data_comparison_tool.set_material_data(material, comparison_data)
    
    # === END GUI ENHANCEMENT ===

    
    def _on_advanced_analysis_completed(self, analysis_type: str, results: dict):
        """Handle advanced statistics analysis completion."""
        print(f"[VizTab] Advanced analysis completed: {analysis_type}")
        print(f"[VizTab] Results keys: {list(results.keys())}")
    
    def _on_stats_export_requested(self, export_type: str):
        """Handle export request from advanced statistics calculator."""
        print(f"[VizTab] Statistics export requested: {export_type}")
        if self.figure:
            self.export_manager.export_figure(
                figure=self.figure,
                format=export_type,
                parent_widget=self
            )
    
    def _on_batch_export_started(self, total_tasks: int):
        """Handle batch export start."""
        print(f"[VizTab] Batch export started: {total_tasks} tasks")
    
    def _on_batch_export_completed(self, successful: int, failed: int):
        """Handle batch export completion."""
        print(f"[VizTab] Batch export completed: {successful} successful, {failed} failed")
    
    def _on_batch_export_progress(self, current: int, total: int, message: str):
        """Handle batch export progress update."""
        if current % 5 == 0:  # Log every 5th task to avoid spam
            print(f"[VizTab] Batch export progress: {current}/{total} - {message}")
    
    def _on_comparison_updated(self, material1: str, material2: str):
        """Handle data comparison update."""
        print(f"[VizTab] Comparison updated: {material1} vs {material2}")
    
    def _on_comparison_export_requested(self, export_type: str):
        """Handle export request from comparison tool."""
        print(f"[VizTab] Comparison export requested: {export_type}")
        if self.figure:
            self.export_manager.export_figure(
                figure=self.figure,
                format=export_type,
                parent_widget=self
            )
    
    # === END GUI ENHANCEMENT ===
