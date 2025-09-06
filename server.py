from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from utils.smspariaz_scraper import scrape_horses_from_smspariaz

from utils.results_scraper import scrape_results_with_fallback
from utils.cloud_storage import get_storage_manager, init_cloud_storage
from utils.user_scores import update_user_scores, get_leaderboard_data, get_current_race_day_scores

app = Flask(__name__)
# Ensure stdout/stderr use UTF-8 to avoid encoding errors on Windows consoles
try:
    import sys
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])

# Data file paths
DATA_DIR = 'data'
ALL_RACES_DIR = os.path.join(DATA_DIR, 'all_races')  # new canonical store

# User data (global)
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

# Current day data (new structure - these are now handled by all_races system)
# RACES_FILE, BETS_FILE, BANKERS_FILE are no longer used as separate files
# All data is now stored in the all_races system

# Race day management
ALL_RACES_INDEX_FILE = os.path.join(ALL_RACES_DIR, 'index.json')  # new canonical store

# Legacy file (for backward compatibility) - DEPRECATED
# LEGACY_RACE_DAYS_FILE = os.path.join(DATA_DIR, 'race_days.json')

# Initialize cloud storage - REQUIRED for unified data access
init_cloud_storage()
storage_manager = get_storage_manager()

if storage_manager.use_cloud:
    print("Cloud storage initialized successfully")
    print(f"   Bucket: {os.getenv('GCS_BUCKET_NAME')}")
    print(f"   Project: {os.getenv('GOOGLE_CLOUD_PROJECT')}")
else:
    print("Cloud storage initialization failed!")
    print("   This application requires Google Cloud Storage for data consistency.")
    print("   Please configure your environment variables:")
    print("   - GCS_BUCKET_NAME")
    print("   - GOOGLE_CLOUD_PROJECT") 
    print("   - GOOGLE_APPLICATION_CREDENTIALS or GOOGLE_APPLICATION_CREDENTIALS_JSON")
    print("   Run: python setup_cloud_storage.py for setup instructions")
    # Don't exit in production, but warn heavily
    if os.getenv('FLASK_ENV') != 'production':
        print("   Exiting - cloud storage required for development")
        exit(1)
    print("   Continuing with local storage fallback in production")

# Create data directories if they don't exist (for local fallback)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ALL_RACES_DIR, exist_ok=True)

def load_json(filepath, default=None):
    """Load JSON data from file using cloud storage or local fallback"""
    storage_manager = get_storage_manager()
    return storage_manager.load_file(filepath, default)

def save_json(filepath, data):
    """Save data to JSON file using cloud storage or local fallback"""
    storage_manager = get_storage_manager()
    return storage_manager.save_file(filepath, data)

def init_default_data():
    """Initialize empty data files if they don't exist"""
    storage_manager = get_storage_manager()
    
    # Initialize users if not exists
    if not storage_manager.file_exists(USERS_FILE):
        save_json(USERS_FILE, [])
    
    # Initialize new all_races index if not exists
    if not storage_manager.file_exists(ALL_RACES_INDEX_FILE):
        index_data = {
            "raceDays": []
        }
        save_json(ALL_RACES_INDEX_FILE, index_data)

# Initialize default data on startup
init_default_data()

def get_current_race_day():
    """Get the current active race day from all_races index; fallback to latest."""
    index_data = load_json(ALL_RACES_INDEX_FILE, {"raceDays": []})
    current_day = next((day["date"] for day in index_data.get("raceDays", []) if day.get("current")), None)
    if current_day:
        return current_day
    # Fallback to latest date if no current day set
    dates = [day.get("date") for day in index_data.get("raceDays", []) if day.get("date")]
    return dates[0] if dates else datetime.now().strftime('%Y-%m-%d')

def set_current_race_day(race_day):
    """Persist the current active race day to all_races index."""
    try:
        print(f"[DEBUG] Setting current race day to: {race_day}")
        index_data = load_json(ALL_RACES_INDEX_FILE, {"raceDays": []})
        print(f"[DEBUG] Loaded index data: {len(index_data.get('raceDays', []))} race days")
        
        # Update all race days to set current=False
        for day in index_data.get("raceDays", []):
            day["current"] = False
        
        # Set the specified race day as current
        current_day = next((day for day in index_data.get("raceDays", []) if day.get("date") == race_day), None)
        if current_day:
            current_day["current"] = True
            print(f"[DEBUG] Updated existing race day: {race_day}")
        else:
            # Add new race day if it doesn't exist
            new_day = {
                "id": race_day,
                "date": race_day,
                "current": True
            }
            index_data.setdefault("raceDays", []).append(new_day)
            print(f"[DEBUG] Added new race day: {race_day}")
        
        # Save the updated index
        success = save_json(ALL_RACES_INDEX_FILE, index_data)
        print(f"[DEBUG] Save index result: {success}")
        
        if success:
            print(f"[SUCCESS] Current race day set to: {race_day}")
        else:
            print(f"[ERROR] Failed to save index file for race day: {race_day}")
            
    except Exception as e:
        print(f"[ERROR] Exception in set_current_race_day: {e}")
        raise

