#!/usr/bin/env bash
# On-chain add AWP to an existing StakeNFT position
# Usage: ./onchain-add-position.sh --token <T> --position <tokenId> --amount <AWP_human> [--extend-days <days>]
# Requires ETH for gas. Handles remainingTime check + approve + addToPosition.
set -euo pipefail

API_BASE="${AWP_API_URL:-https://tapi.awp.sh/api}"
RPC_URL="${BASE_RPC_URL:-https://mainnet.base.org}"
TOKEN=""
POSITION=""
AMOUNT=""
EXTEND_DAYS="0"

while [[ $# -gt 0 ]]; do
  case $1 in
    --token) TOKEN="$2"; shift 2 ;;
    --position) POSITION="$2"; shift 2 ;;
    --amount) AMOUNT="$2"; shift 2 ;;
    --extend-days) EXTEND_DAYS="$2"; shift 2 ;;
    *) echo '{"error": "Unknown arg: '"$1"'"}' >&2; exit 1 ;;
  esac
done

[[ -z "$TOKEN" || -z "$POSITION" || -z "$AMOUNT" ]] && {
  echo '{"error": "Missing required: --token, --position, --amount"}' >&2; exit 1
}

# Validate inputs
[[ "$POSITION" =~ ^[1-9][0-9]*$ ]] || { echo '{"error": "Invalid --position: must be a positive integer"}' >&2; exit 1; }
[[ "$AMOUNT" =~ ^[0-9]+\.?[0-9]*$ && "$AMOUNT" != "0" && "$AMOUNT" != "0.0" && "$AMOUNT" != "0.00" ]] || { echo '{"error": "Invalid --amount: must be a positive number"}' >&2; exit 1; }
[[ "$EXTEND_DAYS" =~ ^[0-9]+\.?[0-9]*$ ]] || { echo '{"error": "Invalid --extend-days: must be a non-negative number"}' >&2; exit 1; }

# Helper: eth_call
eth_call() {
  local to="$1" data="$2"
  curl -s -X POST "$RPC_URL" -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"eth_call","params":[{"to":"'"$to"'","data":"'"$data"'"},"latest"],"id":1}' | jq -r '.result'
}

hex_to_dec() {
  local val="$1"
  [[ -z "$val" || "$val" == "null" || "$val" == "0x" ]] && { echo '{"error": "RPC returned empty/null value"}' >&2; exit 1; }
  python3 -c "print(int('$val', 16))"
}

# Pre-flight: wallet address
WALLET_ADDR=$(awp-wallet status --token "$TOKEN" | jq -r '.address')
[[ -z "$WALLET_ADDR" || "$WALLET_ADDR" == "null" ]] && { echo '{"error": "Invalid token"}' >&2; exit 1; }

# Fetch registry
REGISTRY=$(curl -s "$API_BASE/registry") || { echo '{"error": "Failed to fetch /registry"}' >&2; exit 1; }
echo "$REGISTRY" | jq -e '.awpToken' > /dev/null 2>&1 || { echo "$REGISTRY" >&2; exit 1; }
AWP_TOKEN=$(echo "$REGISTRY" | jq -r '.awpToken')
STAKE_NFT=$(echo "$REGISTRY" | jq -r '.stakeNFT')

# Pad tokenId to 32 bytes
TOKEN_ID_HEX=$(python3 -c "print(hex($POSITION)[2:].zfill(64))")

# Step 1: Check remainingTime(tokenId) — selector = keccak256("remainingTime(uint256)")[:4] = 0x0c64a7f2
REMAINING_HEX=$(eth_call "$STAKE_NFT" "0x0c64a7f2${TOKEN_ID_HEX}")
[[ -z "$REMAINING_HEX" || "$REMAINING_HEX" == "0x" || "$REMAINING_HEX" == "null" ]] && {
  echo '{"error": "remainingTime() call failed — position may not exist"}' >&2; exit 1
}
REMAINING=$(hex_to_dec "$REMAINING_HEX")
[[ "$REMAINING" -eq 0 ]] && {
  echo '{"error": "PositionExpired: position '"$POSITION"' lock has expired (remainingTime=0). Cannot add to an expired position."}' >&2; exit 1
}

# Step 2: Fetch current lockEndTime from positions(tokenId)
# positions(uint256) returns (uint128 amount, uint64 lockEndTime, uint64 createdAt)
# selector = keccak256("positions(uint256)")[:4] = 0x99fbab88
POSITIONS_HEX=$(eth_call "$STAKE_NFT" "0x99fbab88${TOKEN_ID_HEX}")
[[ -z "$POSITIONS_HEX" || "$POSITIONS_HEX" == "0x" || "$POSITIONS_HEX" == "null" ]] && {
  echo '{"error": "positions() call failed"}' >&2; exit 1
}
# Return is 3 words (96 bytes): amount(uint128 padded to 32), lockEndTime(uint64 padded to 32), createdAt(uint64 padded to 32)
CURRENT_LOCK_END=$(python3 -c "
data = '${POSITIONS_HEX#0x}'
# word 1 = lockEndTime (offset 64..128)
lock_end = int(data[64:128], 16)
print(lock_end)
")

# Step 3: Compute newLockEndTime
NOW=$(date +%s)
NEW_LOCK_END=$(python3 -c "
import math
extend_days = float('$EXTEND_DAYS')
current_lock_end = $CURRENT_LOCK_END
now = $NOW
if extend_days > 0:
    candidate = now + int(extend_days * 86400)
    new_lock_end = max(current_lock_end, candidate)
else:
    new_lock_end = current_lock_end
print(new_lock_end)
")

# Verify newLockEndTime >= currentLockEndTime (contract requirement)
python3 -c "
new = $NEW_LOCK_END
cur = $CURRENT_LOCK_END
if new < cur:
    import sys
    print('{\"error\": \"newLockEndTime (' + str(new) + ') < currentLockEndTime (' + str(cur) + '). Contract requires newLockEndTime >= currentLockEndTime.\"}', file=sys.stderr)
    sys.exit(1)
"

# Convert amount to wei
AMOUNT_WEI=$(python3 -c "print(int(float('$AMOUNT') * 10**18))")

# Step 4: Approve AWP to StakeNFT
echo '{"step": "approve", "spender": "'"$STAKE_NFT"'", "amount": "'"$AMOUNT"' AWP"}' >&2
awp-wallet approve --token "$TOKEN" --asset "$AWP_TOKEN" --spender "$STAKE_NFT" --amount "$AMOUNT" --chain base

# Step 5: Build calldata for addToPosition(uint256 tokenId, uint256 amount, uint64 newLockEndTime)
# selector = keccak256("addToPosition(uint256,uint256,uint64)")[:4] = 0xd2845e7d
ADD_DATA=$(python3 -c "
token_id = $POSITION
amount_wei = $AMOUNT_WEI
new_lock_end = $NEW_LOCK_END
selector = '0xd2845e7d'
calldata = selector + hex(token_id)[2:].zfill(64) + hex(amount_wei)[2:].zfill(64) + hex(new_lock_end)[2:].zfill(64)
print(calldata)
")

echo '{"step": "addToPosition", "tokenId": '"$POSITION"', "amount_wei": "'"$AMOUNT_WEI"'", "newLockEndTime": '"$NEW_LOCK_END"', "remainingTime": '"$REMAINING"'}' >&2
awp-wallet send --token "$TOKEN" --to "$STAKE_NFT" --data "$ADD_DATA" --chain base
