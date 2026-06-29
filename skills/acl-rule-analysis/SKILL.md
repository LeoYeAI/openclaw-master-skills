---
name: acl-rule-analysis
description: >-
  Vendor-agnostic ACL and firewall rule analysis with shadowed rule detection,
  overly permissive rule identification, unused rule discovery, redundant rule
  flagging, and rule ordering optimization. Covers ACLs (Cisco/JunOS/EOS) and
  firewall policies (PAN-OS/FortiGate/CheckPoint).
license: Apache-2.0
metadata:
  safety: read-only
  author: network-security-skills-suite
  version: "1.0.0"
  openclaw: '{"emoji":"📋","safetyTier":"read-only","requires":{"bins":["ssh"],"env":[]},"tags":["acl","firewall","rules"],"mcpDependencies":[],"egressEndpoints":[]}'
---

# ACL and Firewall Rule Analysis

Vendor-agnostic rule analysis for access control lists and firewall policies.
Unlike vendor-specific firewall audit skills that evaluate platform features
(App-ID, Security Profile Groups, zone protection), this skill focuses on
universal rule patterns that apply across all platforms: shadowed rules,
redundant rules, overly permissive rules, and unused rules.

Covers ACL-based platforms (Cisco IOS/IOS-XE/ASA, Juniper JunOS, Arista EOS)
and policy-based firewalls (Palo Alto PAN-OS, Fortinet FortiGate, Check Point).
The analysis algorithms are vendor-agnostic — only the rule retrieval commands
differ by platform.

Commands use inline labels **[Cisco]**, **[JunOS]**, **[EOS]**, **[PAN-OS]**,
**[FortiGate]**, **[CheckPoint]** where syntax diverges. Unlabeled statements
apply universally. See `references/cli-reference.md` for full command tables
and `references/rule-patterns.md` for detection algorithm details.

## When to Use

- Post-migration rule cleanup after converting from one platform to another
- Periodic rulebase hygiene to remove accumulated technical debt
- Compliance preparation requiring rule-level justification and minimal privilege
- Incident investigation — determining whether a rule permitted malicious traffic
- Change validation after rulebase modifications to confirm no shadowed rules
- Capacity optimization — reducing rule count to improve lookup performance
- Merger/acquisition integration — consolidating overlapping rulebases

## Prerequisites

- Read-only access to the target device via SSH, console, or API
- Rulebase with hit counters enabled (most platforms enable by default)
- For unused rule detection: hit count data accumulated over an extended period
  (30+ days minimum, 90 days recommended for seasonal traffic patterns)
- Knowledge of intended security policy — which traffic should be permitted
  and which should be denied between network segments
- Understanding of implicit deny behavior for the platform (varies — see
  Troubleshooting)

## Procedure

Follow this analysis flow sequentially. Each step builds on prior findings.
The procedure moves from data collection through pattern detection to
consolidated recommendations.

### Step 1: Collect Rulebase

Retrieve the full ACL or firewall policy from the target device.

**[Cisco]** IOS/IOS-XE:
```
show ip access-lists
show access-lists
```

**[Cisco]** ASA:
```
show access-list
show running-config access-list
```

**[JunOS]**
```
show configuration firewall family inet filter
show firewall filter
```

**[EOS]**
```
show ip access-lists
show access-lists counters
```

**[PAN-OS]**
```
show running security-policy
```

**[FortiGate]**
```
get firewall policy
```

**[CheckPoint]** SmartConsole CLI or Expert mode:
```
fw stat -l
```

Record each rule: sequence number/name, match criteria (source, destination,
protocol, port/service), action (permit/deny/drop/reject), and hit count.
Normalize the data into a common format for analysis.

### Step 2: Identify Shadowed Rules

A rule is **shadowed** when a preceding rule matches all traffic that the
shadowed rule would match. The shadowed rule never triggers because the
earlier rule always matches first.

Detection algorithm:
1. For each rule R at position N, examine all rules at positions 1 through N-1.
2. If any preceding rule P has match criteria that is a superset of R's
   criteria and the same or broader action scope, then R is shadowed by P.
3. A superset means P's source contains R's source, P's destination contains
   R's destination, and P's service/port contains R's service/port.

