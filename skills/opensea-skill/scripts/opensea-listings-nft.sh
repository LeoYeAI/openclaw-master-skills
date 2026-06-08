#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 3 ]; then
  echo "Usage: opensea-listings-nft.sh <chain> <contract_address> <token_id> [limit]" >&2
  echo "Example: opensea-listings-nft.sh ethereum 0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d 1234" >&2
  exit 1
fi

chain="$1"
contract="$2"
token_id="$3"
limit="${4:-50}"

"$(dirname "$0")/opensea-get.sh" "/api/v2/orders/${chain}/seaport/listings" "asset_contract_address=${contract}&token_ids=${token_id}&limit=${limit}"
