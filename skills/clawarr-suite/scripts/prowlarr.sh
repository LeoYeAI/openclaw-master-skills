#!/usr/bin/env bash
# prowlarr.sh - Prowlarr indexer management
# Usage: prowlarr.sh <command> [args...]
# Requires: CLAWARR_HOST, PROWLARR_KEY

set -euo pipefail

HOST="${CLAWARR_HOST:-}"
API_KEY="${PROWLARR_KEY:-}"
BASE_URL=""

init() {
  if [[ -z "$HOST" ]]; then
    echo "Error: CLAWARR_HOST not set" >&2; exit 1
  fi
  if [[ -z "$API_KEY" ]]; then
    echo "Error: PROWLARR_KEY not set" >&2; exit 1
  fi
  BASE_URL="http://${HOST}:9696"
}

api() {
  local method="${1:-GET}"
  local endpoint="$2"
  shift 2
  curl -sf -X "$method" \
    -H "X-Api-Key: ${API_KEY}" \
    -H "Content-Type: application/json" \
    "${BASE_URL}/api/v1${endpoint}" "$@" 2>/dev/null
}

cmd_indexers() {
  echo "📡 Prowlarr Indexers"
  echo ""
  local data
  data=$(api GET "/indexer")
  local count
  count=$(echo "$data" | jq 'length')
  echo "Total: ${count} indexers"
  echo ""
  echo "$data" | jq -r '.[] | "  [\(.id)] \(.name) (\(.protocol)) - \(if .enable then "✅ Enabled" else "❌ Disabled" end)"'
}

cmd_test() {
  local id="${1:-}"
  if [[ -z "$id" ]]; then
    echo "Testing all indexers..."
    local data
    data=$(api GET "/indexer")
    echo "$data" | jq -r '.[] | select(.enable == true) | "\(.id) \(.name)"' | while read -r iid iname; do
      if api POST "/indexer/test" -d "{\"id\":${iid}}" >/dev/null 2>&1; then
        echo "  ✅ ${iname}"
      else
        echo "  ❌ ${iname} - Test failed"
      fi
    done
  else
    echo "Testing indexer ${id}..."
    if api POST "/indexer/test" -d "{\"id\":${id}}" >/dev/null 2>&1; then
      echo "  ✅ Test passed"
    else
      echo "  ❌ Test failed"
    fi
  fi
}

cmd_stats() {
  echo "📊 Prowlarr Stats"
  echo ""
  local indexers
  indexers=$(api GET "/indexer")
  local total enabled
  total=$(echo "$indexers" | jq 'length')
  enabled=$(echo "$indexers" | jq '[.[] | select(.enable == true)] | length')
  echo "  Indexers: ${enabled} enabled / ${total} total"

  # Protocol breakdown
  local usenet torrent
  usenet=$(echo "$indexers" | jq '[.[] | select(.protocol == "usenet")] | length')
  torrent=$(echo "$indexers" | jq '[.[] | select(.protocol == "torrent")] | length')
  echo "  Usenet: ${usenet}"
  echo "  Torrent: ${torrent}"

  # App sync targets
  local apps
  apps=$(api GET "/applications" 2>/dev/null || echo "[]")
  local app_count
  app_count=$(echo "$apps" | jq 'length' 2>/dev/null || echo "0")
  echo "  Synced Apps: ${app_count}"
  if [[ "$app_count" != "0" ]]; then
    echo "$apps" | jq -r '.[] | "    - \(.name) (\(.implementation))"' 2>/dev/null
  fi
}

cmd_search() {
  local query="${1:-}"
  local type="${2:-}"
  if [[ -z "$query" ]]; then
    echo "Usage: prowlarr.sh search <query> [movie|tv|audio|book]" >&2; exit 1
  fi
  echo "🔍 Searching: ${query}"
  local params="query=$(echo "$query" | sed 's/ /%20/g')"
  if [[ -n "$type" ]]; then
    local cat_ids=""
    case "$type" in
      movie|movies) cat_ids="&categories=2000" ;;
      tv|shows) cat_ids="&categories=5000" ;;
      audio|music) cat_ids="&categories=3000" ;;
      book|books) cat_ids="&categories=7000" ;;
    esac
    params="${params}${cat_ids}"
  fi
  local results
  results=$(api GET "/search?${params}")
  local count
  count=$(echo "$results" | jq 'length')
  echo "Found: ${count} results"
  echo ""
  echo "$results" | jq -r '.[:20] | .[] | "  [\(.indexer)] \(.title) (\(.size / 1048576 | floor)MB) - \(.protocol)"'
}

