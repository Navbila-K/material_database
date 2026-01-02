"""
Add Material Dialog - Part 1: Metadata Section

Creates a new material from scratch with tabbed interface:
- Tab 1: Metadata (Name, Description, Author, etc.) - THIS PART
- Tab 2: Properties (Categories with values/units/references) - TODO #8
- Tab 3: Models (Model types with parameters) - TODO #9

Design Principle: Build material_data dict → DynamicMaterialInserter.insert_material()
All data flows through existing dynamic insertion system.

Part 1 Status: Metadata tab complete with validation framework
"""

from typing import Dict
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QMessageBox, QTabWidget,
    QTextEdit, QWidget, QSpinBox, QDoubleSpinBox
)
from PyQt6.QtCore import pyqtSignal
from db.database import DatabaseManager
from db.dynamic_insert import DynamicMaterialInserter
from datetime import datetime


class AddMaterialDialog(QDialog):
    """Dialog for adding a complete new material to the database."""
    
    material_added = pyqtSignal(int)  # Emits material_id
    
    def __init__(self, db_manager=None, parent=None):
        super().__init__(parent)
        self.db = db_manager if db_manager else DatabaseManager()
        
        self.setWindowTitle("Add New Material")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the user interface with tabbed layout."""
        main_layout = QVBoxLayout(self)
        
        # ===== Tab Widget for organizing complex dialog =====
        self.tab_widget = QTabWidget()
        
        # Tab 1: Metadata (THIS PART - TODO #7)
        self.metadata_tab = self._create_metadata_tab()
        self.tab_widget.addTab(self.metadata_tab, "1. Metadata")
        
        # Tab 2: Properties (TODO #8)
        self.properties_tab = self._create_properties_tab_placeholder()
        self.tab_widget.addTab(self.properties_tab, "2. Properties")
        
        # Tab 3: Models (TODO #9)
        self.models_tab = self._create_models_tab_placeholder()
        self.tab_widget.addTab(self.models_tab, "3. Models")
        
        main_layout.addWidget(self.tab_widget)
        
        # ===== Action Buttons =====
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_btn = QPushButton("Create Material")
        self.save_btn.clicked.connect(self._on_save)
        self.save_btn.setDefault(True)
        button_layout.addWidget(self.save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(button_layout)
        
        # Info label
        info_label = QLabel("* Required fields | Tab through sections to build complete material")
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        main_layout.addWidget(info_label)
    
    def _create_metadata_tab(self) -> QWidget:
        """Create Tab 1: Metadata input section."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # ===== Basic Information Group =====
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout()
        
        # Material ID (auto-generated from name)
        self.material_id_input = QLineEdit()
        self.material_id_input.setPlaceholderText("Auto-generated from material name")
        self.material_id_input.setReadOnly(True)
        self.material_id_input.setStyleSheet("background-color: #f0f0f0;")
        basic_layout.addRow("Material ID:", self.material_id_input)
        
        # Material Name (REQUIRED)
        self.material_name_input = QLineEdit()
        self.material_name_input.setPlaceholderText("e.g., 'Titanium Alloy Ti-6Al-4V', 'Polycarbonate'")
        self.material_name_input.textChanged.connect(self._on_name_changed)
        name_label = QLabel("Material Name*:")
        name_label.setStyleSheet("font-weight: bold;")
        basic_layout.addRow(name_label, self.material_name_input)
        
        # Description (optional)
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText(
            "Enter material description (optional):\n"
            "- Physical properties\n"
            "- Common applications\n"
            "- Manufacturing notes\n"
            "- Composition details"
        )
        self.description_input.setMaximumHeight(100)
        basic_layout.addRow("Description:", self.description_input)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # ===== Metadata Fields Group =====
        metadata_group = QGroupBox("Metadata (Optional)")
        metadata_layout = QFormLayout()
        
        # Author
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Your name or organization")
        metadata_layout.addRow("Author:", self.author_input)
        
        # Date (auto-filled with today)
        self.date_input = QLineEdit()
        self.date_input.setText(datetime.now().strftime("%Y-%m-%d"))
        self.date_input.setPlaceholderText("YYYY-MM-DD")
        metadata_layout.addRow("Date:", self.date_input)
        
        # Version
        self.version_input = QLineEdit()
        self.version_input.setPlaceholderText("e.g., '1.0.0' or '0.0.1-ALPHA'")
        self.version_input.setText("1.0.0")
        metadata_layout.addRow("Version:", self.version_input)
        
        # Version Meaning
        self.version_meaning_input = QLineEdit()
        self.version_meaning_input.setPlaceholderText("e.g., 'Initial release', 'schema_version'")
        metadata_layout.addRow("Version Meaning:", self.version_meaning_input)
        
        metadata_group.setLayout(metadata_layout)
        layout.addWidget(metadata_group)
        
        # ===== Atomic/Chemical Properties (Optional) =====
        atomic_group = QGroupBox("Atomic/Chemical Properties (Optional)")
        atomic_layout = QFormLayout()
        
        # Atomic Number
        self.atomic_number_input = QSpinBox()
        self.atomic_number_input.setRange(0, 118)
        self.atomic_number_input.setValue(0)
        self.atomic_number_input.setSpecialValueText("N/A (compound/alloy)")
        atomic_layout.addRow("Atomic Number:", self.atomic_number_input)
        
        # Atomic Mass
        self.atomic_mass_input = QDoubleSpinBox()
        self.atomic_mass_input.setRange(0.0, 500.0)
        self.atomic_mass_input.setDecimals(6)
        self.atomic_mass_input.setValue(0.0)
        self.atomic_mass_input.setSuffix(" g/mol")
        self.atomic_mass_input.setSpecialValueText("N/A")
        atomic_layout.addRow("Atomic Mass:", self.atomic_mass_input)
        
        atomic_group.setLayout(atomic_layout)
        layout.addWidget(atomic_group)
        
        # Info note
        info = QLabel(
            "ℹ️ Note: Material Name is required. All other fields are optional.\n"
            "   Properties and Models can be added in the next tabs."
        )
        info.setStyleSheet("color: #0066cc; background-color: #e6f2ff; padding: 8px; border-radius: 4px;")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        layout.addStretch()
        return tab
    
    def _create_properties_tab_placeholder(self) -> QWidget:
        """Create Tab 2: Properties section (TODO #8)."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        label = QLabel("Properties Section - Coming in TODO #8")
        label.setStyleSheet("font-size: 14px; color: gray; font-style: italic;")
        layout.addWidget(label)
        
        note = QLabel(
            "This tab will allow you to:\n"
            "• Add property categories (Thermal, Mechanical, Optical, etc.)\n"
            "• Define properties with values, units, and references\n"
            "• Support multiple values per property\n\n"
            "For now, you can create a material with metadata only,\n"
            "then use 'Add Property' dialog to add properties later."
        )
        note.setStyleSheet("color: #666; padding: 20px;")
        layout.addWidget(note)
        layout.addStretch()
        
        return tab
    
    def _create_models_tab_placeholder(self) -> QWidget:
        """Create Tab 3: Models section (TODO #9)."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        label = QLabel("Models Section - Coming in TODO #9")
        label.setStyleSheet("font-size: 14px; color: gray; font-style: italic;")
        layout.addWidget(label)
        
        note = QLabel(
            "This tab will allow you to:\n"
            "• Add model types (ElasticModel, EOSModel, StrengthModel, etc.)\n"
            "• Define model parameters with units and references\n"
            "• Support nested sub-models\n\n"
            "For now, you can create a material with metadata only."
        )
        note.setStyleSheet("color: #666; padding: 20px;")
        layout.addWidget(note)
        layout.addStretch()
        
        return tab
    
    def _on_name_changed(self, text: str):
        """Auto-generate material ID from name."""
        if text:
            # Create ID: uppercase, replace spaces with hyphens
            material_id = text.upper().replace(' ', '-')
            # Remove special characters except hyphens and numbers
            material_id = ''.join(c for c in material_id if c.isalnum() or c == '-')
            # Add suffix
            material_id = f"{material_id}-001"
            self.material_id_input.setText(material_id)
        else:
            self.material_id_input.clear()
    
    def _validate_metadata(self) -> bool:
        """Validate metadata tab inputs."""
        # Material name is required
        if not self.material_name_input.text().strip():
            QMessageBox.warning(
                self,
                "Validation Error",
                "Material Name is required.\n\nPlease enter a name for this material."
            )
            self.tab_widget.setCurrentIndex(0)  # Switch to metadata tab
            self.material_name_input.setFocus()
            return False
        
        # Check for duplicate material name
        material_name = self.material_name_input.text().strip()
        if self._check_duplicate_material(material_name):
            reply = QMessageBox.question(
                self,
                "Duplicate Material",
                f"A material named '{material_name}' already exists.\n\n"
                f"Do you want to create it anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return False
        
        # Validate date format if provided
        date_text = self.date_input.text().strip()
        if date_text:
            try:
                datetime.strptime(date_text, "%Y-%m-%d")
            except ValueError:
                QMessageBox.warning(
                    self,
                    "Validation Error",
                    "Invalid date format. Please use YYYY-MM-DD format."
                )
                self.tab_widget.setCurrentIndex(0)
                self.date_input.setFocus()
                return False
        
        return True
    
    def _check_duplicate_material(self, material_name: str) -> bool:
        """Check if material with this name already exists."""
        conn = self.db.connect()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT COUNT(*) FROM materials WHERE LOWER(name) = LOWER(%s)',
                (material_name,)
            )
            count = cursor.fetchone()[0]
            return count > 0
        except Exception:
            return False
        finally:
            conn.close()
    
    def _build_material_data(self) -> Dict:
        """Build material_data dictionary for DynamicMaterialInserter."""
        # Get metadata values
        material_id = self.material_id_input.text().strip()
        material_name = self.material_name_input.text().strip()
        description = self.description_input.toPlainText().strip() or None
        author = self.author_input.text().strip() or None
        date = self.date_input.text().strip() or None
        version = self.version_input.text().strip() or None
        version_meaning = self.version_meaning_input.text().strip() or None
        
        # Build metadata dict
        metadata = {
            'id': material_id,
            'name': material_name,
            'author': author,
            'date': date,
            'version': version,
            'version_meaning': version_meaning
        }
        
        # Start building material_data
        material_data = {
            'metadata': metadata,
            'properties': {},  # TODO #8: Will be populated from properties tab
            'models': {}       # TODO #9: Will be populated from models tab
        }
        
        # Store atomic properties as Phase properties (optional)
        atomic_num = self.atomic_number_input.value()
        atomic_mass = self.atomic_mass_input.value()
        
        if atomic_num > 0 or atomic_mass > 0:
            phase_props = {}
            if atomic_num > 0:
                phase_props['AtomicNumber'] = str(atomic_num)
            if atomic_mass > 0:
                phase_props['AtomicMass'] = str(atomic_mass)
            if description:
                phase_props['Description'] = description
            
            material_data['properties']['Phase'] = phase_props
        
        return material_data
    
    def _on_save(self):
        """Save the material to database."""
        # Validate metadata
        if not self._validate_metadata():
            return
        
        # Build material data
        material_data = self._build_material_data()
        material_name = material_data['metadata']['name']
        
        # Confirm creation
        reply = QMessageBox.question(
            self,
            "Confirm Material Creation",
            f"Create new material: '{material_name}'?\n\n"
            f"Note: Properties and models tabs are not yet implemented.\n"
            f"You can add properties later using 'Add Property' dialog.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        # Insert into database
        try:
            inserter = DynamicMaterialInserter(self.db)
            material_id = inserter.insert_material(material_data)
            
            QMessageBox.information(
                self,
                "Success",
                f"✓ Material '{material_name}' created successfully!\n\n"
                f"Material ID: {material_id}\n\n"
                f"You can now:\n"
                f"• Add properties using 'Data → Add Property'\n"
                f"• View the material in Material Browser\n"
                f"• Add overrides if needed"
            )
            
            # Emit signal with material_id
            self.material_added.emit(material_id)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Database Error",
                f"Error creating material:\n\n{str(e)}"
            )


# For standalone testing
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = AddMaterialDialog()
    dialog.show()
    sys.exit(app.exec())
