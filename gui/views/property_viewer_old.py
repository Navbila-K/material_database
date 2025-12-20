"""
Property Viewer

Displays material properties and model parameters in tabs.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QTableWidget,
    QTableWidgetItem, QLabel, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class PropertyViewer(QWidget):
    """
    Property viewer with tabbed interface for different data categories.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
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
        
        # Create tabs
        self.properties_tab = self.create_table_widget()
        self.models_tab = self.create_table_widget()
        self.overrides_tab = self.create_table_widget()
        
        self.tabs.addTab(self.properties_tab, "Properties")
        self.tabs.addTab(self.models_tab, "Models")
        self.tabs.addTab(self.overrides_tab, "Overrides")
    
    def create_table_widget(self):
        """Create a configured table widget."""
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Property", "Value", "Unit", "Reference"])
        
        # Configure headers
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        # Make read-only
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        return table
    
    def display_material(self, material_data, overrides_list=None):
        """
        Display material data.
        
        Args:
            material_data: Dictionary with material information
            overrides_list: Optional list of override dictionaries
        """
        self.title_label.setText(f"Material: {material_data.get('name', 'Unknown')}")
        
        # Clear existing data
        self.properties_tab.setRowCount(0)
        self.models_tab.setRowCount(0)
        self.overrides_tab.setRowCount(0)
        
        # Load properties
        self._load_properties(material_data.get('properties', {}))
        
        # Load models
        self._load_models(material_data.get('models', {}))
        
        # Load overrides if provided
        if overrides_list:
            self._load_overrides(overrides_list)
    
    def _load_properties(self, properties):
        """Load properties into table."""
        row = 0
        
        for category, props in properties.items():
            if category == "Phase":
                # Handle Phase specially
                state = props.get('State')
                if state:
                    self.properties_tab.insertRow(row)
                    self.properties_tab.setItem(row, 0, QTableWidgetItem(f"Phase.State"))
                    self.properties_tab.setItem(row, 1, QTableWidgetItem(state))
                    self.properties_tab.setItem(row, 2, QTableWidgetItem(""))
                    self.properties_tab.setItem(row, 3, QTableWidgetItem(""))
                    row += 1
                continue
            
            # Handle other categories
            for prop_name, prop_data in props.items():
                entries = prop_data.get('entries', [])
                unit = prop_data.get('unit', '')
                
                for entry in entries:
                    self.properties_tab.insertRow(row)
                    
                    # Property name
                    name_item = QTableWidgetItem(f"{category}.{prop_name}")
                    self.properties_tab.setItem(row, 0, name_item)
                    
                    # Value
                    value = entry.get('value', '')
                    value_item = QTableWidgetItem(str(value))
                    self.properties_tab.setItem(row, 1, value_item)
                    
                    # Unit
                    unit_item = QTableWidgetItem(unit)
                    self.properties_tab.setItem(row, 2, unit_item)
                    
                    # Reference
                    ref = entry.get('ref', '')
                    ref_item = QTableWidgetItem(str(ref))
                    
                    # Highlight overrides
                    if ref == "USER_OVERRIDE":
                        color = QColor(255, 215, 0, 50)  # Gold background
                        for col in range(4):
                            item = self.properties_tab.item(row, col)
                            if item:
                                item.setBackground(color)
                    
                    self.properties_tab.setItem(row, 3, ref_item)
                    row += 1
    
    def _load_models(self, models):
        """Load model parameters into table."""
        row = 0
        
        for model_type, model_data in models.items():
            # Handle different model structures
            if model_type == "ElastoPlastic":
                self._load_elastoplastic(model_data, row)
                row = self.models_tab.rowCount()
            
            elif model_type == "ElasticModel":
                # ThermoMechanical sub-model
                thermo = model_data.get('ThermoMechanical', {})
                for param_name, param_value in thermo.items():
                    if isinstance(param_value, list):
                        # Multiple entries
                        for entry in param_value:
                            self.models_tab.insertRow(row)
                            self.models_tab.setItem(row, 0, QTableWidgetItem(f"ElasticModel.ThermoMechanical.{param_name}"))
                            self.models_tab.setItem(row, 1, QTableWidgetItem(str(entry.get('value', ''))))
                            self.models_tab.setItem(row, 2, QTableWidgetItem(entry.get('unit', '')))
                            
                            ref = entry.get('ref', '')
                            ref_item = QTableWidgetItem(str(ref))
                            
                            # Highlight overrides
                            if ref == "USER_OVERRIDE":
                                color = QColor(255, 215, 0, 50)
                                for col in range(4):
                                    item = self.models_tab.item(row, col)
                                    if item:
                                        item.setBackground(color)
                            
                            self.models_tab.setItem(row, 3, ref_item)
                            row += 1
                    
                    elif isinstance(param_value, dict):
                        # Nested structure (like SpecificHeatConstants)
                        for sub_name, sub_data in param_value.items():
                            self.models_tab.insertRow(row)
                            self.models_tab.setItem(row, 0, QTableWidgetItem(f"ElasticModel.ThermoMechanical.{param_name}.{sub_name}"))
                            
                            if isinstance(sub_data, dict):
                                self.models_tab.setItem(row, 1, QTableWidgetItem(str(sub_data.get('value', ''))))
                                self.models_tab.setItem(row, 2, QTableWidgetItem(sub_data.get('unit', '')))
                                self.models_tab.setItem(row, 3, QTableWidgetItem(str(sub_data.get('ref', ''))))
                            else:
                                self.models_tab.setItem(row, 1, QTableWidgetItem(str(sub_data)))
                            
                            row += 1
    
    def _load_elastoplastic(self, model_data, start_row):
        """Load ElastoPlastic model data."""
        row = start_row
        
        for param_name, param_value in model_data.items():
            if isinstance(param_value, list):
                # Direct parameters (ShearModulus, YieldStrength)
                for entry in param_value:
                    self.models_tab.insertRow(row)
                    self.models_tab.setItem(row, 0, QTableWidgetItem(f"ElastoPlastic.{param_name}"))
                    self.models_tab.setItem(row, 1, QTableWidgetItem(str(entry.get('value', ''))))
                    self.models_tab.setItem(row, 2, QTableWidgetItem(entry.get('unit', '')))
                    
                    ref = entry.get('ref', '')
                    ref_item = QTableWidgetItem(str(ref))
                    
                    # Highlight overrides
                    if ref == "USER_OVERRIDE":
                        color = QColor(255, 215, 0, 50)
                        for col in range(4):
                            item = self.models_tab.item(row, col)
                            if item:
                                item.setBackground(color)
                    
                    self.models_tab.setItem(row, 3, ref_item)
                    row += 1
            
            elif isinstance(param_value, dict) and param_name == "JohnsonCookModelConstants":
                # JohnsonCook parameters
                for sub_name, sub_data in param_value.items():
                    self.models_tab.insertRow(row)
                    self.models_tab.setItem(row, 0, QTableWidgetItem(f"ElastoPlastic.JohnsonCookModelConstants.{sub_name}"))
                    
                    if isinstance(sub_data, dict):
                        self.models_tab.setItem(row, 1, QTableWidgetItem(str(sub_data.get('value', ''))))
                        self.models_tab.setItem(row, 2, QTableWidgetItem(sub_data.get('unit', '')))
                        self.models_tab.setItem(row, 3, QTableWidgetItem(str(sub_data.get('ref', ''))))
                    
                    row += 1
    
    def _load_overrides(self, overrides_list):
        """
        Load overrides into the Overrides tab.
        
        Args:
            overrides_list: List of override dictionaries from list_overrides()
        """
        if not overrides_list:
            # Show message if no overrides
            self.overrides_tab.insertRow(0)
            no_override_item = QTableWidgetItem("No overrides applied to this material")
            no_override_item.setForeground(QColor(150, 150, 150))
            self.overrides_tab.setItem(0, 0, no_override_item)
            self.overrides_tab.setSpan(0, 0, 1, 4)
            return
        
        row = 0
        for override in overrides_list:
            property_path = override.get('property_path', '')
            override_type = override.get('override_type', '')
            override_data = override.get('override_data', {})
            
            self.overrides_tab.insertRow(row)
            
            # Property path
            path_item = QTableWidgetItem(property_path)
            
            if override_type == 'value_override':
                # Value override
                value = override_data.get('value', '')
                unit = override_data.get('unit', '')
                reason = override_data.get('reason', '')
                
                self.overrides_tab.setItem(row, 0, path_item)
                self.overrides_tab.setItem(row, 1, QTableWidgetItem(str(value)))
                self.overrides_tab.setItem(row, 2, QTableWidgetItem(unit))
                self.overrides_tab.setItem(row, 3, QTableWidgetItem(f"Value Override: {reason}" if reason else "Value Override"))
                
            elif override_type == 'reference_preference':
                # Reference preference override
                preferred_ref = override_data.get('preferred_reference', '')
                
                self.overrides_tab.setItem(row, 0, path_item)
                self.overrides_tab.setItem(row, 1, QTableWidgetItem(""))
                self.overrides_tab.setItem(row, 2, QTableWidgetItem(""))
                self.overrides_tab.setItem(row, 3, QTableWidgetItem(f"Preferred Reference: {preferred_ref}"))
            
            # Highlight the entire row in gold
            color = QColor(255, 215, 0, 50)
            for col in range(4):
                item = self.overrides_tab.item(row, col)
                if item:
                    item.setBackground(color)
            
            row += 1
