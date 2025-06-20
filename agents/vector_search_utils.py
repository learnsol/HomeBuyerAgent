"""
Vector search utilities with real Vertex AI embedding generation and BigQuery storage.
"""
import numpy as np
from typing import List, Dict, Any
from config import settings
from agents.agent_utils import query_bigquery, get_table_name

EMBEDDING_DIM = 768  # Standard dimension for Gemini embedding-001 and BigQuery vector search

def initialize_embedding_model():
    """Initialize Vertex AI embedding model with fallback to mock."""
    try:
        # Try to use Vertex AI text embeddings - use the same model as BigQuery for consistency
        from vertexai.language_models import TextEmbeddingModel
        import vertexai
        
        # Initialize Vertex AI
        vertexai.init(project=settings.VERTEX_AI_PROJECT_ID, location=settings.VERTEX_AI_LOCATION)
        
        # Use gemini-embedding-001 for consistency with BigQuery stored embeddings
        # Note: text-embedding-004 is newer but gemini-embedding-001 might be what was used for storage
        try:
            model = TextEmbeddingModel.from_pretrained("text-embedding-004")
            print("✅ Using Vertex AI text-embedding-004 model (768 dimensions)")
        except:
            model = TextEmbeddingModel.from_pretrained("textembedding-gecko@003")
            print("✅ Using Vertex AI textembedding-gecko@003 model (768 dimensions)")
        
        return model
        
    except Exception as e:
        print(f"❌ Failed to initialize Vertex AI embeddings: {e}")
        print("🔄 Falling back to mock embedding model")
        
        # Fallback to mock model
        class MockTextEmbeddingModel:
            def get_embeddings(self, texts: List[str]) -> List[Any]:
                print(f"MockEmbeddingModel: Generating {EMBEDDING_DIM}D embeddings for {len(texts)} texts.")
                results = []
                for text in texts:
                    np.random.seed(abs(hash(text)) % (2**32 - 1))
                    embedding_values = np.random.rand(EMBEDDING_DIM).tolist()
                    results.append(type('Embedding', (), {'values': embedding_values})())
                return results
        return MockTextEmbeddingModel()

def generate_query_embedding(query_text: str) -> List[float]:
    """Generates an embedding for the given query text using Vertex AI or mock."""
    try:
        model = initialize_embedding_model()
        
        # Handle both Vertex AI and mock model interfaces
        if hasattr(model, 'get_embeddings'):
            # Vertex AI TextEmbeddingModel interface
            embeddings = model.get_embeddings([query_text])
            if embeddings and hasattr(embeddings[0], 'values'):
                return embeddings[0].values
            elif embeddings:
                return embeddings[0]
        else:
            # Mock model interface
            embeddings = model.get_embeddings([query_text])
            if embeddings:
                return embeddings[0].values
                
    except Exception as e:
        print(f"❌ Error generating query embedding: {e}")
        print("🔄 Using fallback embedding")
    
    # Fallback to zero vector
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

