---
name: agent-bom-runtime
description: >-
  AI runtime security monitoring — context graph analysis, runtime audit log
  correlation with CVE findings, and vulnerability analytics queries. Use when
  the user mentions runtime monitoring, context graphs, lateral movement analysis,
  audit log correlation, or vulnerability analytics.
version: 0.75.10
license: Apache-2.0
compatibility: >-
  Requires Python 3.11+. Install via pipx or pip. Optional: kubectl for
  Kubernetes context, ClickHouse for analytics storage. No API keys required.
metadata:
  author: msaad00
  homepage: https://github.com/msaad00/agent-bom
  source: https://github.com/msaad00/agent-bom
  pypi: https://pypi.org/project/agent-bom/
  scorecard: https://securityscorecards.dev/viewer/?uri=github.com/msaad00/agent-bom
  tests: 6040
  install:
    pipx: agent-bom
    pip: agent-bom
  openclaw:
    requires:
      bins: []
      env: []
      credentials: none
    credential_policy: "Zero credentials required. Optional ClickHouse URL enables analytics storage. Never auto-discovered or inferred."
    optional_env: []
    optional_bins:
      - kubectl
    emoji: "\U0001F4CA"
    homepage: https://github.com/msaad00/agent-bom
    source: https://github.com/msaad00/agent-bom
    license: Apache-2.0
    os:
      - darwin
      - linux
      - windows
    data_flow: "Operates on scan results in memory and user-provided audit log files. Optional ClickHouse connection for persistent analytics (user-configured, not auto-discovered)."
    file_reads:
      - "user-provided audit log files (JSONL format from agent-bom proxy)"
    file_writes: []
    network_endpoints: []
    telemetry: false
    persistence: false
    privilege_escalation: false
    always: false
    autonomous_invocation: restricted
---

# agent-bom-runtime — AI Runtime Security Monitoring

Context graph analysis, runtime audit log correlation with CVE findings, and
vulnerability analytics queries.

## Install

```bash
pipx install agent-bom
```

## Tools (3)

| Tool | Description |
|------|-------------|
| `context_graph` | Agent context graph with lateral movement analysis |
| `analytics_query` | Query vulnerability trends, posture history, and runtime events |
| `runtime_correlate` | Cross-reference runtime audit logs with CVE findings |

## Example Workflows

```
# Build context graph from scan results
context_graph()

# Correlate runtime audit with CVE data
runtime_correlate(audit_file="proxy-audit.jsonl")

# Query analytics
analytics_query(query="top_cves", days=30)
```

## Privacy & Data Handling

Operates on scan results already in memory and user-provided audit log files.
No automatic file discovery. No network calls unless you configure an optional
ClickHouse endpoint for persistent analytics.

## Verification

- **Source**: [github.com/msaad00/agent-bom](https://github.com/msaad00/agent-bom) (Apache-2.0)
- **6,040+ tests** with CodeQL + OpenSSF Scorecard
- **No telemetry**: Zero tracking, zero analytics
