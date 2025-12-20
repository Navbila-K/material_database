# Visualization Tab Integration Guide

## 🔗 Material Browser ↔ Visualization Tab Integration

The Visualization tab is now **fully linked** with the Material Browser. This means:

### Automatic Synchronization

**When you select a material in Material Browser:**
1. The material is **automatically selected** in the Visualization tab
2. You can then select properties and generate plots
3. The data view mode (Original/Active) can be chosen

**When you switch between tabs in Property Viewer:**
- Original Data tab → shows raw data without overrides
- Overrides tab → shows list of overrides
- Active View tab → shows data WITH overrides applied
- References tab → shows reference information

**In Visualization tab:**
- Choose "Active View (with Overrides)" → plots WITH user modifications
- Choose "Original Data (no Overrides)" → plots raw database values

---

## 📊 Complete Workflow

### Step-by-Step Usage

**1. Select Material in Browser**
```
Material Browser (Tab 1)
  ↓ (select "Copper")
  Auto-selects "Copper" in Visualization tab
```

**2. Switch to Visualization Tab**
```
Click "Visualization" tab (Tab 2)
  → Material "Copper" is already selected ✓
```

**3. Select Properties**
```
Hold Ctrl/Cmd and click:
  - density
  - thermal_conductivity
  - specific_heat_capacity
```

**4. Choose Data View Mode**
```
Dropdown: "Active View (with Overrides)"
  → Will include any overrides you applied
  
OR

Dropdown: "Original Data (no Overrides)"
  → Will show pure database values
```

**5. Choose Chart Type**
```
Dropdown: Line or Bar
```

**6. Generate Plot**
```
Click "Generate Plot" button
  → Chart appears with selected data
  → Dashboard updates with statistics
  → References shown in details panel
```

**7. Export (Optional)**
```
Click "Export Plot (PNG/PDF)"
  → Save high-quality chart
```

---

## 🔄 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   Material Browser                       │
│                                                          │
│  [Material List] → Select "Aluminum"                    │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Original Data│  │  Overrides   │  │ Active View  │  │
│  │ (no changes) │  │  (list)      │  │ (modified)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
│  ┌──────────────┐                                       │
│  │ References   │                                       │
│  │ (biblio info)│                                       │
│  └──────────────┘                                       │
└──────────────────────┬───────────────────────────────────┘
                       │
                       │ AUTO-SYNC
                       ↓
┌─────────────────────────────────────────────────────────┐
│                  Visualization Tab                       │
│                                                          │
│  ✓ "Aluminum" selected automatically                    │
│                                                          │
│  Data View Mode:                                         │
│  [Active View (with Overrides) ▼]  ← match browser tab  │
│                                                          │
│  Select Properties:                                      │
│  ☑ density                                              │
│  ☑ thermal_conductivity                                 │
│                                                          │
│  Chart Type: [Line ▼]                                   │
│                                                          │
│  [Generate Plot] [Export Plot]                          │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │         📈 PLOT AREA                           │    │
│  │                                                  │    │
│  │  Aluminum - Density                             │    │
│  │  Aluminum - Thermal Conductivity                │    │
│  │                                                  │    │
│  │  (legend, grid, axis labels)                    │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  Dashboard:                                              │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐           │
│  │   1    │ │   2    │ │  12   │ │   0    │           │
│  │Materials│ │  Props │ │ Points │ │Missing │           │
│  └────────┘ └────────┘ └────────┘ └────────┘           │
│                                                          │
│  Details:                                                │
│  - Data View: Active View (with Overrides)              │
│  - References: 107, 121                                  │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Features

### 1. **Material Browser Linkage**
- Selecting material in browser → auto-selects in visualization
- No need to re-select manually
- Instant synchronization

### 2. **Data View Modes**
Match the Property Viewer tabs:
- **Original Data** = Raw database values
- **Active View** = With user overrides applied

### 3. **Reference Tracking**
- Dashboard shows unique reference count
- Details panel lists all reference IDs used
- Matches the References tab in browser

### 4. **Multi-Material Comparison**
- Can still select multiple materials manually
- Overlay them on same chart
- Each gets distinct color

