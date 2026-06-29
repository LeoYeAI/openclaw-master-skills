#!/bin/bash
# status.sh — AMCP system status
#
# Usage:
#   status.sh              Basic readiness check (READY/NO_IDENTITY/NO_PINNING/INVALID_IDENTITY)
#   status.sh --full       Comprehensive status of all subsystems
#   status.sh --json       Machine-readable JSON output (implies --full)
#
# Subsystems reported in --full mode:
#   identity    — AMCP keypair validity and AID
#   solvr       — Solvr registration and key presence
#   ipfs        — Pinning provider and last checkpoint CID
#   watchdog    — Health state, consecutive failures, last check time
#   checkpoints — Local checkpoint count, last CID and timestamp
#   auth        — OAuth/auth profile presence
#   learning    — Problem and learning entity counts

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0" 2>/dev/null || realpath "$0" 2>/dev/null || echo "$0")")" && pwd)"
IDENTITY_PATH="${IDENTITY_PATH:-$HOME/.amcp/identity.json}"
CONFIG_FILE="${CONFIG_FILE:-$HOME/.amcp/config.json}"
AMCP_CLI="${AMCP_CLI:-$(command -v amcp 2>/dev/null || echo "$HOME/bin/amcp")}"
STATE_FILE="${STATE_FILE:-$HOME/.amcp/watchdog-state.json}"
LAST_CHECKPOINT_FILE="${LAST_CHECKPOINT_FILE:-$HOME/.amcp/last-checkpoint.json}"
CHECKPOINT_DIR="${CHECKPOINT_DIR:-$HOME/.amcp/checkpoints}"
SESSION_DIR="${SESSION_DIR:-$HOME/.openclaw/agents/main/sessions}"

# ============================================================
# Parse args
# ============================================================
MODE="basic"       # basic | full
OUTPUT="human"     # human | json

while [[ $# -gt 0 ]]; do
  case "$1" in
    --full)  MODE="full"; shift ;;
    --json)  MODE="full"; OUTPUT="json"; shift ;;
    -h|--help)
      cat <<EOF
proactive-amcp status — Check AMCP system health

Usage:
  status              Basic readiness check
  status --full       Comprehensive subsystem status
  status --json       Machine-readable JSON (implies --full)

Exit codes:
  0 = READY (all core subsystems healthy)
  1 = one or more issues detected
EOF
      exit 0
      ;;
    *) shift ;;
  esac
done

# ============================================================
# Helper: read config value via python3
# ============================================================
config_get() {
  local key="$1"
  python3 -c "
import json, functools, sys
try:
    with open('$CONFIG_FILE') as f:
        d = json.load(f)
    val = functools.reduce(lambda o, k: o.get(k, {}), '$key'.split('.'), d)
    if isinstance(val, dict) and not val:
        print('')
    else:
        print(val)
except Exception:
    print('')
" 2>/dev/null || echo ""
}

# ============================================================
# Subsystem checks (each sets variables for later output)
# ============================================================

