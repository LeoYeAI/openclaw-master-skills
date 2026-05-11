#!/usr/bin/env bash
# kometa.sh - Kometa (Plex Meta Manager) collection & overlay management
# Usage: kometa.sh <command> [args...]
# Requires: Docker access to kometa container or SSH

set -euo pipefail

DOCKER_HOST_SSH="${KOMETA_SSH:-}"
DOCKER_CMD="${KOMETA_DOCKER_CMD:-docker}"
CONTAINER="${KOMETA_CONTAINER:-kometa}"
HOST="${CLAWARR_HOST:-}"
PLEX_TOKEN="${PLEX_TOKEN:-}"

docker_exec() {
  if [[ -n "$DOCKER_HOST_SSH" ]]; then
    ssh "$DOCKER_HOST_SSH" "${DOCKER_CMD} $*" 2>&1
  else
    ${DOCKER_CMD} "$@" 2>&1
  fi
}

run_kometa() {
  if [[ -n "$DOCKER_HOST_SSH" ]]; then
    ssh "$DOCKER_HOST_SSH" "${DOCKER_CMD} exec ${CONTAINER} python kometa.py $*" 2>&1
  else
    ${DOCKER_CMD} exec "${CONTAINER}" python kometa.py "$@" 2>&1
  fi
}

cmd_status() {
  echo "🎨 Kometa Status"
  echo ""

  local state
  state=$(docker_exec inspect --format '{{.State.Status}}' "$CONTAINER" 2>/dev/null || echo "not_found")

  if [[ "$state" == "not_found" ]]; then
    echo "  ❌ Container '${CONTAINER}' not found"
    return
  fi

  echo "  Container: ${CONTAINER} (${state})"

  # Check last run
  local logs
  logs=$(docker_exec logs --tail 30 "$CONTAINER" 2>&1)
  local last_run
  last_run=$(echo "$logs" | grep -i "finished\|complete\|run start" | tail -1)
  if [[ -n "$last_run" ]]; then
    echo "  Last activity: ${last_run}"
  fi

  # Check config exists
  if [[ -n "$DOCKER_HOST_SSH" ]]; then
    local config_exists
    config_exists=$(ssh "$DOCKER_HOST_SSH" "test -f ${DOCKER_CONFIG_BASE:-/volume1/docker}/kometa/config.yml && echo yes || echo no" 2>/dev/null)
    echo "  Config: $([ "$config_exists" = "yes" ] && echo "✅ Found" || echo "❌ Missing")"
  fi
}

cmd_run() {
  local library="${1:-}"
  echo "🎨 Running Kometa..."
  echo ""
  if [[ -n "$library" ]]; then
    echo "Library: ${library}"
    docker_exec run --rm \
      -v ${DOCKER_CONFIG_BASE:-/volume1/docker}/kometa:/config \
      kometateam/kometa:latest \
      --run --run-libraries "${library}" 2>&1 | tail -20
  else
    echo "Running all libraries..."
    docker_exec run --rm \
      -v ${DOCKER_CONFIG_BASE:-/volume1/docker}/kometa:/config \
      kometateam/kometa:latest \
      --run 2>&1 | tail -40
  fi
}

cmd_collections() {
  echo "📚 Kometa Collections"
  echo ""
  if [[ -z "$HOST" || -z "$PLEX_TOKEN" ]]; then
    echo "  Need CLAWARR_HOST and PLEX_TOKEN to query Plex collections"
    return
  fi

  # Query Plex for collections
  local sections
  sections=$(curl -sf -H "X-Plex-Token: ${PLEX_TOKEN}" \
    "http://${HOST}:32400/library/sections" 2>/dev/null)

  echo "$sections" | jq -r '.MediaContainer.Directory[] | "\(.key) \(.title)"' 2>/dev/null | while read -r key title; do
    echo "  📁 ${title}:"
    local cols
    cols=$(curl -sf -H "X-Plex-Token: ${PLEX_TOKEN}" \
      "http://${HOST}:32400/library/sections/${key}/collections" 2>/dev/null)
    local count
    count=$(echo "$cols" | jq '.MediaContainer.size // 0' 2>/dev/null)
    if [[ "$count" != "0" && "$count" != "null" ]]; then
      echo "$cols" | jq -r '.MediaContainer.Metadata[:15][] | "    - \(.title) (\(.childCount // 0) items)"' 2>/dev/null
      if [[ $(echo "$cols" | jq '.MediaContainer.size' 2>/dev/null) -gt 15 ]]; then
        echo "    ... and more"
      fi
    else
      echo "    (no collections)"
    fi
    echo ""
  done
}

