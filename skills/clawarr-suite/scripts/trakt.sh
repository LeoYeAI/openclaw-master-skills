#!/usr/bin/env bash
# trakt.sh - Full Trakt.tv integration for media tracking
# Usage: trakt.sh <command> [options]
#
# Authentication:
#   auth                                  - Device code OAuth flow
#   auth-status                           - Check authentication status
#
# Profile & Stats:
#   profile [username]                    - Show user profile/stats
#   stats [username]                      - Detailed viewing statistics
#
# Watching & History:
#   watching                              - Currently watching (scrobble status)
#   history [movies|shows|episodes] [n]   - Watch history (default: 20)
#   sync-history <import|export> [file]   - Import/export watch history as JSON
#
# Scrobbling:
#   scrobble <start|pause|stop> <type> <id> [progress] - Manual scrobble
#   checkin <type> <title>                - Check in to something
#
# Lists & Collections:
#   watchlist [movies|shows]              - View watchlist
#   watchlist-add <type> <title|id>       - Add to watchlist
#   collection [movies|shows]             - View collection (owned media)
#   collection-add <type> <title|id>      - Add to collection
#   lists                                 - User's custom lists
#   list-items <list-slug>                - Items in a list
#
# Ratings:
#   ratings [movies|shows] [min_rating]   - View ratings
#   rate <type> <title|id> <1-10>         - Rate something
#
# Discovery:
#   recommendations [movies|shows]        - Personalized recommendations
#   trending [movies|shows]               - Trending content
#   popular [movies|shows]                - Most popular
#   calendar [movies|shows] [days]        - Upcoming releases (default: 7)
#
# Search:
#   search <query> [type]                 - Search Trakt (type: movie, show, all)
#
# Sync:
#   sync-plex                             - Sync Plex watch history to Trakt
#
# Traktarr Integration (Trakt → Arr):
#   traktarr-status                       - Check if traktarr is installed
#   traktarr-add <movies|shows> [list] [limit] - Add from Trakt list to Arr
#   traktarr-config                       - Show/edit traktarr config
#
# Retraktarr Integration (Arr → Trakt):
#   retraktarr-status                     - Check if retraktarr is installed
#   retraktarr-sync [movies|shows|all]    - Sync library to Trakt lists
#   retraktarr-config                     - Show/edit retraktarr config

set -euo pipefail

# API Configuration
CLIENT_ID="${TRAKT_CLIENT_ID:-}"
CLIENT_SECRET="${TRAKT_CLIENT_SECRET:-}"

if [[ -z "$CLIENT_ID" || -z "$CLIENT_SECRET" ]]; then
  echo "Error: TRAKT_CLIENT_ID and TRAKT_CLIENT_SECRET are required."
  echo ""
  echo "Create a Trakt API app at https://trakt.tv/oauth/applications/new"
  echo "Then export both variables:"
  echo "  export TRAKT_CLIENT_ID=your_client_id"
  echo "  export TRAKT_CLIENT_SECRET=your_client_secret"
  exit 1
fi
TOKEN_FILE="${TRAKT_TOKEN_FILE:-$HOME/.config/clawarr/trakt_tokens.json}"
API_BASE="https://api.trakt.tv"

if ! command -v jq &> /dev/null; then
  echo "❌ Error: jq is required"
  exit 1
fi

show_help() {
  head -n 50 "$0" | grep "^#" | sed 's/^# \?//'
  exit 0
}

# Helper: Load tokens from file
load_tokens() {
  if [[ ! -f "$TOKEN_FILE" ]]; then
    return 1
  fi
  
  ACCESS_TOKEN=$(jq -r '.access_token // empty' "$TOKEN_FILE" 2>/dev/null || echo "")
  REFRESH_TOKEN=$(jq -r '.refresh_token // empty' "$TOKEN_FILE" 2>/dev/null || echo "")
  EXPIRES_AT=$(jq -r '.expires_at // 0' "$TOKEN_FILE" 2>/dev/null || echo "0")
  
  if [[ -z "$ACCESS_TOKEN" ]]; then
    return 1
  fi
  
  return 0
}

# Helper: Save tokens to file
save_tokens() {
  local access=$1
  local refresh=$2
  local expires_in=$3
  
  local expires_at
  expires_at=$(($(date +%s) + expires_in))
  
  mkdir -p "$(dirname "$TOKEN_FILE")"
  
  cat > "$TOKEN_FILE" <<EOF
{
  "access_token": "$access",
  "refresh_token": "$refresh",
  "expires_at": $expires_at,
  "created_at": $(date +%s)
}
EOF
  
  chmod 600 "$TOKEN_FILE"
}

# Helper: Check if token is expired and refresh if needed
check_and_refresh_token() {
  if ! load_tokens; then
    echo "❌ Not authenticated. Run: trakt.sh auth"
    exit 1
  fi
  
  local now
  now=$(date +%s)
  
  # Refresh if expired or expiring in next hour
  if [[ $EXPIRES_AT -lt $((now + 3600)) ]]; then
    echo "🔄 Token expired, refreshing..."
    
    local response
    response=$(curl -sf -X POST "$API_BASE/oauth/token" \
      -H "Content-Type: application/json" \
      -d "{
        \"refresh_token\": \"$REFRESH_TOKEN\",
        \"client_id\": \"$CLIENT_ID\",
        \"client_secret\": \"$CLIENT_SECRET\",
        \"redirect_uri\": \"urn:ietf:wg:oauth:2.0:oob\",
        \"grant_type\": \"refresh_token\"
      }" || echo "")
    
    if [[ -z "$response" ]]; then
      echo "❌ Failed to refresh token. Re-authenticate: trakt.sh auth"
      exit 1
    fi
    
    local new_access
    new_access=$(echo "$response" | jq -r '.access_token')
    local new_refresh
    new_refresh=$(echo "$response" | jq -r '.refresh_token')
    local expires_in
    expires_in=$(echo "$response" | jq -r '.expires_in')
    
    save_tokens "$new_access" "$new_refresh" "$expires_in"
    load_tokens
    
    echo "✅ Token refreshed"
  fi
}

# Helper: Make authenticated API call
trakt_api() {
  local method=$1
  local endpoint=$2
  local data=${3:-}
  
  check_and_refresh_token
  
  local url="${API_BASE}${endpoint}"
  
  if [[ -n "$data" ]]; then
    curl -sf -X "$method" "$url" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -H "trakt-api-version: 2" \
      -H "trakt-api-key: $CLIENT_ID" \
      -d "$data"
  else
    curl -sf -X "$method" "$url" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -H "trakt-api-version: 2" \
      -H "trakt-api-key: $CLIENT_ID"
  fi
}

