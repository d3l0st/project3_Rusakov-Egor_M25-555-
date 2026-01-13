import os
from dataclasses import dataclass, field
from typing import Tuple, Dict

@dataclass
class ParserConfig:
    EXCHANGERATE_API_KEY: str = "799b0c0edeafa534a54e5798" 
    COINGECKO_API_KEY: str = "CG-5DhVNq6b4K5iaQccYUxJKTTV"
    
    COINGECKO_URL: str = "https://api.coingecko.com/api/v3/simple/price"
    EXCHANGERATE_API_URL: str = "https://v6.exchangerate-api.com/v6"
    
    BASE_CURRENCY: str = "USD"
    
    FIAT_CURRENCIES: Tuple[str, ...] = field(default_factory=lambda: ("EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "RUB", "CNY"))
    CRYPTO_CURRENCIES: Tuple[str, ...] = field(default_factory=lambda: ("BTC", "ETH", "BNB", "ADA", "SOL", "XRP", "DOT", "DOGE"))
    
    CRYPTO_ID_MAP: Dict[str, str] = field(default_factory=lambda: {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "BNB": "binancecoin",
        "ADA": "cardano",
        "SOL": "solana",
        "XRP": "ripple",
        "DOT": "polkadot",
        "DOGE": "dogecoin",
    })
    
    RATES_FILE_PATH: str = "data/rates.json"
    HISTORY_FILE_PATH: str = "data/exchange_rates.json"
    
    REQUEST_TIMEOUT: int = 10
    MAX_RETRIES: int = 3
    UPDATE_INTERVAL_MINUTES: int = 30 
    CACHE_TTL_MINUTES: int = 5
    
    @property
    def coingecko_full_url(self) -> str:
        return f"{self.COINGECKO_URL}"
    
    @property
    def exchangerate_full_url(self) -> str:
        return f"{self.EXCHANGERATE_API_URL}/{self.EXCHANGERATE_API_KEY}/latest/{self.BASE_CURRENCY}"