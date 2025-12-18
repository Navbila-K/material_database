# QUICK COMMAND REFERENCE - Materials Database

## 🚀 When You Forget - Start Here!

### 1️⃣ First Time Setup (Only Once)

```bash
# Create PostgreSQL database
createdb Materials_DB

# Configure database in config.py (edit with your credentials)
# Then initialize
python main.py init

# Import all materials
python main.py import-all
```

---

## 📖 Daily Use Commands

### List Materials
```bash
python main.py list
```

### Query a Material
```bash
python main.py query Copper
python main.py query Aluminum
python main.py query Sucrose
```

### Export to XML
```bash
python main.py export Copper
# Creates: export/output/Copper_exported.xml
```

---

## 🎛️ Override Commands (Most Used)

### Set Value Override
```bash
# Format:
python main.py set-override <Material> <property_path> <value> --unit <unit> --reason <reason>

# Examples:
python main.py set-override Copper properties.Thermal.Cp 400 --unit "J/kg/K" --reason "Lab measurement"
python main.py set-override Copper models.ElastoPlastic.ShearModulus 48E9 --unit Pa
```

### Set Reference Preference
```bash
# Format:
python main.py set-preference <Material> <property_path> <ref_id> --reason <reason>

# Example:
python main.py set-preference Copper properties.Mechanical.Density 121 --reason "Most reliable"
```

### List Overrides
```bash
python main.py list-overrides Copper
python main.py list-overrides Sucrose
```

### Clear Overrides
```bash
# Clear specific
python main.py clear-overrides Copper properties.Thermal.Cp

# Clear all for material
python main.py clear-overrides Copper
```

---

## 📝 Property Path Formats

### Properties (3 parts)
```
properties.Category.PropertyName
```

**Examples:**
- `properties.Thermal.Cp`
- `properties.Thermal.Cv`
- `properties.Mechanical.Density`

### Models - Direct Parameters (3 parts)
```
models.ModelType.ParameterName
```

**Examples:**
- `models.ElastoPlastic.ShearModulus`
- `models.ElastoPlastic.YieldStrength`

### Models - Nested Parameters (4 parts)
```
models.ModelType.SubModelType.ParameterName
```

**Examples:**
- `models.ElasticModel.ThermoMechanical.MeltingTemperature`
- `models.ElasticModel.ThermoMechanical.ThermalConductivity`

---

## 🧪 Complete Test Workflow (Copy-Paste)

### Copper Test
```bash
# Check original
python main.py query Copper

# Set 7 overrides
python main.py set-override Copper properties.Thermal.Cp 400 --unit "J/kg/K"
python main.py set-override Copper properties.Thermal.Cv 390 --unit "J/kg/K"
python main.py set-preference Copper properties.Mechanical.Density 121
python main.py set-override Copper models.ElasticModel.ThermoMechanical.MeltingTemperature 1358 --unit K
python main.py set-override Copper models.ElasticModel.ThermoMechanical.ThermalConductivity 401 --unit "W/m/K"
python main.py set-override Copper models.ElastoPlastic.ShearModulus 48E9 --unit Pa
python main.py set-override Copper models.ElastoPlastic.YieldStrength 70E6 --unit Pa

# Verify
python main.py list-overrides Copper
python main.py export Copper
grep "USER_OVERRIDE" export/output/Copper_Override_exported.xml
```

### Sucrose Test
```bash
python main.py set-override Sucrose properties.Thermal.Cp 1300 --unit "J/kg/K"
python main.py set-override Sucrose properties.Thermal.Cv 450 --unit "J/kg/K"
python main.py set-override Sucrose properties.Mechanical.Density 1600 --unit "kg/m^3"
python main.py set-override Sucrose models.ElasticModel.ThermoMechanical.MeltingTemperature 465 --unit K
python main.py set-override Sucrose models.ElasticModel.ThermoMechanical.ThermalConductivity 500 --unit "W/m/K"
python main.py set-override Sucrose models.ElastoPlastic.ShearModulus 9E9 --unit Pa
python main.py set-override Sucrose models.ElastoPlastic.YieldStrength 50E6 --unit Pa

python main.py list-overrides Sucrose
python main.py export Sucrose
```

---

## 🗃️ Database Commands

### Connect to Database
```bash
psql -U postgres -d Materials_DB
```

### Check Materials
```sql
SELECT material_id, name FROM materials;
```

### Check Overrides
```sql
SELECT material_id, property_path, override_type 
FROM material_overrides;
```

---

## 🧪 Testing

```bash
# Run override tests (5/5 should pass)
python test_overrides.py
```

---

## 📚 Documentation Files

- **README.md** - Main documentation (this is comprehensive!)
- **QUICKSTART.md** - Quick setup guide
- **OVERRIDE_GUIDE.md** - Complete override system guide
- **SUCROSE_OVERRIDE_COMMANDS.md** - Sucrose test commands
- **PHASE3_COMPLETION.md** - Implementation details
- **OVERRIDE_VERIFICATION_COMPLETE.md** - Bug fixes and verification

---

## 🎯 Available Materials

Aluminum, Copper, Magnesium, Nickel, Tantalum, Titanium, Tungsten, RDX, TNT, HMX, PETN, TATB, CL-20, HNS, Nitromethane, Sucrose, Helium

---

## 🔧 Troubleshooting

### Database Not Found
```bash
createdb Materials_DB
python main.py init
python main.py import-all
```

### Connection Error
```bash
# Edit config.py with correct credentials
# Check PostgreSQL is running:
pg_isready
```

### Override Not Working
```bash
# Verify it's stored
python main.py list-overrides <Material>

# Check export
grep "USER_OVERRIDE" export/output/<Material>_Override_exported.xml
```

---

## 💾 Git Commands (For Future Updates)

```bash
# Check status
git status

# Add changes
git add .

# Commit
git commit -m "Your message"

# Push to GitHub
git push origin main

# Pull latest
git pull origin main
```

---

## 🌐 GitHub Repository

https://github.com/Navbila-K/material_database

---

**Remember**: All overrides are NON-DESTRUCTIVE. Original data stays safe! ✅

*Last Updated: December 18, 2025*
