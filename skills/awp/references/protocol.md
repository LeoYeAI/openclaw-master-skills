# AWP Protocol Reference (V2)

Shared definitions for the AWP skill.

---

## Data Structures

### SubnetStatus Enum

| Value | Name | Description |
|-------|------|-------------|
| 0 | Pending | Registered but not yet activated |
| 1 | Active | Operational, receiving allocations |
| 2 | Paused | Temporarily halted by owner |
| 3 | Banned | Governance-banned via Timelock |

### SubnetInfo (on-chain struct)

Returned by `AWPRegistry.getSubnet(subnetId)`. AWPRegistry lifecycle state only — identity data lives in SubnetNFT.

| Field | Type | Notes |
|-------|------|-------|
| lpPool | bytes32 | PancakeSwap V4 PoolId |
| status | SubnetStatus | Enum (0–3), see SubnetStatus above |
| createdAt | uint64 | Unix timestamp when subnet was registered |
| activatedAt | uint64 | Unix timestamp when activated (0 if never activated) |

> **Important**: On-chain SubnetInfo does NOT include `name`, `symbol`, `skillsURI`, `subnetManager`, `alphaToken`, `minStake`, or `owner`. Use `getSubnetFull()` or the REST API for those fields.

### SubnetFullInfo (on-chain struct)

Returned by `AWPRegistry.getSubnetFull(subnetId)`. Combined: AWPRegistry state + SubnetNFT identity.

| Field | Type | Notes |
|-------|------|-------|
| subnetManager | address | Subnet manager contract (Alpha minter) |
| alphaToken | address | Alpha token address |
| lpPool | bytes32 | PancakeSwap V4 PoolId |
| status | SubnetStatus | Enum (0–3) |
| createdAt | uint64 | Unix timestamp when subnet was registered |
| activatedAt | uint64 | Unix timestamp when activated (0 if never activated) |
| name | string | Alpha token name |
| symbol | string | Alpha token symbol |
| skillsURI | string | Skills file URI (set via SubnetNFT.setSkillsURI) |
| minStake | uint128 | Minimum stake for agents (0 = no minimum) |
| owner | address | SubnetNFT owner |

### SubnetParams (registration input)

Used in `AWPRegistry.registerSubnet(params)`.

| Field | Type | Constraints |
|-------|------|-------------|
| name | string | Alpha token name, 1–64 bytes |
| symbol | string | Alpha token symbol, 1–16 bytes |
| subnetManager | address | `address(0)` = auto-deploy SubnetManager proxy |
| salt | bytes32 | CREATE2 salt; `bytes32(0)` = use subnetId as salt |
| minStake | uint128 | Minimum stake for agents (0 = no minimum) |
| skillsURI | string | Skills file URI (IPFS/HTTPS) |

### AgentInfo (on-chain struct)

Returned by `AWPRegistry.getAgentInfo(agent, subnetId)`.

| Field | Type |
|-------|------|
| boundTo | address |
| isValid | bool |
| stake | uint256 |
| recipient | address |

### StakeNFT Position

Returned by `StakeNFT.positions(tokenId)`.

| Field | Type | Notes |
|-------|------|-------|
| amount | uint128 | Staked AWP in wei |
| lockEndTime | uint64 | Unix timestamp when lock expires |
| createdAt | uint64 | Unix timestamp when position was created |

> **Important**: StakeNFT is NOT ERC721Enumerable. Token IDs cannot be iterated on-chain. Always retrieve position lists via `GET /staking/user/{address}/positions`.

---

## Event Field Table (26 types)

All events arrive via WebSocket (`wss://<API_HOST>/ws/live`) with envelope:
```json
{"type": "EventName", "blockNumber": 12345, "txHash": "0x...", "data": {...}}
```

### User & Delegation Events

| Event | Source | Data Fields |
|-------|--------|-------------|
| Bound | AWPRegistry | `{user, target, oldTarget}` |
| RecipientUpdated | AWPRegistry | `{user, recipient}` |
| DelegateGranted | AWPRegistry | `{user, delegate}` |
| DelegateRevoked | AWPRegistry | `{user, delegate}` |

### Staking Events

| Event | Source | Data Fields | Pitfall |
|-------|--------|-------------|---------|
| Deposited | StakeNFT | `{user, tokenId, amount, lockEndTime}` | `lockEndTime` is **absolute** unix timestamp, NOT relative lock duration |
| PositionIncreased | StakeNFT | `{tokenId, addedAmount, newLockEndTime}` | — |
| Withdrawn | StakeNFT | `{user, tokenId, amount}` | — |
| Allocated | AWPRegistry | `{user, agent, subnetId, amount, operator}` | Includes `operator` field |
| Deallocated | AWPRegistry | `{user, agent, subnetId, amount, operator}` | Includes `operator` field |
| Reallocated | AWPRegistry | `{user, fromAgent, fromSubnet, toAgent, toSubnet, amount, operator}` | Includes `operator` field; `user` = stake owner, `operator` = caller |

