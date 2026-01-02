"""
Database schema migration for 10-category structure.

This migration adds support for:
1. 10 standardized property categories
2. Optional subcategories
3. Category-based organization

IMPORTANT: This is a NON-DESTRUCTIVE migration.
Existing data will be preserved. New columns will be added.
"""

MIGRATION_SQL = """
-- ============================================================
-- STEP 1: Create new category master table
-- ============================================================
CREATE TABLE IF NOT EXISTS category_master (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    display_order INTEGER NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- STEP 2: Create subcategory master table
-- ============================================================
CREATE TABLE IF NOT EXISTS subcategory_master (
    subcategory_id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES category_master(category_id) ON DELETE CASCADE,
    subcategory_name VARCHAR(100) NOT NULL,
    is_optional BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(category_id, subcategory_name)
);

-- ============================================================
-- STEP 3: Insert the 10 standardized categories
-- ============================================================
INSERT INTO category_master (category_name, display_order, description) VALUES
('Structure_and_Formulation', 1, 'Chemical composition, formulation, and structural details'),
('Physical_Properties', 2, 'Physical state, appearance, density, phase transitions'),
('Chemical_Properties', 3, 'Thermochemical properties, reactivity, solubility'),
('Thermal_Properties', 4, 'Thermal conductivity, heat capacity, thermal stability'),
('Mechanical_Properties', 5, 'Mechanical strength, creep, stress-strain behavior'),
('Detonation_Properties', 6, 'Detonation velocity, pressure, energy (for explosives)'),
('Sensitivity', 7, 'Impact, friction, shock sensitivity (for explosives)'),
('Electrical_Properties', 8, 'Electrical conductivity, dielectric properties'),
('Toxicity', 9, 'Toxicological and safety information'),
('Additional_Properties', 10, 'Miscellaneous properties and data')
ON CONFLICT (category_name) DO NOTHING;

-- ============================================================
-- STEP 4: Add category foreign key to existing properties table
-- ============================================================
-- Add new column to link properties to standard categories
ALTER TABLE properties 
ADD COLUMN IF NOT EXISTS standard_category_id INTEGER REFERENCES category_master(category_id);

-- Add new column for subcategory name (optional/dynamic)
ALTER TABLE properties 
ADD COLUMN IF NOT EXISTS subcategory_name VARCHAR(100);

-- Add index for performance
CREATE INDEX IF NOT EXISTS idx_properties_standard_category ON properties(standard_category_id);
CREATE INDEX IF NOT EXISTS idx_properties_subcategory ON properties(subcategory_name);

-- ============================================================
-- STEP 5: Add category foreign key to property_categories table
-- ============================================================
ALTER TABLE property_categories 
ADD COLUMN IF NOT EXISTS standard_category_id INTEGER REFERENCES category_master(category_id);

CREATE INDEX IF NOT EXISTS idx_property_categories_standard_category ON property_categories(standard_category_id);

-- ============================================================
-- STEP 6: Create view for easy category querying
-- ============================================================
CREATE OR REPLACE VIEW v_properties_with_categories AS
SELECT 
    p.property_id,
    p.property_name,
    p.unit,
    pc.category_type AS old_category_type,
    cm.category_name AS standard_category,
    cm.display_order,
    p.subcategory_name,
    m.material_id,
    m.name AS material_name
FROM properties p
LEFT JOIN property_categories pc ON p.category_id = pc.category_id
LEFT JOIN category_master cm ON p.standard_category_id = cm.category_id
LEFT JOIN materials m ON pc.material_id = m.material_id
ORDER BY m.name, cm.display_order, p.subcategory_name, p.property_name;

-- ============================================================
-- STEP 7: Helper function to map old categories to new ones
-- ============================================================
CREATE OR REPLACE FUNCTION map_old_to_new_category(old_category_type VARCHAR)
RETURNS INTEGER AS $$
DECLARE
    new_category_id INTEGER;
BEGIN
    -- Map old category types to new standard categories
    CASE old_category_type
        WHEN 'Phase' THEN 
            SELECT category_id INTO new_category_id FROM category_master WHERE category_name = 'Physical_Properties';
        WHEN 'Thermal' THEN 
            SELECT category_id INTO new_category_id FROM category_master WHERE category_name = 'Thermal_Properties';
        WHEN 'Mechanical' THEN 
            SELECT category_id INTO new_category_id FROM category_master WHERE category_name = 'Mechanical_Properties';
        ELSE 
            SELECT category_id INTO new_category_id FROM category_master WHERE category_name = 'Additional_Properties';
    END CASE;
    
    RETURN new_category_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- STEP 8: Migrate existing data to use standard categories
-- ============================================================
-- Update property_categories with standard category mappings
UPDATE property_categories pc
SET standard_category_id = map_old_to_new_category(pc.category_type)
WHERE standard_category_id IS NULL;

-- Update properties with standard category mappings (via property_categories)
UPDATE properties p
SET standard_category_id = (
    SELECT pc.standard_category_id 
    FROM property_categories pc 
    WHERE pc.category_id = p.category_id
)
WHERE p.standard_category_id IS NULL;

-- ============================================================
-- STEP 9: Create helper views for each category
-- ============================================================
CREATE OR REPLACE VIEW v_structure_formulation AS
SELECT * FROM v_properties_with_categories 
WHERE standard_category = 'Structure_and_Formulation';

CREATE OR REPLACE VIEW v_physical_properties AS
SELECT * FROM v_properties_with_categories 
WHERE standard_category = 'Physical_Properties';

CREATE OR REPLACE VIEW v_chemical_properties AS
SELECT * FROM v_properties_with_categories 
WHERE standard_category = 'Chemical_Properties';

CREATE OR REPLACE VIEW v_thermal_properties AS
SELECT * FROM v_properties_with_categories 
WHERE standard_category = 'Thermal_Properties';

CREATE OR REPLACE VIEW v_mechanical_properties AS
SELECT * FROM v_properties_with_categories 
WHERE standard_category = 'Mechanical_Properties';

CREATE OR REPLACE VIEW v_detonation_properties AS
SELECT * FROM v_properties_with_categories 
WHERE standard_category = 'Detonation_Properties';

CREATE OR REPLACE VIEW v_sensitivity AS
SELECT * FROM v_properties_with_categories 
WHERE standard_category = 'Sensitivity';

CREATE OR REPLACE VIEW v_electrical_properties AS
SELECT * FROM v_properties_with_categories 
WHERE standard_category = 'Electrical_Properties';

CREATE OR REPLACE VIEW v_toxicity AS
SELECT * FROM v_properties_with_categories 
WHERE standard_category = 'Toxicity';

CREATE OR REPLACE VIEW v_additional_properties AS
SELECT * FROM v_properties_with_categories 
WHERE standard_category = 'Additional_Properties';

-- ============================================================
-- STEP 10: Create indexes for performance
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_category_master_display_order ON category_master(display_order);
CREATE INDEX IF NOT EXISTS idx_subcategory_master_category ON subcategory_master(category_id);
"""

