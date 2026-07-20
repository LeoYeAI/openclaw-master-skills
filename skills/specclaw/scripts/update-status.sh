#!/usr/bin/env bash
# Regenerate STATUS.md dashboard from current state
# Usage: update-status.sh <specclaw_dir>

set -euo pipefail

SPECCLAW_DIR="$1"
CHANGES_DIR="$SPECCLAW_DIR/changes"
ARCHIVE_DIR="$CHANGES_DIR/archive"
STATUS_FILE="$SPECCLAW_DIR/STATUS.md"

# Read project name from config
PROJECT_NAME=$(grep 'name:' "$SPECCLAW_DIR/config.yaml" | head -1 | sed 's/.*name: *"\(.*\)"/\1/')

ACTIVE_COUNT=0
COMPLETED_COUNT=0
ACTIVE_LINES=""
PENDING_LINES=""
COMPLETED_LINES=""

# Scan active changes
for change_dir in "$CHANGES_DIR"/*/; do
  [ -d "$change_dir" ] || continue
  [ "$(basename "$change_dir")" = "archive" ] && continue

  change_name=$(basename "$change_dir")

  if [ -f "$change_dir/tasks.md" ]; then
    total=$(grep -c '^\- \[' "$change_dir/tasks.md" 2>/dev/null || true)
    done=$(grep -c '^\- \[x\]' "$change_dir/tasks.md" 2>/dev/null || true)
    failed=$(grep -c '^\- \[!\]' "$change_dir/tasks.md" 2>/dev/null || true)
    total=${total:-0}
    done=${done:-0}
    failed=${failed:-0}

    if [ "$total" -gt 0 ]; then
      pct=$((done * 100 / total))
    else
      pct=0
    fi

    status_emoji="🔨"
    [ "$failed" -gt 0 ] && status_emoji="⚠️"
    [ "$done" -eq "$total" ] && [ "$total" -gt 0 ] && status_emoji="✅"

    ACTIVE_LINES="${ACTIVE_LINES}\n- $status_emoji **$change_name** — $done/$total tasks ($pct%) ${failed:+| $failed failed}"
    ACTIVE_COUNT=$((ACTIVE_COUNT + 1))
  elif [ -f "$change_dir/proposal.md" ]; then
    PENDING_LINES="${PENDING_LINES}\n- 📋 **$change_name** — proposal ready, awaiting planning"
  fi
done

# Scan archived changes
if [ -d "$ARCHIVE_DIR" ]; then
  for arch_dir in "$ARCHIVE_DIR"/*/; do
    [ -d "$arch_dir" ] || continue
    arch_name=$(basename "$arch_dir")
    COMPLETED_LINES="${COMPLETED_LINES}\n- ✅ **$arch_name**"
    COMPLETED_COUNT=$((COMPLETED_COUNT + 1))
  done
fi

TOTAL=$((ACTIVE_COUNT + COMPLETED_COUNT))

cat > "$STATUS_FILE" << EOF
# 🦞 SpecClaw Dashboard

**Project:** $PROJECT_NAME
**Last Updated:** $(date -u +"%Y-%m-%d %H:%M UTC")

## Active Changes

$([ -n "$ACTIVE_LINES" ] && echo -e "$ACTIVE_LINES" || echo "_No active changes._")

## Pending Proposals

$([ -n "$PENDING_LINES" ] && echo -e "$PENDING_LINES" || echo "_None._")

## Recently Completed

$([ -n "$COMPLETED_LINES" ] && echo -e "$COMPLETED_LINES" || echo "_None._")

## Stats

- **Total changes:** $TOTAL
- **Active:** $ACTIVE_COUNT
- **Completed:** $COMPLETED_COUNT
EOF

echo "OK: Updated $STATUS_FILE"
