# Materials Database

A simple desktop app to manage material properties for research and simulations.

## What is this?

If you're a researcher working with materials like explosives, metals, or propellants, you know the pain of finding property data scattered across PDFs, papers, and Excel sheets. This tool puts everything in one place.

## What it does

- **Stores material data**: 17 materials with 150+ properties each
- **Shows references**: Every value is linked to the paper it came from
- **Makes charts**: 6 types of charts built-in, no Excel needed
- **Exports data**: One-click export to ANSYS, LS-DYNA, or CSV
- **Tracks changes**: Override published values without losing original data

## Materials included

**Explosives:** RDX, TNT, PETN, HMX, TATB, CL-20, HNS  
**Metals:** Aluminum, Copper, Nickel, Titanium, Tungsten, Tantalum, Magnesium  
**Others:** Sucrose, Nitromethane, Helium

## Quick start

### What you need

- Python 3.13 or newer
- PostgreSQL (any recent version works)

### Install

```bash
# Clone the repo
git clone https://github.com/Navbila-K/material_database.git
cd material_database

# Install dependencies
pip install -r requirements.txt

# Set up database (edit config.py with your PostgreSQL details first)
python main.py init

# Import materials
python main.py import-all

# Import references
python main.py import-references
```

### Run the GUI

```bash
python run_gui.py
```

That's it. The window opens, click around, explore.

## How to use it

### Browse materials

Click on any material in the list. You'll see all its properties organized by category (Thermal, Mechanical, etc.). Each value shows which paper it came from.

### Make charts

Go to the Visualization tab. Pick a chart type, select materials and properties, click Generate. Export as PNG or SVG for your thesis.

### Override values

Found better data from your lab? Click the Override tab, set your value, add a note. The original stays in the database, but you see your corrected value everywhere.

### Export for simulations

Need data in ANSYS? Click Export, select the material, choose format. Done. No manual typing.

## Why we built this

We got tired of:
- Searching for the same property in 5 different papers
- Making charts in Excel for hours
- Typing material data into simulation software (and making typos)
- Losing track of which reference said what

So we built this. It's not fancy, but it works.

## Tech stuff

- **Frontend:** PyQt6 (desktop GUI)
- **Database:** PostgreSQL 
- **Charts:** Matplotlib
- **Language:** Python 3.13

## Project structure

```
materials_db/
├── gui/              # GUI code
│   ├── main_window.py
│   └── views/        # Different tabs
├── db/               # Database stuff
│   ├── schema.py
│   ├── query.py
│   └── insert.py
├── parser/           # XML parsers
├── overrides/        # Override system
├── export/           # Export to XML/CSV
├── xml/              # Material XML files
└── run_gui.py        # Start here
```

## Features

**What works:**
- View all material properties
- See references for each value
- 6 types of charts (comparison, temperature plots, etc.)
- Override system with rollback
- Export to ANSYS, LS-DYNA, CSV
- Dark and light themes
- Search and filter

**What's coming:**
- More materials (polymers, ceramics)
- Machine learning predictions
- Web version
- Mobile app

## Common issues

**"Can't connect to database"**  
Check your PostgreSQL is running and config.py has the right credentials.

**"Import failed"**  
Make sure you ran `python main.py init` first to create tables.

**"GUI won't start"**  
Install PyQt6: `pip install PyQt6`

**"Charts look weird"**  
Update matplotlib: `pip install --upgrade matplotlib`

## Examples

### Command line

```bash
# Query a material
python main.py query Copper

# Export to XML
python main.py export RDX

# Set an override
python main.py set-override Aluminum "Thermal/Thermal Conductivity" 240

# Clear overrides
python main.py clear-overrides Aluminum
```

### In the GUI

Just click around. It's pretty obvious. Material list on left, properties on right, tabs at top.

## Who made this

Two students who got annoyed at how hard it is to find material data for simulations.

## License

MIT - do whatever you want with it.

## Contributing

Found a bug? Have data to add? Pull requests welcome. Or just open an issue.

## Contact

- GitHub: [@Navbila-K](https://github.com/Navbila-K)
- Issues: https://github.com/Navbila-K/material_database/issues

## Acknowledgments

Thanks to all the researchers whose papers we referenced. The 112 sources are listed in the References tab.

---

**Note:** This is research software. Double-check values before using in real simulations. We did our best, but verify critical data yourself.
