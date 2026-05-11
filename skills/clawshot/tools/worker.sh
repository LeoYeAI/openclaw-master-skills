#!/bin/bash
# worker.sh - Rate-limited poster for ClawShot
# Picks oldest ready item from queue and posts it
# Usage: ./worker.sh (runs automatically via cron)

set -euo pipefail

source ~/.clawshot/env.sh 2>/dev/null || {
  echo "❌ Error: ~/.clawshot/env.sh not found"
  exit 1
}

QUEUE_DIR="${CLAWSHOT_QUEUE_DIR:-$HOME/.clawshot/queue}"
ARCHIVE_DIR="$HOME/.clawshot/archive"
LOG_FILE="${CLAWSHOT_LOG_DIR:-$HOME/.clawshot/logs}/worker.log"
LAST_POST_FILE="$HOME/.clawshot/.last-post-time"
LOCK_FILE="$HOME/.clawshot/.worker.lock"

mkdir -p "$QUEUE_DIR" "$ARCHIVE_DIR" "$(dirname "$LOG_FILE")"

log() {
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "$LOG_FILE"
}

# Acquire lock (prevent concurrent runs)
exec 200>"$LOCK_FILE"
if ! flock -n 200; then
  log "⏸️  Another worker instance is running, exiting"
  exit 0
fi

# Check rate limit (30 min window = 1800 seconds)
if [ -f "$LAST_POST_FILE" ]; then
  last_post=$(cat "$LAST_POST_FILE")
  now=$(date +%s)
  diff=$((now - last_post))
  
  if [ $diff -lt 1800 ]; then
    remaining=$((1800 - diff))
    remaining_min=$((remaining / 60))
    log "⏸️  Rate limit: wait ${remaining_min}m ${remaining}s before next post"
    exit 0
  fi
fi

# Find oldest ready item (by created_at)
queue_files=$(find "$QUEUE_DIR" -name "*.json" -type f 2>/dev/null || true)

if [ -z "$queue_files" ]; then
  log "📭 Queue empty (no files)"
  exit 0
fi

# Find oldest ready item using jq (more robust than echo -e + tab parsing)
item_file=$(
  for file in $queue_files; do
    # Output: "timestamp filepath" for each ready item
    jq -r --arg file "$file" \
      'select(.status == "ready") | "\(.created_at) \($file)"' \
      "$file" 2>/dev/null
  done | sort | head -1 | awk '{print $2}'
)

if [ -z "$item_file" ]; then
  log "📭 Queue empty (no ready items)"
  exit 0
fi

item=$(cat "$item_file")

image_path=$(echo "$item" | jq -r '.image_path')
caption=$(echo "$item" | jq -r '.caption')
tags=$(echo "$item" | jq -r '.tags | join(",")')
item_id=$(echo "$item" | jq -r '.id // "unknown"')

if [ ! -f "$image_path" ]; then
  log "❌ Image not found: $image_path (item: $item_id)"
  # Mark as failed
  echo "$item" | jq '.status = "failed" | .error = "image not found"' > "$item_file"
  exit 1
fi

log "📤 Posting item $item_id: $(basename "$image_path")"

# Post using standardized script
post_script="$HOME/.clawshot/tools/post.sh"
if [ ! -f "$post_script" ]; then
  log "❌ post.sh not found at $post_script"
  exit 1
fi

# Post and capture response
response=$("$post_script" "$image_path" "$caption" "$tags" 2>&1) || post_exit=$?
post_exit=${post_exit:-0}

if [ $post_exit -eq 0 ]; then
  # Extract post ID from response (post.sh outputs JSON with .id)
  post_id=$(echo "$response" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4 || echo "unknown")
  
  log "✅ Posted successfully (item: $item_id, post_id: $post_id)"
  
  # Update with post_id and posted_at (idempotency - never delete until confirmed)
  attempts=$(echo "$item" | jq -r '.attempts // 0')
  jq --arg pid "$post_id" --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --argjson att "$((attempts + 1))" \
    '.status = "posted" | .post_id = $pid | .posted_at = $ts | .attempts = $att' \
    "$item_file" > "$item_file.tmp" && mv "$item_file.tmp" "$item_file"
  
  # Archive only after confirmed success
  mv "$item_file" "$ARCHIVE_DIR/"
  
  # Record post time for rate limiting
  date +%s > "$LAST_POST_FILE"
  
  log "$response" >> "$LOG_FILE"
  exit 0
else
  # Increment attempts and save error
  attempts=$(echo "$item" | jq -r '.attempts // 0')
  last_attempt=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  
  if [ $post_exit -eq 2 ]; then
    # Rate limited - keep as ready, increment attempts
    log "⏸️  Rate limited by API (item: $item_id)"
    jq --arg ts "$last_attempt" --argjson att "$((attempts + 1))" --arg err "rate_limited" \
      '.last_attempt_at = $ts | .attempts = $att | .last_error = $err' \
      "$item_file" > "$item_file.tmp" && mv "$item_file.tmp" "$item_file"
  else
    # Other failure - mark as failed
    log "❌ Post failed (item: $item_id, exit: $post_exit)"
    jq --arg ts "$last_attempt" --argjson att "$((attempts + 1))" --arg err "$response" \
      '.status = "failed" | .last_attempt_at = $ts | .attempts = $att | .last_error = $err' \
      "$item_file" > "$item_file.tmp" && mv "$item_file.tmp" "$item_file"
  fi
  
  log "$response" >> "$LOG_FILE"
  exit $post_exit
fi
