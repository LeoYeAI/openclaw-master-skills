# Network-AI Integration Guide

**For technical leads, solutions architects, and engineering teams evaluating or deploying Network-AI in a production environment.**

This guide walks from "we want this" to "it's running in production" — covering discovery, framework mapping, phased rollout, enterprise concerns, and validation.

---

## Table of Contents

1. [Before You Start — Discovery](#1-before-you-start--discovery)
2. [Framework Mapping](#2-framework-mapping)
3. [Primitive Mapping — What Solves What](#3-primitive-mapping--what-solves-what)
4. [Phased Rollout](#4-phased-rollout)
5. [Enterprise Concerns](#5-enterprise-concerns)
6. [Architecture Patterns](#6-architecture-patterns)
7. [Validation Checklist](#7-validation-checklist)
8. [Common Integration Mistakes](#8-common-integration-mistakes)

---

## 1. Before You Start — Discovery

Before touching any code, answer these questions. They determine which adapters you need and which governance primitives are non-negotiable.

### 1.1 Agent Inventory

Document every AI agent or automated process your team currently runs:

| Agent / Process | Language | Framework | Shares State With | Writes To |
|----------------|----------|-----------|-------------------|-----------|
| e.g. "invoice classifier" | Python | LangChain | "approvals bot" | Postgres |
| e.g. "customer triage" | Node | AutoGen | "CRM writer" | Salesforce API |

> **Why this matters:** Each row maps to one or more Network-AI adapters. Agents that share state with others are your highest-risk race condition points.

### 1.2 Race Condition Audit

For each pair of agents that write to the same resource, ask:

- Can both agents run at the same time?
- What happens if Agent A's write is overwritten by Agent B before Agent A reads it back?
- Is there any locking or retry logic today?

If the answer to the first question is "yes" and the second is "data loss / wrong decision / double spend" — that's a `LockedBlackboard` candidate.

### 1.3 Budget and Cost Exposure

- Do you have per-agent token limits today?
- Can a single runaway agent exhaust your OpenAI / Anthropic budget?
- Do you have hard cut-offs or just alerts?

Network-AI's `FederatedBudget` enforces hard ceilings. If you have no ceiling today, this is your first priority.

### 1.4 Compliance and Audit Requirements

- Does your industry require audit trails for automated decisions (GDPR, SOC 2, HIPAA, PCI-DSS)?
- Do you need to prove *which agent* made *which decision* and *when*?
- Are there regulatory rules about which systems an AI agent may access?

Answers drive `AuthGuardian` configuration and audit log retention policy.

---

## 2. Framework Mapping

Network-AI ships 12 adapters. Map your existing agents to the right one:

| Your Stack | Network-AI Adapter | Notes |
|-----------|-------------------|-------|
| LangChain (JS/TS) | `LangChainAdapter` | Supports Runnables, chains, agents |
| AutoGen / AG2 | `AutoGenAdapter` | Supports `.run()` and `.generateReply()` |
| CrewAI | `CrewAIAdapter` | Individual agents and full crew objects |
| OpenAI Assistants | `OpenAIAssistantsAdapter` | Thread management included |
| LlamaIndex | `LlamaIndexAdapter` | Query engines, chat engines, agent runners |
| Semantic Kernel | `SemanticKernelAdapter` | Microsoft SK kernels, functions, planners |
| Haystack | `HaystackAdapter` | Pipelines, agents, components |
| DSPy | `DSPyAdapter` | Modules, programs, predictors |
| Agno (ex-Phidata) | `AgnoAdapter` | Agents, teams, functions |
| MCP tools | `McpAdapter` | Tool serving and discovery |
| OpenClaw / Clawdbot / Moltbot | `OpenClawAdapter` | Native skill execution via `callSkill` |
| **Anything else** | `CustomAdapter` | Wrap any async function or HTTP endpoint |

### No matching framework?

Use `CustomAdapter`. Any async function becomes a governed agent in three lines:

```typescript
import { CustomAdapter } from 'network-ai';

const adapter = new CustomAdapter();
adapter.registerHandler('my-agent', async (payload) => {
  // your existing logic here — unchanged
  return { result: '...' };
});
```

This is the recommended entry point for **legacy systems**, **internal microservices**, and **REST APIs** — you do not need to rewrite anything.

---

## 3. Primitive Mapping — What Solves What

Match your problem to the Network-AI primitive:

| Problem | Primitive | How |
|---------|-----------|-----|
| Two agents overwriting each other's data | `LockedBlackboard` | Atomic `propose → validate → commit` with file-system mutex |
| Agent overspending token budget | `FederatedBudget` | Per-agent ceiling; hard cut-off on overspend |
| Agent accessing a resource it shouldn't | `AuthGuardian` + `SecureTokenManager` | HMAC-signed scoped tokens required at every sensitive operation |
| No audit trail for automated decisions | Audit log (`data/audit_log.jsonl`) | Cryptographic HMAC-signed chain, every write recorded |
| Agent running out of turn / taking too many actions | `ComplianceMonitor` | TOOL_ABUSE, TURN_TAKING, RESPONSE_TIMEOUT, JOURNEY_TIMEOUT detected in real time |
| Workflow needs defined states (e.g. INTAKE → REVIEW → APPROVE) | `JourneyFSM` | State machine gates which agents may act in which states |
| Content safety / hallucination in agent outputs | `QualityGateAgent` + `BlackboardValidator` | Two-layer validation before output enters the blackboard |
| Race conditions in parallel agent writes | `LockedBlackboard` with `priority-wins` | Higher-priority agents preempt lower-priority writes on conflict |
| Need to expose all tools to an AI via MCP | `McpSseServer` + `network-ai-server` | HTTP/SSE server at `GET /sse`, `POST /mcp`, `GET /tools` |
| Runtime AI control of the orchestrator | `ControlMcpTools` | AI can read/set config, spawn/stop agents, drive FSM transitions |

---

## 4. Phased Rollout

Do not try to enable everything at once. This is the recommended sequence for a zero-disruption integration:

### Phase 1 — Wrap (Day 1–3)

**Goal:** Get your existing agents running inside Network-AI without changing their behaviour.

1. `npm install network-ai`
2. Wrap each agent in the matching adapter (see §2)
3. Register all adapters with `AdapterRegistry`
4. Replace direct agent calls with `registry.executeAgent(...)` or `orchestrator.execute(...)`
5. Run `npm run demo -- --08` to verify the framework itself is healthy in your environment

**Nothing changes behaviourally yet.** This phase is purely structural.

```typescript
import { createSwarmOrchestrator, CustomAdapter } from 'network-ai';

const orchestrator = createSwarmOrchestrator({ swarmName: 'acme-swarm' });
const adapter = new CustomAdapter();

// Wrap your existing function — unchanged
adapter.registerHandler('invoice-classifier', async (payload) => {
  return await yourExistingClassifier(payload.params);
});

await orchestrator.addAdapter(adapter);
```

---

### Phase 2 — Shared State (Day 3–7)

**Goal:** Replace ad-hoc shared resources (databases, files, in-memory objects) with the blackboard.

1. Identify all keys agents share (from your §1.1 audit)
2. Introduce `SharedBlackboard` for low-contention data
3. Introduce `LockedBlackboard` for any key that two or more agents write to concurrently

```typescript
import { LockedBlackboard } from 'network-ai';

const board = new LockedBlackboard('.', { conflictResolution: 'priority-wins' });

// Atomic write — no other agent can interfere during this operation
const changeId = board.proposeChange('account:balance', newBalance, 'payment-agent');
board.validateChange(changeId);
board.commitChange(changeId);
```

> **Migration tip:** Start by shadowing — write to both your existing DB and the blackboard simultaneously. Once you're confident they match, remove the DB writes.

---

### Phase 3 — Budget Enforcement (Day 7–10)

**Goal:** Add hard token ceilings so no single agent can exhaust your LLM budget.

```typescript
import { FederatedBudget } from 'network-ai/lib/federated-budget';

const budget = new FederatedBudget({
  pools: {
    'classifier':   { ceiling: 50_000  },  // tokens per run
    'summarizer':   { ceiling: 100_000 },
    'orchestrator': { ceiling: 200_000 },
  }
});

// Check before each LLM call
const check = budget.canSpend('classifier', estimatedTokens);
if (!check.allowed) throw new Error(`Budget ceiling reached: ${check.reason}`);

// Record actual spend after
budget.recordSpend('classifier', actualTokens);
```

Map your cost centers to pool names. Budget state persists across agent runs.

---

### Phase 4 — Access Control (Day 10–14)

**Goal:** Gate access to sensitive APIs and resources behind cryptographically signed tokens.

1. Define your resources and risk levels (see `references/auth-guardian.md`)
2. Map your agents to trust levels (see `references/trust-levels.md`)
3. Replace direct API calls with `AuthGuardian`-gated calls

```typescript
import { AuthGuardian, SecureTokenManager } from 'network-ai';

const guardian = new AuthGuardian();
const tokenManager = new SecureTokenManager(process.env.HMAC_SECRET!);

// Agent requests access with a justification
const request = await guardian.requestPermission({
  agentId: 'payment-agent',
  resource: 'PAYMENTS',
  action: 'write',
  justification: 'Processing approved invoice #INV-2847 per workflow step 3',
  trustLevel: 0.8,
});

if (request.approved) {
  const token = tokenManager.createToken('payment-agent', ['PAYMENTS:write'], 300);
  // pass token to downstream call
}
```

**IAM integration:** The token payload (agentId, permissions, expiry) can be forwarded as a JWT claim to your existing IAM layer. Network-AI does not replace your IAM — it sits in front of it as a pre-authorization layer.

---

### Phase 5 — Governance and FSM (Day 14–21)

**Goal:** Define explicit workflow states so agents can only act when the system is in the right state.

```typescript
import { JourneyFSM, WORKFLOW_STATES } from 'network-ai';

const fsm = new JourneyFSM({
  agentId: 'workflow',
  journeyId: 'invoice-processing',
  transitions: [
    { from: 'INTAKE',   to: 'ANALYZE',  allowedAgents: ['intake-agent']  },
    { from: 'ANALYZE',  to: 'APPROVE',  allowedAgents: ['analyst-agent'] },
    { from: 'APPROVE',  to: 'EXECUTE',  allowedAgents: ['approver-agent'] },
    { from: 'EXECUTE',  to: 'DELIVER',  allowedAgents: ['payment-agent'] },
  ]
});

// Before any agent acts, check the FSM
const canAct = fsm.canTransition(currentState, nextState, agentId);
```

Add `ComplianceMonitor` to detect violations in real time without blocking the main thread:

```typescript
import { ComplianceMonitor } from 'network-ai';

const monitor = new ComplianceMonitor(fsm, {
  maxActionsPerTurn: 5,
  responseTimeoutMs: 30_000,
  journeyTimeoutMs: 300_000,
});
monitor.start(1_000); // poll every second
```

---

### Phase 6 — Observability and MCP (Day 21+)

**Goal:** Expose everything to your monitoring stack and optionally give your AI models control-plane access.

Start the MCP server (exposes 20+ tools via SSE/JSON-RPC):

```bash
npx network-ai-server --port 3001 --audit-log data/audit_log.jsonl --ceiling 500000
```

Connect your AI model to `http://localhost:3001/sse` — it can now:
- Read and write live config (`config_get`, `config_set`)
- Spawn and stop agents (`agent_spawn`, `agent_stop`)
- Drive FSM transitions (`fsm_transition`)
- Query the audit log (`audit_query`, `audit_tail`)
- Check and top up budgets (`budget_status`, `budget_spend`)

---

## 5. Enterprise Concerns

### Authentication & IAM

Network-AI does **not** require or replace an external IAM system. `AuthGuardian` operates as a **pre-authorization layer**:

```
AI Agent → AuthGuardian (justification scoring) → your IAM (final auth) → resource
```

The HMAC secret (`HMAC_SECRET` env var) should be rotated on the same schedule as your other API keys and stored in your secret manager (AWS Secrets Manager, Azure Key Vault, HashiCorp Vault).

### Audit Log Retention

The audit log at `data/audit_log.jsonl` is a HMAC-signed append-only chain. Each entry contains: timestamp, agentId, eventType, resource, outcome, and a chain signature.

- **GDPR / right to erasure:** Entries are immutable by design. If data subject erasure applies, store identifying data outside the log and reference only pseudonymized agent IDs inside it.
- **Retention:** Rotate files using your standard log rotation tooling (logrotate, Fluentd, etc.). The chain continues across files — verification just needs the previous file's last hash.
- **SIEM integration:** Stream `audit_log.jsonl` to Splunk, Datadog, or Elastic via the `audit_tail` MCP tool or a simple `tail -F` feed.

### Air-Gapped / On-Prem Deployment

Network-AI has **zero required external network calls**. All operations (blackboard, FSM, compliance, budget, tokens, audit) run entirely on-premises:

- No telemetry, no call-home, no cloud dependency
- LLM calls only happen if *you* add an adapter that calls an LLM — e.g. `OpenAIAssistantsAdapter` will call `api.openai.com`, but this is your explicit choice
- The MCP server (`network-ai-server`) binds to localhost by default; deploy behind your internal API gateway to expose it to your agent fleet

### Multi-Tenant Deployments

Isolate tenants by:
1. **Separate blackboard roots** — each tenant gets their own directory path passed to `LockedBlackboard(tenantPath)`
2. **Separate budget pools** — prefix pool names with tenant ID: `tenant-abc:classifier`
3. **Separate HMAC secrets** — one `SecureTokenManager` instance per tenant
4. **Namespace scoping** — use consistent key prefixes in the blackboard (e.g. `tenant-abc:invoice:42`)

### Scaling

Network-AI is a **single-process orchestrator** by design — it does not require a broker, queue, or service mesh. For horizontal scaling:

- **Shared `LockedBlackboard`:** Point multiple instances at the same directory on a shared volume (NFS, EFS, Azure Files). File-system mutexes work across processes on the same mount.
- **Independent budget tracking:** Each instance tracks its own pool. Use a sidecar or the `audit_tail` MCP tool to aggregate spend across instances.
- **FSM per workflow:** One `JourneyFSM` per workflow instance, not per process. FSM state persists to the blackboard, so any process can resume an interrupted journey.

---

## 6. Architecture Patterns

### Pattern A — Sidecar (Minimal Disruption)

Keep your existing agent orchestration. Add Network-AI only for coordination, safety, and audit on the shared state layer.

```
[Existing LangChain agent] ──writes──▶ [LockedBlackboard] ◀──reads── [Existing AutoGen agent]
                                              │
                                       [Audit log]
                                       [Budget tracking]
```

No changes to your agent code. Network-AI wraps the shared resource only.

---

### Pattern B — Full Orchestrator

Network-AI owns the entire agent lifecycle. All agents run through the adapter registry.

```
User request
     │
     ▼
SwarmOrchestrator
     │
     ├──▶ AuthGuardian (permission check)
     ├──▶ JourneyFSM (state gate)
     ├──▶ FederatedBudget (cost check)
     │
     ├──▶ LangChainAdapter ──▶ your LangChain agent
     ├──▶ AutoGenAdapter   ──▶ your AutoGen agent
     └──▶ CustomAdapter    ──▶ your existing functions
```

---

### Pattern C — MCP Control Plane

Your AI model connects to `network-ai-server` via SSE and drives the whole system through MCP tools — no hand-coded orchestration logic at all.

```
AI Model (Claude / GPT-4o)
     │  SSE/JSON-RPC
     ▼
network-ai-server (port 3001)
     │
     ├── ControlMcpTools   (spawn agents, drive FSM, set config)
     ├── ExtendedMcpTools  (budget, tokens, audit)
     └── BlackboardMCPTools (read/write blackboard)
```

---

## 7. Validation Checklist

Run these before declaring the integration production-ready:

### Functional

- [ ] All agents execute via the adapter registry without errors
- [ ] `npx ts-node test-standalone.ts` — 79 core tests pass
- [ ] `npx ts-node test-security.ts` — 33 security tests pass
- [ ] `npx ts-node test-adapters.ts` — 139 adapter tests pass
- [ ] `npx ts-node test-phase4.ts` — 147 behavioral tests pass
- [ ] `npm run demo -- --08` runs to completion in < 10 seconds

### Race Condition Safety

- [ ] Two agents can write to the same blackboard key concurrently without data loss
- [ ] `LockedBlackboard.validateChange()` rejects a stale change after a conflict
- [ ] `priority-wins` correctly overwrites a lower-priority pending write

### Budget Enforcement

- [ ] Spending past the ceiling throws / returns `allowed: false`
- [ ] Budget state persists across process restart
- [ ] Per-agent pools are independent (overspending in pool A does not affect pool B)

### Access Control

- [ ] A token issued by `SecureTokenManager` validates correctly
- [ ] An expired token is rejected
- [ ] A token with insufficient scope is rejected at the `AuthGuardian` gate
- [ ] `--active-grants` shows the correct active token set

### Compliance

- [ ] `ComplianceMonitor` fires `TOOL_ABUSE` after the configured action threshold
- [ ] `RESPONSE_TIMEOUT` fires when an agent exceeds the timeout window
- [ ] `JOURNEY_TIMEOUT` fires when the overall journey exceeds its ceiling
- [ ] FSM blocks a transition attempted by an unauthorized agent

### Audit

- [ ] Every blackboard write produces a signed entry in `audit_log.jsonl`
- [ ] `audit_query` returns filtered results correctly
- [ ] The audit chain signature is intact after N entries (run the chain verifier)

---

## 8. Common Integration Mistakes

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Using `SharedBlackboard` for concurrent writes | Race conditions / data loss | Use `LockedBlackboard` for any key two agents write to |
| Not committing the lock file (`package-lock.json`) | CI `npm ci` fails on Node version mismatch | Always commit `package-lock.json` after version bumps |
| Not including `socket.json` in `package.json` `files` | Socket.dev ignores aren't shipped; supply chain score drops | Add `socket.json` to the `files` array |
| Hardcoded agent IDs in trust level config | Agent added later gets default 0.5 trust and is silently denied | Maintain a central trust registry; register new agents before deploying |
| One `FederatedBudget` pool shared by all agents | One runaway agent exhausts budget for everyone | One pool per agent or per role |
| FSM with no timeout | Stuck workflow holds locks indefinitely | Always set `timeoutMs` on states that involve external calls |
| Storing PII as blackboard keys | Audit log contains PII in plain text | Use pseudonymised keys; store PII in a separate encrypted store |
| Running `network-ai-server` on `0.0.0.0` in production | MCP control plane is publicly accessible | Bind to localhost and expose via authenticated internal API gateway only |

---

## Further Reading

| Document | What It Covers |
|----------|---------------|
| [QUICKSTART.md](QUICKSTART.md) | Get running in 5 minutes |
| [QUICKSTART.md § CLI](QUICKSTART.md) | CLI reference — bb, auth, budget, audit commands |
| [references/adapter-system.md](references/adapter-system.md) | All 12 adapters with code examples |
| [references/trust-levels.md](references/trust-levels.md) | Trust scoring formula and agent roles |
| [references/auth-guardian.md](references/auth-guardian.md) | Permission system, justification scoring, token lifecycle |
| [references/blackboard-schema.md](references/blackboard-schema.md) | Blackboard key conventions and namespacing |
| [references/mcp-roadmap.md](references/mcp-roadmap.md) | MCP server tools reference |
| [examples/README.md](examples/README.md) | All runnable demos |
| [CHANGELOG.md](CHANGELOG.md) | Full version history |

---

*Network-AI v4.0.6 · MIT License · https://github.com/jovanSAPFIONEER/Network-AI*
