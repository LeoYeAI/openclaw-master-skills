#!/bin/bash
# disk-cleanup.sh — Auto-cleanup when disk usage is high
# Part of proactive-amcp skill
# Usage: disk-cleanup.sh [--threshold 85] [--dry-run]

set -euo pipefail

THRESHOLD=85
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --threshold) THRESHOLD="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    *) shift ;;
  esac
done

# Get current disk usage percentage
DISK_PCT=$(df / | tail -1 | awk '{print int($5)}')

echo "Disk usage: ${DISK_PCT}% (threshold: ${THRESHOLD}%)"

if [ "$DISK_PCT" -le "$THRESHOLD" ]; then
  echo "✅ Disk OK, no cleanup needed"
  exit 0
fi

echo "⚠️ Disk above threshold, cleaning..."

BEFORE_FREE=$(df / | tail -1 | awk '{print $4}')

cleanup() {
  local name="$1"
  local cmd="$2"
  
  if [ "$DRY_RUN" = true ]; then
    echo "[DRY-RUN] Would run: $cmd"
  else
    echo "Cleaning: $name"
    eval "$cmd" 2>/dev/null || true
  fi
}

# Safe cleanup targets (all can be rebuilt on demand)
cleanup "pnpm store" "rm -rf ~/.local/share/pnpm/store"
cleanup "go mod cache" "go clean -modcache"
cleanup "pip cache" "rm -rf ~/.cache/pip"
cleanup "npm cache" "npm cache clean --force"
cleanup "yarn cache" "rm -rf ~/.cache/yarn"
cleanup "old tmp logs" "find /tmp -name '*.log' -mtime +3 -delete"
cleanup "old openclaw logs" "find /tmp/openclaw -name '*.log' -mtime +7 -delete"
cleanup "old coverage" "find ~ -name 'coverage' -type d -mtime +7 -exec rm -rf {} + 2>/dev/null"
cleanup "pytest cache" "find ~ -name '.pytest_cache' -type d -exec rm -rf {} + 2>/dev/null"
cleanup "mypy cache" "find ~ -name '.mypy_cache' -type d -exec rm -rf {} + 2>/dev/null"

if [ "$DRY_RUN" = true ]; then
  echo "[DRY-RUN] No changes made"
  exit 0
fi

AFTER_FREE=$(df / | tail -1 | awk '{print $4}')
DISK_AFTER=$(df / | tail -1 | awk '{print int($5)}')

echo ""
echo "📊 Results:"
echo "  Before: ${BEFORE_FREE} free"
echo "  After:  ${AFTER_FREE} free"
echo "  Disk:   ${DISK_AFTER}%"

if [ "$DISK_AFTER" -gt 90 ]; then
  echo ""
  echo "🚨 CRITICAL: Disk still above 90% after cleanup!"
  echo "Manual intervention required."
  exit 1
elif [ "$DISK_AFTER" -gt "$THRESHOLD" ]; then
  echo ""
  echo "⚠️ Warning: Disk still above threshold but manageable"
  exit 0
else
  echo ""
  echo "✅ Disk cleaned successfully"
  exit 0
fi
