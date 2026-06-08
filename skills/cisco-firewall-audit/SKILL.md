---
name: cisco-firewall-audit
description: >-
  Dual-platform Cisco ASA and Firepower Threat Defense (FTD) firewall audit
  with ACL analysis, NAT policy validation, Modular Policy Framework / Access
  Control Policy evaluation, Snort IPS assessment, VPN configuration review,
  and logging completeness verification.
license: Apache-2.0
metadata:
  safety: read-only
  author: network-security-skills-suite
  version: "1.0.0"
  openclaw: '{"emoji":"🛡️","safetyTier":"read-only","requires":{"bins":["ssh"],"env":[]},"tags":["cisco","asa","ftd","firewall"],"mcpDependencies":[],"egressEndpoints":[]}'
---

# Cisco ASA / FTD Firewall Security Policy Audit

Policy-audit-driven analysis covering both Cisco ASA (classic) and Firepower
Threat Defense (FTD). Unlike generic firewall checklists that check for open
ports and default-deny, this skill evaluates the platform-specific security
architecture: ASA security levels with interface-bound ACLs and Modular
Policy Framework, or FTD Access Control Policy with Snort IPS integration
and Firepower Management Center (FMC) orchestration.

Where platforms diverge, sections use **[ASA]** and **[FTD]** labels.
Shared concepts apply to both platforms unlabeled. Covers ASA 9.x+ and
FTD 6.x+ / 7.x+ managed by FMC or FDM. Reference
`references/policy-model.md` for the ASA security-level model and FTD ACP
evaluation chain, and `references/cli-reference.md` for dual-platform
read-only commands.

## When to Use

- ACL review after rule changes or migration from ASA to FTD
- Annual or quarterly compliance audit requiring per-rule justification
- Post-incident rule assessment to identify how traffic was permitted
- **[ASA]** Security level and interface ACL gap analysis
- **[ASA]** Modular Policy Framework audit — verifying inspection maps
- **[FTD]** Access Control Policy rule ordering and IPS coverage review
- **[FTD]** Snort IPS policy tuning assessment — false positive vs detection gap balance
- NAT policy validation after network re-addressing or migration
- VPN configuration security review — site-to-site and remote access
- Failover / HA posture verification
- Pre-migration baseline before ASA-to-FTD conversion

## Prerequisites

- **[ASA]** Privilege level 5+ (read-only `show` commands) or ASDM read-only access
- **[FTD]** Read-only analyst access to FMC web UI or FMC REST API; Expert shell access for Snort-level diagnostics
- Understanding of the interface topology — which interfaces exist, their security levels (**[ASA]**), and network segment assignments
- Knowledge of expected access policies per interface pair or zone
- For multi-context ASA: access to system and each security context
- **[FTD]** Knowledge of IPS policy baseline — which Snort ruleset and network analysis policy are expected
- Active configuration — audit evaluates the running configuration, not pending changes

## Procedure

Follow this audit flow sequentially. Each step builds on prior findings.
The procedure moves from platform identification through access policy,
NAT, inspection/IPS, VPN, and logging.

### Step 1: Platform Identification and Architecture Inventory

Determine the platform and collect architectural baseline.

```
show version
```

Identify: ASA vs FTD, software version, hardware platform (ASA 5500-X,
Firepower 1000/2100/4100/9300, virtual), licensed features.

**[ASA]** Inventory interfaces, security levels, and context mode:

```
show interface ip brief
show nameif
show mode
```

Security levels (0–100) determine implicit traffic flow: traffic from a
higher security level to a lower is permitted by default (unless ACLs
override); lower-to-higher is denied by default. Record each interface
name, security level, and IP address.

For multi-context ASA:

```
show context
changeto context <name>
show interface ip brief
```

**[FTD]** Identify management model and registered devices:

```
show managers
```

FTD managed by FMC: policy is pushed from FMC — audit via FMC UI/API.
FTD managed by FDM (local): policy configured on-device — audit via
FDM web UI or REST API.

