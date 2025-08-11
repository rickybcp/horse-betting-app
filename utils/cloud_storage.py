"""
Cloud Storage Utilities for Horse Betting App
Handles file operations using Google Cloud Storage when available
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import tempfile

# Try to import Google Cloud Storage
try:
    from google.cloud import storage
    from google.cloud.exceptions import NotFound
    CLOUD_STORAGE_AVAILABLE = True
except ImportError:
    CLOUD_STORAGE_AVAILABLE = False
    storage = None
    NotFound = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CloudStorageManager:
    """Manages file operations using Google Cloud Storage"""
    
    def __init__(self, bucket_name: str = None, project_id: str = None):
        self.bucket_name = bucket_name or os.getenv('GCS_BUCKET_NAME')
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
        self.client = None
        self.bucket = None
        
        if CLOUD_STORAGE_AVAILABLE and self.bucket_name:
            try:
                self.client = storage.Client(project=self.project_id)
                self.bucket = self.client.bucket(self.bucket_name)
                logger.info(f"✅ Cloud Storage initialized with bucket: {self.bucket_name}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Cloud Storage: {e}")
                self.client = None
                self.bucket = None
    
    def is_available(self) -> bool:
        """Check if cloud storage is available and configured"""
        return CLOUD_STORAGE_AVAILABLE and self.client is not None and self.bucket is not None
    
    def save_file(self, filepath: str, data: Any) -> bool:
        """Save data to cloud storage"""
        if not self.is_available():
            return False
        
        try:
            blob = self.bucket.blob(filepath)
            if isinstance(data, (dict, list)):
                json_data = json.dumps(data, indent=2, default=str)
                blob.upload_from_string(json_data, content_type='application/json')
            else:
                blob.upload_from_string(str(data))
            
            logger.info(f"✅ Saved to cloud storage: {filepath}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save to cloud storage {filepath}: {e}")
            return False
    
    def load_file(self, filepath: str, default: Any = None) -> Any:
        """Load data from cloud storage"""
        if not self.is_available():
            return default
        
        try:
            blob = self.bucket.blob(filepath)
            if not blob.exists():
                logger.info(f"📁 File not found in cloud storage: {filepath}")
                return default
            
            content = blob.download_as_text()
            if filepath.endswith('.json'):
                return json.loads(content)
            else:
                return content
                
        except NotFound:
            logger.info(f"📁 File not found in cloud storage: {filepath}")
            return default
        except Exception as e:
            logger.error(f"❌ Failed to load from cloud storage {filepath}: {e}")
            return default
    
    def delete_file(self, filepath: str) -> bool:
        """Delete file from cloud storage"""
        if not self.is_available():
            return False
        
        try:
            blob = self.bucket.blob(filepath)
            if blob.exists():
                blob.delete()
                logger.info(f"🗑️ Deleted from cloud storage: {filepath}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Failed to delete from cloud storage {filepath}: {e}")
            return False
    
    def list_files(self, prefix: str = "") -> List[str]:
        """List files in cloud storage with optional prefix"""
        if not self.is_available():
            return []
        
        try:
            blobs = self.bucket.list_blobs(prefix=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            logger.error(f"❌ Failed to list files in cloud storage: {e}")
            return []
    
    def file_exists(self, filepath: str) -> bool:
        """Check if file exists in cloud storage"""
        if not self.is_available():
            return False
        
        try:
            blob = self.bucket.blob(filepath)
            return blob.exists()
        except Exception as e:
            logger.error(f"❌ Failed to check file existence {filepath}: {e}")
            return False

class HybridStorageManager:
    """Hybrid storage manager that uses cloud storage when available, falls back to local"""
    
    def __init__(self, bucket_name: str = None, project_id: str = None):
        self.cloud_manager = CloudStorageManager(bucket_name, project_id)
        self.use_cloud = self.cloud_manager.is_available()
        
        if self.use_cloud:
            logger.info("🚀 Using Cloud Storage for data persistence")
        else:
            logger.info("💾 Using local file storage (cloud storage not available)")
    
    def save_file(self, filepath: str, data: Any) -> bool:
        """Save file using cloud storage if available, otherwise local"""
        if self.use_cloud:
            success = self.cloud_manager.save_file(filepath, data)
            if success:
                return True
            else:
                logger.warning(f"⚠️ Cloud storage failed, falling back to local for: {filepath}")
                self.use_cloud = False
        
        # Fallback to local storage
        return self._save_local(filepath, data)
    
    def load_file(self, filepath: str, default: Any = None) -> Any:
        """Load file using cloud storage if available, otherwise local"""
        if self.use_cloud:
            data = self.cloud_manager.load_file(filepath, default)
            if data is not default:
                return data
            else:
                logger.warning(f"⚠️ Cloud storage failed, falling back to local for: {filepath}")
                self.use_cloud = False
        
        # Fallback to local storage
        return self._load_local(filepath, default)
    
    def delete_file(self, filepath: str) -> bool:
        """Delete file using cloud storage if available, otherwise local"""
        if self.use_cloud:
            success = self.cloud_manager.delete_file(filepath)
            if success:
                return True
            else:
                logger.warning(f"⚠️ Cloud storage failed, falling back to local for: {filepath}")
                self.use_cloud = False
        
        # Fallback to local storage
        return self._delete_local(filepath)
    
    def list_files(self, prefix: str = "") -> List[str]:
        """List files using cloud storage if available, otherwise local"""
        if self.use_cloud:
            files = self.cloud_manager.list_files(prefix)
            if files is not None:
                return files
            else:
                logger.warning(f"⚠️ Cloud storage failed, falling back to local for listing")
                self.use_cloud = False
        
        # Fallback to local storage
        return self._list_local(prefix)
    
    def file_exists(self, filepath: str) -> bool:
        """Check if file exists using cloud storage if available, otherwise local"""
        if self.use_cloud:
            exists = self.cloud_manager.file_exists(filepath)
            if exists is not None:
                return exists
            else:
                logger.warning(f"⚠️ Cloud storage failed, falling back to local for existence check")
                self.use_cloud = False
        
        # Fallback to local storage
        return self._exists_local(filepath)
    
    def _save_local(self, filepath: str, data: Any) -> bool:
        """Save file locally"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                if isinstance(data, (dict, list)):
                    json.dump(data, f, indent=2, default=str)
                else:
                    f.write(str(data))
            logger.info(f"💾 Saved locally: {filepath}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save locally {filepath}: {e}")
            return False
    
    def _load_local(self, filepath: str, default: Any = None) -> Any:
        """Load file locally"""
        if not os.path.exists(filepath):
            return default
        
        try:
            with open(filepath, 'r') as f:
                if filepath.endswith('.json'):
                    return json.load(f)
                else:
                    return f.read()
        except Exception as e:
            logger.error(f"❌ Failed to load locally {filepath}: {e}")
            return default
    
    def _delete_local(self, filepath: str) -> bool:
        """Delete file locally"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"🗑️ Deleted locally: {filepath}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Failed to delete locally {filepath}: {e}")
            return False
    
    def _list_local(self, prefix: str = "") -> List[str]:
        """List files locally"""
        try:
            if not prefix:
                return []
            
            base_dir = os.path.dirname(prefix)
            if not os.path.exists(base_dir):
                return []
            
            files = []
            for filename in os.listdir(base_dir):
                if filename.startswith(os.path.basename(prefix)):
                    files.append(os.path.join(base_dir, filename))
            return files
        except Exception as e:
            logger.error(f"❌ Failed to list files locally: {e}")
            return []
    
    def _exists_local(self, filepath: str) -> bool:
        """Check if file exists locally"""
        return os.path.exists(filepath)

# Global storage manager instance
storage_manager = None

def get_storage_manager() -> HybridStorageManager:
    """Get the global storage manager instance"""
    global storage_manager
    if storage_manager is None:
        storage_manager = HybridStorageManager()
    return storage_manager

def init_cloud_storage(bucket_name: str = None, project_id: str = None):
    """Initialize cloud storage with custom configuration"""
    global storage_manager
    storage_manager = HybridStorageManager(bucket_name, project_id)
    return storage_manager
