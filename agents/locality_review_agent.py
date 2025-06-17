"""
Locality Review Agent - Analyzes neighborhood data for listings.
Following ADK patterns.
"""
from agents.base_agent import HomeBuyerBaseAgent
from mock_adk import LlmAgent, FunctionTool, InvocationContext
from agents.agent_utils import query_bigquery, get_table_name, convert_to_json_serializable
from config import settings
from typing import Dict, Any

def analyze_locality(listing_id: str) -> Dict[str, Any]:
    """
    Tool function to analyze locality details for a listing using actual BigQuery schema.
    """
    print(f"🏘️ analyze_locality called for listing: {listing_id}")
    
    if not isinstance(listing_id, str) or not listing_id.strip():
        return {"error": "listing_id must be a non-empty string"}

    try:
        # Query using actual BigQuery schema from the CSV files
        listings_table = get_table_name('listings')
        neighborhoods_table = get_table_name('neighborhoods')
        
        locality_query = f"""
        SELECT
            l.listing_id,
            l.address_street,
            l.neighborhood_id,
            n.neighborhood_name,
            n.zip_code,
            n.school_district_rating,
            n.crime_rate_index,
            n.avg_aqi,
            n.avg_annual_temp_fahrenheit,
            n.dominant_weather_pattern,
            n.fema_flood_zone_designation,
            n.tornado_risk_level,
            n.wildfire_risk_level,
            n.earthquake_risk_level
        FROM {listings_table} l
        JOIN {neighborhoods_table} n ON l.neighborhood_id = n.neighborhood_id
        WHERE l.listing_id = '{listing_id}'
        LIMIT 1
        """
        
        locality_info = query_bigquery(locality_query)
        
        if not locality_info:
            return {"error": f"No locality details found for listing: {listing_id}"}

        data = locality_info[0]
        
        # Create analysis using actual schema fields
        analysis = {
            "listing_id": data.get("listing_id"),
            "address": data.get("address_street"),
            "neighborhood_info": {
                "neighborhood_id": data.get("neighborhood_id"),
                "neighborhood_name": data.get("neighborhood_name"),
                "zip_code": data.get("zip_code")
            },
            "education": {
                "school_district_rating": data.get("school_district_rating", 0),
                "rating_interpretation": _interpret_school_rating(data.get("school_district_rating", 0))
            },
            "safety": {
                "crime_rate_index": data.get("crime_rate_index", "Unknown"),
                "safety_score": _convert_crime_index_to_score(data.get("crime_rate_index", "Unknown"))
            },
            "environment": {
                "avg_aqi": data.get("avg_aqi", 50),
                "air_quality_rating": _interpret_aqi(data.get("avg_aqi", 50)),
                "avg_annual_temp_fahrenheit": data.get("avg_annual_temp_fahrenheit", 70),
                "dominant_weather_pattern": data.get("dominant_weather_pattern", "Mixed")
            },
            "natural_hazards": {
                "fema_flood_zone": data.get("fema_flood_zone_designation", "Unknown"),
                "tornado_risk": data.get("tornado_risk_level", "Unknown"),
                "wildfire_risk": data.get("wildfire_risk_level", "Unknown"),
                "earthquake_risk": data.get("earthquake_risk_level", "Unknown")
            },
            "overall_rating": _calculate_overall_locality_rating(data),
            "analysis_summary": _generate_locality_summary(data)
        }

        print(f"✅ Locality analysis completed successfully for {listing_id}")
        return convert_to_json_serializable(analysis)

    except Exception as e:
        print(f"❌ Error in analyze_locality: {e}")
        return {"error": f"Locality analysis failed: {str(e)}"}

def _interpret_school_rating(rating: int) -> str:
    """Convert school district rating to interpretation."""
    if rating >= 9:
        return "Excellent"
    elif rating >= 7:
        return "Good"
    elif rating >= 5:
        return "Average"
    else:
        return "Below Average"

