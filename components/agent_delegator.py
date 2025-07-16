import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from langflow.custom import Component
from langflow.io import MessageTextInput, DropdownInput, Output, BoolInput, DataInput
from langflow.schema import Data

class AgentDelegator(Component):
    display_name = "Agent Delegator"
    description = "Intelligent task delegation between Primary and Specialist agents with runtime hooks"
    icon = "🎯"
    
    inputs = [
        MessageTextInput(
            name="user_input",
            display_name="User Input",
            value="",
            info="Natural language input from external client"
        ),
        DropdownInput(
            name="delegation_mode",
            display_name="Delegation Mode",
            options=[
                "auto_detect",
                "force_specialist",
                "primary_only",
                "hybrid"
            ],
            value="auto_detect",
            info="How to handle task delegation"
        ),
        DataInput(
            name="specialist_tools",
            display_name="Specialist Tools",
            info="Available tools for the specialist agent"
        ),
        DataInput(
            name="context_data",
            display_name="Context Data",
            info="Additional context for task execution"
        ),
        BoolInput(
            name="enable_hooks",
            display_name="Enable Runtime Hooks",
            value=True,
            info="Enable progress notifications and status updates"
        ),
        MessageTextInput(
            name="primary_system_prompt",
            display_name="Primary Agent System Prompt",
            value="You are a generalist AI agent that delegates specialized tasks to expert agents. When users request CRM operations, delegate to the Specialist Agent.",
            info="System prompt for the primary agent"
        ),
        MessageTextInput(
            name="specialist_system_prompt", 
            display_name="Specialist Agent System Prompt",
            value="You are an expert in Assistable AI and GoHighLevel operations. Use specialized tools to complete CRM tasks and always emit progress hooks.",
            info="System prompt for the specialist agent"
        )
    ]
    
    outputs = [
        Output(display_name="Response", name="response", method="delegate_task"),
        Output(display_name="Hooks", name="hooks", method="get_hooks"),
        Output(display_name="Agent Used", name="agent_used", method="get_agent_used"),
        Output(display_name="Task Analysis", name="task_analysis", method="get_task_analysis")
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hooks = []
        self.current_agent = None
        self.task_analysis = {}
        
    def emit_hook(self, hook_type: str, data: Dict[str, Any]):
        """Emit runtime hook for progress tracking"""
        if self.enable_hooks:
            hook = {
                "hook_type": hook_type,
                "timestamp": datetime.now().isoformat(),
                "component": "agent_delegator",
                "data": data,
                "status": "active",
                "session_id": getattr(self, '_session_id', str(uuid.uuid4()))
            }
            self.hooks.append(hook)
            return hook
        return None
    
    def analyze_task(self, user_input: str) -> Dict[str, Any]:
        """Analyze user input to determine task delegation"""
        
        # CRM-related keywords that suggest specialist agent
        crm_keywords = [
            'assistant', 'ai call', 'contact', 'gohighlevel', 'ghl', 
            'conversation', 'lead', 'crm', 'customer', 'phone',
            'message', 'create assistant', 'make call', 'update contact',
            'calling campaign', 'bulk call', 'leads', 'sales'
        ]
        
        # Natural language processing keywords
        natural_keywords = [
            'chat', 'talk', 'explain', 'help', 'question', 'general',
            'what is', 'how to', 'can you', 'please help'
        ]
        
        user_lower = user_input.lower()
        
        crm_score = sum(1 for keyword in crm_keywords if keyword in user_lower)
        natural_score = sum(1 for keyword in natural_keywords if keyword in user_lower)
        
        analysis = {
            "input": user_input,
            "crm_score": crm_score,
            "natural_score": natural_score,
            "keywords_found": {
                "crm": [kw for kw in crm_keywords if kw in user_lower],
                "natural": [kw for kw in natural_keywords if kw in user_lower]
            },
            "recommended_agent": "specialist" if crm_score > natural_score else "primary",
            "confidence": abs(crm_score - natural_score) / max(len(crm_keywords), len(natural_keywords)),
            "delegation_reason": ""
        }
        
        # Set delegation reason
        if crm_score > 2:
            analysis["delegation_reason"] = "Multiple CRM keywords detected, requires specialist knowledge"
        elif crm_score > 0:
            analysis["delegation_reason"] = "CRM operation detected, delegating to specialist"
        elif natural_score > 0:
            analysis["delegation_reason"] = "General conversation, handling with primary agent"
        else:
            analysis["delegation_reason"] = "Ambiguous input, using auto-detection"
            
        return analysis
    
    def should_delegate_to_specialist(self, analysis: Dict[str, Any]) -> bool:
        """Determine if task should be delegated to specialist"""
        
        if self.delegation_mode == "force_specialist":
            return True
        elif self.delegation_mode == "primary_only":
            return False
        elif self.delegation_mode == "auto_detect":
            return analysis["recommended_agent"] == "specialist"
        elif self.delegation_mode == "hybrid":
            # Use specialist for high-confidence CRM tasks, primary for everything else
            return analysis["recommended_agent"] == "specialist" and analysis["confidence"] > 0.3
        
        return False
    
    async def execute_with_primary_agent(self, user_input: str) -> Dict[str, Any]:
        """Execute task with primary agent"""
        
        self.emit_hook("pre_task", {
            "agent": "primary",
            "action": "natural_language_processing",
            "input": user_input
        })
        
        # Simulate primary agent response (in real implementation, this would call an LLM)
        response = {
            "agent": "primary",
            "response": f"I understand you're asking about: {user_input}. I'm a general assistant and can help with various tasks. If you need CRM operations like creating assistants or managing contacts, I can delegate that to our specialist agent.",
            "can_delegate": True,
            "suggested_next_steps": [
                "Ask for more specific information",
                "Delegate to specialist if CRM operation needed",
                "Provide general assistance"
            ]
        }
        
        self.emit_hook("end_run", {
            "agent": "primary",
            "response": response,
            "success": True
        })
        
        return response
    
    async def execute_with_specialist_agent(self, user_input: str, tools: Optional[Any] = None) -> Dict[str, Any]:
        """Execute task with specialist agent"""
        
        self.emit_hook("pre_task", {
            "agent": "specialist",
            "action": "crm_operation",
            "input": user_input,
            "tools_available": bool(tools)
        })
        
        # Parse the input for CRM operations
        operation_mapping = {
            "create assistant": "create_assistant_operation",
            "make call": "ai_call_operation", 
            "find contact": "contact_lookup_operation",
            "send message": "message_operation",
            "switch location": "location_switch_operation",
            "calling campaign": "bulk_call_operation",
            "bulk call": "bulk_call_operation"
        }
        
        detected_operation = None
        for phrase, operation in operation_mapping.items():
            if phrase in user_input.lower():
                detected_operation = operation
                break
        
        self.emit_hook("start_task", {
            "agent": "specialist",
            "operation": detected_operation or "general_crm_task",
            "task_id": str(uuid.uuid4())
        })
        
        # Simulate specialist agent response
        if detected_operation:
            response = {
                "agent": "specialist",
                "operation": detected_operation,
                "response": f"I've identified this as a {detected_operation.replace('_', ' ')}. I'm equipped with specialized CRM tools to handle this request.",
                "tool_calls_planned": self._plan_tool_calls(detected_operation, user_input),
                "next_steps": self._get_next_steps(detected_operation),
                "can_execute": True
            }
        else:
            response = {
                "agent": "specialist", 
                "operation": "analysis",
                "response": f"I'm analyzing your CRM request: {user_input}. I have access to Assistable AI and GoHighLevel tools to help you.",
                "available_operations": list(operation_mapping.keys()),
                "suggestion": "Please specify which CRM operation you'd like to perform.",
                "can_execute": False
            }
        
        self.emit_hook("end_run", {
            "agent": "specialist",
            "operation": detected_operation,
            "response": response,
            "success": True
        })
        
        return response
    
    def _plan_tool_calls(self, operation: str, user_input: str) -> List[str]:
        """Plan which tools to call for the operation"""
        
        tool_plans = {
            "create_assistant_operation": [
                "validate_location_access",
                "create_assistant_api_call",
                "confirm_creation"
            ],
            "ai_call_operation": [
                "lookup_contact",
                "validate_phone_number",
                "initiate_ai_call",
                "track_call_status"  
            ],
            "bulk_call_operation": [
                "validate_contact_list",
                "create_assistant_if_needed",
                "initiate_bulk_calls",
                "monitor_campaign_progress"
            ],
            "contact_lookup_operation": [
                "search_by_identifier",
                "retrieve_contact_details",
                "format_contact_info"
            ],
            "message_operation": [
                "lookup_conversation",
                "send_message",
                "confirm_delivery"
            ],
            "location_switch_operation": [
                "validate_location_access",
                "switch_context",
                "confirm_switch"
            ]
        }
        
        return tool_plans.get(operation, ["analyze_request", "determine_next_steps"])
    
    def _get_next_steps(self, operation: str) -> List[str]:
        """Get suggested next steps for the operation"""
        
        next_steps = {
            "create_assistant_operation": [
                "Provide assistant name and description",
                "Specify location ID if different from default",
                "Configure assistant parameters"
            ],
            "ai_call_operation": [
                "Provide contact ID or phone number",
                "Specify assistant to use for the call",
                "Confirm number pool for outbound calling"
            ],
            "bulk_call_operation": [
                "Provide contact list or criteria",
                "Create or specify assistant for calls",
                "Configure campaign parameters"
            ],
            "contact_lookup_operation": [
                "Provide email, phone, or contact ID",
                "Specify which location to search",
                "Review returned contact information"
            ]
        }
        
        return next_steps.get(operation, ["Provide more specific details about your request"])
    
    async def delegate_task(self) -> Data:
        """Main delegation logic"""
        try:
            # Generate session ID for tracking
            if not hasattr(self, '_session_id'):
                self._session_id = str(uuid.uuid4())
            
            # Analyze the task
            self.task_analysis = self.analyze_task(self.user_input)
            
            self.emit_hook("task_analysis", {
                "analysis": self.task_analysis,
                "delegation_mode": self.delegation_mode
            })
            
            # Determine delegation
            should_use_specialist = self.should_delegate_to_specialist(self.task_analysis)
            
            if should_use_specialist:
                self.current_agent = "specialist"
                result = await self.execute_with_specialist_agent(
                    self.user_input, 
                    self.specialist_tools
                )
            else:
                self.current_agent = "primary"
                result = await self.execute_with_primary_agent(self.user_input)
            
            # Add delegation metadata
            result["delegation_info"] = {
                "agent_used": self.current_agent,
                "delegation_mode": self.delegation_mode,
                "task_analysis": self.task_analysis,
                "session_id": self._session_id
            }
            
            return Data(data=result)
            
        except Exception as e:
            error_result = {
                "error": f"Delegation failed: {str(e)}",
                "agent_used": self.current_agent,
                "session_id": getattr(self, '_session_id', 'unknown')
            }
            
            self.emit_hook("error", {
                "error": str(e),
                "agent": self.current_agent
            })
            
            return Data(data=error_result)
    
    def get_hooks(self) -> Data:
        """Return runtime hooks for monitoring"""
        return Data(data={"hooks": self.hooks})
    
    def get_agent_used(self) -> Data:
        """Return which agent was used"""
        return Data(data={"agent": self.current_agent})
    
    def get_task_analysis(self) -> Data:
        """Return task analysis results"""
        return Data(data={"analysis": self.task_analysis})
