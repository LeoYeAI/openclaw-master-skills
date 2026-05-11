#!/usr/bin/env bash
# Shared environment checks for ListenHub scripts
# Source this at the beginning of each script

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
VERSION_FILE="${SKILL_DIR}/VERSION"
REMOTE_VERSION_URL="https://raw.githubusercontent.com/marswaveai/skills/main/skills/listenhub/VERSION"

# === Version Check (non-blocking) ===

check_version() {
  # Skip if no local VERSION file
  [ -f "$VERSION_FILE" ] || return 0

  local local_ver remote_ver http_code response
  local_ver=$(cat "$VERSION_FILE" 2>/dev/null | tr -d '[:space:]')

  # Validate local version before integer comparisons
  [[ "$local_ver" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || return 0

  # Fetch remote version with 5s timeout, check HTTP status
  response=$(curl -sS --max-time 5 -w "\n%{http_code}" "$REMOTE_VERSION_URL" 2>/dev/null) || return 0
  http_code=$(echo "$response" | tail -1)
  remote_ver=$(echo "$response" | head -1 | tr -d '[:space:]')

  # Only compare if HTTP 200 and valid semver-like format
  [[ "$http_code" == "200" && "$remote_ver" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || return 0

  # Same version, skip
  [ "$local_ver" != "$remote_ver" ] || return 0

  # Parse semver: major.minor.patch
  local local_major local_minor local_patch
  local remote_major remote_minor remote_patch

  IFS='.' read -r local_major local_minor local_patch <<< "$local_ver"
  IFS='.' read -r remote_major remote_minor remote_patch <<< "$remote_ver"

  # Notify if remote version is newer (major/minor bump or patch bump)
  if [ "$remote_major" -gt "$local_major" ] || \
     { [ "$remote_major" -eq "$local_major" ] && [ "$remote_minor" -gt "$local_minor" ]; } || \
     { [ "$remote_major" -eq "$local_major" ] && [ "$remote_minor" -eq "$local_minor" ] && [ "$remote_patch" -gt "$local_patch" ]; }; then
    echo "┌─────────────────────────────────────────────────────┐" >&2
    echo "│  Update available: $local_ver → $remote_ver" >&2
    echo "│  Run: npx skills add marswaveai/skills             │" >&2
    echo "└─────────────────────────────────────────────────────┘" >&2
  fi
}

# Run version check (notify-only, no auto-update)
# Set LISTENHUB_SKIP_VERSION_CHECK=1 to disable
if [ "${LISTENHUB_SKIP_VERSION_CHECK:-}" != "1" ]; then
  check_version
fi

# Load API key from shell config (try multiple sources)
# Extract value safely without eval to prevent code injection
if [ -n "${LISTENHUB_API_KEY:-}" ]; then
  : # Already set, skip loading
else
  _extract_api_key() {
    local file="$1"
    [ -f "$file" ] || return 1
    # Match: export LISTENHUB_API_KEY="value" or export LISTENHUB_API_KEY='value' or unquoted
    local line
    line=$(grep -m1 '^[[:space:]]*export[[:space:]]\{1,\}LISTENHUB_API_KEY=' "$file" 2>/dev/null) || return 1
    # Strip everything up to and including the first =
    local value="${line#*=}"
    # Extract based on quoting style
    case "$value" in
      \"*)
        # Double-quoted: extract between first and last double quote
        value="${value#\"}"
        value="${value%\"*}"
        ;;
      \'*)
        # Single-quoted: extract between first and last single quote
        value="${value#\'}"
        value="${value%\'*}"
        ;;
      *)
        # Unquoted: strip trailing comments and whitespace
        value="${value%%#*}"
        value="${value%"${value##*[![:space:]]}"}"
        ;;
    esac
    [ -n "$value" ] && printf '%s' "$value"
  }
  _key=$(_extract_api_key ~/.zshrc) || _key=$(_extract_api_key ~/.bashrc) || _key=""
  if [ -n "$_key" ]; then
    export LISTENHUB_API_KEY="$_key"
  fi
  unset -f _extract_api_key
  unset _key
fi

# === Environment Checks ===

check_curl() {
  if ! command -v curl &>/dev/null; then
    echo "Error: curl not found (should be pre-installed on most systems)" >&2
    exit 127
  fi
}

check_jq() {
  if ! command -v jq &>/dev/null; then
    cat >&2 <<'EOF'
Error: jq not found

Install:
  macOS (Homebrew): brew install jq
  Ubuntu/Debian: apt-get install jq
  RHEL/CentOS: yum install jq
  Fedora: dnf install jq
  Arch: pacman -S jq
EOF
    exit 127
  fi
}

check_api_key() {
  if [ -z "${LISTENHUB_API_KEY:-}" ]; then
    cat >&2 <<'EOF'
Error: LISTENHUB_API_KEY not set

Setup:
  1. Get API key from https://listenhub.ai/settings/api-keys
  2. Add to ~/.zshrc or ~/.bashrc:
     export LISTENHUB_API_KEY="lh_sk_..."
  3. Run: source ~/.zshrc
EOF
    exit 1
  fi
}

# Run checks
check_curl
check_api_key

# === Input Validation ===

# Validate that an ID contains only safe characters (alphanumeric, hyphen, underscore)
# Usage: validate_id "value" "field_name"
validate_id() {
  local value="$1"
  local name="${2:-id}"
  if [[ ! "$value" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    echo "Error: Invalid $name (only alphanumeric, hyphen, underscore allowed): $value" >&2
    exit 1
  fi
}

# === API Helpers ===

API_BASE="https://api.marswave.ai/openapi/v1"
AGENT_SKILLS_CLIENT_ID="PJBkELS1o_q9nJ~NzF2_Fmr21TNX&~eoJR49FFdFhD3U"

# Trim leading and trailing whitespace
trim_ws() {
  local input="$1"
  input="${input#"${input%%[![:space:]]*}"}"
  input="${input%"${input##*[![:space:]]}"}"
  printf '%s' "$input"
}

# Make authenticated POST request with JSON body
# Usage: api_post "endpoint" 'json_body'
api_post() {
  local endpoint="$1"
  local body="$2"

  curl -sS -X POST "${API_BASE}/${endpoint}" \
    -H "Authorization: Bearer ${LISTENHUB_API_KEY}" \
    -H "Content-Type: application/json" \
    -H "x-marswave-client-id: ${AGENT_SKILLS_CLIENT_ID}" \
    -d "$body"
}

# Make authenticated GET request
# Usage: api_get "endpoint"
api_get() {
  local endpoint="$1"

  curl -sS -X GET "${API_BASE}/${endpoint}" \
    -H "Authorization: Bearer ${LISTENHUB_API_KEY}" \
    -H "x-marswave-client-id: ${AGENT_SKILLS_CLIENT_ID}"
}
