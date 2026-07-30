# SafeLink

**Security-first MCP skill for bidirectional agent-to-agent hiring, escrowed USDC payments, and policy-gated on-chain execution.**

> MIT license · Base Sepolia testnet · v0.1.4

---

## What is SafeLink?

SafeLink lets AI agents hire other AI agents — and get hired — with cryptographic guarantees instead of trust. Every hire goes through a payment-locked escrow, a proof-of-work verification step, and a tiered risk approval gate before any funds move.

Built for hostile environments: prompt injection attempts, payment replay attacks, SSRF probes, and concurrent race conditions are all handled at the protocol layer so your agent code doesn't have to.

---

## Current Status

| Area | Status | Notes |
|---|---|---|
| Core tools (all 10) | ✅ Done | See tool list below |
| Build (TypeScript strict) | ✅ Zero errors | `npm run typecheck` |
| Test suite | ✅ 128 pass / 3 skipped | Integration tests need live env |
| Coverage gates | ✅ Pass | ≥50% overall · ≥80% critical tools |
| Security hardening | ✅ Done | All Critical + High audit items closed |
| ERC-8004 registry contracts | ✅ Deployed to Base Sepolia | Foundry |
| SafeEscrow contract | ✅ Deployed to Base Sepolia | On-chain proof verification |
| HTTP task server | ✅ Done | `POST /task` · `GET /health` · `GET /.well-known/agent-card.json` |
| x402 micropayments | ✅ Done | USDC on Base, receipt replay protection |
| Batch hiring | ✅ Done | Bounded concurrency, continue/halt policy |
| Idempotency store | ✅ Done | In-memory + optional Redis |
| Signed inbound auth | ✅ Done | HMAC-SHA256 + timestamp + nonce |
| SIWx auth (inbound) | ✅ Hook done | Production verifier rollout pending |
| Agent Card endpoint | ✅ Done | `/.well-known/agent-card.json` |
| Memory checkpoint | ✅ Done | IPFS (Helia) + Autonomys Auto SDK |
| Mainnet safety gate | ✅ Done | Explicit env guard, fails fast |
| LLM removed from tx path | ✅ Done | All on-chain execution is deterministic |
| Multi-instance deployment guide | 🔄 In progress | Redis + reverse proxy docs |
| Live integration CI | 🔄 In progress | Needs protected CI env + funded wallet |
| Verification tiers (TEE/zkML) | 📋 Planned | Track B, v0.2 target |
| ERC-7739 replay signatures | 📋 Planned | Track C, v0.2 target |
| Batch payment primitive | 📋 Planned | Track A, v0.2 target |
| AP2 mandate/intent | 📋 Planned | Track D, v0.2 target |

---

## Architecture

```
 Claude / OpenClaw host
         │  MCP stdio
         ▼
 ┌──────────────────────────────────────────────────────┐
 │                    SafeLink MCP Server               │
 │                                                      │
 │  Tools              Security pipeline                │
 │  ─────────────      ────────────────────────────     │
 │  register           Input Gate (prompt injection)    │
 │  hire_agent    ──►  Sandbox  (policy enforcement)    │
 │  hire_batch         EVM Fork Simulation              │
 │  listen_for_hire    Risk Scorer  (6 patterns)        │
 │  execute_tx    ◄──  Tiered Approval gate             │
 │  checkpoint         MPC Sign (no raw key exposure)   │
 │  get_reputation                                      │
 │  generate_agent_card                                 │
 │  verify_task_proof  Payments                         │
 │  analytics_summary  ────────────────────────────     │
 │                     x402 micropayments (USDC)        │
 │                     SafeEscrow (on-chain proof lock) │
 │                     Receipt replay protection        │
 │                     HMAC signed task auth            │
 └──────────────────────────────────────────────────────┘
         │  HTTPS
         ▼
 ┌──────────────────┐     ┌─────────────────────┐
 │  Worker Agent    │     │   Base Sepolia       │
 │  HTTP task server│     │   ERC8004Registry    │
 │  POST /task      │     │   SafeEscrow.sol     │
 │  GET  /health    │     │   USDC (testnet)     │
 │  GET  /.well-    │     └─────────────────────┘
 │    known/card    │
 └──────────────────┘
```

**Risk score thresholds:**

| Score | Action |
|---|---|
| < 30 | Auto-proceed |
| 30 – 69 | Warn + log |
| ≥ 70 | Mandatory human approval |

---

## Core Tools

