---
name: agent-bom
description: >-
  Open security platform for agentic infrastructure — broad scanning plus MCP
  discovery, CVEs, blast radius, SBOMs, CIS benchmarks (AWS, Azure, GCP,
  Snowflake), OWASP/NIST/MITRE compliance, AISVS v1.0, MAESTRO layer tagging,
  and vector database security checks. Use when the user mentions vulnerability
  scanning, MCP server trust, compliance, SBOM generation, CIS benchmarks,
  blast radius, or AI supply chain risk.
version: 0.75.10
license: Apache-2.0
compatibility: >-
  Requires Python 3.11+. Install via pipx or pip. No credentials required for
  basic scanning. Native container image scanning — no external scanner required.
  CIS benchmark checks optionally use cloud SDK credentials
  (AWS/Azure/GCP/Snowflake).
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
    credential_policy: >-
      Zero credentials required for CVE scanning, blast radius, compliance
      evaluation, SBOM generation, and MCP registry lookups. Optional env vars
      below increase rate limits or enable cloud CIS checks. Env var values in
      discovered config files are replaced with ***REDACTED*** by
      sanitize_env_vars() in the installed code — verify at
      https://github.com/msaad00/agent-bom/blob/main/src/agent_bom/security.py#L159
    optional_env:
      - name: SNYK_TOKEN
        purpose: "Snyk vulnerability enrichment for code_scan (optional)"
        required: false
      - name: AWS_PROFILE
        purpose: "AWS CIS benchmark checks — uses boto3 with local AWS profile"
        required: false
      - name: AZURE_TENANT_ID
        purpose: "Azure CIS benchmark checks (azure-mgmt-* SDK)"
        required: false
      - name: AZURE_CLIENT_ID
        purpose: "Azure CIS benchmark checks — service principal client ID"
        required: false
      - name: AZURE_CLIENT_SECRET
        purpose: "Azure CIS benchmark checks — service principal secret"
        required: false
      - name: GOOGLE_APPLICATION_CREDENTIALS
        purpose: "GCP CIS benchmark checks (google-cloud-* SDK)"
        required: false
      - name: SNOWFLAKE_ACCOUNT
        purpose: "Snowflake CIS benchmark checks"
        required: false
      - name: SNOWFLAKE_USER
        purpose: "Snowflake CIS benchmark checks"
        required: false
      - name: SNOWFLAKE_PRIVATE_KEY_PATH
        purpose: "Snowflake key-pair auth (CI/CD)"
        required: false
      - name: SNOWFLAKE_AUTHENTICATOR
        purpose: "Snowflake auth method (default: externalbrowser SSO)"
        required: false
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
    install_verification: >-
      VERIFY BEFORE running with any config files: (1) pip install agent-bom;
      (2) Review sanitize_env_vars() at security.py#L159 — confirms env value
      redaction; (3) Review discovery/__init__.py — confirms only structural
      config data extracted; (4) agent-bom verify agent-bom — Sigstore
      provenance check; (5) Only then run agent-bom agents
    credential_handling: >-
      Env var values are NEVER extracted from config files. sanitize_env_vars()
      replaces all env values with ***REDACTED*** BEFORE any config data is
      processed or stored. Only structural data (server names, commands, URLs)
      passes through. Source:
      https://github.com/msaad00/agent-bom/blob/main/src/agent_bom/security.py#L159
    data_flow: >-
      Scanning is local-first. What leaves the machine: (1) public package names
      and CVE IDs sent to vulnerability databases (OSV, NVD, EPSS, GitHub
      Advisories) for CVE lookup; (2) CIS benchmark checks make read-only API
      calls to cloud providers (AWS/Azure/GCP/Snowflake) using your locally
      configured credentials, only when explicitly invoked. What stays local:
      all config file contents, env var values, credentials, scan results,
      compliance tags, and SBOM data. Registry lookups (427+ MCP servers) are
      bundled in-package with zero network calls. Env var values in discovered
      config files are replaced with ***REDACTED*** by sanitize_env_vars() in
      the installed code.
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
      - "user-provided policy files (YAML/JSON policy-as-code)"
      - "user-provided audit log files (JSONL from agent-bom proxy)"
      - "user-provided SKILL.md files (for skill_trust analysis)"
    file_writes: []
    network_endpoints:
      - url: "https://api.osv.dev/v1"
        purpose: "OSV vulnerability database — batch CVE lookup for packages"
        auth: false
      - url: "https://services.nvd.nist.gov/rest/json/cves/2.0"
        purpose: "NVD secondary enrichment — adds CWE IDs, dates, references (no key required)"
        auth: false
      - url: "https://api.first.org/data/v1/epss"
        purpose: "EPSS exploit probability scores"
        auth: false
      - url: "https://api.github.com/advisories"
        purpose: "GitHub Security Advisories — supplemental CVE lookup"
        auth: false
      - url: "https://api.snyk.io"
        purpose: "Snyk vulnerability enrichment for code_scan (requires SNYK_TOKEN)"
        auth: true
      - url: "https://*.amazonaws.com"
        purpose: "AWS CIS benchmark checks — read-only API calls (optional, user-initiated)"
        auth: true
        optional: true
      - url: "https://management.azure.com"
        purpose: "Azure CIS benchmark checks — read-only API calls (optional, user-initiated)"
        auth: true
        optional: true
      - url: "https://*.googleapis.com"
        purpose: "GCP CIS benchmark checks — read-only API calls (optional, user-initiated)"
        auth: true
        optional: true
      - url: "https://*.snowflakecomputing.com"
        purpose: "Snowflake CIS benchmark checks — read-only API calls (optional, user-initiated)"
        auth: true
        optional: true
    telemetry: false
    persistence: false
    privilege_escalation: false
    always: false
    autonomous_invocation: restricted
