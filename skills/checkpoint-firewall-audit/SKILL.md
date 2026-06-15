---
name: checkpoint-firewall-audit
description: >-
  Check Point R80+/R81.x rulebase layer analysis with blade activation audit,
  SmartConsole management plane validation, NAT policy review, identity
  awareness assessment, and compliance verification. Systematic layer-by-layer
  evaluation for Check Point Security Gateways managed via Management Server
  or Multi-Domain Server (MDS).
license: Apache-2.0
metadata:
  safety: read-only
  author: network-security-skills-suite
  version: "1.0.0"
  openclaw: '{"emoji":"🛡️","safetyTier":"read-only","requires":{"bins":["ssh"],"env":[]},"tags":["checkpoint","firewall","audit"],"mcpDependencies":[],"egressEndpoints":[]}'
---

# Check Point Firewall Security Policy Audit

Policy-audit-driven analysis of Check Point Security Gateway policies. Unlike
generic firewall checklists that check for open ports and default-deny, this
skill evaluates the Check Point-specific security architecture: rulebase
ordered and inline layers, Software Blade activation coverage, management
plane trust (SIC), and the Unified Policy model introduced in R80+.

Covers R80.x and R81.x gateways managed via SmartConsole connected to a
Security Management Server or Multi-Domain Server (MDS). Reference
`references/policy-model.md` for the R80+ architecture and layer model,
and `references/cli-reference.md` for read-only CLI and API commands.

## When to Use

- Rulebase layer review after rule additions or layer restructuring
- Blade activation audit verifying that licensed blades are enabled on all gateways
- Annual or quarterly compliance audit requiring per-rule justification
- Post-incident rulebase assessment to identify how traffic was permitted
- SmartConsole management plane validation — SIC trust, log server connectivity
- Multi-Domain (MDS) domain isolation audit for MSSP or multi-tenant environments
- NAT policy review after network re-addressing or migration
- Pre-upgrade rulebase baseline before R80.x → R81.x migration
- Identity awareness assessment — verifying AD integration and access role coverage

## Prerequisites

- Read-only administrator access to SmartConsole or Management Server API (`mgmt_cli` / Web API)
- SSH access to the Security Gateway for `fw`, `cpstat`, and `cpview` commands (Expert mode)
- Understanding of the management architecture — Management Server, Log Server, and Security Gateway relationships
- Knowledge of expected blade activation per gateway — which blades should be enabled where
- For MDS environments: domain-level access with visibility into each managed domain
- Policy installed — audit evaluates the installed policy, not the SmartConsole staging session

## Procedure

Follow this audit flow sequentially. Each step builds on prior findings.
The procedure moves from management architecture through rulebase layer
analysis to blade activation, NAT, identity, and compliance verification.

### Step 1: Management Architecture Inventory

Map the management plane topology.

```
cpstat mg
mgmt_cli show gateways-and-servers --format json -r true
```

Record: Management Server hostname and version, Log Server(s), Security
Gateway(s) with version and SIC status. In MDS environments, list all
domains and their assigned gateways.

Verify SIC trust between Management Server and each gateway:

```
cpstat sic
fw stat
```

SIC (Secure Internal Communication) trust must be established for policy
installation and log forwarding. A gateway with SIC status other than
"Trust established" cannot receive policy updates — stale policy is a
Critical finding.

For Multi-Domain deployments, verify domain isolation:

```
mdsstat
```

Each domain should be an independent management container. Cross-domain
policy leakage indicates architecture misconfiguration.

Check Management Server disk space and health — a full log partition
prevents logging:

```
cpstat os -f disk
cpview
```

### Step 2: Rulebase Layer Analysis

R80+ uses a Unified Policy model with ordered layers. Each layer is an
independent rulebase evaluated sequentially.

```
mgmt_cli show access-rulebase name "Network" --format json -r true
```

Retrieve each access layer and evaluate:

- **Layer structure:** Ordered layers evaluate top-to-bottom. Each layer
  must independently reach a decision (Accept/Drop/Reject) for the traffic,
  or the traffic is implicitly dropped. An inline layer is embedded within
  a rule in a parent layer — it sub-divides that rule's match.
- **Rule ordering within layers:** First-match evaluation. Rules within a
  layer are evaluated top-down; the first matching rule is applied.
