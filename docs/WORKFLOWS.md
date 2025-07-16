# 🔄 Workflow Examples

Practical examples and patterns for using the Skyward Assistable Bundle components.

## 🎯 **Agent Delegation Pattern**

The core pattern that enables external clients to delegate tasks to specialized agents.

### **Architecture Overview**

```
External Client (Forge/Claude Desktop)
         ↓
    Langflow MCP Server (/api/v1/mcp/sse)
         ↓
    Primary Agent (Natural Language Interface)
         ↓
    Agent Delegator (Task Analysis & Routing)
         ↓
    Specialist Agent (CRM Expert)
         ↓
    API Components (Assistable AI + GoHighLevel)
         ↓
    Runtime Hooks (Progress Notifications)
         ↑
    Back to Primary Agent → External Client
```

---

## 🛠️ **Basic Workflows**

### **Workflow 1: Simple Assistant Creation**

**Use Case**: Create a new AI assistant for a specific purpose.

**Components Flow**:
```
ChatInput → AssistableAIClient → ChatOutput
              ↓
        RuntimeHooks (monitoring)
```

**Configuration**:

1. **AssistableAIClient**:
   ```yaml
   operation: create_assistant
   assistant_name: "Customer Support Bot"
   assistant_description: "AI assistant for customer service inquiries"
   input_text: "You are a helpful customer service representative..."
   emit_hooks: true
   ```

2. **RuntimeHooks**:
   ```yaml
   hook_mode: monitor
   real_time_updates: true
   ```

**Expected Flow**:
1. User provides assistant details
2. Component emits `pre_task` hook
3. API call creates assistant
4. Component emits `end_run` hook
5. Assistant ID returned to user

**Sample Input**:
```
"Create a customer service assistant that can help with billing questions"
```

**Sample Output**:
```json
{
  "assistant_id": "asst_abc123",
  "name": "Customer Support Bot", 
  "description": "AI assistant for customer service inquiries",
  "location_id": "waq32uRFJqZ8Sjb9Hoql",
  "created_at": "2025-07-15T10:30:00Z"
}
```

### **Workflow 2: Contact Lookup and Messaging**

**Use Case**: Find a contact and send them a message.

**Components Flow**:
```
ChatInput → GoHighLevelClient (lookup) → GoHighLevelClient (message) → ChatOutput
                      ↓                            ↓
                RuntimeHooks ←────────────────────┘
```

**Configuration**:

1. **First GoHighLevelClient** (Contact Lookup):
   ```yaml
   operation: get_contact_by_email
   email: "customer@example.com"
   emit_hooks: true
   ```

2. **Second GoHighLevelClient** (Send Message):
   ```yaml
   operation: create_message
   contact_id: "{from_previous_component}"
   message_text: "Thank you for your inquiry!"
   emit_hooks: true
   ```

**Expected Flow**:
1. Look up contact by email
2. Extract contact ID from result
3. Send message to contact
4. Return message confirmation

---

## 🎯 **Agent Delegation Workflows**

### **Workflow 3: Intelligent Task Delegation**

**Use Case**: External client makes request, system automatically routes to appropriate agent.

**Components Flow**:
```
ChatInput → AgentDelegator → [Conditional Routing] → ChatOutput
              ↓                       ↓
        Task Analysis            Specialist Tools
              ↓                       ↓
        RuntimeHooks ←─────────────────┘
```

**Configuration**:

1. **AgentDelegator**:
   ```yaml
   delegation_mode: auto_detect
   enable_hooks: true
   primary_system_prompt: "You are a general assistant that delegates CRM tasks to specialists."
   specialist_system_prompt: "You are a CRM expert with access to Assistable AI and GoHighLevel tools."
   ```

2. **Specialist Tools** (Connected via specialist_tools input):
   - AssistableAIClient components
   - GoHighLevelClient components

**Sample Inputs and Routing**:

| Input | Detected Agent | Reason |
|-------|----------------|---------|
| `"Create an assistant for sales calls"` | Specialist | CRM keywords: assistant, sales, calls |
| `"What's the weather like?"` | Primary | General conversation |
| `"Find contact john@example.com"` | Specialist | CRM keywords: contact, find |
| `"Help me understand AI"` | Primary | General help request |
| `"Make calls to all leads from yesterday"` | Specialist | CRM keywords: calls, leads |

