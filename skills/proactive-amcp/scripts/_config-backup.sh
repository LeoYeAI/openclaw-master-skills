#!/bin/bash
# _config-backup.sh — Automatic OpenClaw config backup system
# Invoked via: config.sh backup (or directly for backwards compat)
#
# Creates timestamped backups of ~/.openclaw/openclaw.json when config is valid.
# Deduplicates via SHA-256 hash. Keeps last N backups, prunes older ones.
#
# Usage:
#   ./backup-config.sh                   Create backup if config is valid and changed
#   ./backup-config.sh --force           Create backup even if unchanged
#   ./backup-config.sh --list            List existing backups
#   ./backup-config.sh --restore [FILE]  Restore from backup (latest or specified)
#
# Exit codes:
#   0 = backup created (or skipped — unchanged)
#   1 = config invalid or error
#   2 = no config file found

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OPENCLAW_CONFIG="${OPENCLAW_CONFIG:-$HOME/.openclaw/openclaw.json}"
BACKUP_DIR="${BACKUP_DIR:-$HOME/.amcp/config-backups}"
MAX_BACKUPS="${MAX_BACKUPS:-10}"

# ============================================================
# Helpers
# ============================================================

ensure_backup_dir() {
  mkdir -p "$BACKUP_DIR"
}

# Compute SHA-256 of a file (portable across Linux/macOS)
file_hash() {
  local file="$1"
  if command -v sha256sum &>/dev/null; then
    sha256sum "$file" | cut -d' ' -f1
  elif command -v shasum &>/dev/null; then
    shasum -a 256 "$file" | cut -d' ' -f1
  else
    python3 -c "import hashlib; print(hashlib.sha256(open('$file','rb').read()).hexdigest())"
  fi
}

# Get hash of most recent backup (empty string if none)
latest_backup_hash() {
  local latest
  latest=$(ls -1t "$BACKUP_DIR"/openclaw-*.json 2>/dev/null | head -1)
  if [ -n "$latest" ] && [ -f "$latest" ]; then
    file_hash "$latest"
  else
    echo ""
  fi
}

# Validate config — try openclaw validate, fall back to jq syntax check
validate_config() {
  local config_file="$1"

  if [ ! -f "$config_file" ]; then
    echo "ERROR: Config file not found: $config_file" >&2
    return 2
  fi

  # Try openclaw config validate first (semantic validation)
  if command -v openclaw &>/dev/null; then
    if openclaw config validate 2>/dev/null; then
      return 0
    fi
    # If openclaw exists but validate failed, config is bad
    echo "ERROR: Config failed openclaw validation" >&2
    return 1
  fi

  # Fallback: at least verify valid JSON
  if command -v jq &>/dev/null; then
    if jq empty "$config_file" 2>/dev/null; then
      return 0
    fi
    echo "ERROR: Config is not valid JSON" >&2
    return 1
  fi

  # Last resort: python3 JSON parse
  if python3 -c "import json; json.load(open('$config_file'))" 2>/dev/null; then
    return 0
  fi

  echo "ERROR: Config is not valid JSON" >&2
  return 1
}

# ============================================================
# Core: create_config_backup
# ============================================================

create_config_backup() {
  local force="${1:-false}"

  if [ ! -f "$OPENCLAW_CONFIG" ]; then
    echo "ERROR: No OpenClaw config at $OPENCLAW_CONFIG" >&2
    return 2
  fi

  # Only backup known-good configs
  if ! validate_config "$OPENCLAW_CONFIG"; then
    echo "SKIP: Config is invalid — not backing up a broken config" >&2
    return 1
  fi

  ensure_backup_dir

  # Compare hash to latest backup — skip if unchanged
  local current_hash
  current_hash=$(file_hash "$OPENCLAW_CONFIG")
  local latest_hash
  latest_hash=$(latest_backup_hash)

  if [ "$force" != "true" ] && [ "$current_hash" = "$latest_hash" ] && [ -n "$latest_hash" ]; then
    echo "SKIP: Config unchanged (hash: ${current_hash:0:12}...)"
    return 0
  fi

  # Generate timestamped backup
  local timestamp
  timestamp=$(date +%Y%m%d-%H%M%S)
  local backup_file="$BACKUP_DIR/openclaw-${timestamp}.json"

  cp "$OPENCLAW_CONFIG" "$backup_file"
  chmod 600 "$backup_file"

  echo "BACKUP: $backup_file (hash: ${current_hash:0:12}...)"

  # Prune old backups — keep last MAX_BACKUPS
  prune_old_backups

  return 0
}

