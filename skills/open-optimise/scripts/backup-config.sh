#!/bin/bash
# backup-config.sh — Snapshot openclaw.json before any change
# Usage: bash backup-config.sh [config-path] [label]
# Backups go to ~/.openclaw/config-backups/

set -euo pipefail

CONFIG="${1:-$HOME/.openclaw/openclaw.json}"
LABEL="${2:-manual}"
BACKUP_DIR="$HOME/.openclaw/config-backups"
BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

if [ ! -f "$CONFIG" ]; then
  echo -e "${RED}Config not found: $CONFIG${NC}"
  exit 1
fi

mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/openclaw-${TIMESTAMP}-${LABEL}.json"

cp "$CONFIG" "$BACKUP_FILE"
echo -e "${GREEN}✅ Backed up to:${NC} $BACKUP_FILE"
echo -e "${CYAN}Size:${NC} $(wc -c < "$BACKUP_FILE") bytes"

# Prune backups older than 30 days
PRUNED=$(find "$BACKUP_DIR" -name "openclaw-*.json" -mtime +30 -delete -print 2>/dev/null | wc -l)
if [ "$PRUNED" -gt 0 ]; then
  echo -e "${CYAN}Pruned:${NC} $PRUNED backups older than 30 days"
fi

# Show recent backups
echo ""
echo -e "${BOLD}Recent backups:${NC}"
ls -lt "$BACKUP_DIR"/openclaw-*.json 2>/dev/null | head -5 | while read -r line; do
  echo "  $line"
done

TOTAL=$(ls "$BACKUP_DIR"/openclaw-*.json 2>/dev/null | wc -l)
echo -e "${CYAN}Total backups:${NC} $TOTAL"
