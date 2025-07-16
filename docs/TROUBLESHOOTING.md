# 🔧 Troubleshooting Guide

Common issues and solutions for the Skyward Assistable Bundle.

## 🚨 Installation Issues

### Components Not Appearing in Langflow

**Symptoms:**
- New components don't show up in Langflow component menu
- Bundle seems to not be loading

**Solutions:**

1. **Check Bundle URL Configuration**
   ```bash
   # Verify this is set in Railway environment variables
   LANGFLOW_BUNDLE_URLS=["https://github.com/promptedForge/flow-bundles.git"]
   ```

2. **Restart Langflow Instance**
   - Bundle loading requires a full restart
   - In Railway: Go to your deployment → Restart

3. **Check Repository Access**
   ```bash
   # Test if repository is accessible
   curl -I https://github.com/promptedForge/flow-bundles.git
   ```

4. **Verify Bundle Structure**
   ```bash
   # Ensure components directory exists and has __init__.py
   ls -la skyward_assistable_bundle/components/
   ```

5. **Check Langflow Logs**
   - In Railway: View logs for bundle loading errors
   - Look for Python import errors or permission issues

### Environment Variables Not Working

**Symptoms:**
- "API token is required" errors despite setting variables
- Components can't find configuration

**Solutions:**

1. **Verify Variable Names**
   ```bash
   # Check exact variable names (case-sensitive)
   ASSISTABLE_API_TOKEN=asst_577b7b4d-8019-43d5-8fc0-efc320a11fd98d6ef4e5-33be-47f5-9c7e-016b5a2a9125
   DEFAULT_LOCATION_ID=waq32uRFJqZ8Sjb9Hoql
   DEFAULT_NUMBER_POOL_ID=pit-8cb6cf70-9a1c-4bb0-b6ea-ce16fb5a9a8b
   ```

2. **Check Variable Scope**
   - Ensure variables are set at Railway deployment level
   - Not just in local .env files

3. **Restart After Changes**
   - Environment variable changes require restart
   - Variables are loaded at startup

4. **Test Environment Access**
   ```python
   import os
   print(os.getenv("ASSISTABLE_API_TOKEN"))  # Should not be None
   ```

---

## 🔐 Authentication Issues

### Assistable AI Authentication Errors

**Symptoms:**
- "Unauthorized - Check API token" errors
- API calls returning 401 status

**Solutions:**

1. **Verify Token Format**
   ```bash
   # Token should start with "asst_"
   ASSISTABLE_API_TOKEN=asst_577b7b4d-8019-43d5-8fc0-efc320a11fd98d6ef4e5-33be-47f5-9c7e-016b5a2a9125
   ```

2. **Test Token Directly**
   ```bash
   curl -H "Authorization: Bearer $ASSISTABLE_API_TOKEN" \
        https://api.assistable.ai/v2/get-assistant
   ```

3. **Check Token Permissions**
   - Ensure token has required permissions
   - Verify token is not expired

4. **Location Access**
   - Verify token has access to the specified location
   - Check DEFAULT_LOCATION_ID is correct

### GoHighLevel Authentication Errors

**Symptoms:**
- "Unauthorized - Check API token or location access" errors
- GHL operations failing with 401/403

**Solutions:**

1. **Verify GHL Credentials**
   ```bash
   # Check all GHL variables are set
   GHL_API_KEY=your_ghl_api_key
   GHL_CLIENT_ID=your_client_id
   GHL_CLIENT_SECRET=your_client_secret
   ```

2. **Test GHL API Access**
   ```bash
   curl -H "Authorization: Bearer $GHL_API_KEY" \
        -H "Version: 2021-07-28" \
        https://services.leadconnectorhq.com/locations/$DEFAULT_LOCATION_ID
   ```

3. **Check Location Permissions**
   - Verify API key has access to the location
   - Check location ID is correct format

4. **OAuth Token Issues**
   - If using OAuth, ensure tokens are not expired
   - Check refresh token functionality

---

## 🧩 Component Issues

### Component Import Errors

**Symptoms:**
- ImportError when loading components
- "Module not found" errors in logs

**Solutions:**

1. **Check Python Dependencies**
   ```bash
   pip install httpx langflow
   ```

2. **Verify Component Syntax**
   ```bash
   python -c "from components.assistable_ai_client import AssistableAIClient"
   ```

3. **Check File Permissions**
   ```bash
   ls -la components/
   # All files should be readable
   ```

4. **Validate Python Syntax**
   ```bash
   python -m py_compile components/assistable_ai_client.py
   ```

### Component Execution Errors

**Symptoms:**
- Components load but fail during execution
- Unexpected errors in component operations

**Solutions:**

1. **Check Input Validation**
   ```python
   # Ensure required inputs are provided
   # Check data types match expected formats
   ```

2. **Monitor Runtime Hooks**
   - Use RuntimeHooks component to see execution details
   - Check for error hooks

