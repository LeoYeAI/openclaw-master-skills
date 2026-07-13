#!/usr/bin/env bash
# lib/config.sh — Configuration management for Claw Drive

CLAW_DRIVE_CONFIG_FILE="${CLAW_DRIVE_CONFIG_FILE:-$HOME/.config/claw-drive/config}"

# Load saved drive path from config, env override takes priority
if [[ -n "${CLAW_DRIVE_DIR:-}" ]]; then
  : # env override
elif [[ -f "$CLAW_DRIVE_CONFIG_FILE" ]]; then
  CLAW_DRIVE_DIR=$(cat "$CLAW_DRIVE_CONFIG_FILE")
else
  CLAW_DRIVE_DIR="$HOME/claw-drive"
fi
CLAW_DRIVE_INDEX="$CLAW_DRIVE_DIR/INDEX.jsonl"
CLAW_DRIVE_HASHES="$CLAW_DRIVE_DIR/.hashes"
CLAW_DRIVE_SYNC_CONFIG="$CLAW_DRIVE_DIR/.sync-config"
CLAW_DRIVE_SYNC_STATE="$CLAW_DRIVE_DIR/.sync-state"
CLAW_DRIVE_LOG_DIR="$HOME/Library/Logs/claw-drive"
CLAW_DRIVE_PLIST_NAME="com.claw-drive.sync"
CLAW_DRIVE_PLIST_PATH="$HOME/Library/LaunchAgents/$CLAW_DRIVE_PLIST_NAME.plist"

CLAW_DRIVE_CATEGORIES=(
  documents finance insurance medical travel identity
  receipts contracts photos misc
)

# Ensure drive directory and essential files exist
claw_drive_init() {
  if [[ ! -d "$CLAW_DRIVE_DIR" ]]; then
    echo "❌ Drive directory not found: $CLAW_DRIVE_DIR"
    echo "   Run: claw-drive init"
    return 1
  fi
  [[ -f "$CLAW_DRIVE_HASHES" ]] || touch "$CLAW_DRIVE_HASHES"
  return 0
}

# Parse sync config: get a top-level key value
sync_config_get() {
  local key="$1"
  if [[ -f "$CLAW_DRIVE_SYNC_CONFIG" ]]; then
    grep -E "^${key}:" "$CLAW_DRIVE_SYNC_CONFIG" | sed "s/^${key}:[[:space:]]*//" | tr -d '"'"'"
  fi
}

# Parse sync config: get exclude list
sync_config_excludes() {
  if [[ -f "$CLAW_DRIVE_SYNC_CONFIG" ]]; then
    sed -n '/^exclude:/,/^[^ -]/p' "$CLAW_DRIVE_SYNC_CONFIG" | grep -E '^\s*-' | sed 's/^[[:space:]]*-[[:space:]]*//'
  fi
}

# Build rclone exclude arguments from sync config as a safe array.
# Output format: one arg per line ("--exclude" then pattern), for mapfile consumption.
sync_build_exclude_args_lines() {
  while IFS= read -r pattern; do
    [[ -n "$pattern" ]] || continue
    printf '%s\n' "--exclude" "$pattern"
  done < <(sync_config_excludes)

  # Always exclude internal state files
  printf '%s\n' "--exclude" ".sync-config" "--exclude" ".sync-state"
}
