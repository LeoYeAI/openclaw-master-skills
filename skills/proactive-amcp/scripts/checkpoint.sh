#!/bin/bash
# checkpoint.sh — Consolidated AMCP checkpoint tool
#
# Modes:
#   (default)    Quick checkpoint (workspace only)
#   --full       Full checkpoint (all content, secrets, ontology, soul drift)
#   --auto       Continuous checkpoint runner (calls quick checkpoint in a loop)
#   --trigger T  Smart checkpoint trigger (decides if checkpoint needed)
#
# Common flags:
#   --notify     Send notifications
#   --force      Skip cleartext validation
#   --smart      Groq-powered content selection
#   --encrypt    Encrypt checkpoint (quick mode only)
#   --dry-run    Preview only (full mode only)
#   --skip-evolution   Skip memory evolution (full mode only)
#   --no-solvr-metadata  Skip Solvr registration
#   --include-secrets    Include API keys/tokens in checkpoint (auto-enabled by --full)
#   --no-secrets         Explicitly exclude secrets (default for quick mode)
#
# Auto mode flags:
#   --interval N   Minutes between checkpoints (default: 60)
#   --pause N      Minutes between batches (default: 3)
#
# Trigger mode flags:
#   --trigger TYPE   heartbeat, learning, recovery, session-end, manual
#   --quiet          Suppress output
#
# Usage:
#   checkpoint.sh                         Quick checkpoint
#   checkpoint.sh --full                  Full checkpoint with secrets
#   checkpoint.sh --full --dry-run        Preview full checkpoint
#   checkpoint.sh --auto --interval 120   Continuous runner (2h interval)
#   checkpoint.sh --trigger heartbeat     Smart trigger
#   checkpoint.sh --smart --full          Full + Groq content selection

set -euo pipefail

command -v python3 &>/dev/null || { echo "FATAL: python3 required but not found" >&2; exit 2; }

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0" 2>/dev/null || realpath "$0" 2>/dev/null || echo "$0")")" && pwd)"
AMCP_CLI="${AMCP_CLI:-$(command -v amcp 2>/dev/null || echo "$HOME/bin/amcp")}"
IDENTITY_PATH="${IDENTITY_PATH:-$HOME/.amcp/identity.json}"
CONFIG_FILE="${CONFIG_FILE:-$HOME/.amcp/config.json}"

# Ensure Node.js webcrypto is available for amcp CLI
case "${NODE_OPTIONS:-}" in
  *--experimental-global-webcrypto*) ;;
  *) export NODE_OPTIONS="${NODE_OPTIONS:+$NODE_OPTIONS }--experimental-global-webcrypto" ;;
esac

# ============================================================
# Arg parsing — determine mode and collect flags
# ============================================================
MODE="quick"
NOTIFY=""
FORCE_CHECKPOINT=""
SMART_CHECKPOINT=false
DRY_RUN=false
SKIP_EVOLUTION=false
NO_SOLVR_METADATA=false
ENCRYPT=false
QUIET=false
INCLUDE_SECRETS=false  # Only extract secrets when explicitly requested or --full mode
INTERVAL_MINS="${INTERVAL_MINS:-60}"
BATCH_PAUSE_MINS="${BATCH_PAUSE_MINS:-3}"
TRIGGER_TYPE="manual"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --full)     MODE="full"; INCLUDE_SECRETS=true; shift ;;
    --auto)     MODE="auto"; shift ;;
    --trigger)  MODE="trigger"; TRIGGER_TYPE="${2:-manual}"; shift 2 || shift ;;
    --trigger=*) MODE="trigger"; TRIGGER_TYPE="${1#*=}"; shift ;;
    --notify)   NOTIFY="--notify"; shift ;;
    --force)    FORCE_CHECKPOINT="force"; shift ;;
    --smart)    SMART_CHECKPOINT=true; shift ;;
    --dry-run)  DRY_RUN=true; shift ;;
    --skip-evolution) SKIP_EVOLUTION=true; shift ;;
    --no-solvr-metadata) NO_SOLVR_METADATA=true; shift ;;
    --encrypt)  ENCRYPT=true; shift ;;
    --quiet|-q) QUIET=true; shift ;;
    --include-secrets) INCLUDE_SECRETS=true; shift ;;
    --no-secrets) INCLUDE_SECRETS=false; shift ;;
    --interval) INTERVAL_MINS="$2"; shift 2 ;;
    --pause)    BATCH_PAUSE_MINS="$2"; shift 2 ;;
    -h|--help)
      sed -n '2,/^[^#]/{ /^#/s/^# \{0,1\}//p; }' "$0"
      exit 0
      ;;
    *) shift ;;
  esac
