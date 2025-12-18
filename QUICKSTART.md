# Material Database Engine - Quick Start Guide

## Overview

This is a professional, solver-safe material database system that preserves XML structure exactly while providing powerful database storage and querying capabilities.

## Installation (Already Complete)

Your system is ready to use! The following components are installed:

✅ Python virtual environment (`.venv/`)  
✅ Required dependencies (psycopg2-binary)  
✅ Database schema created  
✅ Sample materials imported (Copper, RDX)  

## Database Connection

Currently configured:
```
postgresql://sridhars:mypassword@localhost:5432/Materials_DB
```

To change: Edit `config.py`

## Quick Commands

### List Materials
```bash
python main.py list
```

### Import Material
```bash
# Single material
python main.py import xml/Aluminum.xml

# All materials
python main.py import-all
```

### Query Material
```bash
python main.py query Copper
python main.py query RDX
```

### Export Material
```bash
# Single material
python main.py export Copper

# All materials  
python main.py export-all
```

Exported files go to: `export/output/`

### Reset Database
```bash
python main.py reset
```
⚠️ **WARNING**: Deletes all data!

## Example Workflow

```bash
# 1. Check what's in the database
python main.py list

# 2. Import a new material
python main.py import xml/Aluminum.xml

# 3. View its details
python main.py query Aluminum

# 4. Export it back to XML
python main.py export Aluminum

# 5. Compare with original
diff xml/Aluminum.xml export/output/Aluminum_exported.xml
```

## Understanding the Output

### List Command
```
ID    Name                 XML ID               Version        
----------------------------------------------------------------------
2     Copper               COPPER-001           0.0.0-0FA756E6 
3     RDX                  RDX-001              0.0.0-4753428F
```

### Query Command
```
Material: Copper
======================================================================

--- METADATA ---
  id: COPPER-001
  name: Copper
  
--- PROPERTIES ---
  Thermal:
    Density (kg/m^3): 4 entries
      - 8940 [ref: 107]
      - 8930 [ref: 109]
      
--- MODELS ---
  ElasticModel
  ElastoPlastic
  ReactionModel
  EOSModel
```

## Available Materials

Currently in `xml/` directory:
- Aluminum
- CL-20
- Copper ✅ (imported)
- HELIUM
- HMX
- HNS
- MAGNESIUM
- Nickel
- Nitromethane
- PETN
- RDX ✅ (imported)
- Sucrose
- TANTALUM
- TATB
- TITANIUM
- TNT
- TUNGSTEN

## Project Structure

```
materials_db/
├── xml/                    # Source XML files
├── export/output/          # Exported XML files
├── parser/                 # XML parsing
├── db/                     # Database operations
├── overrides/              # Override logic
├── main.py                 # Main CLI
└── config.py               # Configuration
```

## Common Tasks

### Task 1: Import All Materials
```bash
python main.py import-all
```
This imports all 17 materials from the `xml/` directory.

### Task 2: Export All Materials
```bash
python main.py export-all
```
This exports all materials to `export/output/`

### Task 3: Compare Original vs Exported
```bash
# Export a material
python main.py export Copper

# Compare (should be structurally identical)
diff xml/Copper.xml export/output/Copper_exported.xml
```

### Task 4: Fresh Start
```bash
# Reset database
python main.py reset

# Reimport materials
python main.py import-all
```

## Testing Modules Individually

### Test Parser
```bash
python parser/xml_parser.py
```

### Test Database Connection
```bash
python db/database.py
```

### Test Query
```bash
python db/query.py
```

### Test Export
```bash
python export/xml_exporter.py
```

### Test Overrides
```bash
python overrides/override_manager.py
```

## What's Preserved

✅ Empty XML tags (`<Entry/>`)  
✅ Scientific notation (`13E9`, `0.385`)  
✅ Units (`kg/m^3`, `J/kg/K`)  
✅ References (`ref="107"`)  
✅ Tag order and hierarchy  
✅ Attributes (`index="1"`, `meaning="schema_version"`)  

## What's NOT Done

- Physics calculations
- Model evaluation
- Unit conversion
- Data validation
- Reference parsing (References.xml not imported yet)

## Core Philosophy

**"Structure is fixed. Data is flexible."**

This system:
- Treats XML as truth
- Never modifies original files
- Works with ANY material
- Preserves solver compatibility
- Stores data, doesn't compute

## Need Help?

1. Check `README.md` for detailed documentation
2. Check `IMPLEMENTATION_SUMMARY.md` for technical details
3. Review error messages (they're descriptive)
4. Test with individual modules first

## Next Steps

After importing all materials, you can:

1. Query any material by name
2. Export materials for solver use
3. Implement override logic for reference selection
4. Add GUI layer (future phase)
5. Implement batch operations (future phase)

---

**Status**: System is operational and tested ✅  
**Version**: Phase 1 Complete  
**Ready for**: Production use

Remember: This is a **DATA MANAGEMENT** system, not a physics engine!
