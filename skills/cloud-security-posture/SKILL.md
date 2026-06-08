---
name: cloud-security-posture
description: >-
  Cross-cloud security posture assessment covering IAM analysis, encryption
  audit, and public exposure detection across AWS, Azure, and GCP using
  [AWS]/[Azure]/[GCP] inline labels for provider-specific commands.
license: Apache-2.0
metadata:
  safety: read-only
  author: network-security-skills-suite
  version: "1.0.0"
  openclaw: '{"emoji":"☁️","safetyTier":"read-only","requires":{"bins":["aws","az","gcloud"],"env":[]},"tags":["cloud","security","posture"],"mcpDependencies":["aws-network-mcp"],"egressEndpoints":["*.amazonaws.com:443","management.azure.com:443","*.googleapis.com:443"]}'
---

# Cloud Security Posture Assessment

Cross-cloud security posture assessment for evaluating IAM policies,
encryption configuration, and public exposure across [AWS], [Azure],
and [GCP] environments. This skill provides a unified assessment
methodology — diagnostic reasoning is provider-independent, while
specific commands and console paths use inline provider labels.

This is an assessment skill, not a deep-dive into any single provider's
networking layer. For detailed VPC, VNet, or VPC Network analysis, use
the dedicated provider skills: `aws-networking-audit` for VPC/Security
Group/Transit Gateway, `azure-networking-audit` for VNet/NSG/Route Table,
and `gcp-networking-audit` for VPC Network/Firewall Rule/Cloud Router
analysis. Reference `references/cli-reference.md` for multi-provider
CLI commands organized by audit step, and `references/security-controls.md`
for the IAM hierarchy model, encryption matrix, and CIS benchmark
control ID mapping.

## When to Use

- Multi-cloud security review — assessing posture across two or more cloud providers in a single engagement
- Pre-compliance audit — evaluating IAM, encryption, and exposure gaps before formal CIS or SOC 2 assessment
- Cloud migration security gate — verifying security controls are in place before production traffic cutover
- Incident response scoping — quickly determining cross-cloud exposure surface during a security event
- Periodic posture check — scheduled assessment of IAM hygiene, encryption coverage, and public attack surface
- Merger or acquisition due diligence — evaluating cloud security maturity across inherited environments

## Prerequisites

- **[AWS]** AWS CLI v2 configured (`aws sts get-caller-identity` succeeds); IAM permissions for `iam:List*`, `iam:Get*`, `kms:List*`, `kms:DescribeKey`, `s3:GetBucketEncryption`, `s3:GetBucketPolicyStatus`, `ec2:DescribeSecurityGroups`, `ec2:DescribeInstances`, `elasticloadbalancing:DescribeLoadBalancers`, `rds:DescribeDBInstances`, `acm:ListCertificates`
- **[Azure]** Azure CLI (`az account show` succeeds); RBAC Reader role on target subscriptions; permissions for `Microsoft.Authorization/roleAssignments/read`, `Microsoft.KeyVault/vaults/read`, `Microsoft.Compute/disks/read`, `Microsoft.Network/publicIPAddresses/read`, `Microsoft.Network/networkSecurityGroups/read`, `Microsoft.Storage/storageAccounts/read`
- **[GCP]** gcloud CLI configured (`gcloud auth list` shows active account); roles `roles/iam.securityReviewer`, `roles/cloudkms.viewer`, `roles/compute.viewer`, `roles/storage.admin` (for bucket IAM inspection) on target project(s)
- **Target scope identified** — cloud accounts/subscriptions/projects, regions, and environment tier (prod, staging, dev) defined before assessment begins
- **Assessment window** — coordinate with operations to avoid snapshot timing during deployments or maintenance windows

## Procedure

Follow these six steps sequentially. Each step produces findings that
feed the cross-cloud posture summary in Step 6.

### Step 1: IAM Posture Assessment

Evaluate identity and access management configuration for privilege
escalation risks, excessive permissions, and policy hygiene across
all in-scope providers. Focus on three areas: overly permissive
policies, missing authentication controls, and privilege escalation
paths through role chaining or impersonation.

**[AWS]** Enumerate IAM users, roles, and policies. Check for wildcard
actions in customer-managed policies:

```
aws iam get-account-authorization-details --output json
aws iam list-policies --scope Local --query 'Policies[?AttachmentCount>`0`]'
```

Flag policies with `"Action": "*"` or `"Resource": "*"` as Critical.
Review Service Control Policies (SCPs) in Organizations for boundary
gaps that allow privilege escalation paths (e.g., `iam:CreateRole` +
`iam:AttachRolePolicy` without SCP deny). Check for IAM users with
console access but no MFA: `aws iam get-credential-report`.

**[Azure]** Audit RBAC role assignments and Entra ID configuration:

