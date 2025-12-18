# Override System Guide

## Overview

The **Override System** allows you to temporarily modify material data **without changing the original database values**. This is useful for:

- **Selecting** a preferred reference when multiple experimental values exist
- **Testing** different values for sensitivity analysis
- **Customizing** material properties for specific simulations
- **Comparing** different literature sources

## Core Principles

✅ **SAFE**: Original database values are **NEVER modified**  
✅ **TEMPORARY**: Overrides are applied at query/export time only  
✅ **PERSISTENT**: Overrides are stored separately and survive restarts  
✅ **REVERSIBLE**: Clear overrides anytime to return to original values  

---

## Use Cases

### Use Case 1: Selecting Preferred Reference

**Problem**: Aluminum has 2 Density values from different sources:
- Entry 1: 2730 kg/m³ (ref: 112)
- Entry 2: 2700 kg/m³ (ref: 121)

**Solution**: Set preference for reference 121:

```bash
python main.py set-preference Aluminum properties.Mechanical.Density 121
```

Now queries and exports will use only the preferred value (2700 kg/m³).

---

### Use Case 2: Custom Value Override

**Problem**: You have a custom lab measurement for Density = 2750 kg/m³

**Solution**: Override with your custom value:

```bash
python main.py set-override Aluminum properties.Mechanical.Density 2750 kg/m^3 "Lab measurement"
```

Queries and exports now use 2750 kg/m³ (marked as USER_OVERRIDE).

---

### Use Case 3: Model Parameter Override

**Problem**: Aluminum has 2 MeltingTemperature values in ThermoMechanical model

**Solution**: Choose preferred reference:

```bash
python main.py set-preference Aluminum models.ElasticModel.ThermoMechanical.MeltingTemperature 112
```

---

## Command Reference

### 1. Set Preference

Select preferred reference for properties with multiple values.

```bash
python main.py set-preference <material> <property_path> <preferred_ref>
```

**Examples:**
```bash
# Property preference
python main.py set-preference Aluminum properties.Mechanical.Density 121

# Model parameter preference  
python main.py set-preference Aluminum models.ElasticModel.ThermoMechanical.MeltingTemperature 112
```

---

### 2. Set Value Override

Replace any value with custom input.

```bash
python main.py set-override <material> <property_path> <value> [unit] [reason]
```

**Examples:**
```bash
# Simple override
python main.py set-override Aluminum properties.Mechanical.Density 2750

# Override with unit
python main.py set-override Aluminum properties.Thermal.Cp 920 J/kg/K

# Override with reason
python main.py set-override Aluminum properties.Mechanical.Density 2750 kg/m^3 "Lab measurement 2024-12-18"

# Model parameter override
python main.py set-override Aluminum models.ElasticModel.ThermoMechanical.ShearModulus 27E9 Pa "Updated value"
```

---

### 3. List Overrides

View all overrides for a material.

```bash
python main.py list-overrides <material>
```

**Example:**
```bash
python main.py list-overrides Aluminum
```

**Output:**
```
================================================================================
OVERRIDES FOR: Aluminum
================================================================================

Property Path: properties.Mechanical.Density
Type:          reference_preference
Preferred Ref: 121
Created:       2024-12-18 10:30:45
--------------------------------------------------------------------------------
Property Path: properties.Thermal.Cp
Type:          value_override
Override Value: 920
Unit:           J/kg/K
Reason:         Updated measurement
Created:       2024-12-18 10:31:12
--------------------------------------------------------------------------------
```

---

### 4. Clear Overrides

Remove overrides to return to original values.

```bash
# Clear specific property override
python main.py clear-overrides <material> <property_path>

# Clear ALL overrides for material
python main.py clear-overrides <material>
```

**Examples:**
```bash
# Clear specific override
python main.py clear-overrides Aluminum properties.Mechanical.Density

# Clear all overrides
python main.py clear-overrides Aluminum
```

---

## Property Path Format

Property paths use dot notation to specify the exact location:

### Properties
```
properties.<CategoryType>.<PropertyName>
```

**Examples:**
- `properties.Mechanical.Density`
- `properties.Thermal.Cp`
- `properties.Thermal.Cv`
- `properties.Phase.State`

### Model Parameters
```
models.<ModelType>.<SubModelType>.<ParameterName>
```

**Examples:**
- `models.ElasticModel.ThermoMechanical.Density`
- `models.ElasticModel.ThermoMechanical.MeltingTemperature`
- `models.ElasticModel.ThermoMechanical.ShearModulus`
- `models.EOSModel.Gruneisen.GammaZero`

---

## How Overrides Work

### 1. Storage

Overrides are stored in a **separate table** (`material_overrides`):

