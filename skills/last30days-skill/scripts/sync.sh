#!/usr/bin/env bash
# sync.sh - Deploy last30days skill to all host locations
# Usage: bash scripts/sync.sh  (run from repo root)
set -euo pipefail

SRC="$(cd "$(dirname "$0")/.." && pwd)"
echo "Source: $SRC"

TARGETS=(
  "$HOME/.claude/skills/last30days"
  "$HOME/.agents/skills/last30days"
  "$HOME/.codex/skills/last30days"
)

for t in "${TARGETS[@]}"; do
  echo ""
  echo "--- Syncing to $t ---"
  mkdir -p "$t/scripts/lib"

  # SKILL.md
  cp "$SRC/SKILL.md" "$t/"

  # Main script
  cp "$SRC/scripts/last30days.py" "$t/scripts/"

  # All lib modules
  cp "$SRC/scripts/lib/"*.py "$t/scripts/lib/"

  # Vendor directory (bird-search CLI)
  if [ -d "$SRC/scripts/lib/vendor" ]; then
    cp -r "$SRC/scripts/lib/vendor" "$t/scripts/lib/"
  fi

  # Fixtures
  if [ -d "$SRC/fixtures" ]; then
    mkdir -p "$t/fixtures"
    cp -r "$SRC/fixtures/"* "$t/fixtures/" 2>/dev/null || true
  fi

  # Count and report
  mod_count=$(ls "$t/scripts/lib/"*.py 2>/dev/null | wc -l | tr -d ' ')
  echo "  Copied $mod_count modules"

  # Verify imports
  if (cd "$t/scripts" && python3 -c "from lib import youtube_yt, bird_x, render, ui; print('  Import check: OK')" 2>&1); then
    true
  else
    echo "  Import check FAILED"
  fi
done

echo ""
echo "Sync complete."
