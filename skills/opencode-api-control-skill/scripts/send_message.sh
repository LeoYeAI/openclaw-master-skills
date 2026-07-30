#!/bin/bash
# Send message to OpenCode session

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

MESSAGE="$1"
PROVIDER_ID="${2:-}"
MODEL_ID="${3:-}"
AGENT="${4:-}"

if [ -z "$MESSAGE" ]; then
  echo "Error: MESSAGE required" >&2
  echo "Usage: $0 <message> [provider_id] [model_id] [agent]" >&2
  exit 1
fi

# Load state
if [ ! -f "$SKILL_DIR/state/current.json" ]; then
  echo "Error: No active session. Create one first." >&2
  exit 1
fi

SESSION_ID=$(jq -r '.session_id' "$SKILL_DIR/state/current.json")
PROJECT_PATH=$(jq -r '.project_path' "$SKILL_DIR/state/current.json")
BASE_URL=$(jq -r '.base_url' "$SKILL_DIR/state/current.json")


# Use provided or default provider/model
if [ -z "$PROVIDER_ID" ]; then
  PROVIDER_ID=$(jq -r '.default_provider' "$SKILL_DIR/config.json")
  MODEL_ID=$(jq -r '.default_model' "$SKILL_DIR/config.json")
fi

# Build request body
if [ -n "$AGENT" ]; then
  REQUEST_BODY=$(jq -n \
    --arg agent "$AGENT" \
    --arg msg "$MESSAGE" \
    --arg provider "$PROVIDER_ID" \
    --arg model "$MODEL_ID" \
    '{
      agent: $agent,
      model: {providerID: $provider, modelID: $model},
      parts: [{type: "text", text: $msg}]
    }')
else
  REQUEST_BODY=$(jq -n \
    --arg msg "$MESSAGE" \
    --arg provider "$PROVIDER_ID" \
    --arg model "$MODEL_ID" \
    '{
      model: {providerID: $provider, modelID: $model},
      parts: [{type: "text", text: $msg}]
    }')
fi

# Send message
RESPONSE=$(curl -s -X POST \
  "$BASE_URL/session/$SESSION_ID/message?directory=$PROJECT_PATH" \
  -H "Content-Type: application/json" \
  -d "$REQUEST_BODY")

# Check for errors
if echo "$RESPONSE" | jq -e '.info.error' >/dev/null 2>&1; then
  echo "Error:" >&2
  echo "$RESPONSE" | jq -r '.info.error.data.message' >&2
  exit 1
fi

# Output response text
echo "$RESPONSE" | jq -r '.parts[] | select(.type=="text") | .text'
exit 0