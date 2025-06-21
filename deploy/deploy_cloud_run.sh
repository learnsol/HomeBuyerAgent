#!/bin/bash
# ADK Home Buyer Application - Cloud Run Deployment Script

set -e

# Configuration
PROJECT_ID="gen-lang-client-0044046698"
SERVICE_NAME="adk-home-buyer"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 Starting deployment of ADK Home Buyer to Google Cloud Run"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI is not installed"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it with required environment variables."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Set up Google Cloud project
echo "🔧 Setting up Google Cloud project..."
gcloud config set project $PROJECT_ID
gcloud auth configure-docker

# Enable required APIs
echo "🔌 Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable aiplatform.googleapis.com

# Build Docker image
echo "🏗️ Building Docker image..."
docker build -t $IMAGE_NAME .

# Push to Google Container Registry
echo "📤 Pushing image to Google Container Registry..."
docker push $IMAGE_NAME

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID \
  --set-env-vars QUERY_HISTORY_BACKEND=firestore \
  --set-env-vars ENABLE_QUERY_HISTORY=true \
  --set-env-vars BIGQUERY_DATASET=home_buyer_hackathon_data \
  --set-env-vars BIGQUERY_LOCATION=northamerica-northeast2 \
  --set-env-vars VERTEX_AI_LOCATION=us-central1 \
  --set-env-vars DEFAULT_AGENT_MODEL=gemini-2.0-flash-001 \
  --set-env-vars ORCHESTRATOR_MODEL=gemini-2.0-flash-001 \
  --set-env-vars EMBEDDING_MODEL_NAME=text-embedding-004 \
  --set-env-vars USE_MOCK_DATA=false \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10 \
  --min-instances 0 \
  --port 8000 \
  --timeout 300

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo "✅ Deployment completed successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Service URL: $SERVICE_URL"
echo "🏥 Health Check: $SERVICE_URL/api/health"
echo "📊 Backend Status: $SERVICE_URL/api/history/status"
echo ""
echo "🧪 Test the deployment:"
echo "curl $SERVICE_URL/api/health"
echo ""
echo "📱 Update your frontend to use this API URL for production"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
