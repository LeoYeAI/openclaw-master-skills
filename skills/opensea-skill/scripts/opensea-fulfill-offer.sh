#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 5 ]; then
  echo "Usage: opensea-fulfill-offer.sh <chain> <order_hash> <fulfiller_address> <contract_address> <token_id>" >&2
  echo "Returns transaction data to execute on-chain to accept an offer (sell NFT)" >&2
  echo "Example: opensea-fulfill-offer.sh ethereum 0x1234... 0xYourWallet 0xContract 5678" >&2
  exit 1
fi

chain="$1"
order_hash="$2"
fulfiller="$3"
contract="$4"
token_id="$5"
protocol="0x0000000000000068f116a894984e2db1123eb395"

body=$(cat <<EOF
{
  "offer": {
    "hash": "$order_hash",
    "chain": "$chain",
    "protocol_address": "$protocol"
  },
  "fulfiller": {
    "address": "$fulfiller"
  },
  "consideration": {
    "asset_contract_address": "$contract",
    "token_id": "$token_id"
  }
}
EOF
)

"$(dirname "$0")/opensea-post.sh" "/api/v2/offers/fulfillment_data" "$body"