# Helper: Make public API call (no auth)
trakt_api_public() {
  local endpoint=$1
  
  curl -sf -X GET "${API_BASE}${endpoint}" \
    -H "Content-Type: application/json" \
    -H "trakt-api-version: 2" \
    -H "trakt-api-key: $CLIENT_ID"
}

# Command: auth (device flow)
cmd_auth() {
  echo "🔐 Trakt.tv Device Authentication"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  # Step 1: Generate device code
  echo "Generating device code..."
  local device_response
  device_response=$(curl -sf -X POST "$API_BASE/oauth/device/code" \
    -H "Content-Type: application/json" \
    -d "{\"client_id\": \"$CLIENT_ID\"}")
  
  local device_code
  device_code=$(echo "$device_response" | jq -r '.device_code')
  local user_code
  user_code=$(echo "$device_response" | jq -r '.user_code')
  local verification_url
  verification_url=$(echo "$device_response" | jq -r '.verification_url')
  local interval
  interval=$(echo "$device_response" | jq -r '.interval')
  local expires_in
  expires_in=$(echo "$device_response" | jq -r '.expires_in')
  
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  Visit: $verification_url"
  echo "  Enter code: $user_code"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "Waiting for authorization (expires in $expires_in seconds)..."
  
  # Step 2: Poll for token
  local max_attempts
  max_attempts=$((expires_in / interval))
  local attempt=0
  
  while [[ $attempt -lt $max_attempts ]]; do
    sleep "$interval"
    attempt=$((attempt + 1))
    
    local token_response
    token_response=$(curl -sf -X POST "$API_BASE/oauth/device/token" \
      -H "Content-Type: application/json" \
      -d "{
        \"code\": \"$device_code\",
        \"client_id\": \"$CLIENT_ID\",
        \"client_secret\": \"$CLIENT_SECRET\"
      }" 2>/dev/null || echo "")
    
    if [[ -n "$token_response" ]] && echo "$token_response" | jq -e '.access_token' > /dev/null 2>&1; then
      local access_token
      access_token=$(echo "$token_response" | jq -r '.access_token')
      local refresh_token
      refresh_token=$(echo "$token_response" | jq -r '.refresh_token')
      local token_expires_in
      token_expires_in=$(echo "$token_response" | jq -r '.expires_in')
      
      save_tokens "$access_token" "$refresh_token" "$token_expires_in"
      
      echo ""
      echo "✅ Successfully authenticated!"
      echo "Tokens saved to: $TOKEN_FILE"
      echo ""
      
      # Get user info
      ACCESS_TOKEN=$access_token
      local user_info
      user_info=$(trakt_api GET "/users/settings")
      local username
      username=$(echo "$user_info" | jq -r '.user.username')
      
      echo "Logged in as: $username"
      echo ""
      
      return 0
    fi
    
    echo -n "."
  done
  
  echo ""
  echo "❌ Authentication timed out. Please try again."
  exit 1
}

# Command: auth-status
cmd_auth_status() {
  echo "🔐 Trakt Authentication Status"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  if ! load_tokens; then
    echo "❌ Not authenticated"
    echo ""
    echo "Run: trakt.sh auth"
    echo ""
    exit 1
  fi
  
  local now
  now=$(date +%s)
  local time_remaining
  time_remaining=$((EXPIRES_AT - now))
  
  echo "✅ Authenticated"
  echo ""
  
  if [[ $time_remaining -gt 0 ]]; then
    local hours
    hours=$((time_remaining / 3600))
    local minutes
    minutes=$(((time_remaining % 3600) / 60))
    echo "Token expires in: ${hours}h ${minutes}m"
  else
    echo "Token expired (will auto-refresh on next use)"
  fi
  
  echo "Token file: $TOKEN_FILE"
  echo ""
  
  # Get user info
  local user_info
  user_info=$(trakt_api GET "/users/settings" 2>/dev/null || echo "")
  
  if [[ -n "$user_info" ]]; then
    local username
    username=$(echo "$user_info" | jq -r '.user.username')
    local name
    name=$(echo "$user_info" | jq -r '.user.name // "N/A"')
    local vip
    vip=$(echo "$user_info" | jq -r '.user.vip')
    
    echo "Username: $username"
    echo "Name: $name"
    echo "VIP: $vip"
    echo ""
  fi
}

# Command: profile
cmd_profile() {
  local username="${1:-me}"
  
  if [[ "$username" == "me" ]]; then
    username="me"
    echo "👤 Your Trakt Profile"
  else
    echo "👤 Trakt Profile: $username"
  fi
  
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  local user_info
  if [[ "$username" == "me" ]]; then
    user_info=$(trakt_api GET "/users/settings")
    username=$(echo "$user_info" | jq -r '.user.username')
  else
    user_info=$(trakt_api_public "/users/$username")
  fi
  
  local name
  name=$(echo "$user_info" | jq -r '.name // "N/A"')
  local location
  location=$(echo "$user_info" | jq -r '.location // "N/A"')
  local about
  about=$(echo "$user_info" | jq -r '.about // "N/A"')
  local joined
  joined=$(echo "$user_info" | jq -r '.joined_at // "N/A"' | cut -d'T' -f1)
  
  echo "Username: $username"
  echo "Name: $name"
  echo "Location: $location"
  echo "Joined: $joined"
  
  if [[ "$about" != "N/A" ]] && [[ -n "$about" ]]; then
    echo ""
    echo "About: $about"
  fi
  
  echo ""
  
  # Get stats
  local stats
  stats=$(trakt_api_public "/users/$username/stats")
  
  echo "Statistics:"
  echo "$stats" | jq -r '"  Movies watched: \(.movies.watched)
  Shows watched: \(.shows.watched)
  Episodes watched: \(.episodes.watched)
  Total plays: \(.episodes.plays + .movies.plays)
  Minutes watched: \(.minutes)"'
  
  echo ""
}

