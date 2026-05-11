#!/usr/bin/env bash
# queue.sh - Show download queues across Sonarr/Radarr
# Usage: queue.sh

set -euo pipefail

HOST="${CLAWARR_HOST:-}"
SONARR_KEY="${SONARR_KEY:-}"
RADARR_KEY="${RADARR_KEY:-}"

if [[ -z "$HOST" ]]; then
  echo "Error: CLAWARR_HOST not set"
  echo ""
  echo "Usage:"
  echo "  export CLAWARR_HOST=192.168.1.100"
  echo "  export SONARR_KEY=abc123..."
  echo "  export RADARR_KEY=def456..."
  echo "  $0"
  exit 1
fi

if ! command -v jq &> /dev/null; then
  echo "❌ Error: jq is required but not installed"
  exit 1
fi

echo "📥 Download Queues"
echo ""

if [[ -n "$RADARR_KEY" ]]; then
  echo "=== Radarr Queue ==="
  
  queue=$(curl -sf -H "X-Api-Key: ${RADARR_KEY}" "http://${HOST}:7878/api/v3/queue" 2>/dev/null || echo '{"records":[]}')
  
  count=$(echo "$queue" | jq '.records | length')
  
  if [[ "$count" -eq 0 ]]; then
    echo "  (empty)"
  else
    echo "$queue" | jq -r '.records[] | "  • \(.title)\n    Status: \(.status) | Progress: \(.sizeleft / 1024 / 1024 | floor)MB left of \(.size / 1024 / 1024 | floor)MB\n    ETA: \(.timeleft // "Unknown")"'
  fi
  echo ""
fi

if [[ -n "$SONARR_KEY" ]]; then
  echo "=== Sonarr Queue ==="
  
  queue=$(curl -sf -H "X-Api-Key: ${SONARR_KEY}" "http://${HOST}:8989/api/v3/queue" 2>/dev/null || echo '{"records":[]}')
  
  count=$(echo "$queue" | jq '.records | length')
  
  if [[ "$count" -eq 0 ]]; then
    echo "  (empty)"
  else
    echo "$queue" | jq -r '.records[] | "  • \(.title)\n    Status: \(.status) | Progress: \(.sizeleft / 1024 / 1024 | floor)MB left of \(.size / 1024 / 1024 | floor)MB\n    ETA: \(.timeleft // "Unknown")"'
  fi
  echo ""
fi

if [[ -z "$RADARR_KEY" && -z "$SONARR_KEY" ]]; then
  echo "No API keys configured. Set RADARR_KEY and/or SONARR_KEY."
fi
