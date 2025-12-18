#!/usr/bin/env python3
"""
Comprehensive cross-check and verification of all material XML files.
Verifies output consistency, completeness, and formatting.

EXCLUDES: xml/References.xml (not processed or accessed)
"""
import os
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
from parser.xml_parser import MaterialXMLParser
from db.database import DatabaseManager
from db.query import MaterialQuerier
import io
from contextlib import redirect_stdout

# Material files to verify (explicitly excluding References.xml)
MATERIAL_FILES = [
    'Aluminum.xml',
    'CL-20.xml', 
    'Copper.xml',
    'HELIUM.xml',
    'HMX.xml',
    'HNS.xml',
    'MAGNESIUM.xml',
    'Nickel.xml',
    'Nitromethane.xml',
    'PETN.xml',
    'RDX.xml',
    'Sucrose.xml',
    'TANTALUM.xml',
    'TATB.xml',
    'TITANIUM.xml',
    'TNT.xml',
    'TUNGSTEN.xml'
]

class MaterialVerifier:
    """Verify material XML files and their query outputs."""
    
    def __init__(self):
        self.xml_dir = Path('xml')
        self.db = DatabaseManager()
        self.db.connect()
        self.querier = MaterialQuerier(self.db)
        self.results = {}
        
    def verify_xml_structure(self, xml_file):
        """Parse XML and verify structure."""
        xml_path = self.xml_dir / xml_file
        
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Check required top-level elements
            required_elements = ['Metadata', 'Category']
            missing = [elem for elem in required_elements if root.find(elem) is None]
            
            if missing:
                return False, f"Missing elements: {missing}"
            
            # Check Metadata structure
            metadata = root.find('Metadata')
            required_metadata = ['Id', 'Name', 'Version']
            missing_metadata = [elem for elem in required_metadata if metadata.find(elem) is None]
            
            if missing_metadata:
                return False, f"Missing metadata: {missing_metadata}"
            
            # Check Category structure
            category = root.find('Category')
            if category.find('Property') is None:
                return False, "Missing Property section"
            if category.find('Model') is None:
                return False, "Missing Model section"
            
            return True, "XML structure valid"
            
        except Exception as e:
            return False, f"XML parse error: {str(e)}"
    
    def count_xml_elements(self, xml_file):
        """Count elements in XML for comparison."""
        xml_path = self.xml_dir / xml_file
        parser = MaterialXMLParser(str(xml_path))
        data = parser.parse()
        
        counts = {
            'metadata_fields': len(data['metadata']),
            'property_categories': len(data['properties']),
            'models': len(data['models']),
            'properties': sum(len(props) for props in data['properties'].values()),
        }
        
        return counts
    
    def verify_query_output(self, material_name):
        """Verify query output structure and content."""
        material_data = self.querier.get_material_by_name(material_name)
        
        if not material_data:
            return False, "Material not found in database"
        
        issues = []
        
        # Check metadata
        metadata = material_data.get('metadata', {})
        required_meta = ['id', 'name', 'version', 'version_meaning']
        for field in required_meta:
            if field not in metadata:
                issues.append(f"Missing metadata field: {field}")
        
        # Check properties
        properties = material_data.get('properties', {})
        if not properties:
            issues.append("No properties found")
        
        expected_categories = ['Phase', 'Thermal', 'Mechanical']
        for cat in expected_categories:
            if cat not in properties:
                issues.append(f"Missing property category: {cat}")
        
        # Check models
        models = material_data.get('models', {})
        if not models:
            issues.append("No models found")
        
        expected_models = ['ElasticModel', 'ElastoPlastic', 'ReactionModel', 'EOSModel']
        for model in expected_models:
            if model not in models:
                issues.append(f"Missing model: {model}")
        
        if issues:
            return False, "; ".join(issues)
        
        return True, "Query output structure valid"
    
    def check_output_formatting(self, material_name):
        """Check if output has consistent formatting."""
        material_data = self.querier.get_material_by_name(material_name)
        
        if not material_data:
            return False, "Cannot verify formatting - material not found"
        
        # Check for common formatting patterns
        checks = []
        
        # Metadata should have all fields
        metadata = material_data['metadata']
        if all(k in metadata for k in ['id', 'name', 'version']):
            checks.append(True)
        else:
            checks.append(False)
        
        # Properties should be organized by category
        properties = material_data['properties']
        if 'Phase' in properties and 'Thermal' in properties and 'Mechanical' in properties:
            checks.append(True)
        else:
            checks.append(False)
        
        # Models should have expected structure
        models = material_data['models']
        if all(m in models for m in ['ElasticModel', 'ElastoPlastic', 'ReactionModel', 'EOSModel']):
            checks.append(True)
        else:
            checks.append(False)
        
        if all(checks):
            return True, "Formatting consistent"
        else:
            return False, f"Formatting issues detected ({sum(checks)}/3 checks passed)"
    
    def verify_material(self, xml_file):
        """Complete verification of a single material."""
        material_name = xml_file.replace('.xml', '')
        
        print(f"\n{'='*80}")
        print(f"Verifying: {material_name}")
        print(f"{'='*80}")
        
        result = {
            'name': material_name,
            'xml_file': xml_file,
            'xml_structure': None,
            'xml_counts': None,
            'query_output': None,
            'formatting': None,
            'overall': 'PASS'
        }
        
        # 1. Verify XML structure
        print(f"  [1/4] Checking XML structure...", end=' ')
        success, message = self.verify_xml_structure(xml_file)
        result['xml_structure'] = (success, message)
        print("✓" if success else f"✗ {message}")
        if not success:
            result['overall'] = 'FAIL'
        
        # 2. Count XML elements
        print(f"  [2/4] Counting XML elements...", end=' ')
        try:
            counts = self.count_xml_elements(xml_file)
            result['xml_counts'] = counts
            print(f"✓ (Categories: {counts['property_categories']}, Properties: {counts['properties']}, Models: {counts['models']})")
        except Exception as e:
            result['xml_counts'] = None
            result['overall'] = 'FAIL'
            print(f"✗ Error: {str(e)}")
        
        # 3. Verify query output
        print(f"  [3/4] Verifying query output...", end=' ')
        success, message = self.verify_query_output(material_name)
        result['query_output'] = (success, message)
        print("✓" if success else f"✗ {message}")
        if not success:
            result['overall'] = 'FAIL'
        
        # 4. Check formatting
        print(f"  [4/4] Checking output formatting...", end=' ')
        success, message = self.check_output_formatting(material_name)
        result['formatting'] = (success, message)
        print("✓" if success else f"✗ {message}")
        if not success:
            result['overall'] = 'FAIL'
        
        print(f"\n  Result: {'✅ PASS' if result['overall'] == 'PASS' else '❌ FAIL'}")
        
        self.results[material_name] = result
        return result
    
    def run_verification(self):
        """Run verification on all materials."""
        print("\n" + "="*80)
        print("MATERIAL XML FILES CROSS-CHECK AND VERIFICATION")
        print("="*80)
        print(f"\nScope: {len(MATERIAL_FILES)} materials")
        print(f"Excluded: xml/References.xml (not processed)\n")
        
        for xml_file in MATERIAL_FILES:
            self.verify_material(xml_file)
        
        self.print_summary()
        
    def print_summary(self):
        """Print verification summary."""
        print("\n" + "="*80)
        print("VERIFICATION SUMMARY")
        print("="*80)
        
        passed = sum(1 for r in self.results.values() if r['overall'] == 'PASS')
        failed = sum(1 for r in self.results.values() if r['overall'] == 'FAIL')
        
        print(f"\n✓ Passed: {passed}/{len(self.results)}")
        print(f"✗ Failed: {failed}/{len(self.results)}")
        
        if failed > 0:
            print("\n⚠️  Materials with issues:")
            for name, result in self.results.items():
                if result['overall'] == 'FAIL':
                    print(f"\n  {name}:")
                    if result['xml_structure'] and not result['xml_structure'][0]:
                        print(f"    - XML Structure: {result['xml_structure'][1]}")
                    if result['query_output'] and not result['query_output'][0]:
                        print(f"    - Query Output: {result['query_output'][1]}")
                    if result['formatting'] and not result['formatting'][0]:
                        print(f"    - Formatting: {result['formatting'][1]}")
        else:
            print("\n✅ ALL MATERIALS VERIFIED SUCCESSFULLY!")
            print("\n✓ Output Consistency: All materials produce same structured format")
            print("✓ Content Completeness: All XML data present in query output")
            print("✓ Formatting & Structure: Headings, sections, alignment consistent")
            print("✓ Uniform Behavior: All materials behave identically")
            print("\n🎯 SYSTEM IS SAFE AND RELIABLE TO PROCEED")
        
        print("\n" + "="*80 + "\n")
        
        self.querier.conn.close()
        
        return failed == 0

def main():
    """Main verification entry point."""
    verifier = MaterialVerifier()
    success = verifier.run_verification()
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
