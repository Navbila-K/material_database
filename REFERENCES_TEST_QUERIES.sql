-- ============================================================
-- REFERENCES TESTING SQL QUERIES
-- PostgreSQL test queries for the references system
-- Run these in psql or any PostgreSQL client
-- ============================================================

-- Connect to database first:
-- psql -U postgres -d Materials_DB

-- ============================================================
-- BASIC REFERENCE QUERIES
-- ============================================================

-- 1. Count total references
SELECT COUNT(*) as total_references FROM "references";

-- 2. View first 10 references
SELECT reference_id, ref_type, author, year, title 
FROM "references" 
ORDER BY reference_id 
LIMIT 10;

-- 3. Get specific reference by ID
SELECT * FROM "references" WHERE reference_id = 112;

-- 4. Check for any NULL or missing data
SELECT 
    COUNT(*) FILTER (WHERE author IS NULL) as null_authors,
    COUNT(*) FILTER (WHERE title IS NULL) as null_titles,
    COUNT(*) FILTER (WHERE year IS NULL) as null_years,
    COUNT(*) FILTER (WHERE ref_type IS NULL) as null_types
FROM "references";

-- ============================================================
-- REFERENCE TYPE STATISTICS
-- ============================================================

-- 5. Count references by type
SELECT ref_type, COUNT(*) as count 
FROM "references" 
GROUP BY ref_type 
ORDER BY count DESC;

-- 6. References by year (top 10 years)
SELECT year, COUNT(*) as count 
FROM "references" 
WHERE year != '--'
GROUP BY year 
ORDER BY count DESC, year DESC 
LIMIT 10;

-- 7. Find articles vs other types
SELECT 
    CASE WHEN ref_type = 'article' THEN 'article' ELSE 'other' END as category,
    COUNT(*) as count
FROM "references"
GROUP BY category;

-- ============================================================
-- MATERIAL-REFERENCE LINKAGE QUERIES
-- ============================================================

-- 8. Count how many materials use each reference (from property_entries)
SELECT 
    pe.ref_id::integer as reference_id,
    COUNT(DISTINCT m.material_id) as material_count,
    STRING_AGG(DISTINCT m.name, ', ' ORDER BY m.name) as materials
FROM property_entries pe
JOIN properties p ON pe.property_id = p.property_id
JOIN property_categories pc ON p.category_id = pc.category_id
JOIN materials m ON pc.material_id = m.material_id
WHERE pe.ref_id IS NOT NULL 
  AND pe.ref_id != ''
  AND pe.ref_id ~ '^[0-9]+$'
GROUP BY pe.ref_id::integer
ORDER BY material_count DESC, reference_id;

-- 9. Count references from model_parameters
SELECT 
    mp.ref_id::integer as reference_id,
    COUNT(DISTINCT m.material_id) as material_count,
    STRING_AGG(DISTINCT m.name, ', ' ORDER BY m.name) as materials
FROM model_parameters mp
JOIN sub_models sm ON mp.sub_model_id = sm.sub_model_id
JOIN models mo ON sm.model_id = mo.model_id
JOIN materials m ON mo.material_id = m.material_id
WHERE mp.ref_id IS NOT NULL 
  AND mp.ref_id != ''
  AND mp.ref_id ~ '^[0-9]+$'
GROUP BY mp.ref_id::integer
ORDER BY material_count DESC, reference_id;

-- 10. All references with material counts (COMBINED from both sources)
WITH prop_refs AS (
    SELECT 
        pe.ref_id::integer as ref_id,
        m.name as material_name
    FROM property_entries pe
    JOIN properties p ON pe.property_id = p.property_id
    JOIN property_categories pc ON p.category_id = pc.category_id
    JOIN materials m ON pc.material_id = m.material_id
    WHERE pe.ref_id ~ '^[0-9]+$'
),
model_refs AS (
    SELECT 
        mp.ref_id::integer as ref_id,
        m.name as material_name
    FROM model_parameters mp
    JOIN sub_models sm ON mp.sub_model_id = sm.sub_model_id
    JOIN models mo ON sm.model_id = mo.model_id
    JOIN materials m ON mo.material_id = m.material_id
    WHERE mp.ref_id ~ '^[0-9]+$'
),
all_refs AS (
    SELECT * FROM prop_refs
    UNION
    SELECT * FROM model_refs
)
SELECT 
    r.reference_id,
    r.ref_type,
    r.author,
    r.year,
    COALESCE(COUNT(DISTINCT ar.material_name), 0) as usage_count,
    STRING_AGG(DISTINCT ar.material_name, ', ' ORDER BY ar.material_name) as used_by_materials
