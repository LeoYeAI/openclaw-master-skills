#!/usr/bin/env bash
# search.sh - Unified search across Radarr/Sonarr/Lidarr
# Usage: search.sh "<query>" <type>
#   type: movie, series, music

set -euo pipefail

QUERY="${1:-}"
TYPE="${2:-movie}"

HOST="${CLAWARR_HOST:-}"
RADARR_KEY="${RADARR_KEY:-}"
SONARR_KEY="${SONARR_KEY:-}"
LIDARR_KEY="${LIDARR_KEY:-}"

if [[ -z "$QUERY" ]]; then
  echo "Usage: $0 \"<query>\" <type>"
  echo ""
  echo "Types: movie, series, music"
  echo ""
  echo "Examples:"
  echo "  $0 \"dune\" movie"
  echo "  $0 \"foundation\" series"
  echo "  $0 \"pink floyd\" music"
  echo ""
  echo "Requires: CLAWARR_HOST, RADARR_KEY/SONARR_KEY/LIDARR_KEY environment variables"
  exit 1
fi

if [[ -z "$HOST" ]]; then
  echo "Error: CLAWARR_HOST not set"
  exit 1
fi

if ! command -v jq &> /dev/null; then
  echo "❌ Error: jq is required but not installed"
  exit 1
fi

# URL encode query
ENCODED_QUERY=$(echo "$QUERY" | jq -sRr @uri)

case "$TYPE" in
  movie)
    if [[ -z "$RADARR_KEY" ]]; then
      echo "Error: RADARR_KEY not set"
      exit 1
    fi
    
    echo "🎬 Searching Radarr for: $QUERY"
    echo ""
    
    results=$(curl -sf -H "X-Api-Key: ${RADARR_KEY}" \
      "http://${HOST}:7878/api/v3/movie/lookup?term=${ENCODED_QUERY}" 2>/dev/null || echo '[]')
    
    count=$(echo "$results" | jq 'length')
    
    if [[ "$count" -eq 0 ]]; then
      echo "No results found"
    else
      echo "Found $count result(s):"
      echo ""
      echo "$results" | jq -r '.[] | "• \(.title) (\(.year))\n  TMDB: \(.tmdbId) | Rating: \(.ratings.imdb.value // "N/A")\n  \(.overview[0:150])...\n"' | head -20
    fi
    ;;
    
  series)
    if [[ -z "$SONARR_KEY" ]]; then
      echo "Error: SONARR_KEY not set"
      exit 1
    fi
    
    echo "📺 Searching Sonarr for: $QUERY"
    echo ""
    
    results=$(curl -sf -H "X-Api-Key: ${SONARR_KEY}" \
      "http://${HOST}:8989/api/v3/series/lookup?term=${ENCODED_QUERY}" 2>/dev/null || echo '[]')
    
    count=$(echo "$results" | jq 'length')
    
    if [[ "$count" -eq 0 ]]; then
      echo "No results found"
    else
      echo "Found $count result(s):"
      echo ""
      echo "$results" | jq -r '.[] | "• \(.title) (\(.year // "N/A"))\n  TVDB: \(.tvdbId) | Seasons: \(.seasons | length)\n  \(.overview[0:150])...\n"' | head -20
    fi
    ;;
    
  music)
    if [[ -z "$LIDARR_KEY" ]]; then
      echo "Error: LIDARR_KEY not set"
      exit 1
    fi
    
    echo "🎵 Searching Lidarr for: $QUERY"
    echo ""
    
    results=$(curl -sf -H "X-Api-Key: ${LIDARR_KEY}" \
      "http://${HOST}:8686/api/v1/search?term=${ENCODED_QUERY}" 2>/dev/null || echo '[]')
    
    count=$(echo "$results" | jq 'length')
    
    if [[ "$count" -eq 0 ]]; then
      echo "No results found"
    else
      echo "Found $count result(s):"
      echo ""
      echo "$results" | jq -r '.[] | "• \(.artistName) - \(.albumTitle // "Artist")\n  Type: \(.albumType // "Artist") | Year: \(.releaseDate[0:4] // "N/A")\n"' | head -20
    fi
    ;;
    
  *)
    echo "Error: Unknown type '$TYPE'"
    echo "Valid types: movie, series, music"
    exit 1
    ;;
esac
