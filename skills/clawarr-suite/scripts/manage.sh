#!/usr/bin/env bash
# manage.sh - Deep content management for Sonarr/Radarr
# Usage: manage.sh <command> [options]
#
# Commands:
#   add-movie <title> [quality] [root]     - Add movie to Radarr
#   add-series <title> [quality] [root]    - Add series to Sonarr
#   remove <app> <id>                      - Remove content
#   wanted [app]                           - Show all wanted/missing content
#   calendar [app] [days]                  - Upcoming releases (default: 7 days)
#   history [app] [count]                  - Recent download/import history
#   rename <app> <id>                      - Trigger rename scan
#   refresh <app> [id]                     - Refresh metadata (all or specific ID)

set -euo pipefail

HOST="${CLAWARR_HOST:-}"
SONARR_KEY="${SONARR_KEY:-}"
RADARR_KEY="${RADARR_KEY:-}"

if [[ -z "$HOST" ]]; then
  echo "❌ Error: CLAWARR_HOST not set"
  exit 1
fi

if ! command -v jq &> /dev/null; then
  echo "❌ Error: jq is required"
  exit 1
fi

show_help() {
  head -n 15 "$0" | grep "^#" | sed 's/^# \?//'
  exit 0
}

# Helper: call API
api_call() {
  local app=$1
  local method=$2
  local endpoint=$3
  local data="${4:-}"
  
  local key=""
  local port=""
  local api_ver=""
  
  case "$app" in
    radarr)
      key="$RADARR_KEY"
      port=7878
      api_ver="v3"
      ;;
    sonarr)
      key="$SONARR_KEY"
      port=8989
      api_ver="v3"
      ;;
    *)
      echo "❌ Unknown app: $app"
      return 1
      ;;
  esac
  
  if [[ -z "$key" ]]; then
    echo "❌ API key not set for $app"
    return 1
  fi
  
  local url="http://${HOST}:${port}/api/${api_ver}${endpoint}"
  
  if [[ "$method" == "GET" ]]; then
    curl -sf -H "X-Api-Key: $key" "$url"
  elif [[ "$method" == "POST" ]]; then
    curl -sf -X POST -H "X-Api-Key: $key" -H "Content-Type: application/json" -d "$data" "$url"
  elif [[ "$method" == "DELETE" ]]; then
    curl -sf -X DELETE -H "X-Api-Key: $key" "$url"
  elif [[ "$method" == "PUT" ]]; then
    curl -sf -X PUT -H "X-Api-Key: $key" -H "Content-Type: application/json" -d "$data" "$url"
  fi
}

