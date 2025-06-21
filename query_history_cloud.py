"""
Cloud-Ready Query History Manager - Multiple storage backend options for production deployment.
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from abc import ABC, abstractmethod

class QueryHistoryBackend(ABC):
    """Abstract base class for query history storage backends."""
    
    @abstractmethod
    def load_history(self) -> List[Dict[str, Any]]:
        """Load query history."""
        pass
    
    @abstractmethod
    def save_history(self, history: List[Dict[str, Any]]):
        """Save query history."""
        pass

class LocalFileBackend(QueryHistoryBackend):
    """Local file storage backend (for development only)."""
    
    def __init__(self, history_file: str = "query_history.json"):
        self.history_file = Path(history_file)
        self.ensure_history_file()
    
    def ensure_history_file(self):
        """Create history file if it doesn't exist."""
        if not self.history_file.exists():
            self.save_history([])
    
    def load_history(self) -> List[Dict[str, Any]]:
        """Load query history from file."""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
            return []
    
    def save_history(self, history: List[Dict[str, Any]]):
        """Save query history to file."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"Error saving history: {e}")

class FirestoreBackend(QueryHistoryBackend):
    """Google Cloud Firestore backend for production."""
    
    def __init__(self, collection_name: str = "query_history"):
        self.collection_name = collection_name
        self._firestore_client = None
    
    @property
    def firestore_client(self):
        """Lazy initialization of Firestore client."""
        if self._firestore_client is None:
            try:
                from google.cloud import firestore
                self._firestore_client = firestore.Client()
            except ImportError:
                raise ImportError("google-cloud-firestore not installed. Run: pip install google-cloud-firestore")
        return self._firestore_client
    
    def load_history(self) -> List[Dict[str, Any]]:
        """Load query history from Firestore."""
        try:
            docs = (self.firestore_client
                   .collection(self.collection_name)
                   .order_by('timestamp')
                   .limit(50)  # Limit to last 50 queries
                   .stream())
            
            history = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                history.append(data)
            return history
        except Exception as e:
            print(f"Error loading history from Firestore: {e}")
            return []
    
    def save_history(self, history: List[Dict[str, Any]]):
        """Save query history to Firestore (saves last entry only)."""
        if not history:
            return
        
        try:
            # Save only the last entry (new query)
            latest_query = history[-1]
            self.firestore_client.collection(self.collection_name).add(latest_query)
        except Exception as e:
            print(f"Error saving history to Firestore: {e}")

class CloudSQLBackend(QueryHistoryBackend):
    """Google Cloud SQL (PostgreSQL) backend for production."""
    
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or os.getenv('DATABASE_URL')
        self._connection_pool = None
        self.init_table()
    
    @property
    def connection_pool(self):
        """Lazy initialization of connection pool."""
        if self._connection_pool is None:
            try:
                import psycopg2
                from psycopg2 import pool
                self._connection_pool = pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=5,
                    dsn=self.connection_string
                )
            except ImportError:
                raise ImportError("psycopg2 not installed. Run: pip install psycopg2-binary")
        return self._connection_pool
    
    def init_table(self):
        """Initialize the query_history table if it doesn't exist."""
        try:
            conn = self.connection_pool.getconn()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_history (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    session_id VARCHAR(255),
                    user_input JSONB,
                    result JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_query_history_timestamp 
                ON query_history(timestamp DESC)
            """)
            conn.commit()
        except Exception as e:
            print(f"Error initializing table: {e}")
        finally:
            if conn:
                self.connection_pool.putconn(conn)
    
    def load_history(self) -> List[Dict[str, Any]]:
        """Load query history from Cloud SQL."""
        try:
            conn = self.connection_pool.getconn()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timestamp, session_id, user_input, result
                FROM query_history 
                ORDER BY timestamp DESC 
                LIMIT 50
            """)
            rows = cursor.fetchall()
            
            history = []
            for row in rows:
                history.append({
                    'timestamp': row[0].isoformat() if row[0] else None,
                    'session_id': row[1],
                    'user_input': row[2],
                    'result': row[3]
                })
            return list(reversed(history))  # Return in chronological order
        except Exception as e:
            print(f"Error loading history from Cloud SQL: {e}")
            return []
        finally:
            if conn:
                self.connection_pool.putconn(conn)
    
    def save_history(self, history: List[Dict[str, Any]]):
        """Save query history to Cloud SQL (saves last entry only)."""
        if not history:
            return
        
        try:
            latest_query = history[-1]
            conn = self.connection_pool.getconn()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO query_history (timestamp, session_id, user_input, result)
                VALUES (%s, %s, %s, %s)
            """, (
                latest_query.get('timestamp'),
                latest_query.get('session_id'),
                json.dumps(latest_query.get('user_input')),
                json.dumps(latest_query.get('result'))
            ))
            conn.commit()
        except Exception as e:
            print(f"Error saving history to Cloud SQL: {e}")
        finally:
            if conn:
                self.connection_pool.putconn(conn)

class InMemoryBackend(QueryHistoryBackend):
    """In-memory storage backend (for testing/temporary use)."""
    
    def __init__(self):
        self._history = []
    
    def load_history(self) -> List[Dict[str, Any]]:
        """Load query history from memory."""
        return self._history.copy()
    
    def save_history(self, history: List[Dict[str, Any]]):
        """Save query history to memory."""
        self._history = history.copy()

class CloudQueryHistoryManager:
    """Cloud-ready Query History Manager with pluggable storage backends."""
    
    def __init__(self, backend: QueryHistoryBackend = None):
        if backend is None:
            # Auto-select backend based on environment
            backend = self._auto_select_backend()
        self.backend = backend
    
    def _auto_select_backend(self) -> QueryHistoryBackend:
        """Automatically select the appropriate backend based on environment."""
        # Check if running in Google Cloud
        if os.getenv('GOOGLE_CLOUD_PROJECT'):
            # In Google Cloud - prefer Firestore for simplicity
            try:
                return FirestoreBackend()
            except ImportError:
                print("Firestore not available, falling back to in-memory storage")
                return InMemoryBackend()
        
        # Check if Cloud SQL is configured
        elif os.getenv('DATABASE_URL'):
            try:
                return CloudSQLBackend()
            except ImportError:
                print("Cloud SQL not available, falling back to in-memory storage")
                return InMemoryBackend()
        
        # Development environment
        else:
            return LocalFileBackend()
    
    def add_query(self, user_input: Dict[str, Any], result: Dict[str, Any], session_id: str = None):
        """Add a new query and result to history."""
        history = self.backend.load_history()
        
        query_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "user_input": user_input,
            "result": {
                "status": "success" if result.get("recommendations") else "no_recommendations",
                "found_listings_count": len(result.get("found_listings", [])),
                "recommendations_count": len(result.get("recommendations", [])),
                "error": result.get("error"),
                "analysis_completed": result.get("analysis_completed", False),
                "session_id": result.get("session_id"),
                # Store full result for debugging (consider size limits in production)
                "full_result": result
            }
        }
        
        history.append(query_entry)
        
        # Keep only last 50 queries to prevent bloat
        if len(history) > 50:
            history = history[-50:]
        
        self.backend.save_history(history)
        print(f"📝 Query saved to history (ID: {len(history)})")
        return len(history)
    
    def get_recent_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent queries."""
        history = self.backend.load_history()
        return history[-limit:] if history else []
    
    def get_query_by_id(self, query_id: int) -> Dict[str, Any]:
        """Get a specific query by its ID (1-based index)."""
        history = self.backend.load_history()
        if 1 <= query_id <= len(history):
            return history[query_id - 1]
        return None
    
    def print_recent_queries(self, limit: int = 5):
        """Print summary of recent queries."""
        queries = self.get_recent_queries(limit)
        if not queries:
            print("📭 No queries in history")
            return        
        print(f"📋 Recent Queries (last {len(queries)}):")
        print("=" * 60)
        
        for i, query in enumerate(queries, 1):
            timestamp = query.get("timestamp", "Unknown")
            user_criteria = query.get("user_input", {}).get("user_criteria", {})
            result = query.get("result", {})
            
            status_icon = "✅" if result.get("status") == "success" else "❌"
            
            print(f"{status_icon} Query {len(self.backend.load_history()) - len(queries) + i}:")
            print(f"   Time: {timestamp}")
            price_max = user_criteria.get('price_max', 'N/A')
            price_str = f"${price_max:,}" if isinstance(price_max, (int, float)) else str(price_max)
            print(f"   Price Max: {price_str}")
            print(f"   Bedrooms: {user_criteria.get('bedrooms_min', 'N/A')}+")
            print(f"   Keywords: {user_criteria.get('keywords', 'N/A')}")
            print(f"   Found: {result.get('found_listings_count', 0)} listings")
            print(f"   Recommendations: {result.get('recommendations_count', 0)}")
            if result.get("error"):
                print(f"   Error: {result.get('error')}")
            print()
    
    def analyze_patterns(self):
        """Analyze query patterns and provide insights."""
        history = self.backend.load_history()
        if not history:
            print("📭 No queries to analyze")
            return
        
        print("📊 Query Analysis:")
        print("=" * 40)
        
        total_queries = len(history)
        successful_queries = sum(1 for q in history if q.get("result", {}).get("status") == "success")
        
        print(f"Total Queries: {total_queries}")
        print(f"Successful: {successful_queries} ({successful_queries/total_queries*100:.1f}%)")
        print(f"No Recommendations: {total_queries - successful_queries} ({(total_queries-successful_queries)/total_queries*100:.1f}%)")
        
        # Analyze price ranges
        price_ranges = []
        for query in history:
            price_max = query.get("user_input", {}).get("user_criteria", {}).get("price_max")
            if price_max:
                price_ranges.append(price_max)
        
        if price_ranges:
            avg_price = sum(price_ranges) / len(price_ranges)
            print(f"Average Max Price: ${avg_price:,.0f}")
            print(f"Price Range: ${min(price_ranges):,} - ${max(price_ranges):,}")

# Factory function for easy instantiation
def create_query_history_manager(backend_type: str = "auto") -> CloudQueryHistoryManager:
    """Create a query history manager with the specified backend."""
    
    backends = {
        "local": LocalFileBackend,
        "firestore": FirestoreBackend,
        "cloudsql": CloudSQLBackend,
        "memory": InMemoryBackend,
        "auto": None  # Auto-select
    }
    
    if backend_type == "auto":
        return CloudQueryHistoryManager()
    elif backend_type in backends:
        backend_class = backends[backend_type]
        return CloudQueryHistoryManager(backend_class())
    else:
        raise ValueError(f"Unknown backend type: {backend_type}")

# Global instance - will auto-select appropriate backend
query_history = CloudQueryHistoryManager()
