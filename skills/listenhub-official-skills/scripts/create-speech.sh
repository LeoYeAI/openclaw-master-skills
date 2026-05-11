#!/usr/bin/env bash
# Create multi-speaker audio from scripts via ListenHub API
# Usage: ./create-speech.sh --scripts <scripts_json_file|->
#
# Example:
#   ./create-speech.sh --scripts scripts.json
#
# scripts.json format:
# {
#   "scripts": [
#     {"content": "Hello everyone", "speakerId": "cozy-man-english"},
#     {"content": "Welcome to the show", "speakerId": "travel-girl-english"}
#   ]
# }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib.sh"

SCRIPTS_FILE=""

usage() {
  cat >&2 <<'EOF'
Usage: ./create-speech.sh --scripts <scripts_json_file|->

Example:
  ./create-speech.sh --scripts scripts.json

scripts.json format:
{
  "scripts": [
    {"content": "Hello everyone", "speakerId": "cozy-man-english"},
    {"content": "Welcome to the show", "speakerId": "travel-girl-english"}
  ]
}

Or use inline JSON:
  echo '{"scripts":[{"content":"Hello","speakerId":"cozy-man-english"}]}' | ./create-speech.sh --scripts -
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
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

if [ -z "$SCRIPTS_FILE" ]; then
  echo "Error: --scripts is required" >&2
  usage
  exit 1
fi

check_jq

# Read scripts from file or stdin
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
if ! echo "$BODY" | jq empty 2>/dev/null; then
  echo "Error: Invalid JSON format" >&2
  exit 1
fi
if ! echo "$BODY" | jq -e '
  (.scripts | type == "array") and
  ((.scripts | length) > 0) and
  (all(.scripts[]; (.content | type == "string" and length > 0) and (.speakerId | type == "string" and length > 0)))
' >/dev/null 2>&1; then
  echo "Error: Invalid scripts structure (require scripts[].content and scripts[].speakerId)" >&2
  exit 1
fi

api_post "speech" "$BODY"
