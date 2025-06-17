"""
Agent utilities for BigQuery interaction and common functions.
"""
from google.cloud import bigquery
from config import settings
import json
from typing import List, Dict, Any
import os

# Configuration for mock data usage
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

# Initialize BigQuery client globally
BQ_CLIENT = None

def initialize_bigquery_client():
    """Initialize BigQuery client with proper error handling."""
    global BQ_CLIENT
    if BQ_CLIENT is not None:
        return BQ_CLIENT
    
    try:
        # Initialize with explicit project and location
        BQ_CLIENT = bigquery.Client(
            project=settings.BIGQUERY_PROJECT_ID,
            location=settings.BIGQUERY_LOCATION
        )
        
        # Test the connection by running a simple query
        test_query = f"SELECT COUNT(*) as count FROM `{settings.BIGQUERY_PROJECT_ID}.{settings.BIGQUERY_DATASET_ID}.{settings.BIGQUERY_LISTINGS_TABLE}` LIMIT 1"
        query_job = BQ_CLIENT.query(test_query)
        result = list(query_job.result())
        
        print(f"✅ Successfully connected to BigQuery project: {settings.BIGQUERY_PROJECT_ID}")
        print(f"✅ Dataset: {settings.BIGQUERY_DATASET_ID}")
        return BQ_CLIENT
        
    except Exception as e:
        print(f"❌ Failed to initialize BigQuery client: {e}")
        print("🔄 Falling back to mock data mode")
        BQ_CLIENT = None
        return None

# Initialize on import
initialize_bigquery_client()

def get_bigquery_client():
    """Returns the BigQuery client."""
    global BQ_CLIENT
    if BQ_CLIENT is None:
        return initialize_bigquery_client()
    return BQ_CLIENT

def query_bigquery(query: str) -> List[Dict[str, Any]]:
    """Executes a SQL query on BigQuery and returns results."""
    # Check if we should use mock data
    if USE_MOCK_DATA:
        print("🔧 Using mock data (USE_MOCK_DATA=true)")
        return _get_mock_data(query)
    
    client = get_bigquery_client()
    if client is None:
        print("🔄 BigQuery client unavailable, using mock data")
        return _get_mock_data(query)
    
    try:
        print(f"🔍 Executing BigQuery query on project {settings.BIGQUERY_PROJECT_ID}")
        print(f"📊 Query: {query[:100]}{'...' if len(query) > 100 else ''}")
        
        query_job = client.query(query, location=settings.BIGQUERY_LOCATION)
        results = query_job.result()
        rows = [dict(row) for row in results]
        
        print(f"✅ BigQuery query successful - returned {len(rows)} rows")
        return rows
        
    except Exception as e:
        print(f"❌ BigQuery query failed: {e}")
        print("🔄 Falling back to mock data")
        return _get_mock_data(query)

