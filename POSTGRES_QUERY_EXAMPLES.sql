-- ============================================================================
-- QUICK REFERENCE: POSTGRESQL QUERIES FOR SPECIFIC MATERIALS
-- Open: psql Materials_DB
-- Then copy-paste any query below (replace 'Aluminum' with your material)
-- ============================================================================

-- ============================================================================
-- BASIC QUERIES
-- ============================================================================

-- 1. Get material metadata
SELECT * FROM materials WHERE name = 'Aluminum';

-- 2. Get all property categories for a material
SELECT pc.category_type 
FROM property_categories pc 
JOIN materials m ON pc.material_id = m.material_id 
WHERE m.name = 'Aluminum';

-- 3. Get all properties with their categories
SELECT 
    pc.category_type,
    p.property_name,
    p.unit
FROM materials m
JOIN property_categories pc ON m.material_id = pc.material_id
JOIN properties p ON pc.category_id = p.category_id
WHERE m.name = 'Aluminum'
ORDER BY pc.category_type, p.property_name;

-- 4. Get ALL property values (COMPLETE)
SELECT 
    pc.category_type,
    p.property_name,
    pe.entry_index,
    pe.value,
    p.unit,
    pe.ref_id
FROM materials m
JOIN property_categories pc ON m.material_id = pc.material_id
JOIN properties p ON pc.category_id = p.category_id
JOIN property_entries pe ON p.property_id = pe.property_id
WHERE m.name = 'Aluminum'
ORDER BY pc.category_type, p.property_name, pe.entry_index;

-- ============================================================================
-- SPECIFIC PROPERTY QUERIES
-- ============================================================================

-- 5. Get only Density values
SELECT 
    p.property_name,
    pe.entry_index,
    pe.value,
    p.unit,
    pe.ref_id
FROM materials m
JOIN property_categories pc ON m.material_id = pc.material_id
JOIN properties p ON pc.category_id = p.category_id
JOIN property_entries pe ON p.property_id = pe.property_id
WHERE m.name = 'Aluminum' AND p.property_name = 'Density'
ORDER BY pe.entry_index;

-- 6. Get only Thermal properties
SELECT 
    p.property_name,
    pe.entry_index,
    pe.value,
    p.unit,
    pe.ref_id
FROM materials m
JOIN property_categories pc ON m.material_id = pc.material_id
JOIN properties p ON pc.category_id = p.category_id
JOIN property_entries pe ON p.property_id = pe.property_id
WHERE m.name = 'Aluminum' AND pc.category_type = 'Thermal'
ORDER BY p.property_name, pe.entry_index;

-- 7. Get only Mechanical properties
SELECT 
    p.property_name,
    pe.entry_index,
    pe.value,
    p.unit,
    pe.ref_id
FROM materials m
JOIN property_categories pc ON m.material_id = pc.material_id
JOIN properties p ON pc.category_id = p.category_id
JOIN property_entries pe ON p.property_id = pe.property_id
WHERE m.name = 'Aluminum' AND pc.category_type = 'Mechanical'
ORDER BY p.property_name, pe.entry_index;

-- ============================================================================
-- MODEL QUERIES
-- ============================================================================

-- 8. Get all models for a material
SELECT model_type FROM models mo
JOIN materials m ON mo.material_id = m.material_id
WHERE m.name = 'Aluminum';

-- 9. Get all sub-models for a material
SELECT 
    mo.model_type,
    sm.sub_model_type,
    sm.row_index
FROM materials m
JOIN models mo ON m.material_id = mo.material_id
JOIN sub_models sm ON mo.model_id = sm.model_id
WHERE m.name = 'Aluminum'
ORDER BY mo.model_type, sm.row_index, sm.sub_model_type;

-- 10. Get ALL model parameters (COMPLETE)
SELECT 
    mo.model_type,
    sm.sub_model_type,
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
ORDER BY mo.model_type, sm.sub_model_type, mp.param_name, mp.entry_index;

