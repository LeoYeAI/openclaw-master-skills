#!/usr/bin/env bash
# post-comments.sh — Post cross-reference comments with jitter-based rate limiting
#
# Usage: ./post-comments.sh <owner/repo> <workspace_dir> [jitter_min] [jitter_max] [daily_max]
#
# Reads approved-comments.json from workspace and posts them with organic-looking
# rate limiting: random jitter between comments, breathing pauses after sustained
# activity, and exponential backoff on rate-limit errors.
#
# Saves progress to comment-progress.json for resume support.
#
# NOTE on resume safety (C4): If the script crashes between posting a comment
# and saving progress, the same comment may be re-posted on resume. GitHub does
# not deduplicate comments. Progress is saved immediately after each successful
# post to minimize this window.

set -euo pipefail

REPO="${1:?Usage: post-comments.sh <owner/repo> <workspace_dir> [jitter_min] [jitter_max] [daily_max]}"
WORKSPACE="${2:?Usage: post-comments.sh <owner/repo> <workspace_dir> [jitter_min] [jitter_max] [daily_max]}"
JITTER_MIN="${3:-75}"
JITTER_MAX="${4:-135}"
DAILY_MAX="${5:-60}"

# Input validation
if ! [[ "$REPO" =~ ^[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$ ]]; then
  echo "Error: Invalid repo format. Expected 'owner/repo', got: $REPO" >&2
  exit 1
fi
if [ "$JITTER_MIN" -gt "$JITTER_MAX" ]; then
  echo "Error: jitter_min ($JITTER_MIN) must be <= jitter_max ($JITTER_MAX)" >&2
  exit 1
fi

PROGRESS_FILE="$WORKSPACE/comment-progress.json"
COMMENTS_FILE="$WORKSPACE/approved-comments.json"

if [ ! -f "$COMMENTS_FILE" ]; then
  echo "Error: $COMMENTS_FILE not found. Run the analysis first." >&2
  exit 1
fi

TOTAL=$(jq 'length' "$COMMENTS_FILE")
echo "=== Cross-Ref Comment Poster ==="
echo "Repo: $REPO"
echo "Total comments: $TOTAL"
echo "Rate: 1 comment per ${JITTER_MIN}-${JITTER_MAX}s (jitter)"
echo "Daily max: $DAILY_MAX"
echo ""

# ─── Resume support ──────────────────────────────────────────────────────
START_INDEX=0
DAY_COUNT=0
TODAY=$(date -u +%Y-%m-%d)

if [ -f "$PROGRESS_FILE" ]; then
  PREV_DAY=$(jq -r '.day_start_utc // ""' "$PROGRESS_FILE")
  if [ "$PREV_DAY" = "$TODAY" ]; then
    DAY_COUNT=$(jq '.day_count // 0' "$PROGRESS_FILE")
    echo "Resuming: $DAY_COUNT comments already posted today"
  else
    echo "New day — resetting daily counter"
    DAY_COUNT=0
  fi
  START_INDEX=$(jq '.completed // 0' "$PROGRESS_FILE")
  echo "Starting from index: $START_INDEX"

  # Grace period on resume after rate limit
  if jq -e '.error' "$PROGRESS_FILE" > /dev/null 2>&1; then
    echo "Previous run was rate-limited. Starting with 5-minute grace period..."
    sleep 300
  fi
fi

if [ "$DAY_COUNT" -ge "$DAILY_MAX" ]; then
  echo "Daily limit reached ($DAILY_MAX). Try again tomorrow."
  echo "Remaining: $((TOTAL - START_INDEX)) comments"
  exit 0
fi

# ─── Helper: save progress ───────────────────────────────────────────────
save_progress() {
  local completed="$1"
  local remaining="$2"
  local error="${3:-}"

  local args=(
    --argjson total "$TOTAL"
    --argjson completed "$completed"
    --argjson remaining "$remaining"
    --argjson day_count "$DAY_COUNT"
    --arg day_start_utc "$TODAY"
    --arg last_commented_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  )
  local tmp="${PROGRESS_FILE}.tmp"
  if [ -n "$error" ]; then
    args+=(--arg error "$error")
    jq -n "${args[@]}" '{total_planned: $total, completed: $completed, remaining: $remaining,
      day_count: $day_count, day_start_utc: $day_start_utc,
      last_commented_at: $last_commented_at, error: $error}' > "$tmp"
  else
    jq -n "${args[@]}" '{total_planned: $total, completed: $completed, remaining: $remaining,
      day_count: $day_count, day_start_utc: $day_start_utc,
      last_commented_at: $last_commented_at}' > "$tmp"
  fi
  mv "$tmp" "$PROGRESS_FILE"
}

# ─── Helper: jitter sleep ────────────────────────────────────────────────
jitter_sleep() {
  local min_secs="${1:-$JITTER_MIN}"
  local max_secs="${2:-$JITTER_MAX}"
  local range=$((max_secs - min_secs + 1))
  local sleep_time=$((RANDOM % range + min_secs))
  echo "  ⏳ Waiting ${sleep_time}s (jitter: ${min_secs}-${max_secs}s)..."
  sleep "$sleep_time"
}

# ─── Helper: exponential backoff ─────────────────────────────────────────
backoff_sleep() {
  local attempt="$1"
  # Progression: attempt 2→2min, 3→4min, 4→8min, 5→30min (cap)
  local base=120   # 2 minutes
  local cap=1800   # 30 minutes
  local wait=$((base * (2 ** (attempt - 2))))
  if [ "$wait" -gt "$cap" ]; then wait=$cap; fi
  echo "  ⏳ Backoff: ${wait}s (~$((wait / 60))min) before retry $attempt of 5..."
  sleep "$wait"
}

