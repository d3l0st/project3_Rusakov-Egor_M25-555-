# valutatrade_hub/infra/database.py
import json
import os
from pathlib import Path
from typing import Dict, List, Any

class DatabaseManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            from .settings import settings
            self.data_path = settings.get('data_path', 'data')
            self._initialized = True
    
    def _get_path(self, filename: str) -> str:
        return os.path.join(self.data_path, filename)
    
    def read_users(self) -> List[Dict]:
        return self._read_json("users.json", [])
    
    def write_users(self, users: List[Dict]):
        self._write_json("users.json", users)
    
    def read_portfolios(self) -> List[Dict]:
        return self._read_json("portfolios.json", [])
    
    def write_portfolios(self, portfolios: List[Dict]):
        self._write_json("portfolios.json", portfolios)
    
    def read_rates(self) -> Dict:
        return self._read_json("rates.json", {})
    
    def write_rates(self, rates: Dict):
        self._write_json("rates.json", rates)
    
    def _read_json(self, filename: str, default: Any = None) -> Any:
        path = self._get_path(filename)
        if not os.path.exists(path):
            return default if default is not None else {}
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return default if default is not None else {}
    
    def _write_json(self, filename: str, data: Any):
        path = self._get_path(filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

db = DatabaseManager()