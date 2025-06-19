#!/usr/bin/env python3
"""
Check embedding status in BigQuery.
"""

from agents.agent_utils import query_bigquery, get_table_name

def check_embeddings():
    """Check the status of embeddings in the BigQuery table."""
    print("🔍 Checking embedding status in BigQuery...")
    
    table_name = get_table_name('listings')
    
    # Check if there are any non-null embeddings
    check_query = f"""
    SELECT 
        COUNT(*) as total_listings,
        COUNT(description_embedding) as listings_with_embeddings,
        COUNT(CASE WHEN description_embedding IS NOT NULL AND ARRAY_LENGTH(description_embedding) > 0 THEN 1 END) as listings_with_valid_embeddings
    FROM {table_name}
    """
    
    result = query_bigquery(check_query)
    if result:
        print("📊 Embedding status:")
        for row in result:
            total = row.get('total_listings', 0)
            with_embeddings = row.get('listings_with_embeddings', 0)
            with_valid = row.get('listings_with_valid_embeddings', 0)
            
            print(f"  Total listings: {total}")
            print(f"  With embeddings: {with_embeddings}")
            print(f"  With valid embeddings: {with_valid}")
            
            if with_valid == 0:
                print("❌ No listings have valid embeddings!")
                print("💡 You may need to populate the description_embedding column first.")
            else:
                print(f"✅ Found {with_valid} listings with valid embeddings")
    
    # Also check a sample of the data
    sample_query = f"""
    SELECT 
        listing_id,
        address_street,
        description,
        description_embedding IS NOT NULL as has_embedding,
        CASE WHEN description_embedding IS NOT NULL THEN ARRAY_LENGTH(description_embedding) ELSE 0 END as embedding_length
    FROM {table_name}
    LIMIT 5
    """
    
    print("\n📋 Sample of listings:")
    sample_results = query_bigquery(sample_query)
    if sample_results:
        for i, row in enumerate(sample_results):
            listing_id = row.get('listing_id', 'N/A')
            address = row.get('address_street', 'N/A')
            has_embedding = row.get('has_embedding', False)
            embed_length = row.get('embedding_length', 0)
            
            print(f"  {i+1}. {listing_id} - {address}")
            print(f"     Has embedding: {has_embedding}, Length: {embed_length}")

if __name__ == "__main__":
    check_embeddings()
