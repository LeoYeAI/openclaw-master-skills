#!/usr/bin/env bash
# Create explainer video via ListenHub API
# Usage: ./create-explainer.sh --content <text> --language zh|en --mode info|story --speakers <id>

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib.sh"

CONTENT=""
LANGUAGE=""
MODE="info"
SPEAKERS=""

usage() {
  cat >&2 <<'EOF'
Usage: ./create-explainer.sh --content <text> --language zh|en --mode info|story --speakers <id>

Examples:
  ./create-explainer.sh --content "介绍产品功能" --language zh --mode info --speakers cozy-man-english
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --content)
      CONTENT="${2:-}"
      shift 2
      ;;
    --language|--lang)
      LANGUAGE="${2:-}"
      shift 2
      ;;
    --mode)
      MODE="${2:-info}"
      shift 2
      ;;
    --speakers)
      SPEAKERS="${2:-}"
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

if [ -z "$CONTENT" ] || [ -z "$LANGUAGE" ] || [ -z "$SPEAKERS" ]; then
  echo "Error: --content, --language, and --speakers are required" >&2
  usage
  exit 1
fi

if [[ ! "$LANGUAGE" =~ ^(zh|en)$ ]]; then
  echo "Error: language must be zh or en" >&2
  exit 1
fi

if [[ ! "$MODE" =~ ^(info|story)$ ]]; then
  echo "Error: mode must be info or story" >&2
  exit 1
fi

check_jq

SPEAKER_IDS=()
IFS=',' read -r -a SPEAKER_ITEMS <<< "$SPEAKERS"
for speaker_item in "${SPEAKER_ITEMS[@]}"; do
  speaker_item=$(trim_ws "$speaker_item")
  if [ -n "$speaker_item" ]; then
    SPEAKER_IDS+=("$speaker_item")
  fi
done
if [ ${#SPEAKER_IDS[@]} -ne 1 ]; then
  echo "Error: speakers must contain 1 item" >&2
  exit 1
fi

CONTENT_JSON=$(jq -n --arg c "$CONTENT" '$c')
SPEAKERS_JSON=$(printf '%s\n' "${SPEAKER_IDS[@]}" | jq -R '{speakerId: .}' | jq -s '.')
BODY=$(jq -n \
  --argjson content "$CONTENT_JSON" \
  --argjson speakers "$SPEAKERS_JSON" \
  --arg lang "$LANGUAGE" \
  --arg mode "$MODE" \
  '{sources: [{type: "text", content: $content}], speakers: $speakers, language: $lang, mode: $mode}')

api_post "storybook/episodes" "$BODY"
