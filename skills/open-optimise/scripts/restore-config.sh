#!/bin/bash
# restore-config.sh — Restore a config backup and restart the gateway
# Usage: bash restore-config.sh [backup-file|"latest"]
# If no argument, lists available backups and prompts.

set -euo pipefail

CONFIG="$HOME/.openclaw/openclaw.json"
BACKUP_DIR="$HOME/.openclaw/config-backups"
BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

if [ ! -d "$BACKUP_DIR" ]; then
  echo -e "${RED}No backup directory found at $BACKUP_DIR${NC}"
  echo "Run backup-config.sh first to create backups."
  exit 1
fi

BACKUPS=($(ls -t "$BACKUP_DIR"/openclaw-*.json 2>/dev/null))

if [ ${#BACKUPS[@]} -eq 0 ]; then
  echo -e "${RED}No backups found.${NC}"
  exit 1
fi

TARGET="${1:-}"

if [ "$TARGET" = "latest" ]; then
  TARGET="${BACKUPS[0]}"
  echo -e "${CYAN}Using latest backup:${NC} $TARGET"
elif [ -z "$TARGET" ]; then
  echo -e "${BOLD}Available backups:${NC}"
  echo ""
  for i in "${!BACKUPS[@]}"; do
    FILE="${BACKUPS[$i]}"
    NAME=$(basename "$FILE")
    SIZE=$(wc -c < "$FILE")
    DATE=$(echo "$NAME" | sed 's/openclaw-\([0-9]*-[0-9]*\)-.*/\1/' | sed 's/\([0-9]\{4\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)-\([0-9]\{2\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)/\1-\2-\3 \4:\5:\6/')
    LABEL=$(echo "$NAME" | sed 's/openclaw-[0-9]*-[0-9]*-//' | sed 's/\.json//')
    printf "  ${CYAN}%2d${NC}) %s  (%s bytes)  label: %s\n" "$((i+1))" "$DATE" "$SIZE" "$LABEL"
  done
  echo ""
  echo -e "Usage: ${BOLD}bash restore-config.sh latest${NC}  (restores most recent)"
  echo -e "   or: ${BOLD}bash restore-config.sh /path/to/backup.json${NC}"
  exit 0
elif [ ! -f "$TARGET" ]; then
  # Maybe it's an index
  if [[ "$TARGET" =~ ^[0-9]+$ ]] && [ "$TARGET" -ge 1 ] && [ "$TARGET" -le ${#BACKUPS[@]} ]; then
    TARGET="${BACKUPS[$((TARGET-1))]}"
  else
    echo -e "${RED}Backup not found: $TARGET${NC}"
    exit 1
  fi
fi

# Safety: backup current config before restoring
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
PRE_RESTORE="$BACKUP_DIR/openclaw-${TIMESTAMP}-pre-restore.json"
cp "$CONFIG" "$PRE_RESTORE"
echo -e "${CYAN}Current config backed up to:${NC} $PRE_RESTORE"

# Restore
cp "$TARGET" "$CONFIG"
echo -e "${GREEN}✅ Restored from:${NC} $(basename "$TARGET")"

# Restart gateway
echo ""
echo -e "${YELLOW}Restarting gateway...${NC}"
if command -v openclaw &>/dev/null; then
  openclaw gateway restart 2>&1 || true
  echo -e "${GREEN}Gateway restart triggered.${NC}"
else
  # Try SIGUSR1 to the running process
  PID=$(pgrep -f "openclaw" | head -1 || true)
  if [ -n "$PID" ]; then
    kill -USR1 "$PID" 2>/dev/null && echo -e "${GREEN}Sent SIGUSR1 to PID $PID${NC}" || echo -e "${RED}Failed to signal PID $PID${NC}"
  else
    echo -e "${YELLOW}Could not find openclaw process. Restart manually.${NC}"
  fi
fi

echo ""
echo -e "${BOLD}Done.${NC} If things are still broken, try: bash restore-config.sh"
echo "to pick a different backup."
