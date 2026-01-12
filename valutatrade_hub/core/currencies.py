from abc import ABC, abstractmethod
from typing import Dict


class Currency(ABC):    
    def __init__(self, name: str, code: str):
        self._validate_code(code)
        self._validate_name(name)
        
        self._name = name
        self._code = code.upper()
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def code(self) -> str:
        return self._code
    
    def _validate_code(self, code: str) -> None:
        if not code or not isinstance(code, str):
            raise ValueError(f"Код валюты '{code}' должен быть строкой")
        
        code_clean = code.strip()
        if len(code_clean) < 2 or len(code_clean) > 5:
            raise ValueError(f"Код валюты '{code}' должен быть от 2 до 5 символов")
        
        if ' ' in code:
            raise ValueError(f"Код валюты '{code}' не должен содержать пробелы")
    
    def _validate_name(self, name: str) -> None:
        if not name or not isinstance(name, str):
            raise ValueError("Имя валюты должно быть непустой строкой")
        
        if len(name.strip()) == 0:
            raise ValueError("Имя валюты не может быть пустым")
    
    @abstractmethod
    def get_display_info(self) -> str:
        pass
    
    def __str__(self) -> str:
        return f"{self.code} - {self.name}"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', code='{self.code}')"


class FiatCurrency(Currency):    
    def __init__(self, name: str, code: str, issuing_country: str):
        super().__init__(name, code)
        
        if not issuing_country or not isinstance(issuing_country, str):
            raise ValueError("Страна эмиссии должна быть непустой строкой")
        
        self._issuing_country = issuing_country
    
    @property
    def issuing_country(self) -> str:
        return self._issuing_country
    
    def get_display_info(self) -> str:
        return f"[FIAT] {self.code} — {self.name} (Issuing: {self.issuing_country})"
    
    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}(name='{self.name}', "
                f"code='{self.code}', issuing_country='{self.issuing_country}')")


class CryptoCurrency(Currency):    
    def __init__(self, name: str, code: str, algorithm: str, market_cap: float = 0.0):
        super().__init__(name, code)
        
        if not algorithm or not isinstance(algorithm, str):
            raise ValueError("Алгоритм должен быть непустой строкой")
        
        if not isinstance(market_cap, (int, float)):
            raise ValueError("Рыночная капитализация должна быть числом")
        
        self._algorithm = algorithm
        self._market_cap = float(market_cap)
    
    @property
    def algorithm(self) -> str:
        return self._algorithm
    
    @property
    def market_cap(self) -> float:
        return self._market_cap
    
    def get_display_info(self) -> str:
        mcap_formatted = f"{self.market_cap:.2e}" if self.market_cap > 0 else "N/A"
        return f"[CRYPTO] {self.code} — {self.name} (Algo: {self.algorithm}, MCAP: {mcap_formatted})"
    
    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}(name='{self.name}', code='{self.code}', "
                f"algorithm='{self.algorithm}', market_cap={self.market_cap})")


_CURRENCY_REGISTRY: Dict[str, Currency] = {}


def register_currency(currency: Currency) -> None:
    _CURRENCY_REGISTRY[currency.code] = currency


def get_currency(code: str) -> Currency:
    code_upper = code.upper()
    if code_upper not in _CURRENCY_REGISTRY:
        raise ValueError(f"Валюта с кодом '{code}' не найдена")
    return _CURRENCY_REGISTRY[code_upper]


def get_all_currencies() -> Dict[str, Currency]:
    return _CURRENCY_REGISTRY.copy()


def _initialize_currency_registry():
    fiats = [
        FiatCurrency("US Dollar", "USD", "United States"),
        FiatCurrency("Euro", "EUR", "Eurozone"),
        FiatCurrency("British Pound", "GBP", "United Kingdom"),
        FiatCurrency("Japanese Yen", "JPY", "Japan"),
        FiatCurrency("Swiss Franc", "CHF", "Switzerland"),
        FiatCurrency("Canadian Dollar", "CAD", "Canada"),
        FiatCurrency("Australian Dollar", "AUD", "Australia"),
        FiatCurrency("Russian Ruble", "RUB", "Russia"),
        FiatCurrency("Chinese Yuan", "CNY", "China"),
    ]
    
    cryptos = [
        CryptoCurrency("Bitcoin", "BTC", "SHA-256", market_cap=1.12e12),
        CryptoCurrency("Ethereum", "ETH", "Ethash", market_cap=4.2e11),
        CryptoCurrency("Binance Coin", "BNB", "BEP-20", market_cap=8.5e10),
        CryptoCurrency("Cardano", "ADA", "Ouroboros", market_cap=3.2e10),
        CryptoCurrency("Solana", "SOL", "Proof of History", market_cap=7.8e10),
        CryptoCurrency("Ripple", "XRP", "XRP Ledger", market_cap=4.5e10),
        CryptoCurrency("Polkadot", "DOT", "Nominated Proof-of-Stake", market_cap=2.9e10),
        CryptoCurrency("Dogecoin", "DOGE", "Scrypt", market_cap=2.3e10),
    ]
    
    for fiat in fiats:
        register_currency(fiat)
    
    for crypto in cryptos:
        register_currency(crypto)

_initialize_currency_registry()