# Command: stats
cmd_stats() {
  local username="${1:-me}"
  
  if [[ "$username" == "me" ]]; then
    check_and_refresh_token
    local user_info
    user_info=$(trakt_api GET "/users/settings")
    username=$(echo "$user_info" | jq -r '.user.username')
  fi
  
  echo "📊 Detailed Statistics: $username"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  local stats
  stats=$(trakt_api_public "/users/$username/stats")
  
  echo "Movies:"
  echo "$stats" | jq -r '"  Watched: \(.movies.watched)
  Collected: \(.movies.collected)
  Ratings: \(.movies.ratings)
  Comments: \(.movies.comments)"'
  
  echo ""
  echo "Shows:"
  echo "$stats" | jq -r '"  Watched: \(.shows.watched)
  Collected: \(.shows.collected)
  Ratings: \(.shows.ratings)
  Comments: \(.shows.comments)"'
  
  echo ""
  echo "Episodes:"
  echo "$stats" | jq -r '"  Watched: \(.episodes.watched)
  Collected: \(.episodes.collected)
  Ratings: \(.episodes.ratings)
  Comments: \(.episodes.comments)
  Total plays: \(.episodes.plays)"'
  
  echo ""
  echo "Network:"
  echo "$stats" | jq -r '"  Friends: \(.network.friends)
  Followers: \(.network.followers)
  Following: \(.network.following)"'
  
  echo ""
  
  local minutes
  minutes=$(echo "$stats" | jq -r '.minutes')
  local hours
  hours=$((minutes / 60))
  local days
  days=$((hours / 24))
  
  echo "Total watch time: $minutes minutes ($hours hours, $days days)"
  echo ""
}

# Command: watching
cmd_watching() {
  echo "👀 Currently Watching"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  local watching
  watching=$(trakt_api GET "/users/me/watching")
  
  if [[ "$watching" == "null" ]] || [[ -z "$watching" ]]; then
    echo "  Not watching anything right now"
    echo ""
    return
  fi
  
  local type
  type=$(echo "$watching" | jq -r '.type')
  
  if [[ "$type" == "movie" ]]; then
    local title
    title=$(echo "$watching" | jq -r '.movie.title')
    local year
    year=$(echo "$watching" | jq -r '.movie.year')
    echo "  Movie: $title ($year)"
  elif [[ "$type" == "episode" ]]; then
    local show
    show=$(echo "$watching" | jq -r '.show.title')
    local season
    season=$(echo "$watching" | jq -r '.episode.season')
    local episode
    episode=$(echo "$watching" | jq -r '.episode.number')
    local ep_title
    ep_title=$(echo "$watching" | jq -r '.episode.title')
    echo "  Show: $show"
    echo "  Episode: S${season}E${episode} - $ep_title"
  fi
  
  local started
  started=$(echo "$watching" | jq -r '.started_at' | cut -d'T' -f1,2 | tr 'T' ' ')
  echo "  Started: $started"
  echo ""
}

# Command: history
cmd_history() {
  local type="${1:-all}"
  local limit="${2:-20}"
  
  local type_path=""
  case "$type" in
    movies) type_path="/movies" ;;
    shows) type_path="/shows" ;;
    episodes) type_path="/episodes" ;;
    all) type_path="" ;;
    *)
      echo "❌ Invalid type. Use: movies, shows, episodes, or all"
      exit 1
      ;;
  esac
  
  echo "📜 Watch History: $type (last $limit)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  local history
  history=$(trakt_api GET "/users/me/history${type_path}?limit=${limit}")
  
  echo "$history" | jq -r '.[] | 
    if .type == "movie" then
      (.watched_at | split("T")[0] + " " + (split("T")[1] | split(".")[0])) + "  " + .movie.title + " (" + (.movie.year | tostring) + ")"
    elif .type == "episode" then
      (.watched_at | split("T")[0] + " " + (split("T")[1] | split(".")[0])) + "  " + .show.title + " - S" + (.episode.season | tostring) + "E" + (.episode.number | tostring) + " - " + .episode.title
    else
      .watched_at + "  Unknown"
    end'
  
  echo ""
}

# Command: scrobble
cmd_scrobble() {
  local action="${1:-}"
  local type="${2:-}"
  local id="${3:-}"
  local progress="${4:-0}"
  
  if [[ -z "$action" ]] || [[ -z "$type" ]] || [[ -z "$id" ]]; then
    echo "Usage: trakt.sh scrobble <start|pause|stop> <movie|episode> <id> [progress]"
    exit 1
  fi
  
  local endpoint=""
  case "$action" in
    start) endpoint="/scrobble/start" ;;
    pause) endpoint="/scrobble/pause" ;;
    stop) endpoint="/scrobble/stop" ;;
    *)
      echo "❌ Invalid action. Use: start, pause, or stop"
      exit 1
      ;;
  esac
  
  echo "📡 Scrobble: $action $type"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  local data="{\"$type\": {\"ids\": {\"trakt\": $id}}, \"progress\": $progress}"
  
  local response
  response=$(trakt_api POST "$endpoint" "$data")
  
  if [[ -n "$response" ]]; then
    echo "✅ Scrobble successful"
    echo ""
  else
    echo "❌ Scrobble failed"
    exit 1
  fi
}

# Command: checkin
cmd_checkin() {
  local type="${1:-}"
  local title="${2:-}"
  
  if [[ -z "$type" ]] || [[ -z "$title" ]]; then
    echo "Usage: trakt.sh checkin <movie|show> <title>"
    exit 1
  fi
  
  echo "📍 Check-in: $title"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  # Search for the item
  local search
  search=$(trakt_api_public "/search/$type?query=$(echo "$title" | sed 's/ /%20/g')&limit=1")
  
  local item_id
  item_id=$(echo "$search" | jq -r ".[0].$type.ids.trakt")
  
  if [[ -z "$item_id" ]] || [[ "$item_id" == "null" ]]; then
    echo "❌ Could not find: $title"
    exit 1
  fi
  
  local data="{\"$type\": {\"ids\": {\"trakt\": $item_id}}}"
  
  local response
  response=$(trakt_api POST "/checkin" "$data")
  
  if [[ -n "$response" ]]; then
    echo "✅ Checked in to: $title"
    echo ""
  else
    echo "❌ Check-in failed"
    exit 1
  fi
}

# Command: watchlist
cmd_watchlist() {
  local type="${1:-all}"
  
  local type_path=""
  case "$type" in
    movies) type_path="/movies" ;;
    shows) type_path="/shows" ;;
    all) type_path="" ;;
    *)
      echo "❌ Invalid type. Use: movies, shows, or all"
      exit 1
      ;;
  esac
  
  echo "⭐ Watchlist: $type"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  local watchlist
  watchlist=$(trakt_api GET "/users/me/watchlist${type_path}")
  
  if [[ "$watchlist" == "[]" ]]; then
    echo "  Watchlist is empty"
    echo ""
    return
  fi
  
  echo "$watchlist" | jq -r '.[] | 
    if .type == "movie" then
      .movie.title + " (" + (.movie.year | tostring) + ")"
    elif .type == "show" then
      .show.title + " (" + (.show.year | tostring) + ")"
    else
      "Unknown"
    end'
  
  echo ""
}

