#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: opensea-account-nfts.sh <chain> <wallet_address> [limit] [next]" >&2
  exit 1
fi

chain="$1"
address="$2"
limit="${3-}"
next="${4-}"

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

"$(dirname "$0")/opensea-get.sh" "/api/v2/chain/${chain}/account/${address}/nfts" "$query"
