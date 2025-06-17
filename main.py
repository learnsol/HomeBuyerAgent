"""
Main entry point for the ADK Home Buyer Multi-Agent Application.
Demonstrates the complete workflow using official ADK patterns.
"""
import asyncio
import json
from orchestrator_adk import create_adk_home_buying_orchestrator
from config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    """Main function to run the ADK home buying application."""
    logger.info("🏡 Starting ADK Home Buyer Multi-Agent Application")
    logger.info(f"Using BigQuery Project: {settings.BIGQUERY_PROJECT_ID}")
    logger.info(f"Models: Default={settings.DEFAULT_AGENT_MODEL}, Orchestrator={settings.ORCHESTRATOR_MODEL}")
    
    # Create the ADK-compliant orchestrator
    orchestrator = create_adk_home_buying_orchestrator()
    
    # Example user request following ADK patterns
    user_request = {
        "search_criteria": {
            "price_max": 750000,
            "price_min": 300000,
            "bedrooms_min": 3,
            "bathrooms_min": 2,
            "keywords": ["modern kitchen", "large backyard", "good school district"]
        },
        "user_financial_info": {
            "annual_income": 120000,
            "down_payment_percentage": 20,
            "monthly_debts": 800
        },
        "priorities": ["good school district", "safety", "large backyard", "modern kitchen"]
    }
    
    logger.info("🎯 Processing user request...")
    logger.info(f"Search criteria: {user_request['search_criteria']}")
    logger.info(f"Financial info: {user_request['user_financial_info']}")
    logger.info(f"Priorities: {user_request['priorities']}")
    
    try:
        # Process the request through the multi-agent workflow
        final_result = await orchestrator.process_home_buying_request(user_request)
        
        # Display results
        print("\n" + "="*80)
        print("🏆 FINAL HOME BUYING RECOMMENDATIONS")
        print("="*80)
        
        if final_result.get("error"):
            logger.error(f"❌ Workflow error: {final_result['error']}")
            return
        
        # Pretty print the recommendations
        print(json.dumps(final_result, indent=2))
        
        # Summary for user
        if "top_recommendations" in final_result:
            print(f"\n📊 SUMMARY:")
            print(f"Total listings analyzed: {len(final_result.get('all_listings_ranked', []))}")
            print(f"Top recommendations: {len(final_result['top_recommendations'])}")
            
            for i, rec in enumerate(final_result['top_recommendations'], 1):
                print(f"\n🏠 #{i} Recommendation - {rec['address']}")
                print(f"   💰 Price: ${rec['price']:,} | Score: {rec['total_score']}")
                print(f"   🏡 {rec['bedrooms']} bed, {rec['bathrooms']} bath")
                print(f"   ✅ Pros: {', '.join(rec['pros'][:3])}")
                if rec['cons']:
                    print(f"   ⚠️  Considerations: {', '.join(rec['cons'][:2])}")
        
        logger.info("✅ Home buying workflow completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Application error: {e}", exc_info=True)

def run_demo():
    """Run a demo of the application with sample data."""
    print("🏡 Home Buyer Multi-Agent Application Demo")
    print("Using mock data for demonstration purposes")
    print("-" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Application interrupted by user")
    except Exception as e:
        logger.critical(f"💥 Critical application error: {e}", exc_info=True)

if __name__ == "__main__":
    run_demo()
