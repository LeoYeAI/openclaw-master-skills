---
name: agent-bom-registry
description: >-
  MCP server security registry and trust assessment — look up servers in the 427+
  server security metadata registry, run pre-install marketplace checks, batch
  fleet risk scoring, assess skill file trust, and run SAST code scans. Use when
  the user mentions MCP server trust, registry lookup, marketplace check, or
  skill trust assessment.
version: 0.75.10
license: Apache-2.0
compatibility: >-
  Requires Python 3.11+. Install via pipx or pip. Optional: Semgrep for SAST
  code scanning. No API keys or network access required (registry is bundled).
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
    credential_policy: "Zero credentials required. Registry data is bundled locally. No network calls needed."
    optional_env:
      - name: SNYK_TOKEN
        purpose: "Snyk vulnerability enrichment for code_scan (optional)"
        required: false
    optional_bins:
      - semgrep
    emoji: "\U0001F50D"
    homepage: https://github.com/msaad00/agent-bom
    source: https://github.com/msaad00/agent-bom
    license: Apache-2.0
    os:
      - darwin
      - linux
      - windows
    data_flow: "Purely local. Registry data (427+ MCP server metadata) is bundled in the package. Lookups are in-memory string matches. Skill trust analysis parses user-provided SKILL.md content passed as a string argument."
    file_reads:
      - "user-provided SKILL.md files (for skill_trust analysis)"
    file_writes: []
    network_endpoints:
      - url: "https://api.snyk.io"
        purpose: "Snyk vulnerability enrichment for code_scan (requires SNYK_TOKEN)"
        auth: true
    telemetry: false
    persistence: false
    privilege_escalation: false
    always: false
    autonomous_invocation: restricted
---

# agent-bom-registry — MCP Server Trust & Security Registry

Look up MCP servers in the 427+ server security metadata registry, assess skill
file trust, and run pre-install marketplace checks.

## Install

```bash
pipx install agent-bom
agent-bom registry-lookup brave-search
agent-bom marketplace-check @anthropic/server-filesystem
```

## Tools (5)

| Tool | Description |
|------|-------------|
| `registry_lookup` | Look up MCP server in 427+ server security metadata registry |
| `marketplace_check` | Pre-install trust check with registry cross-reference |
| `fleet_scan` | Batch registry lookup + risk scoring for MCP server inventories |
| `skill_trust` | Assess skill file trust level (5-category analysis) |
| `code_scan` | SAST scanning via Semgrep with CWE-based compliance mapping |

## Example Workflows

```
# Look up a server in the registry
registry_lookup(server_name="brave-search")

# Pre-install trust check
marketplace_check(package="@modelcontextprotocol/server-filesystem")

# Assess trust of a skill file
skill_trust(skill_content="<paste SKILL.md content>")

# Batch risk scoring
fleet_scan(servers=["brave-search", "github", "slack"])
```

## MCP Resources

| Resource | Description |
|----------|-------------|
| `registry://servers` | Browse 427+ MCP server security metadata registry |

## Privacy & Data Handling

Registry data is **bundled in the package** — lookups are in-memory string
matches with zero network calls. Skill trust analysis parses content passed
as a string argument (no file system access needed).

## Verification

- **Source**: [github.com/msaad00/agent-bom](https://github.com/msaad00/agent-bom) (Apache-2.0)
- **6,040+ tests** with CodeQL + OpenSSF Scorecard
- **No telemetry**: Zero tracking, zero analytics
