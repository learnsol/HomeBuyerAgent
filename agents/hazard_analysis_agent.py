"""
Hazard Analysis Agent - Analyzes natural hazard risks for listings.
Following ADK patterns.
"""
from agents.base_agent import HomeBuyerBaseAgent
from mock_adk import LlmAgent, FunctionTool, InvocationContext
from agents.agent_utils import query_bigquery, get_table_name, convert_to_json_serializable
from config import settings
from typing import Dict, Any, List

def analyze_hazard_risks(listing_id: str) -> Dict[str, Any]:
    """
    Tool function to analyze hazard risks for a listing using actual BigQuery schema.
    """
    print(f"⚠️ analyze_hazard_risks called for listing: {listing_id}")
    
    if not isinstance(listing_id, str) or not listing_id.strip():
        return {"error": "listing_id must be a non-empty string"}

    try:
        # Query using actual BigQuery schema
        listings_table = get_table_name('listings')
        neighborhoods_table = get_table_name('neighborhoods')
        
        hazard_query = f"""
        SELECT
            l.listing_id,
            l.address_street,
            l.neighborhood_id,
            n.neighborhood_name,
            n.fema_flood_zone_designation,
            n.tornado_risk_level,
            n.wildfire_risk_level,
            n.earthquake_risk_level,
            n.dominant_weather_pattern
        FROM {listings_table} l
        JOIN {neighborhoods_table} n ON l.neighborhood_id = n.neighborhood_id
        WHERE l.listing_id = '{listing_id}'
        LIMIT 1
        """
        
        hazard_info = query_bigquery(hazard_query)

        if not hazard_info:
            return {"error": f"No hazard data found for listing: {listing_id}"}

        data = hazard_info[0]
        
        # Create comprehensive hazard analysis using actual schema
        analysis = {
            "listing_id": data.get("listing_id"),
            "address": data.get("address_street"),
            "neighborhood_name": data.get("neighborhood_name"),
            "flood_risk": {
                "fema_designation": data.get("fema_flood_zone_designation", "Unknown"),
                "risk_level": _interpret_flood_risk(data.get("fema_flood_zone_designation", "Unknown")),
                "insurance_required": _flood_insurance_required(data.get("fema_flood_zone_designation", "Unknown"))
            },
            "tornado_risk": {
                "risk_level": data.get("tornado_risk_level", "Unknown"),
                "risk_score": _convert_risk_to_score(data.get("tornado_risk_level", "Unknown"))
            },
            "wildfire_risk": {
                "risk_level": data.get("wildfire_risk_level", "Unknown"),
                "risk_score": _convert_risk_to_score(data.get("wildfire_risk_level", "Unknown"))
            },
            "earthquake_risk": {
                "risk_level": data.get("earthquake_risk_level", "Unknown"),
                "risk_score": _convert_risk_to_score(data.get("earthquake_risk_level", "Unknown"))
            },
            "weather_patterns": {
                "dominant_pattern": data.get("dominant_weather_pattern", "Mixed")
            },
            "overall_hazard_score": _calculate_overall_hazard_score(data),
            "risk_summary": _generate_risk_summary(data),
            "recommendations": _generate_risk_recommendations(data)
        }

        print(f"✅ Hazard analysis completed for {listing_id}")
        return convert_to_json_serializable(analysis)

    except Exception as e:
        print(f"❌ Error in analyze_hazard_risks: {e}")
        return {"error": f"Hazard analysis failed: {str(e)}"}

def _interpret_flood_risk(fema_designation: str) -> str:
    """Interpret FEMA flood zone designation."""
    if "High Risk" in fema_designation:
        return "High"
    elif "Medium Risk" in fema_designation:
        return "Medium" 
    elif "Low Risk" in fema_designation:
        return "Low"
    else:
        return "Unknown"

def _flood_insurance_required(fema_designation: str) -> bool:
    """Determine if flood insurance is required based on FEMA designation."""
    return "High Risk" in fema_designation

def _convert_risk_to_score(risk_level: str) -> float:
    """Convert risk level to numeric score (1-10, lower is better)."""
    risk_mapping = {
        "Low": 2.0,
        "Medium": 5.0,
        "High": 8.0
    }
    return risk_mapping.get(risk_level, 5.0)

