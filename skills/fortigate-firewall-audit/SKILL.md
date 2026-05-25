---
name: fortigate-firewall-audit
description: >-
  FortiOS VDOM segmentation audit with UTM profile binding validation,
  FortiGuard service health assessment, SD-WAN security evaluation, and
  HA cluster posture check. Systematic per-VDOM policy analysis for
  FortiGate appliances and FortiGate-VM instances.
license: Apache-2.0
metadata:
  safety: read-only
  author: network-security-skills-suite
  version: "1.0.0"
  openclaw: '{"emoji":"🛡️","safetyTier":"read-only","requires":{"bins":["ssh"],"env":[]},"tags":["fortinet","fortigate","firewall"],"mcpDependencies":[],"egressEndpoints":[]}'
---

# FortiGate Firewall Security Policy Audit

Policy-audit-driven analysis of FortiGate/FortiOS firewall policies. Unlike
generic firewall checklists that check for open ports and default-deny, this
skill evaluates the FortiOS-specific security architecture: Virtual Domain
(VDOM) segmentation, UTM profile binding on every allow policy, FortiGuard
signature freshness, and SD-WAN SLA-based traffic steering security
implications.

Covers FortiOS 7.x+ on FortiGate hardware appliances and FortiGate-VM virtual
instances. For FortiManager-managed deployments, the audit addresses ADOM
hierarchy and policy package consistency. Reference `references/policy-model.md`
for the full VDOM/UTM inspection chain and `references/cli-reference.md` for
read-only CLI commands.

## When to Use

- Post-change policy review after rule additions or VDOM topology changes
- VDOM segmentation audit verifying inter-VDOM link isolation and per-VDOM policy independence
- UTM profile coverage assessment — finding allow policies without antivirus, IPS, or web-filter inspection
- SD-WAN security evaluation — confirming SLA violations do not steer traffic around security controls
- FortiGuard license and connectivity validation — ensuring signature databases are current
- HA cluster security posture check — verifying firmware parity, config sync, and session-sync settings
- Quarterly or annual compliance audit requiring per-policy justification
- Pre-upgrade baseline before FortiOS major version changes

## Prerequisites

- Read-only administrative access to FortiOS CLI (or `diagnose`-level privilege for runtime state)
- Understanding of the VDOM topology — which VDOMs exist, their function (management, traffic, DMZ), and expected inter-VDOM links
- Knowledge of expected UTM profile assignments per policy category (internet-bound, inter-zone, intrazone)
- For FortiManager-managed environments: access to the ADOM with visibility into policy packages
- Awareness of SD-WAN configuration — SLA targets, member interfaces, and health-check definitions
- Running configuration committed — audit evaluates the active configuration, not pending changes

## Procedure

Follow this audit flow sequentially. Each step builds on prior findings.
The procedure moves from VDOM architecture inventory through per-VDOM
rule-level analysis to UTM coverage, FortiGuard health, SD-WAN security,
and HA posture.

### Step 1: VDOM Architecture Inventory

Collect all VDOMs and their roles.

```
config vdom
edit root
end
get system status
```

On a multi-VDOM system, list all VDOMs:

```
diagnose sys vd list
```

For each VDOM, record: name, type (traffic/management/admin), assigned
interfaces (physical and virtual), inter-VDOM link pairs, and VDOM resource
limits (session count, CPU quota). Identify the management VDOM — this
is where FortiGuard updates, logging, and administrative access are
configured.

Check inter-VDOM links:

```
show system vdom-link
```

Inter-VDOM links function as virtual interfaces connecting two VDOMs.
Traffic crossing a VDOM link is subject to the receiving VDOM's firewall
policies — verify that inter-VDOM traffic is not bypassing inspection.

Verify VDOM resource limits to detect unbounded VDOMs that could starve
other VDOMs during volumetric events:

```
config global
get system vdom-property
```

Flag any VDOM without explicit resource limits in a multi-VDOM deployment.

