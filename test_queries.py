#!/usr/bin/env python3
"""
Quick Test Queries for Vector Search with Real BigQuery Embeddings.

Run this to quickly test various search queries against the real embeddings.
"""

from agents.vector_search_utils import generate_query_embedding, vector_similarity_search, create_search_query_from_criteria

def test_search_queries():
    """Test various search queries to see how well the vector search works."""
    
    print("🔍 Testing Vector Search with Real BigQuery Embeddings")
    print("=" * 60)
    
    # Define test queries with expected characteristics
    test_queries = [
        {
            "query": "Modern kitchen with granite countertops",
            "description": "Should find homes with updated kitchens",
            "expected_features": ["kitchen", "modern", "granite"]
        },
        {
            "query": "Family home with backyard and good schools",
            "description": "Should find family-friendly properties",
            "expected_features": ["family", "backyard", "schools"]
        },
        {
            "query": "Luxury home with high-end finishes",
            "description": "Should find premium properties",
            "expected_features": ["luxury", "high-end", "premium"]
        },
        {
            "query": "Affordable starter home for first-time buyers",
            "description": "Should find budget-friendly options",
            "expected_features": ["affordable", "starter", "budget"]
        },
        {
            "query": "Downtown urban condo with city amenities",
            "description": "Should find urban properties",
            "expected_features": ["downtown", "urban", "city"]
        },
        {
            "query": "Quiet suburban house with garage",
            "description": "Should find suburban homes",
            "expected_features": ["suburban", "quiet", "garage"]
        },
        {
            "query": "Victorian style home with historic charm",
            "description": "Should find older/historic properties",
            "expected_features": ["victorian", "historic", "charm"]
        },
        {
            "query": "Open floor plan with lots of natural light",
            "description": "Should find homes with modern layouts",
            "expected_features": ["open", "light", "floor plan"]
        }
    ]
    
    results_summary = []
    
    for i, test_case in enumerate(test_queries, 1):
        query = test_case["query"]
        description = test_case["description"]
        
        print(f"\n🔍 Test {i}: {query}")
        print(f"   Expected: {description}")
        print("-" * 50)
        
        try:
            # Generate embedding
            embedding = generate_query_embedding(query)
            
            # Perform search
            results = vector_similarity_search(embedding, query, limit=5)
            
            if results:
                print(f"   ✅ Found {len(results)} results:")
                top_scores = []
                
                for j, result in enumerate(results, 1):
                    score = result.get('similarity_score', 0)
                    address = result.get('address', 'N/A')
                    price = result.get('price', 0)
                    bedrooms = result.get('bedrooms', 0)
                    bathrooms = result.get('bathrooms', 0)
                    description_text = result.get('description', '')[:100]
                    
                    print(f"      {j}. {address}")
                    print(f"         ${price:,} | {bedrooms}BR/{bathrooms}BA | Score: {score:.4f}")
                    print(f"         Description: {description_text}...")
                    
                    top_scores.append(score)
                
                # Calculate average score for this query
                avg_score = sum(top_scores) / len(top_scores) if top_scores else 0
                results_summary.append({
                    "query": query,
                    "results_count": len(results),
                    "avg_score": avg_score,
                    "top_score": max(top_scores) if top_scores else 0,
                    "status": "success"
                })
                
            else:
                print("   ❌ No results found")
                results_summary.append({
                    "query": query,
                    "results_count": 0,
                    "avg_score": 0,
                    "top_score": 0,
                    "status": "no_results"
                })
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results_summary.append({
                "query": query,
                "results_count": 0,
                "avg_score": 0,
                "top_score": 0,
                "status": "error",
                "error": str(e)
            })
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 SEARCH PERFORMANCE SUMMARY")
    print(f"{'='*60}")
    
    successful_queries = [r for r in results_summary if r['status'] == 'success']
    
    if successful_queries:
        avg_results_per_query = sum(r['results_count'] for r in successful_queries) / len(successful_queries)
        avg_similarity_score = sum(r['avg_score'] for r in successful_queries) / len(successful_queries)
        
        print(f"Successful queries: {len(successful_queries)}/{len(results_summary)}")
        print(f"Average results per query: {avg_results_per_query:.1f}")
        print(f"Average similarity score: {avg_similarity_score:.4f}")
        print(f"Best similarity score: {max(r['top_score'] for r in successful_queries):.4f}")
        
        print(f"\n📋 Query Performance:")
        for result in results_summary:
            status_icon = "✅" if result['status'] == 'success' else "❌"
            print(f"  {status_icon} {result['query'][:40]}...")
            if result['status'] == 'success':
                print(f"      {result['results_count']} results, avg score: {result['avg_score']:.4f}")
            elif result['status'] == 'error':
                print(f"      Error: {result.get('error', 'Unknown')}")
    
    print(f"\n🎉 Vector search testing completed!")

def test_user_criteria_conversion():
    """Test the conversion of user criteria to search queries."""
    
    print(f"\n{'='*60}")
    print("🔧 Testing User Criteria to Search Query Conversion")
    print(f"{'='*60}")
    
    test_criteria = [
        {
            "bedrooms_min": 3,
            "bathrooms_min": 2,
            "price_max": 500000,
            "keywords": ["modern kitchen", "backyard"]
        },
        {
            "bedrooms_min": 2,
            "price_min": 300000,
            "price_max": 450000,
            "keywords": ["downtown", "urban", "walkable"]
        },
        {
            "bedrooms_min": 4,
            "bathrooms_min": 3,
            "price_max": 800000,
            "keywords": ["luxury", "high-end"]
        }
    ]
    
    for i, criteria in enumerate(test_criteria, 1):
        search_query = create_search_query_from_criteria(criteria)
        print(f"\n{i}. Criteria: {criteria}")
        print(f"   Generated Query: '{search_query}'")
        
        # Test the generated query
        embedding = generate_query_embedding(search_query)
        results = vector_similarity_search(embedding, search_query, limit=2)
        
        if results:
            print(f"   Results: {len(results)} listings found")
            for result in results:
                print(f"     - {result.get('address', 'N/A')} (${result.get('price', 0):,})")
        else:
            print("   Results: No listings found")

if __name__ == "__main__":
    test_search_queries()
    test_user_criteria_conversion()
    print("\n🏁 All tests completed!")
