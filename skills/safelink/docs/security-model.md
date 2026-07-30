# SafeChainAgent — Security Model

## Threat Model

SafeChainAgent operates in an adversarial environment where:

- **Malicious hiring agents** may submit tasks designed to exfiltrate secrets or execute harmful transactions
- **Malicious worker agents** may fail to deliver, deliver incorrect results, or attempt to claim payment without doing work
- **Compromised task descriptions** may contain prompt injection, PII, or attempts to override agent behavior
- **On-chain attackers** may submit crafted transactions designed to drain wallets or manipulate contracts

The security architecture is designed to be **zero-config safe by default**: the most dangerous actions are blocked before any signing or execution occurs.

---

## Defence Layers

```
Layer 1: Input Gate       — validate + sanitize before anything else
Layer 2: Sandbox          — enforce policy constraints on every call
Layer 3: EVM Simulation   — simulate before signing (never sign blind)
Layer 4: Risk Scoring     — block/warn based on detected threat patterns
Layer 5: Tiered Approval  — human-in-the-loop for high-risk actions
Layer 6: MPC Signing      — private keys split across HSMs, never exposed
Layer 7: Session Isolation — temporary contexts, auto-destroyed on completion
```

### Layer 1: Input Gate (`src/security/input-gate.ts`)

Every tool input passes through `validateInput()` before any business logic runs.

**PII stripping** — regex patterns detect and redact:
- Private keys and seed phrases (`0x` hex ≥ 32 bytes, 12/24-word mnemonics)
- API keys (common prefixes: `sk-`, `Bearer `, etc.)
- Email addresses
- Phone numbers
- Social Security Numbers
- Credit card numbers

**Schema validation** — Zod schemas enforce:
- EVM addresses: `/^0x[a-fA-F0-9]{40}$/`
- USDC rates: 0–100 USDC
- Task descriptions: max 2000 chars, PII-free
- Capabilities: max 20 items, no private keys in strings

Validation runs with `exactOptionalPropertyTypes: true` — absent fields are never treated as `undefined` when not explicitly declared optional.

### Layer 2: Sandbox (`src/security/sandbox.ts`)

Per-call policy enforcement before any network calls:

| Policy field | Default | Description |
|---|---|---|
| `max_task_seconds` | 300 | Hard timeout for task execution |
| `allowed_chains` | `["base-sepolia"]` | Whitelist of acceptable chain IDs |
| `require_escrow` | `true` | Block payments without escrow |
| `max_rate_usdc` | 10 USDC | Maximum single payment |

Violations throw `ValidationError` before any funds move.

### Layer 3: EVM Simulation (`src/security/simulation.ts`)

**All transactions are simulated before signing** — the agent never signs a transaction it hasn't first seen the effects of.

Simulation flow:
1. **Tenderly API** (if `TENDERLY_ACCESS_KEY` set) — full state trace with approval events, delegate calls, event logs, and opcode-level analysis
2. **viem `eth_call` fallback** — simulates via `call` on the public client when Tenderly is unavailable

Simulation returns a `SimulationReport`:
```typescript
{
  success: boolean,
  revertReason?: string,
  gasUsed: bigint,
  approvals: { spender, amount }[],     // ERC-20 Approval events
  delegateCalls: { target }[],           // DELEGATECALL targets
  eventLogs: { topic0, data }[],
  opcodes: string[],                     // Critical opcodes (SELFDESTRUCT etc)
}
```

This report feeds directly into the risk scorer.

### Layer 4: Risk Scoring (`src/security/risk-scorer.ts`)

Eight threat patterns are checked against the simulation report. Each pattern carries a weight:

| Pattern | Weight | Trigger |
|---|---|---|
| `UNLIMITED_APPROVAL` | 40 | ERC-20 approval ≥ 2^128 (max uint128) |
| `BLACKLISTED_ADDRESS` | 60 | `to` address on known scam/exploit list |
| `OWNERSHIP_TRANSFER` | 50 | `transferOwnership` or `renounceOwnership` call |
| `CONTRACT_UPGRADE` | 45 | `upgradeTo` / `upgradeToAndCall` detected |
| `SELF_DESTRUCT` | 80 | `SELFDESTRUCT` opcode in call trace |
| `DELEGATECALL_TO_EOA` | 70 | `DELEGATECALL` targeting a non-contract address |
| `HIGH_GAS` | 15 | Gas estimate > 500,000 |
| `ZERO_VALUE_LARGE_CALLDATA` | 20 | 0 ETH value + calldata > 1 KB |

**Score interpretation:**

| Score | Action |
|---|---|
| 0–29 | Auto-proceed (no user prompt) |
| 30–69 | Warn + log, proceed |
| 70–100 | Block — requires `confirmed: true` in tool args |

Scores are capped at 100. Multiple patterns stack additively.

### Layer 5: Tiered Approval (`src/security/approval.ts`)

For risk score ≥ 70, the agent cannot self-approve:

