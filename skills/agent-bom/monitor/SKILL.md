---
name: agent-bom-monitor
description: >-
  Monitor agent fleet, track trust scores, and manage lifecycle states. Use
  when: "fleet", "watch agents", "runtime status", "trust scores",
  "fleet sync", "agent lifecycle", "serve dashboard".
version: 0.75.10
license: Apache-2.0
compatibility: >-
  Requires Python 3.11+. Install via pipx or pip. No credentials required for
  fleet listing and trust score tracking. Optional server dashboard available
  via agent-bom serve.
metadata:
  author: msaad00
  homepage: https://github.com/msaad00/agent-bom
  source: https://github.com/msaad00/agent-bom
  pypi: https://pypi.org/project/agent-bom/
  scorecard: https://securityscorecards.dev/viewer/?uri=github.com/msaad00/agent-bom
  tests: 6533
  install:
    pipx: agent-bom
    pip: agent-bom
    docker: ghcr.io/msaad00/agent-bom:0.75.10
  openclaw:
    requires:
      bins: []
      env: []
      credentials: none
    credential_policy: "Zero credentials required for fleet listing and trust score tracking. Fleet sync reads local scan state. Dashboard server (agent-bom serve) runs on localhost only."
    optional_env: []
    optional_bins: []
    emoji: "\U0001F4CA"
    homepage: https://github.com/msaad00/agent-bom
    source: https://github.com/msaad00/agent-bom
    license: Apache-2.0
    os:
      - darwin
      - linux
      - windows
    data_flow: "Purely local. Fleet data is read from local scan state. Dashboard server (agent-bom serve) runs on localhost and exposes no data externally. No data leaves the machine."
    file_reads:
      - "local scan state and fleet registry (managed by agent-bom)"
    file_writes: []
    network_endpoints: []
    telemetry: false
    persistence: false
    privilege_escalation: false
    always: false
    autonomous_invocation: restricted
---

# agent-bom-monitor — Agent Fleet Monitor

Monitor agent fleet health, track trust scores, and manage agent lifecycle
states across your AI infrastructure. Start a local dashboard server for
continuous monitoring.

## Install

```bash
pipx install agent-bom
agent-bom fleet sync         # sync fleet state with latest scan
agent-bom fleet list         # list all agents and trust scores
agent-bom serve              # start local monitoring dashboard
```

## When to Use

- "fleet" / "agent fleet"
- "watch agents" / "monitor agents"
- "runtime status"
- "trust scores"
- "fleet sync"
- "agent lifecycle"
- "serve dashboard" / "start dashboard"

## Commands

```bash
# Sync fleet state with latest scan
agent-bom fleet sync

# List all agents with trust scores
agent-bom fleet list

# Start local monitoring dashboard
agent-bom serve
```

## Examples

```
# Sync fleet
fleet_sync()

# List agents and trust scores
fleet_list()

# Start dashboard server
serve()
```

**Example fleet list output:**
```
Agent Fleet — 7 agents tracked
  filesystem   trust: 92  status: healthy   last-scan: 2m ago
  brave-search trust: 88  status: healthy   last-scan: 2m ago
  github       trust: 95  status: healthy   last-scan: 2m ago
  slack        trust: 71  status: warning   last-scan: 2m ago  [2 CVEs]
  postgres     trust: 84  status: healthy   last-scan: 2m ago
  linear       trust: 90  status: healthy   last-scan: 2m ago
  notion       trust: 67  status: at-risk   last-scan: 2m ago  [CRITICAL]
```

## Guardrails

- Fleet monitoring is read-only — no agents are modified.
- The dashboard server runs on localhost only — no external exposure.
- Confirm with the user before starting `agent-bom serve` — it binds a local port.
- Trust scores are derived from local scan data; they do not contact external services.
