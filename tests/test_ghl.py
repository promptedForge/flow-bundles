"""
Tests for GoHighLevelClient component
"""

import pytest
import asyncio
import os
from unittest.mock import AsyncMock, patch, MagicMock

# Import the component
from ghl_client import GoHighLevelClient


class TestGoHighLevelClient:
    """Test cases for GoHighLevelClient component"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = GoHighLevelClient()
        self.client.api_key = "test_ghl_key"
        self.client.location_id = "loc_test123"
        self.client.contact_id = "contact_test456"
        self.client.email = "test@example.com"
        self.client.phone = "+1234567890"
        self.client.first_name = "John"
        self.client.last_name = "Doe"
        self.client.message_text = "Hello from test"
        
    def test_initialization(self):
        """Test component initialization"""
        client = GoHighLevelClient()
        assert client.hooks == []
        assert client.base_url == "https://services.leadconnectorhq.com"
        assert client._location_tokens == {}
        assert hasattr(client, 'emit_hook')
        
    def test_hook_emission(self):
        """Test runtime hook emission"""
        self.client.emit_hooks = True
        hook = self.client.emit_hook("test", {"message": "test hook"})
        
        assert hook is not None
        assert hook["hook_type"] == "test"
        assert hook["component"] == "ghl_client"
        assert "timestamp" in hook
        assert len(self.client.hooks) == 1
        
    def test_hook_emission_disabled(self):
        """Test hook emission when disabled"""
        self.client.emit_hooks = False
        hook = self.client.emit_hook("test", {"message": "test hook"})
        
        assert hook is None
        assert len(self.client.hooks) == 0
        
    @patch.dict(os.environ, {"GHL_API_KEY": "env_key"})
    def test_environment_key_usage(self):
        """Test that component uses environment API key when no input key"""
        client = GoHighLevelClient()
        client.api_key = ""  # Empty input key
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {"success": True}
            
            asyncio.run(client.get_contact())
            
            # Verify request was attempted
            mock_request.assert_called_once()
            
    @pytest.mark.asyncio
    async def test_get_contact_success(self):
        """Test successful contact retrieval"""
        expected_response = {
            "contact": {
                "id": "contact_test456",
                "firstName": "John",
                "lastName": "Doe",
                "email": "test@example.com"
            }
        }
        
        with patch.object(self.client, '_make_request') as mock_request:
            mock_request.return_value = expected_response
            
            result = await self.client.get_contact()
            
            assert result == expected_response
            # Check that hooks were emitted
            assert len(self.client.hooks) >= 2  # pre_task and end_run
            
    @pytest.mark.asyncio
    async def test_get_contact_missing_id(self):
        """Test contact retrieval with missing contact ID"""
        self.client.contact_id = ""
        
        result = await self.client.get_contact()
        
        assert "error" in result
        assert "Contact ID is required" in result["error"]
        
    @pytest.mark.asyncio
    async def test_get_contact_by_email_success(self):
        """Test successful contact lookup by email"""
        expected_response = {
            "contacts": [
                {
                    "id": "contact_test456",
                    "email": "test@example.com",
                    "firstName": "John"
                }
            ]
        }
        
        with patch.object(self.client, '_make_request') as mock_request:
            mock_request.return_value = expected_response
            
            result = await self.client.get_contact_by_email()
            
            assert result == expected_response
            # Verify correct endpoint was called
            mock_request.assert_called_with(
                "GET",
                "/contacts/search",
                params={"email": "test@example.com"},
                location_id="loc_test123"
            )
            
    @pytest.mark.asyncio
    async def test_get_contact_by_email_missing_email(self):
        """Test contact lookup with missing email"""
        self.client.email = ""
        
        result = await self.client.get_contact_by_email()
        
        assert "error" in result
        assert "Email is required" in result["error"]
        
    @pytest.mark.asyncio
    async def test_get_contact_by_phone_success(self):
        """Test successful contact lookup by phone"""
        expected_response = {
            "contacts": [
                {
                    "id": "contact_test456",
                    "phone": "+1234567890"
                }
            ]
        }
        
        with patch.object(self.client, '_make_request') as mock_request:
            mock_request.return_value = expected_response
            
            result = await self.client.get_contact_by_phone()
            
            assert result == expected_response
            
    @pytest.mark.asyncio
    async def test_create_contact_success(self):
        """Test successful contact creation"""
        expected_response = {
            "contact": {
                "id": "contact_new123",
                "firstName": "John",
                "lastName": "Doe",
                "email": "test@example.com",
                "phone": "+1234567890"
            }
        }
        
        with patch.object(self.client, '_make_request') as mock_request:
            mock_request.return_value = expected_response
            
            result = await self.client.create_contact()
            
            assert result == expected_response
            # Check that hooks were emitted
            assert len(self.client.hooks) >= 2  # pre_task and end_run
            
    @pytest.mark.asyncio
    async def test_create_contact_missing_email_and_phone(self):
        """Test contact creation with missing email and phone"""
        self.client.email = ""
        self.client.phone = ""
        
        result = await self.client.create_contact()
        
        assert "error" in result
        assert "Either email or phone is required" in result["error"]
        
    @pytest.mark.asyncio
    async def test_switch_location_success(self):
        """Test successful location switching"""
        new_location = "loc_new789"
        self.client.location_id = new_location
        
        with patch.dict(os.environ, {}, clear=False):
            result = await self.client.switch_location()
            
            assert result["success"] is True
            assert result["location_id"] == new_location
            assert "Switched to location" in result["message"]
            # Check environment was updated
            assert os.environ.get("CURRENT_LOCATION_ID") == new_location
            
    @pytest.mark.asyncio
    async def test_switch_location_missing_id(self):
        """Test location switching with missing location ID"""
        self.client.location_id = ""
        
        result = await self.client.switch_location()
        
        assert "error" in result
        assert "Location ID is required" in result["error"]
        
    @pytest.mark.asyncio
    async def test_api_request_headers(self):
        """Test API request headers are set correctly"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": True}
            mock_client.return_value.__aenter__.return_value.request.return_value = mock_response
            
            await self.client._make_request("GET", "/test")
            
            # Check that request was called with correct headers
            call_args = mock_client.return_value.__aenter__.return_value.request.call_args
            headers = call_args[1]['headers']
            
            assert "Authorization" in headers
            assert "Bearer test_ghl_key" in headers["Authorization"]
            assert headers["Version"] == "2021-07-28"
            assert "Skyward-Langflow-Bundle" in headers["User-Agent"]
            
    @pytest.mark.asyncio
    async def test_location_token_usage(self):
        """Test location-specific token usage"""
        # Set a location-specific token
        location_id = "loc_special123"
        location_token = "special_token_456"
        self.client._location_tokens[location_id] = location_token
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": True}
            mock_client.return_value.__aenter__.return_value.request.return_value = mock_response
            
            await self.client._make_request("GET", "/test", location_id=location_id)
            
            # Check that location-specific token was used
            call_args = mock_client.return_value.__aenter__.return_value.request.call_args
            headers = call_args[1]['headers']
            assert f"Bearer {location_token}" in headers["Authorization"]
            
    @pytest.mark.asyncio
    async def test_api_request_error_handling(self):
        """Test API request error handling"""
        test_cases = [
            (401, "Unauthorized - Check API token or location access"),
            (403, "Forbidden - Insufficient permissions"),
            (429, "Rate limited - Please try again later"),
            (500, "GHL API Error 500:")
        ]
        
        for status_code, expected_error in test_cases:
            with patch('httpx.AsyncClient') as mock_client:
                mock_response = MagicMock()
                mock_response.status_code = status_code
                mock_response.text = f"Server error {status_code}"
                mock_client.return_value.__aenter__.return_value.request.return_value = mock_response
                
                result = await self.client._make_request("GET", "/test")
                
                assert "error" in result
                assert expected_error in result["error"]
                
    @pytest.mark.asyncio
    async def test_execute_operation_get_contact(self):
        """Test execute_operation with get_contact"""
        self.client.operation = "get_contact"
        
        with patch.object(self.client, 'get_contact') as mock_get:
            mock_get.return_value = {"contact": {"id": "contact_test456"}}
            
            result = await self.client.execute_operation()
            
            mock_get.assert_called_once()
            assert result.data == {"contact": {"id": "contact_test456"}}
            
    @pytest.mark.asyncio
    async def test_execute_operation_get_contact_by_email(self):
        """Test execute_operation with get_contact_by_email"""
        self.client.operation = "get_contact_by_email"
        
        with patch.object(self.client, 'get_contact_by_email') as mock_get:
            mock_get.return_value = {"contacts": []}
            
            result = await self.client.execute_operation()
            
            mock_get.assert_called_once()
            assert result.data == {"contacts": []}
            
    @pytest.mark.asyncio
    async def test_execute_operation_create_contact(self):
        """Test execute_operation with create_contact"""
        self.client.operation = "create_contact"
        
        with patch.object(self.client, 'create_contact') as mock_create:
            mock_create.return_value = {"contact": {"id": "contact_new123"}}
            
            result = await self.client.execute_operation()
            
            mock_create.assert_called_once()
            assert result.data == {"contact": {"id": "contact_new123"}}
            
    @pytest.mark.asyncio
    async def test_execute_operation_switch_location(self):
        """Test execute_operation with switch_location"""
        self.client.operation = "switch_location"
        
        with patch.object(self.client, 'switch_location') as mock_switch:
            mock_switch.return_value = {"success": True, "location_id": "loc_test123"}
            
            result = await self.client.execute_operation()
            
            mock_switch.assert_called_once()
            assert result.data == {"success": True, "location_id": "loc_test123"}
            
    @pytest.mark.asyncio
    async def test_execute_operation_not_implemented(self):
        """Test execute_operation with not yet implemented operation"""
        self.client.operation = "update_contact"  # Not fully implemented in test
        
        result = await self.client.execute_operation()
        
        assert "error" in result.data
        assert "not yet implemented" in result.data["error"]
        
    @pytest.mark.asyncio
    async def test_execute_operation_exception(self):
        """Test execute_operation when exception occurs"""
        self.client.operation = "get_contact"
        
        with patch.object(self.client, 'get_contact') as mock_get:
            mock_get.side_effect = Exception("Test exception")
            
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
            {"hook_type": "pre_task", "data": {"action": "get_contact"}},
            {"hook_type": "end_run", "data": {"success": True}}
        ]
        
        result = self.client.get_hooks()
        
        assert result.data == {"hooks": self.client.hooks}
        assert len(result.data["hooks"]) == 2
        
    @patch.dict(os.environ, {"DEFAULT_LOCATION_ID": "env_location123"})
    @pytest.mark.asyncio
    async def test_default_location_from_env(self):
        """Test using default location from environment"""
        self.client.location_id = ""  # No location provided
        
        with patch.object(self.client, '_make_request') as mock_request:
            mock_request.return_value = {"contact": {"id": "test"}}
            
            await self.client.get_contact()
            
            # Verify the environment location was used
            call_args = mock_request.call_args[1]
            assert call_args.get("location_id") == "env_location123"
            
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
            
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test timeout handling"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.request.side_effect = asyncio.TimeoutError()
            
            result = await self.client._make_request("GET", "/test")
            
            assert "error" in result
            assert "Request timeout" in result["error"]


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__])