done

# ============================================================
# Auto mode — continuous checkpoint runner
# No identity validation needed upfront (each iteration validates)
# ============================================================
if [ "$MODE" = "auto" ]; then
  AGENT_NAME="${AGENT_NAME:-ClaudiusThePirateEmperor}"
  BATCH_PAUSE_SECS=$((BATCH_PAUSE_MINS * 60))
  INTERVAL_SECS=$((INTERVAL_MINS * 60))

  format_time() {
    local secs=$1
    printf "%02d:%02d:%02d" $((secs/3600)) $((secs%3600/60)) $((secs%60))
  }

  checkpoint_count=0
  runner_start=$(date +%s)

  trap 'echo "Interrupted"; [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "⏹️ [$AGENT_NAME] Auto-checkpoint stopped"; exit 1' INT TERM

  echo "=== AMCP Auto-Checkpoint ==="
  echo "Agent: $AGENT_NAME"
  echo "Checkpoint interval: ${INTERVAL_MINS}m"
  echo "Batch pause: ${BATCH_PAUSE_MINS}m"
  echo ""

  [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" \
    "🚀 [$AGENT_NAME] Auto-checkpoint started. Interval: ${INTERVAL_MINS}m, pause: ${BATCH_PAUSE_MINS}m"

  while true; do
    checkpoint_count=$((checkpoint_count + 1))
    batch_start=$(date +%s)

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "▶ CHECKPOINT #${checkpoint_count}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" \
      "🔄 [$AGENT_NAME] Checkpoint #${checkpoint_count} starting..."

    if "$SCRIPT_DIR/checkpoint.sh"; then
      batch_end=$(date +%s)
      batch_time=$((batch_end - batch_start))
      total_time=$((batch_end - runner_start))
      CID=$(python3 -c "import json; print(json.load(open('$HOME/.amcp/last-checkpoint.json')).get('cid','local'))" 2>/dev/null || echo 'local')
      [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" \
        "✅ [$AGENT_NAME] Checkpoint #${checkpoint_count} complete. CID: $CID. Took: $(format_time $batch_time). Total uptime: $(format_time $total_time)"
    else
      batch_end=$(date +%s)
      batch_time=$((batch_end - batch_start))
      [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" \
        "❌ [$AGENT_NAME] Checkpoint #${checkpoint_count} FAILED after $(format_time $batch_time)"
    fi

    echo ""
    remaining=$((INTERVAL_SECS - BATCH_PAUSE_SECS))
    if [ "$remaining" -gt 0 ]; then
      echo "⏸️  Pausing ${BATCH_PAUSE_MINS}m before next interval check..."
      sleep $BATCH_PAUSE_SECS
      echo "⏳ Waiting remaining time until next checkpoint..."
      sleep $remaining
    else
      echo "⏸️  Waiting ${INTERVAL_MINS}m until next checkpoint..."
      sleep $INTERVAL_SECS
    fi
  done
  exit 0
fi

# ============================================================
# Trigger mode — smart checkpoint decision
# Decides WHETHER to checkpoint based on trigger type
# ============================================================
if [ "$MODE" = "trigger" ]; then
  LAST_CHECKPOINT_FILE="${LAST_CHECKPOINT_FILE:-$HOME/.amcp/last-checkpoint.json}"
  WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
  CHECKPOINT_STATE_FILE="${CHECKPOINT_STATE_FILE:-$HOME/.amcp/checkpoint-state.json}"
  HEARTBEAT_CHECKPOINT_HOURS="${HEARTBEAT_CHECKPOINT_HOURS:-2}"
  HEARTBEAT_CHECKPOINT_CHANGES="${HEARTBEAT_CHECKPOINT_CHANGES:-10}"

  tlog() { [ "$QUIET" = true ] || echo "[smart-checkpoint] $1"; }

  get_last_checkpoint_time() {
    if [ -f "$LAST_CHECKPOINT_FILE" ]; then
      python3 -c "
from datetime import datetime
import json
try:
    d = json.load(open('$LAST_CHECKPOINT_FILE'))
    ts = d.get('timestamp', '')
    if ts:
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        print(int(dt.timestamp()))
    else:
        print(0)
except Exception:
    print(0)
" 2>/dev/null || echo "0"
    else
      echo "0"
    fi
  }

  hours_since_checkpoint() {
    local last_ts now_ts diff
    last_ts=$(get_last_checkpoint_time)
    now_ts=$(date +%s)
    diff=$((now_ts - last_ts))
    echo $((diff / 3600))
  }

  count_changes_since_checkpoint() {
    local last_ts count
    last_ts=$(get_last_checkpoint_time)
    if [ "$last_ts" -eq 0 ]; then
      echo "999"
      return
    fi
    count=$(find "$WORKSPACE" -type f \( -name "*.md" -o -name "*.json" \) -newermt "@$last_ts" 2>/dev/null | wc -l)
    echo "$count"
  }

  # Load thresholds from config
  if [ -f "$CONFIG_FILE" ]; then
    HEARTBEAT_CHECKPOINT_HOURS=$(python3 -c "
import json
try:
    d = json.load(open('$CONFIG_FILE'))
    print(d.get('checkpoint',{}).get('heartbeatHours', 2))
except:
    print(2)
" 2>/dev/null || echo "2")
    HEARTBEAT_CHECKPOINT_CHANGES=$(python3 -c "
import json
try:
    d = json.load(open('$CONFIG_FILE'))
    print(d.get('checkpoint',{}).get('heartbeatChanges', 10))
except:
    print(10)
" 2>/dev/null || echo "10")
  fi

  should_checkpoint() {
    local trigger="$1"
    case "$trigger" in
      learning|recovery)
        tlog "Trigger '$trigger' → always checkpoint"
        return 0
        ;;
      heartbeat)
        local hours changes
        hours=$(hours_since_checkpoint)
        changes=$(count_changes_since_checkpoint)
        tlog "Heartbeat check: ${hours}h since last, $changes files changed"
        if [ "$hours" -ge "$HEARTBEAT_CHECKPOINT_HOURS" ]; then
          tlog "Checkpoint needed: ${hours}h >= ${HEARTBEAT_CHECKPOINT_HOURS}h threshold"
          return 0
        fi
        if [ "$changes" -ge "$HEARTBEAT_CHECKPOINT_CHANGES" ]; then
          tlog "Checkpoint needed: $changes changes >= $HEARTBEAT_CHECKPOINT_CHANGES threshold"
          return 0
        fi
        tlog "No checkpoint needed (${hours}h, $changes changes)"
        return 1
        ;;
      session-end)
        local changes
        changes=$(count_changes_since_checkpoint)
        if [ "$changes" -gt 0 ]; then
          tlog "Session end: $changes files changed → checkpoint"
          return 0
        fi
        tlog "Session end: no changes → skip"
        return 1
        ;;
      manual|*)
        tlog "Manual trigger → checkpoint"
        return 0
        ;;
    esac
  }

  do_trigger_checkpoint() {
    local trigger="$1"
    tlog "Creating checkpoint (trigger: $trigger)..."
    # Use full checkpoint for recovery and learning triggers
    local checkpoint_args=("--notify")
    if [ "$trigger" = "recovery" ] || [ "$trigger" = "learning" ]; then
      checkpoint_args+=("--full")
    fi

    if "$SCRIPT_DIR/checkpoint.sh" "${checkpoint_args[@]}" 2>&1 | while IFS= read -r line; do
      tlog "  $line"
    done; then
      mkdir -p "$(dirname "$CHECKPOINT_STATE_FILE")"
      python3 -c "
import json
from datetime import datetime
state = {
    'lastTrigger': '$trigger',
    'lastCheckpoint': datetime.utcnow().isoformat() + 'Z',
    'triggerCounts': {}
}
try:
    with open('$CHECKPOINT_STATE_FILE') as f:
        old = json.load(f)
        state['triggerCounts'] = old.get('triggerCounts', {})
except Exception:
    pass
state['triggerCounts']['$trigger'] = state['triggerCounts'].get('$trigger', 0) + 1
with open('$CHECKPOINT_STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)
"
      tlog "✅ Checkpoint complete"
      return 0
    else
      tlog "❌ Checkpoint failed"
      return 1
    fi
  }

  if [ "$FORCE_CHECKPOINT" = "force" ]; then
    do_trigger_checkpoint "$TRIGGER_TYPE"
    exit $?
  fi

  if should_checkpoint "$TRIGGER_TYPE"; then
    do_trigger_checkpoint "$TRIGGER_TYPE"
    exit $?
  fi
  exit 0
fi

# ============================================================
# Shared setup for quick/full checkpoint modes
# ============================================================
get_workspace() {
  local ws
  ws=$(python3 -c "import json,os; d=json.load(open(os.path.expanduser('~/.openclaw/openclaw.json'))); print(d.get('agents',{}).get('defaults',{}).get('workspace','~/.openclaw/workspace'))" 2>/dev/null || echo '~/.openclaw/workspace')
  echo "${ws/#\~/$HOME}"
}

CONTENT_DIR="${CONTENT_DIR:-$(get_workspace)}"
CHECKPOINT_DIR="${CHECKPOINT_DIR:-$HOME/.amcp/checkpoints}"
LAST_CHECKPOINT_FILE="$HOME/.amcp/last-checkpoint.json"
SECRETS_FILE="$HOME/.amcp/secrets.json"
KEEP_CHECKPOINTS="${KEEP_CHECKPOINTS:-5}"
AGENT_NAME="${AGENT_NAME:-ClaudiusThePirateEmperor}"

# Source secret scanner
source "$SCRIPT_DIR/audit-config.sh"

# Pinata config — read from ~/.amcp/config.json
PINATA_JWT="${PINATA_JWT:-$(python3 -c "import json; d=json.load(open('$HOME/.amcp/config.json')); print(d.get('pinata',{}).get('jwt',''))" 2>/dev/null || echo '')}"
PINNING_PROVIDER="${PINNING_PROVIDER:-$(python3 -c "import json; d=json.load(open('$HOME/.amcp/config.json')); print(d.get('pinning',{}).get('provider','pinata'))" 2>/dev/null || echo 'pinata')}"

# Cleanup secrets on exit
cleanup() { rm -f "$SECRETS_FILE"; }
trap cleanup EXIT

# ============================================================
# Identity validation
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

validate_identity
warn_identity_secrets
mkdir -p "$CHECKPOINT_DIR"

# Get previous CID
PREVIOUS_CID=""
if [ -f "$LAST_CHECKPOINT_FILE" ]; then
  PREVIOUS_CID=$(python3 -c "import json; print(json.load(open('$LAST_CHECKPOINT_FILE')).get('cid',''))" 2>/dev/null || echo '')
fi

# ============================================================
# Shared pinning functions
# ============================================================
# CHECKPOINT_PATH and TIMESTAMP must be set before calling these
pin_to_pinata() {
  if [ -z "$PINATA_JWT" ]; then
    echo "⚠️ No Pinata JWT configured"
    return 1
  fi
  local response
  response=$(curl -s -X POST "https://api.pinata.cloud/pinning/pinFileToIPFS" \
    -H "Authorization: Bearer $PINATA_JWT" \
    -F "file=@$CHECKPOINT_PATH" \
    -F "pinataMetadata={\"name\":\"amcp-${CHECKPOINT_TYPE:-quick}-$AGENT_NAME-$TIMESTAMP\"}")
  PINATA_CID=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('IpfsHash',''))" 2>/dev/null || echo '')
  if [ -n "$PINATA_CID" ]; then
    echo "  Pinata: $PINATA_CID"
    return 0
  else
    echo "⚠️ Pinata error: $response"
    return 1
  fi
}

pin_to_solvr() {
  if [ -x "$SCRIPT_DIR/pin-to-solvr.sh" ]; then
    local solvr_output
    solvr_output=$("$SCRIPT_DIR/pin-to-solvr.sh" "$CHECKPOINT_PATH" "amcp-${CHECKPOINT_TYPE:-quick}-$AGENT_NAME-$TIMESTAMP") || {
      echo "⚠️ Solvr pin failed"
      SOLVR_CID=""
      return 1
    }
    SOLVR_CID="$solvr_output"
    echo "  Solvr: $SOLVR_CID"
    return 0
  else
    echo "⚠️ pin-to-solvr.sh not found"
    return 1
  fi
}

do_pinning() {
  CID=""
  PINATA_CID=""
  SOLVR_CID=""
  echo "Pinning to IPFS (provider: $PINNING_PROVIDER)..."
  case "$PINNING_PROVIDER" in
    solvr)
      pin_to_solvr
      CID="$SOLVR_CID"
      ;;
    both)
      pin_to_pinata || true
      pin_to_solvr || true
      CID="${PINATA_CID:-$SOLVR_CID}"
      if [ -z "$PINATA_CID" ] && [ -z "$SOLVR_CID" ]; then
        echo "⚠️ Both pinning providers failed"
      elif [ -n "$PINATA_CID" ] && [ -n "$SOLVR_CID" ] && [ "$PINATA_CID" != "$SOLVR_CID" ]; then
        echo "⚠️ CID mismatch: Pinata=$PINATA_CID Solvr=$SOLVR_CID"
      fi
      ;;
    pinata|*)
      pin_to_pinata
      CID="$PINATA_CID"
      ;;
  esac
}

