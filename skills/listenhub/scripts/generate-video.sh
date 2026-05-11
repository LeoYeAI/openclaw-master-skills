#!/usr/bin/env bash
# Generate video file from explainer episode
# Usage: ./generate-video.sh --episode <episode-id>

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib.sh"

EPISODE_ID=""

usage() {
  echo "Usage: $0 --episode <episode-id>" >&2
}

while [ $# -gt 0 ]; do
  case "$1" in
    --episode)
      EPISODE_ID="${2:-}"
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

api_post "storybook/episodes/${EPISODE_ID}/video" "{}"
