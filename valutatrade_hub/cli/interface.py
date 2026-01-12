# valutatrade_hub/cli/interface.py
from typing import Optional

from ..core.usecases import AuthUseCases, ExchangeUseCases, PortfolioUseCases


class CLIInterface:
    def __init__(self):
        self.current_user: Optional[dict] = None
    
    def _parse_args(self, args):
        parsed = {}
        i = 0
        while i < len(args):
            if args[i].startswith('--'):
                key = args[i][2:]
                if i + 1 < len(args) and not args[i + 1].startswith('--'):
                    parsed[key] = args[i + 1]
                    i += 2
                else:
                    parsed[key] = True
                    i += 1
            else:
                parsed['command'] = args[i]
                i += 1
        return parsed
    
    def register(self, args_dict):
        try:
            username = args_dict.get('username')
            password = args_dict.get('password')
            
            if not username or not password:
                print("Ошибка: требуются --username и --password")
                return False
            
            result = AuthUseCases.register(username, password)
            print(result['message'])
            return True
        except ValueError as e:
            error_msg = str(e)
            if "уже занято" in error_msg:
                print(f"Имя пользователя '{args_dict.get('username')}' уже занято")
            elif "не короче 4 символов" in error_msg:
                print("Пароль должен быть не короче 4 символов")
            else:
                print(f"Ошибка: {error_msg}")
            return False
    
    def login(self, args_dict):
        try:
            username = args_dict.get('username')
            password = args_dict.get('password')
            
            if not username or not password:
                print("Ошибка: требуются --username и --password")
                return False
            
            user_info = AuthUseCases.login(username, password)
            if user_info:
                self.current_user = user_info
                print(f"Вы вошли как '{username}'")
                return True
            else:
                print("Неверное имя пользователя или пароль")
                return False
        except Exception as e:
            print(f"Ошибка: {e}")
            return False
    
    def show_portfolio(self, args_dict):
        if not self.current_user:
            print("Сначала выполните login")
            return False
        
        base_currency = args_dict.get('base', 'USD').upper()
        
        try:
            result = PortfolioUseCases.show_portfolio(
                self.current_user['user_id'], 
                base_currency
            )
            
            print(f"Портфель пользователя '{self.current_user['username']}' (база: {base_currency}):")
            
            if not result['wallets']:
                print("Портфель пуст")
            else:
                for wallet in result['wallets']:
                    if wallet['value_in_base'] > 0:
                        print(f"- {wallet['currency']}: {wallet['balance']:.4f}  → {wallet['value_in_base']:.2f} {base_currency}")
                    else:
                        print(f"- {wallet['currency']}: {wallet['balance']:.4f}")
            
            print(f"ИТОГО: {result['total_value']:,.2f} {base_currency}")
            return True
            
        except Exception as e:
            print(f"Ошибка: {e}")
            return False
    
    def get_rate(self, args_dict):
        try:
            from_currency = args_dict.get('from', '').upper().strip()
            to_currency = args_dict.get('to', '').upper().strip()
            
            if not from_currency or not to_currency:
                print("Ошибка: требуются --from и --to")
                return False
            
            rate_info = PortfolioUseCases.get_exchange_rate(from_currency, to_currency)
            
            if rate_info:
                print(f"Курс {from_currency}→{to_currency}: {rate_info['rate']} (обновлено: {rate_info['updated_at']})")
                
                reverse_rate = 1 / rate_info['rate'] if rate_info['rate'] != 0 else 0
                print(f"Обратный курс {to_currency}→{from_currency}: {reverse_rate:.8f}")
            else:
                print(f"Курс {from_currency}→{to_currency} недоступен. Повторите попытку позже.")
            
            return True
        except Exception as e:
            print(f"Ошибка: {e}")
            return False
    
    def buy(self, args_dict):
        if not self.current_user:
            print("Сначала выполните login")
            return False
        
        try:
            currency = args_dict.get('currency', '').upper().strip()
            amount_str = args_dict.get('amount', '')
            
            if not currency:
                print("Ошибка: требуется --currency")
                return False
            
            if not amount_str:
                print("Ошибка: требуется --amount")
                return False
            
            try:
                amount = float(amount_str)
            except ValueError:
                print("Ошибка: amount должен быть числом")
                return False
            
            if amount <= 0:
                print("Ошибка: 'amount' должен быть положительным числом")
                return False
            
            result = ExchangeUseCases.buy_currency(
                self.current_user['user_id'],
                currency,
                amount
            )
            
            if result['success']:
                print(f"Покупка выполнена: {amount:.4f} {currency} по курсу {result['rate']} USD/{currency}")
                print("Изменения в портфеле:")
                print(f"- {currency}: было 0.0000 → стало {result['new_balance']:.4f}")
                if result['estimated_cost_usd'] > 0:
                    print(f"Оценочная стоимость покупки: {result['estimated_cost_usd']:.2f} USD")
            else:
                print(f"Ошибка: {result.get('error', 'Неизвестная ошибка')}")
            
            return result['success']
        except Exception as e:
            print(f"Ошибка: {e}")
            return False
    
    def sell(self, args_dict):
        if not self.current_user:
            print("Сначала выполните login")
            return False
        
        try:
            currency = args_dict.get('currency', '').upper().strip()
            amount_str = args_dict.get('amount', '')
            
            if not currency:
                print("Ошибка: требуется --currency")
                return False
            
            if not amount_str:
                print("Ошибка: требуется --amount")
                return False
            
            try:
                amount = float(amount_str)
            except ValueError:
                print("Ошибка: amount должен быть числом")
                return False
            
            if amount <= 0:
                print("Ошибка: сумма должна быть положительной")
                return False
            
            result = ExchangeUseCases.sell_currency(
                self.current_user['user_id'],
                currency,
                amount
            )
            
            if result['success']:
                if currency != 'USD':
                    print(f"Продажа выполнена: {amount:.4f} {currency} по курсу {result['rate']} USD/{currency}")
                    print("Изменения в портфеле:")
                    print(f"- {currency}: было {result['old_balance']:.4f} → стало {result['new_balance']:.4f}")
                    print(f"Оценочная выручка: {result['revenue_usd']:.2f} USD")
                else:
                    print(f"Продажа выполнена: {amount:.4f} {currency}")
                    print("Изменения в портфеле:")
                    print(f"- USD: было {result['old_balance']:.2f} → стало {result['new_balance']:.2f}")
            else:
                print(f"Ошибка: {result.get('error', 'Неизвестная ошибка')}")
        
            return result['success']
        except Exception as e:
            print(f"Ошибка: {e}")
            return False