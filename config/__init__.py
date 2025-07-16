"""
Configuration module for Skyward Assistable Bundle

Centralizes configuration management, environment variable handling,
and settings validation across all components.
"""

from .settings import *
from .environment import *

__all__ = [
    "Settings",
    "get_settings",
    "validate_configuration",
    "EnvironmentManager",
    "get_env_manager",
    "ASSISTABLE_API_TOKEN",
    "GHL_API_KEY",
    "GHL_CLIENT_ID", 
    "GHL_CLIENT_SECRET",
    "DEFAULT_LOCATION_ID"
]
