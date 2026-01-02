"""
GUI Dialogs for Dynamic Data Addition

This package contains dialogs for adding new materials with properties, models,
and references to the database through the GUI interface.

Design Principles:
- Zero modifications to existing business logic
- Use existing DynamicMaterialInserter and database schema
- All dropdowns are query-driven (no hardcoded lists)
- Emit signals for auto-refresh of GUI components
- Support NULL values for optional fields

Components:
- AddMaterialDialog: Create new materials with properties, models, and references
"""

from .add_material_dialog import AddMaterialDialog

__all__ = [
    'AddMaterialDialog',
]

