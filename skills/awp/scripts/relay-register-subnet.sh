#!/usr/bin/env bash
# Fully gasless subnet registration via dual EIP-712 signatures (V2)
# Usage: ./relay-register-subnet.sh --token <session_token> --name <name> --symbol <sym> [options]
#
# Required: --token, --name, --symbol
# Optional: --salt <hex>, --min-stake <wei>, --subnet-manager <address>, --skills-uri <uri>
#
# --token is the awp-wallet session token from `awp-wallet unlock`.
# The agent manages the wallet password and provides the token.
#
# Prerequisites: awp-wallet (unlocked), curl, jq, python3

set -euo pipefail

API_BASE="${AWP_API_URL:-https://tapi.awp.sh/api}"
RPC_URL="${BASE_RPC_URL:-https://mainnet.base.org}"
CHAIN_ID=""
TOKEN=""
NAME=""
SYMBOL=""
SALT="0x0000000000000000000000000000000000000000000000000000000000000000"
MIN_STAKE=0
SUBNET_MANAGER="0x0000000000000000000000000000000000000000"
SKILLS_URI=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --token) TOKEN="$2"; shift 2 ;;
    --name) NAME="$2"; shift 2 ;;
    --symbol) SYMBOL="$2"; shift 2 ;;
    --salt) SALT="$2"; shift 2 ;;
    --min-stake) MIN_STAKE="$2"; shift 2 ;;
    --subnet-manager) SUBNET_MANAGER="$2"; shift 2 ;;
    --skills-uri) SKILLS_URI="$2"; shift 2 ;;
    --api) API_BASE="$2"; shift 2 ;;
    --rpc) RPC_URL="$2"; shift 2 ;;
    *) echo '{"error": "Unknown arg: '"$1"'"}' >&2; exit 1 ;;
  esac
done

[[ -z "$TOKEN" || -z "$NAME" || -z "$SYMBOL" ]] && {
  echo '{"error": "Missing required: --token, --name, --symbol"}' >&2; exit 1
}
[[ "$MIN_STAKE" =~ ^[0-9]+$ ]] || { echo '{"error": "Invalid --min-stake: must be a non-negative integer (wei)"}' >&2; exit 1; }

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

# Step 1: Fetch registry (fresh, never cached)
REGISTRY=$(curl -s "$API_BASE/registry") || { echo '{"error": "Failed to fetch /registry"}' >&2; exit 1; }
AWP_REGISTRY=$(echo "$REGISTRY" | jq -r '.awpRegistry')
[[ -z "$AWP_REGISTRY" || "$AWP_REGISTRY" == "null" ]] && { echo '{"error": "Cannot find contract address in /registry"}' >&2; exit 1; }
AWP_TOKEN=$(echo "$REGISTRY" | jq -r '.awpToken')

