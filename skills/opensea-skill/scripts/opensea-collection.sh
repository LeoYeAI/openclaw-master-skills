#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: opensea-collection.sh <collection_slug>" >&2
  exit 1
fi

slug="$1"

"$(dirname "$0")/opensea-get.sh" "/api/v2/collections/${slug}"
