#!/bin/bash
# Team Dispatch restore (rollback) script
# Restores openclaw.json + team-dispatch.json from a backup created by setup.sh
# Usage:
#   bash <SKILL_DIR>/scripts/restore.sh --latest
#   bash <SKILL_DIR>/scripts/restore.sh --from <backupDir>
#   bash <SKILL_DIR>/scripts/restore.sh --dry-run

set -euo pipefail

DRY_RUN=0
FROM=""
USE_LATEST=0

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --latest) USE_LATEST=1; shift ;;
    --from) FROM="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 2 ;;
  esac
done

run() {
  if [ "$DRY_RUN" = "1" ]; then
    printf '[dry-run]'; printf ' %q' "$@"; printf '\n'
  else
    "$@"
  fi
}

say() { echo "$@"; }

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_ROOT="$HOME/.openclaw/backups/team-dispatch"
LATEST_FILE="$BACKUP_ROOT/latest"
OPENCLAW_JSON="$HOME/.openclaw/openclaw.json"
CFG="$HOME/.openclaw/configs/team-dispatch.json"

if [ "$USE_LATEST" = "1" ]; then
  if [ ! -f "$LATEST_FILE" ]; then
    echo "No latest backup pointer: $LATEST_FILE"; exit 1
  fi
  FROM="$(cat "$LATEST_FILE")"
fi

if [ -z "$FROM" ]; then
  echo "Please specify --latest or --from <backupDir>"; exit 2
fi

say "♻️  Team Dispatch restore"
say "Backup dir: $FROM"

if [ ! -d "$FROM" ]; then
  echo "Backup dir not found: $FROM"; exit 1
fi

# restore openclaw.json
if [ -f "$FROM/openclaw.json.bak" ]; then
  run cp "$FROM/openclaw.json.bak" "$OPENCLAW_JSON"
  say "✅ restored: $OPENCLAW_JSON"
else
  say "⏭️  no openclaw.json backup in $FROM"
fi

# restore team-dispatch config
if [ -f "$FROM/team-dispatch.json.bak" ]; then
  run mkdir -p "$HOME/.openclaw/configs"
  run cp "$FROM/team-dispatch.json.bak" "$CFG"
  say "✅ restored: $CFG"
else
  say "⏭️  no team-dispatch.json backup in $FROM"
fi

# restart gateway
say ""
say "🔄 restarting gateway..."
run openclaw gateway restart
if [ "$DRY_RUN" != "1" ]; then
  openclaw gateway status | head -20
fi

say ""
say "✅ restore done."
