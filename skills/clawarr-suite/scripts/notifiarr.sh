#!/usr/bin/env bash
# notifiarr.sh - Notifiarr notification management
# Usage: notifiarr.sh <command> [args...]
# Requires: CLAWARR_HOST (port 5454), NOTIFIARR_KEY

set -euo pipefail

HOST="${CLAWARR_HOST:-}"
API_KEY="${NOTIFIARR_KEY:-}"
BASE_URL=""
PORT="${NOTIFIARR_PORT:-5454}"

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
  if [[ -n "$API_KEY" ]]; then
    curl -sf -X "$method" \
      -H "x-api-key: ${API_KEY}" \
      -H "Content-Type: application/json" \
      "${BASE_URL}/api${endpoint}" "$@" 2>/dev/null
  else
    curl -sf -X "$method" \
      -H "Content-Type: application/json" \
      "${BASE_URL}/api${endpoint}" "$@" 2>/dev/null
  fi
}

cmd_status() {
  echo "🔔 Notifiarr Status"
  echo ""
  if curl -sf -o /dev/null "${BASE_URL}" 2>/dev/null; then
    echo "  ✅ Running on ${BASE_URL}"
  else
    echo "  ❌ Not reachable on ${BASE_URL}"
    return
  fi

  # Check version/status
  local info
  info=$(api GET "/version" 2>/dev/null || echo "{}")
  local version
  version=$(echo "$info" | jq -r '.version // "unknown"' 2>/dev/null)
  echo "  Version: ${version}"

  # Check configured services
  local config
  config=$(api GET "/config" 2>/dev/null || echo "{}")
  echo ""
  echo "  Configured integrations:"

  # Check each *arr service
  for svc in sonarr radarr lidarr readarr prowlarr; do
    local svc_url
    svc_url=$(echo "$config" | jq -r ".${svc}[0].url // empty" 2>/dev/null)
    if [[ -n "$svc_url" ]]; then
      echo "    ✅ ${svc} (${svc_url})"
    fi
  done

  # Check Plex
  local plex_url
  plex_url=$(echo "$config" | jq -r '.plex.url // empty' 2>/dev/null)
  if [[ -n "$plex_url" ]]; then
    echo "    ✅ Plex (${plex_url})"
  fi
}

cmd_triggers() {
  echo "⚡ Notification Triggers"
  echo ""
  local data
  data=$(api GET "/triggers" 2>/dev/null)
  if [[ -z "$data" || "$data" == "null" ]]; then
    echo "  Configure triggers in the Notifiarr web UI at ${BASE_URL}"
    return
  fi
  echo "$data" | jq -r 'to_entries[] | "  \(.key): \(.value)"' 2>/dev/null || echo "  Check web UI for trigger config"
}

cmd_test() {
  local channel="${1:-}"
  echo "🧪 Testing Notification Delivery..."
  echo ""
  if [[ -n "$channel" ]]; then
    local result
    result=$(api POST "/notification/test" -d "{\"channel\": \"${channel}\"}" 2>/dev/null)
    if [[ $? -eq 0 ]]; then
      echo "  ✅ Test notification sent to ${channel}"
    else
      echo "  ❌ Failed to send test notification" >&2
    fi
  else
    echo "  Sending test to all configured channels..."
    api POST "/notification/test" -d '{}' 2>/dev/null && echo "  ✅ Test sent" || echo "  ❌ Failed" >&2
  fi
}

cmd_services() {
  echo "🔗 Connected Services"
  echo ""
  local data
  data=$(api GET "/services" 2>/dev/null || echo "{}")
  if [[ "$data" == "{}" || -z "$data" ]]; then
    echo "  No services data. Configure in web UI."
    return
  fi
  echo "$data" | jq -r 'to_entries[] | "  \(.key): \(if .value.enabled then "✅" else "❌" end) \(.value.name // .key)"' 2>/dev/null
}

cmd_logs() {
  echo "📋 Notifiarr Recent Notifications"
  echo ""
  local data
  data=$(api GET "/logs?count=20" 2>/dev/null || echo "[]")
  if [[ "$data" == "[]" || -z "$data" ]]; then
    echo "  No recent notifications"
    return
  fi
  echo "$data" | jq -r '.[:20] | .[] | "  [\(.timestamp // .time)] \(.event // .message)"' 2>/dev/null || echo "  Check container logs for notification history"
}

cmd_config() {
  echo "⚙️ Notifiarr Configuration Summary"
  echo ""
  echo "  Web UI: ${BASE_URL}"
  echo ""
  echo "  To configure Notifiarr:"
  echo "  1. Open ${BASE_URL} in your browser"
  echo "  2. Add Discord webhook URL in Settings"
  echo "  3. Add *arr service URLs and API keys"
  echo "  4. Enable notification triggers"
  echo ""
  echo "  Environment variables for this script:"
  echo "    CLAWARR_HOST=${HOST}"
  echo "    NOTIFIARR_KEY=${API_KEY:-<not set>}"
  echo "    NOTIFIARR_PORT=${PORT}"
}

usage() {
  cat <<EOF
Usage: notifiarr.sh <command> [args...]

Commands:
  status                Check Notifiarr status & integrations
  triggers              List notification triggers
  services              Show connected services
  test [channel]        Send test notification
  config                Configuration summary
  logs                  Recent notification log

Environment:
  CLAWARR_HOST          Host IP/hostname
  NOTIFIARR_KEY         Notifiarr API key
  NOTIFIARR_PORT        Port (default: 5454)

Setup:
  Notifiarr needs a Discord webhook to send notifications.
  Configure in the web UI: http://<host>:5454
EOF
}

init

case "${1:-}" in
  status) cmd_status ;;
  triggers) cmd_triggers ;;
  services) cmd_services ;;
  test) shift; cmd_test "${1:-}" ;;
  config) cmd_config ;;
  logs) cmd_logs ;;
  *) usage ;;
esac
