#!/bin/bash
# BrainX V5 Health Check Cron Job
# Runs every 30 minutes to verify BrainX status

set -euo pipefail

ROOT="/home/clawd/.openclaw/skills/brainx-v5"
LOG_FILE="$ROOT/cron/health.log"
LOCK_FILE="/tmp/brainx-health-check.lock"

load_env() {
  for env_file in "$ROOT/.env" "/home/clawd/.openclaw/.env" "/home/clawd/.env"; do
    if [ -f "$env_file" ]; then
      set -a
      # shellcheck disable=SC1090
      source "$env_file"
      set +a
    fi
  done
  export DOTENV_CONFIG_QUIET="${DOTENV_CONFIG_QUIET:-true}"
}

detect_cli() {
  for candidate in "$ROOT/brainx" "$ROOT/brainx-v5" "$ROOT/brainx-v5-cli"; do
    if [ -x "$candidate" ]; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Prevent concurrent runs
if [ -f "$LOCK_FILE" ]; then
  PID=$(cat "$LOCK_FILE" 2>/dev/null || echo "")
  if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
    log "Health check already running (PID: $PID), skipping"
    exit 0
  fi
fi

mkdir -p "$(dirname "$LOG_FILE")"
echo $$ > "$LOCK_FILE"
trap 'rm -f "$LOCK_FILE" "$TMP_OUT"' EXIT

load_env

if ! BRAINX_CLI="$(detect_cli)"; then
  log "ERROR: BrainX CLI not found (checked: brainx, brainx-v5, brainx-v5-cli)"
  exit 1
fi

if [ -z "${DATABASE_URL:-}" ]; then
  log "ERROR: DATABASE_URL not set"
  exit 1
fi

TMP_OUT="$(mktemp /tmp/brainx-health-output.XXXXXX)"
log "Starting BrainX health check (cli=$(basename "$BRAINX_CLI"))"

if "$BRAINX_CLI" health > "$TMP_OUT" 2>&1; then
  DETAILS=$(tr '\n' ' ' < "$TMP_OUT" | sed 's/[[:space:]]\+/ /g')
  log "Health check PASSED: ${DETAILS:-ok}"

  MEM_COUNT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM brainx_memories;" 2>/dev/null | xargs || echo "0")
  RECENT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM brainx_memories WHERE created_at > NOW() - INTERVAL '24 hours';" 2>/dev/null | xargs || echo "0")
  log "Total memories: $MEM_COUNT"
  log "Last 24h: $RECENT memories"
  STATUS="OK"
else
  ERROR_MSG=$(tr '\n' ' ' < "$TMP_OUT" | sed 's/[[:space:]]\+/ /g')
  log "Health check FAILED: ${ERROR_MSG:-Unknown error}"
  STATUS="FAILED"
fi

# Keep log bounded
if [ -f "$LOG_FILE" ]; then
  tail -n 1000 "$LOG_FILE" > "$LOG_FILE.tmp" 2>/dev/null && mv "$LOG_FILE.tmp" "$LOG_FILE" || true
fi

log "Completed. Status: $STATUS"
exit 0