# Read eip712Domain from registry (new API), with fallback
EIP712_NAME=$(echo "$REGISTRY" | jq -r '.eip712Domain.name // "AWPRegistry"')
EIP712_VERSION=$(echo "$REGISTRY" | jq -r '.eip712Domain.version // "1"')
CHAIN_ID=$(echo "$REGISTRY" | jq -r '.eip712Domain.chainId // .chainId // empty')
[[ -z "$CHAIN_ID" || "$CHAIN_ID" == "null" ]] && {
  CHAIN_ID_HEX=$(curl -s -X POST "$RPC_URL" -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' | jq -r '.result')
  CHAIN_ID=$(hex_to_dec "$CHAIN_ID_HEX")
}
EIP712_CONTRACT=$(echo "$REGISTRY" | jq -r '.eip712Domain.verifyingContract // empty')
[[ -z "$EIP712_CONTRACT" || "$EIP712_CONTRACT" == "null" ]] && EIP712_CONTRACT="$AWP_REGISTRY"

# Step 2: Get wallet address
WALLET_ADDR=$(awp-wallet status --token "$TOKEN" | jq -r '.address') || {
  echo '{"error": "Failed to get wallet address — is the token valid?"}' >&2; exit 1
}
[[ -z "$WALLET_ADDR" || "$WALLET_ADDR" == "null" ]] && {
  echo '{"error": "Wallet address is empty — token may be expired"}' >&2; exit 1
}

# Step 3: Get initialAlphaPrice — selector = 0x6d345eea
PRICE_HEX=$(eth_call "$AWP_REGISTRY" "0x6d345eea")
[[ -z "$PRICE_HEX" || "$PRICE_HEX" == "0x" || "$PRICE_HEX" == "null" ]] && {
  echo '{"error": "initialAlphaPrice() returned empty — is AWP_REGISTRY correct?"}' >&2; exit 1
}
INITIAL_ALPHA_PRICE=$(hex_to_dec "$PRICE_HEX")

# LP_COST = 100M * 10^18 * initialAlphaPrice / 10^18
LP_COST=$(python3 -c "print(100_000_000 * 10**18 * $INITIAL_ALPHA_PRICE // 10**18)")

# Step 4: Get nonces
# Registry nonce — try /api/nonce/{addr} first (new API), fallback to RPC
NONCE_RESP=$(curl -s "$API_BASE/nonce/$WALLET_ADDR" 2>/dev/null)
REGISTRY_NONCE=$(echo "$NONCE_RESP" | jq -r '.nonce // empty' 2>/dev/null)
if [[ -z "$REGISTRY_NONCE" || "$REGISTRY_NONCE" == "null" ]]; then
  # Fallback: read nonce from contract via RPC
  ADDR_PADDED=$(python3 -c "print('${WALLET_ADDR#0x}'.lower().zfill(64))")
  REGISTRY_NONCE_HEX=$(eth_call "$AWP_REGISTRY" "0x7ecebe00${ADDR_PADDED}")
  REGISTRY_NONCE=$(hex_to_dec "$REGISTRY_NONCE_HEX")
fi

# AWPToken permit nonce (always from RPC — no REST endpoint for token nonces)
ADDR_PADDED=$(python3 -c "print('${WALLET_ADDR#0x}'.lower().zfill(64))")
PERMIT_NONCE_HEX=$(eth_call "$AWP_TOKEN" "0x7ecebe00${ADDR_PADDED}")
PERMIT_NONCE=$(hex_to_dec "$PERMIT_NONCE_HEX")

# Step 5: Deadline
DEADLINE=$(( $(date +%s) + 3600 ))

# Step 6: Sign ERC-2612 Permit
PERMIT_DATA=$(cat <<EIPJSON
{
  "types": {
    "EIP712Domain": [
      {"name": "name", "type": "string"},
      {"name": "version", "type": "string"},
      {"name": "chainId", "type": "uint256"},
      {"name": "verifyingContract", "type": "address"}
    ],
    "Permit": [
      {"name": "owner", "type": "address"},
      {"name": "spender", "type": "address"},
      {"name": "value", "type": "uint256"},
      {"name": "nonce", "type": "uint256"},
      {"name": "deadline", "type": "uint256"}
    ]
  },
  "primaryType": "Permit",
  "domain": {
    "name": "AWP Token",
    "version": "1",
    "chainId": $CHAIN_ID,
    "verifyingContract": "$AWP_TOKEN"
  },
  "message": {
    "owner": "$WALLET_ADDR",
    "spender": "$AWP_REGISTRY",
    "value": $LP_COST,
    "nonce": $PERMIT_NONCE,
    "deadline": $DEADLINE
  }
}
EIPJSON
)

PERMIT_SIG=$(awp-wallet sign-typed-data --token "$TOKEN" --data "$PERMIT_DATA") || {
  echo '{"error": "Permit signing failed"}' >&2; exit 1
}
PERMIT_SIGNATURE=$(echo "$PERMIT_SIG" | jq -r '.signature')

# Step 7: Sign EIP-712 RegisterSubnet (V2 includes skillsURI field)
REGISTER_DATA=$(cat <<EIPJSON
{
  "types": {
    "EIP712Domain": [
      {"name": "name", "type": "string"},
      {"name": "version", "type": "string"},
      {"name": "chainId", "type": "uint256"},
      {"name": "verifyingContract", "type": "address"}
    ],
    "RegisterSubnet": [
      {"name": "user", "type": "address"},
      {"name": "name", "type": "string"},
      {"name": "symbol", "type": "string"},
      {"name": "subnetManager", "type": "address"},
      {"name": "salt", "type": "bytes32"},
      {"name": "minStake", "type": "uint128"},
      {"name": "skillsURI", "type": "string"},
      {"name": "nonce", "type": "uint256"},
      {"name": "deadline", "type": "uint256"}
    ]
  },
  "primaryType": "RegisterSubnet",
  "domain": {
    "name": "$EIP712_NAME",
    "version": "$EIP712_VERSION",
    "chainId": $CHAIN_ID,
    "verifyingContract": "$EIP712_CONTRACT"
  },
  "message": {
    "user": "$WALLET_ADDR",
    "name": "$NAME",
    "symbol": "$SYMBOL",
    "subnetManager": "$SUBNET_MANAGER",
    "salt": "$SALT",
    "minStake": $MIN_STAKE,
    "skillsURI": "$SKILLS_URI",
    "nonce": $REGISTRY_NONCE,
    "deadline": $DEADLINE
  }
}
EIPJSON
)

REGISTER_SIG=$(awp-wallet sign-typed-data --token "$TOKEN" --data "$REGISTER_DATA") || {
  echo '{"error": "RegisterSubnet signing failed"}' >&2; exit 1
}
REGISTER_SIGNATURE=$(echo "$REGISTER_SIG" | jq -r '.signature')

# Step 8: Submit to relay (use jq to safely encode user strings)
RELAY_BODY=$(jq -n \
  --arg user "$WALLET_ADDR" \
  --arg name "$NAME" \
  --arg symbol "$SYMBOL" \
  --arg subnetManager "$SUBNET_MANAGER" \
  --arg salt "$SALT" \
  --argjson minStake "$MIN_STAKE" \
  --arg skillsUri "$SKILLS_URI" \
  --argjson deadline "$DEADLINE" \
  --arg permitSignature "$PERMIT_SIGNATURE" \
  --arg registerSignature "$REGISTER_SIGNATURE" \
  '{user:$user,name:$name,symbol:$symbol,subnetManager:$subnetManager,salt:$salt,minStake:$minStake,skillsUri:$skillsUri,deadline:$deadline,permitSignature:$permitSignature,registerSignature:$registerSignature}')

RELAY_RESULT=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE/relay/register-subnet" \
  -H "Content-Type: application/json" \
  -d "$RELAY_BODY")

HTTP_CODE=$(echo "$RELAY_RESULT" | tail -1)
BODY=$(echo "$RELAY_RESULT" | sed '$d')

if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
  echo "$BODY"
else
  echo "$BODY" >&2
  exit 1
fi
