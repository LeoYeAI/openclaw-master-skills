#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
TODAY=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%H:%M:%S)

# Source shared security library
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib/security.sh"

CATEGORY="${1:?Usage: log-training.sh <category> <content>  (categories: agents, soul, user, memory, daily, consolidate)}"

# Validate category is one of the allowed values
validate_category() {
  case "$1" in
    agents|soul|user|memory|daily|consolidate) return 0 ;;
    *)
      echo "ERROR: Unknown category '$1'"
      echo "Valid categories: agents, soul, user, memory, daily, consolidate"
      exit 1
      ;;
  esac
}

# Map category to target filename for tiered filtering
_category_to_target() {
  case "$1" in
    agents) echo "AGENTS.md" ;;
    soul)   echo "SOUL.md" ;;
    user)   echo "USER.md" ;;
    memory) echo "MEMORY.md" ;;
    daily)  echo "daily" ;;
    *)      echo "MEMORY.md" ;;
  esac
}

validate_category "$CATEGORY"

# --- Consolidate command: merge Training Update sections into main body ---
if [ "$CATEGORY" = "consolidate" ]; then
  TARGET_FILE="${2:-}"
  if [ -z "$TARGET_FILE" ]; then
    echo "Usage: log-training.sh consolidate <filename>"
    echo "Example: log-training.sh consolidate AGENTS.md"
    echo ""
    echo "Files with Training Update sections:"
    for f in SOUL.md AGENTS.md USER.md; do
      path="$WORKSPACE/$f"
      if [ -f "$path" ]; then
        count=$(grep -c '## Training Update' "$path" 2>/dev/null || true)
        if [ "$count" -gt 0 ]; then
          printf '  %s: %d update(s)\n' "$f" "$count"
        fi
      fi
    done
    exit 0
  fi

  # Validate TARGET_FILE: must be a simple filename, no path traversal
  if printf '%s' "$TARGET_FILE" | grep -qE '/|\\|\.\.'; then
    echo "ERROR: Invalid filename '$TARGET_FILE'. Must be a simple filename (e.g. AGENTS.md), no paths."
    exit 1
  fi

  # Whitelist: only allow known workspace files
  case "$TARGET_FILE" in
    SOUL.md|AGENTS.md|USER.md|TOOLS.md|IDENTITY.md|MEMORY.md) ;;
    *)
      echo "ERROR: Consolidation only works on workspace bootstrap files."
      echo "Allowed: SOUL.md, AGENTS.md, USER.md, TOOLS.md, IDENTITY.md, MEMORY.md"
      exit 1
      ;;
  esac

  FULL_PATH="$WORKSPACE/$TARGET_FILE"
  if [ ! -f "$FULL_PATH" ]; then
    echo "ERROR: $FULL_PATH does not exist."
    exit 1
  fi

  count=$(grep -c '## Training Update' "$FULL_PATH" 2>/dev/null || true)
  if [ "$count" -eq 0 ]; then
    echo "No Training Update sections found in $TARGET_FILE. Nothing to consolidate."
    exit 0
  fi

  # Extract all training update content into a staging file
  STAGING="$WORKSPACE/.training-consolidate-staging.md"
  printf '# Pending Consolidation from %s\n' "$TARGET_FILE" > "$STAGING"
  printf '# %d Training Update section(s) extracted on %s %s\n' "$count" "$TODAY" "$TIMESTAMP" >> "$STAGING"
  printf '# Review these items and merge them into the main sections of %s,\n' "$TARGET_FILE" >> "$STAGING"
  printf '# then delete this staging file.\n\n' >> "$STAGING"

  # Extract lines within "## Training Update" sections (inclusive)
  # Stop at ANY heading that isn't a Training Update; check stop before print
  awk '/^## Training Update/{found=1} /^## / && !/^## Training Update/{if(found){found=0; next}} found{print}' "$FULL_PATH" >> "$STAGING"

  # Remove Training Update sections from the original file
  # Same heading pattern: stop at any ## that isn't "## Training Update"
  awk '
    /^## Training Update/ { skip=1; next }
    skip && /^## / && !/^## Training Update/ { skip=0 }
    skip && /^---$/ { skip=0 }
    !skip { print }
  ' "$FULL_PATH" > "${FULL_PATH}.tmp"
  mv "${FULL_PATH}.tmp" "$FULL_PATH"

  # Remove trailing blank lines from original
  sed -i.bak -e :a -e '/^\n*$/{$d;N;ba' -e '}' "$FULL_PATH" 2>/dev/null || true
  rm -f "${FULL_PATH}.bak"

  echo "=== Consolidation ==="
  printf '  Extracted %d Training Update section(s) from %s\n' "$count" "$TARGET_FILE"
  printf '  Staging file: %s\n' "$STAGING"
  echo ""
  echo "Next steps:"
  printf '  1. Review %s\n' "$STAGING"
  printf '  2. Merge the items into the appropriate sections of %s\n' "$TARGET_FILE"
  printf '  3. Delete the staging file: rm %s\n' "$STAGING"
  exit 0