# --- Identity ---
check_identity() {
  IDENTITY_STATUS="unknown"
  IDENTITY_AID=""
  IDENTITY_PATH_DISPLAY="$IDENTITY_PATH"

  if [ ! -f "$IDENTITY_PATH" ]; then
    IDENTITY_STATUS="missing"
    return
  fi

  if "$AMCP_CLI" identity validate --identity "$IDENTITY_PATH" 2>/dev/null; then
    IDENTITY_STATUS="valid"
    # Extract AID
    IDENTITY_AID=$(python3 -c "
import json
with open('$IDENTITY_PATH') as f:
    d = json.load(f)
print(d.get('aid', d.get('id', '')))
" 2>/dev/null || echo "")
  else
    IDENTITY_STATUS="invalid"
  fi
}

# --- Solvr ---
check_solvr() {
  SOLVR_REGISTERED="false"
  SOLVR_KEY_PRESENT="false"
  SOLVR_DISPLAY_NAME=""
  SOLVR_AGENT_ID=""
  SOLVR_CLAIM_URL=""

  if [ ! -f "$CONFIG_FILE" ]; then
    return
  fi

  local solvr_key
  solvr_key=$(config_get "solvr.apiKey")
  if [ -n "$solvr_key" ]; then
    SOLVR_KEY_PRESENT="true"
    SOLVR_REGISTERED="true"
  fi

  SOLVR_DISPLAY_NAME=$(config_get "solvr.displayName")
  [ -z "$SOLVR_DISPLAY_NAME" ] && SOLVR_DISPLAY_NAME=$(config_get "solvr.name")
  SOLVR_AGENT_ID=$(config_get "solvr.agentId")
  SOLVR_CLAIM_URL=$(config_get "solvr.claimUrl")
}

# --- IPFS / Pinning ---
check_ipfs() {
  IPFS_PROVIDER="pinata"
  IPFS_LAST_CID=""
  IPFS_LAST_TIMESTAMP=""
  IPFS_PINATA_CONFIGURED="false"
  IPFS_SOLVR_CONFIGURED="false"

  if [ ! -f "$CONFIG_FILE" ]; then
    return
  fi

  IPFS_PROVIDER=$(config_get "pinning.provider")
  [ -z "$IPFS_PROVIDER" ] && IPFS_PROVIDER="pinata"

  local pinata_jwt solvr_pin_key
  pinata_jwt=$(config_get "pinata.jwt")
  [ -n "$pinata_jwt" ] && IPFS_PINATA_CONFIGURED="true"

  solvr_pin_key=$(config_get "pinning.solvr.apiKey")
  [ -z "$solvr_pin_key" ] && solvr_pin_key=$(config_get "solvr.apiKey")
  [ -n "$solvr_pin_key" ] && IPFS_SOLVR_CONFIGURED="true"

  # Last checkpoint info
  if [ -f "$LAST_CHECKPOINT_FILE" ]; then
    IPFS_LAST_CID=$(python3 -c "
import json
with open('$LAST_CHECKPOINT_FILE') as f:
    d = json.load(f)
print(d.get('cid', d.get('pinataCid', d.get('solvrCid', ''))))
" 2>/dev/null || echo "")
    IPFS_LAST_TIMESTAMP=$(python3 -c "
import json
with open('$LAST_CHECKPOINT_FILE') as f:
    d = json.load(f)
print(d.get('timestamp', d.get('created', '')))
" 2>/dev/null || echo "")
  fi
}

# --- Watchdog ---
check_watchdog() {
  WATCHDOG_RUNNING="false"
  WATCHDOG_STATE="unknown"
  WATCHDOG_FAILURES=0
  WATCHDOG_LAST_CHECK=""
  WATCHDOG_LAST_HEALTHY=""
  WATCHDOG_RETRY_DELAY=0

  # Check if watchdog process is running (systemd or direct)
  if systemctl --user is-active amcp-watchdog.service &>/dev/null 2>&1; then
    WATCHDOG_RUNNING="true"
  elif pgrep -f "watchdog.sh" &>/dev/null 2>&1; then
    WATCHDOG_RUNNING="true"
  fi

  # Read state file
  if [ -f "$STATE_FILE" ]; then
    python3 -c "
import json
with open('$STATE_FILE') as f:
    d = json.load(f)
print(d.get('state', 'unknown'))
print(d.get('consecutiveFailures', 0))
print(d.get('lastCheck', ''))
print(d.get('lastHealthy', ''))
print(d.get('retryDelay', 0))
" 2>/dev/null | {
      read -r WATCHDOG_STATE
      read -r WATCHDOG_FAILURES
      read -r WATCHDOG_LAST_CHECK
      read -r WATCHDOG_LAST_HEALTHY
      read -r WATCHDOG_RETRY_DELAY
      # Export to parent scope via temp file
      cat > /tmp/.amcp-watchdog-status.$$ <<EOTMP
$WATCHDOG_STATE
$WATCHDOG_FAILURES
$WATCHDOG_LAST_CHECK
$WATCHDOG_LAST_HEALTHY
$WATCHDOG_RETRY_DELAY
EOTMP
    }
    if [ -f "/tmp/.amcp-watchdog-status.$$" ]; then
      {
        read -r WATCHDOG_STATE
        read -r WATCHDOG_FAILURES
        read -r WATCHDOG_LAST_CHECK
        read -r WATCHDOG_LAST_HEALTHY
        read -r WATCHDOG_RETRY_DELAY
      } < "/tmp/.amcp-watchdog-status.$$"
      rm -f "/tmp/.amcp-watchdog-status.$$"
    fi
  fi
}

# --- Checkpoints ---
check_checkpoints() {
  CHECKPOINT_COUNT=0
  CHECKPOINT_LAST_CID=""
  CHECKPOINT_LAST_TIMESTAMP=""
  CHECKPOINT_LAST_LOCAL=""

  # Count local checkpoint files
  if [ -d "$CHECKPOINT_DIR" ]; then
    CHECKPOINT_COUNT=$(find "$CHECKPOINT_DIR" -maxdepth 1 -name "*.json" -type f 2>/dev/null | wc -l)
  fi

  # Last checkpoint metadata
  if [ -f "$LAST_CHECKPOINT_FILE" ]; then
    python3 -c "
import json
with open('$LAST_CHECKPOINT_FILE') as f:
    d = json.load(f)
print(d.get('cid', ''))
print(d.get('timestamp', d.get('created', '')))
print(d.get('localPath', ''))
" 2>/dev/null | {
      read -r CHECKPOINT_LAST_CID
      read -r CHECKPOINT_LAST_TIMESTAMP
      read -r CHECKPOINT_LAST_LOCAL
      cat > /tmp/.amcp-checkpoint-status.$$ <<EOTMP
$CHECKPOINT_LAST_CID
$CHECKPOINT_LAST_TIMESTAMP
$CHECKPOINT_LAST_LOCAL
EOTMP
    }
    if [ -f "/tmp/.amcp-checkpoint-status.$$" ]; then
      {
        read -r CHECKPOINT_LAST_CID
        read -r CHECKPOINT_LAST_TIMESTAMP
        read -r CHECKPOINT_LAST_LOCAL
      } < "/tmp/.amcp-checkpoint-status.$$"
      rm -f "/tmp/.amcp-checkpoint-status.$$"
    fi
  fi
}

# --- Auth ---
check_auth() {
  AUTH_STATUS="unknown"
  AUTH_PROFILES_PRESENT="false"

  local auth_file="$HOME/.openclaw/agents/main/agent/auth-profiles.json"
  if [ -f "$auth_file" ]; then
    AUTH_PROFILES_PRESENT="true"
    AUTH_STATUS="ok"
  else
    AUTH_STATUS="no_profiles"
  fi
}

# --- Learning ---
check_learning() {
  LEARNING_PROBLEMS_TOTAL=0
  LEARNING_PROBLEMS_OPEN=0
  LEARNING_LEARNINGS_TOTAL=0

  # Determine learning dir
  local learning_dir
  learning_dir="${LEARNING_DIR:-}"
  if [ -z "$learning_dir" ]; then
    local content_dir
    content_dir=$(python3 -c "
import json, os
oc = os.path.expanduser('~/.openclaw/openclaw.json')
try:
    with open(oc) as f:
        d = json.load(f)
    ws = d.get('agents',{}).get('defaults',{}).get('workspace','~/.openclaw/workspace')
    print(os.path.expanduser(ws))
except Exception:
    print(os.path.expanduser('~/.openclaw/workspace'))
" 2>/dev/null || echo "$HOME/.openclaw/workspace")
    learning_dir="$content_dir/memory/learning"
  fi

  local problems_file="$learning_dir/problems.jsonl"
  local learnings_file="$learning_dir/learnings.jsonl"

  if [ -f "$problems_file" ]; then
    python3 -c "
import json
total = 0
open_count = 0
seen = {}
with open('$problems_file') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
            pid = r.get('id', '')
            if pid:
                seen[pid] = r
        except json.JSONDecodeError:
            pass
total = len(seen)
open_count = sum(1 for p in seen.values() if p.get('status', 'open') == 'open')
print(total)
print(open_count)
" 2>/dev/null | {
      read -r LEARNING_PROBLEMS_TOTAL
      read -r LEARNING_PROBLEMS_OPEN
      cat > /tmp/.amcp-learning-status.$$ <<EOTMP
$LEARNING_PROBLEMS_TOTAL
$LEARNING_PROBLEMS_OPEN
EOTMP
    }
    if [ -f "/tmp/.amcp-learning-status.$$" ]; then
      {
        read -r LEARNING_PROBLEMS_TOTAL
        read -r LEARNING_PROBLEMS_OPEN
      } < "/tmp/.amcp-learning-status.$$"
      rm -f "/tmp/.amcp-learning-status.$$"
    fi
  fi

  if [ -f "$learnings_file" ]; then
    python3 -c "
import json
seen = {}
with open('$learnings_file') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
            lid = r.get('id', '')
            if lid:
                seen[lid] = r
        except json.JSONDecodeError:
            pass
print(len(seen))
" 2>/dev/null | {
      read -r LEARNING_LEARNINGS_TOTAL
      cat > /tmp/.amcp-learnings-count.$$ <<EOTMP
$LEARNING_LEARNINGS_TOTAL
EOTMP
    }
    if [ -f "/tmp/.amcp-learnings-count.$$" ]; then
      read -r LEARNING_LEARNINGS_TOTAL < "/tmp/.amcp-learnings-count.$$"
      rm -f "/tmp/.amcp-learnings-count.$$"
    fi
  fi
}

