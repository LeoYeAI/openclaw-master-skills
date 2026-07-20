#!/usr/bin/env bash
set -euo pipefail

VALID_CATEGORIES="spec_gap design_gap pattern best_practice agent_issue"
VALID_PRIORITIES="low medium high"

usage() {
  cat <<'EOF'
Usage:
  log-learning.sh <specclaw_dir> <change_name> <category> <priority> "<detail>" ["<action>"]
  log-learning.sh <specclaw_dir> <change_name> --list
  log-learning.sh <specclaw_dir> <change_name> --promote <learning_id>

Modes:
  log (default)   Append a new learning entry
  --list          Show summary table of all learnings
  --promote <id>  Promote a learning (e.g. L1) from pending to promoted

Categories: spec_gap, design_gap, pattern, best_practice, agent_issue
Priorities: low, medium, high
EOF
  exit 0
}

# Help check
for arg in "$@"; do
  [[ "$arg" == "--help" || "$arg" == "-h" ]] && usage
done

if [[ $# -lt 3 ]]; then
  echo "Error: Not enough arguments. Use --help for usage." >&2
  exit 1
fi

SPECCLAW_DIR="$1"
CHANGE_NAME="$2"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$(cd "$SCRIPT_DIR/../templates" && pwd)"
LEARNINGS_FILE="$SPECCLAW_DIR/learnings.md"

# Ensure learnings.md exists, create from template if missing
ensure_learnings() {
  if [[ ! -f "$LEARNINGS_FILE" ]]; then
    if [[ ! -f "$TEMPLATE_DIR/learnings.md" ]]; then
      echo "Error: Template not found at $TEMPLATE_DIR/learnings.md" >&2
      exit 1
    fi
    sed "s/{{change_name}}/$CHANGE_NAME/g" "$TEMPLATE_DIR/learnings.md" > "$LEARNINGS_FILE"
  fi
}

# Count existing entries to compute next ID
next_id() {
  local count
  count=$(grep -c '^## \[L' "$LEARNINGS_FILE" 2>/dev/null || true)
  echo "L$(( count + 1 ))"
}

# --- List mode ---
if [[ "$3" == "--list" ]]; then
  if [[ ! -f "$LEARNINGS_FILE" ]] || ! grep -q '^## \[L' "$LEARNINGS_FILE" 2>/dev/null; then
    echo "No learnings recorded."
    exit 0
  fi

  # Parse entries: ID, category, priority, status, title
  while IFS= read -r line; do
    if [[ "$line" =~ ^##\ \[(L[0-9]+)\]\ ([a-z_]+)\ —\ (.+)$ ]]; then
      id="${BASH_REMATCH[1]}"
      cat="${BASH_REMATCH[2]}"
      title="${BASH_REMATCH[3]}"
      priority=""
      status=""
    elif [[ "$line" =~ ^\*\*Priority:\*\*\ (.+)$ ]]; then
      priority="${BASH_REMATCH[1]}"
    elif [[ "$line" =~ ^\*\*Status:\*\*\ (.+)$ ]]; then
      status="${BASH_REMATCH[1]}"
      printf "%-4s %-15s %-8s %-10s %s\n" "$id" "$cat" "$priority" "$status" "$title"
    fi
  done < "$LEARNINGS_FILE"
  exit 0
fi

# --- Promote mode ---
if [[ "$3" == "--promote" ]]; then
  if [[ $# -lt 4 ]]; then
    echo "Error: --promote requires a learning ID (e.g. L1)" >&2
    exit 1
  fi
  TARGET_ID="$4"

  if [[ ! -f "$LEARNINGS_FILE" ]]; then
    echo "Error: No learnings file found at $LEARNINGS_FILE" >&2
    exit 1
  fi

  if ! grep -q "^## \[${TARGET_ID}\]" "$LEARNINGS_FILE"; then
    echo "Error: Learning $TARGET_ID not found" >&2
    exit 1
  fi

  # Replace status for the target entry
  # We need to find the entry and change its status
  in_target=false
  promoted=false
  tmp_file="${LEARNINGS_FILE}.tmp"
  entry_lines=""

  while IFS= read -r line; do
    if [[ "$line" =~ ^##\ \[${TARGET_ID}\] ]]; then
      in_target=true
      entry_lines="$line"$'\n'
      echo "$line" >> "$tmp_file"
    elif $in_target && [[ "$line" =~ ^##\ \[L ]]; then
      # Next entry starts, stop capturing
      in_target=false
      echo "$line" >> "$tmp_file"
    elif $in_target && [[ "$line" == "**Status:** pending" ]]; then
      echo "**Status:** promoted" >> "$tmp_file"
      entry_lines+="**Status:** promoted"$'\n'
      promoted=true
    elif $in_target; then
      echo "$line" >> "$tmp_file"
      entry_lines+="$line"$'\n'
    else
      echo "$line" >> "$tmp_file"
    fi
  done < "$LEARNINGS_FILE"

  mv "$tmp_file" "$LEARNINGS_FILE"

  if $promoted; then
    # Print the full entry
    in_target=false
    while IFS= read -r line; do
      if [[ "$line" =~ ^##\ \[${TARGET_ID}\] ]]; then
        in_target=true
        echo "$line"
      elif $in_target && [[ "$line" =~ ^##\ \[L ]]; then
        break
      elif $in_target; then
        echo "$line"
      fi
    done < "$LEARNINGS_FILE"
  else
    echo "Warning: $TARGET_ID status was not 'pending', no change made." >&2
  fi
  exit 0
fi

# --- Log mode ---
if [[ $# -lt 5 ]]; then
  echo "Error: Log mode requires: <specclaw_dir> <change_name> <category> <priority> \"<detail>\" [\"<action>\"]" >&2
  exit 1
fi

CATEGORY="$3"
PRIORITY="$4"
DETAIL="$5"
ACTION="${6:-}"

# Validate category
if ! echo "$VALID_CATEGORIES" | grep -qw "$CATEGORY"; then
  echo "Error: Invalid category '$CATEGORY'. Must be one of: $VALID_CATEGORIES" >&2
  exit 1
fi

# Validate priority
if ! echo "$VALID_PRIORITIES" | grep -qw "$PRIORITY"; then
  echo "Error: Invalid priority '$PRIORITY'. Must be one of: $VALID_PRIORITIES" >&2
  exit 1
fi

ensure_learnings

ID=$(next_id)
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M UTC")

# Build short title from first ~60 chars of detail
SHORT_TITLE="$DETAIL"
if [[ ${#SHORT_TITLE} -gt 60 ]]; then
  SHORT_TITLE="${SHORT_TITLE:0:57}..."
fi

ACTION_TEXT="${ACTION:-No action specified}"

cat >> "$LEARNINGS_FILE" <<EOF

## [$ID] $CATEGORY — $SHORT_TITLE

**When:** $TIMESTAMP
**Category:** $CATEGORY
**Priority:** $PRIORITY
**Status:** pending

### Detail
$DETAIL

### Action
$ACTION_TEXT

---
EOF

echo "Logged $ID: $CATEGORY ($PRIORITY) — $SHORT_TITLE"