# Command: add-movie
cmd_add_movie() {
  local title="$1"
  local quality="${2:-}"
  local root="${3:-}"
  
  if [[ -z "$title" ]]; then
    echo "❌ Error: Title required"
    echo "Usage: $0 add-movie \"<title>\" [quality_profile_id] [root_folder_path]"
    exit 1
  fi
  
  echo "🔍 Searching for: $title"
  
  # Search for the movie
  local search_results
  search_results=$(api_call radarr GET "/movie/lookup?term=$(echo "$title" | sed 's/ /%20/g')")
  
  if [[ $(echo "$search_results" | jq 'length') -eq 0 ]]; then
    echo "❌ No results found for: $title"
    exit 1
  fi
  
  # Show results
  echo ""
  echo "Search Results:"
  echo "$search_results" | jq -r '.[] | "  [\(.tmdbId)] \(.title) (\(.year)) - \(.overview[0:80])..."' | head -5
  echo ""
  
  # Get first result
  local movie
  movie=$(echo "$search_results" | jq '.[0]')
  local tmdb_id
  tmdb_id=$(echo "$movie" | jq -r '.tmdbId')
  local movie_title
  movie_title=$(echo "$movie" | jq -r '.title')
  local year
  year=$(echo "$movie" | jq -r '.year')
  
  # Get quality profiles if not specified
  if [[ -z "$quality" ]]; then
    local profiles
    profiles=$(api_call radarr GET "/qualityprofile")
    echo "Available Quality Profiles:"
    echo "$profiles" | jq -r '.[] | "  [\(.id)] \(.name)"'
    echo ""
    read -p "Enter quality profile ID (or press Enter for default=1): " quality
    quality="${quality:-1}"
  fi
  
  # Get root folders if not specified
  if [[ -z "$root" ]]; then
    local folders
    folders=$(api_call radarr GET "/rootfolder")
    echo "Available Root Folders:"
    echo "$folders" | jq -r '.[] | "  \(.path)"'
    echo ""
    read -p "Enter root folder path (or press Enter for first): " root
    if [[ -z "$root" ]]; then
      root=$(echo "$folders" | jq -r '.[0].path')
    fi
  fi
  
  # Prepare add request
  local add_data
  add_data=$(echo "$movie" | jq \
    --arg qp "$quality" \
    --arg rf "$root" \
    '{
      title: .title,
      tmdbId: .tmdbId,
      year: .year,
      qualityProfileId: ($qp | tonumber),
      rootFolderPath: $rf,
      monitored: true,
      minimumAvailability: "released",
      addOptions: {
        searchForMovie: true
      }
    }')
  
  echo "➕ Adding: $movie_title ($year)"
  
  local result
  if result=$(api_call radarr POST "/movie" "$add_data"); then
    echo "✅ Successfully added: $movie_title"
    echo "   Search started automatically"
  else
    echo "❌ Failed to add movie"
    echo "$result"
  fi
}

# Command: add-series
cmd_add_series() {
  local title="$1"
  local quality="${2:-}"
  local root="${3:-}"
  
  if [[ -z "$title" ]]; then
    echo "❌ Error: Title required"
    echo "Usage: $0 add-series \"<title>\" [quality_profile_id] [root_folder_path]"
    exit 1
  fi
  
  echo "🔍 Searching for: $title"
  
  # Search for the series
  local search_results
  search_results=$(api_call sonarr GET "/series/lookup?term=$(echo "$title" | sed 's/ /%20/g')")
  
  if [[ $(echo "$search_results" | jq 'length') -eq 0 ]]; then
    echo "❌ No results found for: $title"
    exit 1
  fi
  
  # Show results
  echo ""
  echo "Search Results:"
  echo "$search_results" | jq -r '.[] | "  [\(.tvdbId)] \(.title) (\(.year // "N/A")) - \(.overview[0:80] // "No description")..."' | head -5
  echo ""
  
  # Get first result
  local series
  series=$(echo "$search_results" | jq '.[0]')
  local tvdb_id
  tvdb_id=$(echo "$series" | jq -r '.tvdbId')
  local series_title
  series_title=$(echo "$series" | jq -r '.title')
  
  # Get quality profiles if not specified
  if [[ -z "$quality" ]]; then
    local profiles
    profiles=$(api_call sonarr GET "/qualityprofile")
    echo "Available Quality Profiles:"
    echo "$profiles" | jq -r '.[] | "  [\(.id)] \(.name)"'
    echo ""
    read -p "Enter quality profile ID (or press Enter for default=1): " quality
    quality="${quality:-1}"
  fi
  
  # Get root folders if not specified
  if [[ -z "$root" ]]; then
    local folders
    folders=$(api_call sonarr GET "/rootfolder")
    echo "Available Root Folders:"
    echo "$folders" | jq -r '.[] | "  \(.path)"'
    echo ""
    read -p "Enter root folder path (or press Enter for first): " root
    if [[ -z "$root" ]]; then
      root=$(echo "$folders" | jq -r '.[0].path')
    fi
  fi
  
  # Prepare add request
  local add_data
  add_data=$(echo "$series" | jq \
    --arg qp "$quality" \
    --arg rf "$root" \
    '{
      title: .title,
      tvdbId: .tvdbId,
      qualityProfileId: ($qp | tonumber),
      rootFolderPath: $rf,
      seasonFolder: true,
      monitored: true,
      addOptions: {
        searchForMissingEpisodes: true
      }
    }')
  
  echo "➕ Adding: $series_title"
  
  local result
  if result=$(api_call sonarr POST "/series" "$add_data"); then
    echo "✅ Successfully added: $series_title"
    echo "   Search started automatically"
  else
    echo "❌ Failed to add series"
    echo "$result"
  fi
}

