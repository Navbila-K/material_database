"""
Property Viewer v3 - PROFESSIONAL ARCHITECTURE

Three-tab design for Material Data Governance:
1. Original Data - Raw database (NO overrides)
2. Overrides - ONLY overridden properties (comparison)
3. Active View - Effective data (original + overrides)

CRITICAL: This is a READ-ONLY explorer.
Overrides are non-destructive and material-specific.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QTableWidget,
    QTableWidgetItem, QLabel, QHeaderView, QHBoxLayout, QPushButton, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

# Import the new ReferenceViewer widget
from gui.views.reference_viewer import ReferenceViewer


class PropertyViewer(QWidget):
    """
    Property viewer with professional three-tab architecture.
    
    Tab Structure:
    - Original Data: Raw database values (NO overrides applied)
    - Overrides: ONLY overridden properties with before/after comparison
    - Active View: Effective data for export/visualization
    """
    
    # Signal to request export
    export_requested = pyqtSignal(str)  # tab_name: "original", "overrides", "active"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_material = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        self.title_label = QLabel("Select a material")
        self.title_label.setProperty("heading", True)
        layout.addWidget(self.title_label)
        
        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # TAB 1: Original Data (read-only, no overrides)
        original_container = QWidget()
        original_layout = QVBoxLayout(original_container)
        original_layout.setContentsMargins(0, 0, 0, 0)
        self.original_data_tab = self._create_table()
        original_layout.addWidget(self.original_data_tab)
        # Export button for Original Data
        export_original_btn = QPushButton("Export Original Data as XML")
        export_original_btn.clicked.connect(lambda: self.export_requested.emit("original"))
        original_layout.addWidget(export_original_btn)
        self.tabs.addTab(original_container, "Original Data")
        self.tabs.setTabToolTip(0, "Raw database values - NO overrides applied")
        
        # TAB 2: Overrides (comparison view)
        overrides_container = QWidget()
        overrides_layout = QVBoxLayout(overrides_container)
        overrides_layout.setContentsMargins(0, 0, 0, 0)
        self.overrides_tab = self._create_override_table()
        overrides_layout.addWidget(self.overrides_tab)
        # Export button for Overrides
        export_overrides_btn = QPushButton("Export Overrides as XML")
        export_overrides_btn.clicked.connect(lambda: self.export_requested.emit("overrides"))
        overrides_layout.addWidget(export_overrides_btn)
        self.tabs.addTab(overrides_container, "Overrides")
        self.tabs.setTabToolTip(1, "ONLY overridden properties - shows original vs your override")
        
        # TAB 3: Active View (with overrides applied)
        active_container = QWidget()
        active_layout = QVBoxLayout(active_container)
        active_layout.setContentsMargins(0, 0, 0, 0)
        self.active_view_tab = self._create_table()
        active_layout.addWidget(self.active_view_tab)
        # Export button for Active View
        export_active_btn = QPushButton("Export Active View as XML")
        export_active_btn.clicked.connect(lambda: self.export_requested.emit("active"))
        active_layout.addWidget(export_active_btn)
        self.tabs.addTab(active_container, "Active View")
        self.tabs.setTabToolTip(2, "Final export-ready data - overrides highlighted in GOLD")
        
        # TAB 4: References (shows citations used by material)
        self.references_tab = ReferenceViewer()
        self.tabs.addTab(self.references_tab, "References")
        self.tabs.setTabToolTip(3, "Scientific references and citations used by this material")
    
    def _create_table(self):
        """Create standard 4-column table for data display."""
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Property", "Value", "Unit", "Reference"])
        
        # Configure headers
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        # Read-only
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        return table
    
    def _create_override_table(self):
        """Create comparison table for overrides (before/after)."""
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Property", 
            "Original Value", 
            "New Value", 
            "Unit", 
            "Reason",
            "Type"
        ])
        
        # Configure headers
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        # Read-only
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        return table
    
    def display_material(self, material_data_with_overrides, material_data_original, overrides_list=None, references_list=None, material_name=None):
        """
        Display material in all four tabs.
        
        Args:
            material_data_with_overrides: Data with overrides applied (Active View)
            material_data_original: Raw database data (Original Data)
            overrides_list: List of override dictionaries (Overrides tab)
            references_list: List of reference dictionaries (References tab)
            material_name: Name of the material
        """
        material_name = material_name or material_data_with_overrides.get('metadata', {}).get('name', 'Unknown')
        self.title_label.setText(f"Material: {material_name}")
        
        # Build reference cache for tooltips
        self.reference_cache = {}
        if references_list:
            for ref in references_list:
                self.reference_cache[ref.get('reference_id')] = ref
        
        # Clear all tabs
        self.original_data_tab.setRowCount(0)
        self.overrides_tab.setRowCount(0)
        self.active_view_tab.setRowCount(0)
        
        # TAB 1: Original Data (NO overrides)
        self._load_data_to_table(
            self.original_data_tab,
            material_data_original.get('properties', {}),
            material_data_original.get('models', {}),
            highlight_overrides=False
        )
        
        # TAB 2: Overrides (comparison)
        self._load_overrides_comparison(
            material_data_original,
            material_data_with_overrides,
            overrides_list or []
        )
        
        # TAB 3: Active View (with overrides)
        self._load_data_to_table(
            self.active_view_tab,
            material_data_with_overrides.get('properties', {}),
            material_data_with_overrides.get('models', {}),
            highlight_overrides=True
        )
        
        # TAB 4: References (NEW)
        if references_list is not None:
            self.references_tab.display_references(material_name, references_list)
        else:
            self.references_tab.clear()
    
    def _load_data_to_table(self, table, properties, models, highlight_overrides=False):
        """
        Load properties and models into a table.
        CRITICAL: Display ALL entries, including empty/null values.
        
        Args:
            table: QTableWidget to populate
            properties: Properties dictionary
            models: Models dictionary
            highlight_overrides: If True, highlight USER_OVERRIDE entries in gold
        """
        row = 0
        
        # Load properties
        for category, props in properties.items():
            if category == "Phase":
                state = props.get('State')
                table.insertRow(row)
                table.setItem(row, 0, QTableWidgetItem(f"properties.Phase.State"))
                table.setItem(row, 1, QTableWidgetItem(state if state else "(empty)"))
                table.setItem(row, 2, QTableWidgetItem(""))
                table.setItem(row, 3, QTableWidgetItem(""))
                if not state:
                    self._set_empty_style(table, row)
                row += 1
                continue
            
            # Handle Thermal, Mechanical, etc.
            for prop_name, prop_data in props.items():
                if isinstance(prop_data, dict):
                    unit = prop_data.get('unit', '')
                    entries = prop_data.get('entries', [])
                    
                    if not entries:
                        # No entries at all - show empty
                        table.insertRow(row)
                        table.setItem(row, 0, QTableWidgetItem(f"properties.{category}.{prop_name}"))
                        table.setItem(row, 1, QTableWidgetItem("(empty)"))
                        table.setItem(row, 2, QTableWidgetItem(unit))
                        table.setItem(row, 3, QTableWidgetItem(""))
                        self._set_empty_style(table, row)
                        row += 1
                    else:
                        # Display ALL entries (including null ones)
                        for entry in entries:
                            table.insertRow(row)
                            table.setItem(row, 0, QTableWidgetItem(f"properties.{category}.{prop_name}"))
                            
                            value = entry.get('value')
                            if value is None or value == '':
                                table.setItem(row, 1, QTableWidgetItem("(null)"))
                                self._set_empty_style(table, row)
                            else:
                                table.setItem(row, 1, QTableWidgetItem(str(value)))
                            
                            table.setItem(row, 2, QTableWidgetItem(unit))
                            
                            ref = entry.get('ref', '')
                            ref_item = QTableWidgetItem(str(ref) if ref else "")
                            table.setItem(row, 3, ref_item)
                            
                            # Add tooltip to reference cell
                            if ref:
                                self._set_reference_tooltip(ref_item, ref)
                            
                            # Highlight overrides in Active View
                            if highlight_overrides and ref == "USER_OVERRIDE":
                                self._highlight_row(table, row)
                            
                            row += 1
        
        # Load models - handle ALL model types
        print(f"DEBUG [property_viewer]: Loading models, total types = {len(models)}")
        print(f"DEBUG [property_viewer]: Model types: {list(models.keys())}")
        for model_type, model_data in models.items():
            print(f"DEBUG [property_viewer]: Processing model_type = '{model_type}'")
            print(f"DEBUG [property_viewer]: model_data type = {type(model_data)}, data = {model_data}")
            if not isinstance(model_data, dict):
                print(f"DEBUG [property_viewer]: Skipping {model_type} - not a dict")
                continue
            
            # Special handling for EOSModel with 'rows' structure
            if model_type == 'EOSModel' and 'rows' in model_data:
                rows_list = model_data.get('rows', [])
                if not rows_list:
                    # Show empty EOS model
                    table.insertRow(row)
                    table.setItem(row, 0, QTableWidgetItem(f"models.{model_type}"))
                    table.setItem(row, 1, QTableWidgetItem("(no rows)"))
                    table.setItem(row, 2, QTableWidgetItem(""))
                    table.setItem(row, 3, QTableWidgetItem(""))
                    self._set_empty_style(table, row)
                    row += 1
                else:
                    # Display each row and its parameters
                    for eos_row in rows_list:
                        row_index = eos_row.get('index', '?')
                        parameters = eos_row.get('parameters', {})
                        
                        for param_name, param_value in parameters.items():
                            if isinstance(param_value, dict):
                                # Simple parameter
                                if 'value' in param_value:
                                    table.insertRow(row)
                                    table.setItem(row, 0, QTableWidgetItem(f"models.{model_type}.Row[{row_index}].{param_name}"))
                                    
                                    value = param_value.get('value')
                                    if value is None or value == '':
                                        table.setItem(row, 1, QTableWidgetItem("(null)"))
                                        self._set_empty_style(table, row)
                                    else:
                                        table.setItem(row, 1, QTableWidgetItem(str(value)))
                                    
                                    table.setItem(row, 2, QTableWidgetItem(param_value.get('unit', '')))
                                    
                                    ref = param_value.get('ref', '')
                                    table.setItem(row, 3, QTableWidgetItem(str(ref) if ref else ""))
                                    
                                    if highlight_overrides and ref == "USER_OVERRIDE":
                                        self._highlight_row(table, row)
                                    
                                    row += 1
                                else:
                                    # Nested dict (unreacted/reacted)
                                    for nested_name, nested_value in param_value.items():
                                        if isinstance(nested_value, dict) and 'value' in nested_value:
                                            table.insertRow(row)
                                            table.setItem(row, 0, QTableWidgetItem(f"models.{model_type}.Row[{row_index}].{param_name}.{nested_name}"))
                                            
                                            value = nested_value.get('value')
                                            if value is None or value == '':
                                                table.setItem(row, 1, QTableWidgetItem("(null)"))
                                                self._set_empty_style(table, row)
                                            else:
                                                table.setItem(row, 1, QTableWidgetItem(str(value)))
                                            
                                            table.setItem(row, 2, QTableWidgetItem(nested_value.get('unit', '')))
                                            
                                            ref = nested_value.get('ref', '')
                                            table.setItem(row, 3, QTableWidgetItem(str(ref) if ref else ""))
                                            
                                            if highlight_overrides and ref == "USER_OVERRIDE":
                                                self._highlight_row(table, row)
                                            
                                            row += 1
                continue  # Skip normal processing for EOSModel
            
            # Process each sub-model or parameter
            print(f"DEBUG [property_viewer]: Processing params for {model_type}, total params = {len(model_data)}")
            for param_name, param_value in model_data.items():
                print(f"DEBUG [property_viewer]:   param_name = '{param_name}', type = {type(param_value)}")
                if isinstance(param_value, list):
                    # List of entries (like ThermoMechanical parameters)
                    print(f"DEBUG [property_viewer]:     It's a list with {len(param_value)} entries")
                    for entry in param_value:
                        if isinstance(entry, dict):
                            table.insertRow(row)
                            table.setItem(row, 0, QTableWidgetItem(f"models.{model_type}.{param_name}"))
                            print(f"DEBUG [property_viewer]:     Inserted row {row}: models.{model_type}.{param_name} = {entry.get('value')}")
                            
                            value = entry.get('value')
                            if value is None or value == '':
                                table.setItem(row, 1, QTableWidgetItem("(null)"))
                                self._set_empty_style(table, row)
                            else:
                                table.setItem(row, 1, QTableWidgetItem(str(value)))
                            
                            table.setItem(row, 2, QTableWidgetItem(entry.get('unit', '')))
                            
                            ref = entry.get('ref', '')
                            ref_item = QTableWidgetItem(str(ref) if ref else "")
                            table.setItem(row, 3, ref_item)
                            
                            # Add tooltip to reference cell
                            if ref:
                                self._set_reference_tooltip(ref_item, ref)
                            
                            if highlight_overrides and ref == "USER_OVERRIDE":
                                self._highlight_row(table, row)
                            
                            row += 1
                
                elif isinstance(param_value, dict):
                    print(f"DEBUG [property_viewer]:     It's a dict with keys: {list(param_value.keys())}")
                    # Could be nested dict (SpecificHeatConstants) or sub-model
                    if 'value' in param_value:
                        print(f"DEBUG [property_viewer]:     Direct value dict")
                        # Direct value dict
                        table.insertRow(row)
                        table.setItem(row, 0, QTableWidgetItem(f"models.{model_type}.{param_name}"))
                        print(f"DEBUG [property_viewer]:     Inserted row {row}: models.{model_type}.{param_name} = {param_value.get('value')}")
                        
                        value = param_value.get('value')
                        if value is None or value == '':
                            table.setItem(row, 1, QTableWidgetItem("(null)"))
                            self._set_empty_style(table, row)
                        else:
                            table.setItem(row, 1, QTableWidgetItem(str(value)))
                        
                        table.setItem(row, 2, QTableWidgetItem(param_value.get('unit', '')))
                        
                        ref = param_value.get('ref', '')
                        ref_item = QTableWidgetItem(str(ref) if ref else "")
                        table.setItem(row, 3, ref_item)
                        
                        # Add tooltip to reference cell
                        if ref:
                            self._set_reference_tooltip(ref_item, ref)
                        
                        if highlight_overrides and ref == "USER_OVERRIDE":
                            self._highlight_row(table, row)
                        
                        row += 1
                    else:
                        # Nested structure - recursively process
                        for sub_name, sub_value in param_value.items():
                            if isinstance(sub_value, dict) and 'value' in sub_value:
                                # Nested parameter (e.g., SpecificHeatConstants.c0)
                                table.insertRow(row)
                                table.setItem(row, 0, QTableWidgetItem(f"models.{model_type}.{param_name}.{sub_name}"))
                                
                                value = sub_value.get('value')
                                if value is None or value == '':
                                    table.setItem(row, 1, QTableWidgetItem("(null)"))
                                    self._set_empty_style(table, row)
                                else:
                                    table.setItem(row, 1, QTableWidgetItem(str(value)))
                                
                                table.setItem(row, 2, QTableWidgetItem(sub_value.get('unit', '')))
                                
                                ref = sub_value.get('ref', '')
                                ref_item = QTableWidgetItem(str(ref) if ref else "")
                                table.setItem(row, 3, ref_item)
                                
                                # Add tooltip to reference cell
                                if ref:
                                    self._set_reference_tooltip(ref_item, ref)
                                
                                if highlight_overrides and ref == "USER_OVERRIDE":
                                    self._highlight_row(table, row)
                                
                                row += 1
                            elif isinstance(sub_value, list):
                                # List of sub-entries
                                for sub_entry in sub_value:
                                    if isinstance(sub_entry, dict):
                                        table.insertRow(row)
                                        table.setItem(row, 0, QTableWidgetItem(f"models.{model_type}.{param_name}.{sub_name}"))
                                        
                                        value = sub_entry.get('value')
                                        if value is None or value == '':
                                            table.setItem(row, 1, QTableWidgetItem("(null)"))
                                            self._set_empty_style(table, row)
                                        else:
                                            table.setItem(row, 1, QTableWidgetItem(str(value)))
                                        
                                        table.setItem(row, 2, QTableWidgetItem(sub_entry.get('unit', '')))
                                        
                                        ref = sub_entry.get('ref', '')
                                        ref_item = QTableWidgetItem(str(ref) if ref else "")
                                        table.setItem(row, 3, ref_item)
                                        
                                        # Add tooltip to reference cell
                                        if ref:
                                            self._set_reference_tooltip(ref_item, ref)
                                        
                                        if highlight_overrides and ref == "USER_OVERRIDE":
                                            self._highlight_row(table, row)
                                        
                                        row += 1
    
    def _load_overrides_comparison(self, original_data, override_data, overrides_list):
        """
        Load ONLY overridden properties with before/after comparison.
        
        Args:
            original_data: Original material data (no overrides)
            override_data: Material data with overrides applied
            overrides_list: List of override entries
        """
        if not overrides_list:
            # No overrides
            self.overrides_tab.insertRow(0)
            msg_item = QTableWidgetItem("No overrides applied to this material")
            msg_item.setForeground(QColor(150, 150, 150))
            self.overrides_tab.setItem(0, 0, msg_item)
            self.overrides_tab.setSpan(0, 0, 1, 6)
            return
        
        row = 0
        for override in overrides_list:
            property_path = override.get('property_path', '')
            override_type = override.get('override_type', '')
            override_data_dict = override.get('override_data', {})
            
            if override_type == 'value_override':
                # Extract original value from path
                original_value = self._get_value_from_path(original_data, property_path)
                new_value = override_data_dict.get('value', '')
                unit = override_data_dict.get('unit', '')
                reason = override_data_dict.get('reason', 'User override')
                
                self.overrides_tab.insertRow(row)
                self.overrides_tab.setItem(row, 0, QTableWidgetItem(property_path))
                self.overrides_tab.setItem(row, 1, QTableWidgetItem(str(original_value)))
                self.overrides_tab.setItem(row, 2, QTableWidgetItem(str(new_value)))
                self.overrides_tab.setItem(row, 3, QTableWidgetItem(unit))
                self.overrides_tab.setItem(row, 4, QTableWidgetItem(reason))
                self.overrides_tab.setItem(row, 5, QTableWidgetItem("Value"))
                
                # Highlight entire row
                self._highlight_row(self.overrides_tab, row, columns=6)
                row += 1
            
            elif override_type == 'reference_preference':
                preferred_ref = override_data_dict.get('preferred_reference', '')
                
                self.overrides_tab.insertRow(row)
                self.overrides_tab.setItem(row, 0, QTableWidgetItem(property_path))
                self.overrides_tab.setItem(row, 1, QTableWidgetItem(""))
                self.overrides_tab.setItem(row, 2, QTableWidgetItem(""))
                self.overrides_tab.setItem(row, 3, QTableWidgetItem(""))
                self.overrides_tab.setItem(row, 4, QTableWidgetItem(f"Preferred reference: {preferred_ref}"))
                self.overrides_tab.setItem(row, 5, QTableWidgetItem("Reference"))
                
                self._highlight_row(self.overrides_tab, row, columns=6)
                row += 1
    
    def _get_value_from_path(self, data, path):
        """
        Extract original value from data using property path.
        
        Args:
            data: Material data dictionary
            path: Property path (e.g., 'properties.Thermal.Cp')
        
        Returns:
            Original value or 'N/A'
        """
        try:
            parts = path.split('.')
            current = data
            
            for part in parts:
                if isinstance(current, dict):
                    current = current.get(part, {})
                else:
                    return 'N/A'
            
            if isinstance(current, dict) and 'value' in current:
                return current['value']
            
            return str(current) if current else 'N/A'
        
        except Exception:
            return 'N/A'
    
    def _highlight_row(self, table, row, columns=4):
        """
        Highlight a row in gold.
        
        Args:
            table: QTableWidget
            row: Row number
            columns: Number of columns to highlight
        """
        color = QColor(255, 215, 0, 50)  # Gold with transparency
        for col in range(columns):
            item = table.item(row, col)
            if item:
                item.setBackground(color)
    
    def _set_empty_style(self, table, row):
        """
        Style empty/null values with gray text.
        
        Args:
            table: QTableWidget
            row: Row number
        """
        gray = QColor(120, 120, 120)
        for col in range(4):
            item = table.item(row, col)
            if item:
                item.setForeground(gray)
    
    def _set_reference_tooltip(self, item, ref_value):
        """
        Add tooltip to reference cell showing full citation.
        
        Args:
            item: QTableWidgetItem for the reference cell
            ref_value: Reference ID (string or number)
        """
        if not ref_value or ref_value == "USER_OVERRIDE":
            return
        
        try:
            # Extract numeric ID from reference string
            ref_id = None
            if isinstance(ref_value, (int, float)):
                ref_id = int(ref_value)
            elif isinstance(ref_value, str) and ref_value.strip().isdigit():
                ref_id = int(ref_value.strip())
            
            if ref_id and hasattr(self, 'reference_cache'):
                # Look up reference in cache (populated when material is loaded)
                ref_data = self.reference_cache.get(ref_id)
                
                if ref_data:
                    # Create rich tooltip with full citation
                    tooltip = f"""<b>Reference #{ref_id}</b><br>
<i>{ref_data.get('title', 'No title')}</i><br>
<br>
<b>Author:</b> {ref_data.get('author', 'Unknown')}<br>
<b>Year:</b> {ref_data.get('year', '--')}<br>
<b>Type:</b> {ref_data.get('ref_type', 'unknown')}<br>
<b>Journal:</b> {ref_data.get('journal', '--')}<br>
<b>Volume:</b> {ref_data.get('volume', '--')}, <b>Pages:</b> {ref_data.get('pages', '--')}
"""
                    item.setToolTip(tooltip)
        except (ValueError, TypeError):
            pass  # Invalid reference format, skip tooltip
