#!/usr/bin/env bash
# specclaw init — Initialize SpecClaw in a project directory
# Usage: init.sh <project_dir> [project_name] [project_description]

set -euo pipefail

PROJECT_DIR="${1:-.}"
PROJECT_NAME="${2:-$(basename "$(cd "$PROJECT_DIR" && pwd)")}"
PROJECT_DESC="${3:-}"

SPECCLAW_DIR="$PROJECT_DIR/.specclaw"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

if [ -d "$SPECCLAW_DIR" ]; then
  echo "ERROR: .specclaw/ already exists in $PROJECT_DIR"
  exit 1
fi

# Create directory structure
mkdir -p "$SPECCLAW_DIR/changes/archive"

# Generate config from template
sed \
  -e "s|^  name: \"\"|  name: \"$PROJECT_NAME\"|" \
  -e "s|^  description: \"\"|  description: \"$PROJECT_DESC\"|" \
  "$SKILL_DIR/templates/config.yaml" > "$SPECCLAW_DIR/config.yaml"

# Create initial STATUS.md
cat > "$SPECCLAW_DIR/STATUS.md" << EOF
# 🦞 SpecClaw Dashboard

**Project:** $PROJECT_NAME
**Last Updated:** $(date -u +"%Y-%m-%d %H:%M UTC")

## Active Changes

_No active changes yet. Run \`specclaw propose "<idea>"\` to start._

## Pending Proposals

_None._

## Recently Completed

_None._

## Stats

- **Total changes:** 0
- **Active:** 0
- **Completed:** 0
EOF

echo "OK: Initialized SpecClaw in $SPECCLAW_DIR"
echo "  config: $SPECCLAW_DIR/config.yaml"
echo "  status: $SPECCLAW_DIR/STATUS.md"
echo "  changes: $SPECCLAW_DIR/changes/"
