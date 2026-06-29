---
name: agent-bom-analyze
description: >-
  Analyze blast radius, attack paths, and threat landscape across your AI
  infrastructure. Use when: "blast radius", "threat intel", "risk score",
  "attack path", "lateral movement", "context graph", "who can reach what".
version: 0.75.10
license: Apache-2.0
compatibility: >-
  Requires Python 3.11+. Install via pipx or pip. No credentials required for
  blast radius and context graph analysis. Threat intelligence lookups query
  EPSS and CVE databases.
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
    credential_policy: "Zero credentials required. Blast radius and context graph analysis operate on local scan data. EPSS and CVE lookups send only public CVE IDs — no internal data."
    optional_env: []
    optional_bins: []
    emoji: "\U0001F4A5"
    homepage: https://github.com/msaad00/agent-bom
    source: https://github.com/msaad00/agent-bom
    license: Apache-2.0
    os:
      - darwin
      - linux
      - windows
    data_flow: "Blast radius and context graph analysis operate on local scan results in memory. Only public CVE IDs are sent to EPSS and vulnerability databases for threat intelligence enrichment. No internal config data, credentials, or scan results leave the machine."
    file_reads: []
    file_writes: []
    network_endpoints:
      - url: "https://api.first.org/data/v1/epss"
        purpose: "EPSS exploit probability scores for CVEs found in scan"
        auth: false
      - url: "https://api.osv.dev/v1"
        purpose: "OSV vulnerability database — CVE detail lookup"
        auth: false
    telemetry: false
    persistence: false
    privilege_escalation: false
    always: false
    autonomous_invocation: restricted
---

# agent-bom-analyze — Blast Radius & Attack Path Analysis

Analyzes blast radius, attack paths, and the threat landscape across your AI
infrastructure. Maps lateral movement risks, identifies high-impact CVEs, and
visualizes agent context graphs.

## Install

```bash
pipx install agent-bom
agent-bom agents --verbose   # blast radius detail for each agent
agent-bom graph              # generate context graph
```

## When to Use

- "blast radius" / "what's the blast radius"
- "threat intel" / "threat intelligence"
- "risk score" / "risk scoring"
- "attack path" / "attack paths"
- "lateral movement"
- "context graph" / "agent graph"
- "who can reach what"

## Commands

```bash
# Blast radius detail (verbose)
agent-bom agents --verbose

# Generate context graph
agent-bom graph
```

## Tools

| Tool | Description |
|------|-------------|
| `blast_radius` | Map CVE impact chain across agents, servers, and credentials |
| `context_graph` | Agent context graph with lateral movement analysis |
| `analytics_query` | Query vulnerability trends, posture history, and risk scores |

## Examples

```
# Map blast radius of a specific CVE
blast_radius(cve_id="CVE-2024-21538")

# Build full context graph
context_graph()

# Query top CVEs by blast radius impact
analytics_query(query="top_blast_radius", days=30)
```

**Example blast radius output:**
```
CVE-2024-21538 — CRITICAL (CVSS 9.8, EPSS 0.94)
Blast Radius: 4 agents affected

  filesystem   [direct]  langchain 0.1.0 → CVE-2024-21538
    └─ github  [indirect] shares filesystem credential scope
    └─ slack   [indirect] accessible via filesystem tool call
  postgres     [direct]  langchain 0.1.0 → CVE-2024-21538

Recommended: Update langchain to ≥ 0.1.17
```

## Guardrails

- Analysis is read-only — no files are modified.
- Only public CVE IDs are sent externally (to EPSS and vulnerability databases).
- No internal config data, credentials, or agent details leave the machine.
- Present blast radius findings clearly and ask the user whether to generate a remediation plan when CRITICAL CVEs are found.
