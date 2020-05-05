from google.cloud import storage

class StorageManager:
    """Manage GCS buckets on GCP"""
    
    def __init__(self):
        """Create a StorageManager object"""
        self.gcs = storage.Client()

    def all_buckets(self):
        """Return all bucktes"""
        return self.gcs.list_buckets()