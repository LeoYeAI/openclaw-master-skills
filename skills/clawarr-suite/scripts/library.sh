#!/usr/bin/env bash
# library.sh - Deep library exploration for Sonarr/Radarr
# Usage: library.sh <command> [options]
#
# Commands:
#   stats [app]          - Overall library statistics
#   quality [app]        - Quality profile breakdown
#   missing [app]        - Missing/wanted content
#   unmonitored [app]    - Unmonitored content
#   recent [app] [days]  - Recently added (default: 7 days)
#   genres [app]         - Genre distribution
#   years [app]          - Year distribution
#   studios [app]        - Studio/network breakdown
#   nofiles [app]        - Monitored content with no files
#   disk [app]           - Disk usage by root folder
#
# App: radarr, sonarr, lidarr (default: all)

set -euo pipefail

HOST="${CLAWARR_HOST:-}"
SONARR_KEY="${SONARR_KEY:-}"
RADARR_KEY="${RADARR_KEY:-}"
LIDARR_KEY="${LIDARR_KEY:-}"

if [[ -z "$HOST" ]]; then
  echo "❌ Error: CLAWARR_HOST not set"
  echo "Usage: export CLAWARR_HOST=192.168.1.100"
  exit 1
fi

if ! command -v jq &> /dev/null; then
  echo "❌ Error: jq is required but not installed"
  exit 1
fi

show_help() {
  head -n 20 "$0" | grep "^#" | sed 's/^# \?//'
  exit 0
}

# Helper: call API
api_call() {
  local app=$1
  local endpoint=$2
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
    lidarr)
      key="$LIDARR_KEY"
      port=8686
      api_ver="v1"
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
  
  curl -sf -H "X-Api-Key: $key" "http://${HOST}:${port}/api/${api_ver}${endpoint}"
}

# Command: stats
cmd_stats() {
  local app="${1:-all}"
  
  if [[ "$app" == "all" || "$app" == "radarr" ]] && [[ -n "$RADARR_KEY" ]]; then
    echo "📊 Radarr Library Statistics"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local data
    data=$(api_call radarr "/movie")
    
    local total
    total=$(echo "$data" | jq 'length')
    local monitored
    monitored=$(echo "$data" | jq '[.[] | select(.monitored == true)] | length')
    local downloaded
    downloaded=$(echo "$data" | jq '[.[] | select(.hasFile == true)] | length')
    local missing
    missing=$(echo "$data" | jq '[.[] | select(.monitored == true and .hasFile == false)] | length')
    local size
    size=$(echo "$data" | jq '[.[] | select(.hasFile == true) | .sizeOnDisk] | add')
    local size_gb
    size_gb=$(echo "scale=2; $size / 1073741824" | bc)
    
    echo "  Total Movies: $total"
    echo "  Monitored: $monitored"
    echo "  Downloaded: $downloaded"
    echo "  Missing: $missing"
    echo "  Disk Usage: ${size_gb} GB"
    echo ""
  fi
  
  if [[ "$app" == "all" || "$app" == "sonarr" ]] && [[ -n "$SONARR_KEY" ]]; then
    echo "📊 Sonarr Library Statistics"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local series_data
    series_data=$(api_call sonarr "/series")
    local episode_data
    episode_data=$(api_call sonarr "/episode")
    
    local total_series
    total_series=$(echo "$series_data" | jq 'length')
    local monitored_series
    monitored_series=$(echo "$series_data" | jq '[.[] | select(.monitored == true)] | length')
    local total_episodes
    total_episodes=$(echo "$episode_data" | jq 'length')
    local downloaded_episodes
    downloaded_episodes=$(echo "$episode_data" | jq '[.[] | select(.hasFile == true)] | length')
    local missing_episodes
    missing_episodes=$(echo "$episode_data" | jq '[.[] | select(.monitored == true and .hasFile == false)] | length')
    local size
    size=$(echo "$series_data" | jq '[.[] | .statistics.sizeOnDisk] | add')
    local size_gb
    size_gb=$(echo "scale=2; $size / 1073741824" | bc)
    
    echo "  Total Series: $total_series"
    echo "  Monitored Series: $monitored_series"
    echo "  Total Episodes: $total_episodes"
    echo "  Downloaded Episodes: $downloaded_episodes"
    echo "  Missing Episodes: $missing_episodes"
    echo "  Disk Usage: ${size_gb} GB"
    echo ""
  fi
  
  if [[ "$app" == "all" || "$app" == "lidarr" ]] && [[ -n "$LIDARR_KEY" ]]; then
    echo "📊 Lidarr Library Statistics"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local artist_data
    artist_data=$(api_call lidarr "/artist")
    
    local total_artists
    total_artists=$(echo "$artist_data" | jq 'length')
    local monitored_artists
    monitored_artists=$(echo "$artist_data" | jq '[.[] | select(.monitored == true)] | length')
    local total_albums
    total_albums=$(echo "$artist_data" | jq '[.[] | .statistics.albumCount] | add')
    local size
    size=$(echo "$artist_data" | jq '[.[] | .statistics.sizeOnDisk] | add')
    local size_gb
    size_gb=$(echo "scale=2; $size / 1073741824" | bc)
    
    echo "  Total Artists: $total_artists"
    echo "  Monitored Artists: $monitored_artists"
    echo "  Total Albums: $total_albums"
    echo "  Disk Usage: ${size_gb} GB"
    echo ""
  fi
}

