"""
Tests for AssistableAIClient component
"""

import pytest
import asyncio
import os
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

# Import the component
from assistable_ai_client import AssistableAIClient


class TestAssistableAIClient:
    """Test cases for AssistableAIClient component"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = AssistableAIClient()
        self.client.api_token = "test_token"
        self.client.assistant_id = "asst_test123"
        self.client.location_id = "loc_test456"
        self.client.assistant_name = "Test Assistant"
        self.client.assistant_description = "Test Description"
        self.client.input_text = "Hello, world!"
        
    def test_initialization(self):
        """Test component initialization"""
        client = AssistableAIClient()
        assert client.hooks == []
        assert client.base_url == "https://api.assistable.ai/v2"
        assert hasattr(client, 'emit_hook')
        
    def test_hook_emission(self):
        """Test runtime hook emission"""
        # Test hook emission enabled
        self.client.emit_hooks = True
        hook = self.client.emit_hook("test", {"message": "test hook"})
        
        assert hook is not None
        assert hook["hook_type"] == "test"
        assert hook["component"] == "assistable_ai_client"
        assert "timestamp" in hook
        assert len(self.client.hooks) == 1
        
    def test_hook_emission_disabled(self):
        """Test hook emission when disabled"""
        self.client.emit_hooks = False
        hook = self.client.emit_hook("test", {"message": "test hook"})
        
        assert hook is None
        assert len(self.client.hooks) == 0
        
    @patch.dict(os.environ, {"ASSISTABLE_API_TOKEN": "env_token"})
    def test_environment_token_usage(self):
        """Test that component uses environment token when no input token"""
        client = AssistableAIClient()
        client.api_token = ""  # Empty input token
        
        # Mock the _make_request to check what token is used
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {"success": True}
            
            # This should trigger token retrieval from environment
            # We'll verify indirectly by checking the request was made
            asyncio.run(client.get_conversation())
            
            # Verify request was attempted (would fail with no token if env not used)
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_assistant_success(self):
        """Test successful assistant creation"""
        expected_response = {
            "assistant_id": "asst_new123",
            "name": "Test Assistant",
            "description": "Test Description"
        }
        
        with patch.object(self.client, '_make_request') as mock_request:
            mock_request.return_value = expected_response
            
            result = await self.client.create_assistant()
            
            assert result == expected_response
            # Check that hooks were emitted
            assert len(self.client.hooks) >= 2  # pre_task and end_run
            
    @pytest.mark.asyncio
    async def test_create_assistant_missing_location(self):
        """Test assistant creation with missing location ID"""
        self.client.location_id = ""
        
        with patch.dict(os.environ, {}, clear=True):  # Clear environment
            result = await self.client.create_assistant()
            
            assert "error" in result
            assert "Location ID is required" in result["error"]
            
    @pytest.mark.asyncio
    async def test_chat_completion_success(self):
        """Test successful chat completion"""
        expected_response = {
            "conversation_id": "conv_test789",
            "response": "Hello! How can I help?",
            "assistant_id": "asst_test123"
        }
        
        with patch.object(self.client, '_make_request') as mock_request:
            mock_request.return_value = expected_response
            
            result = await self.client.chat_completion()
            
            assert result == expected_response
            # Verify conversation ID was auto-generated if not provided
            assert self.client.conversation_id or "conv_" in str(mock_request.call_args)
            
    @pytest.mark.asyncio
    async def test_make_ai_call_success(self):
        """Test successful AI call initiation"""
        self.client.contact_id = "contact_test456"
        self.client.number_pool_id = "pool_test789"
        
        expected_response = {
            "call_id": "call_test123",
            "status": "initiated",
            "contact_id": "contact_test456"
        }
        
        with patch.object(self.client, '_make_request') as mock_request:
            mock_request.return_value = expected_response
            
            result = await self.client.make_ai_call()
            
            assert result == expected_response
            
    @pytest.mark.asyncio
    async def test_make_ai_call_missing_fields(self):
        """Test AI call with missing required fields"""
        self.client.contact_id = ""  # Missing required field
        
        result = await self.client.make_ai_call()
        
        assert "error" in result
        assert "Missing required fields" in result["error"]
        
    @pytest.mark.asyncio
    async def test_api_request_timeout(self):
        """Test API request timeout handling"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.request.side_effect = asyncio.TimeoutError()
            
            result = await self.client._make_request("GET", "/test")
            
            assert "error" in result
            assert "Request timeout" in result["error"]
            
    @pytest.mark.asyncio
    async def test_api_request_unauthorized(self):
        """Test API request unauthorized response"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_client.return_value.__aenter__.return_value.request.return_value = mock_response
            
            result = await self.client._make_request("GET", "/test")
            
            assert "error" in result
            assert "Unauthorized" in result["error"]
            
    @pytest.mark.asyncio
    async def test_api_request_rate_limited(self):
        """Test API request rate limited response"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_client.return_value.__aenter__.return_value.request.return_value = mock_response
            
            result = await self.client._make_request("GET", "/test")
            
            assert "error" in result
            assert "Rate limited" in result["error"]
            
    @pytest.mark.asyncio
    async def test_execute_operation_create_assistant(self):
        """Test execute_operation with create_assistant"""
        self.client.operation = "create_assistant"
        
        with patch.object(self.client, 'create_assistant') as mock_create:
            mock_create.return_value = {"assistant_id": "asst_test123"}
            
            result = await self.client.execute_operation()
            
            mock_create.assert_called_once()
            assert result.data == {"assistant_id": "asst_test123"}
            
    @pytest.mark.asyncio
    async def test_execute_operation_chat_completion(self):
        """Test execute_operation with chat_completion"""
        self.client.operation = "chat_completion"
        
        with patch.object(self.client, 'chat_completion') as mock_chat:
            mock_chat.return_value = {"response": "Hello!"}
            
            result = await self.client.execute_operation()
            
            mock_chat.assert_called_once()
            assert result.data == {"response": "Hello!"}
            
    @pytest.mark.asyncio
    async def test_execute_operation_make_ai_call(self):
        """Test execute_operation with make_ai_call"""
        self.client.operation = "make_ai_call"
        
        with patch.object(self.client, 'make_ai_call') as mock_call:
            mock_call.return_value = {"call_id": "call_test123"}
            
            result = await self.client.execute_operation()
            
            mock_call.assert_called_once()
            assert result.data == {"call_id": "call_test123"}
            
    @pytest.mark.asyncio
    async def test_execute_operation_unknown(self):
        """Test execute_operation with unknown operation"""
        self.client.operation = "unknown_operation"
        
        result = await self.client.execute_operation()
        
        assert "error" in result.data
        assert "Unknown operation" in result.data["error"]
        
    @pytest.mark.asyncio
    async def test_execute_operation_exception(self):
        """Test execute_operation when exception occurs"""
        self.client.operation = "create_assistant"
        
        with patch.object(self.client, 'create_assistant') as mock_create:
            mock_create.side_effect = Exception("Test exception")
            
            result = await self.client.execute_operation()
            
            assert "error" in result.data
            assert "Operation failed" in result.data["error"]
            # Check error hook was emitted
            error_hooks = [h for h in self.client.hooks if h["hook_type"] == "error"]
            assert len(error_hooks) > 0
            
    def test_get_hooks(self):
        """Test get_hooks method"""
        # Add some test hooks
        self.client.hooks = [
            {"hook_type": "test1", "data": {}},
            {"hook_type": "test2", "data": {}}
        ]
        
        result = self.client.get_hooks()
        
        assert result.data == {"hooks": self.client.hooks}
        assert len(result.data["hooks"]) == 2
        
    @pytest.mark.asyncio
    async def test_conversation_id_generation(self):
        """Test automatic conversation ID generation"""
        self.client.conversation_id = ""  # No conversation ID provided
        
        with patch.object(self.client, '_make_request') as mock_request:
            mock_request.return_value = {"success": True}
            
            await self.client.chat_completion()
            
            # Check that a conversation ID was generated and used
            call_args = mock_request.call_args[1]["data"]
            assert "conversation_id" in call_args
            assert call_args["conversation_id"].startswith("conv_")
            
    @pytest.mark.asyncio
    async def test_json_response_parsing(self):
        """Test JSON response parsing"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"test": "data"}
            mock_client.return_value.__aenter__.return_value.request.return_value = mock_response
            
            result = await self.client._make_request("GET", "/test")
            
            assert result == {"test": "data"}
            
    @pytest.mark.asyncio
    async def test_non_json_response_handling(self):
        """Test handling of non-JSON responses"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.side_effect = Exception("Not JSON")
            mock_response.text = "Plain text response"
            mock_client.return_value.__aenter__.return_value.request.return_value = mock_response
            
            result = await self.client._make_request("GET", "/test")
            
            assert result == {"success": True, "response": "Plain text response"}


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__])
