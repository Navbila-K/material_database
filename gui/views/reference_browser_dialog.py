"""
Reference Browser Dialog

Standalone dialog to browse ALL references in the database.
Provides search, filter, and detailed view capabilities.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QLabel, QPushButton, QLineEdit,
    QComboBox, QHeaderView, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class ReferenceBrowserDialog(QDialog):
    """
    Dialog to browse all references in the database.
    
    Features:
    - View all 124 references
    - Filter by type (article, conference, report, etc.)
    - Search by author, title, or year
    - View details of any reference
    - See which materials use each reference
    - Export all references
    """
    
    def __init__(self, ref_querier, parent=None):
        super().__init__(parent)
        self.ref_querier = ref_querier
        self.all_references = []
        self.filtered_references = []
        
        self.setWindowTitle("Browse All References")
        self.setGeometry(200, 100, 1200, 700)
        self.init_ui()
        self.load_references()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("📚 REFERENCE DATABASE BROWSER")
        header_label.setProperty("heading", True)
        layout.addWidget(header_label)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        # Search box
        filter_layout.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search by author, title, or year...")
        self.search_box.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.search_box)
        
        # Type filter
        filter_layout.addWidget(QLabel("Type:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems([
            "All Types", "article", "conference", "report", "misc", "chapter", "book"
        ])
        self.type_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.type_filter)
        
        # Reset button
        reset_btn = QPushButton("Reset Filters")
        reset_btn.clicked.connect(self.reset_filters)
        filter_layout.addWidget(reset_btn)
        
        layout.addLayout(filter_layout)
        
        # Count label
        self.count_label = QLabel("Loading...")
        layout.addWidget(self.count_label)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Type", "Author", "Year", "Title", "Journal", "Used By"
        ])
        
        # Configure table
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)       # Author
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Year
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)           # Title
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)       # Journal
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Interactive)       # Used By
        
        # Enable sorting
        self.table.setSortingEnabled(True)
        
        # Read-only
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Double-click for details
        self.table.doubleClicked.connect(self.on_row_double_clicked)
        
        layout.addWidget(self.table)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.view_details_btn = QPushButton("View Details")
        self.view_details_btn.setEnabled(False)
        self.view_details_btn.clicked.connect(self.on_view_details)
        button_layout.addWidget(self.view_details_btn)
        
        self.export_all_btn = QPushButton("Export All as XML")
        self.export_all_btn.clicked.connect(self.on_export_all)
        button_layout.addWidget(self.export_all_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # Enable buttons when selection changes
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
    
    def load_references(self):
        """Load all references from database."""
        try:
            self.all_references = self.ref_querier.list_all_references()
            self.filtered_references = self.all_references.copy()
            self.populate_table()
            self.update_count_label()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Load Error",
                f"Failed to load references:\n{str(e)}"
            )
    
    def populate_table(self):
        """Populate table with filtered references."""
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        
        for ref in self.filtered_references:
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
                type_item.setBackground(QColor(230, 245, 255))
            elif ref_type == 'conference':
                type_item.setBackground(QColor(255, 245, 230))
            elif ref_type == 'report':
                type_item.setBackground(QColor(245, 255, 230))
            elif ref_type == 'misc':
                type_item.setBackground(QColor(245, 245, 245))
            
            self.table.setItem(row_position, 1, type_item)
            
            # Author
            author = ref.get('author', 'Unknown')
            if len(author) > 30:
                author = author[:27] + '...'
            author_item = QTableWidgetItem(author)
            author_item.setToolTip(ref.get('author', 'Unknown'))
            self.table.setItem(row_position, 2, author_item)
            
            # Year
            year_item = QTableWidgetItem(ref.get('year', '--'))
            year_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_position, 3, year_item)
            
            # Title
            title = ref.get('title', 'No title')
            if len(title) > 50:
                title = title[:47] + '...'
            title_item = QTableWidgetItem(title)
            title_item.setToolTip(ref.get('title', 'No title'))
            self.table.setItem(row_position, 4, title_item)
            
            # Journal
            journal = ref.get('journal', '--')
            if journal and len(journal) > 30:
                journal = journal[:27] + '...'
            journal_item = QTableWidgetItem(journal or '--')
            journal_item.setToolTip(ref.get('journal', '--'))
            self.table.setItem(row_position, 5, journal_item)
            
            # Used By (fetch materials using this reference)
            try:
                materials = self.ref_querier.get_materials_using_reference(ref.get('reference_id'))
                used_by = ', '.join(materials) if materials else '--'
                if len(used_by) > 40:
                    used_by = used_by[:37] + '...'
                used_by_item = QTableWidgetItem(used_by)
                if materials:
                    used_by_item.setToolTip(', '.join(materials))
                    used_by_item.setForeground(QColor(0, 100, 0))  # Green for used references
                else:
                    used_by_item.setForeground(QColor(150, 150, 150))  # Gray for unused
                self.table.setItem(row_position, 6, used_by_item)
            except:
                self.table.setItem(row_position, 6, QTableWidgetItem("--"))
        
        self.table.setSortingEnabled(True)
        self.table.sortItems(0, Qt.SortOrder.AscendingOrder)
    
    def apply_filters(self):
        """Apply search and type filters."""
        search_text = self.search_box.text().lower()
        selected_type = self.type_filter.currentText()
        
        self.filtered_references = []
        
        for ref in self.all_references:
            # Type filter
            if selected_type != "All Types" and ref.get('ref_type') != selected_type:
                continue
            
            # Search filter
            if search_text:
                author = ref.get('author', '').lower()
                title = ref.get('title', '').lower()
                year = ref.get('year', '').lower()
                journal = ref.get('journal', '').lower()
                
                if not (search_text in author or search_text in title or 
                        search_text in year or search_text in journal):
                    continue
            
            self.filtered_references.append(ref)
        
        self.populate_table()
        self.update_count_label()
    
    def reset_filters(self):
        """Reset all filters."""
        self.search_box.clear()
        self.type_filter.setCurrentIndex(0)
    
    def update_count_label(self):
        """Update the count label."""
        total = len(self.all_references)
        filtered = len(self.filtered_references)
        
        if filtered == total:
            self.count_label.setText(f"Showing all {total} references")
        else:
            self.count_label.setText(f"Showing {filtered} of {total} references")
    
    def on_selection_changed(self):
        """Enable/disable buttons based on selection."""
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
        for ref in self.all_references:
            if ref.get('reference_id') == ref_id:
                ref_data = ref
                break
        
        if not ref_data:
            return
        
        # Get materials using this reference
        try:
            materials = self.ref_querier.get_materials_using_reference(ref_id)
            materials_str = ', '.join(materials) if materials else 'None'
        except:
            materials_str = 'Unknown'
        
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
<tr><td><b>Used by:</b></td><td>{materials_str}</td></tr>
</table>
"""
        
        msg = QMessageBox(self)
        msg.setWindowTitle(f"Reference #{ref_id} Details")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(details)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()
    
    def on_export_all(self):
        """Export all references to an XML file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export All References as XML",
            "All_References.xml",
            "XML Files (*.xml);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            # Create XML content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write(f'<references database="Materials_DB" count="{len(self.all_references)}">\n')
                
                for ref in self.all_references:
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
                f"All {len(self.all_references)} references exported to XML:\n{file_path}"
            )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export references:\n{str(e)}"
            )
