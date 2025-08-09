from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

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

def scrape_horses_from_smspariaz():
    """Scrape horse racing data from smspariaz.com (placeholder implementation)"""
    chrome_options = Options()
    # Ensure headless mode for server environments
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = None
    races_data = [] # To store scraped race data
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get('https://www.smspariaz.com/local/')
        
        wait = WebDriverWait(driver, 10)
        
        # Attempt to find race containers. This is a simplified placeholder.
        # In a real scenario, you'd parse more details like horse names, odds, etc.
        try:
            # Look for elements that might contain race information
            race_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.race-card, .race-info'))) 
            
            if race_elements:
                for i, race_el in enumerate(race_elements[:3]): # Limit to first 3 for example
                    race_name = f"Race {i+1} at {datetime.now().strftime('%H:%M')}"
                    race_time = (datetime.now() + timedelta(minutes=30 * (i+1))).strftime('%H:%M')
                    horses = []
                    for j in range(1, 4): # Dummy horses
                        horses.append({
                            "number": j, 
                            "name": f"Horse {j}-{chr(65+i)}", 
                            "odds": round(2.0 + j * 0.5 + i * 0.1, 1),
                            "points": (3 if (2.0 + j * 0.5 + i * 0.1) > 10 else (2 if (2.0 + j * 0.5 + i * 0.1) > 5 else 1))
                        })
                    races_data.append({
                        "id": f"race_{i+1}_{datetime.now().strftime('%Y%m%d')}",
                        "name": race_name,
                        "time": race_time,
                        "horses": horses,
                        "winner": None,
                        "status": "upcoming"
                    })
            else:
                print("No race elements found, returning dummy data.")
                # Fallback to dummy data if no elements are found
                races_data = [
                    {"id": "race_1_dummy", "name": "Dummy Race 1", "time": "14:00", "horses": [{"number": 1, "name": "Dummy Horse A", "odds": 2.5, "points": 1}, {"number": 2, "name": "Dummy Horse B", "odds": 3.0, "points": 1}], "winner": None, "status": "upcoming"},
                    {"id": "race_2_dummy", "name": "Dummy Race 2", "time": "15:00", "horses": [{"number": 1, "name": "Dummy Horse X", "odds": 4.0, "points": 1}, {"number": 2, "name": "Dummy Horse Y", "odds": 2.0, "points": 1}], "winner": None, "status": "upcoming"},
                ]
        except Exception as e:
            print(f"Could not find race elements or parse them: {e}")
            # Fallback to dummy data if parsing fails
            races_data = [
                {"id": "race_1_dummy", "name": "Dummy Race 1", "time": "14:00", "horses": [{"number": 1, "name": "Dummy Horse A", "odds": 2.5, "points": 1}, {"number": 2, "name": "Dummy Horse B", "odds": 3.0, "points": 1}], "winner": None, "status": "upcoming"},
                {"id": "race_2_dummy", "name": "Dummy Race 2", "time": "15:00", "horses": [{"number": 1, "name": "Dummy Horse X", "odds": 4.0, "points": 1}, {"number": 2, "name": "Dummy Horse Y", "odds": 2.0, "points": 1}], "winner": None, "status": "upcoming"},
            ]
            
    except Exception as e:
        print(f"Error during scraping setup or navigation: {e}")
        # Return dummy data on setup/navigation failure
        races_data = [
            {"id": "race_1_dummy", "name": "Dummy Race 1", "time": "14:00", "horses": [{"number": 1, "name": "Dummy Horse A", "odds": 2.5, "points": 1}, {"number": 2, "name": "Dummy Horse B", "odds": 3.0, "points": 1}], "winner": None, "status": "upcoming"},
            {"id": "race_2_dummy", "name": "Dummy Race 2", "time": "15:00", "horses": [{"number": 1, "name": "Dummy Horse X", "odds": 4.0, "points": 1}, {"number": 2, "name": "Dummy Horse Y", "odds": 2.0, "points": 1}], "winner": None, "status": "upcoming"},
        ]
    finally:
        if driver:
            driver.quit()
    
    return races_data

