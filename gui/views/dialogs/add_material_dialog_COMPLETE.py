"""
Add Material Dialog - COMPLETE VERSION

Creates a new material from scratch with full functionality:
- Tab 1: Metadata (Name, Description, Author, etc.) ✅ COMPLETE
- Tab 2: Properties (Categories with values/units/references) ✅ COMPLETE  
- Tab 3: Models (Model types with parameters) ✅ COMPLETE

Design Principle: Build material_data dict → DynamicMaterialInserter.insert_material()
All data flows through existing dynamic insertion system.

Status: FULLY FUNCTIONAL - All tabs implemented
"""

from typing import Dict, List
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QMessageBox, QTabWidget,
    QTextEdit, QWidget, QSpinBox, QDoubleSpinBox, QComboBox,
    QScrollArea, QCheckBox
)
from PyQt6.QtCore import pyqtSignal
from db.database import DatabaseManager
from db.dynamic_insert import DynamicMaterialInserter
from datetime import datetime


class PropertyCategoryGroup(QGroupBox):
    """Widget for one property category with multiple properties."""
    
    def __init__(self, category_name: str, references: Dict, parent=None):
        super().__init__(category_name, parent)
        self.category_name = category_name
        self.references = references
        self.property_widgets = []
        
        self.setCheckable(True)
        self.setChecked(False)
        
        layout = QVBoxLayout()
        
        # Add property button
        add_prop_btn = QPushButton(f"+ Add Property to {category_name}")
        add_prop_btn.clicked.connect(self._add_property)
        layout.addWidget(add_prop_btn)
        
        # Properties container
        self.props_layout = QVBoxLayout()
        layout.addLayout(self.props_layout)
        
        self.setLayout(layout)
    
    def _add_property(self):
        """Add a new property entry."""
        prop_widget = PropertyEntryGroup(self.references, self)
        self.property_widgets.append(prop_widget)
        self.props_layout.addWidget(prop_widget)
    
    def get_properties(self) -> Dict:
        """Get all properties in this category."""
        if not self.isChecked():
            return {}
        
        properties = {}
        for prop_widget in self.property_widgets:
            prop_data = prop_widget.get_property_data()
            if prop_data:
                prop_name, prop_values = prop_data
                if prop_name in properties:
                    properties[prop_name]['entries'].extend(prop_values['entries'])
                else:
                    properties[prop_name] = prop_values
        return properties


class PropertyEntryGroup(QWidget):
    """Widget for one property with name, unit, and multiple values."""
    
    def __init__(self, references: Dict, parent=None):
        super().__init__(parent)
        self.references = references
        self.value_rows = []
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Property name and unit
        header = QHBoxLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Property name (e.g., 'Density', 'Cp')")
        header.addWidget(QLabel("Property:"))
        header.addWidget(self.name_input)
        
        self.unit_input = QLineEdit()
        self.unit_input.setPlaceholderText("Unit (e.g., 'kg/m^3')")
        header.addWidget(QLabel("Unit:"))
        header.addWidget(self.unit_input)
        
        remove_btn = QPushButton("Remove Property")
        remove_btn.clicked.connect(self.deleteLater)
        header.addWidget(remove_btn)
        
        layout.addLayout(header)
        
        # Values container
        self.values_layout = QVBoxLayout()
        layout.addLayout(self.values_layout)
        
        # Add value button
        add_val_btn = QPushButton("+ Add Value")
        add_val_btn.clicked.connect(self._add_value)
        layout.addWidget(add_val_btn)
        
        # Add first value by default
        self._add_value()
        
        self.setLayout(layout)
        self.setStyleSheet("PropertyEntryGroup { border: 1px solid #ccc; padding: 5px; margin: 2px; }")
    
    def _add_value(self):
        """Add a value entry row."""
        row = QWidget()
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        
        value_input = QLineEdit()
        value_input.setPlaceholderText("Value (e.g., '8960' or '1.23E-5')")
        row_layout.addWidget(QLabel("Value:"))
        row_layout.addWidget(value_input)
        
        ref_combo = QComboBox()
        ref_combo.addItem("(No Reference)", None)
        for ref_id, display in self.references.items():
            ref_combo.addItem(display, ref_id)
        row_layout.addWidget(QLabel("Ref:"))
        row_layout.addWidget(ref_combo)
        
        remove_btn = QPushButton("-")
        remove_btn.setMaximumWidth(30)
        remove_btn.clicked.connect(lambda: self._remove_value(row))
        row_layout.addWidget(remove_btn)
        
        row.setLayout(row_layout)
        row.value_input = value_input
        row.ref_combo = ref_combo
        
        self.value_rows.append(row)
        self.values_layout.addWidget(row)
    
    def _remove_value(self, row):
        """Remove a value row."""
        if row in self.value_rows:
            self.value_rows.remove(row)
            row.deleteLater()
    
    def get_property_data(self):
        """Get property name and values."""
        prop_name = self.name_input.text().strip()
        if not prop_name:
            return None
        
        unit = self.unit_input.text().strip() or None
        
        entries = []
        for row in self.value_rows:
            value = row.value_input.text().strip()
            if value:
                ref_id = row.ref_combo.currentData()
                entries.append({
                    'value': value,
                    'ref': str(ref_id) if ref_id else None
                })
        
        if not entries:
            return None
        
        return (prop_name, {'unit': unit, 'entries': entries})