```
az role assignment list --all --output table
az ad user list --query "[?userType=='Member']" --output table
```

Identify Owner/Contributor role sprawl — assignments at subscription
scope with no expiration indicate missing Privileged Identity Management
(PIM) activation policies. Review Conditional Access policies for gaps:
no policy covering all users, missing device compliance requirements,
or legacy authentication protocols not blocked.

**[GCP]** Analyze IAM bindings and Organization Policy constraints:

```
gcloud projects get-iam-policy <project-id> --format=json
gcloud resource-manager org-policies list --project=<project-id>
```

Flag bindings with `roles/owner` or `roles/editor` on service accounts
as Critical. Check for service account key age exceeding 90 days:
`gcloud iam service-accounts keys list --iam-account=<sa-email>`.
Verify Organization Policy constraints enforce `iam.disableServiceAccountKeyCreation`
where applicable.

### Step 2: Encryption Audit

Assess encryption at rest and in transit across storage, compute,
and database services. Evaluate key management practices including
rotation schedules, access policies, and customer-managed vs
provider-managed key usage.

**[AWS]** Verify KMS key policies, storage encryption, and certificate
management:

```
aws kms list-keys --output table
aws s3api get-bucket-encryption --bucket <bucket-name>
aws rds describe-db-instances --query 'DBInstances[*].[DBInstanceIdentifier,StorageEncrypted,KmsKeyId]'
```

Check EBS volume encryption: `aws ec2 describe-volumes --query 'Volumes[?!Encrypted]'`.
Review ACM certificate expiry: `aws acm list-certificates --query 'CertificateSummaryList[?Status==`ISSUED`]'`.
Flag any unencrypted S3 buckets, EBS volumes, or RDS instances as
High severity. Verify KMS key rotation is enabled for customer-managed
keys: `aws kms get-key-rotation-status --key-id <key-id>`.

**[Azure]** Audit Key Vault configuration, disk encryption, and TLS:

```
az keyvault list --output table
az disk list --query "[?encryption.type!='EncryptionAtRestWithPlatformKey']" --output table
```

Verify Key Vault access policies follow least privilege — no vault
with "Get, List, Set, Delete" for all principals. Check managed disk
encryption type (platform-managed vs customer-managed keys). Review
TLS minimum version on App Services: `az webapp list --query "[].{name:name, minTlsVersion:siteConfig.minTlsVersion}"`.

**[GCP]** Assess Cloud KMS configuration and default encryption:

```
gcloud kms keyrings list --location=<location>
gcloud kms keys list --keyring=<keyring> --location=<location>
```

Determine CMEK vs Google-managed encryption per service. Flag any
Cloud Storage buckets or Compute disks without CMEK if the
organization policy requires it. Check KMS key rotation period:
`gcloud kms keys describe <key> --keyring=<keyring> --location=<location>`.
Verify SSL policy compliance on load balancers:
`gcloud compute ssl-policies list`.

### Step 3: Public Exposure Detection

Identify publicly accessible resources and evaluate network-level
exposure across all three providers. Public exposure combined with
weak authentication (Step 1) or missing encryption (Step 2) compounds
severity — cross-reference findings when classifying risk.

**[AWS]** Check for public S3 buckets, permissive Security Groups,
and load balancer configuration:

```
aws s3api list-buckets --query 'Buckets[*].Name' --output text
aws s3api get-bucket-policy-status --bucket <bucket-name>
aws ec2 describe-security-groups --filters "Name=ip-permission.cidr,Values=0.0.0.0/0"
```

Flag Security Groups allowing `0.0.0.0/0` ingress on non-standard
ports as Critical. Check ELB access logging: `aws elbv2 describe-load-balancer-attributes --load-balancer-arn <arn> --query 'Attributes[?Key==`access_logs.s3.enabled`]'`.

**[Azure]** Identify public IPs without network security controls:

```
az network public-ip list --output table
az network nsg list --output table
az storage account list --query "[].{name:name, publicAccess:allowBlobPublicAccess}"
```

Flag public IPs with no associated NSG as High severity. Check
storage account public access settings — `allowBlobPublicAccess: true`
requires justification. Verify Application Gateway WAF mode is
"Prevention" not "Detection" for production workloads.

**[GCP]** Detect public firewall rules and external load balancer
exposure:

```
gcloud compute firewall-rules list --filter="sourceRanges:0.0.0.0/0" --format=table
gcloud compute forwarding-rules list --filter="loadBalancingScheme=EXTERNAL"
```

Flag firewall rules with `0.0.0.0/0` source range on non-443/80
ports as Critical. Check Cloud Storage public access:
`gsutil iam get gs://<bucket>` and look for `allUsers` or
`allAuthenticatedUsers` bindings. Verify external load balancer
backends are intentionally public.