Check failover/HA status on both platforms:

```
show failover
show failover state
```

Record active/standby status, failover interface, and last failover time.

### Step 2: Access Policy Analysis

**[ASA]** ACL-based access control:

```
show access-list
show running-config access-list
show running-config access-group
```

ASA uses interface-bound ACLs. Each ACL is applied inbound or outbound on
an interface via `access-group`. Evaluate:

- **ACL evaluation order:** Top-down within each ACL. First matching ACE
  (Access Control Entry) is applied. Implicit deny at the bottom.
- **Global ACL:** If configured, applies to all interfaces. Interface ACLs
  are evaluated before the global ACL.
- **Overly permissive ACEs:** `permit ip any any` or `permit tcp any any`
  entries are Critical findings — they permit all traffic of that protocol.
- **Unused ACEs:** ACEs with zero hit counts (check `show access-list`
  output for `hitcnt=0`) over 90+ days are cleanup candidates.
- **EtherType ACLs:** Used on transparent firewall interfaces. Review for
  overly broad EtherType permits.

```
show access-list <acl-name> brief
```

**[FTD]** Access Control Policy (ACP):

Access the ACP via FMC UI or REST API. The ACP evaluates traffic through
a defined chain (see `references/policy-model.md`). Evaluate:

- **Prefilter policy:** Hardware-level rules that bypass Snort. Overly
  broad prefilter Trust rules skip all inspection.
- **SSL policy:** Determines which TLS flows are decrypted for inspection.
- **Access Control rules:** Top-down evaluation. Actions: Allow (with or
  without IPS), Trust (bypass Snort), Block, Monitor.
  - Rules with Action=Allow and no Intrusion Policy pass traffic without
    IPS inspection.
  - Rules with Action=Trust bypass all further inspection including IPS
    and file/malware — use only for verified trusted flows.
- **Default action:** Applied when no rule matches. Should be Block with
  logging, not Allow.
- **Intrusion Policy binding:** Each Allow rule can bind an Intrusion
  Policy (Snort ruleset). Rules without one pass traffic uninspected.

```
system support diagnostic-cli
show access-control-config
```

### Step 3: NAT Policy Audit

**[ASA]** NAT order of operations:

```
show nat
show nat detail
show running-config nat
show xlate
```

ASA NAT evaluates in three sections:

- **Section 1 (Manual NAT / Twice NAT):** Explicit rules, top-down. Highest
  priority. Used for fine-grained control.
- **Section 2 (Auto NAT / Object NAT):** Per-object NAT definitions.
  Evaluated after Section 1. Ordering: static rules first, then dynamic.
- **Section 3 (Manual NAT after-auto):** Low-priority manual rules evaluated
  after auto NAT. Used for catch-all translations.

Check for NAT rule conflicts — a Section 1 rule that matches the same traffic
as a Section 2 object NAT always wins. Verify that static NAT entries for
published servers have corresponding ACL entries restricting access.

**[FTD]** NAT rules in FMC:

FTD NAT follows the same three-section model as ASA but is configured via
FMC. Review NAT rules in the FMC NAT policy. Verify:

- Manual NAT rules take precedence over auto NAT
- NAT rules align with ACP rules — ensure translated addresses match ACP
  source/destination references
- No unnecessary identity NAT rules consuming processing

Cross-reference NAT entries with access policy on both platforms — static NAT
that exposes internal servers must have restrictive access rules.

### Step 4: Inspection and IPS Assessment

**[ASA]** Modular Policy Framework (MPF):

```
show running-config class-map
show running-config policy-map
show running-config service-policy
show service-policy
```

ASA inspection uses MPF: class-maps define traffic → policy-maps bind
inspections → service-policies apply to interfaces. Evaluate:

