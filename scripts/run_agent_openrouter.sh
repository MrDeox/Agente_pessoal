#!/bin/bash
# Script to run the personal agent with OpenRouter configuration

# Set OpenRouter configuration
# Note: API key should be set as an environment variable before running this script
export PA_LLM__PROVIDER="${PA_LLM__PROVIDER:-openrouter}"
export PA_LLM__MODEL="${PA_LLM__MODEL:-qwen/qwen3-coder:free}"

# Check if API key is set
if [ -z "$PA_LLM__API_KEY" ]; then
    echo "Error: PA_LLM__API_KEY environment variable is not set"
    echo "Please set it before running this script:"
    echo "  export PA_LLM__API_KEY='your-api-key-here'"
    echo "  $0"
    exit 1
fi

echo "Starting Personal Agent with OpenRouter..."
echo "Provider: $PA_LLM__PROVIDER"
echo "Model: $PA_LLM__MODEL"
echo ""

# Run the agent
python3 scripts/run_agent.py