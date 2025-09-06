# routes/betting.py (Updated - Using DataService)
from flask import Blueprint, jsonify, request
import logging
from services import data_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

betting_bp = Blueprint('betting', __name__)

@betting_bp.route('/bet', methods=['POST'])
def place_bet():
    """Place a regular bet for a user on a specific horse."""
    data = request.json
    user_id = data.get('userId')
    race_id = data.get('raceId')
    horse_number = data.get('horseNumber')

    if not all([user_id, race_id, horse_number]):
        return jsonify({"error": "Missing required fields: userId, raceId, horseNumber"}), 400

    success = data_service.place_bet(user_id, race_id, horse_number, is_banker=False)
    if success:
        return jsonify({"success": True, "message": f"Bet placed for user {user_id} on horse {horse_number} in race {race_id}"}), 200
    else:
        # Check if race is completed to provide specific error message
        from models import Race
        race = Race.query.get(race_id)
        if race and race.status == 'completed':
            return jsonify({"success": False, "error": "Cannot place bet on completed race"}), 400
        else:
            return jsonify({"success": False, "error": "Failed to place bet"}), 500

@betting_bp.route('/banker', methods=['POST'])
def place_banker_bet():
    """Place a banker bet for a user on a specific horse."""
    data = request.json
    user_id = data.get('userId')
    race_id = data.get('raceId')
    horse_number = data.get('horseNumber')

    if not all([user_id, race_id, horse_number]):
        return jsonify({"error": "Missing required fields: userId, raceId, horseNumber"}), 400

    success = data_service.place_bet(user_id, race_id, horse_number, is_banker=True)
    if success:
        return jsonify({"success": True, "message": f"Banker bet placed for user {user_id} on horse {horse_number} in race {race_id}"}), 200
    else:
        # Check if race is completed to provide specific error message
        from models import Race
        race = Race.query.get(race_id)
        if race and race.status == 'completed':
            return jsonify({"success": False, "error": "Cannot place banker bet on completed race"}), 400
        else:
            return jsonify({"success": False, "error": "Failed to place banker bet"}), 500

@betting_bp.route('/bets', methods=['GET'])
def get_all_bets():
    """Get all bets from the database."""
    from models import Bet, User, Race
    bets = Bet.query.all()
    bets_data = []
    for bet in bets:
        bets_data.append({
            "userId": bet.user_id,
            "raceId": bet.race_id,
            "horse": bet.horse_number,
            "is_banker": bet.is_banker
        })
    return jsonify(bets_data)

@betting_bp.route('/bankers', methods=['GET'])
def get_all_bankers():
    """Get all banker bets from the database, optionally filtered by race date."""
    from models import Bet, Race
    
    race_date = request.args.get('race_date')
    
    if race_date:
        # Filter bankers by specific race date
        bankers = Bet.query.join(Race).filter(
            Bet.is_banker == True,
            Race.date == race_date
        ).all()
    else:
        # Return all bankers (backward compatibility)
        bankers = Bet.query.filter_by(is_banker=True).all()
    
    bankers_data = {}
    for banker in bankers:
        bankers_data[banker.user_id] = banker.race_id
    return jsonify(bankers_data)