- **Default inspection:** ASA enables inspection for common protocols
  (HTTP, DNS, FTP, etc.) via the `global_policy`. Verify the global
  policy is applied (`service-policy global_policy global`).
- **Custom inspections:** Additional class-maps/policy-maps for specific
  traffic patterns. Verify they are applied to correct interfaces.
- **Missing inspections:** Traffic not matching any class-map in the
  service-policy receives no application-layer inspection — only ACL
  enforcement.
- **Connection limits:** MPF can set connection limits and timeouts.
  Review for overly permissive or missing connection limits on
  internet-facing interfaces.

**[FTD]** Snort IPS and File/Malware policies:

- **Intrusion Policy:** Each ACP Allow rule can reference an Intrusion
  Policy that determines the Snort ruleset. Check that internet-facing
  Allow rules bind an Intrusion Policy.
- **Snort rule sets:** Verify the base policy (Balanced Security and
  Connectivity, Connectivity Over Security, Security Over Connectivity,
  Maximum Detection). For production environments, "Balanced Security
  and Connectivity" is the minimum recommended baseline.
- **Network Analysis Policy (NAP):** Controls protocol decoder settings
  and preprocessor configuration. Misconfigured NAP can cause Snort
  detection gaps.
- **File and Malware Policy:** Detects and blocks malware file transfers.
  Verify binding on rules permitting file-carrying protocols
  (HTTP, SMTP, FTP, SMB).
- **Snort deployment mode:** Inline (can block) vs passive (alert only).
  Production deployments should use inline mode for active prevention.

```
system support diagnostic-cli
show snort statistics
```

### Step 5: VPN and Remote Access Audit

Evaluate VPN configuration security on both platforms.

```
show crypto ipsec sa
show crypto ikev2 sa
show vpn-sessiondb
```

Check:

- **Site-to-site tunnels:** Verify IKE version (IKEv2 preferred over
  IKEv1), encryption algorithms (AES-256-GCM recommended; DES/3DES are
  findings), DH groups (group 14+ recommended; groups 1/2/5 are weak),
  and PFS settings.
- **Crypto maps / tunnel groups:** **[ASA]** Review crypto map entries
  and tunnel group definitions. **[FTD]** Review site-to-site VPN
  topology in FMC.
- **AnyConnect / remote access VPN:** If configured, evaluate:
  - Authentication method (certificate + MFA preferred over password-only)
  - Split tunneling settings (full tunnel recommended for security;
    split tunnel for performance — document the choice)
  - Connection profiles and group policies
  - Client certificate validation settings
  - Banner and session timeout configuration

```
show running-config tunnel-group
show running-config group-policy
```

- **IKE/IPSec SA lifetimes:** Very long lifetimes (>24h IKE, >8h IPSec)
  increase exposure if keys are compromised.

### Step 6: Logging and Monitoring

Evaluate logging configuration and coverage.

**[ASA]** Syslog configuration:

```
show logging
show running-config logging
```

- **Syslog severity:** Verify logging level is set to at least
  "informational" (level 6) for security-relevant events. Level 5
  (notifications) misses connection teardown events. Level 7 (debugging)
  generates excessive volume.
- **Syslog destinations:** Verify syslog server(s) are configured and
  reachable. Check for encrypted syslog (TCP/TLS) for log integrity.
- **SNMP:** If configured, verify community strings are not defaults and
  SNMP v3 is used for authentication/encryption.

**[FTD]** Firepower event logging:

- **Connection events:** In FMC, verify connection logging is enabled on
  ACP rules. "Log at End of Connection" is standard; "Log at Beginning"
  adds volume but provides immediate visibility.
- **Intrusion events:** Automatically logged by Snort when rules trigger.
  Verify events are forwarded to the SIEM.
- **eStreamer:** The Firepower event streaming API for SIEM integration.
  Verify eStreamer client connectivity if in use.
- **Security Analytics / SecureX:** If integrated, verify telemetry
  forwarding is active.

```
show logging
show running-config logging
```

