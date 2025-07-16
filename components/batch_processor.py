import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import json

from langflow.custom import Component
from langflow.io import MessageTextInput, DropdownInput, Output, BoolInput, IntInput, DataInput
from langflow.schema import Data

class BatchProcessor(Component):
    display_name = "Batch Processor"
    description = "Bulk operations for Assistable AI and GoHighLevel with progress tracking"
    icon = "📦"
    
    inputs = [
        DropdownInput(
            name="batch_operation",
            display_name="Batch Operation",
            options=[
                "bulk_create_assistants",
                "bulk_ai_calls",
                "bulk_contact_updates",
                "bulk_message_send",
                "bulk_contact_lookup",
                "bulk_tag_operations"
            ],
            value="bulk_ai_calls",
            info="Type of batch operation to perform"
        ),
        DataInput(
            name="batch_data",
            display_name="Batch Data",
            info="List of items to process in batch"
        ),
        MessageTextInput(
            name="assistant_id",
            display_name="Assistant ID",
            value="",
            info="Assistant ID for batch AI calls"
        ),
        MessageTextInput(
            name="location_id",
            display_name="Location ID",
            value="",
            info="GoHighLevel location ID (uses DEFAULT_LOCATION_ID if empty)"
        ),
        MessageTextInput(
            name="number_pool_id",
            display_name="Number Pool ID",
            value="",
            info="Phone number pool for batch calls (uses DEFAULT_NUMBER_POOL_ID if empty)"
        ),
        IntInput(
            name="batch_size",
            display_name="Batch Size",
            value=10,
            info="Number of items to process simultaneously"
        ),
        IntInput(
            name="delay_between_batches",
            display_name="Delay Between Batches (seconds)",
            value=2,
            info="Delay between batch processing"
        ),
        BoolInput(
            name="stop_on_error",
            display_name="Stop on Error",
            value=False,
            info="Stop processing if an error occurs"
        ),
        BoolInput(
            name="emit_progress_hooks",
            display_name="Emit Progress Hooks",
            value=True,
            info="Enable detailed progress tracking"
        ),
        IntInput(
            name="timeout_per_item",
            display_name="Timeout Per Item (seconds)",
            value=30,
            info="Timeout for each individual operation"
        )
    ]
    
    outputs = [
        Output(display_name="Results", name="results", method="process_batch"),
        Output(display_name="Progress", name="progress", method="get_progress"),
        Output(display_name="Summary", name="summary", method="get_summary"),
        Output(display_name="Errors", name="errors", method="get_errors")
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.progress_hooks = []
        self.batch_results = []
        self.batch_errors = []
        self.batch_summary = {}
        self.session_id = str(uuid.uuid4())
        
    def emit_progress_hook(self, hook_type: str, data: Dict[str, Any]):
        """Emit progress tracking hook"""
        if self.emit_progress_hooks:
            hook = {
                "hook_type": hook_type,
                "timestamp": datetime.now().isoformat(),
                "component": "batch_processor",
                "session_id": self.session_id,
                "data": data,
                "batch_operation": self.batch_operation
            }
            self.progress_hooks.append(hook)
            return hook
        return None
    
    async def process_item_with_timeout(self, process_func, item: Any, index: int) -> Dict[str, Any]:
        """Process a single item with timeout"""
        try:
            result = await asyncio.wait_for(
                process_func(item, index),
                timeout=self.timeout_per_item
            )
            return {
                "index": index,
                "item": item,
                "result": result,
                "success": True,
                "error": None,
                "timestamp": datetime.now().isoformat()
            }
        except asyncio.TimeoutError:
            return {
                "index": index,
                "item": item,
                "result": None,
                "success": False,
                "error": f"Timeout after {self.timeout_per_item} seconds",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "index": index,
                "item": item,
                "result": None,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def process_batch_chunk(self, process_func, items: List[Any], start_index: int) -> List[Dict[str, Any]]:
        """Process a chunk of items concurrently"""
        
        self.emit_progress_hook("batch_chunk_start", {
            "chunk_size": len(items),
            "start_index": start_index,
            "operation": self.batch_operation
        })
        
        # Create tasks for concurrent processing
        tasks = [
            self.process_item_with_timeout(process_func, item, start_index + i)
            for i, item in enumerate(items)
        ]
        
        # Process concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions from gather
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "index": start_index + i,
                    "item": items[i],
                    "result": None,
                    "success": False,
                    "error": str(result),
                    "timestamp": datetime.now().isoformat()
                })
            else:
                processed_results.append(result)
        
        self.emit_progress_hook("batch_chunk_complete", {
            "chunk_size": len(items),
            "start_index": start_index,
            "successful": sum(1 for r in processed_results if r["success"]),
            "failed": sum(1 for r in processed_results if not r["success"])
        })
        
        return processed_results
    
    async def bulk_create_assistants_item(self, item: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Process single assistant creation"""
        # This would integrate with AssistableAIClient in real implementation
        
        required_fields = ["name", "description", "prompt"]
        for field in required_fields:
            if field not in item:
                raise ValueError(f"Missing required field: {field}")
        
        # Get location ID
        import os
        location_id = self.location_id or item.get("location_id") or os.getenv("DEFAULT_LOCATION_ID")
        
        # Simulate API call delay
        await asyncio.sleep(0.5)
        
        # Simulated successful response
        return {
            "assistant_id": f"asst_{uuid.uuid4().hex[:8]}",
            "name": item["name"],
            "description": item["description"],
            "location_id": location_id,
            "created_at": datetime.now().isoformat()
        }
    
    async def bulk_ai_calls_item(self, item: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Process single AI call"""
        # This would integrate with AssistableAIClient in real implementation
        
        required_fields = ["contact_id"]
        for field in required_fields:
            if field not in item:
                raise ValueError(f"Missing required field: {field}")
        
        # Use provided or default values
        assistant_id = item.get("assistant_id") or self.assistant_id
        
        import os
        number_pool_id = item.get("number_pool_id") or self.number_pool_id or os.getenv("DEFAULT_NUMBER_POOL_ID")
        location_id = item.get("location_id") or self.location_id or os.getenv("DEFAULT_LOCATION_ID")
        
        if not all([assistant_id, number_pool_id, location_id]):
            raise ValueError("Missing required fields: assistant_id, number_pool_id, location_id")
        
        # Simulate API call delay
        await asyncio.sleep(1.0)
        
        # Simulated successful response
        return {
            "call_id": f"call_{uuid.uuid4().hex[:8]}",
            "contact_id": item["contact_id"],
            "assistant_id": assistant_id,
            "number_pool_id": number_pool_id,
            "location_id": location_id,
            "status": "initiated",
            "initiated_at": datetime.now().isoformat()
        }
    
    async def bulk_contact_lookup_item(self, item: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Process single contact lookup"""
        # This would integrate with GoHighLevelClient in real implementation
        
        if not any(key in item for key in ["contact_id", "email", "phone"]):
            raise ValueError("Must provide contact_id, email, or phone")
        
        # Simulate API call delay
        await asyncio.sleep(0.3)
        
        # Simulated successful response
        return {
            "contact_id": item.get("contact_id", f"contact_{uuid.uuid4().hex[:8]}"),
            "email": item.get("email"),
            "phone": item.get("phone"),
            "first_name": item.get("first_name", "John"),
            "last_name": item.get("last_name", "Doe"),
            "found": True,
            "lookup_method": "email" if "email" in item else "phone" if "phone" in item else "id"
        }
    
    async def process_batch(self) -> Data:
        """Main batch processing method"""
        try:
            # Validate inputs
            if not self.batch_data:
                return Data(data={"error": "No batch data provided"})
            
            batch_items = self.batch_data if isinstance(self.batch_data, list) else [self.batch_data]
            total_items = len(batch_items)
            
            self.emit_progress_hook("batch_start", {
                "total_items": total_items,
                "batch_size": self.batch_size,
                "operation": self.batch_operation,
                "estimated_chunks": (total_items + self.batch_size - 1) // self.batch_size
            })
            
            # Select processing function
            process_functions = {
                "bulk_create_assistants": self.bulk_create_assistants_item,
                "bulk_ai_calls": self.bulk_ai_calls_item,
                "bulk_contact_lookup": self.bulk_contact_lookup_item,
                # Add other functions as needed
            }
            
            process_func = process_functions.get(self.batch_operation)
            if not process_func:
                return Data(data={"error": f"Unknown batch operation: {self.batch_operation}"})
            
            # Process in chunks
            all_results = []
            
            for i in range(0, total_items, self.batch_size):
                chunk = batch_items[i:i + self.batch_size]
                
                self.emit_progress_hook("chunk_progress", {
                    "chunk_index": i // self.batch_size,
                    "processed_items": i,
                    "total_items": total_items,
                    "progress_percentage": (i / total_items) * 100
                })
                
                # Process chunk
                chunk_results = await self.process_batch_chunk(process_func, chunk, i)
                all_results.extend(chunk_results)
                
                # Check for errors
                chunk_errors = [r for r in chunk_results if not r["success"]]
                if chunk_errors and self.stop_on_error:
                    self.emit_progress_hook("batch_stopped", {
                        "reason": "stop_on_error",
                        "processed_items": len(all_results),
                        "errors": len(chunk_errors)
                    })
                    break
                
                # Delay between chunks (except for last chunk)
                if i + self.batch_size < total_items and self.delay_between_batches > 0:
                    await asyncio.sleep(self.delay_between_batches)
            
            # Compile results
            self.batch_results = all_results
            self.batch_errors = [r for r in all_results if not r["success"]]
            
            # Generate summary
            successful_results = [r for r in all_results if r["success"]]
            self.batch_summary = {
                "total_items": total_items,
                "processed_items": len(all_results),
                "successful": len(successful_results),
                "failed": len(self.batch_errors),
                "success_rate": len(successful_results) / len(all_results) if all_results else 0,
                "operation": self.batch_operation,
                "session_id": self.session_id,
                "started_at": self.progress_hooks[0]["timestamp"] if self.progress_hooks else None,
                "completed_at": datetime.now().isoformat()
            }
            
            self.emit_progress_hook("batch_complete", self.batch_summary)
            
            return Data(data={
                "results": self.batch_results,
                "summary": self.batch_summary,
                "session_id": self.session_id
            })
            
        except Exception as e:
            error_summary = {
                "error": str(e),
                "operation": self.batch_operation,
                "session_id": self.session_id,
                "failed_at": datetime.now().isoformat()
            }
            
            self.emit_progress_hook("batch_error", error_summary)
            
            return Data(data=error_summary)
    
    def get_progress(self) -> Data:
        """Get batch processing progress"""
        return Data(data={
            "progress_hooks": self.progress_hooks,
            "session_id": self.session_id
        })
    
    def get_summary(self) -> Data:
        """Get batch processing summary"""
        return Data(data=self.batch_summary)
    
    def get_errors(self) -> Data:
        """Get batch processing errors"""
        return Data(data={
            "errors": self.batch_errors,
            "error_count": len(self.batch_errors)
        })
