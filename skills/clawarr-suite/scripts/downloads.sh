#!/usr/bin/env bash
# downloads.sh - SABnzbd download client operations
# Usage: downloads.sh <command> [options]
#
# Commands:
#   active           - Currently downloading
#   speed            - Current download speed
#   history [count]  - Download history (default: 20)
#   pause            - Pause downloads
#   resume           - Resume downloads
#   queue            - Full queue details

set -euo pipefail

HOST="${CLAWARR_HOST:-}"
SABNZBD_KEY="${SABNZBD_KEY:-}"

if [[ -z "$HOST" ]]; then
  echo "❌ Error: CLAWARR_HOST not set"
  exit 1
fi

if [[ -z "$SABNZBD_KEY" ]]; then
  echo "❌ Error: SABNZBD_KEY not set"
  exit 1
fi

if ! command -v jq &> /dev/null; then
  echo "❌ Error: jq is required"
  exit 1
fi

show_help() {
  head -n 13 "$0" | grep "^#" | sed 's/^# \?//'
  exit 0
}

# Helper: call SABnzbd API
sabnzbd_api() {
  local mode=$1
  shift
  local params="$*"
  
  local url="http://${HOST}:38080/api?apikey=${SABNZBD_KEY}&mode=${mode}&output=json"
  if [[ -n "$params" ]]; then
    url="${url}&${params}"
  fi
  
  curl -sf "$url"
}

# Command: active
cmd_active() {
  echo "⬇️  Currently Downloading"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  local queue
  queue=$(sabnzbd_api "queue")
  
  local paused
  paused=$(echo "$queue" | jq -r '.queue.paused')
  local speed
  speed=$(echo "$queue" | jq -r '.queue.speed')
  local size_left
  size_left=$(echo "$queue" | jq -r '.queue.sizeleft')
  local time_left
  time_left=$(echo "$queue" | jq -r '.queue.timeleft')
  
  if [[ "$paused" == "true" ]]; then
    echo "  Status: ⏸️  PAUSED"
  else
    echo "  Status: ▶️  ACTIVE"
  fi
  
  echo "  Speed: $speed"
  echo "  Remaining: $size_left"
  echo "  ETA: $time_left"
  echo ""
  
  local slots
  slots=$(echo "$queue" | jq '.queue.slots | length')
  
  if [[ $slots -eq 0 ]]; then
    echo "  No active downloads"
  else
    echo "  Active Downloads:"
    echo "$queue" | jq -r '.queue.slots[] | 
      "    \(.filename)
      Size: \(.size) | Progress: \(.percentage)% | ETA: \(.timeleft)
      "' | sed 's/^/  /'
  fi
  
  echo ""
}

# Command: speed
cmd_speed() {
  echo "⚡ Download Speed"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  local queue
  queue=$(sabnzbd_api "queue")
  
  local speed
  speed=$(echo "$queue" | jq -r '.queue.speed')
  local kbps
  kbps=$(echo "$queue" | jq -r '.queue.kbpersec')
  
  echo "  Current Speed: $speed ($kbps KB/s)"
  
  local speed_limit
  speed_limit=$(echo "$queue" | jq -r '.queue.speedlimit')
  if [[ "$speed_limit" != "0" && "$speed_limit" != "null" ]]; then
    echo "  Speed Limit: $speed_limit KB/s"
  else
    echo "  Speed Limit: Unlimited"
  fi
  
  echo ""
}

# Command: history
cmd_history() {
  local count="${1:-20}"
  
  echo "📜 Download History (Last $count)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  local history
  history=$(sabnzbd_api "history" "limit=${count}")
  
  local slots
  slots=$(echo "$history" | jq '.history.slots | length')
  
  if [[ $slots -eq 0 ]]; then
    echo "  No download history"
    echo ""
    return
  fi
  
  echo "$history" | jq -r '.history.slots[] | 
    "  \(.name)
    Status: \(.status) | Size: \(.size) | Category: \(.category)
    Completed: \(.completed // "N/A")
    "' | sed 's/^/  /'
  
  echo ""
}

# Command: pause
cmd_pause() {
  echo "⏸️  Pausing downloads..."
  
  if sabnzbd_api "pause" >/dev/null 2>&1; then
    echo "✅ Downloads paused"
  else
    echo "❌ Failed to pause downloads"
  fi
}

# Command: resume
cmd_resume() {
  echo "▶️  Resuming downloads..."
  
  if sabnzbd_api "resume" >/dev/null 2>&1; then
    echo "✅ Downloads resumed"
  else
    echo "❌ Failed to resume downloads"
  fi
}

# Command: queue
cmd_queue() {
  echo "📋 Download Queue"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  local queue
  queue=$(sabnzbd_api "queue")
  
  local total_size
  total_size=$(echo "$queue" | jq -r '.queue.size')
  local size_left
  size_left=$(echo "$queue" | jq -r '.queue.sizeleft')
  local slots
  slots=$(echo "$queue" | jq '.queue.slots | length')
  
  echo "  Total Queue Size: $total_size"
  echo "  Remaining: $size_left"
  echo "  Items: $slots"
  echo ""
  
  if [[ $slots -eq 0 ]]; then
    echo "  Queue is empty"
    echo ""
    return
  fi
  
  echo "$queue" | jq -r '.queue.slots[] | 
    "  [\(.nzo_id | .[0:8])] \(.filename)
    Size: \(.size) | Downloaded: \(.mb) MB / \(.size)
    Progress: \(.percentage)% | ETA: \(.timeleft)
    Priority: \(.priority) | Category: \(.cat)
    "' | sed 's/^/  /'
  
  echo ""
}

# Main command router
COMMAND="${1:-help}"

case "$COMMAND" in
  active)  cmd_active ;;
  speed)   cmd_speed ;;
  history) cmd_history "${2:-20}" ;;
  pause)   cmd_pause ;;
  resume)  cmd_resume ;;
  queue)   cmd_queue ;;
  help|--help|-h) show_help ;;
  *)
    echo "❌ Unknown command: $COMMAND"
    echo "Run '$0 help' for usage"
    exit 1
    ;;
esac
