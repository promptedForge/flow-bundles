"""
Utilities package for Skyward Assistable Bundle

Provides authentication, validation, error handling, and caching utilities
for all components in the bundle.
"""

from .auth_manager import AuthManager, auth_manager, AuthenticationError, TokenExpiredError
from .validators import (
    Validators, ValidationError, InputSanitizer,
    validate_contact_data, validate_assistant_data, validate_api_operation_data
)
from .error_handler import (
    ErrorHandler, error_handler, SkywardError, AuthenticationError as AuthError,
    ValidationError as ValidError, APIError, NetworkError, TimeoutError, RateLimitError,
    handle_errors, log_error, create_user_friendly_error, map_http_error,
    ErrorSeverity, ErrorCategory
)
from .cache_manager import (
    CacheManager, CacheEntry, APIResponseCache, ComputationCache,
    global_cache, api_cache, computation_cache,
    cached, cache_key_from_request, DistributedCacheManager,
    warmup_cache, setup_cache_cleanup
)

__all__ = [
    # Auth Manager
    "AuthManager",
    "auth_manager", 
    "AuthenticationError",
    "TokenExpiredError",
    
    # Validators
    "Validators",
    "ValidationError", 
    "InputSanitizer",
    "validate_contact_data",
    "validate_assistant_data", 
    "validate_api_operation_data",
    
    # Error Handler
    "ErrorHandler",
    "error_handler",
    "SkywardError",
    "AuthError",
    "ValidError", 
    "APIError",
    "NetworkError",
    "TimeoutError",
    "RateLimitError",
    "handle_errors",
    "log_error",
    "create_user_friendly_error",
    "map_http_error",
    "ErrorSeverity",
    "ErrorCategory",
    
    # Cache Manager
    "CacheManager",
    "CacheEntry",
    "APIResponseCache", 
    "ComputationCache",
    "global_cache",
    "api_cache",
    "computation_cache",
    "cached",
    "cache_key_from_request",
    "DistributedCacheManager",
    "warmup_cache",
    "setup_cache_cleanup"
]

__version__ = "1.0.0"
__description__ = "Utilities for Skyward Assistable Bundle - authentication, validation, error handling, and caching"
