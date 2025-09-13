# ChillBuddy Mental Health Chatbot - Configuration Module
#
# This file contains:
# - Application configuration settings
# - Logging configuration
# - Environment-specific settings
# - Database configuration
# - Security settings

import os
import logging
import logging.config
from datetime import timedelta
from typing import Dict, Any

class Config:
    """Base configuration class"""
    
    # Basic Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///chillbuddy.db'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session Configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'chillbuddy:'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Security Configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # CORS Configuration
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = 'memory://'
    RATELIMIT_DEFAULT = '100 per hour'
    RATELIMIT_HEADERS_ENABLED = True
    
    # Application Settings
    MAX_MESSAGE_LENGTH = int(os.environ.get('MAX_MESSAGE_LENGTH', '5000'))
    MAX_CONVERSATION_HISTORY = int(os.environ.get('MAX_CONVERSATION_HISTORY', '50'))
    SESSION_TIMEOUT_HOURS = int(os.environ.get('SESSION_TIMEOUT_HOURS', '24'))
    
    # AI and Safety Settings
    CRISIS_DETECTION_THRESHOLD = float(os.environ.get('CRISIS_DETECTION_THRESHOLD', '0.7'))
    SAFETY_CHECK_ENABLED = os.environ.get('SAFETY_CHECK_ENABLED', 'True').lower() == 'true'
    PROFANITY_FILTER_ENABLED = os.environ.get('PROFANITY_FILTER_ENABLED', 'True').lower() == 'true'
    
    # File Storage
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/chillbuddy.log')
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', '10485760'))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', '5'))
    
    # External API Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
    OPENAI_MAX_TOKENS = int(os.environ.get('OPENAI_MAX_TOKENS', '1000'))
    OPENAI_TEMPERATURE = float(os.environ.get('OPENAI_TEMPERATURE', '0.7'))
    
    # Email Configuration (for alerts)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Crisis Response Configuration
    CRISIS_ALERT_EMAIL = os.environ.get('CRISIS_ALERT_EMAIL')
    CRISIS_HOTLINE_SA = '+27 0800 567 567'  # SADAG Helpline
    CRISIS_SMS_SA = '31393'  # SADAG SMS Line
    
    # Data Retention
    DATA_RETENTION_DAYS = int(os.environ.get('DATA_RETENTION_DAYS', '365'))
    CONVERSATION_RETENTION_DAYS = int(os.environ.get('CONVERSATION_RETENTION_DAYS', '90'))
    LOG_RETENTION_DAYS = int(os.environ.get('LOG_RETENTION_DAYS', '30'))
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    
    # Relaxed security for development
    WTF_CSRF_ENABLED = False
    
    # More verbose logging
    LOG_LEVEL = 'DEBUG'
    
    # Local database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///chillbuddy_dev.db'
    
    # Disable some safety checks for testing
    SAFETY_CHECK_ENABLED = False
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Development-specific initialization
        print("Running in DEVELOPMENT mode")

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    
    # In-memory database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Disable rate limiting for testing
    RATELIMIT_ENABLED = False
    
    # Fast sessions for testing
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=5)
    
    # Minimal logging for testing
    LOG_LEVEL = 'WARNING'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Testing-specific initialization
        import logging
        logging.disable(logging.CRITICAL)

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Strict security
    WTF_CSRF_ENABLED = True
    
    # Production logging
    LOG_LEVEL = 'WARNING'
    
    # Production database (should be set via environment)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:password@localhost/chillbuddy'
    
    # Enable all safety features
    SAFETY_CHECK_ENABLED = True
    PROFANITY_FILTER_ENABLED = True
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Production-specific initialization
        import logging
        from logging.handlers import SMTPHandler, RotatingFileHandler
        
        # Email error handler
        if app.config.get('MAIL_SERVER'):
            auth = None
            if app.config.get('MAIL_USERNAME') and app.config.get('MAIL_PASSWORD'):
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            
            secure = None
            if app.config.get('MAIL_USE_TLS'):
                secure = ()
            
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr=app.config['MAIL_DEFAULT_SENDER'],
                toaddrs=[app.config['CRISIS_ALERT_EMAIL']],
                subject='ChillBuddy Application Error',
                credentials=auth,
                secure=secure
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
        
        # File error handler
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/chillbuddy.log',
            maxBytes=app.config['LOG_MAX_BYTES'],
            backupCount=app.config['LOG_BACKUP_COUNT']
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('ChillBuddy startup')

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Logging Configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'detailed': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'json': {
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'detailed',
            'filename': 'logs/chillbuddy.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'encoding': 'utf8'
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'detailed',
            'filename': 'logs/chillbuddy_errors.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'encoding': 'utf8'
        },
        'security_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'WARNING',
            'formatter': 'json',
            'filename': 'logs/chillbuddy_security.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'encoding': 'utf8'
        }
    },
    'loggers': {
        'chillbuddy': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': False
        },
        'chillbuddy.security': {
            'level': 'WARNING',
            'handlers': ['console', 'security_file'],
            'propagate': False
        },
        'chillbuddy.errors': {
            'level': 'ERROR',
            'handlers': ['console', 'error_file'],
            'propagate': False
        },
        'werkzeug': {
            'level': 'WARNING',
            'handlers': ['console'],
            'propagate': False
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console']
    }
}

