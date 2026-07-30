#!/usr/bin/env bash
set -euo pipefail

CONTACT=""
DID=""
INTERNAL_ID=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --contact) CONTACT="$2"; shift 2 ;;
    --did) DID="$2"; shift 2 ;;
    --internal-id) INTERNAL_ID="$2"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$CONTACT" && -z "$DID" && -z "$INTERNAL_ID" ]]; then
  echo '{"error": "Missing required argument: --contact, --did, or --internal-id"}' >&2
  exit 1
fi

source "$(dirname "$0")/sign-request.sh"

QUERY=""
if [[ -n "$CONTACT" ]]; then
  QUERY="contact=$(printf '%s' "$CONTACT" | jq -sRr @uri)"
elif [[ -n "$DID" ]]; then
  QUERY="did=$(printf '%s' "$DID" | jq -sRr @uri)"
elif [[ -n "$INTERNAL_ID" ]]; then
  QUERY="internalId=$(printf '%s' "$INTERNAL_ID" | jq -sRr @uri)"
fi

via_curl GET "/v1/user?${QUERY}"
