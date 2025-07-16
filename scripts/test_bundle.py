#!/usr/bin/env python3
"""
Test script for Skyward Assistable Bundle components
"""

import os
import sys
import asyncio
import json
from datetime import datetime

# Add components to path
sys.path.append('components')

def test_environment_variables():
    """Test that required environment variables are set"""
    print("🔍 Testing environment variables...")
    
    required_vars = [
        "ASSISTABLE_API_TOKEN",
        "DEFAULT_LOCATION_ID", 
        "DEFAULT_NUMBER_POOL_ID"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
        else:
            print(f"✅ {var} is set")
    
    if missing:
        print(f"❌ Missing required variables: {', '.join(missing)}")
        return False
    
    print("✅ All required environment variables are set")
    return True

def test_component_imports():
    """Test that all components can be imported"""
    print("\n🐍 Testing component imports...")
    
    try:
        from assistable_ai_client import AssistableAIClient
        print("✅ AssistableAIClient imported successfully")
        
        from ghl_client import GoHighLevelClient
        print("✅ GoHighLevelClient imported successfully")
        
        from agent_delegator import AgentDelegator
        print("✅ AgentDelegator imported successfully")
        
        from runtime_hooks import RuntimeHooks
        print("✅ RuntimeHooks imported successfully")
        
        from batch_processor import BatchProcessor
        print("✅ BatchProcessor imported successfully")
        
        print("✅ All components imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Component import failed: {e}")
        return False

def test_component_initialization():
    """Test that components can be initialized"""
    print("\n🔧 Testing component initialization...")
    
    try:
        from assistable_ai_client import AssistableAIClient
        from ghl_client import GoHighLevelClient
        from agent_delegator import AgentDelegator
        from runtime_hooks import RuntimeHooks
        from batch_processor import BatchProcessor
        
        # Test basic initialization
        assistable = AssistableAIClient()
        print("✅ AssistableAIClient initialized")
        
        ghl = GoHighLevelClient()
        print("✅ GoHighLevelClient initialized")
        
        delegator = AgentDelegator()
        print("✅ AgentDelegator initialized")
        
        hooks = RuntimeHooks()
        print("✅ RuntimeHooks initialized")
        
        processor = BatchProcessor()
        print("✅ BatchProcessor initialized")
        
        print("✅ All components initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Component initialization failed: {e}")
        return False

async def test_agent_delegator_logic():
    """Test agent delegator decision logic"""
    print("\n🎯 Testing Agent Delegator logic...")
    
    try:
        from agent_delegator import AgentDelegator
        
        delegator = AgentDelegator()
        
        # Test CRM-related input
        crm_analysis = delegator.analyze_task("Create an assistant for customer service")
        if crm_analysis["recommended_agent"] == "specialist":
            print("✅ CRM task correctly routed to specialist agent")
        else:
            print("❌ CRM task routing failed")
            return False
            
        # Test general input
        general_analysis = delegator.analyze_task("What's the weather like today?")
        if general_analysis["recommended_agent"] == "primary":
            print("✅ General task correctly routed to primary agent")
        else:
            print("❌ General task routing failed")
            return False
        
        print("✅ Agent delegation logic working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Agent delegator test failed: {e}")
        return False

def test_runtime_hooks():
    """Test runtime hooks functionality"""
    print("\n🔔 Testing Runtime Hooks...")
    
    try:
        from runtime_hooks import RuntimeHooks
        
        hooks = RuntimeHooks()
        
        # Test hook emission
        hook = hooks.emit_hook(
            hook_type="test",
            component="test_script",
            data={"message": "Test hook"},
            session_id="test_session"
        )
        
        if hook and hook["hook_type"] == "test":
            print("✅ Hook emission working")
        else:
            print("❌ Hook emission failed")
            return False
        
        # Test hook storage
        if len(hooks.hook_storage) > 0:
            print("✅ Hook storage working")
        else:
            print("❌ Hook storage failed")
            return False
        
        print("✅ Runtime hooks working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Runtime hooks test failed: {e}")
        return False

def test_flow_files():
    """Test that flow files are valid JSON"""
    print("\n📋 Testing flow files...")
    
    flow_dir = "flows"
    if not os.path.exists(flow_dir):
        print("❌ Flows directory not found")
        return False
    
    flow_files = [f for f in os.listdir(flow_dir) if f.endswith('.json')]
    
    for flow_file in flow_files:
        try:
            with open(os.path.join(flow_dir, flow_file), 'r') as f:
                json.load(f)
            print(f"✅ {flow_file} is valid JSON")
        except Exception as e:
            print(f"❌ {flow_file} is invalid: {e}")
            return False
    
    print("✅ All flow files are valid")
    return True

async def run_all_tests():
    """Run all tests"""
    print("🚀 Running Skyward Assistable Bundle Tests\n")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Component Imports", test_component_imports),
        ("Component Initialization", test_component_initialization),
        ("Agent Delegator Logic", test_agent_delegator_logic),
        ("Runtime Hooks", test_runtime_hooks),
        ("Flow Files", test_flow_files)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📝 Running {test_name} test...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📈 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All tests passed! Your bundle is ready for deployment.")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
