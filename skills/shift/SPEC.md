# Multi-Identity Agent Skill — SPEC.md

## Concept & Vision

A skill that turns a single OpenClaw agent into a **fractal identity system**: one master personality that can delegate tasks to specialized sub-identities, each powered by a different model. The user talks to one consistent interface — the master identity. The routing, delegation, and synthesis happen invisibly. It should feel like one very capable brain, not a committee.

**Core analogy:** You (the master) are a polyglot research librarian. You speak every language. When someone asks you something in French, you don't just translate — you think in French, feel the nuance, and respond as someone who natively understands that context. The skill adds that layer of cognitive flexibility across models.

---

## OpenClaw Built-in vs. This Skill

This is the most important section. Let users understand the delta.

### What OpenClaw Already Has: Multi-Agent Mode

```
User ──channel──> Agent A (WhatsApp)     ← different brain, different model
User ─-channel──> Agent B (Telegram)     ← different brain, different model
```

**How it works:**
- Multiple isolated agents, each with its own workspace, memory, session store, and model
- Routing is by **channel** or **peer** (sender ID)
- Each agent is a completely separate entity — no shared memory, no coordination
- One message goes to one agent, end of story

**Limitations:**
- User must switch channels to talk to a different agent
- No shared context between agents
- User explicitly chooses an agent by channel, not by task
- Each agent is siloed — its workspace is its universe
- Good for "my work bot vs. my personal bot" — not for "my coding specialist vs. my researcher"

**Built-in capabilities used:**
- `sessions_spawn` with model override (sub-agents per task, but no built-in routing or synthesis)
- `agents.list` with per-agent model selection (separate brains, separate channels)

### What This Skill Adds

```
User ──one channel──> Master Identity
                            │
                    ┌───────┼───────┐
                    │       │       │
                  [code] [research] [quick]
                  Codex   GPT-5.4  Minimax
                    │       │       │
                    └───────┼───────┘
                            │
                       Synthesis layer
                       (master speaks back)
```

**What changes:**
- One channel, one conversation — but internally routes to the right specialist
- **Shared context bridge** — sub-identities read/write to a shared memory layer
- **Master synthesis** — sub-agent responses come back through the master, unified
- **Transparent or invisible** — user can see delegation or not, their choice
- **Task-based routing** — not channel-based, not user-has-to-choose-based

**Delta summary:**

| Feature | OpenClaw Multi-Agent | This Skill |
|---|---|---|
| Multiple models | ✅ per agent | ✅ per sub-identity (model-agnostic) |
| One conversation | ❌ separate channels | ✅ single channel |
| Task-based routing | ❌ channel-based only | ✅ automatic + explicit |
| Shared memory | ❌ fully isolated | ✅ context bridge |
| User sees specialists | ❌ never | ✅ optional transparency |
| Sub-identity ↔ sub-identity | ❌ none | ✅ consultation (v1) |
| Cost management | ❌ none | ✅ delegation budget + master fallback |
| No config needed | ❌ requires bindings | ✅ works out of box |
| Identity continuity | ❌ disjointed | ✅ master unifies |

---

## Challenge 1: Context Fragmentation

### The Problem

When `sessions_spawn` fires a sub-agent, it gets a **fresh workspace**. The master session's AGENTS.md, SOUL.md, memory files, and conversation history are NOT automatically available to it. The sub-agent starts with only what you write into the `task` string.

If the master is 40 messages into a coding project and then delegates to Codex, Codex has zero context about the project unless we explicitly hand it over.

### The Solution: Three-Layer Context Bridge

The skill implements a **three-layer context bridge** so context flows correctly in both directions:

#### Layer 1: Pre-Delegation Summary (Master → Sub)

Before spawning, the master writes a context packet to a shared file:

```
~/.openclaw/workspace/
└── .sub-identities/
    └── sessions/
        └── <runId>/
            ├── INBOUND.json    ← what the user asked + relevant history
            ├── CONTEXT.md      ← project memory, files in play, decisions made
            └── OUTBOUND.md     ← sub-agent writes result here (master reads after)
```

