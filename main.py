#!/usr/bin/env python3
import sys


def _parse_args(args):
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


def main():
    try:
        from valutatrade_hub.cli.interface import CLIInterface
    except ImportError as e:
        print(f"Ошибка импорта: {e}")
        return 1
    
    cli = CLIInterface()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        args = _parse_args(sys.argv[2:])
        
        command_map = {
            'register': cli.register,
            'login': cli.login,
            'show-portfolio': cli.show_portfolio,
            'get-rate': cli.get_rate,
            'update-rates': cli.update_rates,
            'show-rates': cli.show_rates,
            'buy': cli.buy,
            'sell': cli.sell,
            'help': lambda args: print_help()
        }
        
        if command in command_map:
            command_map[command](args)
        else:
            print(f"Неизвестная команда: {command}")
            print_help()
        return 0
    
    print("Введите команду или 'exit' для выхода")
    print_help()
    print("-" * 50)
    
    while True:
        try:
            user_input = input("Введите команду:").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Выход из программы...")
                break
            
            args_list = user_input.split()
            command = args_list[0]
            
            args_dict = {}
            i = 1
            while i < len(args_list):
                if args_list[i].startswith('--'):
                    key = args_list[i][2:]
                    if i + 1 < len(args_list) and not args_list[i + 1].startswith('--'):
                        args_dict[key] = args_list[i + 1]
                        i += 2
                    else:
                        args_dict[key] = True
                        i += 1
                else:
                    i += 1
            
            command_map = {
                'register': cli.register,
                'login': cli.login,
                'show-portfolio': cli.show_portfolio,
                'get-rate': cli.get_rate,
                'update-rates': cli.update_rates,
                'show-rates': cli.show_rates,
                'buy': cli.buy,
                'sell': cli.sell,
                'help': lambda args: print_help()
            }
            
            if command in command_map:
                command_map[command](args_dict)
            else:
                print(f"Неизвестная команда: {command}")
                print_help()
                
        except KeyboardInterrupt:
            print("\n\nВыход из программы...")
            break
        except EOFError:
            print("\n\nВыход из программы...")
            break
        except Exception as e:
            print(f"Ошибка: {e}")

def print_help():
    print("\nДоступные команды:")
    print("Аутентификация:")
    print("register --username <имя> --password <пароль>")
    print("login --username <имя> --password <пароль>")
    print("Портфель:")
    print("show-portfolio [--base <валюта>]")
    print("Курсы валют:")
    print("update-rates [--source coingecko|exchangerate]")
    print("show-rates [--currency <код>] [--top <число>]")
    print("get-rate --from <валюта> --to <валюта>")
    print("Торговля:")
    print("buy --currency <код> --amount <сумма>")
    print("sell --currency <код> --amount <сумма>")
    print("Система:")
    print("help - показать справку")
    print("exit - выйти из программы")


if __name__ == "__main__":
    sys.exit(main())