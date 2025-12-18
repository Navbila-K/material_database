# Material Database Engine

A professional, solver-safe material data management system that treats XML as the source of truth and provides structured storage, querying, and export capabilities.

## Project Philosophy

**Structure is fixed. Data is flexible.**

This system:
- ✓ Preserves XML structure exactly
- ✓ Never infers or computes physics values
- ✓ Maintains solver compatibility
- ✓ Stores empty tags as NULL (never removes them)
- ✓ Works with ANY material without code changes
- ✓ Exports solver-ready XML that matches original schema

## Architecture

```
project/
│
├── xml/                # Source XML files (read-only)
├── parser/             # XML → Python dictionaries
├── db/                 # PostgreSQL schema & operations
├── export/             # DB → Solver-compatible XML
├── overrides/          # Query-time override logic
├── validation/         # Future: Schema validation
├── config.py           # Configuration
├── main.py             # CLI interface
└── requirements.txt    # Dependencies
```

## Database Schema

The PostgreSQL schema mirrors XML hierarchy exactly:

- **materials** - One row per material file
- **property_categories** - Phase, Thermal, Mechanical
- **properties** - Density, Cp, Cv, etc.
- **property_entries** - Actual values with refs and units
- **models** - ElasticModel, ElastoPlastic, ReactionModel, EOSModel
- **sub_models** - ThermoMechanical, Rows, etc.
- **model_parameters** - Individual model values
- **references** - Bibliographic references

All numeric values stored as TEXT to preserve scientific notation (e.g., "13E9").

## Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Update config.py with your database credentials
# Default: postgresql://sridhars:mypassword@localhost:5432/Materials_DB
```

## Quick Start

```bash
# 1. Initialize database schema
python main.py init

# 2. Import all materials from xml/
python main.py import-all

# 3. List materials
python main.py list

# 4. Query a material
python main.py query Copper

# 5. Export material back to XML
python main.py export Copper

# 6. Export all materials
python main.py export-all
```

## Usage

### Initialize Database
```bash
python main.py init
```
Creates all tables, indexes, and schema. Safe to run multiple times.

### Import Materials
```bash
# Import single material
python main.py import xml/Copper.xml

# Import all materials
python main.py import-all
```

### Query Materials
```bash
# List all materials
python main.py list

# View material details
python main.py query Copper
python main.py query RDX
```

### Export Materials
```bash
# Export single material
python main.py export Copper

# Export all materials
python main.py export-all
```
Exported files saved to `export/output/`

### Override System (Phase 3)

**Safely customize material data without modifying original database values.**

```bash
# Set preferred reference (when multiple values exist)
python main.py set-preference Aluminum properties.Mechanical.Density 121

# Set custom value override
python main.py set-override Aluminum properties.Mechanical.Density 2750 kg/m^3 "Lab measurement"

# List all overrides
python main.py list-overrides Aluminum

# Clear overrides
python main.py clear-overrides Aluminum
```

**Key Features:**
- ✅ Original data NEVER modified
- ✅ Overrides applied at query/export time
- ✅ Works with properties and model parameters
- ✅ Persists across sessions

📖 **Full Guide**: See [OVERRIDE_GUIDE.md](OVERRIDE_GUIDE.md) for complete documentation.

### Reset Database
```bash
python main.py reset
```
⚠️ **WARNING**: Deletes ALL data!

## Module Overview

### parser/xml_parser.py
- Parses XML into Python dictionaries
- Preserves empty tags, units, references, indices
- Material-agnostic (works for metals, explosives, etc.)

### db/schema.py
- Normalized database schema
- Mirrors XML hierarchy exactly
- Supports all material types with fixed schema

### db/database.py
- Database connection management
- Schema creation/deletion
- Connection pooling

### db/insert.py
- Inserts parsed XML data into database
- Preserves NULL values
- Stores numbers as TEXT

### db/query.py
- Retrieves material data from database
- Applies overrides at query time
- Returns data in XML-compatible structure

### db/override_storage.py
- Stores user overrides in separate table
- Never modifies core material tables
- Supports preference selection and value overrides

### overrides/override_manager.py
- Applies overrides in memory at runtime
- Handles both properties and model parameters
- Maintains original data integrity
- Reconstructs XML-like structure
- Supports joins across all tables

### export/xml_exporter.py
- Exports database data to XML
- Preserves exact tag order and hierarchy
- Includes empty tags
- Solver-compatible output

### overrides/override_manager.py
- Query-time overrides (never modifies DB)
- Reference preference selection
- User-defined value overrides

## Data Integrity Principles

1. **XML is Truth** - Original XML files are never modified
2. **NULL Preservation** - Empty tags stored as NULL, not removed
3. **No Computation** - Never calculate or infer physics values
4. **Text Storage** - Numeric values stored as TEXT to preserve "13E9" format
5. **Structure Rigidity** - Schema works for all materials without changes
6. **Solver Safety** - Exported XML exactly matches solver expectations

## Supported Materials

The system supports ANY material that follows the XML schema:

- Metals: Copper, Aluminum, Titanium, Tungsten, etc.
- Explosives: RDX, HMX, PETN, TNT, CL-20, etc.
- Others: Any material following the schema

No code changes needed for new materials!

## Future Enhancements

- ~~**Phase 3**: Override system~~ ✅ **COMPLETE**
- **Phase 4**: Batch operations and validation hooks
- **Phase 5**: Advanced querying with filters and statistics
- **Phase 6**: Visualization layer (plots, comparisons)
- **Phase 7**: Multi-user access control and API

## Development

### Running Tests

```bash
# Test parser
python parser/xml_parser.py

# Test database connection
python db/database.py

# Test insertion
python db/insert.py

# Test query
python db/query.py

# Test export
python export/xml_exporter.py

# Test overrides (COMPREHENSIVE)
python test_overrides.py

# Test override manager
python overrides/override_manager.py
```

### Code Style

- Clean, modular, readable Python
- Single-responsibility principle
- Clear docstrings
- Explicit over clever
- Type hints where helpful

## Troubleshooting

### Database Connection Fails
- Check PostgreSQL is running
- Verify credentials in `config.py`
- Ensure database exists: `createdb Materials_DB`

### Import Fails
- Check XML file exists in `xml/` directory
- Verify XML is well-formed
- Check database schema is initialized

### Export Fails
- Verify material exists: `python main.py list`
- Check export directory is writable
- Ensure database connection is active

## Contributing

When contributing, always ask:

**"Does this change preserve the XML structure exactly and keep the solver safe?"**

If not, don't implement it.

## License

Proprietary - Internal use only

## Contact

For questions or issues, contact the development team.

---

**Remember**: This is a DATA MANAGEMENT system, not a physics engine.
Correctness of structure > Completeness of data.
Solver compatibility is the highest priority.
