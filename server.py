from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from utils.smspariaz_scraper import scrape_horses_from_smspariaz
from utils.mtc_scraper import scrape_mtc_next_race_day

app = Flask(__name__)
CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])

# Data file paths
DATA_DIR = 'data'
CURRENT_DIR = os.path.join(DATA_DIR, 'current')
RACE_DAYS_DIR = os.path.join(DATA_DIR, 'race_days')

# User data (global)
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

# Current day data (new structure)
RACES_FILE = os.path.join(CURRENT_DIR, 'races.json')
BETS_FILE = os.path.join(CURRENT_DIR, 'bets.json')
BANKERS_FILE = os.path.join(CURRENT_DIR, 'bankers.json')

# Race day management
RACE_DAYS_INDEX_FILE = os.path.join(RACE_DAYS_DIR, 'index.json')
CURRENT_RACE_DAY_FILE = os.path.join(DATA_DIR, 'current_race_day.json')

# Legacy file (for backward compatibility)
LEGACY_RACE_DAYS_FILE = os.path.join(DATA_DIR, 'race_days.json')

# Create data directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CURRENT_DIR, exist_ok=True)
os.makedirs(RACE_DAYS_DIR, exist_ok=True)

def load_json(filepath, default=None):
    """Load JSON data from file or return default if file doesn't exist"""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {filepath}. Returning default.")
            pass # Fall through to return default
    
    # Return appropriate default based on file type
    if 'users' in filepath or 'races' in filepath:
        return default if default is not None else []
    else:
        return default if default is not None else {}

def save_json(filepath, data):
    """Save data to JSON file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def init_default_data():
    """Initialize empty data files if they don't exist"""
    if not os.path.exists(USERS_FILE):
        save_json(USERS_FILE, [])
    
    if not os.path.exists(RACES_FILE):
        save_json(RACES_FILE, [])
    
    if not os.path.exists(BETS_FILE):
        save_json(BETS_FILE, {})
    
    if not os.path.exists(BANKERS_FILE):
        save_json(BANKERS_FILE, {})
    
    if not os.path.exists(RACE_DAYS_INDEX_FILE):
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
        save_json(RACE_DAYS_INDEX_FILE, index_data)
    
    if not os.path.exists(CURRENT_RACE_DAY_FILE):
        # Set today's date as the current race day
        today = datetime.now().strftime('%Y-%m-%d')
        save_json(CURRENT_RACE_DAY_FILE, {"current_race_day": today})

# Initialize default data on startup
init_default_data()

def get_current_race_day():
    """Get the current active race day"""
    current_data = load_json(CURRENT_RACE_DAY_FILE, {"current_race_day": datetime.now().strftime('%Y-%m-%d')})
    return current_data["current_race_day"]

def set_current_race_day(race_day):
    """Set the current active race day"""
    save_json(CURRENT_RACE_DAY_FILE, {"current_race_day": race_day})

def get_race_day_data(race_day):
    """Get all data for a specific race day"""
    race_days = load_json(LEGACY_RACE_DAYS_FILE, {})
    if race_day not in race_days:
        race_days[race_day] = {
            "date": race_day,
            "races": [],
            "bets": {},
            "bankers": {},
            "completed": False
        }
        save_json(LEGACY_RACE_DAYS_FILE, race_days)
    return race_days[race_day]

def save_race_day_data(race_day, data):
    """Save data for a specific race day"""
    race_days = load_json(LEGACY_RACE_DAYS_FILE, {})
    race_days[race_day] = data
    save_json(RACE_DAYS_FILE, race_days)

def sync_current_race_day_to_files():
    """Sync current race day data to the legacy files for backward compatibility"""
    current_race_day = get_current_race_day()
    race_day_data = get_race_day_data(current_race_day)
    
    # Update legacy files with current race day data
    save_json(RACES_FILE, race_day_data["races"])
    save_json(BETS_FILE, race_day_data["bets"])
    save_json(BANKERS_FILE, race_day_data["bankers"])

