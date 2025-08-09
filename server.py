from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
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

@app.route('/api/reset', methods=['POST'])
def reset_data():
    users = load_json(USERS_FILE, [])
    current_races = load_json(RACES_FILE, [])
    current_bets = load_json(BETS_FILE, {})
    current_bankers = load_json(BANKERS_FILE, {})

    for user in users:
        user_id = user['id']
        daily_score = 0
        
        for race in current_races:
            if race.get('winner') and current_bets.get(user_id) and current_bets[user_id].get(race['id']):
                user_bet = current_bets[user_id][race['id']]
                if user_bet == race['winner']:
                    horse = next((h for h in race['horses'] if h['number'] == race['winner']), None)
                    if horse:
                        odds = horse['odds']
                        points = 1
                        if odds > 10: points = 3
                        elif odds > 5: points = 2
                        daily_score += points
        
        # Apply banker bonus
        if current_bankers.get(user_id):
            banker_race_id = str(current_bankers[user_id]) # Ensure it's a string
            # Check if user won their banker race
            if (current_bets.get(user_id) and 
                current_bets[user_id].get(banker_race_id) and
                # Check if the user's bet on the banker race matches the winner of that race
                current_bets[user_id][banker_race_id] == next((r for r in current_races if r['id'] == banker_race_id), {}).get('winner')):
                daily_score *= 2

        user['totalScore'] = user.get('totalScore', 0) + daily_score
    
    save_json(USERS_FILE, users)

    save_json(RACES_FILE, [])
    save_json(BETS_FILE, {})
    save_json(BANKERS_FILE, {})
    
    return jsonify({"success": True}), 200

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
def complete_race_day(race_day):
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

if __name__ == '__main__':
    # Ensure the data directory exists before running the app
    os.makedirs(DATA_DIR, exist_ok=True)
    init_default_data() # Initialize data files on server start
    
    # Get port from environment variable (for Render deployment) or use 5000 for local
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

