"""
Cloud Storage Utilities for Horse Betting App
Handles file operations using Google Cloud Storage when available
"""

import os
import json
import logging
import re
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
# Ensure logging handlers don't attempt to emit non-ASCII by default
for handler in logger.handlers:
    try:
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    except Exception:
        pass

def sanitize_unicode_for_encoding(data):
    """
    Recursively sanitize Unicode characters that might cause encoding issues.
    Removes or replaces problematic Unicode characters like emojis.
    """
    if isinstance(data, dict):
        return {k: sanitize_unicode_for_encoding(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_unicode_for_encoding(item) for item in data]
    elif isinstance(data, str):
        # Remove emojis and other problematic Unicode characters
        # This regex removes most emojis and special Unicode symbols
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002700-\U000027BF"  # dingbats
            "\U0001F900-\U0001F9FF"  # supplemental symbols
            "\U00002600-\U000026FF"  # miscellaneous symbols
            "\U00002B50-\U00002B55"  # stars
            "]+",
            flags=re.UNICODE
        )
        # Replace emojis with a safe alternative or remove them
        sanitized = emoji_pattern.sub('', data)
        
        # Also handle any remaining non-ASCII characters that might cause issues
        # Keep only ASCII characters and common extended ASCII
        try:
            # Try to encode with 'ascii' and if it fails, replace problematic chars
            sanitized.encode('ascii')
            return sanitized
        except UnicodeEncodeError:
            # If ASCII encoding fails, keep only safe characters
            safe_chars = ''.join(char for char in sanitized if ord(char) < 256)
            return safe_chars
    else:
        return data

