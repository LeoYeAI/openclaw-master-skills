#!/usr/bin/env bash
# AWP Gasless onboarding — register or bind via relay
#
# Usage:
#   Principal mode (register / set recipient to self):
#     ./relay-start.sh --token <session_token> --mode principal
#
#   Agent mode (bind to a target address):
#     ./relay-start.sh --token <session_token> --mode agent --target <address>
#
# Nonce: fetched from GET /api/nonce/{address}
# EIP-712 domain: fetched from GET /api/registry → eip712Domain
# Signature: 65 bytes (r[32]+s[32]+v[1]), hex with 0x prefix = 132 chars
#
# Prerequisites: awp-wallet (unlocked), curl, jq

set -euo pipefail

API_BASE="${AWP_API_URL:-https://tapi.awp.sh/api}"
TOKEN=""
MODE=""
TARGET=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --token) TOKEN="$2"; shift 2 ;;
    --mode) MODE="$2"; shift 2 ;;
    --target) TARGET="$2"; shift 2 ;;
    --principal) MODE="principal"; shift 1 ;;
    --api) API_BASE="$2"; shift 2 ;;
    *) echo '{"error": "Unknown arg: '"$1"'"}' >&2; exit 1 ;;
  esac
done

[[ -z "$TOKEN" ]] && { echo '{"error": "Missing --token"}' >&2; exit 1; }
[[ -z "$MODE" ]] && { echo '{"error": "Missing --mode (principal or agent)"}' >&2; exit 1; }
[[ "$MODE" != "principal" && "$MODE" != "agent" ]] && { echo '{"error": "--mode must be principal or agent"}' >&2; exit 1; }
[[ "$MODE" == "agent" && -z "$TARGET" ]] && { echo '{"error": "Agent mode requires --target <address>"}' >&2; exit 1; }
[[ -n "$TARGET" && ! "$TARGET" =~ ^0x[0-9a-fA-F]{40}$ ]] && { echo '{"error": "Invalid --target: must be 0x + 40 hex chars"}' >&2; exit 1; }

# Step 1: Fetch registry + eip712Domain
REGISTRY=$(curl -s "$API_BASE/registry") || { echo '{"error": "Failed to fetch /registry"}' >&2; exit 1; }

# Read eip712Domain from registry (new V2 API)
EIP712_NAME=$(echo "$REGISTRY" | jq -r '.eip712Domain.name // empty')
EIP712_VERSION=$(echo "$REGISTRY" | jq -r '.eip712Domain.version // empty')
EIP712_CHAIN_ID=$(echo "$REGISTRY" | jq -r '.eip712Domain.chainId // empty')
EIP712_CONTRACT=$(echo "$REGISTRY" | jq -r '.eip712Domain.verifyingContract // empty')

# Fallback: if eip712Domain not present, construct from registry fields
if [[ -z "$EIP712_NAME" || "$EIP712_NAME" == "null" ]]; then
  EIP712_CONTRACT=$(echo "$REGISTRY" | jq -r '.awpRegistry')
  [[ -z "$EIP712_CONTRACT" || "$EIP712_CONTRACT" == "null" ]] && { echo '{"error": "Cannot determine contract address from /registry"}' >&2; exit 1; }
  EIP712_CHAIN_ID=$(echo "$REGISTRY" | jq -r '.chainId // empty')
  [[ -z "$EIP712_CHAIN_ID" || "$EIP712_CHAIN_ID" == "null" ]] && { echo '{"error": "Cannot determine chainId from /registry"}' >&2; exit 1; }
  EIP712_NAME="AWPRegistry"
  EIP712_VERSION="1"
  echo '{"info": "eip712Domain not in registry, using fallback"}' >&2
fi

echo '{"info": "domain: '"$EIP712_NAME"' v'"$EIP712_VERSION"' chain='"$EIP712_CHAIN_ID"' contract='"$EIP712_CONTRACT"'"}' >&2

# Step 2: Get wallet address
WALLET_ADDR=$(awp-wallet status --token "$TOKEN" | jq -r '.address') || {
  echo '{"error": "Failed to get wallet address"}' >&2; exit 1
}
[[ -z "$WALLET_ADDR" || "$WALLET_ADDR" == "null" ]] && {
  echo '{"error": "Wallet address is empty — token may be expired"}' >&2; exit 1
}

# Step 3: Check current status
CHECK=$(curl -s "$API_BASE/address/$WALLET_ADDR/check") || true
IS_REGISTERED=$(echo "$CHECK" | jq -r '.isRegistered // .isRegisteredUser // false' 2>/dev/null)
BOUND_TO=$(echo "$CHECK" | jq -r '.boundTo // empty' 2>/dev/null)

if [[ "$MODE" == "principal" && "$IS_REGISTERED" == "true" ]]; then
  echo '{"status": "already_registered", "address": "'"$WALLET_ADDR"'"}'
  exit 0
