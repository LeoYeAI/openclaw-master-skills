#!/bin/bash
# config.sh - Manage ~/.amcp/config.json
# Usage:
#   config.sh set <key> <value>   Set a config value (dot-path, e.g. pinata.jwt)
#   config.sh get <key>           Get a config value (dot-path)
#   config.sh get                 Print entire config (redacted)

set -euo pipefail

command -v python3 &>/dev/null || { echo "FATAL: python3 required but not found" >&2; exit 2; }

CONFIG_FILE="${CONFIG_FILE:-$HOME/.amcp/config.json}"

usage() {
  cat <<EOF
proactive-amcp config — Manage ~/.amcp/config.json

Usage:
  config set <key> <value>   Set a config value using dot-path notation
  config get [key]           Get a config value (or print all, redacted)
  config evaluators          Manage evaluator array (list/add/remove/show)
  config backup              Create/list/restore OpenClaw config backups
  config fix                 3-tier config recovery (backup restore → doctor → minimal)

Examples:
  config set pinata.jwt eyJhbGciOi...
  config set notify.target 123456789
  config set notify.emailTo user@example.com
  config set notify.emailOnResurrect true
  config set notify.agentmailInbox inbox@agentmail.to
  config set watchdog.interval 120
  config set checkpoint.schedule "0 */4 * * *"
  config get pinata.jwt
  config get
  config backup --list
  config backup --restore
  config fix --dry-run

Config path: $CONFIG_FILE
EOF
  exit 1
}

# Ensure config directory exists
ensure_config_dir() {
  local config_dir
  config_dir="$(dirname "$CONFIG_FILE")"
  mkdir -p "$config_dir"
}

# Initialize config file if missing
ensure_config_file() {
  ensure_config_dir
  if [ ! -f "$CONFIG_FILE" ]; then
    echo "{}" > "$CONFIG_FILE"
    chmod 600 "$CONFIG_FILE"
  fi
}

# ============================================================
# config set <key> <value>
# ============================================================
config_set() {
  local key="${1:-}"
  local value="${2:-}"

  if [ -z "$key" ] || [ -z "$value" ]; then
    echo "ERROR: Usage: config set <key> <value>" >&2
    exit 1
  fi

  ensure_config_file

  # Use Python to do a safe nested JSON set with dot-path
  python3 -c "
import json, sys, os

config_path = os.path.expanduser('$CONFIG_FILE')
key = '''$key'''
value = '''$value'''

# Load existing config
with open(config_path) as f:
    data = json.load(f)

# Navigate dot-path, creating intermediate objects as needed
parts = key.split('.')
obj = data
for part in parts[:-1]:
    if part not in obj or not isinstance(obj[part], dict):
        obj[part] = {}
    obj = obj[part]

# Attempt type coercion for booleans and integers
if value.lower() == 'true':
    value = True
elif value.lower() == 'false':
    value = False
else:
    try:
        value = int(value)
    except ValueError:
        pass  # keep as string

obj[parts[-1]] = value

# Write back
with open(config_path, 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
"

  chmod 600 "$CONFIG_FILE"
  echo "Set $key in $CONFIG_FILE"

  # Post-set validation for known keys
  validate_after_set "$key" "$value"
}

# ============================================================
# Post-set validation for specific config keys
# ============================================================
validate_after_set() {
  local key="$1"
  local value="$2"

  case "$key" in
    solvr.apiKey|pinning.solvr.apiKey)
      # Validate Solvr API key format
      if ! echo "$value" | grep -qE '^solvr_|^[a-zA-Z0-9_-]{20,}$'; then
        echo "WARNING: Solvr API key format looks unusual (expected 'solvr_...' or agent key)" >&2
      fi
      # Test key validity via GET /v1/me
      local solvr_base="${SOLVR_BASE:-https://api.solvr.dev/v1}"
      local me_response
      me_response=$(curl -s --max-time 10 "$solvr_base/me" \
        -H "Authorization: Bearer $value" 2>/dev/null || echo '')
      if [ -n "$me_response" ]; then
        local name
        name=$(echo "$me_response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('name',''))" 2>/dev/null || echo '')
        if [ -n "$name" ]; then
          echo "  Solvr account verified: $name"
        else
          echo "  WARNING: Could not verify Solvr API key (GET /v1/me did not return a name)" >&2
        fi
      else
        echo "  WARNING: Could not reach Solvr API to verify key" >&2
      fi
      ;;
  esac
}

