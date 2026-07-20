#!/usr/bin/env bash
# Update task status(es) in tasks.md
#
# Usage:
#   update-task-status.sh [OPTIONS] <tasks.md> <task_id> <new_status>
#   update-task-status.sh [OPTIONS] <tasks.md> --batch T1:complete T2:failed ...
#
# Statuses: pending | in_progress | complete | failed
# Markers:  [ ] pending  [~] in_progress  [x] complete  [!] failed
#
# Options:
#   --batch        Accept multiple task_id:status pairs
#   --quiet        Suppress stdout (errors still go to stderr)
#   --log          Append transitions to a ## Status Log section in tasks.md
#   -h, --help     Show this help

set -euo pipefail

# ── Helpers ──────────────────────────────────────────────────────────────────

show_help() {
  sed -n '2,/^$/{ s/^# \?//; p }' "$0"
  exit 0
}

status_to_marker() {
  case "$1" in
    pending)     echo "[ ]" ;;
    in_progress) echo "[~]" ;;
    complete)    echo "[x]" ;;
    failed)      echo "[!]" ;;
    *) return 1 ;;
  esac
}

marker_to_status() {
  case "$1" in
    "[ ]") echo "pending" ;;
    "[~]") echo "in_progress" ;;
    "[x]") echo "complete" ;;
    "[!]") echo "failed" ;;
    *)     echo "unknown" ;;
  esac
}

# Read the current marker for a task from the file
read_current_status() {
  local file="$1" task_id="$2"
  local marker
  marker=$(grep -oP "^- \[\K.\](?= \`${task_id}\`)" "$file" 2>/dev/null | head -1) || true
  if [[ -n "$marker" ]]; then
    marker_to_status "[$marker"
  else
    echo ""
  fi
}

# ── Parse flags ──────────────────────────────────────────────────────────────

BATCH=false
QUIET=false
LOG=false
POSITIONAL=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)  show_help ;;
    --batch)    BATCH=true; shift ;;
    --quiet)    QUIET=true; shift ;;
    --log)      LOG=true;   shift ;;
    --)         shift; POSITIONAL+=("$@"); break ;;
    -*)         echo "ERROR: Unknown option '$1'. Use --help for usage." >&2; exit 1 ;;
    *)          POSITIONAL+=("$1"); shift ;;
  esac
done
set -- "${POSITIONAL[@]}"

if [[ $# -lt 1 ]]; then
  echo "ERROR: Missing tasks file argument. Use --help for usage." >&2
  exit 1
fi

TASKS_FILE="$1"; shift

if [[ ! -f "$TASKS_FILE" ]]; then
  echo "ERROR: File not found: $TASKS_FILE" >&2
  exit 1
fi

# ── Build pairs list ─────────────────────────────────────────────────────────

declare -a PAIRS=()

if $BATCH; then
  if [[ $# -lt 1 ]]; then
    echo "ERROR: --batch requires at least one TASK_ID:STATUS pair." >&2
    exit 1
  fi
  for arg in "$@"; do
    if [[ "$arg" != *:* ]]; then
      echo "ERROR: Invalid batch pair '$arg'. Expected TASK_ID:STATUS." >&2
      exit 1
    fi
    PAIRS+=("$arg")
  done
else
  # Single-task (backward-compatible) mode
  if [[ $# -lt 2 ]]; then
    echo "ERROR: Missing task_id and/or status. Use --help for usage." >&2
    exit 1
  fi
  PAIRS+=("$1:$2")
fi

# ── Process each pair ────────────────────────────────────────────────────────

HAD_ERROR=false

for pair in "${PAIRS[@]}"; do
  TASK_ID="${pair%%:*}"
  NEW_STATUS="${pair#*:}"
  TIMESTAMP=$(date -u '+%Y-%m-%d %H:%M UTC')

  # Validate status
  if ! NEW_MARKER=$(status_to_marker "$NEW_STATUS"); then
    echo "ERROR: Invalid status '$NEW_STATUS' for $TASK_ID. Use: pending|in_progress|complete|failed" >&2
    HAD_ERROR=true
    continue
  fi

  # Check task exists
  if ! grep -q "\`$TASK_ID\`" "$TASKS_FILE"; then
    echo "ERROR: Task $TASK_ID not found in $TASKS_FILE" >&2
    HAD_ERROR=true
    continue
  fi

  # Detect previous status
  PREV_STATUS=$(read_current_status "$TASKS_FILE" "$TASK_ID")
  PREV_STATUS="${PREV_STATUS:-unknown}"

  # Update marker in file
  sed -i "s/^- \[.\] \`$TASK_ID\`/- $NEW_MARKER \`$TASK_ID\`/" "$TASKS_FILE"

  # Build transition string
  TRANSITION="$TASK_ID: $PREV_STATUS → $NEW_STATUS"

  # Timestamp to stderr (always, for logging)
  echo "[$TIMESTAMP] $TRANSITION" >&2

  # Stdout (unless --quiet)
  if ! $QUIET; then
    echo "OK: $TRANSITION"
  fi

  # Append to ## Status Log section if --log
  if $LOG; then
    if ! grep -q '^## Status Log' "$TASKS_FILE"; then
      printf '\n## Status Log\n' >> "$TASKS_FILE"
    fi
    echo "- $TIMESTAMP — $TRANSITION" >> "$TASKS_FILE"
  fi
done

if $HAD_ERROR; then
  exit 1
fi
