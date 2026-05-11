#!/usr/bin/env bash
# On-chain vote on AWP DAO proposal
# Uses castVoteWithReasonAndParams(uint256,uint8,string,bytes)
# params = abi.encode(uint256[] tokenIds) — eligible stakeNFT positions only
# Usage: ./onchain-vote.sh --token <T> --proposal <id> --support <0|1|2> [--reason <text>]
# Requires ETH for gas.
set -euo pipefail

API_BASE="${AWP_API_URL:-https://tapi.awp.sh/api}"
RPC_URL="${BASE_RPC_URL:-https://mainnet.base.org}"
TOKEN=""
PROPOSAL=""
SUPPORT=""
REASON=""
while [[ $# -gt 0 ]]; do
  case $1 in --token) TOKEN="$2"; shift 2 ;; --proposal) PROPOSAL="$2"; shift 2 ;; --support) SUPPORT="$2"; shift 2 ;; --reason) REASON="$2"; shift 2 ;; *) echo '{"error": "Unknown arg: '"$1"'"}' >&2; exit 1 ;; esac
done
[[ -z "$TOKEN" || -z "$PROPOSAL" || -z "$SUPPORT" ]] && { echo '{"error": "Missing --token, --proposal, --support"}' >&2; exit 1; }

# Validate --proposal is a positive integer
[[ "$PROPOSAL" =~ ^[1-9][0-9]*$ ]] || { echo '{"error": "Invalid --proposal: must be a positive integer"}' >&2; exit 1; }

# Validate --support is 0, 1, or 2
[[ "$SUPPORT" =~ ^[012]$ ]] || { echo '{"error": "Invalid --support: must be 0 (Against), 1 (For), or 2 (Abstain)"}' >&2; exit 1; }

# Pre-flight: get wallet address
WALLET_ADDR=$(awp-wallet status --token "$TOKEN" | jq -r '.address')
[[ -z "$WALLET_ADDR" || "$WALLET_ADDR" == "null" ]] && { echo '{"error": "Invalid token"}' >&2; exit 1; }
[[ "$WALLET_ADDR" =~ ^0x[0-9a-fA-F]{40}$ ]] || { echo '{"error": "Invalid wallet address: '"$WALLET_ADDR"'"}' >&2; exit 1; }

# Fetch registry
REGISTRY=$(curl -s "$API_BASE/registry")
DAO_ADDR=$(echo "$REGISTRY" | jq -r '.dao')
[[ -z "$DAO_ADDR" || "$DAO_ADDR" == "null" ]] && { echo '{"error": "Could not fetch DAO address from registry"}' >&2; exit 1; }

# Helper: eth_call via JSON-RPC
eth_call() {
  local to="$1" data="$2"
  local payload='{"jsonrpc":"2.0","method":"eth_call","params":[{"to":"'"$to"'","data":"'"$data"'"},"latest"],"id":1}'
  local result
  result=$(curl -s -X POST "$RPC_URL" -H "Content-Type: application/json" -d "$payload")
  echo "$result" | jq -r '.result'
}

# Step 1: Fetch proposalCreatedAt from chain
# proposalCreatedAt(uint256) selector = 0x5f9103b2
PROPOSAL_PADDED=$(python3 -c "print(hex($PROPOSAL)[2:].zfill(64))")
CREATED_AT_HEX=$(eth_call "$DAO_ADDR" "0x5f9103b2${PROPOSAL_PADDED}")
[[ -z "$CREATED_AT_HEX" || "$CREATED_AT_HEX" == "null" || "$CREATED_AT_HEX" == "0x" ]] && { echo '{"error": "Could not fetch proposalCreatedAt — proposal may not exist"}' >&2; exit 1; }
PROPOSAL_CREATED_AT=$(python3 -c "print(int('$CREATED_AT_HEX', 16))")
[[ "$PROPOSAL_CREATED_AT" -eq 0 ]] && { echo '{"error": "Proposal '"$PROPOSAL"' does not exist (createdAt=0)"}' >&2; exit 1; }

echo '{"step": "proposalCreatedAt", "proposalId": '"$PROPOSAL"', "createdAt": '"$PROPOSAL_CREATED_AT"'}' >&2

# Step 2: Fetch user positions via REST
POSITIONS=$(curl -s "$API_BASE/staking/user/$WALLET_ADDR/positions")

