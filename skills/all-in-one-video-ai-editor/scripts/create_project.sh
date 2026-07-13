#!/usr/bin/env bash
# Create an AI video processing project from previously uploaded assets.
#
# Usage: create_project.sh <object_keys> <tips> [user_prompt] [aspect_ratio] [duration]
#
# Args:
#   object_keys:   Comma-separated list of object_key values from upload_asset.sh
#   tips:          Comma-separated list of tip IDs or descriptions (e.g. "1,2" or "dynamic,trendy")
#   user_prompt:   (optional) Free-text requirement description
#   aspect_ratio:  (optional) Output aspect ratio — "9:16" (default), "1:1", "16:9"
#   duration:      (optional) Target output duration in seconds (integer)
#
# Outputs (stdout): project_id on success
# Exits with 1 on argument error, 2 on API error.

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
if [[ $# -lt 2 ]]; then
  echo "Usage: create_project.sh <object_keys> <tips> [user_prompt] [aspect_ratio] [duration]" >&2
  echo "  object_keys:  comma-separated (e.g. 'assets/98/abc.mp4')" >&2
  echo "  tips:         comma-separated IDs or text (e.g. '1,2')" >&2
  exit 1
fi

OBJECT_KEYS_CSV="$1"
TIPS_CSV="$2"
USER_PROMPT="${3:-}"
ASPECT_RATIO="${4:-9:16}"
DURATION="${5:-}"

# ---------------------------------------------------------------------------
# Build JSON arrays from CSV inputs using jq
# ---------------------------------------------------------------------------
OBJECT_KEYS_JSON=$(echo "$OBJECT_KEYS_CSV" | jq -Rc 'split(",")')
TIPS_JSON=$(echo "$TIPS_CSV" | jq -Rc 'split(",") | map(tonumber? // .)')

# Build request body — conditionally include optional fields
REQUEST_BODY=$(jq -n \
  --argjson object_keys "$OBJECT_KEYS_JSON" \
  --argjson tips "$TIPS_JSON" \
  --arg user_prompt "$USER_PROMPT" \
  --arg aspect_ratio "$ASPECT_RATIO" \
  --arg duration "$DURATION" \
  '{
    object_keys: $object_keys,
    tips: $tips,
    aspect_ratio: $aspect_ratio
  }
  | if $user_prompt != "" then . + {user_prompt: $user_prompt} else . end
  | if $duration != "" then . + {duration: ($duration | tonumber)} else . end')

# ---------------------------------------------------------------------------
# Create project via POST
# ---------------------------------------------------------------------------
sleep "$RATE_LIMIT_SLEEP"

RESPONSE=$(curl -sS \
  -X POST "${SPARKI_API_BASE}/business/projects" \
  -H "X-API-Key: $SPARKI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$REQUEST_BODY")

# Parse response
HTTP_CODE=$(echo "$RESPONSE" | jq -r '.code // "unknown"')
MESSAGE=$(echo "$RESPONSE" | jq -r '.message // "unknown"')

if [[ "$HTTP_CODE" != "200" && "$HTTP_CODE" != "0" ]]; then
  echo "Error: Project creation failed (code=$HTTP_CODE): $MESSAGE" >&2
  if [[ "$HTTP_CODE" == "453" ]]; then
    echo "Tip: Too many concurrent projects. Wait for an existing project to complete, or run edit_video.sh which handles this automatically." >&2
  fi
  exit 2
fi

PROJECT_ID=$(echo "$RESPONSE" | jq -r '.data.project_id // empty')
if [[ -z "$PROJECT_ID" ]]; then
  echo "Error: No project_id in response. Full response:" >&2
  echo "$RESPONSE" >&2
  exit 2
fi

echo "$PROJECT_ID"
