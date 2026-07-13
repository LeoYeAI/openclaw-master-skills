#!/usr/bin/env bash
# lib/sync.sh — Google Drive sync daemon for Claw Drive

SYNC_DEBOUNCE_SEC=3
SYNC_AUTH_TIMEOUT=120

# Authenticate with Google Drive via rclone
sync_auth() {
  echo "🔐 Claw Drive — Google Drive Authorization"
  echo ""

  if ! command -v rclone &>/dev/null; then
    echo "❌ rclone not found. Install: brew install rclone"
    return 1
  fi

  if rclone listremotes 2>/dev/null | grep -q "^gdrive:$"; then
    echo "⚠️  rclone remote 'gdrive' already exists."
    echo "   To re-authorize, run: rclone config delete gdrive"
    echo "   Then run this command again."
    return 1
  fi

  echo "Starting rclone authorization..."
  echo ""

  # Start rclone in background so we can capture the token
  local rclone_out
  rclone_out=$(mktemp) || { echo "❌ mktemp failed"; return 1; }
  # Ensure token file is cleaned up on exit/interrupt
  trap 'rm -f "$rclone_out"' EXIT INT TERM

  rclone authorize "drive" --auth-no-open-browser > "$rclone_out" 2>&1 &
  local rclone_pid=$!

  # Wait for auth URL
  local waited=0
  local auth_url=""
  while [[ $waited -lt 10 ]]; do
    sleep 1
    ((waited++)) || true
    auth_url=$(grep -o 'http://127.0.0.1:53682/auth[?][^ ]*' "$rclone_out" 2>/dev/null | head -1 || true)
    [[ -n "$auth_url" ]] && break
  done

  if [[ -z "$auth_url" ]]; then
    echo "❌ rclone failed to start auth server."
    cat "$rclone_out"
    rm -f "$rclone_out"
    kill "$rclone_pid" 2>/dev/null
    return 1
  fi

  # Try to open browser on the machine
  open "$auth_url" 2>/dev/null || true

  echo "🌐 Auth URL: $auth_url"
  echo ""
  echo "⏳ Waiting for authorization..."
  echo "   Complete sign-in in the browser on this machine."

  # Wait for rclone to finish
  wait "$rclone_pid" 2>/dev/null
  local exit_code=$?

  if [[ $exit_code -ne 0 ]]; then
    echo "❌ Authorization failed or timed out."
    cat "$rclone_out"
    rm -f "$rclone_out"
    return 1
  fi

  # Extract token
  local token
  token=$(sed -n '/^{/,/^}/p' "$rclone_out" | head -20)
  rm -f "$rclone_out"

  if [[ -z "$token" ]]; then
    echo "❌ Could not extract token."
    return 1
  fi

  # Configure rclone remote
  rclone config create gdrive drive config_is_local=false config_token="$token" > /dev/null 2>&1

  echo "✅ Authorization successful!"
  echo "✅ rclone remote 'gdrive' configured."

  # Create default .sync-config
  if [[ ! -f "$CLAW_DRIVE_SYNC_CONFIG" ]]; then
    cat > "$CLAW_DRIVE_SYNC_CONFIG" <<EOF
backend: google-drive
remote: gdrive:claw-drive
exclude:
  - identity/
  - .hashes
EOF
    echo "✅ Created .sync-config"
  fi

  echo ""
  echo "🎉 Google Drive sync is ready!"
  echo "   Run: claw-drive sync start"
}

# Check sync prerequisites
sync_setup() {
  echo "🗄️  Claw Drive Sync Setup"
  echo ""

  local ok=true

  if command -v rclone &>/dev/null; then
    echo "✅ rclone installed ($(rclone version | head -1))"
  else
    echo "❌ rclone not found. Install: brew install rclone"
    ok=false
  fi

  if command -v fswatch &>/dev/null; then
    echo "✅ fswatch installed"
  else
    echo "❌ fswatch not found. Install: brew install fswatch"
    ok=false
  fi

  if [[ -d "$CLAW_DRIVE_DIR" ]]; then
    echo "✅ Drive directory: $CLAW_DRIVE_DIR"
  else
    echo "❌ Drive directory not found: $CLAW_DRIVE_DIR"
    ok=false
  fi

  local remote
  remote=$(sync_config_get "remote")
  if [[ -z "$remote" ]]; then
    echo ""
    echo "⚠️  No .sync-config found. Create $CLAW_DRIVE_SYNC_CONFIG:"
    echo ""
    echo "  backend: google-drive"
    echo "  remote: gdrive:claw-drive"
    echo "  exclude:"
    echo "    - identity/"
    echo "    - .hashes"
    return 1
  fi

  local remote_name="${remote%%:*}"
  if rclone listremotes | grep -q "^${remote_name}:$"; then
    echo "✅ rclone remote '$remote_name' configured"
  else
    echo "❌ rclone remote '$remote_name' not found. Run: rclone config"
    ok=false
  fi

  [[ "$ok" == "true" ]] || return 1

  echo ""
  echo "✅ Ready! Run: claw-drive sync start"
}

