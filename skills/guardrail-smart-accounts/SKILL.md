---
name: guardrail-smart-accounts
description: Give AI agents on-chain spending guardrails. Deploy ERC-4337 smart accounts with policy-enforced limits — agents cannot move funds beyond what you authorize, enforced at the contract level, not just in software.
version: 1.1.0
metadata:
  openclaw:
    requires:
      env:
        - GUARDRAIL_CHAIN_ID
        - GUARDRAIL_RPC_URL
        - GUARDRAIL_SIGNING_MODE
    optionalSecrets:
      - name: GUARDRAIL_API_URL
        when: Using dashboard API for policy/permission management
        sensitive: false
        description: AgentGuardrail API base URL. Defaults to https://agentguardrail.xyz
      - name: GUARDRAIL_SIGNER_ENDPOINT
        when: GUARDRAIL_SIGNING_MODE is external_signer
        sensitive: true
        description: External signer service URL
      - name: GUARDRAIL_SIGNER_AUTH_TOKEN
        when: GUARDRAIL_SIGNING_MODE is external_signer
        sensitive: true
        description: Scoped, revocable auth token for the external signer
      - name: GUARDRAIL_DASHBOARD_API_KEY
        when: Using dashboard API for policy/permission management
        sensitive: true
        description: API key for AgentGuardrail management API at agentguardrail.xyz
    primaryEnv: GUARDRAIL_RPC_URL
    emoji: "\U0001F6E1"
    homepage: https://agentguardrail.xyz
    tags:
      - ai-agents
      - smart-accounts
      - erc-4337
      - defi
      - guardrails
      - policy-enforcement
      - on-chain
      - spending-limits
      - permissions
      - audit
---

# AgentGuardrail — On-Chain Spending Guardrails for AI Agents

> **Give your AI agents a wallet they can't abuse.** AgentGuardrail deploys ERC-4337 smart accounts with policy-enforced spending limits. Agents cannot move funds beyond what you authorize — enforcement happens at the contract level, not just in software.

**Homepage:** https://agentguardrail.xyz

---

## Why AgentGuardrail?

AI agents need to move money. The problem is trust: how do you let an agent trade, bridge, or pay for compute without risking runaway spending, compromised keys, or unauthorized actions?

AgentGuardrail solves this with:

- **On-chain enforcement** — `AgentSmartAccount.validateUserOp()` calls `PermissionEnforcer` before any transaction executes. Violating transactions revert. There is no override.
- **Policy-bound accounts** — every smart account is deployed against a policy that defines allowed actions, tokens, protocols, chains, and spend limits.
- **Non-custodial** — AgentGuardrail never holds your funds. Enforcement is in the contracts you deploy.
- **Full audit trail** — every intent, validation, and on-chain event is logged with tx hash and block number.

---

## Overview

Every agent gets an ERC-4337 smart account deployed via `AgentAccountFactory`. The account's `validateUserOp()` enforces your policy through `PermissionEnforcer` before any transaction reaches the blockchain. If the action violates the policy — wrong token, wrong protocol, spend limit exceeded — the UserOperation reverts.

**Execution path:**
```
Agent builds UserOperation
  → AgentSmartAccount.validateUserOp()
    → PermissionEnforcer.validateAction()
      → Policy constraints checked on-chain
  → EntryPoint executes (only if all checks pass)
```

The AgentGuardrail API at **https://agentguardrail.xyz** provides:
- A management interface for creating policies and granting permissions
- Pre-flight validation for simulation and dashboards
- Aggregated audit logs with on-chain event indexing

Most enforcement operations can be done directly against the contracts without the API. The API is most useful for policy management, pre-flight simulation, and audit log queries.

---

## Security & Credential Model (Required)

This skill performs on-chain operations that require JSON-RPC access and transaction signing.

**Private keys must never be provided in chat and must never be stored in unconstrained agent memory.**

### Signing Modes

#### 1. External Signer (Recommended)

