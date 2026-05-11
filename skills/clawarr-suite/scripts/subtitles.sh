#!/usr/bin/env bash
# subtitles.sh - Bazarr subtitle management
# Usage: subtitles.sh <command> [options]
#
# Commands:
#   wanted              - Missing subtitles
#   history [count]     - Recent subtitle downloads (default: 20)
#   search <type> <id>  - Manual subtitle search (type: series|movie)
#   languages           - Configured languages

set -euo pipefail

HOST="${CLAWARR_HOST:-}"
BAZARR_KEY="${BAZARR_KEY:-}"

if [[ -z "$HOST" ]]; then
  echo "❌ Error: CLAWARR_HOST not set"
  exit 1
fi

if [[ -z "$BAZARR_KEY" ]]; then
  echo "❌ Error: BAZARR_KEY not set"
  exit 1
fi

if ! command -v jq &> /dev/null; then
  echo "❌ Error: jq is required"
  exit 1
fi

show_help() {
  head -n 12 "$0" | grep "^#" | sed 's/^# \?//'
  exit 0
}

# Helper: call Bazarr API
bazarr_api() {
  local endpoint=$1
  local method="${2:-GET}"
  local data="${3:-}"
  
  local url="http://${HOST}:6767/api${endpoint}"
  
  if [[ "$method" == "GET" ]]; then
    curl -sf -H "X-API-Key: $BAZARR_KEY" "$url"
  elif [[ "$method" == "POST" ]]; then
    curl -sf -X POST -H "X-API-Key: $BAZARR_KEY" -H "Content-Type: application/json" -d "$data" "$url"
  fi
}

# Command: wanted
cmd_wanted() {
  echo "📋 Missing Subtitles"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  echo ""
  echo "Episodes:"
  local episodes
  episodes=$(bazarr_api "/episodes/wanted?start=0&length=20")
  
  if [[ $(echo "$episodes" | jq '.data | length') -eq 0 ]]; then
    echo "  No missing episode subtitles"
  else
    echo "$episodes" | jq -r '.data[] | "  \(.seriesTitle) - S\(.season | tostring | if length == 1 then "0" + . else . end)E\(.episode | tostring | if length == 1 then "0" + . else . end) - \(.title // "Unknown")
    Missing: \(.missing_subtitles)"' | sed 's/^/  /'
  fi
  
  echo ""
  echo "Movies:"
  local movies
  movies=$(bazarr_api "/movies/wanted?start=0&length=20")
  
  if [[ $(echo "$movies" | jq '.data | length') -eq 0 ]]; then
    echo "  No missing movie subtitles"
  else
    echo "$movies" | jq -r '.data[] | "  \(.title) (\(.year // "N/A"))
    Missing: \(.missing_subtitles)"' | sed 's/^/  /'
  fi
  
  echo ""
}

# Command: history
cmd_history() {
  local count="${1:-20}"
  
  echo "📜 Recent Subtitle Downloads (Last $count)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  local history
  history=$(bazarr_api "/history?length=${count}")
  
  if [[ $(echo "$history" | jq '.data | length') -eq 0 ]]; then
    echo "  No recent downloads"
    echo ""
    return
  fi
  
  echo "$history" | jq -r '.data[] | 
    "\(.timestamp | split("T")[0]) \(.timestamp | split("T")[1] | split(".")[0])  [\(.action | ascii_upcase)] \(.seriesTitle // .title)
    Language: \(.language) | Provider: \(.provider)"' | sed 's/^/  /'
  
  echo ""
}

# Command: search
cmd_search() {
  local type="$1"
  local id="$2"
  
  if [[ -z "$type" || -z "$id" ]]; then
    echo "❌ Error: Type and ID required"
    echo "Usage: $0 search <series|movie> <id>"
    exit 1
  fi
  
  echo "🔍 Searching subtitles for $type ID: $id"
  
  if [[ "$type" == "series" ]]; then
    # Trigger episode subtitle search
    local data
    data=$(jq -n --arg id "$id" '{seriesId: $id}')
    
    if bazarr_api "/episodes/search" "POST" "$data" >/dev/null 2>&1; then
      echo "✅ Search triggered for series $id"
    else
      echo "❌ Failed to trigger search"
    fi
  elif [[ "$type" == "movie" ]]; then
    # Trigger movie subtitle search
    local data
    data=$(jq -n --arg id "$id" '{radarrId: $id}')
    
    if bazarr_api "/movies/search" "POST" "$data" >/dev/null 2>&1; then
      echo "✅ Search triggered for movie $id"
    else
      echo "❌ Failed to trigger search"
    fi
  else
    echo "❌ Invalid type. Use 'series' or 'movie'"
    exit 1
  fi
}

# Command: languages
cmd_languages() {
  echo "🌐 Configured Languages"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  # Get system settings
  local settings
  settings=$(bazarr_api "/system/settings")
  
  echo "  Enabled Languages:"
  echo "$settings" | jq -r '.settings.general.enabled_languages[]' 2>/dev/null | while read -r lang; do
    echo "    - $lang"
  done
  
  echo ""
  echo "  Default Settings:"
  echo "$settings" | jq -r '
    "    Series Sync: \(.settings.general.serie_default_enabled)",
    "    Movie Sync: \(.settings.general.movie_default_enabled)",
    "    Single Language: \(.settings.general.single_language)"
  ' 2>/dev/null || echo "    (Unable to fetch settings)"
  
  echo ""
}

# Main command router
COMMAND="${1:-help}"

case "$COMMAND" in
  wanted)    cmd_wanted ;;
  history)   cmd_history "${2:-20}" ;;
  search)    cmd_search "${2:-}" "${3:-}" ;;
  languages) cmd_languages ;;
  help|--help|-h) show_help ;;
  *)
    echo "❌ Unknown command: $COMMAND"
    echo "Run '$0 help' for usage"
    exit 1
    ;;
esac
