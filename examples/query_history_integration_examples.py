"""
Example of how to update your main application files to use cloud-ready query history.
"""

# BEFORE (current approach)
"""
from query_history import query_history

# This stores data in local JSON file - not suitable for Cloud Run
query_history.add_query(user_input, result, session_id)
"""

# AFTER (cloud-ready approach)
"""
from query_history_cloud import query_history
# OR for explicit backend selection:
# from query_history_cloud import CloudQueryHistoryManager, FirestoreBackend
# query_history = CloudQueryHistoryManager(FirestoreBackend())

# This automatically selects appropriate backend based on environment
query_history.add_query(user_input, result, session_id)
"""

# Example integration in orchestrator_adk.py:
def example_orchestrator_integration():
    """Example of how to integrate cloud query history in orchestrator."""
    
    # Import the cloud-ready version
    from query_history_cloud import query_history
    from config.settings import ENABLE_QUERY_HISTORY
    
    def process_user_query(user_input, session_id=None):
        """Process user query and save to history if enabled."""
        
        # Your existing logic here...
        result = {
            "recommendations": [],
            "found_listings": [],
            "analysis_completed": True,
            "session_id": session_id
        }
        
        # Save to history if enabled
        if ENABLE_QUERY_HISTORY:
            try:
                query_history.add_query(
                    user_input={"user_criteria": user_input, "timestamp": "2025-06-20T10:00:00"},
                    result=result,
                    session_id=session_id
                )
            except Exception as e:
                # Don't fail the main request if history storage fails
                print(f"Warning: Failed to save query history: {e}")
        
        return result

# Example API server integration:
def example_api_server_integration():
    """Example of how to integrate in API server."""
    
    from flask import Flask, request, jsonify
    from query_history_cloud import query_history
    import uuid
    
    app = Flask(__name__)
    
    @app.route('/search', methods=['POST'])
    def search_properties():
        data = request.json
        session_id = str(uuid.uuid4())
        
        # Process the search request
        result = process_search(data)
        
        # Save to history (non-blocking)
        try:
            query_history.add_query(
                user_input=data,
                result=result,
                session_id=session_id
            )
        except Exception as e:
            # Log error but don't fail the request
            app.logger.warning(f"Failed to save query history: {e}")
        
        return jsonify(result)
    
    @app.route('/history', methods=['GET'])
    def get_query_history():
        """Get recent query history."""
        try:
            limit = request.args.get('limit', 10, type=int)
            recent_queries = query_history.get_recent_queries(limit)
            return jsonify(recent_queries)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# Environment-specific configuration examples:

# For local development (.env file):
"""
QUERY_HISTORY_BACKEND=local
ENABLE_QUERY_HISTORY=true
"""

# For Cloud Run with Firestore:
"""
GOOGLE_CLOUD_PROJECT=your-project-id
QUERY_HISTORY_BACKEND=firestore
FIRESTORE_COLLECTION=query_history
ENABLE_QUERY_HISTORY=true
"""

# For Cloud Run with Cloud SQL:
"""
DATABASE_URL=postgresql://user:pass@host:port/database
QUERY_HISTORY_BACKEND=cloudsql
ENABLE_QUERY_HISTORY=true
"""

# For privacy-focused deployment (no persistence):
"""
QUERY_HISTORY_BACKEND=memory
ENABLE_QUERY_HISTORY=true
"""
