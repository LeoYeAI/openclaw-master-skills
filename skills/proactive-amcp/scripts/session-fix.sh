#!/bin/bash
# session-fix.sh — Repair corrupted or stuck OpenClaw session transcripts
#
# Modes:
#   Default:          Wraps fix-openclaw-session.py for corruption repair
#   --truncate-errors: Remove trailing error turns from session JSONL
#   --archive:         Archive session file and let gateway start fresh
#
# Dry-run by default. Use --fix to apply.
#
# Usage:
#   ./session-fix.sh [--fix] [--session-dir DIR] [--session-id ID]
#   ./session-fix.sh --fix --truncate-errors --session-dir DIR --session-id ID
#   ./session-fix.sh --fix --archive --session-dir DIR --session-id ID

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SESSION_DIR="${SESSION_DIR:-$HOME/.openclaw/agents/main/sessions}"
FIX_MODE=false
SESSION_ID=""
VERBOSE=false
TRUNCATE_ERRORS=false
ARCHIVE=false

# Parse args
while [[ $# -gt 0 ]]; do
  case $1 in
    --fix) FIX_MODE=true; shift ;;
    --session-dir) SESSION_DIR="$2"; shift 2 ;;
    --session-id) SESSION_ID="$2"; shift 2 ;;
    --verbose) VERBOSE=true; shift ;;
    --truncate-errors) TRUNCATE_ERRORS=true; shift ;;
    --archive) ARCHIVE=true; shift ;;
    *) shift ;;
  esac
done

# ============================================================
# Mode: Truncate trailing error turns from session
# ============================================================
if [ "$TRUNCATE_ERRORS" = true ]; then
  if [ -z "$SESSION_ID" ]; then
    echo "ERROR: --session-id required with --truncate-errors"
    exit 1
  fi

  SESSION_FILE="$SESSION_DIR/${SESSION_ID}.jsonl"
  if [ ! -f "$SESSION_FILE" ]; then
    echo "ERROR: Session file not found: $SESSION_FILE"
    exit 1
  fi

  SESSIONFIX_FILE="$SESSION_FILE" \
  SESSIONFIX_FIX="$FIX_MODE" \
  python3 << 'PYEOF'
import json, os, sys

session_file = os.environ["SESSIONFIX_FILE"]
fix_mode = os.environ["SESSIONFIX_FIX"] == "true"

# Error patterns indicating stuck session (matches diagnose.sh check_session_health)
ERROR_PATTERNS = [
    "400", "rate_limit", "rate limit", "overloaded", "capacity",
    "internal_error", "server_error", "context_length_exceeded",
    "invalid_request_error", "unexpected `tool_use_id`",
]

# Read all lines
lines = []
with open(session_file) as f:
    for line in f:
        stripped = line.rstrip('\n')
        if stripped:
            lines.append(stripped)

if not lines:
    print("Session file is empty")
    sys.exit(0)

# Walk backward to find where the trailing error block starts
truncate_from = len(lines)
for i in range(len(lines) - 1, -1, -1):
    try:
        obj = json.loads(lines[i])
    except (json.JSONDecodeError, ValueError):
        # Malformed line — treat as error
        truncate_from = i
        continue

    msg = obj.get("message", {})
    err = (msg.get("errorMessage", "") or "").lower()
    content = msg.get("content", [])

    has_error = False
    for pattern in ERROR_PATTERNS:
        if pattern in err:
            has_error = True
            break

    if not has_error and isinstance(content, list):
        for block in content:
            if isinstance(block, dict):
                text = (block.get("text", "") or "").lower()
                for pattern in ERROR_PATTERNS:
                    if pattern in text:
                        has_error = True
                        break
            if has_error:
                break

    if has_error:
        truncate_from = i
    else:
        break

removed = len(lines) - truncate_from
if removed == 0:
    print("No trailing error turns found")
    sys.exit(0)

print(f"Found {removed} trailing error turn(s) to remove ({truncate_from} turns kept)")

if not fix_mode:
    print("Dry run — use --fix to apply")
    sys.exit(0)

# Write back without trailing errors
with open(session_file, 'w') as f:
    for line in lines[:truncate_from]:
        f.write(line + '\n')

print(f"Truncated: {removed} error turns removed")
PYEOF
  exit $?
fi

# ============================================================
# Mode: Archive session file and start fresh
# ============================================================
if [ "$ARCHIVE" = true ]; then
  if [ -z "$SESSION_ID" ]; then
    echo "ERROR: --session-id required with --archive"
    exit 1
  fi

  SESSION_FILE="$SESSION_DIR/${SESSION_ID}.jsonl"
  if [ ! -f "$SESSION_FILE" ]; then
    echo "ERROR: Session file not found: $SESSION_FILE"
    exit 1
  fi

  BACKUP_FILE="${SESSION_FILE}.$(date +%Y%m%d%H%M%S).bak"

  if [ "$FIX_MODE" != true ]; then
    echo "Would archive: $SESSION_FILE -> $BACKUP_FILE"
    echo "Dry run — use --fix to apply"
    exit 0
  fi

  mv "$SESSION_FILE" "$BACKUP_FILE"
  echo "Archived: $SESSION_FILE -> $BACKUP_FILE"
  exit 0
fi

# ============================================================
# Default mode: Delegate to fix-openclaw-session.py
# ============================================================
REPAIR_SCRIPT="$SCRIPT_DIR/fix-openclaw-session.py"

if [ ! -f "$REPAIR_SCRIPT" ]; then
  echo "ERROR: fix-openclaw-session.py not found at $REPAIR_SCRIPT"
  exit 1
fi

if [ ! -d "$SESSION_DIR" ]; then
  echo "ERROR: Session directory not found: $SESSION_DIR"
  exit 1
fi

# Build command
CMD=(python3 "$REPAIR_SCRIPT" "$SESSION_DIR")

if [ "$FIX_MODE" = true ]; then
  CMD+=(--fix)
fi

if [ "$VERBOSE" = true ]; then
  CMD+=(--verbose)
fi

if [ -n "$SESSION_ID" ]; then
  CMD+=(--session-id "$SESSION_ID")
fi

# Run
exec "${CMD[@]}"
