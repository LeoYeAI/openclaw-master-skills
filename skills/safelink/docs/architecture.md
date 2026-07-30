# SafeChainAgent — Architecture

## Overview

SafeChainAgent is an MCP (Model Context Protocol) skill that enables **bidirectional agent-hire-agent** interactions on the Base blockchain. Agents can register themselves as services, hire other agents, and receive hire requests — all with automated payments, escrow, and on-chain reputation.

```
┌─────────────────────────────────────────────────────────┐
│                   Claude Desktop / Claude Code           │
│                    (MCP host — stdio)                    │
└────────────────────────┬────────────────────────────────┘
                         │ MCP protocol (stdio)
                         ▼
┌─────────────────────────────────────────────────────────┐
│                     src/index.ts                         │
│               MCP Server (5 tools)                       │
├─────────┬──────────┬──────────┬───────────┬────────────┤
│register │  hire    │  listen  │ execute   │ checkpoint │
│         │          │          │    _tx    │  _memory   │
└────┬────┴────┬─────┴────┬─────┴─────┬─────┴─────┬──────┘
     │         │          │           │            │
     ▼         ▼          ▼           ▼            ▼
┌──────────────────────────────────────────────────────────┐
│                    Core Modules                           │
│                                                          │
│  security/   wallet/   payments/   registry/   memory/   │
│  ─────────   ───────   ─────────   ─────────   ───────   │
│  input-gate  mpc.ts    usdc.ts     erc8004.ts  ipfs.ts   │
│  simulation  provider  x402.ts     reputation  autonomys │
│  risk-scorer types.ts  escrow.ts               merkle.ts │
│  session.ts                                              │
│  approval.ts                                             │
│  sandbox.ts                                              │
└──────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────────┐
│                HTTP Task Server (port 3402)               │
│                  src/server/http.ts                       │
│                                                          │
│  POST /task   ← hiring agents deliver tasks here         │
│  GET  /health ← readiness probe                          │
└──────────────────────────────────────────────────────────┘
```

## Directory Structure

```
safechain-agent/
├── src/
│   ├── index.ts              # MCP server entry — 5 tools registered
│   ├── server/
│   │   └── http.ts           # HTTP task server (port 3402)
│   ├── tools/                # One file per MCP tool
│   │   ├── register.ts       # safe_register_as_service
│   │   ├── hire.ts           # safe_hire_agent
│   │   ├── listen.ts         # safe_listen_for_hire + processIncomingTask
│   │   ├── execute_tx.ts     # safe_execute_tx
│   │   └── checkpoint.ts     # checkpoint_memory
│   ├── security/
│   │   ├── input-gate.ts     # PII stripping, Zod schemas, input validation
│   │   ├── simulation.ts     # Off-chain EVM simulation (Tenderly + viem fallback)
│   │   ├── risk-scorer.ts    # 8 threat patterns → 0–100 risk score
│   │   ├── session.ts        # Temporary session lifecycle + auto-purge
│   │   ├── approval.ts       # Tiered human approval (stdin / MCP structured)
│   │   └── sandbox.ts        # Policy enforcement (rate limits, chain whitelist)
│   ├── wallet/
│   │   ├── types.ts          # MPCWallet interface
│   │   ├── mpc.ts            # Privy MPC wallet — private keys never exposed
│   │   └── provider.ts       # viem PublicClient (read-only)
│   ├── payments/
│   │   ├── usdc.ts           # USDC helpers, atomic conversions
│   │   ├── x402.ts           # x402 micropayment send + verify
│   │   └── escrow.ts         # SafeEscrow deposit / release / refund
│   ├── registry/
│   │   ├── erc8004.ts        # ERC-8004 agent registry read/write
│   │   └── reputation.ts     # Reputation fetch + assertion
│   ├── memory/
│   │   ├── ipfs.ts           # Helia in-process IPFS upload/download
│   │   ├── autonomys.ts      # Autonomys Auto Drive permanent storage
│   │   └── merkle.ts         # Merkle tree, AES-256-GCM encrypt/decrypt
│   └── utils/
│       ├── config.ts         # Zod env schema + getConfig() singleton
│       ├── logger.ts         # Structured JSON logger with PII redaction
│       └── errors.ts         # Typed error hierarchy
├── contracts/
│   ├── foundry.toml
│   ├── src/
│   │   ├── ERC8004Registry.sol
│   │   └── SafeEscrow.sol
│   ├── test/SafeEscrow.t.sol
│   └── script/Deploy.s.sol
├── tests/
│   ├── unit/
│   │   ├── input-gate.test.ts
│   │   ├── risk-scorer.test.ts
│   │   ├── merkle.test.ts
│   │   └── http-server.test.ts
│   └── integration/hire-flow.test.ts
└── scripts/
    ├── generate-env.ts       # Interactive setup wizard
    ├── deploy-contracts.ts   # Forge deploy → updates .env
    └── register-agent.ts     # ERC-8004 registration CLI
```

