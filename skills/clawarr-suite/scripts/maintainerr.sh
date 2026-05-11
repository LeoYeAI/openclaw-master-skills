#!/usr/bin/env bash
# maintainerr.sh - Maintainerr library cleanup management
# Usage: maintainerr.sh <command> [args...]
# Requires: CLAWARR_HOST (port 6246)

set -euo pipefail

HOST="${CLAWARR_HOST:-}"
BASE_URL=""
PORT="${MAINTAINERR_PORT:-6246}"

init() {
  if [[ -z "$HOST" ]]; then
    echo "Error: CLAWARR_HOST not set" >&2; exit 1
  fi
  BASE_URL="http://${HOST}:${PORT}"
}

api() {
  local method="${1:-GET}"
  local endpoint="$2"
  shift 2
  curl -sf -X "$method" \
    -H "Content-Type: application/json" \
    "${BASE_URL}/api${endpoint}" "$@" 2>/dev/null
}

cmd_status() {
  echo "🧹 Maintainerr Status"
  echo ""
  if curl -sf -o /dev/null "${BASE_URL}" 2>/dev/null; then
    echo "  ✅ Running on ${BASE_URL}"
  else
    echo "  ❌ Not reachable on ${BASE_URL}"
    return
  fi

  # Get rules summary
  local rules
  rules=$(api GET "/rules" 2>/dev/null || echo "[]")
  local count
  count=$(echo "$rules" | jq 'length' 2>/dev/null || echo "0")
  echo "  Rules: ${count} configured"

  # Get collections
  local collections
  collections=$(api GET "/collections" 2>/dev/null || echo "[]")
  local col_count
  col_count=$(echo "$collections" | jq 'length' 2>/dev/null || echo "0")
  echo "  Collections: ${col_count} managed"
}

cmd_rules() {
  echo "📋 Maintainerr Rules"
  echo ""
  local data
  data=$(api GET "/rules")
  local count
  count=$(echo "$data" | jq 'length')
  if [[ "$count" == "0" ]]; then
    echo "  No rules configured. Create rules in the web UI at ${BASE_URL}"
    return
  fi
  echo "$data" | jq -r '.[] | "  [\(.id)] \(.name) - \(if .isActive then "✅ Active" else "⏸️ Paused" end) | Media: \(.mediaCount // 0) items"'
}

cmd_collections() {
  echo "📚 Maintainerr Collections"
  echo ""
  local data
  data=$(api GET "/collections")
  local count
  count=$(echo "$data" | jq 'length')
  if [[ "$count" == "0" ]]; then
    echo "  No collections. Collections are created by rules."
    return
  fi
  echo "$data" | jq -r '.[] | "  [\(.id)] \(.title) - \(.mediaCount // 0) items | Delete after: \(.deleteAfterDays // "never") days"'
}

cmd_run() {
  local rule_id="${1:-}"
  if [[ -z "$rule_id" ]]; then
    echo "Running all active rules..."
    if api POST "/rules/run" -d '{}' >/dev/null 2>&1; then
      echo "✅ Rule execution triggered"
    else
      echo "❌ Failed to trigger rules" >&2
    fi
  else
    echo "Running rule ${rule_id}..."
    if api POST "/rules/${rule_id}/run" -d '{}' >/dev/null 2>&1; then
      echo "✅ Rule ${rule_id} triggered"
    else
      echo "❌ Failed to trigger rule ${rule_id}" >&2
    fi
  fi
}

cmd_exclude() {
  local media_id="${1:-}"
  local rule_id="${2:-}"
  if [[ -z "$media_id" || -z "$rule_id" ]]; then
    echo "Usage: maintainerr.sh exclude <media_id> <rule_id>" >&2; exit 1
  fi
  if api POST "/rules/${rule_id}/exclusion" -d "{\"plexId\": ${media_id}}" >/dev/null 2>&1; then
    echo "✅ Excluded media ${media_id} from rule ${rule_id}"
  else
    echo "❌ Failed to exclude" >&2
  fi
}

cmd_media() {
  local rule_id="${1:-}"
  if [[ -z "$rule_id" ]]; then
    echo "Usage: maintainerr.sh media <rule_id>" >&2; exit 1
  fi
  echo "📺 Media matched by rule ${rule_id}"
  echo ""
  local data
  data=$(api GET "/rules/${rule_id}/media")
  echo "$data" | jq -r '.[] | "  [\(.plexId)] \(.title) (\(.addDate // "unknown"))"'
}

cmd_logs() {
  echo "📋 Maintainerr Activity Log"
  echo ""
  local data
  data=$(api GET "/logs" 2>/dev/null || echo "[]")
  echo "$data" | jq -r '.[:20] | .[] | "  [\(.createdAt | split("T")[0])] \(.message)"' 2>/dev/null || echo "  No logs available via API. Check container logs."
}

usage() {
  cat <<EOF
Usage: maintainerr.sh <command> [args...]

Commands:
  status                Check Maintainerr status
  rules                 List cleanup rules
  collections           List managed collections
  run [rule_id]         Trigger rule execution (all or specific)
  media <rule_id>       Show media matched by a rule
  exclude <media_id> <rule_id>  Exclude media from a rule
  logs                  View activity log

Environment:
  CLAWARR_HOST          Host IP/hostname
  MAINTAINERR_PORT      Port (default: 6246)

Common Rules to Create (via web UI):
  - Delete movies unwatched for 180+ days
  - Delete shows with all episodes watched 90+ days ago
  - Delete movies rated below 5.0 and unwatched for 60+ days
  - Keep movies in specific collections regardless
EOF
}

init

case "${1:-}" in
  status) cmd_status ;;
  rules) cmd_rules ;;
  collections) cmd_collections ;;
  run) shift; cmd_run "${1:-}" ;;
  media) shift; cmd_media "${1:-}" ;;
  exclude) shift; cmd_exclude "${1:-}" "${2:-}" ;;
  logs) cmd_logs ;;
  *) usage ;;
esac