def scrape_mtc_next_race_day(desired_month_text: str | None = None):
    """Scrape next race day card from MTC Jockey Club fixtures page.
    Attempts to:
      1) Open fixtures page
      2) Optionally select the desired month tab/button if provided
      3) Click the first visible "View Race Card" link
      4) On the race card page, iterate races tabs and extract race name/time and runners
    Returns the races list in our standard schema.
    """
    fixtures_url = 'https://www.mtcjockeyclub.com/form-guide/fixtures'

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = None
    races_data = []

    def safe_text(el):
        try:
            return el.text.strip()
        except Exception:
            return ''

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(fixtures_url)

        wait = WebDriverWait(driver, 20)
        # Wait for any content to be present
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'body *')))

        # If a month is specified, try to click it
        if desired_month_text:
            try:
                month_buttons = driver.find_elements(By.XPATH, f"//button[contains(., '{desired_month_text}') or contains(., '{desired_month_text[:3]}')]|//a[contains(., '{desired_month_text}') or contains(., '{desired_month_text[:3]}')]")
                for btn in month_buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        btn.click()
                        time.sleep(1)
                        break
            except Exception:
                pass

        # Find and click the first visible "View Race Card" (or similar) link
        racecard_links = driver.find_elements(By.XPATH, "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'view race card') or contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'race card')]")
        clicked = False
        for link in racecard_links:
            try:
                if link.is_displayed() and link.is_enabled():
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
                    link.click()
                    clicked = True
                    break
            except Exception:
                continue

        if not clicked:
            # If no direct link found, try to locate buttons
            buttons = driver.find_elements(By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'view race card') or contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'race card')]")
            for btn in buttons:
                try:
                    if btn.is_displayed() and btn.is_enabled():
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                        btn.click()
                        clicked = True
                        break
                except Exception:
                    continue

        if not clicked:
            print("Could not find a 'View Race Card' link/button. Returning empty result.")
            return []

        # We should now be on the race card page; wait for tabbed races or content
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'body *')))

        # Try to collect race tabs/buttons
        race_tabs = driver.find_elements(By.XPATH, "//a[contains(@class,'nav-link') and (contains(., 'Race') or contains(., 'R') or contains(., 'Course'))] | //button[contains(@class,'nav-link') and (contains(., 'Race') or contains(., 'R'))]")
        if not race_tabs:
            # Fallback: look for elements that look like race selectors
            race_tabs = driver.find_elements(By.XPATH, "//a[contains(., 'Race') or contains(., 'R1') or contains(., 'R2')] | //button[contains(., 'Race') or contains(., 'R1') or contains(., 'R2')]")

        # If still nothing, try to treat the current page as a single race card (no tabs)
        if not race_tabs:
            race_tabs = []

        def parse_current_race_panel() -> dict | None:
            """Parse current visible race panel into our schema."""
            # Race header/name
            race_name = ''
            race_time = ''

            # Try common header containers
            header_candidates = driver.find_elements(By.XPATH, "//h1|//h2|//h3|//div[contains(@class,'race')][contains(@class,'title')]|//div[contains(@class,'race')][contains(@class,'header')]")
            for hc in header_candidates:
                txt = safe_text(hc)
                if txt and ('Race' in txt or 'R' in txt or ':' in txt):
                    race_name = txt
                    # Extract time like 12:45
                    m = re.search(r"(\d{1,2}:\d{2})", txt)
                    if m:
                        race_time = m.group(1)
                    break

            # If time still empty, search elsewhere
            if not race_time:
                try:
                    time_el = driver.find_element(By.XPATH, "//*[contains(text(),':') and string-length(normalize-space())<=10]")
                    race_time = safe_text(time_el)
                except Exception:
                    race_time = ''

            # Horses list
            horses = []
            # Try several candidate containers commonly used for runners
            runner_containers = driver.find_elements(By.XPATH, "//div[contains(@class,'runner') or contains(@class,'entry') or contains(@class,'horse') or contains(@class,'card') or contains(@class,'row')]//div[.//text()]")
            if not runner_containers:
                # Fallback to list items/rows
                runner_containers = driver.find_elements(By.XPATH, "//li[contains(@class,'runner') or contains(@class,'entry')] | //tr[contains(@class,'runner') or contains(@class,'entry')] | //div[contains(@class,'runner')]")

            # Limit to a reasonable number to avoid grabbing layout grids
            candidates = runner_containers[:50]
            for idx, rc in enumerate(candidates, start=1):
                txt = safe_text(rc)
                if not txt:
                    continue
                # Heuristic: require some alphabetic content to avoid empty grid cols
                if not re.search(r"[A-Za-z]", txt):
                    continue
                # Extract horse number if present like "1" or "No. 1"
                num_match = re.search(r"(?:No\.?\s*)?(\d{1,2})\b", txt)
                horse_number = int(num_match.group(1)) if num_match else idx
                # Extract a name-like token: longest word sequence
                # This is heuristic; the site may have a dedicated name element
                name_match = None
                try:
                    # Prefer child element that looks like a name
                    name_el = rc.find_element(By.XPATH, ".//*[contains(@class,'name') or contains(@class,'horse')][1]")
                    name_match = safe_text(name_el)
                except Exception:
                    pass
                horse_name = name_match if name_match else (re.search(r"([A-Z][A-Z'\- ]{2,})", txt) or [None])
                if isinstance(horse_name, list):
                    horse_name = horse_name[0]
                if not horse_name:
                    # Fallback to first 4 words as name
                    horse_name = " ".join(txt.split()[:4])

                horses.append({
                    "number": horse_number,
                    "name": horse_name.strip(),
                    # Odds may not be available in fixture; skip or set None
                    "odds": None,
                    # Default points to 1 if odds unknown
                    "points": 1
                })

            if not race_name:
                # Provide a generic name
                race_name = f"Race {len(races_data) + 1}"

            return {
                "id": f"mtc_{len(races_data)+1}_{datetime.now().strftime('%Y%m%d')}",
                "name": race_name,
                "time": race_time or datetime.now().strftime('%H:%M'),
                "horses": horses,
                "winner": None,
                "status": 'upcoming'
            }

        if race_tabs:
            for tab in race_tabs[:12]:  # reasonable upper bound
                try:
                    if tab.is_displayed() and tab.is_enabled():
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tab)
                        tab.click()
                        time.sleep(0.8)
                        race_data = parse_current_race_panel()
                        if race_data:
                            races_data.append(race_data)
                except Exception as e:
                    print(f"Tab parse error: {e}")
                    continue
        else:
            # Single race card fallback
            race_data = parse_current_race_panel()
            if race_data:
                races_data.append(race_data)

    except Exception as e:
        print(f"Error during MTC scraping: {e}")
        races_data = []
    finally:
        if driver:
            driver.quit()

    return races_data

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