**Critical case:** A permit rule shadowing a deny rule means traffic intended
to be blocked is actually permitted. This is a security gap — flag as Critical.

**Benign case:** A deny rule shadowing another deny rule is a redundancy issue,
not a security gap — flag as Medium.

Verify suspected shadows by checking hit counts: a truly shadowed rule has
zero hits despite the traffic pattern existing in the network.

### Step 3: Detect Overly Permissive Rules

Identify rules with excessively broad match criteria that violate least
privilege. Risky patterns by platform:

**ACL platforms (Cisco, JunOS, EOS):**
- `permit ip any any` — allows all IPv4 traffic, bypasses all filtering
- `permit ip any <broad-subnet>` where subnet is /8 or larger
- `permit tcp any any eq <high-risk-port>` — unrestricted source to
  sensitive service (e.g., SSH, RDP, SQL)

**Policy platforms (PAN-OS, FortiGate, CheckPoint):**
- Source `any` + Destination `any` + Action `allow`
- Application/service set to `any` or `all`
- Broad service groups containing dozens of ports

For each overly permissive rule found, check its hit count and traffic logs
to determine actual usage patterns. Many "any/any" rules exist as legacy
migration artifacts that can be narrowed to observed traffic.

### Step 4: Find Unused Rules

Unused rules are those with zero hit count over an extended observation
period.

**[Cisco]** Check hit counts inline with `show access-lists` output.

**[JunOS]** `show firewall filter <name> counter` — per-term counters.

**[EOS]** `show access-lists counters` — per-entry match counts.

**[PAN-OS]** `show rule-hit-count vsys vsys1 security rules all`

**[FortiGate]** `diagnose firewall iprope list` — per-policy packet/byte counts.

**[CheckPoint]** SmartConsole → Policy → hit count column, or `cpstat fw -f policy`

**Caveats for unused rule detection:**
- Hit counters reset on device reboot — verify uptime before concluding
  a rule is unused
- Seasonal traffic (quarterly reports, annual processes) may not appear in
  30-day windows — extend observation to 90+ days when possible
- Backup/failover paths only activate during outages — low hit count does
  not mean the rule is unnecessary
- Unused deny rules are low-risk findings; unused permit rules waste rulebase
  space and may indicate abandoned access that should be revoked

### Step 5: Identify Redundant Rules

Redundant rules have overlapping match criteria and the same action. They
increase rulebase complexity without adding security value.

Detection approach:
1. Group rules by action (permit/deny).
2. Within each group, compare pairs for overlapping source, destination, and
   service criteria.
3. If rule A's match criteria is a subset of rule B's and both have the same
   action, rule A is redundant (B already covers it).
4. If two rules have identical match criteria and the same action, one is a
   direct duplicate.

Merge candidates: rules with adjacent or overlapping source/destination
ranges and the same action can often be consolidated into a single rule with
a summarized address range.

### Step 6: Rule Ordering Optimization

Rule ordering affects both security and performance.

**Performance optimization:** Place highest-hit-count rules near the top.
ACL platforms evaluate rules sequentially — a rule matching 80% of traffic at
position 50 forces 49 unnecessary comparisons per packet.

**Security optimization:** Place most-specific deny rules before broader
permit rules to ensure explicit blocks take precedence.

**Conflict analysis:** When a permit rule and a deny rule match the same
traffic, the first-match rule determines the outcome. Identify all
permit/deny conflicts and verify the intended rule wins by position.

Review current ordering:
1. Sort rules by hit count (descending).
2. Compare current position against hit-count-optimal position.
3. Identify rules where reordering would improve performance without
   changing security posture.
4. Flag any reordering that would change effective policy (a permit moving
   above a deny or vice versa) — these require explicit approval.

### Step 7: Generate Consolidated Recommendations

Compile findings from Steps 2–6 into a prioritized remediation list.

Prioritization order:
1. **Critical:** Shadowed deny rules (security gap) and any/any permits
2. **High:** Overly permissive rules with active traffic, unused permit rules
3. **Medium:** Redundant rules, suboptimal ordering, unused deny rules
4. **Low:** Cosmetic issues (naming, comments, organization)