- **Implicit rules:** Check Point inserts implicit rules controlled by
  Global Properties. Key implicit rules include:
  - Accept control connections (Management, logging)
  - Accept outgoing from gateway
  - Cleanup rule (default drop at bottom)
  - Stealth rule (protect the gateway itself — must be explicitly added)
- **Disabled rules:** Rules with `enabled: false` consume rulebase space
  but do not evaluate. Flag for cleanup.
- **Rule hit counts:** Identify rules with zero hits over 90+ days as
  cleanup candidates. Hit counts are available via SmartConsole or API.
- **Overly permissive rules:** Rules with Source=Any, Destination=Any,
  Service=Any, Action=Accept are Critical — they permit all traffic
  within the layer.

```
mgmt_cli show access-rulebase name "Network" details-level full --format json -r true
```

Use `details-level full` to retrieve source, destination, service, action,
track, and profile bindings for each rule.

### Step 3: Blade Activation Audit

Check Point Software Blades provide security functions. Each blade must be
licensed and enabled per gateway.

```
cpstat blades
cpstat fw
```

Verify activation status for each blade on every gateway:

| Blade | Function | Expected On |
|-------|----------|-------------|
| Firewall | Stateful packet inspection | All gateways |
| IPS | Intrusion prevention signatures | Internet-facing gateways |
| Application Control | Application identification and enforcement | Internet-facing gateways |
| URL Filtering | URL categorization and blocking | Gateways with user web traffic |
| Anti-Bot | Bot C2 communication detection | All gateways |
| Anti-Virus | File-based malware scanning | All gateways |
| Threat Emulation | Sandbox analysis for unknown files | Internet-facing gateways |
| Threat Extraction | Content disarm and reconstruction | Email/download gateways |
| Content Awareness | Data visibility and DLP | Gateways handling sensitive data |
| HTTPS Inspection | TLS decryption for content inspection | Internet-facing gateways |

Compare licensed blades (contract entitlement) against enabled blades.
Licensed but disabled blades represent undeployed security capability.
Enabled but unlicensed blades will stop functioning on license expiry.

```
cpstat licenseStat
cplic print
```

Check Threat Prevention profiles assigned to rules — blades are only
effective when both enabled on the gateway AND referenced in policy rules
via a Threat Prevention profile.

### Step 4: NAT Policy Review

Check Point supports two NAT methods: Automatic NAT (per-object) and
Manual NAT (explicit rulebase).

```
mgmt_cli show nat-rulebase --format json -r true
```

Evaluate NAT policy:

- **Automatic NAT rules:** Defined on network objects (host, network,
  address range). Check Point generates NAT rules automatically based on
  object NAT settings. Review each object's NAT configuration.
- **Manual NAT rules:** Explicit rules in the NAT rulebase, evaluated
  top-down before automatic rules. Review rule ordering for conflicts.
- **NAT method:** Hide NAT (many-to-one PAT) vs Static NAT (one-to-one).
  Static NAT on internal servers should have corresponding security rules
  restricting access to required services only.
- **NAT rule ordering:** Manual rules evaluate before Automatic rules.
  Within each section, rules evaluate top-down. Conflicting rules in
  manual section override automatic NAT.

Verify that NAT does not expose internal addressing or create unintended
access paths. Cross-reference static NAT entries with security policy rules.

### Step 5: Identity Awareness and Access Role Assessment

If Identity Awareness blade is enabled, evaluate the identity integration.

```
pdp status stat
mgmt_cli show access-roles --format json -r true
```

Check:

- **Identity sources:** Active Directory integration (AD Query or Identity
  Collector), RADIUS accounting, Terminal Servers agent, captive portal,
  Remote Access VPN identity. Verify connectivity to each source.
- **Access roles in security rules:** Access roles combine user/group
  identity with machine identity. Rules referencing access roles require
  functioning identity sources — if AD connectivity fails, identity-based
  rules cannot match, and traffic falls to non-identity rules.
- **Identity agent deployment:** Check whether Identity Agent or Captive
  Portal covers all user segments. Gaps in identity collection mean those
  users match rules as "unknown user."
- **Identity sharing:** In MDS or distributed environments, verify identity
  information is shared between gateways that need it.

### Step 6: Log and Compliance Verification

Verify log infrastructure and compliance monitoring.

```
cpstat logging
fw log -t
```

Check:

