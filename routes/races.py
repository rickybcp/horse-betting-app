from flask import Blueprint, jsonify, request
from datetime import datetime
import os
from services.data_service import DataService
# from services.scraping_service import ScrapingService  # Disabled until scraper modules exist

# Initialize a DataService instance for use within this blueprint.
# This instance will handle all data interactions.
data_service = DataService()
# scraping_service = ScrapingService(data_service)  # Disabled until scraper modules exist

races_bp = Blueprint('races', __name__)

@races_bp.route('/races', methods=['GET'])
def get_races():
    """Returns a list of all races for the current race day."""
    current_day_data = data_service.get_current_race_day_data()
    races = current_day_data.get("races", [])
    return jsonify(races)

@races_bp.route('/races/scrape', methods=['POST'])
def scrape_races():
    """
    Scrapes races for a new race day and sets it as current.
    NOTE: Scraping functionality temporarily disabled - returns existing data.
    """
    try:
        # TODO: Re-enable scraping when scraper modules are available
        # For now, return the current race day data
        current_day = data_service.get_current_race_day_data()
        if not current_day.get('races'):
            return jsonify({"success": False, "error": "No race data available. Scraping functionality is temporarily disabled."}), 500
        
        # Add a record to the all_races index
        index_data = data_service.get_race_day_index()
        
        # Clear any old 'current' race day and set the new one
        for day in index_data["raceDays"]:
            day["current"] = False

        race_day_record = {
            "date": current_day["date"],
            "status": "active",
            "current": True # Set this new day as the current active one
        }
        
        # Check if this race day record already exists
        record_exists = any(
            day["date"] == race_day_record["date"]
            for day in index_data["raceDays"]
        )
        
        if not record_exists:
            index_data["raceDays"].append(race_day_record)
        else:
            # Update the existing record
            for i, day in enumerate(index_data["raceDays"]):
                if day["date"] == race_day_record["date"]:
                    index_data["raceDays"][i] = race_day_record
                    break

        data_service.save_race_day_index(index_data)
        
        return jsonify({"success": True, "message": "Using existing race data (scraping temporarily disabled)."}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@races_bp.route('/races/results', methods=['POST'])
def scrape_results():
    """Compatibility: scrape results for current race day and update scores."""
    try:
        # TODO: Re-enable scraping when scraper modules are available
        # For now, just recalculate scores with existing data
        data_service.update_current_user_scores()
        
        # Get current race day for results summary
        current_day = data_service.get_current_race_day_data()
        
        # Compose a compact results summary
        summary = {}
        for race in current_day.get('races', []):
            if 'winner' in race and race['winner'] is not None:
                summary[str(race.get('id'))] = race['winner']

        return jsonify({"success": True, "results": summary, "message": "Scores recalculated with existing data (scraping temporarily disabled)"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@races_bp.route('/races/<int:race_id>/result', methods=['POST'])
def update_single_race_result(race_id):
    """Manually updates the result for a specific race."""
    try:
        current = data_service.get_current_race_day_data()
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
        data_service.save_current_race_day_data(current)
        
        # Recalculate and update current user scores after race result change
        data_service.update_current_user_scores()
        
        print(f"[OK] Race result updated and synced to current race day")
        return jsonify({"success": True, "message": f"Race {race_id} winner set to horse #{winner_number}"}), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
