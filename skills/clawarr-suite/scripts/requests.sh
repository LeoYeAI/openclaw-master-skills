#!/usr/bin/env bash
# requests.sh - Overseerr request management
# Usage: requests.sh <command> [options]
#
# Commands:
#   list [status]     - List requests (pending|approved|available|all, default: all)
#   approve <id>      - Approve a request
#   deny <id> [reason] - Deny a request with optional reason
#   info <id>         - Show request details
#   stats             - Request statistics

set -euo pipefail

HOST="${CLAWARR_HOST:-}"
OVERSEERR_KEY="${OVERSEERR_KEY:-}"

if [[ -z "$HOST" ]]; then
  echo "❌ Error: CLAWARR_HOST not set"
  exit 1
fi

if [[ -z "$OVERSEERR_KEY" ]]; then
  echo "❌ Error: OVERSEERR_KEY not set"
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

# Helper: call Overseerr API
overseerr_api() {
  local method=$1
  local endpoint=$2
  local data="${3:-}"
  
  local url="http://${HOST}:5055/api/v1${endpoint}"
  
  if [[ "$method" == "GET" ]]; then
    curl -sf -H "X-Api-Key: $OVERSEERR_KEY" "$url"
  elif [[ "$method" == "POST" ]]; then
    curl -sf -X POST -H "X-Api-Key: $OVERSEERR_KEY" -H "Content-Type: application/json" -d "$data" "$url"
  fi
}

# Command: list
cmd_list() {
  local status="${1:-all}"
  local filter=""
  
  case "$status" in
    pending)    filter="&filter=pending" ;;
    approved)   filter="&filter=approved" ;;
    available)  filter="&filter=available" ;;
    all)        filter="" ;;
    *)
      echo "❌ Invalid status. Use: pending, approved, available, or all"
      exit 1
      ;;
  esac
  
  echo "📋 Requests - $(echo "$status" | tr '[:lower:]' '[:upper:]')"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  local requests
  requests=$(overseerr_api GET "/request?take=50&skip=0${filter}")
  
  if [[ $(echo "$requests" | jq '.results | length') -eq 0 ]]; then
    echo "  No requests found"
    echo ""
    return
  fi
  
  echo "$requests" | jq -r '.results[] | 
    "[ID:\(.id)] \(.media.tmdbId // .media.tvdbId) - \(.type | ascii_upcase) - \(.media.title // .media.name // "Unknown")
    Status: \(if .media.status == 5 then "✅ Available" elif .media.status == 4 then "⏬ Downloading" elif .media.status == 3 then "🔍 Processing" elif .media.status == 2 then "⏳ Pending" else "❓ Unknown" end)
    Requested by: \(.requestedBy.displayName // .requestedBy.email)
    "' | sed 's/^/  /'
  
  local total
  total=$(echo "$requests" | jq '.pageInfo.results')
  echo "  Total: $total"
  echo ""
}

# Command: approve
cmd_approve() {
  local id="$1"
  
  if [[ -z "$id" ]]; then
    echo "❌ Error: Request ID required"
    echo "Usage: $0 approve <id>"
    exit 1
  fi
  
  echo "✅ Approving request ID: $id"
  
  if overseerr_api POST "/request/$id/approve" '{}' >/dev/null 2>&1; then
    echo "✅ Request approved successfully"
  else
    echo "❌ Failed to approve request"
  fi
}

# Command: deny
cmd_deny() {
  local id="$1"
  local reason="${2:-No reason provided}"
  
  if [[ -z "$id" ]]; then
    echo "❌ Error: Request ID required"
    echo "Usage: $0 deny <id> [reason]"
    exit 1
  fi
  
  echo "❌ Denying request ID: $id"
  echo "   Reason: $reason"
  
  local data
  data=$(jq -n --arg reason "$reason" '{message: $reason}')
  
  if overseerr_api POST "/request/$id/decline" "$data" >/dev/null 2>&1; then
    echo "✅ Request denied successfully"
  else
    echo "❌ Failed to deny request"
  fi
}

# Command: info
cmd_info() {
  local id="$1"
  
  if [[ -z "$id" ]]; then
    echo "❌ Error: Request ID required"
    echo "Usage: $0 info <id>"
    exit 1
  fi
  
  echo "ℹ️  Request Details - ID: $id"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  local request
  request=$(overseerr_api GET "/request/$id")
  
  echo "$request" | jq -r '
    "Title: \(.media.title // .media.name // "Unknown")",
    "Type: \(.type | ascii_upcase)",
    "Status: \(
      if .media.status == 5 then "Available"
      elif .media.status == 4 then "Downloading"
      elif .media.status == 3 then "Processing"
      elif .media.status == 2 then "Pending"
      else "Unknown"
      end
    )",
    "Requested by: \(.requestedBy.displayName // .requestedBy.email)",
    "Requested on: \(.createdAt | split("T")[0])",
    "TMDB/TVDB ID: \(.media.tmdbId // .media.tvdbId)",
    (if .seasons then "Seasons: \(.seasons | map(.seasonNumber) | join(", "))" else empty end),
    ""
  ' | sed 's/^/  /'
}

# Command: stats
cmd_stats() {
  echo "📊 Request Statistics"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  # Get all requests
  local all_requests
  all_requests=$(overseerr_api GET "/request?take=1000")
  
  local total
  total=$(echo "$all_requests" | jq '.results | length')
  
  local pending
  pending=$(echo "$all_requests" | jq '[.results[] | select(.media.status == 2)] | length')
  
  local processing
  processing=$(echo "$all_requests" | jq '[.results[] | select(.media.status == 3)] | length')
  
  local available
  available=$(echo "$all_requests" | jq '[.results[] | select(.media.status == 5)] | length')
  
  local movies
  movies=$(echo "$all_requests" | jq '[.results[] | select(.type == "movie")] | length')
  
  local tv
  tv=$(echo "$all_requests" | jq '[.results[] | select(.type == "tv")] | length')
  
  echo "  Total Requests: $total"
  echo "  Pending: $pending"
  echo "  Processing: $processing"
  echo "  Available: $available"
  echo ""
  echo "  Movies: $movies"
  echo "  TV Shows: $tv"
  echo ""
  
  # Top requesters
  echo "  Top Requesters:"
  echo "$all_requests" | jq -r '.results[] | .requestedBy.displayName // .requestedBy.email' | \
    sort | uniq -c | sort -rn | head -5 | while read -r count user; do
      printf "    %-30s %5d requests\n" "$user" "$count"
    done
  
  echo ""
}

# Main command router
COMMAND="${1:-help}"

case "$COMMAND" in
  list)    cmd_list "${2:-all}" ;;
  approve) cmd_approve "${2:-}" ;;
  deny)    cmd_deny "${2:-}" "${3:-}" ;;
  info)    cmd_info "${2:-}" ;;
  stats)   cmd_stats ;;
  help|--help|-h) show_help ;;
  *)
    echo "❌ Unknown command: $COMMAND"
    echo "Run '$0 help' for usage"
    exit 1
    ;;
esac
