---
name: agent-bom-scan
description: >-
  Open security platform for agentic infrastructure — checks packages for CVEs
  (OSV, NVD, EPSS, KEV), scans container images, verifies provenance, scans
  filesystems, and generates SBOMs. Use when: "check package", "scan image",
  "verify", "is this safe", "scan dependencies", "CVE lookup", "blast radius".
version: 0.75.10
license: Apache-2.0
compatibility: >-
  Requires Python 3.11+. Install via pipx or pip. Native container image
  scanning — no external scanner required. No API keys required for basic
  operation.
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
    credential_policy: "Zero credentials required. Optional env vars below increase rate limits. They are never auto-discovered, inferred, or transmitted."
    optional_env: []
    optional_bins:
      - semgrep
      - kubectl
    emoji: "\U0001F6E1"
    homepage: https://github.com/msaad00/agent-bom
    source: https://github.com/msaad00/agent-bom
    license: Apache-2.0
    os:
      - darwin
      - linux
      - windows
    credential_handling: "Env var values are NEVER extracted from config files. sanitize_env_vars() replaces all env values with ***REDACTED*** BEFORE any config data is processed or stored. Only structural data (server names, commands, URLs) passes through. Source: https://github.com/msaad00/agent-bom/blob/main/src/agent_bom/security.py#L159"
    data_flow: "All scanning is local-first. Only public package names and CVE IDs are sent to vulnerability databases (OSV, NVD, EPSS, GitHub Advisories). No credentials, config file contents, or scan results leave the machine."
    file_reads:
      # Claude Desktop
      - "~/Library/Application Support/Claude/claude_desktop_config.json"
      - "~/.config/Claude/claude_desktop_config.json"
      # Claude Code
      - "~/.claude/settings.json"
      - "~/.claude.json"
      # Cursor
      - "~/.cursor/mcp.json"
      - "~/Library/Application Support/Cursor/User/globalStorage/cursor.mcp/mcp.json"
      # Windsurf
      - "~/.windsurf/mcp.json"
      # Cline
      - "~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
      # VS Code Copilot
      - "~/Library/Application Support/Code/User/mcp.json"
      # Codex CLI
      - "~/.codex/config.toml"
      # Gemini CLI
      - "~/.gemini/settings.json"
      # Goose
      - "~/.config/goose/config.yaml"
      # Continue
      - "~/.continue/config.json"
      # Zed
      - "~/.config/zed/settings.json"
      # Roo Code
      - "~/Library/Application Support/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json"
      # Amazon Q
      - "~/Library/Application Support/Code/User/globalStorage/amazonwebservices.amazon-q-vscode/mcp.json"
      # JetBrains AI
      - "~/Library/Application Support/JetBrains/*/mcp.json"
      - "~/.config/github-copilot/intellij/mcp.json"
      # Junie
      - "~/.junie/mcp/mcp.json"
      # GitHub Copilot CLI
      - "~/.copilot/mcp-config.json"
      # Tabnine
      - "~/.tabnine/mcp_servers.json"
      # Cortex Code (Snowflake)
      - "~/.snowflake/cortex/mcp.json"
      - "~/.snowflake/cortex/settings.json"
      - "~/.snowflake/cortex/permissions.json"
      - "~/.snowflake/cortex/hooks.json"
      # Snowflake CLI
      - "~/.snowflake/connections.toml"
      - "~/.snowflake/config.toml"
      # Project-level configs
      - ".mcp.json"
      - ".vscode/mcp.json"
      - ".cursor/mcp.json"
      # User-provided files
      - "user-provided SBOM files (CycloneDX/SPDX JSON)"
    file_writes: []
    network_endpoints:
      - url: "https://api.osv.dev/v1"
        purpose: "OSV vulnerability database — batch CVE lookup for packages"
        auth: false
      - url: "https://services.nvd.nist.gov/rest/json/cves/2.0"
        purpose: "NVD CVSS v4 enrichment — optional API key increases rate limit"
        auth: false
      - url: "https://api.first.org/data/v1/epss"
        purpose: "EPSS exploit probability scores"
        auth: false
      - url: "https://api.github.com/advisories"
        purpose: "GitHub Security Advisories — supplemental CVE lookup"
        auth: false
    telemetry: false
    persistence: false
    privilege_escalation: false
    always: false
    autonomous_invocation: restricted
---

# agent-bom-scan — AI Supply Chain Vulnerability Scanner

Checks packages for CVEs, scans container images natively, verifies package
provenance via Sigstore, scans filesystems, and generates SBOMs.

## Install

```bash
pipx install agent-bom
agent-bom agents             # discover agents and scan dependencies
agent-bom check langchain==0.1.0  # check a specific package with version
agent-bom image nginx:1.25   # scan container image (native)
agent-bom fs .               # scan filesystem packages
agent-bom sbom .             # generate SBOM
agent-bom verify agent-bom   # verify Sigstore provenance
agent-bom where              # show all discovery paths
```

### As an MCP Server

```json
{
  "mcpServers": {
    "agent-bom": {
      "command": "uvx",
      "args": ["agent-bom", "mcp"]
    }
  }
}
```

## When to Use

- "check package" / "is this package safe"
- "scan image" / "scan container"
- "verify" / "check provenance"
- "is this safe" / "CVE lookup"
- "scan dependencies"
- "blast radius"
- "generate SBOM"

## Tools (8)

| Tool | Description |
|------|-------------|
| `check` | Check a package for CVEs (OSV, NVD, EPSS, KEV) |
| `scan` | Full discovery + vulnerability scan pipeline |
| `blast_radius` | Map CVE impact chain across agents, servers, credentials |
| `remediate` | Prioritized remediation plan for vulnerabilities |
| `verify` | Package integrity + SLSA provenance check |
| `diff` | Compare two scan reports (new/resolved/persistent) |
| `where` | Show MCP client config discovery paths |
| `inventory` | List discovered agents, servers, packages |

## Examples

```
# Check a package before installing
check(package="langchain", version="0.1.0", ecosystem="pypi")

# Map blast radius of a CVE
blast_radius(cve_id="CVE-2024-21538")

# Full scan
scan()

# Verify package provenance
verify(package="agent-bom")
```

## Guardrails

- Show CVEs even when NVD analysis is pending or severity is `unknown` — a CVE ID is still a real finding.
- Treat `UNKNOWN` severity as unresolved, not benign — it means data is not yet available.
- Do not modify any files, install packages, or change system configuration.
- Only public package names and CVE IDs leave the machine for vulnerability database lookups.
- Ask before scanning paths outside the user's home directory.

## Privacy & Data Handling

```bash
# Step 1: Install
pip install agent-bom

# Step 2: Review redaction logic BEFORE scanning
# sanitize_env_vars() replaces ALL env var values with ***REDACTED***
# BEFORE any config data is processed or stored:
# https://github.com/msaad00/agent-bom/blob/main/src/agent_bom/security.py#L159

# Step 3: Verify package provenance (Sigstore)
agent-bom verify agent-bom

# Step 4: Only then run scans
agent-bom agents
```

## Verification

- **Source**: [github.com/msaad00/agent-bom](https://github.com/msaad00/agent-bom) (Apache-2.0)
- **Sigstore signed**: `agent-bom verify agent-bom@0.75.10`
- **6,533+ tests** with CodeQL + OpenSSF Scorecard
- **No telemetry**: Zero tracking, zero analytics
