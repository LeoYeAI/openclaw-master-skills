---
name: safelink
description: Secure agent-to-agent hiring and execution skill for OpenClaw MCP with escrowed settlement, x402 facilitator payments, ERC-8004 identity/reputation checks, strict replay protection, DNS-safe endpoint validation, and MPC wallet signing. Use when building or operating production A2A workflows that require proof-before-settlement, policy gating, risk-scored transactions, and beginner-friendly wallet setup.
license: MIT
compatibility: "Node.js >= 20. Foundry (forge) required for one-time contract deployment only — not needed at MCP runtime."
metadata:
  author: charliebot8888
  version: "0.1.1"
  required_env: "BASE_RPC_URL (Base RPC endpoint), ERC8004_REGISTRY_ADDRESS (after deploy), SAFE_ESCROW_ADDRESS (after deploy), X402_FACILITATOR_URL (default: https://x402.org/facilitator)"
  required_env_wallet: "One of: COINBASE_CDP_API_KEY_NAME + COINBASE_CDP_API_KEY_PRIVATE_KEY (Coinbase AgentKit) OR PRIVY_APP_ID + PRIVY_APP_SECRET (Privy MPC). Both are MPC providers — private keys never enter app memory."
  required_env_llm: "ANTHROPIC_API_KEY (when LLM_PROVIDER=anthropic, default) OR LLM_BASE_URL + LLM_API_KEY (when LLM_PROVIDER=openai_compatible)"
  optional_env: "REDIS_URL (multi-instance replay store), TENDERLY_ACCESS_KEY (simulation), BASESCAN_API_KEY (explorer), TASK_AUTH_SHARED_SECRET (>=32 chars, when TASK_AUTH_REQUIRED=true), SIWX_VERIFIER_URL (when SIWX_REQUIRED=true), AUTONOMYS_RPC_URL (memory checkpoints)"
  deploy_only_env: "DEPLOYER_PRIVATE_KEY — used once by scripts/deploy-contracts.ts to deploy on-chain contracts. NOT loaded at MCP runtime. Use a throwaway funded key; discard after deployment."
  runtime_network: "Opens HTTP server on TASK_SERVER_PORT (default 3402, bound to 127.0.0.1) only when safe_listen_for_hire tool is called."
  runtime_files: "scripts/generate-env.ts writes .env interactively on first setup. scripts/deploy-contracts.ts writes deployed contract addresses back to .env after one-time deployment. Neither runs automatically."
  security_test_note: "tests/stress/ files contain literal prompt-injection strings (e.g. Ignore all previous instructions) as adversarial test fixtures to verify the input-gate blocks them. These are not instructions."
  homepage: "https://github.com/charliebot8888/SafeLink"
  repository: "https://github.com/charliebot8888/SafeLink"
---

# SafeLink

Production-grade OpenClaw skill for safe bidirectional hire-agent and execute-agent flows.

## Brand and Discovery

`SafeLink` is designed for trusted agent economies:

- tagline: `Secure A2A hiring, settled by proof`
- target users: OpenClaw developers, MCP operators, agent marketplaces
- recommended ClawHub tags:
  - `security`
  - `web3`
  - `a2a`
  - `payments`
  - `escrow`
  - `x402`
  - `erc-8004`
  - `agentic-wallet`
  - `mcp`
  - `production`

## Design Goals

- Default-safe operations with explicit escalation for risk.
- Zero private key exposure through MPC wallet providers.
- Proof-before-settlement: no proof, no release.
- Deterministic validation and replay defenses.
- Fast onboarding: one-call wallet setup and beginner-safe examples.

## Security Guarantees

SafeLink enforces the following guarantees in runtime code paths:

1. Wallet custody
- Private keys are never loaded into app memory.
- Signing is delegated to Coinbase AgentKit MPC or Privy MPC.

2. Settlement safety
- Escrow deposit happens before task execution.
- Release requires proof hash equality with on-chain commitment.
- Failed delivery and invalid proofs trigger refund path.

3. Replay and race protection
- Receipt replay reservation/used state is enforced.
- Idempotency lock prevents concurrent duplicates.
- Completed idempotency keys are blocked for reuse (terminal dedupe window).

4. Input and endpoint hardening
- Strict zod validation on tool inputs.
- PII redaction for task and intent text.
- Endpoint URL checks include scheme, hostname denylist, private IP range checks, and DNS resolution checks to prevent SSRF pivots.

