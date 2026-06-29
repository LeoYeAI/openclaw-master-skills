#!/bin/bash
# _config-fix.sh — Standalone config fix script (no IPFS/crypto dependencies)
# Invoked via: config.sh fix (or directly for backwards compat)
#
# Lightweight 3-tier config recovery for watchdog escalation:
#   Tier A: Restore from latest config backup
#   Tier B: Run 'openclaw doctor --fix'
#   Tier C: Generate minimal safe config (last resort)
#
# After each tier, restarts gateway and checks health.
# Saves broken config as openclaw.json.broken-TIMESTAMP for debugging.
#
# Usage:
#   ./try-fix-config.sh
#   ./try-fix-config.sh --dry-run
#
# Exit codes:
#   0 = config fixed, gateway healthy
#   1 = all tiers failed

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OPENCLAW_CONFIG="${OPENCLAW_CONFIG:-$HOME/.openclaw/openclaw.json}"
BACKUP_DIR="${BACKUP_DIR:-$HOME/.amcp/config-backups}"
GATEWAY_SETTLE_TIME="${GATEWAY_SETTLE_TIME:-5}"
DRY_RUN=false
LOG_FILE="$HOME/.amcp/config-fix-$(date +%Y%m%d-%H%M%S).log"

# Parse args
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run) DRY_RUN=true; shift ;;
    --config) OPENCLAW_CONFIG="$2"; shift 2 ;;
    --backup-dir) BACKUP_DIR="$2"; shift 2 ;;
    *) shift ;;
  esac
done

mkdir -p "$(dirname "$LOG_FILE")"

log() {
  echo "[$(date -Iseconds)] $1" | tee -a "$LOG_FILE"
}

# ============================================================
# Gateway detection and restart (matches watchdog/resuscitate patterns)
# ============================================================
is_gateway_running() {
  if pgrep -f "openclaw-gateway" > /dev/null 2>&1; then
    return 0
  fi
  if pgrep -f "openclaw.*gateway" > /dev/null 2>&1; then
    return 0
  fi
  return 1
}

