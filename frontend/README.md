# ADK Home Buyer Frontend

A modern React application that provides an intuitive interface for AI-powered home buying assistance. Built with React 18, Ant Design, and deployed on Google Cloud Run.

## 🚀 Features

- **Intelligent Search Form**: Comprehensive property search with financial criteria
- **Real-time Progress Tracking**: Visual feedback during AI analysis
- **Beautiful Results Display**: Modern cards with detailed property analysis
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Cloud-Ready**: Optimized for Google Cloud Run deployment

## 🏗️ Architecture

```
Frontend (React) → API Server (Flask) → ADK Orchestrator → AI Agents
```

- **React Frontend**: User interface with Ant Design components
- **Flask API Server**: RESTful backend serving the orchestrator
- **ADK Orchestrator**: Multi-agent workflow coordination
- **AI Agents**: Property analysis, locality review, safety assessment, affordability

## 📦 Components

### Core Components
- **App.js**: Main application component with state management
- **SearchForm.js**: Property search form with validation
- **ProgressTracker.js**: Real-time analysis progress display
- **RecommendationResults.js**: Property recommendations with detailed analysis

### Services
- **api.js**: Axios-based API client with error handling and timeouts

## 🛠️ Development

### Prerequisites
- Node.js 18+
- npm or yarn
- Python 3.11+ (for backend)

### Local Development

1. **Install Dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start Development Server**:
   ```bash
   npm start
   ```
   Opens http://localhost:3000

3. **Start Backend** (in separate terminal):
   ```bash
   cd ..
   python api_server.py
   ```
   Backend runs on http://localhost:8000

### Environment Variables

Create `.env` file in frontend directory:
```env
REACT_APP_API_URL=http://localhost:8000/api
```

For production:
```env
REACT_APP_API_URL=https://your-backend-url.run.app/api
```

## 🌐 Deployment

### Google Cloud Run Deployment

#### Option 1: Automated Deployment (Recommended)

**Windows (PowerShell)**:
```powershell
# Set your project ID
$env:GOOGLE_CLOUD_PROJECT = "your-project-id"

# Run deployment script
.\deploy\deploy.ps1
```

**Linux/Mac (Bash)**:
```bash
# Set your project ID
export GOOGLE_CLOUD_PROJECT="your-project-id"

# Make script executable and run
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

#### Option 2: Manual Deployment

1. **Deploy Backend**:
   ```bash
   gcloud run deploy adk-home-buyer-backend \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 2Gi \
     --cpu 2 \
     --timeout 300
   ```

2. **Deploy Frontend**:
   ```bash
   gcloud run deploy homebuyeragent \
     --source frontend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 512Mi \
     --cpu 1 \
     --set-env-vars "REACT_APP_API_URL=https://your-backend-url/api"
   ```

### Docker Deployment

#### Local Docker Testing:
```bash
# Build and run with Docker Compose
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

#### Build Individual Images:
```bash
# Backend
docker build -t adk-home-buyer-backend .

# Frontend
docker build -f frontend/Dockerfile -t homebuyeragent .
```

## 📊 API Integration

### API Endpoints

#### Health Check
```
GET /api/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-06-20T10:30:00Z",
  "service": "ADK Home Buyer API",
  "version": "1.0.0"
}
```

#### Home Analysis
```
POST /api/analyze
```

Request:
```json
{
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
}
```

Response:
```json
{
  "top_recommendations": [
    {
      "listing_id": "listing_1",
      "address": "123 Main St, Anytown, CA",
      "price": 650000,
      "bedrooms": 3,
      "bathrooms": 2,
      "total_score": 85,
      "pros": ["Great school district", "Safe neighborhood"],
      "cons": ["Busy street", "Small backyard"],
      "affordability_score": 22,
      "locality_score": 24,
      "safety_score": 20
    }
  ],
  "summary": {
    "total_listings": 15,
    "recommended_count": 5,
    "average_score": 78.5
  }
}
```

## 🎨 Styling & Theming

### Design System
- **Primary Colors**: Blue gradient (#667eea to #764ba2)
- **Component Library**: Ant Design 5.x
- **Typography**: System fonts with fallbacks
- **Layout**: Responsive grid system

### Custom Styles
- **Glass morphism effects** for cards and containers
- **Smooth animations** and hover effects
- **Mobile-first responsive design**
- **Accessible color contrast** (WCAG AA compliant)

## 🧪 Testing

### Frontend Tests
```bash
cd frontend
npm test
```

### API Testing
```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Test analysis endpoint
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d @test-request.json
```

## 📈 Performance

### Optimization Features
- **Code splitting** with React.lazy()
- **Asset optimization** with webpack
- **Image compression** and lazy loading
- **API request caching** and retry logic
- **Progressive enhancement** for mobile devices

### Cloud Run Optimization
- **Multi-stage Docker builds** for smaller images
- **Nginx caching** for static assets
- **Health checks** and auto-scaling
- **Resource limits** for cost optimization

## 🔧 Configuration

### Build Configuration
- **React Scripts 5.x** with modern JS/TS support
- **ESLint + Prettier** for code quality
- **Proxy configuration** for local development
- **Environment-based builds** (dev/staging/prod)

### Security Features
- **CORS protection** with Flask-CORS
- **Content Security Policy** headers
- **Input validation** and sanitization
- **Rate limiting** (Cloud Run built-in)

## 🚨 Troubleshooting

### Common Issues

#### Frontend Build Errors
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### API Connection Issues
- Check `REACT_APP_API_URL` environment variable
- Verify backend service is running
- Check CORS configuration

#### Deployment Issues
- Ensure Google Cloud Project ID is set
- Verify authentication: `gcloud auth list`
- Check service account permissions

### Debug Commands
```bash
# View Cloud Run logs
gcloud run logs tail adk-home-buyer-backend --region=us-central1

# Check service status
gcloud run services describe homebuyeragent --region=us-central1

# Test API locally
python api_server.py
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and test locally
4. Run tests: `npm test` and `python -m pytest`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

For support, please check:
1. This README and troubleshooting section
2. GitHub Issues for known problems
3. Google Cloud Run documentation
4. React and Ant Design documentation