5. Transaction execution safety
- Simulate before signing.
- Risk score and flags decide gating path.
- High-risk actions require explicit confirmation.

## Industry Alignment Matrix

Reference themes: x402 v2 facilitator model, ERC-8004 reputation/verification tiers, proof-before-settlement, cryptoeconomic reputation, opaque A2A execution, gas-aware risk controls, zkML/TEE extensibility.

- x402 facilitator flow: `Partially covered`
  - covered: requirements/pay/verify flows, domain checks, timeout handling
  - gap: SIWx auth binding, batch settlement primitive, sponsored gas ergonomics
- ERC-8004 base identity/reputation: `Covered`
  - covered: register, getAgent, active checks, threshold gating
  - gap: tiered verification fields and verifier lifecycle
- Proof-before-settlement: `Covered`
  - covered: deterministic proof commitment and strict on-chain proof match
- Reputation cryptoeconomics: `Partially covered`
  - covered: escrow success/failure reputation updates, minimum threshold checks
  - gap: robust Sybil graph scoring, stake/slash challenge economics
- A2A opaque execution: `Partially covered`
  - covered: minimal metadata task payload and policy gates
  - gap: encrypted envelope mode and selective disclosure controls
- Gas and DoS hardening: `Partially covered`
  - covered: simulation gas checks, request body limits, concurrency cap, timeout controls
  - gap: adaptive rate control, weighted queues, quota market controls
- zkML/TEE hooks: `Partially covered`
  - covered: tool fields and hook placeholders
  - gap: real attestation verification and circuit verifier integration

## Tool Contract (Production)

### `setup_agentic_wallet`

Purpose: Create or load an MPC wallet and return balance/network readiness.

Parameters:

- `provider` (optional): `"auto" | "coinbase" | "privy"`
  - `auto`: choose Coinbase when available, else Privy

Returns:

```json
{
  "provider": "coinbase",
  "wallet_id": "wallet_...",
  "address": "0x...",
  "eth_balance": "0.120000 ETH",
  "usdc_balance": "12.50 USDC",
  "network": "base-sepolia",
  "network_id": 84532,
  "ready": true,
  "setup_note": "optional"
}
```

Safety notes:

- Never return secrets.
- If user selects a provider explicitly, honor that choice.
- Fail with actionable configuration guidance.

Example:

```json
{
  "tool": "setup_agentic_wallet",
  "arguments": { "provider": "auto" }
}
```

### `safe_hire_agent`

Purpose: Hire one agent with escrow + x402 + proof verification.

Parameters:

- `target_id`: `0x...` agent address
- `task_description`: text task
- `payment_model`: `"per_request" | "per_min" | "per_execution"`
- `rate`: number USDC
- `idempotency_key` (optional): dedupe key
- `policy` (optional): runtime constraints
- `confirmed` (optional): explicit high-risk confirmation

Returns:

```json
{
  "task_id": "...",
  "escrow_id": "0x...",
  "result": {},
  "proof_hash": "0x...",
  "status": "completed",
  "reputation_score_at_hire": 82,
  "amount_paid_usdc": 0.05,
  "idempotency_key": "hire-..."
}
```

Safety notes:

- Blocks low-reputation targets.
- Enforces strict endpoint validation including DNS/IP checks.
- Refuses invalid proofs and refunds escrow.

Example:

```json
{
  "tool": "safe_hire_agent",
  "arguments": {
    "target_id": "0xabc123...",
    "task_description": "Summarize this PR and list top 3 security risks.",
    "payment_model": "per_request",
    "rate": 0.05,
    "idempotency_key": "hire-pr-2026-03-05"
  }
}
```

### `safe_execute_tx`

Purpose: Intent-to-transaction execution pipeline with mandatory simulation and risk gating.

Parameters:

- `intent_description`: plain-English tx intent
- `confirmed` (optional): high-risk confirmation

Returns:

```json
{
  "tx_hash": "0x...",
  "simulation_report": {
    "success": true,
    "gas_estimate": "142331"
  },
  "risk_score": 24,
  "risk_flags": ["HIGH_GAS"],
  "status": "broadcast"
}
```

Safety notes:

- Never sign when simulation fails.
- Never bypass confirmation for high-risk score.

