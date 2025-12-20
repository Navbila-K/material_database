# Visualization Tab - Quick Start Guide

## Overview
A new **Visualization** tab has been added to the Materials Database GUI for offline data visualization and comparison.

## Features

### 3-Panel Layout

**LEFT: Control Panel**
- Multi-select material list (Ctrl/Cmd + Click)
- Multi-select property list
- Chart type selector (Line / Bar)
- "Generate Plot" button
- "Export Plot (PNG/PDF)" button

**CENTER: Plot Area**
- Embedded matplotlib canvas
- Interactive navigation toolbar (zoom, pan, save)
- Multi-material overlay with distinct colors
- Grid and legend enabled
- Professional axis labels

**RIGHT: Dashboard**
- **Materials Selected** - Count of selected materials
- **Properties Selected** - Count of selected properties  
- **Data Points** - Total number of data points plotted
- **Missing Values** - Count of missing property values
- **Details Panel** - Summary text

## Usage

### Step 1: Open Visualization Tab
Click on the **"Visualization"** tab in the main window

### Step 2: Select Materials
- Hold Ctrl (Windows/Linux) or Cmd (Mac)
- Click multiple materials from the list

### Step 3: Select Properties
- Hold Ctrl/Cmd and click multiple properties
- Available properties:
  - density
  - specific_heat_capacity
  - thermal_conductivity
  - thermal_expansion
  - youngs_modulus
  - shear_modulus
  - poissons_ratio
  - electrical_conductivity

### Step 4: Choose Chart Type
- **Line**: Shows trends across data points
- **Bar**: Compares average values

### Step 5: Generate Plot
Click **"Generate Plot"** button

### Step 6: Export (Optional)
Click **"Export Plot (PNG/PDF)"** to save

## Chart Features

### Line Chart
- Each material-property combination gets a unique line
- Markers show individual data points
- Legend identifies each series
- Grid for easy reading

### Bar Chart
- Grouped bars by property
- Each material has a distinct color
- Shows average values
- Rotated x-axis labels for readability

## Color Scheme
- Materials cycle through 8 distinct colors:
  - Red (#e74c3c)
  - Blue (#3498db)
  - Green (#2ecc71)
  - Orange (#f39c12)
  - Purple (#9b59b6)
  - Teal (#1abc9c)
  - Dark Orange (#e67e22)
  - Dark Gray (#34495e)

## Data Handling

### Data Source
- Fetches data from PostgreSQL database
- Applies user overrides automatically
- Extracts both scalar and table values

### Missing Data
- Materials without selected properties show zero/missing
- Dashboard counts missing values
- Empty selections handled gracefully

## Export Options

### PNG
- High resolution (300 DPI)
- Suitable for presentations

### PDF
- Vector format
- Suitable for publications
- Maintains quality at any scale

## Tips

1. **Start Small**: Select 1-2 materials and properties first
2. **Compare**: Use Line chart for trends, Bar chart for averages
3. **Zoom**: Use toolbar to zoom into specific regions
4. **Save**: Export before changing selections

## Technical Details

### Framework
- **PyQt6** for GUI
- **matplotlib** for plotting (offline)
- **numpy** for calculations

### Performance
- Limits table data to 20 points per property
- Efficient database queries
- Fast rendering with matplotlib

### Offline Operation
- ✅ No internet required
- ✅ All processing local
- ✅ Database queries via PostgreSQL

## Troubleshooting

**Q: Plot shows "No data available"**
- Ensure materials have the selected properties in database
- Check if XML data was imported correctly

**Q: Export button doesn't work**
- Generate a plot first
- Check file system permissions

**Q: No materials showing**
- Verify database connection
- Check that materials table has entries

## Integration

The Visualization tab is fully integrated with:
- Existing database connection
- MaterialQuerier for data fetching
- Override system (automatically applied)

No changes were made to existing tabs or functionality.

---

**Ready to visualize your materials data!** 📊
