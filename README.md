# Multi-Agent Home Buying Application

A sophisticated multi-agent home buying application built using the **Google Agent Development Kit (ADK) framework**. This application demonstrates advanced agent composition, workflow orchestration, and inter-agent communication using real data integration with BigQuery and Vertex AI.

## 🎯 Overview

This application demonstrates a complete multi-agent system for home buying that coordinates **5 specialized agents** to help users find, analyze, and get personalized recommendations for property listings. The system successfully processes real estate data, performs vector similarity search, and provides comprehensive property analysis.

### ✨ Key Achievements

- **🏠 100% Success Rate**: All 5 test scenarios consistently succeed with comprehensive property analysis
- **🔍 Advanced Vector Search**: Semantic property search using Vertex AI text-embedding-004 (768 dimensions)
- **🤖 Multi-Agent Orchestration**: 5 specialized agents working in parallel for complete analysis
- **📊 Real Data Integration**: Live BigQuery data with 20+ property listings and vector embeddings
- **🎯 Personalized Recommendations**: User priority-based scoring with detailed property writeups
- **⚡ Enhanced Performance**: Increased vector search results from 5 to 15 for better property discovery

### 🏗️ Architecture Overview

```
HomeBuyingOrchestrator
├── 📋 ListingReviewAgent (Vector search & filtering)
├── 🏘️ LocalityReviewAgent (Neighborhood analysis)  
├── ⚠️ HazardAnalysisAgent (Risk assessment)
├── 💰 AffordabilityAgent (Financial analysis)
└── 🎯 RecommendationAgent (Scoring & recommendations)
```

### 🔄 Workflow Execution

```
User Criteria → 
  📋 Find Properties (Vector Search) →
  🔄 Parallel Analysis:
    🏘️ Locality (Schools, Safety, Demographics)
    ⚠️ Hazards (Wildfire, Flood, Natural Disasters)  
    💰 Affordability (Monthly Payments, DTI)
  → 🎯 Generate Personalized Recommendations
→ 📊 Ranked Results with Detailed Explanations
```

## 📁 Project Structure

```
c:\github\ADKAgent\
├── agents/                     # Specialized agent implementations
│   ├── base_agent.py          # Base agent class with common functionality
│   ├── listing_review_agent.py # Vector search and property filtering
│   ├── locality_review_agent.py # Neighborhood analysis
│   ├── hazard_analysis_agent.py # Risk assessment
│   ├── affordability_agent.py  # Financial analysis
│   ├── recommendation_agent.py # Scoring and recommendations
│   ├── agent_utils.py         # Shared utilities (BigQuery, etc.)
│   └── vector_search_utils.py # Vector search and embeddings
├── config/
│   ├── settings.py            # Configuration management
│   ├── listings.csv           # Sample listings data
│   ├── neighborhoods.csv      # Sample neighborhood data
│   └── affordability_params.json # Financial calculation parameters
├── frontend/                   # React web application
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── SearchForm.js  # Property search form
│   │   │   ├── ProgressTracker.js # Analysis progress display
│   │   │   └── RecommendationResults.js # Results display
│   │   ├── services/
│   │   │   └── api.js         # API client for backend communication
│   │   ├── App.js             # Main React application
│   │   └── index.js           # React entry point
│   ├── public/                # Static assets
│   ├── package.json           # Node.js dependencies
│   ├── Dockerfile            # Frontend container configuration
│   └── README.md             # Frontend documentation
├── deploy/                    # Deployment configurations
│   ├── deploy.sh             # Linux/Mac deployment script
│   ├── deploy.ps1            # Windows PowerShell deployment script
│   └── README.md             # Deployment guide
├── orchestrator_adk.py       # Main ADK-compliant orchestrator implementation
├── api_server.py             # Flask API server for frontend
├── main.py                   # Application entry point
├── test_end_to_end.py       # Comprehensive end-to-end tests
├── docker-compose.yml        # Multi-container orchestration
├── pyproject.toml           # Python package configuration
└── README.md               # This documentation
```

## 🌐 Frontend Application

### ✨ Modern React Interface

The project includes a **modern React frontend** that provides an intuitive web interface for the AI-powered home buying assistant:

