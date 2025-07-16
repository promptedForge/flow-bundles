"""
Basic usage examples for Skyward Assistable Bundle components

This file demonstrates simple, straightforward usage of each component
for developers getting started with the bundle.
"""

import asyncio
import os
from datetime import datetime

# Import bundle components
import sys
sys.path.append('../components')

from assistable_ai_client import AssistableAIClient
from ghl_client import GoHighLevelClient
from agent_delegator import AgentDelegator
from runtime_hooks import RuntimeHooks
from batch_processor import BatchProcessor


async def example_create_assistant():
    """Example: Create a new AI assistant"""
    print("🤖 Example: Creating AI Assistant")
    
    # Initialize client
    client = AssistableAIClient()
    
    # Configure for assistant creation
    client.operation = "create_assistant"
    client.assistant_name = "Customer Support Bot"
    client.assistant_description = "AI assistant for handling customer inquiries"
    client.input_text = "You are a helpful customer service representative. Be polite, professional, and helpful."
    client.emit_hooks = True
    
    # Execute operation
    result = await client.execute_operation()
    
    print(f"Result: {result.data}")
    print(f"Hooks emitted: {len(client.hooks)}")
    
    return result.data


async def example_chat_with_assistant():
    """Example: Chat with an existing assistant"""
    print("\n💬 Example: Chatting with Assistant")
    
    client = AssistableAIClient()
    
    # Configure for chat
    client.operation = "chat_completion"
    client.assistant_id = "asst_example123"  # Replace with actual assistant ID
    client.input_text = "Hello! Can you help me with my account?"
    client.emit_hooks = True
    
    # Execute chat
    result = await client.execute_operation()
    
    print(f"Chat response: {result.data}")
    
    return result.data


async def example_find_contact():
    """Example: Find a contact in GoHighLevel"""
    print("\n👥 Example: Finding Contact in GHL")
    
    client = GoHighLevelClient()
    
    # Configure for contact lookup
    client.operation = "get_contact_by_email"
    client.email = "customer@example.com"
    client.emit_hooks = True
    
    # Execute lookup
    result = await client.execute_operation()
    
    print(f"Contact found: {result.data}")
    
    return result.data


async def example_create_contact():
    """Example: Create a new contact"""
    print("\n➕ Example: Creating New Contact")
    
    client = GoHighLevelClient()
    
    # Configure for contact creation
    client.operation = "create_contact"
    client.email = "newcustomer@example.com"
    client.first_name = "John"
    client.last_name = "Doe"
    client.phone = "+1234567890"
    client.emit_hooks = True
    
    # Execute creation
    result = await client.execute_operation()
    
    print(f"Contact created: {result.data}")
    
    return result.data


async def example_agent_delegation():
    """Example: Intelligent task delegation"""
    print("\n🎯 Example: Agent Task Delegation")
    
    delegator = AgentDelegator()
    
    # Test CRM-related input
    delegator.user_input = "Create an assistant for handling sales calls"
    delegator.delegation_mode = "auto_detect"
    delegator.enable_hooks = True
    
    # Execute delegation
    result = await delegator.delegate_task()
    
    print(f"Delegated to: {result.data['delegation_info']['agent_used']}")
    print(f"Task analysis: {result.data['delegation_info']['task_analysis']['delegation_reason']}")
    
    # Test general input
    delegator.user_input = "What's the weather like today?"
    result2 = await delegator.delegate_task()
    
    print(f"Second delegation to: {result2.data['delegation_info']['agent_used']}")
    
    return result.data


def example_runtime_hooks():
    """Example: Runtime hooks monitoring"""
    print("\n🔔 Example: Runtime Hooks Monitoring")
    
    hooks = RuntimeHooks()
    
    # Emit some test hooks
    hook1 = hooks.emit_hook("pre_task", "test_component", {"action": "create_assistant"})
    hook2 = hooks.emit_hook("start_task", "test_component", {"task_id": "task_123"})
    hook3 = hooks.emit_hook("end_run", "test_component", {"success": True})
    
    print(f"Hooks emitted: {len(hooks.hook_storage)}")
    
    # Generate summary
    summary = hooks.get_hook_summary(list(hooks.hook_storage))
    print(f"Hook summary: {summary}")
    
    return summary


async def example_batch_calling():
    """Example: Batch AI calling campaign"""
    print("\n📦 Example: Batch AI Calling Campaign")
    
    processor = BatchProcessor()
    
    # Configure batch operation
    processor.batch_operation = "bulk_ai_calls"
    processor.assistant_id = "asst_sales123"  # Replace with actual assistant ID
    processor.batch_data = [
        {"contact_id": "contact_001"},
        {"contact_id": "contact_002"},
        {"contact_id": "contact_003"}
    ]
    processor.batch_size = 2
    processor.delay_between_batches = 1
    processor.emit_progress_hooks = True
    
    # Execute batch operation
    result = await processor.process_batch()
    
    print(f"Batch results: {result.data['summary']}")
    print(f"Progress hooks: {len(processor.progress_hooks)}")
    
    return result.data


