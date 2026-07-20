---
name: ship-loop
description: >
  Run a chained build→ship→verify→notify pipeline for multi-segment feature work.
  Use when implementing multiple features in sequence, each as a coding agent task
  that gets committed, deployed, and verified before moving to the next. Prevents
  dropped handoffs between segments.
metadata:
  openclaw:
    emoji: "🚢"
    version: "5.0.0"
    requires:
      bins: ["git", "python3"]
      python: ["pyyaml>=6.0", "pydantic>=2.0"]
    trigger_phrases:
      - "ship loop"
      - "keep building"
      - "run the next segment"
      - "build these features"
      - "multi-feature pipeline"
      - "ship these segments"
---

# Ship Loop v5.0 — TARS Convergence

Orchestrate multi-segment feature work as a self-healing pipeline. Three nested loops ensure maximum autonomy: **Loop 1** runs the standard code→preflight→ship→verify chain, **Loop 2** auto-repairs failures via the coding agent, **Loop 3** spawns experiment branches when repairs stall. A **SQLite state backend** provides crash recovery and cross-run analytics. A **verdict router** replaces hardcoded branching with a configurable decision table. A **reflection loop** audits historical effectiveness and auto-generates learnings.

## Architecture: Three Loops + Event Queue + Verdict Router

```
┌───────────────────────────────────────────────────────────┐
│                  SHIP LOOP v5.0                           │
│                                                           │
│  LOOP 1: Ship Loop                                        │
│  code → preflight → ship → verify → emit(segment_shipped)│
│          │                                                │
│       on fail (verdict → action via VerdictRouter)        │
│          ▼                                                │
│  LOOP 2: Repair Loop                                      │
│  capture context → agent fix → re-preflight (max N)      │
│  ↳ emit events: repair_done | repair_failed               │
│  ↳ convergence detected → CONVERGED verdict → META        │
│  ↳ unknown error → record_decision_gap()                  │
│          │                                                │
│       exhausted                                           │
│          ▼                                                │
│  LOOP 3: Meta Loop                                        │
│  meta-analysis → N experiment branches → winner → merge   │
│  ↳ emit: meta_done                                        │
│                                                           │
│  🗄  SQLite (tars.db): runs, segments, events, learnings  │
│  📋  Event Queue: crash recovery via unprocessed events   │
│  🔀  Verdict Router: configurable verdict→action table    │
│  📚  Learnings Engine: scored lessons (score tracks use)  │
│  🪞  Reflect Loop: post-run analysis + recommendations    │
│  💰  Budget Tracker: token/cost tracking per run          │
└───────────────────────────────────────────────────────────┘
```

## Security Notice

> **SHIPLOOP.yml is equivalent to running a script.** The `agent_command`, all preflight commands (`build`, `lint`, `test`), and custom deploy scripts execute with your full user privileges. Ship Loop does **not** sandbox these commands. **Never use on untrusted repos without reviewing the config.** Treat SHIPLOOP.yml with the same caution as a Makefile or CI pipeline.

## When to Use

- Building multiple features for a project in sequence
- Any work that follows: code → preflight → commit → deploy → verify → next
- When you need checkpointing so progress survives session restarts
- When you want self-healing: failures auto-repair before asking humans
- When you want cost visibility and learning from past runs

## Prerequisites

- Python 3.10+ with `pyyaml` and `pydantic` installed
- A git repository with a remote
- A deployment pipeline triggered by push (Vercel, Netlify, etc.)
- A coding agent CLI configured via `agent_command` in SHIPLOOP.yml

## Installation

```bash
pip install pyyaml pydantic
```

## CLI Usage

```bash
# Core pipeline
shiploop run              # Start or resume the pipeline
shiploop run --dry-run    # Preview what would happen
shiploop status           # Show segment states (reads from DB)
shiploop reset <segment>  # Reset a segment to pending

# Learnings
shiploop learnings list
shiploop learnings search "dark mode theme toggle"

# Budget
shiploop budget           # Show cost summary

# v5.0 NEW
shiploop reflect          # Run meta-reflection on recent run history
shiploop reflect --depth 20  # Analyze last 20 runs
shiploop events           # View event history for latest run
shiploop events <run_id>  # View event history for specific run
shiploop history          # View past run history from DB

# Options
shiploop -c /path/to/SHIPLOOP.yml run
shiploop -v run           # Verbose logging
shiploop --version        # Show version (5.0.0)
```

## Pipeline Definition (SHIPLOOP.yml)

