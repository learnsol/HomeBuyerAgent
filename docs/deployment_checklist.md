# Production Deployment Checklist

## Pre-Deployment Preparation

### ✅ Code Cleanup
- [x] Removed test files (`quick_firestore_test.py`, `test_query.json`, `validate_firestore_setup.py`)
- [x] Removed old query history data (`query_history.json`)
- [x] Updated all imports to use cloud-ready components
- [x] Added proper error handling and logging
- [x] Verified no development dependencies in production requirements

### ✅ Configuration
- [x] Environment variables properly set in `.env`
- [x] Google Cloud project configured
- [x] Firestore database created and operational
- [x] BigQuery datasets and tables verified
- [x] API endpoints tested and working
- [x] CORS configured for production domains

### ✅ Security
- [x] Sensitive data in environment variables (not hardcoded)
- [x] Service account permissions minimal and appropriate
- [x] API input validation implemented
- [x] Error messages sanitized (no sensitive info leaked)
- [x] HTTPS enforced (Cloud Run default)

## Cloud Infrastructure Setup

### Google Cloud Project Setup
```bash
# Set up the project
gcloud config set project gen-lang-client-0044046698

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable aiplatform.googleapis.com
```

### Firestore Database
- [x] Database created in us-central1 region
- [x] Native mode selected
- [x] Security rules configured (if needed)
- [x] Collections properly indexed

### BigQuery Setup
- [x] Dataset: `home_buyer_hackathon_data`
- [x] Tables: `listings`, `neighborhoods`, `affordability_parameters`
- [x] Proper IAM permissions for Cloud Run service account
- [x] Data loaded and verified

## Deployment Steps

### 1. Container Preparation
```bash
# Build the container image
docker build -t gcr.io/gen-lang-client-0044046698/adk-home-buyer .

# Test locally
docker run -p 8000:8000 --env-file .env gcr.io/gen-lang-client-0044046698/adk-home-buyer

# Push to Google Container Registry
docker push gcr.io/gen-lang-client-0044046698/adk-home-buyer
```

### 2. Cloud Run Deployment
```bash
# Deploy to Cloud Run
gcloud run deploy adk-home-buyer \
  --image gcr.io/gen-lang-client-0044046698/adk-home-buyer \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=gen-lang-client-0044046698 \
  --set-env-vars QUERY_HISTORY_BACKEND=firestore \
  --set-env-vars ENABLE_QUERY_HISTORY=true \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10 \
  --port 8000
```

### 3. Frontend Deployment
```bash
# Build React frontend
cd frontend
npm run build

# Deploy to Firebase Hosting, Netlify, or other static host
# Update API_BASE_URL to point to Cloud Run service
```

## Post-Deployment Verification

### ✅ Health Checks
- [ ] API health endpoint responding: `GET /api/health`
- [ ] Backend status endpoint working: `GET /api/history/status`
- [ ] Sample analysis request successful: `POST /api/analyze`
- [ ] Firestore query history being saved
- [ ] BigQuery queries executing successfully
- [ ] Vertex AI models responding

### ✅ Performance Testing
- [ ] Load testing with multiple concurrent requests
- [ ] Response times under acceptable thresholds
- [ ] Auto-scaling working properly
- [ ] Memory and CPU usage within limits

### ✅ Monitoring Setup
- [ ] Cloud Logging configured and working
- [ ] Error alerting set up
- [ ] Performance monitoring enabled
- [ ] Uptime checks configured

## Environment Variables for Production

### Required Environment Variables
```bash
# Core Configuration
GOOGLE_CLOUD_PROJECT=gen-lang-client-0044046698
PORT=8000

# Query History
QUERY_HISTORY_BACKEND=firestore
FIRESTORE_COLLECTION=query_history
ENABLE_QUERY_HISTORY=true
MAX_HISTORY_ENTRIES=50

# BigQuery Configuration
BIGQUERY_DATASET=home_buyer_hackathon_data
BIGQUERY_LOCATION=northamerica-northeast2
LISTINGS_TABLE=listings
NEIGHBORHOODS_TABLE=neighborhoods

# Vertex AI Configuration
VERTEX_AI_LOCATION=us-central1
DEFAULT_AGENT_MODEL=gemini-2.0-flash-001
ORCHESTRATOR_MODEL=gemini-2.0-flash-001
EMBEDDING_MODEL_NAME=text-embedding-004

# Feature Flags
USE_MOCK_DATA=false
```

## Rollback Plan

### In case of deployment issues:
1. **Immediate Rollback**: Use Cloud Run revisions to rollback to previous version
   ```bash
   gcloud run services update-traffic adk-home-buyer --to-revisions=PREVIOUS_REVISION=100
   ```

2. **Database Issues**: Firestore has automatic backups, BigQuery has versioned tables

3. **Configuration Issues**: Update environment variables without redeployment
   ```bash
   gcloud run services update adk-home-buyer --set-env-vars KEY=VALUE
   ```

## Maintenance Procedures

### Regular Tasks
- [ ] Monitor Cloud Run logs for errors
- [ ] Review Firestore usage and clean up old queries if needed
- [ ] Monitor BigQuery costs and optimize queries
- [ ] Update dependencies monthly
- [ ] Review and rotate service account keys (if applicable)

### Scaling Considerations
- [ ] Monitor request patterns and adjust instance limits
- [ ] Consider regional deployment for global users
- [ ] Optimize database queries for performance
- [ ] Implement caching if needed

## Success Criteria

✅ **Deployment is successful when:**
- API responds to health checks
- Frontend can connect to API
- Property searches return results
- Query history is being saved to Firestore
- No errors in Cloud Run logs
- Response times < 10 seconds for analysis requests
- System handles multiple concurrent users

## Support Contacts

- **Development Team**: [Your team contact]
- **Google Cloud Support**: [Your support plan]
- **Incident Response**: [Your on-call procedures]

---

**Deployment Date**: ________________  
**Deployed By**: ___________________  
**Version**: ______________________  
**Rollback Plan Tested**: ✅ / ❌
