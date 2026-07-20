#!/usr/bin/env bash
# Parse tasks.md and output JSON for the build engine
# Usage: parse-tasks.sh [OPTIONS] <tasks.md>
# Output: JSON array of tasks with id, title, status, files, depends, wave
#
# Options:
#   --wave N         Only output tasks from wave N
#   --status STATUS  Only output tasks matching status (pending|in_progress|complete|failed)
#   --validate       Only check if output is valid JSON (exit 0/1, no output)
#   -h, --help       Show this help message

set -euo pipefail

# --- Argument parsing ---
FILTER_WAVE=""
FILTER_STATUS=""
VALIDATE_ONLY=false
TASKS_FILE=""

usage() {
  cat <<'EOF'
Usage: parse-tasks.sh [OPTIONS] <tasks.md>

Parse tasks.md into a JSON array of task objects.

Options:
  --wave N         Only output tasks from wave N
  --status STATUS  Only output tasks matching STATUS
                   (pending, in_progress, complete, failed)
  --validate       Check if output is valid JSON (exit 0/1)
  -h, --help       Show this help message

Examples:
  parse-tasks.sh tasks.md
  parse-tasks.sh --wave 2 tasks.md
  parse-tasks.sh --status pending tasks.md
  parse-tasks.sh --wave 1 --status complete tasks.md
  parse-tasks.sh --validate tasks.md
EOF
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      ;;
    --wave)
      [[ $# -lt 2 ]] && { echo "ERROR: --wave requires a number" >&2; exit 1; }
      FILTER_WAVE="$2"
      if ! [[ "$FILTER_WAVE" =~ ^[0-9]+$ ]]; then
        echo "ERROR: --wave value must be a positive integer, got '$FILTER_WAVE'" >&2
        exit 1
      fi
      shift 2
      ;;
    --status)
      [[ $# -lt 2 ]] && { echo "ERROR: --status requires a value" >&2; exit 1; }
      FILTER_STATUS="$2"
      case "$FILTER_STATUS" in
        pending|in_progress|complete|failed) ;;
        *) echo "ERROR: --status must be one of: pending, in_progress, complete, failed" >&2; exit 1 ;;
      esac
      shift 2
      ;;
    --validate)
      VALIDATE_ONLY=true
      shift
      ;;
    -*)
      echo "ERROR: Unknown option '$1'. Use --help for usage." >&2
      exit 1
      ;;
    *)
      if [[ -z "$TASKS_FILE" ]]; then
        TASKS_FILE="$1"
      else
        echo "ERROR: Unexpected argument '$1'. Only one file allowed." >&2
        exit 1
      fi
      shift
      ;;
  esac
done

if [[ -z "$TASKS_FILE" ]]; then
  echo "ERROR: No tasks file specified. Use --help for usage." >&2
  exit 1
fi

if [[ ! -f "$TASKS_FILE" ]]; then
  echo "ERROR: $TASKS_FILE not found" >&2
  exit 1
fi

# --- Parse tasks into JSON using awk ---
JSON_OUTPUT=$(awk \
  -v filter_wave="$FILTER_WAVE" \
  -v filter_status="$FILTER_STATUS" \
'
# Escape a string for safe JSON embedding
function json_escape(s,   out, i, c) {
  out = ""
  for (i = 1; i <= length(s); i++) {
    c = substr(s, i, 1)
    if      (c == "\\") out = out "\\\\"
    else if (c == "\"") out = out "\\\""
    else if (c == "\t") out = out "\\t"
    else if (c == "\n") out = out "\\n"
    else if (c == "\r") out = out "\\r"
    else                out = out c
  }
  return out
}

function emit_task() {
  if (task_id == "") return
  # Apply filters
  if (filter_wave != "" && wave != int(filter_wave)) { task_id = ""; return }
  if (filter_status != "" && status != filter_status) { task_id = ""; return }

  if (!first) printf ","
  first = 0
  printf "\n  {\"id\":\"%s\",\"title\":\"%s\",\"status\":\"%s\",\"wave\":%d,\"files\":\"%s\",\"depends\":\"%s\",\"estimate\":\"%s\"}",
    json_escape(task_id),
    json_escape(title),
    json_escape(status),
    wave,
    json_escape(files),
    json_escape(depends),
    json_escape(estimate)
  task_id = ""
  next_is_detail = 0
}

BEGIN {
  printf "["
  first = 1
  wave = 0
  task_id = ""
  next_is_detail = 0
}

/^### Wave/ {
  # Emit any pending task before switching waves
  emit_task()
  wave++
  gsub(/^### Wave [0-9]+ — /, "")
  gsub(/^### Wave [0-9]+/, "")
  wave_desc = $0
  next
}

/^- \[/ {
  # Emit any previous pending task
  emit_task()

  # Extract status
  status = "pending"
  if ($0 ~ /\[x\]/) status = "complete"
  else if ($0 ~ /\[~\]/) status = "in_progress"
  else if ($0 ~ /\[!\]/) status = "failed"

  # Extract task ID — require backtick-wrapped ID
  match($0, /`T[0-9]+`/)
  if (RSTART > 0) {
    task_id = substr($0, RSTART+1, RLENGTH-2)
  } else {
    # Malformed: no backtick ID — skip with warning
    printf "WARNING: Skipping malformed task at line %d (no task ID): %s\n", NR, $0 > "/dev/stderr"
    task_id = ""
    next_is_detail = 0
    next
  }

  # Extract title (after the task ID and em-dash)
  title = $0
  sub(/^- \[.\] `T[0-9]+` — /, "", title)
  sub(/^- \[.\] `T[0-9]+` /, "", title)
  sub(/^- \[.\] /, "", title)

  # Reset per-task fields
  files = ""
  depends = ""
  estimate = ""
  notes = ""
  next_is_detail = 1
  next
}

next_is_detail && /^  - Files:/ {
  files = $0
  sub(/^  - Files: /, "", files)
  next
}

next_is_detail && /^  - Depends:/ {
  depends = $0
  sub(/^  - Depends: /, "", depends)
  next
}

next_is_detail && /^  - Estimate:/ {
  estimate = $0
  sub(/^  - Estimate: /, "", estimate)
  next
}

next_is_detail && /^  - Notes:/ {
  notes = $0
  sub(/^  - Notes: /, "", notes)
  next
}

# When we hit a non-detail line after a task, emit the task
next_is_detail && !/^  -/ && !/^$/ {
  emit_task()
}

/^$/ {
  if (task_id != "" && next_is_detail) {
    emit_task()
  }
}

END {
  emit_task()
  print "\n]"
}
' "$TASKS_FILE")

# --- Validate JSON if jq is available ---
if command -v jq &>/dev/null; then
  if ! echo "$JSON_OUTPUT" | jq --exit-status . >/dev/null 2>&1; then
    echo "ERROR: Generated JSON is invalid" >&2
    echo "$JSON_OUTPUT" >&2
    exit 1
  fi

  if [[ "$VALIDATE_ONLY" == true ]]; then
    exit 0
  fi
else
  if [[ "$VALIDATE_ONLY" == true ]]; then
    echo "WARNING: jq not available, cannot validate JSON" >&2
    exit 1
  fi
fi

# --- Output ---
echo "$JSON_OUTPUT"
