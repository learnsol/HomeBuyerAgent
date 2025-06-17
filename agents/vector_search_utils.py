"""
Vector search utilities with mock embedding generation.
"""
import numpy as np
from typing import List, Dict, Any
from config import settings
from agents.agent_utils import query_bigquery, get_table_name

EMBEDDING_DIM = 768

def initialize_embedding_model():
    """Mock embedding model for development."""
    class MockTextEmbeddingModel:
        def get_embeddings(self, texts: List[str]) -> List[Any]:
            print(f"MockEmbeddingModel: Generating embeddings for {len(texts)} texts.")
            results = []
            for text in texts:
                np.random.seed(abs(hash(text)) % (2**32 - 1))
                embedding_values = np.random.rand(EMBEDDING_DIM).tolist()
                results.append(type('Embedding', (), {'values': embedding_values})())
            return results
    return MockTextEmbeddingModel()

def generate_query_embedding(query_text: str) -> List[float]:
    """Generates an embedding for the given query text."""
    model = initialize_embedding_model()
    embeddings = model.get_embeddings([query_text])
    if embeddings:
        return embeddings[0].values
    return [0.0] * EMBEDDING_DIM

def create_search_query_from_criteria(user_criteria: Dict[str, Any]) -> str:
    """Creates a natural language search query from user criteria."""
    parts = []
    if "bedrooms_min" in user_criteria:
        parts.append(f"{user_criteria['bedrooms_min']} bedroom{'s' if user_criteria['bedrooms_min'] > 1 else ''}")
    if "bathrooms_min" in user_criteria:
        parts.append(f"{user_criteria['bathrooms_min']} bathroom{'s' if user_criteria['bathrooms_min'] > 1 else ''}")
    if "price_max" in user_criteria:
        parts.append(f"under ${user_criteria['price_max']:,}")
    if "price_min" in user_criteria:
        parts.append(f"over ${user_criteria['price_min']:,}")
    
    keywords = user_criteria.get("keywords", [])
    if isinstance(keywords, list) and keywords:
        parts.append(f"with features like {', '.join(keywords)}")
    elif isinstance(keywords, str) and keywords:
        parts.append(f"with features like {keywords}")

    if not parts:
        return "Find a suitable house."
    
    return f"Find a {' '.join(parts)} house."

def vector_similarity_search(query_embedding: List[float], search_query: str = "", limit: int = 5) -> List[Dict[str, Any]]:
    """Performs vector similarity search using BigQuery or mock data."""
    print(f"🔍 Performing vector similarity search with {len(query_embedding)}D embedding")
    
    # Try BigQuery basic search first (without ML.DISTANCE for now)
    try:
        from agents.agent_utils import query_bigquery, get_table_name
        
        # Create BigQuery basic search query (simplified without vector similarity for now)
        table_name = get_table_name("listings")
          # Simple query with text matching instead of vector similarity
        # Extract keywords from search query for basic text matching
        keywords = []
        if "bedrooms" in search_query.lower():
            keywords.append("bedroom")
        if "bathroom" in search_query.lower():
            keywords.append("bathroom")
        if "kitchen" in search_query.lower():
            keywords.append("kitchen")
        if "backyard" in search_query.lower():
            keywords.append("backyard")
        if "school" in search_query.lower():
            keywords.append("school")
            
        # Build WHERE clause for text matching
        where_conditions = ["price IS NOT NULL", "bedrooms IS NOT NULL", "bathrooms IS NOT NULL"]
        
        if keywords:
            keyword_conditions = []
            for keyword in keywords:
                keyword_conditions.append(f"LOWER(description) LIKE '%{keyword}%'")
            where_conditions.append(f"({' OR '.join(keyword_conditions)})")
        
        where_clause = " AND ".join(where_conditions)
        
        basic_query = f"""
        SELECT 
            listing_id,
            address_street as address,
            neighborhood_id,
            price,
            bedrooms,
            bathrooms,
            square_footage,
            property_type,
            year_built,
            description,
            image_url
        FROM `{table_name}`
        WHERE {where_clause}
        ORDER BY price ASC
        LIMIT {limit * 2}
        """
        
        results = query_bigquery(basic_query)
        
        if results:
            print(f"✅ BigQuery basic search returned {len(results)} results")
            # Add mock similarity scores for now (in a real implementation, you'd compute actual similarity)
            for i, result in enumerate(results):
                result['similarity_score'] = max(0.5, 1.0 - (i * 0.1))  # Decreasing similarity
            return results[:limit]
            
    except Exception as e:
        print(f"❌ BigQuery basic search failed: {e}")
        print("🔄 Falling back to mock data")
    
    # Fallback to mock data
    print("🔧 Using mock vector search data")
    mock_listings = [
        {
            "listing_id": "MOCK001",
            "description": "Beautiful 3-bedroom home with modern kitchen and large backyard",
            "price": 450000.0,
            "bedrooms": 3,
            "bathrooms": 2.0,
            "address": "123 Main St, Anytown",
            "neighborhood": "Downtown",
            "similarity_score": 0.95
        },
        {
            "listing_id": "MOCK002",
            "description": "Family-friendly 4-bedroom house with updated kitchen in safe neighborhood",
            "price": 520000.0,
            "bedrooms": 4,
            "bathrooms": 3.0,
            "address": "456 Oak Ave, Anytown",
            "neighborhood": "Suburbs",
            "similarity_score": 0.88
        },
        {
            "listing_id": "MOCK003",
            "description": "Cozy 3-bedroom home near excellent schools with modern amenities",
            "price": 380000.0,
            "bedrooms": 3,
            "bathrooms": 2.0,
            "address": "789 Pine Rd, Anytown",
            "neighborhood": "School District",
            "similarity_score": 0.82
        }
    ]
    
    return mock_listings[:limit]
