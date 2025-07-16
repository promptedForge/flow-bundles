"""
Centralized error handling and logging for Skyward Assistable Bundle

Provides consistent error handling, logging, and recovery mechanisms
across all components with detailed error tracking and reporting.
"""

import traceback
import logging
import json
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum
import uuid
from functools import wraps

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories for classification"""
    AUTHENTICATION = "authentication"
    VALIDATION = "validation"
    API_ERROR = "api_error"
    NETWORK = "network"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    CONFIGURATION = "configuration"
    INTERNAL = "internal"
    USER_INPUT = "user_input"

class SkywardError(Exception):
    """Base exception for Skyward bundle errors"""
    
    def __init__(self, message: str, category: ErrorCategory = ErrorCategory.INTERNAL,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                 details: Optional[Dict[str, Any]] = None,
                 error_code: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.error_code = error_code or f"SKY_{category.value.upper()}_{uuid.uuid4().hex[:8]}"
        self.timestamp = datetime.now().isoformat()

class AuthenticationError(SkywardError):
    """Authentication-related errors"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.AUTHENTICATION, **kwargs)

class ValidationError(SkywardError):
    """Validation-related errors"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.VALIDATION, **kwargs)

class APIError(SkywardError):
    """API-related errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, **kwargs):
        details = kwargs.get('details', {})
        if status_code:
            details['status_code'] = status_code
        super().__init__(message, category=ErrorCategory.API_ERROR, details=details, **kwargs)

class NetworkError(SkywardError):
    """Network-related errors"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.NETWORK, **kwargs)

class TimeoutError(SkywardError):
    """Timeout-related errors"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.TIMEOUT, **kwargs)

class RateLimitError(SkywardError):
    """Rate limiting errors"""
    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        details = kwargs.get('details', {})
        if retry_after:
            details['retry_after'] = retry_after
        super().__init__(message, category=ErrorCategory.RATE_LIMIT, details=details, **kwargs)