## Data Flow

### Hiring an Agent (`safe_hire_agent`)

```
Claude calls safe_hire_agent(target_id, task_description, payment_model, rate)
    │
    ├─1─► Input Gate: strip PII, validate Zod schema
    ├─2─► ERC-8004: check target agent is registered
    ├─3─► Reputation: assert score ≥ MIN_REPUTATION_SCORE (default 70)
    ├─4─► Sandbox: enforce policy (chains, rate limits)
    ├─5─► SafeEscrow: deposit USDC (simulate → risk-score → MPC sign)
    ├─6─► x402: send micropayment receipt to target's HTTP endpoint
    ├─7─► HTTP POST /task: deliver task to target agent
    ├─8─► Verify proof_hash returned by worker
    └─9─► SafeEscrow: release funds (if proof valid) or refund (on error)
```

### Receiving a Task (`safe_listen_for_hire` + `POST /task`)

```
Hiring agent sends POST /task to http://your-agent:3402/task
    │
    ├─1─► Validate headers: X-Payment-Receipt, X-Escrow-Id
    ├─2─► Validate body: task_description, payer, amount_atomic_usdc
    ├─3─► verifyX402Receipt() — abort if payment insufficient
    ├─4─► createTempSession() — isolated context
    ├─5─► defaultTaskExecutor() → Claude Haiku processes task
    ├─6─► keccak256(sessionId + agentAddress) → proof_hash
    ├─7─► destroySession() — always, even on error
    └─8─► Return { task_id, proof_hash, output }
```

### Executing a Transaction (`safe_execute_tx`)

```
Claude calls safe_execute_tx("Approve 50 USDC to contract 0x...")
    │
    ├─1─► Input Gate: validate, strip PII
    ├─2─► Claude Haiku: parse intent → { to, data, value }
    ├─3─► Simulation: Tenderly API (fallback: viem eth_call)
    ├─4─► Risk Scorer: 8 patterns → score 0–100
    │       score < 30 : auto-proceed
    │       score 30–69: warn + log
    │       score ≥ 70 : require confirmed: true
    ├─5─► Approval: stdin (CLI) or ApprovalRequiredError (MCP)
    └─6─► MPC sign + broadcast via Privy wallet
```

## Contracts

### ERC8004Registry.sol

On-chain agent registry. Each agent has:
- `address owner` — MPC wallet address
- `string[] capabilities` — e.g. `["code-review", "endpoint:https://..."]`
- `uint256 minRateAtomic` — minimum USDC per operation (6 decimals)
- `uint256 reputationScore` — 0–100, starts at 50, updated by SafeEscrow
- `uint256 registeredAt` — Unix timestamp
- `bool active`

### SafeEscrow.sol

Proof-gated USDC escrow:
- `deposit(worker, amount, expiry)` → `bytes32 escrowId`
- `release(escrowId, proofHash)` — hirer only, verifies `keccak256(sessionId + workerAddress)`, increments worker reputation +5
- `refund(escrowId)` — hirer only (after expiry), decrements worker reputation -5

## Security Boundaries

| Boundary | Protection |
|----------|-----------|
| User input | Zod validation + PII stripping in input-gate.ts |
| Transaction intent | EVM fork simulation before any signing |
| Sensitive data | Session isolation, auto-purge on completion |
| Private keys | Privy MPC — keys split across HSMs, never exposed |
| Payment proof | x402 receipt verified before task execution starts |
| Escrow release | keccak256 proof required, verified on-chain |
| Memory | AES-256-GCM encrypted, Merkle root anchored on-chain |

## Environment Variables

See `.env.example` for the complete list. Required at startup:
- `ANTHROPIC_API_KEY`
- `PRIVY_APP_ID` + `PRIVY_APP_SECRET`
- `BASE_RPC_URL`

Optional but recommended:
- `ERC8004_REGISTRY_ADDRESS` + `SAFE_ESCROW_ADDRESS` (populated by `npm run deploy:contracts`)
- `TENDERLY_ACCESS_KEY` (better simulation accuracy)
- `TASK_SERVER_PORT` (default: 3402)
