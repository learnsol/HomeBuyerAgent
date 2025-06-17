"""
Recommendation Agent - Generates final recommendations based on all analysis.
Following ADK patterns.
"""
from agents.base_agent import HomeBuyerBaseAgent
from mock_adk import LlmAgent, FunctionTool, InvocationContext
from config import settings
from typing import Dict, Any, List
from agents.agent_utils import convert_to_json_serializable

def generate_recommendation_report(aggregated_data: Dict[str, Any], user_priorities: List[str]) -> Dict[str, Any]:
    """
    Tool function to generate final recommendation report.
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
            
            # Extract analysis data
            listing_details = data.get("listing_details", {})
            locality = data.get("locality_analysis", {})
            hazard = data.get("hazard_analysis", {})
            affordability = data.get("affordability_analysis", {})
            
            # Basic scoring logic
            summary = {
                "listing_id": listing_id,
                "price": listing_details.get("price", "N/A"),
                "address": listing_details.get("address", "N/A"),
                "bedrooms": listing_details.get("bedrooms", "N/A"),
                "bathrooms": listing_details.get("bathrooms", "N/A")
            }
            
            # Locality scoring
            if isinstance(locality, dict) and not locality.get("error"):
                locality_details = locality.get("locality_details", {})
                school_rating = locality_details.get("school_rating", 0)
                crime_rate = str(locality_details.get("crime_rate", "")).lower()
                
                if school_rating >= 7:
                    score += 2
                    pros.append("Good school rating")
                if "low" in crime_rate:
                    score += 2
                    pros.append("Low crime area")
                    
                summary["school_rating"] = school_rating
                summary["crime_rate"] = locality_details.get("crime_rate", "N/A")
            else:
                cons.append("Locality data unavailable")
            
            # Hazard scoring
            if isinstance(hazard, dict) and not hazard.get("error"):
                hazard_details = hazard.get("hazard_analysis", {})
                flood_risk = str(hazard_details.get("flood_risk_level", "")).lower()
                wildfire_risk = str(hazard_details.get("wildfire_risk_level", "")).lower()
                
                if "low" in flood_risk:
                    score += 1
                    pros.append("Low flood risk")
                if "low" in wildfire_risk:
                    score += 1
                    pros.append("Low wildfire risk")
                    
                summary["flood_risk"] = hazard_details.get("flood_risk_level", "N/A")
                summary["wildfire_risk"] = hazard_details.get("wildfire_risk_level", "N/A")
            else:
                cons.append("Hazard data unavailable")
            
            # Affordability scoring
            if isinstance(affordability, dict) and not affordability.get("error"):
                monthly_payment = affordability.get("total_estimated_monthly_payment", 0)
                is_affordable = affordability.get("is_affordable_back_end", False)
                
                if is_affordable:
                    score += 3
                    pros.append("Financially affordable")
                else:
                    cons.append("May strain budget")
                    
                summary["monthly_payment"] = monthly_payment
                summary["is_affordable"] = is_affordable
            else:
                cons.append("Affordability data unavailable")
            
            # User priorities matching (basic keyword matching)
            data_text = str(listing_details) + str(locality) + str(hazard)
            for priority in user_priorities:
                if priority.lower() in data_text.lower():
                    score += 1
                    pros.append(f"Matches priority: {priority}")
            
            summary.update({
                "total_score": score,
                "pros": pros,
                "cons": cons
            })
            
            ranked_listings.append(summary)
        
        # Sort by score descending
        ranked_listings.sort(key=lambda x: x["total_score"], reverse=True)
        
        final_report = {
            "recommendation_summary": f"Analyzed {len(aggregated_data)} listings based on your criteria",
            "user_priorities_considered": user_priorities,
            "top_recommendations": ranked_listings[:settings.FINAL_RECOMMENDATION_COUNT],
            "all_listings_ranked": ranked_listings
        }
        
        print(f"Recommendation report generated successfully")
        return convert_to_json_serializable(final_report)

    except Exception as e:
        print(f"Error in generate_recommendation_report: {e}")
        return {"error": f"Report generation failed: {str(e)}"}

class RecommendationAgent(HomeBuyerBaseAgent):
    """Agent for generating final property recommendations."""
    
    def __init__(self):
        super().__init__(
            name="RecommendationAgent",
            description="Generates final property recommendations by synthesizing all analysis results"
        )
        
        # Create LLM agent with recommendation generation tool
        self.llm_agent = LlmAgent(
            name="RecommendationLLM",
            model=settings.ORCHESTRATOR_MODEL,  # Use more capable model for synthesis
            description="LLM agent for generating recommendations",
            instruction="""You generate comprehensive property recommendations. Use the 
            generate_recommendation_report tool with aggregated analysis data and user priorities 
            to create ranked recommendations with pros/cons for each property.""",
            tools=[FunctionTool(func=generate_recommendation_report)],
            output_key="final_recommendations"
        )

    async def process_business_logic(self, ctx: InvocationContext) -> Dict[str, Any]:
        """Process final recommendation generation."""
        self._log("Processing final recommendation generation")
        
        # Get aggregated data and user priorities from context state
        aggregated_data = ctx.session.state.get("aggregated_analysis_data", {})
        user_priorities = ctx.session.state.get("user_priorities", [])
        
        if not aggregated_data:
            return {"error": "No aggregated analysis data available for recommendations"}
        
        # Call the recommendation tool
        result = generate_recommendation_report(aggregated_data, user_priorities)
        
        # Store final result in session state
        ctx.session.state["final_recommendations"] = result
        
        return result

def create_recommendation_agent() -> RecommendationAgent:
    """Factory function to create a RecommendationAgent."""
    return RecommendationAgent()
