#!/usr/bin/env bash
# On-chain register() — optional explicit registration (V2)
# In V2, register() is equivalent to setRecipient(msg.sender).
# Every address is implicitly a root; calling register() just explicitly
# sets your recipient to yourself.
# Usage: ./onchain-register.sh --token <session_token>
# Requires ETH for gas.
set -euo pipefail

API_BASE="${AWP_API_URL:-https://tapi.awp.sh/api}"
TOKEN=""
while [[ $# -gt 0 ]]; do
  case $1 in --token) TOKEN="$2"; shift 2 ;; *) echo '{"error": "Unknown arg: '"$1"'"}' >&2; exit 1 ;; esac
done
[[ -z "$TOKEN" ]] && { echo '{"error": "Missing --token"}' >&2; exit 1; }

# Pre-flight
WALLET_ADDR=$(awp-wallet status --token "$TOKEN" | jq -r '.address')
[[ -z "$WALLET_ADDR" || "$WALLET_ADDR" == "null" ]] && { echo '{"error": "Invalid token"}' >&2; exit 1; }

REGISTRY=$(curl -s "$API_BASE/registry")
AWP_REGISTRY=$(echo "$REGISTRY" | jq -r '.awpRegistry')
[[ -z "$AWP_REGISTRY" || "$AWP_REGISTRY" == "null" ]] && { echo '{"error": "Failed to get contract address from /registry"}' >&2; exit 1; }

CHECK=$(curl -s "$API_BASE/address/$WALLET_ADDR/check")
# V2: .isRegistered; V1: .isRegisteredUser
IS_REGISTERED=$(echo "$CHECK" | jq -r '.isRegistered // empty' 2>/dev/null)
[[ -z "$IS_REGISTERED" || "$IS_REGISTERED" == "null" ]] && IS_REGISTERED=$(echo "$CHECK" | jq -r '.isRegisteredUser // "false"' 2>/dev/null)
RECIPIENT=$(echo "$CHECK" | jq -r '.recipient // empty' 2>/dev/null)
[[ "$IS_REGISTERED" == "true" ]] && { echo '{"status": "already_registered", "address": "'"$WALLET_ADDR"'", "recipient": "'"$RECIPIENT"'"}'; exit 0; }

# register() selector = 0x1aa3a008
awp-wallet send --token "$TOKEN" --to "$AWP_REGISTRY" --data "0x1aa3a008" --chain base