```sql
CREATE TABLE material_overrides (
    override_id SERIAL PRIMARY KEY,
    material_id INTEGER REFERENCES materials(material_id),
    property_path TEXT NOT NULL,
    override_type TEXT CHECK (override_type IN ('reference_preference', 'value_override')),
    override_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Original data tables are NEVER modified.**

---

### 2. Query-Time Application

When you query a material:

```bash
python main.py query Aluminum
```

The system:
1. Loads original data from database
2. Loads overrides from `material_overrides` table
3. Applies overrides **in memory**
4. Displays merged result

Original data remains untouched in database.

---

### 3. Export Integration

When you export a material:

```bash
python main.py export Aluminum
```

The exported XML includes override values, making it solver-ready with your custom settings.

---

## Testing Overrides

Run the comprehensive test suite:

```bash
python test_overrides.py
```

**Tests include:**
1. ✅ Reference preference selection
2. ✅ Value override
3. ✅ Model parameter override
4. ✅ Override persistence
5. ✅ Export integration

---

## Workflow Example

### Complete Override Workflow

```bash
# 1. Import material
python main.py import xml/Aluminum.xml

# 2. Query original data
python main.py query Aluminum
# Shows 2 Density values: 2730, 2700 kg/m³

# 3. Set preference for reference 121
python main.py set-preference Aluminum properties.Mechanical.Density 121

# 4. Query with override
python main.py query Aluminum
# Now shows only 2700 kg/m³

# 5. Export with override
python main.py export Aluminum
# XML contains only 2700 kg/m³

# 6. List overrides
python main.py list-overrides Aluminum
# Shows active overrides

# 7. Clear overrides (return to original)
python main.py clear-overrides Aluminum

# 8. Query again
python main.py query Aluminum
# Back to showing both values: 2730, 2700 kg/m³
```

---

## Advanced: Python API

### Programmatic Override Management

```python
from db.database import DatabaseManager
from db.query import MaterialQuerier
from db.override_storage import OverrideStorage

# Setup
db = DatabaseManager()
conn = db.connect()
storage = OverrideStorage(conn)
querier = MaterialQuerier(db)

# Get material ID
cursor = conn.cursor()
cursor.execute("SELECT material_id FROM materials WHERE name = 'Aluminum'")
material_id = cursor.fetchone()[0]

# Set preference
storage.save_reference_preference(
    material_id, 
    'properties.Mechanical.Density', 
    '121'
)

# Set value override
storage.save_value_override(
    material_id,
    'properties.Thermal.Cp',
    '920',
    'J/kg/K',
    'Lab measurement'
)

# Query with overrides
material_data = querier.get_material_by_name('Aluminum', apply_overrides=True)

# Query without overrides
original_data = querier.get_material_by_name('Aluminum', apply_overrides=False)

# List overrides
overrides = storage.list_overrides(material_id)

# Clear overrides
storage.delete_all_overrides(material_id)
```

---

## Database Verification

Check overrides directly in PostgreSQL:

```sql
-- View all overrides
SELECT * FROM material_overrides;

-- View overrides for specific material
SELECT mo.*, m.name
FROM material_overrides mo
JOIN materials m ON mo.material_id = m.material_id
WHERE m.name = 'Aluminum';

-- Count overrides per material
SELECT m.name, COUNT(*) as override_count
FROM materials m
LEFT JOIN material_overrides mo ON m.material_id = mo.material_id
GROUP BY m.name
ORDER BY override_count DESC;
```

---

## Important Notes

### ⚠️ What Overrides DON'T Do

- ❌ **Don't modify original database values** (original data always preserved)
- ❌ **Don't perform physics calculations** (just value selection/replacement)
- ❌ **Don't evaluate equations** (no EOS evaluation or model solving)
- ❌ **Don't convert units** (use values as-is)

### ✅ What Overrides DO

- ✅ Select one value among multiple references
- ✅ Replace reference values with custom values
- ✅ Apply changes at query/export time only
- ✅ Persist across sessions (stored in database)
- ✅ Work with both properties and model parameters

---

## Troubleshooting

### Override Not Applied

**Problem**: Override set but not showing in query

**Solutions**:
1. Check property path is correct (case-sensitive)
2. Verify material name is exact match
3. Run `python main.py list-overrides <material>` to confirm override exists
4. Ensure you're querying the same material

### Property Path Not Found

**Problem**: Error setting override for property path

**Solutions**:
1. Query material first to see structure: `python main.py query <material>`
2. Use exact property names from database
3. Follow path format: `properties.<Category>.<Property>` or `models.<Model>.<SubModel>.<Parameter>`

### Override Not Persisting

**Problem**: Override disappears after restart

**Check**:
1. Verify override_storage table exists: `\dt material_overrides` in psql
2. Check database connection is working
3. Run test script: `python test_overrides.py`

---

## Summary

The Override System provides a **safe, reversible** way to customize material data for specific use cases without compromising the integrity of reference data in the database.

**Key Commands:**
- `set-preference` - Choose preferred reference
- `set-override` - Set custom value
- `list-overrides` - View active overrides
- `clear-overrides` - Remove overrides

**Remember**: Original database values are **NEVER** modified. Overrides are applied at query/export time only.
