#!/usr/bin/env bash
set -euo pipefail

ID=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --id) ID="$2"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$ID" ]]; then
  echo '{"error": "Missing required argument: --id"}' >&2
  exit 1
fi

source "$(dirname "$0")/sign-request.sh"

via_curl DELETE "/v1/request/${ID}"