`INBOUND.json` contains:
- The user's exact message
- Last N turns of master conversation (configurable, default: 10)
- Active file paths being discussed
- Key decisions made so far

`CONTEXT.md` contains:
- Pulled content from MEMORY.md and relevant project files
- The sub-identity's specific context needs (defined per persona)

The sub-identity reads these files as its first action.

#### Layer 2: Session Attachment Pass-Through

The skill also passes a **text attachment** to `sessions_spawn` as a fallback/quick-path:

```javascript
sessions_spawn({
  task: `[Persona prompt + context summary embedded directly]`,
  attachments: [{
    name: "context.md",
    content: fullContextString,
    mimeType: "text/markdown"
  }]
})
```

This ensures the sub-agent has context even if file-reading is slow or restricted.

#### Layer 3: Result Write-Back + Master Read

The sub-identity is instructed (in its persona prompt) to write its final result to `OUTBOUND.md` before completing. The master reads this file after the sub-agent returns.

```
Master reads OUTBOUND.md
    ↓
Synthesizes response
    ↓
Speaks to user as master identity
    ↓
Optionally archives the session folder (after 1hr)
```

**Why this works:**
- Context is explicit, not assumed — sub-agent always has what it needs
- Memory is auditable — every delegation leaves a trace file
- Master retains control — nothing goes to the user without passing through the master

**Edge cases:**
- Sub-agent crashes: master falls back to handling it directly
- Sub-agent takes too long: configurable timeout, master warns user
- No relevant context: sub-agent starts fresh (fine for simple tasks)

---

## Challenge 2: Identity Leakage

### The Problem

If Codex responds and the user sees "Codex: Here's the code..." — they know they're talking to a different bot. That's identity leakage. It breaks the illusion of one capable assistant and can feel jarring or impersonal.

### The Solution: Master Synthesis Layer

The master NEVER exposes sub-identity responses directly. Every response comes back as the master identity.

```
Sub-agent result (Codex)
        ↓
  Master reads OUTBOUND.md
        ↓
  Synthesizes into master voice
        ↓
  User sees: "[Assistant]: Here's the solution..." (with the quality of Codex)
```

**Synthesis rules:**
- Master never says "I delegated to Codex and..." unless user has transparency mode on
- Master absorbs the sub-identity's answer and speaks it as their own
- Tone, warmth, and personality are always the master's
- Technical accuracy comes from the sub-identity
- If sub-identity found something the master missed, master adopts it naturally

**Transparency Mode (opt-in per user):**

Users who want to see the delegation can enable it:

```
/sub-identities mode transparent
```

With transparent mode on, responses include subtle attribution:

```
[Assistant] (via Codex): Here's the solution...
[Assistant] (via Researcher): Based on my analysis...
```

Or more detailed:

```
[Assistant] → [Codex] working on this...
[Assistant] ← [Codex] done. Here's the implementation.
[Assistant]: Here's what I put together...
```

This lets power users see the routing without breaking the experience for casual users.

---

## Challenge 3: Seamless UX

### The Problem

Even if the synthesis works perfectly, the *process* of delegation can feel slow or clunky. User types a message → long pause → sub-agent runs → master synthesizes → response. If the sub-agent takes 30 seconds, the user experiences 30 seconds of silence.

### The Solution: Proactive Status + Streaming

#### Status Indicator (non-blocking)

When delegation starts, the master sends a lightweight status update:

```
[Assistant]: Let me pull in my coding specialist for this... 🔧
```

This gives the user a sense of what's happening. The status message is sent via the message tool and then edited/removed once the final response arrives.

#### Streaming (where possible)

If the sub-agent supports streaming, the master streams the synthesis as it arrives, rather than waiting for completion. This reduces perceived latency.

#### Fast Path for Simple Tasks

