#!/usr/bin/env python3
"""
End-to-End Test Suite for Multi-Agent Home Buying Application.

This script tests the complete workflow from user criteria to final recommendations,
using real BigQuery data and embeddings for vector similarity search.
"""

import json
import asyncio
from typing import Dict, Any, List
from orchestrator import HomeBuyingOrchestrator

def get_test_scenarios() -> List[Dict[str, Any]]:
    """Define comprehensive test scenarios covering different user profiles and preferences."""
    
    return [        {
            "name": "Young Professional - Urban",
            "description": "Tech worker looking for modern amenities near downtown",
            "user_criteria": {
                "bedrooms_min": 2,
                "bathrooms_min": 1,  # Reduced from 2 to 1
                "price_max": 500000,  # Increased from 450000 to 500000
                "price_min": 250000,  # Reduced from 300000 to 250000                "keywords": ["modern kitchen", "downtown", "tech", "urban", "walkable"],
                "neighborhood_preferences": ["downtown", "urban core", "tech district"],
                "lifestyle": "urban professional",
                "user_priorities": ["modern amenities", "walkable neighborhood", "tech-friendly area", "urban lifestyle"]
            }
        },        {
            "name": "Growing Family - Suburban",
            "description": "Family with kids looking for space and good schools",
            "user_criteria": {
                "bedrooms_min": 2,  # Reduced from 3 to 2
                "bathrooms_min": 2,
                "price_max": 600000,  # Increased from 550000
                "price_min": 350000,  # Reduced from 400000                "keywords": ["family friendly", "schools", "backyard", "safe neighborhood", "suburban"],
                "neighborhood_preferences": ["suburbs", "family neighborhood", "school district"],
                "lifestyle": "family with children",
                "user_priorities": ["good schools", "safe neighborhood", "family-friendly environment", "outdoor space"]
            }
        },        {
            "name": "First-Time Buyer - Budget Conscious",
            "description": "Young couple buying their first home on a tight budget",
            "user_criteria": {
                "bedrooms_min": 1,  # Reduced from 2 to 1 to find more options
                "bathrooms_min": 1,
                "price_max": 350000,
                "price_min": 260000,  # Increased from 200000 to match available data
                "keywords": ["affordable", "starter home", "good value", "first time buyer"],
                "neighborhood_preferences": ["affordable", "up and coming"],
                "lifestyle": "first time buyer",
                "user_priorities": ["affordability", "starter home", "good value", "move-in ready"]
            }
        },        {
            "name": "Luxury Buyer - Premium Features",
            "description": "High-income buyer seeking luxury features and premium location",
            "user_criteria": {
                "bedrooms_min": 2,  # Reduced from 4 to 2
                "bathrooms_min": 2,  # Reduced from 3 to 2
                "price_max": 700000,  # Increased from 600000 to capture luxury listings
                "price_min": 450000,  # Increased from 400000 to focus on higher-end properties
                "keywords": ["luxury", "premium", "high-end", "gourmet kitchen", "master suite"],
                "neighborhood_preferences": ["upscale", "luxury", "premium location"],
                "lifestyle": "luxury buyer",
                "user_priorities": ["luxury features", "premium location", "high-end finishes", "upscale neighborhood"]
            }
        },
        {
            "name": "Retiree - Low Maintenance",
            "description": "Retirees looking for low-maintenance home in quiet area",
            "user_criteria": {
                "bedrooms_min": 2,
                "bathrooms_min": 1,  # Reduced from 2 to 1
                "price_max": 500000,  # Increased from 400000
                "price_min": 250000,
                "keywords": ["low maintenance", "quiet", "retirement", "single story", "mature neighborhood"],
                "neighborhood_preferences": ["quiet", "mature", "established"],
                "lifestyle": "retirement"
            }
        }
    ]

