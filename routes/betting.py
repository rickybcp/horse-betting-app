from flask import Blueprint, jsonify, request
from services.data_service import DataService

betting_bp = Blueprint('betting', __name__)
data_service = DataService()

@betting_bp.route('/bet', methods=['POST'])
def place_bet():
    """Place a bet on a horse for the current race day."""
    try:
        data = request.json
        user_id = data.get('userId')
        race_id = data.get('raceId')
        horse_number = data.get('horseNumber')
        is_banker = data.get('isBanker', False)

        if not all([user_id, race_id, horse_number]):
            return jsonify({"error": "Missing required data"}), 400

        current_day_data = data_service.get_current_race_day_data()
        
        # Ensure the bets and bankers dictionaries exist for the user
        current_day_data['bets'].setdefault(user_id, {})
        current_day_data['bankers'].setdefault(user_id, [])

        # Check if race exists and is not completed
        race_found = False
        for race in current_day_data.get('races', []):
            if race['id'] == race_id:
                if race.get('status') == 'completed':
                    return jsonify({"error": "Race is already completed, no more bets."}), 403
                race_found = True
                break

        if not race_found:
            return jsonify({"error": "Race not found"}), 404
        
        # Check if the user has already placed a bet on this race
        if str(race_id) in current_day_data['bets'][user_id]:
            return jsonify({"error": f"You have already placed a bet on race {race_id}. You can only place one bet per race."}), 409

        # Check if the bet is valid
        horses_in_race = [horse['number'] for race in current_day_data['races'] if race['id'] == race_id for horse in race['horses']]
        if horse_number not in horses_in_race:
            return jsonify({"error": f"Horse {horse_number} is not in race {race_id}."}), 400

        # Place the bet
        current_day_data['bets'][user_id][str(race_id)] = horse_number

        # Add banker bet if applicable
        if is_banker:
            banker_bet = {"raceId": race_id, "horseNumber": horse_number}
            if banker_bet not in current_day_data['bankers'][user_id]:
                current_day_data['bankers'][user_id].append(banker_bet)

        data_service.save_current_race_day_data(current_day_data)
        
        print(f"[BET] User {user_id} placed bet on race {race_id}, horse {horse_number}")
        return jsonify({"success": True, "message": "Bet placed successfully."}), 201

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ---- Compatibility endpoints expected by the current frontend ----

@betting_bp.route('/bets', methods=['GET'])
def list_bets():
    """Compatibility: return bets as an array of { userId, raceId, horse }."""
    try:
        current = data_service.get_current_race_day_data()
        bets_map = current.get('bets', {})
        bet_list = []
        for user_id, race_map in bets_map.items():
            for race_id_str, horse_num in race_map.items():
                bet_list.append({
                    "userId": user_id,
                    "raceId": int(race_id_str) if str(race_id_str).isdigit() else race_id_str,
                    "horse": horse_num
                })
        return jsonify(bet_list), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@betting_bp.route('/bets', methods=['POST'])
def place_bet_compat():
    """Compatibility: accept { userId, raceId, horse } and set a bet."""
    try:
        data = request.json
        user_id = data.get('userId')
        race_id = data.get('raceId')
        horse_number = data.get('horse')

        if not all([user_id, race_id, horse_number]):
            return jsonify({"success": False, "error": "Missing required data"}), 400

        current = data_service.get_current_race_day_data()
        current.setdefault('bets', {}).setdefault(user_id, {})

        # Validate race exists and not completed
        race = next((r for r in current.get('races', []) if r.get('id') == race_id), None)
        if not race:
            return jsonify({"success": False, "error": "Race not found"}), 404
        if race.get('status') == 'completed':
            return jsonify({"success": False, "error": "Race is already completed, no more bets."}), 403

        current['bets'][user_id][str(race_id)] = horse_number
        data_service.save_current_race_day_data(current)

        return jsonify({
            "success": True,
            "bet": {"userId": user_id, "raceId": race_id, "horse": horse_number}
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@betting_bp.route('/bankers', methods=['GET'])
def list_bankers():
    """Compatibility: return bankers as { userId: raceId }. If multiple, choose the last set."""
    try:
        current = data_service.get_current_race_day_data()
        bankers_map = current.get('bankers', {})
        flat = {}
        for user_id, banker_entries in bankers_map.items():
            # banker_entries expected as list of { raceId, horseNumber } in new model; FE expects just raceId
            if isinstance(banker_entries, list) and banker_entries:
                flat[user_id] = banker_entries[-1].get('raceId')
            elif isinstance(banker_entries, (str, int)):
                flat[user_id] = banker_entries
        return jsonify(flat), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@betting_bp.route('/bankers', methods=['POST'])
def set_banker_compat():
    """Compatibility: accept { userId, raceId } and set as banker (without horse number)."""
    try:
        data = request.json
        user_id = data.get('userId')
        race_id = data.get('raceId')

        if not all([user_id, race_id]):
            return jsonify({"success": False, "error": "Missing required data"}), 400

        current = data_service.get_current_race_day_data()
        current.setdefault('bankers', {}).setdefault(user_id, [])

        # Append/replace latest banker
        current['bankers'][user_id].append({"raceId": race_id})

        data_service.save_current_race_day_data(current)

        # Return updated flat shape
        updated = {}
        for uid, entries in current['bankers'].items():
            if isinstance(entries, list) and entries:
                updated[uid] = entries[-1].get('raceId')
        return jsonify({"success": True, "bankers": updated}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500