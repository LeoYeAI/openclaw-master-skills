#!/bin/bash
# Create new OpenCode session

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

PROJECT_PATH="$1"
TITLE="${2:-New Session}"

if [ -z "$PROJECT_PATH" ]; then
  echo "Error: PROJECT_PATH required" >&2
  echo "Usage: $0 <project_path> [title]" >&2
  exit 1
fi

# Read config
BASE_URL=$(jq -r '.base_url' "$SKILL_DIR/config.json")


# Create session
RESPONSE=$(curl -s -X POST "$BASE_URL/session?directory=$PROJECT_PATH" \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"$TITLE\"}")

# Check for errors
if echo "$RESPONSE" | jq -e '.errors' >/dev/null 2>&1; then
  echo "Error creating session:" >&2
  echo "$RESPONSE" | jq -r '.errors[].message' >&2
  exit 1
fi

SESSION_ID=$(echo "$RESPONSE" | jq -r '.id')

if [ -z "$SESSION_ID" ] || [ "$SESSION_ID" = "null" ]; then
  echo "Error: Failed to get session ID" >&2
  exit 1
fi

# Save state automatically
bash "$SCRIPT_DIR/save_state.sh" "$SESSION_ID" "$PROJECT_PATH" >/dev/null

echo "$SESSION_ID"
exit 0