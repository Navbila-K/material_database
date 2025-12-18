-- ============================================================================
-- DATABASE VERIFICATION QUERIES FOR SPECIFIC MATERIAL
-- Run these in psql or use: psql Materials_DB -c "QUERY"
-- ============================================================================

-- Replace 'Aluminum' with your material name throughout

-- ============================================================================
-- 1. MATERIALS TABLE - Main material information
-- ============================================================================

-- Get material metadata
SELECT 
    material_id,
    xml_id,
    name,
    author,
    date,
    version,
    version_meaning,
    created_at
FROM materials
WHERE name = 'Aluminum';

-- ============================================================================
-- 2. PROPERTY CATEGORIES - Property groups for the material
-- ============================================================================

-- Get all property categories
SELECT 
    pc.category_id,
    pc.category_type,
    m.name as material_name
FROM property_categories pc
JOIN materials m ON pc.material_id = m.material_id
WHERE m.name = 'Aluminum'
ORDER BY pc.category_type;

-- ============================================================================
-- 3. PROPERTIES - Individual properties in each category
-- ============================================================================

-- Get all properties with their categories
SELECT 
    m.name as material_name,
    pc.category_type,
    p.property_id,
    p.property_name,
    p.unit,
    COUNT(pe.entry_id) as num_entries
FROM materials m
JOIN property_categories pc ON m.material_id = pc.material_id
JOIN properties p ON pc.category_id = p.category_id
LEFT JOIN property_entries pe ON p.property_id = pe.property_id
WHERE m.name = 'Aluminum'
GROUP BY m.name, pc.category_type, p.property_id, p.property_name, p.unit
ORDER BY pc.category_type, p.property_name;

-- ============================================================================
-- 4. PROPERTY ENTRIES - Actual data values
-- ============================================================================

-- Get ALL property entries with full details
SELECT 
    m.name as material_name,
    pc.category_type,
    p.property_name,
    p.unit,
    pe.entry_index,
    pe.value,
    pe.ref_id
FROM materials m
JOIN property_categories pc ON m.material_id = pc.material_id
JOIN properties p ON pc.category_id = p.category_id
JOIN property_entries pe ON p.property_id = pe.property_id
WHERE m.name = 'Aluminum'
ORDER BY pc.category_type, p.property_name, pe.entry_index;

-- Get specific property (e.g., Density)
SELECT 
    p.property_name,
    p.unit,
    pe.entry_index,
    pe.value,
    pe.ref_id
FROM materials m
JOIN property_categories pc ON m.material_id = pc.material_id
JOIN properties p ON pc.category_id = p.category_id
JOIN property_entries pe ON p.property_id = pe.property_id
WHERE m.name = 'Aluminum' 
  AND p.property_name = 'Density'
ORDER BY pe.entry_index;

-- ============================================================================
-- 5. MODELS - Model types for the material
-- ============================================================================

-- Get all models
SELECT 
    mo.model_id,
    mo.model_type,
    m.name as material_name,
    COUNT(DISTINCT sm.sub_model_id) as num_sub_models
FROM materials m
JOIN models mo ON m.material_id = mo.material_id
LEFT JOIN sub_models sm ON mo.model_id = sm.model_id
WHERE m.name = 'Aluminum'
GROUP BY mo.model_id, mo.model_type, m.name
ORDER BY mo.model_type;

-- ============================================================================
-- 6. SUB_MODELS - Nested model structures
-- ============================================================================

-- Get all sub-models with hierarchy
SELECT 
    m.name as material_name,
    mo.model_type,
    sm.sub_model_id,
    sm.sub_model_type,
    sm.row_index,
    sm.parent_name,
    COUNT(mp.param_id) as num_parameters
FROM materials m
JOIN models mo ON m.material_id = mo.material_id
JOIN sub_models sm ON mo.model_id = sm.model_id
LEFT JOIN model_parameters mp ON sm.sub_model_id = mp.sub_model_id
WHERE m.name = 'Aluminum'
GROUP BY m.name, mo.model_type, sm.sub_model_id, sm.sub_model_type, sm.row_index, sm.parent_name
ORDER BY mo.model_type, sm.row_index, sm.sub_model_type;

-- Get specific model's sub-models (e.g., ElasticModel)
SELECT 
    sm.sub_model_type,
    sm.row_index,
    sm.parent_name,
    COUNT(mp.param_id) as num_parameters
