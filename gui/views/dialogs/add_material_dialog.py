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
    QScrollArea, QCheckBox, QApplication
)
from PyQt6.QtCore import pyqtSignal
from db.database import DatabaseManager
from db.dynamic_insert import DynamicMaterialInserter
from datetime import datetime


class PropertyWidget(QGroupBox):
    """Widget for one property with 10-category dropdown."""
    
    def __init__(self, references: Dict, parent=None):
        super().__init__("Property", parent)
        self.references = references
        self.value_rows = []
        
        layout = QVBoxLayout()
        
        # Category and Subcategory
        cat_layout = QFormLayout()
        
        self.category_combo = QComboBox()
        self.category_combo.addItem("1. Structure and Formulation", "Structure_and_Formulation")
        self.category_combo.addItem("2. Physical Properties", "Physical_Properties")
        self.category_combo.addItem("3. Chemical Properties", "Chemical_Properties")
        self.category_combo.addItem("4. Thermal Properties", "Thermal_Properties")
        self.category_combo.addItem("5. Mechanical Properties", "Mechanical_Properties")
        self.category_combo.addItem("6. Detonation Properties", "Detonation_Properties")
        self.category_combo.addItem("7. Sensitivity", "Sensitivity")
        self.category_combo.addItem("8. Electrical Properties", "Electrical_Properties")
        self.category_combo.addItem("9. Toxicity", "Toxicity")
        self.category_combo.addItem("10. Additional Properties", "Additional_Properties")
        cat_layout.addRow("Category*:", self.category_combo)
        
        self.subcategory_input = QLineEdit()
        self.subcategory_input.setPlaceholderText("Optional subcategory")
        cat_layout.addRow("Subcategory:", self.subcategory_input)
        
        layout.addLayout(cat_layout)
        
        # Property details
        prop_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., 'Density', 'Young Modulus'")
        prop_layout.addRow("Property Name*:", self.name_input)
        
        self.unit_input = QLineEdit()
        self.unit_input.setPlaceholderText("e.g., 'kg/m^3', 'GPa'")
        prop_layout.addRow("Unit:", self.unit_input)
        
        layout.addLayout(prop_layout)
        
        # Values section
        values_group = QGroupBox("Values")
        values_layout = QVBoxLayout()
        
        self.values_container = QVBoxLayout()
        values_layout.addLayout(self.values_container)
        
        add_value_btn = QPushButton("+ Add Value")
        add_value_btn.clicked.connect(self._add_value_row)
        values_layout.addWidget(add_value_btn)
        
        values_group.setLayout(values_layout)
        layout.addWidget(values_group)
        
        # Add first value by default
        self._add_value_row()
        
        # Remove button
        remove_btn = QPushButton("Remove Property")
        remove_btn.clicked.connect(self.deleteLater)
        remove_btn.setStyleSheet("background-color: #ff4444; color: white;")
        layout.addWidget(remove_btn)
        
        self.setLayout(layout)
        self.setStyleSheet("PropertyWidget { border: 2px solid #4CAF50; margin: 5px; padding: 10px; }")
    
    def _add_value_row(self):
        """Add a value entry row."""
        row = QWidget()
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        
        value_input = QLineEdit()
        value_input.setPlaceholderText("Value")
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
        remove_btn.clicked.connect(lambda: self._remove_value_row(row))
        row_layout.addWidget(remove_btn)
        
        row.setLayout(row_layout)
        row.value_input = value_input
        row.ref_combo = ref_combo
        
        self.value_rows.append(row)
        self.values_container.addWidget(row)
    
    def _remove_value_row(self, row):
        """Remove a value row."""
        if len(self.value_rows) > 1:  # Keep at least one
            self.value_rows.remove(row)
            row.deleteLater()
    
    def get_property_data(self) -> Dict:
        """Get property data in format for database."""
        category_id = self.category_combo.currentData()
        subcategory = self.subcategory_input.text().strip() or None
        prop_name = self.name_input.text().strip()
        unit = self.unit_input.text().strip() or None
        
        if not prop_name:
            return None
        
        values = []
        for row in self.value_rows:
            value = row.value_input.text().strip()
            if value:
                ref_id = row.ref_combo.currentData()
                values.append({
                    'value': value,
                    'reference_id': str(ref_id) if ref_id else None  # Changed from 'ref' to 'reference_id'
                })
        
        if not values:
            return None
        
        return {
            'category_id': category_id,
            'subcategory': subcategory,
            'name': prop_name,
            'unit': unit,
            'values': values
        }


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
                    'reference_id': row.ref_combo.currentData()
                })
        return params