def get_race_day_data(race_day):
    """Get all data for a specific race day from all_races."""
    storage_manager = get_storage_manager()
    primary = os.path.join(ALL_RACES_DIR, f"{race_day}.json")
    if storage_manager.file_exists(primary):
        return load_json(primary, {})
    return {
        "date": race_day,
        "status": "in_progress",
        "races": [],
        "bets": {},
        "bankers": {},
        "userScores": []
    }

def save_race_day_data(race_day, data):
    """Save data for a specific race day to all_races directory."""
    race_day_file = os.path.join(ALL_RACES_DIR, f"{race_day}.json")
    save_json(race_day_file, data)

def load_current_day_data() -> Dict:
    """Load the current race day data from all_races."""
    current_day = get_current_race_day()
    return get_race_day_data(current_day)

def save_current_day_data(data: Dict) -> None:
    """Persist the current race day data to all_races and ensure index entry exists."""
    current_day = get_current_race_day()
    save_race_day_data(current_day, data)
    # Ensure index entry exists
    index_data = load_json(ALL_RACES_INDEX_FILE, {"raceDays": []})
    if not any(d.get("date") == current_day for d in index_data.get("raceDays", [])):
        index_data.setdefault("raceDays", []).append({
            "id": current_day,
            "date": current_day,
            "current": True
        })
        # Set all other days to current=False
        for day in index_data["raceDays"]:
            if day["date"] != current_day:
                day["current"] = False
    save_json(ALL_RACES_INDEX_FILE, index_data)

def sync_current_race_day_to_files():
    """Deprecated: no-op (we work directly from all_races)."""
    return

def sync_files_to_current_race_day():
    """Deprecated: no-op (we work directly from all_races)."""
    return





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
    new_user = {"id": new_user_id, "name": new_user_name}
    users.append(new_user)
    save_json(USERS_FILE, users)
    return jsonify(new_user), 201

@app.route('/api/races', methods=['GET'])
def get_races():
    current = load_current_day_data()
    races = current.get("races", [])
    return jsonify(races)

@app.route('/api/bets', methods=['GET'])
def get_bets():
    current = load_current_day_data()
    bets = current.get("bets", {})
    return jsonify(bets)

@app.route('/api/bets', methods=['POST'])
def place_bet():
    current = load_current_day_data()
    bets = current.get("bets", {})
    user_id = request.json.get('userId')
    race_id = request.json.get('raceId')
    horse_number = request.json.get('horseNumber')

    if not all([user_id, race_id, horse_number is not None]):
        return jsonify({"error": "Missing bet data"}), 400
    
    if user_id not in bets:
        bets[user_id] = {}
    
    bets[user_id][race_id] = horse_number
    current["bets"] = bets
    save_current_day_data(current)
    
    # Recalculate and update current user scores
    update_current_user_scores()
    
    return jsonify({"success": True, "bets": bets}), 200

@app.route('/api/bankers', methods=['GET'])
def get_bankers():
    current = load_current_day_data()
    bankers = current.get("bankers", {})
    return jsonify(bankers)

@app.route('/api/bankers', methods=['POST'])
def set_banker():
    current = load_current_day_data()
    bankers = current.get("bankers", {})
    user_id = request.json.get('userId')
    race_id = request.json.get('raceId')  # Changed from horseNumber to raceId

    if not all([user_id, race_id is not None]):
        return jsonify({"error": "Missing banker data"}), 400
    
    bankers[user_id] = race_id  # Store race ID, not horse number
    current["bankers"] = bankers
    save_current_day_data(current)
    
    # Recalculate and update current user scores
    update_current_user_scores()
    
    return jsonify({"success": True, "bankers": bankers}), 200

@app.route('/api/races/scrape', methods=['POST'])
def scrape_races_endpoint():
    try:
        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"[SCRAPE] Creating new race day for: {today}")
        
        # Scrape the race data
        scraped_data = scrape_horses_from_smspariaz()
        
        # Create fresh data structure for today
        today_data = {
            "date": today,
            "status": scraped_data.get("status", "in_progress"),
            "races": scraped_data["races"],
            "bets": {},  # Start with empty bets for new race day
            "bankers": {}  # Start with empty bankers for new race day
        }
        
        # Save directly to today's file (no "current" concept needed)
        save_race_day_data(today, today_data)
        print(f"[SUCCESS] Saved race data for {today}")
        
        # Update the index to mark today as current (for backward compatibility)
        set_current_race_day(today)
        
        return jsonify({"success": True, "races": scraped_data["races"], "date": today}), 200
    except Exception as e:
        print(f"Error in /api/races/scrape: {e}")
        return jsonify({"success": False, "error": str(e)}), 500



