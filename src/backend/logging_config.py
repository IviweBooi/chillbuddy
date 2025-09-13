# ChillBuddy Backend - Logging Configuration
# Comprehensive logging setup for the mental health chatbot backend

import logging
import logging.config
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import json

# Custom log formatter for structured logging
class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs structured JSON logs for better parsing and analysis.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as structured JSON.
        
        Args:
            record: Log record to format
        
        Returns:
            Formatted log string
        """
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process_id': os.getpid(),
            'thread_id': record.thread
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        
        if hasattr(record, 'endpoint'):
            log_entry['endpoint'] = record.endpoint
        
        if hasattr(record, 'ip_address'):
            log_entry['ip_address'] = record.ip_address
        
        if hasattr(record, 'response_time'):
            log_entry['response_time'] = record.response_time
        
        if hasattr(record, 'status_code'):
            log_entry['status_code'] = record.status_code
        
        return json.dumps(log_entry, ensure_ascii=False)


class SafetyLogFilter(logging.Filter):
    """
    Filter to ensure sensitive information is not logged.
    """
    
    def __init__(self):
        super().__init__()
        self.sensitive_patterns = [
            'password',
            'token',
            'secret',
            'key',
            'auth',
            'session',
            'cookie'
        ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter out log records containing sensitive information.
        
        Args:
            record: Log record to filter
        
        Returns:
            True if record should be logged, False otherwise
        """
        message = record.getMessage().lower()
        
        # Check for sensitive patterns
        for pattern in self.sensitive_patterns:
            if pattern in message:
                # Replace sensitive information with placeholder
                record.msg = record.msg.replace(
                    record.args[0] if record.args else '',
                    '[REDACTED]'
                )
                break
        
        return True


class PerformanceLogFilter(logging.Filter):
    """
    Filter to add performance metrics to log records.
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add performance context to log records.
        
        Args:
            record: Log record to enhance
        
        Returns:
            True (always log the record)
        """
        # Add memory usage information
        try:
            import psutil
            process = psutil.Process()
            record.memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            record.cpu_percent = process.cpu_percent()
        except ImportError:
            # psutil not available
            pass
        
        return True


