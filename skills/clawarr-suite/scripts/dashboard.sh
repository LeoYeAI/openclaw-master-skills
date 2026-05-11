#!/usr/bin/env bash
# dashboard.sh - Generate premium self-contained HTML dashboard
# Usage: dashboard.sh [output_file]
#
# Generates a comprehensive 1440p-optimized HTML dashboard with:
# - Hero stats with SVG progress rings
# - Library health with quality distribution charts
# - Active streams and download queue
# - Service health grid with response times
# - Analytics with sparklines and donut charts
# - Recent additions and watch history
#
# Output defaults to: clawarr-dashboard.html

set -euo pipefail

HOST="${CLAWARR_HOST:-}"
SONARR_KEY="${SONARR_KEY:-}"
RADARR_KEY="${RADARR_KEY:-}"
TAUTULLI_KEY="${TAUTULLI_KEY:-}"
SABNZBD_KEY="${SABNZBD_KEY:-}"
PROWLARR_KEY="${PROWLARR_KEY:-}"
OVERSEERR_KEY="${OVERSEERR_KEY:-}"
BAZARR_KEY="${BAZARR_KEY:-}"
PLEX_TOKEN="${PLEX_TOKEN:-}"

OUTPUT_FILE="${1:-clawarr-dashboard.html}"

if [[ -z "$HOST" ]]; then
  echo "❌ Error: CLAWARR_HOST not set"
  exit 1
fi

if ! command -v jq &> /dev/null; then
  echo "❌ Error: jq is required"
  exit 1
fi

echo "📊 Generating ClawARR Premium Dashboard (1440p optimized)..."
echo "   Host: $HOST"
echo "   Output: $OUTPUT_FILE"
echo ""

# API helper for *arr apps with response time measurement
api_call() {
  local app=$1
  local endpoint=$2
  local key="" port="" api_ver=""
  
  case "$app" in
    radarr)   key="$RADARR_KEY"; port=7878; api_ver="v3" ;;
    sonarr)   key="$SONARR_KEY"; port=8989; api_ver="v3" ;;
    prowlarr) key="$PROWLARR_KEY"; port=9696; api_ver="v1" ;;
    bazarr)   key="$BAZARR_KEY"; port=6767; api_ver="" ;;
    *) echo "{}"; return 1 ;;
  esac
  
  [[ -z "$key" ]] && echo "{}" && return 1
  
  local url="http://${HOST}:${port}/api/${api_ver}${endpoint}"
  if [[ "$app" == "bazarr" ]]; then
    url="http://${HOST}:${port}/api${endpoint}"
  fi
  
  curl -sf -H "X-Api-Key: $key" "$url" 2>/dev/null || echo "{}"
}

# Measure API response time (using curl's time_total)
measure_response_time() {
  local url=$1
  local auth_header=${2:-}
  
  local time_ms
  if [[ -n "$auth_header" ]]; then
    time_ms=$(curl -sf -o /dev/null -w "%{time_total}" -H "$auth_header" "$url" 2>/dev/null || echo "0")
  else
    time_ms=$(curl -sf -o /dev/null -w "%{time_total}" "$url" 2>/dev/null || echo "0")
  fi
  
  if [[ "$time_ms" == "0" || -z "$time_ms" ]]; then
    echo "N/A"
  else
    # Convert seconds to milliseconds and round
    echo "$time_ms" | awk '{printf "%.0f", $1 * 1000}'
  fi
}

# Collect data
echo "📡 Collecting data from services..."

# Initialize all variables with defaults
RADARR_TOTAL=0 RADARR_MONITORED=0 RADARR_DOWNLOADED=0 RADARR_MISSING=0 RADARR_SIZE=0 RADARR_SIZE_GB=0 RADARR_DOWNLOADING=0
SONARR_TOTAL=0 SONARR_MONITORED=0 SONARR_SIZE=0 SONARR_SIZE_GB=0 SONARR_DOWNLOADING=0 SONARR_EPISODES=0 SONARR_EPISODE_FILES=0
SABNZBD_SPEED="0 B/s" SABNZBD_SIZE_LEFT="0 B" SABNZBD_TIME_LEFT="0:00:00" SABNZBD_PAUSED="false" SABNZBD_ITEMS=0
TAUTULLI_STREAMS=0
OVERSEERR_PENDING=0 OVERSEERR_TOTAL=0
PROWLARR_TOTAL=0 PROWLARR_ENABLED=0
BAZARR_TOTAL=0

RADARR_MOVIES="{}" SONARR_SERIES="{}" RADARR_QUEUE="{}" SONARR_QUEUE="{}"
RADARR_RECENT="[]" SONARR_RECENT="[]"
TAUTULLI_ACTIVITY="{}" TAUTULLI_HISTORY="{}" TAUTULLI_PLAYS="[]"
SABNZBD_QUEUE="{}"

# Quality distribution variables
QUAL_4K=0 QUAL_1080P=0 QUAL_720P=0 QUAL_SD=0

# Genre data
GENRE_DATA=""

# Radarr stats
if [[ -n "$RADARR_KEY" ]]; then
  echo "  • Radarr..."
  RADARR_MOVIES=$(api_call radarr "/movie")
  RADARR_QUEUE=$(api_call radarr "/queue")
  RADARR_RECENT=$(api_call radarr "/movie" | jq '[.[] | select(.hasFile == true)] | sort_by(.added) | reverse | .[0:10]')
  
  RADARR_TOTAL=$(echo "$RADARR_MOVIES" | jq 'length')
  RADARR_MONITORED=$(echo "$RADARR_MOVIES" | jq '[.[] | select(.monitored == true)] | length')
  RADARR_DOWNLOADED=$(echo "$RADARR_MOVIES" | jq '[.[] | select(.hasFile == true)] | length')
  RADARR_MISSING=$(echo "$RADARR_MOVIES" | jq '[.[] | select(.monitored == true and .hasFile == false)] | length')
  RADARR_SIZE=$(echo "$RADARR_MOVIES" | jq '[.[] | select(.hasFile == true) | .sizeOnDisk] | add // 0')
  RADARR_SIZE_GB=$(echo "scale=1; $RADARR_SIZE / 1073741824" | bc 2>/dev/null || echo "0")
  RADARR_DOWNLOADING=$(echo "$RADARR_QUEUE" | jq 'if .records then .records | length else 0 end')
  
  # Quality distribution from Radarr
  QUAL_4K=$(echo "$RADARR_MOVIES" | jq '[.[] | select(.hasFile == true) | select(.movieFile.quality.quality.resolution >= 2160)] | length')
  QUAL_1080P=$(echo "$RADARR_MOVIES" | jq '[.[] | select(.hasFile == true) | select(.movieFile.quality.quality.resolution == 1080)] | length')
  QUAL_720P=$(echo "$RADARR_MOVIES" | jq '[.[] | select(.hasFile == true) | select(.movieFile.quality.quality.resolution == 720)] | length')
  QUAL_SD=$(echo "$RADARR_MOVIES" | jq '[.[] | select(.hasFile == true) | select(.movieFile.quality.quality.resolution < 720)] | length')
  
  # Genre distribution (top 5)
  GENRE_DATA=$(echo "$RADARR_MOVIES" | jq -r '[.[] | .genres[]?] | group_by(.) | map({genre: .[0], count: length}) | sort_by(.count) | reverse | .[0:5] | map("\(.genre):\(.count)") | join(",")')