def sync_files_to_current_race_day():
    """Sync legacy files data to current race day storage"""
    current_race_day = get_current_race_day()
    race_day_data = get_race_day_data(current_race_day)
    
    # Update race day data with current legacy file contents
    race_day_data["races"] = load_json(RACES_FILE, [])
    race_day_data["bets"] = load_json(BETS_FILE, {})
    race_day_data["bankers"] = load_json(BANKERS_FILE, {})
    
    save_race_day_data(current_race_day, race_day_data)





@app.route('/api/users', methods=['GET'])
def get_users():
    users = load_json(USERS_FILE, [])
    return jsonify(users)

@app.route('/api/users', methods=['POST'])
def add_user():
    users = load_json(USERS_FILE, [])
    new_user_name = request.json.get('name')
    if not new_user_name:
        return jsonify({"error": "Name is required"}), 400
    
    # Generate a simple ID for the new user
    new_user_id = str(len(users) + 1)
    new_user = {"id": new_user_id, "name": new_user_name, "totalScore": 0}
    users.append(new_user)
    save_json(USERS_FILE, users)
    return jsonify(new_user), 201

@app.route('/api/races', methods=['GET'])
def get_races():
    races = load_json(RACES_FILE, [])
    return jsonify(races)

@app.route('/api/bets', methods=['GET'])
def get_bets():
    bets = load_json(BETS_FILE, {})
    return jsonify(bets)

@app.route('/api/bets', methods=['POST'])
def place_bet():
    bets = load_json(BETS_FILE, {})
    user_id = request.json.get('userId')
    race_id = request.json.get('raceId')
    horse_number = request.json.get('horseNumber')

    if not all([user_id, race_id, horse_number is not None]):
        return jsonify({"error": "Missing bet data"}), 400
    
    if user_id not in bets:
        bets[user_id] = {}
    
    bets[user_id][race_id] = horse_number
    save_json(BETS_FILE, bets)
    
    # Also sync to current race day
    sync_files_to_current_race_day()
    
    return jsonify({"success": True, "bets": bets}), 200

@app.route('/api/bankers', methods=['GET'])
def get_bankers():
    bankers = load_json(BANKERS_FILE, {})
    return jsonify(bankers)

@app.route('/api/bankers', methods=['POST'])
def set_banker():
    bankers = load_json(BANKERS_FILE, {})
    user_id = request.json.get('userId')
    race_id = request.json.get('raceId')  # Changed from horseNumber to raceId

    if not all([user_id, race_id is not None]):
        return jsonify({"error": "Missing banker data"}), 400
    
    bankers[user_id] = race_id  # Store race ID, not horse number
    save_json(BANKERS_FILE, bankers)
    
    # Also sync to current race day
    sync_files_to_current_race_day()
    
    return jsonify({"success": True, "bankers": bankers}), 200

