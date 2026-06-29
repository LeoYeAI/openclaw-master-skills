---
name: agent-bom-compliance
description: >-
  AI compliance and policy engine — evaluate scan results against OWASP, NIST,
  SOC 2, ISO 27001, CMMC, EU AI Act, AISVS v1.0, and related frameworks.
  Generate SBOMs and compliance reports. Use when:
  "compliance report", "NIST", "SOC 2", "ISO 27001", "OWASP", "EU AI Act",
  "AISVS", "generate SBOM", "policy check".
version: 0.75.10
license: Apache-2.0
compatibility: >-
  Requires Python 3.11+. Install via pipx or pip. OWASP/NIST/EU AI Act/MITRE
  evaluation and SBOM generation are fully local with zero credentials. CIS
  benchmark checks optionally use cloud SDK credentials (AWS/Azure/GCP/Snowflake)
  and make read-only API calls to cloud providers when explicitly invoked.
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
    credential_policy: "Zero credentials required for OWASP/NIST/EU AI Act compliance and SBOM generation. CIS benchmark checks (AWS, Azure, GCP, Snowflake) optionally accept cloud credentials — only used locally to call cloud APIs, never transmitted elsewhere."
    optional_env:
      - name: AWS_PROFILE
        purpose: "AWS CIS benchmark checks — uses boto3 with your local AWS profile"
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
    optional_bins: []
    emoji: "\U00002705"
    homepage: https://github.com/msaad00/agent-bom
    source: https://github.com/msaad00/agent-bom
    license: Apache-2.0
    os:
      - darwin
      - linux
      - windows
    data_flow: >-
      OWASP/NIST/EU AI Act/MITRE/SBOM evaluation is purely local — zero network
      calls. CIS benchmark checks (optional, user-initiated) call cloud provider
      APIs (AWS/Azure/GCP/Snowflake) using locally configured credentials. No data
      is stored or transmitted beyond the cloud provider's own API. File reads are
      limited to user-provided SBOMs and policy files.
    file_reads:
      - "user-provided SBOM files (CycloneDX/SPDX JSON)"
      - "user-provided policy files (YAML/JSON policy-as-code)"
    file_writes: []
    network_endpoints:
      - url: "https://*.amazonaws.com"
        purpose: "AWS CIS benchmark checks — read-only API calls (IAM, S3, CloudTrail, etc.)"
        auth: true
        optional: true
      - url: "https://management.azure.com"
        purpose: "Azure CIS benchmark checks — read-only API calls (Azure Resource Manager)"
        auth: true
        optional: true
      - url: "https://*.googleapis.com"
        purpose: "GCP CIS benchmark checks — read-only API calls (Cloud Resource Manager, IAM, etc.)"
        auth: true
        optional: true
      - url: "https://*.snowflakecomputing.com"
        purpose: "Snowflake CIS benchmark checks — read-only API calls (ACCOUNT_USAGE views)"
        auth: true
        optional: true
    telemetry: false
    persistence: false
    privilege_escalation: false
    always: false
    autonomous_invocation: restricted
---

# agent-bom-compliance — AI Compliance & Policy Engine

Evaluate AI infrastructure scan results against 14 security and regulatory
frameworks. Enforce policy-as-code rules. Generate SBOMs in standard formats.
Run AISVS v1.0 and CIS benchmark checks.

## Install

```bash
pipx install agent-bom
agent-bom agents -f compliance-export  # run agents scan with compliance export
agent-bom generate-sbom                # generate CycloneDX SBOM
```

## When to Use

- "compliance report" / "run compliance"
- "NIST" / "NIST AI RMF" / "NIST CSF" / "NIST 800-53"
- "SOC 2" / "SOC2"
- "ISO 27001"
- "OWASP" / "OWASP LLM Top 10" / "OWASP Agentic Top 10"
- "EU AI Act"
- "AISVS" / "AI Security Verification Standard"
- "CMMC" / "FedRAMP"
- "generate SBOM" / "CycloneDX" / "SPDX"
- "policy check" / "policy enforcement"

## Tools (5)

| Tool | Description |
|------|-------------|
| `compliance` | OWASP LLM/Agentic Top 10, EU AI Act, MITRE ATLAS, NIST AI RMF |
| `policy_check` | Evaluate results against custom security policy (17 conditions) |
| `cis_benchmark` | Run CIS benchmark checks against cloud accounts |
| `generate_sbom` | Generate SBOM (CycloneDX or SPDX format) |
| `aisvs_benchmark` | OWASP AISVS v1.0 compliance — 9 AI security checks |

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

## Examples

```
# Run compliance check against multiple frameworks
compliance(frameworks=["owasp_llm", "eu_ai_act", "nist_ai_rmf"])

# Enforce custom policy
policy_check(policy={"max_critical": 0, "max_high": 5})

# Generate SBOM
generate_sbom(format="cyclonedx")

# Run AISVS v1.0 compliance
aisvs_benchmark()

# Run AWS CIS benchmark
cis_benchmark(provider="aws")
```

## Privacy & Data Handling

**OWASP, NIST, EU AI Act, MITRE ATLAS, AISVS, SBOM generation, and policy
checks** run entirely locally on scan data already in memory. No network calls,
no credentials needed for these features.

**CIS benchmark checks** (optional, user-initiated) call cloud provider APIs
using your locally configured credentials. These are read-only API calls to
AWS, Azure, GCP, or Snowflake. You must explicitly run `cis_benchmark(provider=...)`
and confirm before any cloud API calls are made.

## Verification

- **Source**: [github.com/msaad00/agent-bom](https://github.com/msaad00/agent-bom) (Apache-2.0)
- **6,533+ tests** with CodeQL + OpenSSF Scorecard
- **No telemetry**: Zero tracking, zero analytics