### Step 2: Firewall Policy Rule-by-Rule Analysis

For each VDOM, retrieve the full policy table:

```
config vdom
edit <vdom-name>
show firewall policy
```

FortiOS evaluates firewall policies top-down by sequence number within each
VDOM. The first matching policy is applied. Evaluate each policy against
these criteria:

- **Overly permissive policies:** Policies with `srcaddr "all"`,
  `dstaddr "all"`, `service "ALL"`, and `action accept` are Critical
  findings — they accept all traffic on all ports with no restriction.
- **Missing UTM profiles:** Allow policies without antivirus, web-filter,
  application-control, or IPS profile binding pass traffic uninspected.
  Check `utm-status`, `av-profile`, `webfilter-profile`,
  `application-list`, and `ips-sensor` on each allow policy.
- **Disabled policies:** Policies with `status disable` still occupy
  sequence numbers and create audit confusion. Flag for cleanup.
- **Schedule-based policies:** Policies with `schedule` other than `always`
  may create time-window security gaps. Verify schedules align with
  intended access windows.
- **Implicit deny:** FortiOS has an implicit deny (policy ID 0) at the
  bottom of each VDOM's policy table. Verify it is logging traffic for
  visibility into denied connections.

Check for unused policies using hit count data:

```
diagnose firewall iprope show 100004 <policy-id>
```

Policies with zero hits over 90+ days are cleanup candidates.

### Step 3: UTM Profile Binding Audit

For each allow policy in every VDOM, verify that UTM inspection profiles
are bound. The goal is zero allow policies without threat inspection.

Check each allow policy for these profile bindings:

- **Antivirus (`av-profile`):** File-based malware scanning. Required on
  all internet-bound and inter-zone policies.
- **Web Filter (`webfilter-profile`):** URL categorization and blocking.
  Required on all policies permitting HTTP/HTTPS.
- **Application Control (`application-list`):** Application identification
  and enforcement. FortiOS equivalent of App-ID.
- **IPS (`ips-sensor`):** Intrusion prevention signatures. Required on
  all allow policies carrying untrusted traffic.
- **Email Filter (`emailfilter-profile`):** Anti-spam for SMTP/IMAP/POP3.
  Required on email-carrying policies.
- **DLP Sensor (`dlp-sensor`):** Data loss prevention pattern matching.
  Required where sensitive data egress risk exists.
- **SSL Inspection (`ssl-ssh-profile`):** Determines whether encrypted
  traffic is decrypted for UTM inspection. Without SSL inspection set to
  `deep-inspection`, AV and IPS see only connection metadata on HTTPS.

Summarize coverage: count allow policies with full UTM binding versus allow
policies with partial or no UTM profiles. Calculate the UTM coverage ratio.

Check the inspection mode per VDOM:

```
config vdom
edit <vdom-name>
get system settings | grep inspection-mode
```

Flow-based mode applies all UTM in a single pass (faster, less thorough).
Proxy-based mode buffers and inspects fully (more thorough, more resource
intensive). The mode affects which UTM features are available and their
efficacy.

### Step 4: FortiGuard Service Validation

FortiGuard provides the signature databases that UTM profiles depend on.
Stale signatures reduce detection efficacy.

```
get system fortiguard-service status
diagnose autoupdate versions
```

Verify the following signature databases are current:

| Database | Maximum Acceptable Age | Check Command |
|----------|----------------------|---------------|
| Antivirus definitions | 24 hours | `diagnose autoupdate versions | grep -A2 'Virus'` |
| IPS signatures | 7 days | `diagnose autoupdate versions | grep -A2 'IPS'` |
| Web filter database | 7 days | `get webfilter status` |
| Application control DB | 7 days | `diagnose autoupdate versions | grep -A2 'App'` |
| Anti-spam database | 7 days | `diagnose autoupdate versions | grep -A2 'Spam'` |

Check FortiGuard connectivity:

```
diagnose debug rating
execute ping service.fortiguard.net
```

