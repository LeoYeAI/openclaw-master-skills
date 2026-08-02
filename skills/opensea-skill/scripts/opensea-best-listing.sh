#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "Usage: opensea-best-listing.sh <collection_slug> <token_id>" >&2
  echo "Example: opensea-best-listing.sh boredapeyachtclub 1234" >&2
  exit 1
fi

slug="$1"
token_id="$2"

"$(dirname "$0")/opensea-get.sh" "/api/v2/listings/collection/${slug}/nfts/${token_id}/best"
