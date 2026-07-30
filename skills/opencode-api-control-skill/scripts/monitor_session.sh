#!/bin/bash
# Monitor OpenCode session events (real-time)
#
# Fixes:
# 1. Process substitution < <() so exit works on main shell (not subshell)
# 2. Handles session.diff event - primary source of file change data
# 3. Saves diff to state/last_diff.json for get_diff.sh to use

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

echo "📡 Monitoring session: $SESSION_ID"
echo "📁 Project: $PROJECT_PATH"
echo "Press Ctrl+C to stop"
echo "----------------------------------------"

# ── Track last status to avoid duplicate messages ──────────────────────────────
LAST_STATUS=""

# ── CRITICAL: process substitution keeps exit in main shell ───────────────────
# pipe (curl | while):    exit runs in subshell → script continues!
# process sub < <(curl):  exit runs in main shell → script truly exits!

while IFS= read -r line; do

  [[ $line != data:* ]] && continue

  EVENT_DATA="${line#data:}"
  [ -z "$EVENT_DATA" ] && continue

  PAYLOAD=$(echo "$EVENT_DATA" | jq -r '.payload // empty' 2>/dev/null)
  [ -z "$PAYLOAD" ] && continue

  EVENT_TYPE=$(echo "$PAYLOAD" | jq -r '.type // empty' 2>/dev/null)
  [ -z "$EVENT_TYPE" ] && continue

  # Filter by session (skip events from other sessions)
  EVENT_SESSION=$(echo "$PAYLOAD" | \
    jq -r '.properties.sessionID // empty' 2>/dev/null)

  if [ -n "$EVENT_SESSION" ] && [ "$EVENT_SESSION" != "$SESSION_ID" ]; then
    continue
  fi

  # ── Event handlers ─────────────────────────────────────────────────────────
  case "$EVENT_TYPE" in

    "message.part.updated")
      DELTA=$(echo "$PAYLOAD" | \
        jq -r '.properties.delta // empty' 2>/dev/null)
      [ -n "$DELTA" ] && echo -n "$DELTA"
      ;;

    "session.status")
      STATUS=$(echo "$PAYLOAD" | \
        jq -r '.properties.status.type // empty' 2>/dev/null)

      if [ "$STATUS" != "$LAST_STATUS" ]; then
        LAST_STATUS="$STATUS"
        case "$STATUS" in
          "idle")
            echo -e "\n\n✅ Task completed"
            exit 0
            ;;
          "retry")
            ATTEMPT=$(echo "$PAYLOAD" | \
              jq -r '.properties.status.attempt // 1' 2>/dev/null)
            MSG=$(echo "$PAYLOAD" | \
              jq -r '.properties.status.message // "Retrying..."' 2>/dev/null)
            echo -e "\n⚠️  Retry $ATTEMPT: $MSG"
            ;;
        esac
      fi
      ;;

    "session.idle")
      echo -e "\n\n✅ Session idle - task completed"
      exit 0
      ;;

    "session.diff")
      # Primary source of file change data (what web UI uses)
      DIFF=$(echo "$PAYLOAD" | jq '.properties.diff // []' 2>/dev/null)
      DIFF_COUNT=$(echo "$DIFF" | jq 'length' 2>/dev/null || echo 0)

      if [ "$DIFF_COUNT" -gt 0 ]; then
        echo -e "\n\n📝 Files changed:"
        echo "$DIFF" | jq -r \
          '.[] | "  \(.status): \(.file) (+\(.additions)/-\(.deletions))"' \
          2>/dev/null

        # Save for get_diff.sh to use later
        echo "$DIFF" > "$SKILL_DIR/state/last_diff.json"
      fi
      ;;

    "message.updated")
      TOKENS=$(echo "$PAYLOAD" | \
        jq -r '.properties.info.tokens.total // empty' 2>/dev/null)
      COST=$(echo "$PAYLOAD" | \
        jq -r '.properties.info.cost // empty' 2>/dev/null)

      [ -n "$TOKENS" ] && echo -e "\n📊 Tokens: $TOKENS | Cost: \$$COST"
      ;;

    "session.error")
      ERROR=$(echo "$PAYLOAD" | \
        jq -r '.properties.error.data.message // "Unknown error"' 2>/dev/null)
      echo -e "\n\n❌ Error: $ERROR" >&2
      exit 1
      ;;

    "file.edited")
      FILE=$(echo "$PAYLOAD" | \
        jq -r '.properties.file // empty' 2>/dev/null)
      [ -n "$FILE" ] && echo -e "\n✏️  Editing: $(basename "$FILE")"
      ;;

  esac

done < <(curl -sN "$BASE_URL/event?directory=$PROJECT_PATH" 2>/dev/null)

echo -e "\nEvent stream closed."
exit 0