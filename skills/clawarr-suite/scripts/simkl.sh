#!/usr/bin/env bash
# simkl.sh - Simkl integration
# Usage: simkl.sh <command> [options]
#
# Commands:
#   auth                  - OAuth authentication
#   profile [username]    - Show user profile
#   stats                 - Viewing statistics
#   history [type]        - Watch history (all, movies, shows, anime)
#   watchlist [type]      - View watchlist
#   sync                  - Sync with Plex/Sonarr/Radarr

set -euo pipefail

# Simkl API Configuration
# Note: You'll need to register your own app at https://simkl.com/settings/developer
CLIENT_ID="${SIMKL_CLIENT_ID:-}"
CLIENT_SECRET="${SIMKL_CLIENT_SECRET:-}"
TOKEN_FILE="${SIMKL_TOKEN_FILE:-$HOME/.config/clawarr/simkl_tokens.json}"
API_BASE="https://api.simkl.com"

if ! command -v jq &> /dev/null; then
  echo "❌ Error: jq is required"
  exit 1
fi

show_help() {
  head -n 14 "$0" | grep "^#" | sed 's/^# \?//'
  exit 0
}

# Helper: Load tokens from file
load_tokens() {
  if [[ ! -f "$TOKEN_FILE" ]]; then
    return 1
  fi
  
  ACCESS_TOKEN=$(jq -r '.access_token // empty' "$TOKEN_FILE" 2>/dev/null || echo "")
  
  if [[ -z "$ACCESS_TOKEN" ]]; then
    return 1
  fi
  
  return 0
}

# Helper: Save tokens to file
save_tokens() {
  local access=$1
  
  mkdir -p "$(dirname "$TOKEN_FILE")"
  
  cat > "$TOKEN_FILE" <<EOF
{
  "access_token": "$access",
  "created_at": $(date +%s)
}
EOF
  
  chmod 600 "$TOKEN_FILE"
}

# Helper: Make authenticated API call
simkl_api() {
  local method=$1
  local endpoint=$2
  local data=${3:-}
  
  if ! load_tokens; then
    echo "❌ Not authenticated. Run: simkl.sh auth"
    exit 1
  fi
  
  local url="${API_BASE}${endpoint}"
  
  if [[ -n "$data" ]]; then
    curl -sf -X "$method" "$url" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -H "simkl-api-key: $CLIENT_ID" \
      -d "$data"
  else
    curl -sf -X "$method" "$url" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -H "simkl-api-key: $CLIENT_ID"
  fi
}

# Helper: Make public API call (no auth)
simkl_api_public() {
  local endpoint=$1
  
  if [[ -z "$CLIENT_ID" ]]; then
    echo "❌ SIMKL_CLIENT_ID not set"
    exit 1
  fi
  
  curl -sf -X GET "${API_BASE}${endpoint}" \
    -H "Content-Type: application/json" \
    -H "simkl-api-key: $CLIENT_ID"
}

# Command: auth
cmd_auth() {
  echo "🔐 Simkl Authentication"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  if [[ -z "$CLIENT_ID" ]] || [[ -z "$CLIENT_SECRET" ]]; then
    echo "❌ Simkl API credentials not configured"
    echo ""
    echo "To set up Simkl integration:"
    echo "  1. Go to: https://simkl.com/settings/developer"
    echo "  2. Create a new application"
    echo "  3. Set redirect URI to: urn:ietf:wg:oauth:2.0:oob"
    echo "  4. Set environment variables:"
    echo "       export SIMKL_CLIENT_ID='your_client_id'"
    echo "       export SIMKL_CLIENT_SECRET='your_client_secret'"
    echo ""
    exit 1
  fi
  
  echo "Step 1: Visit the authorization URL..."
  echo ""
  
  local auth_url="https://simkl.com/oauth/authorize?response_type=code&client_id=${CLIENT_ID}&redirect_uri=urn:ietf:wg:oauth:2.0:oob"
  
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "Visit: $auth_url"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "After authorizing, you'll receive a code."
  echo -n "Enter the authorization code: "
  read -r auth_code
  
  if [[ -z "$auth_code" ]]; then
    echo "❌ No code provided"
    exit 1
  fi
  
  echo ""
  echo "Exchanging code for access token..."
  
  local token_response
  token_response=$(curl -sf -X POST "${API_BASE}/oauth/token" \
    -H "Content-Type: application/json" \
    -d "{
      \"code\": \"$auth_code\",
      \"client_id\": \"$CLIENT_ID\",
      \"client_secret\": \"$CLIENT_SECRET\",
      \"redirect_uri\": \"urn:ietf:wg:oauth:2.0:oob\",
      \"grant_type\": \"authorization_code\"
    }")
  
  if [[ -z "$token_response" ]]; then
    echo "❌ Failed to get access token"
    exit 1
  fi
  
  local access_token
  access_token=$(echo "$token_response" | jq -r '.access_token')
  
  if [[ -z "$access_token" ]] || [[ "$access_token" == "null" ]]; then
    echo "❌ Invalid response from Simkl"
    echo "$token_response" | jq '.'
    exit 1
  fi
  
  save_tokens "$access_token"
  
  echo "✅ Successfully authenticated!"
  echo "Token saved to: $TOKEN_FILE"
  echo ""
}

