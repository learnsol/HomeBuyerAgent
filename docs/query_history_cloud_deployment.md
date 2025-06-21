# Query History Storage for Cloud Run Deployment

## Problem with Current Approach

The current `QueryHistoryManager` stores data in a local JSON file, which has several issues in Cloud Run:

1. **Ephemeral Storage**: Files are lost when containers restart
2. **No Persistence**: Data doesn't survive deployments
3. **No Sharing**: Each container instance has separate storage
4. **Scalability Issues**: Multiple instances can't share history

## Recommended Solutions

### Option 1: Google Cloud Firestore (Recommended)
**Best for**: Simple setup, automatic scaling, serverless
```python
# Automatically selected when GOOGLE_CLOUD_PROJECT is set
query_history = CloudQueryHistoryManager()
```

**Setup**:
1. Enable Firestore API in Google Cloud Console
2. Set environment variable: `GOOGLE_CLOUD_PROJECT=your-project-id`
3. Deploy with service account that has Firestore permissions

**Pros**: 
- Serverless, no infrastructure management
- Automatic scaling and backup
- Simple integration
- Pay-per-use pricing

**Cons**:
- Vendor lock-in to Google Cloud
- Query limitations for complex analytics

### Option 2: Google Cloud SQL (PostgreSQL)
**Best for**: Complex queries, existing SQL knowledge, data relationships
```python
# Set DATABASE_URL environment variable
query_history = CloudQueryHistoryManager()
```

**Setup**:
1. Create Cloud SQL PostgreSQL instance
2. Set environment variable: `DATABASE_URL=postgresql://user:pass@host:port/db`
3. Configure VPC connector if using private IP

**Pros**:
- Full SQL capabilities
- Better for complex analytics
- Standard PostgreSQL (portable)

**Cons**:
- More complex setup
- Always-on billing (even when idle)
- Requires database management

### Option 3: In-Memory (Session-only)
**Best for**: Privacy-focused, temporary storage
```python
query_history = CloudQueryHistoryManager(InMemoryBackend())
```

**Pros**:
- No external dependencies
- Maximum privacy
- Fast access

**Cons**:
- Data lost on restart
- No persistence across sessions

## Migration Guide

### Step 1: Update Dependencies
```bash
pip install google-cloud-firestore  # For Firestore
# OR
pip install psycopg2-binary  # For Cloud SQL
```

### Step 2: Update Your Code
Replace the import in your main files:
```python
# Old
from query_history import query_history

# New
from query_history_cloud import query_history
```

### Step 3: Set Environment Variables

**For Firestore:**
```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export FIRESTORE_COLLECTION=query_history  # optional
```

**For Cloud SQL:**
```bash
export DATABASE_URL=postgresql://user:pass@host:port/database
```

**For Configuration:**
```bash
export QUERY_HISTORY_BACKEND=firestore  # or cloudsql, memory, local
export ENABLE_QUERY_HISTORY=true
export MAX_HISTORY_ENTRIES=50
```

### Step 4: Deploy
The system will automatically select the appropriate backend based on your environment variables.

## Security Considerations

1. **Firestore**: Use IAM roles to limit access
2. **Cloud SQL**: Use private IP and VPC connector
3. **Data Privacy**: Consider data retention policies
4. **Authentication**: Implement user session isolation

## Cost Considerations

**Firestore**: ~$0.06 per 100K reads, $0.18 per 100K writes
**Cloud SQL**: ~$15-45/month for small instances (always-on)
**In-Memory**: No additional cost

## Monitoring

Add logging to track usage:
```python
import logging
from google.cloud import logging as cloud_logging

# Set up Cloud Logging
cloud_logging.Client().setup_logging()
logging.info(f"Query history saved: {query_count} total queries")
```

## Testing

Test each backend:
```python
# Test with different backends
backends = {
    "memory": InMemoryBackend(),
    "firestore": FirestoreBackend(),
    "cloudsql": CloudSQLBackend()
}

for name, backend in backends.items():
    manager = CloudQueryHistoryManager(backend)
    # Test your functionality
```