def _calculate_overall_hazard_score(data: Dict[str, Any]) -> float:
    """Calculate overall hazard score (1-10, lower is better)."""
    flood_score = _convert_risk_to_score(_interpret_flood_risk(data.get("fema_flood_zone_designation", "Unknown")))
    tornado_score = _convert_risk_to_score(data.get("tornado_risk_level", "Unknown"))
    wildfire_score = _convert_risk_to_score(data.get("wildfire_risk_level", "Unknown"))
    earthquake_score = _convert_risk_to_score(data.get("earthquake_risk_level", "Unknown"))
    
    # Weight the risks based on typical impact
    overall = (flood_score * 0.3 + wildfire_score * 0.3 + earthquake_score * 0.25 + tornado_score * 0.15)
    return round(overall, 2)

def _generate_risk_summary(data: Dict[str, Any]) -> str:
    """Generate a summary of the hazard risks."""
    neighborhood = data.get("neighborhood_name", "Unknown")
    flood_risk = _interpret_flood_risk(data.get("fema_flood_zone_designation", "Unknown"))
    wildfire_risk = data.get("wildfire_risk_level", "Unknown")
    earthquake_risk = data.get("earthquake_risk_level", "Unknown")
    
    summary = f"{neighborhood} has {flood_risk.lower()} flood risk, {wildfire_risk.lower()} wildfire risk, and {earthquake_risk.lower()} earthquake risk."
    return summary

def _generate_risk_recommendations(data: Dict[str, Any]) -> List[str]:
    """Generate risk-based recommendations."""
    recommendations = []
    
    flood_risk = _interpret_flood_risk(data.get("fema_flood_zone_designation", "Unknown"))
    if flood_risk == "High":
        recommendations.append("Consider flood insurance - may be required for mortgage")
        recommendations.append("Evaluate property elevation and drainage")
    
    wildfire_risk = data.get("wildfire_risk_level", "Unknown")
    if wildfire_risk == "High":
        recommendations.append("Review wildfire insurance coverage")
        recommendations.append("Consider defensible space around property")
    
    earthquake_risk = data.get("earthquake_risk_level", "Unknown")
    if earthquake_risk == "High":
        recommendations.append("Consider earthquake insurance")
        recommendations.append("Evaluate building seismic safety")
    
    if not recommendations:
        recommendations.append("Overall low natural hazard risk - standard homeowner's insurance should suffice")    
    return recommendations

class HazardAnalysisAgent(HomeBuyerBaseAgent):
    """Agent for analyzing natural hazard risks."""
    
    def __init__(self):
        super().__init__(
            name="HazardAnalysisAgent",
            description="Analyzes natural hazard risks for property listings"
        )
        
        # Create LLM agent with hazard analysis tool
        self.llm_agent = LlmAgent(
            name="HazardAnalysisLLM",
            model=settings.DEFAULT_AGENT_MODEL,
            description="LLM agent for hazard risk analysis",
            instruction="""You analyze natural hazard risks for property listings. Use the 
            analyze_hazard_risks tool with the listing_id to assess flood, wildfire, earthquake, 
            and hurricane risks based on the property's location.""",
            tools=[FunctionTool(func=analyze_hazard_risks)],
            output_key="hazard_analysis"
        )

    async def process_business_logic(self, ctx: InvocationContext) -> Dict[str, Any]:
        """Process hazard analysis for a listing."""
        self._log("Processing hazard analysis request")
        
        # Get listing_id from context state
        listing_id = ctx.session.state.get("current_listing_id")
        if not listing_id:
            return {"error": "No listing_id provided for hazard analysis"}
        
        # Call the analysis tool
        result = analyze_hazard_risks(listing_id)
        
        # Store result in session state with listing-specific key
        hazard_key = f"hazard_analysis_{listing_id}"
        ctx.session.state[hazard_key] = result
        
        return result

def create_hazard_analysis_agent() -> HazardAnalysisAgent:
    """Factory function to create a HazardAnalysisAgent."""
    return HazardAnalysisAgent()
