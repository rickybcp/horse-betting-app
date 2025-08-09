#!/usr/bin/env python3
"""
Task 2: Enhanced Reset Functionality
Core functions for the new race day completion system
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple

# File paths (matching server.py)
DATA_DIR = 'data'
CURRENT_DIR = os.path.join(DATA_DIR, 'current')
RACE_DAYS_DIR = os.path.join(DATA_DIR, 'race_days')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
RACES_FILE = os.path.join(CURRENT_DIR, 'races.json')
BETS_FILE = os.path.join(CURRENT_DIR, 'bets.json')
BANKERS_FILE = os.path.join(CURRENT_DIR, 'bankers.json')
RACE_DAYS_INDEX_FILE = os.path.join(RACE_DAYS_DIR, 'index.json')

def load_json(filepath: str, default=None):
    """Load JSON data from file or return default if file doesn't exist"""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {filepath}. Returning default.")
    
    # Return appropriate default
    if 'users' in filepath or 'races' in filepath:
        return default if default is not None else []
    else:
        return default if default is not None else {}

def save_json(filepath: str, data):
    """Save data to JSON file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def calculate_daily_scores() -> Dict[str, Dict]:
    """
    Calculate all user scores for current race day
    Returns: {user_id: {daily_score, bets_won, total_bets, banker_won, etc.}}
    """
    print("🧮 Calculating daily scores...")
    
    # Load current data
    users = load_json(USERS_FILE, [])
    current_races = load_json(RACES_FILE, [])
    current_bets = load_json(BETS_FILE, {})
    current_bankers = load_json(BANKERS_FILE, {})
    
    user_scores = {}
    
    for user in users:
        user_id = user['id']
        user_name = user['name']
        
        # Initialize user score data
        user_score_data = {
            "userId": user_id,
            "userName": user_name,
            "dailyScore": 0,
            "basePoints": 0,
            "afterBankerMultiplier": 0,
            "bankerRaceId": current_bankers.get(user_id),
            "bankerWon": False,
            "bankerMultiplierApplied": False,
            "bets": [],
            "betsWon": 0,
            "totalBets": 0,
            "winRate": 0.0,
            "pointsBreakdown": {
                "basePoints": 0,
                "afterBankerMultiplier": 0
            }
        }
        
        base_points = 0
        user_bets = current_bets.get(user_id, {})
        
        # Calculate points from each race
        for race in current_races:
            race_id = race['id']
            
            if race_id in user_bets:
                user_score_data["totalBets"] += 1
                user_bet = user_bets[race_id]
                
                bet_data = {
                    "raceId": race_id,
                    "raceName": race.get('name', f'Race {race_id}'),
                    "horseNumber": user_bet,
                    "won": False,
                    "points": 0
                }
                
                # Check if bet won
                if race.get('winner') and user_bet == race['winner']:
                    user_score_data["betsWon"] += 1
                    bet_data["won"] = True
                    
                    # Calculate points based on odds
                    winner_horse = next((h for h in race['horses'] if h['number'] == race['winner']), None)
                    if winner_horse:
                        odds = winner_horse['odds']
                        points = 1
                        if odds > 10: 
                            points = 3
                        elif odds > 5: 
                            points = 2
                        
                        bet_data["points"] = points
                        base_points += points
                
                user_score_data["bets"].append(bet_data)
        
        # Calculate win rate
        if user_score_data["totalBets"] > 0:
            user_score_data["winRate"] = user_score_data["betsWon"] / user_score_data["totalBets"]
        
        user_score_data["basePoints"] = base_points
        user_score_data["pointsBreakdown"]["basePoints"] = base_points
        
        # Apply banker bonus if applicable
        daily_score = base_points
        if current_bankers.get(user_id):
            banker_race_id = str(current_bankers[user_id])
            user_score_data["bankerRaceId"] = banker_race_id
            
            # Check if user won their banker race
            if (banker_race_id in user_bets and 
                any(race['id'] == banker_race_id and race.get('winner') == user_bets[banker_race_id] 
                    for race in current_races)):
                user_score_data["bankerWon"] = True
                user_score_data["bankerMultiplierApplied"] = True
                daily_score *= 2
        
        user_score_data["dailyScore"] = daily_score
        user_score_data["afterBankerMultiplier"] = daily_score
        user_score_data["pointsBreakdown"]["afterBankerMultiplier"] = daily_score
        
        user_scores[user_id] = user_score_data
        
        print(f"  ✅ {user_name}: {daily_score} points ({user_score_data['betsWon']}/{user_score_data['totalBets']} bets)")
    
    print(f"✅ Calculated scores for {len(user_scores)} users")
    return user_scores

def save_completed_race_day(race_date: str, user_scores: Dict) -> bool:
    """
    Save completed race day to individual file and update index
    """
    print(f"💾 Saving completed race day: {race_date}")
    
    try:
        # Load current data
        current_races = load_json(RACES_FILE, [])
        
        # Create race day data structure
        race_day_data = {
            "date": race_date,
            "totalRaces": len(current_races),
            "completedRaces": len([r for r in current_races if r.get('winner')]),
            "status": "completed",
            "completedAt": datetime.now().isoformat(),
            "races": []
        }
        
        # Add race details with winners
        for race in current_races:
            race_data = {
                "id": race['id'],
                "name": race.get('name', f'Race {race["id"]}'),
                "time": race.get('time', ''),
                "winner": race.get('winner'),
                "totalHorses": len(race.get('horses', [])),
                "status": race.get('status', 'unknown')
            }
            
            # Add winning horse details if available
            if race.get('winner'):
                winner_horse = next((h for h in race['horses'] if h['number'] == race['winner']), None)
                if winner_horse:
                    race_data["winningHorse"] = {
                        "number": winner_horse['number'],
                        "name": winner_horse['name'],
                        "odds": winner_horse['odds'],
                        "points": 3 if winner_horse['odds'] > 10 else (2 if winner_horse['odds'] > 5 else 1)
                    }
            
            race_day_data["races"].append(race_data)
        
        # Add user scores
        race_day_data["userScores"] = list(user_scores.values())
        
        # Save to individual race day file
        race_day_file = os.path.join(RACE_DAYS_DIR, f'{race_date}.json')
        save_json(race_day_file, race_day_data)
        print(f"  ✅ Saved race day data to: {os.path.basename(race_day_file)}")
        
        # Update index
        update_race_days_index(race_date, race_day_data, user_scores)
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving race day: {e}")
        return False

def update_race_days_index(race_date: str, race_day_data: Dict, user_scores: Dict):
    """Update the race days index with new completed day"""
    print("📚 Updating race days index...")
    
    try:
        # Load current index
        index_data = load_json(RACE_DAYS_INDEX_FILE, {
            "availableDates": [],
            "lastUpdated": "",
            "totalRaceDays": 0,
            "metadata": {
                "structureVersion": "2.0",
                "description": "Historical race day data index"
            }
        })
        
        # Find highest score and top user
        highest_score = 0
        top_user = "Unknown"
        total_users = len(user_scores)
        
        for user_data in user_scores.values():
            if user_data["dailyScore"] > highest_score:
                highest_score = user_data["dailyScore"]
                top_user = user_data["userName"]
        
        # Create new date entry
        date_entry = {
            "date": race_date,
            "status": "completed",
            "totalUsers": total_users,
            "totalRaces": race_day_data["totalRaces"],
            "completedRaces": race_day_data["completedRaces"],
            "highestScore": highest_score,
            "topUser": top_user,
            "completedAt": race_day_data["completedAt"]
        }
        
        # Remove existing entry for this date (if any)
        index_data["availableDates"] = [d for d in index_data["availableDates"] if d["date"] != race_date]
        
        # Add new entry and sort by date (newest first)
        index_data["availableDates"].append(date_entry)
        index_data["availableDates"].sort(key=lambda x: x["date"], reverse=True)
        
        # Update metadata
        index_data["totalRaceDays"] = len(index_data["availableDates"])
        index_data["lastUpdated"] = datetime.now().isoformat()
        
        # Save updated index
        save_json(RACE_DAYS_INDEX_FILE, index_data)
        print(f"  ✅ Updated index: {index_data['totalRaceDays']} total race days")
        
    except Exception as e:
        print(f"❌ Error updating index: {e}")

def update_user_statistics(user_scores: Dict) -> bool:
    """Update user total scores and statistics"""
    print("👥 Updating user statistics...")
    
    try:
        users = load_json(USERS_FILE, [])
        
        for user in users:
            user_id = user['id']
            if user_id in user_scores:
                score_data = user_scores[user_id]
                daily_score = score_data["dailyScore"]
                
                # Update total score
                old_total = user.get('totalScore', 0)
                user['totalScore'] = old_total + daily_score
                
                # Initialize or update statistics
                if 'statistics' not in user:
                    user['statistics'] = {
                        "raceDaysPlayed": 0,
                        "bestDayScore": 0,
                        "bestDayDate": "",
                        "averageScore": 0.0,
                        "winRate": 0.0
                    }
                
                stats = user['statistics']
                
                # Update race days played
                stats["raceDaysPlayed"] += 1
                
                # Update best day score
                if daily_score > stats["bestDayScore"]:
                    stats["bestDayScore"] = daily_score
                    stats["bestDayDate"] = datetime.now().strftime('%Y-%m-%d')
                
                # Calculate average score
                stats["averageScore"] = user['totalScore'] / stats["raceDaysPlayed"]
                
                # Update overall win rate (simplified - could be more sophisticated)
                stats["winRate"] = score_data["winRate"]
                
                print(f"  ✅ {user['name']}: +{daily_score} → Total: {user['totalScore']}")
        
        # Save updated users
        save_json(USERS_FILE, users)
        print(f"✅ Updated statistics for {len(users)} users")
        return True
        
    except Exception as e:
        print(f"❌ Error updating user statistics: {e}")
        return False

def clear_current_day_data():
    """Clear current day data for new race day"""
    print("🧹 Clearing current day data...")
    
    try:
        save_json(RACES_FILE, [])
        save_json(BETS_FILE, {})
        save_json(BANKERS_FILE, {})
        print("✅ Cleared current day data files")
        return True
    except Exception as e:
        print(f"❌ Error clearing data: {e}")
        return False

def complete_race_day() -> Dict:
    """
    Main function to complete current race day
    Returns summary of completed day
    """
    print("🏁 COMPLETING RACE DAY")
    print("=" * 50)
    
    race_date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        # Step 1: Calculate daily scores
        user_scores = calculate_daily_scores()
        
        # Step 2: Save completed race day
        if not save_completed_race_day(race_date, user_scores):
            raise Exception("Failed to save race day data")
        
        # Step 3: Update user statistics
        if not update_user_statistics(user_scores):
            raise Exception("Failed to update user statistics")
        
        # Step 4: Clear current day data
        if not clear_current_day_data():
            raise Exception("Failed to clear current day data")
        
        # Create summary
        total_users = len(user_scores)
        highest_score = max((score["dailyScore"] for score in user_scores.values()), default=0)
        top_user = next((score["userName"] for score in user_scores.values() if score["dailyScore"] == highest_score), "Unknown")
        
        summary = {
            "success": True,
            "raceDate": race_date,
            "totalUsers": total_users,
            "totalRaces": len(load_json(RACES_FILE, [])),
            "highestScore": highest_score,
            "topUser": top_user,
            "completedAt": datetime.now().isoformat(),
            "userScores": user_scores
        }
        
        print("🎉 RACE DAY COMPLETED SUCCESSFULLY!")
        print(f"   📅 Date: {race_date}")
        print(f"   👑 Top Score: {highest_score} ({top_user})")
        print(f"   👥 Users: {total_users}")
        print("=" * 50)
        
        return summary
        
    except Exception as e:
        print(f"❌ RACE DAY COMPLETION FAILED: {e}")
        return {
            "success": False,
            "error": str(e),
            "raceDate": race_date
        }

if __name__ == "__main__":
    # Test the complete race day functionality
    result = complete_race_day()
    
    if result["success"]:
        print(f"✅ Race day completion test successful!")
        print(f"Summary: {json.dumps(result, indent=2)}")
    else:
        print(f"❌ Race day completion test failed: {result.get('error')}")
    
    input("\\nPress Enter to continue...")