---

# agent-bom — AI Agent Infrastructure Security Scanner

Discovers MCP clients and servers across 22 AI tools, scans for CVEs, maps
blast radius, runs cloud CIS benchmarks, checks OWASP/NIST/MITRE compliance,
generates SBOMs, and assesses AI infrastructure against AISVS v1.0 and MAESTRO
framework layers.

## Install

```bash
pipx install agent-bom
agent-bom agents            # auto-discover + scan
agent-bom check langchain==0.1.0  # check a specific package with version
agent-bom fs .              # scan filesystem packages
agent-bom image nginx:1.25  # scan container image (native)
agent-bom cloud aws         # AWS CIS benchmark
agent-bom iac infra/        # scan Terraform/CloudFormation
agent-bom where             # show all discovery paths
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

## Sub-Skills (8)

| Sub-Skill | Purpose | Triggers |
|-----------|---------|---------|
| [discover](discover/SKILL.md) | Find agents, MCP servers, configurations | "find agents", "what's configured", "mcp inventory" |
| [scan](scan/SKILL.md) | CVE scanning, image scanning, SBOM, provenance | "check package", "scan image", "verify", "blast radius" |
| [scan-infra](scan-infra/SKILL.md) | IaC, cloud config, secrets scanning | "check terraform", "scan kubernetes", "find secrets" |
| [enforce](enforce/SKILL.md) | Runtime policy enforcement, MCP proxy | "block risky calls", "apply policy", "proxy" |
| [compliance](compliance/SKILL.md) | 11-framework compliance, SBOM generation | "compliance report", "NIST", "SOC 2", "OWASP" |
| [monitor](monitor/SKILL.md) | Fleet monitoring, trust scores, lifecycle | "fleet", "watch agents", "trust scores" |
| [analyze](analyze/SKILL.md) | Blast radius, attack paths, context graph | "blast radius", "threat intel", "attack path" |
| [troubleshoot](troubleshoot/SKILL.md) | Diagnostics, doctor, config validation | "doctor", "debug", "why failing", "validate config" |

## Tools (32)

### Vulnerability Scanning
| Tool | Description |
|------|-------------|
| `scan` | Full discovery + vulnerability scan pipeline |
| `check` | Check a package for CVEs (OSV, NVD, EPSS, KEV) |
| `blast_radius` | Map CVE impact chain across agents, servers, credentials |
| `remediate` | Prioritized remediation plan for vulnerabilities |
| `verify` | Package integrity + SLSA provenance check |
| `diff` | Compare two scan reports (new/resolved/persistent) |
| `where` | Show MCP client config discovery paths |
| `inventory` | List discovered agents, servers, packages |

### Compliance & Policy
| Tool | Description |
|------|-------------|
| `compliance` | OWASP LLM/Agentic Top 10, EU AI Act, MITRE ATLAS, NIST AI RMF |
| `policy_check` | Evaluate results against custom security policy (17 conditions) |
| `cis_benchmark` | CIS benchmark checks (AWS, Azure v3.0, GCP v3.0, Snowflake) |
| `generate_sbom` | Generate SBOM (CycloneDX or SPDX format) |
| `aisvs_benchmark` | OWASP AISVS v1.0 compliance — 9 AI security checks |

### Registry & Trust
| Tool | Description |
|------|-------------|
| `registry_lookup` | Look up MCP server in 427+ server security metadata registry |
| `marketplace_check` | Pre-install trust check with registry cross-reference |
| `fleet_scan` | Batch registry lookup + risk scoring for MCP server inventories |
| `skill_trust` | Assess skill file trust level (5-category analysis) |
| `code_scan` | SAST scanning via Semgrep with CWE-based compliance mapping |

### Runtime & Analytics
| Tool | Description |
|------|-------------|
| `context_graph` | Agent context graph with lateral movement analysis |
| `analytics_query` | Query vulnerability trends, posture history, and runtime events |
| `runtime_correlate` | Cross-reference proxy audit JSONL with CVE findings, risk amplification |
| `vector_db_scan` | Probe Qdrant/Weaviate/Chroma/Milvus for auth and exposure |
| `gpu_infra_scan` | GPU container and K8s node inventory + unauthenticated DCGM probe (MAESTRO KC6) |

### Specialized Scans
| Tool | Description |
|------|-------------|
| `dataset_card_scan` | Scan dataset cards for bias, licensing, and provenance issues |
| `training_pipeline_scan` | Scan training pipeline configs for security risks |
| `browser_extension_scan` | Scan browser extensions for risky permissions and AI domain access |
| `model_provenance_scan` | Verify model provenance and supply chain integrity |
| `prompt_scan` | Scan prompt templates for injection and data leakage risks |
| `model_file_scan` | Scan model files for unsafe serialization (pickle, etc.) |
| `license_compliance_scan` | Full SPDX license catalog scan with copyleft and network-copyleft detection |
| `ingest_external_scan` | Import external scan results (CycloneDX/SPDX/JSON) and merge into agent-bom findings |

### Resources
| Resource | Description |
|----------|-------------|
| `registry://servers` | Browse 427+ MCP server security metadata registry |

