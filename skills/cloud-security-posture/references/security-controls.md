# Security Controls Reference — Cloud Security Posture Assessment

IAM hierarchy models, encryption matrices, public exposure detection
patterns, and CIS benchmark control ID references across AWS, Azure,
and GCP.

## IAM Hierarchy Model

### [AWS] IAM Hierarchy

```
AWS Organizations
└── Service Control Policies (SCPs) — permission boundary
    └── Account
        ├── IAM Users — direct principals with long-lived credentials
        │   └── IAM Policies (inline + managed)
        ├── IAM Roles — assumable principals with temporary credentials
        │   ├── Trust Policy — who can assume
        │   └── Permission Policy — what can be done
        ├── IAM Groups — policy attachment point for users
        └── Permission Boundaries — maximum permission envelope per principal
```

**Escalation paths:** `iam:CreateRole` + `iam:AttachRolePolicy` (create
admin role), `iam:PassRole` + `lambda:CreateFunction` (execute as role),
`sts:AssumeRole` with overly permissive trust policy.

### [Azure] IAM Hierarchy

```
Entra ID (Azure AD) Tenant
├── Management Groups — RBAC inheritance scope
│   └── Subscriptions
│       └── Resource Groups
│           └── Resources
├── Privileged Identity Management (PIM) — just-in-time activation
├── Conditional Access Policies — authentication context controls
└── App Registrations / Service Principals — application identity
```

**Escalation paths:** Owner at subscription scope without PIM
(permanent admin), User Access Administrator (can grant others Owner),
Application with Directory.ReadWrite.All (can modify any directory object).

### [GCP] IAM Hierarchy

```
Organization
├── Organization Policies — constraint enforcement
├── Folders — project grouping with inherited IAM
│   └── Projects
│       └── Resources
├── Service Accounts — application identity
│   ├── User-managed keys — long-lived, rotation required
│   └── Google-managed keys — automatic rotation
└── Workload Identity Federation — external identity mapping
```

**Escalation paths:** `iam.serviceAccountTokenCreator` (impersonate
any SA), `resourcemanager.projectIamAdmin` (grant self any role),
user-managed service account keys with `roles/owner`.

## Encryption Matrix

### Encryption at Rest

| Service Category | [AWS] | [Azure] | [GCP] |
|-----------------|-------|---------|-------|
| Object storage | S3 — SSE-S3, SSE-KMS, SSE-C | Blob — Microsoft-managed, CMK | GCS — Google-managed, CMEK, CSEK |
| Block storage | EBS — AES-256, KMS optional | Managed Disk — platform or CMK | Persistent Disk — Google-managed or CMEK |
| Database | RDS — KMS encryption | SQL DB — TDE with service or CMK | Cloud SQL — Google-managed or CMEK |
| File storage | EFS — KMS encryption | Azure Files — Microsoft or CMK | Filestore — Google-managed or CMEK |
| Default behavior | Not encrypted by default (opt-in per service) | Encrypted by default (platform-managed) | Encrypted by default (Google-managed) |

### Encryption in Transit

| Control | [AWS] | [Azure] | [GCP] |
|---------|-------|---------|-------|
| Load balancer TLS | ALB/NLB TLS termination, ACM certs | App Gateway TLS, Key Vault certs | Cloud Load Balancer SSL policies |
| Minimum TLS | Security policy on LB | minTlsVersion on App Service/SQL | SSL policy profile (MODERN/RESTRICTED) |
| Internal traffic | VPC-internal unencrypted by default | VNet-internal unencrypted by default | Encrypted by default (inter-VM) |
| API endpoints | HTTPS enforced on all AWS APIs | HTTPS enforced on management plane | HTTPS enforced on all GCP APIs |

## Public Exposure Detection Patterns

### Storage Exposure

| Pattern | [AWS] | [Azure] | [GCP] |
|---------|-------|---------|-------|
| Public access check | `get-bucket-policy-status` IsPublic flag | `allowBlobPublicAccess` property | `allUsers`/`allAuthenticatedUsers` IAM binding |
| Block mechanism | S3 Block Public Access (account + bucket) | Storage account public access disable | Uniform bucket-level access + org policy |
| Audit signal | S3 Access Logs, CloudTrail data events | Storage Analytics logs, diagnostic logs | Cloud Audit Logs data access |

### Network Exposure

| Pattern | [AWS] | [Azure] | [GCP] |
|---------|-------|---------|-------|
| Open ingress | SG rule with `0.0.0.0/0` source | NSG rule with `*` source | Firewall rule with `0.0.0.0/0` source |
| Public IP | EIP attached to instance/ENI | Public IP resource associated to NIC | External IP on instance access config |
| Load balancer | Internet-facing ALB/NLB/CLB | Public load balancer frontend | External forwarding rule |
| WAF protection | AWS WAF on ALB/CloudFront | App Gateway WAF or Azure Front Door WAF | Cloud Armor policy on backend service |

## CIS Cloud Benchmark Control ID Reference

Control IDs for cross-referencing assessment findings to CIS benchmark
sections. Reference only — see the published CIS benchmark documents
for full control descriptions and audit procedures.

### [AWS] CIS AWS Foundations Benchmark

| Section | Domain | Example Control IDs |
|---------|--------|-------------------|
| 1 | Identity and Access Management | 1.1–1.22 |
| 2 | Storage | 2.1.1–2.1.4, 2.2.1, 2.3.1–2.3.3 |
| 3 | Logging | 3.1–3.11 |
| 4 | Monitoring | 4.1–4.16 |
| 5 | Networking | 5.1–5.6 |

### [Azure] CIS Azure Foundations Benchmark

| Section | Domain | Example Control IDs |
|---------|--------|-------------------|
| 1 | Identity and Access Management | 1.1–1.25 |
| 2 | Microsoft Defender | 2.1.1–2.1.22 |
| 3 | Storage Accounts | 3.1–3.15 |
| 4 | Database Services | 4.1.1–4.5.1 |
| 5 | Logging and Monitoring | 5.1.1–5.3.1 |
| 6 | Networking | 6.1–6.7 |
| 7 | Virtual Machines | 7.1–7.7 |
| 8 | Key Vault | 8.1–8.7 |

### [GCP] CIS GCP Foundations Benchmark

| Section | Domain | Example Control IDs |
|---------|--------|-------------------|
| 1 | Identity and Access Management | 1.1–1.18 |
| 2 | Logging and Monitoring | 2.1–2.16 |
| 3 | Networking | 3.1–3.10 |
| 4 | Virtual Machines | 4.1–4.12 |
| 5 | Storage | 5.1–5.3 |
| 6 | Cloud SQL Database | 6.1–6.7 |
| 7 | BigQuery | 7.1–7.3 |

### SOC 2 Trust Services Criteria Mapping

| Criteria | Domain | Cloud Posture Relevance |
|----------|--------|----------------------|
| CC6.1 | Logical Access Security | IAM policy assessment, MFA enforcement |
| CC6.2 | System Access Restrictions | Network exposure detection, firewall rules |
| CC6.3 | Encryption of Data | Encryption at rest and in transit audit |
| CC6.6 | Boundaries and Authentication | Cross-cloud network security posture |
| CC6.7 | Data Transmission Protection | TLS configuration, SSL policy compliance |
| CC7.1 | Detection of Changes | Configuration drift, compliance monitoring |
| CC7.2 | Monitoring for Anomalies | Logging coverage, audit trail completeness |
