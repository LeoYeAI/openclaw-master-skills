#!/bin/bash
# Team Dispatch backups helper
# Usage:
#   bash <SKILL_DIR>/scripts/backups.sh list
#   bash <SKILL_DIR>/scripts/backups.sh latest
#   bash <SKILL_DIR>/scripts/backups.sh show <timestamp>

set -e

CMD="${1:-list}"
ARG="${2:-}"

BACKUP_ROOT="$HOME/.openclaw/backups/team-dispatch"
LATEST_FILE="$BACKUP_ROOT/latest"

case "$CMD" in
  list)
    if [ ! -d "$BACKUP_ROOT" ]; then
      echo "No backups dir: $BACKUP_ROOT"; exit 0
    fi
    echo "Backups under: $BACKUP_ROOT"
    ls -1 "$BACKUP_ROOT" | grep -E '^[0-9]{8}-[0-9]{6}$' | sort -r || true
    ;;
  latest)
    if [ ! -f "$LATEST_FILE" ]; then
      echo "No latest pointer: $LATEST_FILE"; exit 1
    fi
    echo "Latest backup: $(cat "$LATEST_FILE")"
    ;;
  show)
    if [ -z "$ARG" ]; then
      echo "Usage: backups.sh show <timestamp>"; exit 2
    fi
    DIR="$BACKUP_ROOT/$ARG"
    if [ ! -d "$DIR" ]; then
      echo "Not found: $DIR"; exit 1
    fi
    echo "Backup: $DIR"
    echo "- $(ls -1 "$DIR" | tr '\n' ' ' | sed 's/ $/\n/')"
    if [ -f "$DIR/openclaw.json.bak" ]; then
      echo "--- openclaw.json.bak (head) ---"
      head -40 "$DIR/openclaw.json.bak"
      echo "--------------------------------"
    fi
    if [ -f "$DIR/team-dispatch.json.bak" ]; then
      echo "--- team-dispatch.json.bak (head) ---"
      head -80 "$DIR/team-dispatch.json.bak"
      echo "-------------------------------------"
    fi
    ;;
  *)
    echo "Unknown command: $CMD"; exit 2
    ;;
esac