### 5. **Property Categories**
All property types supported:
- Thermal (density, Cp, k, α, Tm, Tb)
- Mechanical (E, G, K, ν, σy, σu)
- Electrical (σ, ρ, εr)
- Optical (n, α)
- EOS (γ, s, c)

---

## 🧪 Testing the Integration

### Test 1: Basic Sync
1. Go to Material Browser tab
2. Click on "Copper"
3. Switch to Visualization tab
4. **Expected**: "Copper" is already selected ✓

### Test 2: Data View Modes
1. Select "Copper" in browser
2. Go to Visualization tab
3. Select "density" property
4. Set view mode to "Original Data"
5. Click "Generate Plot"
6. **Note the value**
7. Switch view mode to "Active View (with Overrides)"
8. Click "Generate Plot"
9. **Expected**: If overrides exist, values differ

### Test 3: References
1. Select material with references
2. Generate plot
3. Check Details panel
4. **Expected**: Reference IDs shown (e.g., "107, 121")

### Test 4: Multi-Material
1. Browser: Select "Aluminum"
2. Visualization: "Aluminum" auto-selected
3. Manually Ctrl+Click "Copper" too
4. Select "density"
5. Generate Line plot
6. **Expected**: 2 lines, different colors

---

## 🔧 Debugging

### Console Output
The visualization tab prints detailed debug info:

```python
=== GENERATE PLOT CALLED ===
Selected materials: ['Copper']
Selected properties: ['density', 'thermal_conductivity']

Fetching data for: Copper
  Properties found: ['density', 'thermal_conductivity', ...]
    density: 1 data points
    thermal_conductivity: 1 data points

[VizTab] Fetching Copper with overrides=True
Generating Line chart...
Plot generated successfully!
=== PLOT GENERATION COMPLETE ===
```

### Common Issues

**Issue**: Plot is empty
- Check console for "No data available"
- Ensure material has the selected properties
- Try different properties

**Issue**: Material not auto-selecting
- Check console for "[VizTab] Selecting material: ..."
- Ensure material exists in database
- Reload materials list

**Issue**: Overrides not showing
- Check view mode dropdown
- Ensure "Active View (with Overrides)" is selected
- Verify overrides exist in database

---

## 📋 Properties Available

Current properties in dropdown:
```
- density
- specific_heat_capacity
- thermal_conductivity
- thermal_expansion
- youngs_modulus
- shear_modulus
- poissons_ratio
- electrical_conductivity
```

To add more properties, edit `visualization_tab.py`:
```python
common_properties = [
    "density",
    "specific_heat_capacity",
    # Add new properties here
    "bulk_modulus",
    "melting_point",
    # etc.
]
```

---

## 🎨 Chart Customization

### Colors
8 materials get 8 distinct colors:
1. Red (#e74c3c)
2. Blue (#3498db)
3. Green (#2ecc71)
4. Orange (#f39c12)
5. Purple (#9b59b6)
6. Teal (#1abc9c)
7. Dark Orange (#e67e22)
8. Dark Gray (#34495e)

### Chart Types

**Line Chart**:
- Best for: Trends, comparisons over data points
- Shows: Individual markers + connecting lines
- Legend: Material - Property name

**Bar Chart**:
- Best for: Comparing average values
- Shows: Grouped bars by property
- Values: Averages across all data points

---

## 💡 Tips & Tricks

1. **Quick Start**: Select material in browser, switch to Viz tab, auto-selected!
2. **Compare Modes**: Use both view modes to see effect of overrides
3. **Export Quality**: Charts export at 300 DPI for publications
4. **Multi-Select**: Hold Ctrl/Cmd to select multiple materials/properties
5. **References**: Check Details panel to see which refs were used

---

## 🚀 Future Enhancements

Possible additions:
- [ ] Auto-switch view mode when switching Property Viewer tabs
- [ ] Show reference titles (not just IDs) in dashboard
- [ ] Click on data point to see reference details
- [ ] Sync property selection with Property Viewer
- [ ] Add "Plot Selected Property" button in Property Viewer
- [ ] Temperature/Pressure dependent plots
- [ ] 3D surface plots for EOS data

---

**The Visualization tab is now fully integrated with your Material Browser!** 🎉
