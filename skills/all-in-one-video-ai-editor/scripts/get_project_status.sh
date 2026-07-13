#!/usr/bin/env bash
# Query the status of a Sparki video processing project.
#
# Usage: get_project_status.sh <project_id>
#
# Args:
#   project_id: UUID returned by create_project.sh
#
# Outputs (stdout):
#   - On COMPLETED:  "COMPLETED <result_url>"
#   - On FAILED:     "FAILED <error_message>"
#   - On other:      "<status>"   (e.g. INIT, CHAT, PLAN, EXECUTOR, QUEUED)
#
# Exit codes:
#   0 — terminal state (COMPLETED or FAILED)
#   2 — still in progress (poll again)
#   1 — argument or API error

set -euo pipefail

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SPARKI_API_BASE="https://agent-api-test.aicoding.live/api/v1"
RATE_LIMIT_SLEEP=3

# ---------------------------------------------------------------------------
# Validate environment
# ---------------------------------------------------------------------------
: "${SPARKI_API_KEY:?Error: SPARKI_API_KEY environment variable is required}"

# ---------------------------------------------------------------------------
# Validate arguments
# ---------------------------------------------------------------------------
if [[ $# -lt 1 ]]; then
  echo "Usage: get_project_status.sh <project_id>" >&2
  exit 1
fi

PROJECT_ID="$1"

# ---------------------------------------------------------------------------
# Query project status
# ---------------------------------------------------------------------------
sleep "$RATE_LIMIT_SLEEP"

RESPONSE=$(curl -sS \
  -X GET "${SPARKI_API_BASE}/business/projects/${PROJECT_ID}" \
  -H "X-API-Key: $SPARKI_API_KEY")

# Check API-level error
HTTP_CODE=$(echo "$RESPONSE" | jq -r '.code // "unknown"')
MESSAGE=$(echo "$RESPONSE" | jq -r '.message // "unknown"')

if [[ "$HTTP_CODE" != "200" && "$HTTP_CODE" != "0" ]]; then
  echo "Error: Query failed (code=$HTTP_CODE): $MESSAGE" >&2
  exit 1
fi

STATUS=$(echo "$RESPONSE" | jq -r '.data.status // "UNKNOWN"')

case "$STATUS" in
  COMPLETED)
    RESULT_URL=$(echo "$RESPONSE" | jq -r '.data.result_url // empty')
    echo "COMPLETED ${RESULT_URL}"
    exit 0
    ;;
  FAILED)
    ERROR_MSG=$(echo "$RESPONSE" | jq -r '.data.error // "unknown error"')
    echo "FAILED ${ERROR_MSG}"
    exit 0
    ;;
  INIT|CHAT|PLAN|EXECUTOR|QUEUED|processing)
    # Still in progress — caller should poll
    echo "$STATUS"
    exit 2
    ;;
  *)
    echo "$STATUS"
    exit 2
    ;;
esac
