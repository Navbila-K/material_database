"""
Main orchestration script for Material Database Engine.
Provides command-line interface for all operations.

Usage:
    python main.py init                                      # Initialize database schema
    python main.py import <xml_file>                         # Import material from XML
    python main.py import-all                                # Import all XML files from xml/
    python main.py list                                      # List all materials
    python main.py export <material_name>                    # Export material to XML
    python main.py export-all                                # Export all materials
    python main.py query <material_name>                     # Query and display material data
    python main.py reset                                     # Reset database (WARNING: deletes all data)
    
    # Override commands
    python main.py set-preference <material> <path> <ref>    # Set preferred reference
    python main.py set-override <material> <path> <value>    # Set value override
    python main.py list-overrides <material>                 # List all overrides
    python main.py clear-overrides <material> [path]         # Clear overrides
    
    # References commands
    python main.py import-references                         # Import References.xml into database
    python main.py query-reference <id>                      # Query specific reference by ID
    python main.py list-references                           # List all references
    python main.py material-references <material>            # Show refs used by material
"""
import sys
import os
import argparse
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import DatabaseManager
from db.insert import MaterialInserter
from db.query import MaterialQuerier
from db.override_storage import OverrideStorage
from parser.xml_parser import parse_material_xml
from export.xml_exporter import export_material_to_xml
from config import XML_DIR, EXPORT_DIR


