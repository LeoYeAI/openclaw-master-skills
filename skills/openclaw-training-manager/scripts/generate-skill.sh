#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"

# Source shared security library
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib/security.sh"

NAME="${1:?Usage: generate-skill.sh <name> <description> <instructions> [requires_bins] [requires_env]}"
DESCRIPTION="${2:?Missing description}"
INSTRUCTIONS="${3:?Missing instructions}"
REQUIRES_BINS="${4:-}"
REQUIRES_ENV="${5:-}"

# --- Rate limit ---
check_rate_limit "generate-skill"

# --- Input validation ---
validate_shell_safety "name" "$NAME"
validate_shell_safety "description" "$DESCRIPTION"
validate_shell_safety "instructions" "$INSTRUCTIONS"
validate_shell_safety "requires_bins" "$REQUIRES_BINS"
validate_shell_safety "requires_env" "$REQUIRES_ENV"

# Check high-risk fields for prompt injection (normal tier — generated skills)
check_prompt_injection_tiered "$DESCRIPTION" "MEMORY.md" "description"
check_prompt_injection_tiered "$INSTRUCTIONS" "MEMORY.md" "instructions"

# Validate requires_bins and requires_env: only allow alphanumeric, hyphens, underscores, commas
if [ -n "$REQUIRES_BINS" ]; then
  if printf '%s' "$REQUIRES_BINS" | grep -qE '[^a-zA-Z0-9_,.-]'; then
    echo "ERROR: requires_bins contains invalid characters. Only alphanumeric, hyphens, underscores, dots, and commas allowed."
    exit 1
  fi
fi

if [ -n "$REQUIRES_ENV" ]; then
  if printf '%s' "$REQUIRES_ENV" | grep -qE '[^a-zA-Z0-9_,]'; then
    echo "ERROR: requires_env contains invalid characters. Only alphanumeric, underscores, and commas allowed."
    exit 1
  fi
fi

# Sanitize skill name: lowercase, hyphens only
SLUG=$(printf '%s' "$NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//')

if [ -z "$SLUG" ]; then
  echo "ERROR: Name sanitized to empty string. Use alphanumeric characters."
  exit 1
fi

SKILL_DIR="$WORKSPACE/skills/$SLUG"

if [ -d "$SKILL_DIR" ]; then
  echo "ERROR: Skill directory already exists: $SKILL_DIR"
  echo "Remove it first or choose a different name."
  exit 1
fi

mkdir -p "$SKILL_DIR"

# Build metadata JSON
# Uses jq when available for robust JSON construction.
# Falls back to string concatenation for environments without jq.
METADATA=""

if [ -n "$REQUIRES_BINS" ] || [ -n "$REQUIRES_ENV" ]; then
  if command -v jq &>/dev/null; then
    # --- jq path: proper JSON encoding ---
    REQUIRES_OBJ="{}"
    if [ -n "$REQUIRES_BINS" ]; then
      REQUIRES_OBJ=$(printf '%s' "$REQUIRES_OBJ" | jq --arg bins "$REQUIRES_BINS" '.bins = ($bins | split(","))')
    fi
    if [ -n "$REQUIRES_ENV" ]; then
      REQUIRES_OBJ=$(printf '%s' "$REQUIRES_OBJ" | jq --arg env "$REQUIRES_ENV" '.env = ($env | split(","))')
    fi
    METADATA_JSON=$(printf '%s' "$REQUIRES_OBJ" | jq -c '{openclaw: {requires: .}}')
    METADATA="metadata: $METADATA_JSON"
  else
    # --- Fallback: string concatenation ---
    # Safe here because requires_bins/requires_env are validated above
    # to contain only [a-zA-Z0-9_,.-] characters.
    REQUIRES_PARTS=()
    if [ -n "$REQUIRES_BINS" ]; then
      BINS_JSON=$(printf '%s' "$REQUIRES_BINS" | sed 's/,/","/g')
      REQUIRES_PARTS+=("\"bins\":[\"$BINS_JSON\"]")
    fi
    if [ -n "$REQUIRES_ENV" ]; then
      ENV_JSON=$(printf '%s' "$REQUIRES_ENV" | sed 's/,/","/g')
      REQUIRES_PARTS+=("\"env\":[\"$ENV_JSON\"]")
    fi
    if [ ${#REQUIRES_PARTS[@]} -gt 0 ]; then
      REQUIRES_JOINED=$(IFS=,; printf '%s' "${REQUIRES_PARTS[*]}")
      METADATA="metadata: {\"openclaw\":{\"requires\":{$REQUIRES_JOINED}}}"
    fi
  fi
fi

# Write SKILL.md using printf to avoid echo expansion issues
{
  printf '%s\n' "---"
  printf 'name: %s\n' "$SLUG"
  printf 'description: %s\n' "$DESCRIPTION"
  if [ -n "$METADATA" ]; then
    printf '%s\n' "$METADATA"
  fi
  printf '%s\n' "---"
  printf '\n'
  printf '# %s\n' "$NAME"
  printf '\n'
  printf '%s\n' "$INSTRUCTIONS"
} > "$SKILL_DIR/SKILL.md"

echo "=== Skill Generated ==="
printf '  Directory: %s\n' "$SKILL_DIR"
printf '  File: %s/SKILL.md\n' "$SKILL_DIR"
echo ""
echo "--- Content ---"
cat "$SKILL_DIR/SKILL.md"
echo ""
echo "--- End ---"
echo ""
printf 'Review the skill above. Install with: cp -r %s ~/.openclaw/workspace/skills/\n' "$SKILL_DIR"