fi

# Sonarr stats
if [[ -n "$SONARR_KEY" ]]; then
  echo "  • Sonarr..."
  SONARR_SERIES=$(api_call sonarr "/series")
  SONARR_QUEUE=$(api_call sonarr "/queue")
  SONARR_RECENT=$(api_call sonarr "/episode" | jq '[.[] | select(.hasFile == true)] | sort_by(.airDateUtc) | reverse | .[0:10]')
  
  SONARR_TOTAL=$(echo "$SONARR_SERIES" | jq 'length')
  SONARR_MONITORED=$(echo "$SONARR_SERIES" | jq '[.[] | select(.monitored == true)] | length')
  SONARR_SIZE=$(echo "$SONARR_SERIES" | jq '[.[] | .statistics.sizeOnDisk] | add // 0')
  SONARR_SIZE_GB=$(echo "scale=1; $SONARR_SIZE / 1073741824" | bc 2>/dev/null || echo "0")
  SONARR_DOWNLOADING=$(echo "$SONARR_QUEUE" | jq 'if .records then .records | length else 0 end')
  SONARR_EPISODES=$(echo "$SONARR_SERIES" | jq '[.[] | .statistics.episodeCount] | add // 0')
  SONARR_EPISODE_FILES=$(echo "$SONARR_SERIES" | jq '[.[] | .statistics.episodeFileCount] | add // 0')
fi

# SABnzbd stats
if [[ -n "$SABNZBD_KEY" ]]; then
  echo "  • SABnzbd..."
  SABNZBD_QUEUE=$(curl -sf "http://${HOST}:38080/api?apikey=${SABNZBD_KEY}&mode=queue&output=json" 2>/dev/null || echo '{}')
  SABNZBD_SPEED=$(echo "$SABNZBD_QUEUE" | jq -r '.queue.speed // "0 B/s"')
  SABNZBD_SIZE_LEFT=$(echo "$SABNZBD_QUEUE" | jq -r '.queue.sizeleft // "0 B"')
  SABNZBD_TIME_LEFT=$(echo "$SABNZBD_QUEUE" | jq -r '.queue.timeleft // "0:00:00"')
  SABNZBD_PAUSED=$(echo "$SABNZBD_QUEUE" | jq -r '.queue.paused // false')
  SABNZBD_ITEMS=$(echo "$SABNZBD_QUEUE" | jq '.queue.slots | length')
fi

# Tautulli stats
if [[ -n "$TAUTULLI_KEY" ]]; then
  echo "  • Tautulli..."
  TAUTULLI_ACTIVITY=$(curl -sf "http://${HOST}:8181/api/v2?apikey=${TAUTULLI_KEY}&cmd=get_activity" 2>/dev/null || echo '{}')
  TAUTULLI_HISTORY=$(curl -sf "http://${HOST}:8181/api/v2?apikey=${TAUTULLI_KEY}&cmd=get_history&length=10" 2>/dev/null || echo '{}')
  TAUTULLI_PLAYS=$(curl -sf "http://${HOST}:8181/api/v2?apikey=${TAUTULLI_KEY}&cmd=get_plays_by_date&time_range=30" 2>/dev/null | jq -r '.response.data.series_1_data // []')
  
  TAUTULLI_STREAMS=$(echo "$TAUTULLI_ACTIVITY" | jq -r '.response.data.stream_count // 0')
fi

# Overseerr stats
if [[ -n "$OVERSEERR_KEY" ]]; then
  echo "  • Overseerr..."
  OVERSEERR_REQUESTS=$(curl -sf -H "X-Api-Key: $OVERSEERR_KEY" "http://${HOST}:5055/api/v1/request?take=100" 2>/dev/null || echo '{}')
  OVERSEERR_PENDING=$(echo "$OVERSEERR_REQUESTS" | jq '[.results[]? | select(.media.status == 2)] | length')
  OVERSEERR_TOTAL=$(echo "$OVERSEERR_REQUESTS" | jq '.results | length')
fi

# Prowlarr indexers
if [[ -n "$PROWLARR_KEY" ]]; then
  echo "  • Prowlarr..."
  PROWLARR_INDEXERS=$(api_call prowlarr "/indexer")
  PROWLARR_TOTAL=$(echo "$PROWLARR_INDEXERS" | jq 'length')
  PROWLARR_ENABLED=$(echo "$PROWLARR_INDEXERS" | jq '[.[] | select(.enable == true)] | length')
fi

# Bazarr stats
if [[ -n "$BAZARR_KEY" ]]; then
  echo "  • Bazarr..."
  BAZARR_STATUS=$(api_call bazarr "/system/status")
  BAZARR_TOTAL=$(echo "$BAZARR_STATUS" | jq -r '.data // 0')
fi

# Service health checks
echo "  • Measuring service response times..."
SONARR_RT=$(measure_response_time "http://${HOST}:8989/api/v3/health" "X-Api-Key: $SONARR_KEY")
RADARR_RT=$(measure_response_time "http://${HOST}:7878/api/v3/health" "X-Api-Key: $RADARR_KEY")
PLEX_RT=$(measure_response_time "http://${HOST}:32400/identity" "")
TAUTULLI_RT=$(measure_response_time "http://${HOST}:8181/api/v2?cmd=arnold" "")
SABNZBD_RT=$(measure_response_time "http://${HOST}:38080/api?mode=version" "")
OVERSEERR_RT=$(measure_response_time "http://${HOST}:5055/api/v1/status" "")
PROWLARR_RT=$(measure_response_time "http://${HOST}:9696/api/v1/health" "X-Api-Key: $PROWLARR_KEY")
BAZARR_RT=$(measure_response_time "http://${HOST}:6767/api/system/status" "X-Api-Key: $BAZARR_KEY")

