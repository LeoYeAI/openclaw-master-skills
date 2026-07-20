#!/usr/bin/env bash
set -euo pipefail

# Sanitized file writer for workspace bootstrap files.
# Used by interactive setup to route all writes through script-level
# sanitization rather than having the agent write files directly.
#
# Usage: write-file.sh [--force] <filename> <content>
#   filename: must be a whitelisted bootstrap file (e.g. SOUL.md, AGENTS.md)
#   content:  the full file content to write
#
# Modes:
#   Default:  refuses to overwrite an existing file
#   --force:  overwrites existing file (requires explicit flag)

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"

# Source shared security library
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib/security.sh"

FORCE=false
for arg in "$@"; do
  case "$arg" in
    --force) FORCE=true; shift ;;
  esac
done

FILENAME="${1:?Usage: write-file.sh [--force] <filename> <content>}"
CONTENT="${2:?Missing file content}"

# --- Rate limit ---
check_rate_limit "write-file"

# --- Validate filename ---
if printf '%s' "$FILENAME" | grep -qE '/|\\|\.\.'; then
  echo "ERROR: Invalid filename '$FILENAME'. Must be a simple filename, no paths."
  exit 1
fi

# Whitelist: only known workspace bootstrap files
case "$FILENAME" in
  SOUL.md|AGENTS.md|USER.md|TOOLS.md|IDENTITY.md|MEMORY.md) ;;
  *)
    echo "ERROR: Only bootstrap files can be written through this script."
    echo "Allowed: SOUL.md, AGENTS.md, USER.md, TOOLS.md, IDENTITY.md, MEMORY.md"
    exit 1
    ;;
esac

TARGET="$WORKSPACE/$FILENAME"

# --- Check overwrite ---
if [ -f "$TARGET" ] && [ "$FORCE" != "true" ]; then
  echo "ERROR: $FILENAME already exists. Use --force to overwrite."
  exit 1
fi

# --- Validate content ---
validate_shell_safety "content" "$CONTENT"
check_prompt_injection_tiered "$CONTENT" "$FILENAME" "content"

# --- Write file ---
mkdir -p "$WORKSPACE"
printf '%s\n' "$CONTENT" > "$TARGET"

echo "=== File Written ==="
printf '  File: %s\n' "$TARGET"
printf '  Size: %s bytes\n' "$(wc -c < "$TARGET" | tr -d ' ')"
