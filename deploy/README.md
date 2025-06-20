# 🚀 Deployment Guide - ADK Home Buyer Application

This guide covers deploying the full-stack ADK Home Buyer application to Google Cloud Run.

## 📋 Prerequisites

### Required Tools
- **Google Cloud SDK** (gcloud CLI)
- **Docker** (for local testing)
- **Node.js 18+** (for frontend development)
- **Python 3.11+** (for backend)

### Google Cloud Setup
1. **Create/Select Project**:
   ```bash
   gcloud projects create your-project-id
   gcloud config set project your-project-id
   ```

2. **Enable Billing**:
   - Go to Google Cloud Console
   - Enable billing for your project

3. **Enable APIs**:
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   gcloud services enable artifactregistry.googleapis.com
   gcloud services enable bigquery.googleapis.com
   gcloud services enable aiplatform.googleapis.com
   ```

## 🔧 Environment Configuration

### 1. Set Environment Variables

**Windows (PowerShell)**:
```powershell
$env:GOOGLE_CLOUD_PROJECT = "your-project-id"
$env:GOOGLE_CLOUD_REGION = "us-central1"
$env:BIGQUERY_PROJECT_ID = "your-project-id"
$env:VERTEX_AI_PROJECT_ID = "your-project-id"
$env:VERTEX_AI_LOCATION = "us-central1"
```

**Linux/Mac (Bash)**:
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_REGION="us-central1"
export BIGQUERY_PROJECT_ID="your-project-id"
export VERTEX_AI_PROJECT_ID="your-project-id"
export VERTEX_AI_LOCATION="us-central1"
```

### 2. Create .env File
```bash
# Copy environment template
cp .env.example .env

# Edit with your values
GOOGLE_CLOUD_PROJECT=your-project-id
BIGQUERY_PROJECT_ID=your-project-id
VERTEX_AI_PROJECT_ID=your-project-id
VERTEX_AI_LOCATION=us-central1
```

## 🚀 Deployment Options

### Option 1: One-Click Deployment (Recommended)

**Windows**:
```powershell
.\deploy\deploy.ps1
```

**Linux/Mac**:
```bash
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

This script will:
- ✅ Validate authentication and project setup
- ✅ Enable required Google Cloud APIs
- ✅ Build and deploy backend service
- ✅ Build and deploy frontend service
- ✅ Configure environment variables
- ✅ Display deployment URLs

### Option 2: Manual Step-by-Step Deployment

#### Step 1: Deploy Backend
```bash
gcloud run deploy adk-home-buyer-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --concurrency 10 \
  --max-instances 5 \
  --set-env-vars "FLASK_ENV=production,PORT=8000,GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,BIGQUERY_PROJECT_ID=$BIGQUERY_PROJECT_ID,VERTEX_AI_PROJECT_ID=$VERTEX_AI_PROJECT_ID,VERTEX_AI_LOCATION=$VERTEX_AI_LOCATION" \
  --port 8000
```

#### Step 2: Get Backend URL
```bash
BACKEND_URL=$(gcloud run services describe adk-home-buyer-backend \
  --region=us-central1 --format='value(status.url)')
echo "Backend URL: $BACKEND_URL"
```

#### Step 3: Deploy Frontend
```bash
gcloud run deploy adk-home-buyer-frontend \
  --source frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60 \
  --concurrency 80 \
  --max-instances 3 \
  --set-env-vars "REACT_APP_API_URL=$BACKEND_URL/api" \
  --port 80
```

#### Step 4: Get Frontend URL
```bash
FRONTEND_URL=$(gcloud run services describe adk-home-buyer-frontend \
  --region=us-central1 --format='value(status.url)')
echo "Frontend URL: $FRONTEND_URL"
```

## 🐳 Docker Development

### Local Testing with Docker
```bash
# Build and run services
docker-compose up --build

# Access services
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

### Individual Container Testing
```bash
# Backend
docker build -t adk-backend .
docker run -p 8000:8000 --env-file .env adk-backend

# Frontend
docker build -f frontend/Dockerfile -t adk-frontend .
docker run -p 3000:80 adk-frontend
```

## 🔍 Verification & Testing

### 1. Health Check
```bash
# Test backend health
curl https://your-backend-url.run.app/api/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-06-20T10:30:00Z",
  "service": "ADK Home Buyer API",
  "version": "1.0.0"
}
```

### 2. Frontend Access
- Open frontend URL in browser
- Verify form loads correctly
- Test with sample search criteria

