import os
import json
import logging
import shutil
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

from services.data_service import DataService
from utils.cloud_storage import get_storage_manager, init_cloud_storage

admin_bp = Blueprint('admin', __name__)
data_service = DataService()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@admin_bp.route('/migrate', methods=['POST'])
def migrate_to_cloud():
    """
    Migrates all local data files to Google Cloud Storage.
    """
    try:
        storage_manager = get_storage_manager()
        if not storage_manager.use_cloud:
            return jsonify({"success": False, "error": "Cloud storage is not configured."}), 500
        
        local_data_dir = data_service.DATA_DIR
        
        if not os.path.exists(local_data_dir):
            return jsonify({"success": False, "error": f"Local data directory '{local_data_dir}' not found."}), 404
            
        uploaded_files = []
        failed_files = []

        # Walk through local data directory and upload all files
        for root, _, files in os.walk(local_data_dir):
            for filename in files:
                local_path = os.path.join(root, filename)
                # Determine the relative path to be used as the GCS blob name
                relative_path = os.path.relpath(local_path, local_data_dir)
                cloud_path = os.path.join(data_service.DATA_DIR, relative_path).replace("\\", "/") # Use forward slashes for cloud storage
                
                try:
                    with open(local_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    storage_manager.save_file(cloud_path, data)
                    uploaded_files.append(cloud_path)
                except Exception as e:
                    failed_files.append({"path": cloud_path, "error": str(e)})
        
        print(f"[MIGRATE] Migration complete. Uploaded {len(uploaded_files)} files, failed {len(failed_files)}.")
        return jsonify({
            "success": True, 
            "message": "Migration to cloud storage completed.",
            "uploaded": uploaded_files,
            "failed": failed_files
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/files', methods=['GET'])
def list_files():
    """Lists all data files in the backend."""
    storage_manager = get_storage_manager()
    files = storage_manager.list_files(prefix=data_service.DATA_DIR)
    
    # Exclude temporary or system files
    files = [f for f in files if not f.startswith('.') and f.endswith('.json')]
    
    file_list = []
    for f in files:
        try:
            # We can't get size/modified date from all backends, so just return path
            file_list.append({"path": f})
        except Exception:
            file_list.append({"path": f})
            
    return jsonify({"success": True, "files": file_list}), 200

@admin_bp.route('/files/<path:filepath>', methods=['PUT'])
def save_file_put(filepath):
    """Compatibility: Save a file via PUT /admin/files/<path> with raw JSON body."""
    try:
        storage_manager = get_storage_manager()
        content_json = request.get_json(force=True, silent=False)
        success = storage_manager.save_file(filepath, content_json)
        if success:
            return jsonify({"success": True, "message": f"File {filepath} saved successfully."}), 200
        else:
            return jsonify({"success": False, "error": f"Failed to save file {filepath}."}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/files/delete', methods=['POST'])
def delete_file():
    """Deletes a file from the backend."""
    try:
        storage_manager = get_storage_manager()
        filepath = request.json.get('path')
        
        if not filepath:
            return jsonify({"error": "Missing file path"}), 400
            
        # Cloud storage does not have a simple 'delete' method in our current manager,
        # but we can simulate by clearing the file. This would be replaced with a proper delete in production.
        # For now, we will handle this by returning an error.
        return jsonify({"success": False, "error": "File deletion is not supported in the current environment."}), 405

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/files/<path:filepath>', methods=['GET'])
def get_file_content(filepath):
    """Compatibility: fetch content via /admin/files/<path>."""
    try:
        storage_manager = get_storage_manager()
        content = storage_manager.load_file(filepath)
        if content is None:
            return jsonify({"success": False, "error": "File not found or content could not be loaded."}), 404
        return jsonify({"success": True, "content": content}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/reset-data', methods=['POST'])
def reset_data():
    """Compatibility: Clear users and reset current day bets/bankers/userScores."""
    try:
        data_service.save_users([])
        current = data_service.get_current_race_day_data()
        current['bets'] = {}
        current['bankers'] = {}
        current['userScores'] = []
        data_service.save_current_race_day_data(current)
        return jsonify({"success": True, "message": "All user data cleared and current race day reset."}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
