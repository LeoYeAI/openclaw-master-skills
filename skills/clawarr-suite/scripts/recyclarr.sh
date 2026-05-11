#!/usr/bin/env bash
# recyclarr.sh - Recyclarr quality profile management (TRaSH Guides sync)
# Usage: recyclarr.sh <command> [args...]
# Requires: SSH access to Docker host or local recyclarr install

set -euo pipefail

HOST="${CLAWARR_HOST:-}"
DOCKER_HOST_SSH="${RECYCLARR_SSH:-}"
DOCKER_CMD="${RECYCLARR_DOCKER_CMD:-docker}"
CONTAINER="${RECYCLARR_CONTAINER:-recyclarr}"

run_recyclarr() {
  if [[ -n "$DOCKER_HOST_SSH" ]]; then
    ssh "$DOCKER_HOST_SSH" "${DOCKER_CMD} exec ${CONTAINER} recyclarr $*" 2>&1
  elif command -v recyclarr &>/dev/null; then
    recyclarr "$@" 2>&1
  else
    ${DOCKER_CMD} exec "${CONTAINER}" recyclarr "$@" 2>&1
  fi
}

docker_exec() {
  if [[ -n "$DOCKER_HOST_SSH" ]]; then
    ssh "$DOCKER_HOST_SSH" "${DOCKER_CMD} $*" 2>&1
  else
    ${DOCKER_CMD} "$@" 2>&1
  fi
}

cmd_status() {
  echo "🔄 Recyclarr Status"
  echo ""

  # Check if container exists and is running
  local state
  state=$(docker_exec inspect --format '{{.State.Status}}' "$CONTAINER" 2>/dev/null || echo "not_found")

  if [[ "$state" == "not_found" ]]; then
    echo "  ❌ Container '${CONTAINER}' not found"
    echo "  Install: docker pull ghcr.io/recyclarr/recyclarr:latest"
    return
  fi

  echo "  Container: ${CONTAINER} (${state})"

  # Check config
  local config_check
  if config_check=$(run_recyclarr config list 2>&1); then
    echo "  Config: ✅ Valid"
    echo "$config_check" | while read -r line; do
      echo "    ${line}"
    done
  else
    echo "  Config: ⚠️  Not configured or invalid"
  fi
}

cmd_sync() {
  local target="${1:-}"
  echo "🔄 Running Recyclarr Sync..."
  echo ""
  if [[ -n "$target" ]]; then
    echo "Target: ${target}"
    run_recyclarr sync "${target}"
  else
    echo "Syncing all configured instances..."
    run_recyclarr sync
  fi
}

cmd_list_profiles() {
  echo "📋 TRaSH Guide Quality Profiles"
  echo ""
  echo "Radarr profiles:"
  run_recyclarr list custom-formats radarr 2>/dev/null | head -30
  echo ""
  echo "Sonarr profiles:"
  run_recyclarr list custom-formats sonarr 2>/dev/null | head -30
}

cmd_list_qualities() {
  local app="${1:-radarr}"
  echo "📋 Quality Definitions for ${app}"
  echo ""
  run_recyclarr list qualities "${app}" 2>/dev/null
}

cmd_config() {
  echo "📝 Recyclarr Configuration"
  echo ""
  if [[ -n "$DOCKER_HOST_SSH" ]]; then
    ssh "$DOCKER_HOST_SSH" "cat ${DOCKER_CONFIG_BASE:-/volume1/docker}/recyclarr/recyclarr.yml 2>/dev/null || echo 'No config found'"
  else
    docker_exec exec "$CONTAINER" cat /config/recyclarr.yml 2>/dev/null || echo "No config found"
  fi
}

cmd_logs() {
  local count="${1:-50}"
  echo "📋 Recyclarr Logs (last ${count} lines)"
  echo ""
  docker_exec logs --tail "$count" "$CONTAINER" 2>&1
}

cmd_create_config() {
  echo "🔧 Creating Recyclarr Config Template"
  echo ""
  run_recyclarr config create 2>&1
  echo ""
  echo "✅ Config template created. Edit it with your Sonarr/Radarr details."
}

cmd_diff() {
  local target="${1:-}"
  echo "🔍 Preview changes (dry run)..."
  echo ""
  if [[ -n "$target" ]]; then
    run_recyclarr sync --preview "${target}" 2>&1
  else
    run_recyclarr sync --preview 2>&1
  fi
}

usage() {
  cat <<EOF
Usage: recyclarr.sh <command> [args...]

Commands:
  status                Check Recyclarr status & config
  sync [instance]       Sync TRaSH Guides profiles (all or specific)
  diff [instance]       Preview changes without applying
  profiles              List available TRaSH quality profiles
  qualities [app]       List quality definitions (radarr|sonarr)
  config                Show current configuration
  create-config         Generate config template
  logs [count]          View recent logs

Environment:
  RECYCLARR_SSH         SSH host for remote Docker (e.g., mynas)
  RECYCLARR_DOCKER_CMD  Docker command (default: docker)
  RECYCLARR_CONTAINER   Container name (default: recyclarr)

Examples:
  recyclarr.sh sync                    # Sync all
  recyclarr.sh diff                    # Preview changes
  recyclarr.sh profiles                # Browse available profiles
EOF
}

case "${1:-}" in
  status) cmd_status ;;
  sync) shift; cmd_sync "${1:-}" ;;
  diff) shift; cmd_diff "${1:-}" ;;
  profiles) cmd_list_profiles ;;
  qualities) shift; cmd_list_qualities "${1:-radarr}" ;;
  config) cmd_config ;;
  create-config) cmd_create_config ;;
  logs) shift; cmd_logs "${1:-50}" ;;
  *) usage ;;
esac
