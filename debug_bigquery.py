#!/usr/bin/env python3
"""
Debug script to test BigQuery connection and query formatting.
"""

from agents.agent_utils import get_table_name, query_bigquery

def test_simple_query():
    """Test a simple BigQuery query."""
    print("🔍 Testing simple BigQuery query...")
    
    try:
        table_name = get_table_name("listings")
        print(f"Table name: {table_name}")
        
        # Very simple query first
        simple_query = f"""
        SELECT listing_id, address_street, price
        FROM {table_name}
        LIMIT 3
        """
        
        print("Query:")
        print(simple_query)
        
        results = query_bigquery(simple_query)
        print(f"Results: {len(results)} rows")
        
        for result in results:
            print(f"  - {result.get('listing_id', 'N/A')}: {result.get('address_street', 'N/A')} - ${result.get('price', 0):,}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_embedding_query():
    """Test query for embeddings."""
    print("\n🔍 Testing embedding query...")
    
    try:
        table_name = get_table_name("listings")
        
        # Query for embeddings
        embedding_query = f"""
        SELECT 
            listing_id,
            address_street,
            price,
            description_embedding
        FROM {table_name}
        WHERE description_embedding IS NOT NULL
        LIMIT 2
        """
        
        print("Query:")
        print(embedding_query)
        
        results = query_bigquery(embedding_query)
        print(f"Results: {len(results)} rows")
        
        for result in results:
            embedding = result.get('description_embedding', [])
            print(f"  - {result.get('listing_id', 'N/A')}: {result.get('address_street', 'N/A')}")
            print(f"    Embedding length: {len(embedding) if embedding else 0}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_simple_query()
    test_embedding_query()
