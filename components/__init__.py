"""
Skyward Assistable Bundle Components

This package provides Langflow components for integrating with:
- Assistable AI API
- GoHighLevel v2 API  
- Agent delegation patterns
- Runtime hooks and notifications
"""

from .assistable_ai_client import AssistableAIClient
from .ghl_client import GoHighLevelClient
from .agent_delegator import AgentDelegator
from .runtime_hooks import RuntimeHooks
from .batch_processor import BatchProcessor

__all__ = [
    "AssistableAIClient",
    "GoHighLevelClient", 
    "AgentDelegator",
    "RuntimeHooks",
    "BatchProcessor"
]

__version__ = "1.0.0"
__description__ = "Langflow bundle for Assistable AI and GoHighLevel integration"