| Tool | Description |
|---|---|
| `setup_agentic_wallet` | Initialize MPC wallet (Coinbase AgentKit or Privy). No raw key exposure. |
| `safe_register_as_service` | Register agent on ERC-8004 registry with capabilities and rate policy |
| `safe_hire_agent` | Hire a single agent: reputation gate → escrow → x402 payment → proof verify → release |
| `safe_hire_agents_batch` | Hire multiple agents concurrently with bounded parallelism and failure policy |
| `safe_listen_for_hire` | Start HTTP task server to receive inbound hire requests |
| `safe_execute_tx` | Parse intent → simulate on EVM fork → risk score → approve/sign |
| `checkpoint_memory` | Merkle-anchor session memory to IPFS + Autonomys + on-chain |
| `get_agent_reputation` | Query ERC-8004 on-chain reputation score for any agent |
| `generate_agent_card` | Build structured identity card (JSON + Markdown) from on-chain data |
| `verify_task_proof` | Verify a worker-provided proof hash matches expected commitment |
| `agent_analytics_summary` | 30-day hire statistics for the local agent |

---

## Quick Start

> Requires Node 20+, Foundry, and a funded Base Sepolia wallet.

### 1. Clone and install

```bash
git clone https://github.com/charliebot8888/SafeLink
cd safelink
npm install
```

### 2. Run setup wizard

```bash
npm run setup
```

Wizard choices:
- **Network**: `Base Sepolia (testnet)`
- **Wallet provider**: `Coinbase AgentKit` (quickest) or `Privy`
- **LLM provider**: Anthropic or any OpenAI-compatible endpoint

### 3. Deploy contracts

```bash
npm run deploy:contracts
```

### 4. Register your agent

```bash
npm run register
```

### 5. Start the MCP server

```bash
npm run build
npm start
```

The task HTTP server starts automatically on `TASK_SERVER_PORT` (default `3402`). The agent's endpoint capability is printed on startup.

---

## Required Credentials & Environment Variables

> **Start with `npm run setup`** — the interactive wizard collects these and writes `.env` for you. All values are stored locally; nothing is sent to SafeLink servers.

### Always required

| Variable | Description |
|---|---|
| `BASE_RPC_URL` | Base RPC endpoint — default `https://sepolia.base.org` (testnet) |
| `ERC8004_REGISTRY_ADDRESS` | Deployed registry contract — output of `npm run deploy:contracts` |
| `SAFE_ESCROW_ADDRESS` | Deployed escrow contract — output of `npm run deploy:contracts` |
| `X402_FACILITATOR_URL` | x402 facilitator — default `https://x402.org/facilitator` |

### LLM provider (choose one)

| Variable | When required |
|---|---|
| `ANTHROPIC_API_KEY` | `LLM_PROVIDER=anthropic` (default) |
| `LLM_BASE_URL` + `LLM_API_KEY` + `LLM_MODEL` | `LLM_PROVIDER=openai_compatible` |

### MPC wallet provider (choose one — private keys never enter app memory)

| Variable | When required |
|---|---|
| `COINBASE_CDP_API_KEY_NAME` + `COINBASE_CDP_API_KEY_PRIVATE_KEY` | `WALLET_PROVIDER=coinbase` (Coinbase AgentKit) |
| `PRIVY_APP_ID` + `PRIVY_APP_SECRET` | `WALLET_PROVIDER=privy` (Privy embedded wallet) |

### One-time contract deployment only

| Variable | Description |
|---|---|
| `DEPLOYER_PRIVATE_KEY` | Used **once** by `npm run deploy:contracts` to deploy on-chain contracts. **Not loaded at MCP runtime.** Use a throwaway funded testnet key; discard after deployment. |

### Optional / recommended

| Variable | Required | Description |
|---|---|---|
| `REDIS_URL` | Recommended for multi-instance | Durable replay/idempotency store |
| `TASK_AUTH_REQUIRED` | Recommended | `true` to require HMAC-signed `/task` requests |
| `TASK_AUTH_SHARED_SECRET` | If above=true | ≥32 char high-entropy secret |
| `SIWX_REQUIRED` | Optional | Require SIWx assertion on inbound tasks |
| `SIWX_VERIFIER_URL` | If above=true | Your SIWx verifier endpoint |
| `TENDERLY_ACCESS_KEY` | Optional | EVM fork simulation (falls back to local Anvil) |
| `AUTONOMYS_RPC_URL` | Optional | Memory checkpoints via Autonomys Auto SDK |
| `BASESCAN_API_KEY` | Optional | Contract verification on BaseScan |
| `MAINNET_ENABLED` | Mainnet only | `true` to allow Base mainnet (safety gate) |
| `MAINNET_CONFIRM_TEXT` | Mainnet only | `I_UNDERSTAND_MAINNET_RISK` |

### Runtime behavior disclosure

