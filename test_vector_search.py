#!/usr/bin/env python3
"""
Test script to verify vector search functionality with real embeddings.
"""

from agents.vector_search_utils import generate_query_embedding, vector_similarity_search, create_search_query_from_criteria

def test_vector_search():
    """Test the vector search functionality."""
    print("🧪 Testing Vector Search with Real Embeddings")
    print("=" * 50)
    
    # Test embedding generation
    print("1. Testing embedding generation...")
    query = "Find a 3 bedroom house with modern kitchen"
    embedding = generate_query_embedding(query)
    print(f"   ✅ Generated embedding dimension: {len(embedding)}")
    
    # Test search criteria conversion
    print("\n2. Testing search criteria conversion...")
    criteria = {
        "bedrooms_min": 3,
        "bathrooms_min": 2,
        "price_max": 500000,
        "keywords": ["modern kitchen", "backyard"]
    }
    search_query = create_search_query_from_criteria(criteria)
    print(f"   ✅ Search query: {search_query}")
    
    # Test vector search
    print("\n3. Testing vector similarity search...")
    results = vector_similarity_search(embedding, search_query, limit=3)
    print(f"   ✅ Found {len(results)} results")
    
    for i, result in enumerate(results):
        address = result.get("address", "N/A")
        score = result.get("similarity_score", 0)
        price = result.get("price", 0)
        bedrooms = result.get("bedrooms", 0)
        bathrooms = result.get("bathrooms", 0)
        
        print(f"   {i+1}. {address}")
        print(f"      Price: ${price:,} | {bedrooms}BR/{bathrooms}BA | Score: {score:.3f}")
    
    print("\n🎉 Vector search test completed!")

if __name__ == "__main__":
    test_vector_search()