check_gateway_health() {
  # Determine port from config or env
  local port="${GATEWAY_PORT:-}"
  if [ -z "$port" ] && [ -f "$OPENCLAW_CONFIG" ]; then
    port=$(python3 -c "
import json, os
try:
    d = json.load(open(os.path.expanduser('$OPENCLAW_CONFIG')))
    print(d.get('gateway',{}).get('port',''))
except: pass
" 2>/dev/null || echo "")
  fi

  # Check configured port first, then defaults
  if [ -n "$port" ]; then
    curl -s --max-time 5 "http://localhost:${port}/health" > /dev/null 2>&1 && return 0
  fi
  for p in 3141 8080 18789; do
    curl -s --max-time 5 "http://localhost:${p}/health" > /dev/null 2>&1 && return 0
  done
  return 1
}

restart_gateway() {
  if [ "$DRY_RUN" = true ]; then
    log "[DRY-RUN] Would restart gateway"
    return 0
  fi

  # Try systemctl first
  if systemctl --user restart openclaw-gateway 2>/dev/null; then
    sleep "$GATEWAY_SETTLE_TIME"
    if is_gateway_running; then
      log "Gateway restarted via systemctl"
      return 0
    fi
  fi

  # Try direct restart
  if command -v openclaw &>/dev/null; then
    pkill -f "openclaw-gateway" 2>/dev/null || true
    sleep 2
    nohup openclaw gateway start > /tmp/openclaw-gateway.log 2>&1 &
    sleep "$GATEWAY_SETTLE_TIME"
    if is_gateway_running; then
      log "Gateway restarted directly"
      return 0
    fi
  fi

  log "Gateway restart failed"
  return 1
}

# ============================================================
# Save broken config before attempting fix
# ============================================================
save_broken_config() {
  if [ ! -f "$OPENCLAW_CONFIG" ]; then
    return 0
  fi

  local broken_path="${OPENCLAW_CONFIG}.broken-$(date +%Y%m%d-%H%M%S)"
  if [ "$DRY_RUN" = true ]; then
    log "[DRY-RUN] Would save broken config to: $broken_path"
    return 0
  fi

  cp "$OPENCLAW_CONFIG" "$broken_path"
  log "Saved broken config to: $broken_path"
}

# ============================================================
# Tier A: Restore from latest config backup
# ============================================================
tier_a_backup_restore() {
  log "--- Tier A: Restore from config backup ---"

  if [ ! -d "$BACKUP_DIR" ]; then
    log "No backup directory at $BACKUP_DIR"
    return 1
  fi

  local latest_backup
  latest_backup=$(ls -1t "$BACKUP_DIR"/openclaw-*.json 2>/dev/null | head -1)

  if [ -z "$latest_backup" ] || [ ! -f "$latest_backup" ]; then
    log "No backups found in $BACKUP_DIR"
    return 1
  fi

  log "Found backup: $latest_backup"

  # Validate backup is valid JSON
  if ! python3 -c "import json; json.load(open('$latest_backup'))" 2>/dev/null; then
    log "Backup is not valid JSON, skipping"
    return 1
  fi

  if [ "$DRY_RUN" = true ]; then
    log "[DRY-RUN] Would restore from: $latest_backup"
    return 0
  fi

  save_broken_config
  cp "$latest_backup" "$OPENCLAW_CONFIG"
  log "Restored config from backup: $(basename "$latest_backup")"

  # Restart and check
  if restart_gateway && check_gateway_health; then
    log "Tier A SUCCESS: Gateway healthy after backup restore"
    return 0
  fi

  log "Tier A: Gateway not healthy after backup restore"
  return 1
}

# ============================================================
# Tier B: Run 'openclaw doctor --fix'
# ============================================================
tier_b_doctor_fix() {
  log "--- Tier B: Run openclaw doctor --fix ---"

  local openclaw_bin
  openclaw_bin=$(command -v openclaw 2>/dev/null || echo "")

  if [ -z "$openclaw_bin" ]; then
    log "openclaw CLI not found, skipping Tier B"
    return 1
  fi

  if [ "$DRY_RUN" = true ]; then
    log "[DRY-RUN] Would run: openclaw doctor --fix"
    return 0
  fi

  save_broken_config

  local doctor_output
  doctor_output=$(timeout 60 "$openclaw_bin" doctor --fix 2>&1 || true)
  log "Doctor output: $doctor_output"

  # Restart and check
  if restart_gateway && check_gateway_health; then
    log "Tier B SUCCESS: Gateway healthy after openclaw doctor --fix"
    return 0
  fi

  log "Tier B: Gateway not healthy after doctor fix"
  return 1
}

# ============================================================
# Tier C: Generate minimal safe config (last resort)
# ============================================================
tier_c_minimal_config() {
  log "--- Tier C: Generate minimal safe config ---"

  # Try to preserve port and workspace from current/broken config
  local gateway_port=""
  local workspace_path=""
  if [ -f "$OPENCLAW_CONFIG" ]; then
    gateway_port=$(python3 -c "
import json
try:
    d = json.load(open('$OPENCLAW_CONFIG'))
    print(d.get('gateway',{}).get('port',''))
except: pass
" 2>/dev/null || echo "")
    workspace_path=$(python3 -c "
import json
try:
    d = json.load(open('$OPENCLAW_CONFIG'))
    ws = d.get('agents',{}).get('main',{}).get('workspacePath','')
    if not ws:
        ws = d.get('workspace',{}).get('path','')
    print(ws)
except: pass
" 2>/dev/null || echo "")
  fi

  # Defaults
  gateway_port="${gateway_port:-18789}"
  workspace_path="${workspace_path:-$HOME/.openclaw/workspace}"

  if [ "$DRY_RUN" = true ]; then
    log "[DRY-RUN] Would generate minimal config (port=$gateway_port, workspace=$workspace_path)"
    return 0
  fi

  save_broken_config

  # Generate minimal safe config — no plugins, no skills
  python3 -c "
import json, os

config = {
    'gateway': {
        'port': int('$gateway_port') if '$gateway_port'.isdigit() else 18789,
        'host': '127.0.0.1'
    },
    'agents': {
        'main': {
            'workspacePath': '$workspace_path'
        }
    },
    'skills': {
        'entries': {}
    },
    '_generated': 'minimal-safe-config',
    '_timestamp': '$(date -Iseconds)',
    '_note': 'Generated by config fix (Tier C). Re-add plugins/skills manually.'
}

config_path = os.path.expanduser('$OPENCLAW_CONFIG')
os.makedirs(os.path.dirname(config_path), exist_ok=True)
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)
" 2>/dev/null

  if [ $? -ne 0 ]; then
    log "Failed to generate minimal config"
    return 1
  fi

  log "Generated minimal safe config (port=$gateway_port, no plugins/skills)"

  # Restart and check
  if restart_gateway && check_gateway_health; then
    log "Tier C SUCCESS: Gateway healthy with minimal config"
    log "WARNING: Skills and plugins removed. Re-add via openclaw config or restore a good backup."
    return 0
  fi

  log "Tier C: Gateway not healthy even with minimal config"
  return 1
}

# ============================================================
# Main — try tiers in order
# ============================================================
main() {
  log "========================================="
  log "=== Config Fix Started ==="
  log "========================================="
  log "Config: $OPENCLAW_CONFIG"
  log "Backups: $BACKUP_DIR"
  log "Log: $LOG_FILE"

  if [ "$DRY_RUN" = true ]; then
    log "MODE: dry-run (no changes will be made)"
  fi

  # Notify start
  [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "Config fix started" 2>/dev/null || true

  # Tier A: Backup restore
  if tier_a_backup_restore; then
    [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "Config fix succeeded (Tier A: backup restore)" 2>/dev/null || true
    return 0
  fi

  # Tier B: openclaw doctor --fix
  if tier_b_doctor_fix; then
    [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "Config fix succeeded (Tier B: openclaw doctor --fix)" 2>/dev/null || true
    return 0
  fi

  # Tier C: Minimal safe config
  if tier_c_minimal_config; then
    [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "Config fix succeeded (Tier C: minimal safe config — skills removed)" 2>/dev/null || true
    return 0
  fi

  log ""
  log "========================================="
  log "ALL CONFIG FIX TIERS FAILED"
  log "========================================="
  [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "Config fix FAILED — all tiers exhausted. Manual intervention needed." 2>/dev/null || true
  return 1
}

main