- **Log Server connectivity:** Verify each gateway can forward logs to the
  Log Server. Check for log gaps that indicate connectivity interruptions.
- **Log completeness:** Rules with Track=None produce no log entries.
  Identify security-relevant rules without logging — at minimum, all Drop
  and Reject rules should log.
- **SmartEvent correlation:** If SmartEvent is deployed, verify correlation
  policy is active and generating events from security logs.
- **Compliance blade:** If enabled, verify compliance checks are running
  and review the latest compliance report for failed checks.

```
cpstat antimalware
cpstat appi
```

Verify Threat Prevention signature databases are current:

| Database | Maximum Age | Check |
|----------|-------------|-------|
| IPS signatures | 7 days | `cpstat ips` |
| Application Control DB | 7 days | `cpstat appi` |
| Anti-Bot signatures | 24 hours | `cpstat antimalware` |
| Anti-Virus signatures | 24 hours | `cpstat antimalware` |
| URL Filtering DB | 7 days | `cpstat urlf` |

## Threshold Tables

### Policy Rule Severity Classification

| Finding | Severity | Rationale |
|---------|----------|-----------|
| Source=Any, Destination=Any, Service=Any, Action=Accept | Critical | Fully open rule — permits all traffic within the layer |
| Gateway SIC trust not established | Critical | Gateway cannot receive policy updates; running stale policy |
| Licensed blades not enabled on internet-facing gateway | High | Purchased security capability not deployed |
| Rule with Action=Accept and no Threat Prevention profile | High | Traffic passes without IPS, Anti-Bot, or AV inspection |
| HTTPS Inspection not enabled on internet-bound traffic | High | Encrypted traffic bypasses content inspection blades |
| Threat Prevention signatures >7 days old | High | Detection gap for recently discovered threats |
| Missing Stealth rule (no rule protecting gateway itself) | High | Gateway management plane exposed to data-plane traffic |
| Manual NAT rule conflicts with Automatic NAT | Medium | Unexpected NAT behavior; traffic may not translate as intended |
| Rules with zero hit count >90 days | Medium | Unused rules — cleanup candidates |
| Disabled rules in production layer | Medium | Audit confusion; stale configuration |
| Track=None on Drop/Reject rule | Medium | Security-relevant denied traffic not logged |
| Identity Awareness source connectivity failure | Medium | Identity-based rules unable to match users; fallback behavior |
| Log Server connectivity intermittent | Medium | Log gaps reduce incident investigation capability |
| Implicit cleanup rule handling all denied traffic | Low | Expected behavior, but verify logging is enabled |

### Blade Activation Maturity

| Coverage | Maturity | Guidance |
|----------|----------|----------|
| All licensed blades enabled + profiles in policy | Mature | Maintain; review profile settings quarterly |
| Blades enabled but profiles not referenced in rules | Developing | Bind Threat Prevention profiles to all Accept rules |
| Licensed blades not enabled | Immature | Enable blades and create Threat Prevention profiles |

## Decision Trees

### Overly Permissive Rule Remediation

```
Rule has Source=Any, Destination=Any, Service=Any
├── Action = Accept?
│   ├── Yes → CRITICAL: Fully open rule
│   │   ├── Is this a temporary migration rule?
│   │   │   ├── Yes → Set expiration, add to migration tracker
│   │   │   └── No → Immediate remediation required
│   │   └── Identify actual traffic via SmartLog:
│   │       Filter by rule number → analyze source/dest/service
│   │       → Replace with specific objects and services
│   └── No (Drop/Reject) → This is the cleanup rule; verify Track=Log
│
├── Threat Prevention profile bound?
│   ├── No → Bind profile BEFORE narrowing rule scope
│   │   └── Ensures threat visibility during migration
│   └── Yes → Proceed with scope reduction
│
└── Rule in ordered layer or inline layer?
    ├── Ordered layer → Affects all traffic in that layer
    └── Inline layer → Scoped to parent rule match
        └── Check parent rule scope to assess true exposure
```

### Blade Gap Remediation

