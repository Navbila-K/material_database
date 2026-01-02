#!/usr/bin/env python3
"""
PDF Table Extractor for LASL Explosive Property Data
Helps extract material property tables from PDF
"""

# Uncomment after installing: pip install pdfplumber pandas
# import pdfplumber
# import pandas as pd

def extract_lasl_tables_manual():
    """
    Manual extraction guide for LASL PDF
    
    Since PDF extraction can be unreliable, this guide helps you
    manually extract data from the PDF and format it correctly.
    """
    
    guide = """
    ╔══════════════════════════════════════════════════════════════════╗
    ║  LASL PDF Data Extraction Guide                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    
    📖 HOW TO EXTRACT DATA FROM PDF:
    
    STEP 1: Open PDF and locate material tables
    ────────────────────────────────────────────
    - Look for material name headers
    - Find property tables (usually organized by:)
      • Physical properties (density, melting point)
      • Thermal properties (conductivity, specific heat)
      • Detonation properties (velocity, pressure)
      • JWL EOS parameters (A, B, R1, R2, omega)
    
    STEP 2: Create a data collection sheet
    ───────────────────────────────────────
    For each material, note:
    
    Material: _______________________
    
    ┌─────────────────────────────────────────────────┐
    │ PHYSICAL PROPERTIES                             │
    ├──────────────────────────┬──────────┬───────────┤
    │ Property                 │ Value    │ Unit      │
    ├──────────────────────────┼──────────┼───────────┤
    │ Density                  │          │ g/cm³     │
    │ Melting Point            │          │ °C        │
    │ Molecular Weight         │          │ g/mol     │
    └──────────────────────────┴──────────┴───────────┘
    
    ┌─────────────────────────────────────────────────┐
    │ THERMAL PROPERTIES                              │
    ├──────────────────────────┬──────────┬───────────┤
    │ Thermal Conductivity     │          │ W/m-K     │
    │ Specific Heat            │          │ J/kg-K    │
    └──────────────────────────┴──────────┴───────────┘
    
    ┌─────────────────────────────────────────────────┐
    │ DETONATION PROPERTIES                           │
    ├──────────────────────────┬──────────┬───────────┤
    │ Detonation Velocity      │          │ m/s       │
    │ Detonation Pressure      │          │ GPa       │
    │ CJ Temperature           │          │ K         │
    └──────────────────────────┴──────────┴───────────┘
    
    ┌─────────────────────────────────────────────────┐
    │ JWL EOS PARAMETERS                              │
    ├──────────────────────────┬──────────┬───────────┤
    │ A                        │          │ GPa       │
    │ B                        │          │ GPa       │
    │ R1                       │          │ --        │
    │ R2                       │          │ --        │
    │ omega (ω)                │          │ --        │
    │ E0                       │          │ GPa       │
    └──────────────────────────┴──────────┴───────────┘
    
    STEP 3: Fill data into lasl_materials_template.py
    ──────────────────────────────────────────────────
    1. Open: lasl_materials_template.py
    2. Copy the template section
    3. Replace 'MATERIAL_NAME' with actual name
    4. Fill in all values from your extraction sheet
    5. Repeat for each material
    
    STEP 4: Generate XML files
    ───────────────────────────
    $ python lasl_materials_template.py
    
    STEP 5: Import into database
    ─────────────────────────────
    $ python main.py import-all
    
    ═══════════════════════════════════════════════════════════
    
    📋 COMMON MATERIALS IN LASL HANDBOOK:
    
    1. Composition B (COMP-B)
    2. Composition C-4 (COMP-C4)
    3. Octol (70/30 HMX/TNT)
    4. Pentolite (50/50 PETN/TNT)
    5. Tetryl
    6. Picric Acid
    7. Baratol
    8. Amatex
    9. Tritonal
    10. H-6
    11. LX-04
    12. LX-07
    13. LX-10
    14. LX-14
    15. PBX-9404
    16. PBX-9501
    
    ═══════════════════════════════════════════════════════════
    
    💡 TIPS:
    
    - Start with 2-3 materials first to test the process
    - Use Ctrl+F in PDF to find specific properties
    - Note page numbers for reference tracking
    - If property is missing in PDF, skip it (don't guess)
    - Units MUST match exactly (check conversion if needed)
    - JWL parameters are usually in tables labeled "EOS"
    
    ═══════════════════════════════════════════════════════════
    """
    
    print(guide)

def extract_with_pdfplumber(pdf_path):
    """
    Automated extraction using pdfplumber (experimental)
    
    NOTE: This may not work perfectly due to PDF formatting
    Manual extraction is more reliable
    """
    
    print("⚠️  Automated PDF extraction is experimental")
    print("   Manual extraction is recommended for accuracy\n")
    
    # Uncomment if you have pdfplumber installed:
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"📄 PDF Pages: {len(pdf.pages)}")
            
            # Extract tables from all pages
            for i, page in enumerate(pdf.pages[:10], 1):  # First 10 pages
                print(f"\n--- Page {i} ---")
                tables = page.extract_tables()
                
                if tables:
                    for j, table in enumerate(tables, 1):
                        print(f"  Table {j}:")
                        df = pd.DataFrame(table[1:], columns=table[0])
                        print(df.head())
                else:
                    print("  No tables found")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nPlease use manual extraction instead.")
    """
    
    print("\n⚠️  pdfplumber not installed or not working")
    print("   Using manual extraction guide instead...\n")
    extract_lasl_tables_manual()

# ============================================================================
# QUICK REFERENCE: Property Names and Units
# ============================================================================

PROPERTY_REFERENCE = {
    'Phase': {
        'Density': 'g/cm^3',
        'Melting Point': '°C',
        'Boiling Point': '°C',
        'Molecular Weight': 'g/mol',
    },
    'Thermal': {
        'Thermal Conductivity': 'W/m-K',
        'Specific Heat': 'J/kg-K',
        'Thermal Expansion Coefficient': '1/K',
    },
    'Mechanical': {
        'Bulk Modulus': 'GPa',
        'Shear Modulus': 'GPa',
        'Yield Strength': 'GPa',
        'Poisson Ratio': '--',
    },
    'Detonation': {
        'Detonation Velocity': 'm/s',
        'Detonation Pressure': 'GPa',
        'Chapman-Jouguet Temperature': 'K',
        'Gurney Energy': 'km/s',
    },
    'JWL_Parameters': {
        'A': 'GPa',
        'B': 'GPa',
        'R1': '--',
        'R2': '--',
        'omega': '--',
        'E0': 'GPa',
    }
}

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        extract_with_pdfplumber(pdf_path)
    else:
        extract_lasl_tables_manual()