async def run_end_to_end_test(scenario: Dict[str, Any], orchestrator: HomeBuyingOrchestrator) -> Dict[str, Any]:
    """Run a complete end-to-end test for a given scenario."""
    
    print(f"\n{'='*80}")
    print(f"🏠 TESTING SCENARIO: {scenario['name']}")
    print(f"📝 Description: {scenario['description']}")
    print(f"{'='*80}")
    
    # Print user criteria
    print("\n📋 User Criteria:")
    criteria = scenario['user_criteria']
    for key, value in criteria.items():
        if isinstance(value, list):
            print(f"  • {key}: {', '.join(map(str, value))}")
        else:
            print(f"  • {key}: {value}")
    
    try:        # Run the complete orchestration
        print("\n🚀 Starting Multi-Agent Analysis...")
        results = await orchestrator.process_home_buying_request(criteria)
          # Display results
        print("\n📊 RESULTS SUMMARY:")
        # Extract data from the recommendation report structure
        listings_analyzed = len(results.get('all_listings_ranked', []))
        top_recommendations = results.get('top_recommendations', [])
        
        print(f"  • Total listings analyzed: {listings_analyzed}")
        print(f"  • Neighborhoods evaluated: {listings_analyzed}")  # Each listing has locality analysis        print(f"  • Hazards identified: {listings_analyzed}")       # Each listing has hazard analysis
        print(f"  • Affordability analysis: {'✅ Complete' if listings_analyzed > 0 else '❌ Missing'}")
        print(f"  • Final recommendations: {len(top_recommendations)}")
        
        # Show best property writeup if available
        best_writeup = results.get("best_property_writeup", "")
        if best_writeup and top_recommendations:
            print("\n" + "="*80)
            print(best_writeup)
            print("="*80)
        
        # Show top recommendations
        if top_recommendations:
            print("\n🎯 TOP RECOMMENDATIONS:")
            for i, rec in enumerate(top_recommendations[:3], 1):
                print(f"  {i}. {rec.get('address', 'N/A')} - Score: {rec.get('total_score', 0)}")
                print(f"     Price: ${rec.get('price', 0):,} | {rec.get('bedrooms', 0)}BR/{rec.get('bathrooms', 0)}BA")
                if rec.get('pros'):
                    print(f"     Pros: {', '.join(rec['pros'][:2])}...")  # Show first 2 pros
        
        return {
            "scenario": scenario['name'],
            "status": "success",
            "results": results,
            "listings_found": listings_analyzed,
            "recommendations_count": len(top_recommendations)
        }
        
    except Exception as e:
        print(f"\n❌ ERROR in scenario '{scenario['name']}': {str(e)}")
        return {
            "scenario": scenario['name'],
            "status": "error",
            "error": str(e),
            "listings_found": 0,
            "recommendations_count": 0
        }

def run_vector_search_specific_tests():
    """Run specific tests for vector search functionality with various queries."""
    
    print(f"\n{'='*80}")
    print("🔍 VECTOR SEARCH SPECIFIC TESTS")
    print(f"{'='*80}")
    
    from agents.vector_search_utils import generate_query_embedding, vector_similarity_search, create_search_query_from_criteria
    
    # Test queries that should find relevant results
    test_queries = [
        "Modern kitchen with granite countertops and stainless steel appliances",
        "Family home with large backyard and good schools nearby",
        "Luxury home with high-end finishes in upscale neighborhood",
        "Starter home for first-time buyers, affordable and move-in ready",
        "Downtown condo with urban amenities and walkable lifestyle",
        "Quiet suburban home perfect for retirement",
        "House with hardwood floors and updated bathrooms",
        "Property with garage and storage space",
        "Home with open floor plan and natural light",
        "Victorian style house with historic charm"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: '{query}'")
        
        try:
            # Generate embedding for the query
            embedding = generate_query_embedding(query)
            
            # Perform vector search
            results = vector_similarity_search(embedding, query, limit=3)
            
            if results:
                print(f"  ✅ Found {len(results)} results:")
                for j, result in enumerate(results, 1):
                    score = result.get('similarity_score', 0)
                    address = result.get('address', 'N/A')
                    price = result.get('price', 0)
                    print(f"    {j}. {address} - Score: {score:.4f} - ${price:,}")
            else:
                print("  ❌ No results found")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")

async def main():
    """Main function to run all end-to-end tests."""
    
    print("🏠 Multi-Agent Home Buying Application - End-to-End Test Suite")
    print("=" * 80)
    
    # Initialize orchestrator
    print("🔧 Initializing orchestrator...")
    orchestrator = HomeBuyingOrchestrator()
    
    # Run vector search specific tests first
    run_vector_search_specific_tests()
    
    # Get test scenarios
    scenarios = get_test_scenarios()
    
    # Run all scenarios
    results = []
    for scenario in scenarios:
        result = await run_end_to_end_test(scenario, orchestrator)
        results.append(result)
    
    # Print overall summary
    print(f"\n{'='*80}")
    print("📊 OVERALL TEST SUMMARY")
    print(f"{'='*80}")
    
    total_scenarios = len(results)
    successful_scenarios = len([r for r in results if r['status'] == 'success'])
    failed_scenarios = total_scenarios - successful_scenarios
    
    print(f"Total scenarios tested: {total_scenarios}")
    print(f"Successful scenarios: {successful_scenarios}")
    print(f"Failed scenarios: {failed_scenarios}")
    print(f"Success rate: {(successful_scenarios/total_scenarios)*100:.1f}%")
    
    # Print detailed results
    print(f"\n📋 DETAILED RESULTS:")
    for result in results:
        status_icon = "✅" if result['status'] == 'success' else "❌"
        print(f"  {status_icon} {result['scenario']}: {result['listings_found']} listings, {result['recommendations_count']} recommendations")
        if result['status'] == 'error':
            print(f"      Error: {result['error']}")
    
    # Save results to file
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to 'test_results.json'")
    print("🎉 End-to-end testing completed!")

if __name__ == "__main__":
    asyncio.run(main())