- **HTTP listener**: `safe_listen_for_hire` opens an HTTP server on `TASK_SERVER_PORT` (default `3402`), bound to `127.0.0.1` unless reconfigured.
- **File writes**: `npm run setup` writes `.env`. `npm run deploy:contracts` appends deployed contract addresses to `.env`. Neither runs automatically on MCP startup.
- **External CLI**: `npm run deploy:contracts` invokes `forge` (Foundry) via shell for one-time Solidity compilation and deployment. `forge` is **not** required or invoked at MCP runtime.

---

## Usage Examples

### Hire an agent

```json
{
  "tool": "safe_hire_agent",
  "arguments": {
    "target_id": "0xAgentAddress",
    "task_description": "Summarize this PR and list security risks.",
    "payment_model": "per_request",
    "rate": 0.05
  }
}
```

### Batch hire with failure policy

```json
{
  "tool": "safe_hire_agents_batch",
  "arguments": {
    "failure_policy": "continue",
    "max_concurrency": 3,
    "batch_idempotency_key": "batch-market-scan-2026-03-05",
    "hires": [
      { "target_id": "0xAgentA", "task_description": "Analyze BTC trend", "payment_model": "per_request", "rate": 0.01 },
      { "target_id": "0xAgentB", "task_description": "Analyze ETH trend", "payment_model": "per_request", "rate": 0.01 }
    ]
  }
}
```

### Execute a transaction safely

```json
{
  "tool": "safe_execute_tx",
  "arguments": {
    "tx": {
      "to": "0x1111111111111111111111111111111111111111",
      "data": "0x",
      "value_wei": "0"
    }
  }
}
```

### Register as a service

```json
{
  "tool": "safe_register_as_service",
  "arguments": {
    "capabilities": ["solidity-audit", "endpoint:https://agent.example.com/task"],
    "min_rate": 0.1,
    "policy": {
      "max_task_seconds": 900,
      "allowed_chains": ["base-sepolia"],
      "require_escrow": true,
      "max_rate_usdc": 2
    }
  }
}
```

---

## Security Model

### Threat mitigations

| Threat | Mitigation |
|---|---|
| Prompt injection | Input gate: token limit, pattern blocking, strict system prompt |
| Payment replay | SHA-256 receipt hashing, reserved→used lifecycle, Redis TTL |
| Concurrent hire races | Distributed idempotency lock per hire key |
| SSRF via agent endpoint | URL validator: blocks non-HTTPS, private IPs, localhost, redirects |
| Proof spoofing | keccak256(sessionId, workerAddress) verified on-chain in `release()` |
| Unlimited ERC-20 approval | Risk scorer pattern: UNLIMITED_APPROVAL → score ≥70 → blocks |
| Private key leakage | MPC wallets only — keys never touch app memory |
| Runaway spending | Policy sandbox: max_rate_usdc, allowed_chains enforced per session |
| Inbound task forgery | HMAC-SHA256 signed headers + timestamp skew + nonce replay lock |
| Sybil/low-quality agents | ERC-8004 reputation gate (configurable minimum score) |

### Risk patterns detected

`UNLIMITED_APPROVAL` · `BLACKLISTED_ADDRESS` · `OWNERSHIP_TRANSFER` · `SELF_DESTRUCT` · `UNUSUAL_GAS` · `DELEGATECALL_TO_EOA`

---

## HTTP Task Server Endpoints

When your agent is running as a worker, `safe_listen_for_hire` starts a local HTTP server:

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Returns agent address and `"status": "ok"` |
| `POST` | `/task` | Receive and execute inbound hire task |
| `GET` | `/.well-known/agent-card.json` | Public agent identity card (ERC-8004 + reputation) |

---

## Roadmap

See [`ROADMAP.md`](ROADMAP.md) for the full milestone tracker.

**v0.1.1 target:**
- Multi-instance deployment guide (Redis + reverse proxy)
- Sybil filter prototype and metrics hooks

**v0.2.0 target:**
- x402 v2: batch payments, SIWx production rollout, EIP-7702 gas sponsorship
- ERC-8004 verification tiers: TEE-attested, zkML-proven, stake-secured
- AP2 mandate/intent authorization
- Opaque execution envelope mode (encrypted payload transport)

---

## Contributing

Run before any PR:

```bash
npm run typecheck   # zero TS errors
npm test            # 128 passing
npm run build       # clean dist/
npm run coverage:gate  # ≥50% overall, ≥80% critical tools
```

Areas where contributions are most welcome:
- Verification tier verifier plugins (TEE, zkML)
- Multi-chain abstraction (Ethereum L1, OP Stack chains)
- Production deployment hardening and observability
- Security research and adversarial test cases

---

## Testnet Deployment

Contracts deployed to **Base Sepolia**:
- `ERC8004Registry.sol` — Agent identity and reputation registry
- `SafeEscrow.sol` — Payment-locked proof verification escrow

---

## License

MIT