def _convert_crime_index_to_score(crime_index: str) -> float:
    """Convert crime rate index to numeric score (1-10, higher is safer)."""
    crime_mapping = {
        "Low": 9.0,
        "Medium": 6.0,
        "High": 3.0
    }
    return crime_mapping.get(crime_index, 5.0)

def _interpret_aqi(aqi: int) -> str:
    """Interpret Air Quality Index."""
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    else:
        return "Unhealthy"

def _calculate_overall_locality_rating(data: Dict[str, Any]) -> float:
    """Calculate overall locality rating based on all factors."""
    school_rating = data.get("school_district_rating", 5) / 10.0  # Normalize to 0-1
    safety_score = _convert_crime_index_to_score(data.get("crime_rate_index", "Medium")) / 10.0
    
    # AQI (lower is better, so invert)
    aqi = data.get("avg_aqi", 50)
    air_quality_score = max(0, (100 - aqi) / 100.0)
    
    # Weight the factors
    overall = (school_rating * 0.4 + safety_score * 0.4 + air_quality_score * 0.2) * 10
    return round(overall, 2)

def _generate_locality_summary(data: Dict[str, Any]) -> str:
    """Generate a summary of the locality analysis."""
    neighborhood = data.get("neighborhood_name", "Unknown")
    school_rating = data.get("school_district_rating", 0)
    crime_index = data.get("crime_rate_index", "Unknown")
    aqi = data.get("avg_aqi", 50)
    
    summary = f"{neighborhood} offers "
    
    if school_rating >= 8:
        summary += "excellent schools, "
    elif school_rating >= 6:
        summary += "good schools, "
    else:
        summary += "average schools, "
    
    if crime_index == "Low":
        summary += "low crime rates, "
    elif crime_index == "Medium":
        summary += "moderate safety, "
    else:
        summary += "higher crime concerns, "
    
    if aqi <= 50:
        summary += "and good air quality."
    elif aqi <= 100:
        summary += "and moderate air quality."
    else:
        summary += "and poor air quality."    
    return summary

class LocalityReviewAgent(HomeBuyerBaseAgent):
    """Agent for analyzing locality and neighborhood data."""
    
    def __init__(self):
        super().__init__(
            name="LocalityReviewAgent",
            description="Analyzes locality and neighborhood data for property listings"
        )
          # Create LLM agent with locality analysis tool
        self.llm_agent = LlmAgent(
            name="LocalityReviewLLM",
            model=settings.DEFAULT_AGENT_MODEL,
            description="LLM agent for locality analysis",
            instruction="""You analyze neighborhood data for property listings. Use the analyze_locality 
            tool with the current_listing_id from session state to get comprehensive neighborhood 
            information including schools, crime rates, and amenities.""",
            tools=[FunctionTool(func=analyze_locality)],
            output_key="locality_analysis"
        )

    async def _run_async_impl(self, ctx: InvocationContext):
        """Execute using ADK pattern - delegate to LLM agent."""
        self._log("Processing locality analysis using ADK patterns")
        
        # The LLM agent will read current_listing_id from session state
        async for event in self.llm_agent.run_stream_async("", ctx):
            yield event

    async def process_business_logic(self, ctx: InvocationContext) -> Dict[str, Any]:
        """Legacy method for backward compatibility."""
        self._log("Processing locality analysis request")
        
        # Get listing_id from context state
        listing_id = ctx.session.state.get("current_listing_id")
        if not listing_id:
            return {"error": "No listing_id provided for locality analysis"}
        
        # Call the analysis tool
        result = analyze_locality(listing_id)
        
        # Store result in session state with listing-specific key
        locality_key = f"locality_analysis_{listing_id}"
        ctx.session.state[locality_key] = result
        
        return result

def create_locality_review_agent() -> LocalityReviewAgent:
    """Factory function to create a LocalityReviewAgent."""
    return LocalityReviewAgent()