-- ============================================================================
-- SPECIFIC MODEL QUERIES
-- ============================================================================

-- 11. Get only ElasticModel parameters
SELECT 
    sm.sub_model_type,
    mp.param_name,
    mp.entry_index,
    mp.value,
    mp.unit,
    mp.ref_id
FROM materials m
JOIN models mo ON m.material_id = mo.material_id
JOIN sub_models sm ON mo.model_id = sm.model_id
JOIN model_parameters mp ON sm.sub_model_id = mp.sub_model_id
WHERE m.name = 'Aluminum' AND mo.model_type = 'ElasticModel'
ORDER BY sm.sub_model_type, mp.param_name, mp.entry_index;

-- 12. Get only ThermoMechanical parameters
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
  AND mo.model_type = 'ElasticModel' 
  AND sm.sub_model_type = 'ThermoMechanical'
ORDER BY mp.param_name, mp.entry_index;

-- 13. Get only ElastoPlastic model
SELECT 
    sm.sub_model_type,
    mp.param_name,
    mp.value,
    mp.unit,
    mp.ref_id
FROM materials m
JOIN models mo ON m.material_id = mo.material_id
JOIN sub_models sm ON mo.model_id = sm.model_id
JOIN model_parameters mp ON sm.sub_model_id = mp.sub_model_id
WHERE m.name = 'Aluminum' AND mo.model_type = 'ElastoPlastic'
ORDER BY sm.sub_model_type, mp.param_name;

-- 14. Get only ReactionModel
SELECT 
    sm.sub_model_type,
    mp.param_name,
    mp.entry_index,
    mp.value,
    mp.unit
FROM materials m
JOIN models mo ON m.material_id = mo.material_id
JOIN sub_models sm ON mo.model_id = sm.model_id
JOIN model_parameters mp ON sm.sub_model_id = mp.sub_model_id
WHERE m.name = 'Aluminum' AND mo.model_type = 'ReactionModel'
ORDER BY sm.sub_model_type, mp.param_name, mp.entry_index;

-- 15. Get only EOSModel
SELECT 
    sm.row_index,
    sm.parent_name,
    mp.param_name,
    mp.value,
    mp.unit
FROM materials m
JOIN models mo ON m.material_id = mo.material_id
JOIN sub_models sm ON mo.model_id = sm.model_id
JOIN model_parameters mp ON sm.sub_model_id = mp.sub_model_id
WHERE m.name = 'Aluminum' AND mo.model_type = 'EOSModel'
ORDER BY sm.row_index, sm.parent_name, mp.param_name;

-- ============================================================================
-- SPECIFIC PARAMETER QUERIES
-- ============================================================================

-- 16. Get specific parameter (e.g., Density from ThermoMechanical)
SELECT 
    mp.entry_index,
    mp.value,
    mp.unit,
    mp.ref_id
FROM materials m
JOIN models mo ON m.material_id = mo.material_id
JOIN sub_models sm ON mo.model_id = sm.model_id
JOIN model_parameters mp ON sm.sub_model_id = mp.sub_model_id
WHERE m.name = 'Aluminum' 
  AND mo.model_type = 'ElasticModel'
  AND sm.sub_model_type = 'ThermoMechanical'
  AND mp.param_name = 'Density'
ORDER BY mp.entry_index;

-- 17. Get MeltingTemperature values
SELECT 
    mp.entry_index,
    mp.value,
    mp.unit,
    mp.ref_id
FROM materials m
JOIN models mo ON m.material_id = mo.material_id
JOIN sub_models sm ON mo.model_id = sm.model_id
JOIN model_parameters mp ON sm.sub_model_id = mp.sub_model_id
WHERE m.name = 'Aluminum' 
  AND mp.param_name = 'MeltingTemperature'
ORDER BY mp.entry_index;

-- 18. Get IsothermalBulkModulus values
SELECT 
    mp.entry_index,
    mp.value,
    mp.unit,
    mp.ref_id