# Register checkpoint with Solvr unified API (best-effort, non-blocking)
register_with_solvr() {
  if [ "$NO_SOLVR_METADATA" = false ] && [ -n "$CID" ] && [ -x "$SCRIPT_DIR/register-checkpoint-solvr.sh" ]; then
    "$SCRIPT_DIR/register-checkpoint-solvr.sh" \
      --cid "$CID" \
      --checkpoint-path "$CHECKPOINT_PATH" \
      --name "amcp-${CHECKPOINT_TYPE:-quick}-$AGENT_NAME-$TIMESTAMP" \
      --content-dir "$CONTENT_DIR" || true
  fi
}

# Rotate old checkpoints matching a glob pattern
rotate_checkpoints() {
  local pattern="$1"
  echo "Rotating old checkpoints (keep $KEEP_CHECKPOINTS)..."
  ls -1t "$CHECKPOINT_DIR"/$pattern 2>/dev/null | tail -n +$((KEEP_CHECKPOINTS + 1)) | while read -r f; do
    echo "Removing old: $f"
    rm -f "$f"
  done
}

# ============================================================
# Full mode — dispatch to _checkpoint-full.sh
# ============================================================
if [ "$MODE" = "full" ]; then
  source "$SCRIPT_DIR/_checkpoint-full.sh"
  run_full_checkpoint
  exit $?