# ============================================================
# Basic status (same as original do_status)
# ============================================================
do_basic_status() {
  local status="READY"
  local messages=()

  # Check identity
  if [ ! -f "$IDENTITY_PATH" ]; then
    status="NO_IDENTITY"
    messages+=("Identity not found at $IDENTITY_PATH")
  elif ! "$AMCP_CLI" identity validate --identity "$IDENTITY_PATH" 2>/dev/null; then
    status="INVALID_IDENTITY"
    messages+=("Identity file exists but is invalid")
  fi

  # Check pinning config (only if identity OK)
  if [ "$status" = "READY" ]; then
    local has_pinning=false

    if [ -f "$CONFIG_FILE" ]; then
      local provider
      provider=$(config_get "pinning.provider")
      [ -z "$provider" ] && provider=$(config_get "ipfs.provider")

      if [ "$provider" = "solvr" ]; then
        local solvr_key
        solvr_key=$(config_get "solvr.apiKey")
        [ -n "$solvr_key" ] && has_pinning=true
      elif [ "$provider" = "both" ]; then
        local solvr_key pinata_jwt
        solvr_key=$(config_get "solvr.apiKey")
        pinata_jwt=$(config_get "pinata.jwt")
        [ -n "$solvr_key" ] || [ -n "$pinata_jwt" ] && has_pinning=true
      else
        # pinata (default)
        local pinata_jwt
        pinata_jwt=$(config_get "pinata.jwt")
        [ -n "$pinata_jwt" ] && has_pinning=true
      fi
    fi

    if ! $has_pinning; then
      status="NO_PINNING"
      messages+=("No IPFS pinning configured (set solvr.apiKey or pinata.jwt)")
    fi
  fi

  echo "STATUS: $status"
  [ "$status" = "READY" ] && echo "  Identity: $IDENTITY_PATH"
  [ "$status" = "READY" ] && echo "  Config: $CONFIG_FILE"
  for msg in "${messages[@]:-}"; do
    [ -n "$msg" ] && echo "  → $msg"
  done

  [ "$status" = "READY" ] && exit 0 || exit 1
}

