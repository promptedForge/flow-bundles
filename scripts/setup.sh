#!/bin/bash

# 🚀 Skyward Assistable Bundle Setup Script
# This script helps set up the bundle for use with Langflow

set -e

echo "🎯 Setting up Skyward Assistable Bundle..."

# Check if we're in the right directory
if [[ ! -f "README.md" ]]; then
    echo "❌ Error: Please run this script from the skyward_assistable_bundle directory"
    exit 1
fi

# Check for required environment variables
echo "🔍 Checking environment variables..."

check_env_var() {
    if [[ -z "${!1}" ]]; then
        echo "⚠️  Warning: $1 is not set"
        return 1
    else
        echo "✅ $1 is set"
        return 0
    fi
}

# Check required variables
missing_vars=0

if ! check_env_var "ASSISTABLE_API_TOKEN"; then
    missing_vars=$((missing_vars + 1))
fi

if ! check_env_var "DEFAULT_LOCATION_ID"; then
    missing_vars=$((missing_vars + 1))
fi

if ! check_env_var "DEFAULT_NUMBER_POOL_ID"; then
    missing_vars=$((missing_vars + 1))
fi

# Optional but recommended
check_env_var "GHL_API_KEY" || echo "ℹ️  GHL_API_KEY not set (required for GoHighLevel operations)"

if [[ $missing_vars -gt 0 ]]; then
    echo ""
    echo "❌ Missing $missing_vars required environment variables"
    echo ""
    echo "📋 Please set the following variables:"
    echo "   export ASSISTABLE_API_TOKEN=your_token_here"
    echo "   export DEFAULT_LOCATION_ID=your_location_id_here"
    echo "   export DEFAULT_NUMBER_POOL_ID=your_number_pool_id_here"
    echo ""
    echo "💡 You can copy values from .env.production or .env.local"
    echo ""
    exit 1
fi

echo ""
echo "✅ Environment variables configured correctly!"

# Test file permissions
echo "🔧 Checking file permissions..."
if [[ ! -r "components/__init__.py" ]]; then
    echo "❌ Cannot read component files"
    exit 1
fi

echo "✅ File permissions are correct"

# Validate component imports (if Python is available)
if command -v python3 &> /dev/null; then
    echo "🐍 Validating Python component imports..."
    
    cd components
    if python3 -c "
import sys
sys.path.append('.')
try:
    from assistable_ai_client import AssistableAIClient
    from ghl_client import GoHighLevelClient
    from agent_delegator import AgentDelegator
    from runtime_hooks import RuntimeHooks
    from batch_processor import BatchProcessor
    print('✅ All components import successfully')
except Exception as e:
    print(f'❌ Component import error: {e}')
    sys.exit(1)
"; then
        echo "✅ Python components validated"
    else
        echo "⚠️  Some component imports failed (this might be okay if dependencies aren't installed)"
    fi
    cd ..
else
    echo "ℹ️  Python not found, skipping component validation"
fi

# Check if flows are valid JSON
echo "📋 Validating flow files..."
for flow_file in flows/*.json; do
    if [[ -f "$flow_file" ]]; then
        if python3 -m json.tool "$flow_file" > /dev/null 2>&1; then
            echo "✅ $(basename "$flow_file") is valid JSON"
        else
            echo "❌ $(basename "$flow_file") is invalid JSON"
            exit 1
        fi
    fi
done

echo ""
echo "🎉 Setup complete! Your Skyward Assistable Bundle is ready to use."
echo ""
echo "📝 Next steps:"
echo "   1. Add this bundle to your Langflow LANGFLOW_BUNDLE_URLS"
echo "   2. Restart your Langflow instance"
echo "   3. Import example flows from the flows/ directory"
echo "   4. Start building AI automation workflows!"
echo ""
echo "📖 Documentation: docs/INSTALLATION.md"
echo "🆘 Troubleshooting: docs/TROUBLESHOOTING.md"
echo ""
echo "🚀 Happy building!"
