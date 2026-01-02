"""
Dynamic Input Widgets for Material Database GUI

Reusable PyQt6 components for building dynamic forms that adapt to
any material structure without hardcoded schemas.

Design Principles:
- All dropdowns populated from database queries
- Support NULL values for optional fields
- Emit signals for data changes
- Validation built-in
- Clean, consistent UI matching existing GUI style
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLineEdit, QComboBox, QPushButton, QLabel, QScrollArea,
    QSpinBox, QDoubleSpinBox, QCheckBox, QTextEdit, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt
from typing import Dict, List, Optional, Any


class PropertyEntryWidget(QWidget):
    """
    Widget for a single property entry (value + unit + reference).
    
    Used in property and model parameter forms.
    Emits signals when data changes.
    """
    
    entry_changed = pyqtSignal()
    remove_requested = pyqtSignal(object)  # Emits self
    
    def __init__(self, references: List[tuple], allow_remove: bool = True, parent=None):
        """
        Initialize property entry widget.
        
        Args:
            references: List of (ref_id, title) tuples from database
            allow_remove: Whether to show remove button
            parent: Parent widget
        """
        super().__init__(parent)
        self.references = references
        self.allow_remove = allow_remove
        self._init_ui()
    
    def _init_ui(self):
        """Initialize user interface."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        
        # Value input
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Value (e.g., 1717, 0.23)")
        self.value_input.textChanged.connect(self.entry_changed)
        layout.addWidget(self.value_input, stretch=2)
        
        # Unit input
        self.unit_input = QLineEdit()
        self.unit_input.setPlaceholderText("Unit (optional)")
        self.unit_input.textChanged.connect(self.entry_changed)
        layout.addWidget(self.unit_input, stretch=1)
        
        # Reference dropdown
        self.ref_combo = QComboBox()
        self.ref_combo.addItem("No Reference", None)
        for ref_id, title in self.references:
            display_text = f"[{ref_id}] {title[:50]}" if len(title) > 50 else f"[{ref_id}] {title}"
            self.ref_combo.addItem(display_text, ref_id)
        self.ref_combo.currentIndexChanged.connect(self.entry_changed)
        layout.addWidget(self.ref_combo, stretch=2)
        
        # Remove button
        if self.allow_remove:
            self.remove_btn = QPushButton("−")
            self.remove_btn.setFixedWidth(30)
            self.remove_btn.setToolTip("Remove this entry")
            self.remove_btn.clicked.connect(lambda: self.remove_requested.emit(self))
            layout.addWidget(self.remove_btn)
    
    def get_data(self) -> Dict[str, Any]:
        """
        Get entry data.
        
        Returns:
            Dictionary with value, unit, ref_id
        """
        return {
            'value': self.value_input.text().strip() or None,
            'unit': self.unit_input.text().strip() or None,
            'ref': self.ref_combo.currentData()
        }
    
    def set_data(self, value: str = "", unit: str = "", ref_id: str = None):
        """Set widget data."""
        self.value_input.setText(value)
        self.unit_input.setText(unit)
        
        # Find and select reference
        if ref_id:
            index = self.ref_combo.findData(ref_id)
            if index >= 0:
                self.ref_combo.setCurrentIndex(index)
    
    def is_empty(self) -> bool:
        """Check if entry is completely empty."""
        data = self.get_data()
        return not any(data.values())
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate entry data.
        
        Returns:
            (is_valid, error_message)
        """
        data = self.get_data()
        
        # Empty entries are valid (will be filtered out)
        if self.is_empty():
            return True, ""
        
        # If has any data, value is required
        if not data['value']:
            return False, "Value is required when unit or reference is specified"
        
        return True, ""


class PropertyGroupWidget(QWidget):
    """
    Widget for a group of property entries (one property, multiple values).
    
    Example: Density with multiple entries from different references.
    """
    
    data_changed = pyqtSignal()
    
    def __init__(self, property_name: str, references: List[tuple], parent=None):
        """
        Initialize property group widget.
        
        Args:
            property_name: Name of the property (e.g., "Density")
            references: List of (ref_id, title) tuples
            parent: Parent widget
        """
        super().__init__(parent)
        self.property_name = property_name
        self.references = references
        self.entry_widgets = []
        self._init_ui()
    
    def _init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header_layout = QHBoxLayout()
        
        label = QLabel(self.property_name)
        label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(label)
        
        header_layout.addStretch()
        
        # Add entry button
        add_btn = QPushButton("+ Add Entry")
        add_btn.clicked.connect(self._add_entry)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Entries container
        self.entries_layout = QVBoxLayout()
        layout.addLayout(self.entries_layout)
        
        # Add first entry by default
        self._add_entry()
    
    def _add_entry(self):
        """Add a new entry widget."""
        entry = PropertyEntryWidget(self.references, allow_remove=len(self.entry_widgets) > 0)
        entry.entry_changed.connect(self.data_changed)
        entry.remove_requested.connect(self._remove_entry)
        
        self.entry_widgets.append(entry)
        self.entries_layout.addWidget(entry)
        self.data_changed.emit()
    
    def _remove_entry(self, widget: PropertyEntryWidget):
        """Remove an entry widget."""
        if len(self.entry_widgets) > 1:
            self.entry_widgets.remove(widget)
            widget.deleteLater()
            self.data_changed.emit()
    
    def get_data(self) -> Dict[str, Any]:
        """
        Get all entries for this property.
        
        Returns:
            Dictionary with unit and entries list
        """
        entries = []
        unit = None
        
        for idx, widget in enumerate(self.entry_widgets):
            if not widget.is_empty():
                data = widget.get_data()
                data['index'] = idx + 1
                entries.append(data)
                
                # Take first non-empty unit
                if not unit and data.get('unit'):
                    unit = data['unit']
        
        return {
            'unit': unit,
            'entries': entries
        }
    
    def validate(self) -> tuple[bool, str]:
        """Validate all entries."""
        for widget in self.entry_widgets:
            valid, error = widget.validate()
            if not valid:
                return False, f"{self.property_name}: {error}"
        
        # At least one non-empty entry required
        data = self.get_data()
        if not data['entries']:
            return False, f"{self.property_name}: At least one entry is required"
        
        return True, ""


class PropertyCategoryWidget(QGroupBox):
    """
    Collapsible widget for a property category (e.g., Thermal, Mechanical).
    
    Contains multiple PropertyGroupWidgets.
    """
    
    data_changed = pyqtSignal()
    remove_requested = pyqtSignal(object)
    
    def __init__(self, category_name: str, references: List[tuple], 
                 is_custom: bool = False, parent=None):
        """
        Initialize property category widget.
        
        Args:
            category_name: Category name (e.g., "Thermal")
            references: List of (ref_id, title) tuples
            is_custom: Whether this is a user-defined category
            parent: Parent widget
        """
        super().__init__(category_name, parent)
        self.category_name = category_name
        self.references = references
        self.is_custom = is_custom
        self.property_widgets = {}
        
        self.setCheckable(True)
        self.setChecked(True)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)
        
        # Add property button
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("+ Add Property")
        add_btn.clicked.connect(self._show_add_property_dialog)
        btn_layout.addWidget(add_btn)
        
        if self.is_custom:
            remove_btn = QPushButton("Remove Category")
            remove_btn.clicked.connect(lambda: self.remove_requested.emit(self))
            btn_layout.addWidget(remove_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Properties container (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(300)
        
        scroll_content = QWidget()
        self.properties_layout = QVBoxLayout(scroll_content)
        self.properties_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
    
    def _show_add_property_dialog(self):
        """Show dialog to add a new property."""
        from PyQt6.QtWidgets import QInputDialog
        
        property_name, ok = QInputDialog.getText(
            self,
            "Add Property",
            f"Enter property name for {self.category_name}:",
            QLineEdit.EchoMode.Normal
        )
        
        if ok and property_name.strip():
            self.add_property(property_name.strip())
    
    def add_property(self, property_name: str):
        """Add a property to this category."""
        if property_name in self.property_widgets:
            QMessageBox.warning(
                self,
                "Duplicate Property",
                f"Property '{property_name}' already exists in {self.category_name}"
            )
            return
        
        widget = PropertyGroupWidget(property_name, self.references)
        widget.data_changed.connect(self.data_changed)
        
        self.property_widgets[property_name] = widget
        self.properties_layout.insertWidget(len(self.property_widgets) - 1, widget)
        self.data_changed.emit()
    
    def get_data(self) -> Dict[str, Any]:
        """Get all properties in this category."""
        if not self.isChecked():
            return {}
        
        data = {}
        for name, widget in self.property_widgets.items():
            prop_data = widget.get_data()
            if prop_data['entries']:  # Only include non-empty properties
                data[name] = prop_data
        
        return data
    
    def validate(self) -> tuple[bool, str]:
        """Validate all properties in category."""
        if not self.isChecked():
            return True, ""
        
        for widget in self.property_widgets.values():
            valid, error = widget.validate()
            if not valid:
                return False, f"{self.category_name}: {error}"
        
        return True, ""


class ModelParameterWidget(QWidget):
    """
    Widget for model parameters (similar to PropertyGroupWidget but for models).
    """
    
    data_changed = pyqtSignal()
    
    def __init__(self, param_name: str, references: List[tuple], parent=None):
        """Initialize model parameter widget."""
        super().__init__(parent)
        self.param_name = param_name
        self.references = references
        self.entry_widgets = []
        self._init_ui()
    
    def _init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header_layout = QHBoxLayout()
        label = QLabel(self.param_name)
        header_layout.addWidget(label)
        header_layout.addStretch()
        
        add_btn = QPushButton("+ Entry")
        add_btn.clicked.connect(self._add_entry)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Entries
        self.entries_layout = QVBoxLayout()
        layout.addLayout(self.entries_layout)
        
        # Add first entry
        self._add_entry()
    
    def _add_entry(self):
        """Add entry widget."""
        entry = PropertyEntryWidget(self.references, allow_remove=len(self.entry_widgets) > 0)
        entry.entry_changed.connect(self.data_changed)
        entry.remove_requested.connect(self._remove_entry)
        
        self.entry_widgets.append(entry)
        self.entries_layout.addWidget(entry)
        self.data_changed.emit()
    
    def _remove_entry(self, widget: PropertyEntryWidget):
        """Remove entry widget."""
        if len(self.entry_widgets) > 1:
            self.entry_widgets.remove(widget)
            widget.deleteLater()
            self.data_changed.emit()
    
    def get_data(self) -> List[Dict[str, Any]]:
        """Get all entries as list."""
        entries = []
        for idx, widget in enumerate(self.entry_widgets):
            if not widget.is_empty():
                data = widget.get_data()
                data['index'] = idx + 1
                entries.append(data)
        return entries
    
    def validate(self) -> tuple[bool, str]:
        """Validate entries."""
        for widget in self.entry_widgets:
            valid, error = widget.validate()
            if not valid:
                return False, f"{self.param_name}: {error}"
        
        data = self.get_data()
        if not data:
            return False, f"{self.param_name}: At least one entry is required"
        
        return True, ""


# Export all widgets
__all__ = [
    'PropertyEntryWidget',
    'PropertyGroupWidget',
    'PropertyCategoryWidget',
    'ModelParameterWidget',
]