# ============================================================
# Full status — human-readable
# ============================================================
do_full_human() {
  check_identity
  check_solvr
  check_ipfs
  check_watchdog
  check_checkpoints
  check_auth
  check_learning

  # Overall status
  local overall="READY"
  [ "$IDENTITY_STATUS" != "valid" ] && overall="DEGRADED"

  echo "═══════════════════════════════════════════════════"
  echo "  AMCP System Status"
  echo "═══════════════════════════════════════════════════"
  echo ""

  # Identity
  echo "  Identity"
  case "$IDENTITY_STATUS" in
    valid)   echo "    Status:  valid" ;;
    missing) echo "    Status:  MISSING — run: proactive-amcp init"; overall="DEGRADED" ;;
    invalid) echo "    Status:  INVALID — run: proactive-amcp init"; overall="DEGRADED" ;;
    *)       echo "    Status:  unknown" ;;
  esac
  [ -n "$IDENTITY_AID" ] && echo "    AID:     $IDENTITY_AID"
  echo "    Path:    $IDENTITY_PATH_DISPLAY"
  echo ""

  # Solvr
  echo "  Solvr"
  if [ "$SOLVR_REGISTERED" = "true" ]; then
    echo "    Registered: yes"
    [ -n "$SOLVR_DISPLAY_NAME" ] && echo "    Name:       $SOLVR_DISPLAY_NAME"
    [ -n "$SOLVR_AGENT_ID" ] && echo "    Agent ID:   $SOLVR_AGENT_ID"
    [ -n "$SOLVR_CLAIM_URL" ] && echo "    Claim URL:  $SOLVR_CLAIM_URL"
  else
    echo "    Registered: no"
    echo "    → Run: proactive-amcp solvr-register"
  fi
  echo ""

  # IPFS
  echo "  IPFS Pinning"
  echo "    Provider:  $IPFS_PROVIDER"
  case "$IPFS_PROVIDER" in
    solvr) echo "    Solvr key: $([ "$IPFS_SOLVR_CONFIGURED" = "true" ] && echo "configured" || echo "MISSING")" ;;
    pinata) echo "    Pinata JWT: $([ "$IPFS_PINATA_CONFIGURED" = "true" ] && echo "configured" || echo "MISSING")" ;;
    both)
      echo "    Pinata JWT: $([ "$IPFS_PINATA_CONFIGURED" = "true" ] && echo "configured" || echo "MISSING")"
      echo "    Solvr key:  $([ "$IPFS_SOLVR_CONFIGURED" = "true" ] && echo "configured" || echo "MISSING")"
      ;;
  esac
  [ -n "$IPFS_LAST_CID" ] && echo "    Last CID:  $IPFS_LAST_CID"
  [ -n "$IPFS_LAST_TIMESTAMP" ] && echo "    Last pin:  $IPFS_LAST_TIMESTAMP"
  echo ""

  # Watchdog
  echo "  Watchdog"
  echo "    Running:     $([ "$WATCHDOG_RUNNING" = "true" ] && echo "yes" || echo "no")"
  echo "    State:       $WATCHDOG_STATE"
  [ "$WATCHDOG_FAILURES" -gt 0 ] 2>/dev/null && echo "    Failures:    $WATCHDOG_FAILURES consecutive"
  [ -n "$WATCHDOG_LAST_CHECK" ] && [ "$WATCHDOG_LAST_CHECK" != "None" ] && echo "    Last check:  $WATCHDOG_LAST_CHECK"
  [ -n "$WATCHDOG_LAST_HEALTHY" ] && [ "$WATCHDOG_LAST_HEALTHY" != "None" ] && echo "    Last healthy: $WATCHDOG_LAST_HEALTHY"
  [ "$WATCHDOG_RETRY_DELAY" -gt 0 ] 2>/dev/null && echo "    Retry delay: ${WATCHDOG_RETRY_DELAY}s"
  echo ""

  # Checkpoints
  echo "  Checkpoints"
  echo "    Local count: $CHECKPOINT_COUNT"
  [ -n "$CHECKPOINT_LAST_CID" ] && echo "    Last CID:    $CHECKPOINT_LAST_CID"
  [ -n "$CHECKPOINT_LAST_TIMESTAMP" ] && echo "    Last time:   $CHECKPOINT_LAST_TIMESTAMP"
  echo ""

  # Auth
  echo "  Auth"
  echo "    Profiles: $([ "$AUTH_PROFILES_PRESENT" = "true" ] && echo "present" || echo "not found")"
  echo ""

  # Learning
  echo "  Learning"
  echo "    Problems:  $LEARNING_PROBLEMS_TOTAL total, $LEARNING_PROBLEMS_OPEN open"
  echo "    Learnings: $LEARNING_LEARNINGS_TOTAL total"
  echo ""

  echo "═══════════════════════════════════════════════════"
  echo "  Overall: $overall"
  echo "═══════════════════════════════════════════════════"

  [ "$overall" = "READY" ] && exit 0 || exit 1
}

