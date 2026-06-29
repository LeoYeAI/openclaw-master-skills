#!/bin/bash
# groq-status.sh - Groq key distribution via Solvr + usage/status reporting
#
# Usage:
#   groq-status.sh status         Show usage, limits, source
#   groq-status.sh request-key    Request Groq key from Solvr (free tier)
#
# Config keys (in ~/.amcp/config.json):
#   groq.apiKey    - Groq API key
#   groq.source    - Where the key came from: "solvr" or "manual"
#   groq.model     - Model name (default: openai/gpt-oss-20b)
#   solvr.apiKey   - Solvr API key (needed for request-key)
#
# Environment:
#   CONFIG_FILE    Override config path (default: ~/.amcp/config.json)
#   GROQ_API_KEY   Override Groq API key from config
#   SOLVR_API_KEY  Override Solvr API key from config

set -euo pipefail

command -v curl &>/dev/null || { echo "FATAL: curl required but not found" >&2; exit 2; }
command -v python3 &>/dev/null || { echo "FATAL: python3 required but not found" >&2; exit 2; }

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0" 2>/dev/null || realpath "$0" 2>/dev/null || echo "$0")")" && pwd)"
CONFIG_FILE="${CONFIG_FILE:-$HOME/.amcp/config.json}"
GROQ_USAGE_FILE="${GROQ_USAGE_FILE:-$HOME/.amcp/groq-usage.json}"
SOLVR_API_URL="${SOLVR_API_URL:-https://api.solvr.dev/v1}"

# ============================================================
# Helpers
# ============================================================

log_info()  { echo "[groq] INFO:  $*"; }
log_ok()    { echo "[groq] OK:    $*"; }
log_warn()  { echo "[groq] WARN:  $*" >&2; }
log_error() { echo "[groq] ERROR: $*" >&2; }

usage() {
  cat <<EOF
proactive-amcp groq — Groq intelligence management

Usage: $(basename "$0") <command>

Commands:
  status         Show Groq usage, limits, and key source
  request-key    Request a free Groq API key from Solvr

Options:
  --json         Output as JSON (status only)
  -h, --help     Show this help

Key Sources:
  solvr     Free tier from Solvr (rate-limited, e.g. 10k tokens/day)
  manual    Your own key from console.groq.com (full access)

Upgrade:
  Want more? Get your own Groq key at https://console.groq.com
  Then: proactive-amcp config set groq.apiKey YOUR_KEY
  This will override the Solvr-provided key with full access.
EOF
  exit 0
}

# Read a dot-path key from config.json
read_config_key() {
  local key="$1"
  local cfg_path="$CONFIG_FILE"
  python3 -c "
import json, os, functools, operator
try:
    with open(os.path.expanduser('$cfg_path')) as f:
        cfg = json.load(f)
    keys = '$key'.split('.')
    val = functools.reduce(operator.getitem, keys, cfg)
    print(val)
except (KeyError, TypeError, IOError, json.JSONDecodeError):
    pass
" 2>/dev/null || true
}

# Write a dot-path key to config.json (reuse config.sh pattern)
write_config_key() {
  local key="$1"
  local value="$2"
  "$SCRIPT_DIR/config.sh" set "$key" "$value" >/dev/null 2>&1
}

# Get Solvr API key from env or config
get_solvr_api_key() {
  local key="${SOLVR_API_KEY:-}"
  [ -n "$key" ] && { echo "$key"; return; }
  key=$(read_config_key "solvr.apiKey")
  [ -n "$key" ] && { echo "$key"; return; }
  key=$(read_config_key "pinning.solvr.apiKey")
  [ -n "$key" ] && { echo "$key"; return; }
  return 1
}

# Get Groq API key from env or config
get_groq_api_key() {
  local key="${GROQ_API_KEY:-}"
  [ -n "$key" ] && { echo "$key"; return; }
  key=$(read_config_key "groq.apiKey")
  [ -n "$key" ] && { echo "$key"; return; }
  return 1
}

# Get Solvr agent ID from /v1/me
get_solvr_agent_id() {
  local solvr_key="$1"
  local response
  response=$(curl -s --max-time 15 \
    -H "Authorization: Bearer $solvr_key" \
    "$SOLVR_API_URL/me" 2>/dev/null || echo "")

  if [ -z "$response" ]; then
    return 1
  fi

  python3 -c "
import json, sys
try:
    data = json.loads('''$response''')
    agent_id = data.get('id', data.get('agent_id', ''))
    if agent_id:
        print(agent_id)
    else:
        sys.exit(1)
except (json.JSONDecodeError, KeyError):
    sys.exit(1)
" 2>/dev/null
}

