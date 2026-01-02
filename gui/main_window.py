"""
Main Application Window

Professional desktop GUI for Materials Database with MVC architecture.
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTabWidget, QStatusBar, QMenuBar,
    QMenu, QToolBar, QMessageBox, QLabel, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon

# Import existing database modules (Model)
sys.path.append(str(Path(__file__).parent.parent.parent))
from db.database import DatabaseManager
from db.query import MaterialQuerier, ReferenceQuerier

# Import GUI components (Views)
from gui.views.material_browser import MaterialBrowser
from gui.views.property_viewer import PropertyViewer
from gui.views.override_panel import OverridePanel
from gui.views.visualization_tab import VisualizationTab


class MainWindow(QMainWindow):
    """
    Main application window using MVC architecture.
    
    Architecture:
    - Model: Existing db/query.py, override_manager.py (unchanged)
    - View: MaterialBrowser, PropertyViewer, OverridePanel widgets
    - Controller: Event handlers in this class
    """
    
    def __init__(self):
        super().__init__()
        
        print("DEBUG: MainWindow __init__ starting...")
        
        # Initialize database connection (Model)
        try:
            print("DEBUG: Connecting to database...")
            self.db = DatabaseManager()
            print("DEBUG: Database connected, creating queriers...")
            self.querier = MaterialQuerier(self.db)
            self.ref_querier = ReferenceQuerier(self.db)
            self.current_material = None
            self.is_dark_mode = True  # Default to dark mode
            print("DEBUG: Database setup complete")
        except Exception as e:
            print(f"DEBUG ERROR: Database connection failed - {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Database Error",
                f"Failed to connect to database:\n{str(e)}\n\nPlease check config.py"
            )
            sys.exit(1)
        
        # Setup UI
        print("DEBUG: Initializing UI...")
        try:
            self.init_ui()
            print("DEBUG: init_ui complete!")
        except Exception as e:
            print(f"DEBUG ERROR in init_ui: {e}")
            import traceback
            traceback.print_exc()
            raise
        
        print("DEBUG: Loading stylesheet...")
        self.load_stylesheet()
        
        # Load initial data
        print("DEBUG: Loading materials...")
        self.load_materials()
        print("DEBUG: MainWindow initialization complete!")
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Materials Database Explorer")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create tool bar
        self.create_tool_bar()
        
        # Create TAB WIDGET for main views
        self.main_tabs = QTabWidget()
        self.main_tabs.setDocumentMode(True)
        
        # TAB 1: Material Browser + Property Viewer (existing functionality)
        browser_widget = self.create_browser_tab()
        self.main_tabs.addTab(browser_widget, "Material Browser")
        
        # TAB 2: NEW Visualization Tab
        self.visualization_tab = VisualizationTab(self.db, self.querier)
        self.main_tabs.addTab(self.visualization_tab, "Visualization")
        
        main_layout.addWidget(self.main_tabs)
        
        # Create status bar
        self.create_status_bar()
    
    def create_browser_tab(self):
        """Create the original material browser tab widget."""
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)
        
        # Create main content area with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left Panel: Material Browser (View)
        self.material_browser = MaterialBrowser()
        self.material_browser.material_selected.connect(self.on_material_selected)
        splitter.addWidget(self.material_browser)
        
        # Center/Right Panel: Property Viewer + Override Panel
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Property Viewer (View)
        self.property_viewer = PropertyViewer()
        right_layout.addWidget(self.property_viewer)
        
        # Connect to tab change signal to hide/show override panel
        self.property_viewer.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Connect to export signal
        self.property_viewer.export_requested.connect(self.on_export_tab)
        
        # Override Panel (View)
        self.override_panel = OverridePanel()
        self.override_panel.override_requested.connect(self.on_override_requested)
        self.override_panel.clear_requested.connect(self.on_clear_override_requested)
        right_layout.addWidget(self.override_panel)
        
        splitter.addWidget(right_widget)
        
        # Set splitter proportions (30% browser, 70% content)
        splitter.setSizes([400, 1000])
        
        # Make splitter handle more visible and easier to drag
        splitter.setHandleWidth(8)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #555;
                margin: 0px 2px;
            }
            QSplitter::handle:hover {
                background-color: #2196F3;
            }
            QSplitter::handle:pressed {
                background-color: #1976D2;
            }
        """)
        
        tab_layout.addWidget(splitter)
        
        return tab_widget
    
    def create_menu_bar(self):
        """Create application menu bar."""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("&File")
        
        export_action = QAction("&Export Material...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.setStatusTip("Export selected material to XML")
        export_action.triggered.connect(self.on_export_material)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View Menu
        view_menu = menubar.addMenu("&View")
        
        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.setStatusTip("Refresh material list")
        refresh_action.triggered.connect(self.load_materials)
        view_menu.addAction(refresh_action)
        
        # Tools Menu
        tools_menu = menubar.addMenu("&Tools")
        
        query_action = QAction("&Query Material...", self)
        query_action.setShortcut("Ctrl+F")
        query_action.setStatusTip("Query material details")
        query_action.triggered.connect(self.on_query_material)
        tools_menu.addAction(query_action)
        
        tools_menu.addSeparator()
        
        # References submenu
        browse_refs_action = QAction("Browse &References...", self)
        browse_refs_action.setShortcut("Ctrl+R")
        browse_refs_action.setStatusTip("Browse all references in database")
        browse_refs_action.triggered.connect(self.on_browse_references)
        tools_menu.addAction(browse_refs_action)
        
        validate_refs_action = QAction("&Validate References...", self)
        validate_refs_action.setStatusTip("Check reference integrity")
        validate_refs_action.triggered.connect(self.on_validate_references)
        tools_menu.addAction(validate_refs_action)
        
        # Data Menu (for adding new data)
        data_menu = menubar.addMenu("&Data")
        
        add_material_action = QAction("Add &Material...", self)
        add_material_action.setShortcut("Ctrl+M")
        add_material_action.setStatusTip("Add a new material to the database")
        add_material_action.triggered.connect(self.on_add_material)
        data_menu.addAction(add_material_action)
        
        # Help Menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.setStatusTip("About Materials Database")
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)
    
    def create_tool_bar(self):
        """Create application toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Refresh button
        refresh_action = QAction("Refresh", self)
        refresh_action.setStatusTip("Refresh material list")
        refresh_action.triggered.connect(self.load_materials)
        toolbar.addAction(refresh_action)
        
        toolbar.addSeparator()
        
        # Override management
        list_overrides_action = QAction("List Overrides", self)
        list_overrides_action.setStatusTip("List all overrides for current material")
        list_overrides_action.triggered.connect(self.on_list_overrides)
        toolbar.addAction(list_overrides_action)
        
        toolbar.addSeparator()
        
        # References
        browse_refs_action = QAction("References", self)
        browse_refs_action.setStatusTip("Browse all references")
        browse_refs_action.triggered.connect(self.on_browse_references)
        toolbar.addAction(browse_refs_action)
        
        toolbar.addSeparator()
        
        # ===== DATA ADDITION BUTTONS (NEW) =====
        add_material_action = QAction("➕ Add Material", self)
        add_material_action.setStatusTip("Add a new material to the database")
        add_material_action.triggered.connect(self.on_add_material)
        toolbar.addAction(add_material_action)
        
        # Add spacer to push theme toggle to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        toolbar.addWidget(spacer)
        
        # Theme toggle button at the top right
        self.theme_toggle_btn = QPushButton("☀️ Light Mode")
        self.theme_toggle_btn.setFixedSize(120, 32)
        self.theme_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
        """)
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)
        toolbar.addWidget(self.theme_toggle_btn)
    
    def create_status_bar(self):
        """Create application status bar."""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Connection status
        self.db_status_label = QLabel("● Connected to Materials_DB")
        self.db_status_label.setStyleSheet("color: #51cf66;")
        self.statusBar.addPermanentWidget(self.db_status_label)
        
        self.statusBar.showMessage("Ready", 3000)
    
    def load_stylesheet(self):
        """Load application stylesheet."""
        try:
            if self.is_dark_mode:
                style_path = Path(__file__).parent / "resources" / "styles.qss"
            else:
                style_path = Path(__file__).parent / "resources" / "styles_light.qss"
            
            with open(style_path, 'r') as f:
                self.setStyleSheet(f.read())
            print(f"DEBUG: Loaded stylesheet: {style_path.name}")
        except Exception as e:
            print(f"Warning: Could not load stylesheet: {e}")
    
    def toggle_theme(self):
        """Toggle between dark and light mode."""
        self.is_dark_mode = not self.is_dark_mode
        
        # Update button text and icon
        if self.is_dark_mode:
            self.theme_toggle_btn.setText("☀️ Light Mode")
        else:
            self.theme_toggle_btn.setText("🌙 Dark Mode")
        
        # Reload stylesheet
        self.load_stylesheet()
        
        # Update visualization tab matplotlib toolbar
        if hasattr(self, 'visualization_tab') and self.visualization_tab:
            self.visualization_tab.update_theme(self.is_dark_mode)
        
        # Update status
        mode = "Dark" if self.is_dark_mode else "Light"
        self.statusBar.showMessage(f"Switched to {mode} Mode", 3000)
        print(f"DEBUG: Theme toggled to {mode} mode")
    
    def load_materials(self):
        """
        Load materials from database (Controller method).
        Calls Model (querier) and updates View (material_browser).
        """
        try:
            print("DEBUG: load_materials() starting...")
            # Get data from Model
            materials = self.querier.list_materials()
            print(f"DEBUG: Got {len(materials)} materials from database")
            print(f"DEBUG: Materials: {materials}")
            
            # Update View
            self.material_browser.load_materials(materials)
            print("DEBUG: Updated material browser")
            
            # Update status
            self.statusBar.showMessage(f"Loaded {len(materials)} materials", 3000)
            print(f"DEBUG: Updated status bar - {len(materials)} materials")
            
        except Exception as e:
            print(f"DEBUG ERROR in load_materials: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(
                self,
                "Load Error",
                f"Failed to load materials:\n{str(e)}"
            )
    
    def on_material_selected(self, material_name):
        """
        Handle material selection (Controller method).
        Called when user selects material in browser.
        
        CRITICAL: Fetch THREE data sets for proper 3-tab display:
        1. Original data (no overrides)
        2. Active data (with overrides)
        3. Overrides list
        """
        try:
            self.current_material = material_name
            
            # Get material ID first
            material_id = self.querier.get_material_id(material_name)
            
            # Fetch ORIGINAL data (NO overrides)
            material_data_original = self.querier.get_material_by_name(
                material_name,
                apply_overrides=False
            )
            
            # Fetch ACTIVE data (WITH overrides)
            material_data_with_overrides = self.querier.get_material_by_name(
                material_name,
                apply_overrides=True
            )
            
            # Fetch list of overrides
            overrides_list = self.querier.override_storage.list_overrides(material_id)
            
            # Fetch references for this material
            ref_ids = self.ref_querier.get_references_for_material(material_name)
            references_list = []
            for ref_id in ref_ids:
                ref_data = self.ref_querier.get_reference_by_id(ref_id)
                if ref_data:
                    references_list.append(ref_data)
            
            # DEBUG: Print data structure to understand what's loaded
            print(f"\n=== DEBUG: Material '{material_name}' data ===")
            print(f"Properties categories: {list(material_data_original.get('properties', {}).keys())}")
            print(f"Models types: {list(material_data_original.get('models', {}).keys())}")
            print(f"Number of overrides: {len(overrides_list)}")
            print(f"Number of references: {len(references_list)}")
            
            # Update property viewer with ALL data (including references)
            self.property_viewer.display_material(
                material_data_with_overrides,
                material_data_original,
                overrides_list,
                references_list,
                material_name
            )
            
            # Update override panel
            self.override_panel.set_material(material_name)
            
            # *** LINK TO VISUALIZATION TAB ***
            # Auto-select the material in visualization tab
            if hasattr(self, 'visualization_tab'):
                print(f"[MainWindow] Syncing material '{material_name}' to visualization tab")
                self.visualization_tab.select_material(material_name)
            
            # Update status
            override_count = len(overrides_list) if overrides_list else 0
            status_msg = f"Loaded: {material_name}"
            if override_count > 0:
                status_msg += f" ({override_count} overrides active)"
            self.statusBar.showMessage(status_msg, 3000)
            
        except Exception as e:
            print(f"DEBUG ERROR in on_material_selected: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(
                self,
                "Query Error",
                f"Failed to load material data:\n{str(e)}"
            )
    
    def on_tab_changed(self, index):
        """
        Handle tab changes in PropertyViewer.
        Show Override Panel ONLY in Original Data tab (tab 0).
        Hide it in all other tabs.
        
        Args:
            index: Index of the currently selected tab
                   0 = Original Data (show override panel)
                   1 = Overrides (hide override panel)
                   2 = Active View (hide override panel)
                   3 = References (hide override panel)
        """
        if index == 0:  # Original Data tab
            # Show override panel - this is where users create overrides
            self.override_panel.show()
        else:
            # Hide override panel for all other tabs
            self.override_panel.hide()
    
    def on_export_material(self):
        """Export current material to XML."""
        if not self.current_material:
            QMessageBox.information(
                self,
                "No Material Selected",
                "Please select a material to export."
            )
            return
        
        try:
            from export.xml_exporter import MaterialXMLExporter
            
            # Export using existing exporter (Model)
            exporter = MaterialXMLExporter(self.db)
            
            material_id = self.querier.get_material_id(self.current_material)
            has_overrides = self.querier.override_storage.has_overrides(material_id)
            
            suffix = "_Override" if has_overrides else ""
            output_path = exporter.export_material(self.current_material)
            
            QMessageBox.information(
                self,
                "Export Successful",
                f"Exported to:\n{output_path}"
            )
            
            self.statusBar.showMessage(f"Exported: {self.current_material}", 5000)
            
        except Exception as e:
            print(f"DEBUG ERROR in on_export_material: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export material:\n{str(e)}"
            )
    
    def on_export_tab(self, tab_name):
        """
        Export data from specific tab.
        
        Args:
            tab_name: "original", "overrides", or "active"
        """
        if not self.current_material:
            QMessageBox.information(
                self,
                "No Material Selected",
                "Please select a material to export."
            )
            return
        
        try:
            from export.xml_exporter import export_material_to_xml
            from PyQt6.QtWidgets import QFileDialog
            from config import EXPORT_DIR
            import os
            
            # Get appropriate data based on tab
            if tab_name == "original":
                # Export original data (no overrides)
                material_data = self.querier.get_material_by_name(
                    self.current_material,
                    apply_overrides=False
                )
                default_filename = f"{self.current_material}_Original.xml"
                title = "Export Original Data"
                
            elif tab_name == "overrides":
                # Export overrides list as XML
                material_id = self.querier.get_material_id(self.current_material)
                overrides_list = self.querier.override_storage.list_overrides(material_id)
                self._export_overrides_xml(overrides_list)
                return
                
            else:  # active
                # Export with overrides applied
                material_data = self.querier.get_material_by_name(
                    self.current_material,
                    apply_overrides=True
                )
                default_filename = f"{self.current_material}_Active.xml"
                title = "Export Active View"
            
            if not material_data:
                QMessageBox.warning(
                    self,
                    "Export Failed",
                    f"Could not retrieve data for {self.current_material}"
                )
                return
            
            # Ask user for save location
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                title,
                os.path.join(EXPORT_DIR, default_filename),
                "XML Files (*.xml);;All Files (*)"
            )
            
            if not file_path:
                return  # User cancelled
            
            # Export to selected file
            export_material_to_xml(material_data, file_path)
            
            QMessageBox.information(
                self,
                "Export Successful",
                f"Exported to:\n{file_path}"
            )
            self.statusBar.showMessage(f"Exported: {self.current_material}", 5000)
        
        except Exception as e:
            print(f"DEBUG ERROR in on_export_tab: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export:\n{str(e)}"
            )
    
    def _export_overrides_xml(self, overrides_list):
        """Export overrides to XML file."""
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Overrides",
            f"{self.current_material}_Overrides.xml",
            "XML Files (*.xml);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write(f'<overrides material="{self.current_material}" count="{len(overrides_list)}">\n')
                
                for override in overrides_list:
                    f.write('  <override>\n')
                    f.write(f'    <property>{override.get("property_path", "")}</property>\n')
                    f.write(f'    <original_value>{override.get("original_value", "")}</original_value>\n')
                    f.write(f'    <new_value>{override.get("new_value", "")}</new_value>\n')
                    if override.get("unit"):
                        f.write(f'    <unit>{override.get("unit")}</unit>\n')
                    if override.get("reason"):
                        f.write(f'    <reason>{override.get("reason")}</reason>\n')
                    f.write(f'    <timestamp>{override.get("timestamp", "")}</timestamp>\n')
                    f.write('  </override>\n')
                
                f.write('</overrides>\n')
            
            QMessageBox.information(
                self,
                "Export Successful",
                f"Overrides exported to:\n{file_path}"
            )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export overrides:\n{str(e)}"
            )
    
    def on_override_requested(self, property_path, value, unit, reason):
        """Handle override request from UI."""
        if not self.current_material:
            return
        
        try:
            # Use the querier's override_storage which already has the connection
            material_id = self.querier.get_material_id(self.current_material)
            
            self.querier.override_storage.save_value_override(
                material_id,
                property_path,
                value,
                unit=unit,
                reason=reason
            )
            
            # Reload material to show override
            self.on_material_selected(self.current_material)
            
            self.statusBar.showMessage("Override applied successfully!", 3000)
            
            QMessageBox.information(
                self,
                "Override Applied",
                f"Successfully applied override to:\n{property_path}"
            )
            
        except Exception as e:
            print(f"DEBUG ERROR in on_override_requested: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(
                self,
                "Override Error",
                f"Failed to apply override:\n{str(e)}"
            )
    
    def on_clear_override_requested(self, property_path):
        """Handle clear override request."""
        if not self.current_material:
            return
        
        try:
            # Use the querier's override_storage which already has the connection
            material_id = self.querier.get_material_id(self.current_material)
            
            self.querier.override_storage.delete_override(material_id, property_path)
            
            # Reload material
            self.on_material_selected(self.current_material)
            
            self.statusBar.showMessage("Override cleared successfully!", 3000)
            
            QMessageBox.information(
                self,
                "Override Cleared",
                f"Successfully cleared override for:\n{property_path}"
            )
            
        except Exception as e:
            print(f"DEBUG ERROR in on_clear_override_requested: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(
                self,
                "Clear Error",
                f"Failed to clear override:\n{str(e)}"
            )
    
    def on_list_overrides(self):
        """List all overrides for current material."""
        if not self.current_material:
            QMessageBox.information(
                self,
                "No Material Selected",
                "Please select a material to view overrides."
            )
            return
        
        try:
            material_id = self.querier.get_material_id(self.current_material)
            overrides = self.querier.override_storage.list_overrides(material_id)
            
            if not overrides:
                QMessageBox.information(
                    self,
                    "No Overrides",
                    f"No overrides found for {self.current_material}"
                )
                return
            
            # Format override list
            override_text = f"Overrides for {self.current_material}:\n\n"
            for override in overrides:
                path = override.get('property_path', 'N/A')
                override_type = override.get('override_type', 'N/A')
                data = override.get('override_data', {})
                created = override.get('created_at', 'N/A')
                
                override_text += f"• {path}\n"
                override_text += f"  Type: {override_type}\n"
                
                if 'value' in data:
                    unit = data.get('unit', '')
                    override_text += f"  Value: {data['value']} {unit}\n".strip() + "\n"
                
                if 'reason' in data:
                    override_text += f"  Reason: {data['reason']}\n"
                
                override_text += f"  Created: {created}\n"
                override_text += "\n"
            
            QMessageBox.information(
                self,
                "Material Overrides",
                override_text
            )
            
        except Exception as e:
            print(f"DEBUG ERROR in on_list_overrides: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(
                self,
                "Error",
                f"Failed to list overrides:\n{str(e)}"
            )
    
    def on_query_material(self):
        """Query material (placeholder for future enhancement)."""
        QMessageBox.information(
            self,
            "Query Material",
            "Advanced query interface coming soon!"
        )
    
    def on_about(self):
        """Show about dialog."""
        about_text = """
        <h2>Materials Database Explorer</h2>
        <p>Version 1.0.0</p>
        <p>A professional desktop application for managing materials data.</p>
        
        <h3>Features:</h3>
        <ul>
            <li>Browse 17 materials with 2000+ parameters</li>
            <li>Non-destructive override system</li>
            <li>XML export with solver compatibility</li>
            <li>PostgreSQL database backend</li>
        </ul>
        
        <p><b>Architecture:</b> PyQt6 with MVC pattern</p>
        <p><b>Database:</b> PostgreSQL 18.1+</p>
        <p><b>Python:</b> 3.13+</p>
        """
        
        QMessageBox.about(self, "About Materials Database", about_text)
    
    def on_browse_references(self):
        """Open the reference browser dialog."""
        try:
            from gui.views.reference_browser_dialog import ReferenceBrowserDialog
            
            dialog = ReferenceBrowserDialog(self.ref_querier, self)
            dialog.exec()
            
        except Exception as e:
            print(f"DEBUG ERROR in on_browse_references: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open reference browser:\n{str(e)}"
            )
    
    def on_validate_references(self):
        """Validate reference integrity."""
        try:
            # Get all materials
            materials = self.querier.list_all_materials()
            
            # Get all references
            all_refs = self.ref_querier.list_all_references()
            ref_ids_in_db = set(ref['reference_id'] for ref in all_refs)
            
            # Check each material for invalid references
            issues = []
            unused_refs = ref_ids_in_db.copy()
            
            for material_name in materials:
                # Get references used by this material
                try:
                    ref_ids = self.ref_querier.get_references_for_material(material_name)
                    
                    for ref_id in ref_ids:
                        # Check if reference exists
                        if ref_id not in ref_ids_in_db:
                            issues.append(f"❌ {material_name}: References missing ID {ref_id}")
                        else:
                            # Remove from unused set
                            unused_refs.discard(ref_id)
                except Exception as e:
                    issues.append(f"⚠ {material_name}: Error checking references - {e}")
            
            # Build report
            report = f"""<h3>Reference Validation Report</h3>
<p><b>Total References:</b> {len(all_refs)}</p>
<p><b>Materials Checked:</b> {len(materials)}</p>
<hr>
"""
            
            if issues:
                report += f"<p><b>❌ Found {len(issues)} issue(s):</b></p><ul>"
                for issue in issues[:20]:  # Limit to first 20
                    report += f"<li>{issue}</li>"
                if len(issues) > 20:
                    report += f"<li>... and {len(issues) - 20} more</li>"
                report += "</ul>"
            else:
                report += "<p><b>✅ All material references are valid!</b></p>"
            
            if unused_refs:
                report += f"<hr><p><b>⚠ {len(unused_refs)} unused reference(s):</b></p>"
                report += f"<p>{', '.join(str(r) for r in sorted(list(unused_refs)[:30]))}"
                if len(unused_refs) > 30:
                    report += f" ... and {len(unused_refs) - 30} more"
                report += "</p>"
            else:
                report += "<hr><p><b>✅ All references are used by materials!</b></p>"
            
            msg = QMessageBox(self)
            msg.setWindowTitle("Reference Validation")
            msg.setTextFormat(Qt.TextFormat.RichText)
            msg.setText(report)
            msg.setIcon(QMessageBox.Icon.Information if not issues else QMessageBox.Icon.Warning)
            msg.exec()
            
        except Exception as e:
            print(f"DEBUG ERROR in on_validate_references: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Validation Error",
                f"Failed to validate references:\n{str(e)}"
            )
    
    # ========== Data Addition Handlers (NEW) ==========
    
    def on_add_material(self):
        """Open dialog to add a new material or add to existing material."""
        try:
            from gui.views.dialogs import AddMaterialDialog
            
            # Check if a material is currently selected
            material_id = None
            if hasattr(self, 'current_material') and self.current_material:
                # Try to get material_id from current selection
                if isinstance(self.current_material, dict):
                    material_id = self.current_material.get('metadata', {}).get('id')
                elif isinstance(self.current_material, str):
                    # current_material is material name, get ID from database
                    material_id = self._get_material_id_by_name(self.current_material)
            
            dialog = AddMaterialDialog(self.db, self, material_id=material_id)
            dialog.material_added.connect(self.on_material_added)
            dialog.property_added.connect(self.on_property_added)
            dialog.model_added.connect(self.on_model_added)
            dialog.exec()
            
        except Exception as e:
            print(f"DEBUG ERROR in on_add_material: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open add material dialog:\n{str(e)}"
            )
    
    def _get_material_id_by_name(self, material_name):
        """Helper to get material_id from name."""
        try:
            conn = self.db.connect()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT material_id FROM materials WHERE name = %s", (material_name,))
                row = cursor.fetchone()
                if row:
                    return row[0]
        except Exception as e:
            print(f"Error getting material ID: {e}")
        return None
    
    def on_material_added(self, material_id: int):
        """Handle material addition - refresh views."""
        try:
            print(f"DEBUG: Material added - ID: {material_id}")
            
            # Refresh material list
            self.load_materials()
            
            # Refresh visualization if it exists
            if hasattr(self, 'visualization_tab'):
                self.visualization_tab.load_available_materials()
            
            # Select the new material
            # TODO: Implement material selection by ID
            
            self.statusBar().showMessage(f"✓ Material added successfully (ID: {material_id})", 5000)
        except Exception as e:
            print(f"ERROR in on_material_added: {e}")
            import traceback
            traceback.print_exc()
    
    def on_property_added(self, material_name: str):
        """Handle property addition - refresh current material view."""
        try:
            print(f"DEBUG: Property added to material: {material_name}")
            
            # Reload current material if it's the one that was modified
            if self.current_material:
                # current_material is a string (material name)
                if isinstance(self.current_material, str) and self.current_material == material_name:
                    # Refresh property viewer
                    self.on_material_selected(material_name)
                elif isinstance(self.current_material, dict) and self.current_material.get('metadata', {}).get('name') == material_name:
                    # Refresh property viewer
                    self.on_material_selected(material_name)
            
            self.statusBar().showMessage(f"✓ Property added to {material_name}", 5000)
        except Exception as e:
            print(f"ERROR in on_property_added: {e}")
            import traceback
            traceback.print_exc()
    
    def on_model_added(self, material_id: int):
        """Handle model addition - refresh current material view."""
        try:
            print(f"DEBUG: Model added to material ID: {material_id}")
            
            # Reload current material if it's the one that was modified
            if self.current_material:
                # Get material name from ID
                conn = self.db.connect()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM materials WHERE material_id = %s", (material_id,))
                    row = cursor.fetchone()
                    if row:
                        material_name = row[0]
                        if isinstance(self.current_material, str) and self.current_material == material_name:
                            self.on_material_selected(material_name)
            
            self.statusBar.showMessage(f"✓ Model added to material (ID: {material_id})", 5000)
        except Exception as e:
            print(f"ERROR in on_model_added: {e}")
            import traceback
            traceback.print_exc()
    
    def on_reference_added(self, reference_id: int):
        """Handle reference addition - show confirmation."""
        try:
            print(f"DEBUG: Reference added - ID: {reference_id}")
            
            self.statusBar().showMessage(f"✓ Reference {reference_id} added successfully", 5000)
            
            # Refresh reference browser if it's open
            # (References are loaded dynamically, so no action needed for dropdowns)
        except Exception as e:
            print(f"ERROR in on_reference_added: {e}")
            import traceback
            traceback.print_exc()
    
    # ========== End Data Addition Handlers ==========
    
    def closeEvent(self, event):
        """Handle window close event."""
        reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to exit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Close database connection
            if hasattr(self, 'db'):
                self.db.close()
            event.accept()
        else:
            event.ignore()
