#!/usr/bin/env bash
# On-chain deposit AWP to StakeNFT (V2)
# Usage: ./onchain-deposit.sh --token <T> --amount <AWP_human> --lock-days <days>
# Requires ETH for gas. Handles approve + deposit in sequence.
set -euo pipefail

API_BASE="${AWP_API_URL:-https://tapi.awp.sh/api}"
TOKEN=""
AMOUNT=""
LOCK_DAYS=""
while [[ $# -gt 0 ]]; do
  case $1 in --token) TOKEN="$2"; shift 2 ;; --amount) AMOUNT="$2"; shift 2 ;; --lock-days) LOCK_DAYS="$2"; shift 2 ;; *) echo '{"error": "Unknown arg: '"$1"'"}' >&2; exit 1 ;; esac
done
[[ -z "$TOKEN" || -z "$AMOUNT" || -z "$LOCK_DAYS" ]] && { echo '{"error": "Missing --token, --amount, --lock-days"}' >&2; exit 1; }

# Validate numeric inputs BEFORE any on-chain calls (shell regex, no python injection risk)
[[ "$AMOUNT" =~ ^[0-9]+\.?[0-9]*$ && "$AMOUNT" != "0" && "$AMOUNT" != "0.0" && "$AMOUNT" != "0.00" ]] || { echo '{"error": "Invalid --amount: must be a positive number"}' >&2; exit 1; }
[[ "$LOCK_DAYS" =~ ^[0-9]+\.?[0-9]*$ ]] || { echo '{"error": "Invalid --lock-days: must be a positive number"}' >&2; exit 1; }

# Pre-flight
WALLET_ADDR=$(awp-wallet status --token "$TOKEN" | jq -r '.address')
[[ -z "$WALLET_ADDR" || "$WALLET_ADDR" == "null" ]] && { echo '{"error": "Invalid token"}' >&2; exit 1; }

REGISTRY=$(curl -s "$API_BASE/registry")
AWP_TOKEN=$(echo "$REGISTRY" | jq -r '.awpToken')
STAKE_NFT=$(echo "$REGISTRY" | jq -r '.stakeNFT')
[[ -z "$STAKE_NFT" || "$STAKE_NFT" == "null" ]] && { echo '{"error": "Failed to get stakeNFT from /registry"}' >&2; exit 1; }

AMOUNT_WEI=$(python3 -c "print(int(float('$AMOUNT') * 10**18))")
LOCK_SECONDS=$(python3 -c "print(int(float('$LOCK_DAYS') * 86400))")

# Step 1: Approve AWP to StakeNFT
echo '{"step": "approve", "spender": "'"$STAKE_NFT"'", "amount": "'"$AMOUNT"' AWP"}' >&2
awp-wallet approve --token "$TOKEN" --asset "$AWP_TOKEN" --spender "$STAKE_NFT" --amount "$AMOUNT" --chain base

# Step 2: Deposit
# deposit(uint256,uint64) selector = 0x7d552ea6
DEPOSIT_DATA=$(python3 -c "print('0x7d552ea6' + hex($AMOUNT_WEI)[2:].zfill(64) + hex($LOCK_SECONDS)[2:].zfill(64))")

echo '{"step": "deposit", "amount_wei": "'"$AMOUNT_WEI"'", "lock_seconds": '"$LOCK_SECONDS"'}' >&2
awp-wallet send --token "$TOKEN" --to "$STAKE_NFT" --data "$DEPOSIT_DATA" --chain base