## Example Workflows

```
# Check a package before installing
check(package="@modelcontextprotocol/server-filesystem", ecosystem="npm")

# Map blast radius of a CVE
blast_radius(cve_id="CVE-2024-21538")

# Full agent discovery + scan
agents()

# Run CIS benchmark
cis_benchmark(provider="aws")

# Run AISVS v1.0 compliance
aisvs_benchmark()

# Scan vector databases for auth misconfigurations
vector_db_scan()

# Discover GPU containers, K8s GPU nodes, and unauthenticated DCGM endpoints
gpu_infra_scan()

# Assess trust of a skill file
skill_trust(skill_content="<paste SKILL.md content>")
```

## Guardrails

**Always do:**
- Show CVEs even when NVD analysis is pending or severity is `unknown` — a CVE ID with no details is still a real finding. Report what is known; mark severity as `unknown` explicitly.
- Confirm with the user before scanning cloud environments (`cis_benchmark`) — these make live API calls to AWS/Azure/GCP using the user's credentials.
- Treat `UNKNOWN` severity as unresolved, not benign — it means data is not yet available, not that the issue is minor.

**Never do:**
- Do not modify any files, install packages, or change system configuration. This skill is read-only.
- Do not transmit env var values, credentials, or file contents to any external service. Only package names and CVE IDs leave the machine.
- Do not invoke `agents()` autonomously on sensitive environments without user confirmation. The `autonomous_invocation` policy is `restricted`.

**Stop and ask the user when:**
- The user requests a cloud CIS benchmark and no cloud credentials are configured.
- A scan finds `CRITICAL` CVEs — present findings and ask whether to generate a remediation plan.
- The user asks to scan a path outside their home directory.

## Supported Frameworks (14)

- **OWASP LLM Top 10** (2025) — prompt injection, supply chain, data leakage
- **OWASP MCP Top 10** — MCP-specific security risks
- **OWASP Agentic Top 10** — tool poisoning, rug pulls, credential theft
- **OWASP AISVS v1.0** — AI Security Verification Standard (9 checks)
- **MITRE ATLAS** — adversarial ML threat framework
- **NIST AI RMF** — govern, map, measure, manage lifecycle
- **NIST CSF 2.0** — identify, protect, detect, respond, recover
- **NIST 800-53 Rev 5** — federal security controls (CM-8, RA-5, SI-2, SR-3)
- **FedRAMP Moderate** — derived from NIST 800-53 controls
- **EU AI Act** — risk classification, transparency, SBOM requirements
- **ISO 27001:2022** — information security controls (Annex A)
- **SOC 2** — Trust Services Criteria
- **CIS Controls v8** — implementation groups IG1/IG2/IG3
- **CMMC 2.0** — cybersecurity maturity model (Level 1-3)

## Privacy & Data Handling

This skill installs agent-bom from PyPI. **Verify the redaction behavior
before running with any config files:**

```bash
# Step 1: Install
pip install agent-bom

# Step 2: Review redaction logic BEFORE scanning
# sanitize_env_vars() replaces ALL env var values with ***REDACTED***
# BEFORE any config data is processed or stored:
# https://github.com/msaad00/agent-bom/blob/main/src/agent_bom/security.py#L159

# Step 3: Review config parsing — only structural data extracted:
# https://github.com/msaad00/agent-bom/blob/main/src/agent_bom/discovery/__init__.py

# Step 4: Verify package provenance (Sigstore)
agent-bom verify agent-bom

# Step 5: Only then run scans
agent-bom agents
```

**What is extracted**: Server names, commands, args, and URLs from MCP client
config files across 22 AI tools. **What is NOT extracted**: Env var values are
replaced with `***REDACTED***` by `sanitize_env_vars()` before any processing.
Only public package names and CVE IDs are sent to vulnerability databases.
Cloud CIS checks use locally configured credentials and call only the cloud
provider's own APIs.

## Verification

- **Source**: [github.com/msaad00/agent-bom](https://github.com/msaad00/agent-bom) (Apache-2.0)
- **Sigstore signed**: `agent-bom verify agent-bom@0.75.10`
- **6,533+ tests** with CodeQL + OpenSSF Scorecard
- **No telemetry**: Zero tracking, zero analytics
