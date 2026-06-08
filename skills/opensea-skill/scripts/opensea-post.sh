#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: opensea-post.sh <path> <json_body>" >&2
  echo "Example: opensea-post.sh /api/v2/listings/fulfillment_data '{\"listing\":{...}}'" >&2
  exit 1
fi

path="$1"
body="$2"
base="${OPENSEA_BASE_URL:-https://api.opensea.io}"
key="${OPENSEA_API_KEY:-}"

if [ -z "$key" ]; then
  echo "OPENSEA_API_KEY is required" >&2
  exit 1
fi

url="$base$path"

curl -sS -X POST \
  -H "x-api-key: $key" \
  -H "Content-Type: application/json" \
  -d "$body" \
  "$url"
