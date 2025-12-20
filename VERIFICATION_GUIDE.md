# 📋 VISUALIZATION TAB - VERIFICATION CHECKLIST

## 🎯 How to Verify and Check the Visualization Tab

Follow these steps IN ORDER to verify everything is working correctly.

---

## ✅ STEP 1: Start the GUI

```bash
cd /Users/sridhars/Projects/materials_db
python run_gui.py
```

### Expected Console Output:
```
DEBUG: Set QT_PLUGIN_PATH to /path/to/PyQt6/Qt6/plugins
DEBUG: Matplotlib default backend: macosx
DEBUG: Matplotlib backend changed to: QtAgg  ← MUST SEE THIS!
DEBUG: MainWindow __init__ starting...
DEBUG: Connecting to database...
DEBUG: Database connected, creating queriers...
[VizTab] Initializing Visualization Tab...     ← MUST SEE THIS!
[VizTab] Setting up UI...
[VizTab] Creating matplotlib Figure...
[VizTab] Figure created successfully           ← MUST SEE THIS!
[VizTab] FigureCanvas created successfully
[VizTab] Subplot added successfully
[VizTab] NavigationToolbar created successfully
[VizTab] Plot panel created successfully!
[VizTab] Generate Plot button created and connected  ← MUST SEE THIS!
[VizTab] Loading materials...
[VizTab] Initialization complete!              ← MUST SEE THIS!
DEBUG: Loading stylesheet...
DEBUG: Loading materials...
DEBUG: MainWindow initialization complete!
```

### ✅ Verification Checklist:
- [ ] No error messages appear
- [ ] GUI window opens
- [ ] Console shows "QtAgg" backend (NOT "macosx")
- [ ] Console shows "[VizTab] Initialization complete!"
- [ ] Console shows "Generate Plot button created and connected"

**If ANY of these fail, STOP and report the error messages.**

---

## ✅ STEP 2: Navigate to Visualization Tab

### Action:
1. Look at the top of the GUI window
2. You should see **TWO TABS**:
   - Tab 1: "Material Browser"
   - Tab 2: "Visualization"
3. **Click on the "Visualization" tab**

### Expected Result:
The screen should change to show **3 PANELS**:

```
┌─────────────────┬──────────────────────┬─────────────────┐
│                 │                      │                 │
│  Control Panel  │     Plot Area        │   Dashboard     │
│  (LEFT)         │     (CENTER)         │   (RIGHT)       │
│                 │                      │                 │
│  - Materials    │  "Select materials   │  - Statistics   │
│  - Properties   │   and properties,    │  - Details      │
│  - Chart Type   │   then click         │                 │
│  - Generate Btn │   Generate Plot"     │                 │
│                 │                      │                 │
└─────────────────┴──────────────────────┴─────────────────┘
```

### ✅ Verification Checklist:
- [ ] Tab switches to "Visualization"
- [ ] Left panel shows "Control Panel" with material list
- [ ] Center panel shows "Plot Area" with instructions
- [ ] Right panel shows "Dashboard" with stat cards
- [ ] Material list is populated with material names (Copper, Aluminum, etc.)
- [ ] Property list shows properties (density, cp, cv, etc.)
- [ ] "Generate Plot" button is visible

**If you don't see 3 panels, something is wrong.**

---

## ✅ STEP 3: Select Material

### Action:
1. In the **LEFT panel** under "Select Materials"
2. Look for **"Copper"** in the list
3. **Click on "Copper"** (should highlight in blue/gray)

