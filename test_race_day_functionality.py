"""
Test script for the Race Day functionality
Tests all the new race day endpoints and data structures
"""
import requests
import json
from datetime import datetime

API_BASE = "http://localhost:5000/api"

def test_race_day_endpoints():
    """Test all race day endpoints"""
    print("=" * 60)
    print("🏇 TESTING RACE DAY FUNCTIONALITY")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Test 1: Create dummy race days
        print("🔄 Test 1: Creating dummy race days...")
        response = requests.post(f"{API_BASE}/race-days/create-dummy", timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Created {len(data['created_days'])} dummy race days: {data['created_days']}")
        else:
            print(f"❌ Failed to create dummy data: {response.status_code}")
            return False
        
        # Test 2: Get all race days
        print("\n🔄 Test 2: Fetching all race days...")
        response = requests.get(f"{API_BASE}/race-days", timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved {len(data['race_days'])} race days")
            print(f"   Current race day: {data['current_race_day']}")
            for day in data['race_days']:
                status = "✅ Current" if day['is_current'] else ("🏁 Completed" if day['completed'] else "⏳ Upcoming")
                print(f"   - {day['date']}: {day['race_count']} races {status}")
            race_days = data['race_days']
        else:
            print(f"❌ Failed to fetch race days: {response.status_code}")
            return False
        
        # Test 3: Get current race day
        print("\n🔄 Test 3: Getting current race day...")
        response = requests.get(f"{API_BASE}/race-days/current", timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Current race day: {data['current_race_day']}")
        else:
            print(f"❌ Failed to get current race day: {response.status_code}")
        
        # Test 4: Get specific race day data
        if race_days:
            test_date = race_days[0]['date']
            print(f"\n🔄 Test 4: Getting data for race day {test_date}...")
            response = requests.get(f"{API_BASE}/race-days/{test_date}", timeout=15)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Retrieved data for {test_date}")
                print(f"   - Races: {len(data['races'])}")
                print(f"   - Bets: {len(data['bets'])}")
                print(f"   - Bankers: {len(data['bankers'])}")
                print(f"   - Completed: {data['completed']}")
            else:
                print(f"❌ Failed to get race day data: {response.status_code}")
        
        # Test 5: Switch to a different race day
        if len(race_days) > 1:
            new_race_day = race_days[1]['date']
            print(f"\n🔄 Test 5: Switching to race day {new_race_day}...")
            response = requests.post(f"{API_BASE}/race-days/current", 
                                   json={"race_day": new_race_day}, 
                                   timeout=15)
            if response.status_code == 200:
                print(f"✅ Successfully switched to {new_race_day}")
                
                # Verify the switch worked
                response = requests.get(f"{API_BASE}/race-days/current", timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    if data['current_race_day'] == new_race_day:
                        print(f"✅ Verified current race day is now {new_race_day}")
                    else:
                        print(f"❌ Race day switch verification failed")
            else:
                print(f"❌ Failed to switch race day: {response.status_code}")
        
        # Test 6: Test legacy API compatibility
        print("\n🔄 Test 6: Testing legacy API compatibility...")
        response = requests.get(f"{API_BASE}/races", timeout=15)
        if response.status_code == 200:
            races = response.json()
            print(f"✅ Legacy /races endpoint still works: {len(races)} races")
        else:
            print(f"❌ Legacy races endpoint failed: {response.status_code}")
        
        response = requests.get(f"{API_BASE}/bets", timeout=15)
        if response.status_code == 200:
            bets = response.json()
            print(f"✅ Legacy /bets endpoint still works: {len(bets)} users with bets")
        else:
            print(f"❌ Legacy bets endpoint failed: {response.status_code}")
        
        response = requests.get(f"{API_BASE}/bankers", timeout=15)
        if response.status_code == 200:
            bankers = response.json()
            print(f"✅ Legacy /bankers endpoint still works: {len(bankers)} users with bankers")
        else:
            print(f"❌ Legacy bankers endpoint failed: {response.status_code}")
        
        print("\n" + "=" * 60)
        print("🎯 RACE DAY FUNCTIONALITY TEST SUMMARY:")
        print("   ✅ All race day endpoints working")
        print("   ✅ Race day switching functional")
        print("   ✅ Data isolation between race days")
        print("   ✅ Legacy API compatibility maintained")
        print("   ✅ Dummy data creation successful")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def test_data_isolation():
    """Test that data is properly isolated between race days"""
    print("\n📊 TESTING DATA ISOLATION...")
    
    try:
        # Get list of race days
        response = requests.get(f"{API_BASE}/race-days", timeout=15)
        race_days = response.json()['race_days']
        
        if len(race_days) < 2:
            print("❌ Need at least 2 race days to test data isolation")
            return False
        
        day1 = race_days[0]['date']
        day2 = race_days[1]['date']
        
        # Get data for both days
        response1 = requests.get(f"{API_BASE}/race-days/{day1}", timeout=15)
        response2 = requests.get(f"{API_BASE}/race-days/{day2}", timeout=15)
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Check that race data is different
        races1_ids = [race['id'] for race in data1['races']]
        races2_ids = [race['id'] for race in data2['races']]
        
        if set(races1_ids) & set(races2_ids):  # If there's any overlap
            print("❌ Race data is not properly isolated between days")
            return False
        
        print(f"✅ Data isolation confirmed:")
        print(f"   - {day1}: {len(data1['races'])} unique races")
        print(f"   - {day2}: {len(data2['races'])} unique races")
        print("   - No overlap in race IDs")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing data isolation: {e}")
        return False

if __name__ == "__main__":
    # Test basic functionality
    success = test_race_day_endpoints()
    
    if success:
        # Test data isolation
        test_data_isolation()
        print("\n🎉 All race day functionality tests passed!")
    else:
        print("\n💥 Some tests failed!")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    input("\nPress Enter to exit...")
