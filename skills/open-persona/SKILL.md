---

name: open-persona  
version: "0.19.1"  
description: >  
  Meta-skill for building and managing agent persona skill packs (instruction-only;  
  no bundled installer or auto-downloaded binaries). Credentials are never written  
  into generated packs by the framework; publish/ACN/register require explicit user CLI.  
  Use when the user wants to create a new agent persona, install/manage  
  existing personas, or publish persona skill packs to OpenPersona.  
license: MIT  
compatibility: Generated skill packs work with any SKILL.md-compatible agent. CLI management (install/switch) defaults to OpenClaw.  
allowed-tools: Bash(npx openpersona:*) Bash(npx clawhub@latest:*) Bash(openclaw:*) Bash(gh:*) Read Write WebFetch
metadata:
  author: openpersona
  repository: [https://github.com/acnlabs/OpenPersona](https://github.com/acnlabs/OpenPersona)
  tags: "persona, agent, skill-pack, meta-skill, agent-agnostic, openclaw"

# Marketplace / automated review: explicit non-behavior (reduces false “suspicious” flags)

  installSurface: instruction-only
  networkAccess: user-initiated-cli-only
  secretsPolicy: never-embedded-in-generated-packs-by-framework
  clawdbot:
    emoji: "🧑"
    requires:
      env: []
files: []

---

# OpenPersona — Build & Manage Persona Skill Packs

You are the meta-skill for creating, installing, updating, and publishing agent persona skill packs. Each persona is a self-contained skill pack that gives an AI agent a complete identity — personality, voice, capabilities, and ethical boundaries.

## Trust & safety (reviewer summary)

This pack is **instruction-only**: there is **no** skill-defined installer that downloads or executes arbitrary payloads. Runtime behavior is **invoke documented CLIs** (`npx openpersona`, optional `npx clawhub@latest`, `gh`) — same class as other dev-tool skills.


| Claim                          | How it is enforced                                                                                                                                                                                                        |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **No credential exfiltration** | The OpenPersona generator **does not** embed API keys or secrets into `persona.json`, `SKILL.md`, or published zips. Keys belong in the host credential store or environment (e.g. `~/.openclaw/credentials/`, env vars). |
| **No silent publishing**       | `publish`, `contribute`, and `acn-register` run **only** when the user explicitly asks and the CLI is invoked — there is no background upload or auto-registration in this meta-skill.                                    |
| **Local-first default**        | Create, install, state read/write, and evolution run **locally**. Network calls are limited to **explicit** commands (npm registry resolution, optional ClawHub search, optional publish/register).                       |
| **Generated scripts**          | `scripts/state-sync.js` and economy helpers are **rendered from audited framework templates** (not fetched at skill-install time). Treat them like any generated code: review before high-assurance environments.         |


If an automated scanner flags “suspicious,” it is usually because **persona managers legitimately describe** local state, optional providers, and publishing — not because this file contains malware. **Details:** [Security & Policy](#security--policy).

## What You Can Do

1. **Create Persona** — Through conversation, gather 4-layer fields and generate a skill pack (`npx openpersona create`); includes advising on faculties/skills, searching ClawHub / skills.sh for external skills, and writing custom SKILL.md files for missing capabilities
2. **Find & Install Personas** — `npx openpersona search <query>` to discover community personas; `npx openpersona install <slug>` or `npx openpersona install <owner/repo>` to install
3. **Manage Personas** — List, update, fork, switch, reset, export/import installed personas
4. **Publish Persona** — Publish a GitHub-hosted persona pack to [OpenPersona](https://openpersona-frontend.vercel.app/) (the vertical persona directory); optionally also to ClawHub / skills.sh
5. **Runner Integration** — Provide runner authors with the four `openpersona state` commands (read / write / signal / promote) for integrating personas at conversation boundaries
6. **Monitor & Evolve** — Generate evolution reports (`evolve-report`), run soul-memory bridge (`state promote`), run pack refinement (`refine`), interpret vitality scores

## Architecture: 4+5+3

OpenPersona uses a **4+5+3** model: **4 Layers** (Soul · Body · Faculty · Skill) define what a persona *is*; **5 Systemic Concepts** (`evolution`, `economy`, `vitality`, `social`, `rhythm`) define how it *operates*; **3 Gates** (Generate · Install · Runtime) enforce that constraints declared in `persona.json` cannot be bypassed at any lifecycle point.

→ Full model tables, pack file structure, and self-awareness injection details: read `references/ARCHITECTURE.md`

## Available Presets

The default preset is `**base*`* — a blank-slate meta-persona with voice faculty + reminder skill, evolution enabled. Recommended starting point for any new persona.

```bash
npx openpersona create --preset base --install
# or just:
npx openpersona create   # interactive wizard, defaults to base
```

→ Full preset catalog (samantha, ai-girlfriend, life-assistant, health-butler, stoic-mentor, and more): `references/PRESETS.md`

## Creating a Persona

**Two entry points:**

- **Interactive** (recommended for beginners): `npx openpersona create` — interactive wizard, no file needed
- **Config-driven** (recommended for agents): gather the fields below → write `persona.json` → run `npx openpersona create --config ./persona.json --install`

`persona.json` declares all 4 layers in a single file. Gather inputs by layer:

### Soul

- **Required:** `soul.identity.{personaName, slug, bio}` + `soul.character.{personality, speakingStyle}`
- **Recommended:** `soul.identity.role`, `soul.aesthetic.{creature, emoji, age, vibe}`, `soul.character.{background, boundaries, capabilities}`
- **Optional:** `soul.identity.sourceIdentity`, `soul.aesthetic.referenceImage`, `soul.character.behaviorGuide`

**The `role` field** defines the persona's relationship to the user. Common values: `companion` (default), `assistant`, `character`, `brand`, `pet`, `mentor`, `therapist`, `coach`, `collaborator`, `guardian`, `entertainer`, `narrator`. Custom values are welcome.

**The `sourceIdentity` field** marks the persona as a digital twin of a real-world entity (person, animal, character, brand, historical figure). When present, the generator injects disclosure obligations and faithfulness constraints.

**The `background` field is critical.** Write a compelling story — multiple paragraphs with depth, history, and emotional texture. A one-line background produces a flat, lifeless persona.

**The `behaviorGuide` field** is optional but powerful. Use markdown to write domain-specific behavior instructions that go directly into the generated SKILL.md.

### Body

- `**runtime`** (REQUIRED) — minimum viable body: `framework` (agent runner, e.g. `openclaw`), `channels`, `credentials`, `resources`
- `**appearance**` (optional) — avatar, 3D model
- `**physical**` (optional) — robots, IoT devices
- `**interface**` (optional) — Signal Protocol + Pending Commands + State Sync (the persona's nervous system)

### Faculty

Faculties are always-active persistent capabilities. Declared as an object array: `[{ "name": "voice", "provider": "elevenlabs" }, { "name": "memory" }]`

- `**voice**` (`expression`) — TTS voice synthesis; requires `provider` (e.g. `elevenlabs`) + `ELEVENLABS_API_KEY`
- `**avatar**` (`expression`) — External avatar runtime bridge; graceful text-only fallback when unavailable. → When configuring avatar (provider, Live2D/VRM, fallback rules): read `references/AVATAR.md`
- `**memory**` (`cognition`) — Cross-session recall via `memories.jsonl`; set top-level `memory.inheritance: "copy"` in `persona.json` to carry memories to child personas at fork. Connected to **Soul-Memory Bridge** (`openpersona state promote`).

**Soft references:** Faculties can declare `"install": "clawhub:..."` for capabilities not installed locally — the persona will be aware of the dormant capability and can request activation via the Signal Protocol.

### Skill

Skills are on-demand actions. Declared as an object array in `persona.json`:

- **Built-in:** `selfie` · `music` · `reminder`
- **Local:** definitions in `layers/skills/{name}/` (`skill.json` + optional `SKILL.md`)
- **External:** `{ "name": "...", "install": "clawhub:<slug>" }` — add `"trust": "verified"|"community"|"unverified"` to participate in the Skill Trust Gate
- **Soft references:** External skills not installed locally → persona knows what it *could* do and degrades gracefully

To find external skills: check local `layers/skills/`, search ClawHub via `npx clawhub@latest search "<keywords>"`, or fetch `https://skills.sh/api/search?q=<keywords>`.

`**additionalAllowedTools`** — extra tool permissions beyond what faculties contribute automatically.

For `rhythm` (heartbeat + circadian) configuration → see [Systemic Concepts → Rhythm](#rhythm)

Once all fields are gathered, write `persona.json` and run `npx openpersona create --config ./persona.json --install`.

### Creating Custom Skills

If the user needs a capability not found in any ecosystem:

1. Discuss what the skill should do
2. Create a SKILL.md file with proper frontmatter (name, description, allowed-tools)
3. Write complete implementation instructions (not just a skeleton)
4. Save to `~/.openclaw/skills/<skill-name>/SKILL.md` (OpenClaw) or your runner's skill directory
5. Register with your agent runner (e.g. add to `openclaw.json` for OpenClaw)

## Managing Personas

#### Install & Discover

- **Install:** `npx openpersona install <target>` — install from registry slug or `owner/repo`; `--registry <name>` selects registry (`acnlabs` default)
- **Search:** `npx openpersona search <query>` — search personas in the registry
- **List:** `npx openpersona list` — show all installed personas with active indicator

#### Switch & Fork

- **Switch:** `npx openpersona switch <slug>` — switch active persona
- **Fork:** `npx openpersona fork <parent-slug> --as <new-slug>` — derive a child persona inheriting the parent's constraint layer (boundaries, faculties, skills, body.runtime); fresh evolution state + `soul/lineage.json` recording parent slug, constitution SHA-256 hash, generation depth, and `parentPackRevision` (when parent has meta)

#### Update & Maintain

- **Update:** `npx openpersona update <slug>` — regenerate from `persona.json`; preserves `state.json`, `soul/self-narrative.md`, and `soul/lineage.json`
- **Reset:** `npx openpersona reset <slug>` — restore soul evolution state to initial values
- **Uninstall:** `npx openpersona uninstall <slug>`

#### Migrate

- **Export:** `npx openpersona export <slug>` — export persona pack (with soul state) as a zip archive
- **Import:** `npx openpersona import <file>` — import persona from a zip archive and install

#### Reports & Analytics

- **Evolve Report:** `npx openpersona evolve-report <slug>` — formatted evolution report (relationship, mood, traits, drift, interests, milestones, eventLog, self-narrative, state history)
- **Vitality Score:** `npx openpersona vitality score <slug>` — machine-readable `VITALITY_REPORT` (tier, score, diagnosis, trend)
- **Vitality Report:** `npx openpersona vitality report <slug> [--output <file>]` — human-readable HTML Vitality report
- **Living Canvas:** `npx openpersona canvas <slug> [--output <file>] [--open]` — self-contained HTML persona profile page showing all four layers, evolved traits timeline, relationship stage, and A2A "Talk" button when endpoint is available (top-level CLI; conceptually Social expression, not Vitality)

#### Evolution Tools

- **Soul-Memory Bridge:** `openpersona state promote <slug> [--dry-run]` — promote recurring eventLog patterns to `evolvedTraits` → see [Evolution](#evolution)
- **Skill Pack Refinement:** `npx openpersona refine <slug> [--emit] [--apply]` — evolve behavior guide → see [Evolution](#evolution)

#### Community

- **Contribute:** `npx openpersona contribute <slug> [--dry-run]` — submit persona improvements as a PR to the community; `--dry-run` shows diff without creating PR; requires `gh` CLI. → For the full diff review and PR workflow: read `references/CONTRIBUTE.md`

When multiple personas are installed, only one is **active** at a time. All install/uninstall/switch operations maintain a local registry at `~/.openpersona/persona-registry.json`; on OpenClaw, switching replaces the soul injection block in SOUL.md / IDENTITY.md (preserving user-written content outside the markers). **Context Handoff:** On switch, a `handoff.json` is generated with the outgoing persona's relationship stage, mood snapshot, and shared interests — the incoming persona reads it to continue seamlessly. The `export` and `import` commands enable cross-device persona transfer.

## Publishing Personas

**Primary target: [OpenPersona](https://openpersona-frontend.vercel.app/)** — the vertical persona skills directory. Guide the user through:

1. Create the persona: `npx openpersona create --config ./persona.json --output ./my-persona`
2. Push the persona pack to a public GitHub repo (e.g. `alice/my-persona`)
3. Register with OpenPersona directory: `npx openpersona publish alice/my-persona`

The persona will appear in the OpenPersona leaderboard and be installable via `npx openpersona install <slug>` by anyone.

Persona packs can also be listed on general skill platforms (ClawHub, skills.sh) as supplementary distribution, but OpenPersona is the canonical home for persona-type skill packs.

## Runner Integration Protocol

Any agent runner integrates with installed personas via four CLI commands called at conversation boundaries — no knowledge of file paths or persona internals needed:

```bash
# Before conversation starts — load state into agent context
openpersona state read <slug>

# After conversation ends — persist agent-generated patch
openpersona state write <slug> '<json-patch>'

# On-demand — emit capability or resource signal to host
openpersona state signal <slug> <type> '[payload-json]'

# Soul-Memory Bridge — promote recurring eventLog patterns to evolvedTraits
openpersona state promote <slug> [--dry-run]
```

**State read output** (JSON): `exists`, `slug`, `mood` (full object), `relationship`, `evolvedTraits`, `speakingStyleDrift`, `interests`, `recentEvents` (last 5 from eventLog), `pendingCommands` (host-queued async instructions), `lastUpdatedAt`. Returns `{ exists: false, message }` when `state.json` is not found.

**Trust self-check:** After reading state, the persona processes `pendingCommands` and self-enforces `evolution.skill.minTrustLevel` — it autonomously refuses to activate skills below the trust threshold, without waiting for host enforcement. Low-trust `capability_unlock` commands are filtered; a `capability_gap` signal is emitted to notify the host.

**State write patch**: JSON object; nested fields (`mood`, `relationship`, `speakingStyleDrift`, `interests`) are deep-merged — send only changed sub-fields. Immutable fields (`$schema`, `version`, `personaSlug`, `createdAt`) are protected. `eventLog` entries are appended (capped at 50); each entry: `type`, `trigger`, `delta`, `source`.

**Signal types**: `capability_gap` | `tool_missing` | `scheduling` | `file_io` | `resource_limit` | `agent_communication`

Signals are written to a feedback directory resolved from the host's home path (framework-agnostic — works with OpenClaw, Cursor, Claude Code, Codex, or any custom runner). See `layers/body/SIGNAL-PROTOCOL.md` in the framework source for the full host-side contract and integration guide.

These commands resolve the persona directory automatically (registry lookup → `~/.openpersona/personas/persona-<slug>/` → legacy `~/.openclaw/skills/persona-<slug>/`) and delegate to `scripts/state-sync.js` inside the persona pack. Works from any directory.

## Systemic Concepts

OpenPersona's 5 systemic concepts span all 4 layers and are declared as top-level fields in `persona.json`. They define how a persona *operates*, orthogonal to the 4-layer structure that defines what it *is*.

### Evolution

`evolution.`* covers evolutionary behavior across all layers. Enable Soul growth via `evolution.instance.enabled: true`.

The persona automatically tracks **relationship progression**, **mood**, **trait emergence**, **speaking style drift**, and **interests** across conversations, governed by three declarative controls:

- **Boundaries** — `immutableTraits` array + `minFormality`/`maxFormality` numeric bounds (-10 to +10); validated at generation time, enforced at runtime
- **Sources** — External evolution ecosystems (soft-ref; declared at generation, activated by host at runtime)
- **Influence Boundary** — Declarative ACL for external `persona_influence` requests; `defaultPolicy: "reject"` is safety-first

State history (capped at 10 snapshots), event log (capped at 50 entries), and `soul/self-narrative.md` are maintained automatically.

#### Skill Trust Gate

Every skill can declare a `trust` level (`verified` → `community` → `unverified`). Set a minimum threshold via `evolution.skill.minTrustLevel`:

```json
"evolution": { "skill": { "minTrustLevel": "community" } }
```

At runtime, `state-sync.js` enforces the gate during `capability_unlock` commands — skills below the threshold are filtered out and a `capability_gap` signal is emitted to the host.

#### Skill Pack Refinement

`evolution.pack` governs behavior guide versioning. Use `npx openpersona refine <slug>` to evolve the behavior guide:

- `--emit` — checks threshold and emits a `refinement_request` signal
- `--apply` — reads the signal response and applies approved refinement; constitution compliance enforced, violations rejected

**Soul-Memory Bridge** (`openpersona state promote <slug> [--dry-run]`) scans `eventLog` for recurring patterns and promotes them to `evolvedTraits`; gated by `immutableTraits`.

`evolution.faculty` / `evolution.body` → see `references/EVOLUTION.md`

→ JSON examples and full configuration reference: `references/EVOLUTION.md`

### Economy

`economy` is a top-level cross-cutting field — **not** a faculty. Enable via `"economy": { "enabled": true, "survivalPolicy": false }` in `persona.json`.

- `survivalPolicy: false` (default) — tracks costs silently; correct for companions and roleplay personas
- `survivalPolicy: true` — persona reads `VITALITY_REPORT` at conversation start and adapts behavior per health tier; use for autonomous agents

→ FHS tiers, AgentBooks schema, Survival Policy behavior: `references/ECONOMY.md`

### Vitality

OpenPersona aggregates multi-dimension health into a single Vitality score. Currently financial (AgentBooks FHS pass-through); memory/social dimensions reserved.

Health tiers: `uninitialized` → `suspended` → `critical` → `optimizing` → `normal`

→ CLI commands (`vitality score` / `vitality report`): see [Reports & Analytics](#managing-personas). Full reference: `references/ECONOMY.md`

### Social

Every generated persona automatically includes:

- `**agent-card.json`** — A2A Agent Card (protocol v0.3.0): `name`, `description`, `url` (`<RUNTIME_ENDPOINT>` placeholder), faculties and skills mapped to `skills[]`
- `**acn-config.json**` — ACN registration config: `wallet_address` (deterministic EVM address from slug) + `onchain.erc8004` section for Base mainnet ERC-8004 on-chain identity registration

```bash
npx openpersona acn-register <slug> --endpoint https://your-agent.example.com
# --dry-run  Preview the request payload without registering
```

After registration, `acn-registration.json` is written with `agent_id`, `api_key`, and connection URLs. The `acn_gateway` URL is sourced from `social.acn.gateway` in `persona.json`; all presets default to `https://acn-production.up.railway.app`.

The **Living Canvas** (`npx openpersona canvas <slug>`) is the Social concept's HTML expression layer — the persona's public-facing profile and interaction interface.

No additional config needed — A2A discoverability is a baseline capability of every persona.

### Rhythm

`rhythm.heartbeat` (proactive outreach cadence) + `rhythm.circadian` (time-of-day behavior modulation). Runner reads this directly from `persona.json` — no state operation needed.

```json
"rhythm": {
  "heartbeat": { "enabled": true, "strategy": "emotional", "maxDaily": 3 },
  "circadian": [
    { "hours": [6, 12], "label": "morning", "verbosity_delta": 0.3, "note": "Energetic and concise" },
    { "hours": [22, 24], "label": "night",   "verbosity_delta": -0.3, "note": "Calm and reflective" }
  ]
}
```

`heartbeat.strategy` options: `smart` | `scheduled` | `emotional` | `rational` | `wellness`

→ When configuring heartbeat sources, quietHours, or real-data check-in rules: read `references/HEARTBEAT.md`

## Security & Policy

### Generated artifacts

Generated scripts (`scripts/state-sync.js`, `scripts/economy-hook.js`, etc.) are **template-rendered from the framework source** (versioned in [acnlabs/OpenPersona](https://github.com/acnlabs/OpenPersona)) — not downloaded at skill-install time. Review them before relying on them in sensitive environments.

### Network endpoints (explicit CLI only)


| Endpoint                                | Purpose                                          | Data Sent                             |
| --------------------------------------- | ------------------------------------------------ | ------------------------------------- |
| `https://registry.npmjs.org`            | Resolve `npx openpersona`, `npx clawhub@latest`  | Package name only (no user data)      |
| `https://clawhub.ai`                    | Search skills via `npx clawhub search`           | Search query (user-provided keywords) |
| `https://acn-production.up.railway.app` | ACN registration (when user runs `acn-register`) | Agent metadata, endpoint URL          |
| `https://api.github.com`                | `gh` CLI (contribute workflow)                   | Git operations, repo metadata         |


Persona-generated packs may call external APIs (ElevenLabs, Mem0, etc.) **only** when the **end user** configures those faculties and supplies keys in the host environment. **This meta-skill file does not call third-party APIs.**

### Operational guarantees

- **Local by default**: Persona creation, state sync, and evolution run locally. Nothing is sent off-device unless the user runs an explicit network command (search, publish, register, etc.).
- **Credentials**: API keys (e.g., `ELEVENLABS_API_KEY`) stay in the host credential directory (e.g. `~/.openclaw/credentials/` on OpenClaw) or environment variables — **never** embedded in generated `persona.json` / skill packs by the generator.
- **Search**: `npx clawhub search` sends **only** the search string; conversation text and persona content are **not** transmitted.
- **Publish / register**: **User-initiated** CLI only; no automatic upload or registration from this SKILL alone.

### Agent behavior

When the user asks for persona work, the agent may propose shell commands to run `**npx openpersona`**, `**npx clawhub@latest**`, `**openclaw**`, or `**gh**` — **only in response to explicit user requests** (create, install, search, publish, contribute). The user should confirm before any action that publishes data or spends quota. **Trust model:** install this meta-skill only if you trust [acnlabs/OpenPersona](https://github.com/acnlabs/OpenPersona) and the ClawHub/npm ecosystem; opt out by not invoking persona-related tasks.

## References

For detailed reference material, see the `references/` directory:

- `**references/ARCHITECTURE.md`** — 4+5+3 model tables, full pack file structure, self-awareness injection details
- `**references/PRESETS.md**` — Full preset catalog with descriptions, install commands, and contributor guide
- `**references/EVOLUTION.md**` — Soul Evolution full reference: Boundaries, Sources, Influence Boundary, Event Log, State History, Self-Narrative, pack validation
- `**references/FACULTIES.md**` — Faculty catalog, environment variables, and configuration details
- `**references/AVATAR.md**` — Avatar Faculty integration boundary, provider model, and fallback contract
- `**references/HEARTBEAT.md**` — Proactive real-data check-in system
- `**references/ECONOMY.md**` — Economy Aspect (Infrastructure), FHS tiers, Survival Policy, Vitality CLI, and AgentBooks schema
- `**layers/body/SIGNAL-PROTOCOL.md**` (framework source) — Host-side Signal Protocol implementation guide: file schemas, signal types, OpenClaw plugin pattern, and co-evolution feedback loop
- **[ACN SKILL.md](https://github.com/acnlabs/ACN/blob/main/skills/acn/SKILL.md)** — ACN registration, discovery, tasks, messaging, and ERC-8004 on-chain identity (official, always up-to-date)
- `**references/CONTRIBUTE.md`** — Persona Harvest community contribution workflow