fi

# --- Normal logging ---
CONTENT="${2:?Missing content to log}"

# Rate limit
check_rate_limit "log-training"

# Validate content: shell safety + tiered prompt injection
TARGET_FILE=$(_category_to_target "$CATEGORY")
validate_shell_safety "content" "$CONTENT"
check_prompt_injection_tiered "$CONTENT" "$TARGET_FILE" "content"

case "$CATEGORY" in
  agents)
    TARGET="$WORKSPACE/AGENTS.md"
    if [ ! -f "$TARGET" ]; then
      echo "ERROR: $TARGET does not exist. Run scaffold first."
      exit 1
    fi
    printf '\n## Training Update (%s %s)\n' "$TODAY" "$TIMESTAMP" >> "$TARGET"
    printf -- '- %s\n' "$CONTENT" >> "$TARGET"
    echo "Appended to AGENTS.md"
    ;;

  soul)
    TARGET="$WORKSPACE/SOUL.md"
    if [ ! -f "$TARGET" ]; then
      echo "ERROR: $TARGET does not exist. Run scaffold first."
      exit 1
    fi
    printf '\n## Training Update (%s %s)\n' "$TODAY" "$TIMESTAMP" >> "$TARGET"
    printf -- '- %s\n' "$CONTENT" >> "$TARGET"
    echo "Appended to SOUL.md"
    ;;

  user)
    TARGET="$WORKSPACE/USER.md"
    if [ ! -f "$TARGET" ]; then
      echo "ERROR: $TARGET does not exist. Run scaffold first."
      exit 1
    fi
    printf '\n## Training Update (%s %s)\n' "$TODAY" "$TIMESTAMP" >> "$TARGET"
    printf -- '- %s\n' "$CONTENT" >> "$TARGET"
    echo "Appended to USER.md"
    ;;

  memory)
    TARGET="$WORKSPACE/MEMORY.md"
    if [ ! -f "$TARGET" ]; then
      echo "ERROR: $TARGET does not exist. Run scaffold first."
      exit 1
    fi
    printf '\n### %s %s\n' "$TODAY" "$TIMESTAMP" >> "$TARGET"
    printf -- '- %s\n' "$CONTENT" >> "$TARGET"
    echo "Appended to MEMORY.md"
    ;;

  daily)
    mkdir -p "$WORKSPACE/memory"
    TARGET="$WORKSPACE/memory/$TODAY.md"
    if [ ! -f "$TARGET" ]; then
      printf '# Daily Log: %s\n\n' "$TODAY" > "$TARGET"
    fi
    printf '## %s\n' "$TIMESTAMP" >> "$TARGET"
    printf -- '- %s\n\n' "$CONTENT" >> "$TARGET"
    echo "Appended to memory/$TODAY.md"
    ;;
esac

echo ""
echo "=== Logged ==="
printf '  Category: %s\n' "$CATEGORY"
printf '  Target: %s\n' "$TARGET"
printf '  Content: %s\n' "$CONTENT"