- **🔍 Intelligent Search Form**: Comprehensive property search with financial criteria and priorities
- **📊 Real-time Progress Tracking**: Visual feedback showing AI agents working in parallel
- **🏠 Beautiful Results Display**: Modern cards with detailed property analysis and scoring
- **📱 Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **☁️ Cloud-Ready**: Optimized for Google Cloud Run deployment

### 🏗️ Full-Stack Architecture

```
React Frontend → Flask API Server → ADK Orchestrator → Multi-Agent System
     ↓               ↓                    ↓                  ↓
  User Interface → REST API → Workflow Coordination → AI Analysis
```

### 🚀 Quick Start - Frontend

1. **Install Dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start Development Servers**:
   ```bash
   # Terminal 1: Backend API
   python api_server.py
   
   # Terminal 2: Frontend Development Server
   cd frontend
   npm start
   ```
   
3. **Access Application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

### ☁️ One-Click Cloud Deployment

Deploy to Google Cloud Run with a single command:

**Windows**:
```powershell
$env:GOOGLE_CLOUD_PROJECT = "your-project-id"
.\deploy\deploy.ps1
```

**Linux/Mac**:
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
./deploy/deploy.sh
```

The deployment script automatically:
- ✅ Builds and deploys backend service
- ✅ Builds and deploys frontend service  
- ✅ Configures environment variables
- ✅ Sets up load balancing and scaling
- ✅ Provides deployment URLs

### 📋 User Experience Flow

1. **Search Form**: Users enter property preferences, financial information, and priorities
2. **Progress Tracking**: Real-time visualization of AI agents working:
   - 🔍 Finding properties (Vector search)
   - 🏘️ Analyzing localities (Demographics, schools)
   - ⚠️ Assessing hazards (Safety, environmental risks)
   - 💰 Calculating affordability (Monthly costs, DTI ratios)
   - 🎯 Generating recommendations (Personalized scoring)
3. **Results Display**: Comprehensive property recommendations with:
   - Property details and descriptions
   - Analysis breakdowns with visual scores
   - Pros and cons for each recommendation
   - AI-generated recommendation summaries

### 🎨 Modern UI Features

- **Glass Morphism Design**: Beautiful translucent cards with backdrop blur effects
- **Ant Design Components**: Professional UI components with consistent styling
- **Progressive Enhancement**: Optimized loading and error states
- **Accessible Design**: WCAG AA compliant color contrast and navigation

## ✨ Key Features

### 🔍 **Advanced Vector Search**
- **Semantic Understanding**: Uses Vertex AI text-embedding-004 model with 768-dimensional embeddings
- **Enhanced Discovery**: Returns up to 15 relevant listings for better filtering and selection
- **Real-time Processing**: Dot product similarity matching with live BigQuery integration
- **Smart Filtering**: Combines vector similarity with user criteria for precise property matching

### 🤖 **Multi-Agent Intelligence** 
- **Parallel Processing**: Concurrent analysis across locality, hazard, and affordability domains
- **Specialized Expertise**: Each agent focuses on specific analysis areas
- **Coordinated Workflow**: Seamless data sharing between agents

### 💰 **Comprehensive Financial Analysis**
- **Mortgage Calculations**: Detailed monthly payment breakdowns
- **Affordability Assessment**: Debt-to-income ratio analysis
- **Market Context**: Property value evaluation and investment insights

### ⚠️ **Risk Assessment**
- **Natural Hazards**: Wildfire, flood, earthquake risk evaluation
- **FEMA Integration**: Official flood zone designations
- **Insurance Analysis**: Required coverage and cost implications

### 🎯 **Personalized Recommendations**
- **User Priority Alignment**: Scoring based on individual preferences
- **Detailed Explanations**: Why each property fits the user's needs
- **Comprehensive Writeups**: Investment summaries and key strengths

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
- Google Cloud SDK 
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
   pip install google-adk google-cloud-bigquery python-dotenv numpy pydantic
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

The system generates comprehensive property recommendations with detailed analysis:

```
🏆 FINAL HOME BUYING RECOMMENDATIONS
================================================================================

📊 SUMMARY:
Total listings analyzed: 14
Top recommendations: 3

