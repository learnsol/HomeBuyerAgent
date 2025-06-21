"""
Query History Manager - Stores user queries and results for debugging and analysis.
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

class QueryHistoryManager:
    """Manages storage and retrieval of user queries and results."""
    
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
    
    def add_query(self, user_input: Dict[str, Any], result: Dict[str, Any], session_id: str = None):
        """Add a new query and result to history."""
        history = self.load_history()
        
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
                # Store full result for debugging
                "full_result": result
            }
        }
        
        history.append(query_entry)
        
        # Keep only last 50 queries to prevent file bloat
        if len(history) > 50:
            history = history[-50:]
        
        self.save_history(history)
        print(f"📝 Query saved to history (ID: {len(history)})")
        return len(history)
    
    def get_recent_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent queries."""
        history = self.load_history()
        return history[-limit:] if history else []
    
    def get_query_by_id(self, query_id: int) -> Dict[str, Any]:
        """Get a specific query by its ID (1-based index)."""
        history = self.load_history()
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
            
            print(f"{status_icon} Query {len(self.load_history()) - len(queries) + i}:")
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
        history = self.load_history()
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

# Global instance
query_history = QueryHistoryManager()
