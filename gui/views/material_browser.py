"""
Material Browser View

Tree widget for browsing materials by category.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLineEdit, QLabel
)
from PyQt6.QtCore import pyqtSignal, Qt


class MaterialBrowser(QWidget):
    """
    Material browser with tree view and search.
    
    Signals:
        material_selected: Emitted when user selects a material
    """
    
    material_selected = pyqtSignal(str)  # material_name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Materials")
        title.setProperty("heading", True)
        layout.addWidget(title)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search materials...")
        self.search_box.textChanged.connect(self.on_search)
        layout.addWidget(self.search_box)
        
        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.tree)
        
        # Stats label
        self.stats_label = QLabel("")
        layout.addWidget(self.stats_label)
    
    def load_materials(self, materials):
        """
        Load materials into tree view.
        
        Args:
            materials: List of material dictionaries with 'name' key
        """
        self.tree.clear()
        self.all_materials = materials
        
        # Extract material names from dictionaries
        material_names = [m['name'] if isinstance(m, dict) else m for m in materials]
        
        # Categorize materials
        categories = {
            "Metals": [],
            "Explosives": [],
            "Other": []
        }
        
        explosives = ["RDX", "TNT", "HMX", "PETN", "TATB", "CL-20", "HNS", "Nitromethane"]
        metals = ["Aluminum", "Copper", "Magnesium", "Nickel", "Tantalum", "Titanium", "Tungsten"]
        
        for material_name in material_names:
            if material_name in metals:
                categories["Metals"].append(material_name)
            elif material_name in explosives:
                categories["Explosives"].append(material_name)
            else:
                categories["Other"].append(material_name)
        
        # Build tree
        for category, items in categories.items():
            if not items:
                continue
            
            # Category node
            category_item = QTreeWidgetItem(self.tree, [f"{category} ({len(items)})"])
            category_item.setExpanded(True)
            
            # Material nodes
            for material in sorted(items):
                material_item = QTreeWidgetItem(category_item, [material])
                material_item.setData(0, Qt.ItemDataRole.UserRole, material)
        
        # Update stats
        self.stats_label.setText(f"Total: {len(material_names)} materials")
    
    def on_item_clicked(self, item, column):
        """Handle tree item click."""
        material_name = item.data(0, Qt.ItemDataRole.UserRole)
        if material_name:
            self.material_selected.emit(material_name)
    
    def on_search(self, text):
        """Filter materials by search text."""
        if not text:
            # Show all
            for i in range(self.tree.topLevelItemCount()):
                category = self.tree.topLevelItem(i)
                category.setHidden(False)
                for j in range(category.childCount()):
                    category.child(j).setHidden(False)
            return
        
        # Filter
        text = text.lower()
        for i in range(self.tree.topLevelItemCount()):
            category = self.tree.topLevelItem(i)
            category_has_match = False
            
            for j in range(category.childCount()):
                child = category.child(j)
                material_name = child.data(0, Qt.ItemDataRole.UserRole)
                
                if material_name and text in material_name.lower():
                    child.setHidden(False)
                    category_has_match = True
                else:
                    child.setHidden(True)
            
            category.setHidden(not category_has_match)