cmd_overlays() {
  echo "🏷️ Overlay Status"
  echo ""
  echo "  Overlays are applied during Kometa runs."
  echo "  Check config for enabled overlays:"
  echo ""
  cmd_config | grep -A 3 "overlay" || echo "  No overlay config found"
}

cmd_config() {
  echo "⚙️ Kometa Configuration"
  echo ""
  if [[ -n "$DOCKER_HOST_SSH" ]]; then
    ssh "$DOCKER_HOST_SSH" "cat ${DOCKER_CONFIG_BASE:-/volume1/docker}/kometa/config.yml 2>/dev/null" || echo "  No config found"
  else
    docker_exec exec "$CONTAINER" cat /config/config.yml 2>/dev/null || echo "  No config found"
  fi
}

cmd_logs() {
  local count="${1:-50}"
  echo "📋 Kometa Logs (last ${count} lines)"
  echo ""
  docker_exec logs --tail "$count" "$CONTAINER" 2>&1
}

cmd_templates() {
  echo "📝 Available Kometa Default Collections"
  echo ""
  echo "  Collection Files:"
  echo "    - basic: Basic genre collections"
  echo "    - imdb: IMDb Top 250, Popular, etc."
  echo "    - tmdb: TMDb Popular, Top Rated, Trending"
  echo "    - trakt: Trakt Trending, Popular, Anticipated"
  echo "    - flixpatrol: Streaming platform top 10s"
  echo "    - anidb: Anime collections"
  echo "    - myanimelist: MAL top anime"
  echo "    - oscars: Academy Award collections"
  echo "    - golden: Golden Globe collections"
  echo "    - spirit: Spirit Award collections"
  echo "    - separator: Visual separators between collection groups"
  echo ""
  echo "  Overlay Files:"
  echo "    - resolution: 4K/1080p/720p badges"
  echo "    - audio_codec: Atmos/DTS-X/TrueHD badges"
  echo "    - video_format: HDR/DV badges"
  echo "    - streaming: Netflix/Disney+/etc logos"
  echo "    - ratings: IMDb/TMDb/RT ratings overlay"
  echo "    - ribbon: Award ribbons"
  echo "    - status: Returning/Ended/Canceled for shows"
  echo ""
  echo "  Add to config.yml under library > collection_files/overlay_files:"
  echo "    collection_files:"
  echo "      - default: imdb"
  echo "      - default: tmdb"
  echo "    overlay_files:"
  echo "      - default: resolution"
}

usage() {
  cat <<EOF
Usage: kometa.sh <command> [args...]

Commands:
  status                Check Kometa container status
  run [library]         Run Kometa (all libraries or specific)
  collections           Show Plex collections (created by Kometa)
  overlays              Check overlay configuration
  config                Show Kometa config
  templates             List available default collections/overlays
  logs [count]          View recent logs

Environment:
  KOMETA_SSH            SSH host for remote Docker
  KOMETA_DOCKER_CMD     Docker command (default: docker)
  KOMETA_CONTAINER      Container name (default: kometa)
  CLAWARR_HOST          Host IP (for Plex queries)
  PLEX_TOKEN            Plex auth token
EOF
}

case "${1:-}" in
  status) cmd_status ;;
  run) shift; cmd_run "${1:-}" ;;
  collections) cmd_collections ;;
  overlays) cmd_overlays ;;
  config) cmd_config ;;
  templates) cmd_templates ;;
  logs) shift; cmd_logs "${1:-50}" ;;
  *) usage ;;
esac
