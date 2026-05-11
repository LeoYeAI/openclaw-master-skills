#!/usr/bin/env bash
# On-chain allocate stake to agent+subnet (V2)
# V2 signature: allocate(address staker, address agent, uint256 subnetId, uint256 amount)
# The staker parameter is now explicit (first param). Caller must be staker or delegate.
# Usage: ./onchain-allocate.sh --token <T> --agent <addr> --subnet <id> --amount <AWP_human>
# Requires ETH for gas.
set -euo pipefail

API_BASE="${AWP_API_URL:-https://tapi.awp.sh/api}"
TOKEN=""
AGENT=""
SUBNET=""
AMOUNT=""
while [[ $# -gt 0 ]]; do
  case $1 in --token) TOKEN="$2"; shift 2 ;; --agent) AGENT="$2"; shift 2 ;; --subnet) SUBNET="$2"; shift 2 ;; --amount) AMOUNT="$2"; shift 2 ;; *) echo '{"error": "Unknown arg: '"$1"'"}' >&2; exit 1 ;; esac
done
[[ -z "$TOKEN" || -z "$AGENT" || -z "$SUBNET" || -z "$AMOUNT" ]] && { echo '{"error": "Missing --token, --agent, --subnet, --amount"}' >&2; exit 1; }
[[ "$AGENT" =~ ^0x[0-9a-fA-F]{40}$ ]] || { echo '{"error": "Invalid --agent address: must be 0x + 40 hex chars"}' >&2; exit 1; }

# Pre-flight
WALLET_ADDR=$(awp-wallet status --token "$TOKEN" | jq -r '.address')
[[ -z "$WALLET_ADDR" || "$WALLET_ADDR" == "null" ]] && { echo '{"error": "Invalid token"}' >&2; exit 1; }

REGISTRY=$(curl -s "$API_BASE/registry")
AWP_REGISTRY=$(echo "$REGISTRY" | jq -r '.awpRegistry')
[[ -z "$AWP_REGISTRY" || "$AWP_REGISTRY" == "null" ]] && { echo '{"error": "Failed to get contract address from /registry"}' >&2; exit 1; }

# Validate numeric inputs (shell regex, no python injection risk)
[[ "$AMOUNT" =~ ^[0-9]+\.?[0-9]*$ && "$AMOUNT" != "0" && "$AMOUNT" != "0.0" && "$AMOUNT" != "0.00" ]] || { echo '{"error": "Invalid --amount: must be a positive number"}' >&2; exit 1; }
[[ "$SUBNET" =~ ^[0-9]+$ && "$SUBNET" -gt 0 ]] || { echo '{"error": "Invalid --subnet: must be a positive integer > 0"}' >&2; exit 1; }

# Check unallocated balance
BALANCE=$(curl -s "$API_BASE/staking/user/$WALLET_ADDR/balance")
UNALLOCATED=$(echo "$BALANCE" | jq -r '.unallocated')
[[ -z "$UNALLOCATED" || "$UNALLOCATED" == "null" ]] && { echo '{"error": "Could not fetch balance — check address"}' >&2; exit 1; }
AMOUNT_WEI=$(python3 -c "print(int(float('$AMOUNT') * 10**18))")

python3 -c "
unalloc = int('$UNALLOCATED')
needed = $AMOUNT_WEI
if needed > unalloc:
    import sys
    print('{\"error\": \"Insufficient unallocated balance: have ' + str(unalloc/10**18) + ' AWP, need $AMOUNT AWP\"}', file=sys.stderr)
    sys.exit(1)
" || exit 1

# allocate(address,address,uint256,uint256) selector = 0xd035a9a7
# params: staker (self), agent, subnetId, amount
STAKER_PADDED=$(python3 -c "print('${WALLET_ADDR#0x}'.lower().zfill(64))")
AGENT_PADDED=$(python3 -c "print('${AGENT#0x}'.lower().zfill(64))")
SUBNET_PADDED=$(python3 -c "print(hex($SUBNET)[2:].zfill(64))")
AMOUNT_PADDED=$(python3 -c "print(hex($AMOUNT_WEI)[2:].zfill(64))")

CALLDATA="0xd035a9a7${STAKER_PADDED}${AGENT_PADDED}${SUBNET_PADDED}${AMOUNT_PADDED}"

echo '{"step": "allocate", "staker": "'"$WALLET_ADDR"'", "agent": "'"$AGENT"'", "subnet": '"$SUBNET"', "amount": "'"$AMOUNT"' AWP"}' >&2
awp-wallet send --token "$TOKEN" --to "$AWP_REGISTRY" --data "$CALLDATA" --chain base