The agent prepares a transaction. The runtime forwards it to a secure signer service (HSM, MPC, hosted signer). The signer enforces scope, rate limits, and allowlists. The agent never sees raw private keys.

#### 2. Wallet Connector / User-Approved Signing

Transactions are prepared by the agent. A user wallet (browser, hardware wallet) prompts for approval. Keys remain in the wallet.

#### 3. Scoped Session Keys (Advanced)

Session keys must be policy-restricted, short-lived, and rotated frequently. Never use a long-lived owner EOA private key as a session key.

### The Skill Must NOT

- Ask users to paste private keys or seed phrases
- Store private keys in memory, logs, or prompts
- Access unrelated environment variables or local files
- Request cloud credentials or system-level secrets
- Persist secrets beyond runtime execution

If secure signing is not configured, operate in **read-only mode** until proper signing is established.

---

## Runtime Configuration

Required (via secure secret storage, not chat):

| Variable | Description |
|----------|-------------|
| `GUARDRAIL_CHAIN_ID` | Target chain ID (e.g., `8453` for Base, `11155111` for Sepolia) |
| `GUARDRAIL_RPC_URL` | JSON-RPC endpoint — treat as sensitive, often contains an API key |
| `GUARDRAIL_SIGNING_MODE` | One of: `external_signer`, `wallet_connector`, `session_key` |

Optional:

| Variable | Description |
|----------|-------------|
| `GUARDRAIL_API_URL` | AgentGuardrail API base. Defaults to `https://agentguardrail.xyz` |
| `GUARDRAIL_SIGNER_ENDPOINT` | External signer URL — required when `GUARDRAIL_SIGNING_MODE=external_signer` |
| `GUARDRAIL_SIGNER_AUTH_TOKEN` | Auth token for the external signer — sensitive, store securely |
| `GUARDRAIL_DASHBOARD_API_KEY` | API key for agentguardrail.xyz management API |

The API URL default in all code examples below is `https://agentguardrail.xyz`. Override with `GUARDRAIL_API_URL` if self-hosting.

---

## Smart Contract Addresses

### Base Mainnet (Chain ID 8453)

| Contract | Address |
|----------|---------|
| IdentityRegistry | `0xc1fa477f991C74Cc665E605fC74f0e2B795b5104` |
| PolicyRegistry | `0x92cd41e6a4aA13072CeBCda8830d48f269F058c4` |
| PermissionEnforcer | `0xbF63Fa97cfBba99647B410f205730d63d831061c` |
| PriceOracle | `0xf3c8c6BDc54C60EDaE6AE84Ef05B123597C355B3` |
| GuardrailFeeManager | `0xD1B7Bd65F2aB60ff84CdDF48f306a599b01d293A` |
| AgentAccountFactory | `0xCE621A324A8cb40FD424EB0D41286A97f6a6c91C` |
| EntryPoint (v0.6) | `0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789` |

### Sepolia Testnet (Chain ID 11155111)

| Contract | Address |
|----------|---------|
| IdentityRegistry | `0xc1fa477f991C74Cc665E605fC74f0e2B795b5104` |
| PolicyRegistry | `0x92cd41e6a4aA13072CeBCda8830d48f269F058c4` |
| PermissionEnforcer | `0x94991827135fbd0E681B3db51699e4988a7752f1` |
| PriceOracle | `0x052cDddba3C55A63F5e48F9e5bC6b70604Db93b8` |
| GuardrailFeeManager | `0x0f77fdD1AFCe0597339dD340E738CE3dC9A5CC12` |
| AgentAccountFactory | `0xA831229B58C05d5bA9ac109f3B29e268A0e5F41E` |
| EntryPoint (v0.6) | `0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789` |

> Start on Sepolia. Move to Base Mainnet when policies are validated.

---

## Core Capabilities

### 1. Deploy a Smart Account

Deploy a new ERC-4337 smart account via `AgentAccountFactory`. The account is bound to `PermissionEnforcer` at creation. Deployment is deterministic via CREATE2 — the same owner, agentId, and salt always produce the same address.

