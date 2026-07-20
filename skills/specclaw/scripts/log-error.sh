#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  log-error.sh <specclaw_dir> <change_name> <task_id> <wave> <agent_label> "<summary>" [--error-file <path>]
  log-error.sh <specclaw_dir> <change_name> --resolve <task_id>

Log mode:
  Appends a structured error entry to <specclaw_dir>/changes/<change_name>/errors.md.
  Error output is read from --error-file, stdin (if piped), or left empty.
  Output is capped at 50 lines.

Resolve mode:
  Marks all pending entries for <task_id> as resolved_on_retry.

Options:
  -h, --help    Show this help message
EOF
}

# --- Help flag ---
for arg in "$@"; do
  case "$arg" in
    -h|--help) usage; exit 0 ;;
  esac
done

if [[ $# -lt 3 ]]; then
  usage >&2
  exit 1
fi

SPECCLAW_DIR="$1"
CHANGE_NAME="$2"
ERRORS_MD="${SPECCLAW_DIR}/changes/${CHANGE_NAME}/errors.md"
TEMPLATE_HEADER="# Error Journal: ${CHANGE_NAME}

Build errors and their resolutions.

---
"

# --- Resolve mode ---
if [[ "$3" == "--resolve" ]]; then
  TASK_ID="${4:?Missing task_id for --resolve}"
  if [[ ! -f "$ERRORS_MD" ]]; then
    exit 0
  fi
  # Replace pending → resolved_on_retry only in sections matching this task_id
  # We use a simple sed: find lines with [TASK_ID] header, then flip status in following lines
  # Simpler approach: since Status lines are unique enough, scope by task_id block
  tmp="$(mktemp)"
  awk -v tid="$TASK_ID" '
    /^## \[/ { in_block = (index($0, "[" tid "]") > 0) }
    in_block && $0 == "**Status:** pending" { $0 = "**Status:** resolved_on_retry" }
    { print }
  ' "$ERRORS_MD" > "$tmp"
  mv "$tmp" "$ERRORS_MD"
  exit 0
fi

# --- Log mode ---
if [[ $# -lt 6 ]]; then
  echo "Error: log mode requires at least 6 arguments" >&2
  usage >&2
  exit 1
fi

TASK_ID="$3"
WAVE="$4"
AGENT_LABEL="$5"
SUMMARY="$6"
shift 6

ERROR_FILE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --error-file)
      ERROR_FILE="${2:?--error-file requires a path}"
      shift 2
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

# Read error output
ERROR_TEXT=""
if [[ -n "$ERROR_FILE" ]]; then
  ERROR_TEXT="$(cat "$ERROR_FILE" 2>/dev/null || true)"
elif [[ ! -t 0 ]]; then
  ERROR_TEXT="$(cat)"
fi

# Cap at 50 lines
LINE_COUNT="$(echo "$ERROR_TEXT" | wc -l)"
if [[ "$LINE_COUNT" -gt 50 ]]; then
  ERROR_TEXT="$(echo "$ERROR_TEXT" | head -n 50)"
  ERROR_TEXT="${ERROR_TEXT}
[truncated — original output was ${LINE_COUNT} lines]"
fi

# Ensure errors.md exists
if [[ ! -f "$ERRORS_MD" ]]; then
  mkdir -p "$(dirname "$ERRORS_MD")"
  printf '%s' "$TEMPLATE_HEADER" > "$ERRORS_MD"
fi

# Compute attempt number (count existing entries for this task_id)
EXISTING="$(grep -c "^## \\[${TASK_ID}\\] Attempt " "$ERRORS_MD" 2>/dev/null || true)"
ATTEMPT=$(( EXISTING + 1 ))

# Timestamp
WHEN="$(date -u '+%Y-%m-%d %H:%M UTC')"

# Append entry
cat >> "$ERRORS_MD" <<EOF

## [${TASK_ID}] Attempt ${ATTEMPT} — Wave ${WAVE}

**When:** ${WHEN}
**Agent:** ${AGENT_LABEL}
**Status:** pending

### Summary
${SUMMARY}

### Error Output
\`\`\`
${ERROR_TEXT}
\`\`\`

---
EOF

exit 0