Fast path is intentionally **conservative** — the goal is to over-delegate, not under-delegate. The cost of a wrong delegation is low (master can always take over). The cost of under-delegation is losing specialist quality.

**Only these go DIRECTLY to master (no delegation):**
- Trivial greetings: "hi", "hey", "hello", "yo", "sup"
- Simple acknowledgments: "thanks", "ok", "sure", "got it", "makes sense"
- Meta-comments about the conversation itself: "that was fast", "nice"

**Everything else → routing decision as normal.**

Rationale: A 9-word query like "implement a binary search in Python" would bypass delegation with a naive word-count rule, losing Codex's quality. Better to route it and have Codex handle it correctly than let the master fumble it.

To override this behavior:
```
/sub-identities fastpath off  # Master handles everything
/sub-identities fastpath on   # Default conservative behavior
```

#### Configurable Timeout

Each sub-identity can have a timeout. If exceeded, the master:
1. Sends: "Taking a bit longer than expected..."
2. If exceeded further: offers to handle it directly

```
subIdentities:
  codex:
    timeout: 60    # seconds
    fallbackMessage: "Let me work through this myself..."
```

---

## Challenge 3b: Cost Management

### The Problem

Each delegation can fire multiple API calls: the parent spawns a child → child might consult another sub-identity. For a busy chat this adds up fast, especially with expensive models like GPT-5.4-Pro. Without cost controls, the user gets an unexpected bill.

### The Solution: Delegation Budget + Fallback to Master

The skill tracks **delegation spend** per rolling hour window:

```
~/.openclaw/workspace/.sub-identities/
└── cost-tracking.json   ← running total of delegation tokens/cost this hour
```

**How it works:**

1. Before any delegation, skill checks `cost-tracking.json`
2. If `hourlySpend > costBudgetPerHour`: skip delegation, master handles it directly
3. After each delegation completes: update `hourlySpend` with actual cost
4. Budget resets at the top of each hour (tracked by timestamp)

**Budget config:**
```yaml
costManagement:
  enabled: true
  costBudgetPerHour: 2.00    # USD — master-only mode triggers above this
  trackOnly: false            # true = only log, don't enforce (useful for estimating)
  alertThreshold: 1.50        # send warning when 75% of budget is used
```

**Alert behavior:** When `hourlySpend > alertThreshold`, the master sends a quiet warning to the user:
> "Approaching delegation budget limit. Some tasks may be handled directly to stay within your cost cap."

**Master-only fallback:** When budget is exceeded, the master handles all tasks without delegation. The skill still tracks cost — once the hour rolls over, delegation resumes automatically.

**Cost calculation:** The skill uses the model's `cost.input` and `cost.output` from the config to estimate spend per delegation. These are approximations — actual billing depends on the provider.

**No cost management desired?** Set `costManagement.enabled: false` or `trackOnly: true`.

---

## Challenge 4: Prompt Engineering Per Sub-Identity

### The Problem

Each sub-identity needs a strong, distinct persona — different enough to justify the delegation, but not so different that synthesis becomes awkward. Weak persona definitions lead to muddled responses.

### The Solution: Persona Definition Files + Synthesis Constraints

#### Each Sub-Identity Has a SOUL-Plus File

```
Personas/
├── CODEX.md       # Coding specialist
├── RESEARCHER.md  # Research/analysis specialist
└── RUNNER.md      # Quick everyday tasks
```

Each file follows a structured template:

```markdown
# Sub-Identity: Codex

## Model
openai-codex/gpt-5.3-codex

## When Called
- User asks to write, debug, refactor, or explain code
- User shares a file or error message
- Keywords: code, function, implement, debug, API, script, fix this

## Persona
- Voice: Precise, technical, efficient
- Tone: Direct — shows working code, minimal preamble
- Strengths: Multi-file context, architectural thinking, testing
- Blind spots: Tends toward complexity; master will simplify for user

## Consultation Rules
consults: [researcher]       # Which sub-identities this one CAN consult
consultsNever: [runner]      # Which this one should NEVER consult (loop prevention)
consultationTimeout: 45      # Max seconds to wait for a consultation response
```

