---
name: cis-benchmark-audit
description: >-
  CIS benchmark compliance assessment for network infrastructure devices.
  Maps device configuration against CIS benchmark controls organized by
  Management Plane, Control Plane, and Data Plane categories across Cisco IOS,
  PAN-OS, JunOS, and Check Point platforms. References control IDs for
  traceability without reproducing copyrighted benchmark content.
license: Apache-2.0
metadata:
  safety: read-only
  author: network-security-skills-suite
  version: "1.0.0"
  openclaw: '{"emoji":"📋","safetyTier":"read-only","requires":{"bins":["ssh"],"env":[]},"tags":["cis","compliance","benchmark"],"mcpDependencies":[],"egressEndpoints":[]}'
---

# CIS Benchmark Compliance Audit

Compliance assessment skill that maps network device configuration against
CIS benchmark controls. Organizes audit checks by Management Plane, Control
Plane, and Data Plane — the three architectural layers CIS uses to structure
network device benchmarks.

Covers the four platforms CIS publishes network device benchmarks for:
Cisco IOS, PAN-OS, JunOS, and Check Point. The operator must obtain the
applicable CIS benchmark document for their specific platform and version —
this skill references CIS control IDs and section categories for traceability
but does not reproduce copyrighted benchmark text, remediation steps, or
rationale (see D026).

Consult `references/control-reference.md` for CIS control ID mappings to
audit areas and `references/cli-reference.md` for per-platform read-only
verification commands.

## When to Use

- Annual or quarterly CIS compliance audit against network infrastructure
- Pre-audit preparation — building evidence collection before formal assessment
- New device commissioning — establishing CIS compliance baseline on day one
- Post-upgrade verification — confirming controls remain in place after OS upgrade
- Regulatory compliance evidence — mapping CIS controls to PCI DSS, HIPAA, or SOX
  technical requirements via CIS crosswalk references
- Merger/acquisition due diligence — assessing acquired network infrastructure
  against organizational CIS compliance posture

## Prerequisites

- Read-only CLI or API access to each target device (SSH, console, or management
  API with read-only administrative role)