### Subnet Events

| Event | Source | Data Fields | Pitfall |
|-------|--------|-------------|---------|
| SubnetRegistered | AWPRegistry | `{subnetId, owner, name, symbol, subnetManager, alphaToken}` | `subnetManager` (not subnetContract); does NOT include skillsURI |
| LPCreated | AWPRegistry | `{subnetId, poolId, awpAmount, alphaAmount}` | — |
| SkillsURIUpdated | SubnetNFT | `{subnetId, skillsURI}` | Emitted by SubnetNFT, not AWPRegistry |
| MinStakeUpdated | SubnetNFT | `{subnetId, minStake}` | Emitted by SubnetNFT, not AWPRegistry |
| SubnetActivated | AWPRegistry | `{subnetId}` | — |
| SubnetPaused | AWPRegistry | `{subnetId}` | — |
| SubnetResumed | AWPRegistry | `{subnetId}` | — |
| SubnetBanned | AWPRegistry | `{subnetId}` | — |
| SubnetUnbanned | AWPRegistry | `{subnetId}` | — |
| SubnetDeregistered | AWPRegistry | `{subnetId}` | — |

### Emission Events [DRAFT]

| Event | Source | Data Fields |
|-------|--------|-------------|
| GovernanceWeightUpdated | AWPEmission | `{addr, weight}` |
| RecipientAWPDistributed | AWPEmission | `{epoch, recipient, awpAmount}` |
| DAOMatchDistributed | AWPEmission | `{epoch, amount}` |
| EpochSettled | AWPEmission | `{epoch, totalEmission, recipientCount}` |
| AllocationsSubmitted | AWPEmission | `{nonce, recipients, weights}` |
| OracleConfigUpdated | AWPEmission | `{oracles, threshold}` |

---

## Shared Endpoints

### `GET /registry`

Returns all 10 protocol contract addresses. Always fetch dynamically — never hardcode.

```json
{
  "awpRegistry": "0x...",
  "awpToken": "0x...",
  "awpEmission": "0x...",
  "stakingVault": "0x...",
  "stakeNFT": "0x...",
  "subnetNFT": "0x...",
  "lpManager": "0x...",
  "alphaTokenFactory": "0x...",
  "dao": "0x...",
  "treasury": "0x..."
}
```

> Note: Per-subnet addresses (`subnet_contract`, `alpha_token`, `lp_pool`) are returned by `GET /subnets/{subnetId}`, not by `/registry`. The on-chain `AWPRegistry.getRegistry()` additionally returns `guardian` which is not in the REST response.

### `GET /address/{address}/check`

Check registration status for any address.

```json
{
  "isRegistered": true,
  "boundTo": "0x...",
  "recipient": "0x..."
}
```

> `isRegistered` = `boundTo != 0x0 || recipient != 0x0`.

### `GET /health`

```json
{"status": "ok"}
```

---

## Protocol Constants

| Constant | Value |
|----------|-------|
| Chain | Base (EVM, Chain ID 8453) |
| Epoch Duration | 1 day (86,400 seconds) |
| Initial Daily Emission | 15,800,000 AWP |
| Decay Factor | 0.996844 per epoch (~0.3156% daily decay) |
| Emission Split | 50% recipients / 50% DAO |
| Max Active Subnets | 10,000 |
| Max Recipients | 10,000 |
| Max Weight Seconds | 54 weeks (32,659,200 seconds) — voting power sqrt cap |
| AWP Max Supply | 10,000,000,000 AWP (10^28 wei) |
| Alpha Max Supply | 10,000,000,000 per subnet (10^28 wei) |
| Token Decimals | 18 (all tokens) |
| Proposal Threshold | 1,000,000 AWP voting power |
| Immunity Period | 30 days |
| Timelock Delay | 2 days |
| Pool Fee | 1% (PancakeSwap V4 CL) |
| Oracle Threshold | DAO-configured (initially 3/5 recommended) |

> Emission constants are **[DRAFT]** — the emission mechanism has not been finalized.

### Voting Power Formula

```
votingPower = amount * sqrt(min(remainingTime, 54 weeks) / 7 days)
```

- `remainingTime` = `lockEndTime - block.timestamp` (in seconds)
- `54 weeks` = 32,659,200 seconds (MAX_WEIGHT_SECONDS)
- `7 days` = 604,800 seconds (base unit for sqrt)
- Time-based calculation using unix timestamps, not epoch numbers

---

## Amount Handling

All amounts in API responses and contract calls are **string-type wei** (18 decimals).

- Process with `BigInt`, never `Number` (precision loss above 2^53)
- Display as human-readable: `amount / 10^18`, show 4 decimal places
- Format helper: `{formatAWP(amount)}` → e.g. "15,800,000.0000 AWP"
- Short address: `{shortAddr(addr)}` → e.g. "0x1234...abcd"
