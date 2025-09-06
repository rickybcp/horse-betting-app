# server.py (Updated - Services and Data Service)
from flask import Flask, jsonify
from flask_cors import CORS
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from utils.cloud_storage import init_cloud_storage

# Import the new route blueprints and services
from routes.users import users_bp
from routes.races import races_bp
from routes.admin import admin_bp
from routes.race_days import race_days_bp
from routes.betting import betting_bp

from services.data_service import DataService

app = Flask(__name__)

# Ensure stdout/stderr use UTF-8 to avoid encoding errors on Windows consoles
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])

# Register the route blueprints
app.register_blueprint(users_bp, url_prefix='/api')
app.register_blueprint(races_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(race_days_bp, url_prefix='/api/race-days')
app.register_blueprint(betting_bp, url_prefix='/api')

# Data file paths
DATA_DIR = 'data'

# Initialize the data service
data_service = DataService()
data_service.init_cloud_storage_and_local_dirs()
data_service.init_default_data() # Initialize data files on server start

@app.route('/')
def index():
    """
    Returns the main application status.
    """
    return jsonify({"status": "OK", "message": "Horse racing betting API is running."})

if __name__ == '__main__':
    # Initialize the cloud storage manager before starting the app
    print(f"🔧 Initializing cloud storage...")
    print(f"   Project ID: {os.getenv('GOOGLE_CLOUD_PROJECT', 'NOT SET')}")
    print(f"   Bucket Name: {os.getenv('GCS_BUCKET_NAME', 'NOT SET')}")
    print(f"   Credentials: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'NOT SET')}")
    
    init_cloud_storage(
        bucket_name=os.getenv("GCS_BUCKET_NAME"),
        project_id=os.getenv("GOOGLE_CLOUD_PROJECT")
    )
    
    # Get port from environment variable (for Render deployment) or use 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
