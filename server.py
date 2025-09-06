# server.py (Fixed - No Circular Imports)
"""
Main Flask application with clean database initialization.
No more circular imports!
"""

from flask import Flask, jsonify
from flask_cors import CORS
import os
import sys

# Import our database initialization
from database import db, init_db, create_tables

# Ensure stdout/stderr use UTF-8 to avoid encoding errors
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

def create_app():
    """Application factory pattern for better testing and organization."""
    app = Flask(__name__)

    # --- Database Configuration ---
    # Use a simple SQLite database for development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///horse_betting.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize database
    init_db(app)
    
    # Configure CORS
    CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
         allow_headers=["Content-Type", "Authorization"])

    # Import models after database is initialized (this registers them with SQLAlchemy)
    from models import User, Race, Horse, Bet, UserScore

    # Import and register route blueprints AFTER database setup
    from routes.users import users_bp
    from routes.races import races_bp
    from routes.admin import admin_bp
    from routes.race_days import race_days_bp
    from routes.betting import betting_bp

    # Register the route blueprints
    app.register_blueprint(users_bp, url_prefix='/api')
    app.register_blueprint(races_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(race_days_bp, url_prefix='/api/race-days')
    app.register_blueprint(betting_bp, url_prefix='/api')

    @app.route('/')
    def index():
        """Returns the main application status."""
        return jsonify({"status": "OK", "message": "Horse racing betting API is running."})

    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    # Create the database tables
    create_tables(app)

    # Get port from environment variable (for Render deployment) or use 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)