# ADK Home Buyer Application - Cloud Deployment Architecture

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │
│  │   React Web     │  │   Mobile Web    │  │   Future Apps   │          │
│  │   Frontend      │  │   (Responsive)  │  │   (iOS/Android) │          │
│  │   Port: 3000    │  │                 │  │                 │          │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘          │
│           │                     │                     │                    │
│           └─────────────────────┼─────────────────────┘                    │
│                                 │                                          │
└─────────────────────────────────┼──────────────────────────────────────────┘
                                  │
                                  │ HTTPS / REST API
                                  │
┌─────────────────────────────────┼──────────────────────────────────────────┐
│                            API GATEWAY                                     │
├─────────────────────────────────┼──────────────────────────────────────────┤
│                                 │                                          │
│  ┌─────────────────────────────┴──────────────────────────────────────┐   │
│  │                    Google Cloud Run                                │   │
│  │                 ADK Home Buyer API Server                          │   │
│  │                     Port: 8000                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐  │   │
│  │  │               Flask Application                              │  │   │
│  │  │  • /api/health - Health check                               │  │   │
│  │  │  • /api/analyze - Main analysis endpoint                    │  │   │
│  │  │  • /api/history - Query history retrieval                   │  │   │
│  │  │  • /api/history/status - Backend status                     │  │   │
│  │  └─────────────────────────────────────────────────────────────┘  │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐  │   │
│  │  │            ADK Orchestrator Engine                          │  │   │
│  │  │  • Sequential & Parallel Agent Coordination                 │  │   │
│  │  │  • Session Management                                       │  │   │
│  │  │  • Multi-Agent Workflow Execution                          │  │   │
│  │  └─────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  │
┌─────────────────────────────────┼──────────────────────────────────────────┐
│                           AGENT LAYER                                      │
├─────────────────────────────────┼──────────────────────────────────────────┤
│                                 │                                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │
│  │  Listing Review │  │ Affordability   │  │ Locality Review │          │
│  │     Agent       │  │     Agent       │  │     Agent       │          │
│  │                 │  │                 │  │                 │          │
│  │ • Find listings │  │ • Calculate     │  │ • Neighborhood  │          │
│  │ • Vector search │  │   affordability │  │   analysis      │          │
│  │ • Filter by     │  │ • Financial     │  │ • Walkability   │          │
│  │   criteria      │  │   validation    │  │ • Amenities     │          │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘          │
│                                                                            │
│  ┌─────────────────┐  ┌─────────────────┐                                │
│  │ Hazard Analysis │  │ Recommendation  │                                │
│  │     Agent       │  │     Agent       │                                │
│  │                 │  │                 │                                │
│  │ • Safety risks  │  │ • Aggregate     │                                │
│  │ • Environmental │  │   analysis      │                                │
│  │   hazards       │  │ • Generate      │                                │
│  │ • Risk scoring  │  │   rankings      │                                │
│  └─────────────────┘  └─────────────────┘                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  │
┌─────────────────────────────────┼──────────────────────────────────────────┐
│                           DATA LAYER                                       │
├─────────────────────────────────┼──────────────────────────────────────────┤
│                                 │                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                        Google BigQuery                              │  │
│  │                                                                     │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │  │
│  │  │    Listings     │  │  Neighborhoods  │  │ Affordability   │   │  │
│  │  │     Table       │  │     Table       │  │   Parameters    │   │  │
│  │  │                 │  │                 │  │     Table       │   │  │
│  │  │ • Property data │  │ • Area features │  │ • Income ratios │   │  │
│  │  │ • Embeddings    │  │ • Demographics  │  │ • Market data   │   │  │
│  │  │ • Pricing       │  │ • Amenities     │  │ • Risk factors  │   │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘   │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                      Google Cloud Firestore                        │  │
│  │                                                                     │  │
│  │  ┌─────────────────────────────────────────────────────────────┐   │  │
│  │  │                  Query History Collection                   │   │  │
│  │  │                                                             │   │  │
│  │  │ • User search criteria                                      │   │  │
│  │  │ • Analysis results                                          │   │  │
│  │  │ • Session tracking                                          │   │  │
│  │  │ • Performance metrics                                       │   │  │
│  │  │ • Automatic scaling & backup                                │   │  │
│  │  └─────────────────────────────────────────────────────────────┘   │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  │
┌─────────────────────────────────┼──────────────────────────────────────────┐
│                            AI LAYER                                        │
├─────────────────────────────────┼──────────────────────────────────────────┤
│                                 │                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                        Google Vertex AI                            │  │
│  │                                                                     │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │  │
│  │  │ Gemini 2.0 Flash│  │ Text Embedding  │  │   Future AI     │   │  │
│  │  │     Models      │  │      004        │  │    Models       │   │  │
│  │  │                 │  │                 │  │                 │   │  │
│  │  │ • Agent LLMs    │  │ • Vector search │  │ • Enhanced      │   │  │
│  │  │ • Analysis      │  │ • Semantic      │  │   capabilities  │   │  │
│  │  │ • Orchestration │  │   matching      │  │ • Specialized   │   │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘   │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend Layer
- **React Application**: Modern, responsive web interface
- **Features**: Search forms, results display, progress tracking
- **Deployment**: Static hosting (Firebase Hosting, Netlify, or CDN)