```yaml
project: "Project Name"
repo: /absolute/path/to/project
site: https://production-url.com
branch: pr               # direct-to-main | per-segment | pr
mode: solo

agent_command: "claude --print --permission-mode bypassPermissions"

preflight:
  build: "npm run build"
  lint: "npm run lint"
  test: "npm run test"

deploy:
  provider: vercel        # vercel | netlify | custom
  routes: [/, /api/health]
  marker: "data-version"
  health_endpoint: /api/health
  deploy_header: x-vercel-deployment-url
  timeout: 300

repair:
  max_attempts: 3

meta:
  enabled: true
  experiments: 3

budget:
  max_usd_per_segment: 10.0
  max_usd_per_run: 50.0
  max_tokens_per_segment: 500000
  halt_on_breach: true

# v5.0 NEW: Reflection config
reflection:
  enabled: true       # run reflect loop after pipeline
  auto_run: true      # automatically run, not just on CLI command
  history_depth: 10   # how many past runs to analyze

# v5.0 NEW: Custom verdict routing
router:
  agent_fail: retry      # override default (fail) with retry
  deploy_fail: fail      # override default (retry) with fail

segments:
  - name: "feature-name"
    status: pending
    prompt: |
      Your coding agent prompt here.
    depends_on: []
```

## SQLite State Backend (v5.0)

State is now stored in `.shiploop/tars.db` (SQLite, WAL mode). SHIPLOOP.yml is config-only.

### Tables

| Table | Purpose |
|-------|---------|
| `runs` | Pipeline execution records (id, project, started_at, status, cost) |
| `segments` | Segment execution records per run (status, commit, touched_paths) |
| `run_events` | Event queue for crash recovery and audit trail |
| `learnings` | Failure/success lessons with effectiveness scores |
| `usage` | Token and cost records per agent invocation |
| `decision_gaps` | Situations the system didn't know how to handle |

### Event Types

| Event | When emitted |
|-------|-------------|
| `agent_started` | Agent invocation begins |
| `preflight_passed` | All preflight steps pass |
| `preflight_failed` | Any preflight step fails |
| `repair_done` | Repair loop succeeded |
| `repair_failed` | Repair loop failed or exhausted |
| `meta_done` | Meta loop winner merged |
| `segment_shipped` | Segment fully complete |
| `segment_failed` | Segment permanently failed |
| `deploy_failed` | Deploy or verification failed |
| `file_overlap_warning` | Segment may touch files changed by prior segment |

**Crash recovery**: On startup, unprocessed events are replayed to restore pipeline state.

## Verdict Router (v5.0)

The orchestrator no longer uses `if/else` chains. Every outcome maps to a `Verdict`, and a `VerdictRouter` maps verdicts to `Action` values.

### Default Routing Table

| Verdict | Default Action |
|---------|---------------|
| `success` | `ship` |
| `preflight_fail` | `repair` |
| `agent_fail` | `fail` |
| `deploy_fail` | `retry` |
| `repair_success` | `ship` |
| `repair_exhausted` | `meta` |
| `meta_success` | `ship` |
| `meta_exhausted` | `fail` |
| `budget_exceeded` | `fail` |
| `converged` | `meta` ← skip remaining repairs, jump to meta |
| `no_changes` | `fail` |
| `unknown` | `pause_and_alert` |

Override via `router:` section in SHIPLOOP.yml (see above).

## Meta-Reflection Loop (v5.0)

Runs automatically after pipeline completion (when `reflection.auto_run: true`) or manually via `shiploop reflect`.

### What It Analyzes

1. **Repeat failures** — same error_signature across multiple segments/runs
2. **Repair-heavy segments** — segments that needed >1 repair loop (same error type)
3. **Efficiency trends** — cost/time per segment trending up or down
4. **Stale learnings** — learnings with score < 0.3 that haven't helped
5. **Decision gaps** — situations that triggered `MISSING_DECISION_BRANCH`

### Auto-creates learnings from patterns

If an error signature appears 3+ times across runs, the reflect loop auto-generates a `AUTO-<sig>` learning flagging it for human review.

```bash
shiploop reflect --depth 20

═════════════════════════════════════════════════════
🪞  Ship Loop Reflection Report
   Generated: 2026-03-27T06:30:00Z
   Runs analyzed: 10
═════════════════════════════════════════════════════

📊 Efficiency
   Total cost:     $12.4200
   Segments run:   8
   Avg/segment:    $1.5525

🔁 Repeat Failures (2)
   abc123def456… × 3
   ...

💡 Recommendations
   ⚠️  Error signature abc123de… repeated 3× across segments: auth, api, db.
   📉 2 stale learning(s) (score < 0.3): L002, L004.
   ✅ No issues detected in recent history. Pipeline looks healthy!

═════════════════════════════════════════════════════
```

## Playbook Evolution (v5.0)

When a repair fails with an error that doesn't match any existing learning, the system records a `decision_gap`:

```python
learnings.record_decision_gap(
    segment="auth",
    context="Repair exhausted with unmatched error: ...",
    verdict="repair_exhausted_unknown_error",
    run_id="...",
)
```

Decision gaps surface in `shiploop reflect` output and the `decision_gaps` DB table. Operators use them to add new learnings or router overrides.

## Convergence Detection (v5.0 Enhanced)

**Same-segment**: if two consecutive repair attempts produce the same error hash → `CONVERGED` verdict → router jumps to META (skipping remaining repair attempts).

