"""
Configuration Management System
Centralized configuration for the entire platform
"""

import os
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """Professional configuration management"""
    
    DEFAULT_CONFIG = {
        # System
        'system': {
            'debug_mode': False,
            'logging_level': 'INFO',
            'environment': 'production'
        },
        
        # Monitoring
        'monitoring': {
            'enabled': True,
            'interval_seconds': 3,
            'history_max_records': 10000,
            'demo_degradation_chance': 0.3
        },
        
        # ML/ML
        'ml': {
            'risk_threshold': 0.65,
            'model_type': 'gradient_boosting',
            'update_interval': 300,
            'enable_auto_retraining': True
        },
        
        # Risk Management
        'risk_management': {
            'auto_taint_on_risk': True,
            'auto_migrate_on_risk': True,
            'migration_grace_period': 30,
            'critical_risk_threshold': 0.85
        },
        
        # Health Scoring
        'health_scoring': {
            'cpu_weight': 0.25,
            'memory_weight': 0.25,
            'temperature_weight': 0.20,
            'latency_weight': 0.15,
            'disk_io_weight': 0.15,
            'sla_target': 0.99
        },
        
        # Alerts
        'alerts': {
            'enabled': True,
            'critical_threshold': 0.80,
            'warning_threshold': 0.60,
            'notification_channels': ['log', 'api'],
            'alert_cooldown_minutes': 5
        },
        
        # API
        'api': {
            'host': '0.0.0.0',
            'port': 5000,
            'debug': False,
            'threaded': True,
            'cors_enabled': True,
            'rate_limit_enabled': False
        },
        
        # Analytics
        'analytics': {
            'enabled': True,
            'enable_predictions': True,
            'history_retention_days': 30,
            'export_formats': ['json', 'csv']
        },
        
        # Audit
        'audit': {
            'enabled': True,
            'log_level': 'INFO',
            'max_records': 100000,
            'export_enabled': True
        }
    }
    
    def __init__(self, config_file=None):
        self.config_file = config_file or 'config.json'
        self.config = self.DEFAULT_CONFIG.copy()
        self.load_config()
    
    def load_config(self):
        """Load configuration from file if exists"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    self._merge_configs(self.config, user_config)
                    logger.info(f"✓ Loaded configuration from {self.config_file}")
            except Exception as e:
                logger.warning(f"Error loading config file: {e}, using defaults")
        else:
            logger.info("No config file found, using defaults")
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"✓ Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def get(self, section, key=None):
        """Get configuration value"""
        if key is None:
            return self.config.get(section, {})
        return self.config.get(section, {}).get(key)
    
    def set(self, section, key, value):
        """Set configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        logger.info(f"Configuration updated: {section}.{key} = {value}")
    
    def get_all(self):
        """Get entire configuration"""
        return self.config
    
    def reset_to_defaults(self):
        """Reset to default configuration"""
        self.config = self.DEFAULT_CONFIG.copy()
        logger.info("Configuration reset to defaults")
    
    def validate(self):
        """Validate configuration"""
        errors = []
        
        # Validate thresholds
        ml_config = self.config.get('ml', {})
        if not (0 <= ml_config.get('risk_threshold', 0.65) <= 1):
            errors.append("ML risk_threshold must be between 0 and 1")
        
        # Validate weights sum to 1
        health = self.config.get('health_scoring', {})
        weight_sum = sum([
            health.get('cpu_weight', 0),
            health.get('memory_weight', 0),
            health.get('temperature_weight', 0),
            health.get('latency_weight', 0),
            health.get('disk_io_weight', 0)
        ])
        if not (0.99 <= weight_sum <= 1.01):  # Allow small floating point errors
            errors.append(f"Health scoring weights sum to {weight_sum}, must equal 1.0")
        
        if errors:
            logger.error(f"Configuration validation failed: {errors}")
            return False, errors
        
        logger.info("✓ Configuration validation passed")
        return True, []
    
    def export_config(self, format='json'):
        """Export configuration"""
        if format == 'json':
            return json.dumps(self.config, indent=2)
        elif format == 'dict':
            return self.config
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def __repr__(self):
        return f"ConfigManager({self.config_file})"


# Global config instance
config = ConfigManager()