# Command: remove
cmd_remove() {
  local app="$1"
  local id="$2"
  
  if [[ -z "$app" || -z "$id" ]]; then
    echo "❌ Error: App and ID required"
    echo "Usage: $0 remove <radarr|sonarr> <id>"
    exit 1
  fi
  
  # Get item details first
  local endpoint=""
  if [[ "$app" == "radarr" ]]; then
    endpoint="/movie/$id"
  else
    endpoint="/series/$id"
  fi
  
  local item
  item=$(api_call "$app" GET "$endpoint")
  local title
  title=$(echo "$item" | jq -r '.title')
  
  read -p "⚠️  Remove $title from $app? (yes/no): " confirm
  if [[ "$confirm" != "yes" ]]; then
    echo "Cancelled"
    exit 0
  fi
  
  if api_call "$app" DELETE "${endpoint}?deleteFiles=false"; then
    echo "✅ Removed: $title"
  else
    echo "❌ Failed to remove"
  fi
}

# Command: wanted
cmd_wanted() {
  local app="${1:-all}"
  
  if [[ "$app" == "all" || "$app" == "radarr" ]] && [[ -n "$RADARR_KEY" ]]; then
    echo "📋 Wanted Movies (Radarr)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local movies
    movies=$(api_call radarr GET "/wanted/missing?pageSize=50&sortKey=title")
    
    echo "$movies" | jq -r '.records[] | "  \(.title) (\(.year))"'
    
    local total
    total=$(echo "$movies" | jq -r '.totalRecords')
    echo ""
    echo "  Total Missing: $total"
    echo ""
  fi
  
  if [[ "$app" == "all" || "$app" == "sonarr" ]] && [[ -n "$SONARR_KEY" ]]; then
    echo "📋 Wanted Episodes (Sonarr)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local episodes
    episodes=$(api_call sonarr GET "/wanted/missing?pageSize=50&sortKey=airDateUtc")
    
    echo "$episodes" | jq -r '.records[] | "  \(.series.title) - S\(.seasonNumber | tostring | if length == 1 then "0" + . else . end)E\(.episodeNumber | tostring | if length == 1 then "0" + . else . end) - \(.title)"'
    
    local total
    total=$(echo "$episodes" | jq -r '.totalRecords')
    echo ""
    echo "  Total Missing Episodes: $total"
    echo ""
  fi
}

# Command: calendar
cmd_calendar() {
  local app="${1:-all}"
  local days="${2:-7}"
  
  local start_date
  start_date=$(date -u +"%Y-%m-%d")
  local end_date
  end_date=$(date -u -v+${days}d +"%Y-%m-%d" 2>/dev/null || date -u -d "${days} days" +"%Y-%m-%d")
  
  if [[ "$app" == "all" || "$app" == "radarr" ]] && [[ -n "$RADARR_KEY" ]]; then
    echo "📅 Upcoming Movies (Next $days days)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local calendar
    calendar=$(api_call radarr GET "/calendar?start=${start_date}&end=${end_date}")
    
    if [[ $(echo "$calendar" | jq 'length') -eq 0 ]]; then
      echo "  No upcoming movies"
    else
      echo "$calendar" | jq -r '.[] | "\(.digitalRelease // .physicalRelease // "TBA")  \(.title) (\(.year))"' | sort
    fi
    echo ""
  fi
  
  if [[ "$app" == "all" || "$app" == "sonarr" ]] && [[ -n "$SONARR_KEY" ]]; then
    echo "📅 Upcoming Episodes (Next $days days)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local calendar
    calendar=$(api_call sonarr GET "/calendar?start=${start_date}&end=${end_date}")
    
    if [[ $(echo "$calendar" | jq 'length') -eq 0 ]]; then
      echo "  No upcoming episodes"
    else
      echo "$calendar" | jq -r '.[] | "\(.airDateUtc | split("T")[0])  \(.series.title) - S\(.seasonNumber | tostring | if length == 1 then "0" + . else . end)E\(.episodeNumber | tostring | if length == 1 then "0" + . else . end) - \(.title)"' | sort
    fi
    echo ""
  fi
}

