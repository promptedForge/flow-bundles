# 🚀 Installation Guide

## Prerequisites

- Langflow deployment (Railway recommended)
- Assistable AI API token
- GoHighLevel API credentials
- Python 3.8+ (for local development/testing)

## 🎯 Production Installation (5 Minutes)

### Step 1: Add Bundle to Langflow

**Set this environment variable in your Railway Langflow deployment:**

```bash
LANGFLOW_BUNDLE_URLS=["https://github.com/promptedForge/flow-bundles.git"]
```

### Step 2: Configure Environment Variables

**Copy these from `.env.production` to your Railway environment:**

```bash
# === ASSISTABLE AI (ALREADY CONFIGURED) ===
ASSISTABLE_API_TOKEN=asst_577b7b4d-8019-43d5-8fc0-efc320a11fd98d6ef4e5-33be-47f5-9c7e-016b5a2a9125

# === DEFAULTS (ALREADY CONFIGURED) ===
DEFAULT_LOCATION_ID=waq32uRFJqZ8Sjb9Hoql
DEFAULT_NUMBER_POOL_ID=pit-8cb6cf70-9a1c-4bb0-b6ea-ce16fb5a9a8b

# === GOHIGHLEVEL (ADD YOUR CREDENTIALS) ===
GHL_API_KEY=your_ghl_api_key_here
GHL_CLIENT_ID=your_ghl_client_id_here
GHL_CLIENT_SECRET=your_ghl_client_secret_here

# === OPTIONAL CONFIGURATION ===
AGENCY_LEVEL_INTEGRATION=true
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Step 3: Restart Langflow

Restart your Railway deployment to load the new components.

### Step 4: Verify Installation

1. **Check Components**: New components should appear in Langflow UI:
   - 🤖 Assistable AI Client
   - 👥 GoHighLevel Client  
   - 🎯 Agent Delegator
   - 🔔 Runtime Hooks
   - 📦 Batch Processor

2. **Import Example Flows**: Use flows from `flows/` directory

3. **Test Basic Operation**:
   ```
   Create flow → Add Assistable AI Client → Set operation to "chat_completion" → Test
   ```

## 🛠️ Local Development Installation

### Step 1: Clone Bundle

```bash
git clone <bundle-repo>
cd skyward_assistable_bundle
```

### Step 2: Set Environment Variables

```bash
# Copy local development configuration
cp .env.local .env

# Edit .env with your values
nano .env
```

### Step 3: Install Dependencies

```bash
# For testing
pip install httpx langflow

# Or use requirements if available
pip install -r requirements.txt
```

### Step 4: Run Setup Script

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Step 5: Test Components

```bash
cd scripts
python test_bundle.py
```

## 🔧 Environment Variable Reference

### Required Variables

| Variable | Description | Example | Status |
|----------|-------------|---------|---------|
| `ASSISTABLE_API_TOKEN` | Assistable AI API token | `asst_577b7b4d...` | ✅ Configured |
| `DEFAULT_LOCATION_ID` | GoHighLevel location ID | `waq32uRFJqZ8Sjb9Hoql` | ✅ Configured |
| `DEFAULT_NUMBER_POOL_ID` | Phone number pool for calls | `pit-8cb6cf70...` | ✅ Configured |
| `GHL_API_KEY` | GoHighLevel API key | `ghl_abc123...` | ⚠️ Need to add |
| `GHL_CLIENT_ID` | GoHighLevel OAuth client ID | `12345678` | ⚠️ Need to add |
| `GHL_CLIENT_SECRET` | GoHighLevel OAuth secret | `secret123...` | ⚠️ Need to add |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AGENCY_LEVEL_INTEGRATION` | Multi-location support | `true` |
| `ENVIRONMENT` | Deployment environment | `production` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `RATE_LIMIT_PER_MINUTE` | API rate limiting | `60` |
| `BATCH_SIZE_DEFAULT` | Default batch size | `10` |

## 🎯 Component Overview

### 🤖 Assistable AI Client
**Purpose**: Direct integration with Assistable AI API

**Operations**:
- `create_assistant` - Create new AI assistants
- `chat_completion` - Process conversations
- `make_ai_call` - Initiate AI phone calls
- `get_conversation` - Retrieve conversation history
- `update_assistant` - Modify assistant settings

