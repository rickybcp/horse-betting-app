from flask import Blueprint, jsonify, request
from services.data_service import DataService
import os

# Initialize a DataService instance for use within this blueprint.
data_service = DataService()

users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['GET'])
def get_users():
    """Get all users."""
    users = data_service.load_users()
    return jsonify(users)

@users_bp.route('/users', methods=['POST'])
def add_user():
    """Add a new user."""
    users = data_service.load_users()
    new_user_name = request.json.get('name')
    
    if not new_user_name:
        return jsonify({"error": "Name is required"}), 400
        
    # Generate a unique ID for the new user
    new_user_id = os.urandom(16).hex()
    
    new_user = {
        "id": new_user_id,
        "name": new_user_name
    }
    
    users.append(new_user)
    data_service.save_users(users)
    
    print(f"[USERS] User added: {new_user_name}")
    # Compatibility shape for frontend: { success, user }
    return jsonify({
        "success": True,
        "user": new_user
    }), 201

@users_bp.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user."""
    users = data_service.load_users()
    users = [user for user in users if user['id'] != user_id]
    
    data_service.save_users(users)
    
    print(f"[USERS] User deleted: {user_id}")
    return jsonify({"success": True, "message": f"User {user_id} deleted"}), 200

@users_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get the overall leaderboard."""
    leaderboard = data_service.get_leaderboard_data()
    return jsonify(leaderboard)

@users_bp.route('/users/<user_id>/scores/<race_date>', methods=['GET'])
def get_user_performance_on_date(user_id, race_date):
    """Get user's detailed performance on a specific race day."""
    try:
        race_day_data = data_service.get_race_day_data(race_date)
        
        if not race_day_data.get("date"):
            return jsonify({
                "success": False,
                "error": f"Race day {race_date} not found"
            }), 404
        
        user_performance = next(
            (user_score for user_score in race_day_data.get("userScores", []) if user_score["userId"] == user_id),
            None
        )
        
        if not user_performance:
            return jsonify({
                "success": False,
                "error": f"User {user_id} did not participate on {race_date}"
            }), 404
        
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
            "error": str(e)
        }), 500
