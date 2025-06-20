#!/bin/bash

# Google Cloud Run Deployment Script for ADK Home Buyer Application

set -e

# Configuration
PROJECT_ID="${GOOGLE_CLOUD_PROJECT}"
REGION="${GOOGLE_CLOUD_REGION:-us-central1}"
SERVICE_NAME_BACKEND="adk-home-buyer-backend"
SERVICE_NAME_FRONTEND="adk-home-buyer-frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏠 ADK Home Buyer Application - Google Cloud Run Deployment${NC}"
echo "=================================================="

# Check if required environment variables are set
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ Error: GOOGLE_CLOUD_PROJECT environment variable is not set${NC}"
    echo "Please set it with: export GOOGLE_CLOUD_PROJECT=your-project-id"
    exit 1
fi

echo -e "${YELLOW}📋 Configuration:${NC}"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Backend Service: $SERVICE_NAME_BACKEND"
echo "  Frontend Service: $SERVICE_NAME_FRONTEND"
echo ""

# Authenticate with Google Cloud (if not already done)
echo -e "${BLUE}🔐 Checking Google Cloud authentication...${NC}"
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}⚠️  Not authenticated. Please run: gcloud auth login${NC}"
    exit 1
fi

# Set the project
echo -e "${BLUE}🎯 Setting Google Cloud project...${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${BLUE}🔌 Enabling required Google Cloud APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Build and deploy backend
echo -e "${BLUE}🔨 Building and deploying backend service...${NC}"
gcloud run deploy $SERVICE_NAME_BACKEND \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --concurrency 10 \
    --max-instances 5 \
    --set-env-vars "FLASK_ENV=production,PORT=8000" \
    --port 8000

# Get backend URL
BACKEND_URL=$(gcloud run services describe $SERVICE_NAME_BACKEND --region=$REGION --format='value(status.url)')
echo -e "${GREEN}✅ Backend deployed at: $BACKEND_URL${NC}"

# Build and deploy frontend
echo -e "${BLUE}🔨 Building and deploying frontend service...${NC}"
gcloud run deploy $SERVICE_NAME_FRONTEND \
    --source frontend \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --timeout 60 \
    --concurrency 80 \
    --max-instances 3 \
    --set-env-vars "REACT_APP_API_URL=$BACKEND_URL/api" \
    --port 80

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe $SERVICE_NAME_FRONTEND --region=$REGION --format='value(status.url)')

echo ""
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo "=================================================="
echo -e "${GREEN}📱 Frontend URL: $FRONTEND_URL${NC}"
echo -e "${GREEN}🔗 Backend URL: $BACKEND_URL${NC}"
echo -e "${GREEN}📊 Health Check: $BACKEND_URL/api/health${NC}"
echo ""
echo -e "${YELLOW}🔧 Next steps:${NC}"
echo "1. Visit the frontend URL to test the application"
echo "2. Check the health endpoint to verify backend status"
echo "3. Monitor logs with: gcloud run logs tail $SERVICE_NAME_BACKEND --region=$REGION"
echo ""
echo -e "${BLUE}📝 To update the application:${NC}"
echo "  ./deploy/deploy.sh"
echo ""

# Optional: Open the frontend URL
if command -v open &> /dev/null; then
    echo -e "${BLUE}🌐 Opening frontend in browser...${NC}"
    open $FRONTEND_URL
elif command -v xdg-open &> /dev/null; then
    echo -e "${BLUE}🌐 Opening frontend in browser...${NC}"
    xdg-open $FRONTEND_URL
fi
