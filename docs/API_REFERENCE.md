# 📚 API Reference

Complete reference for all Skyward Assistable Bundle components.

## 🤖 AssistableAIClient

Direct integration with Assistable AI API for creating assistants and managing conversations.

### Configuration

| Input | Type | Required | Description | Default |
|-------|------|----------|-------------|---------|
| `api_token` | str | No* | Assistable AI API token | `ASSISTABLE_API_TOKEN` env |
| `operation` | dropdown | Yes | Operation to perform | `chat_completion` |
| `assistant_id` | str | No | Assistant ID for operations | - |
| `conversation_id` | str | No | Conversation ID (auto-generated if empty) | - |
| `location_id` | str | No | GoHighLevel location ID | `DEFAULT_LOCATION_ID` env |
| `input_text` | str | No | Message content or assistant prompt | - |
| `assistant_name` | str | No | Name for new assistant | - |
| `assistant_description` | str | No | Description for new assistant | - |
| `contact_id` | str | No | GoHighLevel contact ID for AI calls | - |
| `number_pool_id` | str | No | Phone number pool for AI calls | `DEFAULT_NUMBER_POOL_ID` env |
| `emit_hooks` | bool | No | Enable runtime hook notifications | `true` |
| `timeout` | int | No | API request timeout in seconds | `30` |

### Operations

#### `create_assistant`
Creates a new AI assistant in Assistable AI.

**Required Inputs:**
- `assistant_name` - Name for the assistant
- `assistant_description` - Description of the assistant's purpose
- `input_text` - System prompt for the assistant

**Response:**
```json
{
  "assistant_id": "asst_abc123",
  "name": "Customer Service Bot",
  "description": "AI assistant for customer support",
  "location_id": "waq32uRFJqZ8Sjb9Hoql",
  "created_at": "2025-07-15T10:30:00Z"
}
```

**Runtime Hooks:**
- `pre_task`: Before assistant creation
- `start_task`: Creation initiated
- `end_run`: Assistant created successfully

#### `chat_completion`
Process a chat completion with an existing assistant.

**Required Inputs:**
- `assistant_id` - ID of the assistant to chat with
- `input_text` - User message

**Response:**
```json
{
  "conversation_id": "conv_xyz789",
  "response": "Hello! How can I help you today?",
  "assistant_id": "asst_abc123",
  "message_id": "msg_def456"
}
```

#### `make_ai_call`
Initiate an AI-powered phone call through GoHighLevel integration.

**Required Inputs:**
- `assistant_id` - Assistant to use for the call
- `contact_id` - GoHighLevel contact to call
- `number_pool_id` - Phone number pool for outbound call

**Response:**
```json
{
  "call_id": "call_ghi789",
  "status": "initiated",
  "contact_id": "contact_123",
  "assistant_id": "asst_abc123",
  "initiated_at": "2025-07-15T10:30:00Z"
}
```

#### `get_conversation`
Retrieve conversation history.

**Optional Inputs:**
- `conversation_id` - Specific conversation to retrieve

**Response:**
```json
{
  "conversation_id": "conv_xyz789",
  "messages": [
    {
      "message_id": "msg_001",
      "role": "user",
      "content": "Hello",
      "timestamp": "2025-07-15T10:30:00Z"
    }
  ]
}
```

#### `create_message`
Create a new message in a conversation.

**Required Inputs:**
- `input_text` - Message content

**Response:**
```json
{
  "message_id": "msg_def456",
  "conversation_id": "conv_xyz789",
  "content": "Hello there!",
  "created_at": "2025-07-15T10:30:00Z"
}
```

#### `update_assistant`
Update an existing assistant's configuration.

**Required Inputs:**
- `assistant_id` - Assistant to update

**Optional Inputs:**
- `assistant_name` - New name
- `assistant_description` - New description
- `input_text` - New system prompt

#### `delete_assistant`
Delete an assistant.

**Required Inputs:**
- `assistant_id` - Assistant to delete

#### `create_flow`
Create a new flow in Assistable AI.

**Response:**
```json
{
  "flow_id": "flow_abc123",
  "location_id": "waq32uRFJqZ8Sjb9Hoql",
  "created_at": "2025-07-15T10:30:00Z"
}
```

### Error Handling