ROLLBACK_SQL = """
-- Rollback migration (if needed)
DROP VIEW IF EXISTS v_additional_properties CASCADE;
DROP VIEW IF EXISTS v_toxicity CASCADE;
DROP VIEW IF EXISTS v_electrical_properties CASCADE;
DROP VIEW IF EXISTS v_sensitivity CASCADE;
DROP VIEW IF EXISTS v_detonation_properties CASCADE;
DROP VIEW IF EXISTS v_mechanical_properties CASCADE;
DROP VIEW IF EXISTS v_thermal_properties CASCADE;
DROP VIEW IF EXISTS v_chemical_properties CASCADE;
DROP VIEW IF EXISTS v_physical_properties CASCADE;
DROP VIEW IF EXISTS v_structure_formulation CASCADE;
DROP VIEW IF EXISTS v_properties_with_categories CASCADE;

DROP FUNCTION IF EXISTS map_old_to_new_category(VARCHAR) CASCADE;

ALTER TABLE properties DROP COLUMN IF EXISTS subcategory_name CASCADE;
ALTER TABLE properties DROP COLUMN IF EXISTS standard_category_id CASCADE;
ALTER TABLE property_categories DROP COLUMN IF EXISTS standard_category_id CASCADE;

DROP TABLE IF EXISTS subcategory_master CASCADE;
DROP TABLE IF EXISTS category_master CASCADE;
"""


def get_migration_sql():
    """Return SQL statements for the migration."""
    return MIGRATION_SQL


def get_rollback_sql():
    """Return SQL statements to rollback the migration."""
    return ROLLBACK_SQL
