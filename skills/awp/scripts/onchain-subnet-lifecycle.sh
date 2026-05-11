#!/usr/bin/env bash
# On-chain subnet lifecycle — activate/pause/resume (V2)
# Usage:
#   ./onchain-subnet-lifecycle.sh --token <T> --subnet <id> --action <activate|pause|resume>
# Requires ETH for gas. SubnetNFT owner only.
# Pre-checks current subnet status to prevent invalid state transitions.
set -euo pipefail

API_BASE="${AWP_API_URL:-https://tapi.awp.sh/api}"
TOKEN=""
SUBNET=""
ACTION=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --token) TOKEN="$2"; shift 2 ;;
    --subnet) SUBNET="$2"; shift 2 ;;
    --action) ACTION="$2"; shift 2 ;;
    *) echo '{"error": "Unknown arg: '"$1"'"}' >&2; exit 1 ;;
  esac
done
[[ -z "$TOKEN" || -z "$SUBNET" || -z "$ACTION" ]] && { echo '{"error": "Missing --token, --subnet, --action"}' >&2; exit 1; }
[[ "$SUBNET" =~ ^[0-9]+$ && "$SUBNET" -gt 0 ]] || { echo '{"error": "Invalid --subnet: must be > 0"}' >&2; exit 1; }
[[ "$ACTION" == "activate" || "$ACTION" == "pause" || "$ACTION" == "resume" ]] || {
  echo '{"error": "--action must be activate, pause, or resume"}' >&2; exit 1
}

# Pre-flight
WALLET_ADDR=$(awp-wallet status --token "$TOKEN" | jq -r '.address')
[[ -z "$WALLET_ADDR" || "$WALLET_ADDR" == "null" ]] && { echo '{"error": "Invalid token"}' >&2; exit 1; }

REGISTRY=$(curl -s "$API_BASE/registry")
AWP_REGISTRY=$(echo "$REGISTRY" | jq -r '.awpRegistry')
[[ -z "$AWP_REGISTRY" || "$AWP_REGISTRY" == "null" ]] && { echo '{"error": "Failed to get contract address from /registry"}' >&2; exit 1; }

# Check current subnet status
SUBNET_INFO=$(curl -s "$API_BASE/subnets/$SUBNET")
STATUS=$(echo "$SUBNET_INFO" | jq -r '.status')
[[ -z "$STATUS" || "$STATUS" == "null" ]] && { echo '{"error": "Subnet #'"$SUBNET"' not found"}' >&2; exit 1; }

# Validate state transition
case "$ACTION" in
  activate)
    [[ "$STATUS" != "Pending" ]] && { echo '{"error": "Cannot activate: subnet is '"$STATUS"' (must be Pending)"}' >&2; exit 1; }
    # activateSubnet(uint256) selector = 0xcead1c96
    SELECTOR="0xcead1c96"
    ;;
  pause)
    [[ "$STATUS" != "Active" ]] && { echo '{"error": "Cannot pause: subnet is '"$STATUS"' (must be Active)"}' >&2; exit 1; }
    # pauseSubnet(uint256) selector = 0x44e047ca
    SELECTOR="0x44e047ca"
    ;;
  resume)
    [[ "$STATUS" != "Paused" ]] && { echo '{"error": "Cannot resume: subnet is '"$STATUS"' (must be Paused)"}' >&2; exit 1; }
    # resumeSubnet(uint256) selector = 0x5364944c
    SELECTOR="0x5364944c"
    ;;
esac

SUBNET_PADDED=$(python3 -c "print(hex($SUBNET)[2:].zfill(64))")
CALLDATA="${SELECTOR}${SUBNET_PADDED}"

echo '{"step": "'"$ACTION"'Subnet", "subnet": '"$SUBNET"', "currentStatus": "'"$STATUS"'"}' >&2
awp-wallet send --token "$TOKEN" --to "$AWP_REGISTRY" --data "$CALLDATA" --chain base
