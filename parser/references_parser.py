"""
XML Parser for References.xml

Parses the References.xml file which contains bibliographic citations
used across all material data files.

Structure:
<References>
  <reference id="1">
    <type>article</type>
    <author>Najjar, F. M.</author>
    <title>Grain-Scale Simulations...</title>
    <journal>Shock Compression of Condensed Matter</journal>
    <year>2009</year>
    <volume>1195</volume>
    <pages>49--</pages>
  </reference>
  ...
</References>

Each reference can be cited by materials using ref="ID" attributes.
"""

import xml.etree.ElementTree as ET
from typing import List, Dict, Any


def parse_references_xml(xml_file: str) -> List[Dict[str, Any]]:
    """
    Parse References.xml and extract all reference data.
    
    CRITICAL: Parse EVERY field - no data should be omitted!
    
    Args:
        xml_file: Path to References.xml
    
    Returns:
        List of reference dictionaries with all fields
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    references = []
    
    for ref_elem in root.findall('reference'):
        # Get reference ID (required attribute)
        ref_id = ref_elem.get('id')
        if not ref_id:
            print(f"WARNING: Found reference without ID, skipping")
            continue
        
        try:
            reference_id = int(ref_id)
        except ValueError:
            print(f"WARNING: Reference ID '{ref_id}' is not a valid integer, skipping")
            continue
        
        # Extract all fields (use empty string as default, preserve "--" as-is)
        ref_type = ref_elem.findtext('type', '').strip()
        author = ref_elem.findtext('author', '').strip()
        title = ref_elem.findtext('title', '').strip()
        journal = ref_elem.findtext('journal', '').strip()
        year = ref_elem.findtext('year', '').strip()
        volume = ref_elem.findtext('volume', '').strip()
        pages = ref_elem.findtext('pages', '').strip()
        
        # Create reference dictionary
        reference = {
            'reference_id': reference_id,
            'ref_type': ref_type if ref_type else None,
            'author': author if author else None,
            'title': title if title else None,
            'journal': journal if journal else None,
            'year': year if year else None,
            'volume': volume if volume else None,
            'pages': pages if pages else None
        }
        
        references.append(reference)
    
    return references


def get_reference_stats(references: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate statistics about parsed references.
    
    Args:
        references: List of parsed references
    
    Returns:
        Dictionary with statistics
    """
    stats = {
        'total_count': len(references),
        'by_type': {},
        'missing_fields': {
            'author': 0,
            'title': 0,
            'journal': 0,
            'year': 0,
            'volume': 0,
            'pages': 0
        },
        'id_range': {
            'min': min(r['reference_id'] for r in references) if references else 0,
            'max': max(r['reference_id'] for r in references) if references else 0
        }
    }
    
    for ref in references:
        # Count by type
        ref_type = ref.get('ref_type', 'unknown')
        stats['by_type'][ref_type] = stats['by_type'].get(ref_type, 0) + 1
        
        # Count missing fields
        for field in ['author', 'title', 'journal', 'year', 'volume', 'pages']:
            if not ref.get(field):
                stats['missing_fields'][field] += 1
    
    return stats


def validate_references(references: List[Dict[str, Any]]) -> List[str]:
    """
    Validate parsed references for completeness and consistency.
    
    Args:
        references: List of parsed references
    
    Returns:
        List of validation warnings/errors
    """
    issues = []
    
    # Check for duplicate IDs
    ids = [r['reference_id'] for r in references]
    duplicates = [id for id in ids if ids.count(id) > 1]
    if duplicates:
        issues.append(f"Duplicate reference IDs found: {set(duplicates)}")
    
    # Check for gaps in ID sequence
    if references:
        min_id = min(ids)
        max_id = max(ids)
        expected_ids = set(range(min_id, max_id + 1))
        actual_ids = set(ids)
        missing_ids = expected_ids - actual_ids
        if missing_ids:
            issues.append(f"Gaps in reference ID sequence: {sorted(missing_ids)}")
    
    # Check for invalid types
    valid_types = {'article', 'book', 'report', 'conference', 'chapter', 'misc'}
    for ref in references:
        if ref['ref_type'] and ref['ref_type'] not in valid_types:
            issues.append(f"Invalid type '{ref['ref_type']}' for reference ID {ref['reference_id']}")
    
    # Check for completely empty references
    for ref in references:
        if not any([ref['author'], ref['title'], ref['journal']]):
            issues.append(f"Reference ID {ref['reference_id']} has no author, title, or journal")
    
    return issues


if __name__ == '__main__':
    # Test the parser
    import sys
    
    if len(sys.argv) > 1:
        xml_file = sys.argv[1]
    else:
        xml_file = 'xml/References.xml'
    
    print(f"Parsing {xml_file}...")
    references = parse_references_xml(xml_file)
    
    print(f"\n✓ Parsed {len(references)} references")
    
    # Show statistics
    stats = get_reference_stats(references)
    print(f"\nStatistics:")
    print(f"  Total references: {stats['total_count']}")
    print(f"  ID range: {stats['id_range']['min']} - {stats['id_range']['max']}")
    print(f"\n  By type:")
    for ref_type, count in sorted(stats['by_type'].items()):
        print(f"    {ref_type}: {count}")
    
    print(f"\n  Missing fields:")
    for field, count in stats['missing_fields'].items():
        if count > 0:
            print(f"    {field}: {count} references")
    
    # Validate
    issues = validate_references(references)
    if issues:
        print(f"\n⚠ Validation issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print(f"\n✓ No validation issues found")
    
    # Show first 3 references as examples
    print(f"\nFirst 3 references:")
    for ref in references[:3]:
        print(f"\n  [{ref['reference_id']}] {ref['ref_type']}")
        print(f"    Author: {ref['author']}")
        print(f"    Title: {ref['title']}")
        print(f"    Journal: {ref['journal']}")
        print(f"    Year: {ref['year']}")
