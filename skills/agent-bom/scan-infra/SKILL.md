---
name: agent-bom-scan-infra
description: >-
  Scan infrastructure-as-code, cloud configurations, and find secrets. Use when:
  "check terraform", "scan kubernetes", "IaC", "find secrets",
  "scan dockerfile", "cloud security", "misconfigurations".
version: 0.75.10
license: Apache-2.0
compatibility: >-
  Requires Python 3.11+. Install via pipx or pip. Optional: kubectl for
  Kubernetes checks. Cloud checks use locally configured credentials
  (AWS/Azure/GCP/Snowflake) when explicitly invoked.
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
    credential_policy: "Zero credentials required for IaC and secrets scanning. Cloud checks (AWS/Azure/GCP/Snowflake) optionally accept cloud credentials — only used locally to call cloud APIs, never transmitted elsewhere."
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
    optional_bins:
      - kubectl
    emoji: "\U0001F3D7"
    homepage: https://github.com/msaad00/agent-bom
    source: https://github.com/msaad00/agent-bom
    license: Apache-2.0
    os:
      - darwin
      - linux
      - windows
    data_flow: >-
      IaC and secrets scanning is purely local — no network calls. Cloud
      benchmark checks (optional, user-initiated) call cloud provider APIs
      (AWS/Azure/GCP/Snowflake) using locally configured credentials. No data
      is stored or transmitted beyond the cloud provider's own API.
    file_reads:
      - "user-specified IaC directories (Terraform, CloudFormation, Kubernetes YAML)"
      - "user-specified Dockerfiles"
      - "user-specified cloud configuration files"
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

# agent-bom-scan-infra — Infrastructure & Cloud Security Scanner

Scans infrastructure-as-code (Terraform, CloudFormation, Kubernetes), finds
secrets in config files, and runs cloud CIS benchmarks against AWS, Azure,
GCP, and Snowflake.

## Install

```bash
pipx install agent-bom
agent-bom iac infra/         # scan Terraform/CloudFormation/K8s
agent-bom cloud aws          # AWS CIS benchmark
agent-bom cloud azure        # Azure CIS benchmark
agent-bom cloud gcp          # GCP CIS benchmark
agent-bom secrets .          # find secrets in current directory
```

## When to Use

- "check terraform" / "scan terraform"
- "scan kubernetes" / "K8s security"
- "IaC" / "infrastructure as code"
- "find secrets" / "secret scanning"
- "scan dockerfile"
- "cloud security" / "CIS benchmark"
- "misconfigurations"

## Commands

```bash
# Scan IaC directory
agent-bom iac infra/

# Run cloud CIS benchmark
agent-bom cloud aws
agent-bom cloud azure
agent-bom cloud gcp
agent-bom cloud snowflake

# Find secrets in files
agent-bom secrets .
```

## Tools

| Tool | Description |
|------|-------------|
| `iac` | Scan Terraform, CloudFormation, Kubernetes YAML for misconfigurations |
| `cloud` | CIS benchmark checks (AWS, Azure v3.0, GCP v3.0, Snowflake) |
| `secrets` | Find secrets and credentials in files and directories |

## Examples

```
# Scan IaC directory for misconfigurations
iac(path="infra/")

# Run AWS CIS benchmark
cloud(provider="aws")

# Find secrets in project
secrets(path=".")
```

## Guardrails

- Confirm with the user before running cloud CIS benchmarks — these make live read-only API calls to AWS/Azure/GCP using the user's locally configured credentials.
- IaC and secrets scanning is purely local — no network calls.
- Do not modify any infrastructure files.
- Ask the user before scanning paths outside their home or project directory.
- Cloud credentials are used only to call the cloud provider's own APIs and are never transmitted elsewhere.
