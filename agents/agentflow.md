User_Input_Event (e.g., search criteria: budget, beds, baths, priorities)
    │
    └── TRIGGER ──> Listing_Review_Agent
                        │ (Input: User criteria)
                        │
                        ├── QUERIES BigQuery 'listings' table
                        │
                        └── OUTPUT: List of top 5 listing_ids
                              │
                              └── FOR EACH listing_id IN top_5_listings:
                                  │
                                  ├── TRIGGER ──> Locality_Review_Agent
                                  │                 │ (Input: listing_id)
                                  │                 ├── QUERIES BigQuery 'listings' & 'neighborhoods'
                                  │                 └── OUTPUT: locality_data (school, crime, aqi, etc.)
                                  │
                                  ├── TRIGGER ──> Hazard_Analysis_Agent
                                  │                 │ (Input: listing_id)
                                  │                 ├── QUERIES BigQuery 'listings' & 'neighborhoods'
                                  │                 └── OUTPUT: hazard_data (flood, tornado, etc.)
                                  │
                                  └── TRIGGER ──> Affordability_Agent
                                                    │ (Input: listing_id, user_financial_info/defaults)
                                                    ├── QUERIES BigQuery 'listings' & 'affordability_params'
                                                    └── OUTPUT: affordability_summary (monthly_payment, etc.)
                                                          │
                                                          │ (Collect all outputs for this listing_id)
                                                          ▼
                                  COLLECT_RESULTS_FOR_ALL_5_LISTINGS
                                      │
                                      └── TRIGGER ──> Recommendation_Agent
                                                          │ (Input: Aggregated data for top 5 listings, user priorities)
                                                          ├── PROCESSES all inputs
                                                          ├── (Optional: CALLS Vertex AI Gemini for report generation)
                                                          └── OUTPUT: Final recommendation report (text/JSON)