---
title: Configuration
description: Full SHIPLOOP.yml reference
---

Ship Loop is configured via a `SHIPLOOP.yml` file in your project root. Generate one with `shiploop init` or write it by hand.

## Full Schema

```yaml
# Required
project: "My App"                    # Project name (shown in output)
repo: /absolute/path/to/project      # Path to git repository
site: https://myapp.vercel.app       # Production URL for deploy verification

# Agent (pick one)
agent: claude-code                   # Use a preset (see Agent Presets)
agent_command: "claude --print ..."  # Or a custom command (overrides agent)

# Branch strategy
branch: pr                           # direct-to-main | per-segment | pr

# Mode
mode: solo                           # solo | team

# Preflight checks (all optional)
preflight:
  build: "npm run build"
  lint: "npm run lint"
  test: "npm test"

# Deploy verification
deploy:
  provider: vercel                   # vercel | netlify | custom
  routes: [/, /api/health]           # Routes to check
  marker: "data-version"             # DOM marker to verify (optional)
  health_endpoint: /api/health       # Health check endpoint (optional)
  deploy_header: x-vercel-deployment-url  # Header to verify (optional)
  script: null                       # Custom script path (for provider: custom)
  timeout: 300                       # Seconds to wait for deploy

# Repair loop
repair:
  max_attempts: 3                    # Repair attempts before meta loop

# Meta loop
meta:
  enabled: true                      # Enable/disable meta experiments
  experiments: 3                     # Number of experiment branches

# Optimization (post-ship)
optimization:
  enabled: true
  max_experiments: 2
  min_repair_attempts: 1
  min_repair_diff_lines: 5
  budget_usd: 5.0

# Budget tracking
budget:
  max_usd_per_segment: 10.0
  max_usd_per_run: 50.0
  max_tokens_per_segment: 500000
  halt_on_breach: true
  optimization_budget_usd: 5.0

# Timeouts (seconds)
timeouts:
  agent: 900                         # Per agent invocation
  preflight: 300                     # Per preflight run
  deploy: 300                        # Deploy verification

# Security
blocked_patterns:                    # Additional patterns to block from commits
  - "*.pem"
  - "internal/"

# Segments (the work to do)
segments:
  - name: "feature-name"
    status: pending                  # Auto-managed, don't set manually
    prompt: |
      Description of what the agent should build.
    depends_on: []                   # Other segment names
    commit: null                     # Auto-set after shipping
    deploy_url: null                 # Auto-set after verification
    tag: null                        # Auto-set after tagging
    touched_paths: []                # For parallel execution detection
```

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `project` | string | Project name |
| `repo` | string | Absolute path to git repo |
| `site` | string | Production URL |
| `agent` or `agent_command` | string | Coding agent to use |
| `segments` | list | At least one segment |

## Agent Resolution

If both `agent` and `agent_command` are set, `agent_command` wins. If only `agent` is set, it must be a valid preset name. See [Agent Presets](/ship-loop/guides/agent-presets/).

## Segment States

States are managed by Ship Loop. Don't edit them manually unless resetting.

| State | Meaning |
|-------|---------|
| `pending` | Not started, waiting for dependencies |
| `coding` | Agent is working |
| `preflight` | Build/lint/test running |
| `shipping` | Committing and pushing |
| `verifying` | Checking deployment |
| `repairing` | In repair loop |
| `experimenting` | In meta loop |
| `shipped` | Done |
| `failed` | All loops exhausted |

## Built-in Blocked Patterns

These are always blocked regardless of config:

`.env`, `.env.*`, `*.key`, `*.pem`, `*.p12`, `*.pfx`, `*.secret`, `id_rsa`, `id_ed25519`, `*.keystore`, `credentials.json`, `service-account*.json`, `token.json`, `.npmrc`, `node_modules/`, `__pycache__/`, `.pytest_cache/`, `*.sqlite`, `*.sqlite3`, `.DS_Store`, `learnings.yml`
