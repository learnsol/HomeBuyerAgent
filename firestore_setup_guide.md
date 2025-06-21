"""
Firestore Database Setup Guide
"""

# 🔧 Firestore Database Setup Required

The validation script shows that your Firestore database hasn't been created yet. 
Here's what you need to do:

## Step 1: Create Firestore Database

You have two options:

### Option A: Using Google Cloud Console (Recommended)
1. Go to: https://console.cloud.google.com/datastore/setup?project=gen-lang-client-0044046698
2. Click "Create Database"
3. Choose "Firestore in Native Mode" (recommended)
4. Select a location (use us-central1 to match your other resources)
5. Click "Create Database"

### Option B: Using gcloud CLI
```bash
# Make sure you're authenticated
gcloud auth login
gcloud config set project gen-lang-client-0044046698

# Create Firestore database in Native mode
gcloud firestore databases create --region=us-central1
```

## Step 2: Set up Authentication

Make sure you're authenticated with Google Cloud:

```bash
# Authenticate for application default credentials
gcloud auth application-default login

# Or set service account key (if using service account)
# export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
```

## Step 3: Enable Firestore API

The API should be enabled automatically when you create the database, but if needed:

```bash
gcloud services enable firestore.googleapis.com
```

## Step 4: Re-run Validation

After completing the setup, run the validation again:

```bash
python validate_firestore_setup.py
```

## Expected Result

After setup, you should see:
- ✅ Environment variables configured
- ✅ Firestore library installed  
- ✅ Firestore client working
- ✅ Permissions verified
- ✅ Query history integration working

## Troubleshooting

If you still have issues:

1. **Check project ID**: Make sure `gen-lang-client-0044046698` is correct
2. **Check permissions**: Your account needs Firestore permissions
3. **Check authentication**: Run `gcloud auth list` to verify login
4. **Check billing**: Make sure billing is enabled for your project

The error message provides a direct link to set up the database:
https://console.cloud.google.com/datastore/setup?project=gen-lang-client-0044046698
