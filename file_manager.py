import os
import time
import threading
from datetime import datetime, timedelta
import logging

class FileManager:
    def __init__(self, upload_folder='uploads', max_file_age_hours=24, post_extraction_minutes=10):
        self.upload_folder = upload_folder
        self.max_file_age_hours = max_file_age_hours
        self.post_extraction_minutes = post_extraction_minutes  # Keep files 10 minutes after extraction
        self.cleanup_interval = 300  # Run cleanup every 5 minutes (more frequent for better UX)
        self.file_registry = {}  # Track uploaded files with timestamps
        
        # Ensure upload directory exists
        os.makedirs(upload_folder, exist_ok=True)
        
        # Start periodic cleanup thread
        self.cleanup_thread = threading.Thread(target=self._periodic_cleanup, daemon=True)
        self.cleanup_thread.start()
        
        # Clean up any existing files on startup
        self.cleanup_old_files()
    
    def register_file(self, filename):
        """Register a new uploaded file with current timestamp."""
        self.file_registry[filename] = {
            'upload_time': datetime.now(),
            'last_activity': datetime.now(),
            'extraction_count': 0
        }
    
    def mark_extracted(self, filename):
        """Update file activity after extraction (keep available for 10 minutes)."""
        if filename in self.file_registry:
            self.file_registry[filename]['last_activity'] = datetime.now()
            self.file_registry[filename]['extraction_count'] += 1
    
    def cleanup_file(self, filename):
        """Clean up a specific file and remove from registry."""
        try:
            file_path = os.path.join(self.upload_folder, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Cleaned up file: {filename}")
            
            # Remove from registry
            if filename in self.file_registry:
                del self.file_registry[filename]
                
            return True
        except Exception as e:
            print(f"Error cleaning up file {filename}: {str(e)}")
            return False
    
    def cleanup_old_files(self):
        """Clean up files based on activity and age."""
        try:
            current_time = datetime.now()
            general_cutoff = current_time - timedelta(hours=self.max_file_age_hours)
            extraction_cutoff = current_time - timedelta(minutes=self.post_extraction_minutes)
            
            # Clean up files from registry
            files_to_remove = []
            for filename, info in self.file_registry.items():
                # If file has been extracted, clean up after 10 minutes from last activity
                if info['extraction_count'] > 0 and info['last_activity'] < extraction_cutoff:
                    files_to_remove.append(filename)
                # If file hasn't been extracted, clean up after 24 hours from upload
                elif info['extraction_count'] == 0 and info['upload_time'] < general_cutoff:
                    files_to_remove.append(filename)
            
            for filename in files_to_remove:
                self.cleanup_file(filename)
            
            # Also clean up any orphaned files in the directory
            if os.path.exists(self.upload_folder):
                for filename in os.listdir(self.upload_folder):
                    file_path = os.path.join(self.upload_folder, filename)
                    if os.path.isfile(file_path):
                        file_age = datetime.now() - datetime.fromtimestamp(os.path.getctime(file_path))
                        # Clean up orphaned files older than 24 hours
                        if file_age > timedelta(hours=self.max_file_age_hours):
                            try:
                                os.remove(file_path)
                                print(f"Cleaned up orphaned file: {filename}")
                            except Exception as e:
                                print(f"Error cleaning up orphaned file {filename}: {str(e)}")
            
            print(f"Cleanup completed. Active files: {len(self.file_registry)}")
            
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
    
    def _periodic_cleanup(self):
        """Run periodic cleanup in background thread."""
        while True:
            time.sleep(self.cleanup_interval)
            self.cleanup_old_files()
    
    def get_file_stats(self):
        """Get statistics about managed files."""
        if not self.file_registry:
            return {
                'total_files': 0,
                'extracted_files': 0,
                'unused_files': 0,
                'total_extractions': 0,
                'oldest_file': None,
                'newest_file': None
            }
        
        extracted_files = [f for f in self.file_registry.values() if f['extraction_count'] > 0]
        total_extractions = sum(f['extraction_count'] for f in self.file_registry.values())
        
        return {
            'total_files': len(self.file_registry),
            'extracted_files': len(extracted_files),
            'unused_files': len(self.file_registry) - len(extracted_files),
            'total_extractions': total_extractions,
            'oldest_file': min([f['upload_time'] for f in self.file_registry.values()]),
            'newest_file': max([f['upload_time'] for f in self.file_registry.values()]),
            'post_extraction_cleanup_minutes': self.post_extraction_minutes,
            'max_file_age_hours': self.max_file_age_hours
        }
    
    def cleanup_all(self):
        """Clean up all managed files (useful for shutdown)."""
        files_to_remove = list(self.file_registry.keys())
        for filename in files_to_remove:
            self.cleanup_file(filename)
        print("All files cleaned up")
    
    def get_file_age(self, filename):
        """Get the age of a file in hours since upload."""
        if filename in self.file_registry:
            age = datetime.now() - self.file_registry[filename]['upload_time']
            return age.total_seconds() / 3600
        return None
    
    def get_file_activity_age(self, filename):
        """Get the age of a file in minutes since last activity."""
        if filename in self.file_registry:
            age = datetime.now() - self.file_registry[filename]['last_activity']
            return age.total_seconds() / 60
        return None 