### Step 4: Network Security Cross-Reference

Delegate deep network security analysis to the dedicated provider
networking skills. This step connects posture findings to network
architecture context and ensures that infrastructure-level controls
complement the identity and data protection evaluated in Steps 1–3.

- **[AWS]** Run `aws-networking-audit` for VPC CIDR design, Security Group rule-by-rule analysis, Transit Gateway topology, VPC Flow Log forensics, and Route Table validation
- **[Azure]** Run `azure-networking-audit` for VNet architecture, NSG effective rules, Route Table/UDR analysis, Network Watcher diagnostics, and Service Endpoint/Private Link coverage
- **[GCP]** Run `gcp-networking-audit` for VPC Network design, hierarchical firewall policy analysis, Cloud Router/BGP configuration, VPC Flow Log analysis, and Cloud NAT verification

Correlate findings: IAM misconfigurations (Step 1) combined with
permissive network rules (this step) represent compounded risk.
A service account with `roles/editor` behind a firewall rule
allowing `0.0.0.0/0` is more urgent than either finding alone.
Document cross-references between posture findings and network
architecture gaps in the final report.

### Step 5: Compliance Mapping

Map findings to compliance framework controls. Reference CIS benchmark
control IDs for provider-specific checks and SOC 2 criteria for
organizational controls. This step transforms technical findings into
auditor-consumable evidence.

**CIS Cloud Benchmark References** (control IDs for audit mapping):

- **[AWS]** CIS AWS Foundations Benchmark — Section 1 (IAM), Section 2 (Storage/Logging), Section 3 (Monitoring), Section 4 (Networking), Section 5 (Compute)
- **[Azure]** CIS Azure Foundations Benchmark — Section 1 (IAM), Section 2 (Microsoft Defender), Section 3 (Storage), Section 4 (Database), Section 5 (Logging), Section 6 (Networking), Section 7 (VM), Section 8 (Key Vault)
- **[GCP]** CIS GCP Foundations Benchmark — Section 1 (IAM), Section 2 (Logging/Monitoring), Section 3 (Networking), Section 4 (VM), Section 5 (Storage), Section 6 (Cloud SQL), Section 7 (BigQuery)

Map each finding to the applicable CIS section and control number.
See `references/security-controls.md` for the full control ID index.

**SOC 2 Control Mapping** — Map infrastructure findings to Trust
Services Criteria: CC6 (Logical and Physical Access Controls) for
IAM and network exposure findings, CC7 (System Operations) for
encryption and monitoring gaps.

**Severity Classification** — Critical: exploitable public exposure
or admin-level privilege escalation. High: unencrypted sensitive
data or overly permissive IAM. Medium: missing logging, stale
credentials, or suboptimal encryption key management. Low:
configuration drift from best practice without direct exploit path.

### Step 6: Cross-Cloud Posture Report

Compile findings into a structured cross-cloud posture report with
provider-by-provider comparison and prioritized remediation actions.

**Provider Comparison Matrix** — Tabulate findings by domain (IAM,
encryption, exposure) and provider. Identify which provider has
the strongest/weakest posture per domain. Flag any provider that
lacks coverage for a domain (e.g., no encryption at rest audit
completed for GCP). Note configuration parity gaps — if AWS
enforces MFA but Azure does not require Conditional Access, the
inconsistency itself is a finding.

**Prioritized Remediation** — Rank all findings by severity, then
by blast radius (multi-provider issues first). Group remediation
actions by provider to enable parallel workstreams. Estimate
effort for each remediation (quick fix vs project-level change).
Identify quick wins: enabling encryption defaults, rotating stale
keys, and restricting overly permissive firewall rules typically
resolve 30–50% of findings with minimal change risk.

**Executive Summary** — Overall posture score per provider (Critical/
High/Medium/Low finding counts), cross-cloud consistency assessment,
top 5 priority remediations, and recommended reassessment timeline.
Include trend data if prior assessments exist — improving or
degrading posture per domain.

## Threshold Tables

| Domain | Severity | Condition | Example |
|--------|----------|-----------|---------|
| IAM | Critical | Wildcard admin policy without SCP boundary | `"Action": "*", "Resource": "*"` |
| IAM | High | Service account/user with no MFA and console access | AWS IAM user, Azure member without CA |
| IAM | Medium | Service account key age >90 days | [GCP] key rotation overdue |
| IAM | Low | Unused IAM role with permissions attached | Role with 0 last-used date |
| Encryption | Critical | Unencrypted database with sensitive data | RDS, Azure SQL, Cloud SQL |
| Encryption | High | Unencrypted storage bucket/volume | S3, Blob Storage, Cloud Storage |
| Encryption | Medium | Customer-managed key rotation >365 days | KMS, Key Vault, Cloud KMS |
| Encryption | Low | Platform-managed keys where CMEK policy exists | Org policy violation |
| Exposure | Critical | Public access on 0.0.0.0/0 non-web ports | SSH/RDP open to internet |
| Exposure | High | Storage bucket publicly accessible | S3, Blob, GCS with allUsers |
| Exposure | Medium | Load balancer without access logging | ALB, App Gateway, Cloud LB |
| Exposure | Low | WAF in detection mode (not prevention) | [Azure] App Gateway WAF |