class AddMaterialDialog(QDialog):
    """Dialog for adding a complete new material to the database."""
    
    material_added = pyqtSignal(int)  # Emits material_id
    property_added = pyqtSignal(int)  # Emits property_id
    model_added = pyqtSignal(int)  # Emits model_id
    
    def __init__(self, db_manager=None, parent=None, material_id=None):
        super().__init__(parent)
        self.db = db_manager if db_manager else DatabaseManager()
        self.references = {}
        self.property_widgets = []
        self.model_groups = []
        
        # Track if editing existing material or creating new
        self.current_material_id = material_id
        self.current_material_name = None
        self.is_edit_mode = material_id is not None
        
        if self.is_edit_mode:
            self.setWindowTitle("Add to Material")
            self._load_material_data()
        else:
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
        # Note: Don't close connection - it's owned by DatabaseManager
    
    def _load_material_data(self):
        """Load existing material data if in edit mode."""
        if not self.current_material_id:
            return
        
        conn = self.db.connect()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM materials WHERE material_id = %s', (self.current_material_id,))
            row = cursor.fetchone()
            if row:
                self.current_material_name = row[0]
        except Exception as e:
            print(f"Error loading material data: {e}")
    
    def _init_ui(self):
        """Initialize the user interface with tabbed layout and context-aware buttons."""
        main_layout = QVBoxLayout(self)
        
        # Show material info banner if editing existing material
        if self.is_edit_mode:
            info_banner = QLabel(f"📝 Adding to Material: <b>{self.current_material_name or self.current_material_id}</b>")
            info_banner.setStyleSheet(
                "background-color: #e3f2fd; color: #1976d2; padding: 10px; "
                "border-radius: 5px; font-size: 12px; margin-bottom: 5px;"
            )
            main_layout.addWidget(info_banner)
        
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
        
        # Tab 4: References
        self.references_tab = self._create_references_tab()
        self.tab_widget.addTab(self.references_tab, "4. References")
        
        main_layout.addWidget(self.tab_widget)

        # Context-aware action buttons
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch()
        
        # Create Material button (Tab 1)
        self.create_material_btn = QPushButton("Create Material")
        self.create_material_btn.clicked.connect(self._on_save)
        self.create_material_btn.setStyleSheet("font-weight: bold; padding: 8px;")
        self.button_layout.addWidget(self.create_material_btn)
        
        # Add Property button (Tab 2)
        self.add_property_btn = QPushButton("Add Property")
        self.add_property_btn.clicked.connect(self._on_add_property)
        self.add_property_btn.setStyleSheet("font-weight: bold; padding: 8px;")
        self.button_layout.addWidget(self.add_property_btn)
        
        # Add Model button (Tab 3)
        self.add_model_btn = QPushButton("Add Model")
        self.add_model_btn.clicked.connect(self._on_add_model)
        self.add_model_btn.setStyleSheet("font-weight: bold; padding: 8px;")
        self.button_layout.addWidget(self.add_model_btn)
        
        # Add Reference button (Tab 4)
        self.add_reference_btn = QPushButton("Add Reference")
        self.add_reference_btn.clicked.connect(self._on_add_reference)
        self.add_reference_btn.setStyleSheet("font-weight: bold; padding: 8px;")
        self.button_layout.addWidget(self.add_reference_btn)
        
        # Cancel/Close button (always visible)
        close_text = "Close" if self.is_edit_mode else "Cancel"
        self.cancel_btn = QPushButton(close_text)
        self.cancel_btn.clicked.connect(self.reject)
        self.button_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(self.button_layout)

        # Info label
        if self.is_edit_mode:
            info_text = "Add properties, models, or references to the selected material"
        else:
            info_text = "* Material Name is required | Tab through sections to add properties, models, and references"
        
        info_label = QLabel(info_text)
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        main_layout.addWidget(info_label)

        # Connect tab changed signal
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        
        # Initial tab state
        if self.is_edit_mode:
            # If editing, disable metadata tab and start at properties
            self.tab_widget.setTabEnabled(0, False)
            self.tab_widget.setCurrentIndex(1)
        
        self._on_tab_changed(self.tab_widget.currentIndex())

    def _on_tab_changed(self, idx):
        """Update button visibility based on current tab."""
        # Hide all action buttons
        self.create_material_btn.setVisible(False)
        self.add_property_btn.setVisible(False)
        self.add_model_btn.setVisible(False)
        self.add_reference_btn.setVisible(False)
        
        # Show only the relevant button for current tab
        if idx == 0:  # Metadata tab
            self.create_material_btn.setVisible(True)
            self.create_material_btn.setEnabled(not self.is_edit_mode)
        elif idx == 1:  # Properties tab
            self.add_property_btn.setVisible(True)
            self.add_property_btn.setEnabled(self.current_material_id is not None)
        elif idx == 2:  # Models tab
            self.add_model_btn.setVisible(True)
            self.add_model_btn.setEnabled(self.current_material_id is not None)
        elif idx == 3:  # References tab
            self.add_reference_btn.setVisible(True)
            self.add_reference_btn.setEnabled(True)  # References are global

    def _create_references_tab(self) -> QWidget:
        """Create Tab 4: References section."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        info = QLabel("Add new references to the database that can be used with properties and models")
        info.setStyleSheet("color: #0066cc; padding: 5px; background: #e6f2ff; border-radius: 3px;")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Reference form
        form_group = QGroupBox("New Reference")
        form_layout = QFormLayout()
        
        # Type dropdown
        self.ref_type_combo = QComboBox()
        self.ref_type_combo.addItems(['Article', 'Book', 'Report', 'Conference', 'Chapter', 'Misc'])
        self.ref_type_combo.setCurrentIndex(0)  # Default to Article
        form_layout.addRow("Type*:", self.ref_type_combo)
        
        self.ref_author_input = QLineEdit()
        self.ref_author_input.setPlaceholderText("Author name(s)")
        form_layout.addRow("Author*:", self.ref_author_input)
        
        self.ref_title_input = QLineEdit()
        self.ref_title_input.setPlaceholderText("Publication title")
        form_layout.addRow("Title*:", self.ref_title_input)
        
        self.ref_journal_input = QLineEdit()
        self.ref_journal_input.setPlaceholderText("Journal, publisher, or conference name")
        form_layout.addRow("Journal/Publisher:", self.ref_journal_input)
        
        self.ref_year_input = QSpinBox()
        self.ref_year_input.setRange(1800, 2100)
        self.ref_year_input.setValue(datetime.now().year)
        form_layout.addRow("Year*:", self.ref_year_input)
        
        self.ref_volume_input = QLineEdit()
        self.ref_volume_input.setPlaceholderText("Volume number")
        form_layout.addRow("Volume:", self.ref_volume_input)
        
        self.ref_doi_input = QLineEdit()
        self.ref_doi_input.setPlaceholderText("Digital Object Identifier (e.g., 10.1234/abc)")
        form_layout.addRow("DOI:", self.ref_doi_input)
        
        self.ref_url_input = QLineEdit()
        self.ref_url_input.setPlaceholderText("https://...")
        form_layout.addRow("URL:", self.ref_url_input)
        
        self.ref_notes_input = QTextEdit()
        self.ref_notes_input.setPlaceholderText("Additional notes or abstract")
        self.ref_notes_input.setMaximumHeight(80)
        form_layout.addRow("Notes:", self.ref_notes_input)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        layout.addStretch()
        return tab
    
    def _on_add_reference(self):
        """Add a new reference to the database."""
        author = self.ref_author_input.text().strip()
        title = self.ref_title_input.text().strip()
        ref_type = self.ref_type_combo.currentText().lower()  # Convert to lowercase for database
        
        if not author or not title:
            QMessageBox.warning(self, "Validation Error", "Author and Title are required")
            return
        
        conn = self.db.connect()
        if not conn:
            QMessageBox.critical(self, "Error", "Database connection failed")
            return
        
        try:
            cursor = conn.cursor()
            
            # Insert reference with all fields
            cursor.execute("""
                INSERT INTO "references" (ref_type, author, title, journal, year, volume, doi, url, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING reference_id
            """, (
                ref_type,
                author,
                title,
                self.ref_journal_input.text().strip() or None,
                str(self.ref_year_input.value()),
                self.ref_volume_input.text().strip() or None,
                self.ref_doi_input.text().strip() or None,
                self.ref_url_input.text().strip() or None,
                self.ref_notes_input.toPlainText().strip() or None
            ))
            
            ref_id = cursor.fetchone()[0]
            conn.commit()
            
            # Export to References.xml if ID >= 1001 (GUI-created references)
            if ref_id >= 1001:
                try:
                    journal = self.ref_journal_input.text().strip() or None
                    year = str(self.ref_year_input.value())
                    volume = self.ref_volume_input.text().strip() or None
                    doi = self.ref_doi_input.text().strip() or None
                    url = self.ref_url_input.text().strip() or None
                    notes = self.ref_notes_input.toPlainText().strip() or None
                    self._export_reference_to_xml(ref_id, ref_type, author, title, journal, year, volume, doi, url, notes)
                except Exception as e:
                    print(f"Warning: Failed to export reference to XML: {e}")
                    # Don't fail the whole operation if XML export fails
            
            # Reload references
            self._load_references()
            
            QMessageBox.information(
                self,
                "Success",
                f"✓ Reference added!\n\n"
                f"Reference ID: {ref_id}\n"
                f"Type: {ref_type.capitalize()}\n"
                f"Author: {author}\n"
                f"Title: {title}\n\n"
                f"{'✓ Exported to References.xml' if ref_id >= 1001 else '(XML import reference)'}"
            )
            
            # Clear form
            self.ref_type_combo.setCurrentIndex(0)  # Reset to Article
            self.ref_author_input.clear()
            self.ref_title_input.clear()
            self.ref_journal_input.clear()
            self.ref_year_input.setValue(datetime.now().year)
            self.ref_volume_input.clear()
            self.ref_doi_input.clear()
            self.ref_url_input.clear()
            self.ref_notes_input.clear()
            
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Error", f"Failed to add reference:\n\n{str(e)}")

    def _on_add_property(self):
        """Add properties to the current material."""
        if not self.current_material_id:
            QMessageBox.warning(self, "No Material", "Please create a material first (Tab 1)")
            return
        
        # Collect property data from widgets
        properties_data = []
        for prop_widget in self.property_widgets:
            prop_data = prop_widget.get_property_data()
            if prop_data:
                properties_data.append(prop_data)
        
        if not properties_data:
            QMessageBox.warning(self, "No Properties", "Please add at least one property using '+ Add Property' button")
            return
        
        conn = self.db.connect()
        if not conn:
            QMessageBox.critical(self, "Error", "Database connection failed")
            return
        
        try:
            cursor = conn.cursor()
            added_count = 0
            
            for prop_data in properties_data:
                category_type = prop_data['category_id']  # e.g., "Physical_Properties"
                subcategory = prop_data.get('subcategory')
                prop_name = prop_data['name']
                unit = prop_data.get('unit')
                
                # Get or create property_categories entry
                cursor.execute("""
                    SELECT category_id FROM property_categories 
                    WHERE material_id = %s AND category_type = %s
                """, (self.current_material_id, category_type))
                cat_row = cursor.fetchone()
                
                if not cat_row:
                    cursor.execute("""
                        INSERT INTO property_categories (material_id, category_type)
                        VALUES (%s, %s)
                        RETURNING category_id
                    """, (self.current_material_id, category_type))
                    db_cat_id = cursor.fetchone()[0]
                else:
                    db_cat_id = cat_row[0]
                
                # Insert property (subcategory is stored as subcategory_name field in properties table)
                cursor.execute("""
                    INSERT INTO properties (category_id, property_name, unit, subcategory_name)
                    VALUES (%s, %s, %s, %s)
                    RETURNING property_id
                """, (db_cat_id, prop_name, unit, subcategory))
                property_id = cursor.fetchone()[0]
                
                # Insert property entries
                for idx, value_data in enumerate(prop_data['values']):
                    cursor.execute("""
                        INSERT INTO property_entries (property_id, value, ref_id, entry_index)
                        VALUES (%s, %s, %s, %s)
                    """, (property_id, value_data['value'], value_data.get('reference_id'), idx))
                
                added_count += 1
            
            conn.commit()
            
            QMessageBox.information(
                self,
                "Success",
                f"✓ Added {added_count} {'property' if added_count == 1 else 'properties'} to material!\n\n"
                f"Material: {self.current_material_name or self.current_material_id}"
            )
            
            # Clear property widgets after successful addition
            for widget in self.property_widgets:
                widget.deleteLater()
            self.property_widgets.clear()
            
            # Emit signal to refresh main window
            self.property_added.emit(self.current_material_id)
            
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Error", f"Failed to add properties:\n\n{str(e)}")

    def _on_add_model(self):
        """Add models to the current material."""
        print(f"DEBUG: _on_add_model called")
        print(f"DEBUG: current_material_id = {self.current_material_id}")
        print(f"DEBUG: Number of model_groups = {len(self.model_groups)}")
        
        if not self.current_material_id:
            QMessageBox.warning(self, "No Material", "Please create a material first (Tab 1)")
            return
        
        # Collect model data
        models_data = []
        for idx, model_widget in enumerate(self.model_groups):
            print(f"DEBUG: Checking model_widget {idx}, isChecked = {model_widget.isChecked()}")
            if model_widget.isChecked():
                model_type = model_widget.type_input.text().strip()
                print(f"DEBUG: Model type = '{model_type}'")
                if model_type:
                    params = model_widget.params_group.get_parameters()
                    print(f"DEBUG: Got {len(params)} parameters for model {model_type}")
                    print(f"DEBUG: Parameters: {params}")
                    models_data.append({
                        'type': model_type,
                        'name': model_widget.name_input.text().strip() or None,
                        'parameters': params
                    })
        
        print(f"DEBUG: Total models_data collected = {len(models_data)}")
        
        if not models_data:
            QMessageBox.warning(self, "No Models", "Please add at least one model using '+ Add Model' button")
            return
        
        conn = self.db.connect()
        if not conn:
            QMessageBox.critical(self, "Error", "Database connection failed")
            return
        
        try:
            cursor = conn.cursor()
            added_count = 0
            
            for model_data in models_data:
                model_type = model_data['type']
                model_name = model_data['name']
                
                # Insert or get model
                cursor.execute("""
                    SELECT model_id FROM models 
                    WHERE material_id = %s AND model_type = %s
                """, (self.current_material_id, model_type))
                existing_model = cursor.fetchone()
                
                if existing_model:
                    model_id = existing_model[0]
                else:
                    cursor.execute("""
                        INSERT INTO models (material_id, model_type)
                        VALUES (%s, %s)
                        RETURNING model_id
                    """, (self.current_material_id, model_type))
                    model_id = cursor.fetchone()[0]
                
                # Create a sub_model for this model (to hold parameters)
                # Use the model_name if provided, otherwise use generic name
                sub_model_type = model_name or f"{model_type}_params"
                
                cursor.execute("""
                    INSERT INTO sub_models (model_id, sub_model_type)
                    VALUES (%s, %s)
                    RETURNING sub_model_id
                """, (model_id, sub_model_type))
                sub_model_id = cursor.fetchone()[0]
                
                # Insert parameters into model_parameters
                for idx, param in enumerate(model_data['parameters']):
                    cursor.execute("""
                        INSERT INTO model_parameters (sub_model_id, param_name, value, unit, ref_id, entry_index)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        sub_model_id,
                        param['name'],
                        param['value'],
                        param.get('unit'),
                        param.get('reference_id'),
                        idx
                    ))
                    print(f"DEBUG: Inserted parameter '{param['name']}' = '{param['value']}' with ref_id={param.get('reference_id')}")
                
                added_count += 1
                print(f"DEBUG: Successfully added model {model_type}, total added = {added_count}")
            
            conn.commit()
            print(f"DEBUG: Committed {added_count} models to database")
            
            QMessageBox.information(
                self,
                "Success",
                f"✓ Added {added_count} {'model' if added_count == 1 else 'models'} to material!\n\n"
                f"Material: {self.current_material_name or self.current_material_id}"
            )
            
            # Clear model widgets
            for widget in self.model_groups:
                widget.deleteLater()
            self.model_groups.clear()
            
            # Emit signal
            print(f"DEBUG: Emitting model_added signal for material_id={self.current_material_id}")
            self.model_added.emit(self.current_material_id)
            
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Error", f"Failed to add models:\n\n{str(e)}")

    
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
        """Create Tab 2: Properties section with 10-category system."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Info message
        info_label = QLabel(
            "Add properties using the 10-category system. "
            "Each property can have multiple values with references."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #0066cc; padding: 5px; background: #e6f2ff; border-radius: 3px;")
        layout.addWidget(info_label)
        
        # Scroll area for properties
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.properties_layout = QVBoxLayout(scroll_widget)
        
        # Add Property button
        add_prop_btn = QPushButton("+ Add Property")
        add_prop_btn.clicked.connect(self._add_property_entry)
        add_prop_btn.setStyleSheet("font-weight: bold; padding: 8px;")
        layout.addWidget(add_prop_btn)
        
        self.properties_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Store property widgets
        self.property_widgets = []
        
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
    
    def _add_property_entry(self):
        """Add a new property entry widget."""
        prop_widget = PropertyWidget(self.references, self)
        self.property_widgets.append(prop_widget)
        
        # Insert before stretch
        insert_pos = self.properties_layout.count() - 1
        self.properties_layout.insertWidget(insert_pos, prop_widget)
    
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
        
        # Add properties from property widgets (10-category system)
        for prop_widget in self.property_widgets:
            prop_data = prop_widget.get_property_data()
            if prop_data:
                # Group by category_id
                cat_id = prop_data['category_id']
                if cat_id not in properties:
                    properties[cat_id] = {}
                
                # Add property to category
                prop_name = prop_data['name']
                properties[cat_id][prop_name] = {
                    'unit': prop_data['unit'],
                    'subcategory': prop_data['subcategory'],
                    'entries': prop_data['values']
                }
        
        # Add atomic properties to Phase (FIXED: Proper structure for DynamicMaterialInserter)
        atomic_num = self.atomic_number_input.value()
        atomic_mass = self.atomic_mass_input.value()
        if atomic_num > 0 or atomic_mass > 0:
            if 'Phase' not in properties:
                properties['Phase'] = {}
            if atomic_num > 0:
                # Store as simple string value, not nested dict
                properties['Phase']['AtomicNumber'] = str(atomic_num)
            if atomic_mass > 0:
                # Store as simple string value, not nested dict
                properties['Phase']['AtomicMass'] = str(atomic_mass)
        
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
        
        # Disable button during processing
        self.create_material_btn.setEnabled(False)
        QApplication.processEvents()
        
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
            self.create_material_btn.setEnabled(True)
            return
        
        try:
            QApplication.processEvents()  # Keep UI responsive
            
            inserter = DynamicMaterialInserter(self.db)
            material_id = inserter.insert_material(material_data)
            
            # Set current material for adding more properties/models
            self.current_material_id = material_id
            self.current_material_name = material_name
            
            # Update buttons
            self.add_property_btn.setEnabled(True)
            self.add_model_btn.setEnabled(True)
            
            # Emit signal FIRST (before showing message)
            self.material_added.emit(material_id)
            
            msg_box = QMessageBox(
                QMessageBox.Icon.Information,
                "Success",
                f"✓ Material '{material_name}' created!\n\n"
                f"Material ID: {material_id}\n"
                f"Properties: {prop_count} categories\n"
                f"Models: {model_count} types\n\n"
                f"You can now add more properties, models, or references using the tabs.",
                QMessageBox.StandardButton.Ok,
                self
            )
            msg_box.exec()
            
            # Don't close dialog - allow user to add more content
            # Switch to properties tab
            self.tab_widget.setCurrentIndex(1)
            
        except Exception as e:
            self.create_material_btn.setEnabled(True)  # Re-enable button on error
            QMessageBox.critical(self, "Error", f"Failed to create material:\n\n{str(e)}")
    
    def _export_reference_to_xml(self, ref_id, ref_type, author, title, journal, year, volume, doi, url, notes):
        """
        Export new reference to References.xml (append mode).
        Only called for GUI-created references (ID >= 1001).
        """
        import xml.etree.ElementTree as ET
        from xml.dom import minidom
        
        xml_path = 'xml/References.xml'
        
        # Parse existing XML
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Create new reference element
        ref_elem = ET.SubElement(root, 'reference')
        ref_elem.set('id', str(ref_id))
        
        # Add child elements (only add if value exists)
        type_elem = ET.SubElement(ref_elem, 'type')
        type_elem.text = ref_type or 'misc'
        
        author_elem = ET.SubElement(ref_elem, 'author')
        author_elem.text = author or 'Unknown'
        
        title_elem = ET.SubElement(ref_elem, 'title')
        title_elem.text = title or ''
        
        if journal:
            journal_elem = ET.SubElement(ref_elem, 'journal')
            journal_elem.text = journal
        
        if year:
            year_elem = ET.SubElement(ref_elem, 'year')
            year_elem.text = year
        
        if volume:
            volume_elem = ET.SubElement(ref_elem, 'volume')
            volume_elem.text = volume
        
        if doi:
            doi_elem = ET.SubElement(ref_elem, 'doi')
            doi_elem.text = doi
        
        if url:
            url_elem = ET.SubElement(ref_elem, 'url')
            url_elem.text = url
        
        if notes:
            notes_elem = ET.SubElement(ref_elem, 'notes')
            notes_elem.text = notes
        
        # Pretty print and save
        xml_str = ET.tostring(root, encoding='utf-8')
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent='  ', encoding='utf-8')
        
        # Remove extra blank lines
        lines = [line for line in pretty_xml.decode('utf-8').split('\n') if line.strip()]
        pretty_xml = '\n'.join(lines) + '\n'
        
        # Write to file
        with open(xml_path, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        
        print(f"✓ Reference #{ref_id} exported to References.xml")


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = AddMaterialDialog()
    dialog.show()
    sys.exit(app.exec())
