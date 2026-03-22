"""
Dynamic Data Panel - Auto-generates tree from available data

This panel automatically builds a tree structure showing:
- Experimental data (by category)
- Model data (by category)
- Calibration ranges

The structure adapts based on what data is actually available.
"""

from typing import Dict, List, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLabel, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from .data_types import DataTypeRegistry


class DynamicDataPanel(QWidget):
    """
    Dynamic data panel that builds tree from available data types
    
    Signals:
        data_selected: Emitted when user clicks a data item
    """
    
    data_selected = pyqtSignal(str, str, str)  # (material, category, data_type)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.current_materials = []
        self.tree_items = {}  # Cache tree items
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Header
        header = QLabel("📊 Data Sources")
        header.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50; padding: 5px;")
        layout.addWidget(header)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)
        
        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QTreeWidget::item:hover {
                background-color: #e8f4f8;
            }
            QTreeWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        self.tree.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.tree)
        
        # Info label
        self.info_label = QLabel("Select materials to view data")
        self.info_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 5px;")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
    
    def set_materials(self, materials: List[str]):
        """
        Set materials to display
        
        Args:
            materials: List of material names
        """
        self.current_materials = materials
        self.rebuild_tree()
    
    def rebuild_tree(self):
        """Rebuild entire tree based on current materials"""
        self.tree.clear()
        self.tree_items.clear()
        
        if not self.current_materials:
            self.info_label.setText("No materials selected")
            return
        
        # Update info
        count = len(self.current_materials)
        self.info_label.setText(f"Showing data for {count} material(s)")
        
        # Build tree for each material
        for material in self.current_materials:
            self._add_material_node(material)
        
        # Expand all
        self.tree.expandAll()
    
    def _add_material_node(self, material: str):
        """Add a material node with all its data"""
        
        # Get available data for this material
        available_data = DataTypeRegistry.get_available_for_material(material)
        
        if not available_data:
            # No data available
            item = QTreeWidgetItem([f"📦 {material} (No data)"])
            item.setForeground(0, Qt.GlobalColor.gray)
            self.tree.addTopLevelItem(item)
            return
        
        # Create material root node
        total_items = sum(len(types) for types in available_data.values())
        material_item = QTreeWidgetItem([f"📦 {material} ({total_items} datasets)"])
        material_item.setFont(0, QFont('Arial', 10, QFont.Weight.Bold))
        self.tree.addTopLevelItem(material_item)
        
        # Add categories
        for category in sorted(available_data.keys()):
            data_types = available_data[category]
            
            # Category node
            category_icon = self._get_category_icon(category)
            category_item = QTreeWidgetItem([f"{category_icon} {category.title()} ({len(data_types)})"])
            category_item.setFont(0, QFont('Arial', 9, QFont.Weight.Bold))
            material_item.addChild(category_item)
            
            # Add each data type
            for data_type in data_types:
                data_item = QTreeWidgetItem([f"  • {data_type.name}"])
                
                # Store metadata
                data_item.setData(0, Qt.ItemDataRole.UserRole, {
                    'material': material,
                    'category': category,
                    'data_type': data_type.name,
                    'instance': data_type
                })
                
                # Get summary
                try:
                    summary = data_type.get_summary(material)
                    data_item.setToolTip(0, summary)
                except Exception as e:
                    print(f"[DataPanel] Error getting summary: {e}")
                
                category_item.addChild(data_item)
                
                # Try to get and add display widget
                try:
                    widget = data_type.get_display_widget(material)
                    if widget:
                        # Add widget as child (for future expansion)
                        # For now, just show text
                        pass
                except Exception as e:
                    print(f"[DataPanel] Error getting widget: {e}")
    
    def _get_category_icon(self, category: str) -> str:
        """Get icon for category"""
        icons = {
            'experimental': '📊',
            'model': '📐',
            'calibration': '📏',
            'simulation': '🔬'
        }
        return icons.get(category.lower(), '📁')
    
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle tree item click"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        
        if data and isinstance(data, dict):
            material = data['material']
            category = data['category']
            data_type = data['data_type']
            
            print(f"[DataPanel] Selected: {material} / {category} / {data_type}")
            self.data_selected.emit(material, category, data_type)
    
    def get_selected_data(self) -> Optional[Dict]:
        """Get currently selected data item"""
        current = self.tree.currentItem()
        if current:
            return current.data(0, Qt.ItemDataRole.UserRole)
        return None
    
    def highlight_material(self, material: str):
        """Highlight a specific material in the tree"""
        # Find and select material node
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if material in item.text(0):
                self.tree.setCurrentItem(item)
                break
    
    def clear(self):
        """Clear the panel"""
        self.tree.clear()
        self.tree_items.clear()
        self.current_materials.clear()
        self.info_label.setText("Select materials to view data")