All operations return error information in case of failure:

```json
{
  "error": "Unauthorized - Check API token",
  "operation": "create_assistant",
  "timestamp": "2025-07-15T10:30:00Z"
}
```

Common errors:
- `"Unauthorized - Check API token"` - Invalid or missing API token
- `"Rate limited - Please try again later"` - API rate limit exceeded
- `"Request timeout"` - Operation took longer than timeout setting
- `"Missing required field: assistant_id"` - Required parameter not provided

---

## 👥 GoHighLevelClient

Direct integration with GoHighLevel v2 API for CRM operations.

### Configuration

| Input | Type | Required | Description | Default |
|-------|------|----------|-------------|---------|
| `api_key` | str | No* | GoHighLevel API key | `GHL_API_KEY` env |
| `operation` | dropdown | Yes | CRM operation to perform | `get_contact` |
| `location_id` | str | No | Location/subaccount ID | `DEFAULT_LOCATION_ID` env |
| `contact_id` | str | No | Contact ID for operations | - |
| `email` | str | No | Contact email address | - |
| `phone` | str | No | Contact phone number | - |
| `first_name` | str | No | Contact first name | - |
| `last_name` | str | No | Contact last name | - |
| `message_text` | str | No | Message content to send | - |
| `tag_name` | str | No | Tag to add/remove | - |
| `conversation_id` | str | No | GHL conversation ID | - |
| `emit_hooks` | bool | No | Enable runtime hook notifications | `true` |
| `timeout` | int | No | API request timeout in seconds | `30` |

### Operations

#### `get_contact`
Retrieve contact information by ID.

**Required Inputs:**
- `contact_id` - GoHighLevel contact ID

**Response:**
```json
{
  "contact": {
    "id": "contact_123",
    "firstName": "John",
    "lastName": "Doe", 
    "email": "john@example.com",
    "phone": "+1234567890",
    "tags": ["lead", "interested"],
    "customFields": {},
    "locationId": "waq32uRFJqZ8Sjb9Hoql"
  }
}
```

#### `get_contact_by_email`
Find contact by email address.

**Required Inputs:**
- `email` - Contact email to search for

**Response:**
```json
{
  "contacts": [
    {
      "id": "contact_123",
      "firstName": "John",
      "lastName": "Doe",
      "email": "john@example.com",
      "phone": "+1234567890"
    }
  ]
}
```

#### `get_contact_by_phone`
Find contact by phone number.

**Required Inputs:**
- `phone` - Contact phone to search for

#### `create_contact`
Create a new contact in GoHighLevel.

**Required Inputs:**
- Either `email` or `phone` (or both)

**Optional Inputs:**
- `first_name` - Contact first name
- `last_name` - Contact last name

**Response:**
```json
{
  "contact": {
    "id": "contact_456",
    "firstName": "Jane",
    "lastName": "Smith",
    "email": "jane@example.com",
    "phone": "+1987654321",
    "locationId": "waq32uRFJqZ8Sjb9Hoql",
    "dateAdded": "2025-07-15T10:30:00Z"
  }
}
```

#### `update_contact`
Update an existing contact.

**Required Inputs:**
- `contact_id` - Contact to update

**Optional Inputs:**
- `email`, `phone`, `first_name`, `last_name` - Fields to update

#### `get_conversation`
Retrieve conversation messages for a contact.

**Required Inputs:**
- Either `conversation_id` or `contact_id`

**Response:**
```json
{
  "conversation": {
    "id": "conv_ghl_123",
    "contactId": "contact_123",
    "messages": [
      {
        "id": "msg_001",
        "body": "Hello!",
        "type": "SMS",
        "direction": "inbound",
        "dateAdded": "2025-07-15T10:30:00Z"
      }
    ]
  }
}
```

#### `create_message`
Send a message to a contact.

**Required Inputs:**
- `contact_id` - Contact to message
- `message_text` - Message content

**Optional Inputs:**
- `conversation_id` - Existing conversation ID

#### `switch_location`
Switch context to a different GoHighLevel location/subaccount.

**Required Inputs:**
- `location_id` - New location to switch to

**Response:**
```json
{
  "success": true,
  "message": "Switched to location waq32uRFJqZ8Sjb9Hoql",
  "location_id": "waq32uRFJqZ8Sjb9Hoql"
}
```

