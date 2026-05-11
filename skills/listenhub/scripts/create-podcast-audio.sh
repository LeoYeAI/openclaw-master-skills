#!/usr/bin/env bash
# Generate audio from podcast text content (Stage 2 of two-stage generation)
# Usage: ./create-podcast-audio.sh --episode <episode-id> [--scripts <scripts_json_file>]
#
# Examples:
#   # Use original scripts
#   ./create-podcast-audio.sh --episode "68d699ebc4b373bd1ae50dde"
#
#   # Use modified scripts
#   ./create-podcast-audio.sh --episode "68d699ebc4b373bd1ae50dde" --scripts modified-scripts.json
#
# modified-scripts.json format:
# {
#   "scripts": [
#     {"content": "Hello everyone", "speakerId": "CN-Man-Beijing-V2"},
#     {"content": "Welcome", "speakerId": "chat-girl-105-cn"}
#   ]
# }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib.sh"

EPISODE_ID=""
SCRIPTS_FILE=""

usage() {
  cat >&2 <<'EOF'
Usage: ./create-podcast-audio.sh --episode <episode-id> [--scripts <scripts_json_file>]

Examples:
  # Use original scripts
  ./create-podcast-audio.sh --episode "68d699ebc4b373bd1ae50dde"

  # Use modified scripts
  ./create-podcast-audio.sh --episode "68d699ebc4b373bd1ae50dde" --scripts modified-scripts.json

  # Use stdin for scripts
  echo '{"scripts":[{"content":"Hello","speakerId":"cozy-man-english"}]}' | ./create-podcast-audio.sh --episode "68d699ebc4b373bd1ae50dde" --scripts -

modified-scripts.json format:
{
  "scripts": [
    {"content": "Hello everyone", "speakerId": "CN-Man-Beijing-V2"},
    {"content": "Welcome", "speakerId": "chat-girl-105-cn"}
  ]
}
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --episode)
      EPISODE_ID="${2:-}"
      shift 2
      ;;
    --scripts)
      SCRIPTS_FILE="${2:-}"
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

# Build request body
if [ -n "$SCRIPTS_FILE" ]; then
  if [ "$SCRIPTS_FILE" = "-" ]; then
    BODY=$(cat)
  else
    if [ ! -f "$SCRIPTS_FILE" ]; then
      echo "Error: File not found: $SCRIPTS_FILE" >&2
      exit 1
    fi
    BODY=$(cat "$SCRIPTS_FILE")
  fi

  # Validate JSON format
  if command -v jq &>/dev/null; then
    if ! echo "$BODY" | jq empty 2>/dev/null; then
      echo "Error: Invalid JSON format" >&2
      exit 1
    fi
  fi
else
  BODY="{}"
fi

api_post "podcast/episodes/${EPISODE_ID}/audio" "$BODY"
