---
name: agent-bom-enforce
description: >-
  Enforce security policies on MCP tool calls and block dangerous operations at
  runtime. Use when: "block risky calls", "apply policy", "proxy",
  "runtime protection", "policy enforcement", "intercept MCP calls".
version: 0.75.10
license: Apache-2.0
compatibility: >-
  Requires Python 3.11+. Install via pipx or pip. No credentials required.
  Policy files are user-provided YAML/JSON. Proxy runs locally.
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
    credential_policy: "Zero credentials required. Policy evaluation is local. Proxy operates on local network only. Policy files are user-provided and never transmitted."
    optional_env: []
    optional_bins: []
    emoji: "\U0001F6AB"
    homepage: https://github.com/msaad00/agent-bom
    source: https://github.com/msaad00/agent-bom
    license: Apache-2.0
    os:
      - darwin
      - linux
      - windows
    data_flow: "Purely local. Policy evaluation runs on scan results in memory. Proxy intercepts MCP calls on local network only. Audit logs are written locally (JSONL). No data leaves the machine."
    file_reads:
      - "user-provided policy files (YAML/JSON policy-as-code)"
      - "user-provided audit log files (JSONL from agent-bom proxy)"
    file_writes:
      - "proxy-audit.jsonl (local audit log, only when proxy is running)"
    network_endpoints: []
    telemetry: false
    persistence: false
    privilege_escalation: false
    always: false
    autonomous_invocation: restricted
    disable-model-invocation: true
---

# agent-bom-enforce — Runtime Policy Enforcement

Enforces security policies on MCP tool calls and blocks dangerous operations
at runtime. Runs a local proxy that intercepts MCP calls and evaluates them
against policy-as-code rules.

## Install

```bash
pipx install agent-bom
agent-bom proxy              # start enforcement proxy
agent-bom policy apply policy.yaml  # apply a policy file
agent-bom policy check       # check current policy status
```

## When to Use

- "block risky calls" / "block dangerous MCP calls"
- "apply policy" / "enforce policy"
- "proxy" / "MCP proxy"
- "runtime protection"
- "policy enforcement"
- "intercept MCP calls"

## Commands

```bash
# Start the enforcement proxy
agent-bom proxy

# Apply a policy file
agent-bom policy apply policy.yaml

# Check current policy status
agent-bom policy check
```

## Example Policy File

```yaml
# policy.yaml
rules:
  - id: block-shell-exec
    description: Block shell execution tool calls
    match:
      tool: "bash|shell|exec|run_command"
    action: block
    severity: critical

  - id: require-path-allowlist
    description: Restrict filesystem access to allowed paths
    match:
      tool: "read_file|write_file|list_directory"
      args.path:
        not_starts_with: ["/home/", "/tmp/"]
    action: block
    severity: high
```

## Guardrails

- IMPORTANT: Do not start the proxy or apply policies without explicit user confirmation — enforcement changes how MCP calls are processed.
- Confirm the policy file contents with the user before applying.
- Do not enable proxy mode autonomously — always ask the user first.
- Audit logs are written locally only; no data is transmitted externally.
- This skill has `disable-model-invocation: true` — do not auto-run enforcement actions.