### Expected Result:
- "Copper" becomes highlighted
- No console output yet (that's normal)

### ✅ Verification Checklist:
- [ ] Material list contains "Copper"
- [ ] Clicking "Copper" highlights it
- [ ] Material stays selected (highlighted)

**Alternative**: If Copper isn't there, select any material you see.

---

## ✅ STEP 4: Select Property

### Action:
1. In the **LEFT panel** under "Select Properties"
2. Look for **"density"** in the list
3. **Click on "density"** (should highlight)

### Expected Result:
- "density" becomes highlighted
- No console output yet (that's normal)

### ✅ Verification Checklist:
- [ ] Property list contains "density"
- [ ] Clicking "density" highlights it
- [ ] Property stays selected (highlighted)

**Alternative**: If density isn't there, try "cp" or any property shown.

---

## ✅ STEP 5: Click "Generate Plot" Button

### Action:
1. In the **LEFT panel** at the bottom
2. **Click the "Generate Plot" button**

### Expected Console Output:
```
=== GENERATE PLOT CALLED ===
Selected materials: ['Copper']
Selected properties: ['density']

Fetching data for: Copper
[VizTab] Fetching Copper with overrides=True
[VizTab] Properties section has categories: ['Phase', 'Thermal', 'Mechanical']
[VizTab]   Category 'Thermal' has 2 properties
[VizTab]   Category 'Mechanical' has 2 properties
[VizTab] Extracted properties: ['cp', 'cv', 'density', 'viscosity']
[VizTab]   cp: 2 values
[VizTab]   cv: 0 values
[VizTab]   density: 4 values               ← IMPORTANT!
[VizTab]   viscosity: 0 values
  Properties found: ['cp', 'cv', 'density', 'viscosity']
    density: 4 data points - Values: [8940.0, 8930.0, 8000.0]  ← DATA!

Generating Line chart...
Plot generated successfully!                  ← SUCCESS!
=== PLOT GENERATION COMPLETE ===
```

### ✅ Verification Checklist:
- [ ] Console shows "=== GENERATE PLOT CALLED ==="
- [ ] Console shows selected materials: ['Copper']
- [ ] Console shows selected properties: ['density']
- [ ] Console shows "density: 4 values" or similar
- [ ] Console shows actual data values like [8940.0, 8930.0, ...]
- [ ] Console shows "Plot generated successfully!"
- [ ] **NO ERROR MESSAGES appear**

**If you see errors instead, copy the entire error and report it.**

---

## ✅ STEP 6: Verify Plot Appears

### What to Look For in CENTER PANEL:

**YOU SHOULD NOW SEE A PLOT with**:

1. **A RED LINE** going through data points
2. **CIRCULAR MARKERS** (dots) at each data point
3. **4 DATA POINTS** (for Copper density)
4. **Y-AXIS values** around 8000-9000
5. **X-AXIS values** 0, 1, 2, 3 (data point indices)
6. **LEGEND** box showing "Copper - Density"
7. **GRID LINES** (light gray dotted lines)
8. **AXIS LABELS**: 
   - X-axis: "Data Point Index"
   - Y-axis: "Property Value"
9. **TITLE**: "Material Property Comparison"
10. **TOOLBAR** at top with zoom/pan/save buttons

### Visual Example of What You Should See:
```
┌────────────────────────────────────────┐
│  Material Property Comparison          │  ← Title
│                                        │
│  9000 ┤                            •   │
│       │                                │
│  8800 ┤          •            •        │  ← Red line + dots
│       │                                │
│  8600 ┤                                │
│       │                                │
│  8400 ┤     •                          │
│       │                                │
│  8000 ┴────────┬────────┬────────┬─────┤
│       0        1        2        3     │  ← X-axis
│                                        │
│       Data Point Index                 │
│                                        │
│  Legend: ▬ Copper - Density           │  ← Legend
└────────────────────────────────────────┘
```

### ✅ Verification Checklist:
- [ ] Plot area shows a LINE (not empty)
- [ ] Line has MARKERS (dots/circles)
- [ ] Multiple data points visible (3-4 for Copper density)
- [ ] Legend appears showing material and property name
- [ ] Axes have labels
- [ ] Grid lines visible
- [ ] Toolbar with buttons appears

**THIS IS THE KEY TEST - If you see the plot, IT'S WORKING! 🎉**

---

## ✅ STEP 7: Verify Dashboard Updates

### What to Look For in RIGHT PANEL:

**Statistics Cards** (top of right panel):
- **Materials**: Should show "1"
- **Properties**: Should show "1"
- **Data Points**: Should show "4" (for Copper density)
- **Missing Values**: Should show a number

**Details Panel** (below stat cards):
- Selected materials listed
- Selected properties listed
- View mode shown (Active View or Original Data)

### ✅ Verification Checklist:
- [ ] Dashboard shows "Materials: 1"
- [ ] Dashboard shows "Properties: 1"
- [ ] Dashboard shows "Data Points: 4" or similar
- [ ] Details panel lists "Copper"
- [ ] Details panel lists "density"

---

## ✅ STEP 8: Test Different Chart Types

### Action:
1. In the **LEFT panel** under "Chart Type"
2. Click the **dropdown menu** (currently shows "Line")
3. **Select "Bar"**
4. **Click "Generate Plot"** again

### Expected Result:
- Console shows plot generation messages
- Plot area now shows **BAR CHART** instead of line chart
- Single red bar showing average density value

### Test All 6 Chart Types:

#### 1. Line Chart ✅ (already tested)
```
Expected: Line with markers connecting data points
```

#### 2. Bar Chart
```
Chart Type: Bar
Expected: Vertical bar showing average value (~8707)
```

#### 3. Scatter Chart
```
Chart Type: Scatter
Expected: Individual dots (no connecting line)
Large circular markers with white edges
```

#### 4. Area Chart
```
Chart Type: Area
Expected: Line with FILLED area below it
Color should be semi-transparent
```

#### 5. Pie Chart
```
Chart Type: Pie
Expected: Circular pie with one slice
Shows percentage (100% for single property)
```

#### 6. Histogram
```
Chart Type: Histogram
Expected: Frequency bars showing distribution
About 10 bins showing how often values appear
```

### ✅ Verification Checklist:
- [ ] Can change chart type in dropdown
- [ ] Line chart works
- [ ] Bar chart works
- [ ] Scatter chart works
- [ ] Area chart works
- [ ] Pie chart works
- [ ] Histogram chart works

---

## ✅ STEP 9: Test Multiple Properties

### Action:
1. Keep "Copper" selected
2. In property list, **HOLD CTRL (or CMD on Mac)**
3. Click **"density"** (if not already selected)
4. **Keep holding CTRL** and click **"cp"**
5. Both should be highlighted now
6. Click **"Generate Plot"**

### Expected Console Output:
```
Selected materials: ['Copper']
Selected properties: ['density', 'cp']    ← TWO properties

Fetching data for: Copper
    density: 4 data points - Values: [8940.0, ...]
    cp: 2 data points - Values: [384.0, 0.385]   ← TWO different properties

Generating Line chart...
Plot generated successfully!
```

### Expected Plot:
- **TWO LINES** on the same chart
- Different colors (red and blue)
- Legend shows both:
  - "Copper - Density"
  - "Copper - Cp"

### ✅ Verification Checklist:
- [ ] Can select multiple properties
- [ ] Plot shows multiple lines
- [ ] Each line has different color
- [ ] Legend shows all selected items

---

## ✅ STEP 10: Test Multiple Materials

### Action:
1. In material list, **HOLD CTRL**
2. Click **"Copper"**
3. **Keep holding CTRL** and click **"Aluminum"** (if available)
4. Both should be highlighted
5. Select one property: **"density"**
6. Click **"Generate Plot"**

### Expected Result:
- **TWO LINES** (one per material)
- Different colors
- Legend shows:
  - "Copper - Density"
  - "Aluminum - Density"

### ✅ Verification Checklist:
- [ ] Can select multiple materials
- [ ] Plot shows line for each material
- [ ] Different colors for each material
- [ ] Legend distinguishes materials

---

## ✅ STEP 11: Test View Mode Toggle

### Action:
1. In the **LEFT panel** find "Data View Mode"
2. Click the **dropdown**
3. Should show two options:
   - "Active View (with Overrides)"
   - "Original Data (no Overrides)"
4. **Switch between them**
5. Click **"Generate Plot"** after each change

### Expected Console Output:
```
# When "Active View" selected:
[VizTab] Fetching Copper with overrides=True

# When "Original Data" selected:
[VizTab] Fetching Copper with overrides=False
```

### ✅ Verification Checklist:
- [ ] Can switch view modes
- [ ] Console shows overrides=True or False accordingly
- [ ] Plot regenerates with new data
- [ ] Dashboard shows current view mode

---

## ✅ STEP 12: Test Export Functionality

### Action:
1. Generate any plot (e.g., Copper density line chart)
2. In the **LEFT panel** click **"Export Plot (PNG/PDF)"** button
3. File save dialog should appear
4. Choose location and filename
5. Select format: PNG or PDF
6. Click Save

### Expected Result:
- File save dialog opens
- Can choose between PNG and PDF
- File is saved to chosen location
- Can open the saved file and see the plot

### ✅ Verification Checklist:
- [ ] Export button clickable
- [ ] File dialog appears
- [ ] Can save as PNG
- [ ] Can save as PDF
- [ ] Exported file opens correctly
- [ ] Plot looks the same as in GUI

---

## 📊 COMPLETE VERIFICATION SUMMARY

### Basic Functionality (MUST WORK):
- [ ] GUI starts without errors
- [ ] Visualization tab appears
- [ ] Can select materials
- [ ] Can select properties
- [ ] Generate Plot button responds
- [ ] Console shows data extraction
- [ ] **PLOT APPEARS** in plot area ← MOST IMPORTANT!

### Chart Types (Should Work):
- [ ] Line chart
- [ ] Bar chart
- [ ] Scatter chart
- [ ] Area chart
- [ ] Pie chart
- [ ] Histogram chart

### Advanced Features (Should Work):
- [ ] Multiple properties on one chart
- [ ] Multiple materials on one chart
- [ ] View mode switching (Original vs Active)
- [ ] Dashboard updates correctly
- [ ] Export to PNG/PDF

---

## 🐛 TROUBLESHOOTING

### Problem: No console output when clicking button
**Solution**: Check if button was connected. Look for:
```
[VizTab] Generate Plot button created and connected
```

### Problem: Console shows "No data available"
**Check**:
```
[VizTab]   density: 0 values    ← BAD
```
**Solution**: Material doesn't have this property. Try different property.

### Problem: Plot area stays empty
**Check Console For**:
- "Plot generated successfully!" ← Should see this
- Any error messages ← Copy and report

**Also Check**:
- Is material selected? (highlighted)
- Is property selected? (highlighted)
- Does console show data values?

### Problem: Plot appears but looks wrong
**Verify**:
- Correct chart type selected?
- Data values make sense?
- Try different chart type

---

## ✅ SUCCESS INDICATORS

### YOU KNOW IT'S WORKING IF:

1. ✅ Console shows "Plot generated successfully!"
2. ✅ Console shows actual data values like [8940.0, 8930.0, ...]
3. ✅ Plot area shows a VISIBLE chart (line/bars/dots/etc.)
4. ✅ Legend appears with material and property names
5. ✅ Can switch chart types and see different visualizations
6. ✅ Dashboard updates with statistics

### MINIMUM SUCCESS:
**If you can see ONE plot (any type) with real data, the visualization tab is WORKING!** 🎉

---

## 📸 WHAT TO REPORT

### If Everything Works:
✅ "Visualization tab is working! I can see plots."
✅ Share screenshot of a plot you generated

### If Something Doesn't Work:
❌ Copy the **ENTIRE console output** from startup to error
❌ Describe what step failed (use step numbers above)
❌ Share screenshot of what you see
❌ Note any error messages

---

## 🎯 QUICK TEST (30 seconds)

**Fastest way to verify**:
1. `python run_gui.py`
2. Click "Visualization" tab
3. Click "Copper"
4. Click "density"
5. Click "Generate Plot"
6. **Look at center panel - do you see a LINE with DOTS?**

**YES** = Working! 🎉
**NO** = Copy console output and report

---

**Now go test it step by step and report back what you see!** 🚀