Example:

```json
{
  "tool": "safe_execute_tx",
  "arguments": {
    "intent_description": "Approve 5 USDC to escrow contract 0x... on Base Sepolia"
  }
}
```

### `safe_listen_for_hire`

Purpose: Start local HTTP receiver for inbound paid tasks.

Parameters:

- none

Returns:

```json
{
  "status": "listening",
  "message": "Agent ... is now accepting hire requests ...",
  "tasks_processed": 0,
  "endpoint": "http://127.0.0.1:8787/task"
}
```

Safety notes:

- Verifies payment receipt before executing work.
- Rejects malformed session IDs and invalid amount values.
- Uses bounded concurrency and body size limits.

Example:

```json
{
  "tool": "safe_listen_for_hire",
  "arguments": {}
}
```

## Additional Tools

- `safe_hire_agents_batch`: batch hires with bounded concurrency and failure policy
- `safe_register_as_service`: publish capabilities/policy to registry
- `verify_task_proof`: validate proof locally and optionally against escrow record
- `get_agent_reputation`: fetch and evaluate target reputation profile
- `generate_agent_card`: produce JSON and markdown profile artifacts
- `checkpoint_memory`: encrypted memory checkpoint + Merkle anchoring
- `agent_analytics_summary`: period metrics and operations summary

## One-Click Setup

1. Install and configure env:

```bash
npm install
npm run setup
```

2. Build and start MCP server:

```bash
npm run build
npm start
```

3. First call from host:

```json
{
  "tool": "setup_agentic_wallet",
  "arguments": { "provider": "auto" }
}
```

## Security-Focused Examples

### Example: Safe hire with deterministic idempotency

```ts
await agent.call("safe_hire_agent", {
  target_id: "0xabc123...",
  task_description: "Analyze the staking contract for reentrancy and auth flaws.",
  payment_model: "per_request",
  rate: 0.08,
  idempotency_key: "audit-staking-v1-2026-03-05"
});
```

### Example: Escalation flow for high-risk tx

```ts
const firstTry = await agent.call("safe_execute_tx", {
  intent_description: "Upgrade proxy at 0x... to implementation 0x..."
});

// If approval required, call again:
await agent.call("safe_execute_tx", {
  intent_description: "Upgrade proxy at 0x... to implementation 0x...",
  confirmed: true
});
```

## Key TypeScript Skeletons

### `setup_agentic_wallet`

```ts
export async function setup_agentic_wallet(rawInput: unknown) {
  const input = validateInput(WalletSchema, rawInput);
  const wallet = await getMPCWalletClient(resolveProvider(input.provider));
  const [eth, usdc, chainId] = await Promise.all([
    publicClient.getBalance({ address: wallet.address }),
    getUSDCBalance(wallet.address, resolveNetwork()),
    publicClient.getChainId()
  ]);

  return formatWalletReady(wallet, eth, usdc, chainId);
}
```

### `safe_hire_agent`

```ts
export async function safe_hire_agent(rawInput: unknown): Promise<HireResult> {
  const input = validateInput(HireSchema, rawInput);
  const key = deriveOrUseIdempotencyKey(input);
  await acquireIdempotencyLock(key);

  try {
    const rep = await assertReputation(input.target_id);
    const commitment = computeProofCommitment(session.id, input.target_id);
    const escrow = await depositEscrow(...);
    const payment = await sendX402Payment(...);
    const task = await deliverTaskToAgentStrict(...);

    if (!verifyProof(task.proof_hash, session.id, input.target_id)) {
      await refundEscrow(escrow.escrowId);
      throw new ProofVerificationError(task.proof_hash);
    }

    await releaseEscrow(escrow.escrowId, task.proof_hash);
    await markIdempotencyCompleted(key);
    return buildHireResult("completed", ...);
  } catch (e) {
    await attemptRefundIfNeeded();
    throw e;
  } finally {
    await releaseIdempotencyLock(key);
    await destroySession(session.id);
  }
}
```

### `safe_execute_tx`

```ts
export async function safe_execute_tx(rawInput: unknown): Promise<ExecuteTxResult> {
  const input = validateInput(ExecuteTxSchema, rawInput);
  const parsed = await intentToTransaction(input.intent_description);
  const simulation = await simulateTx(parsed);

  if (!simulation.success) return simulationFailed(simulation);

  const { score, flags } = await scoreRisk(simulation);
  enforceApprovalGate(score, flags, input.confirmed, simulation);

  const wallet = await getMPCWalletClient();
  const txHash = await wallet.sendTransaction(toTxRequest(parsed, simulation));
  return buildExecuteResult(txHash, simulation, score, flags);
}
```

