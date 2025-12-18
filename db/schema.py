"""
Database schema that mirrors the XML structure exactly.
Schema is designed to be material-agnostic and preserve all XML hierarchy.
"""

# SQL schema creation statements

SCHEMA_SQL = """
-- ============================================================
-- REFERENCES TABLE
-- Stores bibliographic references used across all materials
-- ============================================================
CREATE TABLE IF NOT EXISTS material_references (
    ref_id VARCHAR(50) PRIMARY KEY,
    ref_type VARCHAR(50),
    author TEXT,
    title TEXT,
    journal TEXT,
    year INTEGER,
    volume VARCHAR(50),
    pages VARCHAR(50),
    doi VARCHAR(255),
    notes TEXT
);

-- ============================================================
-- MATERIALS TABLE
-- One row per material (one XML file = one material)
-- ============================================================
CREATE TABLE IF NOT EXISTS materials (
    material_id SERIAL PRIMARY KEY,
    xml_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    author VARCHAR(255),
    date VARCHAR(50),
    version VARCHAR(100),
    version_meaning VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- PROPERTY CATEGORIES
-- Tracks Property/Phase, Property/Thermal, Property/Mechanical
-- ============================================================
CREATE TABLE IF NOT EXISTS property_categories (
    category_id SERIAL PRIMARY KEY,
    material_id INTEGER REFERENCES materials(material_id) ON DELETE CASCADE,
    category_type VARCHAR(50) NOT NULL,  -- 'Phase', 'Thermal', 'Mechanical'
    UNIQUE(material_id, category_type)
);

-- ============================================================
-- PROPERTIES
-- Individual properties within categories (Density, Cp, Cv, etc.)
-- ============================================================
CREATE TABLE IF NOT EXISTS properties (
    property_id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES property_categories(category_id) ON DELETE CASCADE,
    property_name VARCHAR(100) NOT NULL,  -- 'Density', 'Cp', 'Viscosity', etc.
    unit VARCHAR(50),  -- 'kg/m^3', 'J/kg/K', etc.
    UNIQUE(category_id, property_name)
);

-- ============================================================
-- PROPERTY ENTRIES
-- Actual data entries within properties
-- Values stored as TEXT to preserve scientific notation
-- ============================================================
CREATE TABLE IF NOT EXISTS property_entries (
    entry_id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES properties(property_id) ON DELETE CASCADE,
    value TEXT,  -- Store as TEXT to preserve '13E9', '0.385', etc.
    ref_id VARCHAR(50),  -- Reference ID (not enforced as foreign key for flexibility)
    entry_index INTEGER  -- For ordered entries
);

-- ============================================================
-- MODELS
-- Top-level model categories: ElasticModel, ElastoPlastic, ReactionModel, EOSModel
-- ============================================================
CREATE TABLE IF NOT EXISTS models (
    model_id SERIAL PRIMARY KEY,
    material_id INTEGER REFERENCES materials(material_id) ON DELETE CASCADE,
    model_type VARCHAR(100) NOT NULL,  -- 'ElasticModel', 'ElastoPlastic', 'ReactionModel', 'EOSModel'
    UNIQUE(material_id, model_type)
);

-- ============================================================
-- SUB_MODELS
-- Nested model structures (e.g., ThermoMechanical under ElasticModel)
-- Also includes EOS Row structures
-- ============================================================
CREATE TABLE IF NOT EXISTS sub_models (
    sub_model_id SERIAL PRIMARY KEY,
    model_id INTEGER REFERENCES models(model_id) ON DELETE CASCADE,
    sub_model_type VARCHAR(100) NOT NULL,  -- 'ThermoMechanical', 'JohnsonCookModelConstants', 'Row', etc.
    row_index INTEGER,  -- For EOS Row indexing (1-6)
    parent_sub_model_id INTEGER REFERENCES sub_models(sub_model_id),  -- For nested structures like 'unreacted'/'reacted'
    parent_name VARCHAR(100)  -- 'unreacted', 'reacted', etc.
);

-- ============================================================
-- MODEL_PARAMETERS
-- Individual parameters within models/sub-models
-- Stores parameter names, values, units, and references
-- ============================================================
CREATE TABLE IF NOT EXISTS model_parameters (
    param_id SERIAL PRIMARY KEY,
    sub_model_id INTEGER REFERENCES sub_models(sub_model_id) ON DELETE CASCADE,
    param_name VARCHAR(100) NOT NULL,  -- 'Density', 'AmbientTemperature', 'A', 'B', 'n', etc.
    value TEXT,  -- Store as TEXT to preserve scientific notation and allow NULL
    unit VARCHAR(50),
    ref_id VARCHAR(50),  -- Reference ID (not enforced as foreign key for flexibility)
    entry_index INTEGER  -- For multiple entries per parameter
);

-- ============================================================
-- INDEXES for performance
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_materials_xml_id ON materials(xml_id);
CREATE INDEX IF NOT EXISTS idx_property_categories_material ON property_categories(material_id);
CREATE INDEX IF NOT EXISTS idx_properties_category ON properties(category_id);
CREATE INDEX IF NOT EXISTS idx_property_entries_property ON property_entries(property_id);
CREATE INDEX IF NOT EXISTS idx_models_material ON models(material_id);
CREATE INDEX IF NOT EXISTS idx_sub_models_model ON sub_models(model_id);
CREATE INDEX IF NOT EXISTS idx_model_parameters_sub_model ON model_parameters(sub_model_id);
CREATE INDEX IF NOT EXISTS idx_property_entries_ref ON property_entries(ref_id);
CREATE INDEX IF NOT EXISTS idx_model_parameters_ref ON model_parameters(ref_id);
"""

DROP_SCHEMA_SQL = """
-- Drop all tables in reverse order of dependencies
DROP TABLE IF EXISTS model_parameters CASCADE;
DROP TABLE IF EXISTS sub_models CASCADE;
DROP TABLE IF EXISTS models CASCADE;
DROP TABLE IF EXISTS property_entries CASCADE;
DROP TABLE IF EXISTS properties CASCADE;
DROP TABLE IF EXISTS property_categories CASCADE;
DROP TABLE IF EXISTS materials CASCADE;
DROP TABLE IF EXISTS material_references CASCADE;
"""


def get_create_schema_sql():
    """Return SQL statements to create the database schema."""
    return SCHEMA_SQL


def get_drop_schema_sql():
    """Return SQL statements to drop the database schema."""
    return DROP_SCHEMA_SQL