FROM "references" r
LEFT JOIN all_refs ar ON r.reference_id = ar.ref_id
GROUP BY r.reference_id, r.ref_type, r.author, r.year
ORDER BY usage_count DESC, r.reference_id;

-- ============================================================
-- ORPHANED/UNUSED REFERENCES
-- ============================================================

-- 11. Find references that are NOT used by any material
WITH used_refs AS (
    SELECT DISTINCT pe.ref_id::integer as ref_id
    FROM property_entries pe
    WHERE pe.ref_id ~ '^[0-9]+$'
    UNION
    SELECT DISTINCT mp.ref_id::integer as ref_id
    FROM model_parameters mp
    WHERE mp.ref_id ~ '^[0-9]+$'
)
SELECT r.reference_id, r.ref_type, r.author, r.year, r.title
FROM "references" r
LEFT JOIN used_refs ur ON r.reference_id = ur.ref_id
WHERE ur.ref_id IS NULL
ORDER BY r.reference_id;

-- 12. Find references used by only ONE material
WITH prop_refs AS (
    SELECT pe.ref_id::integer as ref_id, m.name as material_name
    FROM property_entries pe
    JOIN properties p ON pe.property_id = p.property_id
    JOIN property_categories pc ON p.category_id = pc.category_id
    JOIN materials m ON pc.material_id = m.material_id
    WHERE pe.ref_id ~ '^[0-9]+$'
),
model_refs AS (
    SELECT mp.ref_id::integer as ref_id, m.name as material_name
    FROM model_parameters mp
    JOIN sub_models sm ON mp.sub_model_id = sm.sub_model_id
    JOIN models mo ON sm.model_id = mo.model_id
    JOIN materials m ON mo.material_id = m.material_id
    WHERE mp.ref_id ~ '^[0-9]+$'
),
all_refs AS (
    SELECT * FROM prop_refs UNION SELECT * FROM model_refs
)
SELECT 
    r.reference_id,
    r.author,
    r.year,
    r.title,
    COUNT(DISTINCT ar.material_name) as material_count,
    STRING_AGG(DISTINCT ar.material_name, ', ') as material
FROM "references" r
JOIN all_refs ar ON r.reference_id = ar.ref_id
GROUP BY r.reference_id, r.author, r.year, r.title
HAVING COUNT(DISTINCT ar.material_name) = 1
ORDER BY r.reference_id;

-- ============================================================
-- MATERIAL-SPECIFIC QUERIES
-- ============================================================

-- 13. Get all references for a specific material (e.g., Aluminum)
WITH prop_refs AS (
    SELECT DISTINCT pe.ref_id::integer as ref_id
    FROM property_entries pe
    JOIN properties p ON pe.property_id = p.property_id
    JOIN property_categories pc ON p.category_id = pc.category_id
    JOIN materials m ON pc.material_id = m.material_id
    WHERE m.name = 'Aluminum'
      AND pe.ref_id ~ '^[0-9]+$'
),
model_refs AS (
    SELECT DISTINCT mp.ref_id::integer as ref_id
    FROM model_parameters mp
    JOIN sub_models sm ON mp.sub_model_id = sm.sub_model_id
    JOIN models mo ON sm.model_id = mo.model_id
    JOIN materials m ON mo.material_id = m.material_id
    WHERE m.name = 'Aluminum'
      AND mp.ref_id ~ '^[0-9]+$'
),
all_material_refs AS (
    SELECT * FROM prop_refs UNION SELECT * FROM model_refs
)
SELECT r.*
FROM "references" r
JOIN all_material_refs amr ON r.reference_id = amr.ref_id
ORDER BY r.reference_id;