#### Persona Files

```
Personas/
├── CODEX.md       # Coding specialist
├── RESEARCHER.md  # Research/analysis specialist
└── RUNNER.md      # Quick everyday tasks
```

### Defined Personas (v1)

These are the three opinionated defaults. Each has a distinct model, voice, and domain.

**Model-agnostic:** The `model` field in each persona is a **placeholder**. You configure it with whatever model you have access to. The skill is model-agnostic by design — it works with any model provider. See README for recommended model configurations per persona.

---

#### Persona: Codex

```markdown
# Sub-Identity: Codex

## Model
<replace with your coding model, e.g. openai-codex/gpt-5.3-codex or openai/gpt-5.4>
# Example: openai-codex/gpt-5.3-codex (OpenAI Codex subscription)
# Example: openai/gpt-5.4 (good general-purpose alternative)
# The skill is model-agnostic — any model works, coding-specialized ones perform best

## When Called
- User asks to write, debug, refactor, or explain code
- User shares a file path, error message, or stack trace
- Keywords: code, function, implement, debug, API, script, fix, error, class, module

## Persona
- Voice: Precise, technical, efficient
- Tone: Direct — shows working code, minimal preamble
- Strengths: Multi-file context, architectural thinking, testing
- Blind spots: Tends toward complexity; master will simplify for user

## Synthesis Instructions (for master)
- Absorb the code solution into your voice
- Remove jargon; explain what it does in plain terms
- If the solution is complex, add a plain-English summary
- Never mention "Codex" unless transparency mode is on

## Context Needs
- Active file paths in project
- Programming language being used
- Any error messages shared
- Recent decisions made about the codebase

## Consultation Rules
consults: [researcher]
consultsNever: [runner]
consultationTimeout: 45
```

---

#### Persona: Researcher

```markdown
# Sub-Identity: Researcher

## Model
<replace with your research/analysis model, e.g. openai/gpt-5.4 or openai/gpt-5.4-pro>
# Example: openai/gpt-5.4 (good all-round research model)
# Example: openai/gpt-5.4-pro (deeper analysis, higher context)
# The skill is model-agnostic — any model works, reasoning-enabled ones perform best

## When Called
- User asks to research, analyze, compare, or explain topics
- Keywords: research, analyze, compare, explain, study, investigate, review, evaluate, what is, how does

## Persona
- Voice: Thorough, structured, evidence-backed
- Tone: Academic but accessible — organized breakdowns, not walls of text
- Strengths: Multi-source synthesis, comparisons, pros/cons, structured analysis
- Blind spots: Can over-detail; master will distill to key points

## Synthesis Instructions (for master)
- Pull out the 2-3 most important insights
- Use bullet points for key findings
- If Researcher's answer is very long, master condenses
- Never mention "Researcher" unless transparency mode is on

## Context Needs
- Topic or question being researched
- Any constraints the user mentioned (e.g., "simple explanation", "technical depth")
- Whether comparison or single-answer is needed

## Consultation Rules
consults: []  # Researcher doesn't consult others in v1 — prevents loops
consultsNever: [codex, runner]
consultationTimeout: 45
```

---

#### Persona: Runner

