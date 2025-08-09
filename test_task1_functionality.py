#!/usr/bin/env python3
"""
Test Task 1: Verify file structure migration worked correctly
"""

import requests
import json
import os
from datetime import datetime

API_BASE = "http://localhost:5000/api"

def test_file_structure():
    """Test that the new file structure exists and is correct"""
    print("📁 TESTING FILE STRUCTURE")
    print("-" * 40)
    
    required_paths = [
        'data/current/',
        'data/current/races.json',
        'data/current/bets.json', 
        'data/current/bankers.json',
        'data/race_days/',
        'data/race_days/index.json',
        'data/users.json'
    ]
    
    all_good = True
    for path in required_paths:
        if os.path.exists(path):
            print(f"✅ {path}")
        else:
            print(f"❌ {path} - MISSING!")
            all_good = False
    
    return all_good

def test_api_endpoints():
    """Test that all API endpoints still work"""
    print("\\n🔌 TESTING API ENDPOINTS")
    print("-" * 40)
    
    endpoints = [
        ('GET', '/users', 'Users endpoint'),
        ('GET', '/races', 'Current races endpoint'),
        ('GET', '/bets', 'Current bets endpoint'),
        ('GET', '/bankers', 'Current bankers endpoint')
    ]
    
    all_good = True
    for method, endpoint, description in endpoints:
        try:
            response = requests.get(f"{API_BASE}{endpoint}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {description}: {response.status_code} ({len(data)} items)")
            else:
                print(f"❌ {description}: {response.status_code}")
                all_good = False
        except Exception as e:
            print(f"❌ {description}: Error - {e}")
            all_good = False
    
    return all_good

def test_data_integrity():
    """Test that data moved correctly to new locations"""
    print("\\n📊 TESTING DATA INTEGRITY")
    print("-" * 40)
    
    try:
        # Check that current races exist
        with open('data/current/races.json', 'r') as f:
            races = json.load(f)
        print(f"✅ Current races: {len(races)} races loaded")
        
        # Check that race days index exists
        with open('data/race_days/index.json', 'r') as f:
            index = json.load(f)
        print(f"✅ Race days index: {index['totalRaceDays']} race days indexed")
        
        # Check that users still exist
        with open('data/users.json', 'r') as f:
            users = json.load(f)
        print(f"✅ Users data: {len(users)} users preserved")
        
        return True
        
    except Exception as e:
        print(f"❌ Data integrity error: {e}")
        return False

def main():
    """Run all Task 1 tests"""
    print("🚀 TASK 1 VERIFICATION TEST")
    print("=" * 50)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run tests
    structure_ok = test_file_structure()
    api_ok = test_api_endpoints()
    data_ok = test_data_integrity()
    
    # Summary
    print("\\n" + "=" * 50)
    print("🎯 TASK 1 VERIFICATION RESULTS:")
    print("=" * 50)
    
    tests = [
        ("File Structure", structure_ok),
        ("API Endpoints", api_ok),
        ("Data Integrity", data_ok)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name:<15}: {status}")
        if result:
            passed += 1
    
    print("-" * 50)
    print(f"   OVERALL: {passed}/{total} tests passed")
    
    if passed == total:
        print("\\n🎉 TASK 1 COMPLETED SUCCESSFULLY!")
        print("\\n📋 SUMMARY OF CHANGES:")
        print("   ✅ Created data/current/ directory")
        print("   ✅ Created data/race_days/ directory") 
        print("   ✅ Moved race data to data/current/races.json")
        print("   ✅ Moved bet data to data/current/bets.json")
        print("   ✅ Moved banker data to data/current/bankers.json")
        print("   ✅ Created race_days/index.json")
        print("   ✅ Updated server.py file paths")
        print("   ✅ All API endpoints working")
        print("\\n🎯 READY FOR TASK 2: Enhanced Reset Functionality")
    else:
        print(f"\\n⚠️  SOME ISSUES DETECTED ({total-passed} failures)")
        print("Please fix issues before proceeding to Task 2")
        
    print(f"\\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
    input("\\nPress Enter to continue...")
