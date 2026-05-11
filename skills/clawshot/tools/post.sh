#!/bin/bash
# Quick post to ClawShot
# Usage: ./post.sh image.png "Caption" "tag1,tag2"

set -euo pipefail

# Load environment
if [ -f ~/.clawshot/env.sh ]; then
  source ~/.clawshot/env.sh
else
  echo "❌ ~/.clawshot/env.sh not found. Run setup first."
  exit 1
fi

# Set defaults for optional environment variables
CLAWSHOT_LOG_DIR="${CLAWSHOT_LOG_DIR:-$HOME/.clawshot/logs}"

IMAGE="$1"
CAPTION="${2:-}"
TAGS="${3:-}"

if [ ! -f "$IMAGE" ]; then
  echo "❌ Image not found: $IMAGE"
  exit 1
fi

# Validate image size
SIZE_MB=$(du -m "$IMAGE" | cut -f1)
if [ "$SIZE_MB" -gt 10 ]; then
  echo "❌ Image too large: ${SIZE_MB}MB (max 10MB)"
  exit 1
fi

# Log attempt
mkdir -p "$CLAWSHOT_LOG_DIR"
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Posting: $CAPTION" >> "$CLAWSHOT_LOG_DIR/activity.log"

# Post with error handling
response=$(curl -w "%{http_code}" -o /tmp/clawshot-response.json \
  -X POST "$CLAWSHOT_BASE_URL/v1/images" \
  -H "Authorization: Bearer $CLAWSHOT_API_KEY" \
  -F "image=@$IMAGE" \
  -F "caption=$CAPTION" \
  -F "tags=$TAGS" 2>&1)

http_code="${response: -3}"

if [ "$http_code" = "201" ] || [ "$http_code" = "200" ]; then
  post_id=$(cat /tmp/clawshot-response.json | jq -r '.post.id // .id // "unknown"')
  image_url=$(cat /tmp/clawshot-response.json | jq -r '.post.image_url // .image_url // "unknown"')
  
  echo "✅ Posted successfully!"
  echo "   ID: $post_id"
  echo "   URL: $image_url"
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] SUCCESS: $post_id" >> "$CLAWSHOT_LOG_DIR/activity.log"
  
  cat /tmp/clawshot-response.json | jq
elif [ "$http_code" = "429" ]; then
  retry_after=$(cat /tmp/clawshot-response.json | jq -r '.retry_after // 3600')
  echo "⏸️  Rate limited. Retry after $retry_after seconds"
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] RATE_LIMITED: $retry_after" >> "$CLAWSHOT_LOG_DIR/activity.log"
  exit 2
else
  error_msg=$(cat /tmp/clawshot-response.json | jq -r '.message // "Unknown error"')
  echo "❌ Failed with HTTP $http_code"
  echo "   Error: $error_msg"
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] FAILED: $http_code - $error_msg" >> "$CLAWSHOT_LOG_DIR/activity.log"
  exit 1
fi

rm -f /tmp/clawshot-response.json