**One-time creation fee:** $10 USD equivalent in ETH.

**Direct contract call (recommended):**

```solidity
// Get required creation fee
uint256 fee = factory.getCreationFee();

// Deploy account (send fee as msg.value)
address account = factory.createAccount{value: fee}(
    ownerAddress,   // Controls the account
    agentId,        // bytes32 identifier for this agent
    salt            // bytes32 for CREATE2 determinism
);
```

**Via API:**

```javascript
const apiUrl = process.env.GUARDRAIL_API_URL ?? "https://agentguardrail.xyz";

const response = await fetch(`${apiUrl}/api/v1/agents/${agentId}/deploy-smart-account`, {
  method: "POST",
  headers: { Authorization: `Bearer ${process.env.GUARDRAIL_DASHBOARD_API_KEY}` },
});
const { smart_account_address } = await response.json();
```

The API path is useful when using dashboard-generated bot signers (the dashboard generates the keypair and handles deployment in one step).

---

### 2. Fund a Smart Account

Send ETH directly to the smart account address. Inbound transfers are free — no fee, no contract call needed.

```javascript
await walletClient.sendTransaction({
  to: smartAccountAddress,
  value: parseEther("1.0"),
});
```

---

### 3. Execute from a Smart Account

Agent executes a transaction from its smart account. `validateUserOp()` enforces the policy before the transaction reaches the chain — no override exists.

**Outbound transfer fee:** 10 bps (0.10%), capped at $100 USD per transaction.

```javascript
// Build the UserOperation
const callData = encodeFunctionData({
  abi: agentSmartAccountABI,
  functionName: "execute",
  args: [destinationAddress, parseEther("1.0"), "0x"],
});

// Submit via ERC-4337 EntryPoint
// The EntryPoint calls validateUserOp → PermissionEnforcer before execution
```

Fee enforcement occurs inside `GuardrailFeeManager`. Fee is deducted from the transaction value automatically.

| Transfer Amount | Fee |
|----------------|-----|
| $1,000 | $1.00 |
| $10,000 | $10.00 |
| $100,000+ | $100.00 (cap) |

---

### 4. Read Contract State (No Signing Required)

```javascript
// Get account owner
const owner = await publicClient.readContract({
  address: smartAccountAddress,
  abi: agentSmartAccountABI,
  functionName: "owner",
});

// Get smart account creation fee
const fee = await publicClient.readContract({
  address: factoryAddress,
  abi: agentAccountFactoryABI,
  functionName: "getCreationFee",
});

// Calculate transfer fee before executing
const transferFee = await publicClient.readContract({
  address: feeManagerAddress,
  abi: guardrailFeeManagerABI,
  functionName: "calculateTransferFee",
  args: [parseEther("10.0")],
});

// Check if a permission is active on-chain
const isActive = await publicClient.readContract({
  address: policyRegistryAddress,
  abi: policyRegistryABI,
  functionName: "isPermissionActive",
  args: [agentAddress, permissionId],
});
```

---

### 5. Policy Management

Policies define what an agent is allowed to do: which actions, tokens, protocols, chains, and spend limits. Policies are stored on-chain in `PolicyRegistry` and enforced by `PermissionEnforcer`.

**On-chain (direct):**

```solidity
// Register a policy on-chain
bytes32 policyId = policyRegistry.registerPolicy(
    bytes32(policyHash),    // Unique identifier
    allowedActions,         // bytes32[] action type hashes
    allowedTokens,          // address[] token contracts
    allowedProtocols,       // address[] protocol contracts
    allowedChains,          // uint256[] chain IDs
    maxValuePerTx,          // uint256 in wei
    maxDailyVolume,         // uint256 in wei
    expiresAt               // uint256 unix timestamp
);
```

**Via API (recommended for most use cases — handles on-chain registration automatically):**

