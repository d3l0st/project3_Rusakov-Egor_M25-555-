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
        
        if command == 'register':
            cli.register(args)
        elif command == 'login':
            cli.login(args)
        elif command == 'show-portfolio':
            cli.show_portfolio(args)
        elif command == 'get-rate':
            cli.get_rate(args)
        elif command == 'buy':
            cli.buy(args)
        elif command == 'sell':
            cli.sell(args)
        else:
            print(f"Неизвестная команда: {command}")
            print("Используйте: register, login, show-portfolio, get-rate, buy, sell")
        return 0

    print("Введите команду или 'exit' для выхода")
    print("Доступные команды: register, login, show-portfolio, get-rate, buy, sell, help")
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
            
            if command == 'register':
                cli.register(args_dict)
            elif command == 'login':
                cli.login(args_dict)
            elif command == 'show-portfolio':
                cli.show_portfolio(args_dict)
            elif command == 'get-rate':
                cli.get_rate(args_dict)
            elif command == 'buy':
                cli.buy(args_dict)
            elif command == 'sell':
                cli.sell(args_dict)
            elif command == 'help':
                print("\nДоступные команды:")
                print("  register --username <имя пользователя> --password <пароль>")
                print("  login --username <имя пользователя> --password <пароль>")
                print("  show-portfolio [--base <валюта>]")
                print("  get-rate --from <валюта> --to <валюта>")
                print("  buy --currency <код валюты> --amount <сумма>")
                print("  sell --currency <код валюты > --amount <сумма>")
                print("  help - показать данную справку")
                print("  exit - выйти из программы")
            else:
                print(f"Неизвестная команда: {command}")
                print("Используйте 'help' для списка команд")
                
        except KeyboardInterrupt:
            print("\n\nВыход из программы...")
            break
        except EOFError:
            print("\n\nВыход из программы...")
            break
        except Exception as e:
            print(f"Ошибка: {e}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())