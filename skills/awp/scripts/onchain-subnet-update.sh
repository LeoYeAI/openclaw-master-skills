#!/usr/bin/env bash
# On-chain subnet settings update — setSkillsURI or setMinStake on SubnetNFT (V2)
# IMPORTANT: These go to SUBNET_NFT, not AWPRegistry!
# Usage:
#   ./onchain-subnet-update.sh --token <T> --subnet <id> --skills-uri <uri>
#   ./onchain-subnet-update.sh --token <T> --subnet <id> --min-stake <wei>
# Requires ETH for gas. NFT owner only.
set -euo pipefail

API_BASE="${AWP_API_URL:-https://tapi.awp.sh/api}"
TOKEN=""
SUBNET=""
SKILLS_URI=""
MIN_STAKE=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --token) TOKEN="$2"; shift 2 ;;
    --subnet) SUBNET="$2"; shift 2 ;;
    --skills-uri) SKILLS_URI="$2"; shift 2 ;;
    --min-stake) MIN_STAKE="$2"; shift 2 ;;
    *) echo '{"error": "Unknown arg: '"$1"'"}' >&2; exit 1 ;;
  esac
done
[[ -z "$TOKEN" || -z "$SUBNET" ]] && { echo '{"error": "Missing --token, --subnet"}' >&2; exit 1; }
[[ -z "$SKILLS_URI" && -z "$MIN_STAKE" ]] && { echo '{"error": "Provide --skills-uri or --min-stake"}' >&2; exit 1; }
[[ -n "$SKILLS_URI" && -n "$MIN_STAKE" ]] && { echo '{"error": "Provide only one of --skills-uri or --min-stake per call"}' >&2; exit 1; }
[[ "$SUBNET" =~ ^[0-9]+$ && "$SUBNET" -gt 0 ]] || { echo '{"error": "Invalid --subnet: must be > 0"}' >&2; exit 1; }
[[ -n "$MIN_STAKE" ]] && { [[ "$MIN_STAKE" =~ ^[0-9]+$ ]] || { echo '{"error": "Invalid --min-stake: must be a non-negative integer (wei)"}' >&2; exit 1; }; }

# Pre-flight
WALLET_ADDR=$(awp-wallet status --token "$TOKEN" | jq -r '.address')
[[ -z "$WALLET_ADDR" || "$WALLET_ADDR" == "null" ]] && { echo '{"error": "Invalid token"}' >&2; exit 1; }

REGISTRY=$(curl -s "$API_BASE/registry")
SUBNET_NFT=$(echo "$REGISTRY" | jq -r '.subnetNFT')
[[ -z "$SUBNET_NFT" || "$SUBNET_NFT" == "null" ]] && { echo '{"error": "Failed to get subnetNFT from /registry"}' >&2; exit 1; }

SUBNET_PADDED=$(python3 -c "print(hex($SUBNET)[2:].zfill(64))")

if [[ -n "$SKILLS_URI" ]]; then
  # setSkillsURI(uint256,string) selector = 0x7c2f4cd6
  # ABI encode: tokenId (32 bytes) + offset to string (32 bytes) + string length (32 bytes) + string data (padded to 32 bytes)
  CALLDATA=$(_SKILLS_URI="$SKILLS_URI" python3 -c "
import os
token_id = $SUBNET
uri = os.environ['_SKILLS_URI']
uri_bytes = uri.encode('utf-8')
uri_len = len(uri_bytes)
# Pad URI to 32-byte boundary
padded_len = ((uri_len + 31) // 32) * 32
uri_hex = uri_bytes.hex().ljust(padded_len * 2, '0')

selector = '0x7c2f4cd6'
# Param 1: tokenId
p1 = hex(token_id)[2:].zfill(64)
# Param 2: offset to string data (2 * 32 = 64 bytes from start of params)
p2 = hex(64)[2:].zfill(64)
# String: length + data
str_len = hex(uri_len)[2:].zfill(64)

print(selector + p1 + p2 + str_len + uri_hex)
")
  echo '{"step": "setSkillsURI", "subnet": '"$SUBNET"', "skillsURI": "'"$SKILLS_URI"'", "target": "SubnetNFT ('"$SUBNET_NFT"')"}' >&2

elif [[ -n "$MIN_STAKE" ]]; then
  # setMinStake(uint256,uint128) selector = 0x63a9bbe5
  MIN_STAKE_PADDED=$(python3 -c "print(hex($MIN_STAKE)[2:].zfill(64))")
  CALLDATA="0x63a9bbe5${SUBNET_PADDED}${MIN_STAKE_PADDED}"
  echo '{"step": "setMinStake", "subnet": '"$SUBNET"', "minStake": "'"$MIN_STAKE"'", "target": "SubnetNFT ('"$SUBNET_NFT"')"}' >&2
fi

awp-wallet send --token "$TOKEN" --to "$SUBNET_NFT" --data "$CALLDATA" --chain base
