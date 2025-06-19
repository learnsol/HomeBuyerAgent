"""
ADK-Compliant Home Buyer Orchestrator - Follows official ADK multi-agent patterns.
Implements Sequential Pipeline and Parallel Fan-Out/Gather patterns using proper ADK workflow agents.
"""
from mock_adk import (
    SequentialAgent, ParallelAgent, LlmAgent, BaseAgent, 
    InvocationContext, Event, EventActions, FunctionTool
)
from agents.listing_review_agent import create_listing_review_agent
from agents.locality_review_agent import create_locality_review_agent
from agents.hazard_analysis_agent import create_hazard_analysis_agent
from agents.affordability_agent import create_affordability_agent
from agents.recommendation_agent import create_recommendation_agent
from config import settings
from typing import Dict, Any, AsyncGenerator
import asyncio

class ListingAnalyzer(BaseAgent):
    """Custom agent that analyzes a single listing using parallel sub-agents."""
    
    def __init__(self):
        # Create analysis agents
        locality_agent = create_locality_review_agent()
        hazard_agent = create_hazard_analysis_agent()
        affordability_agent = create_affordability_agent()
        
        # Create parallel agent for concurrent analysis
        parallel_analyzer = ParallelAgent(
            name="ParallelListingAnalyzer",
            description="Analyzes a single listing using locality, hazard, and affordability agents",
            sub_agents=[locality_agent, hazard_agent, affordability_agent]
        )
        
        super().__init__(
            name="ListingAnalyzer",
            description="Analyzes individual listings by coordinating parallel analysis agents",
            sub_agents=[parallel_analyzer]
        )
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """Analyze the current listing set in session state."""
        listing_id = ctx.session.state.get("current_listing_id")
        if not listing_id:
            yield Event(author=self.name, content="Error: No current_listing_id in session state")
            return
        
        yield Event(author=self.name, content=f"Starting analysis of listing {listing_id}")
        
        # Execute the parallel analysis
        async for event in self.sub_agents[0].run_stream_async("", ctx):
            yield event
        
        yield Event(author=self.name, content=f"Completed analysis of listing {listing_id}")

class HomeBuyingWorkflow(SequentialAgent):
    """Main workflow agent following ADK Sequential Pipeline pattern."""
    
    def __init__(self):
        # Create specialized agents
        listing_agent = create_listing_review_agent()
        listing_analyzer = ListingAnalyzer()
        recommendation_agent = create_recommendation_agent()
        
        super().__init__(
            name="HomeBuyingWorkflow",
            description="Complete home buying workflow: find listings, analyze each, generate recommendations",
            sub_agents=[listing_agent, listing_analyzer, recommendation_agent]
        )

class MultiListingProcessor(BaseAgent):
    """Processes multiple listings by iterating through them."""
    
    def __init__(self):
        self.listing_analyzer = ListingAnalyzer()
        super().__init__(
            name="MultiListingProcessor",
            description="Processes multiple listings sequentially",
            sub_agents=[self.listing_analyzer]
        )
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """Process each listing found in session state."""
        found_listings = ctx.session.state.get("found_listings", [])
        
        if not found_listings or not isinstance(found_listings, list):
            yield Event(author=self.name, content="Error: No valid listings found to analyze")
            return
        
        yield Event(author=self.name, content=f"Processing {len(found_listings)} listings")
        
        # Initialize aggregated data storage
        aggregated_data = {}
        
        for listing in found_listings:
            listing_id = listing.get("listing_id")
            if not listing_id:
                continue
            
            yield Event(author=self.name, content=f"Processing listing {listing_id}")
            
            # Set current listing context
            ctx.session.state["current_listing_id"] = listing_id
            
            # Initialize listing data
            aggregated_data[listing_id] = {
                "listing_details": listing,
                "locality_analysis": {},
                "hazard_analysis": {},
                "affordability_analysis": {}
            }
            
            # Analyze this listing
            async for event in self.listing_analyzer.run_stream_async("", ctx):
                yield event
            
            # Collect results from session state
            aggregated_data[listing_id]["locality_analysis"] = ctx.session.state.get("locality_analysis", {})
            aggregated_data[listing_id]["hazard_analysis"] = ctx.session.state.get("hazard_analysis", {})
            aggregated_data[listing_id]["affordability_analysis"] = ctx.session.state.get("affordability_analysis", {})
        
        # Store aggregated results
        ctx.session.state["aggregated_analysis_data"] = aggregated_data
        yield Event(author=self.name, content="Completed processing all listings")

class ADKHomeBuyingOrchestrator(SequentialAgent):
    """
    ADK-compliant orchestrator using proper workflow agents and session state communication.
    Follows Sequential Pipeline with embedded Parallel Fan-Out/Gather pattern.
    """
    
    def __init__(self):
        # Create the workflow agents
        listing_agent = create_listing_review_agent()
        multi_listing_processor = MultiListingProcessor()
        recommendation_agent = create_recommendation_agent()
        
        super().__init__(
            name="ADKHomeBuyingOrchestrator",
            description="Complete ADK-compliant home buying workflow with proper agent composition",
            sub_agents=[listing_agent, multi_listing_processor, recommendation_agent]
        )
        
        print("🏠 ADKHomeBuyingOrchestrator initialized with proper ADK workflow patterns")

    async def process_home_buying_request(self, user_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a home buying request using ADK workflow patterns.
        
        Args:
            user_criteria: Dictionary containing user search criteria and financial info
            
        Returns:
            Dictionary containing final recommendations
        """
        print(f"🚀 Starting ADK home buying workflow for criteria: {user_criteria}")
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
            priorities = []
        
        ctx.session.state.update({
            "user_criteria": search_criteria,
            "user_financial_info": financial_info,
            "user_priorities": priorities
        })
        
        try:
            # Execute the main workflow using ADK patterns
            final_result = {}
            async for event in self.run_stream_async("", ctx):
                print(f"[{event.author}]: {event.content}")
                if event.author == "RecommendationAgent" and isinstance(event.content, dict):
                    final_result = event.content
            
            # Get final recommendations from session state if not captured in events
            if not final_result:
                final_result = ctx.session.state.get("final_recommendations", {})
            
            return final_result
            
        except Exception as e:
            print(f"❌ Error in ADK home buying workflow: {e}")
            return {"error": f"Workflow failed: {str(e)}"}

def create_adk_home_buying_orchestrator() -> ADKHomeBuyingOrchestrator:
    """Factory function to create an ADK-compliant HomeBuyingOrchestrator."""
    return ADKHomeBuyingOrchestrator()

# Example usage following ADK patterns
async def example_usage():
    """Example of how to use the ADK-compliant orchestrator."""
    orchestrator = create_adk_home_buying_orchestrator()
    
    user_criteria = {
        "search_criteria": {
            "price_max": 500000,
            "bedrooms_min": 3,
            "bathrooms_min": 2,
            "keywords": ["family-friendly", "good schools", "safe neighborhood"]
        },
        "user_financial_info": {
            "annual_income": 80000,
            "down_payment": 50000,
            "debt_to_income_ratio": 0.3
        },
        "priorities": ["school_rating", "safety", "commute_time"]
    }
    
    result = await orchestrator.process_home_buying_request(user_criteria)
    print(f"Final recommendations: {result}")

if __name__ == "__main__":
    asyncio.run(example_usage())