```javascript
const apiUrl = process.env.GUARDRAIL_API_URL ?? "https://agentguardrail.xyz";
const headers = {
  "Content-Type": "application/json",
  Authorization: `Bearer ${process.env.GUARDRAIL_DASHBOARD_API_KEY}`,
};

// Create and activate a policy
const policy = await fetch(`${apiUrl}/api/v1/policies`, {
  method: "POST",
  headers,
  body: JSON.stringify({
    name: "DeFi Trading Policy",
    description: "Allow swaps and transfers with daily limits",
    definition: {
      actions: ["swap", "transfer"],
      assets: {
        tokens: ["0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"],
        protocols: ["*"],
        chains: [1, 8453],
      },
      constraints: {
        maxValuePerTx: "1000000000000000000",   // 1 ETH
        maxDailyVolume: "10000000000000000000",  // 10 ETH
        maxTxCount: 100,
        requireApproval: false,
      },
      duration: {
        validFrom: "2026-01-01T00:00:00Z",
        validUntil: "2026-12-31T23:59:59Z",
      },
    },
  }),
}).then((r) => r.json());

// Activate it (registers on-chain via PolicyRegistry)
await fetch(`${apiUrl}/api/v1/policies/${policy.id}/activate`, {
  method: "POST",
  headers,
});
```

**PolicyDefinition fields:**

| Field | Type | Description |
|-------|------|-------------|
| `actions` | `string[]` | `swap`, `transfer`, `approve`, `stake`, `unstake`, `deposit`, `withdraw`, `mint`, `burn`, `bridge`, `claim`, `vote`, `delegate`, `lp_add`, `lp_remove`, `borrow`, `repay`, `liquidate`, `*` |
| `assets.tokens` | `string[]` | Token contract addresses, or `["*"]` for all |
| `assets.protocols` | `string[]` | Protocol addresses, or `["*"]` for all |
| `assets.chains` | `number[]` | Allowed chain IDs |
| `constraints.maxValuePerTx` | `string` | Max per-tx value in wei |
| `constraints.maxDailyVolume` | `string` | Max daily volume in wei |
| `constraints.maxWeeklyVolume` | `string` | Max weekly volume in wei |
| `constraints.maxTxCount` | `number` | Max transactions within the duration |
| `duration.validFrom` / `validUntil` | `string` | ISO 8601 |
| `conditions` | `array` | Advanced rules: `{ field, operator, value }`. Operators: `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `in`, `not_in`, `contains`, `regex` |

**Other policy operations:**

```javascript
// Update (draft policies update in place; active policies create a new version)
await fetch(`${apiUrl}/api/v1/policies/${policyId}`, { method: "PUT", headers, body: JSON.stringify({...}) });

// Revoke (disables on-chain — active permissions using this policy stop validating)
await fetch(`${apiUrl}/api/v1/policies/${policyId}/revoke`, { method: "POST", headers });

// Reactivate
await fetch(`${apiUrl}/api/v1/policies/${policyId}/reactivate`, { method: "POST", headers });

// List / Get / Delete (draft only)
await fetch(`${apiUrl}/api/v1/policies`, { headers });
await fetch(`${apiUrl}/api/v1/policies/${policyId}`, { headers });
await fetch(`${apiUrl}/api/v1/policies/${policyId}`, { method: "DELETE", headers });
```

---

### 6. Permission Management

Permissions link an agent to a policy for a defined period. On-chain, `PolicyRegistry.grantPermission()` registers the link. `PermissionEnforcer` reads active permissions during `validateUserOp`.

**On-chain (direct):**

```solidity
// Grant permission on-chain
bytes32 permissionId = policyRegistry.grantPermission(
    agentAddress,   // The smart account address
    policyId,       // bytes32 policy identifier
    validFrom,      // uint256 unix timestamp
    validUntil      // uint256 unix timestamp
);
```

**Revoke on-chain:**

```solidity
policyRegistry.revokePermission(permissionId);
```

**Via API (handles on-chain registration + constraint sync to PermissionEnforcer):**

```javascript
const apiUrl = process.env.GUARDRAIL_API_URL ?? "https://agentguardrail.xyz";
const headers = {
  "Content-Type": "application/json",
  Authorization: `Bearer ${process.env.GUARDRAIL_DASHBOARD_API_KEY}`,
};