# One-shot sync
sync_push() {
  local remote
  remote=$(sync_config_get "remote")
  if [[ -z "$remote" ]]; then
    echo "❌ No remote configured. Run: claw-drive sync setup"
    return 1
  fi

  local exclude_args=()
  mapfile -t exclude_args < <(sync_build_exclude_args_lines)

  echo "📤 Syncing $CLAW_DRIVE_DIR → $remote ..."
  rclone sync "$CLAW_DRIVE_DIR" "$remote" "${exclude_args[@]}" --verbose 2>&1

  date -u +"%Y-%m-%dT%H:%M:%SZ" > "$CLAW_DRIVE_SYNC_STATE"
  echo "✅ Sync complete."
}

# Internal: fswatch loop (called by launchd)
sync_watch_loop() {
  local remote
  remote=$(sync_config_get "remote")
  if [[ -z "$remote" ]]; then
    echo "❌ No remote configured." >&2
    return 1
  fi

  local exclude_args=()
  mapfile -t exclude_args < <(sync_build_exclude_args_lines)

  echo "👀 Watching $CLAW_DRIVE_DIR for changes (debounce: ${SYNC_DEBOUNCE_SEC}s)..."
  echo "📡 Remote: $remote"

  fswatch -o -l "$SYNC_DEBOUNCE_SEC" \
    --exclude '\.sync-state$' \
    --exclude '\.sync-config$' \
    --exclude '\.DS_Store$' \
    "$CLAW_DRIVE_DIR" | while read -r _count; do
    echo "[$(date '+%H:%M:%S')] Change detected, syncing..."
    if rclone sync "$CLAW_DRIVE_DIR" "$remote" "${exclude_args[@]}" 2>&1; then
      date -u +"%Y-%m-%dT%H:%M:%SZ" > "$CLAW_DRIVE_SYNC_STATE"
      echo "[$(date '+%H:%M:%S')] ✅ Sync complete."
    else
      echo "[$(date '+%H:%M:%S')] ❌ Sync failed." >&2
    fi
  done
}

# Start the sync daemon via launchd
sync_start() {
  if launchctl list "$CLAW_DRIVE_PLIST_NAME" 2>/dev/null; then
    echo "⚠️  Already running. Use 'claw-drive sync stop' first."
    return 1
  fi

  mkdir -p "$CLAW_DRIVE_LOG_DIR"

  local script_path
  script_path="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/bin/claw-drive"

  cat > "$CLAW_DRIVE_PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$CLAW_DRIVE_PLIST_NAME</string>
    <key>ProgramArguments</key>
    <array>
        <string>$script_path</string>
        <string>sync</string>
        <string>_watch</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
        <key>CLAW_DRIVE_DIR</key>
        <string>$CLAW_DRIVE_DIR</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$CLAW_DRIVE_LOG_DIR/sync.log</string>
    <key>StandardErrorPath</key>
    <string>$CLAW_DRIVE_LOG_DIR/sync.err</string>
</dict>
</plist>
EOF

  launchctl load "$CLAW_DRIVE_PLIST_PATH"
  echo "✅ Sync daemon started."
  echo "   Logs: $CLAW_DRIVE_LOG_DIR/sync.log"
}

# Stop the sync daemon
sync_stop() {
  if [[ -f "$CLAW_DRIVE_PLIST_PATH" ]]; then
    launchctl unload "$CLAW_DRIVE_PLIST_PATH" 2>/dev/null || true
    rm -f "$CLAW_DRIVE_PLIST_PATH"
    echo "✅ Sync daemon stopped."
  else
    echo "⚠️  Not running."
  fi
}

# Show sync status
sync_status() {
  local format="${1:-table}"

  local running="false"
  if launchctl list "$CLAW_DRIVE_PLIST_NAME" &>/dev/null; then
    running="true"
  fi

  local remote
  remote=$(sync_config_get "remote")

  local last_sync="never"
  if [[ -f "$CLAW_DRIVE_SYNC_STATE" ]]; then
    last_sync=$(cat "$CLAW_DRIVE_SYNC_STATE")
  fi

  if [[ "$format" == "json" ]]; then
    printf '{"daemon_running":%s,"remote":"%s","last_sync":"%s"}\n' \
      "$running" "${remote:-null}" "$last_sync"
  else
    echo "🗄️  Claw Drive Sync Status"
    echo ""
    if [[ "$running" == "true" ]]; then
      echo "🟢 Daemon: running"
    else
      echo "🔴 Daemon: stopped"
    fi
    echo "📡 Remote: ${remote:-not configured}"
    echo "🕐 Last sync: $last_sync"

    local excludes
    excludes=$(sync_config_excludes)
    if [[ -n "$excludes" ]]; then
      echo "🚫 Excludes:"
      while IFS= read -r e; do
        echo "   - $e"
      done <<< "$excludes"
    fi
  fi
}
