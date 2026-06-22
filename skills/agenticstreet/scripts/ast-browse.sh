#!/bin/bash
# Browse funds or check fund details
# Usage: ast-browse.sh                    → list all funds
#        ast-browse.sh <vault_address>    → show fund stats
#        ast-browse.sh terms <vault_addr> → show fund terms

API_URL="${AST_API_URL:-https://agenticstreet.ai/api}"

if [ -z "$1" ]; then
  curl -s "$API_URL/funds" | jq '.'
elif [ "$1" = "terms" ]; then
  curl -s "$API_URL/funds/$2/terms" | jq '.'
else
  curl -s "$API_URL/funds/$1/stats" | jq '.'
fi