FROM materials m
JOIN models mo ON m.material_id = mo.material_id
JOIN sub_models sm ON mo.model_id = sm.model_id
LEFT JOIN model_parameters mp ON sm.sub_model_id = mp.sub_model_id
WHERE m.name = 'Aluminum' 
  AND mo.model_type = 'ElasticModel'
GROUP BY sm.sub_model_type, sm.row_index, sm.parent_name;

-- ============================================================================
-- 7. MODEL_PARAMETERS - Parameter values in models
-- ============================================================================

-- Get ALL model parameters with full details
SELECT 
    m.name as material_name,
    mo.model_type,
    sm.sub_model_type,
    sm.row_index,
    mp.param_name,
    mp.value,
    mp.unit,
    mp.ref_id,
    mp.entry_index
FROM materials m
JOIN models mo ON m.material_id = mo.material_id
JOIN sub_models sm ON mo.model_id = sm.model_id
JOIN model_parameters mp ON sm.sub_model_id = mp.sub_model_id
WHERE m.name = 'Aluminum'
ORDER BY mo.model_type, sm.sub_model_type, sm.row_index, mp.param_name, mp.entry_index;

-- Get ThermoMechanical parameters only
SELECT 
    mp.param_name,
    mp.value,
    mp.unit,
    mp.ref_id,
    mp.entry_index
FROM materials m
JOIN models mo ON m.material_id = mo.material_id
JOIN sub_models sm ON mo.model_id = sm.model_id
JOIN model_parameters mp ON sm.sub_model_id = mp.sub_model_id
WHERE m.name = 'Aluminum'
  AND mo.model_type = 'ElasticModel'
  AND sm.sub_model_type = 'ThermoMechanical'
ORDER BY mp.param_name, mp.entry_index;

-- Get parameters with multiple entries (like Density)
SELECT 
    mp.param_name,
    mp.entry_index,
    mp.value,
    mp.unit,
    mp.ref_id
FROM materials m
JOIN models mo ON m.material_id = mo.material_id
JOIN sub_models sm ON mo.model_id = sm.model_id
JOIN model_parameters mp ON sm.sub_model_id = mp.sub_model_id
WHERE m.name = 'Aluminum'
  AND mp.param_name = 'Density'
ORDER BY mp.entry_index;

-- Count parameters by model type
SELECT 
    mo.model_type,
    sm.sub_model_type,
    COUNT(mp.param_id) as parameter_count
FROM materials m
JOIN models mo ON m.material_id = mo.material_id
JOIN sub_models sm ON mo.model_id = sm.model_id
LEFT JOIN model_parameters mp ON sm.sub_model_id = mp.sub_model_id
WHERE m.name = 'Aluminum'
GROUP BY mo.model_type, sm.sub_model_type
ORDER BY mo.model_type, sm.sub_model_type;

-- ============================================================================
-- 8. MATERIAL_REFERENCES - Bibliographic references (if used)
-- ============================================================================

-- Get all unique references used by this material
SELECT DISTINCT mr.*
FROM material_references mr
WHERE mr.ref_id IN (
    -- From property entries
    SELECT DISTINCT pe.ref_id
    FROM materials m
    JOIN property_categories pc ON m.material_id = pc.material_id
    JOIN properties p ON pc.category_id = p.category_id
    JOIN property_entries pe ON p.property_id = pe.property_id
    WHERE m.name = 'Aluminum' AND pe.ref_id IS NOT NULL
    
    UNION
    
    -- From model parameters
    SELECT DISTINCT mp.ref_id
    FROM materials m
    JOIN models mo ON m.material_id = mo.material_id
    JOIN sub_models sm ON mo.model_id = sm.model_id
    JOIN model_parameters mp ON sm.sub_model_id = mp.sub_model_id
    WHERE m.name = 'Aluminum' AND mp.ref_id IS NOT NULL
)
ORDER BY mr.ref_id;

-- ============================================================================
-- COMPREHENSIVE SUMMARY QUERIES
-- ============================================================================

