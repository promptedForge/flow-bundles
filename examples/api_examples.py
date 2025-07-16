"""
Direct API usage examples for Skyward Assistable Bundle

This file demonstrates how to use the API clients directly
without the Langflow component wrapper, useful for:
- Understanding the underlying API structure
- Building custom integrations
- Debugging API issues
- Testing API connectivity
"""

import asyncio
import os
import json
from datetime import datetime

# Import the underlying API clients
import sys
sys.path.append('../components')

# We'll import the core logic from the components
# In a real scenario, you might extract this to separate modules


class DirectAssistableAPIExample:
    """Direct usage examples for Assistable AI API"""
    
    def __init__(self, api_token: str = None):
        self.api_token = api_token or os.getenv("ASSISTABLE_API_TOKEN")
        self.base_url = "https://api.assistable.ai/v2"
        
        if not self.api_token:
            raise ValueError("API token is required. Set ASSISTABLE_API_TOKEN or provide token.")
    
    async def test_connection(self):
        """Test basic API connectivity"""
        print("🔗 Testing Assistable AI API Connection")
        
        import httpx
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/get-assistant", headers=headers)
                
                if response.status_code == 200:
                    print("✅ Connection successful")
                    return response.json()
                else:
                    print(f"❌ Connection failed: {response.status_code}")
                    return {"error": response.text}
                    
        except Exception as e:
            print(f"❌ Connection error: {str(e)}")
            return {"error": str(e)}
    
    async def create_assistant_example(self):
        """Example: Create assistant with direct API call"""
        print("\n🤖 Creating Assistant via Direct API")
        
        import httpx
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "name": "Direct API Test Assistant",
            "description": "Assistant created via direct API call",
            "location_id": os.getenv("DEFAULT_LOCATION_ID", "test_location"),
            "prompt": "You are a helpful assistant created via direct API integration.",
            "temperature": 0.7,
            "model": "gpt-4",
            "queue": 1
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/create-assistant",
                    headers=headers,
                    json=data
                )
                
                result = response.json()
                
                if response.status_code == 200:
                    print(f"✅ Assistant created: {result.get('assistant_id')}")
                    return result
                else:
                    print(f"❌ Creation failed: {result}")
                    return result
                    
        except Exception as e:
            print(f"❌ API call failed: {str(e)}")
            return {"error": str(e)}
    
    async def chat_completion_example(self, assistant_id: str):
        """Example: Chat completion with direct API call"""
        print(f"\n💬 Chat Completion with Assistant {assistant_id}")
        
        import httpx
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        conversation_id = f"direct_api_conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        data = {
            "conversation_id": conversation_id,
            "input": "Hello! This is a test message via direct API.",
            "location_id": os.getenv("DEFAULT_LOCATION_ID", "test_location"),
            "assistant_id": assistant_id,
            "channel": "web",
            "messages": []
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/ghl-chat-completion",
                    headers=headers,
                    json=data
                )
                
                result = response.json()
                
                if response.status_code == 200:
                    print(f"✅ Chat response: {result.get('response', 'No response')}")
                    return result
                else:
                    print(f"❌ Chat failed: {result}")
                    return result
                    
        except Exception as e:
            print(f"❌ Chat API call failed: {str(e)}")
            return {"error": str(e)}
    
    async def make_ai_call_example(self, assistant_id: str, contact_id: str):
        """Example: Make AI call with direct API call"""
        print(f"\n📞 Making AI Call: Assistant {assistant_id} → Contact {contact_id}")
        
        import httpx
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "assistant_id": assistant_id,
            "contact_id": contact_id,
            "number_pool_id": os.getenv("DEFAULT_NUMBER_POOL_ID", "test_pool"),
            "location_id": os.getenv("DEFAULT_LOCATION_ID", "test_location")
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/ghl/make-call",
                    headers=headers,
                    json=data
                )
                
                result = response.json()
                
                if response.status_code == 200:
                    print(f"✅ Call initiated: {result.get('call_id')}")
                    return result
                else:
                    print(f"❌ Call failed: {result}")
                    return result
                    
        except Exception as e:
            print(f"❌ Call API failed: {str(e)}")
            return {"error": str(e)}


