# OpenPersona Architecture Reference

## 4+5+3 Model

OpenPersona uses a **4+5+3** model. A persona's constraints are declared once in `persona.json` and cannot be bypassed at any point in its lifecycle.

**4 Layers** — structure, what the persona *is*:

| Layer | Type | Key Content |
|-------|------|------------|
| **Soul** | identity | personality, role, bio, boundaries, constitution, evolution config |
| **Body** | substrate | `runtime` (REQUIRED) · appearance · physical · interface (nervous system) |
| **Faculty** | persistent capability | always-active dimensions: `voice` · `avatar` · `memory` |
| **Skill** | on-demand action | built-in: selfie · music · reminder; external via `install` field |

**5 Systemic Concepts** — behavior, how it *operates* (declared as top-level fields in `persona.json`):

| Field | Concept | Controls |
|-------|---------|---------|
| `evolution` | **Evolution** | Trait growth, relationship progression, speaking style drift, event log |
| `economy` | **Economy** | Financial ledger (AgentBooks), vitality scoring, survival policy |
| `vitality` | **Vitality** | Multi-dimension health aggregation (currently financial pass-through) |
| `social` | **Social** | ACN discovery, ERC-8004 on-chain identity, A2A Agent Card |
| `rhythm` | **Rhythm** | Temporal behavior: `heartbeat` (proactive outreach cadence) + `circadian` (time-of-day modulation) |

**3 Gates** — enforcement, how constraints are *protected*:

| Gate | Module | Mechanism |
|------|--------|-----------|
| **Generate** | `lib/generator/validate.js` | hard-reject (`throw`) — required fields, constitution §3/§6 compliance, boundary schema |
| **Install** | `lib/lifecycle/installer.js` | warning (`printWarning`) — constitution SHA-256 hash integrity |
| **Runtime** | `scripts/state-sync.js` | clamp / filter — immutableTraits, formality bounds, stage progression, trust gate |

## Skill Pack Structure

```
persona-<slug>/
├── SKILL.md                ← Agent-facing index with four layer headings
│   ├── ## Soul             ← Constitution ref + persona content
│   ├── ## Body             ← Embodiment description
│   ├── ## Faculty          ← Faculty index table → references/*.md
│   └── ## Skill            ← Active skill definitions
├── persona.json            ← Complete persona declaration (pack root)
├── state.json              ← Body nervous system runtime state (pack root)
├── soul/                   ← Soul layer artifacts
│   ├── injection.md        ← Soul injection for host integration
│   ├── constitution.md     ← Universal ethical foundation
│   ├── behavior-guide.md   ← Domain-specific behavior instructions (when behaviorGuide declared)
│   ├── behavior-guide.meta.json ← Refinement metadata (when behavior-guide.md exists)
│   ├── self-narrative.md   ← First-person growth storytelling (when evolution enabled)
│   └── lineage.json        ← Fork lineage + constitution hash (when forked)
├── economy/                ← Economy Infrastructure data (when economy.enabled: true)
│   ├── economic-identity.json
│   └── economic-state.json
├── references/             ← Agent-readable detail docs (on demand)
│   ├── <faculty>.md        ← Per-faculty usage instructions
│   └── SIGNAL-PROTOCOL.md  ← Host-side Signal Protocol implementation guide (always generated)
├── agent-card.json         ← A2A Agent Card (protocol v0.3.0)
├── acn-config.json         ← ACN registration config (runtime fills owner/endpoint)
├── .gitignore              ← Protects state.json + private files
├── scripts/
│   ├── state-sync.js       ← Body nervous system nerve fiber (read / write / signal / promote)
│   ├── economy.js          ← Economy management commands (when economy.enabled: true)
│   ├── economy-guard.js    ← Outputs FINANCIAL_HEALTH_REPORT (when economy.enabled: true)
│   └── economy-hook.js     ← Post-conversation cost recorder (when economy.enabled: true)
└── assets/                 ← Static assets (per Agent Skills spec)
    ├── avatar/             ← Body > Appearance: images, Live2D .model3.json, VRM
    ├── reference/          ← Reference images (e.g. for selfie skill)
    └── templates/          ← Document/config templates (optional)
```

## Self-Awareness System

The generator injects a unified **Self-Awareness** section into every persona's `soul/injection.md` with four dimensions:

1. **Identity** — constitutional grounding (Safety › Honesty › Helpfulness), digital twin disclosure when `sourceIdentity` is present
2. **Capabilities** — dormant skill awareness + graceful degradation when `install` fields are declared on skills/faculties/body
3. **Body** — Signal Protocol, Pending Commands queue, State Sync; plus `body.runtime` specifics (platform, channels, credentials) when declared
4. **Growth** — evolution state, influence boundary policy, external sources — injected when `evolutionEnabled`

You don't need to manually write degradation instructions — declare `install` fields on skills/faculties/body, and the persona automatically knows what it *could* do but *can't yet*.