```
Gateway missing expected blades
├── Blade licensed?
│   ├── No → Procurement required; document risk until enabled
│   └── Yes → Enable blade in SmartConsole gateway object
│       ├── IPS → Assign IPS profile; set to Prevent mode
│       ├── Application Control → Create/assign App Control policy
│       ├── Anti-Bot → Assign profile; enable in Threat Prevention
│       ├── Anti-Virus → Assign profile; enable in Threat Prevention
│       ├── Threat Emulation → Assign profile; select emulation env
│       ├── HTTPS Inspection → Configure CA cert + inspection policy
│       └── URL Filtering → Assign categorization profile
│
├── Performance concern?
│   ├── SecureXL acceleration enabled? → Verify blade compatibility
│   └── CoreXL CPU allocation → Check SNDs and FW workers balance
│       cpstat os -f multi_cpu
│
└── After enabling → Install policy and verify blade active:
    cpstat blades -f blade_name
```

## Report Template

```
CHECK POINT SECURITY POLICY AUDIT REPORT
==========================================
Management Server: [hostname] [version]
Gateway(s): [hostname(s)] [version(s)]
Domain: [domain name (MDS) / N/A (SMS)]
Policy Name: [installed policy name]
Audit Date: [timestamp]
Performed By: [operator/agent]

MANAGEMENT ARCHITECTURE:
- Management Server: [hostname] R[version]
- Log Server: [hostname(s)]
- Gateways: [count] ([list with SIC status])
- MDS domains: [count or N/A]

RULEBASE LAYER SUMMARY:
- Ordered layers: [count] ([layer names])
- Total rules across layers: [count]
- Accept rules: [n] | Drop rules: [n] | Inline layers: [n]
- Rules with Threat Prevention profiles: [n] / [accept count]
- Rules with zero hits (>90d): [count]
- Disabled rules: [count]

BLADE ACTIVATION:
Per Gateway: [gateway name]
  - Licensed blades: [list]
  - Enabled blades: [list]
  - Gap: [licensed but not enabled]

NAT SUMMARY:
- Manual NAT rules: [count]
- Automatic NAT objects: [count]
- Static NAT entries: [count]
- Conflicting rules identified: [count or none]

IDENTITY AWARENESS:
- Identity sources: [list with status]
- Access roles in policy: [count]
- Coverage gaps: [segments without identity]

FINDINGS:
1. [Severity] [Category] — [Description]
   Layer: [layer name]
   Rule Number: [n]
   Issue: [specific problem]
   Current Config: [what the rule does now]
   Recommendation: [specific remediation]

SIGNATURE CURRENCY:
- IPS: [version] ([age])
- App Control: [version] ([age])
- Anti-Bot: [version] ([age])
- Anti-Virus: [version] ([age])

RECOMMENDATIONS:
- [Prioritized action list by severity]

NEXT AUDIT: [CRITICAL: 30d, HIGH: 90d, clean: 180d]
```

## Troubleshooting

### Large Rulebases Spanning Multiple Layers

Auditing rulebases with hundreds of rules across multiple ordered layers
is impractical via SmartConsole alone. Use the Management API to export
all layers programmatically:
`mgmt_cli show access-rulebase name "<layer>" details-level full --format json -r true`
Iterate over all layers and merge into a single dataset for automated
shadow detection, profile gap analysis, and hit count review.

### Multi-Domain Server (MDS) Audits

In MDS deployments, each domain is an isolated management container. The
auditor must connect to each domain separately (or use the MDS-level API
with domain context). Policy in one domain does not affect another — but
verify that cross-domain traffic paths have consistent policies on both
domain gateways.

### Policy Installation Failures

If a gateway shows "Policy out of date" in SmartConsole, the running policy
may not match the current rulebase. Use `fw stat` on the gateway to see
the installed policy name and timestamp. Compare with SmartConsole to
identify the delta. Audit findings should be based on the installed policy,
not the pending session.

### SecureXL and CoreXL Impact on Inspection

SecureXL accelerates traffic by bypassing full inspection for established
sessions. Some blades (especially IPS and Threat Emulation) require traffic
to pass through the Firewall kernel (Medium Path or Firewall Path), not
the accelerated path. Verify SecureXL template status:
`fwaccel stat` and `fwaccel templates -S`
Templates that match security-sensitive traffic and bypass blade inspection
are a finding.

### ClusterXL and VSX Considerations

In ClusterXL (HA) deployments, verify both members run the same policy
version and software release. In VSX (Virtual System Extension) deployments,
each virtual system has independent policy — audit each VS separately.
Use `vsx stat -v` to list virtual systems.
