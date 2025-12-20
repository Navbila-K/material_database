# 🎯 VISUALIZATION TAB - COMPARISON FEATURE IMPLEMENTATION PLAN

## Current Status ✅

**What's Working**:
- ✓ All 17 materials loaded from database
- ✓ Properties extracted correctly (cp, cv, density, viscosity)
- ✓ Models available (ElasticModel, ElastoPlastic, ReactionModel, EOSModel)
- ✓ Comparison possible (common properties exist)
- ✓ Data structure correctly parsed
- ✓ Charts render properly

**Diagnostic Results**:
```
Total Materials: 17
Materials can be loaded: YES
Properties can be extracted: YES
Models are available: YES
Comparison possible: YES (2 common properties: cp, density)
```

---

## Missing Feature: Comparison Table View

### What's Missing:
Currently only has:
- Chart visualizations (Line, Bar, Scatter, Area, Pie, Histogram)
- Dashboard with statistics

Needs to add:
- **Comparison Table** showing side-by-side material property values
- Reference IDs for each value
- Units clearly displayed
- Multiple entries per property visible

---

## Implementation Plan

### Option 1: Add Comparison Table as New Tab in Plot Area

**Structure**:
```
Plot Area
├─ Tab 1: Charts (existing matplotlib plots)
└─ Tab 2: Comparison Table (NEW)
     ├─ Table with columns: Property | Material 1 | Material 2 | ... | Unit | References
     ├─ Rows: One per property
     ├─ Cells show: value (ref: ID)
     └─ Highlight differences
```

### Option 2: Add Comparison Table Below Charts

**Structure**:
```
Plot Area
├─ Charts (top 70%)
└─ Comparison Table (bottom 30%)
     ├─ Shows data for currently plotted materials/properties
     ├─ Synchronized with chart
     └─ Click row to highlight in chart
```

### Option 3: Separate Comparison View in Dashboard

**Structure**:
```
Dashboard (Right Panel)
├─ Statistics Cards (existing)
├─ Details Panel (existing)
└─ Comparison Table (NEW)
     ├─ Compact table
     ├─ Shows selected materials/properties
     └─ Reference IDs in tooltips
```

---

## Recommended: Option 2 (Table Below Charts)

### Why:
1. Keeps chart and data together
2. Easy to compare visual and numerical
3. References visible at all times
4. No extra navigation needed

### Implementation:
1. Split plot panel vertically (QSplitter)
2. Top: Existing matplotlib canvas
3. Bottom: QTableWidget with data
4. Populate table when plot is generated
5. Show: Property | Value | Unit | Reference | Index for each entry

---

## Detailed Table Design

### Columns:
| Property | Material | Value | Unit | Reference | Index | Notes |
|----------|----------|-------|------|-----------|-------|-------|
| Density  | Copper   | 8940  | kg/m³ | 107      | 1     |       |
| Density  | Copper   | 8930  | kg/m³ | 109      | 2     | Preferred |
| Density  | Copper   | 8000  | kg/m³ | 109      | 3     |       |
| Density  | Copper   | 8960  | kg/m³ | 121      | 4     |       |
| Density  | Aluminum | 2700  | kg/m³ | 115      | 1     |       |
| Cp       | Copper   | 384   | J/kg/K | 121    | 1     |       |

### Features:
- ✓ One row per database entry
- ✓ No aggregation or averaging
- ✓ Reference ID always visible
- ✓ Unit in separate column
- ✓ Index shows entry order
- ✓ Highlight overridden values
- ✓ Sortable by column
- ✓ Exportable to CSV

---

## Code Changes Needed

### File: `gui/views/visualization_tab.py`

#### 1. Add QTableWidget Import
```python
from PyQt6.QtWidgets import (..., QTableWidget, QTableWidgetItem, QHeaderView)
```

