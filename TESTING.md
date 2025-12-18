# Testing Guide - Material Database Engine

## Quick Test

**Run the comprehensive test suite:**
```bash
python test_system.py
```

This tests all 7 components:
1. ✅ Database Connection
2. ✅ XML Parser
3. ✅ Database Schema
4. ✅ Data Insertion
5. ✅ Data Query
6. ✅ XML Export
7. ✅ Override Manager

---

## Manual Testing

### Step-by-Step Test Workflow

#### **1. Initialize Database**
```bash
python main.py init
```
Expected output: `✓ Database initialization complete!`

#### **2. Import a Material**
```bash
# Import single material
python main.py import xml/Aluminum.xml
```
Expected output:
```
Importing: Aluminum.xml
  Parsing XML...
  Inserting into database...
  ✓ Inserted material metadata (ID: X)
  ✓ Inserted properties
  ✓ Inserted models
✓ Material 'Aluminum' inserted successfully
```

#### **3. List Materials**
```bash
python main.py list
```
Expected output:
```
Materials in database: 3
======================================================================
ID    Name                 XML ID               Version        
----------------------------------------------------------------------
2     Copper               COPPER-001           0.0.0-0FA756E6 
3     RDX                  RDX-001              0.0.0-4753428F 
4     Aluminum             ALUMINUM-001         0.0.0-33C90239
======================================================================
```

#### **4. Query Material Details**
```bash
python main.py query Aluminum
```
Expected output:
```
======================================================================
Material: Aluminum
======================================================================

--- METADATA ---
  id: ALUMINUM-001
  name: Aluminum
  ...

--- PROPERTIES ---
  Phase:
    State: solid
  Thermal:
    Cp (J/kg/K): 1 entries
  ...

--- MODELS ---
  ElasticModel
  ElastoPlastic
  ...
```

#### **5. Export Material**
```bash
python main.py export Aluminum
```
Expected output:
```
Exporting: Aluminum
Output: /path/to/export/output/Aluminum_exported.xml
✓ Exported to: /path/to/export/output/Aluminum_exported.xml
✓ Export complete!
```

#### **6. Verify Export**
```bash
# Check the exported file exists
ls -lh export/output/Aluminum_exported.xml

# View first 50 lines
head -50 export/output/Aluminum_exported.xml

# Compare structure with original (will show differences in ordering/formatting)
diff xml/Aluminum.xml export/output/Aluminum_exported.xml
```

---

## Testing Individual Modules

### **Test Database Connection**
```bash
python db/database.py
```
Expected output:
```
Testing database connection...
✓ Connected to database: Materials_DB
✓ PostgreSQL version: PostgreSQL 18.1 ...
Creating schema...
✓ Database schema created successfully
Database setup complete!
```

### **Test XML Parser**
```bash
python parser/xml_parser.py
```
Expected output:
```
Parsing xml/Copper.xml...

=== METADATA ===
{
  "id": "COPPER-001",
  "name": "Copper",
  ...
}

=== PROPERTIES ===
Categories: ['Phase', 'Thermal', 'Mechanical']

=== MODELS ===
Model types: ['ElasticModel', 'ElastoPlastic', 'ReactionModel', 'EOSModel']

✓ Parse successful!
```

### **Test Query System**
```bash
python db/query.py
```
Expected output:
```
=== ALL MATERIALS ===
  - Copper (ID: 2)
  - RDX (ID: 3)

=== QUERYING: Copper ===
Metadata:
{
  "id": "COPPER-001",
  ...
}
```

### **Test Export System**
```bash
python export/xml_exporter.py
```
Expected output:
```
Exporting: Copper
✓ Exported to: /path/to/export/output/Copper_exported.xml
```

### **Test Override Manager**
```bash
python overrides/override_manager.py
```
Expected output:
```
=== ORIGINAL DATA ===
[
  { "value": "8940", "ref": "107", ... },
  { "value": "8930", "ref": "109", ... },
  { "value": "8960", "ref": "121", ... }
]

=== APPLYING REFERENCE PREFERENCE (ref=109) ===
[
  { "value": "8930", "ref": "109", ... }
]

=== APPLYING VALUE OVERRIDE ===
[
  { "value": "9000", "unit": "kg/m^3", "ref": "USER_OVERRIDE", ... }
]

✓ Override tests complete
```

---

## Batch Testing

### **Import All Materials**
```bash
python main.py import-all
```
This imports all 17 materials. Expected: Most should succeed.

