#!/usr/bin/env bash
# Shared security functions for training-manager scripts.
# Source this file: source "$(dirname "$0")/lib/security.sh"

# =============================================================================
# RATE LIMITING
# =============================================================================
# Uses a lockfile with timestamps to enforce max writes per window.
# Default: 10 writes per 60 seconds. Override with RATE_LIMIT_MAX and
# RATE_LIMIT_WINDOW_SECS environment variables.

RATE_LIMIT_MAX="${RATE_LIMIT_MAX:-10}"
RATE_LIMIT_WINDOW_SECS="${RATE_LIMIT_WINDOW_SECS:-60}"
RATE_LIMIT_DIR="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}/.rate-limit"

check_rate_limit() {
  local caller="${1:-write}"
  mkdir -p "$RATE_LIMIT_DIR"

  local lock_file="$RATE_LIMIT_DIR/${caller}.log"
  local now
  now=$(date +%s)
  local cutoff=$((now - RATE_LIMIT_WINDOW_SECS))

  # Create log file if it doesn't exist
  touch "$lock_file"

  # Prune entries older than the window
  local tmp_file="${lock_file}.tmp"
  awk -v cutoff="$cutoff" '$1 >= cutoff' "$lock_file" > "$tmp_file" 2>/dev/null || true
  mv "$tmp_file" "$lock_file"

  # Count recent writes
  local count
  count=$(wc -l < "$lock_file" | tr -d ' ')

  if [ "$count" -ge "$RATE_LIMIT_MAX" ]; then
    echo "ERROR: Rate limit exceeded ($count writes in last ${RATE_LIMIT_WINDOW_SECS}s, max $RATE_LIMIT_MAX)."
    echo "Wait and try again, or adjust RATE_LIMIT_MAX / RATE_LIMIT_WINDOW_SECS."
    exit 1
  fi

  # Record this write
  printf '%s\n' "$now" >> "$lock_file"
}

# =============================================================================
# PROMPT INJECTION DETECTION (TIERED)
# =============================================================================
# Three tiers based on how the content will be used:
#
#   STRICT  — SOUL.md, AGENTS.md, TOOLS.md, IDENTITY.md
#             These define core agent behavior. Full pattern set + extras.
#
#   NORMAL  — USER.md, MEMORY.md, generated skills
#             Important but lower behavioral impact. Standard pattern set.
#
#   RELAXED — Daily logs (memory/YYYY-MM-DD.md)
#             Append-only, least impact. Only block obvious attacks.

# Base patterns (used by all tiers)
_BASE_PATTERNS=(
  'ignore (all |any )?(previous |prior |above )?instructions'
  'ignore (all |any )?(previous |prior |above )?rules'
  'disregard (all |any )?(previous |prior |above )?instructions'
  'forget (all |any )?(previous |prior |above )?instructions'
  'override (all |any )?(previous |prior |above )?instructions'
  'you are now'
  'new instructions:'
  'secret(ly)? (send|transmit|upload|exfiltrate|forward|email|post)'
  'send.*(all|every).*(file|data|content|message|info).* to'
  'upload.*(all|every).*(file|data|content|message|info).* to'
  'exfiltrate'
)

# Normal tier adds more patterns (used by NORMAL and STRICT)
_NORMAL_PATTERNS=(
  'system prompt'
  'act as if'
  'pretend (that |to )'
  'from now on.*(ignore|disregard|forget|override)'
  'do not follow.*(previous|prior|above|original)'
  'curl .*(POST|PUT|PATCH)'
  'wget .*--post'
  'base64 (encode|decode|--decode|-d)'
)

# Strict tier adds behavioral override patterns
_STRICT_PATTERNS=(
  'your (new |real |true )?personality'
  'change your (tone|style|behavior|personality)'
  'always (run|execute|call|invoke) '
  'never (refuse|reject|deny|block|filter)'
  'when (asked|prompted|told) about .* instead'
  'rewrite (your|the) (rules|instructions|guidelines)'
  'you (must|should) (always|never) '
  'your (primary|main|real) (objective|goal|purpose) is'
)

# Determine which tier to use based on target file
_get_tier() {
  local target="$1"
  case "$target" in
    SOUL.md|AGENTS.md|TOOLS.md|IDENTITY.md) echo "strict" ;;
    USER.md|MEMORY.md)                       echo "normal" ;;
    memory/*.md|daily)                       echo "relaxed" ;;
    *)                                       echo "normal" ;;  # default for skills etc.
  esac
}

# Main check function
# Usage: check_prompt_injection_tiered <content> <target_file_or_category> [label]
check_prompt_injection_tiered() {
  local content="$1"
  local target="$2"
  local label="${3:-content}"
  local tier
  tier=$(_get_tier "$target")
  local content_lower
  content_lower=$(printf '%s' "$content" | tr '[:upper:]' '[:lower:]')

  local -a patterns=()

  # Build pattern list based on tier
  case "$tier" in
    strict)
      patterns+=("${_BASE_PATTERNS[@]}")
      patterns+=("${_NORMAL_PATTERNS[@]}")
      patterns+=("${_STRICT_PATTERNS[@]}")
      ;;
    normal)
      patterns+=("${_BASE_PATTERNS[@]}")
      patterns+=("${_NORMAL_PATTERNS[@]}")
      ;;
    relaxed)
      patterns+=("${_BASE_PATTERNS[@]}")
      ;;
  esac

  for pattern in "${patterns[@]}"; do
    if printf '%s' "$content_lower" | grep -qEi "$pattern"; then
      printf 'ERROR: %s rejected — matches prompt injection pattern (tier: %s).\n' "$label" "$tier"
      printf 'Blocked pattern: %s\n' "$pattern"
      echo ""
      echo "If this is legitimate content, edit the target file manually."
      echo "This filter protects against instructions being injected into"
      echo "the agent's behavioral rules."
      exit 1
    fi
  done
}

# Legacy wrapper for scripts that use the old function name
# Usage: check_prompt_injection <content> [label]  (assumes "normal" tier)
check_prompt_injection() {
  local content="$1"
  local label="${2:-content}"
  check_prompt_injection_tiered "$content" "MEMORY.md" "$label"
}

# =============================================================================
# SHELL METACHARACTER VALIDATION
# =============================================================================
validate_shell_safety() {
  local label="$1"
  local input="$2"
  if printf '%s' "$input" | grep -qE '`|\$\('; then
    printf 'ERROR: %s contains shell metacharacters (` or $()). Refusing to proceed.\n' "$label"
    echo "Remove backticks and command substitutions, then retry."
    exit 1
  fi
}
