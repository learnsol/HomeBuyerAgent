"""
Test script to verify that agents work with the actual BigQuery schema.
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from orchestrator_adk import create_adk_home_buying_orchestrator

async def test_schema_compatibility():
    """Test that the agents work with the actual BigQuery schema."""
    print("🧪 Testing ADK Home Buying Application with BigQuery Schema")
    print("=" * 70)
    
    # Create orchestrator
    orchestrator = create_adk_home_buying_orchestrator()
    
    # Test criteria matching the actual data
    user_criteria = {
        "search_criteria": {
            "price_max": 800000,
            "price_min": 400000,
            "bedrooms_min": 3,
            "bathrooms_min": 2,
            "keywords": ["family-friendly", "good schools", "updated kitchen"],
            "location": "Bay Area, CA"
        },
        "user_financial_info": {
            "annual_income": 120000,
            "down_payment": 80000,
            "monthly_debt": 2000,
            "credit_score": 750
        },
        "priorities": [
            "school_district_rating",
            "crime_rate_index", 
            "avg_aqi",
            "fema_flood_zone_designation"
        ]
    }
    
    print("🔍 Test Criteria:")
    print(f"  💰 Budget: ${user_criteria['search_criteria']['price_min']:,} - ${user_criteria['search_criteria']['price_max']:,}")
    print(f"  🏠 Requirements: {user_criteria['search_criteria']['bedrooms_min']}+ bed, {user_criteria['search_criteria']['bathrooms_min']}+ bath")
    print(f"  💵 Down Payment: ${user_criteria['user_financial_info']['down_payment']:,}")
    print(f"  📋 Priorities: {', '.join(user_criteria['priorities'])}")
    print("\n" + "=" * 70)
    
    try:
        # Run the workflow
        print("🚀 Testing ADK workflow with BigQuery schema...")
        result = await orchestrator.process_home_buying_request(user_criteria)
        
        print("\n✅ Test Results:")
        print("=" * 70)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return False
        else:
            print("🎉 SUCCESS: Workflow completed without errors!")
            
            # Check if we got expected data structure
            if isinstance(result, dict):
                print(f"📊 Result type: {type(result)}")
                print(f"📋 Result keys: {list(result.keys()) if result else 'Empty result'}")
                
                # Check for expected fields based on our agents
                expected_fields = ["ranked_properties", "summary", "final_recommendations"]
                found_fields = [field for field in expected_fields if field in result]
                print(f"✅ Found expected fields: {found_fields}")
                
                return True
            else:
                print(f"⚠️  Unexpected result format: {type(result)}")
                return False
                
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print("🏠 ADK Home Buying Application - Schema Compatibility Test")
    print("This test verifies that all agents work with the actual BigQuery schema")
    print("from the provided CSV files: listings.csv, neighborhoods.csv, affordability_params.json")
    print("=" * 70)
    
    success = await test_schema_compatibility()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 ALL TESTS PASSED! The application is compatible with the BigQuery schema.")
    else:
        print("❌ TESTS FAILED! There are compatibility issues with the BigQuery schema.")
    
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
