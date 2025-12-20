"""
Reference Viewer Widget

Displays references used by a material in a professional table format.
Part of the 4-tab PropertyViewer architecture.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QLabel, QPushButton, QHeaderView,
    QMessageBox, QFileDialog, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QDrag, QCursor


class ReferenceViewer(QWidget):
    """
    Widget to display references used by a material.
    
    Features:
    - Table with ID, Type, Author, Year, Title, Journal
    - Double-click to view full details
    - Export citations functionality
    - Sort by any column
    """
    
    # Signal emitted when user wants to see which properties use a reference
    reference_selected = pyqtSignal(int)  # reference_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_material = None
        self.reference_data = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header with count
        header_layout = QHBoxLayout()
        self.count_label = QLabel("No references")
        self.count_label.setProperty("subheading", True)
        header_layout.addWidget(self.count_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Table widget (will expand to fill available space)
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Type", "Author", "Year", "Title", "Journal"
        ])
        
        # Configure table
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)       # Author
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Year
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)           # Title
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)       # Journal
        
        # Enable column reordering (drag columns)
        header.setSectionsMovable(True)
        header.setDragEnabled(True)
        header.setDragDropMode(QHeaderView.DragDropMode.InternalMove)
        
        # Enable row resizing - drag row borders to resize height
        vertical_header = self.table.verticalHeader()
        vertical_header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        vertical_header.setDefaultSectionSize(30)  # Default row height
        vertical_header.setMinimumSectionSize(20)  # Minimum row height
        
        # Enable sorting
        self.table.setSortingEnabled(True)
        
        # Read-only
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Enable drag selection
        self.table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        
        # Enable word wrap for better readability when rows are resized
        self.table.setWordWrap(True)
        
        # Double-click for details
        self.table.doubleClicked.connect(self.on_row_double_clicked)
        
        # Add table to layout (it will expand to fill space)
        layout.addWidget(self.table, 1)  # stretch factor = 1
        
        # Action buttons (fixed at bottom, always visible)
        button_layout = QHBoxLayout()
        
        self.view_details_btn = QPushButton("View Details")
        self.view_details_btn.setEnabled(False)
        self.view_details_btn.clicked.connect(self.on_view_details)
        button_layout.addWidget(self.view_details_btn)
        
        self.export_btn = QPushButton("Export as XML")
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self.on_export_citations)
        button_layout.addWidget(self.export_btn)
        
        button_layout.addStretch()
        
        # Add button layout (fixed size, always visible)
        layout.addLayout(button_layout, 0)  # stretch factor = 0 (fixed)
        
        # Enable buttons when selection changes
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
    
    def display_references(self, material_name: str, references: list):
        """
        Display references for a material.
        
        Args:
            material_name: Name of the material
            references: List of reference dictionaries from ReferenceQuerier
        """
        self.current_material = material_name
        self.reference_data = references
        
        # Update count label
        count = len(references)
        self.count_label.setText(
            f"REFERENCES FOR {material_name.upper()} ({count} total)"
        )
        
        # Clear existing data
        self.table.setSortingEnabled(False)  # Disable sorting while populating
        self.table.setRowCount(0)
        
        if not references:
            self.export_btn.setEnabled(False)
            self.table.setSortingEnabled(True)
            return
        
        # Populate table
        for ref in references:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            
            # ID
            id_item = QTableWidgetItem(str(ref.get('reference_id', '')))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_position, 0, id_item)
            
            # Type
            ref_type = ref.get('ref_type', '')
            type_item = QTableWidgetItem(ref_type)
            type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Color-code by type
            if ref_type == 'article':
                type_item.setBackground(QColor(230, 245, 255))  # Light blue
            elif ref_type == 'conference':
                type_item.setBackground(QColor(255, 245, 230))  # Light orange
            elif ref_type == 'report':
                type_item.setBackground(QColor(245, 255, 230))  # Light green
            elif ref_type == 'misc':
                type_item.setBackground(QColor(245, 245, 245))  # Light gray
            
            self.table.setItem(row_position, 1, type_item)
            
            # Author
            author = ref.get('author', 'Unknown')
            # Truncate if too long
            if len(author) > 40:
                author = author[:37] + '...'
            author_item = QTableWidgetItem(author)
            author_item.setToolTip(ref.get('author', 'Unknown'))  # Full name on hover
            self.table.setItem(row_position, 2, author_item)
            
            # Year
            year_item = QTableWidgetItem(ref.get('year', '--'))
            year_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_position, 3, year_item)
            
            # Title
            title = ref.get('title', 'No title')
            # Truncate if too long
            if len(title) > 60:
                title = title[:57] + '...'
            title_item = QTableWidgetItem(title)
            title_item.setToolTip(ref.get('title', 'No title'))  # Full title on hover
            self.table.setItem(row_position, 4, title_item)
            
            # Journal
            journal = ref.get('journal', '--')
            if journal and len(journal) > 30:
                journal = journal[:27] + '...'
            journal_item = QTableWidgetItem(journal or '--')
            journal_item.setToolTip(ref.get('journal', '--'))
            self.table.setItem(row_position, 5, journal_item)
        
        # Re-enable sorting and sort by ID by default
        self.table.setSortingEnabled(True)
        self.table.sortItems(0, Qt.SortOrder.AscendingOrder)
        
        # Enable export button
        self.export_btn.setEnabled(True)
    
    def clear(self):
        """Clear the reference display."""
        self.current_material = None
        self.reference_data = []
        self.table.setRowCount(0)
        self.count_label.setText("No references")
        self.export_btn.setEnabled(False)
        self.view_details_btn.setEnabled(False)
    
    def on_selection_changed(self):
        """Enable/disable view details button based on selection."""
        has_selection = len(self.table.selectedItems()) > 0
        self.view_details_btn.setEnabled(has_selection)
    
    def on_row_double_clicked(self, index):
        """Handle double-click on a row."""
        self.on_view_details()
    
    def on_view_details(self):
        """Show detailed view of selected reference."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        ref_id = int(self.table.item(row, 0).text())
        
        # Find the reference data
        ref_data = None
        for ref in self.reference_data:
            if ref.get('reference_id') == ref_id:
                ref_data = ref
                break
        
        if not ref_data:
            return
        
        # Create detailed message
        details = f"""
<h3>Reference #{ref_id}</h3>
<table cellspacing='5'>
<tr><td><b>Type:</b></td><td>{ref_data.get('ref_type', '--')}</td></tr>
<tr><td><b>Author:</b></td><td>{ref_data.get('author', 'Unknown')}</td></tr>
<tr><td><b>Title:</b></td><td><i>{ref_data.get('title', 'No title')}</i></td></tr>
<tr><td><b>Journal:</b></td><td>{ref_data.get('journal', '--')}</td></tr>
<tr><td><b>Year:</b></td><td>{ref_data.get('year', '--')}</td></tr>
<tr><td><b>Volume:</b></td><td>{ref_data.get('volume', '--')}</td></tr>
<tr><td><b>Pages:</b></td><td>{ref_data.get('pages', '--')}</td></tr>
</table>
"""
        
        msg = QMessageBox(self)
        msg.setWindowTitle(f"Reference #{ref_id} Details")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(details)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()
    
    def on_export_citations(self):
        """Export references to an XML file."""
        if not self.reference_data or not self.current_material:
            return
        
        # Ask user for file location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export References as XML",
            f"{self.current_material}_references.xml",
            "XML Files (*.xml);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            # Create XML content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write(f'<references material="{self.current_material}" count="{len(self.reference_data)}">\n')
                
                for ref in self.reference_data:
                    f.write('  <reference>\n')
                    f.write(f'    <id>{ref.get("reference_id", "")}</id>\n')
                    f.write(f'    <type>{ref.get("ref_type", "misc")}</type>\n')
                    f.write(f'    <author>{ref.get("author", "Unknown")}</author>\n')
                    f.write(f'    <title>{ref.get("title", "")}</title>\n')
                    
                    if ref.get('journal'):
                        f.write(f'    <journal>{ref.get("journal")}</journal>\n')
                    if ref.get('year') and ref.get('year') != '--':
                        f.write(f'    <year>{ref.get("year")}</year>\n')
                    if ref.get('volume') and ref.get('volume') != '--':
                        f.write(f'    <volume>{ref.get("volume")}</volume>\n')
                    if ref.get('pages') and ref.get('pages') != '--':
                        f.write(f'    <pages>{ref.get("pages")}</pages>\n')
                    
                    f.write('  </reference>\n')
                
                f.write('</references>\n')
            
            QMessageBox.information(
                self,
                "Export Successful",
                f"References exported to XML:\n{file_path}"
            )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export references:\n{str(e)}"
            )
