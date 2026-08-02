#!/usr/bin/env bash
# Nimble Web Search - Agent Skill Wrapper
# Usage: ./scripts/search.sh '{"query": "...", "focus": "general", "max_results": 10}'

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_error() {
    echo -e "${RED}Error: $1${NC}" >&2
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}" >&2
}

# Check if input provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 '<json>'"
    echo ""
    echo "Examples:"
    echo "  $0 '{\"query\": \"React hooks\", \"focus\": \"coding\"}'"
    echo "  $0 '{\"query\": \"AI news\", \"focus\": \"news\", \"max_results\": 15}'"
    echo "  $0 '{\"query\": \"research papers\", \"focus\": \"academic\", \"include_answer\": true}'"
    echo ""
    echo "Available focus modes:"
    echo "  general, coding, news, academic, shopping, social, geo, location"
    exit 1
fi

JSON_INPUT="$1"

# Validate API key
if [ -z "${NIMBLE_API_KEY:-}" ]; then
    print_error "NIMBLE_API_KEY environment variable not set"
    echo ""
    echo "Get your API key at: https://www.nimbleway.com/"
    echo ""
    echo "Configure using your platform's method:"
    echo "  Claude Code: Add to ~/.claude/settings.json"
    echo '  {"env": {"NIMBLE_API_KEY": "your-key"}}'
    echo ""
    echo "  Shell: export NIMBLE_API_KEY=\"your-key\""
    exit 1
fi

# Validate JSON syntax
if ! echo "$JSON_INPUT" | jq empty 2>/dev/null; then
    print_error "Invalid JSON syntax"
    echo ""
    echo "Example valid JSON:"
    echo '  {"query": "search term", "focus": "general"}'
    exit 1
fi

# Validate required field
if ! echo "$JSON_INPUT" | jq -e '.query' >/dev/null 2>&1; then
    print_error "Missing required field: query"
    echo ""
    echo "The 'query' field is required in your JSON input"
    exit 1
fi

# Add performance-optimized defaults if not specified
# deep_search defaults to false for 5-10x faster responses
JSON_WITH_DEFAULTS=$(echo "$JSON_INPUT" | jq '. + {deep_search: (.deep_search // false)}')

# Auto-detect platform
detect_platform() {
    if [ -n "${CLAUDE_CODE_VERSION:-}" ]; then
        echo "claude-code"
    elif [ -n "${GITHUB_COPILOT:-}" ]; then
        echo "github-copilot"
    elif [ -n "${VSCODE_PID:-}" ]; then
        echo "vscode"
    else
        echo "cli"
    fi
}

PLATFORM=$(detect_platform)
SKILL_VERSION="0.1.0"
API_URL="https://nimble-retriever.webit.live/search"

# Make API request with tracking headers
curl -s -X POST "$API_URL" \
    -H "Authorization: Bearer $NIMBLE_API_KEY" \
    -H "Content-Type: application/json" \
    -H "User-Agent: nimble-agent-skill/$SKILL_VERSION" \
    -H "X-Client-Source: agent-skill" \
    -H "X-Nimble-Request-Origin: $PLATFORM" \
    -d "$JSON_WITH_DEFAULTS" | jq .