## Decision Trees

```
Cloud Posture Assessment Scoping:
├─ Single provider? → Use dedicated provider skill (aws/azure/gcp-networking-audit)
├─ Multiple providers? → Use this skill for cross-cloud posture assessment
│  ├─ All 3 providers in scope? → Full procedure (Steps 1–6)
│  ├─ 2 providers? → Skip provider-specific checks for absent provider
│  └─ Compliance required? → Include Step 5 mapping
└─ Provider deep-dive needed? → Cross-reference to dedicated skill (Step 4)

Finding Severity Assignment:
├─ Exploitable from internet with no authentication? → Critical
├─ Data exposure or privilege escalation path? → High
├─ Missing logging or stale credentials? → Medium
└─ Configuration drift without exploit path? → Low

IAM Escalation Path Detection:
├─ User/role can create new roles? → Check SCP/org policy boundary
│  ├─ No boundary? → Critical — unbounded privilege escalation
│  └─ Boundary exists? → Verify deny rules cover CreateRole + AttachPolicy
├─ Service account can impersonate other accounts? → High
└─ Cross-account trust allows external principals? → High
```

## Report Template

```markdown
# Cloud Security Posture Assessment Report

## Executive Summary
- **Assessment scope:** [AWS accounts / Azure subscriptions / GCP projects]
- **Assessment date:** [date]
- **Overall posture:** [Critical/High/Medium/Low finding summary]

## Provider Comparison Matrix
| Domain     | AWS        | Azure      | GCP        |
|------------|------------|------------|------------|
| IAM        | [findings] | [findings] | [findings] |
| Encryption | [findings] | [findings] | [findings] |
| Exposure   | [findings] | [findings] | [findings] |
| Network    | [ref: provider skill] | [ref: provider skill] | [ref: provider skill] |

## Findings by Severity

### Critical
| # | Provider | Domain | Finding | CIS Control | Remediation |
|---|----------|--------|---------|-------------|-------------|

### High
| # | Provider | Domain | Finding | CIS Control | Remediation |
|---|----------|--------|---------|-------------|-------------|

### Medium / Low
[Grouped table for lower-severity findings]

## Remediation Roadmap
1. [Immediate — Critical findings, estimated effort]
2. [Short-term — High findings within 30 days]
3. [Medium-term — Medium findings within 90 days]

## Appendix
- Provider-specific networking audit references
- Full CIS control mapping table
- Evidence collection inventory
```

## Troubleshooting

**Insufficient permissions on one provider** — If credential checks
fail for a single provider (`aws sts get-caller-identity`, `az account
show`, or `gcloud auth list`), proceed with available providers and
document the gap. Partial assessments are valuable — note "Provider X
not assessed" in the comparison matrix.

**Cross-account or cross-subscription enumeration failures** — Multi-
account AWS environments require assume-role chains; multi-subscription
Azure requires Reader on each subscription. If enumeration returns
empty results, verify role trust policies and subscription RBAC before
assuming clean posture.

**Large-scale environments** — For environments with 50+ accounts or
subscriptions, sample-based assessment is acceptable. Prioritize
production accounts, internet-facing workloads, and accounts with
external trust relationships. Document sampling methodology and
coverage percentage in the report. Consider using cloud-native
aggregation tools ([AWS] Security Hub, [Azure] Defender for Cloud,
[GCP] Security Command Center) to supplement manual CLI checks.

**Conflicting severity across providers** — The same logical risk
(e.g., public storage) may present differently per provider. Use the
Threshold Tables severity definitions consistently. A publicly
accessible S3 bucket, Azure Blob container, and GCS bucket all receive
the same severity regardless of provider-specific defaults or naming.

**Stale credentials not surfaced by default** — [AWS] credential
reports require generation (`aws iam generate-credential-report`)
before download. [Azure] sign-in logs require Azure AD Premium P1.
[GCP] service account key listing shows creation date but not last
usage without additional audit log queries. Document data freshness
limitations in the report appendix.

**CIS benchmark version alignment** — Verify which CIS benchmark
version applies to the deployed cloud service versions. Cite the
benchmark version in findings (e.g., "CIS AWS Foundations v2.0.0 —
1.4"). Reference `references/security-controls.md` for control IDs.
