"""
Cloud Storage Setup Script for Lekours Horse Betting App
Sets up environment variables and credentials for Google Cloud Storage
"""
import os
import json
import sys
from pathlib import Path


def setup_environment():
    """
    Setup environment variables for Google Cloud Storage
    """
    print("🏇 Lekours Cloud Storage Setup")
    print("=" * 50)
    
    # Check if running in local development or production
    print("🔧 Configuring Google Cloud Storage...")
    
    # Load existing environment configuration
    env_file = "cloud_storage_config.env"
    if os.path.exists(env_file):
        print(f"📄 Found existing config file: {env_file}")
        with open(env_file, 'r') as f:
            print("Current configuration:")
            print(f.read())
    else:
        print(f"⚠️ Config file {env_file} not found")
    
    print("\n" + "=" * 50)
    print("🚀 SETUP INSTRUCTIONS")
    print("=" * 50)
    
    print("\n1️⃣ GOOGLE CLOUD PROJECT SETUP")
    print("-" * 30)
    print("• Create a Google Cloud project if you haven't already")
    print("• Enable the Cloud Storage API")
    print("• Create a Cloud Storage bucket")
    
    print("\n2️⃣ SERVICE ACCOUNT SETUP")
    print("-" * 30)
    print("• Go to Google Cloud Console > IAM & Admin > Service Accounts")
    print("• Create a new service account")
    print("• Grant 'Storage Object Admin' role")
    print("• Create and download a JSON key file")
    
    print("\n3️⃣ ENVIRONMENT CONFIGURATION")
    print("-" * 30)
    print("Choose one of these options:")
    
    print("\n   OPTION A: Use local service account file")
    print("   • Place your service account JSON file in the project root")
    print("   • Set GOOGLE_APPLICATION_CREDENTIALS to the file path")
    
    print("\n   OPTION B: Use environment variable (recommended for deployment)")
    print("   • Set GOOGLE_APPLICATION_CREDENTIALS_JSON to the JSON content")
    print("   • This is more secure for deployed environments")
    
    print("\n4️⃣ REQUIRED ENVIRONMENT VARIABLES")
    print("-" * 30)
    print("Set these environment variables:")
    print("• GCS_BUCKET_NAME=your-bucket-name")
    print("• GOOGLE_CLOUD_PROJECT=your-project-id")
    print("• GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json")
    print("  OR")
    print("• GOOGLE_APPLICATION_CREDENTIALS_JSON={...json content...}")
    
    print("\n5️⃣ INSTALL DEPENDENCIES")
    print("-" * 30)
    print("Install required packages:")
    print("pip install google-cloud-storage")
    
    print("\n6️⃣ TEST YOUR SETUP")
    print("-" * 30)
    print("Run the migration script to test and upload your data:")
    print("python utils/migrate_to_cloud.py")
    
    print("\n" + "=" * 50)
    print("🔍 CURRENT ENVIRONMENT CHECK")
    print("=" * 50)
    
    # Check current environment
    env_vars = [
        'GCS_BUCKET_NAME',
        'GOOGLE_CLOUD_PROJECT', 
        'GOOGLE_APPLICATION_CREDENTIALS',
        'GOOGLE_APPLICATION_CREDENTIALS_JSON'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if var == 'GOOGLE_APPLICATION_CREDENTIALS_JSON':
                print(f"✅ {var}: [JSON content set]")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
    
    # Check if google-cloud-storage is installed
    try:
        import google.cloud.storage
        print("✅ google-cloud-storage: Installed")
    except ImportError:
        print("❌ google-cloud-storage: Not installed")
        print("   Run: pip install google-cloud-storage")
    
    print("\n" + "=" * 50)
    print("📝 SAMPLE .ENV FILE")
    print("=" * 50)
    print("Create a .env file with these contents:")
    print()
    print("# Google Cloud Storage Configuration")
    print("GCS_BUCKET_NAME=your-bucket-name-here")
    print("GOOGLE_CLOUD_PROJECT=your-project-id-here") 
    print("GOOGLE_APPLICATION_CREDENTIALS=service-account-key.json")
    print()
    print("# OR use JSON content directly (for deployment)")
    print("# GOOGLE_APPLICATION_CREDENTIALS_JSON={\"type\":\"service_account\",...}")
    
    print("\n" + "=" * 50)
    print("🎯 NEXT STEPS")
    print("=" * 50)
    print("1. Set up your Google Cloud project and service account")
    print("2. Configure environment variables")
    print("3. Install google-cloud-storage: pip install google-cloud-storage")
    print("4. Run migration: python utils/migrate_to_cloud.py")
    print("5. Test your application")


def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import google.cloud.storage
        print("✅ google-cloud-storage is installed")
        return True
    except ImportError:
        print("❌ google-cloud-storage is not installed")
        print("Please run: pip install google-cloud-storage")
        return False


def create_sample_env_file():
    """Create a sample environment file"""
    env_content = """# Google Cloud Storage Configuration for Lekours
# Copy this file to .env and fill in your actual values

# Your Google Cloud Storage bucket name
GCS_BUCKET_NAME=your-bucket-name-here

# Your Google Cloud project ID
GOOGLE_CLOUD_PROJECT=your-project-id-here

# Path to your service account JSON file (local development)
GOOGLE_APPLICATION_CREDENTIALS=service-account-key.json

# OR use JSON content directly (for deployment/Render)
# GOOGLE_APPLICATION_CREDENTIALS_JSON={"type":"service_account","project_id":"..."}

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=false
"""
    
    sample_file = ".env.sample"
    with open(sample_file, 'w') as f:
        f.write(env_content)
    
    print(f"📄 Created sample environment file: {sample_file}")
    print("Copy this to .env and fill in your actual values")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--create-sample":
        create_sample_env_file()
    else:
        setup_environment()
        
        if "--create-sample" in sys.argv:
            print("\n")
            create_sample_env_file()
