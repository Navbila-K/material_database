# 📚 Materials Database - Complete Documentation Summary

> **Comprehensive guide to the Materials Database project - All documentation in one place**

**Repository**: https://github.com/Navbila-K/material_database  
**Contributors**: Navbila-K, Sridhar1233sri  
**Last Updated**: December 22, 2025

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Quick Start Guide](#quick-start-guide)
3. [System Architecture](#system-architecture)
4. [Features & Capabilities](#features--capabilities)
5. [Installation & Setup](#installation--setup)
6. [Usage Guide](#usage-guide)
7. [Database Schema](#database-schema)
8. [GUI Components](#gui-components)
9. [Override System](#override-system)
10. [Visualization & Charts](#visualization--charts)
11. [References System](#references-system)
12. [Testing & Verification](#testing--verification)
13. [Troubleshooting](#troubleshooting)
14. [Command Reference](#command-reference)

---

## 🎯 Project Overview

### What is Materials Database?

A comprehensive **offline** materials database management system that stores, queries, visualizes, and manages material properties from XML files. Built for scientists and engineers working with material data.

### Key Features

✅ **PostgreSQL Database** - Stores 17 materials with properties, models, and references  
✅ **XML Parser** - Imports material data from XML files  
✅ **Modern GUI** - PyQt6-based interface with Material Browser and Visualization  
✅ **6 Chart Types** - Line, Bar, Scatter, Area, Pie, Histogram  
✅ **Dark/Light Themes** - Toggle between themes with adaptive colors  
✅ **Override System** - Modify values for testing without losing originals  
✅ **Reference Management** - Track 50+ scientific sources  
✅ **Export Functionality** - Export materials back to XML format  

### Technology Stack

- **Python 3.13** - Programming language
- **PostgreSQL** - Database system
- **PyQt6 6.10.1** - GUI framework
- **Matplotlib 3.7+** - Chart generation
- **psycopg2** - Database connector

### Materials Included (17 Total)

**Metals**: Aluminum, Copper, Nickel, Magnesium, Tantalum, Titanium, Tungsten  
**Gases**: Helium  
**Explosives**: TNT, RDX, HMX, PETN, TATB, CL-20, HNS  
**Others**: Sucrose, Nitromethane

---

## 🚀 Quick Start Guide

### For Beginners (GUI Mode)

```bash
# 1. Start the application
python run_gui.py

# 2. Browse materials
#    - Click "Material Browser" tab
#    - Select any material (e.g., Copper)
#    - View properties in tables

# 3. Create charts
#    - Click "Visualization" tab
#    - Select materials (Copper, Aluminum)
#    - Choose properties (density, cp)
#    - Pick chart type (Bar Chart)
#    - Click "Generate Plot"

# 4. Switch themes
#    - Click "☀️ Light Mode" button (top-right corner)
#    - Click "🌙 Dark Mode" to switch back
```

### For Experts (Command-Line Mode)

```bash
# List all materials
python main.py --list

# Query specific material
python main.py --query "name=Copper"

# Override a property value
python main.py --override "properties.Mechanical.Density" 9000 "Testing new value"

# Export material to XML
python main.py --export Copper

# List all overrides
python main.py --list-overrides Copper

# Clear overrides
python main.py --clear-overrides Copper
```

---

## 🏗️ System Architecture

### Data Flow

```
XML Files (Materials)
    ↓
XML Parser (reads & extracts metadata + properties)
    ↓
PostgreSQL Database (stores all data)
    ↓
    ├─→ GUI (Material Browser, Visualization)
    ├─→ Command-Line Tools (queries, overrides)
    └─→ Query & Fetch (retrieve material data)
         ↓
    Override Panel (user edits parameters)
         ↓
    Override Manager (applies changes in memory)
         ↓
    Active View (combined original + overrides)
         ↓
    Export to XML
```

**Visual Flowchart**: See `Flowchart.jpg` in repository

### Database Structure

**5 Main Tables**:
1. **materials** - Basic material information (name, ID, version)
2. **property_categories** - Organized by category (Mechanical, Thermal, etc.)
3. **properties** - Individual properties with entries
4. **models** - Material behavior models (Elastic, Plastic, Reaction, EOS)
5. **references** - Scientific sources and citations

---

## ✨ Features & Capabilities

### Material Browser
- ✅ View all 17 materials in a list
- ✅ Click to see detailed properties
- ✅ Organized by categories (Mechanical, Thermal, Chemical, Optical)
- ✅ Color-coded property tables
- ✅ Search and filter materials

### Visualization Dashboard
- ✅ **6 Chart Types**: Line, Bar, Scatter, Area, Pie, Histogram
- ✅ Multi-material comparison
- ✅ Multi-property selection
- ✅ Interactive zoom/pan tools
- ✅ Export charts (PNG, PDF, SVG)
- ✅ Statistics dashboard (avg, min, max)
- ✅ Auto-sync with Material Browser

### Override System
- ✅ Modify any property value for testing
- ✅ Original values remain safe
- ✅ Track who changed what and when
- ✅ Switch between "Original" and "Active View"
- ✅ Clear overrides individually or all at once
- ✅ Export with overrides applied

### References Browser
- ✅ View 50+ scientific sources
- ✅ Filter by type (Journal, Conference, Report, Book)
- ✅ Search by keyword
- ✅ See which materials use each reference
- ✅ Full citation details

### Theme System
- ✅ Dark Mode (default) - Easy on eyes
- ✅ Light Mode - Bright during daytime
- ✅ All text readable in both modes
- ✅ Charts adapt automatically
- ✅ Toolbar icons change color
- ✅ One-click toggle button

---

## 💾 Installation & Setup

### Prerequisites

```bash
# Python 3.13 (recommended) or 3.11+
python --version

# PostgreSQL 12+ installed and running
psql --version
```

### Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/Navbila-K/material_database.git
cd material_database

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure database (edit config.py)
DB_CONFIG = {
    'host': 'localhost',
    'database': 'Materials_DB',
    'user': 'postgres',
    'password': 'your_password'
}

# 4. Create database and load data
createdb Materials_DB
python main.py --load-xml xml/

# 5. Run GUI
python run_gui.py
```

### Dependencies

```txt
PyQt6==6.10.1
matplotlib>=3.7.0
numpy>=1.24.0
psycopg2-binary>=2.9.9
```

---

## 📖 Usage Guide

### GUI Mode

#### Material Browser Tab

1. **View Materials**:
   - Left panel shows material list (17 materials)
   - Click any material to see details
   - Properties displayed in organized tables

2. **View Properties**:
   - **Original Data** tab - Shows database values
   - **Active View** tab - Shows values with overrides applied
   - **References** tab - Shows scientific sources

3. **Property Categories**:
   - Mechanical (Density, Elastic/Plastic models)
   - Thermal (Heat capacity, conductivity)
   - Chemical (Reaction models)
   - Optical (Refractive index)

#### Visualization Tab

1. **Select Materials**:
   - Use dropdown to select one or more materials
   - Multi-select: Hold Ctrl/Cmd and click

2. **Select Properties**:
   - Choose what to compare (density, cp, cv, viscosity)
   - Multi-select supported

3. **Choose Chart Type**:
   - **Line Chart**: Good for trends
   - **Bar Chart**: Good for comparing averages
   - **Scatter Plot**: See all individual data points
   - **Area Chart**: Filled region under curve
   - **Pie Chart**: Percentage distribution
   - **Histogram**: Value frequency distribution

4. **Generate & Export**:
   - Click "Generate Plot" button
   - Use toolbar to zoom, pan, save
   - Export as PNG/PDF using save button

#### Override Panel

1. **Create Override**:
   - Select material
   - Choose property path (e.g., `properties.Mechanical.Density`)
   - Enter new value
   - Add comment/reason
   - Click "Apply Override"

2. **View Overrides**:
   - Click "List Overrides" button
   - See all active overrides
   - Switch to "Active View" tab to see modified values

3. **Clear Overrides**:
   - Click "Clear Override" for specific property
   - Or clear all overrides at once

#### References Browser

1. **Open Browser**:
   - Menu → Tools → References
   - Or click "References" in toolbar

2. **Search & Filter**:
   - Type in search box
   - Filter by type dropdown
   - Click "Reset Filters" to clear

3. **View Details**:
   - Click any reference to see full details
   - See which materials use it

### Command-Line Mode

#### Basic Commands

```bash
# List all materials
python main.py --list

# Query material by name
python main.py --query "name=Copper"

# Query by property
python main.py --query "density>8000"

# Show material details
python main.py --material Aluminum
```

#### Override Commands

```bash
# Set override
python main.py --override "properties.Mechanical.Density" 9000 "Testing"

# List overrides for material
python main.py --list-overrides Copper

# Clear specific override
python main.py --clear-override Copper "properties.Mechanical.Density"

# Clear all overrides
python main.py --clear-overrides Copper
```

#### Export Commands

```bash
# Export single material
python main.py --export Copper

# Export with overrides
python main.py --export Copper --with-overrides

# Export all materials
python main.py --export-all
```

---

## 🗄️ Database Schema

### Core Tables

#### materials
```sql
material_id    SERIAL PRIMARY KEY
xml_id         VARCHAR(50) UNIQUE
name           VARCHAR(100) NOT NULL
author         VARCHAR(200)
date           VARCHAR(50)
version        VARCHAR(50)
created_at     TIMESTAMP DEFAULT NOW()
```

#### property_categories
```sql
category_id    SERIAL PRIMARY KEY
material_id    INTEGER REFERENCES materials(material_id)
category_name  VARCHAR(100)  -- Mechanical, Thermal, Chemical, Optical
```

#### properties
```sql
property_id    SERIAL PRIMARY KEY
category_id    INTEGER REFERENCES property_categories(category_id)
property_name  VARCHAR(100)  -- Density, Cp, Cv, etc.
unit           VARCHAR(50)
```

#### property_entries
```sql
entry_id       SERIAL PRIMARY KEY
property_id    INTEGER REFERENCES properties(property_id)
value          VARCHAR(500)
ref_id         VARCHAR(50)
comment        TEXT
```

#### models
```sql
model_id       SERIAL PRIMARY KEY
material_id    INTEGER REFERENCES materials(material_id)
model_type     VARCHAR(50)  -- ElasticModel, PlasticModel, etc.
model_name     VARCHAR(100)
```

#### references
```sql
reference_id   INTEGER PRIMARY KEY
ref_type       VARCHAR(50)  -- article, conference, report, book
author         TEXT
year           VARCHAR(10)
title          TEXT
journal        TEXT
volume         VARCHAR(50)
pages          VARCHAR(50)
```

### Relationships

```
materials (1) ──→ (Many) property_categories
property_categories (1) ──→ (Many) properties
properties (1) ──→ (Many) property_entries
materials (1) ──→ (Many) models
references (1) ──→ (Many) property_entries (via ref_id)
```

---

## 🖥️ GUI Components

### Main Window (`gui/main_window.py`)

- Menu bar (File, Tools, Help)
- Toolbar with action buttons
- Tab widget (Material Browser, Visualization)
- Status bar (connection status)
- **Theme toggle button** (top-right corner)

### Material Browser (`gui/views/material_browser.py`)

- Tree view of all materials
- Material count statistics
- Click to select material

### Property Viewer (`gui/views/property_viewer.py`)

- Tabbed view (Original Data, Active View, References)
- Color-coded property tables
- Category organization
- Export button

### Visualization Tab (`gui/views/visualization_tab.py`)

- **Control Panel** (left 25%):
  - Material selector (multi-select dropdown)
  - Property selector (multi-select list)
  - View mode selector (Original/Active)
  - Chart type selector (6 types)
  - Generate button

- **Plot Area** (center 50%):
  - Matplotlib canvas
  - Interactive toolbar (zoom, pan, save)
  - Chart display

- **Dashboard** (right 25%):
  - Statistics cards (Total points, Average, Min, Max)
  - Details panel
  - Reference tracking

### Override Panel (`gui/views/override_panel.py`)

- Material display
- Property path input
- Value input
- Comment/reason text
- Apply/Clear buttons
- Quick templates

### References Browser (`gui/views/reference_browser_dialog.py`)

- Search box
- Type filter dropdown
- Reference count label
- Table view with all references
- Export functionality

---

## 🔧 Override System

### How It Works

1. **Storage**: Overrides stored in separate database table
2. **Memory**: Applied dynamically when viewing "Active View"
3. **Preservation**: Original values never modified
4. **Tracking**: Records who, when, and why

### Override Data Structure

```python
{
    'material_id': 3,
    'material_name': 'Copper',
    'property_path': 'properties.Mechanical.Density',
    'original_value': '8940',
    'override_value': '9000',
    'comment': 'Testing higher density',
    'created_at': '2025-12-22 10:30:00',
    'created_by': 'user'
}
```

### Property Path Format

```
properties.CategoryName.PropertyName
models.ModelType.ParameterName
models.ModelType.SubModel.ParameterName
```

### Examples

```bash
# Override density
properties.Mechanical.Density

# Override specific heat
properties.Thermal.Cp

# Override elastic model parameter
models.ElasticModel.YoungsModulus

# Override plastic model nested parameter
models.PlasticModel.JohnsonCook.A
```

### GUI Workflow

1. Select material in Material Browser
2. Go to Override Panel
3. Choose property or use template
4. Enter new value and comment
5. Click "Apply Override"
6. Switch to "Active View" tab to see changes
7. Export with overrides if needed

### Command-Line Workflow

```bash
# Set override
python main.py --override "properties.Mechanical.Density" 9000 "Testing"

# View in Active View
python main.py --material Copper --active-view

# Export with overrides
python main.py --export Copper --with-overrides

# Clear when done
python main.py --clear-overrides Copper
```

---

## 📊 Visualization & Charts

### Chart Types & Use Cases

#### 1. Line Chart
- **Best for**: Trends over time or ordered data
- **Example**: Temperature vs density
- **Features**: Markers, line styles, multiple series

#### 2. Bar Chart
- **Best for**: Comparing averages across materials
- **Example**: Average density of Copper vs Aluminum
- **Features**: Grouped bars, different colors per material

#### 3. Scatter Plot
- **Best for**: Seeing individual data points
- **Example**: All density measurements with references
- **Features**: Point markers, white edges for visibility

#### 4. Area Chart
- **Best for**: Filled regions, cumulative data
- **Example**: Range of property values
- **Features**: Semi-transparent fill, boundary lines

#### 5. Pie Chart
- **Best for**: Percentage distribution
- **Example**: Property value distribution for one material
- **Features**: Auto-percentages, exploded slices

#### 6. Histogram
- **Best for**: Value frequency distribution
- **Example**: How many measurements fall in each range
- **Features**: Automatic binning, bar counts

### Chart Customization

- **Colors**: Automatic color cycling per material
- **Labels**: Auto-generated axis labels with units
- **Title**: Shows materials and properties
- **Legend**: Material names with colors
- **Grid**: Optional gridlines
- **Theme**: Adapts to dark/light mode

### Toolbar Features

- **Home**: Reset to original view
- **Back/Forward**: Navigation history
- **Pan**: Move around the chart
- **Zoom**: Zoom to rectangle
- **Configure**: Adjust subplot parameters
- **Save**: Export as PNG/PDF/SVG

### Export Options

```python
# From GUI: Use toolbar save button
# Formats: PNG (default), PDF, SVG, EPS
# Resolution: 300 DPI for publications

# From code:
fig.savefig('chart.png', dpi=300, bbox_inches='tight')
```

---

## 📚 References System

### Reference Data Structure

```python
{
    'reference_id': 112,
    'ref_type': 'article',
    'author': 'Smith, J. and Doe, A.',
    'year': '2020',
    'title': 'Material Properties of Copper',
    'journal': 'Journal of Materials Science',
    'volume': '45',
    'pages': '123-145'
}
```

### Reference Types

- **article** - Journal articles
- **conference** - Conference papers
- **report** - Technical reports
- **book** - Book chapters
- **misc** - Other sources
- **chapter** - Book chapters

### Linking to Materials

References linked via `ref_id` in:
- **property_entries**: Property values cite references
- **model_parameters**: Model parameters cite references

### Usage Statistics

```sql
-- Find most cited references
SELECT r.reference_id, r.author, r.title, COUNT(*) as citations
FROM references r
JOIN property_entries pe ON r.reference_id = pe.ref_id::integer
GROUP BY r.reference_id
ORDER BY citations DESC;
```

### Citation Format

```
[ID] Author (Year) Title. Journal, vol. Volume, pp. Pages
```

**Example**:
```
[112] Smith, J. (2020) Material Properties of Copper. Journal of Materials Science, vol. 45, pp. 123-145
```

---

## ✅ Testing & Verification

### Automated Tests

#### Chart Verification (`verify_all_charts.py`)

```bash
python verify_all_charts.py
```

**Output**:
```
✓ Line         : PASS
✓ Bar          : PASS
✓ Scatter      : PASS
✓ Area         : PASS
✓ Pie          : PASS
✓ Histogram    : PASS

6/6 TESTS PASSED
```

**Generated Files**: `chart_verification_output/*.png`

#### Database Verification

```bash
# Check data completeness
python check_visualization_readiness.py

# Run test queries
psql -U postgres -d Materials_DB -f REFERENCES_TEST_QUERIES.sql
```

### Manual Testing

#### GUI Testing Checklist

- [ ] Material Browser loads all 17 materials
- [ ] Property tables display correctly
- [ ] Visualization tab creates all 6 chart types
- [ ] Theme toggle works (dark/light)
- [ ] Toolbar icons visible in both themes
- [ ] Override system applies changes
- [ ] Export generates XML files
- [ ] References browser shows all references

#### Command-Line Testing

```bash
# Test listing
python main.py --list

# Test query
python main.py --query "name=Copper"

# Test override
python main.py --override "properties.Mechanical.Density" 9000 "Test"
python main.py --list-overrides Copper
python main.py --clear-overrides Copper

# Test export
python main.py --export Aluminum
```

### Bug Fixes Applied

#### Bug #1: Matplotlib Backend Conflict
- **Problem**: Charts wouldn't show
- **Solution**: Set `matplotlib.use('QtAgg', force=True)`
- **Status**: ✅ Fixed

#### Bug #2: No Data Extraction
- **Problem**: Empty charts
- **Solution**: Rewrote `fetch_material_data()` for hierarchical structure
- **Status**: ✅ Fixed

#### Bug #3: Text Visibility in Light Mode
- **Problem**: Light text on light background
- **Solution**: Created separate light/dark stylesheets
- **Status**: ✅ Fixed

#### Bug #4: Toolbar Icons Not Visible
- **Problem**: Light icons on light background
- **Solution**: Added icon inversion for light mode
- **Status**: ✅ Fixed

#### Bug #5: ComboBox Text Not Visible
- **Problem**: Blue selection background hides text
- **Solution**: Explicit selection color styles
- **Status**: ✅ Fixed

---

## 🔍 Troubleshooting

### Common Issues

#### Database Connection Failed

```
Error: could not connect to server
```

**Solution**:
1. Check PostgreSQL is running: `pg_isready`
2. Verify credentials in `config.py`
3. Ensure database exists: `psql -l | grep Materials_DB`

#### GUI Won't Start

```
ImportError: No module named 'PyQt6'
```

**Solution**:
```bash
pip install -r requirements.txt
```

#### Charts Not Showing

```
Backend error or blank canvas
```

**Solution**:
1. Check `run_gui.py` has matplotlib setup
2. Verify backend: `python -c "import matplotlib; print(matplotlib.get_backend())"`
3. Should output: `QtAgg`

#### Theme Not Changing

```
Stylesheets not loading
```

**Solution**:
1. Check `gui/resources/styles.qss` exists
2. Check `gui/resources/styles_light.qss` exists
3. Verify file permissions

#### Override Not Applying

```
Active View shows original value
```

**Solution**:
1. Check override was saved: `python main.py --list-overrides MaterialName`
2. Ensure you're viewing "Active View" tab, not "Original Data"
3. Try refreshing: Close and reopen material

### Performance Issues

#### Slow Startup

**Causes**:
- Large database
- Many materials

**Solutions**:
- Use indexed queries
- Lazy load properties
- Cache frequently accessed data

#### Chart Generation Slow

**Causes**:
- Too many data points
- Complex calculations

**Solutions**:
- Limit data points displayed
- Use downsampling for large datasets
- Pre-calculate statistics

---

## 📝 Command Reference

### Main Commands

```bash
# List materials
python main.py --list
python main.py -l

# Query
python main.py --query "name=Copper"
python main.py -q "density>8000"

# Material details
python main.py --material Aluminum
python main.py -m Copper
```

### Override Commands

```bash
# Set override
python main.py --override PATH VALUE "COMMENT"
python main.py -o properties.Mechanical.Density 9000 "Test"

# List overrides
python main.py --list-overrides MATERIAL
python main.py --list-overrides Copper

# Clear override
python main.py --clear-override MATERIAL PATH
python main.py --clear-override Copper properties.Mechanical.Density

# Clear all overrides
python main.py --clear-overrides MATERIAL
python main.py --clear-overrides Copper
```

### Export Commands

```bash
# Export single material
python main.py --export MATERIAL
python main.py --export Aluminum

# Export with overrides
python main.py --export MATERIAL --with-overrides
python main.py --export Copper --with-overrides

# Export all materials
python main.py --export-all

# Export to specific directory
python main.py --export Copper --output export/
```

### Database Commands

```bash
# Load XML files
python main.py --load-xml xml/

# Load single file
python main.py --load-xml xml/Copper.xml

# Reload all data (WARNING: Clears database)
python main.py --reload-all
```

### GUI Commands

```bash
# Start GUI
python run_gui.py

# Start with specific material
python run_gui.py --material Copper

# Start in light mode
python run_gui.py --light-mode
```

---

## 📖 Additional Resources

### Documentation Files (Local Only)

The following detailed documentation files are available in your local repository:

**Quick Guides**:
- `QUICKSTART.md` - Getting started guide
- `GUI_QUICKSTART.md` - GUI user guide
- `COMMANDS_CHEATSHEET.md` - Command reference card

**Feature Documentation**:
- `OVERRIDE_GUIDE.md` - Override system detailed guide
- `OVERRIDE_USAGE_GUIDE.md` - Override examples
- `GUI_REFERENCES_USER_GUIDE.md` - References browser guide
- `VISUALIZATION_TAB_GUIDE.md` - Visualization features
- `CHART_TYPES_GUIDE.md` - All chart types explained

**Technical Documentation**:
- `SCHEMA_ANALYSIS.md` - Database schema details
- `IMPLEMENTATION_SUMMARY.md` - Architecture overview
- `REFERENCES_IMPLEMENTATION_PLAN.md` - References system design

**Verification Reports**:
- `CHART_VERIFICATION_REPORT.md` - Chart testing results
- `VERIFICATION_REPORT.md` - Complete system verification
- `TESTING.md` - Testing procedures

**Development History**:
- `Whole_idea.md` - Complete project story (simple English)
- `PHASE3_COMPLETION.md` - Development phases
- `FIX_SUMMARY.md` - Bug fixes applied

### External Resources

- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **PyQt6 Documentation**: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- **Matplotlib Documentation**: https://matplotlib.org/stable/contents.html

---

## 👥 Contributors & Credits

**Repository Owner**: Navbila-K (https://github.com/Navbila-K)  
**Collaborator**: Sridhar1233sri (https://github.com/Sridhar1233sri)

**Built with**:
- Python, PostgreSQL, PyQt6, Matplotlib
- Coffee ☕☕☕ and determination!

---

## 📄 License & Usage

This project is for educational and research purposes. Please cite the repository if using in academic work.

---

## 🎯 Summary Statistics

- **Total Files**: 56+ Python modules and scripts
- **Lines of Code**: 13,000+ lines
- **Materials**: 17 materials loaded
- **Properties**: ~50-100 per material
- **References**: 50+ scientific sources
- **Chart Types**: 6 visualization options
- **Themes**: 2 (Dark & Light)
- **Documentation**: 37 MD files (consolidated here)

---

## 🚀 Next Steps

### For New Users
1. Read the [Quick Start Guide](#quick-start-guide)
2. Install the application following [Installation & Setup](#installation--setup)
3. Run `python run_gui.py` and explore!

### For Developers
1. Review [System Architecture](#system-architecture)
2. Check [Database Schema](#database-schema)
3. Read [GUI Components](#gui-components)
4. See `Flowchart.jpg` for visual overview

### For Scientists
1. Explore materials in Material Browser
2. Create comparison charts in Visualization tab
3. Use Override System for testing scenarios
4. Export modified data for simulations

---

**This document consolidates 37 separate documentation files into one comprehensive reference.**

For the complete project story explained in simple English, see `Whole_idea.md` in your local repository.

**Repository**: https://github.com/Navbila-K/material_database

*Last updated: December 22, 2025*