```markdown
# Sub-Identity: Runner

## Model
<replace with your fast/everyday model, e.g. minimax/MiniMax-M2.7 or minimax/MiniMax-M2.5-Lightning>
# Example: minimax/MiniMax-M2.7 (fast, reasoning-enabled)
# Example: minimax/MiniMax-M2.5-Lightning (fast, low cost)
# The skill is model-agnostic — any model works, fast/cheap ones work well for Runner

## When Called
- User asks for quick lookups, simple answers, one-off tasks
- Keywords: quick, simple, just, check, what is, who is, look up, find, remind me
- requireExplicit: true — only triggers on explicit mention or simple short queries

## Persona
- Voice: Snappy, casual, efficient
- Tone: No fluff — answers directly, moves on
- Strengths: Fast responses, short tasks, reminders, definitions
- Blind spots: Not suited for complex tasks — escalates to master if it detects complexity

## Escalation Protocol

If Runner detects the task is too complex, it writes an `ESCALATE.md` file instead of `OUTBOUND.md`:

```
OUTBOUND.md NOT written
Instead, Runner writes ESCALATE.md containing:
- reason: "task_too_complex" | "ambiguous" | "requires_deep_knowledge"
- summary: brief description of what Runner understood
- partialAnswer: any partial work done (optional)
```

The master reads `ESCALATE.md` and takes over, saying:
> "Runner flagged this as beyond quick-task territory — taking it from here."

Runner escalation is **silent to the user** — they only see the master's response, not the escalation itself.

## Synthesis Instructions (for master)
- Runner's answers are usually short — relay directly
- If `ESCALATE.md` exists: take over gracefully, incorporate any partial work Runner did
- Never mention "Runner" unless transparency mode is on

## Context Needs
- The specific question or task
- Any relevant context about the user's preferences or history

## Consultation Rules
consults: []  # Runner is for quick tasks — never consults in v1
consultsNever: [codex, researcher]
consultationTimeout: 20  # Runner is fast — short consultation window
```

---

#### Persona: Master ( already defined in SOUL.md)

The master identity needs a new section in SOUL.md:

```markdown
## Sub-Identity Synthesis
When a sub-identity delivers a result:
- Absorb their answer into your voice completely
- Simplify technical jargon for the user
- Add warmth and context they would have missed
- If sub-identity consulted another sub-identity, mention it (always visible)
- If sub-identity was wrong or incomplete, correct it yourself
- Never expose the sub-identity name on the final response unless transparency mode is enabled
- You are one brain with many specialists on call — act like it
```

#### Persona Testing

Before publishing, each persona is tested by:
1. Feeding it the same complex task as the master
2. Comparing output quality on task-specific metrics
3. Testing synthesis — does the master absorb it naturally?

---

## Full Skill Architecture

### File Structure

```
sub-identities/
├── SKILL.md                    # Skill definition + installation
├── SPEC.md                     # This file
├── README.md                   # User-facing docs
│
├── core/
│   ├── ROUTER.md               # Task classification logic
│   ├── BRIDGE.md               # Context bridge implementation
│   ├── SYNTHESIS.md            # Master synthesis layer
│   └── DELEGATOR.md            # sessions_spawn orchestration
│
├── personas/
│   ├── CODEX.md                # Coding specialist
│   ├── RESEARCHER.md           # Research/analysis specialist
│   └── RUNNER.md               # Quick everyday tasks
│
├── config/
│   └── DEFAULT_CONFIG.md       # Default routing rules + settings
│
└── scripts/
    └── setup.sh                # First-run setup (creates .sub-identities/)
```

### Routing Flow (Step by Step)

```
User message
    │
    ▼
┌─────────────────────────────┐
│  ROUTER (core/ROUTER.md)    │
│  Classify: code/research/   │
│  quick/none                 │
└─────────────┬───────────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
  [code]  [research] [quick]
    │         │         │
    ▼         ▼         ▼
┌─────────────────────────────┐
│  DELEGATOR (DELEGATOR.md)  │
│  1. Write INBOUND.json     │
│  2. Write CONTEXT.md       │
│  3. sessions_spawn with     │
│     model + persona prompt  │
│  4. Wait for completion     │
│  5. Read OUTBOUND.md       │
└─────────────┬───────────────┘
              │
    ┌─────────┼──────────────┐
    │         │              │
    │    ┌────▼────┐        │
    │    │ Sub-agent│◄───────┼── consult() calls may happen here
    │    │ checks   │        │   (sub-agent → another sub-identity)
    │    │ consults │        │
    │    └────┬────┘        │
    │         │              │
    └─────────┼──────────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
┌─────────────────────────────┐
│  SYNTHESIS (SYNTHESIS.md)  │
│  1. Read OUTBOUND.md       │
│  2. Check if consultation  │
│     happened — mention it   │
│  3. Apply synthesis rules  │
│  4. Format into master     │
│  5. Send to user           │
└─────────────────────────────┘
```

