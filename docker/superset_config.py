"""
Superset Configuration File
Custom configuration for Health Data Pipeline
"""

import os

# Flask App Builder configuration
# Your App secret key
SECRET_KEY = os.environ.get('SUPERSET_SECRET_KEY', 'your_secret_key_change_in_production')

# The SQLAlchemy connection string to your database backend
# This connection defines the path to the database that stores your
# superset metadata (slices, connections, tables, dashboards, ...).
SQLALCHEMY_DATABASE_URI = 'sqlite:////app/superset_home/superset.db'

# Flask-WTF flag for CSRF
WTF_CSRF_ENABLED = True

# Set this API key to enable Mapbox visualizations
MAPBOX_API_KEY = ''

# Disable example data loading
SUPERSET_LOAD_EXAMPLES = False

# Configuration to allow CORS
ENABLE_CORS = True
CORS_OPTIONS = {
    'supports_credentials': True,
    'allow_headers': ['*'],
    'resources': ['*'],
    'origins': ['*']
}

# Configuration for database connections
PREVENT_UNSAFE_DB_CONNECTIONS = False

# Allow users to create databases
DATABASE_ALLOW_MULTI_SCHEMA_METADATA_FETCH = True

# Row limit for SQL Lab queries
SQL_MAX_ROW = 100000
SUPERSET_WEBSERVER_TIMEOUT = 300

# Feature flags
FEATURE_FLAGS = {
    'ENABLE_TEMPLATE_PROCESSING': True,
    'DASHBOARD_NATIVE_FILTERS': True,
    'DASHBOARD_CROSS_FILTERS': True,
    'DASHBOARD_NATIVE_FILTERS_SET': True,
    'EMBEDDED_SUPERSET': True,
}

# Cache configuration
CACHE_CONFIG = {
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300
}

# Dashboard auto-refresh intervals
SUPERSET_DASHBOARD_POSITION_DATA_LIMIT = 65535