class CloudStorageManager:
    """Manages file operations using Google Cloud Storage"""
    
    def __init__(self, bucket_name: str = None, project_id: str = None):
        self.bucket_name = bucket_name or os.getenv('GCS_BUCKET_NAME')
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
        self.client = None
        self.bucket = None
        self.use_cloud = False  # Will be set to True only if cloud storage is properly initialized
        
        if not CLOUD_STORAGE_AVAILABLE:
            raise Exception("Google Cloud Storage not available - install google-cloud-storage package")
        
        if not self.bucket_name:
            raise Exception("GCS_BUCKET_NAME environment variable not set")
        
        if not self.project_id:
            raise Exception("GOOGLE_CLOUD_PROJECT environment variable not set")
        
        # Force cloud storage only - no local fallback
        if CLOUD_STORAGE_AVAILABLE and self.bucket_name:
            try:
                # Check if we have service account credentials in environment variable
                credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
                credentials_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
                if credentials_json:
                    # Use credentials from environment variable
                    import json
                    from google.oauth2 import service_account
                    
                    try:
                        credentials_info = json.loads(credentials_json)
                        credentials = service_account.Credentials.from_service_account_info(credentials_info)
                        self.client = storage.Client(project=self.project_id, credentials=credentials)
                        logger.info("[OK] Cloud Storage initialized with service account credentials from environment")
                    except Exception as e:
                        logger.error(f"[ERROR] Failed to parse service account credentials from environment: {e}")
                        # Fall back to default authentication
                        self.client = storage.Client(project=self.project_id)
                else:
                    # If GOOGLE_APPLICATION_CREDENTIALS not set, try to locate a default key file
                    if not credentials_file:
                        default_key_paths = [
                            os.path.join(os.getcwd(), 'service-account-key.json'),
                            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'service-account-key.json'))
                        ]
                        for candidate in default_key_paths:
                            if os.path.exists(candidate):
                                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = candidate
                                credentials_file = candidate
                                logger.info(f"[KEY] Using discovered service account file: {candidate}")
                                break
                    
                    # Initialize client with discovered or environment-provided credentials file if present
                    if credentials_file and os.path.exists(credentials_file):
                        try:
                            from google.oauth2 import service_account
                            credentials = service_account.Credentials.from_service_account_file(credentials_file)
                            self.client = storage.Client(project=self.project_id, credentials=credentials)
                            logger.info("[OK] Cloud Storage initialized with service account file")
                        except Exception as e:
                            logger.error(f"[ERROR] Failed to initialize with service account file: {e}")
                            self.client = storage.Client(project=self.project_id)
                    else:
                        # Use default authentication chain (ADC)
                        self.client = storage.Client(project=self.project_id)
                
                self.bucket = self.client.bucket(self.bucket_name)
                logger.info(f"[OK] Cloud Storage initialized with bucket: {self.bucket_name}")
            except Exception as e:
                logger.error(f"[ERROR] Failed to initialize Cloud Storage: {e}")
                self.client = None
                self.bucket = None

    def _normalize_path(self, path: str) -> str:
        """Normalize blob path to use forward slashes for GCS."""
        if path is None:
            return path
        normalized = path.replace("\\", "/")
        # Collapse duplicate slashes (but keep leading if any were present)
        while "//" in normalized:
            normalized = normalized.replace("//", "/")
        # Remove any leading slash to avoid root-style names
        if normalized.startswith("/"):
            normalized = normalized[1:]
        return normalized
    
    def is_available(self) -> bool:
        """Check if cloud storage is available and configured"""
        return CLOUD_STORAGE_AVAILABLE and self.client is not None and self.bucket is not None
    
    def save_file(self, filepath: str, data: Any) -> bool:
        """Save data to cloud storage"""
        if not self.is_available():
            raise Exception(f"Cloud storage not available - cannot save {filepath}")
        
        try:
            normalized = self._normalize_path(filepath)
            blob = self.bucket.blob(normalized)
            
            # Sanitize data to remove problematic Unicode characters
            sanitized_data = sanitize_unicode_for_encoding(data)
            
            if isinstance(sanitized_data, (dict, list)):
                # Use ensure_ascii=True to avoid any Unicode encoding issues
                json_data = json.dumps(sanitized_data, indent=2, default=str, ensure_ascii=True)
                blob.upload_from_string(json_data, content_type='application/json')
            else:
                # Ensure string data is safe for encoding
                safe_string = str(sanitized_data)
                # Try to encode as ASCII first, fall back to Latin-1 if needed
                try:
                    safe_string.encode('ascii')
                    blob.upload_from_string(safe_string, content_type='text/plain')
                except UnicodeEncodeError:
                    # If ASCII fails, use Latin-1 which maps to Windows charmap
                    blob.upload_from_string(safe_string.encode('latin-1', errors='ignore').decode('latin-1'), 
                                          content_type='text/plain')
            
            logger.info(f"[OK] Saved to cloud storage: {normalized}")
            return True
        except Exception as e:
            logger.error(f"[ERROR] Failed to save to cloud storage {filepath}: {e}")
            return False
    
    def load_file(self, filepath: str, default: Any = None) -> Any:
        """Load data from cloud storage"""
        if not self.is_available():
            raise Exception(f"Cloud storage not available - cannot load {filepath}")
        
        try:
            normalized = self._normalize_path(filepath)
            blob = self.bucket.blob(normalized)
            if not blob.exists():
                logger.info(f"[NOT FOUND] File not found in cloud storage: {normalized}")
                return default
            
            # Explicitly specify UTF-8 encoding when downloading
            content = blob.download_as_text(encoding='utf-8')
            if normalized.endswith('.json'):
                return json.loads(content)
            else:
                return content
                
        except NotFound:
            logger.info(f"[NOT FOUND] File not found in cloud storage: {normalized}")
            return default
        except Exception as e:
            logger.error(f"[ERROR] Failed to load from cloud storage {filepath}: {e}")
            return default
    
    def delete_file(self, filepath: str) -> bool:
        """Delete file from cloud storage"""
        if not self.is_available():
            raise Exception(f"Cloud storage not available - cannot delete {filepath}")
        
        try:
            normalized = self._normalize_path(filepath)
            blob = self.bucket.blob(normalized)
            if blob.exists():
                blob.delete()
                logger.info(f"[DELETE] Deleted from cloud storage: {normalized}")
                return True
            return False
        except Exception as e:
            logger.error(f"[ERROR] Failed to delete from cloud storage {filepath}: {e}")
            return False
    
    def list_files(self, prefix: str = "") -> List[str]:
        """List files in cloud storage with optional prefix"""
        if not self.is_available():
            return []
        
        try:
            normalized = self._normalize_path(prefix) if prefix else prefix
            blobs = self.bucket.list_blobs(prefix=normalized)
            return [blob.name for blob in blobs]
        except Exception as e:
            logger.error(f"[ERROR] Failed to list files in cloud storage: {e}")
            return []
    
    def file_exists(self, filepath: str) -> bool:
        """Check if file exists in cloud storage"""
        if not self.is_available():
            return False
        
        try:
            normalized = self._normalize_path(filepath)
            blob = self.bucket.blob(normalized)
            return blob.exists()
        except Exception as e:
            logger.error(f"[ERROR] Failed to check file existence {filepath}: {e}")
            return False

