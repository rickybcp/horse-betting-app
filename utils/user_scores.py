"""
User Score Management System
Handles all user score calculations based on race day JSON files
Uses cloud storage for data persistence
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# Handle both relative and absolute imports
try:
    from .cloud_storage import get_storage_manager
except ImportError:
    from cloud_storage import get_storage_manager


def load_json_file(filepath: str, default=None):
    """Load JSON data from cloud storage with error handling"""
    try:
        storage_manager = get_storage_manager()
        return storage_manager.load_file(filepath, default)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return default


def save_json_file(filepath: str, data: Any) -> bool:
    """Save data to cloud storage with error handling"""
    try:
        storage_manager = get_storage_manager()
        return storage_manager.save_file(filepath, data)
    except Exception as e:
        print(f"Error saving {filepath}: {e}")
        return False


def calculate_points_from_odds(odds: float) -> int:
    """Calculate points based on horse odds"""
    if odds > 10:
        return 3
    elif odds > 5:
        return 2
    else:
        return 1


def calculate_user_score_for_race_day(race_date: str, user_id: str) -> int:
    """
    Calculate a user's score for a specific race day
    Returns just the daily score (integer)
    """
    # Load race day data
    race_day_file = f"data/all_races/{race_date}.json"
    race_day_data = load_json_file(race_day_file, {})
    
    if not race_day_data or not race_day_data.get('races'):
        return 0
    
    races = race_day_data.get('races', [])
    bets = race_day_data.get('bets', {})
    bankers = race_day_data.get('bankers', {})
    
    user_bets = bets.get(user_id, {})
    user_banker = bankers.get(user_id)
    
    # Calculate base score
    base_points = 0
    
    for race in races:
        # Handle different ID formats
        race_id = None
        if 'id' in race:
            race_id = str(race['id'])
        elif 'raceId' in race:
            race_id = str(race['raceId'])
        else:
            # Skip races without ID
            continue
        
        # Check if user has bet on this race and won
        if race_id in user_bets and race.get('winner'):
            user_bet = user_bets[race_id]
            
            if user_bet == race['winner']:
                # Find the winning horse to get odds
                winning_horse = None
                for horse in race.get('horses', []):
                    if horse['number'] == race['winner']:
                        winning_horse = horse
                        break
                
                if winning_horse:
                    points = calculate_points_from_odds(winning_horse['odds'])
                    base_points += points
    
    # Apply banker bonus (double points if banker race was won)
    daily_score = base_points
    if user_banker:
        banker_race_id = str(user_banker)
        # Check if user won their banker race
        if banker_race_id in user_bets:
            for race in races:
                race_id = str(race.get('id', race.get('raceId', '')))
                if (race_id == banker_race_id and 
                    race.get('winner') == user_bets[banker_race_id]):
                    daily_score = base_points * 2
                    break
    
    return daily_score


def get_all_race_dates() -> List[str]:
    """Get all available race dates from cloud storage"""
    race_dates = []
    
    try:
        storage_manager = get_storage_manager()
        # List all files in the all_races directory
        files = storage_manager.list_files("data/all_races/")
        
        for filepath in files:
            filename = os.path.basename(filepath)
            if filename.endswith('.json') and filename != 'index.json':
                # Extract date from filename (e.g., "2025-08-30.json" -> "2025-08-30")
                race_date = filename.replace('.json', '')
                race_dates.append(race_date)
    except Exception as e:
        print(f"Error getting race dates: {e}")
        return []
    
    # Sort dates in descending order (newest first)
    race_dates.sort(reverse=True)
    return race_dates


def calculate_all_user_scores(user_id: str) -> Dict[str, Any]:
    """
    Calculate scores for a user across all race days
    Returns simplified scoring data with dailyScores as {date: score}
    """
    race_dates = get_all_race_dates()
    daily_scores = {}
    total_score = 0
    
    for race_date in race_dates:
        daily_score = calculate_user_score_for_race_day(race_date, user_id)
        daily_scores[race_date] = daily_score
        total_score += daily_score
    
    return {
        "userId": user_id,
        "totalScore": total_score,
        "dailyScores": daily_scores
    }


def update_user_scores(race_date: Optional[str] = None) -> bool:
    """
    Update user scores in users.json
    If race_date is provided, only update scores for that date
    If race_date is None, recalculate all scores
    """
    print(f"[SCORES] Updating user scores{f' for {race_date}' if race_date else ' (all race days)'}")
    
    # Load users
    users_file = "data/users.json"
    users = load_json_file(users_file, [])
    
    if not users:
        print("[ERROR] No users found")
        return False
    
    updated_users = []
    
    for user in users:
        user_id = user['id']
        user_name = user['name']
        
        if race_date:
            # Update only specific race date
            current_daily_scores = user.get('dailyScores', {})
            daily_score = calculate_user_score_for_race_day(race_date, user_id)
            current_daily_scores[race_date] = daily_score
            
            # Recalculate total score
            total_score = sum(current_daily_scores.values())
            
            updated_user = {
                "id": user_id,
                "name": user_name,
                "totalScore": total_score,
                "dailyScores": current_daily_scores
            }
        else:
            # Recalculate all scores
            all_scores = calculate_all_user_scores(user_id)
            updated_user = {
                "id": user_id,
                "name": user_name,
                "totalScore": all_scores["totalScore"],
                "dailyScores": all_scores["dailyScores"]
            }
        
        updated_users.append(updated_user)
        print(f"  [OK] {user_name}: {updated_user['totalScore']} total points")
    
    # Save updated users
    if save_json_file(users_file, updated_users):
        print(f"[OK] Successfully updated scores for {len(updated_users)} users")
        return True
    else:
        print("[ERROR] Failed to save updated user scores")
        return False


def get_leaderboard_data(race_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Get leaderboard data for display
    If race_date is provided, returns daily leaderboard for that date
    If race_date is None, returns total score leaderboard
    """
    users_file = "data/users.json"
    users = load_json_file(users_file, [])
    
    if not users:
        return {"users": [], "type": "total" if race_date is None else "daily", "date": race_date}
    
    leaderboard_users = []
    
    for user in users:
        if race_date:
            # Daily leaderboard
            score = user.get('dailyScores', {}).get(race_date, 0)
            leaderboard_users.append({
                "id": user['id'],
                "name": user['name'],
                "score": score
            })
        else:
            # Total score leaderboard
            leaderboard_users.append({
                "id": user['id'],
                "name": user['name'],
                "score": user.get('totalScore', 0),
                "dailyScores": user.get('dailyScores', {})
            })
    
    # Sort by score (highest first)
    leaderboard_users.sort(key=lambda x: x['score'], reverse=True)
    
    # Add rankings
    for i, user in enumerate(leaderboard_users):
        user['rank'] = i + 1
    
    return {
        "users": leaderboard_users,
        "type": "total" if race_date is None else "daily",
        "date": race_date,
        "totalUsers": len(leaderboard_users),
        "activeUsers": len([u for u in leaderboard_users if u['score'] > 0])
    }