# Command: watchlist-add
cmd_watchlist_add() {
  local type="${1:-}"
  local query="${2:-}"
  
  if [[ -z "$type" ]] || [[ -z "$query" ]]; then
    echo "Usage: trakt.sh watchlist-add <movie|show> <title|id>"
    exit 1
  fi
  
  echo "➕ Adding to watchlist: $query"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  # Check if it's a numeric ID or title
  local item_id=""
  if [[ "$query" =~ ^[0-9]+$ ]]; then
    item_id="$query"
  else
    # Search for the item
    local search
    search=$(trakt_api_public "/search/$type?query=$(echo "$query" | sed 's/ /%20/g')&limit=1")
    
    item_id=$(echo "$search" | jq -r ".[0].$type.ids.trakt")
    
    if [[ -z "$item_id" ]] || [[ "$item_id" == "null" ]]; then
      echo "❌ Could not find: $query"
      exit 1
    fi
  fi
  
  local data="{\"${type}s\": [{\"ids\": {\"trakt\": $item_id}}]}"
  
  local response
  response=$(trakt_api POST "/sync/watchlist" "$data")
  
  local added
  added=$(echo "$response" | jq -r ".added.${type}s")
  
  if [[ "$added" -gt 0 ]]; then
    echo "✅ Added to watchlist"
    echo ""
  else
    echo "⚠️  Already in watchlist"
    echo ""
  fi
}

# Command: collection
cmd_collection() {
  local type="${1:-all}"
  
  local type_path=""
  case "$type" in
    movies) type_path="/movies" ;;
    shows) type_path="/shows" ;;
    all) type_path="" ;;
    *)
      echo "❌ Invalid type. Use: movies, shows, or all"
      exit 1
      ;;
  esac
  
  echo "📚 Collection: $type"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  local collection
  collection=$(trakt_api GET "/users/me/collection${type_path}")
  
  if [[ "$collection" == "[]" ]]; then
    echo "  Collection is empty"
    echo ""
    return
  fi
  
  echo "$collection" | jq -r '.[] | 
    if .type == "movie" then
      .movie.title + " (" + (.movie.year | tostring) + ")"
    elif .type == "show" then
      .show.title + " - " + (.seasons | length | tostring) + " seasons"
    else
      "Unknown"
    end'
  
  echo ""
}

# Command: collection-add
cmd_collection_add() {
  local type="${1:-}"
  local query="${2:-}"
  
  if [[ -z "$type" ]] || [[ -z "$query" ]]; then
    echo "Usage: trakt.sh collection-add <movie|show> <title|id>"
    exit 1
  fi
  
  echo "➕ Adding to collection: $query"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  # Check if it's a numeric ID or title
  local item_id=""
  if [[ "$query" =~ ^[0-9]+$ ]]; then
    item_id="$query"
  else
    # Search for the item
    local search
    search=$(trakt_api_public "/search/$type?query=$(echo "$query" | sed 's/ /%20/g')&limit=1")
    
    item_id=$(echo "$search" | jq -r ".[0].$type.ids.trakt")
    
    if [[ -z "$item_id" ]] || [[ "$item_id" == "null" ]]; then
      echo "❌ Could not find: $query"
      exit 1
    fi
  fi
  
  local data="{\"${type}s\": [{\"ids\": {\"trakt\": $item_id}}]}"
  
  local response
  response=$(trakt_api POST "/sync/collection" "$data")
  
  local added
  added=$(echo "$response" | jq -r ".added.${type}s")
  
  if [[ "$added" -gt 0 ]]; then
    echo "✅ Added to collection"
    echo ""
  else
    echo "⚠️  Already in collection"
    echo ""
  fi
}

# Command: ratings
cmd_ratings() {
  local type="${1:-all}"
  local min_rating="${2:-1}"
  
  local type_path=""
  case "$type" in
    movies) type_path="/movies" ;;
    shows) type_path="/shows" ;;
    all) type_path="" ;;
    *)
      echo "❌ Invalid type. Use: movies, shows, or all"
      exit 1
      ;;
  esac
  
  echo "⭐ Your Ratings: $type (>= $min_rating)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  local ratings
  ratings=$(trakt_api GET "/users/me/ratings${type_path}/${min_rating}")
  
  if [[ "$ratings" == "[]" ]]; then
    echo "  No ratings found"
    echo ""
    return
  fi
  
  echo "$ratings" | jq -r '.[] | 
    if .type == "movie" then
      (.rating | tostring) + "/10  " + .movie.title + " (" + (.movie.year | tostring) + ")"
    elif .type == "show" then
      (.rating | tostring) + "/10  " + .show.title + " (" + (.show.year | tostring) + ")"
    else
      "Unknown"
    end' | sort -rn
  
  echo ""
}

# Command: rate
cmd_rate() {
  local type="${1:-}"
  local query="${2:-}"
  local rating="${3:-}"
  
  if [[ -z "$type" ]] || [[ -z "$query" ]] || [[ -z "$rating" ]]; then
    echo "Usage: trakt.sh rate <movie|show> <title|id> <1-10>"
    exit 1
  fi
  
  if [[ ! "$rating" =~ ^[1-9]$|^10$ ]]; then
    echo "❌ Rating must be between 1 and 10"
    exit 1
  fi
  
  echo "⭐ Rating: $query"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  # Check if it's a numeric ID or title
  local item_id=""
  if [[ "$query" =~ ^[0-9]+$ ]]; then
    item_id="$query"
  else
    # Search for the item
    local search
    search=$(trakt_api_public "/search/$type?query=$(echo "$query" | sed 's/ /%20/g')&limit=1")
    
    item_id=$(echo "$search" | jq -r ".[0].$type.ids.trakt")
    
    if [[ -z "$item_id" ]] || [[ "$item_id" == "null" ]]; then
      echo "❌ Could not find: $query"
      exit 1
    fi
  fi
  
  local data="{\"${type}s\": [{\"ids\": {\"trakt\": $item_id}, \"rating\": $rating}]}"
  
  local response
  response=$(trakt_api POST "/sync/ratings" "$data")
  
  local added
  added=$(echo "$response" | jq -r ".added.${type}s")
  
  if [[ "$added" -gt 0 ]]; then
    echo "✅ Rated $rating/10"
    echo ""
  else
    echo "⚠️  Rating may have already existed (updated)"
    echo ""
  fi
}

# Command: recommendations
cmd_recommendations() {
  local type="${1:-movies}"
  
  if [[ "$type" != "movies" ]] && [[ "$type" != "shows" ]]; then
    echo "❌ Invalid type. Use: movies or shows"
    exit 1
  fi
  
  echo "💡 Personalized Recommendations: $type"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  local recs
  recs=$(trakt_api GET "/recommendations/$type?limit=20")
  
  if [[ "$recs" == "[]" ]]; then
    echo "  No recommendations available"
    echo "  (Rate more content to get recommendations)"
    echo ""
    return
  fi
  
  echo "$recs" | jq -r '.[] | .title + " (" + (.year | tostring) + ")"'
  
  echo ""
}

