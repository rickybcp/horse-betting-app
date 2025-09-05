"""
Migration Script: Upload Local Data to Google Cloud Storage
This script uploads all local data files to Google Cloud Storage
"""
import os
import json
from datetime import datetime
from cloud_storage import get_storage_manager, init_cloud_storage


def migrate_local_to_cloud():
    """
    Migrate all local data files to Google Cloud Storage
    """
    print("[MIGRATE] Starting migration from local storage to Google Cloud Storage")
    print("=" * 60)
    
    # Initialize cloud storage
    print("[MIGRATE] Initializing cloud storage...")
    storage_manager = get_storage_manager()
    
    if not storage_manager.use_cloud:
        print("[ERROR] Cloud storage is not available. Please check your configuration:")
        print("   - GCS_BUCKET_NAME environment variable")
        print("   - GOOGLE_CLOUD_PROJECT environment variable") 
        print("   - GOOGLE_APPLICATION_CREDENTIALS or GOOGLE_APPLICATION_CREDENTIALS_JSON")
        return False
    
    print("[OK] Cloud storage initialized successfully")
    
    # Define local data directory
    local_data_dir = "data"
    
    if not os.path.exists(local_data_dir):
        print(f"❌ Local data directory '{local_data_dir}' not found")
        return False
    
    # Track migration statistics
    total_files = 0
    uploaded_files = 0
    failed_files = 0
    
    # Walk through all local data files
    print("\n[FILES] Scanning local data files...")
    
    for root, dirs, files in os.walk(local_data_dir):
        for file in files:
            if file.endswith('.json'):
                local_path = os.path.join(root, file)
                # Convert local path to cloud storage path (use forward slashes)
                cloud_path = local_path.replace(os.sep, '/')
                
                total_files += 1
                
                try:
                    # Load local file
                    with open(local_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Upload to cloud storage
                    success = storage_manager.cloud_manager.save_file(cloud_path, data)
                    
                    if success:
                        uploaded_files += 1
                        print(f"  [OK] {local_path} -> {cloud_path}")
                    else:
                        failed_files += 1
                        print(f"  [ERROR] Failed to upload: {local_path}")
                        
                except Exception as e:
                    failed_files += 1
                    print(f"  [ERROR] Error uploading {local_path}: {e}")
    
    # Print migration summary
    print("\n" + "=" * 60)
    print("[SUMMARY] MIGRATION SUMMARY")
    print("=" * 60)
    print(f"Total files found:     {total_files}")
    print(f"Successfully uploaded: {uploaded_files}")
    print(f"Failed uploads:        {failed_files}")
    
    if failed_files == 0:
        print("[OK] Migration completed successfully!")
        print("\n[NEXT] Next steps:")
        print("   1. Test your application with cloud storage")
        print("   2. Update your local environment to use cloud storage")
        print("   3. Consider backing up local files before removing them")
        return True
    else:
        print("[WARN] Migration completed with some failures")
        print("   Please check the failed files and try again")
        return False


def verify_cloud_data():
    """
    Verify that data was uploaded correctly to cloud storage
    """
    print("\n[VERIFY] Verifying cloud storage data...")
    
    storage_manager = get_storage_manager()
    
    if not storage_manager.use_cloud:
        print("[ERROR] Cloud storage not available for verification")
        return False
    
    # Check key files
    key_files = [
        "data/users.json",
        "data/all_races/index.json",
        "data/all_races/2025-08-30.json",
        "data/all_races/2025-08-16.json",
        "data/all_races/2025-08-09.json",
        "data/all_races/2025-08-02.json"
    ]
    
    verified_files = 0
    total_key_files = len(key_files)
    
    for filepath in key_files:
        try:
            data = storage_manager.cloud_manager.load_file(filepath)
            if data is not None:
                verified_files += 1
                print(f"  [OK] {filepath} - OK")
                
                # Show some stats for users.json
                if filepath == "data/users.json" and isinstance(data, list):
                    print(f"     [INFO] Contains {len(data)} users")
                
                # Show some stats for race day files
                elif filepath.startswith("data/all_races/") and isinstance(data, dict):
                    races_count = len(data.get('races', []))
                    bets_count = len(data.get('bets', {}))
                    bankers_count = len(data.get('bankers', {}))
                    print(f"     [INFO] {races_count} races, {bets_count} users with bets, {bankers_count} bankers")
            else:
                print(f"  [ERROR] {filepath} - NOT FOUND")
                
        except Exception as e:
            print(f"  [ERROR] {filepath} - ERROR: {e}")
    
    print(f"\n[VERIFY] Verification complete: {verified_files}/{total_key_files} key files found")
    
    if verified_files == total_key_files:
        print("[OK] All key files verified successfully!")
        return True
    else:
        print("[WARN] Some key files are missing from cloud storage")
        return False


def list_cloud_files():
    """
    List all files in cloud storage for inspection
    """
    print("\n[FILES] Listing all files in cloud storage...")
    
    storage_manager = get_storage_manager()
    
    if not storage_manager.use_cloud:
        print("[ERROR] Cloud storage not available")
        return
    
    try:
        # List all files
        files = storage_manager.cloud_manager.list_files()
        
        if not files:
            print("[INFO] No files found in cloud storage")
            return
        
        print(f"[FILES] Found {len(files)} files in cloud storage:")
        print("-" * 50)
        
        # Group files by directory
        data_files = []
        all_races_files = []
        other_files = []
        
        for file in sorted(files):
            if file.startswith('data/all_races/'):
                all_races_files.append(file)
            elif file.startswith('data/'):
                data_files.append(file)
            else:
                other_files.append(file)
        
        if data_files:
            print("[FILES] Data files:")
            for file in data_files:
                print(f"  {file}")
        
        if all_races_files:
            print("\n[FILES] Race day files:")
            for file in all_races_files:
                print(f"  {file}")
        
        if other_files:
            print("\n[FILES] Other files:")
            for file in other_files:
                print(f"  {file}")
                
    except Exception as e:
        print(f"❌ Error listing cloud files: {e}")


if __name__ == "__main__":
    print("[TOOL] Lekours Data Migration Tool")
    print("=" * 60)
    
    # Run migration
    success = migrate_local_to_cloud()
    
    if success:
        # Verify the migration
        verify_cloud_data()
        
        # List all cloud files
        list_cloud_files()
        
        print("\n" + "=" * 60)
        print("[DONE] MIGRATION COMPLETE!")
        print("=" * 60)
        print("Your local data has been uploaded to Google Cloud Storage.")
        print("You can now use the same data across all environments!")
        
    else:
        print("\n" + "=" * 60)
        print("[ERROR] MIGRATION FAILED")
        print("=" * 60)
        print("Please check the errors above and try again.")
