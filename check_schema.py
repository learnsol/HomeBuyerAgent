from agents.agent_utils import query_bigquery

# Check table schema
schema_query = """
SELECT column_name, data_type 
FROM `gen-lang-client-0044046698.home_buyer_hackathon_data.INFORMATION_SCHEMA.COLUMNS` 
WHERE table_name = 'listings' 
ORDER BY ordinal_position
"""

print("Checking listings table schema...")
schema_result = query_bigquery(schema_query)
if schema_result:
    print("Available columns:")
    for col in schema_result:
        print(f"  - {col['column_name']}: {col['data_type']}")
else:
    print("Could not retrieve schema")

# Try a simple query to see actual data structure
simple_query = """
SELECT * 
FROM `gen-lang-client-0044046698.home_buyer_hackathon_data.listings` 
LIMIT 1
"""

print("\nChecking actual data structure...")
data_result = query_bigquery(simple_query)
if data_result:
    print("Sample data columns:", list(data_result[0].keys()))
else:
    print("Could not retrieve sample data")
