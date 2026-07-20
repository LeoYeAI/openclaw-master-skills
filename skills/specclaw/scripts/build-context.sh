#!/usr/bin/env bash
# Build context payload for a specific task — feeds the coding agent
# Usage: build-context.sh <specclaw_dir> <change_name> <task_id>
#
# Reads spec.md, design.md, task details from tasks.md, existing file contents,
# and formats everything into a complete Build Agent prompt sent to stdout.
#
# Dependencies: bash, coreutils, jq (with grep fallback)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MAX_FILE_LINES=500

# --- Help ---
usage() {
  cat <<'EOF'
Usage: build-context.sh <specclaw_dir> <change_name> <task_id>

Build a context payload for a coding agent to implement a specific task.

Arguments:
  specclaw_dir   Path to the .specclaw directory
  change_name    Name of the current change (subdirectory under changes/)
  task_id        Task ID to build context for (e.g. T1, T4)

The script reads spec.md, design.md, task details, and existing file contents,
then outputs a formatted prompt to stdout.

Examples:
  build-context.sh .specclaw my-feature T3
  build-context.sh /project/.specclaw auth-system T1
EOF
  exit 0
}

# --- Argument parsing ---
[[ "${1:-}" == "-h" || "${1:-}" == "--help" ]] && usage

if [[ $# -lt 3 ]]; then
  echo "ERROR: Expected 3 arguments: <specclaw_dir> <change_name> <task_id>" >&2
  echo "Use --help for usage." >&2
  exit 1
fi

SPECCLAW_DIR="$1"
CHANGE_NAME="$2"
TASK_ID="$3"

# Validate specclaw dir
if [[ ! -d "$SPECCLAW_DIR" ]]; then
  echo "ERROR: specclaw directory not found: $SPECCLAW_DIR" >&2
  exit 1
fi

CHANGE_DIR="$SPECCLAW_DIR/changes/$CHANGE_NAME"
if [[ ! -d "$CHANGE_DIR" ]]; then
  echo "ERROR: Change directory not found: $CHANGE_DIR" >&2
  exit 1
fi

# Project root is parent of .specclaw
PROJECT_ROOT="$(cd "$SPECCLAW_DIR/.." && pwd)"

# --- Config extraction ---
CONFIG_FILE="$SPECCLAW_DIR/config.yaml"

yaml_get() {
  # Simple YAML value extractor — handles: key: "value" or key: value
  local file="$1" key="$2"
  grep -E "^[[:space:]]*${key}:" "$file" 2>/dev/null \
    | head -1 \
    | sed 's/^[^:]*:[[:space:]]*//' \
    | sed 's/^["'\'']\(.*\)["'\'']\s*$/\1/' \
    | sed 's/[[:space:]]*$//'
}

PROJECT_NAME=""
COMMIT_PREFIX=""

if [[ -f "$CONFIG_FILE" ]]; then
  PROJECT_NAME="$(yaml_get "$CONFIG_FILE" "name")"
  COMMIT_PREFIX="$(yaml_get "$CONFIG_FILE" "commit_prefix")"
else
  echo "WARNING: config.yaml not found at $CONFIG_FILE" >&2
fi

PROJECT_NAME="${PROJECT_NAME:-unnamed-project}"
COMMIT_PREFIX="${COMMIT_PREFIX:-specclaw}"

# --- Task extraction ---
TASKS_FILE="$CHANGE_DIR/tasks.md"
if [[ ! -f "$TASKS_FILE" ]]; then
  echo "ERROR: tasks.md not found: $TASKS_FILE" >&2
  exit 1
fi

# Parse all tasks
TASKS_JSON="$("$SCRIPT_DIR/parse-tasks.sh" "$TASKS_FILE")"

# Extract the specific task by ID
extract_task_jq() {
  echo "$TASKS_JSON" | jq -e --arg id "$TASK_ID" '.[] | select(.id == $id)' 2>/dev/null
}

extract_task_grep() {
  # Fallback: grep-based extraction from JSON array
  # Find the object containing our task ID
  local in_match=false
  local result=""
  local brace_depth=0

  while IFS= read -r line; do
    if [[ "$line" == *"\"id\":\"$TASK_ID\""* ]]; then
      in_match=true
    fi
    if [[ "$in_match" == true ]]; then
      result+="$line"
      # Count braces to find object boundaries
      local opens="${line//[^\{]/}"
      local closes="${line//[^\}]/}"
      brace_depth=$(( brace_depth + ${#opens} - ${#closes} ))
      if [[ $brace_depth -le 0 && -n "$result" ]]; then
        # Clean trailing comma
        result="${result%,}"
        echo "$result"
        return 0
      fi
    fi
  done <<< "$TASKS_JSON"

  return 1
}

# Extract field from a single JSON object (no jq)
json_field_grep() {
  local json="$1" field="$2"
  echo "$json" | grep -o "\"${field}\":\"[^\"]*\"" | head -1 | sed "s/\"${field}\":\"//" | sed 's/"$//'
}

json_field_grep_num() {
  local json="$1" field="$2"
  echo "$json" | grep -o "\"${field}\":[0-9]*" | head -1 | sed "s/\"${field}\"://"
}

TASK_JSON=""
if command -v jq &>/dev/null; then
  TASK_JSON="$(extract_task_jq)" || true
else
  echo "WARNING: jq not available, using grep fallback" >&2
  TASK_JSON="$(extract_task_grep)" || true
fi

if [[ -z "$TASK_JSON" ]]; then
  echo "ERROR: Task $TASK_ID not found in $TASKS_FILE" >&2
  exit 1
fi

# Extract task fields
if command -v jq &>/dev/null; then
  TASK_TITLE="$(echo "$TASK_JSON" | jq -r '.title')"
  TASK_FILES="$(echo "$TASK_JSON" | jq -r '.files')"
  TASK_STATUS="$(echo "$TASK_JSON" | jq -r '.status')"
  TASK_DEPENDS="$(echo "$TASK_JSON" | jq -r '.depends')"
  TASK_WAVE="$(echo "$TASK_JSON" | jq -r '.wave')"
  TASK_ESTIMATE="$(echo "$TASK_JSON" | jq -r '.estimate')"
else
  TASK_TITLE="$(json_field_grep "$TASK_JSON" "title")"
  TASK_FILES="$(json_field_grep "$TASK_JSON" "files")"
  TASK_STATUS="$(json_field_grep "$TASK_JSON" "status")"
  TASK_DEPENDS="$(json_field_grep "$TASK_JSON" "depends")"
  TASK_WAVE="$(json_field_grep_num "$TASK_JSON" "wave")"
  TASK_ESTIMATE="$(json_field_grep "$TASK_JSON" "estimate")"
fi

# --- Task notes extraction ---
# Extract notes from tasks.md for this specific task
TASK_NOTES=""
if grep -q "^\`${TASK_ID}\`" "$TASKS_FILE" || grep -q " \`${TASK_ID}\`" "$TASKS_FILE"; then
  # Get the Notes: line for this task
  TASK_NOTES="$(awk -v tid="$TASK_ID" '
    $0 ~ "`"tid"`" { found=1; next }
    found && /^  - Notes:/ { sub(/^  - Notes: /, ""); print; found=0; next }
    found && /^- \[/ { found=0 }
    found && /^###/ { found=0 }
  ' "$TASKS_FILE")"
fi

# --- Spec & Design ---
SPEC_FILE="$CHANGE_DIR/spec.md"
DESIGN_FILE="$CHANGE_DIR/design.md"

SPEC_CONTENT=""
if [[ -f "$SPEC_FILE" ]]; then
  SPEC_CONTENT="$(cat "$SPEC_FILE")"
else
  echo "WARNING: spec.md not found at $SPEC_FILE — using placeholder" >&2
  SPEC_CONTENT="*No specification found. Use your best judgment based on the task description.*"
fi

DESIGN_CONTENT=""
if [[ -f "$DESIGN_FILE" ]]; then
  DESIGN_CONTENT="$(cat "$DESIGN_FILE")"
else
  echo "WARNING: design.md not found at $DESIGN_FILE — using placeholder" >&2
  DESIGN_CONTENT="*No design document found. Use your best judgment based on the task description.*"
fi

# --- Existing file contents ---
build_file_contents() {
  local file_list="$1"
  local output=""

  # Split comma-separated file list
  IFS=',' read -ra FILES <<< "$file_list"

  for raw_file in "${FILES[@]}"; do
    # Trim whitespace and backticks
    local file
    file="$(echo "$raw_file" | sed 's/^[[:space:]`]*//;s/[[:space:]`]*$//')"
    [[ -z "$file" ]] && continue

    local full_path="$PROJECT_ROOT/$file"

    output+="### \`$file\`"$'\n'

    if [[ -f "$full_path" ]]; then
      local line_count
      line_count="$(wc -l < "$full_path")"
      if [[ "$line_count" -gt "$MAX_FILE_LINES" ]]; then
        output+="*(Truncated: showing first $MAX_FILE_LINES of $line_count lines)*"$'\n'
        output+='```'$'\n'
        output+="$(head -n "$MAX_FILE_LINES" "$full_path")"$'\n'
        output+='```'$'\n'
      else
        output+='```'$'\n'
        output+="$(cat "$full_path")"$'\n'
        output+='```'$'\n'
      fi
    else
      output+="*New file — to be created*"$'\n'
    fi
    output+=$'\n'
  done

  echo "$output"
}

EXISTING_CODE=""
if [[ -n "$TASK_FILES" && "$TASK_FILES" != "null" ]]; then
  EXISTING_CODE="$(build_file_contents "$TASK_FILES")"
else
  EXISTING_CODE="*No files specified for this task.*"
fi

# --- Format file list for display ---
format_file_list() {
  local file_list="$1"
  IFS=',' read -ra FILES <<< "$file_list"
  for raw_file in "${FILES[@]}"; do
    local file
    file="$(echo "$raw_file" | sed 's/^[[:space:]`]*//;s/[[:space:]`]*$//')"
    [[ -z "$file" ]] && continue
    echo "- \`$file\`"
  done
}

FILE_LIST_FORMATTED=""
if [[ -n "$TASK_FILES" && "$TASK_FILES" != "null" ]]; then
  FILE_LIST_FORMATTED="$(format_file_list "$TASK_FILES")"
else
  FILE_LIST_FORMATTED="*No files specified*"
fi

# --- Error history for retries ---
ERRORS_FILE="$CHANGE_DIR/errors.md"
ERROR_HISTORY=""

if [[ -f "$ERRORS_FILE" ]]; then
  # Extract blocks for this task_id: from "## <TASK_ID>" line through "---"
  # Take only the last 3 entries
  TASK_ERRORS="$(awk -v tid="$TASK_ID" '
    BEGIN { block=""; capturing=0 }
    /^## / {
      if (capturing) {
        # End previous block (no trailing ---)
        blocks[++n] = block
        block = ""
        capturing = 0
      }
      if ($2 == tid) {
        capturing = 1
        block = $0 "\n"
        next
      }
    }
    /^---$/ {
      if (capturing) {
        blocks[++n] = block
        block = ""
        capturing = 0
        next
      }
    }
    capturing { block = block $0 "\n" }
    END {
      if (capturing && block != "") blocks[++n] = block
      # Output last 3 blocks
      start = (n > 3) ? n - 2 : 1
      for (i = start; i <= n; i++) {
        printf "%s---\n", blocks[i]
      }
    }
  ' "$ERRORS_FILE")"

  if [[ -n "$TASK_ERRORS" ]]; then
    ERROR_HISTORY="## Previous Errors for This Task

The following errors occurred in previous attempts. **Avoid repeating these mistakes.**

${TASK_ERRORS}"
  fi
fi

# --- Build the prompt ---
cat <<PROMPT
You are a coding agent implementing a specific task in the project "${PROJECT_NAME}".

## Your Task
${TASK_TITLE}
${TASK_NOTES}

## Files to Modify
${FILE_LIST_FORMATTED}

## Specification Context
${SPEC_CONTENT}

## Design Context
${DESIGN_CONTENT}

## Existing Code
${EXISTING_CODE}

${ERROR_HISTORY}
## Constraints
1. ONLY modify/create the files listed above
2. Follow existing code style and patterns
3. Write tests for new functionality (if test framework exists)
4. Use existing utilities/helpers — don't duplicate
5. Keep changes minimal and focused on THIS task only
6. Commit with message: "${COMMIT_PREFIX}(${CHANGE_NAME}): ${TASK_ID} — ${TASK_TITLE}"

## Definition of Done
- All listed files created/modified correctly
- Code compiles/runs without errors
- Tests pass (if applicable)
- No unrelated changes
PROMPT
