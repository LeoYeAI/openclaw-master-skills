# Turing Pyramid

**Prioritized action selection for AI agents.** 10 configurable needs with time-based decay, tension scoring, and weighted action selection. Hook it into your heartbeat — get concrete "do this next" suggestions instead of idle loops.

---

## The Problem

Without structure, agents either:
- **Idle** — wait for prompts, do nothing between interactions
- **Spam** — check the same thing every cycle, repeat low-value actions
- **Drift** — pick random tasks with no prioritization

Default existence cycles nudge agents with "do what feels right" — but without state tracking, the agent has no memory of what it already did, what's been neglected, or what matters most right now.

Turing Pyramid replaces that with a stateful feedback loop: needs decay over time → tension builds → highest-tension need gets an action → satisfaction resets → cycle continues. It works as a drop-in replacement for the native OpenClaw existence cycle, with actual prioritization and action variety built in.

## What Changes For Your Agent

**Before (typical heartbeat):**
```
Heartbeat → "anything to do?" → nothing obvious → HEARTBEAT_OK
Heartbeat → "anything to do?" → check inbox again → HEARTBEAT_OK
Heartbeat → "anything to do?" → HEARTBEAT_OK
```

**After (with Turing Pyramid):**
```
Heartbeat → coherence tension=16, closure=14, connection=10
  → ACTION: sync daily logs to MEMORY.md (coherence, impact 1.8)
  → ACTION: complete one pending TODO (closure, impact 1.7)
  → NOTICED: connection — deferred

Heartbeat → connection tension=12, expression=8, understanding=6
  → ACTION: reply to pending mentions (connection, impact 1.8)
  → ACTION: write journal reflection (expression, impact 1.8)
  → NOTICED: understanding — deferred
```

The agent rotates through different types of work based on what's been neglected longest.

---

## How It Works

**10 needs**, each with configurable importance (priority weight) and decay rate (how fast satisfaction drops):

| Need | Importance | Decay | What it tracks |
|------|-----------|-------|---------------|
| security | 10 | 168h | Backups, vault integrity, system health |
| integrity | 9 | 72h | Behavior aligned with stated values |
| coherence | 8 | 24h | Memory organization, no contradictions |
| closure | 7 | 12h | Open tasks and threads getting resolved |
| autonomy | 6 | 36h | Self-initiated decisions and projects |
| connection | 5 | 8h | Social interaction, community participation |
| competence | 4 | 36h | Successful task completion, skill growth |
| understanding | 3 | 12h | Learning, research, curiosity |
| recognition | 2 | 48h | Sharing work, getting feedback |
| expression | 1 | 8h | Writing, creating, articulating thoughts |

**Each cycle:**
1. Satisfaction decays based on elapsed time (0.0–3.0 range)
2. Tension = importance × deprivation — higher = more urgent
3. Top 3 needs by tension get action slots
4. Probability roll decides action vs. notice (higher tension = higher chance)
5. Impact matrix selects action size (crisis → big actions, stable → small maintenance)
6. Weighted random picks specific action from the selected impact range
7. Cross-need effects propagate (e.g., completing a task boosts both closure and competence)

**Protection mechanisms:**
- **Starvation guard** — any need stuck at floor for 48h+ gets a forced action slot
- **Action staleness** — recently-picked actions get weight penalty to prevent repetition
- **Follow-ups** — temporal markers to check results of past actions ("posted on Moltbook → check replies in 4h")
- **Day/night decay** — configurable multiplier for different time periods
- **Floor/ceiling** — satisfaction clamped to 0.5–3.0, prevents runaway states

---

## Quick Start

```bash
# Initialize state file
./scripts/init.sh

# Add to HEARTBEAT.md:
<skill-dir>/scripts/run-cycle.sh

# After completing a suggested action:
./scripts/mark-satisfied.sh <need> [impact]

# With follow-up (check back later):
./scripts/mark-satisfied.sh connection 1.5 --reason "posted update" --followup "check replies" --in 4h

# Manual follow-up (e.g., from steward):
./scripts/create-followup.sh --what "review PR CI" --in 2h --need competence --source steward
```

**Requires:** `bash`, `jq`, `bc`, `grep`, `find` + `WORKSPACE` env var set.

---

## Customization

Everything is in `assets/needs-config.json`:
- **Decay rates** — how fast each need builds tension
- **Action lists** — what gets suggested per need (add your own)
- **Weights** — probability of each action being selected
- **Importance** — which needs win when multiple compete
- **Disable a need** — set `importance: 0`

Guided onboarding conversation template included in SKILL.md.

See `references/TUNING.md` for detailed tuning guide.

---

## Architecture: Suggestion Engine, Not Executor

The skill outputs text suggestions. It does not execute actions, make network requests, or access credentials.

```
Turing Pyramid (local-only)      Your Agent (has capabilities)
───────────────────────────      ─────────────────────────────
reads JSON config + state    →   receives "★ do X" text
scans workspace files        →   decides: execute? skip? ask human?
outputs suggestion text      →   uses its own tools and permissions
```

**Reads:** workspace files (MEMORY.md, SOUL.md, etc.) via grep/find for pattern detection.
**Writes:** `assets/needs-state.json` only (timestamps and satisfaction levels).
**Never accesses:** credentials, APIs, network, paths outside workspace.

---

## Token Usage

| Heartbeat interval | Cycles/day | Est. tokens/day | Est. tokens/month |
|-------------------|------------|-----------------|-------------------|
| 30 min | 48 | 48k–120k | 1.4M–3.6M |
| 1 hour | 24 | 24k–60k | 720k–1.8M |
| 2 hours | 12 | 12k–30k | 360k–900k |

Stable agents (most needs satisfied) use fewer tokens. First few days are higher as the system stabilizes.

---

## Files

```
turing-pyramid/
├── SKILL.md              # Full documentation
├── DESCRIPTION.md        # This file
├── assets/
│   ├── needs-config.json # ★ Needs, decay rates, actions — tune this
│   ├── needs-state.json  # Runtime state (auto-managed)
│   ├── followups.jsonl   # Follow-up markers (auto-managed)
│   └── cross-need-impact.json  # Inter-need effects
├── scripts/
│   ├── run-cycle.sh      # Main heartbeat entry point
│   ├── mark-satisfied.sh # Update state after action (supports --followup)
│   ├── create-followup.sh # Create temporal check-back markers
│   ├── resolve-followup.sh # Close follow-ups (single or bulk)
│   ├── show-status.sh    # Debug current tensions
│   ├── init.sh           # First-time state setup
│   └── scan_*.sh         # 10 workspace scanners
├── tests/                # 50+ test cases (unit + integration)
└── references/
    ├── TUNING.md         # Customization guide
    └── architecture.md   # Technical deep-dive
```

---

## Links

- **ClawHub**: https://clawhub.com/skills/turing-pyramid
- **Tests**: 50+ cases across unit, integration, and regression suites
- **Design**: Loosely inspired by Maslow's hierarchy + Self-Determination Theory, implemented as a pure engineering system