# Command: trending
cmd_trending() {
  local type="${1:-movies}"
  
  if [[ "$type" != "movies" ]] && [[ "$type" != "shows" ]]; then
    echo "❌ Invalid type. Use: movies or shows"
    exit 1
  fi
  
  echo "🔥 Trending: $type"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  local trending
  trending=$(trakt_api_public "/$type/trending?limit=20")
  
  echo "$trending" | jq -r '.[] | 
    if .movie then
      .movie.title + " (" + (.movie.year | tostring) + ") - " + (.watchers | tostring) + " watchers"
    elif .show then
      .show.title + " (" + (.show.year | tostring) + ") - " + (.watchers | tostring) + " watchers"
    else
      "Unknown"
    end'
  
  echo ""
}

# Command: popular
cmd_popular() {
  local type="${1:-movies}"
  
  if [[ "$type" != "movies" ]] && [[ "$type" != "shows" ]]; then
    echo "❌ Invalid type. Use: movies or shows"
    exit 1
  fi
  
  echo "📈 Most Popular: $type"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  local popular
  popular=$(trakt_api_public "/$type/popular?limit=20")
  
  echo "$popular" | jq -r '.[] | .title + " (" + (.year | tostring) + ")"'
  
  echo ""
}

# Command: calendar
cmd_calendar() {
  local type="${1:-all}"
  local days="${2:-7}"
  
  local today
  today=$(date -u +"%Y-%m-%d")
  
  echo "📅 Upcoming Releases: $type (next $days days)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  if [[ "$type" == "movies" ]] || [[ "$type" == "all" ]]; then
    echo "Movies:"
    local movies
    movies=$(trakt_api GET "/calendars/my/movies/$today/$days")
    
    if [[ "$movies" == "[]" ]]; then
      echo "  No movie releases"
    else
      echo "$movies" | jq -r '.[] | .released + "  " + .movie.title + " (" + (.movie.year | tostring) + ")"'
    fi
    echo ""
  fi
  
  if [[ "$type" == "shows" ]] || [[ "$type" == "all" ]]; then
    echo "TV Shows:"
    local shows
    shows=$(trakt_api GET "/calendars/my/shows/$today/$days")
    
    if [[ "$shows" == "[]" ]]; then
      echo "  No show releases"
    else
      echo "$shows" | jq -r '.[] | 
        .first_aired + "  " + .show.title + " - S" + (.episode.season | tostring) + "E" + (.episode.number | tostring) + " - " + .episode.title'
    fi
    echo ""
  fi
}

# Command: lists
cmd_lists() {
  echo "📋 Your Custom Lists"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  local lists
  lists=$(trakt_api GET "/users/me/lists")
  
  if [[ "$lists" == "[]" ]]; then
    echo "  No custom lists"
    echo ""
    return
  fi
  
  echo "$lists" | jq -r '.[] | .name + " (" + (.item_count | tostring) + " items) - " + .ids.slug'
  
  echo ""
}

# Command: list-items
cmd_list_items() {
  local slug="${1:-}"
  
  if [[ -z "$slug" ]]; then
    echo "Usage: trakt.sh list-items <list-slug>"
    echo ""
    echo "Get slug from: trakt.sh lists"
    exit 1
  fi
  
  echo "📋 List Items: $slug"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  local items
  items=$(trakt_api GET "/users/me/lists/$slug/items")
  
  if [[ "$items" == "[]" ]]; then
    echo "  List is empty"
    echo ""
    return
  fi
  
  echo "$items" | jq -r '.[] | 
    if .type == "movie" then
      .movie.title + " (" + (.movie.year | tostring) + ")"
    elif .type == "show" then
      .show.title + " (" + (.show.year | tostring) + ")"
    else
      "Unknown"
    end'
  
  echo ""
}

# Command: search
cmd_search() {
  local query="${1:-}"
  local type="${2:-all}"
  
  if [[ -z "$query" ]]; then
    echo "Usage: trakt.sh search <query> [type]"
    echo "Types: movie, show, all"
    exit 1
  fi
  
  local type_param=""
  if [[ "$type" != "all" ]]; then
    type_param="&type=$type"
  fi
  
  echo "🔍 Search Results: $query"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  local results
  results=$(trakt_api_public "/search/$type?query=$(echo "$query" | sed 's/ /%20/g')&limit=20${type_param}")
  
  if [[ "$results" == "[]" ]]; then
    echo "  No results found"
    echo ""
    return
  fi
  
  echo "$results" | jq -r '.[] | 
    if .movie then
      "[MOVIE] " + .movie.title + " (" + (.movie.year | tostring) + ") - ID: " + (.movie.ids.trakt | tostring)
    elif .show then
      "[SHOW]  " + .show.title + " (" + (.show.year | tostring) + ") - ID: " + (.show.ids.trakt | tostring)
    else
      "Unknown"
    end'
  
  echo ""
}

# Command: sync-history (import/export)
cmd_sync_history() {
  local action="${1:-export}"
  local file="${2:-trakt_history.json}"
  
  if [[ "$action" == "export" ]]; then
    echo "📤 Exporting watch history to: $file"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    local history
    history=$(trakt_api GET "/users/me/history?limit=10000")
    
    echo "$history" > "$file"
    
    local count
    count=$(echo "$history" | jq 'length')
    
    echo "✅ Exported $count items to: $file"
    echo ""
    
  elif [[ "$action" == "import" ]]; then
    echo "📥 Importing watch history from: $file"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    if [[ ! -f "$file" ]]; then
      echo "❌ File not found: $file"
      exit 1
    fi
    
    local history
    history=$(cat "$file")
    
    # Transform to sync format
    local movies
    movies=$(echo "$history" | jq '[.[] | select(.type == "movie") | {ids: .movie.ids, watched_at: .watched_at}]')
    local episodes
    episodes=$(echo "$history" | jq '[.[] | select(.type == "episode") | {ids: .episode.ids, watched_at: .watched_at}]')
    
    local data
    data=$(jq -n --argjson movies "$movies" --argjson episodes "$episodes" '{movies: $movies, episodes: $episodes}')
    
    local response
    response=$(trakt_api POST "/sync/history" "$data")
    
    local added_movies
    added_movies=$(echo "$response" | jq -r '.added.movies')
    local added_episodes
    added_episodes=$(echo "$response" | jq -r '.added.episodes')
    
    echo "✅ Imported:"
    echo "  Movies: $added_movies"
    echo "  Episodes: $added_episodes"
    echo ""
  else
    echo "❌ Invalid action. Use: export or import"
    exit 1
  fi
}