def setup_logging(config_name='development'):
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Adjust logging level based on environment
    if config_name == 'development':
        LOGGING_CONFIG['loggers']['chillbuddy']['level'] = 'DEBUG'
        LOGGING_CONFIG['handlers']['console']['level'] = 'DEBUG'
    elif config_name == 'production':
        LOGGING_CONFIG['loggers']['chillbuddy']['level'] = 'INFO'
        LOGGING_CONFIG['handlers']['console']['level'] = 'WARNING'
    elif config_name == 'testing':
        LOGGING_CONFIG['loggers']['chillbuddy']['level'] = 'CRITICAL'
        LOGGING_CONFIG['handlers']['console']['level'] = 'CRITICAL'
    
    # Apply logging configuration
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # Get logger for this module
    logger = logging.getLogger('chillbuddy.config')
    logger.info(f"Logging configured for {config_name} environment")
    
    return logger

def get_config(config_name=None):
    """Get configuration class based on environment"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    return config.get(config_name, config['default'])

def validate_config(config_obj):
    """Validate configuration settings"""
    errors = []
    warnings = []
    
    # Check required settings
    if not config_obj.SECRET_KEY or config_obj.SECRET_KEY == 'dev-secret-key-change-in-production':
        if config_obj.__class__.__name__ == 'ProductionConfig':
            errors.append("SECRET_KEY must be set for production")
        else:
            warnings.append("Using default SECRET_KEY (not suitable for production)")
    
    # Check database configuration
    if not config_obj.SQLALCHEMY_DATABASE_URI:
        errors.append("Database URI must be configured")
    
    # Check external API keys
    if not config_obj.OPENAI_API_KEY:
        warnings.append("OpenAI API key not configured - AI features will be limited")
    
    # Check email configuration for production
    if config_obj.__class__.__name__ == 'ProductionConfig':
        if not config_obj.MAIL_SERVER:
            warnings.append("Email server not configured - error notifications disabled")
        
        if not config_obj.CRISIS_ALERT_EMAIL:
            warnings.append("Crisis alert email not configured")
    
    # Check file permissions
    try:
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Test write permissions
        test_file = 'logs/test_write.tmp'
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
    except Exception as e:
        errors.append(f"Cannot write to logs directory: {e}")
    
    return errors, warnings

def print_config_summary(config_obj):
    """Print configuration summary"""
    print("\n" + "="*50)
    print(f"ChillBuddy Configuration: {config_obj.__class__.__name__}")
    print("="*50)
    
    print(f"Debug Mode: {getattr(config_obj, 'DEBUG', False)}")
    print(f"Testing Mode: {getattr(config_obj, 'TESTING', False)}")
    print(f"Database: {config_obj.SQLALCHEMY_DATABASE_URI[:50]}...")
    print(f"Log Level: {config_obj.LOG_LEVEL}")
    print(f"Safety Checks: {config_obj.SAFETY_CHECK_ENABLED}")
    print(f"Rate Limiting: {config_obj.RATELIMIT_DEFAULT}")
    print(f"Session Timeout: {config_obj.SESSION_TIMEOUT_HOURS} hours")
    print(f"Max Message Length: {config_obj.MAX_MESSAGE_LENGTH} chars")
    
    # Validate and show any issues
    errors, warnings = validate_config(config_obj)
    
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"  ⚠️  {warning}")
    
    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  ❌ {error}")
    
    if not errors and not warnings:
        print("\n✅ Configuration is valid")
    
    print("="*50 + "\n")

# Environment-specific helper functions
def is_development():
    """Check if running in development mode"""
    return os.environ.get('FLASK_ENV', 'development') == 'development'

def is_production():
    """Check if running in production mode"""
    return os.environ.get('FLASK_ENV', 'development') == 'production'

def is_testing():
    """Check if running in testing mode"""
    return os.environ.get('FLASK_ENV', 'development') == 'testing'

def get_version():
    """Get application version"""
    return os.environ.get('APP_VERSION', '1.0.0')

def get_build_info():
    """Get build information"""
    return {
        'version': get_version(),
        'environment': os.environ.get('FLASK_ENV', 'development'),
        'build_date': os.environ.get('BUILD_DATE', 'unknown'),
        'commit_hash': os.environ.get('COMMIT_HASH', 'unknown')
    }