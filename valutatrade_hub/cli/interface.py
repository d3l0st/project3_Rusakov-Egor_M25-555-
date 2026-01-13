# valutatrade_hub/cli/interface.py
from typing import Optional
import json
import os
from ..core.usecases import AuthUseCases, ExchangeUseCases, PortfolioUseCases
from ..core.currencies import FiatCurrency, CryptoCurrency, get_currency, get_all_currencies
from valutatrade_hub.parser_service.updater import RatesUpdater
from valutatrade_hub.parser_service.config import ParserConfig
from ..core.exceptions import (  
    InsufficientFundsError,
    CurrencyNotFoundError,
    ApiRequestError,
    ValutaTradeException
)

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
                    parsed[key] = ''
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
                    try:
                        currency_obj = get_currency(wallet['currency'])
                        
                        if isinstance(currency_obj, FiatCurrency):
                            currency_type = "[FIAT]"
                        elif isinstance(currency_obj, CryptoCurrency):
                            currency_type = "[CRYPTO]"
                        else:
                            currency_type = "[?]"
                    except CurrencyNotFoundError:
                        currency_type = "[?]"
                    
                    if wallet['value_in_base'] > 0:
                        print(f"- {currency_type} {wallet['currency']}: {wallet['balance']:.4f}  → {wallet['value_in_base']:.2f} {base_currency}")
                    else:
                        print(f"- {currency_type} {wallet['currency']}: {wallet['balance']:.4f}")
        
            print(f"ИТОГО: {result['total_value']:,.2f} {base_currency}")
            return True
        except Exception as e:
            print(f"Ошибка: {e}")
            return False

    def update_rates(self, args_dict):
        source = args_dict.get('source') 
        
        print("Начало обновления курсов...")
        
        try:
            updater = RatesUpdater()
            
            sources = None
            if source:
                if source not in ['coingecko', 'exchangerate']:
                    print(f"Ошибка: неизвестный источник '{source}'. Используйте 'coingecko' или 'exchangerate'")
                    return False
                sources = [source]
                print(f"Обновление данных только из источника: {source}")
            else:
                print("Обновление данных из всех источников...")
            
            result = updater.run_update(sources)
            
            if result['total_rates'] > 0:
                print(f"\nОбновление завершено успешно!")
                print(f"   Всего курсов обновлено: {result['total_rates']}")
                print(f"   Время обновления: {result['timestamp']}")
                
                for source_name, info in result['sources'].items():
                    if info['status'] == 'success':
                        print(f"{source_name}: {info.get('rates_count', 0)} курсов")
                    else:
                        print(f"{source_name}: ошибка - {info.get('error', 'unknown')}")
            else:
                print("\nОбновление завершено, но курсы не получены")
                print("   Проверьте подключение к интернету и API ключи")
            
            return result['total_rates'] > 0
            
        except ApiRequestError as e:
            print(f"\nОшибка API: {str(e)}")
            print("   Рекомендация: проверьте подключение к сети и API ключи")
            return False
        except Exception as e:
            print(f"\nНеизвестная ошибка при обновлении курсов: {e}")
            return False    
        
    def get_rate(self, args_dict):
        try:
            from_currency = args_dict.get('from', '').upper().strip()
            to_currency = args_dict.get('to', '').upper().strip()
            
            if not from_currency or not to_currency:
                print("Ошибка: требуются --from и --to")
                return False
            try:
                from_currency_obj = get_currency(from_currency)
            except CurrencyNotFoundError:
                print(f"Ошибка: неизвестная валюта '{from_currency}'")
                self._show_currency_help()
                return False
            
            try:
                to_currency_obj = get_currency(to_currency)
            except CurrencyNotFoundError:
                print(f"Ошибка: неизвестная валюта '{to_currency}'")
                self._show_currency_help()
                return False
            
            try:
                rate_info = PortfolioUseCases.get_exchange_rate(from_currency, to_currency)
            except ApiRequestError as e:
                print(f"Ошибка: {str(e)}")
                print("Попробуйте выполнить: update-rates")
                return False
            
            if rate_info:
                print(f"Курс {from_currency}→{to_currency}: {rate_info['rate']} (обновлено: {rate_info['updated_at']})")
                
                if not rate_info.get('is_fresh', True):
                    print(f"Внимание: {rate_info.get('message', 'Данные могут быть устаревшими')}")
                
                reverse_rate = 1 / rate_info['rate'] if rate_info['rate'] != 0 else 0
                print(f"Обратный курс {to_currency}→{from_currency}: {reverse_rate:.8f}")
            else:
                print(f"Курс {from_currency}→{to_currency} недоступен. Повторите попытку позже.")

            return True
        except ValutaTradeException as e:
            print(f"Ошибка: {e}")
            return False
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
        except ValutaTradeException as e:
            print(f"Ошибка: {e}")
            return False
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
        except ValutaTradeException as e:
            print(f"Ошибка: {e}")
            return False
        except Exception as e:
            print(f"Ошибка: {e}")
            return False

    def _show_currency_help(self):
        print("\nПоддерживаемые валюты:")
        
        try:
            config = ParserConfig()
            
            print(f"\nФиатные валюты (база: {config.BASE_CURRENCY}):")
            for fiat in sorted(config.FIAT_CURRENCIES):
                print(f"  {fiat}")
            
            print(f"\nКриптовалюты (база: {config.BASE_CURRENCY}):")
            for crypto in sorted(config.CRYPTO_CURRENCIES):
                print(f"  {crypto}")
            
            print("\nИспользуйте команды:")
            print("  update-rates [--source coingecko|exchangerate] - обновить курсы")
            print("  show-rates [--currency USD] [--top 5] - показать курсы из кэша")
            print("  get-rate --from USD --to EUR - получить конкретный курс")
            
        except Exception:
            try:
                from ..core.currencies import get_all_currencies
                
                all_currencies = get_all_currencies()
                fiats = []
                cryptos = []
                
                for code, currency in all_currencies.items():
                    if isinstance(currency, FiatCurrency):
                        fiats.append(f"{code} - {currency.name}")
                    elif isinstance(currency, CryptoCurrency):
                        cryptos.append(f"{code} - {currency.name}")
                
                if fiats:
                    print("\nФиатные валюты:")
                    for fiat in sorted(fiats):
                        print(f"  {fiat}")
                
                if cryptos:
                    print("\nКриптовалюты:")
                    for crypto in sorted(cryptos):
                        print(f"  {crypto}")
                
                print("\nИспользуйте команду: get-rate --from <валюта> --to <валюта>")
                
            except Exception:
                print("Не удалось получить список валют. Проверьте настройки парсера.")
    def show_rates(self, args_dict):
        try:
            if not os.path.exists('data/rates.json'):
                print("Локальный кэш курсов пуст.")
                print("Выполните 'update-rates', чтобы загрузить данные.")
                return False
            
            with open('data/rates.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            currency_filter = args_dict.get('currency', '').upper()
            top_count = args_dict.get('top')
            
            if top_count:
                try:
                    top_count = int(top_count)
                except ValueError:
                    print("Ошибка: параметр --top должен быть числом")
                    return False
            
            pairs = data.get('pairs', {})
            
            if not pairs:
                print("Кэш курсов пуст.")
                print("Выполните 'update-rates', чтобы загрузить данные.")
                return False
            
            filtered_pairs = {}
            for pair, info in pairs.items():
                if currency_filter:
                    from_curr, to_curr = pair.split('_')
                    if from_curr != currency_filter and to_curr != currency_filter:
                        continue
                filtered_pairs[pair] = info
            
            if not filtered_pairs:
                print(f"Курс для '{currency_filter}' не найден в кеше.")
                return False
            
            sorted_pairs = sorted(
                filtered_pairs.items(),
                key=lambda x: x[1]['rate'],
                reverse=True
            )
            
            if top_count:
                sorted_pairs = sorted_pairs[:top_count]
            
            print(f"\nКурсы валют из кэша (обновлено: {data.get('last_refresh')}):")
            print("=" * 60)
            
            for pair, info in sorted_pairs:
                from_curr, to_curr = pair.split('_')
                print(f"  {from_curr} → {to_curr}:")
                print(f"    Курс: {info['rate']:.6f}")
                print(f"    Обновлен: {info['updated_at']}")
                print(f"    Источник: {info['source']}")
                print("-" * 40)
            
            print(f"Всего курсов: {len(sorted_pairs)}")
            return True
            
        except json.JSONDecodeError:
            print("Ошибка чтения файла с курсами. Файл поврежден.")
            return False
        except Exception as e:
            print(f"Ошибка при отображении курсов: {e}")
            return False