class MaterialDatabaseCLI:
    """Command-line interface for Material Database Engine."""
    
    def __init__(self):
        """Initialize CLI with database manager."""
        self.db = DatabaseManager()
        self.override_storage = None  # Lazy initialization
    
    def _get_override_storage(self):
        """Lazy initialization of override storage."""
        if self.override_storage is None:
            conn = self.db.connect()
            self.override_storage = OverrideStorage(conn)
        return self.override_storage
    
    def init_database(self):
        """Initialize database schema."""
        print("Initializing database schema...")
        
        try:
            self.db.test_connection()
            self.db.create_schema()
            print("\n✓ Database initialization complete!")
        except Exception as e:
            print(f"\n✗ Database initialization failed: {e}")
            sys.exit(1)
    
    def reset_database(self):
        """Reset database (drop and recreate schema)."""
        print("WARNING: This will delete all data!")
        response = input("Are you sure? (yes/no): ")
        
        if response.lower() == 'yes':
            try:
                self.db.reset_schema()
                print("\n✓ Database reset complete!")
            except Exception as e:
                print(f"\n✗ Database reset failed: {e}")
                sys.exit(1)
        else:
            print("Reset cancelled.")
    
    def import_material(self, xml_file_path: str):
        """
        Import a single material from XML file.
        
        Args:
            xml_file_path: Path to XML file
        """
        if not os.path.exists(xml_file_path):
            print(f"✗ File not found: {xml_file_path}")
            return
        
        print(f"\nImporting: {os.path.basename(xml_file_path)}")
        print("-" * 50)
        
        try:
            # Parse XML
            print("  Parsing XML...")
            material_data = parse_material_xml(xml_file_path)
            
            # Insert into database
            print("  Inserting into database...")
            inserter = MaterialInserter(self.db)
            material_id = inserter.insert_material(material_data)
            
            print(f"\n✓ Import complete! Material ID: {material_id}")
            
        except Exception as e:
            print(f"\n✗ Import failed: {e}")
            import traceback
            traceback.print_exc()
    
    def import_all(self):
        """Import all XML files from xml/ directory."""
        xml_files = list(Path(XML_DIR).glob("*.xml"))
        
        # Exclude References.xml
        xml_files = [f for f in xml_files if f.name != "References.xml"]
        
        if not xml_files:
            print("✗ No XML files found in xml/ directory")
            return
        
        print(f"\nFound {len(xml_files)} material files")
        print("=" * 50)
        
        success_count = 0
        fail_count = 0
        
        for xml_file in sorted(xml_files):
            try:
                self.import_material(str(xml_file))
                success_count += 1
            except Exception as e:
                print(f"✗ Failed to import {xml_file.name}: {e}")
                fail_count += 1
            print()
        
        print("=" * 50)
        print(f"Import complete: {success_count} succeeded, {fail_count} failed")
    
    def list_materials(self):
        """List all materials in database."""
        querier = MaterialQuerier(self.db)
        materials = querier.list_materials()
        
        if not materials:
            print("No materials found in database.")
            print("Use 'python main.py import-all' to import materials.")
            return
        
        print(f"\nMaterials in database: {len(materials)}")
        print("=" * 70)
        print(f"{'ID':<5} {'Name':<20} {'XML ID':<20} {'Version':<15}")
        print("-" * 70)
        
        for mat in materials:
            print(f"{mat['material_id']:<5} {mat['name']:<20} {mat['xml_id']:<20} {mat['version'] or 'N/A':<15}")
        
        print("=" * 70)
    
    def query_material(self, material_name: str):
        """
        Query and display ALL material data in detail.
        
        Args:
            material_name: Name of material to query
        """
        querier = MaterialQuerier(self.db)
        material_data = querier.get_material_by_name(material_name)
        
        if not material_data:
            print(f"✗ Material not found: {material_name}")
            return
        
        print(f"\n{'='*80}")
        print(f"MATERIAL: {material_data['metadata']['name']}")
        print(f"{'='*80}")
        
        # ========== METADATA ==========
        print("\n" + "="*80)
        print("METADATA")
        print("="*80)
        metadata = material_data['metadata']
        print(f"  ID:              {metadata.get('id')}")
        print(f"  Name:            {metadata.get('name')}")
        print(f"  Author:          {metadata.get('author') or '(empty)'}")
        print(f"  Date:            {metadata.get('date') or '(empty)'}")
        print(f"  Version:         {metadata.get('version')}")
        print(f"  Version Meaning: {metadata.get('version_meaning')}")
        
        # ========== PROPERTIES ==========
        print("\n" + "="*80)
        print("PROPERTIES")
        print("="*80)
        
        for category, props in material_data['properties'].items():
            print(f"\n  [{category}]")
            print("  " + "-"*76)
            
            if category == 'Phase':
                print(f"    State: {props.get('State')}")
            else:
                for prop_name, prop_data in props.items():
                    entries = prop_data.get('entries', [])
                    unit = prop_data.get('unit') or 'no unit'
                    
                    print(f"\n    {prop_name} (unit: {unit})")
                    if entries:
                        for idx, entry in enumerate(entries, 1):
                            value = entry.get('value')
                            ref = entry.get('ref')
                            
                            if value:
                                ref_str = f" [ref: {ref}]" if ref else ""
                                print(f"      Entry {idx}: {value}{ref_str}")
                            else:
                                print(f"      Entry {idx}: (empty)")
                    else:
                        print(f"      No entries")
        
        # ========== MODELS ==========
        print("\n" + "="*80)
        print("MODELS")
        print("="*80)
        
        for model_type, model_data in material_data['models'].items():
            print(f"\n  [{model_type}]")
            print("  " + "-"*76)
            
            if model_type == 'ElasticModel':
                self._print_elastic_model(model_data)
            elif model_type == 'ElastoPlastic':
                self._print_elastoplastic_model(model_data)
            elif model_type == 'ReactionModel':
                self._print_reaction_model(model_data)
            elif model_type == 'EOSModel':
                self._print_eos_model(model_data)
        
        print("\n" + "="*80)
    
    def _print_elastic_model(self, model_data):
        """Print ElasticModel details."""
        thermo = model_data.get('ThermoMechanical', {})
        if thermo:
            print("\n    ThermoMechanical:")
            for param_name, param_value in thermo.items():
                if isinstance(param_value, dict) and not isinstance(param_value, list):
                    # Complex structure like SpecificHeatConstants
                    print(f"\n      {param_name}:")
                    for sub_name, sub_data in param_value.items():
                        if isinstance(sub_data, dict):
                            value = sub_data.get('value') or '(empty)'
                            unit = sub_data.get('unit') or ''
                            print(f"        {sub_name}: {value} {unit}".strip())
                elif isinstance(param_value, list):
                    # List of entries - show ALL entries
                    print(f"\n      {param_name}:")
                    for idx, entry in enumerate(param_value, 1):
                        value = entry.get('value') or '(empty)'
                        unit = entry.get('unit') or ''
                        ref = entry.get('ref')
                        ref_str = f" [ref: {ref}]" if ref else ""
                        print(f"        Entry {idx}: {value} {unit}{ref_str}".strip())
                else:
                    # Single value (shouldn't happen but handle gracefully)
                    print(f"\n      {param_name}: {param_value}")
    
    def _print_elastoplastic_model(self, model_data):
        """Print ElastoPlastic model details."""
        for param_name, param_value in model_data.items():
            if 'Constants' in param_name or 'Model' in param_name:
                # Complex structure
                print(f"\n    {param_name}:")
                for sub_name, sub_data in param_value.items():
                    if isinstance(sub_data, dict):
                        value = sub_data.get('value') or '(empty)'
                        unit = sub_data.get('unit') or ''
                        ref = sub_data.get('ref')
                        ref_str = f" [ref: {ref}]" if ref else ""
                        print(f"      {sub_name}: {value} {unit}{ref_str}".strip())
            else:
                # Simple entries - show ALL entries
                print(f"\n    {param_name}:")
                if isinstance(param_value, list):
                    for idx, entry in enumerate(param_value, 1):
                        value = entry.get('value') or '(empty)'
                        unit = entry.get('unit') or ''
                        ref = entry.get('ref')
                        ref_str = f" [ref: {ref}]" if ref else ""
                        print(f"      Entry {idx}: {value} {unit}{ref_str}".strip())
                elif isinstance(param_value, dict):
                    value = param_value.get('value') or '(empty)'
                    unit = param_value.get('unit') or ''
                    ref = param_value.get('ref')
                    ref_str = f" [ref: {ref}]" if ref else ""
                    print(f"      Entry 1: {value} {unit}{ref_str}".strip())
    
    def _print_reaction_model(self, model_data):
        """Print ReactionModel details."""
        # Print Kind
        kind = model_data.get('Kind')
        print(f"\n    Kind: {kind or '(empty)'}")
        
        # Print indexed parameters
        for param_name in ['LnZ', 'ActivationEnergy', 'HeatRelease']:
            if param_name in model_data:
                print(f"\n    {param_name}:")
                for entry in model_data[param_name]:
                    index = entry.get('index')
                    value = entry.get('value') or '(empty)'
                    unit = entry.get('unit') or ''
                    ref = entry.get('ref')
                    ref_str = f" [ref: {ref}]" if ref else ""
                    print(f"      Entry {index}: {value} {unit}{ref_str}".strip())
        
        # Print ReactionModelParameter
        if 'ReactionModelParameter' in model_data:
            print(f"\n    ReactionModelParameter:")
            for sub_name, sub_data in model_data['ReactionModelParameter'].items():
                if isinstance(sub_data, dict):
                    value = sub_data.get('value') or '(empty)'
                    unit = sub_data.get('unit') or ''
                    print(f"      {sub_name}: {value} {unit}".strip())
    
    def _print_eos_model(self, model_data):
        """Print EOSModel details."""
        rows = model_data.get('rows', [])
        for row in rows:
            row_index = row.get('index')
            print(f"\n    Row {row_index}:")
            parameters = row.get('parameters', {})
            
            for param_name, param_data in parameters.items():
                if isinstance(param_data, dict) and 'value' not in param_data:
                    # Nested structure (unreacted/reacted)
                    print(f"      {param_name}:")
                    for sub_name, sub_data in param_data.items():
                        if isinstance(sub_data, dict):
                            value = sub_data.get('value') or '(empty)'
                            unit = sub_data.get('unit') or ''
                            print(f"        {sub_name}: {value} {unit}".strip())
                else:
                    # Simple parameter
                    if isinstance(param_data, dict):
                        value = param_data.get('value') or '(empty)'
                        unit = param_data.get('unit') or ''
                        print(f"      {param_name}: {value} {unit}".strip())
    
    def export_material(self, material_name: str):
        """
        Export material to XML file.
        
        Args:
            material_name: Name of material to export
        """
        querier = MaterialQuerier(self.db)
        storage = self._get_override_storage()
        
        # Get material ID to check for overrides
        material_id = self._get_material_id(material_name)
        if material_id is None:
            print(f"✗ Material not found: {material_name}")
            return
        
        # Check if material has overrides
        has_overrides = storage.has_overrides(material_id)
        
        # Get material data (with overrides applied)
        material_data = querier.get_material_by_name(material_name)
        
        if not material_data:
            print(f"✗ Material not found: {material_name}")
            return
        
        # Set filename based on whether overrides exist
        if has_overrides:
            output_filename = f"{material_name}_Override_exported.xml"
        else:
            output_filename = f"{material_name}_exported.xml"
        
        output_path = os.path.join(EXPORT_DIR, output_filename)
        
        print(f"\nExporting: {material_name}")
        print(f"Output: {output_path}")
        print("-" * 50)
        
        try:
            export_material_to_xml(material_data, output_path)
            print(f"\n✓ Export complete!")
        except Exception as e:
            print(f"\n✗ Export failed: {e}")
            import traceback
            traceback.print_exc()
    
    def export_all(self):
        """Export all materials to XML files."""
        querier = MaterialQuerier(self.db)
        materials = querier.list_materials()
        
        if not materials:
            print("No materials found in database.")
            return
        
        print(f"\nExporting {len(materials)} materials")
        print("=" * 50)
        
        success_count = 0
        fail_count = 0
        
        for mat in materials:
            try:
                self.export_material(mat['name'])
                success_count += 1
            except Exception as e:
                print(f"✗ Failed to export {mat['name']}: {e}")
                fail_count += 1
            print()
        
        print("=" * 50)
        print(f"Export complete: {success_count} succeeded, {fail_count} failed")
    
    def set_preference(self, material_name: str, property_path: str, preferred_ref: str):
        """
        Set preferred reference for a property with multiple values.
        
        Args:
            material_name: Name of material
            property_path: Path to property (e.g., 'properties.Thermal.Density')
            preferred_ref: Preferred reference ID
        """
        querier = MaterialQuerier(self.db)
        material_data = querier.get_material_by_name(material_name, apply_overrides=False)
        
        if not material_data:
            print(f"✗ Material not found: {material_name}")
            return
        
        material_id = self._get_material_id(material_name)
        storage = self._get_override_storage()
        
        print(f"\nSetting preference for: {material_name}")
        print(f"Property path: {property_path}")
        print(f"Preferred reference: {preferred_ref}")
        print("-" * 50)
        
        try:
            storage.save_reference_preference(material_id, property_path, preferred_ref)
            print(f"\n✓ Preference set successfully!")
        except Exception as e:
            print(f"\n✗ Failed to set preference: {e}")
            import traceback
            traceback.print_exc()
    
    def set_override(self, material_name: str, property_path: str, 
                     override_value: str, unit: str = None, reason: str = None):
        """
        Set value override for a property.
        
        Args:
            material_name: Name of material
            property_path: Path to property
            override_value: Override value
            unit: Unit (optional)
            reason: Reason for override (optional)
        """
        querier = MaterialQuerier(self.db)
        material_data = querier.get_material_by_name(material_name, apply_overrides=False)
        
        if not material_data:
            print(f"✗ Material not found: {material_name}")
            return
        
        material_id = self._get_material_id(material_name)
        storage = self._get_override_storage()
        
        print(f"\nSetting override for: {material_name}")
        print(f"Property path: {property_path}")
        print(f"Override value: {override_value}")
        if unit:
            print(f"Unit: {unit}")
        if reason:
            print(f"Reason: {reason}")
        print("-" * 50)
        
        try:
            storage.save_value_override(material_id, property_path, override_value, unit, reason)
            print(f"\n✓ Override set successfully!")
        except Exception as e:
            print(f"\n✗ Failed to set override: {e}")
            import traceback
            traceback.print_exc()
    
    def list_overrides(self, material_name: str):
        """
        List all overrides for a material.
        
        Args:
            material_name: Name of material
        """
        querier = MaterialQuerier(self.db)
        material_data = querier.get_material_by_name(material_name, apply_overrides=False)
        
        if not material_data:
            print(f"✗ Material not found: {material_name}")
            return
        
        material_id = self._get_material_id(material_name)
        storage = self._get_override_storage()
        
        overrides = storage.list_overrides(material_id)
        
        if not overrides:
            print(f"\nNo overrides found for: {material_name}")
            return
        
        print(f"\n{'=' * 80}")
        print(f"OVERRIDES FOR: {material_name}")
        print(f"{'=' * 80}\n")
        
        for override in overrides:
            print(f"Property Path: {override['property_path']}")
            print(f"Type:          {override['override_type']}")
            
            if override['override_type'] == 'reference_preference':
                print(f"Preferred Ref: {override['override_data']['preferred_ref']}")
            elif override['override_type'] == 'value_override':
                print(f"Override Value: {override['override_data']['value']}")
                if override['override_data'].get('unit'):
                    print(f"Unit:           {override['override_data']['unit']}")
                if override['override_data'].get('reason'):
                    print(f"Reason:         {override['override_data']['reason']}")
            
            print(f"Created:       {override['created_at']}")
            print("-" * 80)
    
    def clear_overrides(self, material_name: str, property_path: str = None):
        """
        Clear overrides for a material.
        
        Args:
            material_name: Name of material
            property_path: Specific property path or None for all
        """
        querier = MaterialQuerier(self.db)
        material_data = querier.get_material_by_name(material_name, apply_overrides=False)
        
        if not material_data:
            print(f"✗ Material not found: {material_name}")
            return
        
        material_id = self._get_material_id(material_name)
        storage = self._get_override_storage()
        
        if property_path:
            print(f"\nClearing overrides for: {material_name} / {property_path}")
        else:
            print(f"\nClearing ALL overrides for: {material_name}")
        print("-" * 50)
        
        try:
            if property_path:
                storage.delete_override(material_id, property_path)
            else:
                storage.delete_all_overrides(material_id)
            print(f"\n✓ Overrides cleared successfully!")
        except Exception as e:
            print(f"\n✗ Failed to clear overrides: {e}")
            import traceback
            traceback.print_exc()
    
    def _get_material_id(self, material_name: str) -> int:
        """Get material ID from name."""
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT material_id FROM materials WHERE name = %s", (material_name,))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None
    
    # ====================================================================
    # REFERENCES COMMANDS
    # ====================================================================
    
    def import_references(self):
        """Import all references from References.xml."""
        from parser.references_parser import parse_references_xml
        from db.insert import insert_references
        
        xml_file = os.path.join(XML_DIR, 'References.xml')
        
        if not os.path.exists(xml_file):
            print(f"✗ References.xml not found at: {xml_file}")
            return
        
        print(f"\nImporting references from: {xml_file}")
        print("-" * 50)
        
        try:
            # Parse References.xml
            print("  Parsing References.xml...")
            references = parse_references_xml(xml_file)
            print(f"  ✓ Parsed {len(references)} references")
            
            # Insert into database
            print("  Inserting into database...")
            count = insert_references(self.db, references)
            
            print(f"\n✓ Successfully imported {count} references!")
            
        except Exception as e:
            print(f"\n✗ Import failed: {e}")
            import traceback
            traceback.print_exc()
    
    def query_reference(self, reference_id: str):
        """
        Query and display a specific reference.
        
        Args:
            reference_id: Reference ID to query
        """
        from db.query import ReferenceQuerier
        
        try:
            ref_id = int(reference_id)
        except ValueError:
            print(f"✗ Invalid reference ID: {reference_id}")
            return
        
        querier = ReferenceQuerier(self.db)
        ref = querier.get_reference_by_id(ref_id)
        
        if not ref:
            print(f"✗ Reference not found: {ref_id}")
            return
        
        print(f"\n{'='*70}")
        print(f"REFERENCE #{ref['reference_id']}")
        print(f"{'='*70}")
        print(f"Type:    {ref['ref_type']}")
        print(f"Author:  {ref['author']}")
        print(f"Title:   {ref['title']}")
        print(f"Journal: {ref['journal']}")
        print(f"Year:    {ref['year']}")
        print(f"Volume:  {ref['volume']}")
        print(f"Pages:   {ref['pages']}")
        print(f"{'='*70}\n")
        
        # Also show which materials use this reference
        materials = querier.get_materials_using_reference(ref_id)
        if materials:
            print(f"Used by {len(materials)} material(s):")
            for mat in materials:
                print(f"  • {mat}")
        else:
            print("Not currently used by any materials")
    
    def list_references(self):
        """List all references in the database."""
        from db.query import ReferenceQuerier
        
        querier = ReferenceQuerier(self.db)
        references = querier.list_all_references()
        
        if not references:
            print("No references found in database. Run 'python main.py import-references' first.")
            return
        
        print(f"\n{'='*100}")
        print(f"ALL REFERENCES ({len(references)} total)")
        print(f"{'='*100}")
        print(f"{'ID':<5} {'Type':<12} {'Author':<30} {'Year':<6} {'Title':<40}")
        print(f"{'-'*5} {'-'*12} {'-'*30} {'-'*6} {'-'*40}")
        
        for ref in references:
            author = (ref['author'] or '')[:30]
            title = (ref['title'] or '')[:40]
            ref_type = (ref['ref_type'] or '')[:12]
            year = (ref['year'] or '')[:6]
            
            print(f"{ref['reference_id']:<5} {ref_type:<12} {author:<30} {year:<6} {title:<40}")
        
        print(f"{'='*100}\n")
    
    def material_references(self, material_name: str):
        """
        Show all references used by a specific material.
        
        Args:
            material_name: Name of material
        """
        from db.query import ReferenceQuerier
        
        querier = ReferenceQuerier(self.db)
        ref_ids = querier.get_references_for_material(material_name)
        
        if not ref_ids:
            print(f"✗ No references found for material: {material_name}")
            print("  (Material may not exist or has no cited references)")
            return
        
        print(f"\n{'='*100}")
        print(f"REFERENCES FOR: {material_name}")
        print(f"{'='*100}")
        print(f"Found {len(ref_ids)} reference(s):")
        print()
        
        for ref_id in ref_ids:
            ref = querier.get_reference_by_id(ref_id)
            if ref:
                print(f"  [{ref_id}] {ref['ref_type']}: {ref['author']} ({ref['year']})")
                print(f"       {ref['title']}")
                print()
        
        print(f"{'='*100}\n")
    
    def close(self):
        """Close database connection."""
        self.db.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Material Database Engine - Solver-safe material data management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py init
  python main.py import xml/Copper.xml
  python main.py import-all
  python main.py list
  python main.py query Copper
  python main.py export Copper
  python main.py export-all
  python main.py set-preference Aluminum properties.Thermal.Density 112
  python main.py set-override Aluminum properties.Thermal.Density 2700
  python main.py list-overrides Aluminum
  python main.py clear-overrides Aluminum
  python main.py import-references
  python main.py list-references
  python main.py query-reference 112
  python main.py material-references Aluminum
        """
    )
    
    parser.add_argument('command', 
                       choices=['init', 'reset', 'import', 'import-all', 
                               'list', 'query', 'export', 'export-all',
                               'set-preference', 'set-override', 
                               'list-overrides', 'clear-overrides',
                               'import-references', 'query-reference',
                               'list-references', 'material-references'],
                       help='Command to execute')
    parser.add_argument('arguments', nargs='*', 
                       help='Additional arguments (material name, property path, value, etc.)')
    
    args = parser.parse_args()
    
    cli = MaterialDatabaseCLI()
    
    try:
        if args.command == 'init':
            cli.init_database()
        
        elif args.command == 'reset':
            cli.reset_database()
        
        elif args.command == 'import':
            if not args.arguments or len(args.arguments) < 1:
                print("✗ Please specify XML file path")
                sys.exit(1)
            cli.import_material(args.arguments[0])
        
        elif args.command == 'import-all':
            cli.import_all()
        
        elif args.command == 'list':
            cli.list_materials()
        
        elif args.command == 'query':
            if not args.arguments or len(args.arguments) < 1:
                print("✗ Please specify material name")
                sys.exit(1)
            cli.query_material(args.arguments[0])
        
        elif args.command == 'export':
            if not args.arguments or len(args.arguments) < 1:
                print("✗ Please specify material name")
                sys.exit(1)
            cli.export_material(args.arguments[0])
        
        elif args.command == 'export-all':
            cli.export_all()
        
        elif args.command == 'set-preference':
            if not args.arguments or len(args.arguments) < 3:
                print("✗ Usage: set-preference <material> <property_path> <preferred_ref>")
                sys.exit(1)
            cli.set_preference(args.arguments[0], args.arguments[1], args.arguments[2])
        
        elif args.command == 'set-override':
            if not args.arguments or len(args.arguments) < 3:
                print("✗ Usage: set-override <material> <property_path> <value> [unit] [reason]")
                sys.exit(1)
            material = args.arguments[0]
            path = args.arguments[1]
            value = args.arguments[2]
            unit = args.arguments[3] if len(args.arguments) > 3 else None
            reason = args.arguments[4] if len(args.arguments) > 4 else None
            cli.set_override(material, path, value, unit, reason)
        
        elif args.command == 'list-overrides':
            if not args.arguments or len(args.arguments) < 1:
                print("✗ Please specify material name")
                sys.exit(1)
            cli.list_overrides(args.arguments[0])
        
        elif args.command == 'clear-overrides':
            if not args.arguments or len(args.arguments) < 1:
                print("✗ Please specify material name")
                sys.exit(1)
            material = args.arguments[0]
            path = args.arguments[1] if len(args.arguments) > 1 else None
            cli.clear_overrides(material, path)
        
        # References commands
        elif args.command == 'import-references':
            cli.import_references()
        
        elif args.command == 'query-reference':
            if not args.arguments or len(args.arguments) < 1:
                print("✗ Please specify reference ID")
                sys.exit(1)
            cli.query_reference(args.arguments[0])
        
        elif args.command == 'list-references':
            cli.list_references()
        
        elif args.command == 'material-references':
            if not args.arguments or len(args.arguments) < 1:
                print("✗ Please specify material name")
                sys.exit(1)
            cli.material_references(args.arguments[0])
    
    finally:
        cli.close()


if __name__ == "__main__":
    main()
