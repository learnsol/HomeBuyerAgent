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
            session_service=self.session_service
        )
    
    async def run_full_analysis(self, user_criteria: Dict[str, Any], user_id: str = "default_user") -> Dict[str, Any]:
        """
        Run the complete home buying analysis workflow.
        """
        session_id = f"home_buying_session_{user_id}"        # Create session
        session = await self.session_service.create_session(
            app_name="home_buyer_app",
            user_id=user_id,
            session_id=session_id
        )
          # Set initial session state        session.state["user_criteria"] = user_criteria
        session.state["user_priorities"] = user_criteria.get("priorities", [])
        session.state["user_financial_info"] = user_criteria.get("user_financial_info", {})
        
        print(f"🏡 Starting Home Buying Analysis Workflow")
        print(f"   User ID: {user_id}")
        print(f"   Session ID: {session_id}")
        print(f"   Criteria: {user_criteria}")
        
        try:
            # Step 1: Find listings
            print(f"\\n🔍 Step 1: Finding property listings...")
            user_content = types.Content(
                role='user', 
                parts=[types.Part(text=json.dumps(user_criteria))]
            )
            
            # Run the listing review agent
            listing_response = None
            async for event in self.listing_runner.run_async(
                user_id=user_id,                session_id=session_id,
                new_message=user_content
            ):
                if event.is_final_response():
                    print(f"   ✅ Listing search completed")
                    break

            # Since the agent uses function tools, check for results in session state
            found_listings = session.state.get("found_listings", [])
            
            # If not found in session, try calling the function directly as fallback
            if not found_listings:
                print(f"   🔍 No listings in session, calling function directly...")
                try:
                    from agents.listing_review_agent import find_listings_by_criteria
                    search_criteria = user_criteria.get("search_criteria", {})
                    function_result = find_listings_by_criteria(search_criteria)
                    if isinstance(function_result, dict) and "found_listings" in function_result:
                        found_listings = function_result["found_listings"]
                        session.state["found_listings"] = found_listings
                        print(f"   📋 Direct function call found {len(found_listings)} listings")
                except Exception as e:                    print(f"   ⚠️ Direct function call failed: {e}")
            else:
                print(f"   📋 Found {len(found_listings)} listings from session state")
            
            if not found_listings:
                return {
                    "error": "No listings found matching criteria",
                    "user_criteria": user_criteria,
                    "results": []
                }
            
            print(f"   📋 Found {len(found_listings)} listings to analyze")
            
            # Step 2: Analyze each listing
            print(f"\\n🔬 Step 2: Analyzing properties...")
            aggregated_results = {}
            
            for i, listing in enumerate(found_listings):
                listing_id = listing.get("listing_id", f"listing_{i}")
                print(f"   🏠 Analyzing {listing_id}...")
                
                # Set current listing in session state
                session.state["current_listing"] = listing
                session.state["listing_details"] = listing
                
                # Run parallel analysis
                analysis_content = types.Content(
                    role='user',
                    parts=[types.Part(text=json.dumps(listing))]
                )
                
                async for event in self.parallel_runner.run_async(
                    user_id=user_id,
                    session_id=session_id,
                    new_message=analysis_content
                ):
                    if event.is_final_response():
                        break                # Collect analysis results
                aggregated_results[listing_id] = {
                    "listing_details": listing,
                    "locality_analysis": session.state.get("locality_analysis", {}),
                    "hazard_analysis": session.state.get("hazard_analysis", {}),
                    "affordability_analysis": session.state.get("affordability_analysis", {})
                }
                
                print(f"     ✅ Analysis completed for {listing_id}")
              # Step 3: Generate recommendations
            print(f"\\n📊 Step 3: Generating recommendations...")
            session.state["aggregated_analysis"] = aggregated_results
            
            recommendation_content = types.Content(
                role='user',
                parts=[types.Part(text=json.dumps({
                    "aggregated_data": aggregated_results,
                    "user_priorities": user_criteria.get("priorities", [])
                }))]
            )
            
            async for event in self.recommendation_runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=recommendation_content
            ):
                if event.is_final_response():
                    print(f"   ✅ Recommendations generated")
                    break
            
            # Get final results
            final_recommendations = session.state.get("final_recommendations", {})
            
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