### API Gateway & Application Layer
- **Google Cloud Run**: Serverless container platform
- **Flask API Server**: RESTful API with CORS support
- **ADK Orchestrator**: Google ADK-compliant agent coordination
- **Auto-scaling**: 0-to-N instances based on demand
- **Health Monitoring**: Built-in health checks and logging

### Agent Architecture (Google ADK)
- **Sequential Processing**: Listing discovery → Analysis → Recommendations
- **Parallel Analysis**: Multiple property aspects analyzed concurrently
- **Session Management**: User state tracking across requests
- **Modular Design**: Each agent handles specific domain expertise

### Data Storage
- **BigQuery**: Primary data warehouse for listings and reference data
- **Firestore**: Real-time query history and session data
- **Vector Search**: Semantic similarity matching for property discovery

### AI/ML Layer
- **Vertex AI Integration**: Managed AI platform
- **Gemini Models**: Latest LLMs for intelligent analysis
- **Embedding Models**: Text-to-vector conversion for search
- **Cost Optimization**: Efficient model usage patterns

## Deployment Characteristics

### Scalability
- **Horizontal Scaling**: Cloud Run auto-scales based on traffic
- **Database Scaling**: BigQuery and Firestore handle any load
- **Cost Efficiency**: Pay-per-use model with generous free tiers

### Security
- **IAM Integration**: Google Cloud Identity and Access Management
- **API Security**: CORS, input validation, rate limiting
- **Data Encryption**: At rest and in transit
- **Private Networking**: VPC connectivity for sensitive operations

### Monitoring & Observability
- **Cloud Logging**: Centralized log aggregation
- **Cloud Monitoring**: Performance metrics and alerting
- **Error Tracking**: Automated error detection and reporting
- **Query History**: User behavior analytics and debugging

### Disaster Recovery
- **Multi-Region**: Automatic data replication
- **Backup Strategy**: Automated BigQuery and Firestore backups
- **Rollback Capability**: Container versioning for quick rollbacks
- **Health Checks**: Automatic failover and recovery

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | React + JavaScript | User interface |
| API | Flask + Python | REST API server |
| Orchestration | Google ADK | Agent coordination |
| Compute | Google Cloud Run | Serverless containers |
| Database | Google BigQuery | Data warehouse |
| Real-time DB | Google Firestore | Query history |
| AI/ML | Google Vertex AI | LLMs and embeddings |
| Monitoring | Google Cloud Ops | Logging & monitoring |

## Deployment Benefits

✅ **Serverless**: No infrastructure management  
✅ **Scalable**: Auto-scales from 0 to millions of users  
✅ **Cost-Effective**: Pay only for actual usage  
✅ **Reliable**: 99.95% uptime SLA  
✅ **Secure**: Enterprise-grade security  
✅ **Observable**: Built-in monitoring and logging  
✅ **Maintainable**: Clean separation of concerns  
✅ **Future-Ready**: Easy to extend and modify  
