# ADK Multi-Agent Home Buying Application

A sophisticated multi-agent home buying application built using **Google's Agent Development Kit (ADK)** official patterns and best practices. This application demonstrates advanced agent composition, workflow orchestration, and inter-agent communication following the official ADK multi-agent documentation.

## Overview

This application demonstrates a complete multi-agent system for home buying that coordinates specialized agents to help users find, analyze, and get recommendations for property listings using **official ADK patterns**.

### ADK Architecture Patterns

The system implements the following **official ADK multi-agent patterns**:

- **Agent Hierarchy**: Parent-child relationships with proper `sub_agents` composition
- **Sequential Pipeline Pattern**: Uses `SequentialAgent` for step-by-step workflow execution
- **Parallel Fan-Out/Gather Pattern**: Uses `ParallelAgent` for concurrent analysis
- **Shared Session State Communication**: Agents communicate via `ctx.session.state`
- **Workflow Agents as Orchestrators**: Proper use of ADK workflow agents
- **LLM Agent with Tools**: `LlmAgent` with `FunctionTool` integration

### Architecture Overview

```
ADKHomeBuyingOrchestrator (SequentialAgent)
├── ListingReviewAgent (finds properties using vector search)
├── MultiListingProcessor (processes each listing)
│   └── ListingAnalyzer (analyzes individual listings)
│       └── ParallelListingAnalyzer (ParallelAgent)
│           ├── LocalityReviewAgent (neighborhood analysis)
│           ├── HazardAnalysisAgent (disaster risk assessment)
│           └── AffordabilityAgent (financial analysis)
└── RecommendationAgent (generates final recommendations)
```

### ADK Communication Patterns

1. **Session State Flow**: Each agent reads from and writes to `ctx.session.state`
2. **Output Keys**: LLM agents use `output_key` to automatically save results
3. **Branch Contexts**: Parallel agents create proper branch contexts
4. **Event Streaming**: All agents implement proper `Event` streaming

### Specialized Agents

1. **ListingReviewAgent**: Finds property listings using semantic vector search with embeddings
2. **LocalityReviewAgent**: Analyzes neighborhood data (schools, crime, amenities, demographics)
3. **HazardAnalysisAgent**: Assesses natural disaster risks (flood, fire, earthquake, wildfire)
4. **AffordabilityAgent**: Calculates mortgage payments and affordability ratios
5. **RecommendationAgent**: Generates ranked recommendations with pros/cons analysis

### ADK Workflow Execution

```
User Input → 
SequentialAgent:
  1. ListingReviewAgent (finds listings) →
  2. MultiListingProcessor:
       For each listing → ListingAnalyzer → ParallelAgent:
         - LocalityReviewAgent
         - HazardAnalysisAgent  
         - AffordabilityAgent
  3. RecommendationAgent (final recommendations)
→ Final Report
```

## Project Structure

```
c:\github\ADKAgent\
├── agents/                     # Individual agent implementations
│   ├── base_agent.py          # Base class following ADK patterns
│   ├── listing_review_agent.py
│   ├── locality_review_agent.py
│   ├── hazard_analysis_agent.py
│   ├── affordability_agent.py
│   ├── recommendation_agent.py
│   ├── agent_utils.py         # Shared utilities (BigQuery, etc.)
│   └── vector_search_utils.py # Vector search and embeddings
├── config/
│   └── settings.py            # Configuration management
├── mock_adk.py               # Mock ADK framework for development
├── orchestrator.py           # Legacy orchestrator
├── orchestrator_adk.py       # ADK-compliant orchestrator (NEW)
├── main.py                   # Application entry point
├── pyproject.toml           # Python package configuration
└── README.md               # This file
```

## Features

- **Vector Similarity Search**: Semantic search for property listings using embeddings
- **Concurrent Analysis**: Parallel processing of locality, hazard, and affordability analysis
- **Financial Calculations**: Comprehensive affordability analysis including DTI ratios
- **Risk Assessment**: Natural hazard risk evaluation by location
- **Intelligent Recommendations**: Scored recommendations based on user priorities
- **Mock Data Support**: Runs with mock data for development/demonstration

## 🔐 Security and Configuration

### Important Security Notes

⚠️ **NEVER commit sensitive credentials to version control!**

This project includes comprehensive protection against accidental credential exposure:

- **`.env` file**: Contains sensitive BigQuery and Google Cloud credentials - automatically ignored by git
- **`.env.example`**: Template file showing required environment variables (safe to commit)
- **`.gitignore`**: Comprehensive exclusions for credentials, keys, and sensitive files

### Setting Up Environment Variables

1. **Copy the template**:
   ```bash
   cp .env.example .env
   ```

2. **Update `.env` with your actual values**:
   ```bash
   # Replace placeholder values with your real credentials
   GOOGLE_CLOUD_PROJECT=your-actual-project-id
   BIGQUERY_DATASET=your-actual-dataset-name
   # ... etc
   ```

