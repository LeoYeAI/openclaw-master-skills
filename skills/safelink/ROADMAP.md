# SafeLink Roadmap

This roadmap tracks gap closure from `v0.1.x` toward production-grade `v0.2`.

## Status Legend

- `done`: implemented and tested
- `in_progress`: actively under development
- `planned`: not started

## Track A: Payments and Settlement

1. x402 v2 facilitator flow hardening - `done`
- Requirements/pay/verify flow
- Domain and token validation against chain config

2. Receipt replay protection - `done`
- Reserved/used receipt lifecycle
- Duplicate receipt rejection

3. Batch hiring and payment orchestration - `done`
- `safe_hire_agents_batch`
- Bounded concurrency and failure policy

4. Batch payment primitive (single call for multiple authorizations) - `planned`

5. SIWx auth integration - `in_progress` (verifier hook added; production verifier rollout pending)

6. EIP-7702 gas sponsorship adapter - `planned`

## Track B: Identity and Verification

1. ERC-8004 register/query/reputation basics - `done`

2. Verification tiers (`basic`, `tee_attested`, `zkml_attested`, `stake_secured`) - `planned`

3. TEE quote verifier plugin - `planned`

4. zkML proof verifier plugin - `planned`

5. Stake-secured re-execution challenge path - `planned`

## Track C: Security and Abuse Resistance

1. Prompt injection input hardening - `done`

2. SSRF protections for agent endpoints - `done`

3. Idempotency lock for duplicate hire calls - `done`

4. Durable distributed replay/idempotency store - `done` (Redis optional via `REDIS_URL`, memory fallback)

5. ERC-7739 replay-protected signature path - `planned`

6. Sybil filtering/indexing and graph heuristics - `planned`
7. Signed inbound task request auth (HMAC + timestamp + nonce replay lock) - `done`

## Track D: A2A Interop and Metadata

1. HTTP endpoint capability and task exchange - `done`

2. Agent Card JSON (`/.well-known/agent-card.json`) - `done`

3. Opaque execution envelope mode (encrypted payload transport) - `planned`

4. AP2 mandate/intent authorization support - `planned`

## Track E: Operations and DX

1. Mainnet explicit safety gate - `done`

2. Better setup UX and provider flexibility - `done`

3. Multi-instance deployment guide (Redis + reverse proxy) - `in_progress`

4. Performance profiling and gas benchmark report - `planned`

## Target Milestones

- Release Readiness TODO (Priority Order)
  - `done` P0: Raise test coverage for critical tool modules (target >= 85% on tools/security hot paths)
  - `done` P1: Add CI hard gate for coverage thresholds and skip-policy for critical suites
  - `in_progress` P2: Unskip live integration smoke tests in protected CI environment
  - `done` P3: Remove LLM dependency from deterministic on-chain anchor and tx intent execution paths
  - `in_progress` P4: Add SIWx auth binding and stronger inbound hire request authentication

- `v0.1.1`
  - Batch hire tool + replay/idempotency hardening
  - Dedicated roadmap and operator guidance updates

- `v0.1.2`
  - Multi-instance deployment docs
  - Sybil filter prototype and metrics hooks

- `v0.2.0`
  - x402 v2 completion (SIWx, 7702 sponsorship, batch payments)
  - ERC-8004 verification tiers and verifier hooks
  - AP2 + Agent Card support

