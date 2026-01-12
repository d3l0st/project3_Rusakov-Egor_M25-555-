# valutatrade_hub/core/usecases.py
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from .models import Portfolio, User, Wallet
from .utils import JSONFileManager, PasswordHasher
from .currencies import get_currency


class AuthUseCases:
    
    @staticmethod
    def register(username: str, password: str) -> Dict[str, Any]:
        """
        Регистрация нового пользователя 
        1. Проверить уникальность username в users.json
        2. Сгенерировать user_id (автоинкремент)
        3. Захешировать пароль с солью
        4. Сохранить пользователя в users.json
        5. Создать пустой портфель в portfolios.json
        6. Вернуть сообщение об успехе
        """
        if not username or not username.strip():
            raise ValueError("Имя пользователя не может быть пустым")
        
        username = username.strip()
        
        users = JSONFileManager.read_users()
        for user in users:
            if user['username'] == username:
                raise ValueError(f"Имя пользователя '{username}' уже занято")
        
        if len(password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов")
        
        user_id = 1
        if users:
            user_id = max(user['user_id'] for user in users) + 1
        
        salt = PasswordHasher.generate_salt()
        hashed_password = PasswordHasher.hash_password(password, salt)
        
        user_data = {
            "user_id": user_id,
            "username": username,
            "hashed_password": hashed_password,
            "salt": salt,
            "registration_date": datetime.now().isoformat()
        }
        
        users.append(user_data)
        JSONFileManager.write_users(users)
        
        portfolios = JSONFileManager.read_portfolios()
        
        portfolio_exists = any(p['user_id'] == user_id for p in portfolios)
        
        if not portfolio_exists:
            portfolio_data = {
                "user_id": user_id,
                "wallets": {}
            }
            portfolios.append(portfolio_data)
            JSONFileManager.write_portfolios(portfolios)
        
        return {
            "success": True,
            "message": f"Пользователь '{username}' зарегистрирован (id={user_id}). Войдите: login --username {username} --password ****",
            "user_id": user_id,
            "username": username
        }
    
    @staticmethod
    def login(username: str, password: str) -> Optional[Dict[str, Any]]:
        users = JSONFileManager.read_users()
        
        for user_data in users:
            if user_data['username'] == username:
                reg_date = datetime.fromisoformat(user_data['registration_date'])
                user = User(
                    user_id=user_data['user_id'],
                    username=user_data['username'],
                    hashed_password=user_data['hashed_password'],
                    salt=user_data['salt'],
                    registration_date=reg_date
                )
                
                if user.verify_password(password):
                    return {
                        "user_id": user.user_id,
                        "username": user.username,
                        "user_object": user
                    }
        
        return None


class PortfolioUseCases:

    @staticmethod
    def show_portfolio(user_id: int, base_currency: str = 'USD') -> Dict:
        portfolio = PortfolioUseCases._load_portfolio(user_id)
        
        rates = JSONFileManager.read_rates()
        
        wallets_info = []
        for currency_code, wallet in portfolio._wallets.items():
            if currency_code == base_currency:
                value_in_base = wallet.balance
            else:
                pair = f"{currency_code}_{base_currency}"
                if pair in rates:
                    rate = rates[pair]['rate']
                    value_in_base = wallet.balance * rate
                else:
                    value_in_base = 0  
            
            wallets_info.append({
                'currency': currency_code,
                'balance': wallet.balance,
                'value_in_base': value_in_base
            })
        
        total_value = portfolio.get_total_value(base_currency)
        
        return {
            "user_id": user_id,
            "wallets": wallets_info,
            "total_value": total_value,
            "base_currency": base_currency
        }
    
    @staticmethod
    def _save_portfolio(portfolio: Portfolio):
        portfolios_data = JSONFileManager.read_portfolios()
        
        portfolio_dict = {
            "user_id": portfolio._user_id,
            "wallets": {}
        }
        
        for currency_code, wallet in portfolio._wallets.items():
            portfolio_dict["wallets"][currency_code] = wallet.get_balance_info()
        
        found = False
        for i, p in enumerate(portfolios_data):
            if p['user_id'] == portfolio._user_id:
                portfolios_data[i] = portfolio_dict
                found = True
                break
        
        if not found:
            portfolios_data.append(portfolio_dict)
        
        JSONFileManager.write_portfolios(portfolios_data)
    
    @staticmethod
    def _load_portfolio(user_id: int) -> Portfolio:
        portfolios_data = JSONFileManager.read_portfolios()
    
        for portfolio_data in portfolios_data:
            if portfolio_data['user_id'] == user_id:
                wallets = {}
                for currency_code, wallet_info in portfolio_data['wallets'].items():
                    wallets[currency_code] = Wallet(currency_code, wallet_info['balance'])
                return Portfolio(user_id, wallets)
    
        return Portfolio(user_id, {})

    @staticmethod
    def get_exchange_rate(from_currency: str, to_currency: str) -> Optional[Dict]:
        rates = JSONFileManager.read_rates()
        pair = f"{from_currency}_{to_currency}"
        
        if pair in rates:
            rate_data = rates[pair]
            updated_at = datetime.fromisoformat(rate_data['updated_at'])
            
            if datetime.now() - updated_at < timedelta(minutes=5):
                return {
                    "from": from_currency,
                    "to": to_currency,
                    "rate": rate_data['rate'],
                    "updated_at": rate_data['updated_at'],
                    "is_fresh": True
                }
            else:
                return {
                    "from": from_currency,
                    "to": to_currency,
                    "rate": rate_data['rate'],
                    "updated_at": rate_data['updated_at'],
                    "is_fresh": False,
                    "message": "Данные могут быть устаревшими"
                }
        
        return None

    
class ExchangeUseCases:
    
    @staticmethod
    def buy_currency(user_id: int, currency_code: str, amount: float) -> Dict:
        try:
            currency_obj = get_currency(currency_code)  
        except ValueError as e:
            return {
                "success": False,
                "error": f"Неверный код валюты: {currency_code}. {e}"
            }
        
        portfolio = PortfolioUseCases._load_portfolio(user_id)
    
        rates = JSONFileManager.read_rates()
        pair = f"{currency_code}_USD"
    
        if pair not in rates:
            return {
                "success": False,
                "error": f"Не удалось получить курс для {currency_code}→USD"
            }
    
        rate = rates[pair]['rate']
        cost_usd = amount * rate
    
    
        if 'USD' not in portfolio._wallets:
            portfolio.add_currency('USD')
    
        usd_wallet = portfolio.get_wallet('USD')
    
    
        if usd_wallet.balance < cost_usd:
            return {
                "success": False,
                "error": "Недостаточно средств на USD кошельке"
            }
    
    
        usd_wallet.withdraw(cost_usd)
    
    
        if currency_code not in portfolio._wallets:
            portfolio.add_currency(currency_code)
        target_wallet = portfolio.get_wallet(currency_code)
        target_wallet.deposit(amount)
    
        PortfolioUseCases._save_portfolio(portfolio)
    
        return {
            "success": True,
            "currency": currency_code,
            "amount": amount,
            "new_balance": target_wallet.balance,
            "rate": rate,
            "estimated_cost_usd": cost_usd,
            "usd_spent": cost_usd
        }
    
    @staticmethod
    def sell_currency(user_id: int, currency_code: str, amount: float) -> Dict:
        try:
            currency_obj = get_currency(currency_code)  # Проверяем, что валюта существует
        except ValueError as e:
            return {
                "success": False,
                "error": f"Неверный код валюты: {currency_code}. {e}"
            }
        
        portfolio = PortfolioUseCases._load_portfolio(user_id)

        
        if currency_code not in portfolio._wallets:
            return {
                "success": False,
                "error": f"У вас нет кошелька '{currency_code}'. Добавьте валюту: она создаётся автоматически при первой покупке."
            }

        wallet = portfolio.get_wallet(currency_code)

        if wallet.balance < amount:
            return {
                "success": False,
                "error": f"Недостаточно средств: доступно {wallet.balance:.4f} {currency_code}, требуется {amount:.4f}"
            }

        old_balance = wallet.balance
        wallet.withdraw(amount)
        new_balance = wallet.balance 

        if currency_code == 'USD':
            PortfolioUseCases._save_portfolio(portfolio)
            return {
                "success": True,
                "currency": currency_code,
                "amount": amount,
                "old_balance": old_balance,
                "new_balance": new_balance,
                "rate": 1.0,
                "revenue_usd": amount
            }

        rates = JSONFileManager.read_rates()
        pair = f"{currency_code}_USD"

        if pair not in rates:
            return {
                "success": False,
                "error": f"Не удалось получить курс для {currency_code}→USD"
            }

        rate = rates[pair]['rate']
        revenue_usd = amount * rate

        if 'USD' not in portfolio._wallets:
            portfolio.add_currency('USD')

        usd_wallet = portfolio.get_wallet('USD')
        usd_wallet.deposit(revenue_usd)

        PortfolioUseCases._save_portfolio(portfolio)

        return {
            "success": True,
            "currency": currency_code,
            "amount": amount,
            "old_balance": old_balance,
            "new_balance": new_balance,
            "rate": rate,
            "revenue_usd": revenue_usd
        }