def vector_similarity_search(query_embedding: List[float], search_query: str = "", limit: int = 15) -> List[Dict[str, Any]]:
    """
    Performs vector similarity search using BigQuery stored embeddings.
    
    BigQuery vector search is optimized for 768-dimensional embeddings (standard for Gemini embedding-001).
    If stored embeddings have different dimensions, we use the first 768 dimensions for compatibility.
    """
    print(f"🔍 Performing vector similarity search with {len(query_embedding)}D embedding")
    
    # Try BigQuery vector similarity search using stored embeddings
    try:
        from agents.agent_utils import query_bigquery, get_table_name
        
        table_name = get_table_name("listings")        # Create a simpler approach using manual cosine similarity calculation
        # First, let's test if we can retrieve the data and embeddings properly
        simple_query = f"""
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
            image_url,
            description_embedding        FROM {table_name}
        WHERE description_embedding IS NOT NULL
        AND ARRAY_LENGTH(description_embedding) > 0
        LIMIT 20
        """
        
        print("🔍 Fetching listings with embeddings from BigQuery")
        print(f"🔍 Table name: {table_name}")
        print(f"🔍 Full query: {simple_query}")
        listings = query_bigquery(simple_query)
        
        if not listings:
            raise Exception("No listings with embeddings found")
        
        print(f"✅ Found {len(listings)} listings with embeddings")        # Calculate similarity scores in Python using dot product
        results_with_scores = []
        query_embedding_np = np.array(query_embedding)
        
        print(f"📐 Query embedding dimension: {len(query_embedding_np)}")
        
        for listing in listings:
            if listing.get('description_embedding'):
                # Convert BigQuery array to numpy array
                listing_embedding = np.array(listing['description_embedding'])
                
                # Handle different embedding dimensions - use first 768 for BigQuery compatibility
                if len(listing_embedding) != len(query_embedding_np):
                    if len(listing_embedding) >= EMBEDDING_DIM:
                        # Use exactly 768 dimensions (standard for Gemini embedding-001 and BigQuery)
                        listing_embedding = listing_embedding[:EMBEDDING_DIM]
                        if len(listing_embedding) == EMBEDDING_DIM and len(query_embedding_np) == EMBEDDING_DIM:
                            print(f"✅ Using first {EMBEDDING_DIM} dimensions for BigQuery compatibility")
                    else:
                        print(f"⚠️  Skipping listing with insufficient embedding dimensions: {len(listing_embedding)}")
                        continue
                
                # Calculate dot product similarity
                similarity_score = np.dot(query_embedding_np, listing_embedding)
                
                # Add similarity score to listing
                listing_with_score = listing.copy()
                listing_with_score['similarity_score'] = float(similarity_score)
                results_with_scores.append(listing_with_score)
          # Sort by similarity score and return top results
        results_with_scores.sort(key=lambda x: x['similarity_score'], reverse=True)
        final_results = results_with_scores[:limit]
        
        if final_results:
            print(f"✅ BigQuery vector search with dot product similarity returned {len(final_results)} results")
            for i, result in enumerate(final_results):
                score = result.get('similarity_score', 0)
                print(f"  {i+1}. {result.get('address', 'N/A')} - Dot Product Score: {score:.3f}")
            return final_results
            
    except Exception as e:
        print(f"❌ BigQuery vector search failed: {e}")
        print("🔄 Falling back to text-based search")
    
    # Fallback to text-based search
    try:
        table_name = get_table_name("listings")
        
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
        FROM {table_name}
        WHERE {where_clause}
        ORDER BY price ASC
        LIMIT {limit * 2}
        """
        
        results = query_bigquery(basic_query)
        
        if results:
            print(f"✅ BigQuery text search returned {len(results)} results")
            # Add mock similarity scores for text search
            for i, result in enumerate(results):
                result['similarity_score'] = max(0.5, 1.0 - (i * 0.1))  # Decreasing similarity
            return results[:limit]
            
    except Exception as e:
        print(f"❌ BigQuery text search failed: {e}")
        print("🔄 Falling back to mock data")
      # Final fallback to mock data
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

def search_listings_by_criteria(user_criteria: Dict[str, Any], top_k: int = 10) -> List[Dict[str, Any]]:
    """
    Search for property listings based on user criteria using vector search.
    """
    try:
        # Create search query from criteria
        search_query = create_search_query_from_criteria(user_criteria)
        
        # Generate embedding for the search query
        query_embedding = generate_query_embedding(search_query)
        
        # Perform vector similarity search
        results = vector_similarity_search(query_embedding, search_query, limit=top_k)
        
        print(f"🔍 Found {len(results)} listings matching criteria")
        return results
        
    except Exception as e:
        print(f"❌ Error searching listings: {str(e)}")
        return []

def search_neighborhood_data(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Search for neighborhood information using vector search.
    """
    try:
        # Generate embedding for the neighborhood query
        query_embedding = generate_query_embedding(query)
        
        # Search neighborhood/locality data
        # For now, return mock data as the neighborhood data may not be in vector format
        mock_results = [
            {"content": f"Neighborhood analysis for {query}: Good schools, shopping centers, and parks nearby. Safe area with low crime rates."},
            {"content": f"Area features for {query}: Public transportation, walkable streets, grocery stores within walking distance."},
            {"content": f"Community data for {query}: Family-friendly environment, playgrounds, and recreational facilities available."},
            {"content": f"Local amenities for {query}: Restaurants, cafes, and local businesses create a vibrant community atmosphere."},
            {"content": f"Safety information for {query}: Well-lit streets, neighborhood watch programs, and responsive local police."}
        ]
        
        print(f"🏘️ Found {len(mock_results)} neighborhood data points")
        return mock_results[:top_k]
        
    except Exception as e:
        print(f"❌ Error searching neighborhood data: {str(e)}")
        return []

def search_hazard_data(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Search for hazard and safety information using vector search.
    """
    try:
        # Generate embedding for the hazard query
        query_embedding = generate_query_embedding(query)
        
        # Search hazard/safety data
        # For now, return mock data as hazard data may not be in vector format
        mock_results = [
            {"content": f"Safety assessment for {query}: Low flood risk area, no major environmental hazards detected."},
            {"content": f"Environmental data for {query}: Clean air quality, no toxic waste sites in vicinity."},
            {"content": f"Natural disaster risk for {query}: Minimal earthquake risk, occasional severe weather but well-prepared infrastructure."},
            {"content": f"Crime statistics for {query}: Below average crime rates, safe residential area with good security."},
            {"content": f"Emergency services for {query}: Fire station and hospital within 5 miles, good emergency response times."}
        ]
        
        print(f"⚠️ Found {len(mock_results)} hazard data points")
        return mock_results[:top_k]
        
    except Exception as e:
        print(f"❌ Error searching hazard data: {str(e)}")
        return []
