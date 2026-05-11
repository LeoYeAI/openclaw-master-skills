#!/usr/bin/env bash
# One-click registerAndStake: register + deposit + allocate in a single tx
# Usage: ./onchain-register-and-stake.sh --token <T> --amount <AWP_human> --lock-days <days> --agent <address> --subnet <id> --allocate-amount <AWP_human>
# Requires ETH for gas. Handles approve (to AWP_REGISTRY) + registerAndStake in sequence.
set -euo pipefail

API_BASE="${AWP_API_URL:-https://tapi.awp.sh/api}"
TOKEN=""
AMOUNT=""
LOCK_DAYS=""
AGENT=""
SUBNET=""
ALLOCATE_AMOUNT=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --token) TOKEN="$2"; shift 2 ;;
    --amount) AMOUNT="$2"; shift 2 ;;
    --lock-days) LOCK_DAYS="$2"; shift 2 ;;
    --agent) AGENT="$2"; shift 2 ;;
    --subnet) SUBNET="$2"; shift 2 ;;
    --allocate-amount) ALLOCATE_AMOUNT="$2"; shift 2 ;;
    *) echo '{"error": "Unknown arg: '"$1"'"}' >&2; exit 1 ;;
  esac
done
[[ -z "$TOKEN" || -z "$AMOUNT" || -z "$LOCK_DAYS" || -z "$AGENT" || -z "$SUBNET" || -z "$ALLOCATE_AMOUNT" ]] && \
  { echo '{"error": "Missing required flags: --token, --amount, --lock-days, --agent, --subnet, --allocate-amount"}' >&2; exit 1; }

# Validate numeric inputs (shell regex, no python3 injection risk)
[[ "$AMOUNT" =~ ^[0-9]+\.?[0-9]*$ && "$AMOUNT" != "0" && "$AMOUNT" != "0.0" && "$AMOUNT" != "0.00" ]] || { echo '{"error": "Invalid --amount: must be a positive number"}' >&2; exit 1; }
[[ "$LOCK_DAYS" =~ ^[0-9]+\.?[0-9]*$ ]] || { echo '{"error": "Invalid --lock-days: must be a positive number"}' >&2; exit 1; }
[[ "$ALLOCATE_AMOUNT" =~ ^[0-9]+\.?[0-9]*$ ]] || { echo '{"error": "Invalid --allocate-amount: must be a positive number"}' >&2; exit 1; }
[[ "$AGENT" =~ ^0x[0-9a-fA-F]{40}$ ]] || { echo '{"error": "Invalid --agent: must be 0x + 40 hex chars"}' >&2; exit 1; }
[[ "$SUBNET" =~ ^[0-9]+$ ]] && [[ "$SUBNET" -gt 0 ]] || { echo '{"error": "Invalid --subnet: must be a positive integer"}' >&2; exit 1; }

# Pre-flight: fetch wallet address
WALLET_ADDR=$(awp-wallet status --token "$TOKEN" | jq -r '.address')
[[ -z "$WALLET_ADDR" || "$WALLET_ADDR" == "null" ]] && { echo '{"error": "Invalid token"}' >&2; exit 1; }

# Fetch registry addresses
REGISTRY=$(curl -s "$API_BASE/registry")
AWP_TOKEN=$(echo "$REGISTRY" | jq -r '.awpToken')
AWP_REGISTRY=$(echo "$REGISTRY" | jq -r '.awpRegistry')
[[ -z "$AWP_REGISTRY" || "$AWP_REGISTRY" == "null" ]] && { echo '{"error": "Failed to get contract address from /registry"}' >&2; exit 1; }

# Convert units: human-readable amounts to wei, days to seconds
AMOUNT_WEI=$(python3 -c "print(int(float('$AMOUNT') * 10**18))")
LOCK_SECONDS=$(python3 -c "print(int(float('$LOCK_DAYS') * 86400))")
ALLOCATE_WEI=$(python3 -c "print(int(float('$ALLOCATE_AMOUNT') * 10**18))")

# Step 1: Approve AWP to AWP_REGISTRY (NOT StakeNFT — registerAndStake pulls tokens via AWPRegistry)
echo '{"step": "approve", "spender": "'"$AWP_REGISTRY"'", "note": "Approve target is AWP_REGISTRY, NOT StakeNFT", "amount": "'"$AMOUNT"' AWP"}' >&2
awp-wallet approve --token "$TOKEN" --asset "$AWP_TOKEN" --spender "$AWP_REGISTRY" --amount "$AMOUNT" --chain base

# Step 2: registerAndStake(uint256 depositAmount, uint64 lockDuration, address agent, uint256 subnetId, uint256 allocateAmount)
# selector = keccak256("registerAndStake(uint256,uint64,address,uint256,uint256)")[:4] = 0x34426564
# ABI encoding: 5 params, each 32-byte padded (address left-padded, uint64 left-padded to 32 bytes)
CALLDATA=$(python3 -c "
selector = '0x34426564'
deposit_amount = int('$AMOUNT_WEI')
lock_duration = int('$LOCK_SECONDS')
agent = '$AGENT'.lower().replace('0x', '')
subnet_id = int('$SUBNET')
allocate_amount = int('$ALLOCATE_WEI')
print(selector
    + hex(deposit_amount)[2:].zfill(64)
    + hex(lock_duration)[2:].zfill(64)
    + agent.zfill(64)
    + hex(subnet_id)[2:].zfill(64)
    + hex(allocate_amount)[2:].zfill(64))
")

echo '{"step": "registerAndStake", "to": "'"$AWP_REGISTRY"'", "deposit_amount_wei": "'"$AMOUNT_WEI"'", "lock_seconds": '"$LOCK_SECONDS"', "agent": "'"$AGENT"'", "subnet": '"$SUBNET"', "allocate_amount_wei": "'"$ALLOCATE_WEI"'"}' >&2
awp-wallet send --token "$TOKEN" --to "$AWP_REGISTRY" --data "$CALLDATA" --chain base