### `safe_listen_for_hire`

```ts
export async function safe_listen_for_hire(): Promise<ListenResult> {
  const server = await startTaskServer(getConfig().TASK_SERVER_PORT);
  return {
    status: "listening",
    message: `Register capability endpoint:${server.address}/task`,
    tasks_processed: 0,
    endpoint: `${server.address}/task`
  };
}
```

## Recommended New Tools (Next Iteration)

- `safe_verify_attestation`
  - verify TEE quotes and zkML proofs against approved verifier sets
- `safe_challenge_settlement`
  - submit challenge evidence for disputed task proofs
- `safe_rate_limit_admin`
  - runtime quotas and payer-level controls

## Recommended Config Additions

- `SAFE_ENDPOINT_ALLOWLIST`: allowed destination domains for outbound A2A calls
- `MAX_INBOUND_AMOUNT_ATOMIC_USDC`: hard cap on inbound job value
- `IDEMPOTENCY_COMPLETED_TTL_MS`: terminal dedupe window
- `SIWX_REQUIRED`: require SIWx signature binding for paid task requests
- `ENABLE_OPAQUE_ENVELOPE`: encrypted A2A payload mode

## Security Disclosure

- **Required environment variables**: `ANTHROPIC_API_KEY` (LLM), `BASE_RPC_URL`, and one of Privy (`PRIVY_APP_ID` + `PRIVY_APP_SECRET`) or Coinbase CDP (`COINBASE_CDP_API_KEY_NAME` + `COINBASE_CDP_API_KEY_PRIVATE_KEY`) for MPC wallet signing. Full list in `.env.example` and `_meta.json`.
- **`DEPLOYER_PRIVATE_KEY`**: Used **once** by `scripts/deploy-contracts.ts` for initial on-chain contract deployment only. Not loaded at MCP runtime. Use a throwaway funded key; discard after deployment.
- **HTTP listener**: `safe_listen_for_hire` opens an HTTP server on `TASK_SERVER_PORT` (default 3402), bound to `127.0.0.1` unless explicitly reconfigured.
- **File writes**: `scripts/deploy-contracts.ts` writes deployed contract addresses back to `.env`. `scripts/generate-env.ts` creates `.env` interactively. Neither runs automatically on MCP startup.
- **External CLI** (`forge`): Used by `scripts/deploy-contracts.ts` for one-time Solidity contract compilation and deployment only. Not required or invoked at MCP runtime.
- **Test files**: `tests/stress/` contains literal prompt-injection strings (e.g. `Ignore all previous instructions`) as adversarial test fixtures that verify the input-gate blocks them. These are not instructions to any agent.

## Changelog

- `v0.1.1` (2026-03-05)
  - added `_meta.json` with full required env vars, binaries, runtime behavior, and security disclosure for registry scanners
  - added clarifying headers to stress test files to prevent false-positive prompt-injection scanner alerts
  - upgraded `x402` to `^1.1.0` (fixes GHSA-3j63-5h8p-gf7c)

- `v0.1.0` (2026-03-05)
  - initial public release
  - strict endpoint DNS/IP validation for outbound task delivery
  - HMAC-signed inbound task auth with nonce replay lock and SIWx hook
  - completion-state idempotency protection blocks post-completion duplicates
  - `/.well-known/agent-card.json` HTTP endpoint
  - 128 unit tests, zero TypeScript errors, CI coverage gates enforced

## Roadmap

1. Complete x402 v2 alignment
- SIWx auth binding
- batch payment primitive
- optional sponsored gas support

2. ERC-8004 tiered verification
- tier metadata (`basic`, `tee_attested`, `zkml_attested`, `stake_secured`)
- verifier registries and revocation handling

3. Cryptoeconomic reputation hardening
- Sybil graph scoring
- challenge/slash dispute mechanisms

4. Opaque A2A execution
- encrypted task/result envelopes
- selective metadata disclosure

5. Production SRE posture
- adaptive rate limits
- weighted queues
- audit log export and incident hooks
