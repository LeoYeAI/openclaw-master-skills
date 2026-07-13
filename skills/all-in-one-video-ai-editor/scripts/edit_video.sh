#!/usr/bin/env bash
# End-to-end Sparki video processing workflow.
#
# Orchestrates upload → wait for asset ready → create project → poll until done.
# Progress logs are written to stderr; only the final result_url is written to stdout,
# making this script safe to use in pipelines.
#
# Usage:
#   edit_video.sh <file_path> <tips> [user_prompt] [aspect_ratio] [duration]
#
# Args:
#   file_path:    Local path to a video file (mp4 or mov, max 3GB)
#   tips:         Comma-separated tip IDs or descriptions (e.g. "1,2")
#   user_prompt:  (optional) Free-text requirement
#   aspect_ratio: (optional) "9:16" (default) | "1:1" | "16:9"
#   duration:     (optional) Target duration in seconds
#
# Environment variables:
#   SPARKI_API_KEY        Required. Your Sparki Business API key.
#   WORKFLOW_TIMEOUT      Optional. Max seconds to wait for project completion (default: 3600).
#   ASSET_TIMEOUT         Optional. Max seconds to wait for asset upload (default: 60).
#
# Outputs (stdout): result_url — the 24-hour pre-signed download URL of the processed video.
# Exit codes:
#   0 — success
#   1 — input/config error
#   2 — asset processing timed out
#   3 — project processing timed out
#   4 — project failed

set -euo pipefail

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SPARKI_API_BASE="https://agent-api-test.aicoding.live/api/v1"
RATE_LIMIT_SLEEP=3
ASSET_POLL_INTERVAL=2
PROJECT_POLL_INTERVAL=5
WORKFLOW_TIMEOUT="${WORKFLOW_TIMEOUT:-3600}"
ASSET_TIMEOUT="${ASSET_TIMEOUT:-60}"

# Resolve scripts directory relative to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---------------------------------------------------------------------------
# Validate environment
# ---------------------------------------------------------------------------
: "${SPARKI_API_KEY:?Error: SPARKI_API_KEY environment variable is required}"

# ---------------------------------------------------------------------------
# Validate arguments
# ---------------------------------------------------------------------------
if [[ $# -lt 2 ]]; then
  echo "Usage: edit_video.sh <file_path> <tips> [user_prompt] [aspect_ratio] [duration]" >&2
  echo "  Example: edit_video.sh my_video.mp4 '1,2' 'make it dynamic' '9:16' 60" >&2
  exit 1
fi

FILE_PATH="$1"
TIPS="$2"
USER_PROMPT="${3:-}"
ASPECT_RATIO="${4:-9:16}"
DURATION="${5:-}"

# ---------------------------------------------------------------------------
# Step 1: Upload asset
# ---------------------------------------------------------------------------
echo "[1/4] Uploading asset: $FILE_PATH" >&2

OBJECT_KEY=$(bash "${SCRIPT_DIR}/upload_asset.sh" "$FILE_PATH")

if [[ -z "$OBJECT_KEY" ]]; then
  echo "Error: upload_asset.sh returned empty object_key" >&2
  exit 1
fi

echo "[1/4] Asset accepted. object_key=$OBJECT_KEY" >&2

# ---------------------------------------------------------------------------
# Step 2: Poll until asset status = completed
# ---------------------------------------------------------------------------
echo "[2/4] Waiting for asset upload to complete (timeout=${ASSET_TIMEOUT}s)..." >&2

ASSET_START=$(date +%s)
while true; do
  sleep "$ASSET_POLL_INTERVAL"

  ASSET_RESP=$(curl -sS \
    -X GET "${SPARKI_API_BASE}/business/assets/${OBJECT_KEY}/status" \
    -H "X-API-Key: $SPARKI_API_KEY")

  ASSET_STATUS=$(echo "$ASSET_RESP" | jq -r '.data.status // "unknown"')
  echo "[2/4] Asset status: $ASSET_STATUS" >&2

  if [[ "$ASSET_STATUS" == "completed" ]]; then
    echo "[2/4] Asset ready." >&2
    break
  fi

  if [[ "$ASSET_STATUS" == "failed" ]]; then
    echo "Error: Asset processing failed." >&2
    exit 2
  fi

  ELAPSED=$(( $(date +%s) - ASSET_START ))
  if (( ELAPSED >= ASSET_TIMEOUT )); then
    echo "Error: Asset upload timed out after ${ASSET_TIMEOUT}s (status=$ASSET_STATUS)." >&2
    exit 2
  fi
done

# ---------------------------------------------------------------------------
# Step 3: Create project
# ---------------------------------------------------------------------------
echo "[3/4] Creating video project (tips=$TIPS, aspect_ratio=$ASPECT_RATIO)..." >&2

sleep "$RATE_LIMIT_SLEEP"

PROJECT_ID=$(bash "${SCRIPT_DIR}/create_project.sh" \
  "$OBJECT_KEY" "$TIPS" "$USER_PROMPT" "$ASPECT_RATIO" "$DURATION")

if [[ -z "$PROJECT_ID" ]]; then
  echo "Error: create_project.sh returned empty project_id" >&2
  exit 1
fi

echo "[3/4] Project created. project_id=$PROJECT_ID" >&2

# ---------------------------------------------------------------------------
# Step 4: Poll until project completes
# ---------------------------------------------------------------------------
echo "[4/4] Waiting for video processing (timeout=${WORKFLOW_TIMEOUT}s)..." >&2

PROJECT_START=$(date +%s)
while true; do
  sleep "$PROJECT_POLL_INTERVAL"

  # Use get_project_status.sh; disable errexit around it since exit code 2 = in-progress
  set +e
  STATUS_LINE=$(bash "${SCRIPT_DIR}/get_project_status.sh" "$PROJECT_ID" 2>/dev/null)
  STATUS_EXIT=$?
  set -e

  # STATUS_LINE format: "COMPLETED <url>" | "FAILED <msg>" | "<status>"
  STATUS_WORD="${STATUS_LINE%% *}"

  echo "[4/4] Project status: $STATUS_WORD" >&2

  if [[ "$STATUS_WORD" == "COMPLETED" ]]; then
    RESULT_URL="${STATUS_LINE#COMPLETED }"
    echo "[4/4] Processing complete!" >&2
    # Write result_url to stdout — safe for pipeline capture
    echo "$RESULT_URL"
    exit 0
  fi

  if [[ "$STATUS_WORD" == "FAILED" ]]; then
    ERROR_MSG="${STATUS_LINE#FAILED }"
    echo "Error: Project failed — $ERROR_MSG" >&2
    exit 4
  fi

  ELAPSED=$(( $(date +%s) - PROJECT_START ))
  if (( ELAPSED >= WORKFLOW_TIMEOUT )); then
    echo "Error: Project processing timed out after ${WORKFLOW_TIMEOUT}s (status=$STATUS_WORD)." >&2
    echo "Tip: Query the project manually: bash get_project_status.sh $PROJECT_ID" >&2
    exit 3
  fi
done
