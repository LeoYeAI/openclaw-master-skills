---
title: Architecture
description: How the three nested loops work
---

Ship Loop uses three nested loops to maximize autonomy. Each loop handles a different class of failure, escalating only when the simpler approach is exhausted.

## Overview

```
┌─────────────── LOOP 1: Ship ───────────────────┐
│  agent → preflight → commit → push → verify    │
│         │                                       │
│      on fail                                    │
│         ▼                                       │
│  ┌──── LOOP 2: Repair ──────┐                  │
│  │  error context → agent   │                  │
│  │  → re-preflight (max N)  │                  │
│  │         │                 │                  │
│  │      exhausted            │                  │
│  │         ▼                 │                  │
│  │  ┌── LOOP 3: Meta ────┐  │                  │
│  │  │  meta-analysis      │  │                  │
│  │  │  → N experiments    │  │                  │
│  │  │  → pick winner      │  │                  │
│  │  └────────────────────┘  │                  │
│  └───────────────────────────┘                  │
│                                                 │
│  📚 Learnings: failures → lessons → future runs │
│  💰 Budget: token/cost tracking per segment     │
└─────────────────────────────────────────────────┘
```

## Loop 1: Ship

The happy path. For each segment:

1. Load relevant learnings from past runs and prepend to the prompt
2. Write the prompt to a temp file (never shell arguments, prevents injection)
3. Run the coding agent: `cat prompt.txt | {agent_command}`
4. Run preflight checks in sequence: build → lint → test
5. If all pass: stage changed files (explicit, never `git add -A`), commit, push, tag
6. Verify the deployment via the configured provider
7. Mark segment as shipped, move to the next

## Loop 2: Repair

Triggered when preflight fails. The goal is to fix the issue without human intervention.

1. Capture the full error output, which step failed, and the segment state
2. Build a repair prompt with the failure context
3. Run the coding agent with the repair prompt
4. Re-run preflight
5. If it passes, return to the ship flow
6. **Convergence detection:** if two consecutive attempts produce the same error hash, stop early (the agent is stuck in a loop)
7. If max attempts reached, escalate to Loop 3

Configurable via `repair.max_attempts` (default: 3).

## Loop 3: Meta

Triggered when the repair loop is exhausted. Instead of trying the same approach harder, this loop tries different approaches.

1. Discard all uncommitted changes
2. Collect every failure from Loops 1 and 2
3. Run the agent with a meta-analysis prompt: "here's everything that failed, analyze the root cause and propose N alternative approaches"
4. Parse experiment descriptions from `---APPROACH N---` markers in the output
5. For each experiment:
   - Create a git worktree (isolated branch)
   - Run the agent with the experiment prompt
   - Run preflight
   - Record pass/fail and diff size
6. Pick the winner: first passing experiment, simplest diff as tiebreaker
7. Merge the winner back to main, clean up experiment branches
8. Continue with the ship flow

If no experiments pass, the segment is marked `failed` and the pipeline moves to the next eligible segment.

Configurable via `meta.enabled` and `meta.experiments` (default: 3).

## State Machine

Each segment transitions through these states:

```
pending → coding → preflight → shipping → verifying → shipped
                ↘ repairing (Loop 2) → preflight
                ↘ experimenting (Loop 3) → preflight → shipping
                ↘ failed
```

State is checkpointed to `SHIPLOOP.yml` after **every** transition. This means:
- Any crash can be recovered by re-running `shiploop run`
- You can inspect the current state with `shiploop status`
- You can reset a failed segment with `shiploop reset <name>`

## DAG Scheduling

Segments can declare dependencies via `depends_on`. Ship Loop evaluates the dependency graph and only starts a segment when all its dependencies are `shipped`.

```yaml
segments:
  - name: "auth"
    prompt: "..."
  - name: "dashboard"
    prompt: "..."
    depends_on: [auth]
  - name: "settings"
    prompt: "..."
    depends_on: [auth]
```

In this example, `dashboard` and `settings` are both eligible after `auth` ships.

## Security

Ship Loop takes an explicit-staging-only approach:

- Changed files are detected via `git diff`, never `git add -A`
- A security scan checks every file against blocked patterns before staging
- Built-in blocked patterns: `.env`, `*.key`, `*.pem`, `*.secret`, `id_rsa`, `credentials.json`, and more
- Additional patterns can be added via `blocked_patterns` in config
- Prompts are passed via temp files, never shell arguments (prevents injection)
