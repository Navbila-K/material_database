"""
Override Panel

Panel for managing material overrides.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QGroupBox, QFormLayout,
    QComboBox, QMessageBox
)
from PyQt6.QtCore import pyqtSignal


class OverridePanel(QWidget):
    """
    Override management panel.
    
    Signals:
        override_requested: Emitted when user requests an override
        clear_requested: Emitted when user requests to clear an override
    """
    
    override_requested = pyqtSignal(str, str, str, str)  # path, value, unit, reason
    clear_requested = pyqtSignal(str)  # path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_material = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Group box for override controls
        group = QGroupBox("Override Management")
        group_layout = QVBoxLayout()
        
        # Material label
        self.material_label = QLabel("No material selected")
        group_layout.addWidget(self.material_label)
        
        # Form for setting overrides
        form_layout = QFormLayout()
        
        # Property path
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("e.g., properties.Thermal.Cp")
        form_layout.addRow("Property Path:", self.path_input)
        
        # Value
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("e.g., 400")
        form_layout.addRow("Value:", self.value_input)
        
        # Unit
        self.unit_input = QLineEdit()
        self.unit_input.setPlaceholderText("e.g., J/kg/K")
        form_layout.addRow("Unit:", self.unit_input)
        
        # Reason
        self.reason_input = QLineEdit()
        self.reason_input.setPlaceholderText("Optional reason")
        form_layout.addRow("Reason:", self.reason_input)
        
        group_layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.apply_btn = QPushButton("Apply Override")
        self.apply_btn.clicked.connect(self.on_apply_override)
        self.apply_btn.setEnabled(False)
        button_layout.addWidget(self.apply_btn)
        
        self.clear_btn = QPushButton("Clear Override")
        self.clear_btn.setProperty("secondary", True)
        self.clear_btn.clicked.connect(self.on_clear_override)
        self.clear_btn.setEnabled(False)
        button_layout.addWidget(self.clear_btn)
        
        group_layout.addLayout(button_layout)
        
        # Quick override templates
        templates_label = QLabel("Quick Templates:")
        templates_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        group_layout.addWidget(templates_label)
        
        template_layout = QVBoxLayout()
        
        # Property templates
        self.add_template_button(
            template_layout,
            "Thermal.Cp",
            "properties.Thermal.Cp"
        )
        self.add_template_button(
            template_layout,
            "Mechanical.Density",
            "properties.Mechanical.Density"
        )
        self.add_template_button(
            template_layout,
            "ElastoPlastic.ShearModulus",
            "models.ElastoPlastic.ShearModulus"
        )
        
        group_layout.addLayout(template_layout)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        
        # Spacer
        layout.addStretch()
        
        # Help text
        help_text = QLabel(
            "<b>Property Path Formats:</b><br>"
            "• Properties: properties.Category.PropertyName<br>"
            "• Models (direct): models.ModelType.ParameterName<br>"
            "• Models (nested): models.ModelType.SubModel.Parameter"
        )
        help_text.setProperty("class", "help-text")
        help_text.setWordWrap(True)
        layout.addWidget(help_text)
    
    def add_template_button(self, layout, label, path):
        """Add a template button."""
        btn = QPushButton(f"📋 {label}")
        btn.setProperty("secondary", True)
        btn.clicked.connect(lambda: self.path_input.setText(path))
        layout.addWidget(btn)
    
    def set_material(self, material_name):
        """Set current material."""
        self.current_material = material_name
        self.material_label.setText(f"Material: {material_name}")
        self.apply_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)
    
    def on_apply_override(self):
        """Handle apply override button click."""
        if not self.current_material:
            return
        
        path = self.path_input.text().strip()
        value = self.value_input.text().strip()
        unit = self.unit_input.text().strip()
        reason = self.reason_input.text().strip()
        
        if not path or not value:
            QMessageBox.warning(
                self,
                "Input Required",
                "Please provide both property path and value."
            )
            return
        
        # Emit signal to controller
        self.override_requested.emit(path, value, unit, reason)
        
        # Clear inputs
        self.value_input.clear()
        self.unit_input.clear()
        self.reason_input.clear()
    
    def on_clear_override(self):
        """Handle clear override button click."""
        if not self.current_material:
            return
        
        path = self.path_input.text().strip()
        
        if not path:
            QMessageBox.warning(
                self,
                "Input Required",
                "Please provide property path to clear."
            )
            return
        
        # Confirm
        reply = QMessageBox.question(
            self,
            "Confirm Clear",
            f"Clear override for:\n{path}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Emit signal to controller
            self.clear_requested.emit(path)
            self.path_input.clear()