def create_log_directory(log_dir: str) -> None:
    """
    Create log directory if it doesn't exist.
    
    Args:
        log_dir: Directory path for log files
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)


def get_log_level(env_var: str = 'LOG_LEVEL', default: str = 'INFO') -> int:
    """
    Get log level from environment variable.
    
    Args:
        env_var: Environment variable name
        default: Default log level if env var not set
    
    Returns:
        Log level as integer
    """
    level_str = os.getenv(env_var, default).upper()
    return getattr(logging, level_str, logging.INFO)


def setup_logging(
    app_name: str = 'chillbuddy',
    log_level: Optional[str] = None,
    log_dir: str = 'logs',
    enable_console: bool = True,
    enable_file: bool = True,
    enable_structured: bool = False,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Set up comprehensive logging configuration.
    
    Args:
        app_name: Application name for log files
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        enable_console: Enable console logging
        enable_file: Enable file logging
        enable_structured: Enable structured JSON logging
        max_file_size: Maximum size of log files before rotation
        backup_count: Number of backup files to keep
    """
    # Determine log level
    if log_level is None:
        log_level = get_log_level()
    else:
        log_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create log directory
    if enable_file:
        create_log_directory(log_dir)
    
    # Configure logging
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(funcName)s(): %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'structured': {
                '()': StructuredFormatter
            }
        },
        'filters': {
            'safety_filter': {
                '()': SafetyLogFilter
            },
            'performance_filter': {
                '()': PerformanceLogFilter
            }
        },
        'handlers': {},
        'loggers': {
            '': {  # Root logger
                'level': log_level,
                'handlers': []
            },
            'chillbuddy': {
                'level': log_level,
                'handlers': [],
                'propagate': False
            },
            'werkzeug': {
                'level': logging.WARNING,
                'handlers': [],
                'propagate': True
            },
            'urllib3': {
                'level': logging.WARNING,
                'handlers': [],
                'propagate': True
            }
        }
    }
    
    # Console handler
    if enable_console:
        config['handlers']['console'] = {
            'class': 'logging.StreamHandler',
            'level': log_level,
            'formatter': 'structured' if enable_structured else 'standard',
            'filters': ['safety_filter'],
            'stream': sys.stdout
        }
        config['loggers']['']['handlers'].append('console')
        config['loggers']['chillbuddy']['handlers'].append('console')
    
    # File handlers
    if enable_file:
        # General application log
        config['handlers']['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': log_level,
            'formatter': 'structured' if enable_structured else 'detailed',
            'filters': ['safety_filter', 'performance_filter'],
            'filename': os.path.join(log_dir, f'{app_name}.log'),
            'maxBytes': max_file_size,
            'backupCount': backup_count,
            'encoding': 'utf-8'
        }
        
        # Error log (errors and above only)
        config['handlers']['error_file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': logging.ERROR,
            'formatter': 'structured' if enable_structured else 'detailed',
            'filters': ['safety_filter'],
            'filename': os.path.join(log_dir, f'{app_name}_errors.log'),
            'maxBytes': max_file_size,
            'backupCount': backup_count,
            'encoding': 'utf-8'
        }
        
        # Security log (for safety and security events)
        config['handlers']['security_file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': logging.WARNING,
            'formatter': 'structured' if enable_structured else 'detailed',
            'filename': os.path.join(log_dir, f'{app_name}_security.log'),
            'maxBytes': max_file_size,
            'backupCount': backup_count,
            'encoding': 'utf-8'
        }
        
        config['loggers']['']['handlers'].extend(['file', 'error_file'])
        config['loggers']['chillbuddy']['handlers'].extend(['file', 'error_file'])
        
        # Add security logger
        config['loggers']['chillbuddy.security'] = {
            'level': logging.WARNING,
            'handlers': ['security_file'],
            'propagate': False
        }
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    # Log startup message
    logger = logging.getLogger('chillbuddy')
    logger.info(f"Logging initialized for {app_name}")
    logger.info(f"Log level: {logging.getLevelName(log_level)}")
    logger.info(f"Console logging: {enable_console}")
    logger.info(f"File logging: {enable_file}")
    logger.info(f"Structured logging: {enable_structured}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    return logging.getLogger(f'chillbuddy.{name}')


def log_request(logger: logging.Logger, request_data: Dict[str, Any]) -> None:
    """
    Log HTTP request information.
    
    Args:
        logger: Logger instance
        request_data: Request information dictionary
    """
    logger.info(
        "HTTP Request",
        extra={
            'request_id': request_data.get('request_id'),
            'endpoint': request_data.get('endpoint'),
            'method': request_data.get('method'),
            'ip_address': request_data.get('ip_address'),
            'user_agent': request_data.get('user_agent'),
            'user_id': request_data.get('user_id')
        }
    )


def log_response(logger: logging.Logger, response_data: Dict[str, Any]) -> None:
    """
    Log HTTP response information.
    
    Args:
        logger: Logger instance
        response_data: Response information dictionary
    """
    logger.info(
        "HTTP Response",
        extra={
            'request_id': response_data.get('request_id'),
            'status_code': response_data.get('status_code'),
            'response_time': response_data.get('response_time'),
            'content_length': response_data.get('content_length')
        }
    )


def log_security_event(event_type: str, details: Dict[str, Any]) -> None:
    """
    Log security-related events.
    
    Args:
        event_type: Type of security event
        details: Event details dictionary
    """
    security_logger = logging.getLogger('chillbuddy.security')
    security_logger.warning(
        f"Security Event: {event_type}",
        extra=details
    )


def log_performance_metric(metric_name: str, value: float, context: Dict[str, Any] = None) -> None:
    """
    Log performance metrics.
    
    Args:
        metric_name: Name of the performance metric
        value: Metric value
        context: Additional context information
    """
    perf_logger = logging.getLogger('chillbuddy.performance')
    extra_data = {'metric_name': metric_name, 'metric_value': value}
    
    if context:
        extra_data.update(context)
    
    perf_logger.info(f"Performance Metric: {metric_name} = {value}", extra=extra_data)


def configure_flask_logging(app) -> None:
    """
    Configure Flask application logging.
    
    Args:
        app: Flask application instance
    """
    # Disable Flask's default logging
    app.logger.handlers.clear()
    
    # Use our custom logger
    app.logger = get_logger('flask')
    
    # Set log level based on Flask environment
    if app.config.get('DEBUG'):
        app.logger.setLevel(logging.DEBUG)
    else:
        app.logger.setLevel(logging.INFO)


# Example usage and testing
if __name__ == '__main__':
    # Set up logging for testing
    setup_logging(
        app_name='chillbuddy_test',
        log_level='DEBUG',
        enable_structured=True
    )
    
    # Test different log levels
    logger = get_logger('test')
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    # Test structured logging with extra data
    logger.info(
        "User action performed",
        extra={
            'user_id': 'test_user_123',
            'action': 'login',
            'ip_address': '192.168.1.1'
        }
    )
    
    # Test security logging
    log_security_event('failed_login', {
        'user_id': 'test_user',
        'ip_address': '192.168.1.100',
        'attempts': 3
    })
    
    # Test performance logging
    log_performance_metric('response_time', 0.125, {
        'endpoint': '/api/chat',
        'method': 'POST'
    })
    
    print("Logging test completed. Check the logs directory for output files.")