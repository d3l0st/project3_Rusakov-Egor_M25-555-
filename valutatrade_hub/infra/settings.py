import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class SettingsLoader:
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsLoader, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._config: Dict[str, Any] = {}
        self._config_path = "data/config.json"
        
        self._load_config()
        self._set_defaults()
        self._initialized = True
    
    def _load_config(self):
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                print(f"Конфигурация загружена из: {self._config_path}")
            except Exception as e:
                print(f"Ошибка загрузки конфигурации: {e}")
    
    def _set_defaults(self):
        defaults = {
            'data_path': 'data',
            'rates_ttl_seconds': 300,
            'default_base_currency': 'USD',
            'log_path': 'logs',
            'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'log_level': 'INFO',
        }
        
        for key, value in defaults.items():
            if key not in self._config:
                self._config[key] = value
    
        self._ensure_directories()
    
    def _ensure_directories(self):
        directories = [
            self.get('data_path', 'data'),
            self.get('log_path', 'logs'),
        ]
        
        for directory in directories:
            if directory:
                os.makedirs(directory, exist_ok=True)
    
    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        self._config[key] = value
    
    def reload(self):
        old_config = self._config.copy()
        self._config = {}
        self._load_config()
        self._set_defaults()
        print("Конфигурация перезагружена")
    
    def get_all(self) -> Dict[str, Any]:
        return self._config.copy()

settings = SettingsLoader()