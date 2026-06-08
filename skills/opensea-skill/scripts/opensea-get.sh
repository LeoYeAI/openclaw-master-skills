#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: opensea-get.sh <path> [query]" >&2
  echo "Example: opensea-get.sh /api/v2/collections/cool-cats-nft" >&2
  exit 1
fi

path="$1"
query="${2-}"
base="${OPENSEA_BASE_URL:-https://api.opensea.io}"
key="${OPENSEA_API_KEY:-}"

if [ -z "$key" ]; then
  echo "OPENSEA_API_KEY is required" >&2
  exit 1
fi

url="$base$path"
if [ -n "$query" ]; then
  url="$url?$query"
fi

curl -sS -H "x-api-key: $key" "$url"