def get_current_race_day_scores() -> Dict[str, Any]:
    """
    Get scores for the current race day (today)
    This provides real-time scoring without updating the users.json
    """
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Load users to get the list
    users_file = "data/users.json"
    users = load_json_file(users_file, [])
    
    if not users:
        return {"users": [], "date": today}
    
    current_scores = []
    
    for user in users:
        user_id = user['id']
        daily_score = calculate_user_score_for_race_day(today, user_id)
        current_scores.append({
            "id": user_id,
            "name": user['name'],
            "score": daily_score
        })
    
    # Sort by score
    current_scores.sort(key=lambda x: x['score'], reverse=True)
    
    # Add rankings
    for i, user in enumerate(current_scores):
        user['rank'] = i + 1
    
    return {
        "users": current_scores,
        "date": today,
        "type": "current"
    }


if __name__ == "__main__":
    # Test the user score system
    print("[TEST] Testing User Score System")
    print("=" * 50)
    
    # Test current race day scores
    current_scores = get_current_race_day_scores()
    print(f"\n[DATE] Current Race Day Scores ({current_scores['date']}):")
    for user in current_scores['users'][:5]:  # Top 5
        print(f"  {user['rank']}. {user['name']}: {user['score']} points")
    
    # Test total leaderboard
    total_leaderboard = get_leaderboard_data()
    print(f"\n[LEADERBOARD] Total Score Leaderboard:")
    for user in total_leaderboard['users'][:5]:  # Top 5
        print(f"  {user['rank']}. {user['name']}: {user['score']} points")
    
    print("\n" + "=" * 50)
    print("[OK] User Score System Test Complete")