# Command: profile
cmd_profile() {
  local username="${1:-}"
  
  echo "👤 Simkl Profile"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  local user_info
  if [[ -z "$username" ]]; then
    user_info=$(simkl_api GET "/users/settings")
  else
    user_info=$(simkl_api_public "/users/$username")
  fi
  
  local name
  name=$(echo "$user_info" | jq -r '.user.name // .name')
  local account_name
  account_name=$(echo "$user_info" | jq -r '.account.id // "N/A"')
  local joined
  joined=$(echo "$user_info" | jq -r '.joined_at // "N/A"')
  
  echo "Name: $name"
  echo "Account: $account_name"
  echo "Joined: $joined"
  echo ""
}

# Command: stats
cmd_stats() {
  echo "📊 Simkl Statistics"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  local stats
  stats=$(simkl_api GET "/users/settings")
  
  echo "Stats:"
  echo "$stats" | jq -r '
    if .stats then
      "  Movies watched: \(.stats.movies.watched // 0)
  Shows watched: \(.stats.tv.watched // 0)
  Episodes watched: \(.stats.tv.episodes_watched // 0)
  Anime watched: \(.stats.anime.watched // 0)"
    else
      "  Stats not available"
    end'
  
  echo ""
}

# Command: history
cmd_history() {
  local type="${1:-all}"
  
  echo "📜 Watch History: $type"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  local endpoint=""
  case "$type" in
    movies) endpoint="/sync/all-items/movies/watched" ;;
    shows) endpoint="/sync/all-items/shows/watched" ;;
    anime) endpoint="/sync/all-items/anime/watched" ;;
    all)
      echo "Movies:"
      simkl_api GET "/sync/all-items/movies/watched" | jq -r '.movies[]? | "  " + .movie.title + " (" + (.movie.year | tostring) + ")"' | head -10
      echo ""
      echo "Shows:"
      simkl_api GET "/sync/all-items/shows/watched" | jq -r '.shows[]? | "  " + .show.title' | head -10
      echo ""
      return
      ;;
    *)
      echo "❌ Invalid type. Use: all, movies, shows, or anime"
      exit 1
      ;;
  esac
  
  local history
  history=$(simkl_api GET "$endpoint")
  
  if [[ "$type" == "movies" ]]; then
    echo "$history" | jq -r '.movies[]? | "  " + .movie.title + " (" + (.movie.year | tostring) + ")"' | head -20
  else
    echo "$history" | jq -r '.shows[]? | "  " + .show.title' | head -20
  fi
  
  echo ""
}

# Command: watchlist
cmd_watchlist() {
  local type="${1:-all}"
  
  echo "⭐ Watchlist: $type"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  local endpoint=""
  case "$type" in
    movies) endpoint="/sync/watchlist/movies" ;;
    shows) endpoint="/sync/watchlist/shows" ;;
    all)
      echo "Movies:"
      simkl_api GET "/sync/watchlist/movies" | jq -r '.[]? | "  " + .movie.title + " (" + (.movie.year | tostring) + ")"' | head -10
      echo ""
      echo "Shows:"
      simkl_api GET "/sync/watchlist/shows" | jq -r '.[]? | "  " + .show.title' | head -10
      echo ""
      return
      ;;
    *)
      echo "❌ Invalid type. Use: all, movies, or shows"
      exit 1
      ;;
  esac
  
  local watchlist
  watchlist=$(simkl_api GET "$endpoint")
  
  if [[ "$type" == "movies" ]]; then
    echo "$watchlist" | jq -r '.[]? | "  " + .movie.title + " (" + (.movie.year | tostring) + ")"'
  else
    echo "$watchlist" | jq -r '.[]? | "  " + .show.title'
  fi
  
  echo ""
}

# Command: sync
cmd_sync() {
  echo "🔄 Syncing with Plex"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  # Check for Tautulli
  if [[ -z "${TAUTULLI_KEY:-}" ]] || [[ -z "${CLAWARR_HOST:-}" ]]; then
    echo "❌ Tautulli not configured"
    echo "Set: TAUTULLI_KEY and CLAWARR_HOST"
    exit 1
  fi
  
  echo "Fetching Plex watch history..."
  
  local tautulli_history
  tautulli_history=$(curl -sf "http://${CLAWARR_HOST}:8181/api/v2?apikey=${TAUTULLI_KEY}&cmd=get_history&length=100")
  
  if [[ -z "$tautulli_history" ]]; then
    echo "❌ Failed to fetch Tautulli history"
    exit 1
  fi
  
  echo "Processing watched items..."
  echo ""
  
  # Build Simkl sync payload
  local movies='[]'
  local shows='[]'
  
  echo "$tautulli_history" | jq -c '.response.data.data[] | select(.watched_status == 1)' | while IFS= read -r item; do
    local media_type
    media_type=$(echo "$item" | jq -r '.media_type')
    local title
    title=$(echo "$item" | jq -r '.full_title')
    
    echo "  $title"
  done
  
  echo ""
  echo "⚠️  Full Simkl sync not yet implemented"
  echo "   (Requires proper ID matching and API mapping)"
  echo ""
}

# Main command router
COMMAND="${1:-help}"

case "$COMMAND" in
  auth)        cmd_auth ;;
  profile)     cmd_profile "${2:-}" ;;
  stats)       cmd_stats ;;
  history)     cmd_history "${2:-all}" ;;
  watchlist)   cmd_watchlist "${2:-all}" ;;
  sync)        cmd_sync ;;
  help|--help|-h) show_help ;;
  *)
    echo "❌ Unknown command: $COMMAND"
    echo "Run '$0 help' for usage"
    exit 1
    ;;
esac