### **Export All Materials**
```bash
python main.py export-all
```
This exports all materials to `export/output/`

### **Verify Exports**
```bash
# Count exported files
ls -1 export/output/*.xml | wc -l

# Check file sizes
ls -lh export/output/*.xml
```

---

## Performance Testing

### **Time Import Operation**
```bash
time python main.py import xml/Copper.xml
```

### **Time Export Operation**
```bash
time python main.py export Copper
```

### **Time Full Query**
```bash
time python main.py query Copper
```

---

## Data Integrity Testing

### **Round-Trip Test**
```bash
# 1. Delete existing Titanium if present
# (manually delete from database or reset)

# 2. Import fresh
python main.py import xml/TITANIUM.xml

# 3. Export
python main.py export TITANIUM

# 4. Compare structures (some formatting differences expected)
diff xml/TITANIUM.xml export/output/TITANIUM_exported.xml
```

### **NULL Preservation Test**
```bash
# Query a material and check for NULL handling
python main.py query Copper | grep "None"

# Expected: Should see "None" for empty entries
```

### **Scientific Notation Test**
```bash
# Export and check scientific notation is preserved
grep -E "[0-9]+E[0-9]+" export/output/Copper_exported.xml

# Expected: Should find entries like "13E9", "140E9", etc.
```

---

## Error Testing

### **Test Missing File**
```bash
python main.py import xml/NonExistent.xml
```
Expected: `✗ File not found: xml/NonExistent.xml`

### **Test Invalid Material Name**
```bash
python main.py query InvalidMaterial
```
Expected: `✗ Material not found: InvalidMaterial`

### **Test Without Database**
```bash
# Stop PostgreSQL, then:
python main.py list
```
Expected: Connection error message

---

## Database Testing

### **Check Tables**
```bash
# Connect to PostgreSQL
psql Materials_DB

# List tables
\dt

# Count materials
SELECT COUNT(*) FROM materials;

# View material names
SELECT name, xml_id FROM materials ORDER BY name;

# Check property entries
SELECT COUNT(*) FROM property_entries;

# Exit
\q
```

### **Reset Database Test**
```bash
# Reset
python main.py reset
# Type 'yes' when prompted

# Verify empty
python main.py list
# Expected: "No materials found in database"

# Re-import
python main.py import-all
```

---

## Regression Testing

After making code changes, run:

```bash
# 1. Run comprehensive test
python test_system.py

# 2. Test import/export for each material type
python main.py import xml/Copper.xml    # Metal
python main.py import xml/RDX.xml       # Explosive
python main.py import xml/HELIUM.xml    # Gas

# 3. Verify exports
python main.py export Copper
python main.py export RDX
python main.py export HELIUM

# 4. Check exports are well-formed
xmllint --noout export/output/Copper_exported.xml
xmllint --noout export/output/RDX_exported.xml
xmllint --noout export/output/HELIUM_exported.xml
```

---

## Test Checklist

- [ ] Comprehensive test passes (`python test_system.py`)
- [ ] Can initialize database
- [ ] Can import metal (Copper/Aluminum)
- [ ] Can import explosive (RDX/HMX)
- [ ] Can list materials
- [ ] Can query material details
- [ ] Can export material
- [ ] Exported XML is well-formed
- [ ] Empty tags preserved in export
- [ ] Scientific notation preserved
- [ ] Units preserved
- [ ] References preserved
- [ ] All CLI commands work
- [ ] Error messages are clear
- [ ] No Python errors or warnings

---

## Troubleshooting Tests

### **If Database Connection Fails:**
```bash
# Check PostgreSQL is running
pg_ctl status

# Check database exists
psql -l | grep Materials_DB

# Create if missing
createdb Materials_DB

# Test connection manually
psql Materials_DB -c "SELECT 1;"
```

### **If Import Fails:**
```bash
# Check file exists
ls -l xml/MaterialName.xml

# Check XML is well-formed
xmllint --noout xml/MaterialName.xml

# Try with verbose Python
python -v main.py import xml/MaterialName.xml
```

### **If Export Fails:**
```bash
# Check material exists
python main.py list

# Check export directory is writable
ls -ld export/output/
touch export/output/test.txt && rm export/output/test.txt
```

---

## Expected Test Results Summary

✅ **test_system.py**: All 7 tests pass  
✅ **Import**: Materials inserted successfully  
✅ **Query**: Complete data retrieved  
✅ **Export**: Valid XML generated  
✅ **Round-trip**: Structure preserved  

**System Status**: Fully Operational ✅