**Task Analysis Output**:
```json
{
  "input": "Create an assistant for sales calls",
  "crm_score": 3,
  "natural_score": 0,
  "keywords_found": {
    "crm": ["assistant", "sales", "calls"],
    "natural": []
  },
  "recommended_agent": "specialist",
  "confidence": 0.15,
  "delegation_reason": "Multiple CRM keywords detected, requires specialist knowledge"
}
```

### **Workflow 4: Multi-Step CRM Operation**

**Use Case**: Complex CRM workflow requiring multiple operations.

**Components Flow**:
```
ChatInput → AgentDelegator → GoHighLevelClient (contact lookup)
              ↓                      ↓
        [If Specialist]        AssistableAIClient (create assistant)
              ↓                      ↓
        RuntimeHooks ←─── AssistableAIClient (make call) ← ChatOutput
```

**Configuration Example**:

```yaml
# Agent Delegator
delegation_mode: auto_detect
user_input: "Create a sales assistant and call john@example.com about our new product"

# This would route to specialist and execute:
# 1. Look up contact by email
# 2. Create sales assistant
# 3. Initiate AI call to contact
```

**Runtime Hooks Flow**:
```json
[
  {
    "hook_type": "task_analysis",
    "data": {"recommended_agent": "specialist"}
  },
  {
    "hook_type": "pre_task", 
    "data": {"agent": "specialist", "action": "multi_step_crm"}
  },
  {
    "hook_type": "pre_task",
    "data": {"action": "get_contact_by_email", "email": "john@example.com"}
  },
  {
    "hook_type": "end_run",
    "data": {"action": "get_contact_by_email", "contact_id": "contact_123"}
  },
  {
    "hook_type": "pre_task",
    "data": {"action": "create_assistant", "name": "Sales Assistant"}
  },
  {
    "hook_type": "end_run", 
    "data": {"action": "create_assistant", "assistant_id": "asst_456"}
  },
  {
    "hook_type": "pre_task",
    "data": {"action": "make_ai_call", "contact_id": "contact_123"}
  },
  {
    "hook_type": "end_run",
    "data": {"action": "make_ai_call", "call_id": "call_789"}
  }
]
```

---

## 📦 **Batch Processing Workflows**

### **Workflow 5: AI Calling Campaign**

**Use Case**: Launch a bulk calling campaign to multiple contacts.

**Components Flow**:
```
DataInput (contact list) → BatchProcessor → RuntimeHooks → DataOutput (results)
                              ↓               ↓
                        Progress Tracking    Real-time Updates
```

**Configuration**:

1. **DataInput** (Campaign Data):
   ```json
   [
     {"contact_id": "contact_123"},
     {"contact_id": "contact_456"},
     {"contact_id": "contact_789"}
   ]
   ```

2. **BatchProcessor**:
   ```yaml
   batch_operation: bulk_ai_calls
   assistant_id: "asst_sales_bot"
   batch_size: 5
   delay_between_batches: 10
   emit_progress_hooks: true
   stop_on_error: false
   ```

3. **RuntimeHooks**:
   ```yaml
   hook_mode: aggregate
   component_filter: batch_processor
   real_time_updates: true
   ```

**Progress Tracking**:
```json
{
  "batch_start": {
    "total_items": 100,
    "estimated_duration": "10-15 minutes"
  },
  "chunk_progress": {
    "processed": 20,
    "remaining": 80,
    "success_rate": 0.95
  },
  "batch_complete": {
    "successful": 95,
    "failed": 5,
    "total_duration": "12 minutes"
  }
}
```

### **Workflow 6: Lead Qualification Pipeline**

**Use Case**: Process a list of leads through qualification workflow.

**Components Flow**:
```
DataInput (leads) → BatchProcessor (contact lookup) → BatchProcessor (assistant creation) → BatchProcessor (qualification calls) → DataOutput (qualified leads)
                        ↓                                    ↓                               ↓
                   RuntimeHooks ←──────────────────────────────────────────────────────────┘
```

**Multi-Stage Configuration**:

1. **Stage 1 - Contact Lookup**:
   ```yaml
   batch_operation: bulk_contact_lookup
   batch_data: [{"email": "lead1@example.com"}, {"email": "lead2@example.com"}]
   ```