Verify logging covers: denied connections (ACL denials), permitted
connections (for audit trail), VPN events, failover events, and
administrative access.

## Threshold Tables

### Policy Rule Severity Classification

| Finding | Severity | Rationale |
|---------|----------|-----------|
| **[ASA]** `permit ip any any` in interface ACL | Critical | Permits all IP traffic — no access restriction |
| **[FTD]** ACP default action set to Allow | Critical | All unmatched traffic permitted without inspection |
| **[FTD]** Prefilter Trust rule with broad match (any/any) | Critical | Traffic bypasses all Snort inspection |
| **[ASA]** No global service-policy applied | High | No application-layer inspection on any traffic |
| **[FTD]** Allow rule without Intrusion Policy binding | High | Traffic permitted without IPS inspection |
| **[FTD]** SSL policy not decrypting internet-bound traffic | High | Snort inspects only metadata on encrypted flows |
| VPN using DES/3DES or DH group 1/2/5 | High | Weak cryptographic algorithms — vulnerable to attack |
| Static NAT with no restricting ACL | High | Published server accessible on all ports |
| Failover configured but standby not monitoring | High | HA not providing redundancy |
| **[FTD]** Snort in passive mode (production) | High | IPS detects but cannot block threats |
| **[ASA]** ACE with hitcnt=0 for >90 days | Medium | Unused rule — cleanup candidate |
| **[FTD]** File/Malware policy not bound on file-carrying rules | Medium | Malware detection gap on HTTP/SMTP/FTP |
| VPN split tunneling enabled | Medium | Remote user traffic may bypass corporate security controls |
| Logging severity below informational (level 6) | Medium | Security events not captured in logs |
| **[ASA]** Security levels equal with same-security-traffic disabled | Low | Traffic between equal interfaces blocked (may be intentional) |

### IPS / Inspection Maturity

| Coverage | Maturity | Guidance |
|----------|----------|----------|
| **[FTD]** All Allow rules have Intrusion + File/Malware policies | Mature | Maintain; tune Snort rules quarterly |
| **[FTD]** Most Allow rules have Intrusion Policy, some gaps | Developing | Bind Intrusion Policy to remaining Allow rules |
| **[ASA]** Global inspection policy active, custom maps defined | Developing | Evaluate FTD migration for deeper inspection |
| **[ASA]** Default global_policy only, no custom inspections | Immature | Add custom inspection maps for critical protocols |

## Decision Trees

### Access Policy Gap Remediation

```
Overly permissive access rule identified
├── Platform?
│   ├── [ASA] permit ip any any in ACL
│   │   ├── Is ACL applied to an interface?
│   │   │   ├── Yes → CRITICAL: All traffic permitted on that interface
│   │   │   │   └── Analyze connections: show conn [interface]
│   │   │   │       → Replace with specific permit entries
│   │   │   └── No → ACL exists but not applied; verify intent
│   │   └── Global ACL?
│   │       └── Applies to all interfaces → assess scope of exposure
│   │
│   └── [FTD] Allow rule without Intrusion Policy
│       ├── What traffic does the rule match?
│       │   ├── Internet-bound → Bind Intrusion Policy (Balanced minimum)
│       │   │   └── Also bind File/Malware policy
│       │   ├── Inter-zone → Bind Intrusion Policy
│       │   └── Trusted internal → Evaluate risk; bind at minimum
│       │
│       └── Is it a Trust rule?
│           ├── Yes → Bypasses ALL inspection
│           │   └── Verify traffic is truly trusted (e.g., backup)
│           │       └── Consider changing to Allow + Intrusion Policy
│           └── No (Allow) → Add Intrusion Policy binding
│
└── Action = Trust vs Allow?
    ├── Trust → Zero inspection; use sparingly
    └── Allow → Inspection possible; bind policies
```

### NAT Conflict Resolution