If FortiGuard is unreachable, all cloud-dependent features (web filter
rating queries, FortiSandbox cloud, outbreak prevention) operate in
degraded mode using cached data only.

Verify the update schedule:

```
show system autoupdate schedule
```

Best practice is scheduled updates every 1–4 hours for AV and daily for
IPS/App-Control. Manual-only updates are a finding.

### Step 5: SD-WAN SLA and Rule Security

If SD-WAN is configured, evaluate security implications of traffic steering.

```
config vdom
edit <vdom-name>
show system sdwan
```

Review SD-WAN components:

- **SLA targets and health checks:** Examine each health check definition
  (protocol, server, threshold). Verify health-check servers are reachable
  and meaningful for the SLA metric (latency, jitter, packet loss).

```
diagnose sys sdwan health-check
```

- **SD-WAN rules:** Each rule maps traffic to preferred WAN members based
  on SLA status. Review rule priorities and the `tie-break` method.

```
diagnose sys sdwan service
```

- **Fail-open behavior:** When all SLA members fail, SD-WAN rules may fall
  through to standard routing. Determine whether this fallback path still
  traverses security inspection. A fail-open that routes around a security
  VDOM or UTM-inspecting policy is a Critical finding.

- **SD-WAN + firewall policy interaction:** SD-WAN selects the egress
  interface, but firewall policies still control access. Verify that
  firewall policies cover all SD-WAN member interfaces. A policy that
  references a specific interface may not match when SD-WAN steers traffic
  to an alternate member.

### Step 6: HA and Session Sync Audit

Evaluate HA cluster security posture.

```
get system ha status
diagnose sys ha checksum cluster
```

Check the following:

- **HA mode:** Active-passive (recommended for stateful firewalls) vs
  active-active (requires careful session-sync configuration). Record
  the mode and verify it matches design intent.
- **Firmware parity:** Both cluster members must run the same FortiOS
  version. Version mismatch can cause session-sync failures and policy
  inconsistencies.

```
diagnose sys ha checksum cluster
```

Compare configuration checksums between members. Mismatched checksums
indicate configuration drift — a security risk when policies differ
between HA members.

- **Session sync configuration:** Verify which session types are
  synchronized (TCP, UDP, ICMP, expectation sessions). Unsynchronized
  sessions drop during failover.

```
show system ha
```

Check `session-pickup` and `session-pickup-connectionless` settings.

- **HA heartbeat security:** Verify heartbeat interfaces use encryption
  and authentication. Unencrypted heartbeats on shared network segments
  are vulnerable to spoofing.
- **HA management interface:** Verify dedicated management access is
  configured for each cluster member (ha-mgmt-interfaces) to ensure
  both nodes remain independently accessible.

## Threshold Tables

### Policy Rule Severity Classification

| Finding | Severity | Rationale |
|---------|----------|-----------|
| `srcaddr "all"` + `dstaddr "all"` + `service "ALL"` + `action accept` | Critical | Fully open policy — no restriction on source, destination, or service |
| Allow policy without any UTM profile (no AV, IPS, web-filter) | Critical | Traffic passes without threat inspection |
| FortiGuard unreachable — all signatures stale | Critical | UTM profiles active but signatures outdated; detection efficacy severely degraded |
| SD-WAN fail-open bypasses security inspection path | Critical | SLA failure routes traffic around UTM inspection |
| Allow policy with `service "ALL"` (specific src/dst) | High | Permits all services — evaluate whether specific services can be defined |
| FortiGuard signatures >7 days old | High | Detection gap for new threats discovered in the past week |
| VDOM without resource limits in multi-VDOM deployment | High | Unbounded VDOM can starve other VDOMs during volumetric events |
| HA configuration checksum mismatch between members | High | Policy or configuration drift — active and standby may enforce different rules |
| HA firmware version mismatch | High | Session sync and feature parity issues during failover |
| Allow policy with partial UTM (missing IPS or AV) | Medium | Some inspection, but exploit or malware detection gap |
| Disabled policies in production VDOM | Medium | Audit confusion; stale configuration; cleanup recommended |
| SSL inspection not set to deep-inspection on internet-bound policy | Medium | UTM sees only metadata on encrypted traffic — AV/IPS efficacy reduced |
| Schedule-based policy creates off-hours security gap | Medium | Access permitted during window only, but gap during that window is intentional risk |
| Inter-VDOM link without receiving-side policy | Medium | Traffic may traverse VDOM boundary without inspection |
| Policies with zero hits >90 days | Low | Unused rules — cleanup candidates |

