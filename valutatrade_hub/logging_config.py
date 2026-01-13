import json
import logging
import logging.handlers
import os
from datetime import datetime

from .infra.settings import settings


class JSONFormatter(logging.Formatter):
    """Форматтер для логирования в JSON формате"""
    
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created).isoformat()
        log_data = {
            "timestamp": timestamp,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, 'action'):
            log_data['action'] = record.action
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'username'):
            log_data['username'] = record.username
        if hasattr(record, 'currency_code'):
            log_data['currency_code'] = record.currency_code
        if hasattr(record, 'amount'):
            log_data['amount'] = record.amount
        if hasattr(record, 'rate'):
            log_data['rate'] = record.rate
        if hasattr(record, 'base_currency'):
            log_data['base_currency'] = record.base_currency
        if hasattr(record, 'result'):
            log_data['result'] = record.result
        if hasattr(record, 'error_type'):
            log_data['error_type'] = record.error_type
        if hasattr(record, 'error_message'):
            log_data['error_message'] = record.error_message
        if hasattr(record, 'old_balance'):
            log_data['old_balance'] = record.old_balance
        if hasattr(record, 'new_balance'):
            log_data['new_balance'] = record.new_balance
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
                
        return json.dumps(log_data, ensure_ascii=False)


class TextFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord) -> str:
        record.asctime = self.formatTime(record, self.datefmt)
        message = f"{record.levelname} {record.asctime} {record.name}: {record.getMessage()}"
        
        extra_parts = []
        
        if hasattr(record, 'action'):
            extra_parts.append(f"action={record.action}")
        if hasattr(record, 'user_id'):
            extra_parts.append(f"user_id={record.user_id}")
        if hasattr(record, 'username'):
            extra_parts.append(f"username='{record.username}'")
        if hasattr(record, 'currency_code'):
            extra_parts.append(f"currency='{record.currency_code}'")
        if hasattr(record, 'amount'):
            extra_parts.append(f"amount={record.amount:.4f}")
        if hasattr(record, 'rate'):
            extra_parts.append(f"rate={record.rate:.2f}")
        if hasattr(record, 'base_currency'):
            extra_parts.append(f"base={record.base_currency}")
        if hasattr(record, 'result'):
            extra_parts.append(f"result={record.result}")
        
        if extra_parts:
            message += " [" + ", ".join(extra_parts) + "]"
        
        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"
        
        return message


def setup_logging():
    log_path = settings.get('log_path', 'logs')
    os.makedirs(log_path, exist_ok=True)
    
    log_level_name = settings.get('log_level', 'INFO').upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    
    log_format_type = settings.get('log_format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
    
    logger = logging.getLogger('valutatrade')
    logger.setLevel(log_level)

    logger.handlers.clear()
    
    log_file = os.path.join(log_path, 'actions.log')
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=settings.get('log_rotation_bytes', 1024 * 1024), 
        backupCount=settings.get('log_backup_count', 5),
        encoding='utf-8'
    )
    
    if log_format_type.lower() == 'json':
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    if log_level <= logging.DEBUG:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_formatter = TextFormatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    return logger


logger = setup_logging()


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f'valutatrade.{name}')