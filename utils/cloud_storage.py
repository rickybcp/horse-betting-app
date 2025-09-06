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
        # This regex removes most emojis
        emoji_pattern = re.compile("["
                                   "\U0001F600-\U0001F64F"  # emoticons
                                   "\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   "\U0001F680-\U0001F6FF"  # transport & map symbols
                                   "\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   "\U00002500-\U00002BEF"  # chinese char
                                   "\U00002702-\U000027B0"
                                   "\U00002702-\U000027B0"
                                   "\U000024C2-\U0001F251"
                                   "\U0001f926-\U0001f937"
                                   "\U00010000-\U0010ffff"
                                   "\u2640-\u2642"
                                   "\u2600-\u2B55"
                                   "\u200d"
                                   "\u23cf"
                                   "\u23e9"
                                   "\u2312"
                                   "\ufe0f"  # dingbats
                                   "\u3030"
                                   "]+", flags=re.UNICODE)
        
        # Replace problematic characters with a space or empty string
        sanitized_string = emoji_pattern.sub(r'', data)
        # Ensure it's a valid string after stripping
        return sanitized_string.encode('ascii', 'ignore').decode('ascii')
    else:
        return data


class CloudStorageManager:
    """
    Manages file operations, with a preference for Google Cloud Storage
    and a local file system fallback.
    """

    def __init__(self, bucket_name: Optional[str] = None, project_id: Optional[str] = None):
        self.bucket_name = bucket_name or os.environ.get('GCS_BUCKET_NAME')
        self.project_id = project_id or os.environ.get('GOOGLE_CLOUD_PROJECT')
        self.bucket = None
        self.use_cloud = False
        
        if CLOUD_STORAGE_AVAILABLE and self.bucket_name and self.project_id:
            try:
                self.storage_client = storage.Client(project=self.project_id)
                self.bucket = self.storage_client.bucket(self.bucket_name)
                # Verify that the bucket exists and is accessible
                self.bucket.exists()
                self.use_cloud = True
                logger.info("✓ Google Cloud Storage is available and connected.")
            except Exception as e:
                logger.error(f"❌ Failed to connect to Google Cloud Storage: {e}")
                self.use_cloud = False
        else:
            logger.info("ℹ️ Google Cloud Storage is not available or not configured. Using local file system.")

    def load_file(self, filepath: str, default: Any = None) -> Any:
        """
        Load JSON data from a file, preferring cloud storage over local disk.
        """
        if self.use_cloud:
            return self._load_from_cloud(filepath, default)
        else:
            return self._load_from_local(filepath, default)

    def save_file(self, filepath: str, data: Any) -> bool:
        """
        Save JSON data to a file, preferring cloud storage over local disk.
        """
        # Sanitize data before saving to prevent encoding errors
        sanitized_data = sanitize_unicode_for_encoding(data)
        
        if self.use_cloud:
            return self._save_to_cloud(filepath, sanitized_data)
        else:
            return self._save_to_local(filepath, sanitized_data)

    def list_files(self, prefix: str = "") -> List[str]:
        """
        List files in cloud storage with an optional prefix.
        Returns a list of file paths.
        """
        if not self.use_cloud:
            logger.warning("Cloud storage not available. Cannot list files.")
            return []
        
        try:
            blobs = self.bucket.list_blobs(prefix=prefix)
            file_paths = [blob.name for blob in blobs]
            logger.info(f"✓ Listed {len(file_paths)} files with prefix '{prefix}'.")
            return file_paths
        except Exception as e:
            logger.error(f"❌ Failed to list files from cloud storage: {e}")
            return []

    def file_exists(self, filepath: str) -> bool:
        """
        Check if a file exists in cloud storage.
        """
        if not self.use_cloud:
            return os.path.exists(filepath)
            
        try:
            blob = self.bucket.blob(filepath)
            return blob.exists()
        except Exception as e:
            logger.error(f"❌ Failed to check existence of {filepath} in cloud storage: {e}")
            return False

    def _load_from_cloud(self, filepath: str, default: Any) -> Any:
        """Load from Google Cloud Storage."""
        try:
            blob = self.bucket.blob(filepath)
            if not blob.exists():
                logger.warning(f"File not found in cloud storage: {filepath}")
                return default
            
            json_data = blob.download_as_text()
            logger.info(f"✓ Loaded data from cloud: {filepath}")
            return json.loads(json_data)
        except (NotFound, json.JSONDecodeError) as e:
            logger.error(f"❌ Error loading from cloud {filepath}: {e}")
            return default
        except Exception as e:
            logger.error(f"❌ Unexpected error loading from cloud {filepath}: {e}")
            return default

    def _save_to_cloud(self, filepath: str, data: Any) -> bool:
        """Save to Google Cloud Storage."""
        try:
            blob = self.bucket.blob(filepath)
            json_data = json.dumps(data, indent=2, ensure_ascii=False)
            blob.upload_from_string(json_data, content_type='application/json')
            logger.info(f"✓ Saved data to cloud: {filepath}")
            return True
        except Exception as e:
            logger.error(f"❌ Error saving to cloud {filepath}: {e}")
            return False

    def _load_from_local(self, filepath: str, default: Any) -> Any:
        """Load from local file system."""
        if not os.path.exists(filepath):
            logger.warning(f"File not found locally: {filepath}")
            return default
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                logger.info(f"✓ Loaded data from local file: {filepath}")
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"❌ Error loading from local {filepath}: {e}")
            return default
        except Exception as e:
            logger.error(f"❌ Unexpected error loading from local {filepath}: {e}")
            return default

    def _save_to_local(self, filepath: str, data: Any) -> bool:
        """Save to local file system."""
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"✓ Saved data to local file: {filepath}")
            return True
        except Exception as e:
            logger.error(f"❌ Error saving to local {filepath}: {e}")
            return False

# Global storage manager instance
_storage_manager = None

def get_storage_manager() -> CloudStorageManager:
    """Get the global storage manager instance."""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = CloudStorageManager()
    return _storage_manager

def init_cloud_storage(bucket_name: str = None, project_id: str = None):
    """Initialize cloud storage with custom configuration."""
    global _storage_manager
    _storage_manager = CloudStorageManager(bucket_name, project_id)
