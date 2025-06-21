"""
ADK-Compliant Home Buyer Orchestrator using official Google ADK patterns.
Uses Runner and proper session management.
"""
import json
from typing import Dict, List, Any
from google.adk.agents import SequentialAgent, ParallelAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agents.listing_review_agent import create_listing_review_agent
from agents.locality_review_agent import create_locality_review_agent
from agents.hazard_analysis_agent import create_hazard_analysis_agent
from agents.affordability_agent import create_affordability_agent
from agents.recommendation_agent import create_recommendation_agent
from config import settings
from typing import Dict, Any, List
import asyncio
import json

class ADKHomeBuyingOrchestrator:
    """
    Main orchestrator that coordinates the home buying analysis workflow using Google ADK.
    """
    
    def __init__(self):
        # Create session service
        self.session_service = InMemorySessionService()        # Create individual agents using factory functions
        self.listing_agent = create_listing_review_agent()
        self.locality_agent = create_locality_review_agent()
        self.hazard_agent = create_hazard_analysis_agent()
        self.affordability_agent = create_affordability_agent()
        self.recommendation_agent = create_recommendation_agent()
        
        # Create parallel analysis agent for concurrent property analysis
        self.parallel_analyzer = ParallelAgent(
            name="PropertyAnalyzer",
            description="Analyzes properties using locality, hazard, and affordability agents in parallel",
            sub_agents=[self.locality_agent, self.hazard_agent, self.affordability_agent]
        )
        
        # Create sequential workflow agent
        self.workflow_agent = SequentialAgent(
            name="HomeBuyingWorkflow",
            description="Complete home buying analysis workflow",
            sub_agents=[self.listing_agent, self.parallel_analyzer, self.recommendation_agent]
        )
        
        # Create runners
        self.listing_runner = Runner(
            agent=self.listing_agent,
            app_name="home_buyer_app",
            session_service=self.session_service
        )
        
        self.parallel_runner = Runner(
            agent=self.parallel_analyzer,
            app_name="home_buyer_app", 
            session_service=self.session_service
        )
        
        self.recommendation_runner = Runner(
            agent=self.recommendation_agent,
            app_name="home_buyer_app",
            session_service=self.session_service
        )
        
        self.workflow_runner = Runner(
            agent=self.workflow_agent,
            app_name="home_buyer_app",
            session_service=self.session_service        )
    
    async def run_full_analysis(self, user_criteria: Dict[str, Any], user_id: str = "default_user") -> Dict[str, Any]:
        """
        Run the complete home buying analysis workflow.
        """
        session_id = f"home_buying_session_{user_id}"
        
        print(f"🏡 Starting Home Buying Analysis Workflow")
        print(f"   User ID: {user_id}")
        print(f"   Session ID: {session_id}")
        print(f"   Criteria: {user_criteria}")

        try:
            # Step 1: Find listings using direct function call (bypassing ADK for now)
            print(f"\\n🔍 Step 1: Finding property listings...")
            
            from agents.listing_review_agent import find_listings_by_criteria
            search_criteria = user_criteria.get("search_criteria", {})
            listing_result = find_listings_by_criteria(search_criteria)
            
            if "error" in listing_result:
                return {
                    "error": listing_result["error"],
                    "user_criteria": user_criteria,
                    "results": []
                }
            
            found_listings = listing_result.get("found_listings", [])
            print(f"   📋 Found {len(found_listings)} listings to analyze")
            
            if not found_listings:
                return {
                    "error": "No listings found matching criteria",
                    "user_criteria": user_criteria,
                    "results": []
                }

            # Step 2: Analyze each listing using direct function calls
            print(f"\\n🔬 Step 2: Analyzing properties...")
            aggregated_results = {}
            
            user_financial_info = user_criteria.get("user_financial_info", {})
            
            for i, listing in enumerate(found_listings):
                listing_id = listing.get("listing_id", f"listing_{i}")
                print(f"   🏠 Analyzing {listing_id}...")
                  # Import and call each analysis function directly
                from agents.affordability_agent import analyze_affordability
                from agents.locality_review_agent import analyze_neighborhood_features
                from agents.hazard_analysis_agent import analyze_property_hazards
                
                # Run affordability analysis
                affordability_analysis = analyze_affordability(listing, user_financial_info)
                
                # Run locality analysis  
                locality_analysis = analyze_neighborhood_features(listing)
                
                # Run hazard analysis
                hazard_analysis = analyze_property_hazards(listing)
                
                # Collect analysis results
                aggregated_results[listing_id] = {
                    "listing_details": listing,
                    "locality_analysis": locality_analysis,
                    "hazard_analysis": hazard_analysis,
                    "affordability_analysis": affordability_analysis
                }
                
                print(f"     ✅ Analysis completed for {listing_id}")
            
            # Step 3: Generate recommendations using direct function call
            print(f"\\n📊 Step 3: Generating recommendations...")
            
            from agents.recommendation_agent import generate_recommendation_report
            user_priorities = user_criteria.get("priorities", [])
            
            final_recommendations = generate_recommendation_report(aggregated_results, user_priorities)
            
            print(f"\\n🎯 Analysis Complete!")
            if isinstance(final_recommendations, dict) and "ranked_listings" in final_recommendations:
                ranked_count = len(final_recommendations["ranked_listings"])
                print(f"   📋 {ranked_count} properties ranked and analyzed")
                
                if ranked_count > 0:
                    top_property = final_recommendations["ranked_listings"][0]
                    print(f"   🏆 Top recommendation: {top_property.get('listing_id', 'Unknown')} (Score: {top_property.get('overall_score', 0)})")
            
            return {
                "user_criteria": user_criteria,
                "found_listings": found_listings,
                "analysis_results": aggregated_results,
                "recommendations": final_recommendations,
                "session_id": session_id,
                "analysis_completed": True
            }
            
        except Exception as e:
            error_msg = f"Error in analysis workflow: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "error": error_msg,
                "user_criteria": user_criteria,
                "analysis_completed": False
            }

def create_adk_home_buying_orchestrator() -> ADKHomeBuyingOrchestrator:
    """Create and configure the ADK Home Buying Orchestrator."""
    return ADKHomeBuyingOrchestrator()

# Create the orchestrator instance
home_buying_orchestrator = create_adk_home_buying_orchestrator()