For each finding, document: the rule identifier, the finding category, the
specific risk, and the recommended action (remove, narrow, reorder, merge).

## Threshold Tables

### Rule Risk Severity Classification

| Finding | Severity | Rationale |
|---------|----------|-----------|
| Permit rule shadowing a deny rule | Critical | Traffic intended to be blocked is permitted |
| `permit ip any any` / any-any-allow | Critical | No filtering — all traffic passes |
| Broad subnet permit (source or dest ≥/8) | High | Overly wide scope; likely exceeds intent |
| Unused permit rule (0 hits, 30+ days) | High | Abandoned access — potential unauthorized path |
| Permit with `any` source to sensitive service | High | Unrestricted access to high-risk ports |
| Redundant rules (same action, overlapping match) | Medium | Complexity without security value |
| Suboptimal rule ordering (high-hit rule low in list) | Medium | Performance impact on sequential evaluation |
| Shadowed deny by another deny | Medium | Redundancy, not a security gap |
| Unused deny rule (0 hits, 30+ days) | Low | Minimal risk; cleanup recommended |
| Missing rule comments/descriptions | Low | Maintainability concern |

### Hit Count Staleness Thresholds

| Observation Period | Confidence | Action |
|-------------------|------------|--------|
| < 7 days | Very Low | Insufficient data — do not remove rules based on hit count |
| 7–29 days | Low | Flag for review; extend observation period |
| 30–89 days | Moderate | Reasonable basis for unused rule identification |
| 90+ days | High | Strong evidence for rule removal or narrowing |
| 180+ days | Very High | Recommend removal with change control documentation |

## Decision Trees

### Remediation Priority

```
Found a flagged rule
├── Is the rule overly permissive (any/any)?
│   ├── Yes
│   │   ├── Is it actively used (hit count > 0)?
│   │   │   ├── Yes → Analyze traffic logs to narrow match criteria
│   │   │   │   ├── Can it be narrowed to specific IPs/services?
│   │   │   │   │   ├── Yes → Create replacement rules, test, then remove original
│   │   │   │   │   └── No → Document business justification, add compensating controls
│   │   │   │   └── Is there a Security Profile/IPS covering this rule?
│   │   │   │       ├── Yes → Lower priority, but still narrow when feasible
│   │   │   │       └── No → High priority — no inspection on broad permit
│   │   │   └── No (zero hits) → Schedule removal with change control
│   │   └── Severity: Critical
│   └── No
│       ├── Is the rule shadowed?
│       │   ├── Shadowed deny (by a permit) → Critical — security gap
│       │   ├── Shadowed permit (by another permit) → Medium — remove redundancy
│       │   └── Shadowed deny (by another deny) → Low — remove redundancy
│       ├── Is the rule unused?
│       │   ├── Unused permit → High — revoke abandoned access
│       │   └── Unused deny → Low — cleanup at convenience
│       └── Is the rule redundant?
│           └── Merge with covering rule → Medium
```

### Rule Reordering Safety Check

```
Proposed rule reorder
├── Does the reorder change which rule matches any traffic flow?
│   ├── Yes → STOP — this is a policy change, not just optimization
│   │   ├── Would a deny move below a permit for the same traffic?
│   │   │   ├── Yes → REJECT — security degradation
│   │   │   └── No → Evaluate as an intentional policy change
│   │   └── Submit for change control review
│   └── No → Safe to reorder for performance
│       ├── Validate with test traffic or policy simulation
│       └── Implement during maintenance window
```

## Report Template

