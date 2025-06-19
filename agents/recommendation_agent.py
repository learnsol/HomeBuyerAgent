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
            
            # Base score for being a valid listing
            score += 2
            pros.append("Property meets basic search criteria")
              # Enhanced Locality scoring
            if isinstance(locality, dict) and not locality.get("error"):
                # Extract education score
                education_info = locality.get("education", {})
                if isinstance(education_info, dict):
                    edu_score = education_info.get("school_district_rating", 0)
                    if edu_score >= 8:
                        score += 4
                        pros.append("Excellent schools in area")
                    elif edu_score >= 6:
                        score += 2
                        pros.append("Good schools in area")
                    elif edu_score >= 4:
                        score += 1
                        pros.append("Decent schools in area")
                    details["education_score"] = edu_score
                
                # Extract safety score
                safety_info = locality.get("safety", {})
                if isinstance(safety_info, dict):
                    safety_score = safety_info.get("safety_score", 0)
                    if safety_score >= 8:
                        score += 4
                        pros.append("Very safe neighborhood")
                    elif safety_score >= 6:
                        score += 2
                        pros.append("Safe neighborhood")
                    elif safety_score >= 4:
                        score += 1
                        pros.append("Reasonably safe area")
                    else:
                        cons.append("Safety concerns in area")
                    details["safety_score"] = safety_score
                
                # Extract environment score based on air quality
                environment_info = locality.get("environment", {})
                if isinstance(environment_info, dict):
                    air_quality = environment_info.get("air_quality_rating", "").lower()
                    avg_aqi = environment_info.get("avg_aqi", 0)
                    if "good" in air_quality or avg_aqi < 50:
                        score += 3
                        pros.append("Excellent air quality")
                        env_score = 8
                    elif "moderate" in air_quality or avg_aqi < 100:
                        score += 1
                        pros.append("Good environmental quality")
                        env_score = 6
                    else:
                        env_score = 4
                    details["environment_score"] = env_score
                
                # Overall locality rating
                overall_rating = locality.get("overall_rating", 0)
                if overall_rating >= 8:
                    score += 2
                    pros.append("Highly rated neighborhood overall")
                elif overall_rating >= 6:
                    score += 1
                    pros.append("Well-rated neighborhood")
                details["overall_locality_rating"] = overall_rating
            else:
                cons.append("Limited locality data available")
            
            # Enhanced Hazard scoring
            if isinstance(hazard, dict) and not hazard.get("error"):
                # Direct access to hazard risks
                flood_risk = hazard.get("flood_risk", "Unknown")
                wildfire_risk = hazard.get("wildfire_risk", "Unknown")
                tornado_risk = hazard.get("tornado_risk", "Unknown")
                earthquake_risk = hazard.get("earthquake_risk", "Unknown")
                
                # Flood risk
                if "low" in str(flood_risk).lower():
                    score += 2
                    pros.append("Low flood risk")
                elif "moderate" in str(flood_risk).lower():
                    score += 1
                    pros.append("Moderate flood risk")
                elif "high" in str(flood_risk).lower():
                    cons.append("High flood risk area")
                
                # Wildfire risk
                if "low" in str(wildfire_risk).lower():
                    score += 2
                    pros.append("Low wildfire risk")
                elif "moderate" in str(wildfire_risk).lower():
                    score += 1
                    pros.append("Moderate wildfire risk")
                elif "high" in str(wildfire_risk).lower():
                    cons.append("High wildfire risk area")
                
                # Bonus for multiple low risks
                low_risks = sum(1 for risk in [flood_risk, wildfire_risk, tornado_risk, earthquake_risk] 
                              if "low" in str(risk).lower())
                if low_risks >= 3:
                    score += 1
                    pros.append("Very low natural disaster risk overall")
                
                details["flood_risk"] = flood_risk
                details["wildfire_risk"] = wildfire_risk
            else:
                cons.append("Limited hazard analysis available")
            
            # Enhanced Affordability scoring
            if isinstance(affordability, dict) and not affordability.get("error"):
                monthly_payment = affordability.get("total_estimated_monthly_payment", 0)
                is_affordable = affordability.get("is_affordable_back_end", False)
                debt_to_income = affordability.get("back_end_ratio", 0)
                
                if is_affordable:
                    score += 5
                    pros.append("Financially comfortable for your budget")
                    if debt_to_income < 0.28:
                        score += 2
                        pros.append("Excellent debt-to-income ratio")
                    elif debt_to_income < 0.36:
                        score += 1
                        pros.append("Good debt-to-income ratio")
                else:
                    score -= 2
                    cons.append("May strain your budget")
                    
                details["monthly_payment"] = monthly_payment
                details["is_affordable"] = is_affordable
                details["debt_to_income_ratio"] = debt_to_income
            else:
                cons.append("Limited affordability analysis available")
            
            # User priorities matching (enhanced keyword matching)
            if user_priorities:
                data_text = (str(listing_details) + str(locality) + str(hazard)).lower()
                priority_matches = []
                for priority in user_priorities:
                    if priority.lower() in data_text:
                        score += 2
                        priority_matches.append(priority)
                
                if priority_matches:
                    pros.append(f"Matches your priorities: {', '.join(priority_matches)}")
            
            summary.update({
                "total_score": score,
                "pros": pros,
                "cons": cons,
                "analysis_details": details
            })
            
            ranked_listings.append(summary)
        
        # Sort by score descending
        ranked_listings.sort(key=lambda x: x["total_score"], reverse=True)
        
        # Generate detailed writeup for the top property
        best_property_writeup = ""
        if ranked_listings:
            best = ranked_listings[0]
            best_property_writeup = generate_property_writeup(best, user_priorities)
        
        final_report = {
            "recommendation_summary": f"Analyzed {len(aggregated_data)} listings based on your criteria",
            "user_priorities_considered": user_priorities,
            "best_property_writeup": best_property_writeup,
            "top_recommendations": ranked_listings[:settings.FINAL_RECOMMENDATION_COUNT],
            "all_listings_ranked": ranked_listings
        }
        
        print(f"Recommendation report generated successfully")
        return convert_to_json_serializable(final_report)

    except Exception as e:
        print(f"Error in generate_recommendation_report: {e}")
        return {"error": f"Report generation failed: {str(e)}"}


