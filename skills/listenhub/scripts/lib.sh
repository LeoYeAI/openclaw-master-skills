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

  # Only update if remote version is newer (not just different)
  # This prevents downgrading when local version is ahead of remote
  if [ "$remote_major" -gt "$local_major" ] || \
     { [ "$remote_major" -eq "$local_major" ] && [ "$remote_minor" -gt "$local_minor" ]; }; then
    echo "┌─────────────────────────────────────────────────────┐" >&2
    echo "│  Auto-updating: $local_ver → $remote_ver" >&2
    echo "└─────────────────────────────────────────────────────┘" >&2

    # Download and replace scripts using curl (non-interactive, no git required)
    local base_url="https://raw.githubusercontent.com/marswaveai/skills/main/skills/listenhub"
    local api_url="https://api.github.com/repos/marswaveai/skills/contents/skills/listenhub/scripts"
    local update_success=true

    # Update VERSION file
    if ! curl -fsSL --max-time 10 "$base_url/VERSION" -o "$VERSION_FILE.tmp" 2>/dev/null; then
      update_success=false
    fi

    # Fetch remote script list from GitHub API and download all scripts
    if [ "$update_success" = true ]; then
      local script_list
      script_list=$(curl -fsSL --max-time 10 "$api_url" 2>/dev/null | grep -o '"name":"[^"]*\.sh"' | cut -d'"' -f4)

      if [ -z "$script_list" ]; then
        update_success=false
      else
        for script_name in $script_list; do
          if ! curl -fsSL --max-time 10 "$base_url/scripts/$script_name" -o "$SCRIPT_DIR/$script_name.tmp" 2>/dev/null; then
            update_success=false
            break
          fi
        done
      fi
    fi

    # If all downloads succeeded, replace files atomically
    if [ "$update_success" = true ]; then
      # Move all script files first
      for script_tmp in "$SCRIPT_DIR"/*.sh.tmp; do
        [ -f "$script_tmp" ] || continue
        local script="${script_tmp%.tmp}"
        mv -f "$script_tmp" "$script" && chmod +x "$script"
      done
      # Only update VERSION after all scripts are successfully moved
      mv -f "$VERSION_FILE.tmp" "$VERSION_FILE" 2>/dev/null || true
      echo "│  ✓ Updated successfully to $remote_ver                  │" >&2
    else
      # Cleanup temp files on failure
      rm -f "$VERSION_FILE.tmp" "$SCRIPT_DIR"/*.sh.tmp 2>/dev/null || true
      echo "│  Auto-update failed. Run manually:                  │" >&2
      echo "│  npx skills add marswaveai/skills                   │" >&2
    fi
  # Patch update available (remote patch > local patch) → notify only
  elif [ "$remote_major" -eq "$local_major" ] && [ "$remote_minor" -eq "$local_minor" ] && \
       [ "$remote_patch" -gt "$local_patch" ]; then
    echo "┌─────────────────────────────────────────────────────┐" >&2
    echo "│  Patch update available: $local_ver → $remote_ver" >&2
    echo "│  Run: npx skills add marswaveai/skills             │" >&2
    echo "└─────────────────────────────────────────────────────┘" >&2
  fi
}

# Run version check (auto-update via curl if available)
check_version

# Load API key from shell config (try multiple sources)
# Note: source may fail on zsh-specific syntax, so we use || true
if [ -n "${LISTENHUB_API_KEY:-}" ]; then
  : # Already set, skip loading
elif [ -f ~/.zshrc ]; then
  # Extract just the export line to avoid zsh syntax issues
  eval "$(grep 'export LISTENHUB_API_KEY' ~/.zshrc 2>/dev/null || true)"
elif [ -f ~/.bashrc ]; then
  eval "$(grep 'export LISTENHUB_API_KEY' ~/.bashrc 2>/dev/null || true)"
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