### 3. End-to-End Test
```bash
# Run comprehensive test
python test_end_to_end.py

# Or test via API
curl -X POST https://your-backend-url.run.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "search_criteria": {
      "price_max": 750000,
      "price_min": 300000,
      "bedrooms_min": 3,
      "bathrooms_min": 2,
      "keywords": ["modern kitchen", "large backyard"]
    },
    "user_financial_info": {
      "annual_income": 120000,
      "down_payment_percentage": 20,
      "monthly_debts": 800
    },
    "priorities": ["safety", "good school district"]
  }'
```

## 📊 Monitoring & Logging

### View Logs
```bash
# Backend logs
gcloud run logs tail adk-home-buyer-backend --region=us-central1

# Frontend logs (less common)
gcloud run logs tail adk-home-buyer-frontend --region=us-central1
```

### Monitor Resources
```bash
# Service status
gcloud run services list --region=us-central1

# Detailed service info
gcloud run services describe adk-home-buyer-backend --region=us-central1
```

## 🔄 Updates & Maintenance

### Update Application
```bash
# Option 1: Re-run deployment script
./deploy/deploy.sh

# Option 2: Manual update
gcloud run deploy adk-home-buyer-backend --source .
gcloud run deploy adk-home-buyer-frontend --source frontend
```

### Environment Variables Update
```bash
gcloud run services update adk-home-buyer-backend \
  --set-env-vars "NEW_VAR=value" \
  --region=us-central1
```

### Scale Services
```bash
# Adjust resource limits
gcloud run services update adk-home-buyer-backend \
  --memory 4Gi \
  --cpu 4 \
  --max-instances 10 \
  --region=us-central1
```

## 💰 Cost Optimization

### Resource Sizing Recommendations

**Backend Service** (AI Analysis):
- **Memory**: 2Gi (for ML models)
- **CPU**: 2 (for parallel processing)
- **Concurrency**: 10 (balance between performance and cost)
- **Max Instances**: 5 (adjust based on usage)

**Frontend Service** (Static Content):
- **Memory**: 512Mi (sufficient for nginx)
- **CPU**: 1 (minimal processing needed)
- **Concurrency**: 80 (high for static content)
- **Max Instances**: 3 (usually sufficient)

### Cost-Saving Tips
1. **Use minimum CPU allocation** when idle
2. **Set appropriate concurrency** limits
3. **Monitor and adjust** max instances
4. **Use Cloud Run's free tier** (2 million requests/month)

## 🚨 Troubleshooting

### Common Issues

#### 1. Authentication Errors
```bash
# Re-authenticate
gcloud auth login
gcloud auth application-default login

# Check current authentication
gcloud auth list
```

#### 2. Build Failures
```bash
# Check build logs
gcloud builds list --limit=5

# View specific build
gcloud builds describe BUILD_ID
```

#### 3. Service Not Responding
```bash
# Check service status
gcloud run services describe SERVICE_NAME --region=us-central1

# View recent logs
gcloud run logs tail SERVICE_NAME --region=us-central1 --limit=50
```

#### 4. Memory/CPU Issues
```bash
# Update resource allocation
gcloud run services update SERVICE_NAME \
  --memory 4Gi \
  --cpu 2 \
  --region=us-central1
```

### Debug Commands
```bash
# List all services
gcloud run services list

# Describe service configuration
gcloud run services describe SERVICE_NAME --region=us-central1

# View service revisions
gcloud run revisions list --service=SERVICE_NAME --region=us-central1

# Get service URL
gcloud run services describe SERVICE_NAME \
  --region=us-central1 --format='value(status.url)'
```

## 🔐 Security Considerations

### IAM & Permissions
- Services run with **minimal required permissions**
- Use **service accounts** for Google Cloud API access
- Enable **unauthenticated access** only for public services

### Network Security
- **HTTPS enforced** by default on Cloud Run
- **CORS configured** for frontend-backend communication
- **Input validation** on all API endpoints

### Data Security
- **No sensitive data** stored in containers
- **Environment variables** for configuration
- **Audit logging** enabled for all services

## 📞 Support & Resources

### Documentation Links
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [React Deployment Guide](https://create-react-app.dev/docs/deployment/)

### Community Support
- GitHub Issues for bug reports
- Google Cloud Community for platform issues
- Stack Overflow for development questions

### Monitoring Tools
- **Google Cloud Monitoring** for metrics
- **Google Cloud Logging** for log analysis
- **Cloud Run Metrics** for performance monitoring
