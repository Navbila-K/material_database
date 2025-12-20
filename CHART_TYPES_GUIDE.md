# 📊 Visualization Tab - Complete Chart Types Guide

## Overview
The Visualization tab now supports **6 different chart types** for comprehensive material property analysis!

---

## 🎨 Available Chart Types

### 1. 📉 Line Chart
**Best For**: Trends, comparisons over data points

**Features**:
- Shows individual data points with markers
- Connects points with lines
- Multiple materials overlay on same plot
- Each material-property gets unique color
- Grid and legend enabled

**Use Case**: 
- Compare how density varies across measurements
- See thermal conductivity trends
- Overlay multiple materials for comparison

**Example**:
```
Material: Copper, Aluminum
Property: density
Result: 2 lines showing density data points
```

---

### 2. 📊 Bar Chart
**Best For**: Comparing average values across properties

**Features**:
- Grouped bars by property
- Shows average values
- Each material has distinct color
- Rotated labels for readability

**Use Case**:
- Compare average density of multiple materials
- See which material has higher thermal conductivity
- Quick visual comparison of averages

**Example**:
```
Materials: Copper, Aluminum, Nickel
Properties: density, thermal_conductivity
Result: Grouped bars showing averages
```

---

### 3. 🔵 Scatter Plot
**Best For**: Identifying patterns, outliers, distributions

**Features**:
- Large circular markers
- White edges for clarity
- Semi-transparent for overlaps
- Grid for easy reading

**Use Case**:
- Find outliers in property measurements
- See data point distributions
- Identify clustering patterns

**Example**:
```
Material: Copper
Properties: density, specific_heat_capacity
Result: Scatter points showing all measurements
```

---

### 4. 📈 Area Chart
**Best For**: Visualizing cumulative trends, filled regions

**Features**:
- Filled area under curve
- Semi-transparent (40% opacity)
- Solid line on top edge
- Multiple areas can overlap

**Use Case**:
- Show cumulative property values
- Emphasize magnitude of differences
- Beautiful presentation charts

**Example**:
```
Material: Aluminum
Properties: thermal_conductivity
Result: Filled area showing magnitude
```

---

### 5. 🥧 Pie Chart
**Best For**: Property distribution for ONE material

**Features**:
- Shows percentage distribution
- Uses absolute values
- Displays percentages on slices
- Circular layout

**Important**: 
- Only uses FIRST selected material
- Compares multiple properties
- Shows relative proportions

**Use Case**:
- See which property dominates in a material
- Property contribution percentage
- Quick overview of property mix

**Example**:
```
Material: Copper (only first one)
Properties: density, thermal_conductivity, specific_heat_capacity
Result: Pie chart showing % of each property value
```

---

### 6. 📊 Histogram
**Best For**: Value distribution, frequency analysis

**Features**:
- 10 bins by default
- Semi-transparent bars (60% opacity)
- Black edges for clarity
- Shows frequency of values

**Use Case**:
- See distribution of property values
- Find common value ranges
- Identify value clusters

**Example**:
```
Materials: Copper, Aluminum
Properties: density
Result: Histogram showing value frequency
```

---

## 🎯 Chart Selection Guide

| Need | Chart Type | Why |
|------|-----------|-----|
| Compare trends | Line | Shows progression |
| Compare averages | Bar | Quick comparison |
| Find outliers | Scatter | See all points |
| Show magnitude | Area | Filled emphasis |
| Property mix | Pie | % distribution |
| Value spread | Histogram | Frequency view |

---

## 🚀 How to Use Each Chart

### Line Chart Workflow
```
1. Select materials: Copper, Aluminum
2. Select properties: density, thermal_conductivity
3. Choose: "Line"
4. Generate Plot
→ Result: 4 lines (2 materials × 2 properties)
```

### Bar Chart Workflow
```
1. Select materials: Copper, Aluminum, Nickel
2. Select properties: density, youngs_modulus
3. Choose: "Bar"
4. Generate Plot
→ Result: Grouped bars showing averages
```

### Scatter Plot Workflow
```
1. Select material: Copper
2. Select properties: density, specific_heat_capacity
3. Choose: "Scatter"
4. Generate Plot
→ Result: Scatter points showing all data
```

### Area Chart Workflow
```
1. Select material: Aluminum
2. Select property: thermal_conductivity
3. Choose: "Area"
4. Generate Plot
→ Result: Filled area showing magnitude
```

### Pie Chart Workflow
```
1. Select materials: Copper (others ignored)
2. Select properties: density, thermal_conductivity, specific_heat
3. Choose: "Pie"
4. Generate Plot
→ Result: Pie showing % of each property
```

### Histogram Workflow
```
1. Select materials: Copper, Aluminum
2. Select properties: density
3. Choose: "Histogram"
4. Generate Plot
→ Result: Bars showing value frequency
```

---

## 🎨 Color Scheme

