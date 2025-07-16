"""
Integration tests for Skyward Assistable Bundle components
Tests component interactions and workflow patterns
"""

import pytest
import asyncio
import os
from unittest.mock import patch, MagicMock, AsyncMock

# Import components
from assistable_ai_client import AssistableAIClient
from ghl_client import GoHighLevelClient
from agent_delegator import AgentDelegator
from runtime_hooks import RuntimeHooks
from batch_processor import BatchProcessor


class TestIntegration:
    """Integration tests for component interactions"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.assistable_client = AssistableAIClient()
        self.ghl_client = GoHighLevelClient()
        self.agent_delegator = AgentDelegator()
        self.runtime_hooks = RuntimeHooks()
        self.batch_processor = BatchProcessor()
        
    def test_component_imports(self):
        """Test that all components can be imported and instantiated"""
        assert self.assistable_client is not None
        assert self.ghl_client is not None
        assert self.agent_delegator is not None
        assert self.runtime_hooks is not None
        assert self.batch_processor is not None
        
    def test_component_hook_compatibility(self):
        """Test that all components have compatible hook systems"""
        components = [
            self.assistable_client,
            self.ghl_client,
            self.agent_delegator,
            self.batch_processor
        ]
        
        for component in components:
            assert hasattr(component, 'emit_hooks')
            assert hasattr(component, 'hooks')
            if hasattr(component, 'emit_hook'):
                # Test hook emission
                component.emit_hooks = True
                hook = component.emit_hook("test", {"test": "data"})
                assert hook is not None
                assert hook["hook_type"] == "test"
                assert "timestamp" in hook
                
    @pytest.mark.asyncio
    async def test_agent_delegator_with_crm_input(self):
        """Test agent delegator with CRM-related input"""
        self.agent_delegator.user_input = "Create an assistant for customer service"
        self.agent_delegator.delegation_mode = "auto_detect"
        self.agent_delegator.enable_hooks = True
        
        result = await self.agent_delegator.delegate_task()
        
        assert result.data["delegation_info"]["agent_used"] == "specialist"
        assert "assistant" in result.data["delegation_info"]["task_analysis"]["keywords_found"]["crm"]
        assert len(self.agent_delegator.hooks) > 0
        
    @pytest.mark.asyncio
    async def test_agent_delegator_with_general_input(self):
        """Test agent delegator with general input"""
        self.agent_delegator.user_input = "What's the weather like today?"
        self.agent_delegator.delegation_mode = "auto_detect"
        self.agent_delegator.enable_hooks = True
        
        result = await self.agent_delegator.delegate_task()
        
        assert result.data["delegation_info"]["agent_used"] == "primary"
        assert len(self.agent_delegator.hooks) > 0
        
    @pytest.mark.asyncio
    async def test_runtime_hooks_aggregation(self):
        """Test runtime hooks aggregating data from multiple components"""
        # Emit hooks from different components
        self.assistable_client.emit_hooks = True
        self.ghl_client.emit_hooks = True
        
        hook1 = self.assistable_client.emit_hook("pre_task", {"action": "create_assistant"})
        hook2 = self.ghl_client.emit_hook("pre_task", {"action": "get_contact"})
        
        # Add hooks to runtime hooks component
        self.runtime_hooks.hook_storage.extend([hook1, hook2])
        self.runtime_hooks.hook_mode = "aggregate"
        
        result = await self.runtime_hooks.process_hooks()
        
        assert "aggregated_sessions" in result.data
        sessions = result.data["aggregated_sessions"]
        assert len(sessions) > 0
        
    @pytest.mark.asyncio
    async def test_batch_processor_with_hooks(self):
        """Test batch processor emitting progress hooks"""
        self.batch_processor.batch_operation = "bulk_ai_calls"
        self.batch_processor.batch_data = [
            {"contact_id": "contact_1"},
            {"contact_id": "contact_2"}
        ]
        self.batch_processor.assistant_id = "asst_test123"
        self.batch_processor.emit_progress_hooks = True
        
        # Mock the batch processing function
        async def mock_process_func(item, index):
            return {"call_id": f"call_{index}", "status": "initiated"}
            
        with patch.object(self.batch_processor, 'bulk_ai_calls_item', side_effect=mock_process_func):
            result = await self.batch_processor.process_batch()
            
            assert "results" in result.data
            assert len(result.data["results"]) == 2
            assert len(self.batch_processor.progress_hooks) > 0
            
            # Check for specific hook types
            hook_types = [h["hook_type"] for h in self.batch_processor.progress_hooks]
            assert "batch_start" in hook_types
            
    def test_hook_filtering_and_monitoring(self):
        """Test hook filtering and monitoring capabilities"""
        # Create test hooks from different components
        test_hooks = [
            {
                "id": "hook_1",
                "hook_type": "pre_task",
                "component": "assistable_ai_client",
                "timestamp": "2025-07-15T10:30:00Z",
                "data": {"action": "create_assistant"}
            },
            {
                "id": "hook_2", 
                "hook_type": "end_run",
                "component": "ghl_client",
                "timestamp": "2025-07-15T10:31:00Z",
                "data": {"action": "get_contact"}
            },
            {
                "id": "hook_3",
                "hook_type": "error",
                "component": "assistable_ai_client", 
                "timestamp": "2025-07-15T10:32:00Z",
                "data": {"error": "API timeout"}
            }
        ]
        
        # Add hooks to runtime hooks component
        self.runtime_hooks.hook_storage.extend(test_hooks)
        
        # Test filtering by component
        self.runtime_hooks.component_filter = "assistable_ai_client"
        filtered = self.runtime_hooks.filter_hooks(test_hooks)
        assert len(filtered) == 2
        assert all(h["component"] == "assistable_ai_client" for h in filtered)
        
        # Test filtering by hook type
        self.runtime_hooks.component_filter = ""
        self.runtime_hooks.filter_type = "error"
        filtered = self.runtime_hooks.filter_hooks(test_hooks)
        assert len(filtered) == 1
        assert filtered[0]["hook_type"] == "error"
        
    def test_hook_summary_generation(self):
        """Test hook summary statistics generation"""
        test_hooks = [
            {"hook_type": "pre_task", "component": "assistable_ai_client", "status": "active"},
            {"hook_type": "pre_task", "component": "ghl_client", "status": "active"},
            {"hook_type": "end_run", "component": "assistable_ai_client", "status": "active"},
            {"hook_type": "error", "component": "batch_processor", "status": "active"}
        ]
        
        summary = self.runtime_hooks.get_hook_summary(test_hooks)
        
        assert summary["total_hooks"] == 4
        assert summary["by_type"]["pre_task"] == 2
        assert summary["by_type"]["end_run"] == 1
        assert summary["by_type"]["error"] == 1
        assert summary["by_component"]["assistable_ai_client"] == 2
        assert summary["by_component"]["ghl_client"] == 1
        assert summary["by_component"]["batch_processor"] == 1
        
    @pytest.mark.asyncio
    async def test_error_propagation_through_hooks(self):
        """Test that errors are properly propagated through hook system"""
        # Setup components to emit hooks
        self.assistable_client.emit_hooks = True
        self.assistable_client.operation = "create_assistant"
        
        # Mock an API failure
        with patch.object(self.assistable_client, 'create_assistant') as mock_create:
            mock_create.side_effect = Exception("API connection failed")
            
            result = await self.assistable_client.execute_operation()
            
            assert "error" in result.data
            
            # Check that error hook was emitted
            error_hooks = [h for h in self.assistable_client.hooks if h["hook_type"] == "error"]
            assert len(error_hooks) > 0
            assert "API connection failed" in error_hooks[0]["data"]["error"]
            
    @pytest.mark.asyncio  
    async def test_workflow_simulation(self):
        """Test simulated end-to-end workflow"""
        # Simulate: User input -> Agent delegation -> CRM operations -> Progress tracking
        
        # Step 1: Agent delegation
        self.agent_delegator.user_input = "Find contact john@example.com and create assistant for follow-up"
        self.agent_delegator.enable_hooks = True
        
        delegation_result = await self.agent_delegator.delegate_task()
        assert delegation_result.data["delegation_info"]["agent_used"] == "specialist"
        
        # Step 2: GHL contact lookup (simulated)
        self.ghl_client.operation = "get_contact_by_email"
        self.ghl_client.email = "john@example.com"
        self.ghl_client.emit_hooks = True
        
        with patch.object(self.ghl_client, '_make_request') as mock_ghl_request:
            mock_ghl_request.return_value = {
                "contacts": [{"id": "contact_123", "email": "john@example.com"}]
            }
            
            contact_result = await self.ghl_client.execute_operation()
            assert "contacts" in contact_result.data
            
        # Step 3: Assistable AI assistant creation (simulated)
        self.assistable_client.operation = "create_assistant"
        self.assistable_client.assistant_name = "Follow-up Assistant"
        self.assistable_client.emit_hooks = True
        
        with patch.object(self.assistable_client, '_make_request') as mock_assistable_request:
            mock_assistable_request.return_value = {
                "assistant_id": "asst_followup123",
                "name": "Follow-up Assistant"
            }
            
            assistant_result = await self.assistable_client.execute_operation()
            assert "assistant_id" in assistant_result.data
            
        # Step 4: Collect and analyze all hooks
        all_hooks = []
        all_hooks.extend(self.agent_delegator.hooks)
        all_hooks.extend(self.ghl_client.hooks)
        all_hooks.extend(self.assistable_client.hooks)
        
        self.runtime_hooks.hook_storage.extend(all_hooks)
        summary = self.runtime_hooks.get_hook_summary(all_hooks)
        
        assert summary["total_hooks"] > 0
        assert "pre_task" in summary["by_type"]
        assert len(summary["session_list"]) > 0
        
    @patch.dict(os.environ, {
        "ASSISTABLE_API_TOKEN": "test_assistable_token",
        "GHL_API_KEY": "test_ghl_key",
        "DEFAULT_LOCATION_ID": "test_location_123"
    })
    def test_environment_variable_integration(self):
        """Test that components properly use environment variables"""
        # Test that components can access environment variables
        client1 = AssistableAIClient()
        client1.api_token = ""  # Should use environment
        
        client2 = GoHighLevelClient()
        client2.api_key = ""  # Should use environment
        client2.location_id = ""  # Should use environment
        
        # Mock requests to verify environment variables are used
        with patch.object(client1, '_make_request') as mock1, \
             patch.object(client2, '_make_request') as mock2:
            
            mock1.return_value = {"success": True}
            mock2.return_value = {"success": True}
            
            # Test that methods don't fail due to missing credentials
            asyncio.run(client1.get_conversation())
            asyncio.run(client2.get_contact_by_email())
            
            # Both should have made requests (indicating credentials were found)
            mock1.assert_called_once()
            mock2.assert_called_once()
            
    def test_component_display_properties(self):
        """Test that components have proper display properties for Langflow"""
        components = [
            (self.assistable_client, "🤖"),
            (self.ghl_client, "👥"),
            (self.agent_delegator, "🎯"),
            (self.runtime_hooks, "🔔"),
            (self.batch_processor, "📦")
        ]
        
        for component, expected_icon in components:
            assert hasattr(component, 'display_name')
            assert hasattr(component, 'description')
            assert hasattr(component, 'icon')
            assert component.icon == expected_icon
            assert len(component.display_name) > 0
            assert len(component.description) > 0
            
    def test_component_input_output_structure(self):
        """Test that components have proper input/output structure"""
        components = [
            self.assistable_client,
            self.ghl_client,
            self.agent_delegator,
            self.runtime_hooks,
            self.batch_processor
        ]
        
        for component in components:
            assert hasattr(component, 'inputs')
            assert hasattr(component, 'outputs')
            assert isinstance(component.inputs, list)
            assert isinstance(component.outputs, list)
            assert len(component.inputs) > 0
            assert len(component.outputs) > 0
            
            # Check that each input has required properties
            for input_item in component.inputs:
                assert hasattr(input_item, 'name')
                assert hasattr(input_item, 'display_name')
                
            # Check that each output has required properties
            for output_item in component.outputs:
                assert hasattr(output_item, 'name')
                assert hasattr(output_item, 'display_name')
                assert hasattr(output_item, 'method')


class TestWorkflowPatterns:
    """Test specific workflow patterns"""
    
    @pytest.mark.asyncio
    async def test_agent_delegation_to_bulk_operations(self):
        """Test delegation pattern leading to bulk operations"""
        delegator = AgentDelegator()
        batch_processor = BatchProcessor()
        
        # User wants bulk calling campaign
        delegator.user_input = "Make calls to all leads from yesterday using our sales assistant"
        delegator.delegation_mode = "auto_detect"
        
        result = await delegator.delegate_task()
        
        # Should route to specialist
        assert result.data["delegation_info"]["agent_used"] == "specialist"
        
        # Should identify bulk operation
        keywords = result.data["delegation_info"]["task_analysis"]["keywords_found"]["crm"]
        assert any(word in keywords for word in ["calls", "bulk", "campaign"])
        
    def test_multi_component_session_tracking(self):
        """Test session tracking across multiple components"""
        session_id = "test_session_123"
        
        # Initialize components with same session
        assistable = AssistableAIClient()
        ghl = GoHighLevelClient() 
        hooks = RuntimeHooks()
        
        # Emit hooks with same session ID
        assistable.emit_hooks = True
        ghl.emit_hooks = True
        
        hook1 = assistable.emit_hook("pre_task", {"action": "create_assistant"})
        hook1["session_id"] = session_id
        
        hook2 = ghl.emit_hook("pre_task", {"action": "get_contact"})
        hook2["session_id"] = session_id
        
        # Add to hooks component
        hooks.hook_storage.extend([hook1, hook2])
        
        # Test session aggregation
        sessions = hooks.aggregate_hooks_by_session([hook1, hook2])
        
        assert session_id in sessions
        assert len(sessions[session_id]["hooks"]) == 2
        assert len(sessions[session_id]["operations"]) >= 1
        
    def test_error_recovery_pattern(self):
        """Test error detection and recovery patterns"""
        hooks = RuntimeHooks()
        
        # Simulate error sequence
        error_hooks = [
            {
                "hook_type": "pre_task",
                "component": "assistable_ai_client",
                "data": {"action": "create_assistant"},
                "timestamp": "2025-07-15T10:30:00Z",
                "session_id": "session_123"
            },
            {
                "hook_type": "error",
                "component": "assistable_ai_client", 
                "data": {"error": "Rate limited", "retry_after": 60},
                "timestamp": "2025-07-15T10:30:30Z",
                "session_id": "session_123"
            }
        ]
        
        hooks.hook_storage.extend(error_hooks)
        sessions = hooks.aggregate_hooks_by_session(error_hooks)
        
        session = sessions["session_123"]
        assert session["status"] == "error"
        assert len(session["errors"]) > 0
        assert "Rate limited" in str(session["errors"])


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__])
