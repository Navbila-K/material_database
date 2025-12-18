"""
Configuration module for Material Database Engine.
Centralizes database connection and application settings.
"""
import os

# Database connection settings
DATABASE_URL = "postgresql://sridhars:mypassword@localhost:5432/Materials_DB"

# Parse connection components
def parse_db_url(url):
    """Extract database connection components from URL."""
    # postgresql://user:password@host:port/database
    parts = url.replace("postgresql://", "").split("@")
    user_pass = parts[0].split(":")
    host_db = parts[1].split("/")
    host_port = host_db[0].split(":")
    
    return {
        "user": user_pass[0],
        "password": user_pass[1],
        "host": host_port[0],
        "port": host_port[1],
        "database": host_db[1]
    }

DB_CONFIG = parse_db_url(DATABASE_URL)

# Application settings
XML_DIR = os.path.join(os.path.dirname(__file__), "xml")
EXPORT_DIR = os.path.join(os.path.dirname(__file__), "export", "output")

# Ensure export directory exists
os.makedirs(EXPORT_DIR, exist_ok=True)