# Command: history
cmd_history() {
  local app="${1:-radarr}"
  local count="${2:-20}"
  
  echo "📜 Recent History - $(echo "$app" | tr '[:lower:]' '[:upper:]')"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  local history
  history=$(api_call "$app" GET "/history?pageSize=${count}&sortKey=date&sortDirection=descending")
  
  if [[ "$app" == "radarr" ]]; then
    echo "$history" | jq -r '.records[] | "\(.date | split("T")[0])  [\(.eventType)] \(.movie.title) - \(.quality.quality.name)"'
  else
    echo "$history" | jq -r '.records[] | "\(.date | split("T")[0])  [\(.eventType)] \(.series.title) - \(.episode.title) - \(.quality.quality.name)"'
  fi
  
  echo ""
}

# Command: rename
cmd_rename() {
  local app="$1"
  local id="$2"
  
  if [[ -z "$app" || -z "$id" ]]; then
    echo "❌ Error: App and ID required"
    echo "Usage: $0 rename <radarr|sonarr> <id>"
    exit 1
  fi
  
  echo "🔄 Triggering rename for ID: $id in $app"
  
  local cmd_data
  if [[ "$app" == "radarr" ]]; then
    cmd_data='{"name": "RenameMovie", "movieIds": ['$id']}'
  else
    cmd_data='{"name": "RenameSeries", "seriesIds": ['$id']}'
  fi
  
  if api_call "$app" POST "/command" "$cmd_data" >/dev/null; then
    echo "✅ Rename command sent"
  else
    echo "❌ Failed to send rename command"
  fi
}

# Command: refresh
cmd_refresh() {
  local app="$1"
  local id="${2:-}"
  
  if [[ -z "$app" ]]; then
    echo "❌ Error: App required"
    echo "Usage: $0 refresh <radarr|sonarr> [id]"
    exit 1
  fi
  
  local cmd_data
  if [[ -n "$id" ]]; then
    echo "🔄 Refreshing metadata for ID: $id in $app"
    if [[ "$app" == "radarr" ]]; then
      cmd_data='{"name": "RefreshMovie", "movieId": '$id'}'
    else
      cmd_data='{"name": "RefreshSeries", "seriesId": '$id'}'
    fi
  else
    echo "🔄 Refreshing all metadata in $app"
    if [[ "$app" == "radarr" ]]; then
      cmd_data='{"name": "RefreshMovie"}'
    else
      cmd_data='{"name": "RefreshSeries"}'
    fi
  fi
  
  if api_call "$app" POST "/command" "$cmd_data" >/dev/null; then
    echo "✅ Refresh command sent"
  else
    echo "❌ Failed to send refresh command"
  fi
}

# Main command router
COMMAND="${1:-help}"

case "$COMMAND" in
  add-movie)   cmd_add_movie "${2:-}" "${3:-}" "${4:-}" ;;
  add-series)  cmd_add_series "${2:-}" "${3:-}" "${4:-}" ;;
  remove)      cmd_remove "${2:-}" "${3:-}" ;;
  wanted)      cmd_wanted "${2:-all}" ;;
  calendar)    cmd_calendar "${2:-all}" "${3:-7}" ;;
  history)     cmd_history "${2:-radarr}" "${3:-20}" ;;
  rename)      cmd_rename "${2:-}" "${3:-}" ;;
  refresh)     cmd_refresh "${2:-}" "${3:-}" ;;
  help|--help|-h) show_help ;;
  *)
    echo "❌ Unknown command: $COMMAND"
    echo "Run '$0 help' for usage"
    exit 1
    ;;
esac
