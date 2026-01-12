class ValutaTradeException(Exception):
    """Базовое исключение для проекта"""
    pass


class InsufficientFundsError(ValutaTradeException):
    def __init__(self, currency_code: str, available: float, required: float):
        self.currency_code = currency_code
        self.available = available
        self.required = required
        super().__init__(
            f"Недостаточно средств: доступно {available:.4f} {currency_code}, "
            f"требуется {required:.4f} {currency_code}"
        )


class CurrencyNotFoundError(ValutaTradeException):
    def __init__(self, currency_code: str):
        self.currency_code = currency_code
        super().__init__(f"Неизвестная валюта '{currency_code}'")


class ApiRequestError(ValutaTradeException):
    def __init__(self, reason: str = "неизвестная ошибка"):
        self.reason = reason
        super().__init__(f"Ошибка при обращении к внешнему API: {reason}")


class WalletNotFoundError(ValutaTradeException):
    def __init__(self, currency_code: str):
        self.currency_code = currency_code
        super().__init__(
            f"У вас нет кошелька '{currency_code}'. "
            f"Добавьте валюту: она создаётся автоматически при первой покупке."
        )