@app.route('/api/races/scrape', methods=['POST'])
def scrape_races_endpoint():
    try:
        scraped_data = scrape_horses_from_smspariaz()
        save_json(RACES_FILE, scraped_data)
        
        # Also sync to current race day
        sync_files_to_current_race_day()
        
        return jsonify({"success": True, "races": scraped_data}), 200
    except Exception as e:
        print(f"Error in /api/races/scrape: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/races/scrape_mtc', methods=['POST'])
def scrape_mtc_endpoint():
    try:
        desired_month = None
        if request.is_json:
            desired_month = request.json.get('month')
        scraped_data = scrape_mtc_next_race_day(desired_month)
        if scraped_data:
            save_json(RACES_FILE, scraped_data)
            
            # Also sync to current race day
            sync_files_to_current_race_day()
            
            return jsonify({"success": True, "races": scraped_data}), 200
        else:
            return jsonify({"success": False, "error": "No races found"}), 200
    except Exception as e:
        print(f"Error in /api/races/scrape_mtc: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/races/results', methods=['POST'])
def scrape_results_endpoint():
    races = load_json(RACES_FILE, [])
    updated_results = {}
    
    # Simulate updating results for races that are past their time and don't have a winner
    now = datetime.now()
    for race in races:
        if not race.get('winner') and race.get('status') != 'completed':
            try:
                race_time_str = race['time']
                # Create a dummy date for comparison, only using time
                race_datetime_today = datetime.strptime(race_time_str, '%H:%M').replace(year=now.year, month=now.month, day=now.day)
                
                if now > race_datetime_today: # If race time has passed
                    if race['horses']:
                        # Assign a random horse as winner for simulation
                        import random
                        winner_horse = random.choice(race['horses'])
                        race['winner'] = winner_horse['number']
                        race['status'] = 'completed'
                        updated_results[race['id']] = race['winner']
            except ValueError:
                print(f"Could not parse race time: {race['time']}")
                continue # Skip to next race if time parsing fails
    
    save_json(RACES_FILE, races)
    
    # Also sync to current race day
    sync_files_to_current_race_day()
    
    return jsonify({"success": True, "results": updated_results}), 200

@app.route('/api/races/<race_id>/result', methods=['POST'])
def set_race_result_manual(race_id):
    races = load_json(RACES_FILE, [])
    winner_number = request.json.get('winner')

    if winner_number is None:
        return jsonify({"error": "Winner number is required"}), 400

    found = False
    for race in races:
        if race['id'] == race_id:
            race['winner'] = winner_number
            race['status'] = 'completed'
            found = True
            break
    
    if not found:
        return jsonify({"error": "Race not found"}), 404
    
    save_json(RACES_FILE, races)
    
    # Also sync to current race day
    sync_files_to_current_race_day()
    
    return jsonify({"success": True}), 200

@app.route('/api/race-day/complete', methods=['POST'])
def complete_race_day():
    """Enhanced race day completion with full historical data preservation"""
    try:
        print("🏁 COMPLETING RACE DAY")
        print("=" * 50)
        
        race_date = datetime.now().strftime('%Y-%m-%d')
        
        # Step 1: Calculate daily scores with enhanced details
        user_scores = calculate_daily_scores_enhanced()
        
        # Step 2: Save completed race day to individual file
        if not save_completed_race_day_enhanced(race_date, user_scores):
            raise Exception("Failed to save race day data")
        
        # Step 3: Update user statistics and total scores
        if not update_user_statistics_enhanced(user_scores):
            raise Exception("Failed to update user statistics")
        
        # Step 4: Clear current day data for new race day
        if not clear_current_day_data_enhanced():
            raise Exception("Failed to clear current day data")
        
        # Create response summary
        total_users = len(user_scores)
        highest_score = max((score["dailyScore"] for score in user_scores.values()), default=0)
        top_user = next((score["userName"] for score in user_scores.values() if score["dailyScore"] == highest_score), "Unknown")
        
        summary = {
            "success": True,
            "raceDate": race_date,
            "totalUsers": total_users,
            "highestScore": highest_score,
            "topUser": top_user,
            "completedAt": datetime.now().isoformat(),
            "message": f"Race day {race_date} completed successfully! Top score: {highest_score} ({top_user})"
        }
        
        print("🎉 RACE DAY COMPLETED SUCCESSFULLY!")
        print(f"   📅 Date: {race_date}")
        print(f"   👑 Top Score: {highest_score} ({top_user})")
        print(f"   👥 Users: {total_users}")
        print("=" * 50)
        
        return jsonify(summary), 200
        
    except Exception as e:
        error_msg = f"Race day completion failed: {str(e)}"
        print(f"❌ {error_msg}")
        return jsonify({
            "success": False,
            "error": error_msg,
            "raceDate": datetime.now().strftime('%Y-%m-%d')
        }), 500

# Enhanced Reset Helper Functions
def calculate_daily_scores_enhanced() -> Dict[str, Dict]:
    """Calculate all user scores for current race day with enhanced details"""
    print("🧮 Calculating daily scores...")
    
    users = load_json(USERS_FILE, [])
    current_races = load_json(RACES_FILE, [])
    current_bets = load_json(BETS_FILE, {})
    current_bankers = load_json(BANKERS_FILE, {})
    
    user_scores = {}
    
    for user in users:
        user_id = user['id']
        user_name = user['name']
        
        user_score_data = {
            "userId": user_id,
            "userName": user_name,
            "dailyScore": 0,
            "basePoints": 0,
            "bankerRaceId": current_bankers.get(user_id),
            "bankerWon": False,
            "bankerMultiplierApplied": False,
            "bets": [],
            "betsWon": 0,
            "totalBets": 0,
            "winRate": 0.0
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
                        if odds > 10: points = 3
                        elif odds > 5: points = 2
                        
                        bet_data["points"] = points
                        base_points += points
                
                user_score_data["bets"].append(bet_data)
        
        # Calculate win rate
        if user_score_data["totalBets"] > 0:
            user_score_data["winRate"] = user_score_data["betsWon"] / user_score_data["totalBets"]
        
        user_score_data["basePoints"] = base_points
        
        # Apply banker bonus
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
        user_scores[user_id] = user_score_data
        
        print(f"  ✅ {user_name}: {daily_score} points ({user_score_data['betsWon']}/{user_score_data['totalBets']} bets)")
    
    print(f"✅ Calculated scores for {len(user_scores)} users")
    return user_scores

def save_completed_race_day_enhanced(race_date: str, user_scores: Dict) -> bool:
    """Save completed race day to individual file and update index"""
    print(f"💾 Saving completed race day: {race_date}")
    
    try:
        current_races = load_json(RACES_FILE, [])
        
        race_day_data = {
            "date": race_date,
            "totalRaces": len(current_races),
            "completedRaces": len([r for r in current_races if r.get('winner')]),
            "status": "completed",
            "completedAt": datetime.now().isoformat(),
            "races": [],
            "userScores": list(user_scores.values())
        }
        
        # Add race details
        for race in current_races:
            race_data = {
                "id": race['id'],
                "name": race.get('name', f'Race {race["id"]}'),
                "time": race.get('time', ''),
                "winner": race.get('winner'),
                "totalHorses": len(race.get('horses', [])),
                "status": race.get('status', 'unknown')
            }
            
            # Add winning horse details
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
        
        # Save to individual race day file
        race_day_file = os.path.join(RACE_DAYS_DIR, f'{race_date}.json')
        save_json(race_day_file, race_day_data)
        print(f"  ✅ Saved race day data to: {os.path.basename(race_day_file)}")
        
        # Update index
        update_race_days_index_enhanced(race_date, race_day_data, user_scores)
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving race day: {e}")
        return False

def update_race_days_index_enhanced(race_date: str, race_day_data: Dict, user_scores: Dict):
    """Update the race days index with new completed day"""
    print("📚 Updating race days index...")
    
    try:
        index_data = load_json(RACE_DAYS_INDEX_FILE, {
            "availableDates": [],
            "lastUpdated": "",
            "totalRaceDays": 0,
            "metadata": {"structureVersion": "2.0", "description": "Historical race day data index"}
        })
        
        # Find highest score and top user
        highest_score = max((user_data["dailyScore"] for user_data in user_scores.values()), default=0)
        top_user = next((user_data["userName"] for user_data in user_scores.values() if user_data["dailyScore"] == highest_score), "Unknown")
        
        date_entry = {
            "date": race_date,
            "status": "completed",
            "totalUsers": len(user_scores),
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
        
        save_json(RACE_DAYS_INDEX_FILE, index_data)
        print(f"  ✅ Updated index: {index_data['totalRaceDays']} total race days")
        
    except Exception as e:
        print(f"❌ Error updating index: {e}")

def update_user_statistics_enhanced(user_scores: Dict) -> bool:
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
                stats["raceDaysPlayed"] += 1
                
                if daily_score > stats["bestDayScore"]:
                    stats["bestDayScore"] = daily_score
                    stats["bestDayDate"] = datetime.now().strftime('%Y-%m-%d')
                
                stats["averageScore"] = user['totalScore'] / stats["raceDaysPlayed"]
                stats["winRate"] = score_data["winRate"]
                
                print(f"  ✅ {user['name']}: +{daily_score} → Total: {user['totalScore']}")
        
        save_json(USERS_FILE, users)
        print(f"✅ Updated statistics for {len(users)} users")
        return True
        
    except Exception as e:
        print(f"❌ Error updating user statistics: {e}")
        return False

def clear_current_day_data_enhanced():
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

# Legacy reset endpoint (for backward compatibility)
@app.route('/api/reset', methods=['POST'])
def reset_data_legacy():
    """Legacy reset endpoint - use /api/race-day/complete instead"""
    return complete_race_day()

# Race Day Management Routes

@app.route('/api/race-days', methods=['GET'])
def get_race_days():
    """Get all race days"""
    race_days = load_json(LEGACY_RACE_DAYS_FILE, {})
    current_race_day = get_current_race_day()
    
    # Convert to list format for frontend
    race_days_list = []
    for date, data in race_days.items():
        race_days_list.append({
            "date": date,
            "completed": data.get("completed", False),
            "race_count": len(data.get("races", [])),
            "is_current": date == current_race_day
        })
    
    # Sort by date (newest first)
    race_days_list.sort(key=lambda x: x["date"], reverse=True)
    
    return jsonify({
        "race_days": race_days_list,
        "current_race_day": current_race_day
    })

@app.route('/api/race-days/current', methods=['GET'])
def get_current_race_day_endpoint():
    """Get current race day"""
    current_race_day = get_current_race_day()
    return jsonify({"current_race_day": current_race_day})

@app.route('/api/race-days/current', methods=['POST'])
def set_current_race_day_endpoint():
    """Set current race day"""
    race_day = request.json.get('race_day')
    if not race_day:
        return jsonify({"error": "Race day is required"}), 400
    
    # Sync current data to storage before switching
    sync_files_to_current_race_day()
    
    # Set new current race day
    set_current_race_day(race_day)
    
    # Sync new race day data to files
    sync_current_race_day_to_files()
    
    return jsonify({"success": True, "current_race_day": race_day})

@app.route('/api/race-days/<race_day>', methods=['GET'])
def get_race_day_data_endpoint(race_day):
    """Get data for a specific race day"""
    race_day_data = get_race_day_data(race_day)
    return jsonify(race_day_data)

@app.route('/api/race-days/<race_day>/complete', methods=['POST'])
def complete_legacy_race_day(race_day):
    """Mark a race day as completed and calculate final scores"""
    race_day_data = get_race_day_data(race_day)
    
    # Calculate scores for this race day
    users = load_json(USERS_FILE, [])
    races = race_day_data["races"]
    bets = race_day_data["bets"]
    bankers = race_day_data["bankers"]
    
    for user in users:
        user_id = user['id']
        daily_score = 0
        
        for race in races:
            if race.get('winner') and bets.get(user_id) and bets[user_id].get(race['id']):
                user_bet = bets[user_id][race['id']]
                if user_bet == race['winner']:
                    horse = next((h for h in race['horses'] if h['number'] == race['winner']), None)
                    if horse:
                        odds = horse['odds']
                        points = 1
                        if odds > 10: points = 3
                        elif odds > 5: points = 2
                        daily_score += points
        
        # Apply banker bonus
        if bankers.get(user_id):
            banker_race_id = str(bankers[user_id])
            if (bets.get(user_id) and 
                bets[user_id].get(banker_race_id) and
                bets[user_id][banker_race_id] == next((r for r in races if r['id'] == banker_race_id), {}).get('winner')):
                daily_score *= 2
        
        user['totalScore'] = user.get('totalScore', 0) + daily_score
    
    # Mark race day as completed
    race_day_data["completed"] = True
    race_day_data["final_scores"] = {user['id']: user['totalScore'] for user in users}
    
    # Save updates
    save_json(USERS_FILE, users)
    save_race_day_data(race_day, race_day_data)
    
    return jsonify({"success": True, "daily_scores": race_day_data.get("final_scores", {})})

@app.route('/api/race-days/create-dummy', methods=['POST'])
def create_dummy_race_days():
    """Create dummy race days for testing"""
    from datetime import timedelta
    
    base_date = datetime.now()
    dummy_days = []
    
    # Create 5 dummy race days
    for i in range(5):
        date = (base_date - timedelta(days=i)).strftime('%Y-%m-%d')
        
        # Create dummy races
        races = []
        for race_num in range(1, 4):  # 3 races per day
            horses = []
            for horse_num in range(1, 6):  # 5 horses per race
                horses.append({
                    "number": horse_num,
                    "name": f"Horse {horse_num} Day {i+1}",
                    "odds": round(2.0 + horse_num * 0.5 + i * 0.2, 1),
                    "points": (3 if (2.0 + horse_num * 0.5 + i * 0.2) > 10 else (2 if (2.0 + horse_num * 0.5 + i * 0.2) > 5 else 1))
                })
            
            races.append({
                "id": f"dummy_R{race_num}_{date.replace('-', '')}",
                "name": f"Dummy Race {race_num} - {date}",
                "time": f"{12 + race_num}:00",
                "horses": horses,
                "winner": 1 if i > 0 else None,  # Set winners for past days
                "status": "completed" if i > 0 else "upcoming"
            })
        
        # Create dummy bets and bankers
        users = load_json(USERS_FILE, [])
        dummy_bets = {}
        dummy_bankers = {}
        
        for user in users:
            user_id = user['id']
            dummy_bets[user_id] = {}
            for race in races:
                dummy_bets[user_id][race['id']] = (int(user_id) % 5) + 1  # Cycle through horse numbers
            
            # Set first race as banker
            if races:
                dummy_bankers[user_id] = races[0]['id']
        
        race_day_data = {
            "date": date,
            "races": races,
            "bets": dummy_bets,
            "bankers": dummy_bankers,
            "completed": i > 0  # Mark past days as completed
        }
        
        save_race_day_data(date, race_day_data)
        dummy_days.append(date)
    
    return jsonify({"success": True, "created_days": dummy_days})

# ================================================================================
# TASK 3: HISTORICAL DATA API ENDPOINTS
# ================================================================================

@app.route('/api/race-days/historical', methods=['GET'])
def get_historical_race_days():
    """Get available race days from index with enhanced information"""
    try:
        index_data = load_json(RACE_DAYS_INDEX_FILE, {
            "availableDates": [],
            "totalRaceDays": 0,
            "lastUpdated": ""
        })
        
        return jsonify({
            "success": True,
            "raceDays": index_data["availableDates"],
            "totalRaceDays": index_data["totalRaceDays"],
            "lastUpdated": index_data["lastUpdated"]
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to load historical race days: {str(e)}"
        }), 500

@app.route('/api/race-days/historical/<race_date>', methods=['GET'])
def get_specific_race_day(race_date):
    """Get complete data for a specific race day"""
    try:
        race_day_file = os.path.join(RACE_DAYS_DIR, f'{race_date}.json')
        
        if not os.path.exists(race_day_file):
            return jsonify({
                "success": False,
                "error": f"Race day {race_date} not found"
            }), 404
        
        race_day_data = load_json(race_day_file, {})
        
        return jsonify({
            "success": True,
            "raceDay": race_day_data
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to load race day {race_date}: {str(e)}"
        }), 500

@app.route('/api/users/<user_id>/history', methods=['GET'])
def get_user_history(user_id):
    """Get user's complete historical performance across all race days"""
    try:
        # Load race days index
        index_data = load_json(RACE_DAYS_INDEX_FILE, {"availableDates": []})
        
        user_history = {
            "userId": user_id,
            "totalRaceDays": 0,
            "totalScore": 0,
            "bestDayScore": 0,
            "bestDayDate": "",
            "averageScore": 0.0,
            "raceDays": []
        }
        
        # Get user info
        users = load_json(USERS_FILE, [])
        user = next((u for u in users if u['id'] == user_id), None)
        
        if not user:
            return jsonify({
                "success": False,
                "error": f"User {user_id} not found"
            }), 404
        
        user_history["userName"] = user["name"]
        user_history["totalScore"] = user.get("totalScore", 0)
        
        if "statistics" in user:
            stats = user["statistics"]
            user_history["totalRaceDays"] = stats.get("raceDaysPlayed", 0)
            user_history["bestDayScore"] = stats.get("bestDayScore", 0)
            user_history["bestDayDate"] = stats.get("bestDayDate", "")
            user_history["averageScore"] = stats.get("averageScore", 0.0)
        
        # Load performance for each race day
        for date_entry in index_data["availableDates"]:
            race_date = date_entry["date"]
            race_day_file = os.path.join(RACE_DAYS_DIR, f'{race_date}.json')
            
            if os.path.exists(race_day_file):
                race_day_data = load_json(race_day_file, {})
                
                # Find user's performance in this race day
                user_score_data = None
                for user_score in race_day_data.get("userScores", []):
                    if user_score["userId"] == user_id:
                        user_score_data = user_score
                        break
                
                if user_score_data:
                    day_performance = {
                        "date": race_date,
                        "dailyScore": user_score_data["dailyScore"],
                        "basePoints": user_score_data.get("basePoints", 0),
                        "bankerMultiplierApplied": user_score_data.get("bankerMultiplierApplied", False),
                        "betsWon": user_score_data.get("betsWon", 0),
                        "totalBets": user_score_data.get("totalBets", 0),
                        "winRate": user_score_data.get("winRate", 0.0),
                        "totalRaces": race_day_data.get("totalRaces", 0),
                        "topScore": date_entry.get("highestScore", 0),
                        "rank": "Unknown"  # Could calculate this
                    }
                    user_history["raceDays"].append(day_performance)
        
        # Sort by date (newest first)
        user_history["raceDays"].sort(key=lambda x: x["date"], reverse=True)
        
        return jsonify({
            "success": True,
            "userHistory": user_history
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to load user history: {str(e)}"
        }), 500

@app.route('/api/users/<user_id>/history/<race_date>', methods=['GET'])
def get_user_performance_on_date(user_id, race_date):
    """Get user's detailed performance on a specific race day"""
    try:
        race_day_file = os.path.join(RACE_DAYS_DIR, f'{race_date}.json')
        
        if not os.path.exists(race_day_file):
            return jsonify({
                "success": False,
                "error": f"Race day {race_date} not found"
            }), 404
        
        race_day_data = load_json(race_day_file, {})
        
        # Find user's performance
        user_performance = None
        for user_score in race_day_data.get("userScores", []):
            if user_score["userId"] == user_id:
                user_performance = user_score
                break
        
        if not user_performance:
            return jsonify({
                "success": False,
                "error": f"User {user_id} did not participate on {race_date}"
            }), 404
        
        # Enhance with race day context
        enhanced_performance = {
            "raceDate": race_date,
            "userPerformance": user_performance,
            "raceDay": {
                "totalRaces": race_day_data.get("totalRaces", 0),
                "completedRaces": race_day_data.get("completedRaces", 0),
                "highestScore": max((score["dailyScore"] for score in race_day_data.get("userScores", [])), default=0),
                "averageScore": sum(score["dailyScore"] for score in race_day_data.get("userScores", [])) / len(race_day_data.get("userScores", [1])),
            },
            "races": race_day_data.get("races", [])
        }
        
        return jsonify({
            "success": True,
            "performance": enhanced_performance
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to load user performance: {str(e)}"
        }), 500

@app.route('/api/leaderboard/enhanced', methods=['GET'])
def get_enhanced_leaderboard():
    """Get enhanced leaderboard with total scores and statistics"""
    try:
        users = load_json(USERS_FILE, [])
        
        # Sort users by total score (highest first)
        users_sorted = sorted(users, key=lambda x: x.get('totalScore', 0), reverse=True)
        
        enhanced_leaderboard = []
        for rank, user in enumerate(users_sorted, 1):
            user_data = {
                "rank": rank,
                "id": user["id"],
                "name": user["name"],
                "totalScore": user.get("totalScore", 0),
                "statistics": user.get("statistics", {
                    "raceDaysPlayed": 0,
                    "bestDayScore": 0,
                    "bestDayDate": "",
                    "averageScore": 0.0,
                    "winRate": 0.0
                })
            }
            enhanced_leaderboard.append(user_data)
        
        # Calculate leaderboard statistics
        total_users = len(enhanced_leaderboard)
        active_users = len([u for u in enhanced_leaderboard if u["statistics"]["raceDaysPlayed"] > 0])
        highest_score = enhanced_leaderboard[0]["totalScore"] if enhanced_leaderboard else 0
        
        return jsonify({
            "success": True,
            "leaderboard": enhanced_leaderboard,
            "summary": {
                "totalUsers": total_users,
                "activeUsers": active_users,
                "highestScore": highest_score,
                "generatedAt": datetime.now().isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to generate enhanced leaderboard: {str(e)}"
        }), 500

@app.route('/api/race-day/current/status', methods=['GET'])
def get_current_race_day_status():
    """Get current race day status and progress"""
    try:
        current_races = load_json(RACES_FILE, [])
        current_bets = load_json(BETS_FILE, {})
        current_bankers = load_json(BANKERS_FILE, {})
        
        # Calculate current day statistics
        total_races = len(current_races)
        completed_races = len([r for r in current_races if r.get('winner')])
        upcoming_races = total_races - completed_races
        
        # Count active users (users with bets)
        active_users = len(current_bets)
        total_bets = sum(len(user_bets) for user_bets in current_bets.values())
        banker_selections = len(current_bankers)
        
        # Find next race
        next_race = None
        now = datetime.now()
        for race in current_races:
            if not race.get('winner'):
                next_race = {
                    "id": race["id"],
                    "name": race.get("name", f"Race {race['id']}"),
                    "time": race.get("time", ""),
                    "totalHorses": len(race.get("horses", []))
                }
                break
        
        status = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "time": datetime.now().strftime('%H:%M:%S'),
            "races": {
                "total": total_races,
                "completed": completed_races,
                "upcoming": upcoming_races,
                "progress": (completed_races / total_races * 100) if total_races > 0 else 0
            },
            "betting": {
                "activeUsers": active_users,
                "totalBets": total_bets,
                "bankerSelections": banker_selections
            },
            "nextRace": next_race,
            "isComplete": completed_races == total_races and total_races > 0
        }
        
        return jsonify({
            "success": True,
            "status": status
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get current race day status: {str(e)}"
        }), 500

if __name__ == '__main__':
    # Ensure the data directory exists before running the app
    os.makedirs(DATA_DIR, exist_ok=True)
    init_default_data() # Initialize data files on server start
    
    # Get port from environment variable (for Render deployment) or use 5000 for local
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