# ============================================================
# Prune — keep last N backups
# ============================================================

prune_old_backups() {
  local count
  count=$(ls -1 "$BACKUP_DIR"/openclaw-*.json 2>/dev/null | wc -l)

  if [ "$count" -le "$MAX_BACKUPS" ]; then
    return 0
  fi

  local to_remove=$((count - MAX_BACKUPS))
  # ls -1t sorts newest first; tail gives oldest
  ls -1t "$BACKUP_DIR"/openclaw-*.json | tail -n "$to_remove" | while read -r old_backup; do
    rm -f "$old_backup"
    echo "PRUNED: $(basename "$old_backup")"
  done
}

# ============================================================
# List — show existing backups
# ============================================================

list_backups() {
  ensure_backup_dir

  local backups
  backups=$(ls -1t "$BACKUP_DIR"/openclaw-*.json 2>/dev/null || true)

  if [ -z "$backups" ]; then
    echo "No backups found in $BACKUP_DIR"
    return 0
  fi

  echo "Config backups in $BACKUP_DIR:"
  echo ""
  local i=1
  echo "$backups" | while read -r backup; do
    local size
    size=$(stat --printf="%s" "$backup" 2>/dev/null || stat -f "%z" "$backup" 2>/dev/null || echo "?")
    local hash
    hash=$(file_hash "$backup")
    echo "  $i. $(basename "$backup")  (${size} bytes, hash: ${hash:0:12}...)"
    i=$((i + 1))
  done
}

# ============================================================
# Restore — restore config from backup
# ============================================================

restore_from_backup() {
  local target="${1:-}"

  ensure_backup_dir

  if [ -z "$target" ]; then
    # Use latest backup
    target=$(ls -1t "$BACKUP_DIR"/openclaw-*.json 2>/dev/null | head -1)
    if [ -z "$target" ]; then
      echo "ERROR: No backups found in $BACKUP_DIR" >&2
      return 1
    fi
  fi

  if [ ! -f "$target" ]; then
    # Maybe they gave just the filename
    if [ -f "$BACKUP_DIR/$target" ]; then
      target="$BACKUP_DIR/$target"
    else
      echo "ERROR: Backup file not found: $target" >&2
      return 1
    fi
  fi

  # Validate backup is valid JSON before restoring
  if ! python3 -c "import json; json.load(open('$target'))" 2>/dev/null; then
    echo "ERROR: Backup file is not valid JSON: $target" >&2
    return 1
  fi

  # Save current broken config
  if [ -f "$OPENCLAW_CONFIG" ]; then
    local broken_backup="$OPENCLAW_CONFIG.broken-$(date +%Y%m%d-%H%M%S)"
    cp "$OPENCLAW_CONFIG" "$broken_backup"
    echo "Saved broken config to: $broken_backup"
  fi

  cp "$target" "$OPENCLAW_CONFIG"
  echo "RESTORED: $OPENCLAW_CONFIG from $(basename "$target")"
  return 0
}

# ============================================================
# Main
# ============================================================

case "${1:-}" in
  --force)
    create_config_backup "true"
    ;;
  --list)
    list_backups
    ;;
  --restore)
    restore_from_backup "${2:-}"
    ;;
  -h|--help)
    echo "Usage: $(basename "$0") [--force] [--list] [--restore [FILE]]"
    echo ""
    echo "  (no args)      Create backup if config is valid and changed"
    echo "  --force        Create backup even if unchanged"
    echo "  --list         List existing backups"
    echo "  --restore [F]  Restore from backup (latest or specified)"
    exit 0
    ;;
  *)
    create_config_backup "false"
    ;;
esac
