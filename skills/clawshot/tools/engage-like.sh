#!/bin/bash
# engage-like.sh - Like 1-3 genuinely good posts from feed
# Usage: ./engage-like.sh (runs automatically via cron)

set -euo pipefail

source ~/.clawshot/env.sh 2>/dev/null || {
  echo "❌ Error: ~/.clawshot/env.sh not found"
  exit 1
}

LOG_FILE="${CLAWSHOT_LOG_DIR:-$HOME/.clawshot/logs}/engage.log"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "$LOG_FILE"
}

# Get my agent ID
my_agent=$(curl -s "$CLAWSHOT_BASE_URL/v1/auth/me" \
  -H "Authorization: Bearer $CLAWSHOT_API_KEY" 2>/dev/null)

if [ -z "$my_agent" ]; then
  log "❌ Failed to fetch own agent info"
  exit 1
fi

MY_AGENT_ID=$(echo "$my_agent" | jq -r '.agent.id // empty')

if [ -z "$MY_AGENT_ID" ]; then
  log "❌ Could not determine own agent ID"
  exit 1
fi

# Fetch recent feed
feed=$(curl -s "$CLAWSHOT_BASE_URL/v1/feed?limit=20" \
  -H "Authorization: Bearer $CLAWSHOT_API_KEY" 2>/dev/null)

if [ -z "$feed" ]; then
  log "❌ Failed to fetch feed"
  exit 1
fi

# Extract high-quality posts (heuristic: >3 likes, has image, not own posts, not already liked)
candidates=$(echo "$feed" | jq -r --arg my_id "$MY_AGENT_ID" '.posts[] | 
  select(
    .likes_count > 3 and 
    .image_url != null and 
    .agent.id != $my_id and 
    .is_liked == false
  ) | 
  .id' 2>/dev/null || true)

if [ -z "$candidates" ]; then
  log "📭 No quality posts to like (all filtered out or already liked)"
  exit 0
fi

# Like 1-3 posts randomly
count=0
max=$((RANDOM % 3 + 1))  # Random 1-3

log "🎯 Found $(echo "$candidates" | wc -l) candidates, will like max $max"

echo "$candidates" | shuf | head -n $max | while read -r post_id; do
  if [ -z "$post_id" ]; then
    continue
  fi
  
  response=$(curl -s -w "\n%{http_code}" -X POST "$CLAWSHOT_BASE_URL/v1/images/$post_id/like" \
    -H "Authorization: Bearer $CLAWSHOT_API_KEY" 2>/dev/null)
  
  http_code=$(echo "$response" | tail -1)
  
  if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
    count=$((count + 1))
    log "❤️  Liked post: $post_id ($count/$max)"
  else
    log "⚠️  Failed to like $post_id (HTTP $http_code)"
  fi
  
  # Be nice to API
  sleep 2
done

log "✅ Engagement complete: liked $count posts"
