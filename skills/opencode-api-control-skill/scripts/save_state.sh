#!/bin/bash
# Save session state

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

SESSION_ID="$1"
PROJECT_PATH="$2"

if [ -z "$SESSION_ID" ] || [ -z "$PROJECT_PATH" ]; then
  echo "Error: SESSION_ID and PROJECT_PATH required" >&2
  echo "Usage: $0 <session_id> <project_path>" >&2
  exit 1
fi

# Create state directory
mkdir -p "$SKILL_DIR/state"

# Read config
BASE_URL=$(jq -r '.base_url' "$SKILL_DIR/config.json")
PROVIDER_ID=$(jq -r '.default_provider' "$SKILL_DIR/config.json")
MODEL_ID=$(jq -r '.default_model' "$SKILL_DIR/config.json")

# Save state
jq -n \
  --arg base_url "$BASE_URL" \
  --arg project_path "$PROJECT_PATH" \
  --arg session_id "$SESSION_ID" \
  --arg provider "$PROVIDER_ID" \
  --arg model "$MODEL_ID" \
  '{
    base_url: $base_url,
    project_path: $project_path,
    session_id: $session_id,
    provider_id: $provider,
    model_id: $model,
    timestamp: now|todate
  }' > "$SKILL_DIR/state/current.json"

echo "✓ Saved state: $SESSION_ID"
exit 0