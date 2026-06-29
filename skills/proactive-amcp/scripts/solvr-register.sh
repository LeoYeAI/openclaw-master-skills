#!/bin/bash
# solvr-register.sh - Auto-register child Solvr account on first boot
# Usage: ./solvr-register.sh [--instance-name <name>]
#
# Checks if a Solvr API key already exists. If not, and if parentSolvrName
# is configured, auto-registers as a child agent using protocol-08 naming.
# Root agents (no parentSolvrName) get a warning and skip registration.
#
# Config read from:
#   - Environment: SOLVR_API_KEY
#   - OpenClaw:    ~/.openclaw/openclaw.json → skills.entries.proactive-solvr.apiKey
#   - AMCP:        ~/.amcp/config.json → solvr.apiKey
#
# Parent name from:
#   - OpenClaw:    ~/.openclaw/openclaw.json → skills.entries.proactive-amcp.config.parentSolvrName
#   - AMCP:        ~/.amcp/config.json → solvr.parentName

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SOLVR_API_URL="${SOLVR_API_URL:-https://api.solvr.dev/v1}"
OC_CONFIG="${OC_CONFIG:-$HOME/.openclaw/openclaw.json}"
AMCP_CONFIG="${AMCP_CONFIG:-$HOME/.amcp/config.json}"
AGENT_NAME="${AGENT_NAME:-$(hostname -s)}"

# ============================================================
# Helpers
# ============================================================

log_info()  { echo "[solvr-register] INFO:  $*"; }
log_ok()    { echo "[solvr-register] OK:    $*"; }
log_warn()  { echo "[solvr-register] WARN:  $*" >&2; }
log_error() { echo "[solvr-register] ERROR: $*" >&2; }

die_json() {
  local code="$1"
  local message="$2"
  cat >&2 <<EOF
{"error": true, "code": "$code", "message": "$message"}
EOF
  exit 1
}

usage() {
  cat <<EOF
proactive-amcp solvr-register — Auto-register child Solvr account

Usage: $(basename "$0") [OPTIONS]

Options:
  --name <name>            Agent name for registration (default: hostname)
  --instance-name <name>   Alias for --name
                           Must be lowercase alphanumeric + underscore, max 32 chars
  --dry-run                Show what would happen without registering
  -h, --help               Show this help

Checks:
  1. If SOLVR_API_KEY already exists → already registered, exits 0
  2. If parentSolvrName configured → auto-registers as child
  3. If no parentSolvrName → root agent, logs warning and exits 0

Config sources (checked in order):
  SOLVR_API_KEY:    env var → openclaw.json → config.json
  parentSolvrName:  openclaw.json → config.json
EOF
  exit 0
}

# ============================================================
# Parse arguments
# ============================================================

INSTANCE_NAME=""
DRY_RUN=false

parse_args() {
  while [ $# -gt 0 ]; do
    case "$1" in
      --name|--instance-name)
        [ $# -lt 2 ] && die_json "missing_arg" "$1 requires a value"
        INSTANCE_NAME="$2"
        shift 2
        ;;
      --dry-run)
        DRY_RUN=true
        shift
        ;;
      -h|--help)
        usage
        ;;
      *)
        die_json "unknown_arg" "Unknown argument: $1"
        ;;
    esac
  done
}

# ============================================================
# Config reading — check multiple sources
# ============================================================

# Read a value from OpenClaw config (jq dot-path)
read_oc_config() {
  local jq_path="$1"
  if [ -f "$OC_CONFIG" ]; then
    jq -r "$jq_path // empty" "$OC_CONFIG" 2>/dev/null || true
  fi
}

# Read a value from AMCP config (Python dot-path)
read_amcp_config() {
  local dot_path="$1"
  if [ -f "$AMCP_CONFIG" ]; then
    python3 -c "
import json, sys
with open('$AMCP_CONFIG') as f:
    d = json.load(f)
parts = '$dot_path'.split('.')
for p in parts:
    if isinstance(d, dict) and p in d:
        d = d[p]
    else:
        sys.exit(0)
if d:
    print(d)
" 2>/dev/null || true
  fi
}

# Get existing SOLVR_API_KEY from any source
get_existing_solvr_key() {
  # 1. Environment variable
  if [ -n "${SOLVR_API_KEY:-}" ]; then
    echo "$SOLVR_API_KEY"
    return
  fi

  # 2. OpenClaw config: skills.entries.proactive-solvr.apiKey
  local oc_key
  oc_key=$(read_oc_config '.skills.entries["proactive-solvr"].apiKey')
  if [ -n "$oc_key" ]; then
    echo "$oc_key"
    return
  fi

  # 3. AMCP config: solvr.apiKey
  local amcp_key
  amcp_key=$(read_amcp_config "solvr.apiKey")
  if [ -n "$amcp_key" ]; then
    echo "$amcp_key"
    return
  fi
}

