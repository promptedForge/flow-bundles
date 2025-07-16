import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import uuid
import asyncio
from collections import deque

from langflow.custom import Component
from langflow.io import MessageTextInput, DropdownInput, Output, BoolInput, IntInput, DataInput
from langflow.schema import Data

class RuntimeHooks(Component):
    display_name = "Runtime Hooks"
    description = "Progress notification and monitoring system for agent operations"
    icon = "🔔"
    
    inputs = [
        DropdownInput(
            name="hook_mode",
            display_name="Hook Mode",
            options=[
                "monitor",
                "emit",
                "filter",
                "aggregate"
            ],
            value="monitor",
            info="Hook operation mode"
        ),
        DataInput(
            name="hook_input",
            display_name="Hook Input",
            info="Hook data to process or emit"
        ),
        MessageTextInput(
            name="filter_type",
            display_name="Filter Type",
            value="",
            info="Filter hooks by type (pre_task, start_task, end_run, error)"
        ),
        MessageTextInput(
            name="component_filter",
            display_name="Component Filter", 
            value="",
            info="Filter hooks by component name"
        ),
        IntInput(
            name="max_hooks",
            display_name="Max Hooks",
            value=100,
            info="Maximum number of hooks to retain"
        ),
        IntInput(
            name="retention_minutes",
            display_name="Retention Minutes",
            value=60,
            info="How long to retain hooks (minutes)"
        ),
        BoolInput(
            name="real_time_updates",
            display_name="Real-time Updates",
            value=True,
            info="Enable real-time hook updates"
        ),
        BoolInput(
            name="auto_cleanup",
            display_name="Auto Cleanup",
            value=True,
            info="Automatically clean up old hooks"
        )
    ]
    
    outputs = [
        Output(display_name="Hooks", name="hooks", method="process_hooks"),
        Output(display_name="Summary", name="summary", method="get_summary"),
        Output(display_name="Status", name="status", method="get_status"),
        Output(display_name="Real-time Feed", name="realtime", method="get_realtime_feed")
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hook_storage = deque(maxlen=self.max_hooks if hasattr(self, 'max_hooks') else 100)
        self.hook_listeners = []
        self.session_hooks = {}
        self.last_cleanup = datetime.now()
        
    def add_hook_listener(self, callback: Callable[[Dict[str, Any]], None]):
        """Add a callback function to listen for new hooks"""
        self.hook_listeners.append(callback)
    
    def emit_hook(self, hook_type: str, component: str, data: Dict[str, Any], session_id: Optional[str] = None) -> Dict[str, Any]:
        """Emit a new runtime hook"""
        
        hook = {
            "id": str(uuid.uuid4()),
            "hook_type": hook_type,
            "component": component,
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "session_id": session_id or "default",
            "status": "active"
        }
        
        # Store the hook
        self.hook_storage.append(hook)
        
        # Store by session
        if session_id:
            if session_id not in self.session_hooks:
                self.session_hooks[session_id] = []
            self.session_hooks[session_id].append(hook)
        
        # Notify listeners
        if self.real_time_updates:
            for listener in self.hook_listeners:
                try:
                    listener(hook)
                except Exception as e:
                    print(f"Hook listener error: {e}")
        
        return hook
    
    def filter_hooks(self, hooks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter hooks based on criteria"""
        
        filtered = hooks
        
        # Filter by hook type
        if self.filter_type:
            filtered = [h for h in filtered if h.get("hook_type") == self.filter_type]
        
        # Filter by component
        if self.component_filter:
            filtered = [h for h in filtered if h.get("component") == self.component_filter]
        
        return filtered
    
    def cleanup_old_hooks(self):
        """Remove hooks older than retention period"""
        if not self.auto_cleanup:
            return
            
        now = datetime.now()
        cutoff = now - timedelta(minutes=self.retention_minutes)
        
        # Clean main storage
        self.hook_storage = deque([
            hook for hook in self.hook_storage 
            if datetime.fromisoformat(hook["timestamp"]) > cutoff
        ], maxlen=self.max_hooks)
        
        # Clean session hooks
        for session_id in list(self.session_hooks.keys()):
            self.session_hooks[session_id] = [
                hook for hook in self.session_hooks[session_id]
                if datetime.fromisoformat(hook["timestamp"]) > cutoff
            ]
            
            # Remove empty sessions
            if not self.session_hooks[session_id]:
                del self.session_hooks[session_id]
        
        self.last_cleanup = now
    
    def get_hook_summary(self, hooks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics for hooks"""
        
        if not hooks:
            return {
                "total_hooks": 0,
                "by_type": {},
                "by_component": {},
                "by_status": {},
                "latest_timestamp": None,
                "sessions": 0
            }
        
        # Count by type
        by_type = {}
        for hook in hooks:
            hook_type = hook.get("hook_type", "unknown")
            by_type[hook_type] = by_type.get(hook_type, 0) + 1
        
        # Count by component
        by_component = {}
        for hook in hooks:
            component = hook.get("component", "unknown")
            by_component[component] = by_component.get(component, 0) + 1
        
        # Count by status
        by_status = {}
        for hook in hooks:
            status = hook.get("status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1
        
        # Get unique sessions
        sessions = set(hook.get("session_id", "default") for hook in hooks)
        
        # Latest timestamp
        latest_timestamp = max(hook["timestamp"] for hook in hooks) if hooks else None
        
        return {
            "total_hooks": len(hooks),
            "by_type": by_type,
            "by_component": by_component,
            "by_status": by_status,
            "latest_timestamp": latest_timestamp,
            "sessions": len(sessions),
            "session_list": list(sessions)
        }
    
    def aggregate_hooks_by_session(self, hooks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate hooks by session for workflow tracking"""
        
        session_data = {}
        
        for hook in hooks:
            session_id = hook.get("session_id", "default")
            
            if session_id not in session_data:
                session_data[session_id] = {
                    "session_id": session_id,
                    "hooks": [],
                    "start_time": hook["timestamp"],
                    "end_time": hook["timestamp"],
                    "status": "active",
                    "operations": [],
                    "errors": []
                }
            
            session_info = session_data[session_id]
            session_info["hooks"].append(hook)
            
            # Update timing
            if hook["timestamp"] < session_info["start_time"]:
                session_info["start_time"] = hook["timestamp"]
            if hook["timestamp"] > session_info["end_time"]:
                session_info["end_time"] = hook["timestamp"]
            
            # Track operations and errors
            if hook["hook_type"] == "pre_task":
                operation = hook.get("data", {}).get("action", "unknown")
                if operation not in session_info["operations"]:
                    session_info["operations"].append(operation)
            
            if hook["hook_type"] == "error":
                session_info["errors"].append(hook["data"])
                session_info["status"] = "error"
            elif hook["hook_type"] == "end_run" and session_info["status"] != "error":
                session_info["status"] = "completed"
        
        return session_data
    
    def get_realtime_updates(self) -> List[Dict[str, Any]]:
        """Get recent hooks for real-time monitoring"""
        
        # Get hooks from last 5 minutes
        cutoff = datetime.now() - timedelta(minutes=5)
        recent_hooks = [
            hook for hook in self.hook_storage
            if datetime.fromisoformat(hook["timestamp"]) > cutoff
        ]
        
        return sorted(recent_hooks, key=lambda x: x["timestamp"], reverse=True)
    
    async def process_hooks(self) -> Data:
        """Main hook processing method"""
        try:
            # Cleanup old hooks periodically
            if datetime.now() - self.last_cleanup > timedelta(minutes=10):
                self.cleanup_old_hooks()
            
            if self.hook_mode == "emit" and self.hook_input:
                # Emit a new hook
                hook_data = self.hook_input if isinstance(self.hook_input, dict) else {}
                hook = self.emit_hook(
                    hook_type=hook_data.get("hook_type", "custom"),
                    component=hook_data.get("component", "runtime_hooks"),
                    data=hook_data.get("data", {}),
                    session_id=hook_data.get("session_id")
                )
                return Data(data={"emitted_hook": hook})
            
            elif self.hook_mode == "monitor":
                # Return all hooks with filtering
                all_hooks = list(self.hook_storage)
                filtered_hooks = self.filter_hooks(all_hooks)
                return Data(data={"hooks": filtered_hooks})
            
            elif self.hook_mode == "filter":
                # Return filtered hooks
                all_hooks = list(self.hook_storage)
                filtered_hooks = self.filter_hooks(all_hooks)
                return Data(data={"filtered_hooks": filtered_hooks})
            
            elif self.hook_mode == "aggregate":
                # Return aggregated hook data
                all_hooks = list(self.hook_storage)
                filtered_hooks = self.filter_hooks(all_hooks)
                aggregated = self.aggregate_hooks_by_session(filtered_hooks)
                return Data(data={"aggregated_sessions": aggregated})
            
            else:
                return Data(data={"error": f"Unknown hook mode: {self.hook_mode}"})
                
        except Exception as e:
            return Data(data={"error": f"Hook processing failed: {str(e)}"})
    
    def get_summary(self) -> Data:
        """Get hook summary statistics"""
        all_hooks = list(self.hook_storage)
        filtered_hooks = self.filter_hooks(all_hooks)
        summary = self.get_hook_summary(filtered_hooks)
        return Data(data=summary)
    
    def get_status(self) -> Data:
        """Get current runtime status"""
        status = {
            "total_hooks_stored": len(self.hook_storage),
            "active_sessions": len(self.session_hooks),
            "last_cleanup": self.last_cleanup.isoformat(),
            "retention_minutes": self.retention_minutes,
            "max_hooks": self.max_hooks,
            "real_time_enabled": self.real_time_updates,
            "listeners_count": len(self.hook_listeners)
        }
        return Data(data=status)
    
    def get_realtime_feed(self) -> Data:
        """Get real-time hook feed"""
        recent_hooks = self.get_realtime_updates()
        return Data(data={"realtime_hooks": recent_hooks})
