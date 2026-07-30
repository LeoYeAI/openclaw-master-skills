#!/usr/bin/env bash
set -euo pipefail

DID=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --did) DID="$2"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$DID" ]]; then
  echo '{"error": "Missing required argument: --did"}' >&2
  exit 1
fi

source "$(dirname "$0")/sign-request.sh"

ENCODED_DID=$(printf '%s' "$DID" | jq -sRr @uri)

via_curl GET "/v1/via/dids/${ENCODED_DID}"
