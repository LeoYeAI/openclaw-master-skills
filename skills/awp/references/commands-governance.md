# AWP Governance Commands

**API Base URL**: `{API_BASE}/api` (default `https://tapi.awp.sh/api`, override via `AWP_API_URL` env var)

> **IMPORTANT**: Always use the bundled `scripts/*.py` files for write operations — they handle ABI encoding natively in Python, require only python3, and work without Foundry or curl/jq.
> The `cast calldata` examples below are for reference only; do NOT run them directly.

## Setup (reference only — bundled scripts handle this automatically)

```bash
# 以下为参考说明，实际操作使用 scripts/*.py 自动完成
REGISTRY=$(curl -s {API_BASE}/api/registry)
AWP_REGISTRY=$(echo $REGISTRY | jq -r '.awpRegistry')
AWP_TOKEN=$(echo $REGISTRY | jq -r '.awpToken')
STAKE_NFT=$(echo $REGISTRY | jq -r '.stakeNFT')
SUBNET_NFT=$(echo $REGISTRY | jq -r '.subnetNFT')
DAO_ADDR=$(echo $REGISTRY | jq -r '.dao')
TREASURY=$(echo $REGISTRY | jq -r '.treasury')

WALLET_ADDR=$(awp-wallet receive | jq -r '.eoaAddress')
```

---

## G1 · Create Proposal

### Contract Calls

```solidity
// Executable proposal (via Timelock)
function proposeWithTokens(
    address[] targets, uint256[] values, bytes[] calldatas,
    string description, uint256[] tokenIds
) returns (uint256 proposalId)
// Requires >= 1,000,000 AWP voting power across tokenIds

// Signal-only proposal (no execution, no Timelock)
function signalPropose(string description, uint256[] tokenIds) returns (uint256 proposalId)

// Check proposal type
function isSignalProposal(uint256 proposalId) view returns (bool)
```

---

## G2 · Vote

### Contract Call

```solidity
function castVoteWithReasonAndParams(
    uint256 proposalId, uint8 support, string reason, bytes params
)
// support: 0=Against, 1=For, 2=Abstain
// params = encodeAbiParameters([{type:'uint256[]'}], [tokenIds])
// DO NOT use encodePacked — use encodeAbiParameters
//
// BLOCKED: castVote() and castVoteWithReason() revert — MUST use params variant
//
// Voting power: amount * sqrt(min(remainingTime, 54 weeks) / 7 days)
// Anti-manipulation: NFTs with createdAt >= proposalCreatedAt CANNOT vote
//   (only positions created strictly before the proposal timestamp are eligible)
// Per-tokenId double-vote prevention
```

### Supporting View Functions

```solidity
function hasVotedWithToken(uint256 proposalId, uint256 tokenId) view returns (bool)
function proposalCreatedAt(uint256 proposalId) view returns (uint64)   // Timestamp when proposal was created
```

### Complete Command Template

```bash
# The bundled script handles position filtering, ABI encoding, and raw call automatically:
python3 scripts/onchain-vote.py --token {T} --proposal {proposalId} --support 1 --reason "I support this"
# support: 0=Against, 1=For, 2=Abstain
```

---

## G3 · Query Proposals

### REST

```
GET /governance/proposals?status=Active&page=1&limit=20
GET /governance/proposals/{proposalId}
```

### On-Chain Enrichment

```solidity
function proposalVotes(uint256 proposalId) view returns (uint256 againstVotes, uint256 forVotes, uint256 abstainVotes)
function isSignalProposal(uint256 proposalId) view returns (bool)
function proposalCreatedAt(uint256 proposalId) view returns (uint64)
function quorum(uint256) view returns (uint256)
function proposalThreshold() view returns (uint256)   // 1,000,000 AWP
```

---

## G4 · Query Treasury

### REST

```
GET /governance/treasury
```
```json
{"treasuryAddress": "0x..."}
```

### On-Chain (optional balance check)

```solidity
function balanceOf(address account) view returns (uint256)   // on AWPToken
```

---

## Supplementary Endpoints

### AWP Token Info

```
GET /tokens/awp
```
```json
{"totalSupply": "5015800000000000000000000000", "maxSupply": "10000000000000000000000000000"}
```

### Alpha Token Info

```
GET /tokens/alpha/{subnetId}
```
```json
{"subnetId": 1, "name": "My Subnet Alpha", "symbol": "MSALPHA", "alphaToken": "0x..."}
```

### Alpha Token Price

```
GET /tokens/alpha/{subnetId}/price
```
```json
{"priceInAWP": "0.015", "reserve0": "...", "reserve1": "...", "updatedAt": "..."}
```

### User Profile

```
GET /users/{address}
```
```json
{
  "user": {"address": "0x...", "bound_to": "0x...", "recipient": "0x...", "registered_at": 1710000000},
  "balance": {"user_address": "0x...", "total_staked": "5000000000000000000000", "total_allocated": "3000000000000000000000"}
}
```

### Staking Details

```
GET /staking/agent/{agent}/subnet/{subnetId}
```
```json
{"amount": "5000000000000000000000"}
```

```
GET /staking/agent/{agent}/subnets
```
```json
[{"subnet_id": 1, "amount": "5000000000000000000000"}, {"subnet_id": 3, "amount": "2000000000000000000000"}]
```

```
GET /staking/subnet/{subnetId}/total
```
```json
{"total": "50000000000000000000000"}
```

### Subnet Earnings

```
GET /subnets/{subnetId}/earnings?page=1&limit=20
```
```json
[{"epoch_id": 5, "recipient": "0x1234...", "awp_amount": "7900000000000000000000000"}]
```
