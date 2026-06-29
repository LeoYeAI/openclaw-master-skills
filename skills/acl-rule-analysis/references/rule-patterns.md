# Rule Analysis Patterns — Detection Logic and Algorithms

Detailed definitions of rule analysis patterns with detection algorithms
and platform-specific considerations. This reference supports the analysis
procedure in SKILL.md.

## Shadowed Rule Detection

A rule is **shadowed** when a preceding rule in the evaluation order matches
all traffic that the shadowed rule would match. Because ACLs and firewall
policies use first-match semantics, the shadowed rule never triggers.

### Detection Algorithm

```
for each rule R[i] where i = 2 to N:
    for each preceding rule R[j] where j = 1 to i-1:
        if is_superset(R[j].source, R[i].source) AND
           is_superset(R[j].destination, R[i].destination) AND
           is_superset(R[j].service, R[i].service) AND
           is_superset(R[j].application, R[i].application):  # policy platforms only
            R[i] is shadowed by R[j]
            break  # no need to check further
```

### Superset Evaluation

For IP address fields, superset means the preceding rule's address range
contains the shadowed rule's address range:
- `any` is a superset of all addresses
- `10.0.0.0/8` is a superset of `10.1.0.0/16`
- A host address is never a superset of a subnet (unless the subnet is a /32)

For service/port fields:
- `any` service is a superset of all specific services
- A port range (e.g., 1024-65535) is a superset of any port within that range
- A service group is a superset of any individual service it contains

For application fields (policy platforms only):
- `any` application is a superset of all specific applications
- An application group is a superset of its member applications

### Severity Classification

| Shadow Type | Severity | Security Impact |
|-------------|----------|-----------------|
| Permit shadows deny | Critical | Traffic intended to be blocked is permitted |
| Deny shadows permit | Medium | Legitimate traffic may be blocked unexpectedly |
| Permit shadows permit | Medium | Redundancy — no security impact |
| Deny shadows deny | Low | Redundancy — no security impact |

### Platform-Specific Considerations

- **Cisco IOS/ASA/EOS:** ACLs are strictly ordered by sequence number. Shadow
  analysis is straightforward — compare each ACE against all preceding ACEs.
- **JunOS:** Firewall filter terms are evaluated in order within the filter.
  Each term can have multiple `from` match conditions (AND logic within a
  term). Shadow analysis must evaluate the combined match criteria.
- **PAN-OS:** Security policies have additional dimensions (zones, users,
  applications) beyond source/destination/service. All dimensions must be
  superset for a true shadow. Pre-rules shadow local rules which shadow
  post-rules.
- **FortiGate:** Policies evaluated top-to-bottom by sequence. Address groups
  and service groups must be expanded for accurate comparison.
- **Check Point:** Layered policies (ordered and inline layers) add
  complexity. A rule in an inline layer may be effectively shadowed by a
  preceding rule in the parent ordered layer.

## Redundant Rule Identification

Redundant rules have overlapping match criteria and the same action. They
increase complexity without adding security value and are candidates for
consolidation.

### Detection Approach

```
Group rules by action (permit/deny):
    for each pair (R[i], R[j]) with same action where i < j:
        if is_subset(R[j].match, R[i].match):
            R[j] is redundant — R[i] already covers it
        elif is_subset(R[i].match, R[j].match):
            R[i] is redundant — R[j] covers it (but R[i] matches first)
            # R[i] is still active; R[j] is partially redundant
        elif overlaps(R[i].match, R[j].match):
            Partial redundancy — candidate for merge
```

### Merge Candidates

Rules are merge candidates when:
- Same action (both permit or both deny)
- Same source but adjacent/overlapping destination ranges (or vice versa)
- Same source and destination but adjacent/overlapping port ranges
- Same criteria except one field differs — that field can potentially be
  summarized

**Example:**
```
Rule 10: permit tcp 10.1.1.0/24 → 192.168.1.0/24 eq 443
Rule 20: permit tcp 10.1.2.0/24 → 192.168.1.0/24 eq 443
→ Merge to: permit tcp 10.1.0.0/22 → 192.168.1.0/24 eq 443
  (if 10.1.0.0/22 summarization is acceptable)
```

### Consolidation Risks

- Summarizing addresses may inadvertently permit traffic from unintended
  sources — verify that the summary range does not include hosts that should
  be excluded.
- Merging port ranges may expose additional services — only merge truly
  adjacent ranges.
- After merging, verify the new rule's match behavior with test traffic.

## Overly Permissive Rule Patterns

Rules that grant broader access than intended. These patterns should be
flagged during any rule analysis.

### Critical Patterns (Immediate Action Required)

| Pattern | Platform | Description |
|---------|----------|-------------|
| `permit ip any any` | Cisco/EOS | Allows all IPv4 traffic — no filtering |
| `permit ipv6 any any` | Cisco/EOS | Allows all IPv6 traffic |
| Source any + Dest any + Service any + Action allow | PAN-OS/FortiGate/CheckPoint | Fully open policy rule |
| `then accept` with no `from` clause | JunOS | Firewall filter term matches all traffic |
| Application `any` + Action allow | PAN-OS | Bypasses App-ID identification |

### High-Risk Patterns (Prompt Review Required)