class CloudOnlyStorageManager:
    """Cloud-only storage manager - requires Google Cloud Storage to be configured"""
    
    def __init__(self, bucket_name: str = None, project_id: str = None):
        self.cloud_manager = CloudStorageManager(bucket_name, project_id)
        self.use_cloud = self.cloud_manager.is_available()
        
        if self.use_cloud:
            logger.info("[INFO] Using Cloud Storage for data persistence")
        else:
            logger.info("[INFO] Using local file storage (cloud storage not available)")
    
    def save_file(self, filepath: str, data: Any) -> bool:
        """Save file using cloud storage only - no local fallback"""
        if not self.use_cloud:
            raise Exception(f"Cloud storage not available - cannot save {filepath}")
        
        success = self.cloud_manager.save_file(filepath, data)
        if not success:
            raise Exception(f"Failed to save {filepath} to cloud storage")
        
        return True
    
    def load_file(self, filepath: str, default: Any = None) -> Any:
        """Load file using cloud storage only - no local fallback"""
        if not self.use_cloud:
            raise Exception(f"Cloud storage not available - cannot load {filepath}")
        
        data = self.cloud_manager.load_file(filepath, default)
        if data is default and default is None:
            raise Exception(f"Failed to load {filepath} from cloud storage")
        
        return data
    
    def delete_file(self, filepath: str) -> bool:
        """Delete file using cloud storage only - no local fallback"""
        if not self.use_cloud:
            raise Exception(f"Cloud storage not available - cannot delete {filepath}")
        
        success = self.cloud_manager.delete_file(filepath)
        if not success:
            raise Exception(f"Failed to delete {filepath} from cloud storage")
        
        return True
    
    def list_files(self, prefix: str = "") -> List[str]:
        """List files using cloud storage only - no local fallback"""
        if not self.use_cloud:
            raise Exception(f"Cloud storage not available - cannot list files")
        
        files = self.cloud_manager.list_files(prefix)
        if files is None:
            raise Exception(f"Failed to list files from cloud storage")
        
        return files
    
    def file_exists(self, filepath: str) -> bool:
        """Check if file exists using cloud storage only - no local fallback"""
        if not self.use_cloud:
            raise Exception(f"Cloud storage not available - cannot check file existence")
        
        exists = self.cloud_manager.file_exists(filepath)
        if exists is None:
            raise Exception(f"Failed to check existence of {filepath} in cloud storage")
        
        return exists
    


# Global storage manager instance
storage_manager = None

def get_storage_manager() -> CloudOnlyStorageManager:
    """Get the global storage manager instance"""
    global storage_manager
    if storage_manager is None:
        storage_manager = CloudOnlyStorageManager()
    return storage_manager

def init_cloud_storage(bucket_name: str = None, project_id: str = None):
    """Initialize cloud storage with custom configuration"""
    global storage_manager
    storage_manager = CloudOnlyStorageManager(bucket_name, project_id)
    return storage_manager
