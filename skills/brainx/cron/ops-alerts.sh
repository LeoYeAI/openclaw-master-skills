#!/bin/bash
set -euo pipefail

ROOT="/home/clawd/.openclaw/skills/brainx-v5"
cd "$ROOT"

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

load_env

if ! BRAINX_CLI="$(detect_cli)"; then
  echo "ERROR: BrainX CLI not found (checked: brainx, brainx-v5, brainx-v5-cli)"
  exit 1
fi

if [ -z "${DATABASE_URL:-}" ]; then
  echo "ERROR: DATABASE_URL not set"
  exit 1
fi

LIFECYCLE_JSON=$("$BRAINX_CLI" lifecycle-run --dryRun --json)
METRICS_JSON=$("$BRAINX_CLI" metrics --days 1 --json)

INJECT_MS=$(echo "$METRICS_JSON" | jq -r '.query_performance[]? | select(.query_kind=="inject") | .avg_duration_ms' | head -n1)
SEARCH_MS=$(echo "$METRICS_JSON" | jq -r '.query_performance[]? | select(.query_kind=="search") | .avg_duration_ms' | head -n1)
PROMOTED=$(echo "$LIFECYCLE_JSON" | jq -r '.updated.promoted // 0')
DEGRADED=$(echo "$LIFECYCLE_JSON" | jq -r '.updated.degraded // 0')

ALERTS=()
if [ -n "$INJECT_MS" ] && [ "$INJECT_MS" != "null" ]; then
  INJECT_INT=${INJECT_MS%.*}
  if [ "$INJECT_INT" -ge 2000 ]; then
    ALERTS+=("inject alto (${INJECT_MS} ms)")
  fi
fi
if [ -n "$SEARCH_MS" ] && [ "$SEARCH_MS" != "null" ]; then
  SEARCH_INT=${SEARCH_MS%.*}
  if [ "$SEARCH_INT" -ge 1300 ]; then
    ALERTS+=("search alto (${SEARCH_MS} ms)")
  fi
fi

if [ "$DEGRADED" -gt 25 ]; then
  ALERTS+=("degradaciones altas (${DEGRADED})")
fi

echo "Reporte operativo BrainX (24h)"
echo "- cli: $(basename "$BRAINX_CLI")"
echo "- lifecycle: promoted=${PROMOTED}, degraded=${DEGRADED}"
echo "- latencia: inject=${INJECT_MS:-n/a}ms, search=${SEARCH_MS:-n/a}ms"
if [ ${#ALERTS[@]} -eq 0 ]; then
  echo "- alertas: ninguna"
else
  echo "- alertas:"
  for a in "${ALERTS[@]}"; do
    echo "  - ${a}"
  done
fi
