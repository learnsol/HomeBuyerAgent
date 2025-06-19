"""
Listing Review Agent - Finds property listings using vector search.
Following ADK patterns with FunctionTool and LlmAgent.
"""
from agents.base_agent import HomeBuyerBaseAgent
from mock_adk import LlmAgent, FunctionTool, InvocationContext
from agents.vector_search_utils import (
    create_search_query_from_criteria,
    generate_query_embedding,
    vector_similarity_search
)
from agents.agent_utils import convert_to_json_serializable
from config import settings
from typing import Dict, Any, List
import json

def find_listings_by_criteria(user_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Tool function to find property listings based on user criteria.
    Uses vector search for semantic matching.
    """
    print(f"🔍 find_listings_by_criteria called with: {user_criteria}")
    
    if not isinstance(user_criteria, dict):
        return {"error": "user_criteria must be a dictionary"}

    try:
        # Create search query from criteria
        search_query = create_search_query_from_criteria(user_criteria)
        print(f"Generated search query: {search_query}")
          # Generate embedding for search
        query_embedding = generate_query_embedding(search_query)
        print(f"Generated {len(query_embedding)}D embedding")
        
        # Perform vector similarity search
        similar_listings = vector_similarity_search(query_embedding, search_query, limit=settings.VECTOR_SEARCH_LIMIT)
        
        # Apply additional filters
        filtered_listings = _apply_filters(similar_listings, user_criteria)
        
        print(f"Found {len(filtered_listings)} matching listings")
        return convert_to_json_serializable(filtered_listings)
        
    except Exception as e:
        print(f"Error in find_listings_by_criteria: {e}")
        return {"error": f"Search failed: {str(e)}"}

def _apply_filters(listings: List[Dict[str, Any]], user_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Apply price, bedroom, bathroom filters to search results using actual schema."""
    filtered = []
    
    print(f"🔍 Filtering {len(listings)} listings with criteria: {user_criteria}")
    
    for i, listing in enumerate(listings):
        print(f"🏠 Listing {i+1}: {listing.get('address', 'N/A')} - Price: ${listing.get('price', 0):,}, Bedrooms: {listing.get('bedrooms', 0)}, Bathrooms: {listing.get('bathrooms', 0)}")
        
        # Price filters
        if "price_min" in user_criteria and listing.get('price', 0) < user_criteria['price_min']:
            print(f"  ❌ Rejected: Price ${listing.get('price', 0):,} < ${user_criteria['price_min']:,}")
            continue
        if "price_max" in user_criteria and listing.get('price', 0) > user_criteria['price_max']:
            print(f"  ❌ Rejected: Price ${listing.get('price', 0):,} > ${user_criteria['price_max']:,}")
            continue
        
        # Bedroom filter
        if "bedrooms_min" in user_criteria and listing.get('bedrooms', 0) < user_criteria['bedrooms_min']:
            print(f"  ❌ Rejected: Bedrooms {listing.get('bedrooms', 0)} < {user_criteria['bedrooms_min']}")
            continue
        
        # Bathroom filter
        if "bathrooms_min" in user_criteria and listing.get('bathrooms', 0) < user_criteria['bathrooms_min']:
            print(f"  ❌ Rejected: Bathrooms {listing.get('bathrooms', 0)} < {user_criteria['bathrooms_min']}")
            continue        
        # Property type filter
        if "property_type" in user_criteria:
            if listing.get('property_type', '').lower() != user_criteria['property_type'].lower():
                print(f"  ❌ Rejected: Property type '{listing.get('property_type', '')}' != '{user_criteria['property_type']}'")
                continue
        
        print(f"  ✅ Accepted: {listing.get('address', 'N/A')}")
        filtered.append(listing)
    
    print(f"🔍 Filter result: {len(filtered)} out of {len(listings)} listings passed filters")
    return filtered

class ListingReviewAgent(HomeBuyerBaseAgent):
    """Agent for finding property listings using vector search."""
    
    def __init__(self):
        super().__init__(
            name="ListingReviewAgent", 
            description="Finds property listings based on user criteria using semantic vector search"
        )
          # Create the LLM agent with the tool
        self.llm_agent = LlmAgent(
            name="ListingReviewLLM",
            model=settings.DEFAULT_AGENT_MODEL,
            description="LLM agent for listing review",
            instruction="""You are a listing review agent. Use the find_listings_by_criteria tool 
            to search for properties that match the user's requirements from session state 'user_criteria'.
            Save the results to session state under 'found_listings'.""",
            tools=[FunctionTool(func=find_listings_by_criteria)],
            output_key="found_listings"  # Automatically saves LLM output to session state
        )

    async def _run_async_impl(self, ctx: InvocationContext):
        """Execute using ADK pattern - delegate to LLM agent."""
        self._log("Processing listing search request using ADK patterns")
        
        # Debug: Check what's in session state
        print(f"🔍 Session state keys: {list(ctx.session.state.keys())}")
        print(f"🔍 user_criteria: {ctx.session.state.get('user_criteria', 'NOT FOUND')}")
        
        # Check if user_criteria exists, use direct tool call if LLM agent fails
        user_criteria = ctx.session.state.get("user_criteria", {})
        if user_criteria:
            self._log(f"Found user criteria: {user_criteria}")
            # Use direct tool call for now
            result = find_listings_by_criteria(user_criteria)
            ctx.session.state["found_listings"] = result
            
            # Yield result as event
            from mock_adk import Event
            yield Event(author=self.name, content=f"Found {len(result) if isinstance(result, list) else 0} listings")
        else:
            self._log("No user criteria found in session state")
            # Still try the LLM agent approach
            async for event in self.llm_agent.run_stream_async("", ctx):
                yield event

    async def process_business_logic(self, ctx: InvocationContext) -> List[Dict[str, Any]]:
        """Legacy method for backward compatibility."""
        self._log("Processing listing search request")
        
        # Get user criteria from context state
        user_criteria = ctx.session.state.get("user_criteria", {})
        if not user_criteria:
            return {"error": "No user criteria provided"}
        
        # Use the tool directly
        result = find_listings_by_criteria(user_criteria)
        
        # Store in session state for other agents
        ctx.session.state["found_listings"] = result
        
        return result
        
        # Call the tool directly for now (in real ADK, the LLM would decide when to call it)
        result = find_listings_by_criteria(user_criteria)
        
        # Store result in session state
        ctx.session.state["found_listings"] = result
        
        return result

def create_listing_review_agent() -> ListingReviewAgent:
    """Factory function to create a ListingReviewAgent."""
    return ListingReviewAgent()