class ModelParameterGroup(QWidget):
    """Widget for model parameters."""
    
    def __init__(self, references: Dict, parent=None):
        super().__init__(parent)
        self.references = references
        self.param_rows = []
        
        layout = QVBoxLayout()
        
        # Add parameter button
        add_btn = QPushButton("+ Add Parameter")
        add_btn.clicked.connect(self._add_parameter)
        layout.addWidget(add_btn)
        
        # Parameters container
        self.params_layout = QVBoxLayout()
        layout.addLayout(self.params_layout)
        
        self.setLayout(layout)
    
    def _add_parameter(self):
        """Add a parameter entry row."""
        row = QWidget()
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        
        name_input = QLineEdit()
        name_input.setPlaceholderText("Parameter name (e.g., 'A', 'B', 'n')")
        row_layout.addWidget(QLabel("Name:"))
        row_layout.addWidget(name_input)
        
        value_input = QLineEdit()
        value_input.setPlaceholderText("Value")
        row_layout.addWidget(QLabel("Value:"))
        row_layout.addWidget(value_input)
        
        unit_input = QLineEdit()
        unit_input.setPlaceholderText("Unit (optional)")
        row_layout.addWidget(QLabel("Unit:"))
        row_layout.addWidget(unit_input)
        
        ref_combo = QComboBox()
        ref_combo.addItem("(No Ref)", None)
        for ref_id, display in self.references.items():
            ref_combo.addItem(display, ref_id)
        row_layout.addWidget(ref_combo)
        
        remove_btn = QPushButton("-")
        remove_btn.setMaximumWidth(30)
        remove_btn.clicked.connect(lambda: self._remove_parameter(row))
        row_layout.addWidget(remove_btn)
        
        row.setLayout(row_layout)
        row.name_input = name_input
        row.value_input = value_input
        row.unit_input = unit_input
        row.ref_combo = ref_combo
        
        self.param_rows.append(row)
        self.params_layout.addWidget(row)
    
    def _remove_parameter(self, row):
        """Remove a parameter row."""
        if row in self.param_rows:
            self.param_rows.remove(row)
            row.deleteLater()
    
    def get_parameters(self) -> List[Dict]:
        """Get all parameters."""
        params = []
        for row in self.param_rows:
            name = row.name_input.text().strip()
            value = row.value_input.text().strip()
            if name and value:
                params.append({
                    'name': name,
                    'value': value,
                    'unit': row.unit_input.text().strip() or None,
                    'ref': row.ref_combo.currentData()
                })
        return params