@app.route('/api/races/results', methods=['POST'])
def scrape_results_endpoint():
    """Scrape actual race results from SMS Pariaz website"""
    try:
        print("[SCRAPE] Starting results scraping...")
        
        # Use the new results scraper
        scraped_results = scrape_results_with_fallback()
        
        if scraped_results:
            # Update races with scraped results
            current = load_current_day_data()
            races = current.get("races", [])
            updated_results = {}
            
            for race in races:
                # Try to match scraped results with current races by race ID
                race_id = race['id']
                if race_id in scraped_results and not race.get('winner'):
                    result_data = scraped_results[race_id]
                    if 'winner_number' in result_data:
                        race['winner'] = result_data['winner_number']
                        race['status'] = 'completed'
                        updated_results[race_id] = result_data['winner_number']
                        print(f"[WINNER] Updated race {race_id} with winner: horse #{result_data['winner_number']}")
            
            if updated_results:
                current["races"] = races
                save_current_day_data(current)
                
                # Recalculate and update current user scores after race results change
                update_current_user_scores()
                
                print(f"[OK] Successfully updated {len(updated_results)} races with results")
                return jsonify({"success": True, "results": updated_results}), 200
            else:
                print("[WARN] No races were updated with scraped results")
                return jsonify({"success": True, "results": {}, "message": "No races updated"}), 200
        else:
            print("[WARN] No results were scraped")
            return jsonify({"success": False, "error": "No results found to scrape"}), 200
            
    except Exception as e:
        print(f"[ERROR] Error in results scraping: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/races/<race_id>/result', methods=['POST'])
def set_race_result_manual(race_id):
    """Manually set the winner for a specific race"""
    try:
        # Convert race_id to integer for comparison
        try:
            race_id = int(race_id)
        except ValueError:
            return jsonify({"error": "Invalid race ID format"}), 400
            
        current = load_current_day_data()
        races = current.get("races", [])
        winner_number = request.json.get('winner')

        if winner_number is None:
            return jsonify({"error": "Winner number is required"}), 400

        found = False
        for race in races:
            if race['id'] == race_id:
                race['winner'] = winner_number
                race['status'] = 'completed'
                found = True
                print(f"[WINNER] Manually set race {race_id} winner to horse #{winner_number}")
                break
        
        if not found:
            return jsonify({"error": "Race not found"}), 404
        
        # Save updated races
        current["races"] = races
        save_current_day_data(current)
        
        # Recalculate and update current user scores after race result change
        update_current_user_scores()
        
        print(f"[OK] Race result updated and synced to current race day")
        return jsonify({"success": True, "message": f"Race {race_id} winner set to horse #{winner_number}"}), 200
        
    except Exception as e:
        print(f"[ERROR] Error setting race result: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/race-day/complete', methods=['POST'])
def complete_race_day():
    """Enhanced race day completion with full historical data preservation"""
    try:
        print("[COMPLETE] COMPLETING RACE DAY")
        print("=" * 50)
        
        race_date = datetime.now().strftime('%Y-%m-%d')
        
        # Step 1: Calculate daily scores with enhanced details
        user_scores = calculate_daily_scores_enhanced()
        
        # Step 2: Save completed race day to individual file
        if not save_completed_race_day_enhanced(race_date, user_scores):
            raise Exception("Failed to save race day data")
        
        # Step 3: Update user total scores
        if not update_user_statistics_enhanced(user_scores):
            raise Exception("Failed to update user total scores")
        
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
        
        print("[DONE] RACE DAY COMPLETED SUCCESSFULLY!")
        print(f"   [DATE] Date: {race_date}")
        print(f"   [TOP] Top Score: {highest_score} ({top_user})")
        print(f"   [USERS] Users: {total_users}")
        print("=" * 50)
        
        return jsonify(summary), 200
        
    except Exception as e:
        error_msg = f"Race day completion failed: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return jsonify({
            "success": False,
            "error": error_msg,
            "raceDate": datetime.now().strftime('%Y-%m-%d')
        }), 500

# Enhanced Reset Helper Functions

