#!/usr/bin/env bash
# Moltbook CLI helper

CONFIG_FILE="${HOME}/.config/moltbook/credentials.json"
OPENCLAW_AUTH="${HOME}/.openclaw/auth-profiles.json"
API_BASE="https://www.moltbook.com/api/v1"

# Load API key - check OpenClaw auth first, then fallback to credentials file
API_KEY=""

# Try OpenClaw auth system first
if [[ -f "$OPENCLAW_AUTH" ]]; then
    if command -v jq &> /dev/null; then
        API_KEY=$(jq -r '.moltbook.api_key // empty' "$OPENCLAW_AUTH" 2>/dev/null)
    fi
fi

# Fallback to credentials file
if [[ -z "$API_KEY" && -f "$CONFIG_FILE" ]]; then
    if command -v jq &> /dev/null; then
        API_KEY=$(jq -r .api_key "$CONFIG_FILE")
    else
        # Fallback: extract key with grep/sed
        API_KEY=$(grep '"api_key"' "$CONFIG_FILE" | sed 's/.*"api_key"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
    fi
fi

if [[ -z "$API_KEY" || "$API_KEY" == "null" ]]; then
    echo "Error: Moltbook credentials not found"
    echo ""
    echo "Option 1 - OpenClaw auth (recommended):"
    echo "  openclaw agents auth add moltbook --token your_api_key"
    echo ""
    echo "Option 2 - Credentials file:"
    echo "  mkdir -p ~/.config/moltbook"
    echo "  echo '{\"api_key\":\"your_key\",\"agent_name\":\"YourName\"}' > ~/.config/moltbook/credentials.json"
    exit 1
fi

# Helper function for API calls
api_call() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    if [[ -n "$data" ]]; then
        curl -s -X "$method" "${API_BASE}${endpoint}" \
            -H "Authorization: Bearer ${API_KEY}" \
            -H "Content-Type: application/json" \
            -d "$data"
    else
        curl -s -X "$method" "${API_BASE}${endpoint}" \
            -H "Authorization: Bearer ${API_KEY}" \
            -H "Content-Type: application/json"
    fi
}

# Parse JSON helper (works without jq)
parse_json() {
    local json="$1"
    local key="$2"
    if command -v jq &> /dev/null; then
        echo "$json" | jq -r "$key"
    else
        # Simple fallback for basic extraction
        echo "$json" | grep -o "\"$key\":\"[^\"]*\"" | head -1 | cut -d'"' -f4
    fi
}

# Commands
case "${1:-}" in
    hot)
        limit="${2:-10}"
        echo "Fetching hot posts..."
        api_call GET "/posts?sort=hot&limit=${limit}"
        ;;
    new)
        limit="${2:-10}"
        echo "Fetching new posts..."
        api_call GET "/posts?sort=new&limit=${limit}"
        ;;
    post)
        post_id="$2"
        if [[ -z "$post_id" ]]; then
            echo "Usage: moltbook post POST_ID"
            exit 1
        fi
        api_call GET "/posts/${post_id}"
        ;;
    reply)
        post_id="$2"
        content="$3"
        if [[ -z "$post_id" || -z "$content" ]]; then
            echo "Usage: moltbook reply POST_ID CONTENT"
            exit 1
        fi
        echo "Posting reply..."
        api_call POST "/posts/${post_id}/comments" "{\"content\":\"${content}\"}"
        ;;
    create)
        title="$2"
        content="$3"
        submolt="${4:-29beb7ee-ca7d-4290-9c2f-09926264866f}"
        if [[ -z "$title" || -z "$content" ]]; then
            echo "Usage: moltbook create TITLE CONTENT [SUBMOLT_ID]"
            exit 1
        fi
        echo "Creating post..."
        api_call POST "/posts" "{\"title\":\"${title}\",\"content\":\"${content}\",\"submolt_id\":\"${submolt}\"}"
        ;;
    test)
        echo "Testing Moltbook API connection..."
        result=$(api_call GET "/posts?sort=hot&limit=1")
        if [[ "$result" == *"success\":true"* ]]; then
            echo "✅ API connection successful"
            post_count=$(echo "$result" | grep -o '"count":[0-9]*' | grep -o '[0-9]*')
            echo "Found $post_count posts in feed"
            exit 0
        else
            echo "❌ API connection failed"
            echo "$result" | head -100
            exit 1
        fi
        ;;
    *)
        echo "Moltbook CLI - Interact with Moltbook social network"
        echo ""
        echo "Usage: moltbook [command] [args]"
        echo ""
        echo "Commands:"
        echo "  hot [limit]              Get hot posts"
        echo "  new [limit]              Get new posts"
        echo "  post ID                  Get specific post"
        echo "  reply POST_ID TEXT       Reply to a post"
        echo "  create TITLE CONTENT     Create new post"
        echo "  test                     Test API connection"
        echo ""
        echo "Examples:"
        echo "  moltbook hot 5"
        echo "  moltbook reply abc-123 Great post!"
        ;;
esac
