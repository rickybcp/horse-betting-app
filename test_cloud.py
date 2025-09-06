#!/usr/bin/env python3
"""Test cloud storage connection"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔧 Testing Cloud Storage Connection")
print("=" * 40)

# Check environment variables
project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
bucket_name = os.getenv('GCS_BUCKET_NAME') 
creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

print(f"Project ID: {project_id}")
print(f"Bucket Name: {bucket_name}")
print(f"Credentials Path: {creds_path}")
print()

# Check if credentials file exists
if creds_path and os.path.exists(creds_path):
    print(f"✅ Credentials file exists: {creds_path}")
else:
    print(f"❌ Credentials file missing: {creds_path}")

# Test cloud storage manager
try:
    from utils.cloud_storage import get_storage_manager
    
    print("\n🔍 Testing Storage Manager...")
    sm = get_storage_manager()
    
    print(f"Cloud Available: {sm.use_cloud}")
    print(f"Bucket Name: {sm.bucket_name}")
    print(f"Project ID: {sm.project_id}")
    
    if sm.use_cloud:
        print("✅ Cloud storage is configured and working!")
        
        # Test bucket access
        try:
            files = sm.list_files()
            print(f"📁 Found {len(files)} files in bucket")
            for f in files[:5]:  # Show first 5 files
                print(f"  - {f}")
        except Exception as e:
            print(f"❌ Error listing files: {e}")
            
    else:
        print("❌ Cloud storage not available - falling back to local files")
        
except Exception as e:
    print(f"❌ Error testing storage manager: {e}")
    import traceback
    traceback.print_exc()

