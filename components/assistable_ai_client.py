import httpx
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from langflow.custom import Component
from langflow.io import DropdownInput, MessageTextInput, Output, BoolInput, IntInput
from langflow.schema import Data

class AssistableAIClient(Component):
    display_name = "Assistable AI Client"
    description = "Direct integration with Assistable AI API for creating assistants and managing conversations"
    icon = "🤖"
    
    inputs = [
        MessageTextInput(
            name="api_token",
            display_name="API Token",
            value="",
            password=True,
            info="Assistable AI API token (will use ASSISTABLE_API_TOKEN env var if empty)"
        ),
        DropdownInput(
            name="operation",
            display_name="Operation",
            options=[
                "create_assistant",
                "chat_completion", 
                "make_ai_call",
                "get_conversation",
                "create_message",
                "update_assistant",
                "delete_assistant",
                "create_flow"
            ],
            value="chat_completion"
        ),
        MessageTextInput(
            name="assistant_id",
            display_name="Assistant ID",
            value="",
            info="Assistant ID for operations (auto-generated for create_assistant)"
        ),
        MessageTextInput(
            name="conversation_id", 
            display_name="Conversation ID",
            value="",
            info="Conversation ID (auto-generated if empty)"
        ),
        MessageTextInput(
            name="location_id",
            display_name="Location ID", 
            value="",
            info="GoHighLevel location ID (uses DEFAULT_LOCATION_ID if empty)"
        ),
        MessageTextInput(
            name="input_text",
            display_name="Input Text",
            value="",
            info="Message content for chat completion or assistant prompt"
        ),
        MessageTextInput(
            name="assistant_name",
            display_name="Assistant Name",
            value="",
            info="Name for new assistant"
        ),
        MessageTextInput(
            name="assistant_description",
            display_name="Assistant Description", 
            value="",
            info="Description for new assistant"
        ),
        MessageTextInput(
            name="contact_id",
            display_name="Contact ID",
            value="",
            info="GoHighLevel contact ID for AI calls"
        ),
        MessageTextInput(
            name="number_pool_id",
            display_name="Number Pool ID",
            value="",
            info="Phone number pool for AI calls (uses DEFAULT_NUMBER_POOL_ID if empty)"
        ),
        BoolInput(
            name="emit_hooks",
            display_name="Emit Runtime Hooks",
            value=True,
            info="Enable runtime hook notifications"
        ),
        IntInput(
            name="timeout",
            display_name="Request Timeout",
            value=30,
            info="API request timeout in seconds"
        )
    ]
    
    outputs = [
        Output(display_name="Result", name="result", method="execute_operation"),
        Output(display_name="Hooks", name="hooks", method="get_hooks")
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hooks = []
        self.base_url = "https://api.assistable.ai/v2"
        
    def emit_hook(self, hook_type: str, data: Dict[str, Any]):
        """Emit runtime hook for progress tracking"""
        if self.emit_hooks:
            hook = {
                "hook_type": hook_type,
                "timestamp": datetime.now().isoformat(),
                "component": "assistable_ai_client",
                "data": data,
                "status": "active"
            }
            self.hooks.append(hook)
            return hook
        return None
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Assistable AI API"""
        
        # Get API token from input or environment
        import os
        api_token = self.api_token or os.getenv("ASSISTABLE_API_TOKEN")
        if not api_token:
            return {"error": "API token is required. Set ASSISTABLE_API_TOKEN environment variable or provide token input."}
        
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "User-Agent": "Skyward-Langflow-Bundle/1.0.0"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data if data else None,
                    params=params if params else None
                )
                
                if response.status_code == 401:
                    return {"error": "Unauthorized - Check API token"}
                elif response.status_code == 429:
                    return {"error": "Rate limited - Please try again later"}
                elif response.status_code >= 400:
                    return {"error": f"API Error {response.status_code}: {response.text}"}
                
                try:
                    return response.json()
                except Exception:
                    return {"success": True, "response": response.text}
                    
        except httpx.TimeoutException:
            return {"error": "Request timeout"}
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    async def create_assistant(self) -> Dict[str, Any]:
        """Create a new assistant"""
        # Get location ID
        import os
        location_id = self.location_id or os.getenv("DEFAULT_LOCATION_ID")
        if not location_id:
            return {"error": "Location ID is required"}
        
        # Emit pre_task hook
        self.emit_hook("pre_task", {
            "action": "create_assistant",
            "name": self.assistant_name,
            "description": self.assistant_description,
            "location_id": location_id
        })
        
        data = {
            "name": self.assistant_name or "New Assistant",
            "description": self.assistant_description or "AI Assistant created via Langflow",
            "location_id": location_id,
            "prompt": self.input_text or "You are a helpful AI assistant.",
            "temperature": 0.7,
            "model": "gpt-4",
            "queue": 1
        }
        
        # Emit start_task hook
        self.emit_hook("start_task", {
            "task_id": str(uuid.uuid4()),
            "action": "create_assistant",
            "data": data
        })
        
        result = await self._make_request("POST", "/create-assistant", data)
        
        # Emit end_run hook
        self.emit_hook("end_run", {
            "action": "create_assistant",
            "result": result,
            "success": "error" not in result
        })
        
        return result
    
    async def chat_completion(self) -> Dict[str, Any]:
        """Process chat completion with assistant"""
        # Generate conversation ID if not provided
        conversation_id = self.conversation_id or f"conv_{uuid.uuid4().hex[:8]}"
        
        # Get location ID
        import os
        location_id = self.location_id or os.getenv("DEFAULT_LOCATION_ID")
        
        # Emit pre_task hook
        self.emit_hook("pre_task", {
            "action": "chat_completion",
            "conversation_id": conversation_id,
            "assistant_id": self.assistant_id,
            "input": self.input_text
        })
        
        data = {
            "conversation_id": conversation_id,
            "input": self.input_text,
            "location_id": location_id,
            "assistant_id": self.assistant_id,
            "channel": "web",
            "messages": []
        }
        
        # Emit start_task hook
        self.emit_hook("start_task", {
            "task_id": str(uuid.uuid4()),
            "action": "chat_completion",
            "conversation_id": conversation_id
        })
        
        result = await self._make_request("POST", "/ghl-chat-completion", data)
        
        # Emit end_run hook
        self.emit_hook("end_run", {
            "action": "chat_completion",
            "conversation_id": conversation_id,
            "result": result,
            "success": "error" not in result
        })
        
        return result
    
    async def make_ai_call(self) -> Dict[str, Any]:
        """Initiate AI call through GoHighLevel integration"""
        # Get default values from environment
        import os
        location_id = self.location_id or os.getenv("DEFAULT_LOCATION_ID")
        number_pool_id = self.number_pool_id or os.getenv("DEFAULT_NUMBER_POOL_ID")
        
        if not all([self.assistant_id, self.contact_id, number_pool_id, location_id]):
            return {"error": "Missing required fields: assistant_id, contact_id, number_pool_id, location_id"}
        
        # Emit pre_task hook
        self.emit_hook("pre_task", {
            "action": "make_ai_call",
            "assistant_id": self.assistant_id,
            "contact_id": self.contact_id,
            "number_pool_id": number_pool_id
        })
        
        data = {
            "assistant_id": self.assistant_id,
            "contact_id": self.contact_id,
            "number_pool_id": number_pool_id,
            "location_id": location_id
        }
        
        # Emit start_task hook
        self.emit_hook("start_task", {
            "task_id": str(uuid.uuid4()),
            "action": "make_ai_call",
            "call_data": data
        })
        
        result = await self._make_request("POST", "/ghl/make-call", data)
        
        # Emit end_run hook
        self.emit_hook("end_run", {
            "action": "make_ai_call",
            "result": result,
            "success": "error" not in result
        })
        
        return result
    
    async def get_conversation(self) -> Dict[str, Any]:
        """Get conversation information"""
        params = {}
        if self.conversation_id:
            params["conversation_id"] = self.conversation_id
        
        return await self._make_request("GET", "/get-conversation", params=params)
    
    async def create_message(self) -> Dict[str, Any]:
        """Create a message in conversation"""
        # Generate conversation ID if not provided
        conversation_id = self.conversation_id or f"conv_{uuid.uuid4().hex[:8]}"
        
        # Get location ID
        import os
        location_id = self.location_id or os.getenv("DEFAULT_LOCATION_ID")
        
        data = {
            "location_id": location_id,
            "content": self.input_text,
            "conversation_id": conversation_id,
            "ai": False,
            "role": "user",
            "channel": "web"
        }
        
        return await self._make_request("POST", "/create-message", data)
    
    async def update_assistant(self) -> Dict[str, Any]:
        """Update an existing assistant"""
        if not self.assistant_id:
            return {"error": "Assistant ID is required for update"}
        
        data = {
            "assistant_id": self.assistant_id
        }
        
        # Add optional update fields
        if self.assistant_name:
            data["name"] = self.assistant_name
        if self.assistant_description:
            data["description"] = self.assistant_description
        if self.input_text:
            data["prompt"] = self.input_text
        
        return await self._make_request("PUT", "/update-assistant", data)
    
    async def delete_assistant(self) -> Dict[str, Any]:
        """Delete an assistant"""
        if not self.assistant_id:
            return {"error": "Assistant ID is required for deletion"}
        
        params = {"assistant_id": self.assistant_id}
        return await self._make_request("DELETE", "/delete-assistant", params=params)
    
    async def create_flow(self) -> Dict[str, Any]:
        """Create a new flow in Assistable AI"""
        # Get location ID
        import os
        location_id = self.location_id or os.getenv("DEFAULT_LOCATION_ID")
        if not location_id:
            return {"error": "Location ID is required"}
        
        data = {"location_id": location_id}
        return await self._make_request("POST", "/create-flow", data)
    
    async def execute_operation(self) -> Data:
        """Execute the selected operation"""
        try:
            if self.operation == "create_assistant":
                result = await self.create_assistant()
            elif self.operation == "chat_completion":
                result = await self.chat_completion()
            elif self.operation == "make_ai_call":
                result = await self.make_ai_call()
            elif self.operation == "get_conversation":
                result = await self.get_conversation()
            elif self.operation == "create_message":
                result = await self.create_message()
            elif self.operation == "update_assistant":
                result = await self.update_assistant()
            elif self.operation == "delete_assistant":
                result = await self.delete_assistant()
            elif self.operation == "create_flow":
                result = await self.create_flow()
            else:
                result = {"error": f"Unknown operation: {self.operation}"}
            
            return Data(data=result)
            
        except Exception as e:
            error_result = {"error": f"Operation failed: {str(e)}"}
            self.emit_hook("error", {
                "action": self.operation,
                "error": str(e)
            })
            return Data(data=error_result)
    
    def get_hooks(self) -> Data:
        """Return runtime hooks for monitoring"""
        return Data(data={"hooks": self.hooks})
