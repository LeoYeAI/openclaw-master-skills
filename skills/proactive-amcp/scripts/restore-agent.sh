#!/bin/bash
# restore-agent.sh - Full resurrection flow
# Usage: ./restore-agent.sh [--from-cid <cid>] [--key-file <path>]
#
# Solvr: SEARCH only (read-only). Agent posts after alive.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AMCP_CLI="${AMCP_CLI:-$(command -v amcp 2>/dev/null || echo "$HOME/bin/amcp")}"
IDENTITY_PATH="${IDENTITY_PATH:-$HOME/.amcp/identity.json}"

# Ensure Node.js webcrypto is available for amcp CLI (fixes "crypto.subtle must be defined")
# Node 18 needs this flag; Node 20+ has webcrypto by default (flag is a harmless no-op)
# Critical for systemd/cron contexts where env may be minimal
case "${NODE_OPTIONS:-}" in
  *--experimental-global-webcrypto*) ;;
  *) export NODE_OPTIONS="${NODE_OPTIONS:+$NODE_OPTIONS }--experimental-global-webcrypto" ;;
esac
LAST_CHECKPOINT_FILE="$HOME/.amcp/last-checkpoint.json"
CONTENT_DIR="${CONTENT_DIR:-$HOME/.openclaw/workspace}"
AGENT_NAME="${AGENT_NAME:-Agent}"
RECOVERY_LOG="$HOME/.amcp/recovery-$(date +%Y%m%d-%H%M%S).log"
LOCK_FILE="$HOME/.amcp/resurrection.lock"
GATEWAY_SETTLE_TIME="${GATEWAY_SETTLE_TIME:-5}"
CHECKPOINT_KEYS_FILE="$HOME/.amcp/checkpoint-keys.json"
KEY_FILE=""

# Solvr config
SOLVR_BASE="https://api.solvr.dev/v1"
CURRENT_DEATH_PROBLEM_FILE="$HOME/.amcp/current-death-problem.json"
CURRENT_APPROACH_FILE="$HOME/.amcp/current-approach.json"

# SOLVR_API_KEY is resolved automatically by solvr-integration.sh
# via _resolve_solvr_api_key() fallback chain when sourced below.

# Track temp files for cleanup
TEMP_FILES=()
cleanup() {
  rm -f "$LOCK_FILE"
  for f in "${TEMP_FILES[@]}"; do
    rm -rf "$f" 2>/dev/null || true
  done
}
trap cleanup EXIT

# --- Lock file: prevent concurrent resurrection ---
acquire_lock() {
  if [ -f "$LOCK_FILE" ]; then
    local existing_pid
    existing_pid=$(cat "$LOCK_FILE" 2>/dev/null || echo "")
    if [ -n "$existing_pid" ] && kill -0 "$existing_pid" 2>/dev/null; then
      echo "Resurrection already running (PID $existing_pid), exiting"
      # Exit without triggering cleanup trap (don't remove their lock)
      trap - EXIT
      exit 0
    fi
    # Stale lock — take over
    echo "Removing stale lock (PID $existing_pid)"
  fi
  mkdir -p "$(dirname "$LOCK_FILE")"
  echo $$ > "$LOCK_FILE"
}

# --- Gateway detection (single source of truth, matches watchdog patterns) ---
is_gateway_running() {
  if pgrep -f "openclaw-gateway" > /dev/null 2>&1; then
    return 0
  fi
  if pgrep -f "openclaw.*gateway" > /dev/null 2>&1; then
    return 0
  fi
  return 1
}

# Parse args
FROM_CID=""
PREFERRED_GATEWAY=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --from-cid) FROM_CID="$2"; shift 2 ;;
    --content-dir) CONTENT_DIR="$2"; shift 2 ;;
    --agent-name) AGENT_NAME="$2"; shift 2 ;;
    --gateway) PREFERRED_GATEWAY="$2"; shift 2 ;;
    --key-file) KEY_FILE="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# Validate CID format if provided (alphanumeric, starts with Qm or bafy)
if [ -n "$FROM_CID" ]; then
  if ! echo "$FROM_CID" | grep -qE '^(Qm[a-zA-Z0-9]{44}|bafy[a-zA-Z0-9]{55,})$'; then
    echo "ERROR: Invalid CID format: $FROM_CID"
    echo "CIDs should start with 'Qm' (CIDv0) or 'bafy' (CIDv1)"
    exit 1
  fi
