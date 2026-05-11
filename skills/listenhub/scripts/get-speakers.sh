#!/usr/bin/env bash
# Get available speakers list via ListenHub API
# Usage: ./get-speakers.sh [--language zh|en]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib.sh"

LANGUAGE="zh"

while [ $# -gt 0 ]; do
  case "$1" in
    --language|--lang)
      LANGUAGE="${2:-}"
      shift 2
      ;;
    --help)
      echo "Usage: ./get-speakers.sh [--language zh|en]" >&2
      exit 0
      ;;
    *)
      echo "Error: Unknown argument $1" >&2
      echo "Usage: ./get-speakers.sh [--language zh|en]" >&2
      exit 1
      ;;
  esac
done

if [[ ! "$LANGUAGE" =~ ^(zh|en)$ ]]; then
  echo "Error: Invalid language '$LANGUAGE'. Must be: zh | en" >&2
  exit 1
fi

api_get "speakers/list?language=${LANGUAGE}"