3. **Test with Minimal Inputs**
   ```python
   # Start with basic operation
   operation: "get_assistant"
   # No additional inputs required
   ```

4. **Check Timeout Settings**
   ```python
   # Increase timeout if operations are slow
   timeout: 60  # seconds
   ```

### Agent Delegator Not Working

**Symptoms:**
- All tasks going to primary agent
- Specialist agent never triggered

**Solutions:**

1. **Check Delegation Mode**
   ```python
   delegation_mode: "auto_detect"  # Not "primary_only"
   ```

2. **Verify Input Analysis**
   - Use task_analysis output to see keyword detection
   - Check CRM keywords are being found

3. **Test with Clear CRM Input**
   ```
   "Create an assistant for customer service calls"
   ```

4. **Check Specialist Tools**
   - Ensure specialist_tools input is connected
   - Verify tools are available

---

## 🔄 Runtime Issues

### Performance Problems

**Symptoms:**
- Slow component execution
- Timeouts occurring frequently

**Solutions:**

1. **Adjust Timeout Settings**
   ```python
   timeout: 60  # Increase from default 30
   ```

2. **Optimize Batch Sizes**
   ```python
   batch_size: 5  # Reduce from default 10
   delay_between_batches: 5  # Increase delay
   ```

3. **Check API Rate Limits**
   - Verify you're not hitting API limits
   - Implement backoff strategies

4. **Monitor Hook Performance**
   ```python
   emit_hooks: false  # Disable if not needed
   ```

### Memory Issues

**Symptoms:**
- Out of memory errors
- Langflow crashing during execution

**Solutions:**

1. **Reduce Hook Retention**
   ```python
   max_hooks: 50  # Reduce from default 100
   retention_minutes: 30  # Reduce from default 60
   ```

2. **Enable Auto Cleanup**
   ```python
   auto_cleanup: true
   ```

3. **Limit Batch Sizes**
   ```python
   batch_size: 3  # Smaller batches
   ```

4. **Disable Unused Features**
   ```python
   emit_progress_hooks: false  # If not monitoring
   real_time_updates: false   # If not using
   ```

### Hook System Issues

**Symptoms:**
- Hooks not appearing
- Progress tracking not working

**Solutions:**

1. **Verify Hook Emission**
   ```python
   emit_hooks: true  # Ensure enabled
   emit_progress_hooks: true
   ```

2. **Check Hook Mode**
   ```python
   hook_mode: "monitor"  # For viewing hooks
   ```

3. **Test Hook Storage**
   ```python
   # Use RuntimeHooks component to monitor
   max_hooks: 100
   auto_cleanup: false  # Temporarily disable
   ```

4. **Check Real-time Updates**
   ```python
   real_time_updates: true
   ```

---

## 🌐 Network Issues

### API Connection Problems

**Symptoms:**
- "Request timeout" errors
- Intermittent connection failures

**Solutions:**

1. **Check Network Connectivity**
   ```bash
   curl -I https://api.assistable.ai/v2/
   curl -I https://services.leadconnectorhq.com/
   ```

2. **Increase Timeouts**
   ```python
   timeout: 60  # Increase timeout
   ```

3. **Implement Retry Logic**
   - Components have built-in error handling
   - Check error messages for retry guidance

4. **Check Railway Networking**
   - Verify Railway deployment has internet access
   - Check for network restrictions

### Rate Limiting Issues

**Symptoms:**
- "Rate limited - Please try again later" errors
- 429 HTTP status codes

**Solutions:**

1. **Reduce Request Frequency**
   ```python
   delay_between_batches: 10  # Increase delays
   batch_size: 3  # Smaller batches
   ```

2. **Implement Exponential Backoff**
   - Components handle rate limiting automatically
   - Retry after the suggested delay

3. **Check API Limits**
   - Verify your API plan limits
   - Consider upgrading if needed

4. **Stagger Operations**
   ```python
   # Don't run multiple batch operations simultaneously
   ```

---

## 📊 Data Issues

### Invalid Data Formats

**Symptoms:**
- "Invalid JSON" errors
- Data parsing failures

**Solutions:**

1. **Validate JSON Format**
   ```bash
   python -m json.tool flows/customer_service_flow.json
   ```

2. **Check Data Types**
   ```python
   # Ensure batch_data is list of objects
   [{"contact_id": "123"}, {"contact_id": "456"}]
   ```

3. **Verify Required Fields**
   ```python
   # Check all required fields are present
   # See API_REFERENCE.md for requirements
   ```

4. **Test with Simple Data**
   ```python
   # Start with minimal valid data
   batch_data: [{"contact_id": "test_123"}]
   ```

### Contact Lookup Failures

**Symptoms:**
- Contacts not found despite existing
- Empty search results

**Solutions:**

1. **Verify Search Criteria**
   ```python
   email: "exact@email.com"  # Exact match required
   phone: "+1234567890"      # Include country code
   ```