cmd_apps() {
  echo "🔗 Prowlarr App Sync Targets"
  echo ""
  local data
  data=$(api GET "/applications")
  local count
  count=$(echo "$data" | jq 'length')
  if [[ "$count" == "0" ]]; then
    echo "  No apps configured. Add Sonarr/Radarr in Prowlarr settings."
  else
    echo "$data" | jq -r '.[] | "  [\(.id)] \(.name) (\(.implementation)) - Sync: \(.syncLevel)"'
  fi
}

cmd_add_app() {
  local app_type="${1:-}"
  local app_url="${2:-}"
  local app_key="${3:-}"
  if [[ -z "$app_type" || -z "$app_url" || -z "$app_key" ]]; then
    echo "Usage: prowlarr.sh add-app <sonarr|radarr|lidarr|readarr> <url> <api_key>" >&2; exit 1
  fi
  local impl=""
  case "$app_type" in
    sonarr) impl="Sonarr" ;;
    radarr) impl="Radarr" ;;
    lidarr) impl="Lidarr" ;;
    readarr) impl="Readarr" ;;
    *) echo "Unknown app type: ${app_type}" >&2; exit 1 ;;
  esac
  local prowlarr_url="http://${HOST}:9696"
  local payload
  payload=$(cat <<EOF
{
  "name": "${impl}",
  "implementation": "${impl}",
  "implementationName": "${impl}",
  "configContract": "${impl}Settings",
  "syncLevel": "fullSync",
  "fields": [
    {"name": "prowlarrUrl", "value": "${prowlarr_url}"},
    {"name": "baseUrl", "value": "${app_url}"},
    {"name": "apiKey", "value": "${app_key}"},
    {"name": "syncCategories", "value": []}
  ]
}
EOF
)
  local result
  if result=$(api POST "/applications" -d "$payload"); then
    local id
    id=$(echo "$result" | jq '.id')
    echo "✅ Added ${impl} (id: ${id})"
  else
    echo "❌ Failed to add ${impl}" >&2
  fi
}

cmd_sync() {
  echo "🔄 Triggering indexer sync to all apps..."
  if api POST "/applications/action/sync" -d '{}' >/dev/null 2>&1; then
    echo "✅ Sync triggered"
  else
    echo "❌ Sync failed" >&2
  fi
}

cmd_status() {
  echo "🏥 Prowlarr Health"
  echo ""
  local health
  health=$(api GET "/health")
  local issues
  issues=$(echo "$health" | jq 'length')
  if [[ "$issues" == "0" ]]; then
    echo "  ✅ No issues"
  else
    echo "$health" | jq -r '.[] | "  ⚠️  [\(.type)] \(.message)"'
  fi
  echo ""
  local status
  status=$(api GET "/system/status")
  echo "  Version: $(echo "$status" | jq -r '.version')"
  echo "  Branch: $(echo "$status" | jq -r '.branch')"
}

cmd_logs() {
  local count="${1:-20}"
  echo "📋 Prowlarr Logs (last ${count})"
  echo ""
  api GET "/log?pageSize=${count}&sortDirection=descending&sortKey=time" | \
    jq -r '.records[] | "  [\(.time | split("T")[0])] [\(.level)] \(.message)"'
}

usage() {
  cat <<EOF
Usage: prowlarr.sh <command> [args...]

Commands:
  indexers              List all indexers
  test [id]             Test indexer(s)
  stats                 Indexer statistics
  search <query> [type] Search across indexers (type: movie|tv|audio|book)
  apps                  List sync targets (Sonarr/Radarr/etc)
  add-app <type> <url> <key>  Add app sync target
  sync                  Trigger sync to all apps
  status                Health check
  logs [count]          Recent logs

Environment:
  CLAWARR_HOST          Host IP/hostname
  PROWLARR_KEY          Prowlarr API key
EOF
}

init

case "${1:-}" in
  indexers) cmd_indexers ;;
  test) shift; cmd_test "${1:-}" ;;
  stats) cmd_stats ;;
  search) shift; cmd_search "${1:-}" "${2:-}" ;;
  apps) cmd_apps ;;
  add-app) shift; cmd_add_app "${1:-}" "${2:-}" "${3:-}" ;;
  sync) cmd_sync ;;
  status) cmd_status ;;
  logs) shift; cmd_logs "${1:-20}" ;;
  *) usage ;;
esac