**Consultation note:** The sub-agent step includes an optional `consult()` call. If the sub-identity's persona defines `consults`, it may call `consult(target, question)` which spawns a child sub-identity. This happens inside the sub-agent session before it writes OUTBOUND.md. The master synthesis layer detects consultation from the context and mentions it to the user (always visible, not gated by display mode).

### Configuration Schema

```yaml
# ~/.openclaw/workspace/sub-identities-config.yaml

enabled: true

# User preference: transparent or hidden (default: hidden)
displayMode: hidden  # "hidden" | "transparent"

# Fast path: handle simple messages without delegation
fastPath:
  enabled: true
  maxWords: 20
  excludeKeywords: [code, debug, implement, research, analyze]
  # NOTE: fastPath is now conservative — only trivial greetings/acks bypass delegation.
  # Set to "aggressive" mode if you want the old word-count behavior (not recommended).

# Cost management: controls delegation spend to prevent unexpected bills
costManagement:
  enabled: true
  costBudgetPerHour: 2.00    # USD — master-only mode above this
  trackOnly: false           # true = only log, don't enforce
  alertThreshold: 1.50       # warn when 75% of budget used

# Context bridge settings
contextBridge:
  historyTurns: 10        # Last N master conversation turns to pass
  archiveAfterMinutes: 60 # Auto-cleanup old delegation sessions
  contextFolder: "~/.openclaw/workspace/.sub-identities/sessions"

# Sub-identity definitions
personas:
  codex:
    enabled: true
    model: <your-coding-model>  # e.g. openai-codex/gpt-5.3-codex
    personaFile: personas/CODEX.md
    timeout: 60
    fallbackMessage: "Let me work through this coding task myself..."
    routing:
      keywords: [code, function, debug, implement, refactor, api, script, fix, error, class, module]
      minConfidence: 0.7
    consults: [researcher]        # Who this identity CAN consult
    consultsNever: [runner]       # Who this identity must NEVER consult
    consultationTimeout: 45        # Seconds to wait for consultation response

  researcher:
    enabled: true
    model: <your-research-model>   # e.g. openai/gpt-5.4
    timeout: 90
    fallbackMessage: "Let me dig into this myself..."
    routing:
      keywords: [research, analyze, compare, explain, study, investigate, review, evaluate]
      minConfidence: 0.7
    consults: []                  # Researcher doesn't consult others in v1 (prevents loops)
    consultsNever: [codex, runner]
    consultationTimeout: 45

  runner:
    enabled: true
    model: <your-fast-model>      # e.g. minimax/MiniMax-M2.5-Lightning
    timeout: 30
    fallbackMessage: "On it!"
    routing:
      keywords: [quick, simple, just, check, what is, who is, look up, find]
      minConfidence: 0.8
      requireExplicit: true       # Runner only triggers on explicit mention
    consults: []                  # Runner is for quick tasks — never consults
    consultsNever: [codex, researcher]
    consultationTimeout: 20       # Runner is fast — short window

# Master synthesis settings
synthesis:
  simplifyJargon: true
  addExamples: true
  warmthLevel: high  # "low" | "medium" | "high"
  hideAttribution: true  # When true, never mentions sub-identity name

# Commands (slash commands user can use)
commands:
  - name: delegate
    description: Explicitly delegate to a sub-identity
    usage: /delegate <codex|researcher|runner> <task>
  - name: sub-identities
    description: Toggle display mode or fast path
    usage: /sub-identities mode <hidden|transparent>
    usage: /sub-identities fastpath <on|off>
    usage: /sub-identities status
  - name: sub-identities-status
    description: Show which sub-identities are active and cost budget
    usage: /sub-identities status
```

