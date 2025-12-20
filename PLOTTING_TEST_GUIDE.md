# 🧪 Visualization Plotting - Test & Verify Guide

## ✅ What Was Fixed & Added

### Bug Fixes:
1. ✅ **Better error handling** - Shows errors on plot area
2. ✅ **Enhanced debug logging** - Shows actual data values
3. ✅ **Data validation** - Checks if properties exist before plotting

### New Chart Types Added:
1. ✅ **Scatter Plot** - For pattern analysis
2. ✅ **Area Chart** - For filled visualization
3. ✅ **Pie Chart** - For property distribution
4. ✅ **Histogram** - For value frequency

### Total Chart Types: **6**
- Line
- Bar
- Scatter
- Area
- Pie
- Histogram

---

## 🧪 Quick Test Checklist

### Test 1: Line Chart (BASIC)
```
□ Select material: "Copper"
□ Select property: "density"
□ Chart type: "Line"
□ Click "Generate Plot"
□ Expected: Line plot with markers
□ Check console for data values
```

### Test 2: Bar Chart (COMPARISON)
```
□ Select materials: "Copper", "Aluminum"
□ Select properties: "density", "thermal_conductivity"
□ Chart type: "Bar"
□ Click "Generate Plot"
□ Expected: Grouped bars, 2 colors
```

### Test 3: Scatter Plot (NEW)
```
□ Select material: "Copper"
□ Select properties: "density", "specific_heat_capacity"
□ Chart type: "Scatter"
□ Click "Generate Plot"
□ Expected: Circular markers with white edges
```

### Test 4: Area Chart (NEW)
```
□ Select material: "Aluminum"
□ Select property: "thermal_conductivity"
□ Chart type: "Area"
□ Click "Generate Plot"
□ Expected: Filled area under curve
```

### Test 5: Pie Chart (NEW)
```
□ Select material: "Copper" (only first used)
□ Select properties: "density", "thermal_conductivity", "specific_heat_capacity"
□ Chart type: "Pie"
□ Click "Generate Plot"
□ Expected: Pie chart with 3 slices and percentages
```

### Test 6: Histogram (NEW)
```
□ Select materials: "Copper", "Aluminum"
□ Select property: "density"
□ Chart type: "Histogram"
□ Click "Generate Plot"
□ Expected: Histogram bars showing frequency
```

---

## 🔍 Expected Console Output

### Successful Plot Generation:
```
=== GENERATE PLOT CALLED ===
Selected materials: ['Copper']
Selected properties: ['density']

Fetching data for: Copper
[VizTab] Fetching Copper with overrides=True
  Properties found: ['density', 'thermal_conductivity', 'specific_heat_capacity', ...]
    density: 1 data points - Values: [8940.0]

Generating Line chart...
Plot generated successfully!
=== PLOT GENERATION COMPLETE ===
```

### If Property Not Found:
```
Fetching data for: Copper
  Properties found: ['density', 'thermal_conductivity']
    youngs_modulus: NOT FOUND in material data
```

### If Error Occurs:
```
Generating Line chart...
ERROR in plotting: <error message>
<traceback>
```
(Error also displays on plot area in red box)

---

## 🐛 Common Issues & Solutions

### Issue 1: "No data available"
**Console Shows**: `Properties found: []`

**Cause**: Material doesn't have data in database

**Solution**:
1. Check if material XML was imported
2. Verify database has property values
3. Try different material

---

### Issue 2: Property "NOT FOUND in material data"
**Console Shows**: `density: NOT FOUND in material data`

**Cause**: Property name mismatch or doesn't exist

**Solution**:
1. Check available properties in console output
2. Use properties that exist
3. Check if property is in different category

---

### Issue 3: Empty Plot Area
**Console Shows**: Plot generated but canvas blank

**Cause**: Data values might be zero or invalid

**Solution**:
1. Check console: "Values: [...]"
2. Verify values are non-zero
3. Try different property

---

### Issue 4: Pie Chart Shows Wrong Material
**Behavior**: Only shows first material

**Cause**: This is CORRECT behavior

**Explanation**: Pie charts compare properties within ONE material, so only first selected material is used

---

### Issue 5: Histogram Looks Empty
**Behavior**: Very few bars or gaps

**Cause**: Too few data points for 10 bins

**Solution**:
1. Select multiple materials
2. Select multiple properties
3. Use properties with more measurements

---

## 📊 Verification Steps

### Step 1: Check All Chart Types Work
```
For each chart type (Line, Bar, Scatter, Area, Pie, Histogram):
  1. Select test data
  2. Generate plot
  3. Verify chart appears
  4. Check console for success message
  5. ✅ Mark as working
```

### Step 2: Verify Data Fetching
```
1. Check console output
2. Look for "Properties found: [...]"
3. Verify selected properties are in list
4. Check "data points - Values: [...]" shows numbers
```

