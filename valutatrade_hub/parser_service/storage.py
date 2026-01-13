# valutatrade_hub/parser_service/storage.py
import json
import logging
import os
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)

class RatesStorage:
    def __init__(self, rates_file_path: str, history_file_path: str):
        self.rates_file_path = rates_file_path
        self.history_file_path = history_file_path
    
    def save_current_rates(self, rates: Dict[str, Dict], source_info: Dict):
        os.makedirs(os.path.dirname(self.rates_file_path), exist_ok=True)
        
        data = {
            "pairs": rates,
            "last_refresh": datetime.now().isoformat(),
            "source_info": source_info
        }
        
        temp_file = self.rates_file_path + ".tmp"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        os.replace(temp_file, self.rates_file_path)
        logger.info(f"Сохранено {len(rates)} курсов в {self.rates_file_path}")
    
    def save_to_history(self, rates: List[Dict]):
        os.makedirs(os.path.dirname(self.history_file_path), exist_ok=True)
    
        history = self._load_history()
        
        history.extend(rates)
        
        with open(self.history_file_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Добавлено {len(rates)} записей в историю")
    
    def _load_history(self) -> List[Dict]:
        if not os.path.exists(self.history_file_path):
            return []
        
        try:
            with open(self.history_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []