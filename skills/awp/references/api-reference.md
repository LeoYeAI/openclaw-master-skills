# AWP Skill — API Reference (Index)

Quick index of read-only REST endpoints. For write operations, see the dedicated command files:
- **commands-staking.md** — S1 Register/Bind, S2 Deposit, S3 Allocate
- **commands-subnet.md** — M1 Register Subnet, M2 Lifecycle, M3-M4 Settings
- **commands-governance.md** — G1 Proposals, G2 Voting, G3/G4 Queries, Supplementary

**API Base URL**: `{API_BASE}/api` (default `https://tapi.awp.sh/api`, override via `AWP_API_URL` env var)

---

## Read-Only Endpoints

| Action | Endpoint | Notes |
|--------|----------|-------|
| Q1 Subnet | `GET /subnets/{subnetId}` | Full subnet object (includes `min_stake`, `immunity_ends_at`, `burned`); fallback: `getSubnetFull(id)` on AWPRegistry |
| Q2 Balance | `GET /staking/user/{addr}/balance` | Also: `/positions`, `/allocations` |
| Q3 Emission | `GET /emission/current` [DRAFT] | Also: `/schedule`, `/epochs` [DRAFT] |
| Q4 Agent | `GET /subnets/{subnetId}/agents/{agent}` | Single agent stake on a subnet |
| Q5 List | `GET /subnets?status={s}&page={p}&limit={n}` | Status: Pending, Active, Paused, Banned |
| Q6 Skills | `GET /subnets/{subnetId}/skills` | Returns skillsURI |
| Q7 Epochs | `GET /emission/epochs?page={p}&limit={n}` [DRAFT] | Epoch history with emissions |

## Shared Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /registry` | Contract addresses + `eip712Domain` + `chainId` — never hardcode |
| `GET /nonce/{address}` | EIP-712 signature nonce for gasless relay |
| `GET /address/{addr}/check` | `{isRegistered, boundTo, recipient}` |
| `GET /health` | Service health |

### `GET /registry` Response

```json
{
  "chainId": 8453,
  "awpRegistry": "0x...",
  "awpToken": "0x...",
  "awpEmission": "0x...",
  "stakingVault": "0x...",
  "stakeNFT": "0x...",
  "subnetNFT": "0x...",
  "lpManager": "0x...",
  "alphaTokenFactory": "0x...",
  "dao": "0x...",
  "treasury": "0x...",
  "eip712Domain": {
    "name": "AWPRegistry",
    "version": "1",
    "chainId": 8453,
    "verifyingContract": "0x..."
  }
}
```

> **Note:** `eip712Domain` provides the complete EIP-712 domain separator for all gasless relay signatures. Per-subnet addresses are returned by `GET /subnets/{subnetId}`, not by `/registry`.

### `GET /nonce/{address}` Response

```json
{"nonce": 0}
```

> The nonce auto-increments after each successful relay call. Use this before signing any EIP-712 relay message.

### `GET /address/{addr}/check` Response

```json
{
  "isRegistered": true,
  "boundTo": "0x...",
  "recipient": "0x..."
}
```
> `isRegistered` = `boundTo != 0x0 || recipient != 0x0`.

### Subnet REST Response

```json
{
  "subnet_id": 1,
  "owner": "0x...",
  "name": "My Subnet",
  "symbol": "MSUB",
  "subnet_contract": "0x...",
  "skills_uri": "ipfs://QmSkills...",
  "alpha_token": "0x...",
  "lp_pool": "0x...",
  "status": "Active",
  "created_at": 1710000000,
  "activated_at": 1710000100,
  "min_stake": 0,
  "immunity_ends_at": null,
  "burned": false
}
```

## Contract Quick Reference

### AWPRegistry — getRegistry()

```solidity
getRegistry() → (awpToken, subnetNFT, alphaTokenFactory, awpEmission, lpManager, stakingVault, stakeNFT, treasury, guardian)
```
> Returns `awpRegistry`-scoped addresses. No `accessManager` in the tuple.

### AWPRegistry — Account System V2

```solidity
register()                          // Optional; equivalent to setRecipient(msg.sender)
bind(address target)                // Tree-based binding with anti-cycle check
setRecipient(address recipient)     // Set reward recipient
grantDelegate(address delegate)     // Grant delegation
revokeDelegate(address delegate)    // Revoke delegation
resolveRecipient(address addr) view // Walks boundTo chain to root
isRegistered(address addr) view     // boundTo[addr] != 0 || recipient[addr] != 0
```
> EIP-712 domain name: `"AWPRegistry"` (not "AWPRootNet").
> `unbind()` and `removeAgent()` are removed in V2.
> `setDelegation` replaced by `grantDelegate` / `revokeDelegate`.
> `setRewardRecipient` replaced by `setRecipient` + gasless `setRecipientFor`.

### AWPRegistry — Staking (allocation only)

```solidity
allocate(address staker, address agent, uint256 subnetId, uint256 amount)
deallocate(address staker, address agent, uint256 subnetId, uint256 amount)
reallocate(address staker, address fromAgent, uint256 fromSubnetId, address toAgent, uint256 toSubnetId, uint256 amount)
```
> `staker` is an explicit parameter (caller must be staker or delegate).

### AWPEmission

```solidity
awpRegistry() → address
```

### StakeNFT

```solidity
depositFor(address user, uint256 amount, uint64 lockDuration) → uint256 tokenId  // onlyAWPRegistry
```

### StakingVault

```solidity
allocate(address staker, address agent, uint256 subnetId, uint256 amount)    // onlyAWPRegistry
deallocate(address staker, address agent, uint256 subnetId, uint256 amount)  // onlyAWPRegistry
reallocate(...)                                                               // onlyAWPRegistry
```
> All functions use `staker` param name and `onlyAWPRegistry` modifier.

## WebSocket Events

> Source contract: **AWPRegistry** (not RootNet). 26 event types total.

| Event | Data Fields | Source |
|-------|-------------|--------|
| `Bound` | `{user, target, oldTarget}` | AWPRegistry |
| `RecipientUpdated` | `{user, recipient}` | AWPRegistry |
| `DelegateGranted` | `{user, delegate}` | AWPRegistry |
| `DelegateRevoked` | `{user, delegate}` | AWPRegistry |
| `Deposited` | `{user, tokenId, amount, lockEndTime}` | StakeNFT |
| `PositionIncreased` | `{tokenId, addedAmount, newLockEndTime}` | StakeNFT |
| `Withdrawn` | `{user, tokenId, amount}` | StakeNFT |
| `Allocated` | `{user, agent, subnetId, amount, operator}` | AWPRegistry |
| `Deallocated` | `{user, agent, subnetId, amount, operator}` | AWPRegistry |
| `Reallocated` | `{user, fromAgent, fromSubnet, toAgent, toSubnet, amount, operator}` | AWPRegistry |
| `SubnetRegistered` | `{subnetId, owner, name, symbol, subnetManager, alphaToken}` | AWPRegistry |
| `LPCreated` | `{subnetId, poolId, awpAmount, alphaAmount}` | AWPRegistry |
| `SkillsURIUpdated` | `{subnetId, skillsURI}` | SubnetNFT |
| `MinStakeUpdated` | `{subnetId, minStake}` | SubnetNFT |
| `SubnetActivated` | `{subnetId}` | AWPRegistry |
| `SubnetPaused` | `{subnetId}` | AWPRegistry |
| `SubnetResumed` | `{subnetId}` | AWPRegistry |
| `SubnetBanned` | `{subnetId}` | AWPRegistry |
| `SubnetUnbanned` | `{subnetId}` | AWPRegistry |
| `SubnetDeregistered` | `{subnetId}` | AWPRegistry |
| `GovernanceWeightUpdated` | `{addr, weight}` | AWPEmission |
| `RecipientAWPDistributed` | `{epoch, recipient, awpAmount}` | AWPEmission |
| `DAOMatchDistributed` | `{epoch, amount}` | AWPEmission |
| `EpochSettled` | `{epoch, totalEmission, recipientCount}` | AWPEmission |
| `AllocationsSubmitted` | `{nonce, recipients, weights}` | AWPEmission |
| `OracleConfigUpdated` | `{oracles, threshold}` | AWPEmission |

For data structures, events, and constants, see **protocol.md**.
