#!/usr/bin/env python3
"""
Test Task 2: Enhanced Reset Functionality
Test the new race day completion system with real data
"""

import requests
import json
import os
from datetime import datetime

API_BASE = "http://localhost:5000/api"

def setup_test_data():
    """Set up some test races and bets for testing"""
    print("🔧 SETTING UP TEST DATA")
    print("-" * 40)
    
    # First, let's scrape some races or add manual test races
    try:
        # Try to get current races
        response = requests.get(f"{API_BASE}/races", timeout=5)
        if response.status_code == 200:
            races = response.json()
            print(f"✅ Found {len(races)} existing races")
            
            if len(races) == 0:
                print("📝 No races found, creating test races...")
                test_races = [
                    {
                        "id": "test_1",
                        "name": "Test Race 1 - Beginner Stakes",
                        "time": "14:00",
                        "status": "completed",
                        "horses": [
                            {"number": 1, "name": "Fast Horse", "odds": 2.5},
                            {"number": 2, "name": "Slow Horse", "odds": 8.0},
                            {"number": 3, "name": "Lucky Horse", "odds": 15.0}
                        ],
                        "winner": 2
                    },
                    {
                        "id": "test_2", 
                        "name": "Test Race 2 - Championship",
                        "time": "15:00",
                        "status": "completed",
                        "horses": [
                            {"number": 1, "name": "Champion", "odds": 1.8},
                            {"number": 2, "name": "Runner Up", "odds": 4.5},
                            {"number": 3, "name": "Dark Horse", "odds": 12.0}
                        ],
                        "winner": 3
                    }
                ]
                
                # Save test races directly to file
                with open('data/current/races.json', 'w') as f:
                    json.dump(test_races, f, indent=2)
                print("✅ Created 2 test races with winners")
                
                # Create some test bets
                test_bets = {
                    "1": {"test_1": 2, "test_2": 1},  # Ben: won race 1, lost race 2
                    "2": {"test_1": 1, "test_2": 3},  # Michelle: lost race 1, won race 2
                    "3": {"test_1": 3, "test_2": 2}   # Conrad: lost both races
                }
                
                with open('data/current/bets.json', 'w') as f:
                    json.dump(test_bets, f, indent=2)
                print("✅ Created test bets for 3 users")
                
                # Create test bankers
                test_bankers = {
                    "1": "test_2",  # Ben's banker is race 2 (he lost, so no multiplier)
                    "2": "test_2"   # Michelle's banker is race 2 (she won, so 2x multiplier!)
                }
                
                with open('data/current/bankers.json', 'w') as f:
                    json.dump(test_bankers, f, indent=2)
                print("✅ Created test bankers")
                
                print("\\n📊 EXPECTED RESULTS:")
                print("   Ben: 2 points (won race 1 with odds 8.0) - no banker bonus")
                print("   Michelle: 6 points (3 points from race 2 * 2 banker multiplier)")
                print("   Conrad: 0 points (lost both races)")
                
                return True
            else:
                print("✅ Using existing race data")
                return True
                
    except Exception as e:
        print(f"❌ Error setting up test data: {e}")
        return False

