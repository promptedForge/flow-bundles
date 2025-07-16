"""
Environment-specific configuration handling
"""

import os
from typing import Dict, Any, Optional
from enum import Enum


class Environment(Enum):
    """Supported environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class EnvironmentConfig:
    """Environment-specific configuration management"""
    
    def __init__(self):
        self.current_env = self._detect_environment()
        self.config = self._load_environment_config()
    
    def _detect_environment(self) -> Environment:
        """Detect current environment from various sources"""
        
        # Check explicit environment variable
        env_str = os.getenv("ENVIRONMENT", "").lower()
        if env_str:
            try:
                return Environment(env_str)
            except ValueError:
                pass
        
        # Check Railway environment
        if os.getenv("RAILWAY_ENVIRONMENT"):
            return Environment.PRODUCTION
        
        # Check other deployment indicators
        if os.getenv("VERCEL_ENV") == "production":
            return Environment.PRODUCTION
        elif os.getenv("VERCEL_ENV") in ["preview", "staging"]:
            return Environment.STAGING
        
        # Check Heroku
        if os.getenv("DYNO"):
            return Environment.PRODUCTION
        
        # Check for development indicators
        if os.getenv("DEBUG", "").lower() == "true":
            return Environment.DEVELOPMENT
        
        # Default to development
        return Environment.DEVELOPMENT
    
    def _load_environment_config(self) -> Dict[str, Any]:
        """Load environment-specific configuration"""
        
        base_config = {
            "api_timeouts": {
                "assistable_ai": 30,
                "gohighlevel": 30
            },
            "batch_processing": {
                "default_size": 10,
                "max_concurrent": 5,
                "delay_between": 2
            },
            "security": {
                "rate_limit_per_minute": 60,
                "enable_audit_logging": True,
                "enable_input_validation": True
            },
            "performance": {
                "cache_ttl": 300,
                "enable_caching": True,
                "enable_metrics": True
            },
            "hooks": {
                "max_hooks": 100,
                "retention_minutes": 60,
                "real_time_updates": True
            }
        }
        
        if self.current_env == Environment.DEVELOPMENT:
            return self._development_config(base_config)
        elif self.current_env == Environment.STAGING:
            return self._staging_config(base_config)
        else:  # Production
            return self._production_config(base_config)
    
    def _development_config(self, base: Dict[str, Any]) -> Dict[str, Any]:
        """Development environment configuration"""
        config = base.copy()
        
        # More relaxed settings for development
        config.update({
            "debug": True,
            "log_level": "DEBUG",
            "api_timeouts": {
                "assistable_ai": 60,  # Longer timeouts for debugging
                "gohighlevel": 60
            },
            "batch_processing": {
                "default_size": 3,  # Smaller batches for testing
                "max_concurrent": 2,
                "delay_between": 1
            },
            "security": {
                "rate_limit_per_minute": 120,  # More permissive
                "enable_audit_logging": False,  # Less logging
                "enable_input_validation": True
            },
            "performance": {
                "cache_ttl": 60,  # Shorter cache for development
                "enable_caching": False,  # Disable for fresh data
                "enable_metrics": True,
                "enable_detailed_logging": True
            },
            "hooks": {
                "max_hooks": 50,  # Smaller buffer
                "retention_minutes": 30,
                "real_time_updates": True
            }
        })
        
        return config
    
    def _staging_config(self, base: Dict[str, Any]) -> Dict[str, Any]:
        """Staging environment configuration"""
        config = base.copy()
        
        # Production-like but with some debugging capabilities
        config.update({
            "debug": False,
            "log_level": "INFO",
            "api_timeouts": {
                "assistable_ai": 45,
                "gohighlevel": 45
            },
            "batch_processing": {
                "default_size": 5,  # Moderate batch sizes
                "max_concurrent": 3,
                "delay_between": 3
            },
            "security": {
                "rate_limit_per_minute": 80,
                "enable_audit_logging": True,
                "enable_input_validation": True
            },
            "performance": {
                "cache_ttl": 180,
                "enable_caching": True,
                "enable_metrics": True,
                "enable_detailed_logging": False
            },
            "hooks": {
                "max_hooks": 75,
                "retention_minutes": 45,
                "real_time_updates": True
            }
        })
        
        return config
    
    def _production_config(self, base: Dict[str, Any]) -> Dict[str, Any]:
        """Production environment configuration"""
        config = base.copy()
        
        # Optimized for performance and reliability
        config.update({
            "debug": False,
            "log_level": "INFO",
            "api_timeouts": {
                "assistable_ai": 30,
                "gohighlevel": 30
            },
            "batch_processing": {
                "default_size": 10,
                "max_concurrent": 5,
                "delay_between": 2
            },
            "security": {
                "rate_limit_per_minute": 60,
                "enable_audit_logging": True,
                "enable_input_validation": True
            },
            "performance": {
                "cache_ttl": 300,
                "enable_caching": True,
                "enable_metrics": True,
                "enable_detailed_logging": False
            },
            "hooks": {
                "max_hooks": 100,
                "retention_minutes": 60,
                "real_time_updates": True
            }
        })
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.current_env == Environment.DEVELOPMENT
    
    def is_staging(self) -> bool:
        """Check if running in staging environment"""
        return self.current_env == Environment.STAGING
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.current_env == Environment.PRODUCTION
    
    def get_environment_name(self) -> str:
        """Get current environment name"""
        return self.current_env.value
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information about environment"""
        return {
            "detected_environment": self.current_env.value,
            "debug_mode": self.get("debug", False),
            "log_level": self.get("log_level", "INFO"),
            "deployment_indicators": {
                "railway": bool(os.getenv("RAILWAY_ENVIRONMENT")),
                "vercel": bool(os.getenv("VERCEL_ENV")),
                "heroku": bool(os.getenv("DYNO")),
                "debug_flag": os.getenv("DEBUG", "").lower() == "true",
                "environment_var": os.getenv("ENVIRONMENT", "not_set")
            },
            "cache_enabled": self.get("performance.enable_caching", True),
            "rate_limiting": self.get("security.rate_limit_per_minute", 60),
            "batch_size": self.get("batch_processing.default_size", 10)
        }
    
    def validate_environment(self) -> Dict[str, bool]:
        """Validate environment configuration"""
        checks = {}
        
        # Check required environment variables
        required_vars = [
            "ASSISTABLE_API_TOKEN",
            "DEFAULT_LOCATION_ID"
        ]
        
        for var in required_vars:
            checks[f"env_var_{var.lower()}"] = bool(os.getenv(var))
        
        # Check environment-specific requirements
        if self.is_production():
            checks.update({
                "production_debug_disabled": not self.get("debug", True),
                "production_caching_enabled": self.get("performance.enable_caching", False),
                "production_audit_logging": self.get("security.enable_audit_logging", False),
                "production_reasonable_timeouts": self.get("api_timeouts.assistable_ai", 0) >= 30
            })
        
        if self.is_development():
            checks.update({
                "development_debug_enabled": self.get("debug", False),
                "development_detailed_logging": self.get("performance.enable_detailed_logging", False)
            })
        
        return checks
    
    def get_recommended_settings(self) -> Dict[str, Any]:
        """Get recommended settings for current environment"""
        recommendations = {}
        
        if self.is_development():
            recommendations = {
                "debug": True,
                "log_level": "DEBUG",
                "cache_enabled": False,
                "detailed_logging": True,
                "batch_size": "small (3-5)",
                "rate_limit": "permissive (120/min)",
                "api_timeouts": "extended (60s)"
            }
        elif self.is_staging():
            recommendations = {
                "debug": False,
                "log_level": "INFO",
                "cache_enabled": True,
                "detailed_logging": False,
                "batch_size": "moderate (5-8)",
                "rate_limit": "moderate (80/min)",
                "api_timeouts": "standard (45s)"
            }
        else:  # Production
            recommendations = {
                "debug": False,
                "log_level": "INFO or WARN",
                "cache_enabled": True,
                "detailed_logging": False,
                "batch_size": "optimized (10-15)",
                "rate_limit": "conservative (60/min)",
                "api_timeouts": "standard (30s)",
                "monitoring": "enabled",
                "audit_logging": "enabled"
            }
        
        return recommendations


# Global environment configuration instance
env_config = EnvironmentConfig()


def get_environment_config() -> EnvironmentConfig:
    """Get the global environment configuration instance"""
    return env_config


def reload_environment_config() -> EnvironmentConfig:
    """Reload environment configuration"""
    global env_config
    env_config = EnvironmentConfig()
    return env_config


def is_development() -> bool:
    """Check if running in development"""
    return env_config.is_development()


def is_staging() -> bool:
    """Check if running in staging"""
    return env_config.is_staging()


def is_production() -> bool:
    """Check if running in production"""
    return env_config.is_production()


def get_env_setting(key: str, default: Any = None) -> Any:
    """Get environment-specific setting"""
    return env_config.get(key, default)


def get_current_environment() -> str:
    """Get current environment name"""
    return env_config.get_environment_name()