**CLI mode** (`MCP_SERVER` not set): prompts stdin with a structured summary of the detected risks. User must type `yes` to proceed.

**MCP mode** (`MCP_SERVER=1`): throws `ApprovalRequiredError` which serializes to a structured MCP tool response. Claude Desktop surfaces this as an actionable dialog — the user must re-invoke the tool with `confirmed: true`.

`ApprovalRequiredError.toMCPContent()` returns:
```json
{
  "approval_required": true,
  "risk_score": 75,
  "flags": ["UNLIMITED_APPROVAL", "BLACKLISTED_ADDRESS"],
  "message": "High-risk transaction detected...",
  "action_required": "Re-invoke with confirmed: true to proceed"
}
```

### Layer 6: MPC Signing (`src/wallet/mpc.ts`)

Private keys are **never stored, loaded, or exposed** in the agent process.

Transaction signing is delegated to **Privy's embedded wallet API**:
- Keys are split using MPC (multi-party computation) across Privy's HSMs
- The agent calls `privy.walletApi.ethereum.sendTransaction()` — Privy coordinates the signing ceremony remotely
- The agent process never sees a private key at any point

Wallet creation on first run stores only a `PRIVY_WALLET_ID` in `.env` — a non-sensitive handle to the wallet, not any key material.

### Layer 7: Session Isolation (`src/security/session.ts`)

Every tool invocation and every incoming HTTP task runs in a **temporary session**:

```typescript
const session = createTempSession({ tool: "safe_listen_for_hire" });
// ... do work ...
await destroySession(session.id); // always, even on error (try/finally)
```

`destroySession()` zeroes out all session context values before Map deletion, preventing memory scraping between tasks.

An auto-purge interval (every 5 minutes) cleans up sessions that were orphaned by crashes.

---

## Payment Security

### x402 Payment Flow

```
Hiring agent                        Worker agent
     │                                    │
     ├─► GET /capabilities (x402)         │
     │◄── 402 Payment Required ──────────│
     │    (payment requirements)          │
     ├─► Build EIP-712 USDC authorization │
     ├─► MPC sign authorization           │
     ├─► POST to x402 facilitator         │
     │◄── payment receipt ───────────────│
     ├─► POST /task + X-Payment-Receipt ─►│
     │                                    ├─ verifyX402Receipt()
     │                                    ├─ (task execution)
     │◄── { proof_hash, output } ────────│
```

The worker **always verifies the payment receipt before starting work**. An invalid or insufficient receipt returns HTTP 402 immediately.

### Escrow Safety

The `SafeEscrow.sol` contract provides trustless payment settlement:

1. Hirer deposits USDC into escrow before task delivery (`deposit()`)
2. Worker delivers task and returns `proof_hash = keccak256(sessionId + workerAddress)`
3. Hirer calls `release(escrowId, proofHash)` — the contract verifies the proof matches
4. If delivery fails or proof is invalid, hirer calls `refund()` after `expiry` timestamp

**Nobody can steal funds:**
- Only the hirer can call `release()` or `refund()`
- `release()` requires a valid proof hash — the hirer must have received a valid delivery
- `refund()` is time-locked to prevent instant cancellation after delivery

---

## Memory Security

Session memory checkpoints are encrypted before leaving the process:

1. `generateSessionKey()` — random 32-byte AES-256-GCM key
2. `encryptPayload(data, key)` — AES-256-GCM with random IV, returns `{ iv, ciphertext, authTag }`
3. `buildMerkleTree(entries)` — deterministic Merkle tree over memory entries
4. Upload ciphertext to IPFS + Autonomys (content-addressed, publicly retrievable — but encrypted)
5. Anchor Merkle root on-chain via `safe_execute_tx` — provides tamper-evident audit trail
6. Unless `persist_key: true`, key is zeroed with `destroyKey()` after anchoring

**Threat: Autonomys/IPFS data leak** — Mitigated. Ciphertext is useless without the AES key. Only the Merkle root (not the content) is on-chain.

**Threat: Merkle root tampering** — Impossible. The root is anchored in an on-chain transaction with MPC signature.

---

## Known Limitations

1. **Tenderly simulation** may miss state changes introduced by MEV or flashbots — simulation is best-effort, not a guarantee.
2. **Blacklist** in risk-scorer.ts uses a small hardcoded list. Production deployments should integrate an on-chain oracle (e.g. Chainabuse).
3. **HTTP task server** binds to `127.0.0.1` by default. To accept external connections, run behind a reverse proxy (nginx, Cloudflare Tunnel) and register the public URL as your `endpoint:` capability.
4. **Session keys in memory** — `destroyKey()` zeroes the buffer but JavaScript GC may have already copied the key elsewhere. A future hardening pass could use `SecureBuffer` patterns.
5. **Privy dependency** — If Privy's servers are unavailable, the agent cannot sign. Failover to local key management (with appropriate security trade-offs) is not yet implemented.