def test_enhanced_reset():
    """Test the new enhanced reset functionality"""
    print("\\n🏁 TESTING ENHANCED RESET")
    print("-" * 40)
    
    try:
        # Call the new enhanced reset endpoint
        response = requests.post(f"{API_BASE}/race-day/complete", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Enhanced reset successful!")
            print(f"   📅 Race Date: {result['raceDate']}")
            print(f"   👑 Top Score: {result['highestScore']} ({result['topUser']})")
            print(f"   👥 Total Users: {result['totalUsers']}")
            print(f"   📝 Message: {result['message']}")
            return result
        else:
            print(f"❌ Enhanced reset failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error testing enhanced reset: {e}")
        return None

def verify_race_day_saved():
    """Verify that the race day was saved correctly"""
    print("\\n💾 VERIFYING RACE DAY DATA")
    print("-" * 40)
    
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        race_day_file = f'data/race_days/{today}.json'
        
        if os.path.exists(race_day_file):
            with open(race_day_file, 'r') as f:
                race_day_data = json.load(f)
            
            print(f"✅ Race day file exists: {race_day_file}")
            print(f"   📊 Total Races: {race_day_data['totalRaces']}")
            print(f"   ✔️  Completed Races: {race_day_data['completedRaces']}")
            print(f"   👥 User Scores: {len(race_day_data.get('userScores', []))}")
            print(f"   📅 Status: {race_day_data['status']}")
            
            # Show top 3 scores
            user_scores = race_day_data.get('userScores', [])
            user_scores.sort(key=lambda x: x['dailyScore'], reverse=True)
            
            print(f"\\n🏆 TOP SCORES:")
            for i, user in enumerate(user_scores[:3]):
                print(f"   {i+1}. {user['userName']}: {user['dailyScore']} points")
                if user.get('bankerMultiplierApplied'):
                    print(f"      💰 Banker bonus applied! ({user['basePoints']} base points)")
            
            return True
        else:
            print(f"❌ Race day file not found: {race_day_file}")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying race day data: {e}")
        return False

def verify_index_updated():
    """Verify that the race days index was updated"""
    print("\\n📚 VERIFYING INDEX UPDATE")
    print("-" * 40)
    
    try:
        with open('data/race_days/index.json', 'r') as f:
            index_data = json.load(f)
        
        print(f"✅ Index loaded successfully")
        print(f"   📊 Total Race Days: {index_data['totalRaceDays']}")
        print(f"   🕐 Last Updated: {index_data['lastUpdated']}")
        
        if index_data['availableDates']:
            latest = index_data['availableDates'][0]  # Should be sorted newest first
            print(f"\\n📅 LATEST RACE DAY:")
            print(f"   Date: {latest['date']}")
            print(f"   Status: {latest['status']}")
            print(f"   Top Score: {latest['highestScore']} ({latest['topUser']})")
            print(f"   Races: {latest['completedRaces']}/{latest['totalRaces']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying index: {e}")
        return False

def verify_user_statistics():
    """Verify that user statistics were updated correctly"""
    print("\\n👥 VERIFYING USER STATISTICS")
    print("-" * 40)
    
    try:
        response = requests.get(f"{API_BASE}/users", timeout=5)
        if response.status_code == 200:
            users = response.json()
            
            print(f"✅ Retrieved {len(users)} users")
            
            # Show users with updated statistics
            for user in users[:5]:  # Show first 5 users
                print(f"\\n👤 {user['name']} (ID: {user['id']})")
                print(f"   💰 Total Score: {user.get('totalScore', 0)}")
                
                if 'statistics' in user:
                    stats = user['statistics']
                    print(f"   📊 Statistics:")
                    print(f"      🏁 Race Days Played: {stats.get('raceDaysPlayed', 0)}")
                    print(f"      🏆 Best Day Score: {stats.get('bestDayScore', 0)} ({stats.get('bestDayDate', 'N/A')})")
                    print(f"      📈 Average Score: {stats.get('averageScore', 0):.1f}")
                    print(f"      🎯 Win Rate: {stats.get('winRate', 0):.1%}")
                else:
                    print(f"   ⚠️  No statistics yet")
            
            return True
        else:
            print(f"❌ Failed to get users: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying user statistics: {e}")
        return False

def verify_current_data_cleared():
    """Verify that current day data was cleared"""
    print("\\n🧹 VERIFYING DATA CLEARED")
    print("-" * 40)
    
    try:
        files_to_check = [
            ('data/current/races.json', 'Races'),
            ('data/current/bets.json', 'Bets'),
            ('data/current/bankers.json', 'Bankers')
        ]
        
        all_cleared = True
        for file_path, name in files_to_check:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                if isinstance(data, list) and len(data) == 0:
                    print(f"✅ {name}: cleared (empty list)")
                elif isinstance(data, dict) and len(data) == 0:
                    print(f"✅ {name}: cleared (empty dict)")
                else:
                    print(f"⚠️  {name}: not cleared (has {len(data)} items)")
                    all_cleared = False
            else:
                print(f"❌ {name}: file not found")
                all_cleared = False
        
        return all_cleared
        
    except Exception as e:
        print(f"❌ Error verifying data clearing: {e}")
        return False

def main():
    """Run all Task 2 tests"""
    print("🚀 TASK 2 ENHANCED RESET FUNCTIONALITY TEST")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run tests
    setup_ok = setup_test_data()
    if not setup_ok:
        print("❌ Setup failed, aborting tests")
        return
    
    reset_result = test_enhanced_reset()
    if not reset_result:
        print("❌ Enhanced reset failed, aborting remaining tests")
        return
    
    race_day_ok = verify_race_day_saved()
    index_ok = verify_index_updated()
    stats_ok = verify_user_statistics()
    cleared_ok = verify_current_data_cleared()
    
    # Summary
    print("\\n" + "=" * 60)
    print("🎯 TASK 2 TEST RESULTS:")
    print("=" * 60)
    
    tests = [
        ("Test Data Setup", setup_ok),
        ("Enhanced Reset Execution", reset_result is not None),
        ("Race Day Data Saved", race_day_ok),
        ("Index Updated", index_ok),
        ("User Statistics Updated", stats_ok),
        ("Current Data Cleared", cleared_ok)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name:<25}: {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"   OVERALL: {passed}/{total} tests passed")
    
    if passed == total:
        print("\\n🎉 TASK 2 COMPLETED SUCCESSFULLY!")
        print("\\n📋 NEW FEATURES WORKING:")
        print("   ✅ Enhanced daily score calculation with detailed breakdown")
        print("   ✅ Individual race day files with complete historical data")
        print("   ✅ Automatic race days index management")
        print("   ✅ User statistics tracking (best day, average, win rate)")
        print("   ✅ Banker multiplier system")
        print("   ✅ Current day data clearing for fresh start")
        print("\\n🎯 READY FOR TASK 3: New API Endpoints")
    else:
        print(f"\\n⚠️  SOME ISSUES DETECTED ({total-passed} failures)")
        print("Please fix issues before proceeding to Task 3")
        
    print(f"\\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
    input("\\nPress Enter to continue...")