fi
if [[ "$MODE" == "agent" && -n "$BOUND_TO" && "$BOUND_TO" != "null" && "$BOUND_TO" != "" && "$BOUND_TO" != "0x0000000000000000000000000000000000000000" ]]; then
  echo '{"status": "already_bound", "address": "'"$WALLET_ADDR"'", "boundTo": "'"$BOUND_TO"'"}'
  exit 0
fi

# Step 4: Get nonce from /api/nonce/{address}
NONCE_RESP=$(curl -s "$API_BASE/nonce/$WALLET_ADDR") || { echo '{"error": "Failed to fetch nonce"}' >&2; exit 1; }
NONCE=$(echo "$NONCE_RESP" | jq -r '.nonce // empty')
[[ -z "$NONCE" || "$NONCE" == "null" ]] && { echo '{"error": "Invalid nonce response: '"$NONCE_RESP"'"}' >&2; exit 1; }

# Step 5: Deadline (1 hour from now)
DEADLINE=$(( $(date +%s) + 3600 ))

# Step 6: Build EIP-712 typed data and submit
if [[ "$MODE" == "principal" ]]; then
  # Principal mode: setRecipient(self) via /relay/set-recipient
  EIP712_DATA=$(cat <<EIPJSON
{
  "types": {
    "EIP712Domain": [
      {"name": "name", "type": "string"},
      {"name": "version", "type": "string"},
      {"name": "chainId", "type": "uint256"},
      {"name": "verifyingContract", "type": "address"}
    ],
    "SetRecipient": [
      {"name": "user", "type": "address"},
      {"name": "recipient", "type": "address"},
      {"name": "nonce", "type": "uint256"},
      {"name": "deadline", "type": "uint256"}
    ]
  },
  "primaryType": "SetRecipient",
  "domain": {
    "name": "$EIP712_NAME",
    "version": "$EIP712_VERSION",
    "chainId": $EIP712_CHAIN_ID,
    "verifyingContract": "$EIP712_CONTRACT"
  },
  "message": {
    "user": "$WALLET_ADDR",
    "recipient": "$WALLET_ADDR",
    "nonce": $NONCE,
    "deadline": $DEADLINE
  }
}
EIPJSON
)
  RELAY_ENDPOINT="$API_BASE/relay/set-recipient"
  RELAY_BODY="{\"user\": \"$WALLET_ADDR\", \"recipient\": \"$WALLET_ADDR\", \"deadline\": $DEADLINE, \"signature\": \"__SIG__\"}"

else
  # AGENT mode: bind(target) via /relay/bind
  # EIP-712 Bind type: {agent, target, nonce, deadline}
  EIP712_DATA=$(cat <<EIPJSON
{
  "types": {
    "EIP712Domain": [
      {"name": "name", "type": "string"},
      {"name": "version", "type": "string"},
      {"name": "chainId", "type": "uint256"},
      {"name": "verifyingContract", "type": "address"}
    ],
    "Bind": [
      {"name": "agent", "type": "address"},
      {"name": "target", "type": "address"},
      {"name": "nonce", "type": "uint256"},
      {"name": "deadline", "type": "uint256"}
    ]
  },
  "primaryType": "Bind",
  "domain": {
    "name": "$EIP712_NAME",
    "version": "$EIP712_VERSION",
    "chainId": $EIP712_CHAIN_ID,
    "verifyingContract": "$EIP712_CONTRACT"
  },
  "message": {
    "agent": "$WALLET_ADDR",
    "target": "$TARGET",
    "nonce": $NONCE,
    "deadline": $DEADLINE
  }
}
EIPJSON
)
  RELAY_ENDPOINT="$API_BASE/relay/bind"
  RELAY_BODY="{\"agent\": \"$WALLET_ADDR\", \"target\": \"$TARGET\", \"deadline\": $DEADLINE, \"signature\": \"__SIG__\"}"
fi

# Step 7: Sign
SIG_RESULT=$(awp-wallet sign-typed-data --token "$TOKEN" --data "$EIP712_DATA") || {
  echo '{"error": "EIP-712 signing failed"}' >&2; exit 1
}
SIGNATURE=$(echo "$SIG_RESULT" | jq -r '.signature')

# Replace signature placeholder
FINAL_BODY=$(echo "$RELAY_BODY" | sed "s|__SIG__|$SIGNATURE|")

# Step 8: Submit
echo '{"info": "Submitting to '"$RELAY_ENDPOINT"'"}' >&2
RELAY_RESULT=$(curl -s -w "\n%{http_code}" -X POST "$RELAY_ENDPOINT" \
  -H "Content-Type: application/json" \
  -d "$FINAL_BODY")

HTTP_CODE=$(echo "$RELAY_RESULT" | tail -1)
BODY=$(echo "$RELAY_RESULT" | sed '$d')

if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
  echo "$BODY"
else
  echo "$BODY" >&2
  exit 1
fi
