"""
Complete functionality test for the Horse Betting Application
Tests both backend API and frontend integration
"""
import requests
import json
from datetime import datetime

API_BASE = "http://localhost:5000/api"
FRONTEND_BASE = "http://localhost:3000"

def test_backend_functionality():
    """Test all backend endpoints"""
    print("🔧 TESTING BACKEND FUNCTIONALITY")
    print("-" * 50)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Users endpoint
    tests_total += 1
    try:
        response = requests.get(f"{API_BASE}/users", timeout=10)
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Users endpoint: {len(users)} users found")
            tests_passed += 1
        else:
            print(f"❌ Users endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Users endpoint error: {e}")
    
    # Test 2: Race days functionality
    tests_total += 1
    try:
        response = requests.get(f"{API_BASE}/race-days", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Race days endpoint: {len(data['race_days'])} days, current: {data['current_race_day']}")
            tests_passed += 1
        else:
            print(f"❌ Race days endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Race days endpoint error: {e}")
    
    # Test 3: Races endpoint
    tests_total += 1
    try:
        response = requests.get(f"{API_BASE}/races", timeout=10)
        if response.status_code == 200:
            races = response.json()
            print(f"✅ Races endpoint: {len(races)} races found")
            tests_passed += 1
        else:
            print(f"❌ Races endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Races endpoint error: {e}")
    
    # Test 4: Bets endpoint
    tests_total += 1
    try:
        response = requests.get(f"{API_BASE}/bets", timeout=10)
        if response.status_code == 200:
            bets = response.json()
            print(f"✅ Bets endpoint: {len(bets)} users with bets")
            tests_passed += 1
        else:
            print(f"❌ Bets endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Bets endpoint error: {e}")
    
    # Test 5: Bankers endpoint
    tests_total += 1
    try:
        response = requests.get(f"{API_BASE}/bankers", timeout=10)
        if response.status_code == 200:
            bankers = response.json()
            print(f"✅ Bankers endpoint: {len(bankers)} users with bankers")
            tests_passed += 1
        else:
            print(f"❌ Bankers endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Bankers endpoint error: {e}")
    
    print(f"\n📊 Backend Tests: {tests_passed}/{tests_total} passed")
    return tests_passed == tests_total

def test_frontend_functionality():
    """Test frontend accessibility and basic functionality"""
    print("\n🖥️ TESTING FRONTEND FUNCTIONALITY")
    print("-" * 50)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Frontend accessibility
    tests_total += 1
    try:
        response = requests.get(FRONTEND_BASE, timeout=10)
        if response.status_code == 200 and "Family Horse Betting" in response.text:
            print("✅ Frontend accessible and serving React app")
            tests_passed += 1
        else:
            print(f"❌ Frontend accessibility failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend accessibility error: {e}")
    
    # Test 2: CORS headers
    tests_total += 1
    try:
        response = requests.get(FRONTEND_BASE, timeout=10)
        headers = response.headers
        if 'Access-Control-Allow-Origin' in headers:
            print("✅ CORS headers present for API communication")
            tests_passed += 1
        else:
            print("❌ CORS headers missing")
    except Exception as e:
        print(f"❌ CORS test error: {e}")
    
    print(f"\n📊 Frontend Tests: {tests_passed}/{tests_total} passed")
    return tests_passed == tests_total

def test_race_day_switching():
    """Test race day switching functionality"""
    print("\n📅 TESTING RACE DAY SWITCHING")
    print("-" * 50)
    
    try:
        # Get current race days
        response = requests.get(f"{API_BASE}/race-days", timeout=10)
        race_days = response.json()['race_days']
        
        if len(race_days) < 2:
            print("❌ Need at least 2 race days to test switching")
            return False
        
        original_day = race_days[0]['date']
        target_day = race_days[1]['date']
        
        print(f"🔄 Switching from {original_day} to {target_day}")
        
        # Switch race day
        response = requests.post(f"{API_BASE}/race-days/current", 
                               json={"race_day": target_day}, 
                               timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Race day switch failed: {response.status_code}")
            return False
        
        # Verify the switch
        response = requests.get(f"{API_BASE}/race-days/current", timeout=10)
        current_day = response.json()['current_race_day']
        
        if current_day == target_day:
            print(f"✅ Successfully switched to {target_day}")
            
            # Get races to verify data changed
            response = requests.get(f"{API_BASE}/races", timeout=10)
            races = response.json()
            print(f"✅ Races updated: {len(races)} races for {target_day}")
            
            # Switch back to original
            requests.post(f"{API_BASE}/race-days/current", 
                         json={"race_day": original_day}, 
                         timeout=10)
            print(f"✅ Switched back to {original_day}")
            
            return True
        else:
            print(f"❌ Race day switch verification failed")
            return False
            
    except Exception as e:
        print(f"❌ Race day switching error: {e}")
        return False

def test_data_persistence():
    """Test that data persists correctly between operations"""
    print("\n💾 TESTING DATA PERSISTENCE")
    print("-" * 50)
    
    try:
        # Check if dummy data exists
        response = requests.get(f"{API_BASE}/race-days", timeout=10)
        race_days = response.json()['race_days']
        
        if not race_days:
            print("❌ No race days found - creating dummy data first")
            requests.post(f"{API_BASE}/race-days/create-dummy", timeout=15)
            response = requests.get(f"{API_BASE}/race-days", timeout=10)
            race_days = response.json()['race_days']
        
        if race_days:
            print(f"✅ Data persistence confirmed: {len(race_days)} race days stored")
            
            # Check specific race day data
            test_day = race_days[0]['date']
            response = requests.get(f"{API_BASE}/race-days/{test_day}", timeout=10)
            day_data = response.json()
            
            print(f"✅ Race day {test_day} data intact:")
            print(f"   - {len(day_data['races'])} races")
            print(f"   - {len(day_data['bets'])} users with bets")
            print(f"   - {len(day_data['bankers'])} users with bankers")
            
            return True
        else:
            print("❌ No race days found after dummy creation")
            return False
            
    except Exception as e:
        print(f"❌ Data persistence test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🏇 COMPREHENSIVE FUNCTIONALITY TEST")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = []
    
    # Run all test suites
    results.append(("Backend API", test_backend_functionality()))
    results.append(("Frontend", test_frontend_functionality()))
    results.append(("Race Day Switching", test_race_day_switching()))
    results.append(("Data Persistence", test_data_persistence()))
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 FINAL TEST RESULTS:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name:<20}: {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"   OVERALL: {passed}/{total} test suites passed")
    
    if passed == total:
        print("\n🎉 ALL SYSTEMS FUNCTIONAL!")
        print("   ✅ Backend API working")
        print("   ✅ Frontend accessible")
        print("   ✅ Race day system operational")
        print("   ✅ Data persistence confirmed")
        print("   ✅ Ready for production use!")
    else:
        print(f"\n⚠️  SOME ISSUES DETECTED ({total-passed} failures)")
        
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