class AddMaterialDialog(QDialog):
    """Dialog for adding a complete new material to the database."""
    
    material_added = pyqtSignal(int)  # Emits material_id
    
    def __init__(self, db_manager=None, parent=None):
        super().__init__(parent)
        self.db = db_manager if db_manager else DatabaseManager()
        self.references = {}
        self.property_categories = []
        self.model_groups = []
        
        self.setWindowTitle("Add New Material - Complete")
        self.setMinimumWidth(900)
        self.setMinimumHeight(700)
        
        self._load_references()
        self._init_ui()
        
    def _load_references(self):
        """Load references from database."""
        conn = self.db.connect()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT reference_id, author, title FROM "references" ORDER BY reference_id')
            for ref_id, author, title in cursor.fetchall():
                display = f"{ref_id}: {author or 'Unknown'} - {(title or 'Untitled')[:50]}"
                self.references[ref_id] = display
        except Exception as e:
            print(f"Error loading references: {e}")
        finally:
            conn.close()
    
    def _init_ui(self):
        """Initialize the user interface with tabbed layout."""
        main_layout = QVBoxLayout(self)
        
        # ===== Tab Widget =====
        self.tab_widget = QTabWidget()
        
        # Tab 1: Metadata
        self.metadata_tab = self._create_metadata_tab()
        self.tab_widget.addTab(self.metadata_tab, "1. Metadata")
        
        # Tab 2: Properties  
        self.properties_tab = self._create_properties_tab()
        self.tab_widget.addTab(self.properties_tab, "2. Properties")
        
        # Tab 3: Models
        self.models_tab = self._create_models_tab()
        self.tab_widget.addTab(self.models_tab, "3. Models")
        
        main_layout.addWidget(self.tab_widget)
        
        # ===== Action Buttons =====
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_btn = QPushButton("Create Complete Material")
        self.save_btn.clicked.connect(self._on_save)
        self.save_btn.setDefault(True)
        button_layout.addWidget(self.save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(button_layout)
        
        # Info label
        info_label = QLabel("* Tab through all sections | All fields except Material Name are optional")
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        main_layout.addWidget(info_label)
    
    def _create_metadata_tab(self) -> QWidget:
        """Create Tab 1: Metadata input section."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Basic Information
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout()
        
        self.material_id_input = QLineEdit()
        self.material_id_input.setReadOnly(True)
        self.material_id_input.setStyleSheet("background-color: #f0f0f0;")
        basic_layout.addRow("Material ID:", self.material_id_input)
        
        self.material_name_input = QLineEdit()
        self.material_name_input.setPlaceholderText("e.g., 'Titanium Alloy Ti-6Al-4V'")
        self.material_name_input.textChanged.connect(self._on_name_changed)
        basic_layout.addRow("Material Name*:", self.material_name_input)
        
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Optional description")
        self.description_input.setMaximumHeight(80)
        basic_layout.addRow("Description:", self.description_input)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # Metadata
        metadata_group = QGroupBox("Metadata (Optional)")
        metadata_layout = QFormLayout()
        
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Your name or organization")
        metadata_layout.addRow("Author:", self.author_input)
        
        self.date_input = QLineEdit()
        self.date_input.setText(datetime.now().strftime("%Y-%m-%d"))
        metadata_layout.addRow("Date:", self.date_input)
        
        self.version_input = QLineEdit()
        self.version_input.setText("1.0.0")
        metadata_layout.addRow("Version:", self.version_input)
        
        self.version_meaning_input = QLineEdit()
        metadata_layout.addRow("Version Meaning:", self.version_meaning_input)
        
        metadata_group.setLayout(metadata_layout)
        layout.addWidget(metadata_group)
        
        # Atomic Properties
        atomic_group = QGroupBox("Atomic/Chemical Properties (Optional)")
        atomic_layout = QFormLayout()
        
        self.atomic_number_input = QSpinBox()
        self.atomic_number_input.setRange(0, 118)
        self.atomic_number_input.setSpecialValueText("N/A")
        atomic_layout.addRow("Atomic Number:", self.atomic_number_input)
        
        self.atomic_mass_input = QDoubleSpinBox()
        self.atomic_mass_input.setRange(0.0, 500.0)
        self.atomic_mass_input.setDecimals(6)
        self.atomic_mass_input.setSuffix(" g/mol")
        self.atomic_mass_input.setSpecialValueText("N/A")
        atomic_layout.addRow("Atomic Mass:", self.atomic_mass_input)
        
        atomic_group.setLayout(atomic_layout)
        layout.addWidget(atomic_group)
        
        layout.addStretch()
        return tab
    
    def _create_properties_tab(self) -> QWidget:
        """Create Tab 2: Properties section."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        info = QLabel("Add property categories (Thermal, Mechanical, Optical, etc.) with their properties")
        info.setStyleSheet("color: #0066cc; padding: 5px;")
        layout.addWidget(info)
        
        # Scroll area for categories
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.props_main_layout = QVBoxLayout(scroll_widget)
        
        # Predefined categories
        for cat_name in ["Phase", "Thermal", "Mechanical", "Optical", "Electrical"]:
            cat_group = PropertyCategoryGroup(cat_name, self.references, self)
            self.property_categories.append(cat_group)
            self.props_main_layout.addWidget(cat_group)
        
        # Custom category
        custom_layout = QHBoxLayout()
        self.custom_cat_input = QLineEdit()
        self.custom_cat_input.setPlaceholderText("Custom category name...")
        custom_layout.addWidget(self.custom_cat_input)
        
        add_cat_btn = QPushButton("+ Add Custom Category")
        add_cat_btn.clicked.connect(self._add_custom_category)
        custom_layout.addWidget(add_cat_btn)
        self.props_main_layout.addLayout(custom_layout)
        
        self.props_main_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        return tab
    
    def _create_models_tab(self) -> QWidget:
        """Create Tab 3: Models section."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        info = QLabel("Add model types (ElasticModel, EOSModel, StrengthModel, etc.)")
        info.setStyleSheet("color: #0066cc; padding: 5px;")
        layout.addWidget(info)
        
        # Scroll area for models
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.models_main_layout = QVBoxLayout(scroll_widget)
        
        # Add model button
        add_model_btn = QPushButton("+ Add Model")
        add_model_btn.clicked.connect(self._add_model)
        self.models_main_layout.addWidget(add_model_btn)
        
        self.models_main_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        return tab
    
    def _add_custom_category(self):
        """Add a custom property category."""
        cat_name = self.custom_cat_input.text().strip()
        if not cat_name:
            QMessageBox.warning(self, "Input Required", "Please enter a category name")
            return
        
        cat_group = PropertyCategoryGroup(cat_name, self.references, self)
        cat_group.setChecked(True)
        self.property_categories.append(cat_group)
        
        # Insert before custom input
        insert_pos = self.props_main_layout.count() - 2
        self.props_main_layout.insertWidget(insert_pos, cat_group)
        self.custom_cat_input.clear()
    
    def _add_model(self):
        """Add a model group."""
        model_widget = QGroupBox()
        model_widget.setCheckable(True)
        model_widget.setChecked(True)
        model_layout = QVBoxLayout()
        
        # Model type and name
        header = QHBoxLayout()
        
        type_input = QLineEdit()
        type_input.setPlaceholderText("Model type (e.g., 'ElasticModel', 'EOSModel')")
        header.addWidget(QLabel("Type:"))
        header.addWidget(type_input)
        
        name_input = QLineEdit()
        name_input.setPlaceholderText("Model name (optional)")
        header.addWidget(QLabel("Name:"))
        header.addWidget(name_input)
        
        remove_btn = QPushButton("Remove Model")
        remove_btn.clicked.connect(lambda: self._remove_model(model_widget))
        header.addWidget(remove_btn)
        
        model_layout.addLayout(header)
        
        # Parameters
        params_group = ModelParameterGroup(self.references, self)
        model_layout.addWidget(params_group)
        
        model_widget.setLayout(model_layout)
        model_widget.setTitle("Model Configuration")
        
        # Store references
        model_widget.type_input = type_input
        model_widget.name_input = name_input
        model_widget.params_group = params_group
        
        self.model_groups.append(model_widget)
        insert_pos = self.models_main_layout.count() - 1
        self.models_main_layout.insertWidget(insert_pos, model_widget)
    
    def _remove_model(self, model_widget):
        """Remove a model."""
        if model_widget in self.model_groups:
            self.model_groups.remove(model_widget)
            model_widget.deleteLater()
    
    def _on_name_changed(self, text: str):
        """Auto-generate material ID from name."""
        if text:
            material_id = text.upper().replace(' ', '-')
            material_id = ''.join(c for c in material_id if c.isalnum() or c == '-')
            material_id = f"{material_id}-001"
            self.material_id_input.setText(material_id)
        else:
            self.material_id_input.clear()
    
    def _validate_metadata(self) -> bool:
        """Validate metadata."""
        if not self.material_name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Material Name is required")
            self.tab_widget.setCurrentIndex(0)
            return False
        return True
    
    def _build_material_data(self) -> Dict:
        """Build complete material_data dictionary."""
        # Metadata
        metadata = {
            'id': self.material_id_input.text().strip(),
            'name': self.material_name_input.text().strip(),
            'author': self.author_input.text().strip() or None,
            'date': self.date_input.text().strip() or None,
            'version': self.version_input.text().strip() or None,
            'version_meaning': self.version_meaning_input.text().strip() or None
        }
        
        # Properties
        properties = {}
        for cat_group in self.property_categories:
            cat_props = cat_group.get_properties()
            if cat_props:
                properties[cat_group.category_name] = cat_props
        
        # Add atomic properties to Phase
        atomic_num = self.atomic_number_input.value()
        atomic_mass = self.atomic_mass_input.value()
        if atomic_num > 0 or atomic_mass > 0:
            if 'Phase' not in properties:
                properties['Phase'] = {}
            if atomic_num > 0:
                properties['Phase']['AtomicNumber'] = {'unit': None, 'entries': [{'value': str(atomic_num), 'ref': None}]}
            if atomic_mass > 0:
                properties['Phase']['AtomicMass'] = {'unit': 'g/mol', 'entries': [{'value': str(atomic_mass), 'ref': None}]}
        
        # Models
        models = {}
        for model_widget in self.model_groups:
            if model_widget.isChecked():
                model_type = model_widget.type_input.text().strip()
                if model_type:
                    params = model_widget.params_group.get_parameters()
                    if params:
                        models[model_type] = {
                            'name': model_widget.name_input.text().strip() or None,
                            'parameters': params
                        }
        
        return {
            'metadata': metadata,
            'properties': properties,
            'models': models
        }
    
    def _on_save(self):
        """Save the complete material."""
        if not self._validate_metadata():
            return
        
        material_data = self._build_material_data()
        material_name = material_data['metadata']['name']
        
        # Show summary
        prop_count = len(material_data['properties'])
        model_count = len(material_data['models'])
        
        reply = QMessageBox.question(
            self,
            "Confirm Creation",
            f"Create material: '{material_name}'?\n\n"
            f"Properties: {prop_count} categories\n"
            f"Models: {model_count} types\n\n"
            f"Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        try:
            inserter = DynamicMaterialInserter(self.db)
            material_id = inserter.insert_material(material_data)
            
            QMessageBox.information(
                self,
                "Success",
                f"✓ Material '{material_name}' created!\n\n"
                f"Material ID: {material_id}\n"
                f"Properties: {prop_count} categories\n"
                f"Models: {model_count} types"
            )
            
            self.material_added.emit(material_id)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create material:\n\n{str(e)}")


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = AddMaterialDialog()
    dialog.show()
    sys.exit(app.exec())