# Step 3: Filter eligible positions (created_at < proposalCreatedAt, strict less-than)
ELIGIBLE_TOKEN_IDS=$(_POSITIONS="$POSITIONS" python3 -c "
import json, sys, os
positions = json.loads(os.environ['_POSITIONS'])
if not isinstance(positions, list):
    print(json.dumps({'error': 'Unexpected positions response'}), file=sys.stderr)
    sys.exit(1)
proposal_created = $PROPOSAL_CREATED_AT
eligible = [p['token_id'] for p in positions if int(p['created_at']) < proposal_created]
if not eligible:
    print(json.dumps({'error': 'No eligible positions: all positions were created at or after proposal creation timestamp (' + str(proposal_created) + '). You need stakeNFT positions created before the proposal.'}), file=sys.stderr)
    sys.exit(1)
# Output as JSON array
print(json.dumps(eligible))
") || exit 1

echo '{"step": "eligibleTokenIds", "tokenIds": '"$ELIGIBLE_TOKEN_IDS"'}' >&2

# Step 4: ABI-encode params = abi.encode(uint256[] tokenIds)
# This is raw ABI encoding of a dynamic uint256[], NOT prefixed with a function selector.
# Layout: offset(32) + length(32) + each element(32)
ABI_PARAMS=$(python3 -c "
import json
token_ids = json.loads('$ELIGIBLE_TOKEN_IDS')
n = len(token_ids)
# offset to start of array data (32 bytes = 0x20)
parts = [format(32, '064x')]
# array length
parts.append(format(n, '064x'))
# each uint256 element
for tid in token_ids:
    parts.append(format(tid, '064x'))
print('0x' + ''.join(parts))
")

# Step 5: Build calldata for castVoteWithReasonAndParams(uint256,uint8,string,bytes)
# Selector: 0x5f398a14
# Parameters (all dynamic-aware):
#   proposalId: uint256 (static)
#   support:    uint8   (static, padded to 32 bytes)
#   reason:     string  (dynamic)
#   params:     bytes   (dynamic)
CALLDATA=$(_REASON="$REASON" _ABI_PARAMS="$ABI_PARAMS" python3 -c "
import json, os

proposal_id = $PROPOSAL
support = $SUPPORT
reason = os.environ['_REASON']
params_hex = os.environ['_ABI_PARAMS']

# Strip 0x prefix from params
params_bytes = bytes.fromhex(params_hex[2:])
reason_bytes = reason.encode('utf-8')

selector = '5f398a14'

# Head: 4 slots (proposalId, support, offset_reason, offset_params)
# proposalId — static
slot0 = format(proposal_id, '064x')
# support — static uint8
slot1 = format(support, '064x')
# offset to reason data (dynamic) — 4 * 32 = 128 = 0x80
slot2 = format(128, '064x')
# offset to params data (dynamic) — computed after reason
# reason encoding: length(32) + ceil(len(reason_bytes)/32)*32
reason_padded_len = ((len(reason_bytes) + 31) // 32) * 32
offset_params = 128 + 32 + reason_padded_len
slot3 = format(offset_params, '064x')

# Encode reason (string): length + padded data
reason_enc = format(len(reason_bytes), '064x')
reason_enc += reason_bytes.hex().ljust(reason_padded_len * 2, '0')

# Encode params (bytes): length + padded data
params_data = params_bytes
params_padded_len = ((len(params_data) + 31) // 32) * 32
params_enc = format(len(params_data), '064x')
params_enc += params_data.hex().ljust(params_padded_len * 2, '0')

calldata = '0x' + selector + slot0 + slot1 + slot2 + slot3 + reason_enc + params_enc
print(calldata)
")

SUPPORT_LABEL="Unknown"
case "$SUPPORT" in
  0) SUPPORT_LABEL="Against" ;;
  1) SUPPORT_LABEL="For" ;;
  2) SUPPORT_LABEL="Abstain" ;;
esac

echo '{"step": "castVote", "proposalId": '"$PROPOSAL"', "support": "'"$SUPPORT_LABEL"'", "reason": "'"$REASON"'", "dao": "'"$DAO_ADDR"'"}' >&2
awp-wallet send --token "$TOKEN" --to "$DAO_ADDR" --data "$CALLDATA" --chain base
