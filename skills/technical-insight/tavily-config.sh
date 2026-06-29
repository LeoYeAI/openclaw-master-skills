#!/bin/bash
# Unified Tavily configuration for technical-insight skill
# Uses the global ~/.openclaw/.env configuration

set -e

# Check if global .env file exists
if [ ! -f "$HOME/.openclaw/.env" ]; then
    echo "Error: Global Tavily configuration not found at ~/.openclaw/.env"
    echo "Please configure your Tavily API key using:"
    echo "echo 'TAVILY_API_KEY=your_api_key_here' > ~/.openclaw/.env"
    exit 1
fi

# Source the global configuration
source "$HOME/.openclaw/.env"

# Verify TAVILY_API_KEY is set
if [ -z "$TAVILY_API_KEY" ]; then
    echo "Error: TAVILY_API_KEY not found in ~/.openclaw/.env"
    exit 1
fi

echo "✅ Technical-insight skill configured to use global Tavily API key"
echo "🔑 Using API key from: ~/.openclaw/.env"