3. **Verify security**: Ensure `.env` is never committed:
   ```bash
   git status  # .env should NOT appear in tracked files
   ```

### Protected Files

The following file types are automatically excluded from version control:
- Environment files (`.env`, `.env.*`)
- Google Cloud credentials (`*.json`, service account keys)
- API keys and secrets (`*.key`, `*.token`)
- Database files (`*.db`, `*.sqlite`)
- Backup and cache files

## Setup

### Prerequisites

- Python 3.8+
- Google Cloud SDK (optional, for real BigQuery data)
- Virtual environment (recommended)

### Installation

1. **Clone and setup**:
   ```bash
   cd c:\github\ADKAgent
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -e .
   ```

2. **Install dependencies**:
   ```bash
   pip install google-cloud-bigquery python-dotenv numpy
   ```

3. **Configure environment**:
   ```bash
   # Copy the template and update with your credentials
   cp .env.example .env
   # Edit .env with your actual BigQuery project details
   ```

## Usage

### Run the Application

```bash
python main.py
```

The application will:
1. Initialize the multi-agent orchestrator
2. Process sample user criteria 
3. Execute the complete workflow
4. Display ranked property recommendations

### Sample Output

```
🏆 FINAL HOME BUYING RECOMMENDATIONS
================================================================================

📊 SUMMARY:
Total listings analyzed: 3
Top recommendations: 3

🏠 #1 Recommendation - 123 Main St, Anytown
   💰 Price: $450,000 | Score: 8
   🏡 3 bed, 2.0 bath
   ✅ Pros: Good school rating, Low crime area, Financially affordable
   
🏠 #2 Recommendation - 456 Oak Ave, Anytown  
   💰 Price: $520,000 | Score: 6
   🏡 4 bed, 3.0 bath
   ✅ Pros: Low flood risk, Matches priority: large backyard
```

## ADK Patterns Used

### 1. Agent Hierarchy
- Clear parent-child relationships with `sub_agents`
- Single parent rule enforcement
- Agent discovery with `find_agent()`

### 2. Sequential Pipeline Pattern
```python
main_workflow = SequentialAgent(
    name="HomeBuyingWorkflow",
    sub_agents=[
        listing_agent,
        parallel_analysis_agent, 
        recommendation_agent
    ]
)
```

### 3. Parallel Fan-Out/Gather Pattern  
```python
parallel_analysis_agent = ParallelAgent(
    name="ParallelAnalysisAgent",
    sub_agents=[
        locality_agent,
        hazard_agent,
        affordability_agent
    ]
)
```

### 4. Shared Session State
```python
# Agents write to shared state
ctx.session.state["found_listings"] = listings
ctx.session.state["locality_analysis"] = analysis

# Other agents read from shared state
listings = ctx.session.state.get("found_listings")
```

### 5. Function Tools
```python
@FunctionTool
def find_listings_by_criteria(user_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Tool implementation
    pass
```

## Development

### Mock Framework

The `mock_adk.py` provides a complete simulation of ADK components:
- `BaseAgent`, `LlmAgent`, `SequentialAgent`, `ParallelAgent`
- `FunctionTool`, `AgentTool` 
- `InvocationContext`, `Event`, `EventActions`

### Extending the System

1. **Add new agents**: Inherit from `HomeBuyerBaseAgent`
2. **Add new tools**: Create functions and wrap with `FunctionTool`
3. **Modify workflow**: Update orchestrator patterns
4. **Add data sources**: Extend `agent_utils.py`

### Real ADK Integration

To use with real ADK:
1. Replace `mock_adk` imports with `google.adk`
2. Configure proper ADK authentication
3. Update BigQuery credentials
4. Replace mock data with real data sources

## Configuration

Key settings in `config/settings.py`:

- `DEFAULT_AGENT_MODEL`: Model for individual agents (default: gemini-1.5-flash-latest)
- `ORCHESTRATOR_MODEL`: Model for orchestrator (default: gemini-1.5-pro-latest) 
- `VECTOR_SEARCH_LIMIT`: Number of listings to find (default: 5)
- `FINAL_RECOMMENDATION_COUNT`: Top recommendations to show (default: 3)

## Data Requirements

For production use with real BigQuery:

### Listings Table
- `listing_id`, `description`, `price`, `bedrooms`, `bathrooms`
- `address`, `neighborhood`
- `description_embedding` (ARRAY<FLOAT64>) for vector search

### Neighborhoods Table  
- `neighborhood_name`, `school_rating`, `crime_rate`
- `flood_risk_level`, `wildfire_risk_level`, etc.

### Affordability Parameters Table
- `interest_rate`, `loan_term_years`, `property_tax_rate`
- `home_insurance_annual`, `down_payment_percentage`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## Acknowledgments

- Inspired by Google's Agent Development Kit (ADK) patterns and best practices
- Built for educational and demonstration purposes
- Uses synthetic data for safe development and testing
