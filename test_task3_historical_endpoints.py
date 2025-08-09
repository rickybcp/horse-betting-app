#!/usr/bin/env python3
"""
Test Task 3: Historical Data API Endpoints
Test all new endpoints for historical data access
"""

import requests
import json
import time
from datetime import datetime

API_BASE = "http://localhost:5000/api"

def wait_for_server():
    """Wait for server to start"""
    print("⏳ Waiting for server to start...")
    for i in range(10):
        try:
            response = requests.get(f"{API_BASE}/users", timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready!")
                return True
        except:
            time.sleep(1)
    print("❌ Server not responding")
    return False

def test_historical_race_days():
    """Test GET /api/race-days/historical"""
    print("📚 TESTING HISTORICAL RACE DAYS ENDPOINT")
    print("-" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/race-days/historical", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Historical race days endpoint working!")
            print(f"   📊 Total Race Days: {data['totalRaceDays']}")
            print(f"   🕐 Last Updated: {data['lastUpdated']}")
            
            if data['raceDays']:
                print(f"   📅 Available Dates:")
                for day in data['raceDays'][:3]:  # Show first 3
                    print(f"      {day['date']}: {day['highestScore']} top score ({day['topUser']})")
            
            return data
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_specific_race_day(race_date):
    """Test GET /api/race-days/historical/:date"""
    print(f"\\n🏁 TESTING SPECIFIC RACE DAY: {race_date}")
    print("-" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/race-days/historical/{race_date}", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            race_day = data['raceDay']
            
            print(f"✅ Specific race day endpoint working!")
            print(f"   📅 Date: {race_day['date']}")
            print(f"   🏇 Races: {race_day['completedRaces']}/{race_day['totalRaces']}")
            print(f"   📊 Status: {race_day['status']}")
            print(f"   👥 Users: {len(race_day.get('userScores', []))}")
            
            # Show top 3 performers
            user_scores = race_day.get('userScores', [])
            if user_scores:
                sorted_scores = sorted(user_scores, key=lambda x: x['dailyScore'], reverse=True)
                print(f"   🏆 Top Performers:")
                for i, user in enumerate(sorted_scores[:3]):
                    banker_info = " (Banker bonus!)" if user.get('bankerMultiplierApplied') else ""
                    print(f"      {i+1}. {user['userName']}: {user['dailyScore']} points{banker_info}")
            
            return race_day
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_user_history(user_id="1"):
    """Test GET /api/users/:userId/history"""
    print(f"\\n👤 TESTING USER HISTORY: User {user_id}")
    print("-" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/users/{user_id}/history", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            history = data['userHistory']
            
            print(f"✅ User history endpoint working!")
            print(f"   👤 User: {history['userName']} (ID: {history['userId']})")
            print(f"   💰 Total Score: {history['totalScore']}")
            print(f"   🏁 Race Days Played: {history['totalRaceDays']}")
            print(f"   🏆 Best Day: {history['bestDayScore']} points ({history['bestDayDate']})")
            print(f"   📈 Average Score: {history['averageScore']:.1f}")
            
            if history['raceDays']:
                print(f"   📅 Recent Performance:")
                for day in history['raceDays'][:3]:  # Show last 3 days
                    banker_info = " + Banker!" if day['bankerMultiplierApplied'] else ""
                    print(f"      {day['date']}: {day['dailyScore']} points ({day['betsWon']}/{day['totalBets']} bets){banker_info}")
            
            return history
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_user_performance_on_date(user_id="2", race_date="2025-08-09"):
    """Test GET /api/users/:userId/history/:date"""
    print(f"\\n📊 TESTING USER PERFORMANCE ON DATE: User {user_id} on {race_date}")
    print("-" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/users/{user_id}/history/{race_date}", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            performance = data['performance']
            user_perf = performance['userPerformance']
            race_day = performance['raceDay']
            
            print(f"✅ User performance on date endpoint working!")
            print(f"   👤 User: {user_perf['userName']}")
            print(f"   📅 Date: {performance['raceDate']}")
            print(f"   💰 Daily Score: {user_perf['dailyScore']}")
            print(f"   🎯 Base Points: {user_perf.get('basePoints', 0)}")
            print(f"   💥 Banker Bonus: {'Yes' if user_perf.get('bankerMultiplierApplied') else 'No'}")
            print(f"   🏇 Bets: {user_perf['betsWon']}/{user_perf['totalBets']} won ({user_perf['winRate']:.1%})")
            
            print(f"   🏁 Race Day Context:")
            print(f"      Races: {race_day['completedRaces']}/{race_day['totalRaces']}")
            print(f"      Top Score: {race_day['highestScore']}")
            print(f"      Average Score: {race_day['averageScore']:.1f}")
            
            return performance
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_enhanced_leaderboard():
    """Test GET /api/leaderboard/enhanced"""
    print(f"\\n🏆 TESTING ENHANCED LEADERBOARD")
    print("-" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/leaderboard/enhanced", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            leaderboard = data['leaderboard']
            summary = data['summary']
            
            print(f"✅ Enhanced leaderboard endpoint working!")
            print(f"   👥 Total Users: {summary['totalUsers']}")
            print(f"   🏃 Active Users: {summary['activeUsers']}")
            print(f"   🏆 Highest Score: {summary['highestScore']}")
            
            print(f"   🥇 TOP 5 LEADERBOARD:")
            for user in leaderboard[:5]:
                stats = user['statistics']
                print(f"      {user['rank']}. {user['name']}: {user['totalScore']} points")
                print(f"         📊 {stats['raceDaysPlayed']} days, avg {stats['averageScore']:.1f}, best {stats['bestDayScore']}")
            
            return leaderboard
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_current_race_day_status():
    """Test GET /api/race-day/current/status"""
    print(f"\\n📈 TESTING CURRENT RACE DAY STATUS")
    print("-" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/race-day/current/status", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            status = data['status']
            
            print(f"✅ Current race day status endpoint working!")
            print(f"   📅 Current Date: {status['date']}")
            print(f"   🕐 Current Time: {status['time']}")
            
            races = status['races']
            print(f"   🏇 Races: {races['completed']}/{races['total']} completed ({races['progress']:.1f}%)")
            
            betting = status['betting']
            print(f"   🎰 Betting: {betting['activeUsers']} users, {betting['totalBets']} bets, {betting['bankerSelections']} bankers")
            
            if status['nextRace']:
                next_race = status['nextRace']
                print(f"   ⏭️  Next Race: {next_race['name']} at {next_race['time']}")
            
            print(f"   ✅ Day Complete: {'Yes' if status['isComplete'] else 'No'}")
            
            return status
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Run all Task 3 endpoint tests"""
    print("🚀 TASK 3 HISTORICAL DATA API ENDPOINTS TEST")
    print("=" * 70)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Wait for server
    if not wait_for_server():
        print("❌ Server not available, aborting tests")
        return
    
    # Run tests for all new endpoints
    historical_days = test_historical_race_days()
    
    # Test specific race day (use today's date from the historical data)
    race_date = "2025-08-09"
    if historical_days and historical_days['raceDays']:
        race_date = historical_days['raceDays'][0]['date']
    
    specific_day = test_specific_race_day(race_date)
    
    # Test user history (Ben and Michelle)
    ben_history = test_user_history("1")
    michelle_history = test_user_history("2")
    
    # Test user performance on specific date (Michelle had best score)
    michelle_performance = test_user_performance_on_date("2", race_date)
    
    # Test enhanced leaderboard
    leaderboard = test_enhanced_leaderboard()
    
    # Test current race day status
    current_status = test_current_race_day_status()
    
    # Summary
    print("\\n" + "=" * 70)
    print("🎯 TASK 3 ENDPOINT TEST RESULTS:")
    print("=" * 70)
    
    tests = [
        ("Historical Race Days", historical_days is not None),
        ("Specific Race Day", specific_day is not None),
        ("User History (Ben)", ben_history is not None),
        ("User History (Michelle)", michelle_history is not None),
        ("User Performance on Date", michelle_performance is not None),
        ("Enhanced Leaderboard", leaderboard is not None),
        ("Current Race Day Status", current_status is not None)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name:<25}: {status}")
        if result:
            passed += 1
    
    print("-" * 70)
    print(f"   OVERALL: {passed}/{total} endpoints working")
    
    if passed == total:
        print("\\n🎉 TASK 3 COMPLETED SUCCESSFULLY!")
        print("\\n📋 NEW API ENDPOINTS WORKING:")
        print("   ✅ GET /api/race-days/historical - List all completed race days")
        print("   ✅ GET /api/race-days/historical/:date - Get specific race day data")
        print("   ✅ GET /api/users/:userId/history - User's complete history")
        print("   ✅ GET /api/users/:userId/history/:date - User's performance on date")
        print("   ✅ GET /api/leaderboard/enhanced - Enhanced leaderboard with stats")
        print("   ✅ GET /api/race-day/current/status - Current race day progress")
        print("\\n🎯 READY FOR PRODUCTION - ALL TASKS COMPLETED!")
    else:
        print(f"\\n⚠️  SOME ENDPOINTS FAILED ({total-passed} failures)")
        print("Please check server logs for details")
        
    print(f"\\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
    input("\\nPress Enter to continue...")