def generate_property_writeup(property_data: Dict[str, Any], user_priorities: List[str]) -> str:
    """
    Generate a detailed writeup for the recommended property explaining why it suits the user.
    """
    try:
        address = property_data.get("address", "this property")
        price = property_data.get("price", "N/A")
        bedrooms = property_data.get("bedrooms", "N/A")
        bathrooms = property_data.get("bathrooms", "N/A")
        score = property_data.get("total_score", 0)
        pros = property_data.get("pros", [])
        analysis = property_data.get("analysis_details", {})
        
        writeup = f"""
🏆 **TOP RECOMMENDATION: {address}**

**Why This Property Is Perfect For You:**

This {bedrooms}-bedroom, {bathrooms}-bathroom property at {address} stands out as our top recommendation with a score of {score} points, making it an excellent match for your needs.

**Key Strengths:**
"""
        
        # Add pros with more detail
        for i, pro in enumerate(pros[:5], 1):  # Limit to top 5 pros
            writeup += f"\n{i}. {pro}"
        
        # Add detailed analysis if available
        if analysis:
            writeup += "\n\n**Detailed Analysis:**"
            
            if "education_score" in analysis and analysis["education_score"] > 0:
                edu_score = analysis["education_score"]
                writeup += f"\n• **Education**: School quality rated {edu_score}/10 - "
                if edu_score >= 8:
                    writeup += "exceptional schools for your family"
                elif edu_score >= 6:
                    writeup += "solid educational opportunities"
                else:
                    writeup += "basic educational amenities"
            
            if "safety_score" in analysis and analysis["safety_score"] > 0:
                safety_score = analysis["safety_score"]
                writeup += f"\n• **Safety**: Neighborhood safety rated {safety_score}/10 - "
                if safety_score >= 8:
                    writeup += "very secure area with low crime rates"
                elif safety_score >= 6:
                    writeup += "safe community environment"
                else:
                    writeup += "adequate security measures"
            
            if "monthly_payment" in analysis and analysis["monthly_payment"] > 0:
                monthly = analysis["monthly_payment"]
                writeup += f"\n• **Affordability**: Estimated monthly payment of ${monthly:,.2f}"
                if analysis.get("is_affordable", False):
                    writeup += " - comfortably within your budget"
                else:
                    writeup += " - requires careful budget consideration"
          # Connect to user priorities
        if user_priorities:
            writeup += f"\n\n**Alignment with Your Priorities:**\nThis property aligns well with your stated preferences for {', '.join(user_priorities[:3])}."
        
        writeup += f"\n\n**Investment Summary:**\nAt ${price:,}, this property offers strong value in today's market and represents a sound investment for your future."
        
        return writeup.strip()
        
    except Exception as e:
        return f"Unable to generate detailed writeup: {str(e)}"


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
