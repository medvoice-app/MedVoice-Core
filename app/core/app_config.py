# This file provides backward compatibility with the old config structure
# Import settings from the new config loader
from app.core.config_loader import INSERT_MOCK_DATA, ON_LOCALHOST, RAG_SYS

# These variables are now imported from config_loader which loads them from YAML files
# INSERT_MOCK_DATA - Toggle for mock data insertion (0=disabled, 1=enabled)
# ON_LOCALHOST - Toggle for development environment (0=prod, 1=local)
# RAG_SYS - Toggle for RAG system (0=disabled, 1=enabled)
