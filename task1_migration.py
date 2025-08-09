#!/usr/bin/env python3
"""
Task 1: File Structure Migration for Lekours Historical Data
Creates new directory structure and migrates current files to data/current/
"""

import os
import shutil
import json
from datetime import datetime

def task1_file_structure_migration():
    """
    Implement Task 1: File Structure Migration
    - Create data/current/ and data/race_days/ directories
    - Move existing race, bet, banker files to data/current/
    - Update file structure for historical data support
    """
    
    print("🚀 Task 1: File Structure Migration")
    print("=" * 50)
    
    # Define paths
    data_dir = 'data'
    current_dir = os.path.join(data_dir, 'current')
    race_days_dir = os.path.join(data_dir, 'race_days')
    
    # Step 1: Create new directories
    print("📁 Step 1: Creating new directory structure...")
    
    try:
        os.makedirs(current_dir, exist_ok=True)
        os.makedirs(race_days_dir, exist_ok=True)
        print(f"✅ Created: {current_dir}")
        print(f"✅ Created: {race_days_dir}")
    except Exception as e:
        print(f"❌ Error creating directories: {e}")
        return False
    
    # Step 2: Move current day files to data/current/
    print("\\n📦 Step 2: Moving current day files...")
    
    files_to_move = [
        ('races.json', 'Current race data'),
        ('bets.json', 'Current bet data'), 
        ('bankers.json', 'Current banker data')
    ]
    
    moved_files = []
    for filename, description in files_to_move:
        src_path = os.path.join(data_dir, filename)
        dest_path = os.path.join(current_dir, filename)
        
        try:
            if os.path.exists(src_path):
                shutil.move(src_path, dest_path)
                print(f"✅ Moved {filename} → current/{filename} ({description})")
                moved_files.append(filename)
            else:
                # Create empty file if it doesn't exist
                if filename == 'races.json':
                    default_data = []
                else:
                    default_data = {}
                
                with open(dest_path, 'w') as f:
                    json.dump(default_data, f, indent=2)
                print(f"✅ Created empty current/{filename} ({description})")
                moved_files.append(filename)
        except Exception as e:
            print(f"❌ Error moving {filename}: {e}")
            return False
    
    # Step 3: Create race_days index file
    print("\\n📚 Step 3: Creating race days index...")
    
    index_path = os.path.join(race_days_dir, 'index.json')
    index_data = {
        "availableDates": [],
        "lastUpdated": datetime.now().isoformat(),
        "totalRaceDays": 0,
        "metadata": {
            "structureVersion": "2.0",
            "createdAt": datetime.now().isoformat(),
            "description": "Historical race day data index"
        }
    }
    
    try:
        with open(index_path, 'w') as f:
            json.dump(index_data, f, indent=2)
        print(f"✅ Created: race_days/index.json")
    except Exception as e:
        print(f"❌ Error creating index: {e}")
        return False
    
    # Step 4: Backup existing race_days.json (if exists)
    print("\\n🔒 Step 4: Backup existing data...")
    
    old_race_days = os.path.join(data_dir, 'race_days.json')
    if os.path.exists(old_race_days):
        backup_path = os.path.join(data_dir, f'race_days_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        try:
            shutil.copy2(old_race_days, backup_path)
            print(f"✅ Backed up race_days.json → {os.path.basename(backup_path)}")
        except Exception as e:
            print(f"⚠️  Warning: Could not backup race_days.json: {e}")
    
    # Step 5: Display new structure
    print("\\n📋 Step 5: New file structure created!")
    print("\\n📁 NEW DIRECTORY STRUCTURE:")
    print("data/")
    print("├── users.json                    # User profiles (unchanged)")
    print("├── current/                      # 🆕 Current active race day")
    print("│   ├── races.json               # Current day races")
    print("│   ├── bets.json               # Current day bets")
    print("│   └── bankers.json            # Current day bankers")
    print("├── race_days/                   # 🆕 Historical completed race days")
    print("│   └── index.json              # Quick lookup of available dates")
    print("├── current_race_day.json       # Tracks current active race day")
    print("└── race_days.json              # Legacy file (will be phased out)")
    
    # Step 6: Show what was migrated
    print("\\n📦 MIGRATION SUMMARY:")
    print(f"✅ Created directories: current/, race_days/")
    print(f"✅ Moved files: {', '.join(moved_files)}")
    print(f"✅ Created index: race_days/index.json")
    print(f"✅ Ready for Task 2: Enhanced Reset Functionality")
    
    return True

def verify_migration():
    """Verify the migration was successful"""
    print("\\n🔍 VERIFICATION:")
    
    required_paths = [
        'data/current/',
        'data/current/races.json',
        'data/current/bets.json', 
        'data/current/bankers.json',
        'data/race_days/',
        'data/race_days/index.json'
    ]
    
    all_good = True
    for path in required_paths:
        if os.path.exists(path):
            print(f"✅ {path}")
        else:
            print(f"❌ {path} - MISSING!")
            all_good = False
    
    return all_good

if __name__ == "__main__":
    print("🏇 LEKOURS HISTORICAL DATA IMPLEMENTATION")
    print("Task 1: File Structure Migration")
    print("=" * 60)
    
    # Run migration
    success = task1_file_structure_migration()
    
    if success:
        # Verify migration
        verification_success = verify_migration()
        
        if verification_success:
            print("\\n🎉 TASK 1 COMPLETED SUCCESSFULLY!")
            print("\\n📋 NEXT STEPS:")
            print("1. Update server.py file paths (Task 1b)")
            print("2. Test current functionality still works")
            print("3. Commit changes")
            print("4. Proceed to Task 2: Enhanced Reset Functionality")
        else:
            print("\\n❌ VERIFICATION FAILED - Please check missing files")
    else:
        print("\\n❌ MIGRATION FAILED - Please check errors above")
    
    input("\\nPress Enter to continue...")
