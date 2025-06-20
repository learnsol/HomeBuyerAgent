"""
Locality Review Agent - Analyzes neighborhood characteristics and amenities.
Using official Google ADK patterns.
"""
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from config import settings
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from agents.vector_search_utils import search_neighborhood_data
from agents.agent_utils import convert_to_json_serializable
import os

# Set up Vertex AI environment variables for Google AI SDK
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
os.environ['GOOGLE_CLOUD_PROJECT'] = settings.VERTEX_AI_PROJECT_ID
os.environ['GOOGLE_CLOUD_LOCATION'] = settings.VERTEX_AI_LOCATION

class LocalityReviewInput(BaseModel):
    """Input schema for locality review."""
    listing_details: Dict[str, Any] = Field(description="Property listing details to analyze")

def analyze_neighborhood_features(listing_details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool function to analyze neighborhood characteristics and amenities.
    """
    print(f"🏘️ analyze_neighborhood_features called for listing: {listing_details.get('listing_id', 'Unknown')}")
    
    if not isinstance(listing_details, dict):
        return {"error": "listing_details must be a dictionary"}
    
    try:
        listing_id = listing_details.get("listing_id", "unknown")
        address = listing_details.get("address", "")
        zip_code = listing_details.get("zip_code", "")
        
        # Search for neighborhood data using vector search
        neighborhood_query = f"neighborhood amenities schools shopping transportation {address} {zip_code}"
        neighborhood_results = search_neighborhood_data(neighborhood_query, top_k=10)
        
        # Initialize locality analysis
        locality_analysis = {
            "listing_id": listing_id,
            "address": address,
            "amenities": [],
            "schools": [],
            "transportation": [],
            "shopping": [],
            "restaurants": [],
            "parks_recreation": [],
            "walkability_score": 0,
            "overall_score": 0,
            "pros": [],
            "cons": []
        }
        
        # Analyze neighborhood features
        feature_keywords = {
            "school": {"category": "schools", "weight": 3},
            "elementary": {"category": "schools", "weight": 2},
            "high school": {"category": "schools", "weight": 3},
            "university": {"category": "schools", "weight": 2},
            "grocery": {"category": "shopping", "weight": 2},
            "mall": {"category": "shopping", "weight": 1},
            "restaurant": {"category": "restaurants", "weight": 1},
            "dining": {"category": "restaurants", "weight": 1},
            "park": {"category": "parks_recreation", "weight": 2},
            "playground": {"category": "parks_recreation", "weight": 1},
            "gym": {"category": "parks_recreation", "weight": 1},
            "transit": {"category": "transportation", "weight": 2},
            "bus": {"category": "transportation", "weight": 1},
            "subway": {"category": "transportation", "weight": 2},
            "train": {"category": "transportation", "weight": 2},
            "walkable": {"category": "amenities", "weight": 2},
            "quiet": {"category": "amenities", "weight": 1},
            "safe": {"category": "amenities", "weight": 2}
        }
        
        total_score = 0
        found_features = {category: [] for category in ["schools", "shopping", "restaurants", "parks_recreation", "transportation", "amenities"]}
        
        for result in neighborhood_results:
            content = result.get("content", "").lower()
            
            for keyword, info in feature_keywords.items():
                if keyword in content:
                    category = info["category"]
                    weight = info["weight"]
                    
                    feature_item = {
                        "feature": keyword.title(),
                        "description": f"Found {keyword} in neighborhood analysis",
                        "score_contribution": weight
                    }
                    
                    if feature_item not in found_features[category]:
                        found_features[category].append(feature_item)
                        total_score += weight
        
        # Calculate walkability score (0-10)
        walkability_indicators = ["walkable", "pedestrian", "sidewalk", "crosswalk"]
        walkability_score = 0
        for result in neighborhood_results:
            content = result.get("content", "").lower()
            for indicator in walkability_indicators:
                if indicator in content:
                    walkability_score += 2
        walkability_score = min(10, walkability_score)
        
        # Calculate overall score (0-25)
        overall_score = min(25, total_score + walkability_score // 2)
        
        # Generate pros and cons
        pros = []
        cons = []
        
        if len(found_features["schools"]) >= 2:
            pros.append("🎓 Good school options nearby")
        elif len(found_features["schools"]) == 0:
            cons.append("🎓 Limited school options in area")
        
        if len(found_features["shopping"]) >= 2:
            pros.append("🛒 Convenient shopping access")
        elif len(found_features["shopping"]) == 0:
            cons.append("🛒 Limited shopping options")
        
        if len(found_features["transportation"]) >= 2:
            pros.append("🚌 Good public transportation")
        elif len(found_features["transportation"]) == 0:
            cons.append("🚌 Limited public transportation")
        
        if walkability_score >= 7:
            pros.append("🚶 Highly walkable neighborhood")
        elif walkability_score <= 3:
            cons.append("🚶 Low walkability area")
        
        if len(found_features["parks_recreation"]) >= 2:
            pros.append("🌳 Good recreational facilities")
        elif len(found_features["parks_recreation"]) == 0:
            cons.append("🌳 Limited recreational options")
        
        if overall_score >= 20:
            pros.append("⭐ Excellent neighborhood overall")
        elif overall_score <= 10:
            cons.append("⭐ Neighborhood needs improvement")
        
        locality_analysis.update({
            "amenities": found_features["amenities"],
            "schools": found_features["schools"],
            "transportation": found_features["transportation"],
            "shopping": found_features["shopping"],
            "restaurants": found_features["restaurants"],
            "parks_recreation": found_features["parks_recreation"],
            "walkability_score": walkability_score,
            "overall_score": overall_score,
            "neighborhood_rating": "Excellent" if overall_score >= 20 else 
                                 "Good" if overall_score >= 15 else
                                 "Fair" if overall_score >= 10 else "Poor",
            "pros": pros,
            "cons": cons,
            "analysis_completed": True
        })
        
        print(f"✅ Locality analysis completed for {listing_id}")
        print(f"   - Overall Score: {overall_score}/25")
        print(f"   - Walkability: {walkability_score}/10")
        print(f"   - Rating: {locality_analysis['neighborhood_rating']}")
        
        return convert_to_json_serializable(locality_analysis)
        
    except Exception as e:
        error_msg = f"Error analyzing locality: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "error": error_msg,
            "listing_id": listing_details.get("listing_id", "unknown"),
            "analysis_completed": False
        }

def create_locality_review_agent() -> LlmAgent:
    """Create and configure the Locality Review Agent using ADK patterns."""
    return LlmAgent(
        name="LocalityReviewAgent",
        model=settings.DEFAULT_AGENT_MODEL,
        description="Analyzes neighborhood characteristics and amenities for property listings",
        instruction="""You are a locality review agent that evaluates neighborhood features.
        
        You receive property listing details and analyze the surrounding area for:
        1. Schools and educational facilities
        2. Shopping and dining options
        3. Transportation accessibility
        4. Parks and recreational facilities
        5. Overall walkability and livability
        
        Use the analyze_neighborhood_features tool with the listing details from session state.
        Save your results to session state under 'locality_analysis'.""",
        tools=[FunctionTool(func=analyze_neighborhood_features)],
        input_schema=LocalityReviewInput,
        output_key="locality_analysis"
    )

# Create the agent instance
locality_review_agent = create_locality_review_agent()