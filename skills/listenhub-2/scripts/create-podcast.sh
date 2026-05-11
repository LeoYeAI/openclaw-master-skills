#!/usr/bin/env bash
# Create podcast episode via ListenHub API
# Usage: ./create-podcast.sh --query <text> --language zh|en --mode quick|deep|debate --speakers <id1,id2> [--source-url <url>] [--source-text <text>]
#
# Examples:
#   ./create-podcast.sh --query "AI 的未来发展" --language zh --mode deep --speakers cozy-man-english
#   ./create-podcast.sh --query "讨论远程工作的利弊" --language en --mode debate --speakers cozy-man-english,travel-girl-english
#   ./create-podcast.sh --query "分析这篇文章" --language en --mode deep --speakers cozy-man-english --source-url "https://blog.example.com/article"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib.sh"

QUERY=""
LANGUAGE=""
MODE="quick"
SPEAKERS=""
SOURCE_URLS=()
SOURCE_TEXTS=()

usage() {
  cat >&2 <<'EOF'
Usage: ./create-podcast.sh --query <text> --language zh|en --mode quick|deep|debate --speakers <id1,id2> [--source-url <url>] [--source-text <text>]

Examples:
  ./create-podcast.sh --query "AI 的未来发展" --language zh --mode deep --speakers cozy-man-english
  ./create-podcast.sh --query "讨论远程工作的利弊" --language en --mode debate --speakers cozy-man-english,travel-girl-english
  ./create-podcast.sh --query "分析这篇文章" --language en --mode deep --speakers cozy-man-english --source-url "https://blog.example.com/article"
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --query)
      QUERY="${2:-}"
      shift 2
      ;;
    --language|--lang)
      LANGUAGE="${2:-}"
      shift 2
      ;;
    --mode)
      MODE="${2:-quick}"
      shift 2
      ;;
    --speakers)
      SPEAKERS="${2:-}"
      shift 2
      ;;
    --source-url)
      SOURCE_URLS+=("${2:-}")
      shift 2
      ;;
    --source-text)
      SOURCE_TEXTS+=("${2:-}")
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

if [ -z "$QUERY" ] || [ -z "$LANGUAGE" ] || [ -z "$SPEAKERS" ]; then
  echo "Error: --query, --language, and --speakers are required" >&2
  usage
  exit 1
fi

check_jq

if [[ ! "$LANGUAGE" =~ ^(zh|en)$ ]]; then
  echo "Error: language must be zh or en" >&2
  exit 1
fi

if [[ ! "$MODE" =~ ^(quick|deep|debate)$ ]]; then
  echo "Error: mode must be quick, deep, or debate" >&2
  exit 1
fi

SPEAKER_IDS=()
IFS=',' read -r -a SPEAKER_ITEMS <<< "$SPEAKERS"
for speaker_item in "${SPEAKER_ITEMS[@]}"; do
  speaker_item=$(trim_ws "$speaker_item")
  if [ -n "$speaker_item" ]; then
    SPEAKER_IDS+=("$speaker_item")
  fi
done
if [ ${#SPEAKER_IDS[@]} -lt 1 ] || [ ${#SPEAKER_IDS[@]} -gt 2 ]; then
  echo "Error: speakers must contain 1-2 items" >&2
  exit 1
fi

if [ "$MODE" = "debate" ] && [ ${#SPEAKER_IDS[@]} -ne 2 ]; then
  echo "Error: debate mode requires 2 speakers" >&2
  exit 1
fi

SOURCE_URLS_CLEAN=()
if [ ${#SOURCE_URLS[@]} -gt 0 ]; then
  for url in "${SOURCE_URLS[@]}"; do
    url=$(trim_ws "$url")
    if [ -n "$url" ]; then
      SOURCE_URLS_CLEAN+=("$url")
    fi
  done
fi
SOURCE_TEXTS_CLEAN=()
if [ ${#SOURCE_TEXTS[@]} -gt 0 ]; then
  for text in "${SOURCE_TEXTS[@]}"; do
    text=$(trim_ws "$text")
    if [ -n "$text" ]; then
      SOURCE_TEXTS_CLEAN+=("$text")
    fi
  done
fi

QUERY_JSON=$(jq -n --arg q "$QUERY" '$q')
SPEAKERS_JSON=$(printf '%s\n' "${SPEAKER_IDS[@]}" | jq -R '{speakerId: .}' | jq -s '.')
SOURCES_JSON="[]"
if [ ${#SOURCE_URLS_CLEAN[@]} -gt 0 ] || [ ${#SOURCE_TEXTS_CLEAN[@]} -gt 0 ]; then
  URL_JSON="[]"
  if [ ${#SOURCE_URLS_CLEAN[@]} -gt 0 ]; then
    URL_JSON=$(printf '%s\0' "${SOURCE_URLS_CLEAN[@]}" | jq -Rs 'split("\u0000")[:-1] | map({type: "url", content: .})')
  fi
  TEXT_JSON="[]"
  if [ ${#SOURCE_TEXTS_CLEAN[@]} -gt 0 ]; then
    TEXT_JSON=$(printf '%s\0' "${SOURCE_TEXTS_CLEAN[@]}" | jq -Rs 'split("\u0000")[:-1] | map({type: "text", content: .})')
  fi
  SOURCES_JSON=$(jq -n --argjson urls "$URL_JSON" --argjson texts "$TEXT_JSON" '$urls + $texts')
fi

if [ "$(echo "$SOURCES_JSON" | jq 'length')" -gt 0 ]; then
  BODY=$(jq -n \
    --argjson query "$QUERY_JSON" \
    --argjson speakers "$SPEAKERS_JSON" \
    --arg lang "$LANGUAGE" \
    --arg mode "$MODE" \
    --argjson sources "$SOURCES_JSON" \
    '{query: $query, speakers: $speakers, language: $lang, mode: $mode, sources: $sources}')
else
  BODY=$(jq -n \
    --argjson query "$QUERY_JSON" \
    --argjson speakers "$SPEAKERS_JSON" \
    --arg lang "$LANGUAGE" \
    --arg mode "$MODE" \
    '{query: $query, speakers: $speakers, language: $lang, mode: $mode}')
fi

api_post "podcast/episodes" "$BODY"