#### 2. Modify `create_plot_panel()`
```python
def create_plot_panel(self):
    panel = QFrame()
    layout = QVBoxLayout(panel)
    
    # Title
    title = QLabel("Plot Area")
    layout.addWidget(title)
    
    # Create splitter for chart + table
    splitter = QSplitter(Qt.Orientation.Vertical)
    
    # Top: Chart area (existing code)
    chart_widget = QWidget()
    chart_layout = QVBoxLayout(chart_widget)
    self.figure = Figure(figsize=(8, 6), dpi=100)
    self.canvas = FigureCanvas(self.figure)
    self.ax = self.figure.add_subplot(111)
    toolbar = NavigationToolbar(self.canvas, chart_widget)
    chart_layout.addWidget(toolbar)
    chart_layout.addWidget(self.canvas)
    splitter.addWidget(chart_widget)
    
    # Bottom: Comparison table (NEW)
    table_widget = QWidget()
    table_layout = QVBoxLayout(table_widget)
    table_label = QLabel("Data Comparison Table")
    table_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
    table_layout.addWidget(table_label)
    
    self.comparison_table = QTableWidget()
    self.comparison_table.setColumnCount(7)
    self.comparison_table.setHorizontalHeaderLabels([
        "Property", "Material", "Value", "Unit", "Reference", "Index", "Notes"
    ])
    self.comparison_table.horizontalHeader().setStretchLastSection(True)
    table_layout.addWidget(self.comparison_table)
    
    splitter.addWidget(table_widget)
    
    # Set splitter proportions (70% chart, 30% table)
    splitter.setStretchFactor(0, 7)
    splitter.setStretchFactor(1, 3)
    
    layout.addWidget(splitter)
    return panel
```

#### 3. Add `update_comparison_table()` Method
```python
def update_comparison_table(self):
    """Populate comparison table with current data"""
    self.comparison_table.setRowCount(0)  # Clear existing
    
    row = 0
    for material_name, mat_data in self.materials_data.items():
        for prop_name in self.selected_properties:
            if prop_name in mat_data:
                for entry in mat_data[prop_name]:
                    self.comparison_table.insertRow(row)
                    
                    # Property name
                    self.comparison_table.setItem(row, 0, 
                        QTableWidgetItem(prop_name.replace('_', ' ').title()))
                    
                    # Material name
                    self.comparison_table.setItem(row, 1, 
                        QTableWidgetItem(material_name))
                    
                    # Value
                    value = entry['value']
                    self.comparison_table.setItem(row, 2, 
                        QTableWidgetItem(f"{value:.4g}"))
                    
                    # Unit
                    self.comparison_table.setItem(row, 3, 
                        QTableWidgetItem(entry.get('unit', '')))
                    
                    # Reference ID
                    self.comparison_table.setItem(row, 4, 
                        QTableWidgetItem(str(entry.get('ref', ''))))
                    
                    # Index
                    self.comparison_table.setItem(row, 5, 
                        QTableWidgetItem(str(entry.get('index', ''))))
                    
                    # Notes (empty for now, can add override status)
                    self.comparison_table.setItem(row, 6, 
                        QTableWidgetItem(""))
                    
                    row += 1
    
    # Resize columns to content
    self.comparison_table.resizeColumnsToContents()
```

#### 4. Call Table Update in `generate_plot()`
```python
def generate_plot(self):
    # ... existing code ...
    
    # After plotting
    self.canvas.draw()
    
    # Update comparison table (NEW)
    self.update_comparison_table()
    
    # Update dashboard
    self.update_dashboard()
```

---

## Additional Enhancements

### 1. Model Parameter Tables
Add separate tabs for:
- Elastic Model Parameters
- Plastic Model Parameters
- Reaction Model Parameters
- EOS Parameters

### 2. Data Completeness Indicator
In dashboard, show:
```
Data Completeness:
  Copper:
    ✓ Density (4 values)
    ✓ Cp (2 values)
    ✗ Cv (no data)
    ✗ Viscosity (no data)
```

### 3. Reference ID Tooltips
When hovering over chart points, show:
```
Tooltip:
Material: Copper
Property: Density
Value: 8940 kg/m³
Reference: 107
Index: 1
```

---

## Implementation Priority

**Phase 1** (Essential):
1. ✅ Fix data extraction (DONE)
2. ✅ Fix matplotlib backend (DONE)
3. ⏳ Add comparison table below charts (IN PROGRESS)

**Phase 2** (Important):
4. Add reference ID tooltips on charts
5. Add data completeness indicator
6. Add table export to CSV

**Phase 3** (Advanced):
7. Add model parameter tables
8. Add override status highlighting
9. Add missing data warnings

---

## Testing Checklist

After implementing comparison table:

- [ ] Table appears below chart
- [ ] Table shows all selected materials
- [ ] Table shows all selected properties
- [ ] One row per database entry (no aggregation)
- [ ] Reference IDs visible
- [ ] Units displayed correctly
- [ ] Values match chart data
- [ ] Can resize table
- [ ] Can sort by columns
- [ ] Table updates when regenerating plot

---

## Next Steps

**Ready to implement?**

Say "implement comparison table" and I'll:
1. Modify `visualization_tab.py` to add QTableWidget
2. Add `update_comparison_table()` method
3. Update `generate_plot()` to populate table
4. Test with Copper + Aluminum comparison
5. Verify all 17 materials work

**Current Status**: All prerequisites met, ready to add comparison feature!
