"""
Home Buyer Orchestrator - Coordinates the multi-agent workflow using ADK patterns.
Implements Sequential Pipeline and Parallel Fan-Out/Gather patterns.
"""
from mock_adk import SequentialAgent, ParallelAgent, LlmAgent, AgentTool, InvocationContext
from agents.listing_review_agent import create_listing_review_agent
from agents.locality_review_agent import create_locality_review_agent
from agents.hazard_analysis_agent import create_hazard_analysis_agent
from agents.affordability_agent import create_affordability_agent
from agents.recommendation_agent import create_recommendation_agent
from config import settings
from typing import Dict, Any
import asyncio

class HomeBuyingOrchestrator:
    """
    Main orchestrator for the home buying workflow.
    Follows ADK Sequential Pipeline and Parallel Fan-Out/Gather patterns.
    """
    
    def __init__(self):
        self._setup_agents()
        self._setup_workflow()
        print("🏠 HomeBuyingOrchestrator initialized with ADK workflow patterns")

    def _setup_agents(self):
        """Create all specialized agents."""
        self.listing_agent = create_listing_review_agent()
        self.locality_agent = create_locality_review_agent()
        self.hazard_agent = create_hazard_analysis_agent()
        self.affordability_agent = create_affordability_agent()
        self.recommendation_agent = create_recommendation_agent()

    def _setup_workflow(self):
        """Setup the ADK workflow using Sequential and Parallel agents."""
        
        # Create parallel agent for concurrent analysis
        self.parallel_analysis_agent = ParallelAgent(
            name="ParallelAnalysisAgent",
            description="Runs locality, hazard, and affordability analysis concurrently",
            sub_agents=[
                self.locality_agent,
                self.hazard_agent,
                self.affordability_agent
            ]
        )
        
        # Create sequential workflow
        self.main_workflow = SequentialAgent(
            name="HomeBuyingWorkflow",
            description="Main sequential workflow for home buying process",
            sub_agents=[
                self.listing_agent,
                self.parallel_analysis_agent,
                self.recommendation_agent
            ]
        )

    async def process_home_buying_request(self, user_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a complete home buying request through the multi-agent workflow.
        
        Args:
            user_criteria: Dictionary containing user search criteria and financial info
            
        Returns:
            Dictionary containing final recommendations
        """
        print(f"🚀 Starting home buying workflow for criteria: {user_criteria}")
          # Create invocation context with user criteria
        ctx = InvocationContext()
          # Handle both nested and direct criteria formats
        if "search_criteria" in user_criteria:
            # Nested format from the example
            search_criteria = user_criteria.get("search_criteria", {})
            financial_info = user_criteria.get("user_financial_info", {})
            priorities = user_criteria.get("priorities", [])
        else:
            # Direct format from test scenarios
            search_criteria = user_criteria
            financial_info = {}
            priorities = user_criteria.get("user_priorities", [])
        
        ctx.session.state.update({
            "user_criteria": search_criteria,
            "user_financial_info": financial_info,
            "user_priorities": priorities
        })
        
        try:
            # Execute the main workflow
            final_result = await self._execute_workflow(ctx)
            return final_result
            
        except Exception as e:
            print(f"❌ Error in home buying workflow: {e}")
            return {"error": f"Workflow failed: {str(e)}"}

    async def _execute_workflow(self, ctx: InvocationContext) -> Dict[str, Any]:
        """Execute the multi-agent workflow with proper data flow."""
        
        # Step 1: Find listings using ListingReviewAgent
        print("📋 Step 1: Finding property listings...")
        listings_result = await self.listing_agent.process_business_logic(ctx)
        
        if isinstance(listings_result, dict) and listings_result.get("error"):
            return listings_result
        
        if not listings_result or not isinstance(listings_result, list):
            return {"error": "No listings found or invalid listing data"}
        
        print(f"✅ Found {len(listings_result)} listings")
        
        # Step 2: Analyze each listing in parallel using the ParallelAnalysisAgent
        print("🔍 Step 2: Analyzing listings (locality, hazards, affordability)...")
        aggregated_data = {}
        
        for listing in listings_result:
            listing_id = listing.get("listing_id")
            if not listing_id:
                continue
                
            # Set current listing context
            ctx.session.state["current_listing_id"] = listing_id
            
            # Store listing details for later use
            aggregated_data[listing_id] = {
                "listing_details": listing,
                "locality_analysis": {},
                "hazard_analysis": {},
                "affordability_analysis": {}
            }
            
            # Run parallel analysis for this listing
            await self._analyze_single_listing(ctx, listing_id, aggregated_data)        # Step 3: Generate final recommendations
        print("🎯 Step 3: Generating final recommendations...")
        ctx.session.state["aggregated_analysis_data"] = aggregated_data
        
        final_recommendations = await self.recommendation_agent.process_business_logic(ctx)
        
        print("✅ Home buying workflow completed successfully")
        return final_recommendations

    async def _analyze_single_listing(self, ctx: InvocationContext, listing_id: str, aggregated_data: Dict[str, Any]):
        """Analyze a single listing using parallel agents."""
        print(f"  🔍 Analyzing listing {listing_id}...")
        
        # Create tasks for parallel execution
        tasks = [
            self.locality_agent.process_business_logic(ctx),
            self.hazard_agent.process_business_logic(ctx),
            self.affordability_agent.process_business_logic(ctx)
        ]
        
        # Execute analysis tasks concurrently
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Store results in aggregated data
            locality_result, hazard_result, affordability_result = results
            
            aggregated_data[listing_id]["locality_analysis"] = locality_result if not isinstance(locality_result, Exception) else {"error": str(locality_result)}
            aggregated_data[listing_id]["hazard_analysis"] = hazard_result if not isinstance(hazard_result, Exception) else {"error": str(hazard_result)}
            aggregated_data[listing_id]["affordability_analysis"] = affordability_result if not isinstance(affordability_result, Exception) else {"error": str(affordability_result)}
            
            print(f"  ✅ Analysis completed for listing {listing_id}")
            
        except Exception as e:
            print(f"  ❌ Error analyzing listing {listing_id}: {e}")
            aggregated_data[listing_id].update({
                "locality_analysis": {"error": f"Analysis failed: {str(e)}"},
                "hazard_analysis": {"error": f"Analysis failed: {str(e)}"},
                "affordability_analysis": {"error": f"Analysis failed: {str(e)}"}
            })

def create_home_buying_orchestrator() -> HomeBuyingOrchestrator:
    """Factory function to create a HomeBuyingOrchestrator."""
    return HomeBuyingOrchestrator()
