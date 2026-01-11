import hashlib
from datetime import datetime


class User:
    '''
    user_id: int — уникальный идентификатор пользователя.
    username: str — имя пользователя.
    hashed_password: str — пароль в зашифрованном виде.
    salt: str — уникальная соль для пользователя.
    registration_date: datetime — дата регистрации пользователя.
    Методы класса:
    get_user_info() — выводит информацию о пользователе (без пароля).
    change_password(new_password: str) — изменяет пароль пользователя, с хешированием нового пароля.
    verify_password(password: str) — проверяет введённый пароль на совпадение.
    '''
    
    def __init__(
        self,
        user_id: int,
        username: str,
        password: str,
        hashed_password: str,
        salt: str,
        registration_date: datetime
    ):
        self._user_id = user_id
        self._username = username
        self._hashed_password = hashed_password
        self._salt = salt
        self._registration_date = registration_date


    @property
    def user_id(self) -> int:
        return self._user_id
    
    @property
    def username(self) -> str:
        return self._username
    
    @property
    def hashed_password(self) -> str:
        return self._hashed_password
    
    @property
    def salt(self) -> str:
        return self._salt
    
    @property
    def registration_date(self) -> datetime:
        return self._registration_date
    
    @username.setter
    def username(self, value: str):
        if not value or not value.strip():
            raise ValueError("Имя не может быть пустым")
        self._username = value.strip()
    
    def get_user_info(self):
        """
        Выводит информацию о пользователе (без пароля)
        """
        return {
            "user_id": self._user_id,
            "username": self._username,
            "registration_date": self._registration_date.isoformat()
        }
    
    def change_password(self, new_password: str):
        """
        Изменяет пароль пользователя, с хешированием нового пароля
        """
        if len(new_password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов")
        hash_object = hashlib.sha256()
        salted_password = new_password + self._salt
        hash_object.update(salted_password.encode('utf-8'))
        self._hashed_password = hash_object.hexdigest()
    
    def verify_password(self, password: str):
        """
        Проверяет введённый пароль на совпадение
        """
        hash_object = hashlib.sha256()
        salted_password = password + self._salt
        hash_object.update(salted_password.encode('utf-8'))
        return hash_object.hexdigest() == self._hashed_password

class Wallet:
    '''
    currency_code: str — код валюты (например, "USD", "BTC").
    _balance: float — баланс в данной валюте (по умолчанию 0.0).
    Методы класса:
    deposit(amount: float) — пополнение баланса.
    withdraw(amount: float) — снятие средств (если баланс позволяет).
    get_balance_info() — вывод информации о текущем балансе.  
    '''

    def __init__(
        self,
        currency_code: str,
        balance: float = 0.0,
    ):
        self.currency_code = currency_code
        self._balance = 0.0
        self.balance = balance
    
    @property
    def balance(self) -> float:
        return self._balance
    
    @balance.setter
    def balance(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError('Баланс должен быть числом')
        if value < 0:
            raise ValueError('Баланс не может быть отрицательным')
        
        self._balance = float(value)
    
    def deposit(self, amount: float):
        if not isinstance(amount, (int, float)):
            raise TypeError('Сумма  для пополнения должна быть числом')
        if amount <= 0:
            raise ValueError('Сумма  для пополнения не может быть отрицательной')
        
        self.balance += amount
    
    def withdraw(self, amount: float):
        if not isinstance(amount, (int, float)):
            raise TypeError('Сумма для снятия должна быть числом')
        if amount <= 0:
            raise ValueError('Сумма для сняти не может быть отрицательной')
        if amount > self.balance:
            raise ValueError('Недостаточно средств на балансе')
        
        self.balance -= amount
    
    def get_balance_info(self):
        return {
            "currency_code": self.currency_code,
            "balance": self._balance
        }
        
class Portfolio:
    '''
    _user_id: int — уникальный идентификатор пользователя.
    _wallets: dict[str, Wallet] — словарь кошельков, где ключ — код валюты, значение — объект Wallet.
    Методы класса:
    add_currency(currency_code: str) — добавляет новый кошелёк в портфель (если его ещё нет).
    get_total_value(base_currency='USD') — возвращает общую стоимость всех валют пользователя в указанной базовой валюте (по курсам, полученным из API или фиктивным данным).
    get_wallet(currency_code) — возвращает объект Wallet по коду 
    '''
    def __init__(
            self,
            user_id: int,
            wallets: dict[str, Wallet]
    ):
        self._user_id = user_id
        self._wallets = wallets
    
    @property
    def user(self):
        return self._user_id
    
    def wallets(self) -> dict:
        return self._wallets.copy()
    
    def add_currency(self, currency_code: str):
        if currency_code in self._wallets:
            raise ValueError(f'Валюта {currency_code} уже есть в портфеле')
        self._wallets[currency_code] = Wallet(currency_code, 0.0)

    def get_total_value(self, base_currency: str = 'USD'):
        exchange_rates = {
            'USD' : 1.0,
            'EUR' : 1.08,
            'BTC' : 45000.0,
            'ETH' : 2500.0,
            'RUB' : 0.011
        }

        base_currency = base_currency.upper()
        if base_currency not in exchange_rates:
            raise ValueError(f"Неизвестная валюта: {base_currency}")
        
        total_value_usd = 0.0
        for currency_code, wallet in self._wallets.items():
            if currency_code in exchange_rates:
                value_in_usd = wallet.balance * exchange_rates[currency_code]
                total_value_usd += value_in_usd
            else:
                continue
        
        if base_currency == 'USD':
            return round(total_value_usd, 2)
        else:
            value_in_base = total_value_usd / exchange_rates[base_currency]
            return round(value_in_base, 2)
    
    
    def get_wallet(self, currency_code: str):
        if currency_code not in self._wallets:
            raise ValueError(f"Валюта {currency_code} не найдена в портфеле")
        
        return self._wallets[currency_code]

    



    