2. **Check Location Context**
   ```python
   location_id: "waq32uRFJqZ8Sjb9Hoql"  # Correct location
   ```

3. **Test Different Search Methods**
   ```python
   # Try different operations
   operation: "get_contact_by_email"
   operation: "get_contact_by_phone"
   operation: "get_contact"  # With contact_id
   ```

4. **Verify Data Exists**
   ```bash
   # Check in GoHighLevel dashboard
   # Ensure contact exists in specified location
   ```

---

## 🔧 Debugging Tools

### Component Testing

1. **Run Test Script**
   ```bash
   cd skyward_assistable_bundle
   python scripts/test_bundle.py
   ```

2. **Individual Component Testing**
   ```python
   # Test specific components
   from components.assistable_ai_client import AssistableAIClient
   client = AssistableAIClient()
   ```

3. **Environment Testing**
   ```bash
   ./scripts/setup.sh
   ```

### Logging and Monitoring

1. **Enable Debug Logging**
   ```python
   # In Railway environment
   LOG_LEVEL=DEBUG
   ```

2. **Monitor Runtime Hooks**
   ```python
   # Add RuntimeHooks component to flows
   hook_mode: "monitor"
   real_time_updates: true
   ```

3. **Check Railway Logs**
   - View deployment logs in Railway dashboard
   - Look for Python exceptions and errors

### Network Debugging

1. **Test API Endpoints**
   ```bash
   # Test Assistable AI
   curl -H "Authorization: Bearer $ASSISTABLE_API_TOKEN" \
        https://api.assistable.ai/v2/get-assistant

   # Test GoHighLevel  
   curl -H "Authorization: Bearer $GHL_API_KEY" \
        -H "Version: 2021-07-28" \
        https://services.leadconnectorhq.com/locations/$DEFAULT_LOCATION_ID
   ```

2. **Check DNS Resolution**
   ```bash
   nslookup api.assistable.ai
   nslookup services.leadconnectorhq.com
   ```

3. **Test from Railway Environment**
   ```bash
   # SSH into Railway deployment if possible
   # Test network connectivity from there
   ```

---

## 📞 Getting Help

### Self-Service Steps

1. **Run Diagnostics**
   ```bash
   python scripts/test_bundle.py
   ./scripts/setup.sh
   ```

2. **Check Documentation**
   - [API Reference](API_REFERENCE.md) - Component details
   - [Installation Guide](INSTALLATION.md) - Setup instructions
   - [Workflows](WORKFLOWS.md) - Usage examples

3. **Review Logs**
   - Railway deployment logs
   - Langflow console output
   - Browser developer tools (for UI issues)

### Information to Collect

When seeking help, please provide:

1. **Environment Details**
   - Railway deployment URL
   - Langflow version
   - Bundle version (check `components/__init__.py`)

2. **Error Information**
   - Exact error messages
   - Component operation being performed
   - Input data (remove sensitive information)

3. **Configuration**
   - Environment variables (remove secrets)
   - Component settings
   - Flow configuration

4. **Steps to Reproduce**
   - What you were trying to do
   - Steps taken before error
   - Expected vs actual behavior

### Escalation Options

1. **GitHub Issues**
   - Report bugs with full details
   - Request new features
   - Community support

2. **Documentation Updates**
   - Suggest improvements to docs
   - Report missing information
   - Share solutions for common issues

3. **Community Forums**
   - Langflow community discussions
   - General AI automation questions

---

## 🔄 Maintenance

### Regular Maintenance

1. **Update Environment Variables**
   ```bash
   # Rotate API tokens periodically
   # Update OAuth tokens before expiry
   ```

2. **Monitor Usage**
   ```python
   # Use RuntimeHooks to track usage patterns
   # Monitor for performance issues
   ```

3. **Clean Up Data**
   ```python
   # Enable auto_cleanup for hooks
   auto_cleanup: true
   retention_minutes: 60
   ```

### Bundle Updates

1. **Check for Updates**
   - Bundle auto-updates from GitHub
   - Check changelog for breaking changes

2. **Test Updates**
   - Test in development before production
   - Verify existing flows still work

3. **Backup Configuration**
   ```bash
   # Export environment variables
   env | grep -E "(ASSISTABLE|GHL|DEFAULT)" > backup.env
   ```

### Performance Optimization

1. **Monitor Metrics**
   ```python
   # Use hook summaries to track performance
   # Identify slow operations
   ```

2. **Optimize Settings**
   ```python
   # Adjust timeouts based on actual usage
   # Optimize batch sizes for your data
   ```

3. **Scale Resources**
   - Upgrade Railway plan if needed
   - Monitor memory and CPU usage

---

**Remember:** Most issues can be resolved by checking environment variables, restarting the deployment, and verifying API credentials. Start with the basics before investigating complex problems.

For additional help, see [INSTALLATION.md](INSTALLATION.md) and [API_REFERENCE.md](API_REFERENCE.md).
