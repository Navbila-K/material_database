#!/usr/bin/env python3
"""
Unit Conversion Helper for LASL Materials
Converts common units found in LASL handbook to database format
"""

# ============================================================================
# UNIT CONVERSIONS
# ============================================================================

CONVERSIONS = {
    'Density': {
        'g/cc': ('g/cm^3', 1.0),
        'kg/m^3': ('g/cm^3', 0.001),
        'lb/in^3': ('g/cm^3', 27.68),
        'g/ml': ('g/cm^3', 1.0),
    },
    
    'Pressure': {
        'kbar': ('GPa', 0.1),
        'Mbar': ('GPa', 100),
        'Pa': ('GPa', 1e-9),
        'MPa': ('GPa', 0.001),
        'psi': ('GPa', 6.89476e-6),
        'ksi': ('GPa', 6.89476e-3),
    },
    
    'Velocity': {
        'mm/μs': ('m/s', 1000),
        'mm/us': ('m/s', 1000),
        'km/s': ('m/s', 1000),
        'cm/s': ('m/s', 0.01),
        'ft/s': ('m/s', 0.3048),
    },
    
    'Energy': {
        'cal/g': ('kJ/kg', 4.184),
        'kcal/kg': ('kJ/kg', 4.184),
        'cal/g-K': ('J/kg-K', 4184),
        'kcal/mol': ('kJ/mol', 4.184),
        'eV': ('J', 1.60218e-19),
    },
    
    'Temperature': {
        'F': ('C', lambda f: (f - 32) * 5/9),
        'K': ('C', lambda k: k - 273.15),
        'R': ('K', lambda r: r * 5/9),  # Rankine to Kelvin
    },
    
    'Thermal Conductivity': {
        'cal/cm-s-K': ('W/m-K', 418.4),
        'BTU/hr-ft-F': ('W/m-K', 1.731),
    },
}

# ============================================================================
# CONVERSION FUNCTIONS
# ============================================================================

def convert_density(value, from_unit):
    """Convert density to g/cm³"""
    if from_unit in CONVERSIONS['Density']:
        target_unit, factor = CONVERSIONS['Density'][from_unit]
        return value * factor, target_unit
    return value, from_unit

def convert_pressure(value, from_unit):
    """Convert pressure to GPa"""
    if from_unit in CONVERSIONS['Pressure']:
        target_unit, factor = CONVERSIONS['Pressure'][from_unit]
        return value * factor, target_unit
    return value, from_unit

def convert_velocity(value, from_unit):
    """Convert velocity to m/s"""
    if from_unit in CONVERSIONS['Velocity']:
        target_unit, factor = CONVERSIONS['Velocity'][from_unit]
        return value * factor, target_unit
    return value, from_unit

def convert_energy(value, from_unit):
    """Convert energy to standard units"""
    if from_unit in CONVERSIONS['Energy']:
        target_unit, factor = CONVERSIONS['Energy'][from_unit]
        return value * factor, target_unit
    return value, from_unit

def convert_temperature(value, from_unit):
    """Convert temperature"""
    if from_unit in CONVERSIONS['Temperature']:
        target_unit, converter = CONVERSIONS['Temperature'][from_unit]
        if callable(converter):
            return converter(value), target_unit
        return value * converter, target_unit
    return value, from_unit

# ============================================================================
# INTERACTIVE CONVERTER
# ============================================================================

def convert_value(value, from_unit, property_type):
    """
    Convert a value to database standard units
    
    Args:
        value: Numeric value to convert
        from_unit: Source unit (e.g., 'kbar', 'mm/μs')
        property_type: Type of property ('Density', 'Pressure', etc.)
    
    Returns:
        (converted_value, target_unit)
    """
    
    converters = {
        'Density': convert_density,
        'Pressure': convert_pressure,
        'Velocity': convert_velocity,
        'Energy': convert_energy,
        'Temperature': convert_temperature,
    }
    
    if property_type in converters:
        return converters[property_type](value, from_unit)
    
    return value, from_unit

# ============================================================================
# QUICK REFERENCE TABLE
# ============================================================================