// Grant a permission
const permission = await fetch(`${apiUrl}/api/v1/permissions`, {
  method: "POST",
  headers,
  body: JSON.stringify({
    agent_id: "agent-uuid",
    policy_id: "policy-uuid",
    valid_from: "2026-01-01T00:00:00Z",
    valid_until: "2026-12-31T23:59:59Z",
  }),
}).then((r) => r.json());

// Mint it on-chain (registers in PolicyRegistry, syncs constraints to PermissionEnforcer)
const minted = await fetch(`${apiUrl}/api/v1/permissions/${permission.id}/mint`, {
  method: "POST",
  headers,
}).then((r) => r.json());
// minted.onchain_token_id — the on-chain token ID

// Revoke
await fetch(`${apiUrl}/api/v1/permissions/${permission.id}`, { method: "DELETE", headers });

// List (filter by agent or policy)
await fetch(`${apiUrl}/api/v1/permissions?agent_id=${agentId}`, { headers });
```

> Use the API path when you need the `PermissionEnforcer` constraints to sync automatically. The direct contract path is sufficient if you are managing `PermissionEnforcer` constraint updates yourself.

---

### 7. Action Validation

**On-chain enforcement (primary):**

Validation happens automatically inside `AgentSmartAccount.validateUserOp()` via `PermissionEnforcer`. You do not call this directly — it runs as part of every UserOperation. Transactions that violate policy constraints revert before execution.

**Off-chain pre-flight (via API — useful for dashboards, simulation, agent planning):**

```javascript
const apiUrl = process.env.GUARDRAIL_API_URL ?? "https://agentguardrail.xyz";