# Command: quality breakdown
cmd_quality() {
  local app="${1:-radarr}"
  
  echo "📊 Quality Profile Breakdown - $(echo "$app" | tr '[:lower:]' '[:upper:]')"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  if [[ "$app" == "radarr" ]]; then
    local profiles
    profiles=$(api_call radarr "/qualityprofile")
    local movies
    movies=$(api_call radarr "/movie")
    
    echo "$profiles" | jq -r '.[] | .name' | while read -r profile; do
      local count
      count=$(echo "$movies" | jq "[.[] | select(.qualityProfileId == $(echo "$profiles" | jq -r ".[] | select(.name == \"$profile\") | .id"))] | length")
      printf "  %-30s %5d movies\n" "$profile" "$count"
    done
  elif [[ "$app" == "sonarr" ]]; then
    local profiles
    profiles=$(api_call sonarr "/qualityprofile")
    local series
    series=$(api_call sonarr "/series")
    
    echo "$profiles" | jq -r '.[] | .name' | while read -r profile; do
      local count
      count=$(echo "$series" | jq "[.[] | select(.qualityProfileId == $(echo "$profiles" | jq -r ".[] | select(.name == \"$profile\") | .id"))] | length")
      printf "  %-30s %5d series\n" "$profile" "$count"
    done
  fi
  echo ""
}

# Command: missing content
cmd_missing() {
  local app="${1:-all}"
  
  if [[ "$app" == "all" || "$app" == "radarr" ]] && [[ -n "$RADARR_KEY" ]]; then
    echo "📋 Missing Movies (Radarr)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local data
    data=$(api_call radarr "/movie")
    
    echo "$data" | jq -r '.[] | select(.monitored == true and .hasFile == false) | "\(.title) (\(.year))"' | head -20
    
    local count
    count=$(echo "$data" | jq '[.[] | select(.monitored == true and .hasFile == false)] | length')
    if [[ $count -gt 20 ]]; then
      echo "  ... and $((count - 20)) more"
    fi
    echo ""
  fi
  
  if [[ "$app" == "all" || "$app" == "sonarr" ]] && [[ -n "$SONARR_KEY" ]]; then
    echo "📋 Missing Episodes (Sonarr)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local series
    series=$(api_call sonarr "/series")
    
    echo "$series" | jq -r '.[] | select(.statistics.episodeFileCount < .statistics.totalEpisodeCount and .monitored == true) | "\(.title): \(.statistics.totalEpisodeCount - .statistics.episodeFileCount) missing"' | head -20
    echo ""
  fi
}

# Command: unmonitored content
cmd_unmonitored() {
  local app="${1:-radarr}"
  
  echo "⏸️  Unmonitored Content - $(echo "$app" | tr '[:lower:]' '[:upper:]')"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  if [[ "$app" == "radarr" ]]; then
    local data
    data=$(api_call radarr "/movie")
    echo "$data" | jq -r '.[] | select(.monitored == false) | "\(.title) (\(.year))"' | head -20
  elif [[ "$app" == "sonarr" ]]; then
    local data
    data=$(api_call sonarr "/series")
    echo "$data" | jq -r '.[] | select(.monitored == false) | .title' | head -20
  fi
  echo ""
}

# Command: recently added
cmd_recent() {
  local app="${1:-radarr}"
  local days="${2:-7}"
  local cutoff_date
  cutoff_date=$(date -u -v-${days}d +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u -d "${days} days ago" +"%Y-%m-%dT%H:%M:%SZ")
  
  echo "🆕 Recently Added (Last $days days) - $(echo "$app" | tr '[:lower:]' '[:upper:]')"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  if [[ "$app" == "radarr" ]]; then
    local data
    data=$(api_call radarr "/movie")
    echo "$data" | jq -r --arg cutoff "$cutoff_date" '.[] | select(.added >= $cutoff) | "\(.added | split("T")[0])  \(.title) (\(.year))"' | sort -r | head -20
  elif [[ "$app" == "sonarr" ]]; then
    local data
    data=$(api_call sonarr "/series")
    echo "$data" | jq -r --arg cutoff "$cutoff_date" '.[] | select(.added >= $cutoff) | "\(.added | split("T")[0])  \(.title)"' | sort -r | head -20
  fi
  echo ""
}

# Command: genres
cmd_genres() {
  local app="${1:-radarr}"
  
  echo "🎭 Genre Distribution - $(echo "$app" | tr '[:lower:]' '[:upper:]')"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  if [[ "$app" == "radarr" ]]; then
    local data
    data=$(api_call radarr "/movie")
    echo "$data" | jq -r '.[] | .genres[]' | sort | uniq -c | sort -rn | head -15 | while read -r count genre; do
      printf "  %-25s %5d\n" "$genre" "$count"
    done
  elif [[ "$app" == "sonarr" ]]; then
    local data
    data=$(api_call sonarr "/series")
    echo "$data" | jq -r '.[] | .genres[]' | sort | uniq -c | sort -rn | head -15 | while read -r count genre; do
      printf "  %-25s %5d\n" "$genre" "$count"
    done
  fi
  echo ""
}

