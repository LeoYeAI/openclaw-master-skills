#!/usr/bin/env bash
# unpackerr.sh - Unpackerr archive extraction monitoring
# Usage: unpackerr.sh <command> [args...]
# Requires: Docker access to unpackerr container or SSH

set -euo pipefail

DOCKER_HOST_SSH="${UNPACKERR_SSH:-}"
DOCKER_CMD="${UNPACKERR_DOCKER_CMD:-docker}"
CONTAINER="${UNPACKERR_CONTAINER:-unpackerr}"

docker_exec() {
  if [[ -n "$DOCKER_HOST_SSH" ]]; then
    ssh "$DOCKER_HOST_SSH" "${DOCKER_CMD} $*" 2>&1
  else
    ${DOCKER_CMD} "$@" 2>&1
  fi
}

cmd_status() {
  echo "📦 Unpackerr Status"
  echo ""

  local state
  state=$(docker_exec inspect --format '{{.State.Status}}' "$CONTAINER" 2>/dev/null || echo "not_found")

  if [[ "$state" == "not_found" ]]; then
    echo "  ❌ Container '${CONTAINER}' not found"
    return
  fi

  echo "  Container: ${CONTAINER} (${state})"
  local uptime
  uptime=$(docker_exec inspect --format '{{.State.StartedAt}}' "$CONTAINER" 2>/dev/null)
  echo "  Started: ${uptime}"

  # Check configured services from env
  local env_vars
  env_vars=$(docker_exec inspect --format '{{range .Config.Env}}{{println .}}{{end}}' "$CONTAINER" 2>/dev/null)

  echo ""
  echo "  Configured services:"
  echo "$env_vars" | grep -E "^UN_(SONARR|RADARR|LIDARR|READARR)" | while read -r line; do
    local key val
    key=$(echo "$line" | cut -d= -f1)
    val=$(echo "$line" | cut -d= -f2-)
    # Don't print API keys
    if echo "$key" | grep -q "API_KEY"; then
      echo "    ${key}=****"
    else
      echo "    ${key}=${val}"
    fi
  done

  # Recent extraction activity
  echo ""
  echo "  Recent activity:"
  docker_exec logs --tail 10 "$CONTAINER" 2>&1 | grep -iE "extract|unpack|complete|error|queue" | tail -5 | while read -r line; do
    echo "    ${line}"
  done
}

cmd_activity() {
  echo "📦 Unpackerr Extraction Activity"
  echo ""
  docker_exec logs --tail 50 "$CONTAINER" 2>&1 | grep -iE "extract|unpack|complete|import|queue|waiting" | tail -20
}

cmd_errors() {
  echo "❌ Unpackerr Errors"
  echo ""
  local errors
  errors=$(docker_exec logs --tail 200 "$CONTAINER" 2>&1 | grep -iE "error|fail|warn" | tail -20)
  if [[ -z "$errors" ]]; then
    echo "  No recent errors"
  else
    echo "$errors"
  fi
}

cmd_logs() {
  local count="${1:-50}"
  echo "📋 Unpackerr Logs (last ${count} lines)"
  echo ""
  docker_exec logs --tail "$count" "$CONTAINER" 2>&1
}

cmd_config() {
  echo "⚙️ Unpackerr Configuration"
  echo ""
  echo "  Unpackerr is configured via environment variables."
  echo "  Current config:"
  echo ""
  local env_vars
  env_vars=$(docker_exec inspect --format '{{range .Config.Env}}{{println .}}{{end}}' "$CONTAINER" 2>/dev/null)
  echo "$env_vars" | grep "^UN_" | while read -r line; do
    local key val
    key=$(echo "$line" | cut -d= -f1)
    val=$(echo "$line" | cut -d= -f2-)
    if echo "$key" | grep -q "API_KEY\|PASSWORD\|SECRET"; then
      echo "  ${key}=****"
    else
      echo "  ${key}=${val}"
    fi
  done
}

cmd_restart() {
  echo "🔄 Restarting Unpackerr..."
  docker_exec restart "$CONTAINER" 2>&1
  echo "✅ Restarted"
}

usage() {
  cat <<EOF
Usage: unpackerr.sh <command> [args...]

Commands:
  status                Check Unpackerr status & config
  activity              Recent extraction activity
  errors                Recent errors/warnings
  config                Show configuration (env vars)
  logs [count]          View recent logs
  restart               Restart container

Environment:
  UNPACKERR_SSH         SSH host for remote Docker
  UNPACKERR_DOCKER_CMD  Docker command (default: docker)
  UNPACKERR_CONTAINER   Container name (default: unpackerr)

Unpackerr auto-extracts archives from download clients for *arr apps.
No manual intervention needed — it monitors Sonarr/Radarr queues.
EOF
}

case "${1:-}" in
  status) cmd_status ;;
  activity) cmd_activity ;;
  errors) cmd_errors ;;
  config) cmd_config ;;
  logs) shift; cmd_logs "${1:-50}" ;;
  restart) cmd_restart ;;
  *) usage ;;
esac
