#!/usr/bin/env python3
"""
LASL Explosive Property Data - Material Templates
Fill in data from PDF and run to generate XML files
"""

from create_new_material import save_material_xml

# ============================================================================
# TEMPLATE: Copy this template for each material in LASL PDF
# ============================================================================

LASL_MATERIALS = [
    
    # ========== MATERIAL 1: Composition B ==========
    {
        'name': 'COMP-B',
        'description': 'Composition B explosive - 60% RDX, 40% TNT binder',
        
        'properties': {
            'Phase': {
                'Density': [
                    {'value': '1.717', 'unit': 'g/cm^3', 'ref': '1', 'note': 'cast density'}
                ],
                'Melting Point': [
                    {'value': '79', 'unit': '°C', 'ref': '1'}
                ]
            },
            'Thermal': {
                'Thermal Conductivity': [
                    {'value': '0.23', 'unit': 'W/m-K', 'ref': '1'}
                ],
                'Specific Heat': [
                    {'value': '1050', 'unit': 'J/kg-K', 'ref': '1'}
                ]
            },
            'Detonation': {
                'Detonation Velocity': [
                    {'value': '7980', 'unit': 'm/s', 'ref': '1'}
                ],
                'Detonation Pressure': [
                    {'value': '29.5', 'unit': 'GPa', 'ref': '1'}
                ],
                'Chapman-Jouguet Temperature': [
                    {'value': '3500', 'unit': 'K', 'ref': '1'}
                ]
            }
        },
        
        'models': {
            'EOSModel': {
                'JWL': {
                    'A': {'value': '524.2', 'unit': 'GPa', 'ref': '1'},
                    'B': {'value': '7.678', 'unit': 'GPa', 'ref': '1'},
                    'R1': {'value': '4.2', 'unit': '--', 'ref': '1'},
                    'R2': {'value': '1.1', 'unit': '--', 'ref': '1'},
                    'omega': {'value': '0.34', 'unit': '--', 'ref': '1'}
                }
            }
        }
    },
    
    # ========== MATERIAL 2: Composition C-4 ==========
    {
        'name': 'COMP-C4',
        'description': 'Composition C-4 plastic explosive - 91% RDX',
        
        'properties': {
            'Phase': {
                'Density': [
                    {'value': '1.601', 'unit': 'g/cm^3', 'ref': '1'}
                ]
            },
            'Detonation': {
                'Detonation Velocity': [
                    {'value': '8193', 'unit': 'm/s', 'ref': '1', 'note': 'at 1.601 g/cm³'}
                ],
                'Detonation Pressure': [
                    {'value': '28.0', 'unit': 'GPa', 'ref': '1'}
                ]
            }
        },
        
        'models': {
            'EOSModel': {
                'JWL': {
                    'A': {'value': '609.8', 'unit': 'GPa', 'ref': '1'},
                    'B': {'value': '12.95', 'unit': 'GPa', 'ref': '1'},
                    'R1': {'value': '4.5', 'unit': '--', 'ref': '1'},
                    'R2': {'value': '1.4', 'unit': '--', 'ref': '1'},
                    'omega': {'value': '0.25', 'unit': '--', 'ref': '1'}
                }
            }
        }
    },
    
    # ========== MATERIAL 3: TEMPLATE (Copy and modify) ==========
    # {
    #     'name': 'MATERIAL_NAME',  # e.g., 'OCTOL', 'TETRYL', 'PENTOLITE'
    #     'description': 'Description from PDF',
    #     
    #     'properties': {
    #         'Phase': {
    #             'Density': [
    #                 {'value': 'X.XXX', 'unit': 'g/cm^3', 'ref': '1'}
    #             ],
    #             'Melting Point': [
    #                 {'value': 'XXX', 'unit': '°C', 'ref': '1'}
    #             ]
    #         },
    #         'Thermal': {
    #             'Thermal Conductivity': [
    #                 {'value': 'X.XXX', 'unit': 'W/m-K', 'ref': '1'}
    #             ],
    #             'Specific Heat': [
    #                 {'value': 'XXXX', 'unit': 'J/kg-K', 'ref': '1'}
    #             ]
    #         },
    #         'Detonation': {
    #             'Detonation Velocity': [
    #                 {'value': 'XXXX', 'unit': 'm/s', 'ref': '1'}
    #             ],
    #             'Detonation Pressure': [
    #                 {'value': 'XX.X', 'unit': 'GPa', 'ref': '1'}
    #             ]
    #         }
    #     },
    #     
    #     'models': {
    #         'EOSModel': {
    #             'JWL': {
    #                 'A': {'value': 'XXX.X', 'unit': 'GPa', 'ref': '1'},
    #                 'B': {'value': 'XX.XX', 'unit': 'GPa', 'ref': '1'},
    #                 'R1': {'value': 'X.X', 'unit': '--', 'ref': '1'},
    #                 'R2': {'value': 'X.X', 'unit': '--', 'ref': '1'},
    #                 'omega': {'value': '0.XX', 'unit': '--', 'ref': '1'}
    #             }
    #         }
    #     }
    # },
]

# ============================================================================
# AVAILABLE PROPERTY CATEGORIES (from existing materials)
# ============================================================================
"""
Common properties you can add:

Phase Properties:
- Density
- Melting Point
- Boiling Point
- Molecular Weight

Thermal Properties:
- Thermal Conductivity
- Specific Heat
- Thermal Expansion Coefficient
- Heat of Fusion

Mechanical Properties:
- Bulk Modulus
- Shear Modulus
- Yield Strength
- Poisson Ratio

Detonation Properties:
- Detonation Velocity
- Detonation Pressure
- Chapman-Jouguet Temperature
- Chapman-Jouguet Pressure
- Gurney Energy

Chemical Properties:
- Chemical Formula
- Heat of Formation
- Heat of Combustion

Models:
- ElasticModel -> Elastic (Bulk Modulus, Shear Modulus)
- EOSModel -> JWL (A, B, R1, R2, omega, E0)
- EOSModel -> Mie-Gruneisen (C0, S1, Gamma0)
- StrengthModel -> Johnson-Cook (A, B, n, C, m)
"""

# ============================================================================
# GENERATE XML FILES
# ============================================================================

def generate_all_lasl_materials():
    """Generate XML files for all LASL materials"""
    
    print("="*70)
    print("LASL Explosive Property Data - XML Generator")
    print("="*70)
    print(f"\nGenerating XML files for {len(LASL_MATERIALS)} materials...\n")
    
    for i, material in enumerate(LASL_MATERIALS, 1):
        try:
            filename = save_material_xml(material)
            print(f"  [{i}/{len(LASL_MATERIALS)}] ✅ {material['name']}")
        except Exception as e:
            print(f"  [{i}/{len(LASL_MATERIALS)}] ❌ {material['name']}: {e}")
    
    print("\n" + "="*70)
    print("Generation complete!")
    print("="*70)
    print("\n📝 Next steps:")
    print("1. Review generated XML files in xml/ directory")
    print("2. Import into database:")
    print("   python main.py import-all")
    print("3. Verify in GUI:")
    print("   python run_gui.py")
    print("\n💡 To add more materials:")
    print("   Edit this file and add more dictionaries to LASL_MATERIALS list")

if __name__ == "__main__":
    generate_all_lasl_materials()