# ============================================================
# groq request-key — Request Groq key from Solvr
# ============================================================

do_request_key() {
  log_info "Requesting Groq API key from Solvr (free tier)..."

  # Check if we already have a Groq key
  local existing_key
  existing_key=$(get_groq_api_key 2>/dev/null || echo "")
  local existing_source
  existing_source=$(read_config_key "groq.source")

  if [ -n "$existing_key" ]; then
    if [ "$existing_source" = "manual" ]; then
      log_warn "You already have a manually-configured Groq key"
      log_warn "A Solvr key would be rate-limited. Keep your manual key for full access."
      echo ""
      echo "Current key source: manual (full access)"
      echo "To switch to Solvr free tier: proactive-amcp config set groq.source solvr"
      exit 0
    elif [ "$existing_source" = "solvr" ]; then
      log_info "You already have a Solvr-provided Groq key"
      echo ""
      echo "Current key source: solvr (free tier)"
      echo "To refresh: delete current key first with: proactive-amcp config set groq.apiKey \"\""
      exit 0
    fi
  fi

  # Get Solvr API key
  local solvr_key
  solvr_key=$(get_solvr_api_key) || {
    log_error "No Solvr API key found"
    echo "" >&2
    echo "Register with Solvr first:" >&2
    echo "  proactive-amcp config set solvr.apiKey YOUR_SOLVR_KEY" >&2
    echo "  or: proactive-amcp solvr-register" >&2
    exit 1
  }

  # Get agent ID from Solvr
  local agent_id
  agent_id=$(get_solvr_agent_id "$solvr_key") || {
    log_error "Could not retrieve agent ID from Solvr (check solvr.apiKey)"
    exit 1
  }

  log_info "Agent ID: $agent_id"
  log_info "Requesting Groq integration..."

  # POST /v1/agents/{id}/integrations/groq
  local response http_code body
  response=$(curl -s -w "\n%{http_code}" --max-time 30 \
    -X POST \
    -H "Authorization: Bearer $solvr_key" \
    -H "Content-Type: application/json" \
    "$SOLVR_API_URL/agents/$agent_id/integrations/groq" 2>/dev/null || echo -e "\n000")

  body=$(echo "$response" | head -n -1)
  http_code=$(echo "$response" | tail -1)

  case "$http_code" in
    200|201)
      # Parse the returned key
      local groq_key
      groq_key=$(python3 -c "
import json, sys
try:
    data = json.loads(sys.stdin.read())
    key = data.get('api_key', data.get('apiKey', data.get('key', data.get('groq_api_key', ''))))
    if key:
        print(key)
    else:
        sys.exit(1)
except (json.JSONDecodeError, KeyError):
    sys.exit(1)
" <<< "$body" 2>/dev/null) || {
        log_error "Solvr returned success but response did not contain a Groq key"
        log_error "Response: $body"
        exit 1
      }

      # Store key and source in config
      write_config_key "groq.apiKey" "$groq_key"
      write_config_key "groq.source" "solvr"

      log_ok "Groq API key obtained from Solvr (free tier)"
      echo ""
      echo "Key stored in: $CONFIG_FILE"
      echo "Source: solvr (rate-limited free tier)"
      echo ""
      echo "Usage limits enforced by Solvr (e.g., 10k tokens/day)."
      echo "Want more? Get your own Groq key at: https://console.groq.com"
      echo "Then: proactive-amcp config set groq.apiKey YOUR_KEY"
      ;;
    401|403)
      log_error "Solvr rejected the request (auth failed)"
      log_error "Check your Solvr API key: proactive-amcp config get solvr.apiKey"
      exit 1
      ;;
    404)
      log_error "Groq integration not available for this agent"
      log_error "This may mean the Solvr Groq integration is not yet enabled for your account."
      echo "" >&2
      echo "Alternative: Get your own Groq key at https://console.groq.com" >&2
      echo "Then: proactive-amcp config set groq.apiKey YOUR_KEY" >&2
      exit 1
      ;;
    429)
      log_error "Rate limited by Solvr — try again later"
      exit 1
      ;;
    000)
      log_error "Could not reach Solvr API at $SOLVR_API_URL"
      echo "" >&2
      echo "Alternative: Get your own Groq key at https://console.groq.com" >&2
      echo "Then: proactive-amcp config set groq.apiKey YOUR_KEY" >&2
      exit 1
      ;;
    *)
      log_error "Unexpected response from Solvr (HTTP $http_code)"
      [ -n "$body" ] && log_error "Body: $body"
      exit 1
      ;;
  esac
}

# ============================================================
# groq status — Show usage, limits, source
# ============================================================