### UTM Coverage Maturity

| UTM Coverage Ratio | Maturity | Guidance |
|---------------------|----------|----------|
| >90% allow policies with full UTM | Mature | Maintain; review remaining gaps quarterly |
| 60–90% allow policies with UTM | Developing | Prioritize internet-bound and inter-zone policies for UTM binding |
| <60% allow policies with UTM | Immature | Systematic UTM profile binding campaign needed |

## Decision Trees

### UTM Gap Remediation

```
Allow policy without UTM profiles
├── What traffic does this policy carry?
│   ├── Internet-bound → CRITICAL: Bind full UTM (AV+IPS+WebFilter+AppCtrl+SSL deep-inspection)
│   ├── Inter-VDOM or inter-zone → HIGH: Bind AV+IPS+AppCtrl minimum
│   ├── Intra-zone management → MEDIUM: Bind IPS+AppCtrl; AV optional
│   └── Monitoring/logging only → LOW: Evaluate if allow is needed
│
├── SSL inspection mode?
│   ├── certificate-inspection → UTM limited to metadata on HTTPS
│   │   └── Evaluate switching to deep-inspection for this policy
│   ├── deep-inspection → Full UTM efficacy on encrypted traffic
│   └── none → Only unencrypted traffic inspected
│       └── Add ssl-ssh-profile before UTM profiles
│
└── Inspection mode (VDOM-level)?
    ├── flow-based → Single-pass; good performance, some UTM features limited
    └── proxy-based → Full buffered inspection; verify resource impact
        └── Check CPU/memory: diagnose sys top
```

### VDOM Consolidation Assessment

```
Multi-VDOM deployment evaluation
├── How many VDOMs are configured?
│   ├── >10 VDOMs → Evaluate consolidation; management complexity increases risk
│   ├── 3–10 VDOMs → Typical; verify each serves a distinct security function
│   └── 1–2 VDOMs → Minimal; verify VDOM is needed vs single-VDOM mode
│
├── Do all VDOMs have active policies?
│   ├── Empty or minimal policy VDOMs → Candidates for consolidation or removal
│   └── Active policy VDOMs → Verify traffic segmentation justification
│
├── Are inter-VDOM links necessary?
│   ├── Inter-VDOM traffic inspected by receiving VDOM → Correct architecture
│   └── Inter-VDOM traffic not inspected → Finding: add policies on VDOM links
│
└── Resource contention?
    ├── VDOM resource limits configured → Check utilization vs limits
    └── No limits → Set limits per VDOM to prevent starvation
```

### SD-WAN Fail-Open Risk Evaluation

```
SD-WAN SLA failure scenario
├── All SLA members for a rule fail
│   ├── Rule has dst = security VDOM or UTM-inspecting path?
│   │   ├── Yes → Traffic falls to routing table
│   │   │   ├── Routing table path includes UTM inspection? → Acceptable
│   │   │   └── Routing table path bypasses UTM? → CRITICAL: fail-open gap
│   │   └── No → Standard egress; verify firewall policy still matches
│   │
│   └── SLA health-check server unreachable (false positive)?
│       ├── Single health-check server → HIGH: Add redundant check servers
│       └── Multiple servers, all down → Likely real outage; verify failover
│
└── Partial SLA failure (some members down)
    ├── Traffic steers to remaining members → Verify capacity
    └── Remaining member is a lower-security path → Evaluate risk
```