**Cross-segment**: before starting a segment, the orchestrator checks if any already-shipped segment touched the same files (via `touched_paths` in DB). If overlap detected, a `file_overlap_warning` event is emitted.

## Learnings Scoring (v5.0)

```
score (default 1.0)
  +0.1 when injected and segment succeeds first-try
  -0.2 when injected and segment fails the same way
```

Search results are sorted by combined keyword-relevance × score. Learnings with `score < 0.3` are flagged as stale in reflection.

```bash
shiploop learnings list  # shows all learnings with scores
```

## State Machine

```
States per segment:
  pending → coding → preflight → shipping → verifying → shipped
                  ↘ repairing (Loop 2) → preflight
                  ↘ experimenting (Loop 3) → preflight → shipping
                  ↘ failed
```

SHIPLOOP.yml checkpointed after every transition (for backward compat). SQLite is the primary state store.

## Deploy Providers

| Provider | How it works |
|----------|-------------|
| `vercel` | Polls routes for HTTP 200, checks `x-vercel-deployment-url` header |
| `netlify` | Polls routes for HTTP 200, checks `x-nf-request-id` header |
| `custom` | Runs `deploy.script` with `SHIPLOOP_COMMIT` and `SHIPLOOP_SITE` env vars |

## Budget Tracking

Token usage and estimated costs tracked per agent invocation in SQLite (falls back to `metrics.json`).

```bash
shiploop budget

💰 Budget Summary: Portfolio
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total cost:       $3.84
  Budget remaining: $46.16
  Total records:    12

  By segment:
    dark-mode: $0.42
    contact-form: $3.42
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Critical Rules

1. **Never break the chain** — after a segment ships, immediately start the next
2. **Preflight is mandatory** — no exceptions, no "ship now fix later"
3. **Explicit staging only** — never `git add -A`, only changed files from `git diff`
4. **Prompts via file** — never shell arguments (prevents injection)
5. **SQLite is source of truth** — SHIPLOOP.yml config-only; runtime state in `tars.db`
6. **Agent command from config** — always read from `agent_command`, never hardcode
7. **Budget-aware** — track costs, enforce limits, fail gracefully

## Project Structure

```
skills/ship-loop/
├── SKILL.md                  # This file
├── pyproject.toml
├── shiploop/
│   ├── __init__.py           # __version__ = "5.0.0"
│   ├── cli.py                # CLI (run, status, reset, reflect, events, history, ...)
│   ├── config.py             # SHIPLOOP.yml parsing + validation (Pydantic v2)
│   ├── orchestrator.py       # Main state machine + event queue + verdict routing
│   ├── db.py                 # NEW: SQLite state backend (tars.db)
│   ├── router.py             # NEW: Verdict→Action router
│   ├── learnings.py          # Learnings engine (SQLite + scoring + decision gaps)
│   ├── budget.py             # Cost/token tracking (SQLite backend)
│   ├── git_ops.py            # git operations + get_touched_paths()
│   ├── agent.py              # Agent runner
│   ├── deploy.py             # Deploy verification
│   ├── preflight.py          # Build + lint + test runner
│   ├── reporting.py          # Status messages + reports
│   ├── ship_utils.py         # Ship and verify helper
│   └── loops/
│       ├── ship.py           # Loop 1: code → preflight → ship
│       ├── repair.py         # Loop 2: repair + decision gap detection
│       ├── meta.py           # Loop 3: meta-analysis + experiments
│       ├── reflect.py        # NEW: post-run reflection + recommendations
│       └── optimize.py       # Optimization loop
├── providers/
│   ├── vercel.py
│   ├── netlify.py
│   └── custom.py
└── tests/
    ├── test_config.py
    ├── test_orchestrator.py
    ├── test_git_ops.py
    ├── test_budget.py
    ├── test_learnings.py
    └── ...
```

## Changelog

### v5.0.0 (2026-03-27) — TARS Convergence

- **SQLite state backend**: `tars.db` replaces `metrics.json` + `learnings.yml` for runtime state
- **Event queue**: all phase transitions emit events; unprocessed events enable crash recovery
- **Verdict router**: configurable `Verdict → Action` table replaces if/else chains in orchestrator
- **Meta-reflection loop**: `shiploop reflect` analyzes run history, finds patterns, auto-generates learnings
- **Playbook evolution**: `MISSING_DECISION_BRANCH` detection → `decision_gaps` table
- **Cross-segment convergence**: `touched_paths` tracked per segment for overlap warnings
- **Learnings scoring**: score field (+0.1 on success, -0.2 on failure), sorted by score
- **New CLI commands**: `reflect`, `events`, `history`
- **New config sections**: `reflection`, `router`

### v4.0.0

- Python CLI replaces bash scripts
- Pydantic v2 config validation
- Budget tracking with per-segment and per-run limits
- Error convergence detection (hash-based)
- Deploy provider plugins (Vercel, Netlify, Custom)
