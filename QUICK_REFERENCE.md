# Quick Reference - Material Database Engine

## 🚀 Essential Commands

```bash
# Activate virtual environment (if needed)
source .venv/bin/activate  # or just use full path

# Initialize database (first time only)
python main.py init

# Import materials
python main.py import xml/Copper.xml        # Single
python main.py import-all                   # All materials

# View materials
python main.py list                         # List all
python main.py query Copper                 # Detailed view

# Export materials
python main.py export Copper                # Single
python main.py export-all                   # All materials

# Reset database (⚠️ deletes all data)
python main.py reset
```

## 🧪 Testing

```bash
# Run comprehensive test suite
python test_system.py

# Test individual modules
python db/database.py          # Database
python parser/xml_parser.py    # Parser
python db/query.py             # Query
python export/xml_exporter.py  # Export
```

## 📂 Project Layout

```
materials_db/
├── xml/                  # 📄 Source XML files (17 materials)
├── export/output/        # 📤 Exported XML files
├── parser/               # 🔍 XML → Python
├── db/                   # 💾 Database operations
├── export/               # 📝 Python → XML
├── overrides/            # ⚙️  Override logic
├── main.py              # 🎮 CLI interface
├── test_system.py       # ✅ Test suite
└── config.py            # ⚙️  Configuration
```

## 📊 Database Info

**Connection:** `postgresql://sridhars:mypassword@localhost:5432/Materials_DB`

**Tables:** (7 total)
- materials
- property_categories  
- properties
- property_entries
- models
- sub_models
- model_parameters

## 🎯 Common Workflows

### Import → Query → Export
```bash
python main.py import xml/TITANIUM.xml
python main.py query TITANIUM
python main.py export TITANIUM
```

### Import All → List → Export All
```bash
python main.py import-all
python main.py list
python main.py export-all
```

### Reset → Import → Test
```bash
python main.py reset            # Type 'yes'
python main.py import-all
python test_system.py
```

## 🔧 Troubleshooting

**Database connection fails?**
```bash
# Check PostgreSQL is running
pg_ctl status
# Start if needed
pg_ctl start
```

**Import fails?**
```bash
# Check file exists
ls xml/MaterialName.xml
# Check it's valid XML
xmllint --noout xml/MaterialName.xml
```

**Module not found?**
```bash
# Use full path to Python
/Users/sridhars/Projects/materials_db/.venv/bin/python main.py list
```

## 📝 File Locations

**Source XML:** `xml/*.xml` (read-only)  
**Exported XML:** `export/output/*.xml`  
**Configuration:** `config.py`  
**Documentation:** `README.md`, `QUICKSTART.md`, `TESTING.md`

## ✅ System Status

**Current Status:** ✅ Fully Operational  
**Materials in DB:** 3 (Aluminum, Copper, RDX)  
**Available Materials:** 17 total  
**Phase:** Phase 1 Complete  

## 🎓 Key Concepts

1. **Structure is Fixed** - XML schema never changes
2. **Data is Flexible** - Any material works with same code  
3. **No Computation** - Pure data management, no physics
4. **NULL Preservation** - Empty tags stored as NULL
5. **Solver-Safe** - Exports match original structure

## 🔗 Quick Links

- Full docs: `README.md`
- Quick start: `QUICKSTART.md`
- Testing guide: `TESTING.md`
- Implementation: `IMPLEMENTATION_SUMMARY.md`
- Project checklist: `CHECKLIST.md`

---

**Need Help?** Check `TESTING.md` for detailed troubleshooting