def calculate_current_user_scores() -> List[Dict]:
    """Calculate current user scores for the current race day (real-time)"""
    print("[SCORES] Calculating current user scores...")
    
    users = load_json(USERS_FILE, [])
    current = load_current_day_data()
    current_races = current.get("races", [])
    current_bets = current.get("bets", {})
    current_bankers = current.get("bankers", {})
    
    user_scores = []

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
        user_scores.append(user_score_data)
        
        print(f"  ✅ {user_name}: {daily_score} points ({user_score_data['betsWon']}/{user_score_data['totalBets']} bets)")
    
    print(f"[OK] Calculated current scores for {len(user_scores)} users")
    return user_scores

def update_current_user_scores():
    """Update the current race day with recalculated user scores"""
    try:
        current_scores = calculate_current_user_scores()
        current = load_current_day_data()
        current["userScores"] = current_scores
        save_current_day_data(current)
        print("[OK] Updated current race day with recalculated user scores")
        return True
    except Exception as e:
        print(f"[ERROR] Error updating current user scores: {e}")
        return False

def calculate_daily_scores_enhanced() -> Dict[str, Dict]:
    """Calculate all user scores for current race day with enhanced details"""
    print("[SCORES] Calculating daily scores...")
    
    users = load_json(USERS_FILE, [])
    current = load_current_day_data()
    current_races = current.get("races", [])
    current_bets = current.get("bets", {})
    current_bankers = current.get("bankers", {})
    
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
        
        print(f"  [OK] {user_name}: {daily_score} points ({user_score_data['betsWon']}/{user_score_data['totalBets']} bets)")
    
    print(f"[OK] Calculated scores for {len(user_scores)} users")
    return user_scores

def save_completed_race_day_enhanced(race_date: str, user_scores: Dict) -> bool:
    """Save completed race day to individual file and update index"""
    print(f"[SAVE] Saving completed race day: {race_date}")
    
    try:
        current = load_current_day_data()
        current_races = current.get("races", [])
        
        race_day_data = {
            "date": race_date,
            "status": "past",
            "races": [],
            "bets": current.get("bets", {}),
            "bankers": current.get("bankers", {}),
            "userScores": list(user_scores.values())
        }
        
        # Add race details
        for race in current_races:
            race_data = {
                "id": race['id'],
                "name": race.get('name', f'Race {race["id"]}'),
                "time": race.get('time', ''),
                "winner": race.get('winner'),
                "status": race.get('status', 'unknown'),
                "horses": race.get('horses', [])
            }
            
            race_day_data["races"].append(race_data)
        
        # Save to individual race day file
        race_day_file = os.path.join(ALL_RACES_DIR, f'{race_date}.json')
        save_json(race_day_file, race_day_data)
        print(f"  [OK] Saved race day data to: {os.path.basename(race_day_file)}")
        
        # Update index
        update_race_days_index_enhanced(race_date, race_day_data, user_scores)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error saving race day: {e}")
        return False

def update_race_days_index_enhanced(race_date: str, race_day_data: Dict, user_scores: Dict):
    """Update the race days index with new completed day"""
    print("[INDEX] Updating race days index...")
    
    try:
        index_data = load_json(ALL_RACES_INDEX_FILE, {"raceDays": []})
        
        # Create new race day entry
        date_entry = {
            "id": race_date,
            "date": race_date,
            "current": False  # This is now a past race day
        }
        
        # Remove existing entry for this date (if any)
        index_data["raceDays"] = [d for d in index_data["raceDays"] if d["date"] != race_date]
        
        # Add new entry and sort by date (newest first)
        index_data["raceDays"].append(date_entry)
        index_data["raceDays"].sort(key=lambda x: x["date"], reverse=True)
        
        save_json(ALL_RACES_INDEX_FILE, index_data)
        print(f"  [OK] Updated index: {len(index_data['raceDays'])} total race days")
        
    except Exception as e:
        print(f"[ERROR] Error updating index: {e}")

def update_user_statistics_enhanced(user_scores: Dict) -> bool:
    """Update user total scores only"""
    print("[USERS] Updating user total scores...")
    
    try:
        users = load_json(USERS_FILE, [])
        
        for user in users:
            user_id = user['id']
            if user_id in user_scores:
                score_data = user_scores[user_id]
                daily_score = score_data["dailyScore"]
                
                # Update total score only
                old_total = user.get('totalScore', 0)
                user['totalScore'] = old_total + daily_score
                
                print(f"  [OK] {user['name']}: +{daily_score} -> Total: {user['totalScore']}")
        
        save_json(USERS_FILE, users)
        print(f"[OK] Updated total scores for {len(users)} users")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error updating user total scores: {e}")
        return False