// Pre-flight check before building a UserOperation
const result = await fetch(`${apiUrl}/api/v1/validate`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${process.env.GUARDRAIL_DASHBOARD_API_KEY}`,
  },
  body: JSON.stringify({
    agent_id: "agent-uuid",
    action: {
      type: "swap",
      token: "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
      protocol: "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
      amount: "500000000000000000",
      chain: 8453,
      to: "0xDef1C0ded9bec7F1a1670819833240f027b25EfF",
    },
  }),
}).then((r) => r.json());
// result.allowed        — boolean
// result.reason         — explanation if denied
// result.permission_id  — matching permission
// result.policy_id      — matching policy
// result.constraints    — active constraints
// result.request_id     — audit trail reference
```

**Simulate (dry-run, no audit record):**

```javascript
const sim = await fetch(`${apiUrl}/api/v1/validate/simulate`, {
  method: "POST",
  headers: { "Content-Type": "application/json", Authorization: `Bearer ${process.env.GUARDRAIL_DASHBOARD_API_KEY}` },
  body: JSON.stringify({
    agent_id: "agent-uuid",
    action: { type: "transfer", amount: "1000000000000000000", chain: 1 },
  }),
}).then((r) => r.json());
// sim.would_allow       — boolean
// sim.current_usage     — current period usage
// sim.remaining_quota   — remaining allowance
// sim.recommendations   — suggested policy adjustments
```

**Batch validate:**

```javascript
// POST /api/v1/validate/batch
// Body: { actions: [...] }  — same structure as single validate
```

---

### 8. Audit & Monitoring

**On-chain events (source of truth):**

The AgentGuardrail indexer polls contracts every 12 seconds and writes events to the audit log with `tx_hash` and `block_number`. Events emitted by the contracts:

| Event | Contract | Description |
|-------|----------|-------------|
| `EnforcementResult` | PermissionEnforcer | Every validateUserOp result |
| `ConstraintViolation` | PermissionEnforcer | Policy constraint breached |
| `UsageRecorded` | PermissionEnforcer | Spend/volume tracked |
| `Executed` | AgentSmartAccount | Transaction executed |
| `AccountCreated` | AgentAccountFactory | New smart account deployed |

**Query via API:**

```javascript
const apiUrl = process.env.GUARDRAIL_API_URL ?? "https://agentguardrail.xyz";

// List audit logs
const logs = await fetch(
  `${apiUrl}/api/v1/audit?agent_id=${agentId}&source=onchain&start_date=2026-01-01T00:00:00Z`,
  { headers: { Authorization: `Bearer ${process.env.GUARDRAIL_DASHBOARD_API_KEY}` } }
).then((r) => r.json());
// Each log entry includes: source ('onchain'|'offchain'), tx_hash, block_number, event_type

// Filter by source
// source=onchain   — events from contract indexer (tx_hash + block_number included)
// source=offchain  — API validation requests

// Export (JSON or CSV)
const csvUrl = `${apiUrl}/api/v1/audit/export?format=csv&start_date=2026-01-01T00:00:00Z`;
```

Event types: `policy.created`, `policy.activated`, `policy.revoked`, `permission.created`, `permission.minted`, `permission.revoked`, `validation.request`.

---

## Enforcement Model

All agents are **ERC-4337 smart accounts with enforced on-chain policy enforcement**. There is no advisory or EOA mode.

`AgentSmartAccount.validateUserOp()` calls `PermissionEnforcer` on every UserOperation. Transactions that violate policy constraints revert before execution. The agent cannot bypass enforcement — it is built into the account's validation logic.

Off-chain validation (`/api/v1/validate`) runs as a pre-flight simulation for dashboards, SDK use, and agent planning. The on-chain `PermissionEnforcer` performs the final, authoritative enforcement.

---

## Recommended Setup Flow

```
1. Deploy smart account (AgentAccountFactory.createAccount)
2. Create policy (API) → activate (registers on-chain via PolicyRegistry)
3. Grant permission (API) → mint (syncs constraints to PermissionEnforcer)
4. Agent builds UserOperations — enforcement is automatic
5. Monitor via audit logs or on-chain events
```

---

## Autonomy & Safety Guidance

1. **Start on Sepolia.** All contract addresses are provided above.
2. Fund accounts with small amounts while validating policies.
3. Use strict policies — prefer explicit token/protocol allowlists over wildcards.
4. Enable autonomous execution only with secure signing configured.
5. Apply rate limits and allowlists at the signer layer as a second line of defense.

---

## Privacy and Data Handling

- This skill does not store, log, or transmit private keys, seed phrases, or signer tokens.
- `GUARDRAIL_RPC_URL` may contain an embedded API key. Treat it as sensitive.
- `GUARDRAIL_SIGNER_AUTH_TOKEN` grants signing capability. Store in secure secret storage — never expose in logs, prompts, or chat.
- On-chain transactions are public by nature. The skill adds no off-chain data collection beyond what the blockchain records.
- The skill does not access local files, browser storage, or environment variables beyond those declared in the manifest.

---

## Design Principles

1. **Contract-first** — All enforcement is on-chain. The API is a convenience layer, not the authority.
2. **Policy-bound by default** — Every account is bound to a policy at creation. No account is unconstrained.
3. **Non-custodial** — AgentGuardrail never holds funds. Enforcement lives in contracts you can verify.
4. **Least privilege** — Signing must use scoped, secure integrations. Never expose long-lived owner keys.
5. **Agent and human neutral** — Authority derives from ownership and policy, not caller identity.
6. **Infrastructure-grade fees** — Fees are enforced at the contract layer. No software bypass exists.

---

## Dashboard

All operations are available via the web dashboard at **https://agentguardrail.xyz** — manage agents, policies, permissions, and audit logs visually. API keys and bot signer keypairs generated by the dashboard should be stored in secure secret storage and never pasted into chat.
