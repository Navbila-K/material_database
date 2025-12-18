# SUCROSE OVERRIDE COMMANDS - TEST GUIDE

**Material**: Sucrose  
**Purpose**: Test override system with property and model parameter overrides

---

## 📋 UNDERSTANDING OVERRIDES

### What is an Override?

**Override = Change a value WITHOUT modifying the original database**

There are 2 types:

1. **REFERENCE PREFERENCE** (Filtering)
   - When a property has MULTIPLE references/sources
   - You CHOOSE which reference to use
   - Other references are HIDDEN (not deleted)
   - Original data stays in database
   
2. **VALUE OVERRIDE** (Modification)
   - You SET a NEW custom value
   - Original value stays in database
   - New value marked as "USER_OVERRIDE"
   - Can add a reason/note

---

## 🔍 STEP 0: CHECK CURRENT VALUES (BEFORE OVERRIDE)

```bash
# See all current values for Sucrose
python main.py query Sucrose
```

**Key values to note:**
- Cp: 1244 J/kg/K (ref: 50)
- Cv: 425 J/kg/K (ref: 52)
- Density: 1580.5 kg/m³ (ref: 50) - **ONLY 1 reference** (cannot use preference)
- MeltingTemperature: 461 K (ref: 50)
- ThermalConductivity: 486 W/m/K (ref: 50)
- ShearModulus: 8.58E9 Pa (ref: 50)
- YieldStrength: (empty) - **NO VALUE** (good for testing override)

---

## 📝 OVERRIDE COMMANDS

### CATEGORY 1: PROPERTY OVERRIDES (Thermal)

#### Command 1: Override Cp (Specific Heat at Constant Pressure)
```bash
python main.py set-override Sucrose properties.Thermal.Cp 1300 --unit "J/kg/K" --reason "Updated lab measurement"
```
**What this does:**
- **Original**: Cp = 1244 J/kg/K (ref 50)
- **After**: Cp = 1300 J/kg/K (ref USER_OVERRIDE)
- **Effect**: Changes value from 1244 → 1300

---

#### Command 2: Override Cv (Specific Heat at Constant Volume)
```bash
python main.py set-override Sucrose properties.Thermal.Cv 450 --unit "J/kg/K" --reason "Calculated from thermodynamic relations"
```
**What this does:**
- **Original**: Cv = 425 J/kg/K (ref 52)
- **After**: Cv = 450 J/kg/K (ref USER_OVERRIDE)
- **Effect**: Changes value from 425 → 450

---

### CATEGORY 2: PROPERTY OVERRIDE (Mechanical)

#### Command 3: Override Density
```bash
python main.py set-override Sucrose properties.Mechanical.Density 1600 --unit "kg/m^3" --reason "High purity sample measurement"
```
**What this does:**
- **Original**: Density = 1580.5 kg/m³ (ref 50)
- **After**: Density = 1600 kg/m³ (ref USER_OVERRIDE)
- **Effect**: Changes value from 1580.5 → 1600
- **Note**: Sucrose has ONLY 1 reference, so cannot use preference (must use value override)

---

### CATEGORY 3: MODEL OVERRIDES (ElasticModel.ThermoMechanical)

#### Command 4: Override MeltingTemperature
```bash
python main.py set-override Sucrose models.ElasticModel.ThermoMechanical.MeltingTemperature 465 --unit K --reason "DSC measurement"
```
**What this does:**
- **Original**: MeltingTemperature = 461 K (ref 50)
- **After**: MeltingTemperature = 465 K (ref USER_OVERRIDE)
- **Effect**: Changes value from 461 → 465

---

#### Command 5: Override ThermalConductivity
```bash
python main.py set-override Sucrose models.ElasticModel.ThermoMechanical.ThermalConductivity 500 --unit "W/m/K" --reason "Higher purity sample"
```
**What this does:**
- **Original**: ThermalConductivity = 486 W/m/K (ref 50)
- **After**: ThermalConductivity = 500 W/m/K (ref USER_OVERRIDE)
- **Effect**: Changes value from 486 → 500

---

### CATEGORY 4: MODEL OVERRIDES (ElastoPlastic)

#### Command 6: Override ShearModulus
```bash
python main.py set-override Sucrose models.ElastoPlastic.ShearModulus 9E9 --unit Pa --reason "Updated mechanical testing"
```
**What this does:**
- **Original**: ShearModulus = 8.58E9 Pa (ref 50)
- **After**: ShearModulus = 9E9 Pa (ref USER_OVERRIDE)
- **Effect**: Changes value from 8.58E9 → 9E9

---

#### Command 7: Override YieldStrength (Currently Empty!)
```bash
python main.py set-override Sucrose models.ElastoPlastic.YieldStrength 50E6 --unit Pa --reason "Experimental yield stress"
```
**What this does:**
- **Original**: YieldStrength = (empty) - NO VALUE
- **After**: YieldStrength = 50E6 Pa (ref USER_OVERRIDE)
- **Effect**: ADDS a value where none existed!

---

## 🔎 VERIFICATION COMMANDS

### Command 8: List All Overrides
```bash
python main.py list-overrides Sucrose
```
**What this shows:**
- All 7 overrides you just created
- Property path, type, value, unit, creation date
- Should show 7 entries

---

### Command 9: Query with Overrides Applied
```bash
python main.py query Sucrose
```
**What this shows:**
- Material data WITH overrides applied
- Values should show your new numbers
- References should show "USER_OVERRIDE"

---

### Command 10: Export to XML
```bash
python main.py export Sucrose
```
**What this does:**
- Exports material to XML with overrides applied
- Filename: `Sucrose_Override_exported.xml` (note the "_Override" suffix!)
- File location: `export/output/Sucrose_Override_exported.xml`

