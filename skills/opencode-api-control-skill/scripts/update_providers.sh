#!/bin/bash
# Update connected providers cache

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Read config
BASE_URL=$(jq -r '.base_url' "$SKILL_DIR/config.json")
PROJECTS_DIR=$(jq -r '.projects_base_dir' "$SKILL_DIR/config.json")

# Use any project path for API call
PROJECT_PATH="${1:-$PROJECTS_DIR}"

# Fetch providers
PROVIDERS=$(curl -s "$BASE_URL/provider?directory=$PROJECT_PATH")

# Filter to connected + opencode only
echo "$PROVIDERS" | jq '{
  connected: .connected,
  providers: [
    .all[] | 
    select(
      (.id as $id | (.connected | index($id))) or 
      .id == "opencode"
    ) |
    {
      id,
      name,
      models: [.models | to_entries[] | .key]
    }
  ]
}' > "$SKILL_DIR/providers.json"

PROVIDER_COUNT=$(jq '.providers | length' "$SKILL_DIR/providers.json")
echo "✓ Updated providers cache: $PROVIDER_COUNT providers available"
exit 0