fi

# ============================================================
# Quick mode (default)
# ============================================================
CHECKPOINT_TYPE="quick"
CHECKPOINT_KEYS_FILE="$HOME/.amcp/checkpoint-keys.json"

extract_secrets() {
  python3 << 'EOF'
import json
import os

secrets = []

# 1. AMCP config (Pinata, API keys)
amcp_path = os.path.expanduser("~/.amcp/config.json")
if os.path.exists(amcp_path):
    with open(amcp_path) as f:
        amcp = json.load(f)

    if "pinata" in amcp:
        if amcp["pinata"].get("jwt"):
            secrets.append({
                "key": "PINATA_JWT",
                "value": amcp["pinata"]["jwt"],
                "type": "jwt",
                "targets": [{"kind": "file", "path": amcp_path, "jsonPath": "pinata.jwt"}]
            })
        if amcp["pinata"].get("apiKey"):
            secrets.append({
                "key": "PINATA_API_KEY",
                "value": amcp["pinata"]["apiKey"],
                "type": "api_key",
                "targets": [{"kind": "file", "path": amcp_path, "jsonPath": "pinata.apiKey"}]
            })
        if amcp["pinata"].get("secret"):
            secrets.append({
                "key": "PINATA_SECRET",
                "value": amcp["pinata"]["secret"],
                "type": "credential",
                "targets": [{"kind": "file", "path": amcp_path, "jsonPath": "pinata.secret"}]
            })

    if "apiKeys" in amcp:
        if amcp["apiKeys"].get("aclawdemy", {}).get("jwt"):
            secrets.append({
                "key": "ACLAWDEMY_JWT",
                "value": amcp["apiKeys"]["aclawdemy"]["jwt"],
                "type": "jwt",
                "targets": [{"kind": "file", "path": amcp_path, "jsonPath": "apiKeys.aclawdemy.jwt"}]
            })
        if amcp["apiKeys"].get("agentarxiv"):
            secrets.append({
                "key": "AGENTARXIV_API_KEY",
                "value": amcp["apiKeys"]["agentarxiv"],
                "type": "api_key",
                "targets": [{"kind": "file", "path": amcp_path, "jsonPath": "apiKeys.agentarxiv"}]
            })
        if amcp["apiKeys"].get("brave"):
            secrets.append({
                "key": "BRAVE_SEARCH_API_KEY",
                "value": amcp["apiKeys"]["brave"],
                "type": "api_key",
                "targets": [{"kind": "file", "path": amcp_path, "jsonPath": "apiKeys.brave"}]
            })

# 2. OpenClaw config
oc_path = os.path.expanduser("~/.openclaw/openclaw.json")
if os.path.exists(oc_path):
    with open(oc_path) as f:
        oc = json.load(f)

    for name, cfg in oc.get("skills", {}).get("entries", {}).items():
        if "apiKey" in cfg:
            secrets.append({
                "key": f"{name.upper()}_API_KEY",
                "value": cfg["apiKey"],
                "type": "api_key",
                "targets": [{"kind": "file", "path": oc_path, "jsonPath": f"skills.entries.{name}.apiKey"}]
            })

# 3. Auth profiles
auth_path = os.path.expanduser("~/.openclaw/auth-profiles.json")
if os.path.exists(auth_path):
    with open(auth_path) as f:
        auth = json.load(f)

    for profile, cfg in auth.get("profiles", {}).items():
        if "token" in cfg:
            secrets.append({
                "key": f"{profile.upper()}_TOKEN",
                "value": cfg["token"].get("key", "") if isinstance(cfg["token"], dict) else cfg["token"],
                "type": "token",
                "targets": [{"kind": "file", "path": auth_path, "jsonPath": f"profiles.{profile}.token.key"}]
            })

print(json.dumps(secrets, indent=2))
EOF
}

