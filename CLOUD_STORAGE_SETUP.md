# 🏇 Lekours Cloud Storage Setup Guide

This guide will help you configure Google Cloud Storage for both local development and production deployment, ensuring you always work with the same data across all environments.

## 🎯 Overview

The Lekours app now uses Google Cloud Storage as the single source of truth for all data. This means:
- ✅ **Unified Data**: Same data across local development and production
- ✅ **Real-time Sync**: Changes in one environment are immediately available in others  
- ✅ **No Data Loss**: Centralized storage prevents data inconsistencies
- ✅ **Easy Collaboration**: Multiple developers can work with the same dataset

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install google-cloud-storage
```

### 2. Run Setup Script
```bash
python setup_cloud_storage.py
```

### 3. Configure Environment
Set up your environment variables (see details below)

### 4. Migrate Existing Data
```bash
python utils/migrate_to_cloud.py
```

## 🔧 Detailed Setup Instructions

### Step 1: Google Cloud Project Setup

1. **Create a Google Cloud Project** (if you don't have one):
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Click "Select a project" → "NEW PROJECT"
   - Enter project name: `lekours-horse-betting`
   - Note the Project ID (you'll need this)

2. **Enable Cloud Storage API**:
   - Go to APIs & Services → Library
   - Search for "Cloud Storage API"
   - Click "Enable"

3. **Create a Storage Bucket**:
   - Go to Cloud Storage → Browser
   - Click "CREATE BUCKET"
   - Name: `lekours-data-[your-name]` (must be globally unique)
   - Location: Choose region closest to your users
   - Storage class: Standard
   - Access control: Fine-grained

### Step 2: Service Account Setup

1. **Create Service Account**:
   - Go to IAM & Admin → Service Accounts
   - Click "CREATE SERVICE ACCOUNT"
   - Name: `lekours-storage-admin`
   - Description: `Service account for Lekours app data storage`

2. **Grant Permissions**:
   - Click on the created service account
   - Go to "Permissions" tab
   - Click "GRANT ACCESS"
   - Add role: `Storage Object Admin`
   - Save

3. **Create JSON Key**:
   - Go to "Keys" tab
   - Click "ADD KEY" → "Create new key"
   - Type: JSON
   - Download the file (keep it secure!)

### Step 3: Environment Configuration

Choose one of these options based on your environment:

#### Option A: Local Development (Recommended)
Create a `.env` file in your project root:

```bash
# Google Cloud Storage Configuration
GCS_BUCKET_NAME=lekours-data-yourname
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json

# Flask Configuration  
FLASK_ENV=development
FLASK_DEBUG=true
```

#### Option B: Production/Render Deployment
Set environment variables in your deployment platform:

```bash
GCS_BUCKET_NAME=lekours-data-yourname
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type":"service_account","project_id":"..."}
```

**For Render:**
1. Go to your service dashboard
2. Click "Environment"
3. Add each variable above
4. For `GOOGLE_APPLICATION_CREDENTIALS_JSON`, paste the entire JSON file content

### Step 4: Load Environment Variables

Add this to your shell profile or run before starting the app:

**Windows (PowerShell):**
```powershell
# Load from .env file (if using local development)
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
    }
}
```

**Linux/Mac (Bash):**
```bash
# Load from .env file (if using local development)
export $(cat .env | xargs)
```

**Or use python-dotenv in your app:**
```python
# Add to the top of server.py
from dotenv import load_dotenv
load_dotenv()
```

## 📁 Migration Process

### Migrate Your Existing Data

Run the migration script to upload your local data to cloud storage:

```bash
python utils/migrate_to_cloud.py
```

This will:
- ✅ Upload all files from `data/` directory to cloud storage
- ✅ Preserve the exact same file structure
- ✅ Verify the upload was successful
- ✅ Show detailed migration report

### Verify Migration

The script will automatically verify your data, but you can also manually check:

1. **Check Cloud Storage Browser**:
   - Go to Cloud Storage → Browser in Google Cloud Console
   - Browse your bucket to see uploaded files

2. **Test App Functionality**:
   - Start your app locally: `python server.py`
   - Check that leaderboard and race data loads correctly
   - Try the "Recalculate" button on the leaderboard

## 🔄 Development Workflow

Once set up, your workflow becomes:

1. **Start Development**:
   ```bash
   # Ensure environment variables are set
   python server.py
   ```

2. **Make Changes**: 
   - Use the app normally
   - All data changes go to cloud storage
   - Changes are immediately available across all environments

3. **Deploy**: 
   - Your deployed app automatically uses the same cloud data
   - No data migration needed between environments

## 🛠️ Troubleshooting

### Common Issues

#### "Cloud storage initialization failed"
**Problem**: Environment variables not set correctly
**Solution**: 
1. Check environment variables: `echo $GCS_BUCKET_NAME`
2. Verify service account JSON file exists and is valid
3. Run `python setup_cloud_storage.py` to check configuration

#### "403 Forbidden" errors
**Problem**: Service account doesn't have proper permissions
**Solution**:
1. Check service account has "Storage Object Admin" role
2. Verify bucket name is correct
3. Ensure bucket exists in the specified project

#### "Module not found: google.cloud.storage"
**Problem**: Required package not installed
**Solution**: `pip install google-cloud-storage`

#### Local vs Cloud Data Conflicts
**Problem**: Some data exists locally, some in cloud
**Solution**:
1. Run migration script again: `python utils/migrate_to_cloud.py`
2. Or start fresh: delete local `data/` folder (after backup)

### Debug Mode

Enable debug logging by setting:
```bash
export GOOGLE_CLOUD_LOG_LEVEL=DEBUG
```

## 🔒 Security Best Practices

1. **Never commit service account keys** to version control
2. **Use environment variables** for all credentials
3. **Restrict service account permissions** to only what's needed
4. **Regularly rotate service account keys**
5. **Use separate buckets** for development and production if needed

## 📊 Monitoring Usage

Monitor your Cloud Storage usage:

1. **Go to Cloud Console → Cloud Storage → Browser**
2. **Check bucket size and request metrics**
3. **Set up billing alerts** if concerned about costs

**Cost Estimate**: For typical usage (small JSON files, few users), costs should be minimal (< $1/month).

## 🎉 Success Checklist

- [ ] Google Cloud project created
- [ ] Cloud Storage API enabled  
- [ ] Storage bucket created
- [ ] Service account created with proper permissions
- [ ] JSON key downloaded and secured
- [ ] Environment variables configured
- [ ] `google-cloud-storage` package installed
- [ ] Migration script run successfully
- [ ] App starts without cloud storage errors
- [ ] Leaderboard and race data loads correctly
- [ ] Can create new users and place bets
- [ ] "Recalculate" button works

## 🆘 Getting Help

If you encounter issues:

1. **Run the setup checker**: `python setup_cloud_storage.py`
2. **Check the migration logs**: Look for specific error messages
3. **Verify cloud console**: Ensure bucket and files are visible
4. **Test authentication**: Try listing bucket contents manually

---

🏇 **Happy racing with unified cloud storage!** 

Your local development and production environments now share the same data source for complete consistency.