-- 14. Count references per material
WITH prop_refs AS (
    SELECT m.name, pe.ref_id::integer as ref_id
    FROM property_entries pe
    JOIN properties p ON pe.property_id = p.property_id
    JOIN property_categories pc ON p.category_id = pc.category_id
    JOIN materials m ON pc.material_id = m.material_id
    WHERE pe.ref_id ~ '^[0-9]+$'
),
model_refs AS (
    SELECT m.name, mp.ref_id::integer as ref_id
    FROM model_parameters mp
    JOIN sub_models sm ON mp.sub_model_id = sm.sub_model_id
    JOIN models mo ON sm.model_id = mo.model_id
    JOIN materials m ON mo.material_id = m.material_id
    WHERE mp.ref_id ~ '^[0-9]+$'
),
all_refs AS (
    SELECT * FROM prop_refs UNION SELECT * FROM model_refs
)
SELECT 
    name as material,
    COUNT(DISTINCT ref_id) as reference_count
FROM all_refs
GROUP BY name
ORDER BY reference_count DESC, name;

-- ============================================================
-- DATA VALIDATION QUERIES
-- ============================================================

-- 15. Check for invalid reference IDs in property_entries
SELECT DISTINCT pe.ref_id, m.name as material
FROM property_entries pe
JOIN properties p ON pe.property_id = p.property_id
JOIN property_categories pc ON p.category_id = pc.category_id
JOIN materials m ON pc.material_id = m.material_id
WHERE pe.ref_id ~ '^[0-9]+$'
  AND pe.ref_id::integer NOT IN (SELECT reference_id FROM "references")
ORDER BY pe.ref_id::integer;

-- 16. Check for invalid reference IDs in model_parameters
SELECT DISTINCT mp.ref_id, m.name as material
FROM model_parameters mp
JOIN sub_models sm ON mp.sub_model_id = sm.sub_model_id
JOIN models mo ON sm.model_id = mo.model_id
JOIN materials m ON mo.material_id = m.material_id
WHERE mp.ref_id ~ '^[0-9]+$'
  AND mp.ref_id::integer NOT IN (SELECT reference_id FROM "references")
ORDER BY mp.ref_id::integer;

-- 17. Find gaps in reference ID sequence
SELECT 
    reference_id + 1 as gap_start,
    (SELECT MIN(reference_id) - 1 FROM "references" r2 
     WHERE r2.reference_id > r1.reference_id) as gap_end
FROM "references" r1
WHERE NOT EXISTS (
    SELECT 1 FROM "references" r2 
    WHERE r2.reference_id = r1.reference_id + 1
)
AND reference_id < (SELECT MAX(reference_id) FROM "references")
ORDER BY gap_start;

-- ============================================================
-- MOST/LEAST CITED REFERENCES
-- ============================================================

-- 18. Top 10 most cited references
WITH prop_refs AS (
    SELECT pe.ref_id::integer as ref_id, m.name
    FROM property_entries pe
    JOIN properties p ON pe.property_id = p.property_id
    JOIN property_categories pc ON p.category_id = pc.category_id
    JOIN materials m ON pc.material_id = m.material_id
    WHERE pe.ref_id ~ '^[0-9]+$'
),
model_refs AS (
    SELECT mp.ref_id::integer as ref_id, m.name
    FROM model_parameters mp
    JOIN sub_models sm ON mp.sub_model_id = sm.sub_model_id
    JOIN models mo ON sm.model_id = mo.model_id
    JOIN materials m ON mo.material_id = m.material_id
    WHERE mp.ref_id ~ '^[0-9]+$'
),
all_refs AS (
    SELECT * FROM prop_refs UNION ALL SELECT * FROM model_refs
)
SELECT 
    r.reference_id,
    r.ref_type,
    r.author,
    r.year,
    r.title,
    COUNT(*) as citation_count,
    COUNT(DISTINCT ar.name) as unique_materials
FROM "references" r
JOIN all_refs ar ON r.reference_id = ar.ref_id
GROUP BY r.reference_id, r.ref_type, r.author, r.year, r.title
ORDER BY citation_count DESC, unique_materials DESC
LIMIT 10;