| Pattern | Platform | Description |
|---------|----------|-------------|
| `permit tcp any any eq 22` | Cisco/EOS | Unrestricted SSH access |
| `permit tcp any any eq 3389` | Cisco/EOS | Unrestricted RDP access |
| `permit tcp any any eq 1433` | Cisco/EOS | Unrestricted SQL Server access |
| Source any + specific dest + Action allow | All policy | No source restriction |
| Broad subnet source (≥/8) + Action permit | All | Source scope too wide |
| Service group with 20+ ports | PAN-OS/FortiGate/CheckPoint | Overly broad service definition |

### Evaluation Process

For each overly permissive rule:
1. **Check hit count** — Is the rule actively used?
2. **Review traffic logs** — What actual traffic matches this rule?
3. **Identify narrowing opportunity** — Can source/destination/service be
   restricted to observed traffic patterns?
4. **Check compensating controls** — Is there IPS/IDS, Security Profile,
   or other inspection on this traffic?
5. **Document business justification** if the rule cannot be narrowed

## Unused Rule Detection

Rules with zero hit count over an extended period are candidates for removal.

### Detection Criteria

| Platform | Hit Count Source | Zero-Count Threshold |
|----------|-----------------|---------------------|
| Cisco IOS/ASA | `show access-lists` (matches count) | 30+ days uptime |
| JunOS | `show firewall filter [name]` (counter) | 30+ days, counter must be configured |
| EOS | `show access-lists counters` | 30+ days uptime |
| PAN-OS | `show rule-hit-count` (includes last-hit date) | 30+ days, use last-hit timestamp |
| FortiGate | `diagnose firewall iprope list` | 30+ days uptime |
| Check Point | SmartConsole hit count / `mgmt_cli` | 30+ days, data from SmartConsole |

### False Positive Caveats

Unused rules are not always unnecessary. Before recommending removal:

- **Seasonal traffic:** Some rules serve quarterly, annual, or event-driven
  traffic. Extend the observation window to capture full business cycles.
- **Backup/failover paths:** Rules for backup links or DR paths may have
  zero hits during normal operation but are critical during outages.
- **Recently added rules:** New rules may not have accumulated hits. Check
  the rule creation date against the observation period.
- **Counter resets:** Device reboots reset hit counters on most platforms.
  Verify uptime covers the desired observation window.
- **Directional rules:** An ACL applied inbound may show zero hits if
  traffic enters through a different interface. Verify the ACL is applied
  to the correct interface and direction.

### Risk-Based Classification

| Rule Type | Hit Count | Risk | Action |
|-----------|-----------|------|--------|
| Permit | 0 (30+ days) | High | Remove — unused permit is potential unauthorized path |
| Permit | 0 (7-29 days) | Medium | Flag for extended monitoring |
| Deny | 0 (30+ days) | Low | Remove for cleanup — blocked traffic doesn't exist |
| Deny | 0 (7-29 days) | Info | Monitor — may be protecting against rare threats |

## Rule Ordering Optimization

Rule ordering affects lookup performance on sequential-evaluation platforms
and determines security outcomes when permit/deny rules overlap.

### Performance Optimization

ACL platforms (Cisco IOS, EOS, JunOS firewall filters) evaluate rules
sequentially. Optimal performance places the most frequently matched rules
near the top:

```
Optimization score for rule R at position P:
    score = R.hit_count × (P - 1)
    # Higher score = more wasted comparisons
    # Move high-score rules toward position 1
```

**Constraints on reordering:**
- A permit rule cannot move above a deny rule that matches overlapping
  traffic (security constraint)
- A deny rule cannot move below a permit rule that matches overlapping
  traffic (security constraint)
- Only reorder within "safe zones" — groups of consecutive rules with no
  permit/deny conflicts

### Security-First Ordering

When performance and security conflict, security wins:
1. Most-specific deny rules first (block known-bad traffic early)
2. Specific permit rules next (allow known-good traffic)
3. Broader deny rules (default deny for remaining traffic)
4. Avoid broad permits above specific denies

### Hardware-Accelerated Platforms

PAN-OS, FortiGate, and Check Point use hardware-accelerated policy lookup
(not sequential). Rule ordering on these platforms affects:
- **Security:** First-match still determines outcome — order matters for
  overlapping rules
- **Performance:** Negligible — hardware TCAM/FPGA evaluates all rules in
  parallel

For hardware-accelerated platforms, optimize ordering purely for security
clarity and auditability, not performance.

## Conflict Detection

Conflicts occur when two rules match the same traffic with different actions.
In first-match evaluation, the rule that appears first determines the outcome.

### Conflict Types

| Conflict | Description | Risk |
|----------|-------------|------|
| Permit before deny | Traffic is allowed that a later deny intends to block | Security gap if deny is the intended policy |
| Deny before permit | Traffic is blocked that a later permit intends to allow | Access failure if permit is the intended policy |
| Same action, different scope | Broader rule before specific rule of same action | Redundancy, not a conflict |

### Conflict Resolution

1. Identify all rule pairs where match criteria overlap and actions differ
2. Determine which action is the intended policy for the overlapping traffic
3. Reorder rules so the intended action's rule appears first
4. After reordering, verify no other traffic flows are affected by the change
5. Document the conflict and resolution in the audit report

### Cross-Platform Conflict Patterns

- **Cisco/EOS:** Conflicts are purely positional — first ACE matching wins
- **JunOS:** Terms evaluated in order within a filter; `then reject` vs
  `then accept` in overlapping terms is the common conflict
- **PAN-OS/FortiGate/CheckPoint:** Multi-dimensional matching (zones, apps,
  users) makes conflicts harder to detect — two rules may overlap in
  IP/port but differ in zone or application, which is not a true conflict