```
NAT rule conflict suspected
├── [ASA] Which section is each rule in?
│   ├── Section 1 (Manual) vs Section 2 (Auto) → Section 1 always wins
│   ├── Both in Section 2 → Static evaluates before dynamic; check overlap
│   └── Section 1 vs Section 3 → Section 1 wins; Section 3 may be unreachable
│
├── [FTD] Same three-section model via FMC
│   └── Review NAT policy → identify ordering conflicts
│
└── Verify with packet tracer:
    packet-tracer input <iface> tcp <src> <sport> <dst> <dport>
```

## Report Template

```
CISCO ASA / FTD SECURITY POLICY AUDIT REPORT
===============================================
Device: [hostname]
Platform: [ASA model / FTD model]
Software: [ASA version / FTD version]
Management: [ASDM / FMC hostname / FDM]
Mode: [routed / transparent] [single / multi-context]
Failover: [active-standby / active-active / standalone]
Audit Date: [timestamp]
Performed By: [operator/agent]

INTERFACE / ZONE SUMMARY:
[ASA]: Interfaces: [count] (security levels: [list]) | Multi-context: [yes/no]
[FTD]: Zones: [count] ([list]) | Managed by: [FMC/FDM]

ACCESS POLICY:
[ASA]: ACLs: [count] | ACEs total: [n] | hitcnt=0 (>90d): [n] | Global service-policy: [yes/no]
[FTD]: ACP rules: [n] (Allow:[n] Block:[n] Trust:[n])
       IPS-bound: [n]/[allow] | File/Malware-bound: [n]/[allow] | Default: [Block/Allow]

NAT: Section 1: [n] | Section 2: [n] | Section 3: [n] | Static: [n] | Conflicts: [n/none]

INSPECTION / IPS:
[ASA]: Service-policy: [applied/missing] | Inspected: [protocols]
[FTD]: IPS policy: [name] | Snort: [inline/passive] | SSL decrypt: [n rules/none]

VPN: Tunnels: [n] | IKE: [v1/v2] | Crypto: [algs] | AnyConnect: [yes/no] | Split: [yes/no]

FINDINGS:
1. [Severity] [Category] — [Description]
   Platform: [ASA/FTD] | Rule: [id] | Interface/Zone: [name]
   Issue: [problem] → Recommendation: [remediation]

RECOMMENDATIONS: [Prioritized by severity]
NEXT AUDIT: [CRITICAL: 30d, HIGH: 90d, clean: 180d]
```

## Troubleshooting

### ASA-to-FTD Migration Assessment

When evaluating an ASA for migration to FTD, document: ACL count, NAT rules,
MPF inspections, VPN configurations (crypto maps don't migrate directly),
and multi-context usage (FTD does not support multi-context). The Cisco
Firepower Migration Tool provides a baseline but audit the migrated policy
for accuracy — automated migration often produces suboptimal rule ordering.

### Multi-Context ASA Audits

Each security context is an independent firewall with its own interfaces,
ACLs, NAT, and routing. Audit each context separately via
`changeto context <name>`. Use `show context` in the system context to
list all contexts and `show resource allocation` for per-context limits.

### Large ACLs (>1000 ACEs)

Export the configuration (`show running-config access-list`) and parse
programmatically. Prioritize by hit count — high-hit-count ACEs carry
the most traffic. Zero-hit-count ACEs over 90 days are removal candidates.

### FTD Diagnostic CLI

FTD runs Snort on top of an ASA-derived data plane. Use
`system support diagnostic-cli` for ASA-style `show` commands. The
canonical policy source is FMC — the diagnostic CLI shows deployed results.

### Packet Tracer for Policy Verification

Both platforms support packet tracer for simulating traffic:

```
packet-tracer input <interface> tcp <src-ip> <src-port> <dst-ip> <dst-port>
```

Shows each processing phase: ACL/ACP evaluation, NAT translation,
inspection, routing, and egress. Use to verify audit findings.
