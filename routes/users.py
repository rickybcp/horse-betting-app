# routes/users.py (Fixed imports)
"""
User-related routes with proper imports.
"""

from flask import Blueprint, jsonify, request
from services import data_service

users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['GET'])
def get_users():
    """Get all users."""
    users = data_service.get_all_users()
    return jsonify(users)

@users_bp.route('/users', methods=['POST'])
def add_user():
    """Add a new user."""
    new_user_name = request.json.get('name')
    if not new_user_name:
        return jsonify({"error": "Name is required"}), 400
    
    new_user = data_service.add_user(name=new_user_name)
    return jsonify(new_user), 201
    
@users_bp.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user."""
    if data_service.delete_user(user_id):
        return jsonify({"success": True, "message": f"User {user_id} deleted"}), 200
    return jsonify({"error": f"User {user_id} not found"}), 404