### Step 3: Test Error Handling
```
1. Select non-existent property
2. Generate plot
3. Should show error on plot area
4. Console should show traceback
```

### Step 4: Test Multi-Material
```
1. Select 3 materials
2. Select 2 properties
3. Generate Line chart
4. Should see 6 lines (3 × 2)
```

### Step 5: Test Export
```
1. Generate any chart
2. Click "Export Plot (PNG/PDF)"
3. Save as PNG
4. Verify file created
5. Open and check quality
```

---

## 🎯 Test Scenarios

### Scenario A: Material Comparison
**Goal**: Compare Copper vs Aluminum

**Test**:
```
Materials: Copper, Aluminum
Properties: density, thermal_conductivity
Chart: Bar
Expected: 2 groups of 2 bars each
Colors: Red (Copper), Blue (Aluminum)
```

**Verify**:
- [ ] Both materials show
- [ ] Both properties show
- [ ] Different colors
- [ ] Legend correct

---

### Scenario B: Single Material Analysis
**Goal**: Analyze all Copper properties

**Test**:
```
Material: Copper only
Properties: density, thermal_conductivity, specific_heat_capacity
Chart: Pie
Expected: Pie with 3 slices
Percentages: Should add to 100%
```

**Verify**:
- [ ] Pie chart appears
- [ ] 3 slices visible
- [ ] Percentages shown
- [ ] Totals 100%

---

### Scenario C: Data Distribution
**Goal**: See value spread

**Test**:
```
Materials: Copper, Aluminum, Nickel
Property: density
Chart: Histogram
Expected: Overlapping histograms
Bins: 10 bars
```

**Verify**:
- [ ] Histogram shows
- [ ] Multiple colors
- [ ] Frequency on Y-axis
- [ ] Value on X-axis

---

## 📋 Full Test Matrix

| Chart | Test Data | Expected Result | Status |
|-------|-----------|----------------|--------|
| Line | 1 material, 1 property | Single line | [ ] |
| Line | 2 materials, 2 properties | 4 lines | [ ] |
| Bar | 2 materials, 2 properties | Grouped bars | [ ] |
| Scatter | 1 material, 2 properties | Dot plot | [ ] |
| Area | 1 material, 1 property | Filled area | [ ] |
| Pie | 1 material, 3 properties | Pie slices | [ ] |
| Histogram | 2 materials, 1 property | Frequency bars | [ ] |

---

## 🚀 Run Tests Now

### Quick Test Commands:
```bash
# Start GUI
python run_gui.py

# In GUI:
1. Go to Material Browser → Select "Copper"
2. Go to Visualization tab → "Copper" auto-selected ✓
3. Select property: "density"
4. Test each chart type:
   - Line → Should work ✓
   - Bar → Should work ✓
   - Scatter → Should work ✓
   - Area → Should work ✓
   - Pie → Should work ✓
   - Histogram → Should work ✓
```

---

## ✅ Success Criteria

Plot generation is SUCCESSFUL if:

1. **Console Output**:
   - ✅ Shows "Plot generated successfully!"
   - ✅ No ERROR messages
   - ✅ Shows actual data values

2. **Visual Output**:
   - ✅ Chart appears in plot area
   - ✅ Correct chart type
   - ✅ Colors visible
   - ✅ Legend present

3. **Functionality**:
   - ✅ All 6 chart types work
   - ✅ Multi-material works
   - ✅ Dashboard updates
   - ✅ Export works

---

## 🎓 Debugging Tips

### Tip 1: Always Check Console
The console output tells you EXACTLY what's happening:
- What data was found
- What values were extracted
- Any errors encountered

### Tip 2: Start Simple
Begin with:
- 1 material
- 1 property
- Line chart

Then build up complexity.

### Tip 3: Verify Data First
Before plotting:
1. Check Material Browser tabs
2. Verify property exists
3. Look at actual values

### Tip 4: Use Debug Output
The console shows:
```
density: 1 data points - Values: [8940.0]
```
This confirms:
- Property exists ✓
- Has 1 data point ✓
- Value is 8940.0 ✓

---

## 📞 If Still Not Working

### Check These:
1. **Database**: Is data imported from XML?
2. **Properties**: Do they match database column names?
3. **Materials**: Are they in the database?
4. **Console**: What does debug output say?

### Get Help:
1. Copy console output
2. Note which chart type
3. Note selected materials/properties
4. Share error traceback

---

## 🎉 Summary

**Before**: Only Line and Bar charts, plotting issues
**Now**: 6 chart types, better debugging, error handling

**All Charts**:
1. Line ✅
2. Bar ✅
3. Scatter ✅ (NEW)
4. Area ✅ (NEW)
5. Pie ✅ (NEW)
6. Histogram ✅ (NEW)

**Features**:
- Better error messages
- Console debug output
- Error display on plot
- All charts exportable

**Ready to test!** 🚀