All charts use **8 distinct colors**:
1. **Red** (#e74c3c) - First material/property
2. **Blue** (#3498db) - Second
3. **Green** (#2ecc71) - Third
4. **Orange** (#f39c12) - Fourth
5. **Purple** (#9b59b6) - Fifth
6. **Teal** (#1abc9c) - Sixth
7. **Dark Orange** (#e67e22) - Seventh
8. **Dark Gray** (#34495e) - Eighth

Colors cycle if you have more than 8 items.

---

## 📐 Chart Customization

### For All Charts:
- **Title**: Bold, 13pt font
- **Grid**: Dashed lines, 30% opacity
- **Legend**: Best position, 9pt font
- **Axes**: 11pt labels

### Specific Features:

**Line Chart**:
- Marker size: 6px
- Line width: 2px

**Bar Chart**:
- Opacity: 80%
- Auto-rotates labels

**Scatter**:
- Marker size: 100px
- Opacity: 70%
- White edge: 1.5px

**Area**:
- Fill opacity: 40%
- Line width: 2px
- Line opacity: 80%

**Pie**:
- Start angle: 90°
- Percentage: 1 decimal
- White, bold percentages

**Histogram**:
- Bins: 10
- Opacity: 60%
- Black edges

---

## 🐛 Troubleshooting

### Issue: Empty Chart
**Symptoms**: "No data available"

**Solutions**:
1. Check console for "Properties found: []"
2. Verify material has the properties
3. Try different properties
4. Check database has data

### Issue: Pie Chart Shows Wrong Material
**Expected**: Pie chart only uses first selected material

**Solution**: This is by design - pie charts compare properties within ONE material

### Issue: Histogram Looks Empty
**Cause**: Too few data points

**Solution**: 
- Select multiple materials
- Select multiple properties
- More data = better histogram

### Issue: Bar Chart Bars Overlapping
**Cause**: Too many materials selected

**Solution**: Limit to 3-5 materials for clarity

---

## 🔍 Debug Output

When you generate plots, console shows:

```
=== GENERATE PLOT CALLED ===
Selected materials: ['Copper']
Selected properties: ['density', 'thermal_conductivity']

Fetching data for: Copper
[VizTab] Fetching Copper with overrides=True
  Properties found: ['density', 'thermal_conductivity', ...]
    density: 1 data points - Values: [8940.0]
    thermal_conductivity: 1 data points - Values: [401.0]

Generating Line chart...
Plot generated successfully!
=== PLOT GENERATION COMPLETE ===
```

**Look For**:
- "Properties found" should list your properties
- Data points should be > 0
- Values should show actual numbers
- "Plot generated successfully!"

**If You See**:
- "NOT FOUND in material data" → Property doesn't exist
- "0 data points" → No values in database
- "ERROR in plotting" → Check traceback

---

## 💡 Pro Tips

### Tip 1: Multi-Material Line Comparison
```
Best: 2-3 materials, 1-2 properties
Why: Clear, not cluttered
Example: Copper vs Aluminum density
```

### Tip 2: Bar Chart for Quick Overview
```
Best: 3-5 materials, 2-4 properties
Why: Easy to compare averages
Example: Compare 3 metals across 3 properties
```

### Tip 3: Scatter for Data Quality
```
Best: 1 material, 1-2 properties
Why: See all individual measurements
Example: Check if data has outliers
```

### Tip 4: Area for Presentations
```
Best: 1-2 materials, 1 property
Why: Beautiful, emphasizes magnitude
Example: Show thermal conductivity range
```

### Tip 5: Pie for Composition
```
Best: 1 material, 3-6 properties
Why: Shows relative proportions
Example: See which property dominates
```

### Tip 6: Histogram for Distribution
```
Best: 1-2 materials, 1 property
Why: See value spread and clusters
Example: Check density value distribution
```

---

## 📊 Example Scenarios

### Scenario 1: Material Selection
**Goal**: Choose between Copper, Aluminum, Nickel for application

**Steps**:
1. Select all 3 materials
2. Select key properties: density, thermal_conductivity, youngs_modulus
3. Generate **Bar Chart** to compare averages
4. Switch to **Line Chart** for detailed trends
5. Check **Histogram** for value distributions

### Scenario 2: Quality Check
**Goal**: Verify data quality for Copper

**Steps**:
1. Select only Copper
2. Select all available properties
3. Generate **Scatter Plot** to see all points
4. Look for outliers or anomalies
5. Check **Histogram** for unusual distributions

### Scenario 3: Presentation
**Goal**: Create beautiful chart for report

**Steps**:
1. Select 1-2 materials
2. Select 1-2 key properties
3. Generate **Area Chart** for visual impact
4. Export as PDF at 300 DPI
5. Use in publication

### Scenario 4: Property Analysis
**Goal**: Understand property mix in Aluminum

**Steps**:
1. Select Aluminum
2. Select multiple properties
3. Generate **Pie Chart** to see % distribution
4. Identify dominant properties

---

## 🎓 Advanced Usage

### Combining Charts
```
1. Generate Line chart → Export as "line.png"
2. Generate Bar chart → Export as "bar.png"
3. Generate Scatter → Export as "scatter.png"
4. Combine in external tool for comprehensive report
```

### Data Exploration Workflow
```
1. Start with Bar chart → Quick overview
2. Switch to Line → See trends
3. Use Scatter → Find outliers
4. Check Histogram → Value distribution
5. Pie chart → Composition analysis
```

---

## 📋 Chart Type Summary Table

| Chart | Materials | Properties | Best For | Output |
|-------|-----------|-----------|----------|--------|
| **Line** | 1-5 | 1-3 | Trends | Lines with markers |
| **Bar** | 2-5 | 2-4 | Averages | Grouped bars |
| **Scatter** | 1-3 | 1-2 | Outliers | Dot plot |
| **Area** | 1-3 | 1-2 | Magnitude | Filled curves |
| **Pie** | 1 only | 3-6 | Distribution | Pie slices |
| **Histogram** | 1-2 | 1 | Frequency | Bar histogram |

---

## 🚀 Ready to Visualize!

All 6 chart types are now available. Choose the right one for your analysis needs!

**Remember**:
- ✅ Debug output helps troubleshoot
- ✅ Console shows what data is found
- ✅ Error messages display on plot
- ✅ All charts exportable to PNG/PDF

**Happy visualizing!** 📊✨