# Command: years
cmd_years() {
  local app="${1:-radarr}"
  
  echo "📅 Year Distribution - $(echo "$app" | tr '[:lower:]' '[:upper:]')"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  if [[ "$app" == "radarr" ]]; then
    local data
    data=$(api_call radarr "/movie")
    echo "$data" | jq -r '.[] | .year' | sort | uniq -c | sort -rn | head -20 | while read -r count year; do
      printf "  %4s  %5d movies\n" "$year" "$count"
    done
  elif [[ "$app" == "sonarr" ]]; then
    local data
    data=$(api_call sonarr "/series")
    echo "$data" | jq -r '.[] | .year' | sort | uniq -c | sort -rn | head -20 | while read -r count year; do
      printf "  %4s  %5d series\n" "$year" "$count"
    done
  fi
  echo ""
}

# Command: studios/networks
cmd_studios() {
  local app="${1:-radarr}"
  
  if [[ "$app" == "radarr" ]]; then
    echo "🎬 Studio Distribution"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local data
    data=$(api_call radarr "/movie")
    echo "$data" | jq -r '.[] | .studio // "Unknown"' | sort | uniq -c | sort -rn | head -15 | while read -r count studio; do
      printf "  %-30s %5d\n" "$studio" "$count"
    done
  elif [[ "$app" == "sonarr" ]]; then
    echo "📺 Network Distribution"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local data
    data=$(api_call sonarr "/series")
    echo "$data" | jq -r '.[] | .network // "Unknown"' | sort | uniq -c | sort -rn | head -15 | while read -r count network; do
      printf "  %-30s %5d\n" "$network" "$count"
    done
  fi
  echo ""
}

# Command: no files
cmd_nofiles() {
  local app="${1:-radarr}"
  
  echo "❌ Monitored Content With No Files - $(echo "$app" | tr '[:lower:]' '[:upper:]')"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  if [[ "$app" == "radarr" ]]; then
    local data
    data=$(api_call radarr "/movie")
    echo "$data" | jq -r '.[] | select(.monitored == true and .hasFile == false) | "\(.title) (\(.year))"' | head -30
  elif [[ "$app" == "sonarr" ]]; then
    local data
    data=$(api_call sonarr "/series")
    echo "$data" | jq -r '.[] | select(.monitored == true and .statistics.episodeFileCount == 0) | .title' | head -30
  fi
  echo ""
}

# Command: disk usage
cmd_disk() {
  local app="${1:-all}"
  
  echo "💾 Disk Usage by Root Folder"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  if [[ "$app" == "all" || "$app" == "radarr" ]] && [[ -n "$RADARR_KEY" ]]; then
    echo "Radarr:"
    local folders
    folders=$(api_call radarr "/rootfolder")
    echo "$folders" | jq -r '.[] | "  \(.path): \(.freeSpace / 1073741824 | floor) GB free / \(.totalSpace / 1073741824 | floor) GB total"'
    echo ""
  fi
  
  if [[ "$app" == "all" || "$app" == "sonarr" ]] && [[ -n "$SONARR_KEY" ]]; then
    echo "Sonarr:"
    local folders
    folders=$(api_call sonarr "/rootfolder")
    echo "$folders" | jq -r '.[] | "  \(.path): \(.freeSpace / 1073741824 | floor) GB free / \(.totalSpace / 1073741824 | floor) GB total"'
    echo ""
  fi
  
  if [[ "$app" == "all" || "$app" == "lidarr" ]] && [[ -n "$LIDARR_KEY" ]]; then
    echo "Lidarr:"
    local folders
    folders=$(api_call lidarr "/rootfolder")
    echo "$folders" | jq -r '.[] | "  \(.path): \(.freeSpace / 1073741824 | floor) GB free / \(.totalSpace / 1073741824 | floor) GB total"'
    echo ""
  fi
}

# Main command router
COMMAND="${1:-help}"

case "$COMMAND" in
  stats)      cmd_stats "${2:-all}" ;;
  quality)    cmd_quality "${2:-radarr}" ;;
  missing)    cmd_missing "${2:-all}" ;;
  unmonitored) cmd_unmonitored "${2:-radarr}" ;;
  recent)     cmd_recent "${2:-radarr}" "${3:-7}" ;;
  genres)     cmd_genres "${2:-radarr}" ;;
  years)      cmd_years "${2:-radarr}" ;;
  studios)    cmd_studios "${2:-radarr}" ;;
  nofiles)    cmd_nofiles "${2:-radarr}" ;;
  disk)       cmd_disk "${2:-all}" ;;
  help|--help|-h) show_help ;;
  *)
    echo "❌ Unknown command: $COMMAND"
    echo "Run '$0 help' for usage"
    exit 1
    ;;
esac