- The applicable CIS benchmark document for the target platform and OS version —
  operators must obtain their own licensed copy (e.g., "CIS Cisco IOS 16
  Benchmark v1.1.0"). This skill references control IDs only
- Understanding of the device's role in the network architecture — the device's
  position (edge, core, distribution, management) affects which controls apply
  and their priority
- Awareness of any compensating controls already in place that satisfy CIS
  requirements through alternative mechanisms
- Documentation of any accepted risk exceptions for controls intentionally not
  implemented

## Procedure

Follow this six-step compliance assessment flow. Each step builds on prior
findings. The procedure maps device configuration to CIS benchmark controls
organized by management architecture layer.

### Step 1: Platform Identification and Benchmark Selection

Identify the device platform, OS version, and hardware model. Select the
matching CIS benchmark by ID and version.

**[Cisco]** `show version` — capture IOS/IOS-XE version, hardware model
**[PAN-OS]** `show system info` — capture PAN-OS version, platform model
**[JunOS]** `show version` — capture Junos OS version, hardware model
**[CheckPoint]** `fw ver` and `cpinfo -y all` — capture Gaia OS version, platform

Record the exact benchmark ID that matches your platform version (e.g.,
"CIS Cisco IOS 16 Benchmark v1.1.0", "CIS Palo Alto Firewall 10 Benchmark
v1.0.0"). If no benchmark exists for the exact OS version, use the closest
available and document the version gap.

Determine the CIS profile level to assess against:
- **Level 1:** Essential security controls, broadly applicable
- **Level 2:** Defense-in-depth controls, may reduce functionality

### Step 2: Management Plane Audit

Assess controls that protect device management access and monitoring.
This covers CIS sections typically numbered 1.x and 2.x.

**Local authentication and authorization:**

**[Cisco]** `show running-config | section aaa` — verify AAA is enabled with
TACACS+ or RADIUS, check that local fallback accounts use strong hashing
(`algorithm-type scrypt` or `secret 9`).

**[PAN-OS]** `show config running | match authentication` — verify
authentication profile binds to RADIUS/LDAP/SAML, check password complexity
profile exists.

**[JunOS]** `show configuration system authentication-order` — verify
TACACS+/RADIUS is primary with local fallback, check `show configuration
system login` for account policies.

**[CheckPoint]** `show configuration aaa` — verify RADIUS/TACACS+ integration,
check administrator account password policies.

**SSH and management transport:**
Verify SSH v2 only (no SSHv1 or Telnet), session timeout configured,
management access restricted to specific source addresses or management VLAN.
Check certificate-based authentication where supported.

**Logging and monitoring:**
Verify syslog is configured to a remote server with appropriate severity
levels (informational minimum for security events), SNMP v3 with
authentication and encryption (no v1/v2c with community strings), and
NTP authentication to trusted time sources.

**Login banners:**
Confirm legal notice/warning banners are configured on all management access
methods (console, VTY, web UI).

### Step 3: Control Plane Audit

Assess controls that protect routing and signaling protocols. CIS sections
typically numbered 3.x.

**Routing protocol authentication:**
Verify OSPF, BGP, and IS-IS neighbor authentication is enabled.

**[Cisco]** `show ip ospf interface` — check for authentication type
(MD5 or SHA-256). `show ip bgp neighbors` — verify password is set per
neighbor.

**[PAN-OS]** `show routing protocol ospf area` — verify area authentication.
`show routing protocol bgp peer` — check MD5 authentication.

**[JunOS]** `show ospf interface detail` — verify authentication-type.
`show bgp neighbor` — check authentication-key presence.

**[CheckPoint]** Routing configured via Gaia Clish: `show route ospf` with
`show configuration ospf` for authentication settings.

**Control Plane Protection:**
Verify rate limiting on management-bound traffic to prevent CPU exhaustion
from packet floods targeting the control plane processor.

**[Cisco]** `show policy-map control-plane` — verify CoPP (Control Plane
Policing) is applied with appropriate rate limits.

**[JunOS]** `show firewall filter` — verify loopback/lo0 filter protects
the routing engine with rate-limit policers.

**ARP and DHCP protection:**
Verify Dynamic ARP Inspection (DAI) and DHCP snooping on access-layer
switches to prevent ARP spoofing and rogue DHCP attacks.

### Step 4: Data Plane Audit

Assess controls that protect traffic forwarding. CIS sections typically
numbered 4.x and 5.x.

**Access control lists:**
Verify explicit deny rules with logging at ACL boundaries. Check that
infrastructure ACLs protect device management addresses from data plane
traffic.

**Unicast Reverse Path Forwarding (uRPF):**

**[Cisco]** `show ip interface` — check for `ip verify unicast source
reachable-via` on external-facing interfaces.

**[JunOS]** `show configuration interfaces` — check for `family inet rpf-check`
on upstream interfaces.

Anti-spoofing via uRPF validates source addresses against the routing table,
dropping packets with forged source IPs.

**Storm control and port security:**
Verify broadcast/multicast/unicast storm control thresholds on access ports.
Check 802.1X or MAC-based authentication on edge ports where applicable.

**Encryption:**
Verify management traffic encryption (SSH, HTTPS, SNMPv3). Assess MACsec
for LAN encryption and IPsec for WAN links where required by organizational
policy or CIS Level 2 controls.

### Step 5: Compliance Scoring and Gap Analysis

Tally results per CIS section and per architectural plane.

For each control tested, record:
- **Pass:** Device configuration satisfies the control requirement
- **Fail:** Device configuration does not meet the control requirement
- **Not Applicable:** Control does not apply to this device role or
  deployment model (document justification)

Calculate compliance percentage per plane:
`Compliance % = (Pass / (Pass + Fail)) × 100` (exclude N/A from denominator)

Identify critical gaps — any Level 1 control failure in the Management Plane
is a priority finding because it affects the security of all other controls
(if management access is compromised, all other controls are bypassable).

### Step 6: Priority-Ranked Remediation Plan

Order findings for remediation based on CIS control level and operational
impact.

**Priority 1 — Level 1 Management Plane failures:**
AAA bypass, cleartext management protocols, missing logging. These undermine
all other controls.

**Priority 2 — Level 1 Control/Data Plane failures:**
Unauthenticated routing protocols, missing ACLs, disabled uRPF. These allow
traffic manipulation or spoofing.

**Priority 3 — Level 2 Management Plane items:**
Enhanced encryption, additional monitoring, granular access controls. These
add defense-in-depth.

**Priority 4 — Level 2 Control/Data Plane items:**
CoPP fine-tuning, MACsec deployment, advanced storm control thresholds.
These optimize existing protections.

Group remediation actions by effort:
- **Quick wins:** Configuration commands that can be applied in a maintenance
  window without service impact
- **Planned changes:** Items requiring change management, testing, or
  coordination with other teams
- **Projects:** Items requiring infrastructure changes, new hardware, or
  significant design work

## Threshold Tables

### Compliance Violation Severity

| Severity | CIS Level | Condition | Examples |
|----------|-----------|-----------|----------|
| Critical | Level 1 fail | Management access without AAA or encryption | Telnet enabled, no AAA configuration, SNMP v1/v2c with default community, no remote logging configured |
| High | Level 1 fail | Partial control implementation with gaps | NTP configured but without authentication, SSH enabled but v1 not disabled, login banner missing on some access methods |
| Medium | Level 2 fail | Defense-in-depth control not implemented | CoPP not configured, uRPF not enabled on external interfaces, storm control disabled on access ports |
| Low | Level 2 | Optional hardening not applied | Custom banner text not meeting organizational standard, SNMP informational traps not tuned, optional encryption on internal-only links |

### Compliance Posture Summary

| Score Range | Posture | Guidance |
|-------------|---------|----------|
| 90–100% | Strong | Address remaining gaps in next maintenance cycle |
| 70–89% | Moderate | Prioritize Level 1 failures, schedule Level 2 within quarter |
| 50–69% | Weak | Immediate remediation plan required, escalate to management |
| <50% | Critical | Device may require isolation until baseline controls are applied |

## Decision Trees

### Compliance Remediation Priority

```
CIS control finding: FAIL
├── Is it a Level 1 control?
│   ├── Yes
│   │   ├── Management Plane control?
│   │   │   ├── Yes → PRIORITY 1 (Critical/High)
│   │   │   │   ├── Is device internet-facing?
│   │   │   │   │   ├── Yes → Immediate remediation required
│   │   │   │   │   └── No → Remediate within 7 days
│   │   │   │   └── Is there a compensating control?
│   │   │   │       ├── Yes → Document compensating control, schedule fix
│   │   │   │       └── No → Escalate immediately
│   │   │   └── Control/Data Plane control?
│   │   │       └── PRIORITY 2 (High)
│   │   │           └── Remediate within 30 days
│   │   └── No (Level 2 control)
│   │       ├── Management Plane?
│   │       │   └── PRIORITY 3 (Medium)
│   │       │       └── Schedule within quarter
│   │       └── Control/Data Plane?
│   │           └── PRIORITY 4 (Low/Medium)
│   │               └── Schedule within next audit cycle
│
└── Control marked Not Applicable?
    ├── Justified? (deployment model, device role)
    │   ├── Yes → Document exception with approval
    │   └── No → Re-evaluate, may be a gap
```

### Benchmark Version Selection

```
Identify target device OS version
├── Exact CIS benchmark version available?
│   ├── Yes → Use exact match
│   └── No → Use nearest lower version benchmark
│       ├── Gap > 2 major versions?
│       │   ├── Yes → Flag reduced coverage, request updated benchmark
│       │   └── No → Acceptable, note version delta in report
│       └── New OS features not covered by benchmark?
│           └── Document as out-of-scope for this assessment
```

## Report Template

```
CIS BENCHMARK COMPLIANCE ASSESSMENT
======================================
Device: [hostname]
Platform: [Cisco IOS / PAN-OS / JunOS / Check Point]
OS Version: [version]
Device Role: [edge / core / distribution / access]
Audit Date: [timestamp]
Performed By: [operator/agent]

BENCHMARK REFERENCE:
- Benchmark ID: [e.g., CIS Cisco IOS 16 Benchmark v1.1.0]
- Profile Level Assessed: [Level 1 / Level 1+2]
- Note: Operator must obtain licensed copy for full control descriptions

COMPLIANCE SCORE BY PLANE:
  Management Plane: [n] pass / [n] fail / [n] N/A  ([%] compliant)
  Control Plane:    [n] pass / [n] fail / [n] N/A  ([%] compliant)
  Data Plane:       [n] pass / [n] fail / [n] N/A  ([%] compliant)
  Overall:          [n] pass / [n] fail / [n] N/A  ([%] compliant)

CRITICAL FINDINGS (Level 1 Failures):
1. [CIS Control ID] — [Config area] — [Finding summary]
   Plane: [Management/Control/Data]
   Current State: [what was observed]
   Impact: [operational risk]

HIGH FINDINGS (Level 1 Partial / Level 2 Critical):
1. [CIS Control ID] — [Config area] — [Finding summary]

REMEDIATION PLAN:
Priority 1 (Immediate — Level 1 Management Plane):
  - [Action] — [CIS Control ID] — [Estimated effort]

Priority 2 (30-day — Level 1 Control/Data Plane):
  - [Action] — [CIS Control ID] — [Estimated effort]

Priority 3 (Quarter — Level 2):
  - [Action] — [CIS Control ID] — [Estimated effort]

EXCEPTIONS AND COMPENSATING CONTROLS:
- [CIS Control ID] — [Reason for exception] — [Compensating control]

NEXT ASSESSMENT: [based on posture — Critical: 30d, Weak: 90d, Moderate: 180d, Strong: 365d]
```

## Troubleshooting

### Benchmark Version Mismatch

CIS benchmarks target specific OS versions. When the device runs a version
not covered by any published benchmark, use the nearest available benchmark
and document the gap. New features introduced after the benchmark's target
version may not have corresponding controls — assess these independently.

### Platform-Specific Configuration Locations

The same logical control (e.g., AAA configuration) exists in different
configuration hierarchies per platform. Cisco IOS uses `aaa new-model` in
global config, PAN-OS uses authentication profiles in device settings, JunOS
uses `system authentication-order`, and Check Point uses SmartConsole or
Gaia Clish. The `references/cli-reference.md` file provides the correct
audit command per platform.

### Controls Not Applicable to All Deployment Models

Some CIS controls assume a specific deployment model. For example, DHCP
snooping controls apply to access-layer switches but not to core routers or
firewalls. 802.1X controls apply to wired access ports but not to WAN
interfaces. Document each N/A determination with a clear justification tied
to the device's role in the network architecture.

### Multi-Context and Virtual System Considerations

PAN-OS virtual systems (vsys), Cisco VDCs/VRFs, and JunOS logical systems
create isolated administrative domains within a single physical device.
Each virtual context should be assessed independently — controls in one
context do not automatically apply to others. Inventory all contexts before
beginning the audit with platform-specific enumeration commands.

### Compensating Controls Documentation

When a CIS control cannot be implemented exactly as described but an
equivalent protection exists, document the compensating control with:
what CIS control it addresses, what alternative mechanism is in place,
and why it provides equivalent or better protection. Accepted risk
exceptions require management sign-off with a review date.
