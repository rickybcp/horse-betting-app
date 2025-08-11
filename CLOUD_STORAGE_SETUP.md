# Cloud Storage Setup Guide for Horse Betting App

## Overview
This guide explains how to set up Google Cloud Storage for the horse betting app to ensure data persistence on Render deployment.

## Why Cloud Storage?
- **Local files are lost** when Render containers restart
- **Git-based data** is not suitable for production (data changes frequently)
- **Cloud storage** provides persistent, scalable data storage
- **Automatic fallback** to local storage when cloud is unavailable

## Prerequisites
1. Google Cloud Platform account
2. Google Cloud project
3. Google Cloud Storage bucket
4. Service account with Storage Admin permissions

## Step-by-Step Setup

### 1. Create Google Cloud Project
```bash
# Install Google Cloud CLI
# Visit: https://cloud.google.com/sdk/docs/install

# Login to Google Cloud
gcloud auth login

# Create new project (or use existing)
gcloud projects create horse-betting-app-123 --name="Horse Betting App"

# Set as default project
gcloud config set project horse-betting-app-123
```

### 2. Enable Cloud Storage API
```bash
# Enable Cloud Storage API
gcloud services enable storage.googleapis.com
```

### 3. Create Storage Bucket
```bash
# Create bucket (must be globally unique)
gcloud storage buckets create gs://horse-betting-data-123

# Set bucket permissions
gcloud storage buckets add-iam-policy-binding gs://horse-betting-data-123 \
    --member="allUsers" \
    --role="storage.objectViewer"
```

### 4. Create Service Account
```bash
# Create service account
gcloud iam service-accounts create horse-betting-sa \
    --display-name="Horse Betting Service Account"

# Grant Storage Admin role
gcloud projects add-iam-policy-binding horse-betting-app-123 \
    --member="serviceAccount:horse-betting-sa@horse-betting-app-123.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# Create and download key
gcloud iam service-accounts keys create service-account-key.json \
    --iam-account=horse-betting-sa@horse-betting-app-123.iam.gserviceaccount.com
```

### 5. Configure Environment Variables

#### For Local Development
Create a `.env` file in your project root:
```env
GCS_BUCKET_NAME=horse-betting-data-123
GOOGLE_CLOUD_PROJECT=horse-betting-app-123
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json
```

#### For Render Deployment
Add these environment variables in your Render dashboard:
- `GCS_BUCKET_NAME`: `horse-betting-data-123`
- `GOOGLE_CLOUD_PROJECT`: `horse-betting-app-123`
- `GOOGLE_APPLICATION_CREDENTIALS`: Upload the service account key file

### 6. Install Dependencies
```bash
# Install Google Cloud Storage library
pip install google-cloud-storage

# Or update requirements.txt and install
pip install -r requirements.txt
```

## How It Works

### Storage Manager
The app uses a `HybridStorageManager` that:
1. **Tries cloud storage first** when environment variables are set
2. **Falls back to local storage** if cloud storage fails
3. **Automatically switches** between storage types as needed

### File Operations
All file operations (`load_json`, `save_json`) now use cloud storage:
- **Local development**: Uses local files
- **Render deployment**: Uses Google Cloud Storage
- **Automatic fallback**: If cloud fails, switches to local

### Data Structure
Files are stored in the cloud bucket with the same structure:
```
gs://your-bucket/
├── data/
│   ├── users.json
│   ├── current/
│   │   ├── races.json
│   │   ├── bets.json
│   │   └── bankers.json
│   └── race_days/
│       ├── index.json
│       ├── 2025-08-02.json
│       └── 2025-08-09.json
```

## Testing

### 1. Test Local Setup
```bash
# Set environment variables
export GCS_BUCKET_NAME=your-bucket-name
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json

# Run the app
python server.py

# Check console output for:
# 🚀 Cloud storage initialized
```

### 2. Test Cloud Storage
```bash
# Check if files are created in cloud
gcloud storage ls gs://your-bucket-name/data/

# View file contents
gcloud storage cat gs://your-bucket-name/data/users.json
```

### 3. Test Fallback
```bash
# Remove credentials to test fallback
unset GOOGLE_APPLICATION_CREDENTIALS

# Run the app
python server.py

# Check console output for:
# 💾 Using local file storage
```

## Troubleshooting

### Common Issues

#### 1. "Permission denied" errors
```bash
# Check service account permissions
gcloud projects get-iam-policy your-project-id

# Ensure service account has Storage Admin role
gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:your-sa@your-project.iam.gserviceaccount.com" \
    --role="roles/storage.admin"
```

#### 2. "Bucket not found" errors
```bash
# List all buckets
gcloud storage ls

# Check bucket name spelling
# Ensure bucket exists in correct project
```

#### 3. "Authentication failed" errors
```bash
# Verify service account key
gcloud auth activate-service-account --key-file=service-account-key.json

# Test authentication
gcloud storage ls gs://your-bucket-name/
```

### Debug Mode
Enable debug logging by setting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Considerations

### 1. Service Account Permissions
- Use **least privilege principle**
- Consider **custom IAM roles** for production
- **Rotate keys regularly**

### 2. Bucket Security
- **Enable versioning** for data recovery
- **Set up lifecycle policies** for cost management
- **Monitor access logs**

### 3. Environment Variables
- **Never commit** service account keys to Git
- Use **Render's secure environment variables**
- **Rotate credentials** regularly

## Cost Optimization

### 1. Storage Classes
- **Standard**: Frequently accessed data
- **Nearline**: Data accessed <1/month
- **Coldline**: Data accessed <1/year
- **Archive**: Long-term backup

### 2. Lifecycle Policies
```bash
# Set lifecycle policy for cost optimization
gcloud storage buckets update gs://your-bucket-name \
    --lifecycle-file=lifecycle.json
```

Example `lifecycle.json`:
```json
{
  "rule": [
    {
      "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
      "condition": {"age": 30}
    },
    {
      "action": {"type": "Delete"},
      "condition": {"age": 365}
    }
  ]
}
```

## Monitoring

### 1. Cloud Console
- Monitor **bucket usage** and costs
- Check **access logs** and **audit logs**
- Set up **alerts** for unusual activity

### 2. Application Logs
The app logs all storage operations:
- ✅ Successful cloud storage operations
- ❌ Failed cloud storage operations
- ⚠️ Fallback to local storage
- 💾 Local storage operations

## Next Steps

1. **Deploy to Render** with environment variables
2. **Test data persistence** across container restarts
3. **Monitor costs** and adjust storage classes
4. **Set up backup** and disaster recovery
5. **Implement monitoring** and alerting

## Support

For issues with:
- **Google Cloud**: Check [Google Cloud documentation](https://cloud.google.com/storage/docs)
- **App integration**: Check app logs and cloud storage console
- **Render deployment**: Check Render logs and environment variables