2. **Stage 2 - Assistant Creation** (if needed):
   ```yaml
   batch_operation: bulk_create_assistants
   batch_data: [{"name": "Qualifier Bot", "description": "Lead qualification assistant"}]
   ```

3. **Stage 3 - Qualification Calls**:
   ```yaml
   batch_operation: bulk_ai_calls
   assistant_id: "asst_qualifier"
   batch_data: [{"contact_id": "contact_123"}, {"contact_id": "contact_456"}]
   ```

**Workflow Orchestration**:
```python
# Pseudo-code for chaining batch operations
leads_input → contact_lookup_batch → assistant_creation → qualification_calls → results_output
```

---

## 🔄 **Real-Time Monitoring Workflows**

### **Workflow 7: Live Campaign Dashboard**

**Use Case**: Monitor ongoing operations with real-time updates.

**Components Flow**:
```
Multiple Operations → RuntimeHooks (aggregation) → Real-time Dashboard
     ↓                      ↓
Batch Processors    Hook Aggregation
     ↓                      ↓  
API Components      Session Tracking
```

**Configuration for Monitoring**:

1. **RuntimeHooks** (Dashboard):
   ```yaml
   hook_mode: aggregate
   real_time_updates: true
   retention_minutes: 120
   max_hooks: 500
   ```

2. **All Operation Components**:
   ```yaml
   emit_hooks: true
   emit_progress_hooks: true
   ```

**Dashboard Data Structure**:
```json
{
  "sessions": {
    "campaign_001": {
      "status": "active",
      "operations": ["bulk_ai_calls", "contact_lookup"],
      "progress": {
        "total_items": 100,
        "completed": 45,
        "success_rate": 0.93
      },
      "timeline": [
        {"time": "10:30:00", "event": "Campaign started"},
        {"time": "10:35:00", "event": "First batch completed"},
        {"time": "10:40:00", "event": "50% progress reached"}
      ]
    }
  },
  "real_time_feed": [
    {"timestamp": "10:45:30", "event": "Contact 789 call completed successfully"},
    {"timestamp": "10:45:25", "event": "Contact 456 call initiated"}
  ]
}
```

### **Workflow 8: Error Monitoring and Recovery**

**Use Case**: Detect and respond to operation failures.

**Components Flow**:
```
Operations → RuntimeHooks (error detection) → [Conditional Logic] → Recovery Actions
     ↓              ↓                               ↓
Error Events    Error Analysis                 Retry/Alert
```

**Error Detection Configuration**:

1. **RuntimeHooks** (Error Monitor):
   ```yaml
   hook_mode: filter
   filter_type: error
   real_time_updates: true
   ```

2. **Error Response Logic**:
   ```python
   # Pseudo-code for error handling
   if error_type == "rate_limited":
       increase_delay_between_batches()
   elif error_type == "unauthorized":
       alert_admin("Check API credentials")
   elif error_type == "timeout":
       retry_with_longer_timeout()
   ```

**Error Recovery Patterns**:
```json
{
  "error_patterns": {
    "rate_limiting": {
      "action": "exponential_backoff",
      "parameters": {"initial_delay": 5, "max_delay": 60}
    },
    "network_timeout": {
      "action": "retry",
      "parameters": {"max_retries": 3, "timeout_increase": 15}
    },
    "authentication_failure": {
      "action": "alert_and_pause",
      "parameters": {"notification": "admin@example.com"}
    }
  }
}
```

---

## 🎯 **Advanced Integration Patterns**

### **Workflow 9: Multi-Location Agency Management**

**Use Case**: Manage operations across multiple GoHighLevel locations.

**Components Flow**:
```
Location Input → GoHighLevelClient (switch) → [Location-Specific Operations] → Results Aggregation
     ↓                    ↓                            ↓
Location List      Token Management              Per-Location Results
```

**Multi-Location Configuration**:

1. **Location Switching**:
   ```yaml
   operation: switch_location
   location_id: "location_chicago"
   ```

2. **Location-Aware Operations**:
   ```yaml
   # Each operation automatically uses current location context
   operation: get_contact_by_email
   email: "customer@example.com"
   # Will search in currently active location
   ```

**Agency Workflow**:
```python
# Pseudo-code for multi-location workflow
for location in agency_locations:
    switch_location(location.id)
    contacts = get_location_contacts()
    campaigns = run_location_campaigns(contacts)
    results[location.name] = campaigns
```

### **Workflow 10: Integration with External MCP Clients**

