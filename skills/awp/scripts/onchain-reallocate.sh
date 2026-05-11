#!/usr/bin/env bash
# On-chain reallocate stake between agent+subnet pairs (V2)
# V2 signature: reallocate(address staker, address fromAgent, uint256 fromSubnetId, address toAgent, uint256 toSubnetId, uint256 amount)
# The staker parameter is now explicit (first param). Caller must be staker or delegate.
# Usage: ./onchain-reallocate.sh --token <T> --from-agent <addr> --from-subnet <id> --to-agent <addr> --to-subnet <id> --amount <AWP_human>
# Requires ETH for gas.
set -euo pipefail

API_BASE="${AWP_API_URL:-https://tapi.awp.sh/api}"
TOKEN=""
FROM_AGENT=""
FROM_SUBNET=""
TO_AGENT=""
TO_SUBNET=""
AMOUNT=""
while [[ $# -gt 0 ]]; do
  case $1 in --token) TOKEN="$2"; shift 2 ;; --from-agent) FROM_AGENT="$2"; shift 2 ;; --from-subnet) FROM_SUBNET="$2"; shift 2 ;; --to-agent) TO_AGENT="$2"; shift 2 ;; --to-subnet) TO_SUBNET="$2"; shift 2 ;; --amount) AMOUNT="$2"; shift 2 ;; *) echo '{"error": "Unknown arg: '"$1"'"}' >&2; exit 1 ;; esac
done
[[ -z "$TOKEN" || -z "$FROM_AGENT" || -z "$FROM_SUBNET" || -z "$TO_AGENT" || -z "$TO_SUBNET" || -z "$AMOUNT" ]] && { echo '{"error": "Missing --token, --from-agent, --from-subnet, --to-agent, --to-subnet, --amount"}' >&2; exit 1; }
[[ "$FROM_AGENT" =~ ^0x[0-9a-fA-F]{40}$ ]] || { echo '{"error": "Invalid --from-agent address: must be 0x + 40 hex chars"}' >&2; exit 1; }
[[ "$TO_AGENT" =~ ^0x[0-9a-fA-F]{40}$ ]] || { echo '{"error": "Invalid --to-agent address: must be 0x + 40 hex chars"}' >&2; exit 1; }

# Pre-flight
WALLET_ADDR=$(awp-wallet status --token "$TOKEN" | jq -r '.address')
[[ -z "$WALLET_ADDR" || "$WALLET_ADDR" == "null" ]] && { echo '{"error": "Invalid token"}' >&2; exit 1; }

REGISTRY=$(curl -s "$API_BASE/registry")
AWP_REGISTRY=$(echo "$REGISTRY" | jq -r '.awpRegistry')
[[ -z "$AWP_REGISTRY" || "$AWP_REGISTRY" == "null" ]] && { echo '{"error": "Failed to get contract address from /registry"}' >&2; exit 1; }

# Validate numeric inputs (shell regex, no python injection risk)
[[ "$AMOUNT" =~ ^[0-9]+\.?[0-9]*$ && "$AMOUNT" != "0" && "$AMOUNT" != "0.0" && "$AMOUNT" != "0.00" ]] || { echo '{"error": "Invalid --amount: must be a positive number"}' >&2; exit 1; }
[[ "$FROM_SUBNET" =~ ^[0-9]+$ && "$FROM_SUBNET" -gt 0 ]] || { echo '{"error": "Invalid --from-subnet: must be > 0"}' >&2; exit 1; }
[[ "$TO_SUBNET" =~ ^[0-9]+$ && "$TO_SUBNET" -gt 0 ]] || { echo '{"error": "Invalid --to-subnet: must be > 0"}' >&2; exit 1; }

# Convert amount to wei
AMOUNT_WEI=$(python3 -c "print(int(float('$AMOUNT') * 10**18))")

# reallocate(address,address,uint256,address,uint256,uint256) selector = 0xd5d5278d
# params: staker (self), fromAgent, fromSubnetId, toAgent, toSubnetId, amount
STAKER_PADDED=$(python3 -c "print('${WALLET_ADDR#0x}'.lower().zfill(64))")
FROM_AGENT_PADDED=$(python3 -c "print('${FROM_AGENT#0x}'.lower().zfill(64))")
FROM_SUBNET_PADDED=$(python3 -c "print(hex($FROM_SUBNET)[2:].zfill(64))")
TO_AGENT_PADDED=$(python3 -c "print('${TO_AGENT#0x}'.lower().zfill(64))")
TO_SUBNET_PADDED=$(python3 -c "print(hex($TO_SUBNET)[2:].zfill(64))")
AMOUNT_PADDED=$(python3 -c "print(hex($AMOUNT_WEI)[2:].zfill(64))")

CALLDATA="0xd5d5278d${STAKER_PADDED}${FROM_AGENT_PADDED}${FROM_SUBNET_PADDED}${TO_AGENT_PADDED}${TO_SUBNET_PADDED}${AMOUNT_PADDED}"

echo '{"step": "reallocate", "staker": "'"$WALLET_ADDR"'", "fromAgent": "'"$FROM_AGENT"'", "fromSubnet": '"$FROM_SUBNET"', "toAgent": "'"$TO_AGENT"'", "toSubnet": '"$TO_SUBNET"', "amount": "'"$AMOUNT"' AWP"}' >&2
awp-wallet send --token "$TOKEN" --to "$AWP_REGISTRY" --data "$CALLDATA" --chain base
