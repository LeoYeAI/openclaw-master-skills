#!/usr/bin/env bash
# diagnose.sh - Check for common *arr stack issues
# Usage: diagnose.sh

set -euo pipefail

HOST="${CLAWARR_HOST:-}"
SONARR_KEY="${SONARR_KEY:-}"
RADARR_KEY="${RADARR_KEY:-}"

if [[ -z "$HOST" ]]; then
  echo "Error: CLAWARR_HOST not set"
  echo ""
  echo "Usage:"
  echo "  export CLAWARR_HOST=192.168.1.100"
  echo "  export SONARR_KEY=abc123..."
  echo "  export RADARR_KEY=def456..."
  echo "  $0"
  exit 1
fi

if ! command -v jq &> /dev/null; then
  echo "❌ Error: jq is required but not installed"
  exit 1
fi

echo "🔍 Running diagnostics for $HOST..."
echo ""

# Check if Docker is available AND host is local (Docker checks only make sense locally)
HAS_DOCKER=false
IS_LOCAL=false
if [[ "$HOST" == "localhost" || "$HOST" == "127.0.0.1" || "$HOST" == "$(hostname)" || "$HOST" == "$(hostname -s 2>/dev/null)" ]]; then
  IS_LOCAL=true
fi
if command -v docker &> /dev/null && [[ "$IS_LOCAL" == true ]]; then
  HAS_DOCKER=true
fi

# 1. Docker container health (only when stack is on this machine)
if [[ "$HAS_DOCKER" == true ]]; then
  echo "=== Docker Container Status ==="
  
  # Get host uptime (skip gracefully if unavailable)
  HOST_UPTIME_SECONDS=0
  if [[ "$(uname)" == "Darwin" ]]; then
    BOOT_TIME=$(/usr/sbin/sysctl -n kern.boottime 2>/dev/null | awk '{print $4}' | tr -d ',' || echo "0")
    if [[ "$BOOT_TIME" != "0" && -n "$BOOT_TIME" ]]; then
      HOST_UPTIME_SECONDS=$(($(date +%s) - BOOT_TIME))
    fi
  else
    HOST_UPTIME_SECONDS=$(awk '{print int($1)}' /proc/uptime 2>/dev/null || echo "0")
  fi
  
  HOST_UPTIME_HOURS=$((HOST_UPTIME_SECONDS / 3600))
  
  echo "  Host uptime: ${HOST_UPTIME_HOURS}h"
  echo ""
  
  # Check common container names
  for container in radarr sonarr lidarr readarr prowlarr bazarr overseerr plex; do
    if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^${container}\$"; then
      UPTIME=$(docker inspect -f '{{.State.StartedAt}}' "$container" 2>/dev/null || echo "")
      if [[ -n "$UPTIME" ]]; then
        STARTED_TS=$(date -j -f "%Y-%m-%dT%H:%M:%S" "${UPTIME:0:19}" +%s 2>/dev/null || echo "0")
        NOW_TS=$(date +%s)
        CONTAINER_UPTIME_HOURS=$(( (NOW_TS - STARTED_TS) / 3600 ))
        
        if [[ $CONTAINER_UPTIME_HOURS -lt $((HOST_UPTIME_HOURS - 1)) ]]; then
          echo "  ⚠️  $container - Uptime: ${CONTAINER_UPTIME_HOURS}h (may have stale mounts)"
        else
          echo "  ✅ $container - Uptime: ${CONTAINER_UPTIME_HOURS}h"
        fi
      fi
    fi
  done
  echo ""
else
  echo "=== Docker Status ==="
  echo "  ℹ️  Docker not available (skip container checks)"
  echo ""
fi

# 2. Queue warnings
echo "=== Queue Warnings ==="

check_queue_warnings() {
  local service=$1
  local port=$2
  local api_key=$3
  
  if [[ -z "$api_key" ]]; then
    return
  fi
  
  queue=$(curl -sf -H "X-Api-Key: ${api_key}" "http://${HOST}:${port}/api/v3/queue" 2>/dev/null || echo '{"records":[]}')
  
  warnings=$(echo "$queue" | jq -r '.records[] | select(.status == "warning" or .status == "failed") | "  ⚠️  \(.title): \(.statusMessages[0].messages[0] // .status)"' 2>/dev/null)
  
  if [[ -n "$warnings" ]]; then
    echo "$warnings"
  fi
}