do_status() {
  local json_output=false
  [ "${1:-}" = "--json" ] && json_output=true

  local groq_key
  groq_key=$(get_groq_api_key 2>/dev/null || echo "")
  local source
  source=$(read_config_key "groq.source")
  local model
  model=$(read_config_key "groq.model")
  model="${model:-openai/gpt-oss-20b}"

  if $json_output; then
    do_status_json "$groq_key" "$source" "$model"
  else
    do_status_text "$groq_key" "$source" "$model"
  fi
}

do_status_json() {
  local groq_key="$1"
  local source="$2"
  local model="$3"

  python3 << PYEOF
import json, os

config = {
    "configured": bool("$groq_key"),
    "source": "$source" if "$source" else None,
    "model": "$model",
}

# Load usage data
usage_file = os.path.expanduser("$GROQ_USAGE_FILE")
try:
    with open(usage_file) as f:
        usage = json.load(f)
except (IOError, json.JSONDecodeError):
    usage = {}

config["usage"] = {
    "total_tokens": usage.get("total_tokens", 0),
    "total_prompt_tokens": usage.get("total_prompt_tokens", 0),
    "total_completion_tokens": usage.get("total_completion_tokens", 0),
    "evaluations": usage.get("evaluations", 0),
    "last_used": usage.get("last_used", None),
    "last_model": usage.get("last_model", None),
}

# Rate limit info for solvr-sourced keys
if "$source" == "solvr":
    config["limits"] = {
        "source": "solvr",
        "note": "Rate limits enforced by Solvr (e.g., 10k tokens/day free tier)",
        "upgrade": "Get your own key at https://console.groq.com for unlimited access"
    }

print(json.dumps(config, indent=2))
PYEOF
}

do_status_text() {
  local groq_key="$1"
  local source="$2"
  local model="$3"

  echo "=== Groq Intelligence Status ==="
  echo ""

  if [ -z "$groq_key" ]; then
    echo "  Status:  NOT CONFIGURED"
    echo ""
    echo "  To enable Groq intelligence:"
    echo "    Option A (free): proactive-amcp groq request-key  (requires Solvr account)"
    echo "    Option B (full): proactive-amcp config set groq.apiKey YOUR_KEY"
    echo "                     Get a key at: https://console.groq.com"
    return 0
  fi

  echo "  Status:  CONFIGURED"
  echo "  Source:  ${source:-unknown}"
  echo "  Model:   $model"

  # Show key info (redacted)
  local key_display
  if [ ${#groq_key} -gt 12 ]; then
    key_display="${groq_key:0:4}...${groq_key: -4}"
  else
    key_display="****"
  fi
  echo "  API Key: $key_display"
  echo ""

  # Rate limits for solvr-sourced keys
  if [ "$source" = "solvr" ]; then
    echo "  Limits:  Solvr free tier (rate limits enforced by Solvr)"
    echo "  Upgrade: Want more? Get your own key at https://console.groq.com"
    echo "           Then: proactive-amcp config set groq.apiKey YOUR_KEY"
    echo ""
  elif [ "$source" = "manual" ]; then
    echo "  Limits:  Per your Groq account plan"
    echo ""
  fi

  # Show usage data if available
  if [ -f "$GROQ_USAGE_FILE" ]; then
    python3 << PYEOF
import json, os

usage_file = os.path.expanduser("$GROQ_USAGE_FILE")
try:
    with open(usage_file) as f:
        usage = json.load(f)
except (IOError, json.JSONDecodeError):
    usage = {}

total_tokens = usage.get("total_tokens", 0)
evals = usage.get("evaluations", 0)
last_used = usage.get("last_used", "never")
last_model = usage.get("last_model", "—")

print("  --- Usage ---")
print(f"  Total tokens:    {total_tokens:,}")
print(f"  Evaluations:     {evals}")
print(f"  Last used:       {last_used}")
print(f"  Last model:      {last_model}")

# Show last 5 sessions if any
sessions = usage.get("sessions", [])
if sessions:
    print(f"  Recent sessions: {len(sessions)} recorded")
PYEOF
  else
    echo "  --- Usage ---"
    echo "  No usage data yet. Run: proactive-amcp memory-prune --dry-run"
  fi
}

# ============================================================
# Main
# ============================================================

SUBCOMMAND="${1:-}"
shift || true

case "$SUBCOMMAND" in
  status)
    do_status "$@"
    ;;
  request-key)
    do_request_key "$@"
    ;;
  -h|--help|"")
    usage
    ;;
  *)
    log_error "Unknown groq command '$SUBCOMMAND'"
    echo "" >&2
    usage
    ;;
esac
