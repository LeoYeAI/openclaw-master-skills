# 🚢 Ship Loop

Self-healing build pipeline for AI coding agents. Define your features, point it at your agent, and it builds, tests, deploys, and verifies each one. When something breaks, it fixes itself. When fixes stall, it experiments with alternatives. It learns from every failure.

[![PyPI version](https://badge.fury.io/py/shiploop.svg)](https://pypi.org/project/shiploop/)
[![CI](https://github.com/fernando-fernandez3/ship-loop/actions/workflows/ci.yml/badge.svg)](https://github.com/fernando-fernandez3/ship-loop/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## Install

```bash
pip install shiploop
```

## Quick Start

```bash
cd /path/to/your/project
shiploop init     # Auto-detects framework, creates SHIPLOOP.yml
# Edit SHIPLOOP.yml to define your segments
shiploop run      # Start the pipeline
```

## Security Notice

> **SHIPLOOP.yml is equivalent to running a script.** The `agent_command`, all preflight commands (`build`, `lint`, `test`), and custom deploy scripts execute with your full user privileges. Ship Loop does **not** sandbox these commands. **Never run `shiploop run` on an untrusted repository without first reviewing its SHIPLOOP.yml.** Treat the config file with the same caution you would give to a Makefile or CI pipeline definition.

## What It Does

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

**Loop 1 (Ship):** Your coding agent builds the feature. Preflight runs build, lint, and tests. If everything passes, it commits, pushes, and verifies the deployment. Past learnings are injected into each agent prompt.

**Loop 2 (Repair):** When preflight fails, Ship Loop captures the error context and asks the agent to fix it. Detects error convergence (same error twice = stop early). Up to N attempts before escalating.

**Loop 3 (Meta):** When repairs stall, Ship Loop runs a meta-analysis of all failures, spawns N experiment branches in git worktrees, runs each through preflight, and picks the simplest passing solution.

## Agent Presets

Use a preset name instead of the full command:

```yaml
# Pick one:
agent: claude-code    # claude --print --permission-mode bypassPermissions
agent: codex          # codex --quiet
agent: aider          # aider --yes-always --no-git

# Or use any command:
agent_command: "your-agent --your-flags"
```

## Example Config

```yaml
project: "My App"
repo: /path/to/project
site: https://myapp.vercel.app
agent: claude-code

preflight:
  build: "npm run build"
  lint: "npm run lint"
  test: "npm test"

deploy:
  provider: vercel       # vercel | netlify | custom
  routes: [/, /api/health]

repair:
  max_attempts: 3

meta:
  enabled: true
  experiments: 3

budget:
  max_usd_per_segment: 10.0
  max_usd_per_run: 50.0

segments:
  - name: "dark-mode"
    prompt: |
      Add dark mode with CSS custom properties and a toggle button.

  - name: "contact-form"
    prompt: |
      Add a contact form at /contact with a serverless API endpoint.
    depends_on: [dark-mode]
```

## CLI

```bash
shiploop run                        # Start or resume pipeline
shiploop status                     # Show segment states
shiploop reset <segment>            # Reset a segment to pending
shiploop learnings list             # List recorded learnings
shiploop learnings search <query>   # Search by keyword
shiploop budget                     # Show cost summary
shiploop init                       # Create SHIPLOOP.yml interactively
```

## Features

- **Self-healing:** Three nested loops ensure maximum autonomy before asking for help
- **Learnings engine:** Every failure-then-fix cycle creates a lesson. Future runs load relevant lessons into the agent prompt automatically.
- **Budget tracking:** Monitor token usage and estimated costs per segment and per run. Set limits, halt on breach.
- **Crash recovery:** State is checkpointed after every transition. Restart anytime and pick up where you left off.
- **DAG scheduling:** Segments declare dependencies. Ship Loop resolves the graph and runs eligible segments in order.
- **Security scanning:** Explicit file staging only. Never `git add -A`. Built-in blocked patterns for secrets, keys, and credentials.
- **Deploy verification:** Pluggable providers for Vercel, Netlify, and custom scripts.
- **Framework detection:** `shiploop init` auto-detects Node, Python, Rust, and Go projects.

## What It Looks Like

```
🚢 Ship Loop: My App (2 segments)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 Segment 1/2: dark-mode
   📚 No prior learnings
   🤖 coding... → ✅ completed in 262s
   🛫 preflight... → ✅ passed
   📦 Committed: a1b2c3d
   ✅ Deploy verified
✅ dark-mode — shipped [7m 30s, $0.42]

🔄 Segment 2/2: contact-form
   📚 Loaded 1 learning(s)
   🤖 coding... → ✅ completed in 310s
   ❌ Preflight FAILED — entering repair loop
   🔧 Repair 1/3 → ❌ lint errors
   🔧 Repair 2/3 → ❌ test errors
   🔧 Repair 3/3 → ❌ build error
   🧪 Meta loop: 3 experiments
   🏆 Winner: experiment 2 (12 lines)
   📦 Committed: e5f6g7h
   ✅ Deploy verified
✅ contact-form — shipped [18m, $3.42]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏁 2/2 segments shipped. Total: 25m 10s, $3.84
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## From Source

```bash
git clone https://github.com/fernando-fernandez3/ship-loop.git
cd ship-loop
pip install -e ".[dev]"
python -m pytest tests/ -x
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). We're especially looking for:
- New deploy providers (AWS Amplify, Cloudflare Pages, Railway, Fly.io)
- New agent presets
- Framework detection for more languages

## Background

Ship Loop's three-loop architecture (ship → repair → meta-experiment) was designed from engineering intuition about how autonomous coding pipelines fail and recover. Interestingly, Meta's [Hyperagents](https://arxiv.org/abs/2603.19461) research (March 2026) independently arrived at similar patterns through open-ended optimization: their self-improving agents autonomously invented persistent memory, performance tracking, and experiment branching, the same core mechanisms Ship Loop uses in production.

## License

MIT
