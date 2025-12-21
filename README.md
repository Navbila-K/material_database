# Materials Database System



A comprehensive PostgreSQL-based materials database system for storing, querying, and managing material properties with XML import/export capabilities and advanced override functionality.A professional, solver-safe material data management system that treats XML as the source of truth and provides structured storage, querying, and export capabilities.



## 🚀 Features## Project Philosophy



- **XML Parsing**: Import material data from XML files into PostgreSQL database**Structure is fixed. Data is flexible.**

- **Advanced Querying**: Query materials with flexible filtering and formatting

- **Override System**: Non-destructive value overrides and reference preferencesThis system:

- **XML Export**: Export materials back to XML format with override detection- ✓ Preserves XML structure exactly

- **17 Materials**: Pre-loaded database with metals, explosives, and other materials- ✓ Never infers or computes physics values

- **2,000+ Parameters**: Comprehensive material property coverage- ✓ Maintains solver compatibility

- ✓ Stores empty tags as NULL (never removes them)

## 📋 Table of Contents- ✓ Works with ANY material without code changes

- ✓ Exports solver-ready XML that matches original schema

- [Quick Start](#quick-start)

- [Installation](#installation)## Architecture

- [Database Setup](#database-setup)

- [Usage Guide](#usage-guide)```

- [Override System](#override-system)project/

- [Project Structure](#project-structure)│

- [Requirements](#requirements)├── xml/                # Source XML files (read-only)

├── parser/             # XML → Python dictionaries

---├── db/                 # PostgreSQL schema & operations

├── export/             # DB → Solver-compatible XML

## 🎯 Quick Start├── overrides/          # Query-time override logic

├── validation/         # Future: Schema validation

### Prerequisites├── config.py           # Configuration

- Python 3.13+├── main.py             # CLI interface

- PostgreSQL 18.1+└── requirements.txt    # Dependencies

- `psycopg2` library```



### Installation## Database Schema



1. **Clone the repository**The PostgreSQL schema mirrors XML hierarchy exactly:

```bash

git clone https://github.com/Navbila-K/material_database.git- **materials** - One row per material file

cd material_database- **property_categories** - Phase, Thermal, Mechanical

```- **properties** - Density, Cp, Cv, etc.

- **property_entries** - Actual values with refs and units

2. **Install Python dependencies**- **models** - ElasticModel, ElastoPlastic, ReactionModel, EOSModel

```bash- **sub_models** - ThermoMechanical, Rows, etc.

pip install -r requirements.txt- **model_parameters** - Individual model values

```- **references** - Bibliographic references



3. **Configure database connection**All numeric values stored as TEXT to preserve scientific notation (e.g., "13E9").



Edit `config.py` with your PostgreSQL credentials:## Installation

```python

DB_CONFIG = {```bash

    'dbname': 'Materials_DB',# Create virtual environment

    'user': 'your_username',python -m venv .venv

    'password': 'your_password',source .venv/bin/activate  # On Windows: .venv\Scripts\activate

    'host': 'localhost',

    'port': 5432# Install dependencies

}pip install -r requirements.txt

```

# Update config.py with your database credentials

4. **Create database**# Default: postgresql://sridhars:mypassword@localhost:5432/Materials_DB

```bash```

# In PostgreSQL

createdb Materials_DB## Quick Start



# Or using psql```bash

psql -U postgres# 1. Initialize database schema

CREATE DATABASE "Materials_DB";python main.py init

\q

```# 2. Import all materials from xml/

python main.py import-all

5. **Initialize database schema**

```bash# 3. List materials

python main.py initpython main.py list

```

# 4. Query a material

6. **Import materials from XML**python main.py query Copper

```bash

python main.py import-all# 5. Export material back to XML

```python main.py export Copper



---# 6. Export all materials

python main.py export-all

## 📖 Usage Guide```



### Basic Commands## Usage



#### 1. List All Materials### Initialize Database

```bash```bash

python main.py listpython main.py init

``````

Creates all tables, indexes, and schema. Safe to run multiple times.

#### 2. Query a Material

```bash### Import Materials

python main.py query Copper```bash

```# Import single material

python main.py import xml/Copper.xml

#### 3. Export Material to XML

```bash# Import all materials

python main.py export Copperpython main.py import-all

# Exports to: export/output/Copper_exported.xml```

# With overrides: export/output/Copper_Override_exported.xml

```### Query Materials

```bash

#### 4. Import Single Material# List all materials

```bashpython main.py list

python main.py import xml/Aluminum.xml

```# View material details

python main.py query Copper

---python main.py query RDX

```

## 🎛️ Override System

### Export Materials

The override system allows you to modify material values **without changing the original database**.```bash

# Export single material

### Set Value Overridepython main.py export Copper

```bash

python main.py set-override Copper properties.Thermal.Cp 400 --unit "J/kg/K" --reason "Lab measurement"# Export all materials

```python main.py export-all

```

### Set Reference PreferenceExported files saved to `export/output/`

```bash

python main.py set-preference Copper properties.Mechanical.Density 121 --reason "Most reliable source"### Override System (Phase 3)

```

**Safely customize material data without modifying original database values.**

### List Overrides

```bash```bash

python main.py list-overrides Copper# Set preferred reference (when multiple values exist)

```python main.py set-preference Aluminum properties.Mechanical.Density 121



### Clear Overrides# Set custom value override

```bashpython main.py set-override Aluminum properties.Mechanical.Density 2750 kg/m^3 "Lab measurement"

# Clear specific override

python main.py clear-overrides Copper properties.Thermal.Cp# List all overrides

python main.py list-overrides Aluminum

# Clear all overrides

python main.py clear-overrides Copper# Clear overrides

```python main.py clear-overrides Aluminum

```

### Property Path Formats

**Key Features:**

**Properties (3 parts):**- ✅ Original data NEVER modified

```- ✅ Overrides applied at query/export time

properties.Category.PropertyName- ✅ Works with properties and model parameters

```- ✅ Persists across sessions

Examples: `properties.Thermal.Cp`, `properties.Mechanical.Density`

📖 **Full Guide**: See [OVERRIDE_GUIDE.md](OVERRIDE_GUIDE.md) for complete documentation.

**Models - Direct Parameters (3 parts):**

```### Reset Database

models.ModelType.ParameterName```bash

```python main.py reset

Examples: `models.ElastoPlastic.ShearModulus`, `models.ElastoPlastic.YieldStrength````

⚠️ **WARNING**: Deletes ALL data!

**Models - Nested Parameters (4 parts):**

```## Module Overview

models.ModelType.SubModelType.ParameterName

```### parser/xml_parser.py

Examples: `models.ElasticModel.ThermoMechanical.MeltingTemperature`- Parses XML into Python dictionaries

- Preserves empty tags, units, references, indices

---- Material-agnostic (works for metals, explosives, etc.)



## 🧪 Complete Override Workflow Example### db/schema.py

- Normalized database schema

### Copper Override Example- Mirrors XML hierarchy exactly

```bash- Supports all material types with fixed schema

# 1. Check original values

python main.py query Copper### db/database.py

- Database connection management

# 2. Set property overrides- Schema creation/deletion

python main.py set-override Copper properties.Thermal.Cp 400 --unit "J/kg/K"- Connection pooling

python main.py set-override Copper properties.Thermal.Cv 390 --unit "J/kg/K"

### db/insert.py

# 3. Set preference (choose ref 121 for Density)- Inserts parsed XML data into database

python main.py set-preference Copper properties.Mechanical.Density 121- Preserves NULL values

- Stores numbers as TEXT

# 4. Set model overrides

python main.py set-override Copper models.ElasticModel.ThermoMechanical.MeltingTemperature 1358 --unit K### db/query.py

python main.py set-override Copper models.ElasticModel.ThermoMechanical.ThermalConductivity 401 --unit "W/m/K"- Retrieves material data from database

python main.py set-override Copper models.ElastoPlastic.ShearModulus 48E9 --unit Pa- Applies overrides at query time

python main.py set-override Copper models.ElastoPlastic.YieldStrength 70E6 --unit Pa- Returns data in XML-compatible structure



# 5. List all overrides### db/override_storage.py

python main.py list-overrides Copper- Stores user overrides in separate table

- Never modifies core material tables

# 6. Export with overrides- Supports preference selection and value overrides

python main.py export Copper

### overrides/override_manager.py

# 7. Verify- Applies overrides in memory at runtime

grep "USER_OVERRIDE" export/output/Copper_Override_exported.xml- Handles both properties and model parameters

```- Maintains original data integrity

- Reconstructs XML-like structure

---- Supports joins across all tables



## 📁 Project Structure### export/xml_exporter.py

- Exports database data to XML

```- Preserves exact tag order and hierarchy

materials_db/- Includes empty tags

├── main.py                          # Main CLI application- Solver-compatible output

├── config.py                        # Database configuration

├── requirements.txt                 # Python dependencies### overrides/override_manager.py

├── README.md                        # This file- Query-time overrides (never modifies DB)

│- Reference preference selection

├── db/                              # Database layer- User-defined value overrides

│   ├── database.py                  # Database connection

│   ├── schema.py                    # Schema creation## Data Integrity Principles

│   ├── insert.py                    # Data insertion

│   ├── query.py                     # Material querying1. **XML is Truth** - Original XML files are never modified

│   └── override_storage.py          # Override storage2. **NULL Preservation** - Empty tags stored as NULL, not removed

│3. **No Computation** - Never calculate or infer physics values

├── parser/                          # XML parsing4. **Text Storage** - Numeric values stored as TEXT to preserve "13E9" format

│   └── xml_parser.py5. **Structure Rigidity** - Schema works for all materials without changes

│6. **Solver Safety** - Exported XML exactly matches solver expectations

├── export/                          # XML export

│   ├── xml_exporter.py## Supported Materials

│   └── output/                      # Exported files

│The system supports ANY material that follows the XML schema:

├── overrides/                       # Override system

│   └── override_manager.py- Metals: Copper, Aluminum, Titanium, Tungsten, etc.

│- Explosives: RDX, HMX, PETN, TNT, CL-20, etc.

├── xml/                             # Source XML files (17 materials)- Others: Any material following the schema

│   ├── Aluminum.xml

│   ├── Copper.xmlNo code changes needed for new materials!

│   ├── RDX.xml

│   └── ...## Future Enhancements

│

└── Documentation/- ~~**Phase 3**: Override system~~ ✅ **COMPLETE**

    ├── QUICKSTART.md- **Phase 4**: Batch operations and validation hooks

    ├── OVERRIDE_GUIDE.md- **Phase 5**: Advanced querying with filters and statistics

    ├── PHASE3_COMPLETION.md- **Phase 6**: Visualization layer (plots, comparisons)

    ├── OVERRIDE_VERIFICATION_COMPLETE.md- **Phase 7**: Multi-user access control and API

    └── ...

```## Development



---### Running Tests



## 📦 Requirements```bash

# Test parser

### Python Dependenciespython parser/xml_parser.py

```

psycopg2-binary==2.9.10# Test database connection

```python db/database.py



Install via:# Test insertion

```bashpython db/insert.py

pip install -r requirements.txt

```# Test query

python db/query.py

### Database Requirements

- PostgreSQL 18.1 or higher# Test export

- Database: `Materials_DB`python export/xml_exporter.py



---# Test overrides (COMPREHENSIVE)

python test_overrides.py

## 🎨 Available Materials

# Test override manager

### Metalspython overrides/override_manager.py

Aluminum, Copper, Magnesium, Nickel, Tantalum, Titanium, Tungsten```



### Explosives### Code Style

RDX, TNT, HMX, PETN, TATB, CL-20, HNS, Nitromethane

- Clean, modular, readable Python

### Other- Single-responsibility principle

Sucrose, Helium- Clear docstrings

- Explicit over clever

---- Type hints where helpful



## 🧪 Testing## Troubleshooting



```bash### Database Connection Fails

# Run override tests- Check PostgreSQL is running

python test_overrides.py- Verify credentials in `config.py`

- Ensure database exists: `createdb Materials_DB`

# Expected: 5/5 tests passed

```### Import Fails

- Check XML file exists in `xml/` directory

---- Verify XML is well-formed

- Check database schema is initialized

## 🐛 Troubleshooting

### Export Fails

### Database Connection Issues- Verify material exists: `python main.py list`

```bash- Check export directory is writable

# Check PostgreSQL is running- Ensure database connection is active

pg_isready

## Contributing

# Test connection

psql -U postgres -d Materials_DB -c "SELECT COUNT(*) FROM materials;"When contributing, always ask:

```

**"Does this change preserve the XML structure exactly and keep the solver safe?"**

### Override Not Appearing

```bashIf not, don't implement it.

# Verify override is stored

python main.py list-overrides <MaterialName>## License



# Check exportProprietary - Internal use only

grep "USER_OVERRIDE" export/output/<MaterialName>_Override_exported.xml

```## Contact



---For questions or issues, contact the development team.



## 📊 Database Statistics---



- **Materials**: 17**Remember**: This is a DATA MANAGEMENT system, not a physics engine.

- **Total Parameters**: 2,006+Correctness of structure > Completeness of data.

- **Properties**: ~180 entriesSolver compatibility is the highest priority.

- **Model Parameters**: ~1,800 entries
- **References**: 124 unique sources

---

## 🎯 Project Status

### ✅ Phase 1: XML Parsing & Schema (Complete)
### ✅ Phase 2: Database Storage (Complete)
### ✅ Phase 3: Override System (Complete)

All features implemented and tested!

---

## 🔗 Documentation

- [Override Guide](OVERRIDE_GUIDE.md)
- [Quick Start](QUICKSTART.md)
- [Schema Documentation](SCHEMA_ANALYSIS.md)
- [Copper Override Workflow](COPPER_OVERRIDE_WORKFLOW.md)
- [Sucrose Override Commands](SUCROSE_OVERRIDE_COMMANDS.md)

---

## 👥 Authors

**Navbila-K** - [GitHub](https://github.com/Navbila-K)

---

*Last Updated: December 18, 2025*  
*Version: 1.0 (Production Ready)*
