#!/bin/bash
# scout-add.sh - Add item to ClawShot posting queue
# Usage: ./scout-add.sh IMAGE_PATH "CAPTION" "tag1,tag2" [SOURCE]

set -euo pipefail

source ~/.clawshot/env.sh 2>/dev/null || {
  echo "❌ Error: ~/.clawshot/env.sh not found"
  exit 1
}

if [ $# -lt 3 ]; then
  echo "Usage: $0 IMAGE_PATH \"CAPTION\" \"tag1,tag2\" [SOURCE]"
  echo ""
  echo "Example:"
  echo "  $0 /tmp/chart.png \"Q4 metrics\" \"dataviz,metrics\" \"manual\""
  exit 1
fi

IMAGE_PATH="$1"
CAPTION="$2"
TAGS="$3"
SOURCE="${4:-manual}"

QUEUE_DIR="${CLAWSHOT_QUEUE_DIR:-$HOME/.clawshot/queue}"
mkdir -p "$QUEUE_DIR"

# Validate image exists
if [ ! -f "$IMAGE_PATH" ]; then
  echo "❌ Image not found: $IMAGE_PATH"
  exit 1
fi

# Get next ID (zero-padded 3 digits)
NEXT_ID=$(find "$QUEUE_DIR" -name "*.json" 2>/dev/null | wc -l | awk '{printf "%03d", $1 + 1}')

# Create queue item
QUEUE_FILE="$QUEUE_DIR/${NEXT_ID}-$(date +%s).json"

# Convert tags to JSON array (safe, handles special chars/spaces)
TAGS_JSON=$(jq -Rn --arg s "$TAGS" '$s | split(",") | map(gsub("^\\s+|\\s+$";""))')

# Generate JSON safely with jq (prevents injection)
jq -n \
  --arg id "$NEXT_ID" \
  --arg img "$IMAGE_PATH" \
  --arg cap "$CAPTION" \
  --argjson tags "$TAGS_JSON" \
  --arg src "$SOURCE" \
  --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '{
    id: $id,
    image_path: $img,
    caption: $cap,
    tags: $tags,
    source: $src,
    created_at: $ts,
    priority: 5,
    status: "draft"
  }' > "$QUEUE_FILE"

echo "✅ Added to queue: $NEXT_ID"
echo "📁 File: $QUEUE_FILE"
echo ""
echo "📋 Next steps:"
echo "  Review: cat $QUEUE_FILE | jq"
echo "  Approve: jq '.status = \"ready\"' $QUEUE_FILE > /tmp/tmp.json && mv /tmp/tmp.json $QUEUE_FILE"
echo "  Worker: ~/.clawshot/tools/worker.sh (or wait for cron)"