---

## 🎯 AgentDelegator

Intelligent task delegation between Primary and Specialist agents with runtime hooks.

### Configuration

| Input | Type | Required | Description | Default |
|-------|------|----------|-------------|---------|
| `user_input` | str | Yes | Natural language input from external client | - |
| `delegation_mode` | dropdown | Yes | How to handle task delegation | `auto_detect` |
| `specialist_tools` | Data | No | Available tools for specialist agent | - |
| `context_data` | Data | No | Additional context for task execution | - |
| `enable_hooks` | bool | No | Enable progress notifications | `true` |
| `primary_system_prompt` | str | No | System prompt for primary agent | Default prompt |
| `specialist_system_prompt` | str | No | System prompt for specialist agent | Default prompt |

### Delegation Modes

#### `auto_detect`
Analyzes input using NLP to determine appropriate agent.

**Decision Logic:**
- Counts CRM-related keywords (assistant, contact, call, etc.)
- Counts general keywords (chat, help, explain, etc.)
- Routes to specialist if CRM score > general score

#### `force_specialist`
Always routes to specialist agent regardless of input.

#### `primary_only`
Always routes to primary agent regardless of input.

#### `hybrid`
Uses confidence-based routing with threshold.

### Task Analysis

The component analyzes input text to determine routing:

```json
{
  "input": "Create an assistant for customer service",
  "crm_score": 3,
  "natural_score": 0,
  "keywords_found": {
    "crm": ["assistant", "customer", "service"],
    "natural": []
  },
  "recommended_agent": "specialist",
  "confidence": 0.15,
  "delegation_reason": "Multiple CRM keywords detected, requires specialist knowledge"
}
```

### Response Format

```json
{
  "agent": "specialist",
  "operation": "create_assistant_operation",
  "response": "I've identified this as a create assistant operation. I'm equipped with specialized CRM tools to handle this request.",
  "tool_calls_planned": [
    "validate_location_access",
    "create_assistant_api_call", 
    "confirm_creation"
  ],
  "next_steps": [
    "Provide assistant name and description",
    "Specify location ID if different from default",
    "Configure assistant parameters"
  ],
  "delegation_info": {
    "agent_used": "specialist",
    "delegation_mode": "auto_detect",
    "task_analysis": {...},
    "session_id": "session_abc123"
  }
}
```

### Runtime Hooks

The AgentDelegator emits several types of hooks:

#### `task_analysis`
```json
{
  "hook_type": "task_analysis",
  "data": {
    "analysis": {...},
    "delegation_mode": "auto_detect"
  }
}
```

#### `pre_task`
```json
{
  "hook_type": "pre_task", 
  "data": {
    "agent": "specialist",
    "action": "crm_operation",
    "input": "Create an assistant...",
    "tools_available": true
  }
}
```

#### `start_task`
```json
{
  "hook_type": "start_task",
  "data": {
    "agent": "specialist", 
    "operation": "create_assistant_operation",
    "task_id": "task_def456"
  }
}
```

#### `end_run`
```json
{
  "hook_type": "end_run",
  "data": {
    "agent": "specialist",
    "operation": "create_assistant_operation", 
    "response": {...},
    "success": true
  }
}
```

---

## 🔔 RuntimeHooks

Progress notification and monitoring system for agent operations.

### Configuration

| Input | Type | Required | Description | Default |
|-------|------|----------|-------------|---------|
| `hook_mode` | dropdown | Yes | Hook operation mode | `monitor` |
| `hook_input` | Data | No | Hook data to process or emit | - |
| `filter_type` | str | No | Filter hooks by type | - |
| `component_filter` | str | No | Filter hooks by component name | - |
| `max_hooks` | int | No | Maximum hooks to retain | `100` |
| `retention_minutes` | int | No | How long to retain hooks | `60` |
| `real_time_updates` | bool | No | Enable real-time hook updates | `true` |
| `auto_cleanup` | bool | No | Auto clean up old hooks | `true` |

### Hook Modes

#### `monitor`
Return all hooks with optional filtering.

#### `emit`
Create and emit a new hook.

#### `filter`
Return hooks filtered by criteria.

