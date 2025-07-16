# 🎯 Skyward Assistable Bundle for Langflow

A comprehensive Langflow bundle that provides direct integration with Assistable AI and GoHighLevel v2 APIs through an intelligent agent delegation pattern.

## ✨ Features

- 🤖 **Agent Delegation**: Primary Agent → Specialist Agent pattern
- 📞 **AI Calling**: Automated calling campaigns through Assistable AI
- 👥 **Contact Management**: Full GoHighLevel v2 CRM integration
- 🔄 **Runtime Hooks**: Real-time progress notifications
- 📊 **Batch Operations**: Bulk processing capabilities
- 🔒 **Security**: Input validation and secure API handling

## 🚀 Quick Start

### 1. **Load Bundle** 
Add this repository to your Langflow `LANGFLOW_BUNDLE_URLS`:

```bash
LANGFLOW_BUNDLE_URLS=["https://github.com/promptedForge/flow-bundles.git"]
```

### 2. **Set Environment Variables**
Copy from `.env.production` to your Railway Langflow environment variables.

### 3. **Restart Langflow**
Components will automatically appear in your Langflow UI.

### 4. **Import Example Flows**
Import flows from the `flows/` directory to get started quickly.

## 📚 Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [API Reference](docs/API_REFERENCE.md)
- [Workflow Examples](docs/WORKFLOWS.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🔧 Environment Variables

### Production Ready Variables (Railway)
See `.env.production` - ready to copy/paste into Railway environment variables.

### Local Development
See `.env.local` - configured for local Langflow development.

### Required Variables
- `ASSISTABLE_API_TOKEN` - Your Assistable AI API token
- `GHL_API_KEY` - GoHighLevel API key
- `DEFAULT_LOCATION_ID` - GoHighLevel location/subaccount ID
- `DEFAULT_NUMBER_POOL_ID` - Phone number pool for AI calls

## 🎯 Agent Architecture

```
External Client → Primary Agent → Agent Delegator → Specialist Agent → API Components
                     ↑                                      ↓
                Runtime Hooks ←─────────── Progress Notifications
```

## 🛠️ Components

### Core Components
1. **Assistable AI Client** - Direct API integration for assistants and calls
2. **GoHighLevel Client** - Direct CRM operations and contact management  
3. **Agent Delegator** - Intelligent Primary → Specialist delegation
4. **Runtime Hooks** - Real-time progress monitoring and notifications
5. **Batch Processor** - Bulk operations for campaigns and data processing

### Example Flows
1. **Customer Service Flow** - Agent delegation with CRM tools
2. **AI Calling Campaign** - Bulk calling with progress tracking
3. **Lead Qualification** - Automated lead processing
4. **Agent Delegation Demo** - Shows delegation pattern in action

## 🎉 What This Enables

- ✅ **Zero separate infrastructure** - All runs in your existing Railway Langflow
- ✅ **Agent delegation** - Primary → Specialist agent pattern
- ✅ **Runtime hooks** - Real-time progress tracking
- ✅ **Production ready** - Error handling, validation, monitoring
- ✅ **MCP compatible** - Works with external MCP clients via `/api/v1/mcp/sse`

## 🚀 Usage Examples

### Create AI Assistant
```python
# Use Assistable AI Client component
operation: create_assistant
assistant_name: "Sales Bot"
assistant_description: "AI assistant for lead qualification"
input_text: "You are a helpful sales assistant..."
```

### Bulk AI Calling Campaign
```python
# Use Batch Processor component
batch_operation: bulk_ai_calls
batch_data: [{"contact_id": "123"}, {"contact_id": "456"}]
assistant_id: "asst_abc123"
number_pool_id: "pit-8cb6cf70-9a1c-4bb0-b6ea-ce16fb5a9a8b"
```

### Agent Delegation
```python
# Use Agent Delegator component
user_input: "Create an assistant for our Chicago office and call the top 5 leads"
delegation_mode: "auto_detect"
# Automatically routes to specialist agent for CRM operations
```

## 📞 Support

For issues and support:
1. Check the [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
2. Review Langflow logs for error details
3. Test API credentials independently
4. Open issue in repository with details

---

**Built with ❤️ by Skyward Prompted** 🚀

Ready to deploy your AI automation platform!