**Use Case**: External tools (Claude Desktop, Cursor) using your Langflow as MCP server.

**MCP Server Endpoint**:
```
https://langflowailangflowlatest-production-0054.up.railway.app/api/v1/mcp/sse
```

**External Client Configuration**:

1. **Claude Desktop** (`claude_desktop_config.json`):
   ```json
   {
     "mcpServers": {
       "Skyward-CRM": {
         "url": "https://langflowailangflowlatest-production-0054.up.railway.app/api/v1/mcp/sse"
       }
     }
   }
   ```

2. **Cursor MCP Settings**:
   ```json
   {
     "mcpServers": {
       "Langflow-CRM": {
         "url": "https://langflowailangflowlatest-production-0054.up.railway.app/api/v1/mcp/sse"
       }
     }
   }
   ```

**External Usage Examples**:

From Claude Desktop:
```
"Use the Skyward-CRM tools to create a sales assistant and call all leads from this week"
→ Claude calls your Langflow flows as MCP tools
→ Flows execute with full agent delegation
→ Results returned to Claude Desktop
```

From Cursor:
```
"Help me analyze the CRM data and suggest follow-up actions"
→ Cursor accesses your CRM flows
→ Data analysis performed by specialist agents
→ Recommendations returned to Cursor
```

---

## 📋 **Best Practices**

### **Component Configuration**

1. **Always Enable Hooks for Monitoring**:
   ```yaml
   emit_hooks: true
   emit_progress_hooks: true
   ```

2. **Set Appropriate Timeouts**:
   ```yaml
   timeout: 60  # For slow operations
   timeout: 30  # For standard operations
   ```

3. **Use Environment Variables**:
   ```yaml
   # Let components use environment defaults
   api_token: ""  # Uses ASSISTABLE_API_TOKEN
   location_id: ""  # Uses DEFAULT_LOCATION_ID
   ```

### **Error Handling**

1. **Always Plan for Failures**:
   ```yaml
   stop_on_error: false  # For batch operations
   timeout_per_item: 45  # Reasonable timeouts
   ```

2. **Monitor Error Rates**:
   ```yaml
   # Use RuntimeHooks to track success rates
   hook_mode: aggregate
   filter_type: error
   ```

### **Performance Optimization**

1. **Batch Size Tuning**:
   ```yaml
   batch_size: 5   # Start small
   delay_between_batches: 2  # Prevent rate limiting
   ```

2. **Hook Management**:
   ```yaml
   max_hooks: 100  # Limit memory usage
   retention_minutes: 60  # Auto cleanup
   auto_cleanup: true
   ```

### **Security Considerations**

1. **Use Environment Variables**:
   ```bash
   # Never hardcode credentials in flows
   ASSISTABLE_API_TOKEN=your_token
   GHL_API_KEY=your_key
   ```

2. **Limit Access**:
   ```yaml
   # Use location-specific tokens when possible
   # Monitor API usage for unusual patterns
   ```

---

## 🔧 **Troubleshooting Workflows**

### **Debugging Failed Operations**

1. **Check Runtime Hooks**:
   ```yaml
   # Add RuntimeHooks to any failing workflow
   hook_mode: monitor
   real_time_updates: true
   ```

2. **Test Components Individually**:
   ```yaml
   # Start with simple operations
   operation: get_assistant
   # No additional inputs required
   ```

3. **Verify Environment Variables**:
   ```bash
   # Test API connectivity
   curl -H "Authorization: Bearer $ASSISTABLE_API_TOKEN" \
        https://api.assistable.ai/v2/get-assistant
   ```

### **Performance Issues**

1. **Monitor Hook Statistics**:
   ```yaml
   # Use RuntimeHooks summary to identify bottlenecks
   hook_mode: aggregate
   ```

2. **Optimize Batch Sizes**:
   ```yaml
   # Reduce if timeouts occur
   batch_size: 3
   delay_between_batches: 5
   ```

3. **Check Resource Usage**:
   ```yaml
   # Reduce memory usage
   max_hooks: 50
   retention_minutes: 30
   ```

---

These workflows provide a comprehensive foundation for building AI automation systems with the Skyward Assistable Bundle. Start with basic workflows and gradually implement more complex patterns as needed.

For detailed component configuration, see [API_REFERENCE.md](API_REFERENCE.md).
For troubleshooting help, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
