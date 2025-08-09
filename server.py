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
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
RACES_FILE = os.path.join(DATA_DIR, 'races.json')
BETS_FILE = os.path.join(DATA_DIR, 'bets.json')
BANKERS_FILE = os.path.join(DATA_DIR, 'bankers.json')

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

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

# Initialize default data on startup
init_default_data()





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
    return jsonify({"success": True, "bankers": bankers}), 200

@app.route('/api/races/scrape', methods=['POST'])
def scrape_races_endpoint():
    try:
        scraped_data = scrape_horses_from_smspariaz()
        save_json(RACES_FILE, scraped_data)
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

if __name__ == '__main__':
    # Ensure the data directory exists before running the app
    os.makedirs(DATA_DIR, exist_ok=True)
    init_default_data() # Initialize data files on server start
    
    # Get port from environment variable (for Render deployment) or use 5000 for local
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