# ============================================================
# Full status — JSON
# ============================================================
do_full_json() {
  check_identity
  check_solvr
  check_ipfs
  check_watchdog
  check_checkpoints
  check_auth
  check_learning

  local overall="READY"
  [ "$IDENTITY_STATUS" != "valid" ] && overall="DEGRADED"

  python3 -c "
import json

data = {
    'overall': '$overall',
    'identity': {
        'status': '$IDENTITY_STATUS',
        'aid': '$IDENTITY_AID',
        'path': '$IDENTITY_PATH_DISPLAY'
    },
    'solvr': {
        'registered': $( [ "$SOLVR_REGISTERED" = "true" ] && echo "True" || echo "False" ),
        'keyPresent': $( [ "$SOLVR_KEY_PRESENT" = "true" ] && echo "True" || echo "False" ),
        'displayName': '$SOLVR_DISPLAY_NAME',
        'agentId': '$SOLVR_AGENT_ID',
        'claimUrl': '$SOLVR_CLAIM_URL'
    },
    'ipfs': {
        'provider': '$IPFS_PROVIDER',
        'pinataConfigured': $( [ "$IPFS_PINATA_CONFIGURED" = "true" ] && echo "True" || echo "False" ),
        'solvrConfigured': $( [ "$IPFS_SOLVR_CONFIGURED" = "true" ] && echo "True" || echo "False" ),
        'lastCid': '$IPFS_LAST_CID',
        'lastTimestamp': '$IPFS_LAST_TIMESTAMP'
    },
    'watchdog': {
        'running': $( [ "$WATCHDOG_RUNNING" = "true" ] && echo "True" || echo "False" ),
        'state': '$WATCHDOG_STATE',
        'consecutiveFailures': int('${WATCHDOG_FAILURES:-0}' or '0'),
        'lastCheck': '$WATCHDOG_LAST_CHECK' or None,
        'lastHealthy': '$WATCHDOG_LAST_HEALTHY' or None,
        'retryDelay': int('${WATCHDOG_RETRY_DELAY:-0}' or '0')
    },
    'checkpoints': {
        'localCount': int('${CHECKPOINT_COUNT:-0}' or '0'),
        'lastCid': '$CHECKPOINT_LAST_CID',
        'lastTimestamp': '$CHECKPOINT_LAST_TIMESTAMP'
    },
    'auth': {
        'status': '$AUTH_STATUS',
        'profilesPresent': $( [ "$AUTH_PROFILES_PRESENT" = "true" ] && echo "True" || echo "False" )
    },
    'learning': {
        'problemsTotal': int('${LEARNING_PROBLEMS_TOTAL:-0}' or '0'),
        'problemsOpen': int('${LEARNING_PROBLEMS_OPEN:-0}' or '0'),
        'learningsTotal': int('${LEARNING_LEARNINGS_TOTAL:-0}' or '0')
    }
}

# Clean up None-string values
def clean(obj):
    if isinstance(obj, dict):
        return {k: clean(v) for k, v in obj.items()}
    if isinstance(obj, str) and obj in ('', 'None', 'null', 'unknown'):
        return None
    return obj

print(json.dumps(clean(data), indent=2))
"

  [ "$overall" = "READY" ] && exit 0 || exit 1
}

# ============================================================
# Main
# ============================================================
if [ "$MODE" = "basic" ]; then
  do_basic_status
elif [ "$OUTPUT" = "json" ]; then
  do_full_json
else
  do_full_human
fi
