# Network-AI — Enterprise Evaluation Guide

This document exists so an engineer or architect can evaluate Network-AI in under 30 minutes without a sales call.

---

## Quick Evaluation Checklist

| Question | Answer |
|---|---|
| Can I run it fully offline / air-gapped? | **Yes.** Core orchestration, blackboard, permissions, FSM, budget, and compliance monitor require no network. Only the OpenAI adapter calls an external API — it is opt-in. |
| Do I control all data? | **Yes.** All state lives in your `data/` directory on your own infrastructure. Nothing is transmitted. |
| Is the source auditable? | **Yes.** MIT-licensed, fully open source, no obfuscated code, no telemetry. |
| Does it have an audit trail? | **Yes.** Every permission request, grant, denial, and revocation is appended to `data/audit_log.jsonl` with a UTC timestamp. See [AUDIT_LOG_SCHEMA.md](AUDIT_LOG_SCHEMA.md). |
| Can I plug in my own LLM / provider? | **Yes.** The adapter registry supports LangChain, AutoGen, CrewAI, LlamaIndex, Semantic Kernel, OpenAI Assistants, Haystack, DSPy, Agno, and a `CustomAdapter` for anything else. |
| Does it work with our existing agent framework? | **Yes.** It wraps around your framework — you keep what you have and add guardrails on top. |
| Is there a security review? | **Yes.** CodeQL scanning on every push, Dependabot auto-merge, Socket.dev supply chain score A, OpenSSF Scorecard. See [SECURITY.md](SECURITY.md). |
| What does it cost to operate? | **Zero licensing cost.** MIT license. Infrastructure cost = your own compute. |
| Is there a compliance module? | **Yes.** `ComplianceMonitor` enforces configurable violation policies with severity classification and async audit loop. |
| Can I restrict which agents access which resources? | **Yes.** `AuthGuardian` evaluates justification quality + agent trust score + resource risk score before issuing a grant token. |

---

## What It Does (One Paragraph)

Network-AI is a TypeScript/Node.js orchestration layer that sits between your agents and your shared state. It enforces: atomic blackboard writes (no race conditions when two agents write simultaneously), permission gating (agents must request access to sensitive resources and provide a scored justification), budget ceilings (per-agent token limits; rogue agents get cut off mid-task), FSM-based workflow governance (agents are blocked from skipping pipeline stages), and real-time compliance monitoring (tool abuse, turn-taking violations, response timeouts). It ships as an npm package with a companion Python skill bundle for OpenClaw/ClawHub environments.

---

## Architecture Summary

```
Your agents
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  Network-AI Orchestration Layer                     │
│                                                     │
│  LockedBlackboard  ──── atomic propose/commit       │
│  AuthGuardian      ──── permission scoring          │
│  FederatedBudget   ──── per-agent token ceilings    │
│  JourneyFSM        ──── FSM state governance        │
│  ComplianceMonitor ──── real-time violation policy  │
│  BlackboardValidator─── content quality gate        │
└─────────────────────────────────────────────────────┘
    │
    ▼
data/ (local filesystem — you own it)
  ├── audit_log.jsonl
  ├── active_grants.json
  └── blackboard state files
```

Full architecture: [ARCHITECTURE.md](ARCHITECTURE.md)

---

## Security & Supply Chain

| Check | Status |
|---|---|
| CodeQL (GitHub Advanced Security) | ✅ All alerts resolved |
| Dependabot | ✅ Auto-merge enabled, dependency graph active |
| Socket.dev supply chain | ✅ No high-severity flags |
| OpenSSF Scorecard | ✅ SHA-pinned CI actions, provenance publishing |
| npm provenance | ✅ Published with `--provenance` since v4.0.0 |
| Secret scanning | ✅ Enabled on repository |
| Vulnerability disclosure | [SECURITY.md](SECURITY.md) — 48h acknowledgment, 7-day response |

---

## Stability & Support Expectations

### Versioning

Network-AI follows [Semantic Versioning](https://semver.org/):
- **Patch** (4.0.x): bug fixes and security patches — safe to auto-update
- **Minor** (4.x.0): additive features, backward-compatible — upgrade at your pace
- **Major** (x.0.0): breaking API changes — migration guide provided in CHANGELOG

### Security Fix Policy

| Version | Policy |
|---|---|
| 4.0.x (current) | Full support — bugs + security fixes |
| 3.5.x – 3.9.x | Security fixes only |
| < 3.5 | No support |

### Response Times (GitHub Issues)

| Severity | Target |
|---|---|
| Security vulnerability (private) | 48h acknowledgment, 7 days remediation |
| Bug with reproduction | Best effort, typically < 7 days |
| Feature request | Triaged on rolling basis |

### Stability Signals

- 1,216 passing assertions across 13 suites
- Deterministic scoring — no random outcomes in permission evaluation or budget enforcement
- CI runs on every push and every PR
- All examples ship with the repo and run without mocking

---

## Integration Entry Points

| Use case | Starting point |
|---|---|
| Wrap existing LangChain agents | [INTEGRATION_GUIDE.md § LangChain](INTEGRATION_GUIDE.md) |
| Add permission gating | `AuthGuardian` in [QUICKSTART.md](QUICKSTART.md) |
| Add budget enforcement | `FederatedBudget` in [QUICKSTART.md](QUICKSTART.md) |
| Add FSM workflow governance | `JourneyFSM` in [ARCHITECTURE.md](ARCHITECTURE.md) |
| MCP server (model context protocol) | `npx network-ai-mcp` — see [QUICKSTART.md](QUICKSTART.md) |
| Inspect / manage state from terminal | `network-ai bb` CLI — see [QUICKSTART.md § CLI](QUICKSTART.md) |
| Full working example (no API key) | `npx ts-node examples/08-control-plane-stress-demo.ts` |
| Full working example (with API key) | `npx ts-node examples/07-full-showcase.ts` |

---

## Known Adopters

See [ADOPTERS.md](ADOPTERS.md).

---

## License

MIT — [LICENSE](LICENSE). No CLA required for contributions.