def clear_current_day_data_enhanced():
    """Clear current day data for new race day"""
    print("[CLEAN] Clearing current day data...")
    
    try:
        # This function is no longer needed in the new system
        # Data is managed through the all_races system
        print("[OK] Current day data clearing not needed in new system")
        return True
    except Exception as e:
        print(f"[ERROR] Error clearing data: {e}")
        return False

# Legacy reset endpoint (for backward compatibility)
@app.route('/api/reset', methods=['POST'])
def reset_data_legacy():
    """Legacy reset endpoint - use /api/race-day/complete instead"""
    return complete_race_day()

# Race Day Management Routes

@app.route('/api/race-days', methods=['GET'])
def get_race_days():
    """Get all race days from the new simplified system"""
    # Load from the new index file (all_races)
    index_data = load_json(ALL_RACES_INDEX_FILE, {"raceDays": []})
    
    # Convert to simplified format
    race_days_list = []
    for race_day_entry in index_data.get("raceDays", []):
        race_days_list.append({
            "date": race_day_entry["date"],
            "status": "current" if race_day_entry.get("current") else "past",
            "current": race_day_entry.get("current", False)
        })
    
    # Sort by date (newest first)
    race_days_list.sort(key=lambda x: x["date"], reverse=True)
    
    return jsonify({
        "raceDays": race_days_list,
        "total": len(race_days_list)
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
    
    # Set new current race day
    set_current_race_day(race_day)
    
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
        race_day_data["status"] = "past"
    
    # Save updates
    save_json(USERS_FILE, users)
    save_race_day_data(race_day, race_day_data)
    
    return jsonify({"success": True, "daily_scores": race_day_data.get("final_scores", {})})

# Removed test endpoint: /api/race-days/create-dummy

# ================================================================================
# TASK 3: HISTORICAL DATA API ENDPOINTS
# ================================================================================

@app.route('/api/race-days/historical', methods=['GET'])
def get_historical_race_days():
    """Get available race days from index with simplified information"""
    try:
        index_data = load_json(ALL_RACES_INDEX_FILE, {"raceDays": []})
        
        # Filter to only show past (non-current) race days
        past_race_days = [
            {
                "date": day["date"],
                "status": "past"
            }
            for day in index_data.get("raceDays", [])
            if not day.get("current", False)
        ]
        
        return jsonify({
            "success": True,
            "raceDays": past_race_days,
            "total": len(past_race_days)
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
        race_day_file = os.path.join(ALL_RACES_DIR, f'{race_date}.json')
        if not load_json(race_day_file, {}).get("date"):
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
        index_data = load_json(ALL_RACES_INDEX_FILE, {"raceDays": []})
        
        user_history = {
            "userId": user_id,
            "totalScore": 0,
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
        # Calculate total score from race day data
        total_score = 0
        for day_performance in user_history["raceDays"]:
            total_score += day_performance["dailyScore"]
        user_history["totalScore"] = total_score
        
        # Load performance for each race day
        for date_entry in index_data["raceDays"]:
            race_date = date_entry["date"]
            race_day_file = os.path.join(ALL_RACES_DIR, f'{race_date}.json')
            
            if load_json(race_day_file, {}).get("date"): # Check if file exists
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
                        "dailyScore": user_score_data["dailyScore"]
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
        race_day_data = get_race_day_data(race_date)
        
        if not race_day_data.get("date"): # Check if file exists
            return jsonify({
                "success": False,
                "error": f"Race day {race_date} not found"
            }), 404
        
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
        
        # Load race days index to get all available dates
        index_data = load_json(ALL_RACES_INDEX_FILE, {"raceDays": []})
        available_dates = [day["date"] for day in index_data.get("raceDays", [])]
        
        # Calculate total scores for each user from all completed race days
        user_total_scores = {}
        
        for user in users:
            user_id = user['id']
            user_total_scores[user_id] = 0
        
        # Sum up scores from all completed race days and update userScores
        for race_date in available_dates:
            try:
                race_day_data = get_race_day_data(race_date)
                if race_day_data and race_day_data.get('status') == 'completed':
                    # Calculate scores from bets and bankers data
                    races = race_day_data.get('races', [])
                    bets = race_day_data.get('bets', {})
                    bankers = race_day_data.get('bankers', {})
                    
                    # Calculate daily score for each user and prepare userScores update
                    updated_user_scores = []
                    for user_id in bets:
                        if user_id in user_total_scores:
                            daily_score = 0
                            
                            # Calculate points from winning bets
                            for race in races:
                                if race.get('winner') and str(race['id']) in bets[user_id]:
                                    user_bet = bets[user_id][str(race['id'])]
                                    if user_bet == race['winner']:
                                        # Find horse odds for points calculation
                                        horse = next((h for h in race['horses'] if h['number'] == race['winner']), None)
                                        if horse:
                                            odds = horse['odds']
                                            if odds > 10:
                                                daily_score += 3
                                            elif odds > 5:
                                                daily_score += 2
                                            else:
                                                daily_score += 1
                            
                            # Apply banker bonus if user has a banker and it won
                            if user_id in bankers:
                                banker_race_id = str(bankers[user_id])
                                banker_race = next((r for r in races if str(r['id']) == banker_race_id), None)
                                if banker_race and banker_race.get('winner'):
                                    user_bet = bets[user_id].get(banker_race_id)
                                    if user_bet == banker_race['winner']:
                                        daily_score *= 2
                            
                            user_total_scores[user_id] += daily_score
                            
                            # Add to updated userScores
                            updated_user_scores.append({
                                "userId": user_id,
                                "dailyScore": daily_score
                            })
                            
                            print(f"[STATS] {race_date}: User {user_id} scored {daily_score} (Total: {user_total_scores[user_id]})")
                    
                    # Update the race day file with the calculated userScores
                    if updated_user_scores:
                        race_day_data['userScores'] = updated_user_scores
                        save_race_day_data(race_date, race_day_data)
                        print(f"[OK] Updated userScores for {race_date}")
                        
            except Exception as e:
                print(f"[WARN] Error processing race day {race_date}: {e}")
                continue
        
        # Create enhanced leaderboard sorted by total score
        enhanced_leaderboard = []
        for rank, user in enumerate(sorted(users, key=lambda x: user_total_scores.get(x['id'], 0), reverse=True), 1):
            user_id = user['id']
            user_data = {
                "rank": rank,
                "id": user["id"],
                "name": user["name"],
                "totalScore": user_total_scores.get(user_id, 0)
            }
            enhanced_leaderboard.append(user_data)
        
        # Calculate leaderboard statistics
        total_users = len(enhanced_leaderboard)
        active_users = len([u for u in enhanced_leaderboard if u["totalScore"] > 0])
        highest_score = enhanced_leaderboard[0]["totalScore"] if enhanced_leaderboard else 0
        
        print(f"[LEADERBOARD] Enhanced leaderboard generated: {total_users} users, {active_users} active, highest score: {highest_score}")
        
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
        print(f"[ERROR] Error generating enhanced leaderboard: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to generate enhanced leaderboard: {str(e)}"
        }), 500

@app.route('/api/race-day/current/status', methods=['GET'])
def get_current_race_day_status():
    """Get current race day status and progress"""
    try:
        current_data = load_current_day_data()
        current_races = current_data.get("races", [])
        current_bets = current_data.get("bets", {})
        current_bankers = current_data.get("bankers", {})
        
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
                    "time": race.get("time", "")
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

# ============================================================================
# 🔧 ADMIN / DATA MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/api/admin/recalculate-scores', methods=['POST'])
def recalculate_scores_endpoint():
    """Manually recalculate user scores for the current race day"""
    try:
        print("[RECALC] Manual score recalculation requested...")
        
        if update_current_user_scores():
            current = load_current_day_data()
            user_scores = current.get("userScores", [])
            
            return jsonify({
                "success": True,
                "message": f"Successfully recalculated scores for {len(user_scores)} users",
                "userScores": user_scores
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Failed to recalculate user scores"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error recalculating scores: {str(e)}"
        }), 500

@app.route('/api/users/recalculate-scores', methods=['POST'])
def recalculate_user_scores_endpoint():
    """Recalculate and update user scores using the new user score system"""
    try:
        print("🧮 Recalculating user scores using new score system...")
        
        # Get race_date from request if provided
        race_date = None
        if request.json and 'raceDate' in request.json:
            race_date = request.json['raceDate']
        
        # Update user scores
        success = update_user_scores(race_date)
        
        if success:
            # Get updated leaderboard data
            leaderboard_data = get_leaderboard_data(race_date)
            
            return jsonify({
                "success": True,
                "message": f"Successfully recalculated scores{f' for {race_date}' if race_date else ' for all race days'}",
                "leaderboard": leaderboard_data,
                "raceDate": race_date
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Failed to recalculate user scores"
            }), 500
            
    except Exception as e:
        print(f"❌ Error recalculating user scores: {e}")
        return jsonify({
            "success": False,
            "error": f"Error recalculating scores: {str(e)}"
        }), 500

@app.route('/api/users/leaderboard', methods=['GET'])
def get_user_leaderboard():
    """Get leaderboard data using the new user score system"""
    try:
        race_date = request.args.get('raceDate')  # Optional race date parameter
        
        leaderboard_data = get_leaderboard_data(race_date)
        
        return jsonify({
            "success": True,
            "leaderboard": leaderboard_data
        }), 200
        
    except Exception as e:
        print(f"❌ Error getting leaderboard: {e}")
        return jsonify({
            "success": False,
            "error": f"Error getting leaderboard: {str(e)}"
        }), 500

@app.route('/api/users/current-scores', methods=['GET'])
def get_current_scores():
    """Get real-time scores for the current race day"""
    try:
        current_scores = get_current_race_day_scores()
        
        return jsonify({
            "success": True,
            "scores": current_scores
        }), 200
        
    except Exception as e:
        print(f"❌ Error getting current scores: {e}")
        return jsonify({
            "success": False,
            "error": f"Error getting current scores: {str(e)}"
        }), 500

@app.route('/api/users/<user_id>/batch-update', methods=['POST'])
def batch_update_user_data(user_id):
    """Update multiple user bets and banker in a single operation"""
    try:
        data = request.get_json()
        user_bets = data.get('bets', {})
        user_banker = data.get('banker')
        race_date = data.get('raceDate')  # Allow specifying which race day to update

        print(f"[UPDATE] Batch update for user {user_id}")
        print(f"   [RECEIVED] Bets: {user_bets}")
        print(f"   [RECEIVED] Banker: {user_banker}")
        print(f"   [DATE] Race date: {race_date}")

        # Load the specified race day data, or current day if not specified
        if race_date:
            current = get_race_day_data(race_date)
            print(f"   [LOADING] Race day data for: {race_date}")
        else:
            current = load_current_day_data()
            race_date = get_current_race_day()
            print(f"   [LOADING] Current race day data: {race_date}")
            
        bets = current.get("bets", {})
        bankers = current.get("bankers", {})
        
        print(f"   [BEFORE] Current bets: {bets}")
        print(f"   [BEFORE] Current bankers: {bankers}")

        # Update bets - convert race IDs to simple format
        if user_bets:
            if user_id not in bets:
                bets[user_id] = {}
            
            # Convert race IDs from "smspariaz_R1_20250816" format to "1" format
            converted_bets = {}
            for race_id, horse_number in user_bets.items():
                if race_id.startswith('smspariaz_R') and '_' in race_id:
                    # Extract race number from "smspariaz_R1_20250816" -> "1"
                    race_number = race_id.split('_R')[1].split('_')[0]
                    converted_bets[race_number] = horse_number
                else:
                    # Already in correct format
                    converted_bets[race_id] = horse_number
            
            print(f"   [CONVERTED] Bets: {user_bets} -> {converted_bets}")
            bets[user_id].update(converted_bets)  # Merge new bets with existing

        # Update banker - convert race ID to simple format
        if user_banker is not None:
            if user_banker.startswith('smspariaz_R') and '_' in user_banker:
                # Extract race number from "smspariaz_R5_20250816" -> "5"
                converted_banker = user_banker.split('_R')[1].split('_')[0]
                print(f"   [CONVERTED] Banker: {user_banker} -> {converted_banker}")
                bankers[user_id] = converted_banker
            else:
                # Already in correct format
                bankers[user_id] = user_banker

        print(f"   [AFTER] Current bets: {bets}")
        print(f"   [AFTER] Current bankers: {bankers}")

        # Save once
        current["bets"] = bets
        current["bankers"] = bankers
        
        if race_date and race_date != get_current_race_day():
            # Save to specific historical race day
            save_race_day_data(race_date, current)
            print(f"   [SAVED] Data saved to historical race day: {race_date}")
        else:
            # Save to current race day
            save_current_day_data(current)
            print(f"   [SAVED] Data saved to current race day")
            # Only recalculate scores for current day
            update_current_user_scores()

        return jsonify({
            "success": True,
            "message": f"Updated {len(user_bets)} bets and banker for user {user_id}"
        }), 200

    except Exception as e:
        print(f"Error in batch update: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/files', methods=['GET'])
def list_data_files():
    """List all data files and their sizes for admin visibility"""
    try:
        files_info = []
        
        # Check all data directories
        for root, dirs, files in os.walk(DATA_DIR):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, DATA_DIR)
                    
                    # Get file size and last modified
                    stat = os.stat(file_path)
                    size = stat.st_size
                    modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
                    
                    # Get record count for JSON files
                    try:
                        data = load_json(file_path, {})
                        if isinstance(data, list):
                            record_count = len(data)
                        elif isinstance(data, dict):
                            if 'raceDays' in data:  # race_days index
                                record_count = len(data['raceDays'])
                            elif 'userScores' in data:  # race day file
                                record_count = len(data['userScores'])
                            else:
                                record_count = len(data)
                        else:
                            record_count = 1
                    except:
                        record_count = 0
                    
                    files_info.append({
                        "path": relative_path,
                        "fullPath": file_path,
                        "size": size,
                        "sizeHuman": f"{size / 1024:.1f} KB" if size > 1024 else f"{size} B",
                        "lastModified": modified,
                        "recordCount": record_count
                    })
        
        # Sort by path
        files_info.sort(key=lambda x: x['path'])
        
        return jsonify({
            "success": True,
            "files": files_info,
            "totalFiles": len(files_info),
            "directories": {
                "data": DATA_DIR,
                "allRaces": ALL_RACES_DIR
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to list files: {str(e)}"
        }), 500

@app.route('/api/admin/files/<path:filepath>', methods=['GET'])
def get_data_file(filepath):
    """Get contents of a specific data file for admin viewing"""
    try:
        # Security: only allow access to files in data directory
        if '..' in filepath or filepath.startswith('/'):
            return jsonify({"error": "Invalid file path"}), 400
        
        full_path = os.path.join(DATA_DIR, filepath)
        
        if not os.path.exists(full_path):
            return jsonify({"error": "File not found"}), 404
        
        if not full_path.endswith('.json'):
            return jsonify({"error": "Only JSON files allowed"}), 400
        
        data = load_json(full_path, {})
        
        # Get file metadata
        stat = os.stat(full_path)
        metadata = {
            "path": filepath,
            "size": stat.st_size,
            "lastModified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "recordCount": len(data) if isinstance(data, (list, dict)) else 1
        }
        
        return jsonify({
            "success": True,
            "metadata": metadata,
            "data": data
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to read file: {str(e)}"
        }), 500

@app.route('/api/admin/status', methods=['GET'])
def get_backend_status():
    """Get comprehensive backend status for admin dashboard"""
    try:
        # Current data stats
        users = load_json(USERS_FILE, [])
        
        # Historical data stats
        index_data = load_json(ALL_RACES_INDEX_FILE, {"raceDays": []})
        historical_days = len(index_data.get("raceDays", []))
        
        # Current race day info
        current_race_day = get_current_race_day()
        
        # Get current race day data for stats
        current_data = load_current_day_data()
        races = current_data.get("races", [])
        bets = current_data.get("bets", {})
        bankers = current_data.get("bankers", {})
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "currentRaceDay": current_race_day,
            "currentData": {
                "users": len(users),
                "races": len(races),
                "bets": len(bets),
                "bankers": len(bankers),
                "completedRaces": len([r for r in races if r.get('winner')])
            },
            "historicalData": {
                "raceDays": historical_days,
                "totalUsers": len(users)
            },
            "directories": {
                "dataDir": DATA_DIR,
                "allRacesDir": ALL_RACES_DIR
            },
            "fileStructure": {
                "users": USERS_FILE,
                "raceDaysIndex": ALL_RACES_INDEX_FILE
            }
        }
        
        return jsonify({
            "success": True,
            "status": status
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get status: {str(e)}"
        }), 500

@app.route('/api/admin/files/<path:filepath>', methods=['PUT'])
def save_data_file(filepath):
    """Save edited content to a specific data file"""
    try:
        # Security: only allow access to files in data directory
        if '..' in filepath or filepath.startswith('/'):
            return jsonify({"error": "Invalid file path"}), 400
        
        full_path = os.path.join(DATA_DIR, filepath)
        
        if not full_path.endswith('.json'):
            return jsonify({"error": "Only JSON files allowed"}), 400
        
        # Get the new content from request
        if not request.json:
            return jsonify({"error": "No JSON content provided"}), 400
        
        new_content = request.json
        
        # Create backup of original file
        if os.path.exists(full_path):
            backup_path = f"{full_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            import shutil
            shutil.copy2(full_path, backup_path)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Save the new content
        with open(full_path, 'w') as f:
            json.dump(new_content, f, indent=2)
        
        # Get updated file metadata
        stat = os.stat(full_path)
        metadata = {
            "path": filepath,
            "size": stat.st_size,
            "lastModified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "recordCount": len(new_content) if isinstance(new_content, (list, dict)) else 1
        }
        
        return jsonify({
            "success": True,
            "message": f"File {filepath} saved successfully",
            "metadata": metadata
        }), 200
        
    except json.JSONDecodeError:
        return jsonify({
            "success": False,
            "error": "Invalid JSON format"
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to save file: {str(e)}"
        }), 500

if __name__ == '__main__':
    # Ensure the data directory exists before running the app
    os.makedirs(DATA_DIR, exist_ok=True)
    init_default_data() # Initialize data files on server start
    
    # Get port from environment variable (for Render deployment) or use 5000 for local
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

