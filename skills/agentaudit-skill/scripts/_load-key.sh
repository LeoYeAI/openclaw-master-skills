#!/usr/bin/env bash
# _load-key.sh — Shared API key loader for all AgentAudit scripts
# Source this file: source "$SCRIPT_DIR/_load-key.sh"
#
# Lookup priority (highest to lowest):
#   1. AGENTAUDIT_API_KEY environment variable
#   2. Skill-local config: <skill-dir>/config/credentials.json
#   3. User-level config: ~/.config/agentaudit/credentials.json
#
# This ensures the key survives:
#   - Skill re-installation (user-level backup)
#   - Environment changes (file-based fallback)
#   - Container/CI environments (env var override)

load_api_key() {
  # 1. Environment variable (highest priority — for CI/CD and containers)
  if [ -n "${AGENTAUDIT_API_KEY:-}" ]; then
    echo "$AGENTAUDIT_API_KEY"
    return
  fi

  # 2. Skill-local credentials (inside the skill directory)
  local skill_cred=""
  if [ -n "${AGENTAUDIT_HOME:-}" ]; then
    skill_cred="$AGENTAUDIT_HOME/config/credentials.json"
  else
    # Derive from script location
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    skill_cred="$script_dir/../config/credentials.json"
  fi

  if [ -f "$skill_cred" ]; then
    local key
    key=$(jq -r '.api_key // empty' "$skill_cred" 2>/dev/null || true)
    if [ -n "$key" ]; then
      echo "$key"
      return
    fi
  fi

  # 3. User-level config (backup that survives reinstalls)
  local user_cred="${XDG_CONFIG_HOME:-$HOME/.config}/agentaudit/credentials.json"
  if [ -f "$user_cred" ]; then
    local key
    key=$(jq -r '.api_key // empty' "$user_cred" 2>/dev/null || true)
    if [ -n "$key" ]; then
      echo "$key"
      return
    fi
  fi

  # No key found
  echo ""
}
