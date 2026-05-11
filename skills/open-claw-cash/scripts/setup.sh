#!/bin/bash
# OpenclawCash Skill Setup
# Creates the .env file for API key configuration

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$SKILL_DIR/.env"

if [ -f "$ENV_FILE" ]; then
    echo "Found existing .env at $ENV_FILE"
    source "$ENV_FILE"
    if [ -n "$AGENTWALLETAPI_KEY" ] && [ "$AGENTWALLETAPI_KEY" != "occ_your_api_key" ]; then
        echo "API key is configured."
        exit 0
    else
        echo "API key is not set. Please edit $ENV_FILE and add your key."
        exit 1
    fi
fi

cat > "$ENV_FILE" << 'EOF'
# OpenclawCash Configuration
# Required binary: curl
# Optional binary: jq (for pretty JSON output in CLI)
# Required env var: AGENTWALLETAPI_KEY
# Optional env var: AGENTWALLETAPI_URL
# Get your API key at https://openclawcash.com (API Keys page)
AGENTWALLETAPI_KEY=occ_your_api_key
AGENTWALLETAPI_URL=https://openclawcash.com
EOF

echo "Created $ENV_FILE"
echo "Edit the file and replace occ_your_api_key with your actual API key."
echo "Get your key at https://openclawcash.com"
