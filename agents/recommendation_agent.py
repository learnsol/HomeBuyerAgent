"""
Recommendation Agent - Generates final recommendations based on all analysis.
Using official Google ADK patterns.
"""
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from config import settings
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from agents.agent_utils import convert_to_json_serializable
import os

# Set up Vertex AI environment variables for Google AI SDK
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
os.environ['GOOGLE_CLOUD_PROJECT'] = settings.VERTEX_AI_PROJECT_ID
os.environ['GOOGLE_CLOUD_LOCATION'] = settings.VERTEX_AI_LOCATION

class RecommendationInput(BaseModel):
    """Input schema for recommendation generation."""
    aggregated_data: Dict[str, Any] = Field(description="Aggregated analysis data from all agents")
    user_priorities: List[str] = Field(description="User's priority preferences", default_factory=list)

class RecommendationOutput(BaseModel):
    """Output schema for recommendation results."""
    ranked_listings: List[Dict[str, Any]] = Field(description="Ranked list of property recommendations")
    summary: Dict[str, Any] = Field(description="Overall recommendation summary")

def generate_recommendation_report(aggregated_data: Dict[str, Any], user_priorities: List[str]) -> Dict[str, Any]:
    """
    Tool function to generate final recommendation report with enhanced scoring and detailed writeup.
    """
    print(f"📋 generate_recommendation_report called")
    print(f"Aggregated data for {len(aggregated_data)} listings")
    print(f"User priorities: {user_priorities}")
    
    if not isinstance(aggregated_data, dict):
        return {"error": "aggregated_data must be a dictionary"}
    if not isinstance(user_priorities, list):
        user_priorities = []

    try:
        ranked_listings = []
        
        for listing_id, data in aggregated_data.items():
            score = 0
            pros = []
            cons = []
            details = {}
            
            # Extract analysis data
            listing_details = data.get("listing_details", {})
            locality = data.get("locality_analysis", {})
            hazard = data.get("hazard_analysis", {})
            affordability = data.get("affordability_analysis", {})
            
            # Basic property information
            summary = {
                "listing_id": listing_id,
                "price": listing_details.get("price", "N/A"),
                "address": listing_details.get("address", "N/A"),
                "bedrooms": listing_details.get("bedrooms", "N/A"),
                "bathrooms": listing_details.get("bathrooms", "N/A"),
                "square_footage": listing_details.get("square_footage", "N/A"),
                "year_built": listing_details.get("year_built", "N/A"),
                "property_type": listing_details.get("property_type", "N/A")
            }
            
            # Scoring based on different factors
            # Affordability scoring (0-25 points)
            if affordability.get("is_affordable", False):
                score += 20
                pros.append("✅ Financially affordable")
            else:
                cons.append("❌ May strain budget")
            
            if affordability.get("good_investment", False):
                score += 5
                pros.append("💰 Good investment potential")
            
            # Locality scoring (0-25 points)
            locality_score = locality.get("overall_score", 0)
            if isinstance(locality_score, (int, float)):
                score += min(locality_score, 25)
                if locality_score >= 20:
                    pros.append(f"🏘️ Excellent neighborhood (score: {locality_score})")
                elif locality_score >= 15:
                    pros.append(f"🏘️ Good neighborhood (score: {locality_score})")
                else:
                    cons.append(f"🏘️ Neighborhood needs improvement (score: {locality_score})")
            
            # Hazard scoring (0-25 points)
            hazard_score = hazard.get("overall_safety_score", 0)
            if isinstance(hazard_score, (int, float)):
                score += min(hazard_score, 25)
                if hazard_score >= 20:
                    pros.append(f"🔐 Very safe area (safety score: {hazard_score})")
                elif hazard_score >= 15:
                    pros.append(f"🔐 Generally safe (safety score: {hazard_score})")
                else:
                    cons.append(f"⚠️ Safety concerns (safety score: {hazard_score})")
            
            # Property condition scoring (0-25 points)
            property_condition = listing_details.get("condition", "").lower()
            if "excellent" in property_condition or "new" in property_condition:
                score += 25
                pros.append("🏠 Excellent property condition")
            elif "good" in property_condition:
                score += 20
                pros.append("🏠 Good property condition")
            elif "fair" in property_condition:
                score += 10
                cons.append("🔧 Property may need some updates")
            else:
                cons.append("🔧 Property condition unknown")
            
            # Priority bonus (0-10 points)
            priority_bonus = 0
            for priority in user_priorities:
                if priority.lower() in str(data).lower():
                    priority_bonus += 2
            score += min(priority_bonus, 10)
            
            if priority_bonus > 0:
                pros.append(f"⭐ Matches {priority_bonus//2} user priorities")
            
            # Create detailed analysis
            details = {
                "affordability_details": affordability,
                "locality_details": locality,
                "hazard_details": hazard,
                "listing_details": listing_details
            }
            
            ranked_listings.append({
                "listing_id": listing_id,
                "overall_score": min(score, 100),  # Cap at 100
                "summary": summary,
                "pros": pros,
                "cons": cons,
                "details": details,
                "recommendation": "Highly Recommended" if score >= 80 else 
                               "Recommended" if score >= 60 else 
                               "Consider with Caution" if score >= 40 else 
                               "Not Recommended"
            })
        
        # Sort by score (highest first)
        ranked_listings.sort(key=lambda x: x["overall_score"], reverse=True)
        
        # Generate overall summary
        total_listings = len(ranked_listings)
        highly_recommended = len([l for l in ranked_listings if l["overall_score"] >= 80])
        recommended = len([l for l in ranked_listings if 60 <= l["overall_score"] < 80])
        
        summary = {
            "total_listings_analyzed": total_listings,
            "highly_recommended_count": highly_recommended,
            "recommended_count": recommended,
            "top_recommendation": ranked_listings[0] if ranked_listings else None,
            "analysis_completed": True,
            "user_priorities_considered": user_priorities
        }
        
        result = {
            "ranked_listings": ranked_listings,
            "summary": summary
        }
        
        print(f"✅ Generated recommendations for {total_listings} listings")
        print(f"   - {highly_recommended} highly recommended")
        print(f"   - {recommended} recommended")
        
        return convert_to_json_serializable(result)
        
    except Exception as e:
        error_msg = f"Error generating recommendations: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "error": error_msg,
            "ranked_listings": [],
            "summary": {"analysis_completed": False, "error": error_msg}
        }

def create_recommendation_agent() -> LlmAgent:
    """Create and configure the Recommendation Agent using ADK patterns."""
    return LlmAgent(
        name="RecommendationAgent",
        model=settings.DEFAULT_AGENT_MODEL,
        description="Generates final property recommendations based on comprehensive analysis",
        instruction="""You are a recommendation agent that creates final property recommendations.
        
        You receive aggregated analysis data from multiple agents and user priorities.
        Use the generate_recommendation_report tool to:
        1. Score each property based on affordability, locality, hazards, and condition
        2. Rank properties by overall score
        3. Generate pros/cons for each property
        4. Provide clear recommendations
        
        The input will be in the session state under 'aggregated_analysis' and 'user_priorities'.
        Save your results to session state under 'final_recommendations'.""",        tools=[FunctionTool(func=generate_recommendation_report)],
        input_schema=RecommendationInput,
        output_key="final_recommendations"
    )

# Create the agent instance
recommendation_agent = create_recommendation_agent()
