"""
Affordability Agent - Analyzes financial affordability of properties.
Using official Google ADK patterns.
"""
import os
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from config import settings
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from agents.agent_utils import convert_to_json_serializable
import json

# Set up Vertex AI environment variables for Google AI SDK
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
os.environ['GOOGLE_CLOUD_PROJECT'] = settings.VERTEX_AI_PROJECT_ID
os.environ['GOOGLE_CLOUD_LOCATION'] = settings.VERTEX_AI_LOCATION

class AffordabilityInput(BaseModel):
    """Input schema for affordability analysis."""
    listing_details: Dict[str, Any] = Field(description="Property listing details to analyze")
    user_financial_info: Dict[str, Any] = Field(description="User's financial information", default_factory=dict)

def analyze_affordability(listing_details: Dict[str, Any], user_financial_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Tool function to analyze financial affordability of a property.
    """
    print(f"💰 analyze_affordability called for listing: {listing_details.get('listing_id', 'Unknown')}")
    
    if not isinstance(listing_details, dict):
        return {"error": "listing_details must be a dictionary"}
    
    if user_financial_info is None:
        user_financial_info = {}
    
    try:
        listing_id = listing_details.get("listing_id", "unknown")
        property_price = listing_details.get("price", 0)
        
        # Load default financial parameters
        try:
            with open("config/affordability_params.json", "r") as f:
                default_params = json.load(f)
        except FileNotFoundError:
            # Default parameters if file doesn't exist
            default_params = {
                "annual_income": 80000,
                "down_payment_percent": 20,
                "interest_rate": 6.5,
                "loan_term_years": 30,
                "debt_to_income_ratio_max": 28,
                "property_tax_rate": 1.2,
                "insurance_annual": 1200,
                "hoa_monthly": 0,
                "utilities_monthly": 200,
                "maintenance_percent": 1.0
            }
        
        # Use user financial info or defaults
        annual_income = user_financial_info.get("annual_income", default_params["annual_income"])
        down_payment_percent = user_financial_info.get("down_payment_percent", default_params["down_payment_percent"])
        interest_rate = user_financial_info.get("interest_rate", default_params["interest_rate"])
        loan_term_years = user_financial_info.get("loan_term_years", default_params["loan_term_years"])
        debt_to_income_max = user_financial_info.get("debt_to_income_ratio_max", default_params["debt_to_income_ratio_max"])
        
        # Calculate affordability metrics
        monthly_income = annual_income / 12
        max_monthly_payment = monthly_income * (debt_to_income_max / 100)
        
        down_payment = property_price * (down_payment_percent / 100)
        loan_amount = property_price - down_payment
        
        # Monthly mortgage payment calculation
        monthly_rate = (interest_rate / 100) / 12
        num_payments = loan_term_years * 12
        
        if monthly_rate > 0:
            monthly_mortgage = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
        else:
            monthly_mortgage = loan_amount / num_payments
        
        # Additional monthly costs
        property_tax_monthly = (property_price * default_params["property_tax_rate"] / 100) / 12
        insurance_monthly = default_params["insurance_annual"] / 12
        hoa_monthly = default_params.get("hoa_monthly", 0)
        utilities_monthly = default_params.get("utilities_monthly", 200)
        maintenance_monthly = (property_price * default_params["maintenance_percent"] / 100) / 12
        
        total_monthly_payment = (monthly_mortgage + property_tax_monthly + 
                               insurance_monthly + hoa_monthly + 
                               utilities_monthly + maintenance_monthly)
        
        # Affordability analysis
        is_affordable = total_monthly_payment <= max_monthly_payment
        affordability_ratio = (total_monthly_payment / monthly_income) * 100
        
        # Investment analysis
        price_per_sqft = property_price / max(listing_details.get("square_footage", 1), 1)
        year_built = listing_details.get("year_built", 2000)
        current_year = 2025
        property_age = current_year - int(year_built) if str(year_built).isdigit() else 25
        
        # Simple investment scoring
        investment_score = 50  # Base score
        if price_per_sqft < 150:  # Good value per sqft
            investment_score += 20
        elif price_per_sqft > 300:  # Expensive per sqft
            investment_score -= 20
            
        if property_age < 10:  # New property
            investment_score += 15
        elif property_age > 50:  # Old property
            investment_score -= 15
        
        good_investment = investment_score >= 60
        
        affordability_analysis = {
            "listing_id": listing_id,
            "property_price": property_price,
            "is_affordable": is_affordable,
            "affordability_ratio": round(affordability_ratio, 2),
            "max_recommended_ratio": debt_to_income_max,
            "monthly_costs": {
                "mortgage_payment": round(monthly_mortgage, 2),
                "property_tax": round(property_tax_monthly, 2),
                "insurance": round(insurance_monthly, 2),
                "hoa": round(hoa_monthly, 2),
                "utilities": round(utilities_monthly, 2),
                "maintenance": round(maintenance_monthly, 2),
                "total_monthly": round(total_monthly_payment, 2)
            },
            "financing": {
                "down_payment_required": round(down_payment, 2),
                "loan_amount": round(loan_amount, 2),
                "interest_rate": interest_rate,
                "loan_term_years": loan_term_years
            },
            "investment_analysis": {
                "price_per_sqft": round(price_per_sqft, 2),
                "property_age": property_age,
                "investment_score": investment_score,
                "good_investment": good_investment
            },
            "financial_summary": {
                "monthly_income": round(monthly_income, 2),
                "max_monthly_payment": round(max_monthly_payment, 2),
                "actual_monthly_payment": round(total_monthly_payment, 2),
                "monthly_surplus": round(max_monthly_payment - total_monthly_payment, 2)
            },
            "analysis_completed": True
        }
        
        print(f"✅ Affordability analysis completed for {listing_id}")
        print(f"   - Affordable: {is_affordable}")
        print(f"   - Affordability Ratio: {affordability_ratio:.1f}% (max: {debt_to_income_max}%)")
        print(f"   - Monthly Payment: ${total_monthly_payment:,.2f}")
        
        return convert_to_json_serializable(affordability_analysis)
        
    except Exception as e:
        error_msg = f"Error analyzing affordability: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "error": error_msg,
            "listing_id": listing_details.get("listing_id", "unknown"),
            "analysis_completed": False
        }

def create_affordability_agent() -> LlmAgent:
    """Create and configure the Affordability Agent using ADK patterns."""
    return LlmAgent(
        name="AffordabilityAgent",
        model=settings.DEFAULT_AGENT_MODEL,
        description="Analyzes financial affordability of property listings",        instruction="""You are an affordability agent that evaluates financial feasibility of properties.
        
        You receive property listing details and analyze:
        1. Monthly payment calculations (mortgage, taxes, insurance, etc.)
        2. Debt-to-income ratios and affordability
        3. Down payment requirements
        4. Investment potential analysis
        
        Use the analyze_affordability tool with both:
        - listing_details from session state (current_listing or listing_details)
        - user_financial_info from session state
        
        Save your results to session state under 'affordability_analysis'.""",
        tools=[FunctionTool(func=analyze_affordability)],
        input_schema=AffordabilityInput,
        output_key="affordability_analysis"
    )

# Create the agent instance
affordability_agent = create_affordability_agent()