class DirectGoHighLevelAPIExample:
    """Direct usage examples for GoHighLevel API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GHL_API_KEY")
        self.base_url = "https://services.leadconnectorhq.com"
        
        if not self.api_key:
            raise ValueError("API key is required. Set GHL_API_KEY or provide key.")
    
    async def test_connection(self):
        """Test basic API connectivity"""
        print("\n🔗 Testing GoHighLevel API Connection")
        
        import httpx
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Version": "2021-07-28",
            "Content-Type": "application/json"
        }
        
        location_id = os.getenv("DEFAULT_LOCATION_ID")
        if not location_id:
            print("⚠️ No DEFAULT_LOCATION_ID set, using test endpoint")
            endpoint = "/locations"
        else:
            endpoint = f"/locations/{location_id}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}{endpoint}", headers=headers)
                
                if response.status_code == 200:
                    print("✅ Connection successful")
                    return response.json()
                else:
                    print(f"❌ Connection failed: {response.status_code}")
                    return {"error": response.text}
                    
        except Exception as e:
            print(f"❌ Connection error: {str(e)}")
            return {"error": str(e)}
    
    async def search_contact_by_email_example(self, email: str):
        """Example: Search contact by email"""
        print(f"\n👥 Searching Contact: {email}")
        
        import httpx
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Version": "2021-07-28",
            "Content-Type": "application/json"
        }
        
        params = {"email": email}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/contacts/search",
                    headers=headers,
                    params=params
                )
                
                result = response.json()
                
                if response.status_code == 200:
                    contacts = result.get("contacts", [])
                    print(f"✅ Found {len(contacts)} contact(s)")
                    return result
                else:
                    print(f"❌ Search failed: {result}")
                    return result
                    
        except Exception as e:
            print(f"❌ Search API failed: {str(e)}")
            return {"error": str(e)}
    
    async def create_contact_example(self, email: str, first_name: str, last_name: str):
        """Example: Create new contact"""
        print(f"\n➕ Creating Contact: {first_name} {last_name} ({email})")
        
        import httpx
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Version": "2021-07-28",
            "Content-Type": "application/json"
        }
        
        data = {
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
            "source": "API Integration Test"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/contacts/",
                    headers=headers,
                    json=data
                )
                
                result = response.json()
                
                if response.status_code == 200 or response.status_code == 201:
                    contact_id = result.get("contact", {}).get("id")
                    print(f"✅ Contact created: {contact_id}")
                    return result
                else:
                    print(f"❌ Creation failed: {result}")
                    return result
                    
        except Exception as e:
            print(f"❌ Create API failed: {str(e)}")
            return {"error": str(e)}
    
    async def send_message_example(self, contact_id: str, message: str):
        """Example: Send message to contact"""
        print(f"\n💬 Sending Message to Contact {contact_id}")
        
        import httpx
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Version": "2021-07-28",
            "Content-Type": "application/json"
        }
        
        data = {
            "contactId": contact_id,
            "message": message,
            "type": "SMS"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/conversations/messages",
                    headers=headers,
                    json=data
                )
                
                result = response.json()
                
                if response.status_code == 200 or response.status_code == 201:
                    message_id = result.get("message", {}).get("id")
                    print(f"✅ Message sent: {message_id}")
                    return result
                else:
                    print(f"❌ Message failed: {result}")
                    return result
                    
        except Exception as e:
            print(f"❌ Message API failed: {str(e)}")
            return {"error": str(e)}


async def run_api_connectivity_tests():
    """Run basic API connectivity tests"""
    print("🔍 API Connectivity Tests")
    print("=" * 50)
    
    # Test Assistable AI API
    try:
        assistable_api = DirectAssistableAPIExample()
        await assistable_api.test_connection()
    except Exception as e:
        print(f"❌ Assistable AI setup failed: {str(e)}")
    
    # Test GoHighLevel API
    try:
        ghl_api = DirectGoHighLevelAPIExample()
        await ghl_api.test_connection()
    except Exception as e:
        print(f"❌ GoHighLevel setup failed: {str(e)}")


async def run_complete_workflow_example():
    """Run a complete workflow using direct API calls"""
    print("\n🎯 Complete Workflow Example")
    print("=" * 50)
    
    try:
        # Initialize API clients
        assistable_api = DirectAssistableAPIExample()
        ghl_api = DirectGoHighLevelAPIExample()
        
        # Step 1: Create an assistant
        print("\n📋 Step 1: Creating Assistant")
        assistant_result = await assistable_api.create_assistant_example()
        
        if "error" in assistant_result:
            print("❌ Workflow stopped: Assistant creation failed")
            return
        
        assistant_id = assistant_result.get("assistant_id")
        
        # Step 2: Search for or create a contact
        print("\n📋 Step 2: Managing Contact")
        test_email = "api.test@example.com"
        
        contact_search = await ghl_api.search_contact_by_email_example(test_email)
        
        if contact_search.get("contacts"):
            contact_id = contact_search["contacts"][0]["id"]
            print(f"✅ Using existing contact: {contact_id}")
        else:
            print("📝 Creating new contact...")
            contact_result = await ghl_api.create_contact_example(
                test_email, "API", "Test User"
            )
            
            if "error" in contact_result:
                print("❌ Workflow stopped: Contact creation failed")
                return
            
            contact_id = contact_result.get("contact", {}).get("id")
        
        # Step 3: Chat with the assistant
        print("\n📋 Step 3: Testing Chat")
        chat_result = await assistable_api.chat_completion_example(assistant_id)
        
        # Step 4: Send a message to the contact
        print("\n📋 Step 4: Sending Message")
        message_result = await ghl_api.send_message_example(
            contact_id, "Hello! This is a test message from our API integration."
        )
        
        # Step 5: Attempt AI call (may not work without proper setup)
        print("\n📋 Step 5: Testing AI Call Setup")
        print("ℹ️  Note: This may fail without proper phone number configuration")
        
        call_result = await assistable_api.make_ai_call_example(assistant_id, contact_id)
        
        # Summary
        print("\n📊 Workflow Summary")
        print("-" * 30)
        print(f"Assistant Created: {'✅' if assistant_id else '❌'}")
        print(f"Contact Available: {'✅' if contact_id else '❌'}")
        print(f"Chat Successful: {'✅' if 'error' not in chat_result else '❌'}")
        print(f"Message Sent: {'✅' if 'error' not in message_result else '❌'}")
        print(f"Call Initiated: {'✅' if 'error' not in call_result else '⚠️'}")
        
        return {
            "assistant_id": assistant_id,
            "contact_id": contact_id,
            "workflow_status": "completed"
        }
        
    except Exception as e:
        print(f"❌ Workflow failed: {str(e)}")
        return {"error": str(e)}


async def run_error_handling_examples():
    """Demonstrate error handling patterns"""
    print("\n🚨 Error Handling Examples")
    print("=" * 50)
    
    # Example 1: Invalid API token
    print("\n🔍 Testing Invalid API Token")
    try:
        invalid_api = DirectAssistableAPIExample("invalid_token_123")
        result = await invalid_api.test_connection()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Handled exception: {str(e)}")
    
    # Example 2: Missing required fields
    print("\n🔍 Testing Missing Required Fields")
    try:
        import httpx
        
        headers = {
            "Authorization": f"Bearer {os.getenv('ASSISTABLE_API_TOKEN', 'test')}",
            "Content-Type": "application/json"
        }
        
        # Missing required fields
        data = {
            "name": "Test Assistant"
            # Missing description, location_id, prompt, etc.
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.assistable.ai/v2/create-assistant",
                headers=headers,
                json=data
            )
            
            result = response.json()
            print(f"API Response: {result}")
            
            if response.status_code != 200:
                print("✅ Error properly handled by API")
            
    except Exception as e:
        print(f"Handled exception: {str(e)}")
    
    # Example 3: Network timeout simulation
    print("\n🔍 Testing Timeout Handling")
    try:
        async with httpx.AsyncClient(timeout=0.001) as client:  # Very short timeout
            response = await client.get("https://api.assistable.ai/v2/get-assistant")
    except httpx.TimeoutException:
        print("✅ Timeout properly handled")
    except Exception as e:
        print(f"Other exception: {str(e)}")


def demonstrate_environment_setup():
    """Demonstrate proper environment variable setup"""
    print("\n⚙️ Environment Setup Demo")
    print("=" * 50)
    
    required_vars = {
        "ASSISTABLE_API_TOKEN": "Assistable AI API token",
        "GHL_API_KEY": "GoHighLevel API key",
        "GHL_CLIENT_ID": "GoHighLevel OAuth client ID",
        "GHL_CLIENT_SECRET": "GoHighLevel OAuth client secret",
        "DEFAULT_LOCATION_ID": "Default GoHighLevel location ID",
        "DEFAULT_NUMBER_POOL_ID": "Default phone number pool ID"
    }
    
    print("📋 Required Environment Variables:")
    print("-" * 30)
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        status = "✅ Set" if value else "❌ Missing"
        masked_value = f"{value[:8]}..." if value and len(value) > 8 else "Not set"
        print(f"{var:<25} {status:<10} ({description})")
        if value:
            print(f"{'':25} Value: {masked_value}")
    
    print("\n📝 Setup Commands:")
    print("-" * 30)
    for var, description in required_vars.items():
        print(f"export {var}=your_{var.lower()}_here")
    
    print("\n💡 Tips:")
    print("- Store credentials in .env file for local development")
    print("- Use Railway environment variables for production")
    print("- Never commit credentials to version control")
    print("- Rotate API tokens periodically")


async def run_performance_benchmarks():
    """Run basic performance benchmarks"""
    print("\n⚡ Performance Benchmarks")
    print("=" * 50)
    
    try:
        assistable_api = DirectAssistableAPIExample()
        
        # Benchmark API response times
        print("🔍 Testing API Response Times...")
        
        import time
        
        # Test connection speed
        start_time = time.time()
        result = await assistable_api.test_connection()
        connection_time = time.time() - start_time
        
        print(f"Connection Test: {connection_time:.2f}s")
        
        if "error" not in result:
            # Test assistant creation speed
            start_time = time.time()
            assistant_result = await assistable_api.create_assistant_example()
            creation_time = time.time() - start_time
            
            print(f"Assistant Creation: {creation_time:.2f}s")
            
            if "assistant_id" in assistant_result:
                # Test chat speed
                start_time = time.time()
                chat_result = await assistable_api.chat_completion_example(
                    assistant_result["assistant_id"]
                )
                chat_time = time.time() - start_time
                
                print(f"Chat Completion: {chat_time:.2f}s")
        
        print("\n📊 Performance Summary:")
        print(f"Total API calls tested: 3")
        print(f"Average response time: {(connection_time + creation_time + chat_time) / 3:.2f}s")
        
    except Exception as e:
        print(f"❌ Benchmark failed: {str(e)}")


async def main():
    """Run all API examples"""
    print("🚀 Skyward Assistable Bundle - Direct API Examples")
    print("=" * 60)
    
    # Environment setup check
    demonstrate_environment_setup()
    
    # Basic connectivity tests
    await run_api_connectivity_tests()
    
    # Complete workflow example
    await run_complete_workflow_example()
    
    # Error handling examples
    await run_error_handling_examples()
    
    # Performance benchmarks
    await run_performance_benchmarks()
    
    print("\n🎉 All API examples completed!")
    print("\n💡 Next Steps:")
    print("- Use these patterns in your own integrations")
    print("- Implement proper error handling and retries")
    print("- Add logging and monitoring")
    print("- Consider rate limiting and caching")


if __name__ == "__main__":
    asyncio.run(main())