class ErrorHandler:
    """Centralized error handling and logging"""
    
    def __init__(self, logger_name: str = "skyward_bundle"):
        self.logger = logging.getLogger(logger_name)
        self.error_history = []
        self.error_callbacks = []
        self.recovery_strategies = {}
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        if not self.logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # File handler
            file_handler = logging.FileHandler('skyward_bundle.log')
            file_handler.setLevel(logging.DEBUG)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)
            
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
            self.logger.setLevel(logging.DEBUG)
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None,
                    component: Optional[str] = None) -> Dict[str, Any]:
        """Handle and log errors with context"""
        
        # Convert to SkywardError if needed
        if not isinstance(error, SkywardError):
            error = self._convert_to_skyward_error(error)
        
        # Create error record
        error_record = {
            "error_id": str(uuid.uuid4()),
            "error_code": error.error_code,
            "message": error.message,
            "category": error.category.value,
            "severity": error.severity.value,
            "details": error.details,
            "timestamp": error.timestamp,
            "component": component,
            "context": context or {},
            "traceback": traceback.format_exc() if error.__traceback__ else None
        }
        
        # Store error
        self.error_history.append(error_record)
        
        # Log error
        self._log_error(error_record)
        
        # Notify callbacks
        self._notify_error_callbacks(error_record)
        
        # Attempt recovery
        recovery_result = self._attempt_recovery(error, context, component)
        if recovery_result:
            error_record["recovery"] = recovery_result
        
        return error_record
    
    def _convert_to_skyward_error(self, error: Exception) -> SkywardError:
        """Convert standard exceptions to SkywardError"""
        
        error_message = str(error)
        
        # Map common exceptions
        if isinstance(error, ConnectionError):
            return NetworkError(error_message, details={"original_type": type(error).__name__})
        
        elif isinstance(error, TimeoutError):
            return TimeoutError(error_message, details={"original_type": type(error).__name__})
        
        elif isinstance(error, ValueError):
            return ValidationError(error_message, details={"original_type": type(error).__name__})
        
        elif isinstance(error, PermissionError):
            return AuthenticationError(error_message, details={"original_type": type(error).__name__})
        
        else:
            return SkywardError(
                error_message,
                category=ErrorCategory.INTERNAL,
                details={"original_type": type(error).__name__}
            )
    
    def _log_error(self, error_record: Dict[str, Any]):
        """Log error based on severity"""
        
        log_message = f"[{error_record['error_code']}] {error_record['message']}"
        
        if error_record['component']:
            log_message = f"[{error_record['component']}] {log_message}"
        
        severity = error_record['severity']
        
        if severity == ErrorSeverity.CRITICAL.value:
            self.logger.critical(log_message, extra=error_record)
        elif severity == ErrorSeverity.HIGH.value:
            self.logger.error(log_message, extra=error_record)
        elif severity == ErrorSeverity.MEDIUM.value:
            self.logger.warning(log_message, extra=error_record)
        else:
            self.logger.info(log_message, extra=error_record)
    
    def _notify_error_callbacks(self, error_record: Dict[str, Any]):
        """Notify registered error callbacks"""
        for callback in self.error_callbacks:
            try:
                callback(error_record)
            except Exception as e:
                self.logger.error(f"Error callback failed: {e}")
    
    def _attempt_recovery(self, error: SkywardError, context: Optional[Dict[str, Any]], 
                         component: Optional[str]) -> Optional[Dict[str, Any]]:
        """Attempt to recover from error using registered strategies"""
        
        recovery_key = f"{error.category.value}_{component}" if component else error.category.value
        
        if recovery_key in self.recovery_strategies:
            try:
                recovery_strategy = self.recovery_strategies[recovery_key]
                return recovery_strategy(error, context)
            except Exception as recovery_error:
                self.logger.error(f"Recovery strategy failed: {recovery_error}")
        
        # Default recovery strategies
        if error.category == ErrorCategory.RATE_LIMIT:
            return self._default_rate_limit_recovery(error, context)
        elif error.category == ErrorCategory.NETWORK:
            return self._default_network_recovery(error, context)
        elif error.category == ErrorCategory.AUTHENTICATION:
            return self._default_auth_recovery(error, context)
        
        return None
    
    def _default_rate_limit_recovery(self, error: SkywardError, 
                                   context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Default recovery for rate limit errors"""
        retry_after = error.details.get('retry_after', 60)
        
        return {
            "strategy": "rate_limit_backoff",
            "retry_after": retry_after,
            "message": f"Rate limited. Retry after {retry_after} seconds."
        }
    
    def _default_network_recovery(self, error: SkywardError, 
                                context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Default recovery for network errors"""
        return {
            "strategy": "exponential_backoff",
            "max_retries": 3,
            "base_delay": 2,
            "message": "Network error. Implementing exponential backoff retry."
        }
    
    def _default_auth_recovery(self, error: SkywardError, 
                              context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Default recovery for authentication errors"""
        return {
            "strategy": "token_refresh",
            "message": "Authentication failed. Attempting token refresh."
        }
    
    def register_error_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Register callback function for error notifications"""
        self.error_callbacks.append(callback)
    
    def register_recovery_strategy(self, category: str, component: Optional[str], 
                                 strategy: Callable[[SkywardError, Optional[Dict[str, Any]]], Dict[str, Any]]):
        """Register recovery strategy for specific error types"""
        key = f"{category}_{component}" if component else category
        self.recovery_strategies[key] = strategy
    
    def get_error_summary(self, last_hours: int = 24) -> Dict[str, Any]:
        """Get error summary for specified time period"""
        
        cutoff_time = datetime.now().replace(
            hour=datetime.now().hour - last_hours
        )
        
        recent_errors = [
            error for error in self.error_history
            if datetime.fromisoformat(error['timestamp']) > cutoff_time
        ]
        
        # Categorize errors
        by_category = {}
        by_severity = {}
        by_component = {}
        
        for error in recent_errors:
            # By category
            category = error['category']
            by_category[category] = by_category.get(category, 0) + 1
            
            # By severity
            severity = error['severity']
            by_severity[severity] = by_severity.get(severity, 0) + 1
            
            # By component
            component = error.get('component', 'unknown')
            by_component[component] = by_component.get(component, 0) + 1
        
        return {
            "time_period_hours": last_hours,
            "total_errors": len(recent_errors),
            "by_category": by_category,
            "by_severity": by_severity,
            "by_component": by_component,
            "most_recent": recent_errors[-1] if recent_errors else None
        }
    
    def clear_error_history(self, older_than_hours: int = 168):  # 1 week default
        """Clear old error history"""
        cutoff_time = datetime.now().replace(
            hour=datetime.now().hour - older_than_hours
        )
        
        self.error_history = [
            error for error in self.error_history
            if datetime.fromisoformat(error['timestamp']) > cutoff_time
        ]

# Decorator for automatic error handling
def handle_errors(component: str = None, 
                 reraise: bool = False,
                 return_on_error: Any = None):
    """Decorator for automatic error handling in functions"""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_record = error_handler.handle_error(
                    e, 
                    context={
                        "function": func.__name__,
                        "args": str(args)[:200],  # Truncate for logging
                        "kwargs": str(kwargs)[:200]
                    },
                    component=component
                )
                
                if reraise:
                    raise
                
                return return_on_error or {"error": error_record}
        
        return wrapper
    return decorator

# Global error handler instance
error_handler = ErrorHandler()

# Convenience functions
def log_error(error: Exception, component: str = None, context: Dict[str, Any] = None):
    """Convenience function to log errors"""
    return error_handler.handle_error(error, context, component)

def create_user_friendly_error(error_record: Dict[str, Any]) -> str:
    """Create user-friendly error message from error record"""
    
    category = error_record.get('category', 'unknown')
    message = error_record.get('message', 'An error occurred')
    
    # Create user-friendly messages based on category
    if category == 'authentication':
        return "Authentication failed. Please check your API tokens and try again."
    
    elif category == 'validation':
        return f"Invalid input: {message}"
    
    elif category == 'api_error':
        status_code = error_record.get('details', {}).get('status_code')
        if status_code == 429:
            return "Service is temporarily busy. Please try again in a few moments."
        elif status_code == 404:
            return "The requested resource was not found."
        else:
            return "An error occurred while communicating with the service."
    
    elif category == 'network':
        return "Network connection failed. Please check your internet connection and try again."
    
    elif category == 'timeout':
        return "The operation timed out. Please try again."
    
    elif category == 'rate_limit':
        retry_after = error_record.get('details', {}).get('retry_after', 60)
        return f"Too many requests. Please wait {retry_after} seconds before trying again."
    
    else:
        return "An unexpected error occurred. Please try again or contact support."

# HTTP status code to error category mapping
def map_http_error(status_code: int, response_text: str = "") -> SkywardError:
    """Map HTTP status codes to appropriate SkywardError"""
    
    if status_code == 401:
        return AuthenticationError("Unauthorized - Invalid or expired token")
    
    elif status_code == 403:
        return AuthenticationError("Forbidden - Insufficient permissions")
    
    elif status_code == 404:
        return APIError(f"Not found - {response_text}", status_code=status_code)
    
    elif status_code == 422:
        return ValidationError(f"Validation failed - {response_text}")
    
    elif status_code == 429:
        return RateLimitError("Rate limit exceeded", details={"status_code": status_code})
    
    elif status_code >= 500:
        return APIError(f"Server error - {response_text}", 
                       status_code=status_code, 
                       severity=ErrorSeverity.HIGH)
    
    else:
        return APIError(f"HTTP error {status_code} - {response_text}", 
                       status_code=status_code)