-- Complete material summary
SELECT 
    'Material Info' as section,
    m.name,
    m.xml_id,
    m.version,
    (SELECT COUNT(*) FROM property_categories WHERE material_id = m.material_id) as property_categories_count,
    (SELECT COUNT(*) FROM properties p 
     JOIN property_categories pc ON p.category_id = pc.category_id 
     WHERE pc.material_id = m.material_id) as properties_count,
    (SELECT COUNT(*) FROM property_entries pe
     JOIN properties p ON pe.property_id = p.property_id
     JOIN property_categories pc ON p.category_id = pc.category_id
     WHERE pc.material_id = m.material_id) as property_entries_count,
    (SELECT COUNT(*) FROM models WHERE material_id = m.material_id) as models_count,
    (SELECT COUNT(*) FROM sub_models sm
     JOIN models mo ON sm.model_id = mo.model_id
     WHERE mo.material_id = m.material_id) as sub_models_count,
    (SELECT COUNT(*) FROM model_parameters mp
     JOIN sub_models sm ON mp.sub_model_id = sm.sub_model_id
     JOIN models mo ON sm.model_id = mo.model_id
     WHERE mo.material_id = m.material_id) as model_parameters_count
FROM materials m
WHERE m.name = 'Aluminum';

-- ============================================================================
-- VERIFICATION: Check for missing or empty data
-- ============================================================================

-- Check for properties with no entries
SELECT 
    m.name as material_name,
    pc.category_type,
    p.property_name,
    COUNT(pe.entry_id) as entry_count
FROM materials m
JOIN property_categories pc ON m.material_id = pc.material_id
JOIN properties p ON pc.category_id = p.category_id
LEFT JOIN property_entries pe ON p.property_id = pe.property_id
WHERE m.name = 'Aluminum'
GROUP BY m.name, pc.category_type, p.property_name
HAVING COUNT(pe.entry_id) = 0;

-- Check for models with no parameters
SELECT 
    m.name as material_name,
    mo.model_type,
    sm.sub_model_type,
    COUNT(mp.param_id) as parameter_count
FROM materials m
JOIN models mo ON m.material_id = mo.material_id
JOIN sub_models sm ON mo.model_id = sm.model_id
LEFT JOIN model_parameters mp ON sm.sub_model_id = mp.sub_model_id
WHERE m.name = 'Aluminum'
GROUP BY m.name, mo.model_type, sm.sub_model_type
HAVING COUNT(mp.param_id) = 0;

-- Check for NULL values in critical fields
SELECT 
    'Property Entries with NULL values' as check_type,
    COUNT(*) as count
FROM materials m
JOIN property_categories pc ON m.material_id = pc.material_id
JOIN properties p ON pc.category_id = p.category_id
JOIN property_entries pe ON p.property_id = pe.property_id
WHERE m.name = 'Aluminum' AND pe.value IS NULL

UNION ALL

SELECT 
    'Model Parameters with NULL values',
    COUNT(*)
FROM materials m
JOIN models mo ON m.material_id = mo.material_id
JOIN sub_models sm ON mo.model_id = sm.model_id
JOIN model_parameters mp ON sm.sub_model_id = mp.sub_model_id
WHERE m.name = 'Aluminum' AND mp.value IS NULL;

-- ============================================================================
-- QUICK ONE-LINER QUERIES
-- ============================================================================

-- Just show everything (condensed)
SELECT 'Materials' as table_name, COUNT(*) as count FROM materials WHERE name = 'Aluminum'
UNION ALL
SELECT 'Property Categories', COUNT(*) FROM property_categories pc JOIN materials m ON pc.material_id = m.material_id WHERE m.name = 'Aluminum'
UNION ALL
SELECT 'Properties', COUNT(*) FROM properties p JOIN property_categories pc ON p.category_id = pc.category_id JOIN materials m ON pc.material_id = m.material_id WHERE m.name = 'Aluminum'
UNION ALL
SELECT 'Property Entries', COUNT(*) FROM property_entries pe JOIN properties p ON pe.property_id = p.property_id JOIN property_categories pc ON p.category_id = pc.category_id JOIN materials m ON pc.material_id = m.material_id WHERE m.name = 'Aluminum'
UNION ALL
SELECT 'Models', COUNT(*) FROM models mo JOIN materials m ON mo.material_id = m.material_id WHERE m.name = 'Aluminum'
UNION ALL
SELECT 'Sub Models', COUNT(*) FROM sub_models sm JOIN models mo ON sm.model_id = mo.model_id JOIN materials m ON mo.material_id = m.material_id WHERE m.name = 'Aluminum'
UNION ALL
SELECT 'Model Parameters', COUNT(*) FROM model_parameters mp JOIN sub_models sm ON mp.sub_model_id = sm.sub_model_id JOIN models mo ON sm.model_id = mo.model_id JOIN materials m ON mo.material_id = m.material_id WHERE m.name = 'Aluminum';
