# GUI Quick Start Guide

## Prerequisites

1. **Start PostgreSQL Database**
   - You're using **Postgres.app**
   - Open **Postgres.app** from Applications folder
   - Click **Start** button
   - Verify it's running (elephant icon in menu bar should be blue)

2. **Activate Python Environment**
   ```bash
   cd /Users/sridhars/Projects/materials_db
   source .venv/bin/activate
   ```

## Launch GUI

```bash
python run_gui.py
```

## GUI Features

### Main Window Layout

```
┌─────────────────────────────────────────────────────────────┐
│ Materials Database                                     [ ] × │
├─────────────────────────────────────────────────────────────┤
│ File  View  Tools  Help                                     │
│ [Export] [Refresh] [List Overrides]                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌───────────┐  ┌────────────────┐  ┌───────────────────┐  │
│  │ Material  │  │   Properties   │  │     Override      │  │
│  │  Browser  │  │                │  │    Management     │  │
│  │           │  │                │  │                   │  │
│  │ [Search]  │  │ ┌────────────┐ │  │  Property Path:   │  │
│  │           │  │ │Properties  │ │  │  [____________]   │  │
│  │ ▼ Metals  │  │ │Models      │ │  │                   │  │
│  │   • Al    │  │ │Overrides   │ │  │  Value:           │  │
│  │   • Cu    │  │ └────────────┘ │  │  [____________]   │  │
│  │           │  │                │  │                   │  │
│  │ ▼ Explosiv│  │ [Table with    │  │  [Apply Override] │  │
│  │   • RDX   │  │  properties]   │  │  [Clear Override] │  │
│  │   • TNT   │  │                │  │                   │  │
│  └───────────┘  └────────────────┘  └───────────────────┘  │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│ ✓ Database Connected │ 17 materials loaded                  │
└─────────────────────────────────────────────────────────────┘
```

### Left Panel: Material Browser
- **Search Box**: Filter materials by name
- **Categories**:
  - 🔩 Metals (Aluminum, Copper, Nickel, etc.)
  - 💥 Explosives (RDX, TNT, HMX, etc.)
  - 📦 Other (Helium, etc.)
- **Click** any material to view its properties

### Center Panel: Property Viewer
Three tabs showing material data:

1. **Properties Tab**
   - Thermal properties (Cp, K, etc.)
   - Mechanical properties (Density, Poisson's ratio)
   - Phase properties
   - Overrides highlighted in **GOLD**

2. **Models Tab**
   - ElasticModel (ThermoMechanical parameters)
   - ElastoPlastic (ShearModulus, YieldStrength, JohnsonCook)
   - Overrides highlighted in **GOLD**

3. **Overrides Tab**
   - List of ALL active overrides for this material
   - Shows: Property path, overridden value, unit, reason

### Right Panel: Override Management
- **Material**: Shows currently selected material
- **Property Path**: Enter path (e.g., `properties.Thermal.Cp`)
- **Value**: Enter new value (e.g., `400`)
- **Unit**: Enter unit (e.g., `J/kg/K`)
- **Reason**: Optional note
- **Buttons**:
  - `Apply Override`: Save the override
  - `Clear Override`: Remove existing override
- **Quick Templates**: Click to auto-fill common property paths

## Common Property Paths

### Properties
```
properties.Thermal.Cp          # Specific heat
properties.Thermal.K           # Thermal conductivity
properties.Mechanical.Density  # Density
properties.Mechanical.Nu       # Poisson's ratio
```

### Models - Direct Parameters
```
models.ElastoPlastic.ShearModulus      # Shear modulus
models.ElastoPlastic.YieldStrength     # Yield strength
models.ElasticModel.ThermoMechanical   # (If single value)
```

### Models - Nested Parameters
```
models.ElasticModel.ThermoMechanical.C11  # Elastic constant
models.ElasticModel.ThermoMechanical.C12
models.ElastoPlastic.JohnsonCook.A        # JC parameter A
models.ElastoPlastic.JohnsonCook.B        # JC parameter B
```

## Toolbar Actions

### Export Material
1. Select a material
2. Click **Export** button
3. Material exported to `export/output/<MaterialName>_exported.xml`
4. If overrides exist: `<MaterialName>_Override_exported.xml`

### Refresh
- Reload all materials from database
- Updates browser and current view

### List Overrides
- Shows dialog with ALL overrides across ALL materials
- Format: `MaterialName: property.path = value unit (reason)`

## Keyboard Shortcuts

- **Ctrl+E** / **Cmd+E**: Export current material
- **Ctrl+R** / **Cmd+R**: Refresh data
- **Ctrl+L** / **Cmd+L**: List all overrides
- **Ctrl+Q** / **Cmd+Q**: Quit application

## Status Bar

Bottom of window shows:
- **Connection Status**: ✓ Database Connected (green) or ✗ Database Error (red)
- **Material Count**: Number of materials loaded

## Workflow Examples

### Example 1: View Material Properties
1. Start Postgres.app
2. Launch GUI: `python run_gui.py`
3. Click "Copper" in browser
4. View properties in center panel
5. Check **Properties** tab for thermal/mechanical data
6. Check **Models** tab for elastic/plastic parameters
7. Check **Overrides** tab if any overrides exist

### Example 2: Set an Override
1. Select material (e.g., "Aluminum")
2. In Override panel, enter:
   - Property Path: `properties.Thermal.Cp`
   - Value: `900`
   - Unit: `J/kg/K`
   - Reason: `Updated from experiment`
3. Click **Apply Override**
4. Property viewer updates with gold highlight
5. Export to see override in XML

### Example 3: Clear an Override
1. Select material with override
2. Enter Property Path: `properties.Thermal.Cp`
3. Click **Clear Override**
4. Confirm in dialog
5. Gold highlight disappears

### Example 4: Export Material
1. Select material (e.g., "RDX")
2. Click **Export** toolbar button
3. Check `export/output/RDX_exported.xml`
4. If overrides exist: `export/output/RDX_Override_exported.xml`

## Troubleshooting

### GUI Won't Start
```bash
# Check PostgreSQL is running
open /Applications/Postgres.app

# Check Python environment
source .venv/bin/activate
python --version  # Should be 3.13.7

# Check dependencies
pip list | grep PyQt6
```

### Database Connection Error
1. Open Postgres.app
2. Click **Start** button
3. Wait for blue elephant icon
4. Restart GUI

### "Module not found" Error
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Override Not Applied
1. Check property path format (case-sensitive)
2. Verify material is selected
3. Check value is valid (numeric for most properties)
4. Use toolbar "List Overrides" to verify

## Theme

Professional dark theme with:
- **Background**: Dark gray (#2b2b2b)
- **Accent**: Blue (#0078d4)
- **Override**: Gold (#ffd700)
- **Error**: Red (#ff4444)
- **Success**: Green (#44ff44)

## Performance Tips

- GUI loads all 17 materials at startup (~2000+ parameters)
- First load may take 1-2 seconds
- Subsequent selections are instant (cached)
- Export is fast (< 100ms per material)

## Known Issues

None currently! If you find any:
1. Check PostgreSQL is running
2. Check Python environment is activated
3. Review error in status bar
4. Check terminal output for detailed errors

---

**Need Help?**
- See: `README.md` for full system documentation
- See: `COMMANDS_CHEATSHEET.md` for CLI commands
- See: `QUICKSTART.md` for database setup