# ─── Helper: breathing pause ─────────────────────────────────────────────
breathing_pause() {
  local pause_secs=$((RANDOM % 421 + 480))  # 480-900s (8-15 min)
  echo ""
  echo "  🫁 Breathing pause: ${pause_secs}s (~$((pause_secs / 60)) min) after $SESSION_COUNT comments this session"
  sleep "$pause_secs"
  echo "  🫁 Resuming..."
  echo ""
}

# ─── Post comments ───────────────────────────────────────────────────────
SESSION_COUNT=0
SKIP_COUNT=0
NEXT_BREATHING=$((RANDOM % 21 + 30))  # 30-50 comments before first pause

for ((i=START_INDEX; i<TOTAL; i++)); do
  if [ "$DAY_COUNT" -ge "$DAILY_MAX" ]; then
    echo ""
    echo "Daily limit reached ($DAILY_MAX comments)."
    echo "Remaining: $((TOTAL - i)) comments"
    echo "Resume tomorrow to continue."
    save_progress "$i" "$((TOTAL - i))"
    exit 0
  fi

  # Extract comment details
  ISSUE_NUM=$(jq -r ".[$i].target_number" "$COMMENTS_FILE")
  BODY=$(jq -r ".[$i].body" "$COMMENTS_FILE")
  TYPE=$(jq -r ".[$i].type" "$COMMENTS_FILE")

  # C3: validate fields before posting
  if [ -z "$ISSUE_NUM" ] || [ "$ISSUE_NUM" = "null" ]; then
    echo "  Skipping index $i: missing target_number"
    SKIP_COUNT=$((SKIP_COUNT + 1))
    continue
  fi
  if [ -z "$BODY" ] || [ "$BODY" = "null" ]; then
    echo "  Skipping index $i: empty body"
    SKIP_COUNT=$((SKIP_COUNT + 1))
    continue
  fi
  if [ "${#BODY}" -gt 65536 ]; then
    echo "  Skipping index $i: body exceeds GitHub 65536 char limit (${#BODY} chars)"
    SKIP_COUNT=$((SKIP_COUNT + 1))
    continue
  fi

  echo "[$((i + 1))/$TOTAL] Commenting on #$ISSUE_NUM ($TYPE)..."

  # Post the comment with exponential backoff on rate-limit failure
  POST_SUCCESS=false
  for attempt in 1 2 3 4 5; do
    # Backoff before retry attempts (not before the first try)
    if [ "$attempt" -gt 1 ]; then
      backoff_sleep "$attempt"
    fi

    if gh api "repos/$REPO/issues/$ISSUE_NUM/comments" -f body="$BODY" > /dev/null 2>"$WORKSPACE/post-stderr.log"; then
      if [ "$attempt" -eq 1 ]; then
        echo "  ✓ Posted"
      else
        echo "  ✓ Posted (attempt $attempt)"
      fi
      POST_SUCCESS=true
      break
    else
      STDERR_CONTENT=$(cat "$WORKSPACE/post-stderr.log")
      echo "  ✗ Failed (attempt $attempt of 5)" >&2
      echo "  $STDERR_CONTENT" >&2
      # Only retry on rate-limit errors; skip permanently-failing comments
      if ! echo "$STDERR_CONTENT" | grep -qiE "rate.limit|secondary|abuse|429|403"; then
        echo "  ⤳ Non-retriable error, skipping #$ISSUE_NUM"
        SKIP_COUNT=$((SKIP_COUNT + 1))
        break
      fi
    fi
  done

  if [ "$POST_SUCCESS" = false ]; then
    # Check if we exhausted all retries (rate-limit case)
    if [ "$attempt" -eq 5 ]; then
      echo "  ✗ All 5 attempts failed. Saving progress and stopping."
      save_progress "$i" "$((TOTAL - i))" "Rate limited on #$ISSUE_NUM after 5 attempts"
      exit 1
    fi
    # Non-retriable error — already skipped above, continue to next comment
    continue
  fi

  DAY_COUNT=$((DAY_COUNT + 1))
  SESSION_COUNT=$((SESSION_COUNT + 1))

  # Save progress immediately after each successful post
  save_progress "$((i + 1))" "$((TOTAL - i - 1))"

  # Breathing pause after sustained commenting
  if [ "$SESSION_COUNT" -ge "$NEXT_BREATHING" ]; then
    if [ "$((i + 1))" -lt "$TOTAL" ] && [ "$DAY_COUNT" -lt "$DAILY_MAX" ]; then
      breathing_pause
      NEXT_BREATHING=$((SESSION_COUNT + RANDOM % 21 + 30))  # re-randomize
    fi
  fi

  # Jitter sleep between comments (skip after last comment)
  if [ "$((i + 1))" -lt "$TOTAL" ] && [ "$DAY_COUNT" -lt "$DAILY_MAX" ]; then
    jitter_sleep
  fi
done

echo ""
echo "=== Done ==="
echo "Total entries: $TOTAL"
echo "Posted: $SESSION_COUNT"
if [ "$SKIP_COUNT" -gt 0 ]; then
  echo "Skipped: $SKIP_COUNT (invalid or non-retriable)"
fi