-- ============================================================
-- PUBLICATION YEAR ANALYSIS
-- ============================================================

-- 19. References by decade
SELECT 
    CASE 
        WHEN year = '--' THEN 'Unknown'
        WHEN year::integer < 1990 THEN 'Before 1990'
        WHEN year::integer BETWEEN 1990 AND 1999 THEN '1990s'
        WHEN year::integer BETWEEN 2000 AND 2009 THEN '2000s'
        WHEN year::integer BETWEEN 2010 AND 2019 THEN '2010s'
        WHEN year::integer >= 2020 THEN '2020s'
    END as decade,
    COUNT(*) as count
FROM "references"
GROUP BY decade
ORDER BY decade;

-- 20. Most recent references (last 5 years)
SELECT reference_id, ref_type, author, year, title
FROM "references"
WHERE year ~ '^[0-9]+$'
  AND year::integer >= 2020
ORDER BY year DESC, reference_id;

-- ============================================================
-- COMPREHENSIVE SUMMARY
-- ============================================================

-- 21. Complete statistics summary
SELECT 
    'Total References' as metric,
    COUNT(*)::text as value
FROM "references"
UNION ALL
SELECT 
    'Articles',
    COUNT(*)::text
FROM "references" WHERE ref_type = 'article'
UNION ALL
SELECT 
    'Conference Papers',
    COUNT(*)::text
FROM "references" WHERE ref_type = 'conference'
UNION ALL
SELECT 
    'Reports',
    COUNT(*)::text
FROM "references" WHERE ref_type = 'report'
UNION ALL
SELECT 
    'Misc',
    COUNT(*)::text
FROM "references" WHERE ref_type = 'misc'
UNION ALL
SELECT 
    'Chapters',
    COUNT(*)::text
FROM "references" WHERE ref_type = 'chapter'
UNION ALL
SELECT 
    'References with Known Year',
    COUNT(*)::text
FROM "references" WHERE year != '--'
UNION ALL
SELECT 
    'ID Range',
    MIN(reference_id)::text || ' to ' || MAX(reference_id)::text
FROM "references";

-- ============================================================
-- EXPORT QUERIES
-- ============================================================

-- 22. Export all references in citation format
SELECT 
    reference_id,
    '[' || reference_id || '] ' || 
    COALESCE(author, 'Unknown') || ' (' || 
    COALESCE(year, '--') || ') ' ||
    COALESCE(title, 'No title') || '. ' ||
    CASE 
        WHEN ref_type = 'article' THEN COALESCE(journal, 'Unknown journal')
        WHEN ref_type = 'conference' THEN COALESCE(journal, 'Unknown conference')
        WHEN ref_type = 'report' THEN COALESCE(journal, 'Unknown publisher')
        ELSE COALESCE(journal, '')
    END ||
    CASE 
        WHEN volume IS NOT NULL AND volume != '--' 
        THEN ', vol. ' || volume 
        ELSE '' 
    END ||
    CASE 
        WHEN pages IS NOT NULL AND pages != '--' 
        THEN ', pp. ' || pages 
        ELSE '' 
    END as citation
FROM "references"
ORDER BY reference_id;

-- 23. Export references with usage counts (for reporting)
WITH usage AS (
    SELECT pe.ref_id::integer as ref_id, COUNT(*) as uses
    FROM property_entries pe
    WHERE pe.ref_id ~ '^[0-9]+$'
    GROUP BY pe.ref_id::integer
    UNION ALL
    SELECT mp.ref_id::integer, COUNT(*)
    FROM model_parameters mp
    WHERE mp.ref_id ~ '^[0-9]+$'
    GROUP BY mp.ref_id::integer
)
SELECT 
    r.reference_id,
    r.ref_type,
    r.author,
    r.year,
    r.title,
    COALESCE(SUM(u.uses), 0) as total_uses
FROM "references" r
LEFT JOIN usage u ON r.reference_id = u.ref_id
GROUP BY r.reference_id, r.ref_type, r.author, r.year, r.title
ORDER BY total_uses DESC, r.reference_id;
