from flask import Blueprint, jsonify
from services.data_service import DataService

race_days_bp = Blueprint('race_days', __name__)
data_service = DataService()

@race_days_bp.route('/', methods=['GET'])
def get_all_race_days():
    """Get a list of all race days available."""
    index_data = data_service.get_race_day_index()
    return jsonify({"raceDays": index_data.get("raceDays", [])})

@race_days_bp.route('/<race_date>', methods=['GET'])
def get_single_race_day(race_date):
    """Get all data for a specific race day by date."""
    race_day_data = data_service.get_race_day_data(race_date)
    
    if not race_day_data.get("date"):
        return jsonify({"error": f"Race day {race_date} not found."}), 404
    
    return jsonify(race_day_data)


# ---- Compatibility endpoints expected by the current frontend ----

@race_days_bp.route('/current', methods=['GET'])
def get_current_race_day():
    """Return current race day wrapped in { success, data }."""
    try:
        data = data_service.get_current_race_day_data()
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@race_days_bp.route('/historical', methods=['GET'])
def get_historical_race_days():
    """Return historical race days list { success, historical_race_days }."""
    try:
        index_data = data_service.get_race_day_index()
        historical = [d for d in index_data.get("raceDays", []) if d.get("status") == "completed"]
        return jsonify({"success": True, "historical_race_days": historical}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@race_days_bp.route('/leaderboard', methods=['GET'])
def get_overall_leaderboard():
    """Return overall leaderboard as { success, leaderboard } with userId,userName,totalScore."""
    try:
        agg = data_service.get_leaderboard_data()
        users = agg.get("users", [])
        leaderboard = [
            {
                "userId": u.get("userId"),
                "userName": u.get("name"),
                "totalScore": u.get("totalScore", 0),
            }
            for u in users
        ]
        return jsonify({"success": True, "leaderboard": leaderboard}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@race_days_bp.route('/leaderboard/current', methods=['GET'])
def get_current_day_leaderboard():
    """Return current day scores as { success, scores } with userId,dailyScore.
    Names are joined on the client.
    """
    try:
        current = data_service.get_current_race_day_data()
        scores = current.get("userScores", [])
        transformed = [
            {
                "userId": s.get("userId"),
                "dailyScore": s.get("score") if "score" in s else s.get("dailyScore", 0),
                "raceScores": s.get("raceScores", {}),
            }
            for s in scores
        ]
        return jsonify({"success": True, "scores": transformed}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500