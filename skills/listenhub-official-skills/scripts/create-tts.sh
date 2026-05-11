#!/usr/bin/env bash
# Create FlowSpeech audio via ListenHub API
# Usage: ./create-tts.sh --type text|url --content <text|url> --language zh|en --mode smart|direct --speakers <id>
#
# Examples:
#   ./create-tts.sh --type text --content "欢迎使用 ListenHub 音频生成服务" --language zh --mode smart --speakers cozy-man-english
#   ./create-tts.sh --type url --content "https://example.com/article.html" --language en --mode smart --speakers cozy-man-english

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib.sh"

TYPE=""
CONTENT=""
LANGUAGE=""
MODE="direct"
SPEAKERS=""

usage() {
  cat >&2 <<'EOF'
Usage: ./create-tts.sh --type text|url --content <text|url> --language zh|en --mode smart|direct --speakers <id>

Examples:
  ./create-tts.sh --type text --content "欢迎使用 ListenHub 音频生成服务" --language zh --mode smart --speakers cozy-man-english
  ./create-tts.sh --type url --content "https://example.com/article.html" --language en --mode smart --speakers cozy-man-english

Notes:
  - Text input length limit: 10000 characters
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --type)
      TYPE="${2:-}"
      shift 2
      ;;
    --content)
      CONTENT="${2:-}"
      shift 2
      ;;
    --language|--lang)
      LANGUAGE="${2:-}"
      shift 2
      ;;
    --mode)
      MODE="${2:-direct}"
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

if [ -z "$TYPE" ] || [ -z "$CONTENT" ] || [ -z "$LANGUAGE" ] || [ -z "$SPEAKERS" ]; then
  echo "Error: --type, --content, --language, and --speakers are required" >&2
  usage
  exit 1
fi

if [[ ! "$TYPE" =~ ^(text|url)$ ]]; then
  echo "Error: type must be text or url" >&2
  exit 1
fi

if [[ ! "$LANGUAGE" =~ ^(zh|en)$ ]]; then
  echo "Error: language must be zh or en" >&2
  exit 1
fi

if [[ ! "$MODE" =~ ^(smart|direct)$ ]]; then
  echo "Error: mode must be smart or direct" >&2
  exit 1
fi

check_jq

if [ "$TYPE" = "text" ]; then
  CONTENT_LEN=$(printf '%s' "$CONTENT" | wc -m | tr -d ' ')
  if [ "$CONTENT_LEN" -gt 10000 ]; then
    echo "Error: text content exceeds 10000 characters" >&2
    exit 1
  fi
fi

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
  --arg type "$TYPE" \
  --argjson speakers "$SPEAKERS_JSON" \
  --arg lang "$LANGUAGE" \
  --arg mode "$MODE" \
  '{sources: [{type: $type, content: $content}], speakers: $speakers, language: $lang, mode: $mode}')

api_post "flow-speech/episodes" "$BODY"
