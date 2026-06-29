---
name: agent-bom-troubleshoot
description: >-
  Diagnose issues, check prerequisites, and validate configurations. Use when:
  "doctor", "debug", "why failing", "validate config", "check prerequisites",
  "something is broken", "db status", "fix my setup".
version: 0.75.10
license: Apache-2.0
compatibility: >-
  Requires Python 3.11+. Install via pipx or pip. No credentials required.
  Doctor checks run locally against the installed environment.
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
    credential_policy: "Zero credentials required. All diagnostic checks run locally against the installed environment. No data leaves the machine."
    optional_env: []
    optional_bins: []
    emoji: "\U0001F527"
    homepage: https://github.com/msaad00/agent-bom
    source: https://github.com/msaad00/agent-bom
    license: Apache-2.0
    os:
      - darwin
      - linux
      - windows
    data_flow: "Purely local. Doctor checks inspect installed packages, config files, and environment settings. No data leaves the machine."
    file_reads:
      - "local agent-bom configuration and state files"
    file_writes: []
    network_endpoints: []
    telemetry: false
    persistence: false
    privilege_escalation: false
    always: false
    autonomous_invocation: restricted
---

# agent-bom-troubleshoot — Diagnostics & Configuration Validator

Diagnoses issues, checks prerequisites, validates configurations, and reports
on the health of the agent-bom installation and connected database.

## Install

```bash
pipx install agent-bom
agent-bom doctor             # check prerequisites and installation health
agent-bom validate           # validate configuration files
agent-bom db status          # check database connection status
```

## When to Use

- "doctor" / "run doctor"
- "debug" / "help me debug"
- "why failing" / "something's broken"
- "validate config" / "check configuration"
- "check prerequisites"
- "db status" / "database status"
- "fix my setup"

## Commands

```bash
# Run full diagnostic check
agent-bom doctor

# Validate configuration
agent-bom validate

# Check database status
agent-bom db status
```

## Examples

```
# Run diagnostics
doctor()

# Validate config
validate()

# Check DB
db_status()
```

**Example doctor output:**
```
agent-bom doctor

  Python        3.12.2   OK
  agent-bom     0.75.9   OK
  pip           24.0     OK
  semgrep       not found  (optional — SAST scanning unavailable)
  kubectl       not found  (optional — K8s context unavailable)

  Config files found:
    Claude Desktop  ~/.config/Claude/claude_desktop_config.json  OK
    Cursor          ~/.cursor/mcp.json                           OK

  Database:      SQLite  ~/.agent-bom/db.sqlite  OK
  Last scan:     2 hours ago

  Status: Ready
```

## Guardrails

- Diagnostics are read-only — no configuration files are modified.
- Doctor checks do not transmit any data externally.
- If the user is experiencing an error, show the full diagnostic output before suggesting fixes.
- Validate configuration files before recommending changes.