#### `aggregate`
Group hooks by session for workflow tracking.

### Hook Structure

```json
{
  "id": "hook_abc123",
  "hook_type": "pre_task",
  "component": "assistable_ai_client",
  "timestamp": "2025-07-15T10:30:00Z",
  "data": {
    "action": "create_assistant",
    "name": "Support Bot"
  },
  "session_id": "session_def456",
  "status": "active"
}
```

### Hook Types

| Type | Description | When Emitted |
|------|-------------|--------------|
| `pre_task` | Before operation starts | Component preparing to execute |
| `start_task` | Operation begins | Component begins execution |
| `end_run` | Operation completes | Component finishes successfully |
| `error` | Error occurred | Component encounters error |
| `task_analysis` | Task analysis complete | AgentDelegator analyzes input |
| `batch_start` | Batch operation starts | BatchProcessor begins |
| `batch_chunk_start` | Chunk processing starts | BatchProcessor chunk begins |
| `batch_chunk_complete` | Chunk processing ends | BatchProcessor chunk ends |
| `batch_complete` | Batch operation ends | BatchProcessor finishes |

### Summary Statistics

```json
{
  "total_hooks": 25,
  "by_type": {
    "pre_task": 8,
    "start_task": 8,
    "end_run": 7,
    "error": 2
  },
  "by_component": {
    "assistable_ai_client": 15,
    "ghl_client": 8,
    "agent_delegator": 2
  },
  "by_status": {
    "active": 23,
    "archived": 2
  },
  "latest_timestamp": "2025-07-15T10:45:00Z",
  "sessions": 3,
  "session_list": ["session_abc", "session_def", "session_ghi"]
}
```

---

## 📦 BatchProcessor

Bulk operations for Assistable AI and GoHighLevel with progress tracking.

### Configuration

| Input | Type | Required | Description | Default |
|-------|------|----------|-------------|---------|
| `batch_operation` | dropdown | Yes | Type of batch operation | `bulk_ai_calls` |
| `batch_data` | Data | Yes | List of items to process | - |
| `assistant_id` | str | No | Assistant ID for batch operations | - |
| `location_id` | str | No | GoHighLevel location ID | `DEFAULT_LOCATION_ID` env |
| `number_pool_id` | str | No | Phone number pool | `DEFAULT_NUMBER_POOL_ID` env |
| `batch_size` | int | No | Items to process simultaneously | `10` |
| `delay_between_batches` | int | No | Delay between batches (seconds) | `2` |
| `stop_on_error` | bool | No | Stop processing if error occurs | `false` |
| `emit_progress_hooks` | bool | No | Enable detailed progress tracking | `true` |
| `timeout_per_item` | int | No | Timeout for each operation (seconds) | `30` |

### Batch Operations

#### `bulk_create_assistants`
Create multiple AI assistants.

**Batch Data Format:**
```json
[
  {
    "name": "Sales Bot",
    "description": "AI assistant for sales",
    "prompt": "You are a helpful sales assistant..."
  },
  {
    "name": "Support Bot", 
    "description": "AI assistant for support",
    "prompt": "You are a helpful support assistant..."
  }
]
```

#### `bulk_ai_calls`
Initiate multiple AI calls.

**Batch Data Format:**
```json
[
  {
    "contact_id": "contact_123",
    "assistant_id": "asst_abc123"
  },
  {
    "contact_id": "contact_456", 
    "assistant_id": "asst_abc123"
  }
]
```

#### `bulk_contact_lookup`
Look up multiple contacts.

**Batch Data Format:**
```json
[
  {
    "email": "john@example.com"
  },
  {
    "phone": "+1234567890"
  },
  {
    "contact_id": "contact_789"
  }
]
```

#### `bulk_contact_updates`
Update multiple contacts.

**Batch Data Format:**
```json
[
  {
    "contact_id": "contact_123",
    "firstName": "John",
    "lastName": "Doe"
  },
  {
    "contact_id": "contact_456",
    "email": "jane@example.com"
  }
]
```

#### `bulk_message_send`
Send messages to multiple contacts.

**Batch Data Format:**
```json
[
  {
    "contact_id": "contact_123",
    "message": "Hello John!"
  },
  {
    "contact_id": "contact_456",
    "message": "Hello Jane!"
  }
]
```

