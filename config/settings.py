"""
Configuration settings for the Home Buyer Agent application.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# BigQuery settings - using your actual project configuration
BIGQUERY_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", os.getenv("BIGQUERY_PROJECT_ID", "gen-lang-client-0044046698"))
BIGQUERY_DATASET_ID = os.getenv("BIGQUERY_DATASET", os.getenv("BIGQUERY_DATASET_ID", "home_buyer_hackathon_data"))
BIGQUERY_LOCATION = os.getenv("BIGQUERY_LOCATION", "northamerica-northeast2")
BIGQUERY_LISTINGS_TABLE = os.getenv("LISTINGS_TABLE", "listings")
BIGQUERY_NEIGHBORHOODS_TABLE = os.getenv("NEIGHBORHOODS_TABLE", "neighborhoods")
BIGQUERY_AFFORDABILITY_PARAMS_TABLE = os.getenv("BIGQUERY_AFFORDABILITY_PARAMS_TABLE", "affordability_parameters")

# Vertex AI settings - using your actual project configuration
VERTEX_AI_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", BIGQUERY_PROJECT_ID)
VERTEX_AI_LOCATION = os.getenv("VERTEX_AI_LOCATION", "us-central1")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "text-embedding-004")

# Agent model names - Updated for Vertex AI compatibility
DEFAULT_AGENT_MODEL = os.getenv("DEFAULT_AGENT_MODEL", "gemini-2.0-flash-001")
ORCHESTRATOR_MODEL = os.getenv("ORCHESTRATOR_MODEL", "gemini-2.0-flash-001")

# Search and recommendation parameters
VECTOR_SEARCH_LIMIT = int(os.getenv("VECTOR_SEARCH_LIMIT", 15))
FINAL_RECOMMENDATION_COUNT = int(os.getenv("FINAL_RECOMMENDATION_COUNT", 3))

# Mock data settings
NUM_MOCK_LISTINGS = int(os.getenv("NUM_MOCK_LISTINGS", 100))
MOCK_DATA_OUTPUT_FILE = os.getenv("MOCK_DATA_OUTPUT_FILE", "mock_listings_data.json")

# Query History Configuration for Cloud Deployment
QUERY_HISTORY_BACKEND = os.getenv('QUERY_HISTORY_BACKEND', 'auto')  # auto, firestore, cloudsql, memory, local
ENABLE_QUERY_HISTORY = os.getenv('ENABLE_QUERY_HISTORY', 'true').lower() == 'true'
MAX_HISTORY_ENTRIES = int(os.getenv('MAX_HISTORY_ENTRIES', 50))

# Firestore Configuration
FIRESTORE_COLLECTION = os.getenv('FIRESTORE_COLLECTION', 'query_history')

# Cloud SQL Configuration  
DATABASE_URL = os.getenv('DATABASE_URL')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME') 
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Cloud Run Configuration
PORT = int(os.getenv('PORT', 8080))

# Deployment Environment Detection
def is_cloud_environment() -> bool:
    """Check if running in a cloud environment."""
    return bool(os.getenv('GOOGLE_CLOUD_PROJECT') or 
                os.getenv('GAE_APPLICATION') or 
                os.getenv('K_SERVICE'))

def get_database_url() -> str:
    """Get database URL, constructing from components if needed."""
    if DATABASE_URL:
        return DATABASE_URL
    
    if all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
        return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    return None
