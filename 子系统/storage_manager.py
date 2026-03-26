import json
import os
from pathlib import Path
from datetime import datetime


class StorageManager:
    APP_DATA_DIR = 'PermissionSubSystem'
    DATA_FILE = 'cached_data.json'
    
    def __init__(self):
        self.storage_path = self._get_storage_path()
        self._ensure_storage_dir()
    
    def _get_storage_path(self):
        system_drive = os.environ.get('SystemDrive', 'C:')
        program_data = os.path.join(system_drive, 'ProgramData')
        
        if os.path.exists(program_data) and os.access(program_data, os.W_OK):
            return Path(program_data) / self.APP_DATA_DIR
        
        local_app_data = os.environ.get('LOCALAPPDATA', '')
        if local_app_data and os.path.exists(local_app_data):
            return Path(local_app_data) / self.APP_DATA_DIR
        
        return Path(system_drive) / self.APP_DATA_DIR
    
    def _ensure_storage_dir(self):
        if not self.storage_path.exists():
            self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def get_data_file_path(self):
        return self.storage_path / self.DATA_FILE
    
    def has_cached_data(self):
        data_file = self.get_data_file_path()
        return data_file.exists() and data_file.stat().st_size > 0
    
    def save_data(self, data, data_type, source_file=None):
        data_file = self.get_data_file_path()
        
        cache_data = {
            'cached_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_type': data_type,
            'source_file': str(source_file) if source_file else None,
            'data': data
        }
        
        temp_file = data_file.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        if data_file.exists():
            data_file.unlink()
        
        temp_file.rename(data_file)
        
        return True
    
    def load_cached_data(self):
        data_file = self.get_data_file_path()
        
        if not data_file.exists():
            return None
        
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            return cache_data
        except (json.JSONDecodeError, IOError):
            return None
    
    def clear_cache(self):
        data_file = self.get_data_file_path()
        if data_file.exists():
            data_file.unlink()
        return True
    
    def get_cache_info(self):
        data_file = self.get_data_file_path()
        
        if not data_file.exists():
            return None
        
        try:
            stat = data_file.stat()
            cache_data = self.load_cached_data()
            
            return {
                'file_path': str(data_file),
                'file_size': stat.st_size,
                'modified_time': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'cached_at': cache_data.get('cached_at') if cache_data else None,
                'data_type': cache_data.get('data_type') if cache_data else None,
                'source_file': cache_data.get('source_file') if cache_data else None
            }
        except Exception:
            return None