fi

# Validate --key-file if provided
if [ -n "$KEY_FILE" ] && [ ! -f "$KEY_FILE" ]; then
  echo "ERROR: Key file not found: $KEY_FILE"
  exit 1
fi

# ============================================================
# Identity pre-flight — validate before operating
# ============================================================
validate_identity() {
  if [ ! -f "$IDENTITY_PATH" ]; then
    echo "FATAL: Invalid AMCP identity — run amcp identity create or amcp identity validate for details"
    exit 1
  fi
  if ! "$AMCP_CLI" identity validate --identity "$IDENTITY_PATH" 2>/dev/null; then
    echo "FATAL: Invalid AMCP identity — run amcp identity create or amcp identity validate for details"
    exit 1
  fi
}

validate_identity

# Warn if secrets found in identity.json (they belong in config.json)
warn_identity_secrets() {
  python3 -c "
import json, os, sys
p = os.path.expanduser('$IDENTITY_PATH')
if not os.path.exists(p): sys.exit(0)
d = json.load(open(p))
bad = [k for k in d if k in ('pinata_jwt','pinata_api_key','solvr_api_key','api_key','apiKey','jwt','token','secret','password','mnemonic','email','notifyTarget')]
if bad:
    print(f'WARNING: Secrets found in identity.json: {\", \".join(bad)}', file=sys.stderr)
    print('  Migrate with: proactive-amcp config set <key> <value>', file=sys.stderr)
" 2>&1 || true
}
warn_identity_secrets

