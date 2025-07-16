# 📚 Skyward Assistable Bundle Documentation

Welcome to the comprehensive documentation for the Skyward Assistable Bundle - a powerful Langflow integration that brings Assistable AI and GoHighLevel capabilities directly into your automation workflows.

## 🎯 Overview

The Skyward Assistable Bundle provides:

- **Direct API Integration** - No separate MCP server needed
- **Agent Delegation Pattern** - Primary → Specialist agent workflow  
- **Runtime Hooks** - Real-time progress notifications and monitoring
- **Batch Processing** - Bulk operations with progress tracking
- **Complete Testing Suite** - Comprehensive validation and testing

## 📖 Documentation Structure

### Getting Started
- [Installation Guide](INSTALLATION.md) - Quick setup and configuration
- [Configuration Reference](../config/README.md) - Environment variables and settings

### API Documentation  
- [API Reference](API_REFERENCE.md) - Complete component API documentation
- [Workflow Examples](WORKFLOWS.md) - Pre-built workflow templates

### Support & Troubleshooting
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Common issues and solutions
- [Testing Guide](../tests/README.md) - Running tests and validation

## 🧩 Component Overview

### Core Components

#### 🤖 Assistable AI Client
- Create and manage AI assistants
- Process chat completions  
- Initiate AI phone calls
- Manage conversations and messages

**Key Operations:**
- `create_assistant` - Create new AI assistants
- `chat_completion` - Process conversational AI requests
- `make_ai_call` - Initiate automated phone calls
- `get_conversation` - Retrieve conversation history

#### 👥 GoHighLevel Client  
- Contact management and CRM operations
- Conversation handling and messaging
- Location switching and multi-tenant support
- Tag operations and opportunity management

**Key Operations:**
- `get_contact` - Retrieve contact information
- `create_contact` - Add new contacts to CRM
- `create_message` - Send messages to contacts
- `add_tag` - Tag contacts for organization

#### 🎯 Agent Delegator
- Intelligent task delegation between agents
- Primary ↔ Specialist agent workflow
- Natural language processing and intent detection
- Automatic CRM operation routing

**Delegation Modes:**
- `auto_detect` - Automatically determine best agent
- `force_specialist` - Always use specialist agent
- `primary_only` - Use only primary agent
- `hybrid` - Smart combination approach

#### 🔔 Runtime Hooks
- Progress monitoring and notifications
- Real-time status updates
- Performance tracking and analytics  
- Error handling and recovery

**Hook Types:**
- `pre_task` - Before operation starts
- `start_task` - Operation beginning
- `end_run` - Operation completion
- `error` - Error occurred

#### 📦 Batch Processor
- Bulk operation processing
- Campaign management
- Progress tracking with hooks
- Error handling and retry logic

**Batch Operations:**
- `bulk_create_assistants` - Create multiple assistants
- `bulk_ai_calls` - Execute calling campaigns  
- `bulk_contact_updates` - Mass contact updates
- `bulk_message_send` - Send messages to multiple contacts

## 🔄 Workflow Patterns

### 1. Customer Service Automation
```
Customer Input → Agent Delegation → CRM Lookup → AI Response → Follow-up
```

### 2. Lead Qualification
```
Lead Input → Qualification Agent → CRM Creation → Tagging → AI Follow-up
```

### 3. AI Calling Campaign
```
Contact List → Batch Processor → AI Calls → Progress Monitoring → Results
```

### 4. Agent Delegation Demo
```
User Input → Task Analysis → Agent Selection → Operation Execution → Results
```

## 🔧 Configuration

### Required Environment Variables

```bash
# Assistable AI
ASSISTABLE_API_TOKEN=your_assistable_token

# GoHighLevel  
GHL_API_KEY=your_ghl_key
GHL_CLIENT_ID=your_client_id
GHL_CLIENT_SECRET=your_client_secret
DEFAULT_LOCATION_ID=your_location_id
```

### Optional Configuration

```bash
# Bundle Settings
AGENCY_LEVEL_INTEGRATION=true
AUTH_ENCRYPTION_KEY=your_encryption_key
AUTH_TOKEN_FILE=.auth_tokens

# Performance Settings
DEFAULT_CACHE_TTL=3600
MAX_BATCH_SIZE=100
REQUEST_TIMEOUT=30
```

