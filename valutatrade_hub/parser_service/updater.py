# valutatrade_hub/parser_service/updater.py
import logging
from datetime import datetime
from typing import Dict

from .api_clients import CoinGeckoClient, ExchangeRateApiClient
from .storage import RatesStorage
from .config import ParserConfig

logger = logging.getLogger(__name__)

class RatesUpdater:
    def __init__(self, config: ParserConfig = None):
        self.config = config or ParserConfig()
        self.storage = RatesStorage(
            self.config.RATES_FILE_PATH,
            self.config.HISTORY_FILE_PATH
        )
        self.clients = {
            'coingecko': CoinGeckoClient(self.config),
            'exchangerate': ExchangeRateApiClient(self.config)
        }
    
    def run_update(self, sources: list = None) -> Dict:
        """Запустить обновление курсов"""
        logger.info("Запуск обновления курсов валют")
        
        all_rates = {}
        source_info = {}
        history_entries = []
        timestamp = datetime.now().isoformat()
        
        sources_to_update = sources or list(self.clients.keys())
        
        for source_name in sources_to_update:
            if source_name not in self.clients:
                logger.warning(f"Неизвестный источник: {source_name}")
                continue
            
            try:
                logger.info(f"Получение данных из {source_name}...")
                client = self.clients[source_name]
                rates = client.fetch_rates()
                
                for pair, rate in rates.items():
                    all_rates[pair] = {
                        'rate': rate,
                        'updated_at': timestamp,
                        'source': source_name
                    }
                    
                    from_currency, to_currency = pair.split('_')
                    history_entries.append({
                        'id': f"{pair}_{timestamp}",
                        'from_currency': from_currency,
                        'to_currency': to_currency,
                        'rate': rate,
                        'timestamp': timestamp,
                        'source': source_name
                    })
                
                source_info[source_name] = {
                    'status': 'success',
                    'rates_count': len(rates),
                    'timestamp': timestamp
                }
                logger.info(f"{source_name}: успешно получено {len(rates)} курсов")
                
            except Exception as e:
                logger.error(f"{source_name}: ошибка - {str(e)}")
                source_info[source_name] = {
                    'status': 'error',
                    'error': str(e),
                    'timestamp': timestamp
                }
        
        if all_rates:
            self.storage.save_current_rates(all_rates, source_info)
            self.storage.save_to_history(history_entries)
        
        logger.info(f"Обновление завершено. Всего курсов: {len(all_rates)}")
        return {
            'total_rates': len(all_rates),
            'sources': source_info,
            'timestamp': timestamp
        }