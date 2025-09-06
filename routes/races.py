from flask import Blueprint, jsonify, request
from services import data_service
from datetime import datetime

races_bp = Blueprint('races', __name__)

@races_bp.route('/races', methods=['GET'])
def get_races():
    """Returns a list of all races for the current race day."""
    current_day_data = data_service.get_race_day_data(datetime.now().strftime('%Y-%m-%d'))
    races = current_day_data.get("races", [])
    return jsonify(races)

@races_bp.route('/races/scrape', methods=['POST'])
def scrape_races():
    """Scrapes races for a new race day and sets it as current."""
    try:
        current_day = data_service.scrape_new_races()
        data_service.save_current_race_day_data(current_day)
        
        print(f"[OK] Scraped {len(current_day.get('races', []))} races for {current_day.get('date')}")
        return jsonify({"success": True, "message": "Races scraped and saved successfully."}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@races_bp.route('/races/<race_id>/result', methods=['POST'])
def update_single_race_result(race_id):
    """Manually updates the result for a specific race."""
    try:
        winner_number = request.json.get('winner')
        if winner_number is None:
            return jsonify({"error": "Winner number is required"}), 400
            
        if data_service.save_race_result(race_id, winner_number):
            # Recalculate and update current user scores after race result change
            data_service.calculate_current_user_scores()
            print(f"[OK] Race result updated and synced to current race day")
            return jsonify({"success": True, "message": f"Race {race_id} winner set to horse #{winner_number}"}), 200
        else:
            return jsonify({"error": "Race not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