# Calculate total storage
TOTAL_SIZE_GB=$(echo "scale=1; $RADARR_SIZE_GB + $SONARR_SIZE_GB" | bc)
TOTAL_STORAGE_TB=24  # Estimated based on typical NAS setups (can be made dynamic via df)
TOTAL_USED_TB=$(echo "scale=2; $TOTAL_SIZE_GB / 1024" | bc)

# Calculate percentages
if [[ $RADARR_MONITORED -gt 0 ]]; then
  RADARR_PERCENT=$(echo "scale=1; ($RADARR_DOWNLOADED * 100) / $RADARR_MONITORED" | bc)
else
  RADARR_PERCENT=0
fi

if [[ $SONARR_EPISODES -gt 0 ]]; then
  SONARR_PERCENT=$(echo "scale=1; ($SONARR_EPISODE_FILES * 100) / $SONARR_EPISODES" | bc)
else
  SONARR_PERCENT=0
fi

if [[ $TOTAL_STORAGE_TB -gt 0 ]]; then
  STORAGE_PERCENT=$(echo "scale=1; ($TOTAL_USED_TB * 100) / $TOTAL_STORAGE_TB" | bc)
else
  STORAGE_PERCENT=0
fi

TOTAL_MISSING=$((RADARR_MISSING + (SONARR_EPISODES - SONARR_EPISODE_FILES)))
TIMESTAMP=$(date "+%Y-%m-%d %H:%M")

echo "✅ Data collected. Generating premium HTML..."

