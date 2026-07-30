#!/bin/bash
# Load session state (source this file)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

if [ ! -f "$SKILL_DIR/state/current.json" ]; then
  echo "Error: No saved state found" >&2
  return 1 2>/dev/null || exit 1
fi

export BASE_URL=$(jq -r '.base_url' "$SKILL_DIR/state/current.json")
export PROJECT_PATH=$(jq -r '.project_path' "$SKILL_DIR/state/current.json")
export SESSION_ID=$(jq -r '.session_id' "$SKILL_DIR/state/current.json")

export PROVIDER_ID=$(jq -r '.provider_id' "$SKILL_DIR/state/current.json")

echo "✓ Loaded: Session=$SESSION_ID, Project=$PROJECT_PATH"