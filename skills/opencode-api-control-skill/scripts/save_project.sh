#!/bin/bash
# Save project-specific state

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

PROJECT_NAME="$1"

if [ -z "$PROJECT_NAME" ]; then
  echo "Error: PROJECT_NAME required" >&2
  echo "Usage: $0 <project_name>" >&2
  exit 1
fi

if [ ! -f "$SKILL_DIR/state/current.json" ]; then
  echo "Error: No current state to save" >&2
  exit 1
fi

cp "$SKILL_DIR/state/current.json" "$SKILL_DIR/state/$PROJECT_NAME.json"
echo "✓ Saved project state: $PROJECT_NAME"
exit 0