# Command: sync-plex
cmd_sync_plex() {
  echo "🔄 Syncing Plex History to Trakt"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  # Check for Tautulli
  if [[ -z "${TAUTULLI_KEY:-}" ]] || [[ -z "${CLAWARR_HOST:-}" ]]; then
    echo "❌ Tautulli not configured"
    echo "Set: TAUTULLI_KEY and CLAWARR_HOST"
    exit 1
  fi
  
  echo "Fetching Plex watch history..."
  
  # Get watch history from Tautulli
  local tautulli_history
  tautulli_history=$(curl -sf "http://${CLAWARR_HOST}:8181/api/v2?apikey=${TAUTULLI_KEY}&cmd=get_history&length=500")
  
  if [[ -z "$tautulli_history" ]]; then
    echo "❌ Failed to fetch Tautulli history"
    exit 1
  fi
  
  local total_items
  total_items=$(echo "$tautulli_history" | jq -r '.response.data.recordsFiltered')
  
  echo "Found $total_items items in Plex history"
  echo ""
  echo "Processing and syncing to Trakt..."
  echo "(This may take a while for large libraries)"
  echo ""
  
  # Transform Tautulli data to Trakt format
  # Note: This is a simplified version - production would need better matching
  local movies='[]'
  local episodes='[]'
  
  echo "$tautulli_history" | jq -r '.response.data.data[] | 
    select(.watched_status == 1) | 
    {
      title: .full_title,
      year: .year,
      type: (if .media_type == "movie" then "movie" elif .media_type == "episode" then "episode" else "unknown" end),
      watched_at: (.date | tonumber | todate)
    }' | while IFS= read -r line; do
    
    local item_type
    item_type=$(echo "$line" | jq -r '.type')
    
    if [[ "$item_type" == "movie" ]]; then
      local title
      title=$(echo "$line" | jq -r '.title')
      local year
      year=$(echo "$line" | jq -r '.year')
      
      # Search Trakt for this movie
      local search
      search=$(trakt_api_public "/search/movie?query=$(echo "$title" | sed 's/ /%20/g')&year=$year&limit=1")
      
      local trakt_id
      trakt_id=$(echo "$search" | jq -r '.[0].movie.ids.trakt')
      
      if [[ -n "$trakt_id" ]] && [[ "$trakt_id" != "null" ]]; then
        movies=$(echo "$movies" | jq --argjson item "{\"ids\": {\"trakt\": $trakt_id}}" '. + [$item]')
      fi
    fi
    
    # Rate limiting
    sleep 0.5
  done
  
  # Sync to Trakt
  if [[ "$movies" != "[]" ]]; then
    local movie_count
    movie_count=$(echo "$movies" | jq 'length')
    
    echo "Syncing $movie_count movies to Trakt..."
    
    local data
    data=$(jq -n --argjson movies "$movies" '{movies: $movies}')
    
    local response
    response=$(trakt_api POST "/sync/history" "$data")
    
    local added
    added=$(echo "$response" | jq -r '.added.movies')
    
    echo "✅ Added $added movies to Trakt history"
  else
    echo "⚠️  No movies to sync"
  fi
  
  echo ""
  echo "Note: Episode syncing requires more complex matching and is not yet implemented"
  echo ""
}

# Helper: Find traktarr executable
find_traktarr() {
  # Check common locations
  if command -v traktarr &> /dev/null; then
    echo "traktarr"
    return 0
  elif [[ -f "$HOME/.local/bin/traktarr" ]]; then
    echo "$HOME/.local/bin/traktarr"
    return 0
  elif [[ -f "/usr/local/bin/traktarr" ]]; then
    echo "/usr/local/bin/traktarr"
    return 0
  fi
  return 1
}

# Helper: Find retraktarr executable
find_retraktarr() {
  # Check common locations
  if command -v retraktarr &> /dev/null; then
    echo "retraktarr"
    return 0
  elif [[ -f "$HOME/.local/bin/retraktarr" ]]; then
    echo "$HOME/.local/bin/retraktarr"
    return 0
  elif [[ -f "/usr/local/bin/retraktarr" ]]; then
    echo "/usr/local/bin/retraktarr"
    return 0
  fi
  return 1
}

# Helper: Get traktarr config path
get_traktarr_config() {
  local config_paths=(
    "$HOME/.config/traktarr/config.json"
    "$HOME/.traktarr/config.json"
    "/config/traktarr/config.json"
  )
  
  for path in "${config_paths[@]}"; do
    if [[ -f "$path" ]]; then
      echo "$path"
      return 0
    fi
  done
  
  # Return default path
  echo "$HOME/.config/traktarr/config.json"
  return 1
}

# Helper: Get retraktarr config path
get_retraktarr_config() {
  local config_paths=(
    "$HOME/.config/retraktarr/config.json"
    "$HOME/.retraktarr/config.json"
    "/config/retraktarr/config.json"
  )
  
  for path in "${config_paths[@]}"; do
    if [[ -f "$path" ]]; then
      echo "$path"
      return 0
    fi
  done
  
  # Return default path
  echo "$HOME/.config/retraktarr/config.json"
  return 1
}

# Command: traktarr-status
cmd_traktarr_status() {
  echo "🔍 Traktarr Status"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  local traktarr_bin=""
  if traktarr_bin=$(find_traktarr); then
    echo "✅ Traktarr found: $traktarr_bin"
    
    # Get version
    if [[ -x "$traktarr_bin" ]]; then
      echo ""
      "$traktarr_bin" --version 2>/dev/null || echo "   (version unknown)"
    fi
  else
    echo "❌ Traktarr not found"
    echo ""
    echo "Install with: pip install traktarr"
    echo "Or: git clone https://github.com/l3uddz/traktarr && cd traktarr && pip install -r requirements.txt"
    echo ""
    return 1
  fi
  
  echo ""
  
  # Check config
  local config_file
  config_file=$(get_traktarr_config)
  
  if [[ -f "$config_file" ]]; then
    echo "✅ Config found: $config_file"
    echo ""
    
    # Show config summary
    echo "Configuration:"
    
    if command -v jq &> /dev/null; then
      local trakt_client
      trakt_client=$(jq -r '.trakt.client_id // "not set"' "$config_file" 2>/dev/null)
      local radarr_url
      radarr_url=$(jq -r '.radarr.url // "not set"' "$config_file" 2>/dev/null)
      local sonarr_url
      sonarr_url=$(jq -r '.sonarr.url // "not set"' "$config_file" 2>/dev/null)
      
      echo "  Trakt Client ID: ${trakt_client:0:10}..."
      echo "  Radarr URL: $radarr_url"
      echo "  Sonarr URL: $sonarr_url"
    else
      echo "  (jq not available for parsing)"
    fi
  else
    echo "⚠️  Config not found: $config_file"
    echo ""
    echo "Run: trakt.sh traktarr-config"
    echo "Or manually create config"
  fi
  
  echo ""
}