---

### Command 11: Check Export File
```bash
grep -A 1 "USER_OVERRIDE" export/output/Sucrose_Override_exported.xml
```
**What this shows:**
- All lines with USER_OVERRIDE reference
- Should show 6 entries (Cp, Cv, Density, MeltingTemperature, ThermalConductivity, ShearModulus, YieldStrength)

---

## 📊 BEFORE vs AFTER COMPARISON

| Property Path | BEFORE (Original) | AFTER (Override) | Change Type |
|---------------|-------------------|------------------|-------------|
| **properties.Thermal.Cp** | 1244 J/kg/K (ref 50) | 1300 J/kg/K (USER_OVERRIDE) | Modified |
| **properties.Thermal.Cv** | 425 J/kg/K (ref 52) | 450 J/kg/K (USER_OVERRIDE) | Modified |
| **properties.Mechanical.Density** | 1580.5 kg/m³ (ref 50) | 1600 kg/m³ (USER_OVERRIDE) | Modified |
| **models.ElasticModel.ThermoMechanical.MeltingTemperature** | 461 K (ref 50) | 465 K (USER_OVERRIDE) | Modified |
| **models.ElasticModel.ThermoMechanical.ThermalConductivity** | 486 W/m/K (ref 50) | 500 W/m/K (USER_OVERRIDE) | Modified |
| **models.ElastoPlastic.ShearModulus** | 8.58E9 Pa (ref 50) | 9E9 Pa (USER_OVERRIDE) | Modified |
| **models.ElastoPlastic.YieldStrength** | (empty) | 50E6 Pa (USER_OVERRIDE) | **ADDED** |

---

## 🗑️ CLEANUP COMMANDS (OPTIONAL)

### Command 12: Clear One Specific Override
```bash
python main.py clear-overrides Sucrose properties.Thermal.Cp
```
**What this does:**
- Removes ONLY the Cp override
- Other 6 overrides remain
- Cp returns to original value (1244)

---

### Command 13: Clear ALL Overrides
```bash
python main.py clear-overrides Sucrose
```
**What this does:**
- Removes ALL 7 overrides
- All values return to original
- Export filename changes back to `Sucrose_exported.xml` (no "_Override")

---

## 🎯 COMPLETE TEST SEQUENCE

Copy and paste this entire sequence:

```bash
# 0. Check original values
python main.py query Sucrose

# 1-7. Set all overrides
python main.py set-override Sucrose properties.Thermal.Cp 1300 --unit "J/kg/K" --reason "Updated lab measurement"
python main.py set-override Sucrose properties.Thermal.Cv 450 --unit "J/kg/K" --reason "Calculated from thermodynamic relations"
python main.py set-override Sucrose properties.Mechanical.Density 1600 --unit "kg/m^3" --reason "High purity sample measurement"
python main.py set-override Sucrose models.ElasticModel.ThermoMechanical.MeltingTemperature 465 --unit K --reason "DSC measurement"
python main.py set-override Sucrose models.ElasticModel.ThermoMechanical.ThermalConductivity 500 --unit "W/m/K" --reason "Higher purity sample"
python main.py set-override Sucrose models.ElastoPlastic.ShearModulus 9E9 --unit Pa --reason "Updated mechanical testing"
python main.py set-override Sucrose models.ElastoPlastic.YieldStrength 50E6 --unit Pa --reason "Experimental yield stress"

# 8. List all overrides
python main.py list-overrides Sucrose

# 9. Query with overrides
python main.py query Sucrose

# 10. Export
python main.py export Sucrose

# 11. Check export
grep -A 1 "USER_OVERRIDE" export/output/Sucrose_Override_exported.xml

# 12. (Optional) Clear all
# python main.py clear-overrides Sucrose
```

---

## ✅ EXPECTED RESULTS

After running all commands:

1. ✅ **7 overrides stored** in database
2. ✅ **All values changed** in query output
3. ✅ **Export filename**: `Sucrose_Override_exported.xml` (with "_Override")
4. ✅ **Export contains**: 7 lines with "ref=\"USER_OVERRIDE\""
5. ✅ **Original data**: Still intact in database (non-destructive)

---

## 🔍 WHAT HAPPENS IN DATABASE

### Original Data (NEVER MODIFIED)
```
materials table: material_id=14, name='Sucrose'
properties table: Cp=1244, Cv=425, Density=1580.5
model_parameters table: MeltingTemperature=461, ThermalConductivity=486, ShearModulus=8.58E9
```

### Override Data (SEPARATE TABLE)
```
material_overrides table:
  - property_path: properties.Thermal.Cp, override_data: {value: "1300", unit: "J/kg/K"}
  - property_path: properties.Thermal.Cv, override_data: {value: "450", unit: "J/kg/K"}
  - property_path: properties.Mechanical.Density, override_data: {value: "1600", unit: "kg/m^3"}
  - ... (4 more overrides)
```

### Query Result (RUNTIME APPLICATION)
```
When you query:
1. Load original data from database
2. Load overrides from material_overrides table
3. Apply overrides IN MEMORY (not in database)
4. Return modified data
```

**KEY POINT**: Original data is NEVER touched! Overrides are stored separately and applied at runtime.

---

## 📝 NOTES

1. **Sucrose has mostly SINGLE references** - Cannot use preference selection (need multiple refs)
2. **YieldStrength is empty** - Good test case for adding value where none existed
3. **All overrides are reversible** - Use `clear-overrides` to restore original
4. **Export auto-detects overrides** - Filename changes to include "_Override"
5. **Original XML never modified** - Export creates NEW file

---

*Ready to test! Run commands in sequence and verify results.*