# Notify start
if [ "$NOTIFY" = "--notify" ]; then
  [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "🔄 [$AGENT_NAME] Starting checkpoint..."
fi

echo "=== AMCP Checkpoint ==="
echo "Content: $CONTENT_DIR"
echo "Identity: $IDENTITY_PATH"
[ -n "$PREVIOUS_CID" ] && echo "Previous CID: $PREVIOUS_CID"

# Extract secrets (only if --full or --include-secrets)
if [ "$INCLUDE_SECRETS" = true ]; then
  echo "Extracting secrets (--full or --include-secrets)..."
  extract_secrets > "$SECRETS_FILE"
  chmod 600 "$SECRETS_FILE"
  SECRET_COUNT=$(python3 -c "import json; print(len(json.load(open('$SECRETS_FILE'))))")
  echo "Found $SECRET_COUNT secrets"
else
  echo "Skipping secrets (quick mode - use --full or --include-secrets to include)"
  echo "[]" > "$SECRETS_FILE"
  chmod 600 "$SECRETS_FILE"
  SECRET_COUNT=0
fi

# Pre-validation: scan content for cleartext secrets
scan_for_secrets "$CONTENT_DIR" "$FORCE_CHECKPOINT"

# Smart content selection (--smart flag): use Groq to filter memory files
EFFECTIVE_CONTENT_DIR="$CONTENT_DIR"
SMART_STAGING=""
if [ "$SMART_CHECKPOINT" = true ] && [ -x "$SCRIPT_DIR/smart-checkpoint-filter.sh" ]; then
  echo ""
  echo "=== Smart Content Selection (Groq) ==="
  local_smart_args=("--content-dir" "$CONTENT_DIR")

  SMART_MANIFEST=$("$SCRIPT_DIR/smart-checkpoint-filter.sh" "${local_smart_args[@]}" 2>&1 | tee /dev/stderr | tail -1) || {
    echo "WARN: Smart filter failed, including all files (fallback)" >&2
    SMART_MANIFEST=""
  }

  if [ -n "$SMART_MANIFEST" ]; then
    SMART_STAGING=$(mktemp -d)
    rsync -a \
      --exclude='.venv' --exclude='.git' --exclude='node_modules' \
      --exclude='__pycache__' --exclude='*.pyc' --exclude='.pytest_cache' \
      "$CONTENT_DIR/" "$SMART_STAGING/"

    excluded_count=0
    while IFS= read -r excl_file; do
      staged_path="$SMART_STAGING/$excl_file"
      if [ -f "$staged_path" ]; then
        rm -f "$staged_path"
        excluded_count=$((excluded_count + 1))
      fi
    done < <(echo "$SMART_MANIFEST" | python3 -c "
import json, sys
try:
    m = json.loads(sys.stdin.read())
    for f in m.get('exclude', []):
        print(f)
except: pass
" 2>/dev/null)
    echo "  Excluded $excluded_count files from checkpoint"
    EFFECTIVE_CONTENT_DIR="$SMART_STAGING"
  fi
elif [ "$SMART_CHECKPOINT" = true ]; then
  echo "WARN: --smart requested but smart-checkpoint-filter.sh not found" >&2
fi

# Cleanup smart staging on exit
cleanup_smart() {
  if [ -n "${SMART_STAGING:-}" ]; then
    rm -rf "$SMART_STAGING"
  fi
}
trap 'cleanup; cleanup_smart' EXIT

# Create checkpoint
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
CHECKPOINT_PATH="$CHECKPOINT_DIR/checkpoint-$TIMESTAMP.amcp"

echo "Creating checkpoint..."
AMCP_ARGS="checkpoint create --identity $IDENTITY_PATH --content $EFFECTIVE_CONTENT_DIR --secrets $SECRETS_FILE --out $CHECKPOINT_PATH"
[ -n "$PREVIOUS_CID" ] && AMCP_ARGS="$AMCP_ARGS --previous $PREVIOUS_CID"

$AMCP_CLI $AMCP_ARGS

echo "Checkpoint created: $CHECKPOINT_PATH"

# Encrypt checkpoint if requested
if [ "$ENCRYPT" = true ]; then
  echo ""
  echo "=== Encrypting Checkpoint ==="
  ENCRYPT_KEY=$(openssl rand -hex 32)
  ENCRYPTED_PATH="${CHECKPOINT_PATH}.enc"
  openssl enc -aes-256-cbc -salt -pbkdf2 \
    -in "$CHECKPOINT_PATH" \
    -out "$ENCRYPTED_PATH" \
    -pass "pass:${ENCRYPT_KEY}" || {
      echo "FATAL: Encryption failed" >&2
      exit 1
    }
  mv "$ENCRYPTED_PATH" "$CHECKPOINT_PATH"
  echo "  Encrypted checkpoint: $CHECKPOINT_PATH"

  if [ ! -f "$CHECKPOINT_KEYS_FILE" ]; then
    echo '{}' > "$CHECKPOINT_KEYS_FILE"
    chmod 600 "$CHECKPOINT_KEYS_FILE"
  fi
  ENCRYPT_KEY_SAVED=true
  echo "  Encryption key will be saved after pinning"
fi

# Pin to IPFS
do_pinning

if [ -n "$CID" ]; then
  if [ "$ENCRYPT" = true ]; then
    echo "✅ Encrypted checkpoint pinned to IPFS: $CID"
  else
    echo "✅ Pinned to IPFS: $CID"
  fi
fi

# Save encryption key keyed by CID (or localPath if no CID)
if [ "$ENCRYPT" = true ] && [ "${ENCRYPT_KEY_SAVED:-false}" = true ]; then
  local_key_id="${CID:-$CHECKPOINT_PATH}"
  python3 -c "
import json, os
keys_path = os.path.expanduser('$CHECKPOINT_KEYS_FILE')
keys = {}
if os.path.exists(keys_path):
    with open(keys_path) as f:
        keys = json.load(f)
keys['$local_key_id'] = {
    'key': '$ENCRYPT_KEY',
    'created': '$(date -Iseconds)',
    'localPath': '$CHECKPOINT_PATH'
}
with open(keys_path, 'w') as f:
    json.dump(keys, f, indent=2)
os.chmod(keys_path, 0o600)
" 2>/dev/null || echo "WARN: Failed to save encryption key" >&2
  echo "  Encryption key saved to $CHECKPOINT_KEYS_FILE"
fi

# Update last checkpoint file
ENCRYPTED_FLAG="false"
[ "$ENCRYPT" = true ] && ENCRYPTED_FLAG="true"
cat > "$LAST_CHECKPOINT_FILE" << EOJSON
{
  "cid": "$CID",
  "localPath": "$CHECKPOINT_PATH",
  "timestamp": "$(date -Iseconds)",
  "previousCID": "$PREVIOUS_CID",
  "secretCount": $SECRET_COUNT,
  "encrypted": $ENCRYPTED_FLAG
}
EOJSON

echo "Updated: $LAST_CHECKPOINT_FILE"

# Register with Solvr
register_with_solvr

# Rotate old checkpoints
rotate_checkpoints "checkpoint-*.amcp"

# Notify end
if [ "$NOTIFY" = "--notify" ]; then
  if [ -n "$CID" ]; then
    [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "✅ [$AGENT_NAME] Checkpoint complete. CID: $CID"
  else
    [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "✅ [$AGENT_NAME] Checkpoint complete (local only)"
  fi
fi

echo "=== Done ==="
