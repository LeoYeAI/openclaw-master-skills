#!/bin/bash
# OpenClaw Backup Script
# Usage: ./backup.sh [backup_dir]

BACKUP_DIR="${1:-$HOME/openclaw-backups}"
DATE=$(date +%Y-%m-%d_%H%M)
BACKUP_FILE="$BACKUP_DIR/openclaw-$DATE.tar.gz"

mkdir -p "$BACKUP_DIR"

# Create backup (exclude completions cache and logs)
tar -czf "$BACKUP_FILE" \
    --exclude='completions' \
    --exclude='*.log' \
    -C "$HOME" .openclaw/ 2>/dev/null

if [ $? -eq 0 ]; then
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    
    # Rotate: keep only last 7 backups
    ls -t "$BACKUP_DIR"/openclaw-*.tar.gz 2>/dev/null | tail -n +8 | xargs -r rm
    
    COUNT=$(ls "$BACKUP_DIR"/openclaw-*.tar.gz 2>/dev/null | wc -l)
    
    echo "✅ Backup created: $BACKUP_FILE ($SIZE)"
    echo "📁 Total backups: $COUNT"
    exit 0
else
    echo "❌ Backup failed"
    exit 1
fi
