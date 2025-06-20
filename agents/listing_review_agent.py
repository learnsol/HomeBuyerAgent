"""
Listing Review Agent - Finds property listings using vector search.
Using official Google ADK patterns.
"""
import os
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from config import settings
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from agents.vector_search_utils import search_listings_by_criteria
from agents.agent_utils import convert_to_json_serializable

# Set up Vertex AI environment variables for Google AI SDK
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
os.environ['GOOGLE_CLOUD_PROJECT'] = settings.VERTEX_AI_PROJECT_ID
os.environ['GOOGLE_CLOUD_LOCATION'] = settings.VERTEX_AI_LOCATION

class ListingSearchInput(BaseModel):
    """Input schema for listing search."""
    user_criteria: Dict[str, Any] = Field(description="User's search criteria for properties")

class ListingSearchOutput(BaseModel):
    """Output schema for listing search results."""
    found_listings: List[Dict[str, Any]] = Field(description="List of property listings found")

def find_listings_by_criteria(user_criteria: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool function to find property listings based on user criteria.
    """
    print(f"🔍 find_listings_by_criteria called with criteria: {user_criteria}")
    
    if not isinstance(user_criteria, dict):
        return {"error": "user_criteria must be a dictionary", "found_listings": []}
    
    try:
        # Use vector search to find matching listings
        results = search_listings_by_criteria(user_criteria, top_k=10)
        
        # Process and format results
        formatted_listings = []
        for i, result in enumerate(results):
            listing = {
                "listing_id": result.get("listing_id", f"listing_{i+1}"),
                "address": result.get("address", "Address not available"),
                "price": result.get("price", 0),
                "bedrooms": result.get("bedrooms", 0),
                "bathrooms": result.get("bathrooms", 0),
                "square_footage": result.get("square_footage", 0),
                "year_built": result.get("year_built", "Unknown"),
                "property_type": result.get("property_type", "House"),
                "description": result.get("description", ""),
                "zip_code": result.get("zip_code", ""),
                "similarity_score": result.get("similarity_score", 0.0)
            }
            formatted_listings.append(listing)
        
        result_data = {
            "found_listings": formatted_listings,
            "total_found": len(formatted_listings),
            "search_criteria": user_criteria
        }
        
        print(f"✅ Found {len(formatted_listings)} listings matching criteria")
        return convert_to_json_serializable(result_data)
        
    except Exception as e:
        error_msg = f"Error finding listings: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "error": error_msg,
            "found_listings": [],
            "search_criteria": user_criteria
        }

def create_listing_review_agent() -> LlmAgent:
    """Create and configure the Listing Review Agent using ADK patterns."""
    return LlmAgent(
        name="ListingReviewAgent",
        model=settings.DEFAULT_AGENT_MODEL,
        description="Finds property listings based on user criteria using semantic vector search",
        instruction="""You are a listing review agent that finds properties matching user criteria.
        
        You receive user search criteria and use the find_listings_by_criteria tool to:
        1. Search for properties using vector similarity search
        2. Filter results based on user requirements
        3. Return a list of matching property listings
        
        The user criteria will be provided in the session state under 'user_criteria'.
        Save your results to session state under 'found_listings'.""",
        tools=[FunctionTool(func=find_listings_by_criteria)],
        input_schema=ListingSearchInput,
        output_key="found_listings"
    )

# Create the agent instance
listing_review_agent = create_listing_review_agent()