**Key Features**:
- Automatic conversation ID generation
- Runtime hook emissions
- Environment variable integration
- Error handling and validation

### 👥 GoHighLevel Client  
**Purpose**: Direct CRM operations with GoHighLevel v2 API

**Operations**:
- `get_contact` / `get_contact_by_email` / `get_contact_by_phone`
- `create_contact` / `update_contact`
- `get_conversation` / `create_message`
- `switch_location` - Change subaccounts
- `add_tag` / `remove_tag`

**Key Features**:
- Multi-location support
- Token management
- Contact search and management
- Conversation handling

### 🎯 Agent Delegator
**Purpose**: Intelligent task delegation between agents

**Delegation Modes**:
- `auto_detect` - Analyze input and route automatically
- `force_specialist` - Always use specialist agent
- `primary_only` - Always use primary agent
- `hybrid` - Confidence-based routing

**Key Features**:
- NLP-based task analysis
- CRM keyword detection
- Session tracking
- Runtime hook integration

### 🔔 Runtime Hooks
**Purpose**: Real-time progress monitoring and notifications

**Hook Types**:
- `pre_task` - Before operation starts
- `start_task` - Operation begins
- `end_run` - Operation completes
- `error` - Error occurred

**Modes**:
- `monitor` - View all hooks
- `filter` - Filter by type/component
- `aggregate` - Group by session
- `emit` - Create new hooks

### 📦 Batch Processor
**Purpose**: Bulk operations with progress tracking

**Operations**:
- `bulk_create_assistants` - Create multiple assistants
- `bulk_ai_calls` - Mass calling campaigns
- `bulk_contact_lookup` - Contact searches
- `bulk_contact_updates` - Contact modifications

**Features**:
- Concurrent processing
- Progress tracking
- Error handling
- Timeout management

## 🔍 Troubleshooting

### Components Not Appearing

1. **Check Bundle URL**: Verify `LANGFLOW_BUNDLE_URLS` is correct
2. **Restart Required**: Langflow needs restart after bundle changes
3. **Repository Access**: Ensure Langflow can access GitHub repo
4. **Check Logs**: Review Langflow startup logs for errors

### API Authentication Errors

1. **Token Validation**: Test tokens with curl:
   ```bash
   curl -H "Authorization: Bearer $ASSISTABLE_API_TOKEN" \
        https://api.assistable.ai/v2/get-assistant
   ```

2. **Environment Variables**: Verify all variables are set correctly

3. **Location Access**: Ensure GHL tokens have proper location permissions

### Component Import Errors

1. **Dependencies**: Check if required packages are installed:
   ```bash
   pip install httpx langflow
   ```

2. **Python Path**: Ensure components directory is accessible

3. **Syntax Errors**: Run test script to check for issues:
   ```bash
   python scripts/test_bundle.py
   ```

### Flow Import Issues

1. **JSON Validation**: Check flows are valid JSON:
   ```bash
   python -m json.tool flows/customer_service_flow.json
   ```

2. **Component References**: Ensure referenced components exist

3. **Version Compatibility**: Check Langflow version compatibility

## 📞 Getting Help

### Self-Service Resources

1. **Run Diagnostics**:
   ```bash
   python scripts/test_bundle.py
   ```

2. **Check Logs**: Review Railway/Langflow logs for errors

3. **Verify Environment**: Ensure all variables are set correctly

### Documentation

- [API Reference](API_REFERENCE.md) - Detailed component documentation
- [Workflow Examples](WORKFLOWS.md) - Pre-built workflow patterns
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions

### Support Channels

1. **GitHub Issues**: Report bugs or request features
2. **Documentation**: Check comprehensive docs
3. **Community**: Langflow community forums

## 🔄 Updates and Maintenance

### Updating the Bundle

Bundle updates automatically when Langflow restarts (pulls from GitHub).

### Version Management

- Check `__version__` in `components/__init__.py`
- Review changelog for breaking changes
- Test updates in development before production

### Backup Configuration

```bash
# Export current environment variables
env | grep -E "(ASSISTABLE|GHL|DEFAULT)" > backup.env

# Backup flows
cp -r flows/ flows_backup/
```

---

**Installation complete!** 🎉 Your AI automation platform is ready to scale.

For next steps, see [DEPLOYMENT.md](../DEPLOYMENT.md) for production deployment guidance.
