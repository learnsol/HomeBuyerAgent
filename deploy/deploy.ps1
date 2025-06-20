# PowerShell deployment script for Windows
# Google Cloud Run Deployment Script for ADK Home Buyer Application

param(
    [string]$ProjectId = $env:GOOGLE_CLOUD_PROJECT,
    [string]$Region = "us-central1"
)

# Configuration
$SERVICE_NAME_BACKEND = "adk-home-buyer-backend"
$SERVICE_NAME_FRONTEND = "adk-home-buyer-frontend"

Write-Host "🏠 ADK Home Buyer Application - Google Cloud Run Deployment" -ForegroundColor Blue
Write-Host "==================================================" -ForegroundColor Blue

# Check if required parameters are set
if (-not $ProjectId) {
    Write-Host "❌ Error: Project ID is not set" -ForegroundColor Red
    Write-Host "Please set it with: `$env:GOOGLE_CLOUD_PROJECT='your-project-id'" -ForegroundColor Yellow
    exit 1
}

Write-Host "📋 Configuration:" -ForegroundColor Yellow
Write-Host "  Project ID: $ProjectId"
Write-Host "  Region: $Region"
Write-Host "  Backend Service: $SERVICE_NAME_BACKEND"
Write-Host "  Frontend Service: $SERVICE_NAME_FRONTEND"
Write-Host ""

# Check Google Cloud authentication
Write-Host "🔐 Checking Google Cloud authentication..." -ForegroundColor Blue
$authCheck = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
if (-not $authCheck) {
    Write-Host "⚠️  Not authenticated. Please run: gcloud auth login" -ForegroundColor Yellow
    exit 1
}

# Set the project
Write-Host "🎯 Setting Google Cloud project..." -ForegroundColor Blue
gcloud config set project $ProjectId

# Enable required APIs
Write-Host "🔌 Enabling required Google Cloud APIs..." -ForegroundColor Blue
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Build and deploy backend
Write-Host "🔨 Building and deploying backend service..." -ForegroundColor Blue
gcloud run deploy $SERVICE_NAME_BACKEND `
    --source . `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --memory 2Gi `
    --cpu 2 `
    --timeout 300 `
    --concurrency 10 `
    --max-instances 5 `
    --set-env-vars "FLASK_ENV=production,PORT=8000" `
    --port 8000

# Get backend URL
$BACKEND_URL = gcloud run services describe $SERVICE_NAME_BACKEND --region=$Region --format='value(status.url)'
Write-Host "✅ Backend deployed at: $BACKEND_URL" -ForegroundColor Green

# Build and deploy frontend
Write-Host "🔨 Building and deploying frontend service..." -ForegroundColor Blue
gcloud run deploy $SERVICE_NAME_FRONTEND `
    --source frontend `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --memory 512Mi `
    --cpu 1 `
    --timeout 60 `
    --concurrency 80 `
    --max-instances 3 `
    --set-env-vars "REACT_APP_API_URL=$BACKEND_URL/api" `
    --port 80

# Get frontend URL
$FRONTEND_URL = gcloud run services describe $SERVICE_NAME_FRONTEND --region=$Region --format='value(status.url)'

Write-Host ""
Write-Host "🎉 Deployment completed successfully!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host "📱 Frontend URL: $FRONTEND_URL" -ForegroundColor Green
Write-Host "🔗 Backend URL: $BACKEND_URL" -ForegroundColor Green
Write-Host "📊 Health Check: $BACKEND_URL/api/health" -ForegroundColor Green
Write-Host ""
Write-Host "🔧 Next steps:" -ForegroundColor Yellow
Write-Host "1. Visit the frontend URL to test the application"
Write-Host "2. Check the health endpoint to verify backend status"
Write-Host "3. Monitor logs with: gcloud run logs tail $SERVICE_NAME_BACKEND --region=$Region"
Write-Host ""
Write-Host "📝 To update the application:" -ForegroundColor Blue
Write-Host "  .\deploy\deploy.ps1 -ProjectId $ProjectId -Region $Region"
Write-Host ""

# Open the frontend URL in browser
Start-Process $FRONTEND_URL
