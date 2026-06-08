#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: opensea-events-collection.sh <collection_slug> [event_type] [limit] [next]" >&2
  exit 1
fi

slug="$1"
event_type="${2-}"
limit="${3-}"
next="${4-}"

query=""
if [ -n "$event_type" ]; then
  query="event_type=$event_type"
fi
if [ -n "$limit" ]; then
  if [ -n "$query" ]; then
    query="$query&limit=$limit"
  else
    query="limit=$limit"
  fi
fi
if [ -n "$next" ]; then
  if [ -n "$query" ]; then
    query="$query&next=$next"
  else
    query="next=$next"
  fi
fi

"$(dirname "$0")/opensea-get.sh" "/api/v2/events/collection/${slug}" "$query"