FROM materials m
JOIN models mo ON m.material_id = mo.material_id
JOIN sub_models sm ON mo.model_id = sm.model_id
JOIN model_parameters mp ON sm.sub_model_id = mp.sub_model_id
WHERE m.name = 'Aluminum' 
  AND mp.param_name = 'IsothermalBulkModulus'
ORDER BY mp.entry_index;

-- 19. Get ThermalConductivity values
SELECT 
    mp.entry_index,
    mp.value,
    mp.unit,
    mp.ref_id
FROM materials m
JOIN models mo ON m.material_id = mo.material_id
JOIN sub_models sm ON mo.model_id = sm.model_id
JOIN model_parameters mp ON sm.sub_model_id = mp.sub_model_id
WHERE m.name = 'Aluminum' 
  AND mp.param_name = 'ThermalConductivity'
ORDER BY mp.entry_index;

-- 20. Get ShearModulus values
SELECT 
    mp.entry_index,
    mp.value,
    mp.unit,
    mp.ref_id
FROM materials m
JOIN models mo ON m.material_id = mo.material_id
JOIN sub_models sm ON mo.model_id = sm.model_id
JOIN model_parameters mp ON sm.sub_model_id = mp.sub_model_id
WHERE m.name = 'Aluminum' 
  AND mp.param_name = 'ShearModulus'
ORDER BY mp.entry_index;

-- ============================================================================
-- SUMMARY & COUNT QUERIES
-- ============================================================================

-- 21. Count all records for a material
SELECT 
    'Properties' as type, COUNT(*) as count
FROM properties p
JOIN property_categories pc ON p.category_id = pc.category_id
JOIN materials m ON pc.material_id = m.material_id
WHERE m.name = 'Aluminum'
UNION ALL
SELECT 
    'Property Entries', COUNT(*)
FROM property_entries pe
JOIN properties p ON pe.property_id = p.property_id
JOIN property_categories pc ON p.category_id = pc.category_id
JOIN materials m ON pc.material_id = m.material_id
WHERE m.name = 'Aluminum'
UNION ALL
SELECT 
    'Models', COUNT(*)
FROM models mo
JOIN materials m ON mo.material_id = m.material_id
WHERE m.name = 'Aluminum'
UNION ALL
SELECT 
    'Sub Models', COUNT(*)
FROM sub_models sm
JOIN models mo ON sm.model_id = mo.model_id
JOIN materials m ON mo.material_id = m.material_id
WHERE m.name = 'Aluminum'
UNION ALL
SELECT 
    'Model Parameters', COUNT(*)
FROM model_parameters mp
JOIN sub_models sm ON mp.sub_model_id = sm.sub_model_id
JOIN models mo ON sm.model_id = mo.model_id
JOIN materials m ON mo.material_id = m.material_id
WHERE m.name = 'Aluminum';

-- 22. Summary by property category
SELECT 
    pc.category_type,
    COUNT(DISTINCT p.property_id) as num_properties,
    COUNT(pe.entry_id) as num_entries
FROM materials m
JOIN property_categories pc ON m.material_id = pc.material_id
JOIN properties p ON pc.category_id = p.category_id
LEFT JOIN property_entries pe ON p.property_id = pe.property_id
WHERE m.name = 'Aluminum'
GROUP BY pc.category_type
ORDER BY pc.category_type;

-- 23. Summary by model type
SELECT 
    mo.model_type,
    COUNT(DISTINCT sm.sub_model_id) as num_sub_models,
    COUNT(mp.param_id) as num_parameters
FROM materials m
JOIN models mo ON m.material_id = mo.material_id
LEFT JOIN sub_models sm ON mo.model_id = sm.model_id
LEFT JOIN model_parameters mp ON sm.sub_model_id = mp.sub_model_id
WHERE m.name = 'Aluminum'
GROUP BY mo.model_type
ORDER BY mo.model_type;

