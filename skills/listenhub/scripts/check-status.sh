#!/usr/bin/env bash
# Check episode status via ListenHub API
# Usage: ./check-status.sh --episode <episode-id> --type podcast|flow-speech|explainer [--wait] [--max-polls N] [--timeout S] [--interval S]
#
# Without --wait: single-shot query (backward compatible)
# With --wait: polls until terminal status, respecting limits
#
# Exit codes:
#   0 = success (or single-shot completed)
#   1 = generation failed / error
#   2 = timeout or rate-limited (still pending, safe to retry after a short wait)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib.sh"

EPISODE_ID=""
TYPE="podcast"
WAIT_MODE=false
MAX_POLLS=30
TIMEOUT=300
INTERVAL=10

usage() {
  cat >&2 <<'EOF'
Usage: ./check-status.sh --episode <episode-id> --type podcast|flow-speech|tts|explainer [--wait] [--max-polls N] [--timeout S] [--interval S]

Options:
  --wait          Enable polling mode (wait for completion)
  --max-polls N   Maximum poll attempts (default: 30)
  --timeout S     Maximum total wait in seconds (default: 300)
  --interval S    Base poll interval in seconds (default: 10)

Exit codes:
  0 = completed successfully
  1 = generation failed or error
  2 = timeout (still pending after limits reached)
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --episode)
      EPISODE_ID="${2:-}"
      shift 2
      ;;
    --type)
      TYPE="${2:-podcast}"
      shift 2
      ;;
    --wait)
      WAIT_MODE=true
      shift
      ;;
    --max-polls)
      MAX_POLLS="${2:-30}"
      shift 2
      ;;
    --timeout)
      TIMEOUT="${2:-300}"
      shift 2
      ;;
    --interval)
      INTERVAL="${2:-10}"
      shift 2
      ;;
    --help)
      usage
      exit 0
      ;;
    *)
      echo "Error: Unknown argument $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [ -z "$EPISODE_ID" ]; then
  echo "Error: --episode is required" >&2
  usage
  exit 1
fi

case "$TYPE" in
  podcast)
    ENDPOINT="podcast/episodes/${EPISODE_ID}"
    ;;
  explainer)
    ENDPOINT="storybook/episodes/${EPISODE_ID}"
    ;;
  flow-speech|tts)
    ENDPOINT="flow-speech/episodes/${EPISODE_ID}"
    ;;
  *)
    echo "Error: Invalid type '$TYPE'. Must be: podcast | flow-speech | tts | explainer" >&2
    exit 1
    ;;
esac

# Single-shot mode (default, backward compatible)
if [ "$WAIT_MODE" = false ]; then
  api_get "$ENDPOINT"
  exit $?
fi

# Polling mode
check_jq

START_TIME=$(date +%s)
POLL_COUNT=0

while true; do
  POLL_COUNT=$((POLL_COUNT + 1))

  # Check poll limit
  if [ $POLL_COUNT -gt $MAX_POLLS ]; then
    echo "Error: Max polls ($MAX_POLLS) reached. Episode still processing." >&2
    exit 2
  fi

  # Check timeout
  ELAPSED=$(( $(date +%s) - START_TIME ))
  if [ $ELAPSED -ge $TIMEOUT ]; then
    echo "Error: Timeout (${TIMEOUT}s) reached. Episode still processing." >&2
    exit 2
  fi

  # Fetch status; catch transient network errors (curl failures) and retry
  if ! RESPONSE=$(api_get "$ENDPOINT"); then
    echo "Poll $POLL_COUNT: network error, retrying in ${INTERVAL}s" >&2
    sleep "$INTERVAL"
    continue
  fi

  # Rate-limited — exit and let the calling agent decide when to retry
  RESP_CODE=$(echo "$RESPONSE" | jq -r '.code // 0' 2>/dev/null || echo "0")
  if [ "$RESP_CODE" = "429" ] || [ "$RESP_CODE" = "25429" ]; then
    echo "Error: Rate limited (429). Retry after a short wait." >&2
    exit 2
  fi

  # Check process status (default to "unknown" if response is not valid JSON)
  STATUS=$(echo "$RESPONSE" | jq -r '.data.processStatus // "unknown"' 2>/dev/null || echo "unknown")

  case "$STATUS" in
    success|completed)
      echo "$RESPONSE"
      exit 0
      ;;
    failed|error)
      echo "$RESPONSE" >&2
      exit 1
      ;;
    *)
      REMAINING=$((TIMEOUT - ELAPSED))
      echo "Poll $POLL_COUNT: status=$STATUS, elapsed=${ELAPSED}s, remaining=${REMAINING}s" >&2
      sleep "$INTERVAL"
      ;;
  esac
done
