# valutatrade_hub/parser_service/api_clients.py
import logging
from abc import ABC, abstractmethod
from typing import Dict

import requests

from ..core.exceptions import ApiRequestError
from .config import ParserConfig

logger = logging.getLogger(__name__)

class BaseApiClient(ABC):

    @abstractmethod
    def fetch_rates(self) -> Dict[str, float]:
        pass

class CoinGeckoClient(BaseApiClient):
    
    def __init__(self, config: ParserConfig):
        self.config = config
    
    def fetch_rates(self) -> Dict[str, float]:
        try:
            crypto_ids = [self.config.CRYPTO_ID_MAP[code] 
                         for code in self.config.CRYPTO_CURRENCIES 
                         if code in self.config.CRYPTO_ID_MAP]
            
            if not crypto_ids:
                return {}
            
            params = {
                'ids': ','.join(crypto_ids),
                'vs_currencies': 'usd'
            }
            
            response = requests.get(
                self.config.COINGECKO_URL,
                params=params,
                timeout=self.config.REQUEST_TIMEOUT
            )
            
            response.raise_for_status()
            data = response.json()
            
            rates = {}
            for code in self.config.CRYPTO_CURRENCIES:
                if code in self.config.CRYPTO_ID_MAP:
                    crypto_id = self.config.CRYPTO_ID_MAP[code]
                    if crypto_id in data and 'usd' in data[crypto_id]:
                        pair = f"{code}_{self.config.BASE_CURRENCY}"
                        rates[pair] = data[crypto_id]['usd']
            
            logger.info(f"CoinGecko: получено {len(rates)} курсов криптовалют")
            return rates
            
        except requests.exceptions.RequestException as e:
            raise ApiRequestError(f"Ошибка CoinGecko API: {str(e)}")

class ExchangeRateApiClient(BaseApiClient):
    def __init__(self, config: ParserConfig):
        self.config = config
    
    def fetch_rates(self) -> Dict[str, float]:
        try:
            url = f"{self.config.EXCHANGERATE_API_URL}/{self.config.EXCHANGERATE_API_KEY}/latest/{self.config.BASE_CURRENCY}" # noqa: E501
            
            response = requests.get(
                url,
                timeout=self.config.REQUEST_TIMEOUT
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('result') != 'success':
                raise ApiRequestError(f"ExchangeRate-API ошибка: {data.get('error-type', 'unknown')}") # noqa: E501
        
            rates = {}
            for currency in self.config.FIAT_CURRENCIES:
                if currency in data.get('conversion_rates', {}):
                    pair = f"{currency}_{self.config.BASE_CURRENCY}"
                    rates[pair] = data['conversion_rates'][currency]
            
            logger.info(f"ExchangeRate-API: получено {len(rates)} курсов фиатных валют")
            return rates
            
        except requests.exceptions.RequestException as e:
            raise ApiRequestError(f"Ошибка ExchangeRate-API: {str(e)}")