-- ============================================================================
-- COMPARISON QUERIES (Multiple Materials)
-- ============================================================================

-- 24. Compare Density across materials
SELECT 
    m.name,
    pe.entry_index,
    pe.value,
    p.unit,
    pe.ref_id
FROM materials m
JOIN property_categories pc ON m.material_id = pc.material_id
JOIN properties p ON pc.category_id = p.category_id
JOIN property_entries pe ON p.property_id = pe.property_id
WHERE p.property_name = 'Density'
  AND m.name IN ('Aluminum', 'Copper', 'Nickel')
ORDER BY m.name, pe.entry_index;

-- 25. Compare all properties of two materials
SELECT 
    m.name,
    pc.category_type,
    p.property_name,
    pe.value,
    p.unit
FROM materials m
JOIN property_categories pc ON m.material_id = pc.material_id
JOIN properties p ON pc.category_id = p.category_id
JOIN property_entries pe ON p.property_id = pe.property_id
WHERE m.name IN ('Aluminum', 'Copper')
ORDER BY m.name, pc.category_type, p.property_name;

-- ============================================================================
-- SEARCH QUERIES
-- ============================================================================

-- 26. Find all materials with a specific property value
SELECT DISTINCT m.name
FROM materials m
JOIN property_categories pc ON m.material_id = pc.material_id
JOIN properties p ON pc.category_id = p.category_id
JOIN property_entries pe ON p.property_id = pe.property_id
WHERE pe.value = 'solid';

-- 27. Find materials with Density > 8000
SELECT DISTINCT m.name, pe.value as density, p.unit
FROM materials m
JOIN property_categories pc ON m.material_id = pc.material_id
JOIN properties p ON pc.category_id = p.category_id
JOIN property_entries pe ON p.property_id = pe.property_id
WHERE p.property_name = 'Density'
  AND pe.value ~ '^[0-9]+(\.[0-9]+)?$'  -- Check if numeric
  AND CAST(pe.value AS FLOAT) > 8000
ORDER BY CAST(pe.value AS FLOAT) DESC;

-- 28. Find all materials with a specific model type
SELECT DISTINCT m.name
FROM materials m
JOIN models mo ON m.material_id = mo.material_id
WHERE mo.model_type = 'ReactionModel'
ORDER BY m.name;

-- ============================================================================
-- REFERENCE QUERIES
-- ============================================================================

-- 29. Get all reference IDs used by a material
SELECT DISTINCT pe.ref_id
FROM materials m
JOIN property_categories pc ON m.material_id = pc.material_id
JOIN properties p ON pc.category_id = p.category_id
JOIN property_entries pe ON p.property_id = pe.property_id
WHERE m.name = 'Aluminum' AND pe.ref_id IS NOT NULL
UNION
SELECT DISTINCT mp.ref_id
FROM materials m
JOIN models mo ON m.material_id = mo.material_id
JOIN sub_models sm ON mo.model_id = sm.model_id
JOIN model_parameters mp ON sm.sub_model_id = mp.sub_model_id
WHERE m.name = 'Aluminum' AND mp.ref_id IS NOT NULL
ORDER BY ref_id;

-- 30. Count references used
SELECT 
    'Property References' as type,
    COUNT(DISTINCT pe.ref_id) as count
FROM materials m
JOIN property_categories pc ON m.material_id = pc.material_id
JOIN properties p ON pc.category_id = p.category_id
JOIN property_entries pe ON p.property_id = pe.property_id
WHERE m.name = 'Aluminum' AND pe.ref_id IS NOT NULL
UNION ALL
SELECT 
    'Model Parameter References',
    COUNT(DISTINCT mp.ref_id)
FROM materials m
JOIN models mo ON m.material_id = mo.material_id
JOIN sub_models sm ON mo.model_id = sm.model_id
JOIN model_parameters mp ON sm.sub_model_id = mp.sub_model_id
WHERE m.name = 'Aluminum' AND mp.ref_id IS NOT NULL;
