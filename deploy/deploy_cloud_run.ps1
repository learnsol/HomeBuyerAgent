# ADK Home Buyer Application - Cloud Run Deployment Script (PowerShell)

# Configuration
$PROJECT_ID = "gen-lang-client-0044046698"
$SERVICE_NAME = "adk-home-buyer"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/$SERVICE_NAME"

Write-Host "🚀 Starting deployment of ADK Home Buyer to Google Cloud Run" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue

# Check prerequisites
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow

# Check if gcloud is installed
try {
    gcloud version | Out-Null
    Write-Host "✅ Google Cloud CLI found" -ForegroundColor Green
} catch {
    Write-Host "❌ Google Cloud CLI is not installed" -ForegroundColor Red
    exit 1
}

# Check if docker is installed
try {
    docker --version | Out-Null
    Write-Host "✅ Docker found" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed" -ForegroundColor Red
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found. Please create it with required environment variables." -ForegroundColor Red
    exit 1
}
Write-Host "✅ .env file found" -ForegroundColor Green

Write-Host "✅ Prerequisites check passed" -ForegroundColor Green

# Set up Google Cloud project
Write-Host "🔧 Setting up Google Cloud project..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID
gcloud auth configure-docker

# Enable required APIs
Write-Host "🔌 Enabling required APIs..." -ForegroundColor Yellow
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable aiplatform.googleapis.com

# Build Docker image
Write-Host "🏗️ Building Docker image..." -ForegroundColor Yellow
docker build -t $IMAGE_NAME .

# Push to Google Container Registry
Write-Host "📤 Pushing image to Google Container Registry..." -ForegroundColor Yellow
docker push $IMAGE_NAME

# Deploy to Cloud Run
Write-Host "🚀 Deploying to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $SERVICE_NAME `
  --image $IMAGE_NAME `
  --platform managed `
  --region $REGION `
  --allow-unauthenticated `
  --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID `
  --set-env-vars QUERY_HISTORY_BACKEND=firestore `
  --set-env-vars ENABLE_QUERY_HISTORY=true `
  --set-env-vars BIGQUERY_DATASET=home_buyer_hackathon_data `
  --set-env-vars BIGQUERY_LOCATION=northamerica-northeast2 `
  --set-env-vars VERTEX_AI_LOCATION=us-central1 `
  --set-env-vars DEFAULT_AGENT_MODEL=gemini-2.0-flash-001 `
  --set-env-vars ORCHESTRATOR_MODEL=gemini-2.0-flash-001 `
  --set-env-vars EMBEDDING_MODEL_NAME=text-embedding-004 `
  --set-env-vars USE_MOCK_DATA=false `
  --memory 2Gi `
  --cpu 2 `
  --max-instances 10 `
  --min-instances 0 `
  --port 8000 `
  --timeout 300

# Get service URL
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format "value(status.url)"

Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host "🌐 Service URL: $SERVICE_URL" -ForegroundColor Cyan
Write-Host "🏥 Health Check: $SERVICE_URL/api/health" -ForegroundColor Cyan
Write-Host "📊 Backend Status: $SERVICE_URL/api/history/status" -ForegroundColor Cyan
Write-Host ""
Write-Host "🧪 Test the deployment:" -ForegroundColor Yellow
Write-Host "Invoke-WebRequest -Uri '$SERVICE_URL/api/health' -Method GET" -ForegroundColor White
Write-Host ""
Write-Host "📱 Update your frontend to use this API URL for production" -ForegroundColor Magenta
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
