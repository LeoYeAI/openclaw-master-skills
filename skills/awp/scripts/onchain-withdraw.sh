#!/usr/bin/env bash
# On-chain withdraw from expired StakeNFT position (V2)
# withdraw(uint256 tokenId) — burns the position NFT, returns AWP
# Usage: ./onchain-withdraw.sh --token <T> --position <tokenId>
# Requires ETH for gas. Only callable when lock has expired (remainingTime == 0).
set -euo pipefail

API_BASE="${AWP_API_URL:-https://tapi.awp.sh/api}"
RPC_URL="${BASE_RPC_URL:-https://mainnet.base.org}"
TOKEN=""
POSITION=""
while [[ $# -gt 0 ]]; do
  case $1 in --token) TOKEN="$2"; shift 2 ;; --position) POSITION="$2"; shift 2 ;; --rpc) RPC_URL="$2"; shift 2 ;; *) echo '{"error": "Unknown arg: '"$1"'"}' >&2; exit 1 ;; esac
done
[[ -z "$TOKEN" || -z "$POSITION" ]] && { echo '{"error": "Missing --token, --position"}' >&2; exit 1; }
[[ "$POSITION" =~ ^[1-9][0-9]*$ ]] || { echo '{"error": "Invalid --position: must be a positive integer"}' >&2; exit 1; }

eth_call() {
  local to="$1" data="$2"
  curl -s -X POST "$RPC_URL" -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"eth_call","params":[{"to":"'"$to"'","data":"'"$data"'"},"latest"],"id":1}' | jq -r '.result'
}

# Pre-flight
WALLET_ADDR=$(awp-wallet status --token "$TOKEN" | jq -r '.address')
[[ -z "$WALLET_ADDR" || "$WALLET_ADDR" == "null" ]] && { echo '{"error": "Invalid token"}' >&2; exit 1; }

REGISTRY=$(curl -s "$API_BASE/registry")
STAKE_NFT=$(echo "$REGISTRY" | jq -r '.stakeNFT')
[[ -z "$STAKE_NFT" || "$STAKE_NFT" == "null" ]] && { echo '{"error": "Failed to get stakeNFT from /registry"}' >&2; exit 1; }

# Check remainingTime(tokenId) — selector = 0x0c64a7f2 (keccak256("remainingTime(uint256)")[:4])
POSITION_PADDED=$(python3 -c "print(hex($POSITION)[2:].zfill(64))")

# remainingTime(uint256) selector = 0x0c64a7f2 (hardcoded, no web3 dependency)
REMAINING_HEX=$(eth_call "$STAKE_NFT" "0x0c64a7f2${POSITION_PADDED}")
[[ -z "$REMAINING_HEX" || "$REMAINING_HEX" == "0x" || "$REMAINING_HEX" == "null" ]] && {
  echo '{"error": "Could not fetch remainingTime — is the position ID valid?"}' >&2; exit 1
}
REMAINING=$(python3 -c "print(int('$REMAINING_HEX', 16))")

[[ "$REMAINING" != "0" ]] && {
  DAYS_LEFT=$(python3 -c "print(round($REMAINING / 86400, 1))")
  echo '{"error": "Position #'"$POSITION"' still locked — '"$DAYS_LEFT"' days remaining. Cannot withdraw yet."}' >&2
  exit 1
}

# withdraw(uint256) selector = 0x2e1a7d4d
CALLDATA="0x2e1a7d4d${POSITION_PADDED}"

echo '{"step": "withdraw", "position": '"$POSITION"', "target": "'"$STAKE_NFT"'"}' >&2
awp-wallet send --token "$TOKEN" --to "$STAKE_NFT" --data "$CALLDATA" --chain base
