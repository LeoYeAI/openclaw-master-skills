#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 3 ]; then
  echo "Usage: opensea-nft.sh <chain> <contract_address> <token_id>" >&2
  exit 1
fi

chain="$1"
contract="$2"
token_id="$3"

"$(dirname "$0")/opensea-get.sh" "/api/v2/chain/${chain}/contract/${contract}/nfts/${token_id}"