## 🚀 Quick Start Examples

### Simple Chat Completion
```python
# Using Assistable AI Client component
operation: "chat_completion"
input_text: "Hello, how can I help you today?"
assistant_id: "asst_your_assistant_id"
```

### Create Contact in CRM
```python
# Using GoHighLevel Client component  
operation: "create_contact"
email: "customer@example.com"
first_name: "John"
last_name: "Doe"
```

### Agent Delegation
```python
# Using Agent Delegator component
user_input: "Create an assistant for customer service"
delegation_mode: "auto_detect"
enable_hooks: true
```

### Batch AI Calls
```python
# Using Batch Processor component
batch_operation: "bulk_ai_calls"
batch_data: [
  {"contact_id": "contact_1"},
  {"contact_id": "contact_2"}
]
assistant_id: "asst_calling_assistant"
```

## 📊 Monitoring & Analytics

### Runtime Hooks
All components emit runtime hooks for monitoring:

```json
{
  "hook_type": "pre_task",
  "timestamp": "2024-01-15T10:30:00Z",
  "component": "assistable_ai_client", 
  "data": {
    "operation": "create_assistant",
    "assistant_name": "Customer Service Bot"
  }
}
```

### Progress Tracking
Track workflow progress in real-time:

```json
{
  "session_id": "sess_12345",
  "total_steps": 5,
  "completed_steps": 3,
  "current_step": "Creating contact in CRM",
  "progress_percentage": 60
}
```

## 🔍 Advanced Features

### Error Handling
- Automatic retry logic with exponential backoff
- Comprehensive error categorization and logging
- Recovery strategies for common failure scenarios
- User-friendly error messages

### Caching System
- API response caching to reduce latency
- Configurable TTL for different data types
- Tag-based cache invalidation
- Memory-efficient LRU eviction

### Security
- Encrypted token storage
- Input validation and sanitization  
- SQL injection prevention
- Secure API communication

### Performance Optimization
- Concurrent batch processing
- Connection pooling and reuse
- Intelligent rate limiting
- Memory usage optimization

## 🤝 Integration Patterns

### With Existing Workflows
The bundle integrates seamlessly with existing Langflow workflows:

1. **Drop-in Replacement** - Replace existing components with enhanced versions
2. **Progressive Enhancement** - Add AI and CRM capabilities to existing flows
3. **Microservice Pattern** - Use components as specialized services

### Multi-tenant Support
Built for agency and multi-location use:

- Location-specific token management
- Automatic context switching
- Isolated data handling
- Scalable architecture

## 📈 Performance Guidelines

### Batch Operations
- **Small batches**: 1-10 items, immediate processing
- **Medium batches**: 10-50 items, chunked processing with delays
- **Large batches**: 50+ items, background processing with progress tracking

### API Rate Limits
- **Assistable AI**: Respect token bucket limits
- **GoHighLevel**: Handle 429 responses gracefully
- **Auto-retry**: Exponential backoff with jitter

### Memory Usage
- **Caching**: Configure appropriate TTL and size limits
- **Batch processing**: Stream large datasets when possible
- **Hook storage**: Automatic cleanup of old runtime hooks

## 🔄 Update Strategy

The bundle is designed for seamless updates:

1. **Backward Compatibility** - New versions maintain API compatibility
2. **Progressive Migration** - Gradual adoption of new features
3. **Hot Reloading** - Update without workflow interruption
4. **Version Management** - Clear versioning and changelog

## 📞 Support & Community

### Getting Help
1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Review the [API Reference](API_REFERENCE.md)
3. Test with provided [Examples](../examples/)
4. Open an issue with detailed error information

### Contributing
We welcome contributions! Please see:
- Component development guidelines
- Testing requirements
- Documentation standards
- Code review process

### Best Practices
- **Testing**: Always test components in isolation first
- **Monitoring**: Enable runtime hooks for production workflows
- **Security**: Use environment variables for sensitive data
- **Performance**: Monitor cache hit rates and API response times

---

**Ready to get started?** 🚀

Begin with the [Installation Guide](INSTALLATION.md) to set up your bundle, then explore the [Workflow Examples](WORKFLOWS.md) to see the components in action!