# Command: traktarr-add
cmd_traktarr_add() {
  local type="${1:-}"
  local list="${2:-anticipated}"
  local limit="${3:-10}"
  
  if [[ -z "$type" ]]; then
    echo "Usage: trakt.sh traktarr-add <movies|shows> [list] [limit]"
    echo ""
    echo "Lists: anticipated, trending, popular, boxoffice, watched, played"
    echo "       Or custom list slug from Trakt"
    exit 1
  fi
  
  if [[ "$type" != "movies" ]] && [[ "$type" != "shows" ]]; then
    echo "❌ Type must be 'movies' or 'shows'"
    exit 1
  fi
  
  echo "➕ Adding from Trakt to $(echo "$type" | sed 's/s$//')arr"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  local traktarr_bin=""
  if ! traktarr_bin=$(find_traktarr); then
    echo "❌ Traktarr not installed"
    echo "Run: trakt.sh traktarr-status"
    exit 1
  fi
  
  echo "Source: $list"
  echo "Type: $type"
  echo "Limit: $limit"
  echo ""
  
  # Build traktarr command
  local cmd="$traktarr_bin --add-limit=$limit"
  
  if [[ "$type" == "movies" ]]; then
    cmd="$cmd movies"
  else
    cmd="$cmd shows"
  fi
  
  # Add list type
  case "$list" in
    anticipated|trending|popular|boxoffice|watched|played)
      cmd="$cmd -t $list"
      ;;
    *)
      # Assume custom list
      cmd="$cmd -l $list"
      ;;
  esac
  
  echo "Running: $cmd"
  echo ""
  
  # Execute
  if $cmd; then
    echo ""
    echo "✅ Traktarr add complete"
  else
    echo ""
    echo "❌ Traktarr failed (check config and logs)"
    exit 1
  fi
  
  echo ""
}

# Command: traktarr-config
cmd_traktarr_config() {
  echo "⚙️  Traktarr Configuration"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  local config_file
  config_file=$(get_traktarr_config)
  
  if [[ -f "$config_file" ]]; then
    echo "Config file: $config_file"
    echo ""
    
    # Show current config
    if command -v jq &> /dev/null; then
      echo "Current configuration:"
      jq '.' "$config_file" 2>/dev/null || cat "$config_file"
    else
      cat "$config_file"
    fi
    
    echo ""
    echo "To edit: $EDITOR $config_file"
  else
    echo "Config file not found: $config_file"
    echo ""
    echo "Create configuration? (y/n)"
    read -r create
    
    if [[ "$create" != "y" ]]; then
      echo "Cancelled"
      exit 0
    fi
    
    echo ""
    echo "Creating traktarr config..."
    
    mkdir -p "$(dirname "$config_file")"
    
    # Get required values
    echo -n "Radarr URL (http://HOST:7878): "
    read -r radarr_url
    radarr_url="${radarr_url:-http://${CLAWARR_HOST:-localhost}:7878}"
    
    echo -n "Radarr API Key: "
    read -r radarr_key
    radarr_key="${radarr_key:-${RADARR_KEY:-}}"
    
    echo -n "Sonarr URL (http://HOST:8989): "
    read -r sonarr_url
    sonarr_url="${sonarr_url:-http://${CLAWARR_HOST:-localhost}:8989}"
    
    echo -n "Sonarr API Key: "
    read -r sonarr_key
    sonarr_key="${sonarr_key:-${SONARR_KEY:-}}"
    
    # Create config
    cat > "$config_file" <<EOF
{
  "core": {
    "debug": false
  },
  "trakt": {
    "client_id": "$CLIENT_ID",
    "client_secret": "$CLIENT_SECRET"
  },
  "radarr": {
    "url": "$radarr_url",
    "api_key": "$radarr_key",
    "root_folder": "/movies",
    "quality_profile": "HD-1080p",
    "minimum_availability": "released"
  },
  "sonarr": {
    "url": "$sonarr_url",
    "api_key": "$sonarr_key",
    "root_folder": "/tv",
    "quality_profile": "HD-1080p",
    "language_profile": "English"
  },
  "filters": {
    "movies": {
      "allowed_countries": ["us", "gb", "ca"],
      "allowed_languages": ["en"],
      "blacklisted_genres": ["anime"],
      "blacklisted_min_year": 1990,
      "rating_limit": 5.0
    },
    "shows": {
      "allowed_countries": ["us", "gb", "ca"],
      "allowed_languages": ["en"],
      "blacklisted_genres": ["anime"],
      "blacklisted_networks": [],
      "rating_limit": 5.0
    }
  },
  "automatic": {
    "movies": {
      "anticipated": 10,
      "trending": 5,
      "popular": 5
    },
    "shows": {
      "anticipated": 10,
      "trending": 5,
      "popular": 5
    }
  }
}
EOF
    
    echo ""
    echo "✅ Config created: $config_file"
    echo ""
    echo "Edit config: $EDITOR $config_file"
    echo "Test with: trakt.sh traktarr-status"
  fi
  
  echo ""
}

# Command: retraktarr-status
cmd_retraktarr_status() {
  echo "🔍 Retraktarr Status"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  local retraktarr_bin=""
  if retraktarr_bin=$(find_retraktarr); then
    echo "✅ Retraktarr found: $retraktarr_bin"
    
    # Get version
    if [[ -x "$retraktarr_bin" ]]; then
      echo ""
      "$retraktarr_bin" --version 2>/dev/null || echo "   (version unknown)"
    fi
  else
    echo "❌ Retraktarr not found"
    echo ""
    echo "Install with: pip install retraktarr"
    echo "Or: git clone https://github.com/l3uddz/retraktarr && cd retraktarr && pip install -r requirements.txt"
    echo ""
    return 1
  fi
  
  echo ""
  
  # Check config
  local config_file
  config_file=$(get_retraktarr_config)
  
  if [[ -f "$config_file" ]]; then
    echo "✅ Config found: $config_file"
    echo ""
    
    # Show config summary
    echo "Configuration:"
    
    if command -v jq &> /dev/null; then
      local trakt_client
      trakt_client=$(jq -r '.trakt.client_id // "not set"' "$config_file" 2>/dev/null)
      local radarr_url
      radarr_url=$(jq -r '.radarr.url // "not set"' "$config_file" 2>/dev/null)
      local sonarr_url
      sonarr_url=$(jq -r '.sonarr.url // "not set"' "$config_file" 2>/dev/null)
      
      echo "  Trakt Client ID: ${trakt_client:0:10}..."
      echo "  Radarr URL: $radarr_url"
      echo "  Sonarr URL: $sonarr_url"
    else
      echo "  (jq not available for parsing)"
    fi
  else
    echo "⚠️  Config not found: $config_file"
    echo ""
    echo "Run: trakt.sh retraktarr-config"
    echo "Or manually create config"
  fi
  
  echo ""
}

