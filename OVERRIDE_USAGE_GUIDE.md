# Override Usage Guide

## Understanding the Three Tabs

### 📄 **Original Data Tab**
- **Purpose**: Shows raw database values
- **Overrides**: NOT applied
- **Use case**: See what's stored in the database originally
- **Example**: MeltingTemperature shows TWO entries:
  - 933.5 K (ref 112)
  - 933.32 K (ref 121)

### ⚡ **Overrides Tab**
- **Purpose**: Shows ONLY properties you've overridden
- **Overrides**: Comparison view (before → after)
- **Use case**: Review all your custom overrides
- **Columns**:
  - Property: Full property path
  - Original Value: Database value
  - New Value: Your override
  - Unit: Unit of measurement
  - Reason: Why you overrode it
  - Type: Always "USER_OVERRIDE"
- **Note**: Empty if no overrides exist

### ✓ **Active View Tab**
- **Purpose**: Final export-ready data
- **Overrides**: Applied and highlighted in GOLD
- **Use case**: See exactly what will be exported to XML
- **Highlight**: User overrides appear with gold background
- **Reference**: Shows "USER_OVERRIDE" for overridden values

---

## How to Apply an Override

### Example: Override MeltingTemperature for Aluminum

1. **Select Material**: Click "Aluminum" in left sidebar

2. **Fill Override Panel** (right side):
   ```
   Property Path: properties.Thermal.MeltingTemperature
   Value: 935.0
   Unit: K
   Reason: Updated experimental value from lab
   ```

3. **Click "Apply Override"**

4. **Check Results**:
   - **Original Data Tab**: Still shows 933.5 K and 933.32 K (unchanged)
   - **Overrides Tab**: Now shows comparison row
   - **Active View Tab**: Shows 935.0 K with GOLD highlight

---

## Property Path Format

### For Properties
Format: `properties.<Category>.<PropertyName>`

Examples:
```
properties.Phase.State
properties.Thermal.MeltingTemperature
properties.Thermal.Cp
properties.Mechanical.Density
```

### For Models (Simple Parameters)
Format: `models.<ModelType>.<ParameterName>`

Examples:
```
models.ElasticModel.Density
models.ElasticModel.SoundSpeed
models.ElastoPlastic.ShearModulus
```

### For Models (Nested Parameters)
Format: `models.<ModelType>.<SubModel>.<ParameterName>`

Examples:
```
models.ElasticModel.ThermoMechanical.Density
models.ElasticModel.ThermoMechanical.MeltingTemperature
models.ElastoPlastic.JohnsonCookModelConstants.A
```

### For EOS Model Rows
Format: `models.EOSModel.Row[N].<ParameterName>`

Examples:
```
models.EOSModel.Row[1].K0
models.EOSModel.Row[3].Rho
models.EOSModel.Row[6].unreacted.A
```

---

## Quick Templates

The Override Panel includes quick templates:
- **Density**: `properties.Mechanical.Density`
- **Temperature**: `properties.Thermal.MeltingTemperature`
- **Elastic**: `models.ElasticModel.ShearModulus`

---

## Clearing Overrides

### Clear Single Override
1. Select material
2. Enter property path in Override Panel
3. Click "Clear Override"
4. Confirm deletion

### Clear All Overrides
- Use "List Overrides" button
- Clear each one individually
- OR use CLI: `python main.py clear-overrides <material_name>`

---

## Export with Overrides

1. Select material with overrides
2. Click "Export Material" in toolbar
3. XML file generated with USER_OVERRIDE values
4. Original database remains unchanged

---

## Important Notes

✅ **Non-Destructive**: Overrides NEVER modify the database
✅ **Material-Specific**: Each override applies to ONE material only
✅ **Reversible**: You can clear any override anytime
✅ **Export-Ready**: Active View shows exactly what exports to XML

❌ **Original Data Tab**: Never changes, always shows database values
❌ **Don't Modify XML**: Always use the GUI or CLI to set overrides
❌ **Path Must Match**: Property path must exactly match database structure
