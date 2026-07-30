#!/bin/bash
# Get session file changes
# Uses message parts (PatchPart + ToolPart) since /diff requires snapshots

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# ── Load state ─────────────────────────────────────────────────────────────────
if [ ! -f "$SKILL_DIR/state/current.json" ]; then
  echo "Error: No active session" >&2
  exit 1
fi

SESSION_ID=$(jq -r '.session_id' "$SKILL_DIR/state/current.json")
PROJECT_PATH=$(jq -r '.project_path' "$SKILL_DIR/state/current.json")
BASE_URL=$(jq -r '.base_url' "$SKILL_DIR/state/current.json")

# ── Fetch all messages ─────────────────────────────────────────────────────────
MESSAGES=$(curl -s "$BASE_URL/session/$SESSION_ID/message?directory=$PROJECT_PATH")

if [ -z "$MESSAGES" ] || [ "$MESSAGES" = "null" ] || [ "$MESSAGES" = "[]" ]; then
  echo "No messages in session yet."
  exit 0
fi

# ── Method 1: PatchPart (type="patch") ────────────────────────────────────────
# PatchPart: { type: "patch", hash: string, files: string[] }
# Listed at end of each step, contains all files modified

PATCH_FILES=$(echo "$MESSAGES" | jq -r '
  [.[] |
    .parts[] |
    select(.type == "patch") |
    .files[]
  ] | unique | .[]
' 2>/dev/null)

if [ -n "$PATCH_FILES" ]; then
  echo "=== Modified Files ==="
  echo "$PATCH_FILES" | while read -r f; do
    echo "  ✏️  $f"
  done
  echo ""
fi

# ── Method 2: ToolPart for file-editing tools ──────────────────────────────────
# Tools that modify files: edit, write, patch, multiedit

TOOL_CHANGES=$(echo "$MESSAGES" | jq -r '
  [.[] |
    .parts[] |
    select(.type == "tool") |
    select(.tool | test("^(edit|write|patch|multiedit)$")) |
    select(.state.status == "completed") |
    {
      tool: .tool,
      file: (.state.input.filePath // .state.input.path // .state.input.file // "unknown")
    }
  ] |
  group_by(.file) |
  .[] |
  {
    file: .[0].file,
    operations: [.[].tool] | unique | join(", ")
  }
' 2>/dev/null)

if [ -n "$TOOL_CHANGES" ]; then
  echo "=== Tool Operations ==="
  echo "$TOOL_CHANGES" | jq -r '"  [\(.operations)] \(.file)"' 2>/dev/null
  echo ""
fi

# ── Method 3: /diff endpoint with messageID ────────────────────────────────────
# Try all user message IDs newest first

ALL_MSG_IDS=$(echo "$MESSAGES" | jq -r '
  [.[] | select(.info.role == "user") | .info.id] | reverse | .[]
' 2>/dev/null)

DIFF_FOUND=false
for MSG_ID in $ALL_MSG_IDS; do
  DIFF=$(curl -s \
    "$BASE_URL/session/$SESSION_ID/diff?directory=$PROJECT_PATH&messageID=$MSG_ID")

  DIFF_COUNT=$(echo "$DIFF" | jq 'length' 2>/dev/null || echo 0)

  if [ "$DIFF_COUNT" -gt 0 ]; then
    echo "=== Diff ==="
    echo "$DIFF" | jq -r \
      '.[] | "\(.status): \(.file) (+\(.additions)/-\(.deletions))"'
    DIFF_FOUND=true
    break
  fi
done

# ── Method 4: Check last_diff.json saved by monitor_session.sh ────────────────
if [ "$DIFF_FOUND" = false ] && [ -z "$PATCH_FILES" ] && [ -z "$TOOL_CHANGES" ]; then
  if [ -f "$SKILL_DIR/state/last_diff.json" ]; then
    SAVED_DIFF=$(cat "$SKILL_DIR/state/last_diff.json")
    SAVED_COUNT=$(echo "$SAVED_DIFF" | jq 'length' 2>/dev/null || echo 0)

    if [ "$SAVED_COUNT" -gt 0 ]; then
      echo "=== Changes (from event stream) ==="
      echo "$SAVED_DIFF" | jq -r \
        '.[] | "\(.status): \(.file) (+\(.additions)/-\(.deletions))"'
      exit 0
    fi
  fi

  echo "No file changes detected in this session."
fi

exit 0