# ============================================================
# config get [key]
# ============================================================
config_get() {
  local key="${1:-}"

  if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: No config file at $CONFIG_FILE" >&2
    echo "Run: proactive-amcp init" >&2
    exit 1
  fi

  if [ -z "$key" ]; then
    # Print entire config, redacted
    python3 -c "
import json, os, re

config_path = os.path.expanduser('$CONFIG_FILE')
with open(config_path) as f:
    data = json.load(f)

SECRET_KEYS = {'jwt', 'apikey', 'api_key', 'secret', 'password', 'mnemonic', 'token', 'key'}

def redact(obj, path=''):
    if isinstance(obj, dict):
        return {k: redact(v, k) for k, v in obj.items()}
    elif isinstance(obj, str) and any(s in path.lower() for s in SECRET_KEYS):
        if len(obj) > 8:
            return obj[:4] + '...' + obj[-4:]
        elif len(obj) > 0:
            return '****'
        return obj
    return obj

print(json.dumps(redact(data), indent=2))
"
  else
    # Get specific key by dot-path
    python3 -c "
import json, os

config_path = os.path.expanduser('$CONFIG_FILE')
key = '''$key'''

with open(config_path) as f:
    data = json.load(f)

parts = key.split('.')
obj = data
for part in parts:
    if isinstance(obj, dict) and part in obj:
        obj = obj[part]
    else:
        print('')
        exit(0)

if isinstance(obj, (dict, list)):
    print(json.dumps(obj, indent=2))
else:
    print(obj)
"
  fi
}

# ============================================================
# Warn if secrets found in identity.json
# ============================================================
warn_identity_secrets() {
  local identity_path="${IDENTITY_PATH:-$HOME/.amcp/identity.json}"

  if [ ! -f "$identity_path" ]; then
    return 0
  fi

  python3 -c "
import json, os, sys

identity_path = os.path.expanduser('$identity_path')
with open(identity_path) as f:
    data = json.load(f)

SECRET_FIELDS = [
    'pinata_jwt', 'pinata_api_key', 'pinata_secret',
    'solvr_api_key', 'api_key', 'apiKey',
    'jwt', 'token', 'secret', 'password', 'mnemonic',
    'email', 'notify_target', 'notifyTarget',
]

found = []
for field in SECRET_FIELDS:
    if field in data and data[field]:
        found.append(field)

if found:
    fields = ', '.join(found)
    print(f'WARNING: Secrets found in identity.json: {fields}', file=sys.stderr)
    print(f'  Migrate with: proactive-amcp config set <key> <value>', file=sys.stderr)
    print(f'  Secrets belong in ~/.amcp/config.json, NEVER in identity.json', file=sys.stderr)
    sys.exit(2)
" 2>&1 || true
}

# ============================================================
# Main
# ============================================================

SUBCOMMAND="${1:-}"
shift || true

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0" 2>/dev/null || realpath "$0" 2>/dev/null || echo "$0")")" && pwd)"

case "$SUBCOMMAND" in
  set)
    warn_identity_secrets
    config_set "$@"
    ;;
  get)
    warn_identity_secrets
    config_get "$@"
    ;;
  evaluators)
    exec "$SCRIPT_DIR/_config-evaluators.sh" "$@"
    ;;
  backup)
    exec "$SCRIPT_DIR/_config-backup.sh" "$@"
    ;;
  fix)
    exec "$SCRIPT_DIR/_config-fix.sh" "$@"
    ;;
  -h|--help|"")
    usage
    ;;
  *)
    echo "ERROR: Unknown config command '$SUBCOMMAND'" >&2
    usage
    ;;
esac
