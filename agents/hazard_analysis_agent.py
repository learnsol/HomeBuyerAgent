"""
Hazard Analysis Agent - Analyzes safety and environmental hazards for properties.
Using official Google ADK patterns.
"""
import os
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from config import settings
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from agents.vector_search_utils import search_hazard_data
from agents.agent_utils import convert_to_json_serializable

# Set up Vertex AI environment variables for Google AI SDK
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
os.environ['GOOGLE_CLOUD_PROJECT'] = settings.VERTEX_AI_PROJECT_ID
os.environ['GOOGLE_CLOUD_LOCATION'] = settings.VERTEX_AI_LOCATION

class HazardAnalysisInput(BaseModel):
    """Input schema for hazard analysis."""
    listing_details: Dict[str, Any] = Field(description="Property listing details to analyze")

def analyze_property_hazards(listing_details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool function to analyze environmental and safety hazards for a property.
    """
    print(f"⚠️ analyze_property_hazards called for listing: {listing_details.get('listing_id', 'Unknown')}")
    
    if not isinstance(listing_details, dict):
        return {"error": "listing_details must be a dictionary"}
    
    try:
        listing_id = listing_details.get("listing_id", "unknown")
        address = listing_details.get("address", "")
        zip_code = listing_details.get("zip_code", "")
        
        # Search for hazard-related data using vector search
        hazard_query = f"safety hazards environmental risks natural disasters {address} {zip_code}"
        hazard_results = search_hazard_data(hazard_query, top_k=5)
        
        # Initialize hazard analysis
        hazard_analysis = {
            "listing_id": listing_id,
            "address": address,
            "hazards_found": [],
            "safety_factors": [],
            "environmental_risks": [],
            "natural_disaster_risk": {},
            "overall_safety_score": 0,
            "recommendations": []
        }
        
        # Analyze hazard data
        hazard_keywords = {
            "flood": {"weight": 3, "category": "natural_disaster"},
            "earthquake": {"weight": 3, "category": "natural_disaster"},
            "fire": {"weight": 2, "category": "safety"},
            "crime": {"weight": 2, "category": "safety"},
            "pollution": {"weight": 2, "category": "environmental"},
            "toxic": {"weight": 3, "category": "environmental"},
            "safe": {"weight": -2, "category": "positive"},
            "secure": {"weight": -1, "category": "positive"}
        }
        
        total_risk_score = 0
        found_hazards = []
        safety_factors = []
        
        for result in hazard_results:
            content = result.get("content", "").lower()
            
            for keyword, info in hazard_keywords.items():
                if keyword in content:
                    if info["category"] == "positive":
                        safety_factors.append({
                            "factor": keyword.title(),
                            "description": f"Positive safety indicator found in area analysis",
                            "score_impact": abs(info["weight"])
                        })
                        total_risk_score += info["weight"]  # Negative weight reduces risk
                    else:
                        found_hazards.append({
                            "hazard": keyword.title(),
                            "category": info["category"],
                            "severity": "High" if info["weight"] >= 3 else "Medium",
                            "description": f"{keyword.title()} risk identified in area analysis"
                        })
                        total_risk_score += info["weight"]
        
        # Calculate overall safety score (0-25, higher is safer)
        base_score = 25
        safety_score = max(0, min(25, base_score - total_risk_score))
        
        # Natural disaster risk assessment
        natural_disasters = ["flood", "earthquake", "hurricane", "tornado", "wildfire"]
        disaster_risks = {}
        for disaster in natural_disasters:
            risk_level = "Low"
            for result in hazard_results:
                if disaster in result.get("content", "").lower():
                    risk_level = "Medium" if disaster in ["flood", "wildfire"] else "High"
                    break
            disaster_risks[disaster] = risk_level
        
        # Generate recommendations
        recommendations = []
        if safety_score < 15:
            recommendations.append("Consider additional security measures for this property")
        if any(h["category"] == "environmental" for h in found_hazards):
            recommendations.append("Environmental assessment recommended before purchase")
        if any(h["category"] == "natural_disaster" for h in found_hazards):
            recommendations.append("Review insurance coverage for natural disaster risks")
        if safety_score >= 20:
            recommendations.append("Property is in a generally safe area")
        
        hazard_analysis.update({
            "hazards_found": found_hazards,
            "safety_factors": safety_factors,
            "environmental_risks": [h for h in found_hazards if h["category"] == "environmental"],
            "natural_disaster_risk": disaster_risks,
            "overall_safety_score": safety_score,
            "risk_level": "Low" if safety_score >= 20 else "Medium" if safety_score >= 10 else "High",
            "recommendations": recommendations,
            "analysis_completed": True
        })
        
        print(f"✅ Hazard analysis completed for {listing_id}")
        print(f"   - Safety Score: {safety_score}/25")
        print(f"   - Risk Level: {hazard_analysis['risk_level']}")
        print(f"   - Hazards Found: {len(found_hazards)}")
        
        return convert_to_json_serializable(hazard_analysis)
        
    except Exception as e:
        error_msg = f"Error analyzing hazards: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "error": error_msg,
            "listing_id": listing_details.get("listing_id", "unknown"),
            "analysis_completed": False
        }

def create_hazard_analysis_agent() -> LlmAgent:
    """Create and configure the Hazard Analysis Agent using ADK patterns."""
    return LlmAgent(
        name="HazardAnalysisAgent",
        model=settings.DEFAULT_AGENT_MODEL,
        description="Analyzes safety and environmental hazards for property listings",
        instruction="""You are a hazard analysis agent that evaluates safety and environmental risks.
        
        You receive property listing details and analyze them for:
        1. Natural disaster risks (floods, earthquakes, etc.)
        2. Environmental hazards (pollution, toxic sites)
        3. Safety concerns (crime rates, fire risks)
        4. Overall safety assessment
        
        Use the analyze_property_hazards tool with the listing details from session state.
        Save your results to session state under 'hazard_analysis'.""",
        tools=[FunctionTool(func=analyze_property_hazards)],
        input_schema=HazardAnalysisInput,
        output_key="hazard_analysis"
    )

# Create the agent instance
hazard_analysis_agent = create_hazard_analysis_agent()