#### `bulk_tag_operations`
Add or remove tags from multiple contacts.

**Batch Data Format:**
```json
[
  {
    "contact_id": "contact_123",
    "tag": "qualified-lead",
    "operation": "add"
  },
  {
    "contact_id": "contact_456",
    "tag": "cold-lead",
    "operation": "remove"
  }
]
```

### Progress Tracking

The BatchProcessor emits detailed progress hooks:

#### `batch_start`
```json
{
  "hook_type": "batch_start",
  "data": {
    "total_items": 100,
    "batch_size": 10,
    "operation": "bulk_ai_calls",
    "estimated_chunks": 10
  }
}
```

#### `chunk_progress`
```json
{
  "hook_type": "chunk_progress",
  "data": {
    "chunk_index": 2,
    "processed_items": 20,
    "total_items": 100,
    "progress_percentage": 20.0
  }
}
```

#### `batch_complete`
```json
{
  "hook_type": "batch_complete",
  "data": {
    "total_items": 100,
    "processed_items": 100,
    "successful": 95,
    "failed": 5,
    "success_rate": 0.95,
    "operation": "bulk_ai_calls",
    "session_id": "batch_abc123",
    "started_at": "2025-07-15T10:30:00Z",
    "completed_at": "2025-07-15T10:45:00Z"
  }
}
```

### Result Format

```json
{
  "results": [
    {
      "index": 0,
      "item": {"contact_id": "contact_123"},
      "result": {"call_id": "call_abc123", "status": "initiated"},
      "success": true,
      "error": null,
      "timestamp": "2025-07-15T10:30:00Z"
    }
  ],
  "summary": {
    "total_items": 100,
    "processed_items": 100,
    "successful": 95,
    "failed": 5,
    "success_rate": 0.95,
    "operation": "bulk_ai_calls",
    "session_id": "batch_abc123"
  },
  "session_id": "batch_abc123"
}
```

---

## 🔧 Error Handling

All components follow consistent error handling patterns:

### Standard Error Response
```json
{
  "error": "Error description",
  "component": "component_name",
  "operation": "operation_name",
  "timestamp": "2025-07-15T10:30:00Z",
  "details": {
    "additional": "context"
  }
}
```

### Common Error Types

| Error | Description | Resolution |
|-------|-------------|------------|
| `"API token is required"` | Missing authentication | Set environment variables |
| `"Unauthorized - Check API token"` | Invalid token | Verify token is correct |
| `"Rate limited - Please try again later"` | API rate limit hit | Reduce request frequency |
| `"Request timeout"` | Operation took too long | Increase timeout setting |
| `"Missing required field: {field}"` | Required input missing | Provide required input |
| `"Location ID is required"` | No location specified | Set DEFAULT_LOCATION_ID |

### Error Hook Emission

When errors occur, components emit error hooks:

```json
{
  "hook_type": "error",
  "component": "assistable_ai_client",
  "data": {
    "action": "create_assistant",
    "error": "API token is required",
    "input_data": {...}
  },
  "timestamp": "2025-07-15T10:30:00Z"
}
```

---

## 🔗 Integration Patterns

### Component Chaining

Components can be chained together for complex workflows:

```
AgentDelegator → AssistableAIClient → RuntimeHooks
     ↓
GoHighLevelClient → RuntimeHooks
```

### Data Flow

1. **Input Validation**: All components validate inputs before processing
2. **Hook Emission**: Components emit pre_task hooks before starting
3. **API Calls**: Direct API integration with error handling
4. **Result Processing**: Response formatting and validation  
5. **Hook Emission**: Components emit end_run hooks after completion
6. **Error Handling**: Automatic error hook emission on failures

### Environment Integration

Components automatically use environment variables:

- `ASSISTABLE_API_TOKEN` - Assistable AI authentication
- `GHL_API_KEY` - GoHighLevel authentication  
- `DEFAULT_LOCATION_ID` - Default GHL location
- `DEFAULT_NUMBER_POOL_ID` - Default phone number pool

Override with component inputs when needed for multi-tenant scenarios.

---

This completes the API reference for all Skyward Assistable Bundle components. For workflow examples and implementation patterns, see [WORKFLOWS.md](WORKFLOWS.md).
