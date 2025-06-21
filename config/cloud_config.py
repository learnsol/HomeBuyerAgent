"""
Configuration for cloud deployment with query history storage options.
"""
import os
from typing import Optional

class CloudConfig:
    """Configuration for cloud deployment."""
    
    # Query History Storage Configuration
    QUERY_HISTORY_BACKEND = os.getenv('QUERY_HISTORY_BACKEND', 'auto')  # auto, firestore, cloudsql, memory
    
    # Firestore Configuration
    GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')
    FIRESTORE_COLLECTION = os.getenv('FIRESTORE_COLLECTION', 'query_history')
    
    # Cloud SQL Configuration
    DATABASE_URL = os.getenv('DATABASE_URL')  # PostgreSQL connection string
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    
    # Cloud Run Configuration
    PORT = int(os.getenv('PORT', 8080))
    
    # Enable/disable query history
    ENABLE_QUERY_HISTORY = os.getenv('ENABLE_QUERY_HISTORY', 'true').lower() == 'true'
    
    # Query history retention
    MAX_HISTORY_ENTRIES = int(os.getenv('MAX_HISTORY_ENTRIES', 50))
    
    @classmethod
    def get_database_url(cls) -> Optional[str]:
        """Get the database URL, constructing it from components if needed."""
        if cls.DATABASE_URL:
            return cls.DATABASE_URL
        
        if all([cls.DB_HOST, cls.DB_NAME, cls.DB_USER, cls.DB_PASSWORD]):
            return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        
        return None
    
    @classmethod
    def is_cloud_environment(cls) -> bool:
        """Check if running in a cloud environment."""
        return bool(cls.GOOGLE_CLOUD_PROJECT or os.getenv('GAE_APPLICATION') or os.getenv('K_SERVICE'))
    
    @classmethod
    def get_recommended_backend(cls) -> str:
        """Get the recommended backend for the current environment."""
        if not cls.ENABLE_QUERY_HISTORY:
            return 'memory'
        
        if cls.is_cloud_environment():
            # In cloud - prefer Firestore for simplicity
            if cls.GOOGLE_CLOUD_PROJECT:
                return 'firestore'
            elif cls.get_database_url():
                return 'cloudsql'
            else:
                return 'memory'
        else:
            # Local development
            return 'local'
