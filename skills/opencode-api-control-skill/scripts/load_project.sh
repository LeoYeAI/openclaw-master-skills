#!/bin/bash
# Load project-specific state

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

PROJECT_NAME="$1"

if [ -z "$PROJECT_NAME" ]; then
  echo "Error: PROJECT_NAME required" >&2
  echo "Usage: $0 <project_name>" >&2
  exit 1
fi

if [ ! -f "$SKILL_DIR/state/$PROJECT_NAME.json" ]; then
  echo "Error: Project state not found: $PROJECT_NAME" >&2
  exit 1
fi

cp "$SKILL_DIR/state/$PROJECT_NAME.json" "$SKILL_DIR/state/current.json"
echo "✓ Loaded project: $PROJECT_NAME"
exit 0