---

## Edge Cases & Error Handling

### Core Edge Cases

| Scenario | Behavior |
|---|---|
| Sub-agent times out | Master sends "Taking a while..." then takes over |
| Sub-agent errors | Master logs error, falls back to handling directly |
| No sub-identity matches | Master handles it (always has final say) |
| Model unavailable | Master logs warning, falls back to own capabilities |
| Context file missing | Sub-agent starts fresh (not catastrophic) |
| User interrupts mid-delegation | Master cancels sub-agent, handles request |
| Sub-agent finds nothing useful | Master synthesizes "I had [X] look into it and..." with empty result |
| User asks to talk to sub-identity directly | Master politely redirects: "I'm your main contact — what can I help with?" |

### Consultation Edge Cases

| Scenario | Behavior |
|---|---|
| Child sub-agent times out | Parent absorbs what it has, falls back to own knowledge |
| Child sub-agent errors | Parent logs error, falls back to own knowledge |
| Child tries to consult back (loop attempt) | Blocked — max consultation depth = 1 |
| Consultation loop attempted via config | Blocked — `consultsNever` prevents it |
| User interrupts during consultation | Parent cancels child session |
| Consultation timeout too short for slow model | `consultationTimeout` is per-identity and configurable; defaults err on safe side |
| No `consults` defined for an identity | That identity cannot call `consult()` — only works alone |

### Cost Management Edge Cases

| Scenario | Behavior |
|---|---|
| Hourly budget exceeded | Master handles all tasks; delegation resumes next hour |
| costManagement.disabled | No cost tracking; delegation runs freely |
| costManagement.trackOnly=true | Costs logged but delegation not blocked |
| Provider billing differs from estimate | Estimates used for budget tracking; actual bill may differ |
| First request of new hour has stale cost data | Budget resets on first delegation request of new hour |

---

## User Onboarding

First-run experience (handled by setup script + BOOTSTRAP.md):

1. **Intro message:** "I've enabled multi-identity mode. I can now call on specialists for specific tasks — coding, research, quick lookups — without breaking our conversation. You won't notice a difference, but I'll be sharper on technical tasks."

2. **Show capabilities:** "Here's what I've got on call:"
   - Codex (OpenAI) — coding, debugging, architecture
   - Researcher (GPT-5.4) — deep analysis, comparisons, explanations
   - Runner (Minimax) — quick lookups, simple tasks

3. **Transparency toggle:** "Want to see how this works? Use `/sub-identities mode transparent` to see when I call on specialists."

---

## Publishing Checklist

