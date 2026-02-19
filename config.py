"""
Production Configuration Management
Centralizes all configuration from environment variables and defaults
"""

import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


class Config:
    """Base configuration with sensible defaults"""
    
    # Application settings
    APP_NAME = os.getenv('APP_NAME', 'Predictive Infrastructure Intelligence')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = os.getenv('TESTING', 'False').lower() == 'true'
    
    # Server settings
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', 5000))
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Kubernetes settings
    K8S_NAMESPACE = os.getenv('K8S_NAMESPACE', 'default')
    K8S_KUBECONFIG = os.getenv('KUBECONFIG', None)
    
    # Monitoring settings
    MONITORING_INTERVAL = int(os.getenv('MONITORING_INTERVAL', 3))
    MAX_HISTORY_RECORDS = int(os.getenv('MAX_HISTORY_RECORDS', 1000))
    
    # API settings
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', 30))
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', 4))
    
    # Health check settings
    HEALTH_CHECK_INTERVAL = int(os.getenv('HEALTH_CHECK_INTERVAL', 5))
    HEALTH_CHECK_TIMEOUT = int(os.getenv('HEALTH_CHECK_TIMEOUT', 10))
    
    # Risk detection thresholds
    RISK_THRESHOLD_CRITICAL = float(os.getenv('RISK_THRESHOLD_CRITICAL', 70.0))
    RISK_THRESHOLD_WARNING = float(os.getenv('RISK_THRESHOLD_WARNING', 50.0))
    
    # Feature flags
    ENABLE_ML_PREDICTIONS = os.getenv('ENABLE_ML_PREDICTIONS', 'True').lower() == 'true'
    ENABLE_AUTO_REMEDIATION = os.getenv('ENABLE_AUTO_REMEDIATION', 'False').lower() == 'true'
    ENABLE_EVENT_STREAMING = os.getenv('ENABLE_EVENT_STREAMING', 'False').lower() == 'true'
    
    # Security settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    API_RATE_LIMIT = int(os.getenv('API_RATE_LIMIT', 1000))
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 60))
    
    @classmethod
    def validate_config(cls):
        """Validate critical configuration values"""
        errors = []
        
        if not isinstance(cls.PORT, int) or cls.PORT < 1 or cls.PORT > 65535:
            errors.append(f"Invalid PORT: {cls.PORT}")
        
        if cls.MONITORING_INTERVAL < 1:
            errors.append("MONITORING_INTERVAL must be >= 1")
        
        if cls.RISK_THRESHOLD_CRITICAL < 0 or cls.RISK_THRESHOLD_CRITICAL > 100:
            errors.append("RISK_THRESHOLD_CRITICAL must be 0-100")
        
        if errors:
            logger.error("Configuration validation failed:")
            for error in errors:
                logger.error(f"  - {error}")
            return False
        
        return True
    
    @classmethod
    def get_summary(cls):
        """Get configuration summary for logging"""
        return {
            'app_name': cls.APP_NAME,
            'debug': cls.DEBUG,
            'host': cls.HOST,
            'port': cls.PORT,
            'log_level': cls.LOG_LEVEL,
            'monitoring_interval': cls.MONITORING_INTERVAL,
            'max_history': cls.MAX_HISTORY_RECORDS,
            'k8s_namespace': cls.K8S_NAMESPACE,
            'ml_enabled': cls.ENABLE_ML_PREDICTIONS,
            'auto_remediation': cls.ENABLE_AUTO_REMEDIATION,
        }


class ProductionConfig(Config):
    """Production-specific configuration"""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'WARNING'


class DevelopmentConfig(Config):
    """Development-specific configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """Testing-specific configuration"""
    DEBUG = False
    TESTING = True
    LOG_LEVEL = 'DEBUG'
    MONITORING_INTERVAL = 1


def get_config(env=None):
    """Get configuration object based on environment"""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    
    config_map = {
        'production': ProductionConfig,
        'prod': ProductionConfig,
        'development': DevelopmentConfig,
        'dev': DevelopmentConfig,
        'testing': TestingConfig,
        'test': TestingConfig,
    }
    
    return config_map.get(env.lower(), DevelopmentConfig)


# Load environment variables from .env file
load_dotenv()

# Default config
config = get_config()

logger.info(f"Configuration loaded: {config.__name__}")
if not config.validate_config():
    raise ValueError("Configuration validation failed")
