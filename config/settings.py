"""
Configuration management for Skyward Assistable Bundle
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class AssistableAIConfig:
    """Configuration for Assistable AI integration"""
    api_token: str = field(default_factory=lambda: os.getenv("ASSISTABLE_API_TOKEN", ""))
    base_url: str = "https://api.assistable.ai/v2"
    default_model: str = "gpt-4"
    default_temperature: float = 0.7
    default_queue: int = 1
    request_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0


@dataclass
class GoHighLevelConfig:
    """Configuration for GoHighLevel integration"""
    api_key: str = field(default_factory=lambda: os.getenv("GHL_API_KEY", ""))
    client_id: str = field(default_factory=lambda: os.getenv("GHL_CLIENT_ID", ""))
    client_secret: str = field(default_factory=lambda: os.getenv("GHL_CLIENT_SECRET", ""))
    base_url: str = "https://services.leadconnectorhq.com"
    api_version: str = "2021-07-28"
    default_location_id: str = field(default_factory=lambda: os.getenv("DEFAULT_LOCATION_ID", ""))
    request_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0


@dataclass
class RuntimeHooksConfig:
    """Configuration for runtime hooks system"""
    max_hooks: int = field(default_factory=lambda: int(os.getenv("MAX_HOOKS", "100")))
    retention_minutes: int = field(default_factory=lambda: int(os.getenv("HOOK_RETENTION_MINUTES", "60")))
    real_time_updates: bool = field(default_factory=lambda: os.getenv("REAL_TIME_HOOKS", "true").lower() == "true")
    auto_cleanup: bool = field(default_factory=lambda: os.getenv("AUTO_CLEANUP_HOOKS", "true").lower() == "true")
    enable_metrics: bool = field(default_factory=lambda: os.getenv("ENABLE_METRICS", "true").lower() == "true")


@dataclass
class BatchProcessingConfig:
    """Configuration for batch processing operations"""
    default_batch_size: int = field(default_factory=lambda: int(os.getenv("BATCH_SIZE_DEFAULT", "10")))
    default_delay_between_batches: int = field(default_factory=lambda: int(os.getenv("BATCH_DELAY_DEFAULT", "2")))
    max_concurrent_requests: int = field(default_factory=lambda: int(os.getenv("CONCURRENT_REQUESTS_MAX", "5")))
    timeout_per_item: int = field(default_factory=lambda: int(os.getenv("BATCH_TIMEOUT_PER_ITEM", "30")))
    stop_on_error: bool = field(default_factory=lambda: os.getenv("BATCH_STOP_ON_ERROR", "false").lower() == "true")


@dataclass
class AgentDelegationConfig:
    """Configuration for agent delegation system"""
    default_delegation_mode: str = "auto_detect"
    confidence_threshold: float = 0.3
    crm_keywords: list = field(default_factory=lambda: [
        'assistant', 'ai call', 'contact', 'gohighlevel', 'ghl', 
        'conversation', 'lead', 'crm', 'customer', 'phone',
        'message', 'create assistant', 'make call', 'update contact',
        'calling campaign', 'bulk call', 'leads', 'sales'
    ])
    natural_keywords: list = field(default_factory=lambda: [
        'chat', 'talk', 'explain', 'help', 'question', 'general',
        'what is', 'how to', 'can you', 'please help'
    ])


@dataclass
class SecurityConfig:
    """Security configuration"""
    enable_input_validation: bool = True
    enable_rate_limiting: bool = field(default_factory=lambda: os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true")
    rate_limit_per_minute: int = field(default_factory=lambda: int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")))
    enable_audit_logging: bool = field(default_factory=lambda: os.getenv("ENABLE_AUDIT_LOGGING", "true").lower() == "true")
    max_input_length: int = 10000
    allowed_file_types: list = field(default_factory=lambda: ['.json', '.csv', '.txt'])


@dataclass
class PerformanceConfig:
    """Performance and caching configuration"""
    cache_ttl: int = field(default_factory=lambda: int(os.getenv("CACHE_TTL", "300")))
    enable_caching: bool = field(default_factory=lambda: os.getenv("ENABLE_CACHING", "true").lower() == "true")
    max_cache_size: int = 1000
    enable_detailed_logging: bool = field(default_factory=lambda: os.getenv("ENABLE_DETAILED_LOGGING", "false").lower() == "true")
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))


@dataclass
class BundleConfig:
    """Main configuration class combining all sub-configurations"""
    assistable_ai: AssistableAIConfig = field(default_factory=AssistableAIConfig)
    gohighlevel: GoHighLevelConfig = field(default_factory=GoHighLevelConfig)
    runtime_hooks: RuntimeHooksConfig = field(default_factory=RuntimeHooksConfig)
    batch_processing: BatchProcessingConfig = field(default_factory=BatchProcessingConfig)
    agent_delegation: AgentDelegationConfig = field(default_factory=AgentDelegationConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    # Global settings
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    version: str = "1.0.0"
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        self.validate()
    
    def validate(self) -> None:
        """Validate configuration settings"""
        errors = []
        
        # Validate required API credentials
        if not self.assistable_ai.api_token:
            errors.append("ASSISTABLE_API_TOKEN is required")
        
        if not self.gohighlevel.default_location_id:
            errors.append("DEFAULT_LOCATION_ID is required")
        
        # Validate numeric ranges
        if self.batch_processing.default_batch_size <= 0:
            errors.append("Batch size must be positive")
        
        if self.runtime_hooks.max_hooks <= 0:
            errors.append("Max hooks must be positive")
        
        if self.security.rate_limit_per_minute <= 0:
            errors.append("Rate limit must be positive")
        
        # Validate environment
        if self.environment not in ["development", "staging", "production"]:
            errors.append(f"Invalid environment: {self.environment}")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "assistable_ai": {
                "api_token": "***" if self.assistable_ai.api_token else None,
                "base_url": self.assistable_ai.base_url,
                "default_model": self.assistable_ai.default_model,
                "request_timeout": self.assistable_ai.request_timeout
            },
            "gohighlevel": {
                "api_key": "***" if self.gohighlevel.api_key else None,
                "base_url": self.gohighlevel.base_url,
                "default_location_id": self.gohighlevel.default_location_id,
                "request_timeout": self.gohighlevel.request_timeout
            },
            "runtime_hooks": {
                "max_hooks": self.runtime_hooks.max_hooks,
                "retention_minutes": self.runtime_hooks.retention_minutes,
                "real_time_updates": self.runtime_hooks.real_time_updates
            },
            "batch_processing": {
                "default_batch_size": self.batch_processing.default_batch_size,
                "max_concurrent_requests": self.batch_processing.max_concurrent_requests,
                "timeout_per_item": self.batch_processing.timeout_per_item
            },
            "security": {
                "enable_rate_limiting": self.security.enable_rate_limiting,
                "rate_limit_per_minute": self.security.rate_limit_per_minute,
                "enable_audit_logging": self.security.enable_audit_logging
            },
            "performance": {
                "cache_ttl": self.performance.cache_ttl,
                "enable_caching": self.performance.enable_caching,
                "log_level": self.performance.log_level
            },
            "global": {
                "environment": self.environment,
                "debug": self.debug,
                "version": self.version
            }
        }
    
    @classmethod
    def from_environment(cls) -> 'BundleConfig':
        """Create configuration from environment variables"""
        return cls()
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'BundleConfig':
        """Create configuration from dictionary"""
        # This would implement loading from a config dictionary
        # For now, we'll just return from environment
        return cls.from_environment()


# Global configuration instance
config = BundleConfig()


def get_config() -> BundleConfig:
    """Get the global configuration instance"""
    return config


def reload_config() -> BundleConfig:
    """Reload configuration from environment"""
    global config
    config = BundleConfig.from_environment()
    return config


def update_config(**kwargs) -> None:
    """Update configuration values"""
    global config
    
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            # Handle nested configuration updates
            if '.' in key:
                section, setting = key.split('.', 1)
                if hasattr(config, section):
                    section_config = getattr(config, section)
                    if hasattr(section_config, setting):
                        setattr(section_config, setting, value)
    
    config.validate()


def get_environment_info() -> Dict[str, Any]:
    """Get environment information for debugging"""
    return {
        "environment": config.environment,
        "debug": config.debug,
        "version": config.version,
        "assistable_ai_configured": bool(config.assistable_ai.api_token),
        "ghl_configured": bool(config.gohighlevel.api_key),
        "default_location_set": bool(config.gohighlevel.default_location_id),
        "hooks_enabled": config.runtime_hooks.real_time_updates,
        "caching_enabled": config.performance.enable_caching,
        "rate_limiting_enabled": config.security.enable_rate_limiting
    }


def validate_required_settings() -> Dict[str, bool]:
    """Validate that all required settings are configured"""
    return {
        "assistable_api_token": bool(config.assistable_ai.api_token),
        "ghl_api_key": bool(config.gohighlevel.api_key),
        "default_location_id": bool(config.gohighlevel.default_location_id),
        "environment_set": bool(config.environment),
        "valid_batch_size": config.batch_processing.default_batch_size > 0,
        "valid_rate_limit": config.security.rate_limit_per_minute > 0
    }


def get_production_checklist() -> Dict[str, bool]:
    """Get production readiness checklist"""
    return {
        "environment_is_production": config.environment == "production",
        "debug_disabled": not config.debug,
        "api_credentials_set": bool(config.assistable_ai.api_token and config.gohighlevel.api_key),
        "location_configured": bool(config.gohighlevel.default_location_id),
        "rate_limiting_enabled": config.security.enable_rate_limiting,
        "audit_logging_enabled": config.security.enable_audit_logging,
        "caching_enabled": config.performance.enable_caching,
        "detailed_logging_disabled": not config.performance.enable_detailed_logging,
        "reasonable_timeouts": (
            config.assistable_ai.request_timeout >= 30 and 
            config.gohighlevel.request_timeout >= 30
        ),
        "reasonable_batch_sizes": (
            config.batch_processing.default_batch_size <= 20 and
            config.batch_processing.max_concurrent_requests <= 10
        )
    }