def _get_mock_data(query: str) -> List[Dict[str, Any]]:
    """Returns mock data for development using actual BigQuery schema."""
    print("Using mock data with actual BigQuery schema")
    
    if "listings" in query.lower():
        return [
            {
                "listing_id": "P0001",
                "address_street": "123 Main St",
                "neighborhood_id": "N001", 
                "price": 750000,
                "bedrooms": 4,
                "bathrooms": 3,
                "square_footage": 2800,
                "property_type": "Single Family",
                "year_built": 2005,
                "description": "Spacious family home in Willow Creek Estates. Features a large backyard, updated kitchen, and close to top-rated schools.",
                "image_url": "placeholder.jpg"
            },
            {
                "listing_id": "P0002", 
                "address_street": "456 Oak Ave",
                "neighborhood_id": "N002",
                "price": 450000,
                "bedrooms": 2,
                "bathrooms": 2,
                "square_footage": 1200,
                "property_type": "Condo",
                "year_built": 2018,
                "description": "Modern condo in Downtown Metro Hub. Open floor plan, city views, and walking distance to amenities.",
                "image_url": "placeholder.jpg"
            },
            {
                "listing_id": "P0003",
                "address_street": "789 Pine Ln", 
                "neighborhood_id": "N001",
                "price": 680000,
                "bedrooms": 3,
                "bathrooms": 2.5,
                "square_footage": 2200,
                "property_type": "Townhouse",
                "year_built": 1999,
                "description": "Charming townhouse in Willow Creek Estates. Quiet street, good schools, recently updated.",
                "image_url": "placeholder.jpg"
            }
        ]
    elif "neighborhood" in query.lower():
        return [
            {
                "neighborhood_id": "N001",
                "neighborhood_name": "Willow Creek Estates",
                "zip_code": "90210",
                "avg_annual_temp_fahrenheit": 70,
                "school_district_rating": 9,
                "crime_rate_index": "Low",
                "avg_aqi": 25,
                "dominant_weather_pattern": "Sunny",
                "fema_flood_zone_designation": "Low Risk",
                "tornado_risk_level": "Low",
                "wildfire_risk_level": "Low", 
                "earthquake_risk_level": "Medium"
            },
            {
                "neighborhood_id": "N002",
                "neighborhood_name": "Downtown Metro Hub",
                "zip_code": "10001", 
                "avg_annual_temp_fahrenheit": 60,
                "school_district_rating": 6,
                "crime_rate_index": "Medium",
                "avg_aqi": 55,
                "dominant_weather_pattern": "Mixed",
                "fema_flood_zone_designation": "Medium Risk",
                "tornado_risk_level": "Low",
                "wildfire_risk_level": "Low",                "earthquake_risk_level": "Low"
            }
        ]
    elif "affordability" in query.lower():
        return [
            {
                "interest_rate": 3.5,
                "loan_term_years": 30,
                "property_tax_rate": 1.2,
                "home_insurance_annual": 1200,
                "down_payment_percentage": 20,
                "pmi_rate_annual_percentage": 0.5,
                "max_front_end_dti": 28,
                "max_back_end_dti": 36
            }
        ]
    
    return []

def get_table_name(table_key: str) -> str:
    """Returns the fully qualified BigQuery table name."""
    project = settings.BIGQUERY_PROJECT_ID
    dataset = settings.BIGQUERY_DATASET_ID
    
    table_mapping = {
        'listings': settings.BIGQUERY_LISTINGS_TABLE,
        'neighborhoods': settings.BIGQUERY_NEIGHBORHOODS_TABLE,
        'affordability_params': settings.BIGQUERY_AFFORDABILITY_PARAMS_TABLE
    }
    
    if table_key not in table_mapping:
        raise ValueError(f"Unknown table key: {table_key}")
    
    table_name = table_mapping[table_key]
    return f"`{project}.{dataset}.{table_name}`"

def load_affordability_params() -> Dict[str, Any]:
    """Loads affordability parameters from the local JSON file."""
    try:
        # Use local JSON file instead of BigQuery
        import os
        params_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'affordability_params.json')
        
        if os.path.exists(params_file):
            with open(params_file, 'r') as f:
                params = json.load(f)
            print(f"✅ Loaded affordability parameters from {params_file}")
            return params
        else:
            print(f"❌ Affordability params file not found: {params_file}")
            
    except Exception as e:
        print(f"❌ Error loading affordability parameters: {e}")
    
    # Return defaults if file loading fails
    print("🔄 Using default affordability parameters")
    return {
        "current_interest_rate_30_year_fixed": 0.065,
        "property_tax_rate_estimate_annual_percentage": 0.012,
        "home_insurance_estimate_annual_avg_per_100k_value": 500,
        "interest_rate": 3.5,
        "loan_term_years": 30,
        "down_payment_percentage": 20
    }

def convert_to_json_serializable(data: Any) -> Any:
    """Converts data to be JSON serializable."""
    if isinstance(data, dict):
        return {k: convert_to_json_serializable(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_to_json_serializable(i) for i in data]
    elif hasattr(data, 'isoformat'):
        return data.isoformat()
    return data