if [[ -n "$RADARR_KEY" ]]; then
  echo "Radarr:"
  check_queue_warnings "Radarr" 7878 "$RADARR_KEY"
fi

if [[ -n "$SONARR_KEY" ]]; then
  echo "Sonarr:"
  check_queue_warnings "Sonarr" 8989 "$SONARR_KEY"
fi

if [[ -z "$RADARR_KEY" && -z "$SONARR_KEY" ]]; then
  echo "  (no API keys configured)"
fi

echo ""

# 3. Recent import failures
echo "=== Recent Import Failures ==="

check_failed_imports() {
  local service=$1
  local port=$2
  local api_key=$3
  
  if [[ -z "$api_key" ]]; then
    return
  fi
  
  history=$(curl -sf -H "X-Api-Key: ${api_key}" \
    "http://${HOST}:${port}/api/v3/history?pageSize=20&eventType=3" 2>/dev/null || echo '{"records":[]}')
  
  failures=$(echo "$history" | jq -r '.records[] | select(.eventType == "downloadFailed") | "  ❌ \(.sourceTitle): \(.data.message // "Unknown error")"' 2>/dev/null | head -5)
  
  if [[ -n "$failures" ]]; then
    echo "$failures"
  else
    echo "  ✅ No recent failures"
  fi
}

if [[ -n "$RADARR_KEY" ]]; then
  echo "Radarr:"
  check_failed_imports "Radarr" 7878 "$RADARR_KEY"
  echo ""
fi

if [[ -n "$SONARR_KEY" ]]; then
  echo "Sonarr:"
  check_failed_imports "Sonarr" 8989 "$SONARR_KEY"
  echo ""
fi

# 4. Disk space (if we can detect volumes)
echo "=== Disk Space ==="

# Try to get root folders from Radarr/Sonarr
if [[ -n "$RADARR_KEY" ]]; then
  folders=$(curl -sf -H "X-Api-Key: ${RADARR_KEY}" "http://${HOST}:7878/api/v3/rootfolder" 2>/dev/null || echo '[]')
  
  echo "$folders" | jq -r '.[] | "  Radarr: \(.path) - \(.freeSpace / 1024 / 1024 / 1024 | floor)GB free"' 2>/dev/null
fi

if [[ -n "$SONARR_KEY" ]]; then
  folders=$(curl -sf -H "X-Api-Key: ${SONARR_KEY}" "http://${HOST}:8989/api/v3/rootfolder" 2>/dev/null || echo '[]')
  
  echo "$folders" | jq -r '.[] | "  Sonarr: \(.path) - \(.freeSpace / 1024 / 1024 / 1024 | floor)GB free"' 2>/dev/null
fi

echo ""

# 5. Common issue recommendations
echo "=== Recommendations ==="

if [[ "$HAS_DOCKER" == true ]]; then
  # Check for stale mounts
  for container in radarr sonarr; do
    if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^${container}\$"; then
      UPTIME=$(docker inspect -f '{{.State.StartedAt}}' "$container" 2>/dev/null || echo "")
      if [[ -n "$UPTIME" ]]; then
        STARTED_TS=$(date -j -f "%Y-%m-%dT%H:%M:%S" "${UPTIME:0:19}" +%s 2>/dev/null || echo "0")
        NOW_TS=$(date +%s)
        CONTAINER_UPTIME_HOURS=$(( (NOW_TS - STARTED_TS) / 3600 ))
        
        if [[ $CONTAINER_UPTIME_HOURS -lt $((HOST_UPTIME_HOURS - 1)) ]]; then
          echo "  💡 Container $container has lower uptime than host - consider restart:"
          echo "     docker restart $container"
        fi
      fi
    fi
  done
fi

echo "  💡 If seeing 'No files eligible for import':"
echo "     - Check remote path mappings (Settings → Download Clients)"
echo "     - Verify download client category matches"
echo "     - Check container can access download directory"
echo ""
echo "  💡 For stuck downloads:"
echo "     - Verify download client is running and accessible"
echo "     - Check indexer health in Prowlarr"
echo "     - Ensure sufficient disk space"

echo ""
echo "✅ Diagnostics complete"