🏠 #1 Recommendation - 2424 Chestnut Ln
   💰 Price: $450,000 | Score: 10/10 | 2BR/2.0BA
   🏡 1,250 sq ft | Built 2018 | Condo
   
   ✅ Key Strengths:
   • Property meets basic search criteria
   • Good schools in area (6/10 rating)
   • Safe neighborhood (6.0/10 safety score)
   • Good environmental quality
   • Low wildfire risk
   • Matches your priorities: modern amenities
   
   💰 Financial Analysis:
   • Estimated monthly payment: $2,912.94
   • Flood risk: Medium (FEMA designation)
   • Insurance considerations included
   
   � Investment Summary:
   At $450,000, this property offers strong value in today's market 
   and represents a sound investment for your future.

🏠 #2 Recommendation - 777 Birch Ln
   💰 Price: $480,000 | Score: 8/10 | 2BR/2.0BA
   🏡 Similar comprehensive analysis...
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

### Google ADK Framework

The application uses the official **Google Agent Development Kit (ADK)** Python package:
- **Agent Classes**: `Agent`, `LlmAgent`, `SequentialAgent`, `ParallelAgent` from `google.adk.agents`
- **Tool System**: `FunctionTool` for wrapping functions and integrating tools
- **Session Management**: `InMemorySessionService`, `Runner` for execution and state management
- **Context Management**: `InvocationContext` for execution context
- **Schema Validation**: Pydantic `BaseModel` schemas for input/output validation

### Extending the System

1. **Add new agents**: Create `LlmAgent` instances with appropriate tools, input schemas, and instructions
2. **Add new tools**: Create functions and wrap with `FunctionTool` 
3. **Modify workflow**: Update orchestrator patterns in `orchestrator_adk.py` using `SequentialAgent` and `ParallelAgent`
4. **Add data sources**: Extend `agent_utils.py` and vector search capabilities

### Architecture Patterns

The system implements these ADK patterns:
- **Sequential Pipeline**: Main workflow execution through `SequentialAgent`
- **Parallel Fan-Out/Gather**: Concurrent analysis using `ParallelAgent`
- **Tool Integration**: Function tools for external system integration
- **Session State Management**: Shared context across agent interactions

## Configuration

Key settings in `config/settings.py`:

- `DEFAULT_AGENT_MODEL`: Model for individual agents (default: gemini-1.5-flash-latest)
- `ORCHESTRATOR_MODEL`: Model for orchestrator (default: gemini-1.5-pro-latest) 
- `VECTOR_SEARCH_LIMIT`: Number of listings to find (default: 15, optimized for better discovery)
- `FINAL_RECOMMENDATION_COUNT`: Top recommendations to show (default: 3)

### Recent Performance Improvements

- **Vector Search Optimization**: Increased search limit from 5 to 15 listings for better property discovery
- **Enhanced Test Coverage**: 5 comprehensive scenarios with 100% success rate
- **Improved Embeddings**: Using Vertex AI text-embedding-004 model with 768-dimensional vectors
- **Better Filtering**: More intelligent property filtering based on user criteria

## Testing & Validation

### End-to-End Test Results

The system has been thoroughly tested with comprehensive scenarios:

| Test Scenario | Status | Listings Analyzed | Recommendations |
|---------------|--------|-------------------|----------------|
| Young Professional - Urban | ✅ | 14 | 3 |
| Growing Family - Suburban | ✅ | 7 | 3 |
| First-Time Buyer - Budget | ✅ | 8 | 3 |
| Luxury Buyer - Premium | ✅ | 7 | 3 |
| Retiree - Low Maintenance | ✅ | 14 | 3 |

**Overall Success Rate: 100%**

Each test validates the complete workflow from vector search through multi-agent analysis to final recommendations.

### Running Tests

```bash
# Run comprehensive end-to-end tests
python test_end_to_end.py

# Run specific vector search tests
python test_vector_search.py

# Test BigQuery schema and connections
python test_schema.py
```

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
- Built for educational and demonstration purposes showcasing multi-agent AI systems
- Uses real BigQuery data with vector embeddings for production-like testing
- Demonstrates integration of Vertex AI, BigQuery, and advanced orchestration patterns

---

*Last Updated: January 2025 | System Status: ✅ All tests passing | Performance: 100% success rate*