# Start building HTML
cat > "$OUTPUT_FILE" << 'HTML_START'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ClawARR Dashboard</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
      background: #0a0e1a;
      color: #ffffff;
      padding: 24px;
      min-height: 100vh;
      line-height: 1.6;
    }
    
    .container {
      max-width: 2560px;
      margin: 0 auto;
    }
    
    /* Top Bar */
    .top-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 20px 32px;
      background: #111827;
      border: 1px solid rgba(59,130,246,0.15);
      border-radius: 12px;
      margin-bottom: 32px;
      backdrop-filter: blur(10px);
    }
    
    .logo {
      font-size: 28px;
      font-weight: 700;
      background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    
    .service-status {
      display: flex;
      gap: 16px;
      align-items: center;
    }
    
    .status-dot {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      color: #94a3b8;
    }
    
    .dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: #10b981;
      box-shadow: 0 0 8px rgba(16,185,129,0.5);
    }
    
    .dot.offline { background: #ef4444; box-shadow: 0 0 8px rgba(239,68,68,0.5); }
    .dot.warning { background: #f59e0b; box-shadow: 0 0 8px rgba(245,158,11,0.5); }
    
    .timestamp {
      font-size: 14px;
      color: #64748b;
    }
    
    /* Grid layouts */
    .row-5 {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 20px;
      margin-bottom: 24px;
    }
    
    .row-3 {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      margin-bottom: 24px;
    }
    
    .row-1 {
      display: grid;
      grid-template-columns: 1fr;
      gap: 20px;
      margin-bottom: 24px;
    }
    
    /* Card styles */
    .card {
      background: #111827;
      border: 1px solid rgba(59,130,246,0.15);
      border-radius: 12px;
      padding: 24px;
      position: relative;
      overflow: hidden;
      backdrop-filter: blur(10px);
    }
    
    .card::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    }
    
    .card.accent-green::before { background: #10b981; }
    .card.accent-amber::before { background: #f59e0b; }
    .card.accent-purple::before { background: #8b5cf6; }
    .card.accent-red::before { background: #ef4444; }
    
    .card-icon {
      position: absolute;
      top: 24px;
      right: 24px;
      font-size: 48px;
      opacity: 0.15;
    }
    
    .card-title {
      font-size: 14px;
      color: #94a3b8;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 12px;
      font-weight: 600;
    }
    
    .card-value {
      font-size: 56px;
      font-weight: 700;
      color: #ffffff;
      line-height: 1;
      margin-bottom: 8px;
      text-shadow: 0 0 20px rgba(59,130,246,0.3);
    }
    
    .card-subtitle {
      font-size: 14px;
      color: #64748b;
    }
    
    /* SVG Progress Ring */
    .progress-ring-container {
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      width: 140px;
      height: 140px;
      margin: 0 auto;
    }
    
    .progress-ring-text {
      position: absolute;
      font-size: 24px;
      font-weight: 700;
      color: #ffffff;
    }
    
    .progress-ring-subtitle {
      position: absolute;
      bottom: 30px;
      font-size: 11px;
      color: #64748b;
    }
    
    /* Stacked bar chart */
    .stacked-bar {
      width: 100%;
      height: 40px;
      background: rgba(0,0,0,0.3);
      border-radius: 8px;
      overflow: hidden;
      display: flex;
      margin: 16px 0;
    }
    
    .bar-segment {
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      font-weight: 600;
      color: #ffffff;
      transition: all 0.3s ease;
    }
    
    .bar-segment:hover {
      filter: brightness(1.2);
    }
    
    .bar-legend {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      margin-top: 12px;
    }
    
    .legend-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
    }
    
    .legend-color {
      width: 16px;
      height: 16px;
      border-radius: 4px;
    }
    
    .legend-label {
      color: #94a3b8;
    }
    
    .legend-value {
      color: #ffffff;
      font-weight: 600;
      margin-left: auto;
    }
    
    /* Activity list */
    .activity-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
      max-height: 400px;
      overflow-y: auto;
    }
    
    .activity-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px;
      background: rgba(255,255,255,0.03);
      border-radius: 8px;
      border: 1px solid rgba(255,255,255,0.05);
    }
    
    .activity-item:nth-child(even) {
      background: rgba(255,255,255,0.05);
    }
    
    .activity-thumb {
      width: 48px;
      height: 48px;
      border-radius: 6px;
      background: rgba(59,130,246,0.2);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      flex-shrink: 0;
    }
    
    .activity-info {
      flex: 1;
      min-width: 0;
    }
    
    .activity-title {
      font-size: 14px;
      font-weight: 600;
      color: #ffffff;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    
    .activity-meta {
      font-size: 12px;
      color: #64748b;
    }
    
    .activity-badge {
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 11px;
      font-weight: 600;
      white-space: nowrap;
    }
    
    .badge-4k { background: #3b82f6; color: #ffffff; }
    .badge-1080p { background: #10b981; color: #ffffff; }
    .badge-720p { background: #f59e0b; color: #ffffff; }
    .badge-sd { background: #ef4444; color: #ffffff; }
    
    /* Progress bar */
    .progress-bar-container {
      width: 100%;
      height: 8px;
      background: rgba(0,0,0,0.3);
      border-radius: 4px;
      overflow: hidden;
      margin: 8px 0;
    }
    
    .progress-bar-fill {
      height: 100%;
      background: linear-gradient(90deg, #3b82f6, #8b5cf6);
      border-radius: 4px;
      transition: width 0.3s ease;
    }
    
    /* Service grid */
    .service-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
    }
    
    .service-card {
      padding: 16px;
      background: rgba(255,255,255,0.03);
      border: 1px solid rgba(255,255,255,0.05);
      border-radius: 8px;
      display: flex;
      align-items: center;
      gap: 12px;
    }
    
    .service-icon {
      font-size: 32px;
      flex-shrink: 0;
    }
    
    .service-info {
      flex: 1;
      min-width: 0;
    }
    
    .service-name {
      font-size: 14px;
      font-weight: 600;
      color: #ffffff;
    }
    
    .service-rt {
      font-size: 12px;
      color: #64748b;
    }
    
    .service-status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #10b981;
      box-shadow: 0 0 8px rgba(16,185,129,0.5);
      flex-shrink: 0;
    }
    
    .service-status-dot.offline { background: #ef4444; box-shadow: 0 0 8px rgba(239,68,68,0.5); }
    .service-status-dot.slow { background: #f59e0b; box-shadow: 0 0 8px rgba(245,158,11,0.5); }
    
    /* Empty state */
    .empty-state {
      text-align: center;
      padding: 40px;
      color: #64748b;
      font-size: 14px;
    }
    
    .empty-state-icon {
      font-size: 48px;
      margin-bottom: 12px;
      opacity: 0.3;
    }
    
    /* Footer */
    footer {
      text-align: center;
      padding: 32px;
      color: #64748b;
      font-size: 13px;
      margin-top: 48px;
      border-top: 1px solid rgba(255,255,255,0.05);
    }
    
    /* Responsive */
    @media (max-width: 1920px) {
      .row-5 { grid-template-columns: repeat(3, 1fr); }
      .service-grid { grid-template-columns: repeat(3, 1fr); }
    }
    
    @media (max-width: 1440px) {
      .row-5 { grid-template-columns: repeat(2, 1fr); }
      .service-grid { grid-template-columns: repeat(2, 1fr); }
    }
    
    @media (max-width: 1024px) {
      .row-5, .row-3 { grid-template-columns: 1fr; }
      .service-grid { grid-template-columns: 1fr; }
      .top-bar { flex-direction: column; gap: 16px; }
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
      width: 8px;
      height: 8px;
    }
    
    ::-webkit-scrollbar-track {
      background: rgba(0,0,0,0.2);
    }
    
    ::-webkit-scrollbar-thumb {
      background: rgba(59,130,246,0.3);
      border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
      background: rgba(59,130,246,0.5);
    }
  </style>
</head>
<body>
  <div class="container">
    
    <!-- Top Bar -->
    <div class="top-bar">
      <div class="logo">ClawARR</div>
      <div class="service-status">
        <div class="status-dot"><div class="dot SERVICE_STATUS_SONARR"></div> Sonarr</div>
        <div class="status-dot"><div class="dot SERVICE_STATUS_RADARR"></div> Radarr</div>
        <div class="status-dot"><div class="dot SERVICE_STATUS_PLEX"></div> Plex</div>
        <div class="status-dot"><div class="dot SERVICE_STATUS_SAB"></div> SABnzbd</div>
      </div>
      <div class="timestamp">Generated: TIMESTAMP_PH</div>
    </div>
    
    <!-- ROW 1: Hero Stats -->
    <div class="row-5">
      
      <div class="card">
        <div class="card-icon">🎬</div>
        <div class="card-title">Total Movies</div>
        <div class="card-value">RADARR_TOTAL_PH</div>
        <div class="card-subtitle">RADARR_MONITORED_PH monitored</div>
      </div>
      
      <div class="card accent-purple">
        <div class="card-icon">📺</div>
        <div class="card-title">Total TV Shows</div>
        <div class="card-value">SONARR_TOTAL_PH</div>
        <div class="card-subtitle">SONARR_MONITORED_PH monitored</div>
      </div>
      
      <div class="card accent-green">
        <div class="card-icon">📼</div>
        <div class="card-title">Total Episodes</div>
        <div class="card-value" style="font-size: 36px;">SONARR_EPISODE_FILES_PH / SONARR_EPISODES_PH</div>
        <div class="card-subtitle">SONARR_PERCENT_PH% complete</div>
      </div>
      
      <div class="card accent-amber">
        <div class="card-icon">💾</div>
        <div class="card-title">Storage</div>
        <div class="progress-ring-container">
          <svg width="140" height="140">
            <circle cx="70" cy="70" r="60" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="12"/>
            <circle cx="70" cy="70" r="60" fill="none" stroke="#f59e0b" stroke-width="12"
              stroke-dasharray="376.99" stroke-dashoffset="STORAGE_DASH_PH"
              transform="rotate(-90 70 70)" stroke-linecap="round"/>
          </svg>
          <div class="progress-ring-text">TOTAL_USED_TB_PH TB</div>
        </div>
        <div class="card-subtitle" style="text-align: center; margin-top: -20px;">of TOTAL_STORAGE_TB_PH TB used</div>
      </div>
      
      <div class="card accent-green">
        <div class="card-icon">▶️</div>
        <div class="card-title">Active Streams</div>
        <div class="card-value">TAUTULLI_STREAMS_PH</div>
        <div class="card-subtitle">Currently watching</div>
      </div>
      
    </div>
    
    <!-- ROW 2: Library Health -->
    <div class="row-3">
      
      <div class="card">
        <div class="card-title">Quality Distribution</div>
        <div class="stacked-bar">
          <div class="bar-segment" style="width: QUAL_4K_PERCENT_PH%; background: #3b82f6;">QUAL_4K_PH</div>
          <div class="bar-segment" style="width: QUAL_1080P_PERCENT_PH%; background: #10b981;">QUAL_1080P_PH</div>
          <div class="bar-segment" style="width: QUAL_720P_PERCENT_PH%; background: #f59e0b;">QUAL_720P_PH</div>
          <div class="bar-segment" style="width: QUAL_SD_PERCENT_PH%; background: #ef4444;">QUAL_SD_PH</div>
        </div>
        <div class="bar-legend">
          <div class="legend-item">
            <div class="legend-color" style="background: #3b82f6;"></div>
            <div class="legend-label">4K</div>
            <div class="legend-value">QUAL_4K_PERCENT_DISPLAY_PH%</div>
          </div>
          <div class="legend-item">
            <div class="legend-color" style="background: #10b981;"></div>
            <div class="legend-label">1080p</div>
            <div class="legend-value">QUAL_1080P_PERCENT_DISPLAY_PH%</div>
          </div>
          <div class="legend-item">
            <div class="legend-color" style="background: #f59e0b;"></div>
            <div class="legend-label">720p</div>
            <div class="legend-value">QUAL_720P_PERCENT_DISPLAY_PH%</div>
          </div>
          <div class="legend-item">
            <div class="legend-color" style="background: #ef4444;"></div>
            <div class="legend-label">SD</div>
            <div class="legend-value">QUAL_SD_PERCENT_DISPLAY_PH%</div>
          </div>
        </div>
      </div>
      
      <div class="card accent-amber">
        <div class="card-title">Missing Content</div>
        <div class="card-value" style="font-size: 42px; color: #f59e0b;">TOTAL_MISSING_PH</div>
        <div class="card-subtitle" style="margin-bottom: 16px;">Items requiring action</div>
        <div style="margin-bottom: 8px;">
          <div style="display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 13px;">
            <span style="color: #94a3b8;">Movies</span>
            <span style="color: #ffffff; font-weight: 600;">RADARR_MISSING_PH</span>
          </div>
          <div class="progress-bar-container">
            <div class="progress-bar-fill" style="width: RADARR_PERCENT_PH%; background: #3b82f6;"></div>
          </div>
        </div>
        <div>
          <div style="display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 13px;">
            <span style="color: #94a3b8;">Episodes</span>
            <span style="color: #ffffff; font-weight: 600;">SONARR_MISSING_PH</span>
          </div>
          <div class="progress-bar-container">
            <div class="progress-bar-fill" style="width: SONARR_PERCENT_PH%; background: #8b5cf6;"></div>
          </div>
        </div>
      </div>
      
      <div class="card">
        <div class="card-title">Completion Status</div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;">
          <div>
            <div class="progress-ring-container" style="width: 100px; height: 100px;">
              <svg width="100" height="100">
                <circle cx="50" cy="50" r="42" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="10"/>
                <circle cx="50" cy="50" r="42" fill="none" stroke="#3b82f6" stroke-width="10"
                  stroke-dasharray="263.89" stroke-dashoffset="RADARR_DASH_PH"
                  transform="rotate(-90 50 50)" stroke-linecap="round"/>
              </svg>
              <div class="progress-ring-text" style="font-size: 18px;">RADARR_PERCENT_PH%</div>
            </div>
            <div style="text-align: center; margin-top: 8px; font-size: 12px; color: #94a3b8;">Movies</div>
          </div>
          <div>
            <div class="progress-ring-container" style="width: 100px; height: 100px;">
              <svg width="100" height="100">
                <circle cx="50" cy="50" r="42" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="10"/>
                <circle cx="50" cy="50" r="42" fill="none" stroke="#8b5cf6" stroke-width="10"
                  stroke-dasharray="263.89" stroke-dashoffset="SONARR_DASH_PH"
                  transform="rotate(-90 50 50)" stroke-linecap="round"/>
              </svg>
              <div class="progress-ring-text" style="font-size: 18px;">SONARR_PERCENT_PH%</div>
            </div>
            <div style="text-align: center; margin-top: 8px; font-size: 12px; color: #94a3b8;">Shows</div>
          </div>
        </div>
      </div>
      
    </div>
    
    <!-- ROW 3: Activity -->
    <div class="row-3">
      
      <div class="card">
        <div class="card-title">Currently Watching</div>
        CURRENTLY_WATCHING_CONTENT_PH
      </div>
      
      <div class="card accent-green">
        <div class="card-title">Download Queue</div>
        <div style="margin-bottom: 16px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <div>
              <div style="font-size: 32px; font-weight: 700; color: #10b981;">SABNZBD_SPEED_PH</div>
              <div style="font-size: 13px; color: #64748b;">SABNZBD_ITEMS_PH active downloads</div>
            </div>
          </div>
          <div style="font-size: 12px; color: #94a3b8; margin-top: 8px;">
            Remaining: SABNZBD_SIZE_LEFT_PH • ETA: SABNZBD_TIME_LEFT_PH
          </div>
        </div>
        QUEUE_ITEMS_CONTENT_PH
      </div>
      
      <div class="card">
        <div class="card-title">Recent Additions</div>
        <div class="activity-list">
          RECENT_ADDITIONS_CONTENT_PH
        </div>
      </div>
      
    </div>
    
    <!-- ROW 4: Service Health -->
    <div class="row-1">
      <div class="card">
        <div class="card-title">Service Health</div>
        <div class="service-grid">
          
          <div class="service-card">
            <div class="service-icon">📺</div>
            <div class="service-info">
              <div class="service-name">Sonarr</div>
              <div class="service-rt">SONARR_RT_PH ms</div>
            </div>
            <div class="service-status-dot SERVICE_STATUS_SONARR"></div>
          </div>
          
          <div class="service-card">
            <div class="service-icon">🎬</div>
            <div class="service-info">
              <div class="service-name">Radarr</div>
              <div class="service-rt">RADARR_RT_PH ms</div>
            </div>
            <div class="service-status-dot SERVICE_STATUS_RADARR"></div>
          </div>
          
          <div class="service-card">
            <div class="service-icon">▶️</div>
            <div class="service-info">
              <div class="service-name">Plex</div>
              <div class="service-rt">PLEX_RT_PH ms</div>
            </div>
            <div class="service-status-dot SERVICE_STATUS_PLEX"></div>
          </div>
          
          <div class="service-card">
            <div class="service-icon">📊</div>
            <div class="service-info">
              <div class="service-name">Tautulli</div>
              <div class="service-rt">TAUTULLI_RT_PH ms</div>
            </div>
            <div class="service-status-dot SERVICE_STATUS_TAUTULLI"></div>
          </div>
          
          <div class="service-card">
            <div class="service-icon">⬇️</div>
            <div class="service-info">
              <div class="service-name">SABnzbd</div>
              <div class="service-rt">SABNZBD_RT_PH ms</div>
            </div>
            <div class="service-status-dot SERVICE_STATUS_SAB"></div>
          </div>
          
          <div class="service-card">
            <div class="service-icon">📝</div>
            <div class="service-info">
              <div class="service-name">Overseerr</div>
              <div class="service-rt">OVERSEERR_RT_PH ms</div>
            </div>
            <div class="service-status-dot SERVICE_STATUS_OVERSEERR"></div>
          </div>
          
          <div class="service-card">
            <div class="service-icon">📡</div>
            <div class="service-info">
              <div class="service-name">Prowlarr</div>
              <div class="service-rt">PROWLARR_RT_PH ms</div>
            </div>
            <div class="service-status-dot SERVICE_STATUS_PROWLARR"></div>
          </div>
          
          <div class="service-card">
            <div class="service-icon">💬</div>
            <div class="service-info">
              <div class="service-name">Bazarr</div>
              <div class="service-rt">BAZARR_RT_PH ms</div>
            </div>
            <div class="service-status-dot SERVICE_STATUS_BAZARR"></div>
          </div>
          
        </div>
      </div>
    </div>
    
    <!-- ROW 5: Analytics -->
    <div class="row-3">
      
      <div class="card">
        <div class="card-title">Watch History (Last 30 Days)</div>
        <div style="margin-top: 20px;">
          <svg width="100%" height="120" style="overflow: visible;">
            SPARKLINE_SVG_PH
          </svg>
        </div>
      </div>
      
      <div class="card">
        <div class="card-title">Genre Distribution</div>
        <div style="display: flex; align-items: center; justify-content: center; margin-top: 20px;">
          <svg width="180" height="180">
            DONUT_SVG_PH
          </svg>
        </div>
        <div style="margin-top: 16px; font-size: 12px;">
          GENRE_LEGEND_PH
        </div>
      </div>
      
      <div class="card">
        <div class="card-title">Recently Watched</div>
        <div class="activity-list">
          RECENT_WATCHED_CONTENT_PH
        </div>
      </div>
      
    </div>
    
    <footer>
      ClawARR Suite Dashboard • Auto-generated by dashboard.sh • Media Server
    </footer>
    
  </div>
</body>
</html>
HTML_START

# Generate dynamic content sections

# Currently watching content
if [[ $TAUTULLI_STREAMS -gt 0 ]]; then
  WATCHING_HTML=$(echo "$TAUTULLI_ACTIVITY" | jq -r '
    .response.data.sessions[]? |
    "<div class=\"activity-item\">
      <div class=\"activity-thumb\">▶️</div>
      <div class=\"activity-info\">
        <div class=\"activity-title\">\(.title // "Unknown")</div>
        <div class=\"activity-meta\">\(.user // "Unknown User") • \(.progress_percent // 0)% complete</div>
        <div class=\"progress-bar-container\">
          <div class=\"progress-bar-fill\" style=\"width: \(.progress_percent // 0)%;\"></div>
        </div>
      </div>
    </div>"
  ' | head -5)
  
  if [[ -z "$WATCHING_HTML" || "$WATCHING_HTML" == "null" ]]; then
    CURRENTLY_WATCHING_CONTENT="<div class=\"empty-state\"><div class=\"empty-state-icon\">📺</div>No active streams</div>"
  else
    CURRENTLY_WATCHING_CONTENT="$WATCHING_HTML"
  fi
else
  CURRENTLY_WATCHING_CONTENT="<div class=\"empty-state\"><div class=\"empty-state-icon\">📺</div>No active streams</div>"
fi

# Queue items content
if [[ $SABNZBD_ITEMS -gt 0 ]]; then
  QUEUE_ITEMS_HTML=$(echo "$SABNZBD_QUEUE" | jq -r '
    .queue.slots[]? |
    "<div style=\"margin-bottom: 12px;\">
      <div style=\"display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 12px;\">
        <span style=\"color: #ffffff; font-weight: 500;\">\(.filename // "Unknown")</span>
        <span style=\"color: #10b981; font-weight: 600;\">\(.percentage // 0)%</span>
      </div>
      <div class=\"progress-bar-container\">
        <div class=\"progress-bar-fill\" style=\"width: \(.percentage // 0)%; background: #10b981;\"></div>
      </div>
    </div>"
  ' | head -3)
  QUEUE_ITEMS_CONTENT="$QUEUE_ITEMS_HTML"
else
  QUEUE_ITEMS_CONTENT="<div class=\"empty-state\" style=\"padding: 20px;\"><div class=\"empty-state-icon\" style=\"font-size: 32px;\">✓</div>Queue empty</div>"
fi

# Recent additions content
RECENT_ADDITIONS_HTML=""
if [[ "$RADARR_RECENT" != "[]" ]]; then
  RECENT_ADDITIONS_HTML=$(echo "$RADARR_RECENT" | jq -r '
    .[] |
    "<div class=\"activity-item\">
      <div class=\"activity-thumb\">🎬</div>
      <div class=\"activity-info\">
        <div class=\"activity-title\">\(.title // "Unknown")</div>
        <div class=\"activity-meta\">\(.added[0:10] // "Unknown") • Movie</div>
      </div>
      <div class=\"activity-badge badge-\(
        if .movieFile.quality.quality.resolution >= 2160 then "4k"
        elif .movieFile.quality.quality.resolution == 1080 then "1080p"
        elif .movieFile.quality.quality.resolution == 720 then "720p"
        else "sd" end
      )\">\(
        if .movieFile.quality.quality.resolution >= 2160 then "4K"
        elif .movieFile.quality.quality.resolution == 1080 then "1080p"
        elif .movieFile.quality.quality.resolution == 720 then "720p"
        else "SD" end
      )</div>
    </div>"
  ')
fi

if [[ -z "$RECENT_ADDITIONS_HTML" || "$RECENT_ADDITIONS_HTML" == "null" ]]; then
  RECENT_ADDITIONS_CONTENT="<div class=\"empty-state\">No recent additions</div>"
else
  RECENT_ADDITIONS_CONTENT="$RECENT_ADDITIONS_HTML"
fi

# Recent watched content
RECENT_WATCHED_HTML=$(echo "$TAUTULLI_HISTORY" | jq -r '
  .response.data.data[]? |
  "<div class=\"activity-item\">
    <div class=\"activity-thumb\">\(if .media_type == "movie" then "🎬" else "📺" end)</div>
    <div class=\"activity-info\">
      <div class=\"activity-title\">\(.full_title // .title // "Unknown")</div>
      <div class=\"activity-meta\">\(.date // "Unknown") • \((.duration // 0) / 60 | floor) min</div>
    </div>
  </div>"
' | head -10)

if [[ -z "$RECENT_WATCHED_HTML" || "$RECENT_WATCHED_HTML" == "null" ]]; then
  RECENT_WATCHED_CONTENT="<div class=\"empty-state\">No watch history</div>"
else
  RECENT_WATCHED_CONTENT="$RECENT_WATCHED_HTML"
fi

# Generate sparkline SVG
SPARKLINE_SVG="<path d=\"M 0 80\" fill=\"none\" stroke=\"#3b82f6\" stroke-width=\"2\"/>"
if [[ "$TAUTULLI_PLAYS" != "[]" && "$TAUTULLI_PLAYS" != "null" ]]; then
  # Convert plays data to sparkline path
  PLAYS_COUNT=$(echo "$TAUTULLI_PLAYS" | jq 'length')
  if [[ $PLAYS_COUNT -gt 0 ]]; then
    MAX_PLAYS=$(echo "$TAUTULLI_PLAYS" | jq 'max')
    if [[ $MAX_PLAYS -gt 0 ]]; then
      SPARKLINE_PATH=$(echo "$TAUTULLI_PLAYS" | jq -r --arg max "$MAX_PLAYS" --arg count "$PLAYS_COUNT" '
        to_entries | map(
          "L \(((.key + 1) / ($count | tonumber) * 100))  \(100 - ((.value / ($max | tonumber)) * 80))"
        ) | join(" ")
      ')
      SPARKLINE_SVG="<path d=\"M 0 100 $SPARKLINE_PATH\" fill=\"none\" stroke=\"#3b82f6\" stroke-width=\"3\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/>"
    fi
  fi
fi

# Generate donut chart SVG and legend
DONUT_SVG="<circle cx=\"90\" cy=\"90\" r=\"70\" fill=\"#111827\"/>"
GENRE_LEGEND=""

if [[ -n "$GENRE_DATA" && "$GENRE_DATA" != "null" ]]; then
  # Parse genre data and create donut segments
  IFS=',' read -ra GENRES <<< "$GENRE_DATA"
  TOTAL_GENRE_COUNT=0
  for genre_pair in "${GENRES[@]}"; do
    count=$(echo "$genre_pair" | cut -d':' -f2)
    TOTAL_GENRE_COUNT=$((TOTAL_GENRE_COUNT + count))
  done
  
  if [[ $TOTAL_GENRE_COUNT -gt 0 ]]; then
    COLORS=("#3b82f6" "#8b5cf6" "#10b981" "#f59e0b" "#ef4444")
    OFFSET=0
    INDEX=0
    
    for genre_pair in "${GENRES[@]}"; do
      genre_name=$(echo "$genre_pair" | cut -d':' -f1)
      count=$(echo "$genre_pair" | cut -d':' -f2)
      percent=$(echo "scale=1; ($count * 100) / $TOTAL_GENRE_COUNT" | bc)
      dasharray=$(echo "scale=2; (($count * 439.82) / $TOTAL_GENRE_COUNT)" | bc)
      color="${COLORS[$INDEX]}"
      
      DONUT_SVG="$DONUT_SVG
        <circle cx=\"90\" cy=\"90\" r=\"70\" fill=\"none\" stroke=\"$color\" stroke-width=\"28\"
          stroke-dasharray=\"$dasharray 439.82\" stroke-dashoffset=\"-$OFFSET\"
          transform=\"rotate(-90 90 90)\"/>"
      
      GENRE_LEGEND="$GENRE_LEGEND
        <div class=\"legend-item\">
          <div class=\"legend-color\" style=\"background: $color;\"></div>
          <div class=\"legend-label\">$genre_name</div>
          <div class=\"legend-value\">$percent%</div>
        </div>"
      
      OFFSET=$(echo "scale=2; $OFFSET + $dasharray" | bc)
      INDEX=$((INDEX + 1))
    done
    
    DONUT_SVG="$DONUT_SVG<circle cx=\"90\" cy=\"90\" r=\"50\" fill=\"#111827\"/>"
  fi
fi

if [[ -z "$GENRE_LEGEND" ]]; then
  GENRE_LEGEND="<div style=\"text-align: center; color: #64748b;\">No genre data available</div>"
fi

# Calculate service status classes
status_class() {
  local rt=$1
  if [[ "$rt" == "N/A" ]]; then
    echo "offline"
  elif [[ $rt -gt 500 ]]; then
    echo "slow"
  else
    echo ""
  fi
}

SERVICE_STATUS_SONARR=$(status_class "$SONARR_RT")
SERVICE_STATUS_RADARR=$(status_class "$RADARR_RT")
SERVICE_STATUS_PLEX=$(status_class "$PLEX_RT")
SERVICE_STATUS_TAUTULLI=$(status_class "$TAUTULLI_RT")
SERVICE_STATUS_SAB=$(status_class "$SABNZBD_RT")
SERVICE_STATUS_OVERSEERR=$(status_class "$OVERSEERR_RT")
SERVICE_STATUS_PROWLARR=$(status_class "$PROWLARR_RT")
SERVICE_STATUS_BAZARR=$(status_class "$BAZARR_RT")

# Calculate quality percentages
TOTAL_ITEMS=$((QUAL_4K + QUAL_1080P + QUAL_720P + QUAL_SD))
if [[ $TOTAL_ITEMS -gt 0 ]]; then
  QUAL_4K_PERCENT=$(echo "scale=1; ($QUAL_4K * 100) / $TOTAL_ITEMS" | bc)
  QUAL_1080P_PERCENT=$(echo "scale=1; ($QUAL_1080P * 100) / $TOTAL_ITEMS" | bc)
  QUAL_720P_PERCENT=$(echo "scale=1; ($QUAL_720P * 100) / $TOTAL_ITEMS" | bc)
  QUAL_SD_PERCENT=$(echo "scale=1; ($QUAL_SD * 100) / $TOTAL_ITEMS" | bc)
else
  QUAL_4K_PERCENT=0 QUAL_1080P_PERCENT=0 QUAL_720P_PERCENT=0 QUAL_SD_PERCENT=0
fi

# Calculate SVG circle dash offsets for progress rings
# Formula: circumference = 2 * π * r, dashoffset = circumference * (1 - percent/100)
STORAGE_CIRCUMFERENCE=376.99
STORAGE_DASH=$(echo "scale=2; $STORAGE_CIRCUMFERENCE * (1 - $STORAGE_PERCENT / 100)" | bc)

RADARR_CIRCUMFERENCE=263.89
RADARR_DASH=$(echo "scale=2; $RADARR_CIRCUMFERENCE * (1 - $RADARR_PERCENT / 100)" | bc)
SONARR_DASH=$(echo "scale=2; $RADARR_CIRCUMFERENCE * (1 - $SONARR_PERCENT / 100)" | bc)

SONARR_MISSING=$((SONARR_EPISODES - SONARR_EPISODE_FILES))

# Replace all placeholders in HTML
sed -i.bak \
  -e "s|TIMESTAMP_PH|$TIMESTAMP|g" \
  -e "s|RADARR_TOTAL_PH|$RADARR_TOTAL|g" \
  -e "s|RADARR_MONITORED_PH|$RADARR_MONITORED|g" \
  -e "s|RADARR_MISSING_PH|$RADARR_MISSING|g" \
  -e "s|RADARR_PERCENT_PH|$RADARR_PERCENT|g" \
  -e "s|RADARR_DASH_PH|$RADARR_DASH|g" \
  -e "s|SONARR_TOTAL_PH|$SONARR_TOTAL|g" \
  -e "s|SONARR_MONITORED_PH|$SONARR_MONITORED|g" \
  -e "s|SONARR_EPISODES_PH|$SONARR_EPISODES|g" \
  -e "s|SONARR_EPISODE_FILES_PH|$SONARR_EPISODE_FILES|g" \
  -e "s|SONARR_MISSING_PH|$SONARR_MISSING|g" \
  -e "s|SONARR_PERCENT_PH|$SONARR_PERCENT|g" \
  -e "s|SONARR_DASH_PH|$SONARR_DASH|g" \
  -e "s|TOTAL_STORAGE_TB_PH|$TOTAL_STORAGE_TB|g" \
  -e "s|TOTAL_USED_TB_PH|$TOTAL_USED_TB|g" \
  -e "s|STORAGE_PERCENT_PH|$STORAGE_PERCENT|g" \
  -e "s|STORAGE_DASH_PH|$STORAGE_DASH|g" \
  -e "s|TAUTULLI_STREAMS_PH|$TAUTULLI_STREAMS|g" \
  -e "s|TOTAL_MISSING_PH|$TOTAL_MISSING|g" \
  -e "s|QUAL_4K_PH|$QUAL_4K|g" \
  -e "s|QUAL_1080P_PH|$QUAL_1080P|g" \
  -e "s|QUAL_720P_PH|$QUAL_720P|g" \
  -e "s|QUAL_SD_PH|$QUAL_SD|g" \
  -e "s|QUAL_4K_PERCENT_PH|$QUAL_4K_PERCENT|g" \
  -e "s|QUAL_1080P_PERCENT_PH|$QUAL_1080P_PERCENT|g" \
  -e "s|QUAL_720P_PERCENT_PH|$QUAL_720P_PERCENT|g" \
  -e "s|QUAL_SD_PERCENT_PH|$QUAL_SD_PERCENT|g" \
  -e "s|QUAL_4K_PERCENT_DISPLAY_PH|$QUAL_4K_PERCENT|g" \
  -e "s|QUAL_1080P_PERCENT_DISPLAY_PH|$QUAL_1080P_PERCENT|g" \
  -e "s|QUAL_720P_PERCENT_DISPLAY_PH|$QUAL_720P_PERCENT|g" \
  -e "s|QUAL_SD_PERCENT_DISPLAY_PH|$QUAL_SD_PERCENT|g" \
  -e "s|SABNZBD_SPEED_PH|$SABNZBD_SPEED|g" \
  -e "s|SABNZBD_SIZE_LEFT_PH|$SABNZBD_SIZE_LEFT|g" \
  -e "s|SABNZBD_TIME_LEFT_PH|$SABNZBD_TIME_LEFT|g" \
  -e "s|SABNZBD_ITEMS_PH|$SABNZBD_ITEMS|g" \
  -e "s|SONARR_RT_PH|$SONARR_RT|g" \
  -e "s|RADARR_RT_PH|$RADARR_RT|g" \
  -e "s|PLEX_RT_PH|$PLEX_RT|g" \
  -e "s|TAUTULLI_RT_PH|$TAUTULLI_RT|g" \
  -e "s|SABNZBD_RT_PH|$SABNZBD_RT|g" \
  -e "s|OVERSEERR_RT_PH|$OVERSEERR_RT|g" \
  -e "s|PROWLARR_RT_PH|$PROWLARR_RT|g" \
  -e "s|BAZARR_RT_PH|$BAZARR_RT|g" \
  -e "s|SERVICE_STATUS_SONARR|$SERVICE_STATUS_SONARR|g" \
  -e "s|SERVICE_STATUS_RADARR|$SERVICE_STATUS_RADARR|g" \
  -e "s|SERVICE_STATUS_PLEX|$SERVICE_STATUS_PLEX|g" \
  -e "s|SERVICE_STATUS_TAUTULLI|$SERVICE_STATUS_TAUTULLI|g" \
  -e "s|SERVICE_STATUS_SAB|$SERVICE_STATUS_SAB|g" \
  -e "s|SERVICE_STATUS_OVERSEERR|$SERVICE_STATUS_OVERSEERR|g" \
  -e "s|SERVICE_STATUS_PROWLARR|$SERVICE_STATUS_PROWLARR|g" \
  -e "s|SERVICE_STATUS_BAZARR|$SERVICE_STATUS_BAZARR|g" \
  "$OUTPUT_FILE"

# Replace multi-line content sections (need to use perl or a different approach for multi-line)
# Using temporary files for multi-line replacements
echo "$CURRENTLY_WATCHING_CONTENT" > /tmp/watching.html
echo "$QUEUE_ITEMS_CONTENT" > /tmp/queue.html
echo "$RECENT_ADDITIONS_CONTENT" > /tmp/recent.html
echo "$RECENT_WATCHED_CONTENT" > /tmp/watched.html
echo "$SPARKLINE_SVG" > /tmp/sparkline.svg
echo "$DONUT_SVG" > /tmp/donut.svg
echo "$GENRE_LEGEND" > /tmp/genres.html

# Use awk for multi-line replacement
awk '
  /CURRENTLY_WATCHING_CONTENT_PH/ {
    system("cat /tmp/watching.html")
    next
  }
  /QUEUE_ITEMS_CONTENT_PH/ {
    system("cat /tmp/queue.html")
    next
  }
  /RECENT_ADDITIONS_CONTENT_PH/ {
    system("cat /tmp/recent.html")
    next
  }
  /RECENT_WATCHED_CONTENT_PH/ {
    system("cat /tmp/watched.html")
    next
  }
  /SPARKLINE_SVG_PH/ {
    system("cat /tmp/sparkline.svg")
    next
  }
  /DONUT_SVG_PH/ {
    system("cat /tmp/donut.svg")
    next
  }
  /GENRE_LEGEND_PH/ {
    system("cat /tmp/genres.html")
    next
  }
  { print }
' "$OUTPUT_FILE" > "$OUTPUT_FILE.tmp" && mv "$OUTPUT_FILE.tmp" "$OUTPUT_FILE"

# Cleanup
rm -f "${OUTPUT_FILE}.bak" /tmp/watching.html /tmp/queue.html /tmp/recent.html /tmp/watched.html /tmp/sparkline.svg /tmp/donut.svg /tmp/genres.html

echo ""
echo "✅ Premium dashboard generated: $OUTPUT_FILE"
echo "   Optimized for 2560x1440 (1440p)"
echo "   Open in browser: file://$(pwd)/$OUTPUT_FILE"
echo ""