# Command: retraktarr-sync
cmd_retraktarr_sync() {
  local type="${1:-all}"
  
  if [[ "$type" != "movies" ]] && [[ "$type" != "shows" ]] && [[ "$type" != "all" ]]; then
    echo "Usage: trakt.sh retraktarr-sync [movies|shows|all]"
    exit 1
  fi
  
  echo "🔄 Syncing Library to Trakt"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  local retraktarr_bin=""
  if ! retraktarr_bin=$(find_retraktarr); then
    echo "❌ Retraktarr not installed"
    echo "Run: trakt.sh retraktarr-status"
    exit 1
  fi
  
  echo "Syncing: $type"
  echo ""
  
  # Build retraktarr command
  local cmd="$retraktarr_bin sync"
  
  case "$type" in
    movies)
      cmd="$cmd --movies"
      ;;
    shows)
      cmd="$cmd --shows"
      ;;
    all)
      # Default is all
      ;;
  esac
  
  echo "Running: $cmd"
  echo ""
  
  # Execute
  if $cmd; then
    echo ""
    echo "✅ Retraktarr sync complete"
    echo ""
    echo "Your library is now synced to Trakt lists:"
    echo "  • Movies: https://trakt.tv/users/me/lists/radarr-library"
    echo "  • Shows: https://trakt.tv/users/me/lists/sonarr-library"
  else
    echo ""
    echo "❌ Retraktarr failed (check config and logs)"
    exit 1
  fi
  
  echo ""
}

# Command: retraktarr-config
cmd_retraktarr_config() {
  echo "⚙️  Retraktarr Configuration"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  local config_file
  config_file=$(get_retraktarr_config)
  
  if [[ -f "$config_file" ]]; then
    echo "Config file: $config_file"
    echo ""
    
    # Show current config
    if command -v jq &> /dev/null; then
      echo "Current configuration:"
      jq '.' "$config_file" 2>/dev/null || cat "$config_file"
    else
      cat "$config_file"
    fi
    
    echo ""
    echo "To edit: $EDITOR $config_file"
  else
    echo "Config file not found: $config_file"
    echo ""
    echo "Create configuration? (y/n)"
    read -r create
    
    if [[ "$create" != "y" ]]; then
      echo "Cancelled"
      exit 0
    fi
    
    echo ""
    echo "Creating retraktarr config..."
    
    mkdir -p "$(dirname "$config_file")"
    
    # Get required values
    echo -n "Radarr URL (http://HOST:7878): "
    read -r radarr_url
    radarr_url="${radarr_url:-http://${CLAWARR_HOST:-localhost}:7878}"
    
    echo -n "Radarr API Key: "
    read -r radarr_key
    radarr_key="${radarr_key:-${RADARR_KEY:-}}"
    
    echo -n "Sonarr URL (http://HOST:8989): "
    read -r sonarr_url
    sonarr_url="${sonarr_url:-http://${CLAWARR_HOST:-localhost}:8989}"
    
    echo -n "Sonarr API Key: "
    read -r sonarr_key
    sonarr_key="${sonarr_key:-${SONARR_KEY:-}}"
    
    # Create config
    cat > "$config_file" <<EOF
{
  "core": {
    "debug": false
  },
  "trakt": {
    "client_id": "$CLIENT_ID",
    "client_secret": "$CLIENT_SECRET"
  },
  "radarr": {
    "url": "$radarr_url",
    "api_key": "$radarr_key",
    "list_name": "radarr-library",
    "list_privacy": "private"
  },
  "sonarr": {
    "url": "$sonarr_url",
    "api_key": "$sonarr_key",
    "list_name": "sonarr-library",
    "list_privacy": "private"
  },
  "sync": {
    "interval_hours": 24,
    "remove_from_trakt": false
  }
}
EOF
    
    echo ""
    echo "✅ Config created: $config_file"
    echo ""
    echo "Edit config: $EDITOR $config_file"
    echo "Test with: trakt.sh retraktarr-status"
  fi
  
  echo ""
}

# Main command router
COMMAND="${1:-help}"

case "$COMMAND" in
  auth)                cmd_auth ;;
  auth-status)         cmd_auth_status ;;
  profile)             cmd_profile "${2:-me}" ;;
  stats)               cmd_stats "${2:-me}" ;;
  watching)            cmd_watching ;;
  history)             cmd_history "${2:-all}" "${3:-20}" ;;
  scrobble)            cmd_scrobble "${2:-}" "${3:-}" "${4:-}" "${5:-0}" ;;
  checkin)             cmd_checkin "${2:-}" "${3:-}" ;;
  watchlist)           cmd_watchlist "${2:-all}" ;;
  watchlist-add)       cmd_watchlist_add "${2:-}" "${3:-}" ;;
  collection)          cmd_collection "${2:-all}" ;;
  collection-add)      cmd_collection_add "${2:-}" "${3:-}" ;;
  ratings)             cmd_ratings "${2:-all}" "${3:-1}" ;;
  rate)                cmd_rate "${2:-}" "${3:-}" "${4:-}" ;;
  recommendations)     cmd_recommendations "${2:-movies}" ;;
  trending)            cmd_trending "${2:-movies}" ;;
  popular)             cmd_popular "${2:-movies}" ;;
  calendar)            cmd_calendar "${2:-all}" "${3:-7}" ;;
  lists)               cmd_lists ;;
  list-items)          cmd_list_items "${2:-}" ;;
  search)              cmd_search "${2:-}" "${3:-all}" ;;
  sync-history)        cmd_sync_history "${2:-export}" "${3:-trakt_history.json}" ;;
  sync-plex)           cmd_sync_plex ;;
  traktarr-status)     cmd_traktarr_status ;;
  traktarr-add)        cmd_traktarr_add "${2:-}" "${3:-anticipated}" "${4:-10}" ;;
  traktarr-config)     cmd_traktarr_config ;;
  retraktarr-status)   cmd_retraktarr_status ;;
  retraktarr-sync)     cmd_retraktarr_sync "${2:-all}" ;;
  retraktarr-config)   cmd_retraktarr_config ;;
  help|--help|-h)      show_help ;;
  *)
    echo "❌ Unknown command: $COMMAND"
    echo "Run '$0 help' for usage"
    exit 1
    ;;
esac