## Report Template

```
FORTIGATE SECURITY POLICY AUDIT REPORT
========================================
Device: [hostname]
FortiOS Version: [version]
Platform: [FortiGate model / FortiGate-VM]
VDOM Mode: [multi-vdom / split-vdom / disabled]
Management: [standalone / FortiManager ADOM name]
Audit Date: [timestamp]
Performed By: [operator/agent]

VDOM ARCHITECTURE:
- VDOMs configured: [count]
- Management VDOM: [name]
- Inter-VDOM links: [count] ([list pairs])
- VDOMs with resource limits: [n] / [total]

PER-VDOM POLICY SUMMARY:
VDOM: [name]
  - Total firewall policies: [count]
  - Accept policies: [n] | Deny policies: [n]
  - Policies with full UTM profiles: [n] / [accept count]
  - Inspection mode: [flow-based / proxy-based]
  - SSL inspection (deep): [n] policies
  [Repeat for each VDOM]

FORTIGUARD STATUS:
- Connectivity: [connected / unreachable]
- AV signatures: [version] ([age])
- IPS signatures: [version] ([age])
- Web filter DB: [version] ([age])
- Application control DB: [version] ([age])
- Update schedule: [interval]

SD-WAN STATUS:
- SD-WAN enabled: [yes/no]
- SLA health checks: [count] ([all passing / N failing])
- Fail-open risk: [none identified / risk details]

HA STATUS:
- HA mode: [active-passive / active-active / standalone]
- Firmware parity: [matched / mismatched — versions]
- Config checksum: [matched / mismatched]
- Session sync: [enabled / disabled]

FINDINGS:
1. [Severity] [Category] — [Description]
   VDOM: [vdom-name]
   Policy ID: [id] (Seq: [sequence])
   Interfaces: [srcintf] → [dstintf]
   Issue: [specific problem]
   Current Config: [relevant policy fields]
   Recommendation: [specific remediation]

UTM COVERAGE:
- Per-VDOM coverage ratios: [list each VDOM: n/total (%)]
- Policies missing AV: [count]
- Policies missing IPS: [count]
- Policies missing web-filter: [count]
- Policies missing application-control: [count]

RECOMMENDATIONS:
- [Prioritized action list by severity]

NEXT AUDIT: [CRITICAL findings: 30d, HIGH: 90d, clean: 180d]
```

## Troubleshooting

### Large Multi-VDOM Deployments

Auditing more than 10 VDOMs manually is impractical. Export per-VDOM policy
tables via the FortiOS REST API (`/api/v2/cmdb/firewall/policy?vdom=<name>`)
for programmatic analysis. Prioritize VDOMs carrying internet-bound or
inter-zone traffic — management VDOMs are lower risk.

### FortiManager Policy Packages

In FortiManager-managed deployments, audit the installed policy on the
FortiGate (via `show firewall policy`), not just the FortiManager package —
local policies and installation state may differ. Use
`diagnose fortimanager policy-check` to identify discrepancies.

### UTM Performance Impact

Before binding UTM profiles on high-throughput policies, assess headroom:

```
get system performance status
diagnose sys top 2 20
```

FortiGate models have rated throughput for NGFW and Threat Protection
profiles. Ensure traffic volume is within rated capacity. If constrained,
prioritize UTM on internet-bound policies and use flow-based inspection.

### Firmware Upgrade Impact on Policies

FortiOS major upgrades may change UTM profile schema or deprecate features.
Export the policy baseline before upgrading, then post-upgrade verify:
UTM profile bindings preserved, policy sequence intact, SD-WAN rules
migrated, and HA cluster upgraded in sequence (secondary first).

### Split-VDOM Mode vs Multi-VDOM Mode

Split-VDOM provides two VDOMs (root + FG-traffic); full multi-VDOM allows
custom count. Audit whether split-VDOM segmentation is sufficient for
compliance requirements. Changing VDOM mode requires a reboot.