async def example_location_switching():
    """Example: Switch between GoHighLevel locations"""
    print("\n🔄 Example: Location Switching")
    
    client = GoHighLevelClient()
    
    # Switch to a different location
    client.operation = "switch_location"
    client.location_id = "loc_chicago123"  # Replace with actual location ID
    client.emit_hooks = True
    
    result = await client.execute_operation()
    
    print(f"Location switch result: {result.data}")
    
    return result.data


async def example_make_ai_call():
    """Example: Initiate an AI call"""
    print("\n📞 Example: Making AI Call")
    
    client = AssistableAIClient()
    
    # Configure for AI call
    client.operation = "make_ai_call"
    client.assistant_id = "asst_sales123"  # Replace with actual assistant ID
    client.contact_id = "contact_456"      # Replace with actual contact ID
    client.number_pool_id = "pool_789"     # Replace with actual number pool ID
    client.emit_hooks = True
    
    # Execute AI call
    result = await client.execute_operation()
    
    print(f"AI call result: {result.data}")
    
    return result.data


def example_environment_setup():
    """Example: Proper environment variable setup"""
    print("\n⚙️ Example: Environment Setup")
    
    required_vars = [
        "ASSISTABLE_API_TOKEN",
        "GHL_API_KEY", 
        "DEFAULT_LOCATION_ID",
        "DEFAULT_NUMBER_POOL_ID"
    ]
    
    print("Required environment variables:")
    for var in required_vars:
        value = os.getenv(var)
        status = "✅ Set" if value else "❌ Missing"
        print(f"  {var}: {status}")
        
    print("\nTo set variables:")
    print("export ASSISTABLE_API_TOKEN=your_token_here")
    print("export GHL_API_KEY=your_key_here")
    print("export DEFAULT_LOCATION_ID=your_location_id")
    print("export DEFAULT_NUMBER_POOL_ID=your_pool_id")


async def example_error_handling():
    """Example: Error handling patterns"""
    print("\n🚨 Example: Error Handling")
    
    client = AssistableAIClient()
    
    # Intentionally cause an error (missing assistant ID)
    client.operation = "chat_completion"
    client.assistant_id = ""  # Missing required field
    client.input_text = "Hello"
    client.emit_hooks = True
    
    result = await client.execute_operation()
    
    if "error" in result.data:
        print(f"Handled error: {result.data['error']}")
        
        # Check for error hooks
        error_hooks = [h for h in client.hooks if h["hook_type"] == "error"]
        if error_hooks:
            print(f"Error hook emitted: {error_hooks[0]['data']}")
    
    return result.data


def example_hook_filtering():
    """Example: Filtering and analyzing hooks"""
    print("\n🔍 Example: Hook Filtering")
    
    hooks = RuntimeHooks()
    
    # Create test hooks from different components
    hooks.emit_hook("pre_task", "assistable_ai_client", {"action": "create_assistant"})
    hooks.emit_hook("end_run", "assistable_ai_client", {"success": True})
    hooks.emit_hook("pre_task", "ghl_client", {"action": "get_contact"})
    hooks.emit_hook("error", "ghl_client", {"error": "Not found"})
    
    # Filter by component
    hooks.component_filter = "assistable_ai_client"
    assistable_hooks = hooks.filter_hooks(list(hooks.hook_storage))
    print(f"Assistable AI hooks: {len(assistable_hooks)}")
    
    # Filter by hook type
    hooks.component_filter = ""
    hooks.filter_type = "error"
    error_hooks = hooks.filter_hooks(list(hooks.hook_storage))
    print(f"Error hooks: {len(error_hooks)}")
    
    # Generate summary
    summary = hooks.get_hook_summary(list(hooks.hook_storage))
    print(f"Total hooks by type: {summary['by_type']}")
    print(f"Total hooks by component: {summary['by_component']}")


async def run_all_examples():
    """Run all examples in sequence"""
    print("🚀 Running Skyward Assistable Bundle Examples")
    print("=" * 50)
    
    # Check environment setup first
    example_environment_setup()
    
    # Run examples that don't require API calls
    print("\n" + "=" * 50)
    example_runtime_hooks()
    
    print("\n" + "=" * 50)
    example_hook_filtering()
    
    print("\n" + "=" * 50)
    await example_agent_delegation()
    
    print("\n" + "=" * 50)
    await example_error_handling()
    
    # API examples (commented out to avoid actual API calls)
    print("\n" + "=" * 50)
    print("📝 API Examples (uncomment to run with real credentials):")
    print("  - example_create_assistant()")
    print("  - example_chat_with_assistant()")
    print("  - example_find_contact()")
    print("  - example_create_contact()")
    print("  - example_make_ai_call()")
    print("  - example_batch_calling()")
    print("  - example_location_switching()")
    
    # Uncomment these lines to run with real API credentials:
    # await example_create_assistant()
    # await example_find_contact()
    # await example_batch_calling()
    
    print("\n🎉 Examples completed!")


if __name__ == "__main__":
    # Run examples
    asyncio.run(run_all_examples())