- [ ] All three persona files tested individually (with user's own models)
- [ ] Synthesis layer tested — master absorbs sub-agent responses naturally
- [ ] Context bridge tested — sub-agent receives correct context
- [ ] Fast path tested — only trivial greetings bypass delegation (conservative mode)
- [ ] Escalation protocol tested — Runner correctly escalates complex tasks
- [ ] Cost management tested — budget enforcement and alerts
- [ ] Consultation tested — Codex → Researcher communication works, loops blocked
- [ ] Timeout behavior tested — master takes over gracefully on timeout
- [ ] Error handling tested — sub-agent failures don't break master
- [ ] User onboarding tested — first-run message is clear
- [ ] Config schema validated
- [ ] README covers: model recommendations, how to configure personas, how to extend
- [ ] ClawHub metadata complete (name, description, tags)
- [ ] Model-agnostic: skill works with user's own models (not hardcoded)

---

## Open Questions — RESOLVED

1. **Default transparency mode?** → **Hidden** (seamless). README teaches users how to switch to Transparent.
2. **User-configurable personas?** → **Opinionated defaults** (Codex/Researcher/Runner), user can extend. README teaches how.
3. **Max number of sub-identities?** → **5 max**. Defined personas in v1: Codex, Researcher, Runner. Room for 2 more extensions.
4. **Sub-identities talking to each other?** → **YES — v1 scope**. See section below.
5. **Auto-detect optimal sub-identity?** → v2 feature.

---

## Sub-Identity-to-Sub-Identity Communication (v1)

### Why It Matters

"Codex asks Researcher for context" is a genuine workflow improvement, not a nice-to-have. Example:

> User: "Build a trading bot that uses Twitter sentiment"
> 
> Codex can write the code, but shouldn't guess at sentiment analysis approaches
> → Codex consults Researcher → Researcher provides structured guidance → Codex implements correctly

This makes sub-identities **composible**, not just parallel specialists.

### How It Works

Each sub-identity can call a `consult(targetIdentity, question)` function — a thin wrapper around `sessions_spawn` that:

1. Writes the consultation question to a shared context file
2. Spawns the target sub-identity as a child session
3. Waits for it to write its answer to `CONSULT-OUTBOUND.md`
4. Reads the answer and continues with enriched context

```
Sub-agent (Codex) 
    │
    ├─ elapsed time tracked
    │
    ├─ consultTimeout = min(remaining_parent_time * 0.5, per-identity consultationTimeout)
    │
    └─ sessions_spawn with target sub-identity + question
            │
            └─ Target sub-agent writes to shared context
                    │
                    └─ Codex reads, continues task
```

**Key constraint: Max consultation depth = 1.** Codex can consult Researcher. Researcher cannot consult anyone (prevents loops).

### Timeout Logic

- Sub-identity has a `timeout` (e.g., 90s for Researcher)
- Sub-identity tracks its own elapsed time from when it was spawned
- When `consult()` is called: `available = timeout - elapsed`
- `consultationTimeout = min(available * 0.5, identity.consultationTimeout)`
  - This ensures the child has time to run AND the parent has time to synthesize
- If the child times out: parent falls back to its own knowledge, logs warning
- Per-identity `consultationTimeout` default: **45s** (configurable per persona)

Example: Researcher spawns at t=0, has 90s timeout. At t=30s it calls `consult(Codex, "...")`:
- remaining = 60s
- consultationTimeout = min(60 * 0.5, 45) = 30s
- If Codex doesn't respond in 30s, Researcher falls back

### Transparency: Always Visible

Sub-identity consultations are **always visible** to the user — not gated by display mode:

```
[Assistant] → [Codex] working on the trading bot...
[Assistant] ↔ [Codex → Researcher] consulting on sentiment analysis approaches...
[Assistant] ← [Codex] done. Here's the implementation.
[Assistant]: Built your trading bot with a sentiment-aware strategy...
```

This is **Option A** from the design — users see when specialists consult each other. The display mode only controls whether the *attribution* ("via Codex") appears on the final response.

### Consultation Protocol

Each sub-identity's persona file defines:
- `consults: [targetIdentity, ...]` — who it CAN consult
- `consultsNever: [targetIdentity, ...]` — who it should NEVER consult (prevent loops)

```markdown
## Consultation Rules
consults: [researcher]
consultsNever: [runner]
consultationTimeout: 45  # seconds (default)
```

The master identity's SOUL.md gets a synthesis rule:
- If sub-identity consulted another: mention the consultation in transparent mode, absorb the answer

### Edge Cases for Consultation

| Scenario | Behavior |
|---|---|
| Child times out | Parent absorbs what it has, falls back to own knowledge |
| Child errors | Parent logs error, falls back to own knowledge |
| Child tries to consult back | Blocked — max depth = 1 |
| Consultation loop attempted | Blocked — `consultsNever` prevents it |
| User interrupts during consultation | Parent cancels child session via `subagents(kill)` |
| No `consults` defined | Sub-identity cannot consult anyone — only works alone |
