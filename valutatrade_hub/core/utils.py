# valutatrade_hub/core/utils.py
import hashlib
import json
import uuid
from pathlib import Path
from typing import Dict, List


class JSONFileManager:
    
    @staticmethod
    def read_users() -> List[Dict]:
        return JSONFileManager._read_json_list("data/users.json")
    
    @staticmethod
    def write_users(users: List[Dict]):
        JSONFileManager._write_json_list("data/users.json", users)
    
    @staticmethod
    def read_portfolios() -> List[Dict]:
        return JSONFileManager._read_json_list("data/portfolios.json")
    
    @staticmethod
    def write_portfolios(portfolios: List[Dict]):
        JSONFileManager._write_json_list("data/portfolios.json", portfolios)
    
    @staticmethod
    def read_rates() -> Dict:
        return JSONFileManager._read_json_dict("data/rates.json")
    
    @staticmethod
    def write_rates(rates: Dict):
        JSONFileManager._write_json_dict("data/rates.json", rates)
    
    @staticmethod
    def _read_json_list(filepath: str) -> List[Dict]:
        path = Path(filepath)
        if not path.exists():
            return []
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    @staticmethod
    def _write_json_list(filepath: str, data: List[Dict]):
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def _read_json_dict(filepath: str) -> Dict:
        path = Path(filepath)
        if not path.exists():
            return {}
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    @staticmethod
    def _write_json_dict(filepath: str, data: Dict):
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


class PasswordHasher:
    
    @staticmethod
    def hash_password(password: str, salt: str) -> str:
        hash_object = hashlib.sha256()
        salted_password = password + salt
        hash_object.update(salted_password.encode('utf-8'))
        return hash_object.hexdigest()
    
    @staticmethod
    def generate_salt() -> str:
        return str(uuid.uuid4().hex[:8])