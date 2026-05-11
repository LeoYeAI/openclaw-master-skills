#!/usr/bin/env bash
# On-chain bind(address target) — bind to a target in the account tree (V2)
# Usage: ./onchain-bind.sh --token <session_token> --target <address>
# Requires ETH for gas. Tree-based binding with anti-cycle check.
set -euo pipefail

API_BASE="${AWP_API_URL:-https://tapi.awp.sh/api}"
TOKEN=""
TARGET=""
while [[ $# -gt 0 ]]; do
  case $1 in --token) TOKEN="$2"; shift 2 ;; --target) TARGET="$2"; shift 2 ;; --principal) TARGET="$2"; shift 2 ;; *) echo '{"error": "Unknown arg: '"$1"'"}' >&2; exit 1 ;; esac
done
[[ -z "$TOKEN" ]] && { echo '{"error": "Missing --token"}' >&2; exit 1; }
[[ -z "$TARGET" ]] && { echo '{"error": "Missing --target"}' >&2; exit 1; }
[[ "$TARGET" =~ ^0x[0-9a-fA-F]{40}$ ]] || { echo '{"error": "Invalid --target address: must be 0x + 40 hex chars"}' >&2; exit 1; }

# Pre-flight
WALLET_ADDR=$(awp-wallet status --token "$TOKEN" | jq -r '.address')
[[ -z "$WALLET_ADDR" || "$WALLET_ADDR" == "null" ]] && { echo '{"error": "Invalid token"}' >&2; exit 1; }

REGISTRY=$(curl -s "$API_BASE/registry")
AWP_REGISTRY=$(echo "$REGISTRY" | jq -r '.awpRegistry')
[[ -z "$AWP_REGISTRY" || "$AWP_REGISTRY" == "null" ]] && { echo '{"error": "Failed to get contract address from /registry"}' >&2; exit 1; }

CHECK=$(curl -s "$API_BASE/address/$WALLET_ADDR/check")
# V2: .boundTo field; V1: .isRegisteredAgent + .ownerAddress
BOUND_TO=$(echo "$CHECK" | jq -r '.boundTo // empty' 2>/dev/null)
IS_AGENT=$(echo "$CHECK" | jq -r '.isRegisteredAgent // false' 2>/dev/null)
[[ "$IS_AGENT" == "true" ]] && BOUND_TO=$(echo "$CHECK" | jq -r '.ownerAddress // empty' 2>/dev/null)
[[ "$BOUND_TO" != "" && "$BOUND_TO" != "null" && "$BOUND_TO" != "0x0000000000000000000000000000000000000000" ]] && {
  echo '{"status": "already_bound", "address": "'"$WALLET_ADDR"'", "boundTo": "'"$BOUND_TO"'"}'; exit 0
}

# bind(address) selector = 0x81bac14f + ABI-encoded address
ADDR_PADDED=$(python3 -c "print('${TARGET#0x}'.lower().zfill(64))")
awp-wallet send --token "$TOKEN" --to "$AWP_REGISTRY" --data "0x81bac14f${ADDR_PADDED}" --chain base