```markdown
# ACL / Firewall Rule Analysis Report

## Executive Summary
- **Device:** [hostname]
- **Platform:** [Cisco IOS / ASA / JunOS / EOS / PAN-OS / FortiGate / CheckPoint]
- **Rulebase Size:** [total rules]
- **Analysis Date:** [timestamp]
- **Performed By:** [operator/agent]
- **Observation Period for Hit Counts:** [start date] to [end date] ([N] days)

**Summary:** [N] findings across [rules examined] rules. [critical count]
Critical, [high count] High, [medium count] Medium, [low count] Low.

## Shadowed Rules
| Rule # | Rule Name | Shadowed By | Match Overlap | Severity | Action |
|--------|-----------|-------------|---------------|----------|--------|
| [seq]  | [name]    | Rule [seq]  | [description] | [sev]   | Remove / Reorder |

## Overly Permissive Rules
| Rule # | Rule Name | Source | Destination | Service | Hit Count | Severity |
|--------|-----------|--------|-------------|---------|-----------|----------|
| [seq]  | [name]    | [src]  | [dst]       | [svc]   | [count]   | [sev]    |

**Recommendation:** [Narrow to observed traffic / Add compensating controls]

## Unused Rules
| Rule # | Rule Name | Action | Last Hit | Days Observed | Severity |
|--------|-----------|--------|----------|---------------|----------|
| [seq]  | [name]    | [act]  | [date]   | [days]        | [sev]    |

**Recommendation:** [Remove with change control / Extend observation period]

## Redundant Rules
| Rule # | Rule Name | Redundant With | Overlap Type | Recommendation |
|--------|-----------|----------------|--------------|----------------|
| [seq]  | [name]    | Rule [seq]     | [type]       | Merge / Remove |

## Ordering Recommendations
| Current Position | Rule # | Hit Count | Optimal Position | Impact |
|-----------------|--------|-----------|------------------|--------|
| [pos]           | [seq]  | [count]   | [new pos]        | [desc] |

## Prioritized Remediation Plan
1. [Critical] [Finding description] — [Specific action]
2. [High] [Finding description] — [Specific action]
3. [Medium] [Finding description] — [Specific action]

## Next Review
- **Critical findings present:** Re-audit in 30 days after remediation
- **High findings only:** Re-audit in 90 days
- **Medium/Low only:** Re-audit in 180 days
```

## Troubleshooting

### Hit Counters Reset After Reboot

Most platforms reset ACL/policy hit counters on reboot. Before concluding
a rule is unused, verify device uptime:
**[Cisco]** `show version | include uptime`,
**[JunOS]** `show system uptime`,
**[EOS]** `show uptime`,
**[PAN-OS]** `show system info | match uptime`,
**[FortiGate]** `get system performance status`,
**[CheckPoint]** `cpstat os -f ifconfig`.
If uptime is less than the desired observation period, hit count data is
incomplete.

### ACL vs Firewall Policy Semantic Differences

ACL-based platforms (Cisco IOS, EOS) evaluate rules top-to-bottom with
first-match semantics. Firewall policy platforms (PAN-OS, FortiGate,
CheckPoint) also use first-match but have additional dimensions (zones,
applications, user identity) that affect matching. Shadowed rule detection
must account for all match dimensions on policy platforms, not just
source/destination/port.

### Implicit Deny Handling Varies by Platform

**[Cisco]** ACLs have an implicit `deny ip any any` at the end (not shown
in the ACL output). **[JunOS]** Firewall filters have an implicit discard
at the end of each term list. **[EOS]** Follows Cisco convention with
implicit deny. **[PAN-OS]** Has configurable interzone-default and
intrazone-default rules (deny and allow respectively). **[FortiGate]**
Implicit deny at end of policy list. **[CheckPoint]** Implicit drop rule
at end of policy (configurable in SmartConsole).

Account for implicit deny when analyzing rule coverage — the absence of an
explicit deny at the bottom is intentional on most platforms.

### Large Rulebases (500+ Rules)

Manual analysis of large rulebases is impractical. Export the rulebase
programmatically for automated analysis:
**[Cisco]** Parse `show access-lists` output.
**[PAN-OS]** Use XML API to export the full policy as structured data.
**[FortiGate]** Use REST API (`/api/v2/cmdb/firewall/policy`).
**[CheckPoint]** Use Management API (`mgmt_cli show access-rulebase`).
Prioritize analysis by hit count — start with the highest-traffic rules
and work down.

### False Positives in Shadowed Rule Detection

Object groups, address groups, and nested service groups can create false
positive shadow detections. When rule A uses an address group and rule B
uses individual addresses that are members of that group, automated tools
may report B as shadowed. Expand all groups to their member objects before
running shadow comparisons.
