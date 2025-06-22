# GitHub Actions CI/CD Setup Guide

## 🚀 Deployment Options

Your ADK Home Buyer application supports multiple deployment approaches:

### Option 1: Direct Cloud Run Deployment (Recommended)
- Deploy manually to Cloud Run first
- Set up GitHub integration for automatic triggers
- See `DIRECT_DEPLOYMENT_GUIDE.md` for detailed instructions

### Option 2: GitHub Actions Workflow  
- Fully automated deployment via GitHub Actions
- Uses the `deploy-app.yml` workflow
- Requires service account setup (see below)

## 📋 Prerequisites

### 1. Google Cloud Service Account Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **IAM & Admin > Service Accounts**
3. Click **Create Service Account**
4. Name: `github-actions-deployer`
5. Add these roles:
   - **Cloud Run Admin**
   - **Cloud Build Service Account**
   - **Service Account User**
   - **Storage Admin** (for container images)

### 2. Create and Download Service Account Key

1. Click on the created service account
2. Go to **Keys** tab
3. Click **Add Key > Create new key**
4. Choose **JSON** format
5. Download the JSON file

### 3. Add GitHub Repository Secret

1. Go to your GitHub repository
2. Navigate to **Settings > Secrets and variables > Actions**
3. Click **New repository secret**
4. Name: `GCP_SA_KEY`
5. Value: Paste the entire content of the downloaded JSON file

## 🔄 Deployment Workflow

### Full Stack Deployment (`deploy-app.yml`)
- **Triggers**: Push to `master`/`main` branch (excludes docs and markdown files)
- **Process**: 
  1. Deploys backend API (`homebuyerassistant`) with 4Gi memory, 2 CPU cores
  2. Deploys frontend (`homebuyeragent`) with 1Gi memory, 1 CPU core
  3. Automatically configures frontend to connect to backend API
- **Features**: Manual trigger support, deployment summary

## 🎯 Manual Deployment

You can trigger deployment manually:

1. Go to **Actions** tab in GitHub
2. Select **Deploy ADK Home Buyer App**
3. Click **Run workflow**
4. Choose the branch and click **Run workflow**

## 🌐 Service Configuration

**Project**: `gen-lang-client-0044046698`  
**Region**: `us-central1`

**Services**:
- **Backend API**: `homebuyerassistant`
- **Frontend App**: `homebuyeragent`

## 🔧 Customization

### Update Service Configuration
Edit the `env` section in `deploy-app.yml`:

```yaml
env:
  PROJECT_ID: gen-lang-client-0044046698
  REGION: us-central1
  BACKEND_SERVICE: homebuyerassistant
  FRONTEND_SERVICE: homebuyeragent
```

### Change Deployment Triggers
Modify the `on` section:

```yaml
on:
  push:
    branches: [ master, main ]
    paths-ignore:
      - 'docs/**'
      - '*.md'
  workflow_dispatch:  # Enables manual triggers
```

## 🛡️ Security Best Practices

1. **Least Privilege**: Service account has minimal required permissions
2. **Secret Management**: Credentials stored as encrypted GitHub secrets
3. **Branch Protection**: Only deploy from protected `master` branch
4. **Environment Isolation**: Production deployments separate from development

## 📊 Monitoring Deployments

1. **GitHub Actions**: Monitor deployment status in the Actions tab
2. **Cloud Run Console**: View service status and logs
3. **Cloud Build**: Check build logs and history

## 🐛 Troubleshooting

### Deployment Fails
1. Check GitHub Actions logs for detailed error messages
2. Verify service account permissions in Google Cloud Console
3. Ensure `GCP_SA_KEY` secret is set correctly

### Service Not Accessible
1. Verify Cloud Run services allow unauthenticated requests
2. Check service URLs in Cloud Run console
3. Test backend health endpoint: `{backend-url}/health`

### Frontend Can't Connect to Backend
1. Verify `REACT_APP_API_URL` environment variable is set correctly
2. Check CORS settings in backend API
3. Ensure both services are in the same region

### Build Failures
1. Check Cloud Build logs in Google Cloud Console
2. Verify Dockerfile syntax and dependencies
3. Ensure all required files are committed to repository

## 🎉 Success!

Once configured, every push to `master` will automatically:

1. ✅ Build and deploy your backend API
2. ✅ Build and deploy your frontend webapp  
3. ✅ Configure frontend to connect to backend
4. ✅ Provide deployment summary with URLs

Your ADK Home Buyer application will be automatically updated and available on Google Cloud Run!