def print_conversion_table():
    """Print quick reference table of common conversions"""
    
    print("\n" + "="*80)
    print(" LASL UNIT CONVERSION QUICK REFERENCE")
    print("="*80)
    
    print("\n📊 DENSITY CONVERSIONS")
    print("─" * 80)
    print(f"{'From':<20} {'To':<20} {'Factor':<20} {'Example':<20}")
    print("─" * 80)
    for from_unit, (to_unit, factor) in CONVERSIONS['Density'].items():
        example = f"{factor:.4f} × value"
        print(f"{from_unit:<20} {to_unit:<20} {factor:<20.4f} {example:<20}")
    
    print("\n💥 PRESSURE CONVERSIONS")
    print("─" * 80)
    print(f"{'From':<20} {'To':<20} {'Factor':<20} {'Example':<20}")
    print("─" * 80)
    for from_unit, (to_unit, factor) in CONVERSIONS['Pressure'].items():
        example = f"{factor:.6f} × value" if factor < 1 else f"{factor:.2f} × value"
        print(f"{from_unit:<20} {to_unit:<20} {factor:<20.6f} {example:<20}")
    
    print("\n🚀 VELOCITY CONVERSIONS")
    print("─" * 80)
    print(f"{'From':<20} {'To':<20} {'Factor':<20} {'Example':<20}")
    print("─" * 80)
    for from_unit, (to_unit, factor) in CONVERSIONS['Velocity'].items():
        example = f"{factor:.4f} × value"
        print(f"{from_unit:<20} {to_unit:<20} {factor:<20.4f} {example:<20}")
    
    print("\n🔥 ENERGY CONVERSIONS")
    print("─" * 80)
    print(f"{'From':<20} {'To':<20} {'Factor':<20} {'Example':<20}")
    print("─" * 80)
    for from_unit, (to_unit, factor) in CONVERSIONS['Energy'].items():
        if isinstance(factor, (int, float)):
            example = f"{factor:.4f} × value"
            print(f"{from_unit:<20} {to_unit:<20} {factor:<20.4f} {example:<20}")
    
    print("\n🌡️  TEMPERATURE CONVERSIONS")
    print("─" * 80)
    print(f"{'From':<20} {'To':<20} {'Formula':<40}")
    print("─" * 80)
    print(f"{'F (Fahrenheit)':<20} {'C (Celsius)':<20} {'(F - 32) × 5/9':<40}")
    print(f"{'K (Kelvin)':<20} {'C (Celsius)':<20} {'K - 273.15':<40}")
    print(f"{'R (Rankine)':<20} {'K (Kelvin)':<20} {'R × 5/9':<40}")
    
    print("\n" + "="*80)
    
    # Examples
    print("\n📝 COMMON EXAMPLES:")
    print("─" * 80)
    
    examples = [
        ("Density", "1.5 g/cc", "1.5 g/cm³", "Direct equivalence"),
        ("Pressure", "295 kbar", "29.5 GPa", "Divide by 10"),
        ("Velocity", "7.98 mm/μs", "7980 m/s", "Multiply by 1000"),
        ("Energy", "1.05 kcal/kg", "4.393 kJ/kg", "Multiply by 4.184"),
        ("Temperature", "77°F", "25°C", "(77-32)×5/9"),
    ]
    
    for prop_type, from_val, to_val, note in examples:
        print(f"\n{prop_type}:")
        print(f"  From: {from_val}")
        print(f"  To:   {to_val}")
        print(f"  Note: {note}")
    
    print("\n" + "="*80)

# ============================================================================
# INTERACTIVE MODE
# ============================================================================

def interactive_convert():
    """Interactive unit converter"""
    
    print("\n🔧 INTERACTIVE UNIT CONVERTER")
    print("─" * 80)
    
    # Get property type
    print("\nSelect property type:")
    print("1. Density")
    print("2. Pressure")
    print("3. Velocity")
    print("4. Energy")
    print("5. Temperature")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    prop_types = {
        '1': 'Density',
        '2': 'Pressure',
        '3': 'Velocity',
        '4': 'Energy',
        '5': 'Temperature',
    }
    
    if choice not in prop_types:
        print("❌ Invalid choice")
        return
    
    prop_type = prop_types[choice]
    
    # Get value
    try:
        value = float(input(f"\nEnter value: "))
    except ValueError:
        print("❌ Invalid number")
        return
    
    # Get source unit
    print(f"\nAvailable units for {prop_type}:")
    for unit in CONVERSIONS[prop_type].keys():
        print(f"  - {unit}")
    
    from_unit = input(f"\nEnter source unit: ").strip()
    
    # Convert
    result, target_unit = convert_value(value, from_unit, prop_type)
    
    print("\n" + "─" * 80)
    print(f"✅ RESULT: {value} {from_unit} = {result:.6f} {target_unit}")
    print("─" * 80)

# ============================================================================
# BATCH CONVERSION
# ============================================================================

def batch_convert_from_file(input_file, output_file):
    """
    Convert units from CSV file
    
    Input CSV format:
    property_type,value,from_unit
    Density,1.5,g/cc
    Pressure,295,kbar
    """
    
    import csv
    
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        
        results = []
        for row in reader:
            prop_type, value, from_unit = row
            value = float(value)
            result, target_unit = convert_value(value, from_unit, prop_type)
            results.append([prop_type, value, from_unit, result, target_unit])
    
    with open(output_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['Property', 'Original Value', 'Original Unit', 'Converted Value', 'Target Unit'])
        writer.writerows(results)
    
    print(f"✅ Converted {len(results)} values")
    print(f"   Output: {output_file}")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--interactive':
            interactive_convert()
        elif sys.argv[1] == '--batch' and len(sys.argv) == 4:
            batch_convert_from_file(sys.argv[2], sys.argv[3])
        else:
            print("Usage:")
            print("  python unit_converter.py              # Show conversion table")
            print("  python unit_converter.py --interactive  # Interactive converter")
            print("  python unit_converter.py --batch input.csv output.csv")
    else:
        print_conversion_table()
