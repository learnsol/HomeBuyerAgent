"""
Affordability Agent - Calculates affordability for listings.
Following ADK patterns.
"""
from agents.base_agent import HomeBuyerBaseAgent
from mock_adk import LlmAgent, FunctionTool, InvocationContext
from agents.agent_utils import query_bigquery, get_table_name, load_affordability_params, convert_to_json_serializable
from config import settings
from typing import Dict, Any

def calculate_affordability(listing_id: str, user_financial_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool function to calculate affordability for a listing using actual BigQuery schema.
    """
    print(f"💰 calculate_affordability called for listing: {listing_id}")
    print(f"User financial info: {user_financial_info}")
    
    if not isinstance(listing_id, str) or not listing_id.strip():
        return {"error": "listing_id must be a non-empty string"}
    if not isinstance(user_financial_info, dict):
        return {"error": "user_financial_info must be a dictionary"}

    try:
        # Get listing details using actual schema
        listing_price = user_financial_info.get("listing_price")
        if not listing_price:
            listings_table = get_table_name('listings')
            price_query = f"""
            SELECT 
                listing_id,
                price,
                address_street,
                property_type,
                square_footage
            FROM {listings_table} 
            WHERE listing_id = '{listing_id}' 
            LIMIT 1
            """
            price_rows = query_bigquery(price_query)
            if not price_rows or "price" not in price_rows[0]:
                return {"error": f"Could not determine price for listing '{listing_id}'"}
            listing_price = float(price_rows[0]["price"])
            listing_details = price_rows[0]
        else:
            listing_price = float(listing_price)
            listing_details = {"listing_id": listing_id, "price": listing_price}

        # Load affordability parameters from the actual JSON file
        params = load_affordability_params()

        # Get user financial details with defaults
        user_income_annual = float(user_financial_info.get("annual_income", 70000))
        down_payment_amount = float(user_financial_info.get("down_payment", 0))
        user_monthly_debts = float(user_financial_info.get("monthly_debt", user_financial_info.get("monthly_debts", 500)))
        credit_score = int(user_financial_info.get("credit_score", 750))

        # Calculate down payment if not provided directly
        if down_payment_amount == 0:
            down_payment_percentage = float(user_financial_info.get("down_payment_percentage", params["down_payment_percentage"]))
            down_payment_amount = listing_price * (down_payment_percentage / 100)

        # Calculate loan amount
        loan_amount = listing_price - down_payment_amount

        # Use actual interest rate from params (convert from decimal to percentage for calculations)
        interest_rate_annual = params["current_interest_rate_30_year_fixed"] * 100  # Convert 0.065 to 6.5%
        interest_rate_monthly = interest_rate_annual / 100 / 12
        loan_term_months = params["loan_term_years"] * 12

        if loan_amount <= 0:
            principal_interest_monthly = 0
        elif interest_rate_monthly > 0:
            m_rate = interest_rate_monthly
            n_payments = loan_term_months
            principal_interest_monthly = loan_amount * (m_rate * (1 + m_rate)**n_payments) / ((1 + m_rate)**n_payments - 1)
        else:
            principal_interest_monthly = loan_amount / loan_term_months if loan_term_months > 0 else 0        # Calculate additional costs using actual parameter names
        property_tax_monthly = (listing_price * params["property_tax_rate_estimate_annual_percentage"]) / 12
        home_insurance_monthly = (listing_price / 100000) * params["home_insurance_estimate_annual_avg_per_100k_value"] / 12
        
        # PMI if down payment < 20%
        down_payment_percentage = (down_payment_amount / listing_price) * 100
        pmi_monthly = 0
        if down_payment_percentage < 20:
            pmi_monthly = (loan_amount * 0.5 / 100) / 12  # 0.5% annual PMI rate

        total_monthly_payment = principal_interest_monthly + property_tax_monthly + home_insurance_monthly + pmi_monthly

        # Debt-to-income ratios
        user_income_monthly = user_income_annual / 12
        front_end_dti = (total_monthly_payment / user_income_monthly) * 100 if user_income_monthly > 0 else float('inf')
        back_end_dti = ((total_monthly_payment + user_monthly_debts) / user_income_monthly) * 100 if user_income_monthly > 0 else float('inf')

        result = {
            "listing_id": listing_id,
            "listing_price": round(listing_price, 2),
            "down_payment_percentage": round(down_payment_percentage, 2),
            "down_payment_amount": round(down_payment_amount, 2),
            "loan_amount": round(loan_amount, 2),
            "principal_and_interest_monthly": round(principal_interest_monthly, 2),
            "property_tax_monthly": round(property_tax_monthly, 2),
            "home_insurance_monthly": round(home_insurance_monthly, 2),
            "pmi_monthly": round(pmi_monthly, 2),
            "total_estimated_monthly_payment": round(total_monthly_payment, 2),
            "front_end_dti_percentage": round(front_end_dti, 2),
            "back_end_dti_percentage": round(back_end_dti, 2),
            "is_affordable_front_end": front_end_dti <= params.get("max_front_end_dti", 28),
            "is_affordable_back_end": back_end_dti <= params.get("max_back_end_dti", 36)
        }
        
        print(f"Affordability calculation completed for {listing_id}")
        return convert_to_json_serializable(result)

    except Exception as e:
        print(f"Error in calculate_affordability: {e}")
        return {"error": f"Affordability calculation failed: {str(e)}"}

class AffordabilityAgent(HomeBuyerBaseAgent):
    """Agent for calculating affordability of property listings."""
    
    def __init__(self):
        super().__init__(
            name="AffordabilityAgent",
            description="Calculates affordability of property listings based on user financial information"
        )
        
        # Create LLM agent with affordability calculation tool
        self.llm_agent = LlmAgent(
            name="AffordabilityLLM",
            model=settings.DEFAULT_AGENT_MODEL,
            description="LLM agent for affordability calculations",
            instruction="""You calculate affordability for property listings. Use the calculate_affordability 
            tool with the listing_id and user_financial_info to determine monthly payments, debt-to-income 
            ratios, and overall affordability.""",
            tools=[FunctionTool(func=calculate_affordability)],
            output_key="affordability_analysis"
        )

    async def process_business_logic(self, ctx: InvocationContext) -> Dict[str, Any]:
        """Process affordability calculation for a listing."""
        self._log("Processing affordability calculation request")
        
        # Get listing_id and user financial info from context state
        listing_id = ctx.session.state.get("current_listing_id")
        user_financial_info = ctx.session.state.get("user_financial_info", {})
        
        if not listing_id:
            return {"error": "No listing_id provided for affordability calculation"}
        
        # Call the calculation tool
        result = calculate_affordability(listing_id, user_financial_info)
        
        # Store result in session state with listing-specific key
        affordability_key = f"affordability_analysis_{listing_id}"
        ctx.session.state[affordability_key] = result
        
        return result

def create_affordability_agent() -> AffordabilityAgent:
    """Factory function to create an AffordabilityAgent."""
    return AffordabilityAgent()