# Get parentSolvrName from config
get_parent_solvr_name() {
  # 1. OpenClaw config
  local oc_parent
  oc_parent=$(read_oc_config '.skills.entries["proactive-amcp"].config.parentSolvrName')
  if [ -n "$oc_parent" ]; then
    echo "$oc_parent"
    return
  fi

  # 2. AMCP config
  local amcp_parent
  amcp_parent=$(read_amcp_config "solvr.parentName")
  if [ -n "$amcp_parent" ]; then
    echo "$amcp_parent"
    return
  fi
}

# ============================================================
# Instance name derivation
# ============================================================

derive_instance_name() {
  local name="${INSTANCE_NAME:-}"

  # Default to sanitized hostname
  if [ -z "$name" ]; then
    name=$(hostname -s 2>/dev/null | tr '[:upper:]' '[:lower:]' | tr -cd 'a-z0-9_' || echo "agent")
  fi

  # Truncate to 32 chars
  echo "${name:0:32}"
}

validate_instance_name() {
  local name="$1"

  if [ -z "$name" ]; then
    log_error "Instance name is empty"
    return 1
  fi

  if [ ${#name} -gt 32 ]; then
    log_error "Instance name must be max 32 characters (got ${#name})"
    return 1
  fi

  if ! echo "$name" | grep -qE '^[a-z0-9_]+$'; then
    log_error "Instance name must be lowercase alphanumeric + underscore only: $name"
    return 1
  fi
}

# ============================================================
# Solvr API calls
# ============================================================

# Check if child name is available (404 = available)
check_name_available() {
  local name="$1"

  local response
  response=$(curl -s -w "\n%{http_code}" --max-time 10 \
    "$SOLVR_API_URL/agents/$name" 2>/dev/null || echo -e "\n404")

  local http_code
  http_code=$(echo "$response" | tail -n1)

  [ "$http_code" = "404" ]
}

# Register child agent on Solvr
register_child() {
  local child_name="$1"
  local parent_key="$2"

  local response
  response=$(curl -s -w "\n%{http_code}" --max-time 30 \
    -X POST \
    -H "Authorization: Bearer $parent_key" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"$child_name\"}" \
    "$SOLVR_API_URL/agents/register")

  local http_code
  http_code=$(echo "$response" | tail -n1)
  local body
  body=$(echo "$response" | sed '$d')

  if [ "$http_code" != "200" ] && [ "$http_code" != "201" ]; then
    log_error "Registration failed (HTTP $http_code): $body"
    return 1
  fi

  # Extract API key from response
  local api_key
  api_key=$(echo "$body" | jq -r '.api_key // .apiKey // empty')

  if [ -z "$api_key" ]; then
    log_error "No API key in registration response: $body"
    return 1
  fi

  echo "$api_key"
}

# ============================================================
# Store API key back to config
# ============================================================

store_solvr_key() {
  local api_key="$1"
  local child_name="$2"
  local parent_name="$3"

  # 1. Store in AMCP config
  if [ -x "$SCRIPT_DIR/config.sh" ]; then
    "$SCRIPT_DIR/config.sh" set solvr.apiKey "$api_key"
    "$SCRIPT_DIR/config.sh" set solvr.name "$child_name"
    "$SCRIPT_DIR/config.sh" set solvr.parentName "$parent_name"
    log_ok "Stored solvr.apiKey in AMCP config"
  fi

  # 2. Store in OpenClaw config (if file exists)
  if [ -f "$OC_CONFIG" ]; then
    python3 -c "
import json
with open('$OC_CONFIG') as f:
    d = json.load(f)
d.setdefault('skills', {}).setdefault('entries', {}).setdefault('proactive-solvr', {})['apiKey'] = '$api_key'
with open('$OC_CONFIG', 'w') as f:
    json.dump(d, f, indent=2)
    f.write('\n')
" 2>/dev/null && log_ok "Stored apiKey in OpenClaw config" || log_warn "Could not update OpenClaw config"
  fi
}

# ============================================================
# Main
# ============================================================

main() {
  parse_args "$@"

  log_info "Checking Solvr registration status..."

  # Step 1: Check if already registered
  local existing_key
  existing_key=$(get_existing_solvr_key)

  if [ -n "$existing_key" ]; then
    # Validate existing key before accepting
    local me_response me_code
    me_response=$(curl -s -w "\n%{http_code}" --max-time 10 \
      -H "Authorization: Bearer $existing_key" \
      "$SOLVR_API_URL/me" 2>/dev/null || echo -e "\n000")
    me_code=$(echo "$me_response" | tail -n1)
    if [ "$me_code" = "200" ]; then
      local display_name
      display_name=$(echo "$me_response" | sed '$d' | jq -r '.display_name // .name // "unknown"' 2>/dev/null || echo "unknown")
      log_ok "Already registered as $display_name on Solvr"
      echo "{\"already_registered\": true, \"display_name\": \"$display_name\"}"
      return 0
    elif [ "$me_code" = "401" ] || [ "$me_code" = "403" ]; then
      log_warn "Existing Solvr key is invalid (HTTP $me_code) — will re-register"
    else
      # Network error or other — accept the key as-is
      log_ok "Already registered — SOLVR_API_KEY exists (could not verify: HTTP $me_code)"
      echo '{"already_registered": true}'
      return 0
    fi
  fi

  log_info "No SOLVR_API_KEY found — checking for parent config..."

  # Step 2: Check for parentSolvrName
  local parent_name
  parent_name=$(get_parent_solvr_name)

  if [ -z "$parent_name" ]; then
    # Root agent — no parent, cannot auto-register
    log_warn "No parentSolvrName configured — this is a root agent"
    log_warn "Solvr features disabled until manual registration"
    log_warn "Register manually at https://solvr.dev or set parentSolvrName in config"
    echo '{"already_registered": false, "reason": "root_agent", "solvr_disabled": true}'
    return 0
  fi

  # Step 3: Child agent — auto-register
  log_info "Parent found: $parent_name"

  # We need the parent's API key to register child
  # The parent key should come from a separate source (e.g., passed during deploy)
  local parent_key="${SOLVR_PARENT_KEY:-${SOLVR_API_KEY:-}}"

  # Check AMCP config for parent key as fallback
  if [ -z "$parent_key" ]; then
    parent_key=$(read_amcp_config "solvr.parentKey")
  fi
  if [ -z "$parent_key" ]; then
    parent_key=$(read_oc_config '.skills.entries["proactive-solvr"].parentKey')
  fi

  if [ -z "$parent_key" ]; then
    log_warn "Cannot auto-register: parentSolvrName is set but no parent API key available"
    log_warn "Set SOLVR_PARENT_KEY env var or solvr.parentKey in config"
    echo '{"already_registered": false, "reason": "no_parent_key"}'
    return 0
  fi

  # Derive and validate instance name
  local instance_name
  instance_name=$(derive_instance_name)
  if ! validate_instance_name "$instance_name"; then
    die_json "invalid_instance_name" "Instance name '$instance_name' is invalid"
  fi

  # Build child name (protocol-08)
  local child_name="${parent_name}_child_${instance_name}"
  log_info "Child name: $child_name"

  if [ "$DRY_RUN" = true ]; then
    log_info "[DRY RUN] Would register: $child_name"
    echo "{\"dry_run\": true, \"child_name\": \"$child_name\", \"parent_name\": \"$parent_name\"}"
    return 0
  fi

  # Check name availability
  log_info "Checking name availability..."
  if ! check_name_available "$child_name"; then
    log_warn "Name '$child_name' may be taken, trying with suffix..."
    local found=false
    for i in 2 3 4 5; do
      child_name="${parent_name}_child_${instance_name}_${i}"
      if check_name_available "$child_name"; then
        log_info "Using: $child_name"
        found=true
        break
      fi
    done
    if [ "$found" != true ]; then
      die_json "name_unavailable" "Could not find available name after 5 attempts"
    fi
  fi

  # Register child
  log_info "Registering child on Solvr..."
  local child_api_key
  child_api_key=$(register_child "$child_name" "$parent_key")

  if [ -z "$child_api_key" ]; then
    die_json "registration_failed" "Child registration returned no API key"
  fi

  # Step 4: Store the key
  store_solvr_key "$child_api_key" "$child_name" "$parent_name"

  # Step 5: Set pinning provider to solvr (key now exists)
  if [ -x "$SCRIPT_DIR/config.sh" ]; then
    "$SCRIPT_DIR/config.sh" set pinning.provider solvr 2>/dev/null || true
    log_ok "Set pinning.provider to solvr"
  fi

  log_ok "Child registered: $child_name"

  # Link AMCP identity to Solvr agent (proves AID ownership)
  local identity_path="${IDENTITY_PATH:-$HOME/.amcp/identity.json}"
  if [ -x "$SCRIPT_DIR/link-identity.sh" ] && [ -f "$identity_path" ]; then
    log_info "Linking AMCP identity to Solvr..."
    "$SCRIPT_DIR/link-identity.sh" --quiet || log_warn "Identity linking deferred — run: proactive-amcp link-identity"
  fi

  [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "[${AGENT_NAME}] Solvr child registered: $child_name" || true

  # Step 6: Show claim URL
  local claim_url="https://solvr.dev/agents/me/claim"
  if [ -x "$SCRIPT_DIR/config.sh" ]; then
    "$SCRIPT_DIR/config.sh" set solvr.claimUrl "$claim_url" 2>/dev/null || true
  fi

  echo ""
  echo "  Registered as: $child_name"
  echo ""
  echo "  To link this agent to your human account:"
  echo "    -> $claim_url"
  echo ""
  echo "  Claiming is optional but gives you control over"
  echo "  agent settings, reputation, and activity visibility."
  echo ""

  # Output for scripting
  cat <<EOF
{"registered": true, "child_name": "$child_name", "parent_name": "$parent_name", "claim_url": "$claim_url"}
EOF

  echo ""
  echo "CHILD_SOLVR_NAME=$child_name"
  echo "CHILD_API_KEY=$child_api_key"
  echo "PARENT_SOLVR_NAME=$parent_name"
}

main "$@"
