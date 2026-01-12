import functools
import logging
from datetime import datetime
from typing import Callable, Any, Dict, Optional

from .logging_config import get_logger


logger = get_logger(__name__)

def _log_action(logger: logging.Logger, context: Dict, 
                level: int = logging.INFO, exc_info: bool = False) -> None:
    message_parts = [f"Action: {context.get('action', 'UNKNOWN')}"]
    
    if 'user_id' in context:
        message_parts.append(f"user_id={context['user_id']}")
    if 'username' in context:
        message_parts.append(f"username='{context['username']}'")
    if 'currency_code' in context:
        message_parts.append(f"currency='{context['currency_code']}'")
    if 'amount' in context:
        amount = context['amount']
        if isinstance(amount, (int, float)):
            message_parts.append(f"amount={amount:.4f}")
        else:
            message_parts.append(f"amount={amount}")
    if 'rate' in context:
        rate = context['rate']
        if isinstance(rate, (int, float)):
            message_parts.append(f"rate={rate:.2f}")
        else:
            message_parts.append(f"rate={rate}")
    if 'base_currency' in context:
        message_parts.append(f"base={context['base_currency']}")
    
    message = ", ".join(message_parts)
    
    logger.log(level, message, extra=context, exc_info=exc_info)

def log_action(action_name: str, verbose: bool = False):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            context = {
                'action': action_name,
                'timestamp': datetime.now().isoformat(),
                'function': func.__name__
            }
            
            if verbose:
                logger.info(f"Начало выполнения {action_name}")
            
            try:
                result = func(*args, **kwargs)
                _extract_logging_data(context, args, kwargs, result, verbose)
                _log_action(logger, context, logging.INFO)
                return result
                
            except Exception as e:
                context['error'] = str(e)
                context['error_type'] = type(e).__name__
                _log_action(logger, context, logging.ERROR, exc_info=True)
                raise
        
        return wrapper
    return decorator

def _extract_logging_data(context: Dict, args: tuple, kwargs: Dict,  
                        result: Any, verbose: bool) -> None:
    if 'action' in context and context['action'] not in ['REGISTER', 'LOGIN']:
        if 'username' in context:
            del context['username']
    
    action = context.get('action', '')
    
    if action in ['REGISTER', 'LOGIN']:
        if 'username' in kwargs:
            context['username'] = kwargs['username']
        elif args and len(args) > 0 and isinstance(args[0], str):
            context['username'] = args[0]
    
    elif action in ['BUY', 'SELL']:
        if len(args) >= 1:
            context['user_id'] = args[0]
        if len(args) >= 2:
            context['currency_code'] = args[1]
        if len(args) >= 3:
            try:
                context['amount'] = float(args[2])
            except (ValueError, TypeError):
                pass
        
        if 'user_id' in kwargs:
            context['user_id'] = kwargs['user_id']
        if 'currency_code' in kwargs:
            context['currency_code'] = kwargs['currency_code']
        elif 'currency' in kwargs:
            context['currency_code'] = kwargs['currency']
        if 'amount' in kwargs:
            try:
                context['amount'] = float(kwargs['amount'])
            except (ValueError, TypeError):
                pass
    
    elif action == 'GET_RATE':
        if len(args) >= 1:
            context['currency_code'] = args[0]  
        if len(args) >= 2:
            context['base_currency'] = args[1]          
        if 'from_currency' in kwargs:
            context['currency_code'] = kwargs['from_currency']
        if 'to_currency' in kwargs:
            context['base_currency'] = kwargs['to_currency']
        if 'from' in kwargs:
            context['currency_code'] = kwargs['from']
        if 'to' in kwargs:
            context['base_currency'] = kwargs['to']
    
    if result and isinstance(result, dict):
        if 'currency' in result:
            context['currency_code'] = result['currency']
        if 'amount' in result:
            context['amount'] = result['amount']
        if 'rate' in result:
            context['rate'] = result['rate']
        if 'from' in result and 'to' in result:
            context['currency_code'] = result['from']
            context['base_currency'] = result['to']
        if 'base_currency' in result:
            context['base_currency'] = result['base_currency']
        if 'new_balance' in result:
            context['new_balance'] = result['new_balance']
        if 'old_balance' in result:
            context['old_balance'] = result['old_balance']

def log_buy(verbose: bool = False):
    return log_action(action_name='BUY', verbose=verbose)


def log_sell(verbose: bool = False):
    return log_action(action_name='SELL', verbose=verbose)


def log_register(verbose: bool = False):
    return log_action(action_name='REGISTER', verbose=verbose)


def log_login(verbose: bool = False):
    return log_action(action_name='LOGIN', verbose=verbose)


def log_get_rate(verbose: bool = False):
    return log_action(action_name='GET_RATE', verbose=verbose)