# Generate open problem summary for agent context (post-resurrection)
surface_open_problems() {
  # Check config toggle (default: true)
  local enabled
  enabled=$(python3 -c "
import json, os
p = os.path.expanduser('$HOME/.amcp/config.json')
if os.path.isfile(p):
    d = json.load(open(p))
    print(d.get('learning',{}).get('resurrection',{}).get('surfaceProblems', True))
else:
    print(True)
" 2>/dev/null || echo 'True')

  if [ "$enabled" = "False" ] || [ "$enabled" = "false" ]; then
    log "Problem surfacing disabled (config: learning.resurrection.surfaceProblems=false)"
    return 0
  fi

  local summary_file="$HOME/.amcp/open-problems-summary.md"
  if [ -x "$SCRIPT_DIR/diagnose.sh" ]; then
    log "Generating open problem summary..."
    "$SCRIPT_DIR/diagnose.sh" summary --output "$summary_file" 2>&1 | tee -a "$RECOVERY_LOG" || true
    if [ -f "$summary_file" ] && [ -s "$summary_file" ]; then
      log "Open problems written to $summary_file"
    fi
  fi
}

# Acquire lock before doing anything
acquire_lock

mkdir -p "$(dirname "$RECOVERY_LOG")"

log() {
  echo "[$(date -Iseconds)] $1" | tee -a "$RECOVERY_LOG"
}

# Send email summary on resurrection completion
send_resurrection_email() {
  local status="$1"  # "success" or "failed"
  local method="$2"  # recovery method used
  local downtime="$3"  # seconds
  local log_file="$4"  # path to recovery log

  local subject="Agent Resurrection: $AGENT_NAME - ${status^^}"
  local body="
=== Agent Resurrection Report ===

Agent: $AGENT_NAME
Status: ${status^^}
Recovery Method: $method
Downtime: ${downtime}s
Timestamp: $(date -Iseconds)

=== Recovery Log ===
$(tail -50 "$log_file" 2>/dev/null || echo "Log not available")
"

  [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "$body" --email "$subject"
}

# --- Solvr integration (sourced from solvr-integration.sh) ---
# Provides: solvr_search_problem, try_solvr_solutions, solvr_create_problem,
#           solvr_start_approach, solvr_update_approach, solvr_post_failed_approach
# shellcheck source=solvr-integration.sh
source "$SCRIPT_DIR/solvr-integration.sh"

# ============================================================
# Attempt tracking — record what was tried for notifications
# ============================================================
ATTEMPTS_FILE=$(mktemp)
TEMP_FILES+=("$ATTEMPTS_FILE")

record_attempt() {
  local method="$1"
  local result="$2"
  local detail="${3:-}"
  echo "{\"method\":\"$method\",\"result\":\"$result\",\"detail\":\"$detail\",\"timestamp\":\"$(date -Iseconds)\"}" >> "$ATTEMPTS_FILE"
}

# Trigger smart checkpoint after successful recovery (capture fresh state)
post_recovery_checkpoint() {
  local checkpoint_script="$SCRIPT_DIR/checkpoint.sh"
  if [ -x "$checkpoint_script" ]; then
    log "Creating post-recovery checkpoint..."
    "$checkpoint_script" --trigger recovery --quiet 2>/dev/null || true
  fi
}

# Write last-recovery.json with attempts_summary
write_recovery_json() {
  local method="$1"
  local downtime="$2"
  local cid="${3:-}"

  AMCP_RECOVERY_FILE="$HOME/.amcp/last-recovery.json" \
  AMCP_ATTEMPTS_FILE="$ATTEMPTS_FILE" \
  AMCP_METHOD="$method" \
  AMCP_DOWNTIME="$downtime" \
  AMCP_CID="$cid" \
  AMCP_LOG="$RECOVERY_LOG" \
  python3 << 'PYEOF'
import json, os
from datetime import datetime

recovery_file = os.environ["AMCP_RECOVERY_FILE"]
attempts_file = os.environ["AMCP_ATTEMPTS_FILE"]
method = os.environ["AMCP_METHOD"]
downtime = int(os.environ["AMCP_DOWNTIME"])
cid = os.environ.get("AMCP_CID", "")
log_path = os.environ.get("AMCP_LOG", "")

attempts = []
try:
    with open(attempts_file) as f:
        for line in f:
            line = line.strip()
            if line:
                attempts.append(json.loads(line))
except (FileNotFoundError, json.JSONDecodeError):
    pass

recovery = {
    "method": method,
    "downtime": downtime,
    "timestamp": datetime.now().isoformat(),
    "attempts_summary": attempts
}
if cid:
    recovery["cid"] = cid
if log_path:
    recovery["log"] = log_path

with open(recovery_file, "w") as f:
    json.dump(recovery, f, indent=2)
PYEOF
}

# Format notification with attempt context: ISSUE → TRIED → RESULT
format_recovery_notification() {
  local icon="$1"
  local status="$2"
  local method="$3"
  local downtime="$4"

  AMCP_ICON="$icon" \
  AMCP_STATUS="$status" \
  AMCP_AGENT="$AGENT_NAME" \
  AMCP_METHOD="$method" \
  AMCP_DOWNTIME="$downtime" \
  AMCP_ATTEMPTS_FILE="$ATTEMPTS_FILE" \
  python3 << 'PYEOF'
import json, os

icon = os.environ["AMCP_ICON"]
status = os.environ["AMCP_STATUS"]
agent = os.environ["AMCP_AGENT"]
method = os.environ["AMCP_METHOD"]
downtime = os.environ["AMCP_DOWNTIME"]
attempts_file = os.environ["AMCP_ATTEMPTS_FILE"]

lines = [f"{icon} [{agent}] {status}"]
lines.append(f"METHOD: {method}")
lines.append(f"DOWNTIME: {downtime}s")

attempts = []
try:
    with open(attempts_file) as f:
        for line in f:
            line = line.strip()
            if line:
                attempts.append(json.loads(line))
except (FileNotFoundError, json.JSONDecodeError):
    pass

if attempts:
    lines.append("ATTEMPTS:")
    for a in attempts:
        aicon = "\u2705" if a["result"] == "succeeded" else "\u274c"
        lines.append(f"  {aicon} {a['method']}: {a.get('detail', '')}")

print("\n".join(lines))
PYEOF
}

# Fetch checkpoint from IPFS gateways (tries multiple in priority order)
fetch_from_gateways() {
  local cid="$1"
  local output="$2"

  # Gateway URLs in priority order: Solvr > Pinata > IPFS.io > Cloudflare
  local -a gateways=(
    "solvr|https://ipfs.solvr.dev/ipfs/$cid"
    "pinata|https://gateway.pinata.cloud/ipfs/$cid"
    "ipfs.io|https://ipfs.io/ipfs/$cid"
    "cloudflare|https://cloudflare-ipfs.com/ipfs/$cid"
  )

  # If --gateway flag specified, try that one first
  if [ -n "$PREFERRED_GATEWAY" ]; then
    local preferred_url=""
    for gw in "${gateways[@]}"; do
      local name="${gw%%|*}"
      local url="${gw#*|}"
      if [ "$name" = "$PREFERRED_GATEWAY" ]; then
        preferred_url="$url"
        break
      fi
    done
    if [ -n "$preferred_url" ]; then
      log "Trying preferred gateway: $PREFERRED_GATEWAY"
      if curl -sf --max-time 120 "$preferred_url" -o "$output" 2>/dev/null && [ -s "$output" ]; then
        log "Checkpoint retrieved from $PREFERRED_GATEWAY gateway"
        return 0
      fi
      log "Preferred gateway $PREFERRED_GATEWAY failed, trying others..."
    fi
  fi

  # Try each gateway in order
  for gw in "${gateways[@]}"; do
    local name="${gw%%|*}"
    local url="${gw#*|}"

    # Skip preferred if already tried
    if [ "$name" = "$PREFERRED_GATEWAY" ]; then
      continue
    fi

    log "Trying gateway: $name"
    if curl -sf --max-time 120 "$url" -o "$output" 2>/dev/null && [ -s "$output" ]; then
      log "Checkpoint retrieved from $name gateway"
      return 0
    fi
    log "Gateway $name failed"
  done

  return 1
}

# Recovery attempts
try_restart_gateway() {
  log "Attempting: restart gateway"

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

  return 1
}

try_fix_config() {
  # Gate: if gateway came up from a previous tier, skip
  if is_gateway_running; then
    log "Gateway already running, skipping config fix"
    return 0
  fi

  log "Attempting: fix config via config.sh fix (3-tier)"

  # Delegate to standalone config fix script (Tier A: backup, Tier B: doctor, Tier C: minimal)
  if [ -x "$SCRIPT_DIR/config.sh" ]; then
    if "$SCRIPT_DIR/config.sh" fix 2>&1 | tee -a "$RECOVERY_LOG"; then
      log "Config fix succeeded"
      return 0
    fi
    log "Standalone config fix exhausted all tiers"
  else
    log "config.sh not found, falling back to inline backup restore"
    # Inline fallback: simple backup restore (in case config.sh fix missing)
    local backup_dir="$HOME/.amcp/config-backups"
    if [ -d "$backup_dir" ]; then
      local latest_backup
      latest_backup=$(ls -1t "$backup_dir"/openclaw-*.json 2>/dev/null | head -1)
      if [ -n "$latest_backup" ] && [ -f "$latest_backup" ]; then
        log "Found backup: $latest_backup"
        if jq . "$latest_backup" > /dev/null 2>&1; then
          cp "$HOME/.openclaw/openclaw.json" "$HOME/.openclaw/openclaw.json.pre-recovery" 2>/dev/null || true
          cp "$latest_backup" "$HOME/.openclaw/openclaw.json"
          log "Restored openclaw.json from backup"
          if try_restart_gateway; then
            return 0
          fi
        else
          log "Backup JSON invalid, skipping"
        fi
      fi
    fi
  fi

  return 1
}

# Source checkpoint decryption helpers
# shellcheck source=checkpoint-decrypt.sh
source "$SCRIPT_DIR/checkpoint-decrypt.sh"

try_rehydrate() {
  local cid="$1"

  # Gate: if gateway came up from a previous tier, skip
  if is_gateway_running; then
    log "Gateway already running, skipping rehydrate"
    return 0
  fi

  log "Attempting: rehydrate from checkpoint ${cid:-local}"

  # Fetch from IPFS if CID provided
  local checkpoint_path=""
  if [ -n "$cid" ]; then
    checkpoint_path="/tmp/checkpoint-$cid.amcp"
    TEMP_FILES+=("$checkpoint_path")
    log "Fetching from IPFS: $cid"
    if ! fetch_from_gateways "$cid" "$checkpoint_path"; then
      log "Failed to fetch from all IPFS gateways"
      return 1
    fi
  else
    # Use local checkpoint
    if [ -f "$LAST_CHECKPOINT_FILE" ]; then
      checkpoint_path=$(jq -r '.localPath // empty' "$LAST_CHECKPOINT_FILE" 2>/dev/null)
    fi

    # Fallback: find latest local checkpoint
    if [ -z "$checkpoint_path" ] || [ ! -f "$checkpoint_path" ]; then
      checkpoint_path=$(ls -1t "$HOME/.amcp/checkpoints"/*.amcp 2>/dev/null | head -1)
    fi
  fi

  if [ -z "$checkpoint_path" ] || [ ! -f "$checkpoint_path" ]; then
    log "No checkpoint found"
    return 1
  fi

  log "Using checkpoint: $checkpoint_path"

  # Detect and handle encrypted checkpoints
  if is_checkpoint_encrypted "$checkpoint_path"; then
    log "Checkpoint is encrypted — resolving decryption key..."
    local decrypt_key
    decrypt_key=$(resolve_decrypt_key "$cid" "$checkpoint_path") || decrypt_key=""
    if [ -z "$decrypt_key" ]; then
      log "ERROR: Checkpoint is encrypted. Provide --key-file or ensure key exists in $CHECKPOINT_KEYS_FILE"
      return 1
    fi
    log "Decrypting checkpoint..."
    if ! decrypt_checkpoint "$checkpoint_path" "$decrypt_key"; then
      return 1
    fi
    log "Checkpoint decrypted successfully"
  fi

  # Verify AMCP CLI exists
  if [ ! -x "$AMCP_CLI" ]; then
    log "AMCP CLI not found at $AMCP_CLI"
    return 1
  fi

  # Resuscitate (verify + decrypt)
  local secrets_file="/tmp/secrets-$$.json"
  local content_dir="/tmp/restored-$$"
  TEMP_FILES+=("$secrets_file" "$content_dir")

  if ! $AMCP_CLI resuscitate \
       --checkpoint "$checkpoint_path" \
       --identity "$IDENTITY_PATH" \
       --out-content "$content_dir" \
       --out-secrets "$secrets_file" 2>&1 | tee -a "$RECOVERY_LOG"; then
    log "Resuscitate command failed"
    return 1
  fi

  log "Checkpoint verified and decrypted"

  # Restore content to workspace
  if [ -d "$content_dir" ]; then
    log "Restoring content to $CONTENT_DIR..."
    mkdir -p "$CONTENT_DIR"

    # Restore workspace files (memory/, AGENTS.md, etc.)
    # Be careful not to overwrite code repos
    for item in "$content_dir"/*; do
      if [ -e "$item" ]; then
        local basename=$(basename "$item")
        # Skip directories that look like code repos
        if [[ "$basename" =~ ^(solvr|amcp-protocol|openclaw-|proactive-)$ ]]; then
          log "Skipping code repo: $basename"
          continue
        fi
        cp -r "$item" "$CONTENT_DIR/" 2>/dev/null || true
        log "Restored: $basename"
      fi
    done
  fi

  # Inject secrets
  if [ -f "$secrets_file" ] && [ -s "$secrets_file" ]; then
    log "Injecting secrets..."
    if [ -x "$SCRIPT_DIR/load-credentials.sh" ]; then
      "$SCRIPT_DIR/load-credentials.sh" "$secrets_file" 2>&1 | tee -a "$RECOVERY_LOG" || true
    else
      log "load-credentials.sh not found, skipping"
    fi
  fi

  # Validate learning storage JSONL format (if present)
  local learning_dir="$CONTENT_DIR/memory/learning"
  if [ -d "$learning_dir" ]; then
    log "Validating learning storage..."
    python3 -c "
import json, os, sys
learning_dir = '$learning_dir'
for fname in ('problems.jsonl', 'learnings.jsonl'):
    fpath = os.path.join(learning_dir, fname)
    if not os.path.isfile(fpath):
        continue
    errors = 0
    with open(fpath) as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError:
                errors += 1
                if errors <= 3:
                    print(f'WARN: {fname} line {i}: invalid JSON', file=sys.stderr)
    if errors:
        print(f'WARN: {fname} has {errors} invalid line(s)', file=sys.stderr)
    else:
        print(f'  {fname}: OK')
# Validate stats.json
stats_path = os.path.join(learning_dir, 'stats.json')
if os.path.isfile(stats_path):
    try:
        json.load(open(stats_path))
        print('  stats.json: OK')
    except json.JSONDecodeError:
        print('WARN: stats.json: invalid JSON', file=sys.stderr)
" 2>&1 | tee -a "$RECOVERY_LOG" || echo "WARN: learning validation failed" | tee -a "$RECOVERY_LOG"
  fi

  # Validate ontology graph (if present)
  local ontology_graph="$CONTENT_DIR/memory/ontology/graph.jsonl"
  if [ -f "$ontology_graph" ] && [ -f "$SCRIPT_DIR/validate-ontology.py" ]; then
    log "Validating ontology graph..."
    python3 "$SCRIPT_DIR/validate-ontology.py" "$ontology_graph" 2>&1 | tee -a "$RECOVERY_LOG" || echo "WARN: ontology validation failed" | tee -a "$RECOVERY_LOG"
  fi

  # Recreate virtual environments from manifest (if present)
  local venvs_manifest="$CONTENT_DIR/memory/venvs-manifest.json"
  if [ -x "$SCRIPT_DIR/recreate-venvs.sh" ]; then
    log "Checking for venv manifest..."
    "$SCRIPT_DIR/recreate-venvs.sh" "$venvs_manifest" 2>&1 | tee -a "$RECOVERY_LOG" || echo "WARN: venv recreation failed" | tee -a "$RECOVERY_LOG"
  fi

  # Cleanup temp files
  rm -rf "$content_dir" "$secrets_file"
  [ -n "$cid" ] && rm -f "$checkpoint_path"

  # Restart gateway with restored config
  if try_restart_gateway; then
    return 0
  fi

  log "Gateway failed to start after rehydration"
  return 1
}

# Main resurrection flow
main() {
  local start_time=$(date +%s)

  log "========================================="
  log "=== AMCP Resurrection Started ==="
  log "========================================="
  log "Agent: $AGENT_NAME"
  log "Identity: $IDENTITY_PATH"
  log "Content dir: $CONTENT_DIR"
  log "Recovery log: $RECOVERY_LOG"

  # Notify start
  if [ -x "$SCRIPT_DIR/notify.sh" ]; then
    "$SCRIPT_DIR/notify.sh" "🔄 [$AGENT_NAME] Starting resurrection..."
  fi

  # Step 1: Search Solvr for similar problems
  log ""
  log "=== Step 1: Search Solvr for solutions ==="
  local solvr_result
  solvr_result=$(solvr_search_problem)

  # Step 1b: Try Solvr solutions before generic recovery
  log ""
  log "=== Step 1b: Try Solvr-suggested solutions ==="
  if try_solvr_solutions "$solvr_result"; then
    record_attempt "solvr_solution" "succeeded" "Matched Solvr solution"
    local end_time=$(date +%s)
    local downtime=$((end_time - start_time))
    log "✅ Recovery succeeded via Solvr solution (${downtime}s)"
    local report
    report=$(format_recovery_notification "✅" "Alive!" "solvr_solution" "$downtime")
    [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "$report"
    write_recovery_json "solvr_solution" "$downtime"
    surface_open_problems
    send_resurrection_email "success" "solvr_solution" "$downtime" "$RECOVERY_LOG"
    post_recovery_checkpoint
    return 0
  fi
  record_attempt "solvr_solution" "failed" "No matching solutions or unavailable"
  log "Solvr solutions exhausted or unavailable"

  # Step 1c: Create Solvr problem if no match found (for tracking approaches)
  local solvr_count
  solvr_count=$(echo "$solvr_result" | jq '.data | length' 2>/dev/null || echo "0")
  if [ "$solvr_count" = "0" ] || [ "$solvr_count" = "null" ]; then
    solvr_create_problem
  fi

  # Step 2: Try recovery hierarchy (lightweight first)
  log ""
  log "=== Step 2: Recovery attempts ==="

  # 2a: Restart gateway
  log ""
  log "--- Attempt 1: Restart gateway ---"
  [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "🔄 [$AGENT_NAME] Trying: restart gateway"
  solvr_start_approach "restart" "Restart gateway via systemctl or direct"

  if try_restart_gateway; then
    record_attempt "restart" "succeeded" "Gateway restarted"
    solvr_update_approach "succeeded"
    local end_time=$(date +%s)
    local downtime=$((end_time - start_time))
    log "✅ Recovery succeeded: restart gateway (${downtime}s)"
    local report
    report=$(format_recovery_notification "✅" "Alive!" "restart" "$downtime")
    [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "$report"
    write_recovery_json "restart" "$downtime"
    surface_open_problems
    send_resurrection_email "success" "restart" "$downtime" "$RECOVERY_LOG"
    post_recovery_checkpoint
    return 0
  fi
  record_attempt "restart" "failed" "systemctl and direct restart both failed"
  solvr_update_approach "failed"
  log "❌ Restart gateway failed"

  # 2b: Fix config
  log ""
  log "--- Attempt 2: Fix config ---"
  [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "🔄 [$AGENT_NAME] Trying: fix config"
  solvr_start_approach "config_fix" "Restore openclaw.json from config backup"

  if try_fix_config; then
    record_attempt "config_fix" "succeeded" "Config restored"
    solvr_update_approach "succeeded"
    local end_time=$(date +%s)
    local downtime=$((end_time - start_time))
    log "✅ Recovery succeeded: fix config (${downtime}s)"
    local report
    report=$(format_recovery_notification "✅" "Alive!" "config_fix" "$downtime")
    [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "$report"
    write_recovery_json "config_fix" "$downtime"
    surface_open_problems
    send_resurrection_email "success" "config_fix" "$downtime" "$RECOVERY_LOG"
    post_recovery_checkpoint
    return 0
  fi
  record_attempt "config_fix" "failed" "Config fix exhausted all tiers"
  solvr_update_approach "failed"
  log "❌ Fix config failed"

  # 2c: Rehydrate from checkpoint
  local cid="$FROM_CID"
  if [ -z "$cid" ] && [ -f "$LAST_CHECKPOINT_FILE" ]; then
    cid=$(jq -r '.cid // empty' "$LAST_CHECKPOINT_FILE" 2>/dev/null)
  fi

  log ""
  log "--- Attempt 3: Rehydrate from checkpoint ---"
  [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "🔄 [$AGENT_NAME] Trying: rehydrate from checkpoint ${cid:-local}"
  solvr_start_approach "rehydrate" "Full rehydrate from IPFS checkpoint ${cid:-local}"

  if try_rehydrate "$cid"; then
    record_attempt "rehydrate" "succeeded" "Restored from checkpoint ${cid:-local}"
    solvr_update_approach "succeeded"
    local end_time=$(date +%s)
    local downtime=$((end_time - start_time))
    log "✅ Recovery succeeded: rehydrate (${downtime}s)"
    local report
    report=$(format_recovery_notification "✅" "Alive!" "rehydrate" "$downtime")
    [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "$report"
    write_recovery_json "rehydrate" "$downtime" "$cid"
    surface_open_problems
    send_resurrection_email "success" "rehydrate" "$downtime" "$RECOVERY_LOG"
    post_recovery_checkpoint
    return 0
  fi
  record_attempt "rehydrate" "failed" "Rehydration failed"
  solvr_update_approach "failed"
  log "❌ Rehydrate failed"

  # All recovery methods failed
  local end_time=$(date +%s)
  local downtime=$((end_time - start_time))

  log ""
  log "========================================="
  log "❌ ALL RECOVERY METHODS FAILED"
  log "Elapsed: ${downtime}s"
  log "Human intervention required"
  log "========================================="

  local report
  report=$(format_recovery_notification "❌" "Resurrection FAILED" "all_methods_exhausted" "$downtime")
  report+=$'\n'"LOG: $RECOVERY_LOG"
  report+=$'\n'"NEXT: Manual intervention required. Review: tail -50 $RECOVERY_LOG"
  [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "$report"
  write_recovery_json "failed" "$downtime"

  # Send email summary (critical - always send on failure)
  send_resurrection_email "failed" "all_methods_exhausted" "$downtime" "$RECOVERY_LOG"
  return 1
}

main "$@"
