#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: opensea-offers-collection.sh <collection_slug> [limit] [next]" >&2
  exit 1
fi

slug="$1"
limit="${2-}"
next="${3-}"

query=""
if [ -n "$limit" ]; then
  query="limit=$limit"
fi
if [ -n "$next" ]; then
  if [ -n "$query" ]; then
    query="$query&next=$next"
  else
    query="next=$next"
  fi
fi

"$(dirname "$0")/opensea-get.sh" "/api/v2/offers/collection/${slug}/all" "$query"
