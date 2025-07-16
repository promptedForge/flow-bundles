import httpx
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from langflow.custom import Component
from langflow.io import DropdownInput, MessageTextInput, Output, BoolInput, IntInput
from langflow.schema import Data

class GoHighLevelClient(Component):
    display_name = "GoHighLevel Client"
    description = "Direct integration with GoHighLevel v2 API for CRM operations"
    icon = "👥"
    
    inputs = [
        MessageTextInput(
            name="api_key",
            display_name="API Key",
            value="",
            password=True,
            info="GoHighLevel API key (will use GHL_API_KEY env var if empty)"
        ),
        DropdownInput(
            name="operation",
            display_name="Operation",
            options=[
                "get_contact",
                "get_contact_by_email",
                "get_contact_by_phone",
                "create_contact",
                "update_contact",
                "get_conversation",
                "create_message",
                "switch_location",
                "add_tag",
                "remove_tag",
                "create_opportunity",
                "create_task"
            ],
            value="get_contact"
        ),
        MessageTextInput(
            name="location_id",
            display_name="Location ID",
            value="",
            info="GoHighLevel location/subaccount ID (uses DEFAULT_LOCATION_ID if empty)"
        ),
        MessageTextInput(
            name="contact_id",
            display_name="Contact ID",
            value="",
            info="Contact ID for operations"
        ),
        MessageTextInput(
            name="email",
            display_name="Email",
            value="",
            info="Contact email address"
        ),
        MessageTextInput(
            name="phone",
            display_name="Phone",
            value="",
            info="Contact phone number"
        ),
        MessageTextInput(
            name="first_name",
            display_name="First Name",
            value="",
            info="Contact first name"
        ),
        MessageTextInput(
            name="last_name",
            display_name="Last Name",
            value="",
            info="Contact last name"
        ),
        MessageTextInput(
            name="message_text",
            display_name="Message Text",
            value="",
            info="Message content to send"
        ),
        MessageTextInput(
            name="tag_name",
            display_name="Tag Name",
            value="",
            info="Tag to add/remove"
        ),
        MessageTextInput(
            name="conversation_id",
            display_name="Conversation ID",
            value="",
            info="GHL conversation ID"
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
        self.base_url = "https://services.leadconnectorhq.com"
        self._location_tokens = {}
        
    def emit_hook(self, hook_type: str, data: Dict[str, Any]):
        """Emit runtime hook for progress tracking"""
        if self.emit_hooks:
            hook = {
                "hook_type": hook_type,
                "timestamp": datetime.now().isoformat(),
                "component": "ghl_client",
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
        params: Optional[Dict[str, Any]] = None,
        location_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to GoHighLevel API"""
        
        # Get API key from input or environment
        import os
        api_key = self.api_key or os.getenv("GHL_API_KEY")
        if not api_key:
            return {"error": "API key is required. Set GHL_API_KEY environment variable or provide key input."}
        
        url = f"{self.base_url}{endpoint}"
        
        # Use location-specific token if available, otherwise use main API key
        headers = {
            "Content-Type": "application/json",
            "Version": "2021-07-28",
            "User-Agent": "Skyward-Langflow-Bundle/1.0.0"
        }
        
        if location_id and location_id in self._location_tokens:
            headers["Authorization"] = f"Bearer {self._location_tokens[location_id]}"
        else:
            headers["Authorization"] = f"Bearer {api_key}"
        
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
                    return {"error": "Unauthorized - Check API token or location access"}
                elif response.status_code == 403:
                    return {"error": "Forbidden - Insufficient permissions"}
                elif response.status_code == 429:
                    return {"error": "Rate limited - Please try again later"}
                elif response.status_code >= 400:
                    return {"error": f"GHL API Error {response.status_code}: {response.text}"}
                
                try:
                    return response.json()
                except Exception:
                    return {"success": True, "response": response.text}
                    
        except httpx.TimeoutException:
            return {"error": "Request timeout"}
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    async def get_contact(self) -> Dict[str, Any]:
        """Get contact information by ID"""
        # Get location ID
        import os
        location_id = self.location_id or os.getenv("DEFAULT_LOCATION_ID")
        
        if not self.contact_id:
            return {"error": "Contact ID is required"}
        
        # Emit pre_task hook
        self.emit_hook("pre_task", {
            "action": "get_contact",
            "contact_id": self.contact_id,
            "location_id": location_id
        })
        
        result = await self._make_request(
            "GET", 
            f"/contacts/{self.contact_id}",
            location_id=location_id
        )
        
        # Emit end_run hook
        self.emit_hook("end_run", {
            "action": "get_contact",
            "contact_id": self.contact_id,
            "result": result,
            "success": "error" not in result
        })
        
        return result
    
    async def get_contact_by_email(self) -> Dict[str, Any]:
        """Get contact by email address"""
        import os
        location_id = self.location_id or os.getenv("DEFAULT_LOCATION_ID")
        
        if not self.email:
            return {"error": "Email is required"}
        
        self.emit_hook("pre_task", {
            "action": "get_contact_by_email",
            "email": self.email,
            "location_id": location_id
        })
        
        params = {"email": self.email}
        result = await self._make_request(
            "GET",
            "/contacts/search",
            params=params,
            location_id=location_id
        )
        
        self.emit_hook("end_run", {
            "action": "get_contact_by_email",
            "email": self.email,
            "result": result,
            "success": "error" not in result
        })
        
        return result
    
    async def get_contact_by_phone(self) -> Dict[str, Any]:
        """Get contact by phone number"""
        import os
        location_id = self.location_id or os.getenv("DEFAULT_LOCATION_ID")
        
        if not self.phone:
            return {"error": "Phone is required"}
        
        params = {"phone": self.phone}
        return await self._make_request(
            "GET",
            "/contacts/search",
            params=params,
            location_id=location_id
        )
    
    async def create_contact(self) -> Dict[str, Any]:
        """Create a new contact"""
        import os
        location_id = self.location_id or os.getenv("DEFAULT_LOCATION_ID")
        
        if not (self.email or self.phone):
            return {"error": "Either email or phone is required"}
        
        self.emit_hook("pre_task", {
            "action": "create_contact",
            "email": self.email,
            "phone": self.phone,
            "location_id": location_id
        })
        
        data = {}
        if self.email:
            data["email"] = self.email
        if self.phone:
            data["phone"] = self.phone
        if self.first_name:
            data["firstName"] = self.first_name
        if self.last_name:
            data["lastName"] = self.last_name
        
        result = await self._make_request(
            "POST",
            "/contacts/",
            data=data,
            location_id=location_id
        )
        
        self.emit_hook("end_run", {
            "action": "create_contact",
            "data": data,
            "result": result,
            "success": "error" not in result
        })
        
        return result
    
    async def switch_location(self) -> Dict[str, Any]:
        """Switch to a different location/subaccount"""
        if not self.location_id:
            return {"error": "Location ID is required for switching"}
        
        # This operation is more about updating internal state
        # In a real implementation, you might need to exchange tokens
        self.emit_hook("pre_task", {
            "action": "switch_location",
            "new_location_id": self.location_id
        })
        
        # Store location context
        import os
        os.environ["CURRENT_LOCATION_ID"] = self.location_id
        
        self.emit_hook("end_run", {
            "action": "switch_location",
            "location_id": self.location_id,
            "success": True
        })
        
        return {
            "success": True,
            "message": f"Switched to location {self.location_id}",
            "location_id": self.location_id
        }
    
    async def execute_operation(self) -> Data:
        """Execute the selected operation"""
        try:
            if self.operation == "get_contact":
                result = await self.get_contact()
            elif self.operation == "get_contact_by_email":
                result = await self.get_contact_by_email()
            elif self.operation == "get_contact_by_phone":
                result = await self.get_contact_by_phone()
            elif self.operation == "create_contact":
                result = await self.create_contact()
            elif self.operation == "switch_location":
                result = await self.switch_location()
            else:
                result = {"error": f"Operation {self.operation} not yet implemented"}
            
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
