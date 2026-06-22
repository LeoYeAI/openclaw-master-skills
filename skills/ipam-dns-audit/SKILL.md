---
name: ipam-dns-audit
description: >-
  IP Address Management and DNS record reconciliation audit covering subnet
  utilization analysis, DNS forward/reverse consistency, IP conflict detection,
  and DHCP scope health. Platform-agnostic with references to common IPAM
  implementations. Uses the reconciliation procedure shape — IPAM source
  extraction, live discovery, diff analysis, and remediation reporting.
license: Apache-2.0
metadata:
  safety: read-only
  author: network-security-skills-suite
  version: "1.0.0"
  openclaw: '{"emoji":"📊","safetyTier":"read-only","requires":{"bins":[],"env":[]},"tags":["ipam","dns","ip-conflict"],"mcpDependencies":[],"egressEndpoints":[]}'
---

# IPAM/DNS Reconciliation Audit

IP Address Management (IPAM) and DNS record reconciliation audit for
assessing the accuracy and health of IP address allocations, subnet
utilization, and DNS records. This skill provides a systematic
methodology for comparing IPAM-recorded state against live subnet
activity and DNS resolution results — identifying conflicts,
orphaned records, exhaustion risks, and stale entries that degrade
network reliability.

IPAM systems maintain the authoritative record of how IP address
space *should* be allocated: prefix hierarchies, subnet assignments,
VLAN mappings, static reservations, and DHCP scopes. DNS servers
maintain the mapping between names and addresses. Live network
state — ARP tables, DHCP leases, and actual DNS resolution — reveals
what the network *actually* looks like. The gap between recorded
allocations and live reality is the reconciliation target.

This skill complements source-of-truth-audit (which covers the
full device inventory) by focusing specifically on IP address and
DNS record accuracy. Reference `references/cli-reference.md` for
DNS query tools, ARP/neighbor table commands, DHCP inspection, and
IPAM API patterns. Reference `references/subnet-dns-reference.md`
for RFC allocation guidance, CIDR math, DNS record types, and DHCP
scope planning.

## When to Use

- Subnet exhaustion investigation — determining actual utilization when IPAM shows a prefix nearing capacity
- DNS troubleshooting — validating forward/reverse consistency when name resolution failures occur
- IP conflict diagnosis — tracking duplicate IP assignments causing intermittent connectivity
- Pre-migration planning — auditing IP allocations before data center moves or re-addressing projects
- DHCP scope health check — verifying lease utilization and scope configuration against IPAM records
- Compliance audit — demonstrating IP address accountability for regulatory or internal governance requirements
- Post-change verification — confirming that IP moves, DNS updates, or subnet resizing are reflected in IPAM

## Prerequisites

- **IPAM data access** — read-only access to the IPAM platform via API or export; for NetBox IPAM module: API token with IPAM read permissions; for Infoblox: WAPI credentials with network/record read access; for BlueCat: API credentials with Address Manager read access
- **DNS server access** — ability to query authoritative DNS servers directly (not just recursive resolvers); zone transfer (AXFR) access preferred for comprehensive audits; at minimum, individual record lookups via `dig` or `nslookup` against the authoritative server
- **Network device access** — read-only credentials for switches and routers to collect ARP tables and DHCP relay information; SNMP v2c/v3 community strings or SSH access for CLI commands
- **Scope definition** — target subnets, VRFs, and DNS zones identified before the audit begins; large environments should scope by site, VRF, or /16 aggregate to keep the audit manageable
- **Baseline IPAM expectations** — understand what the IPAM is expected to track: all IPs including DHCP dynamics, or only static allocations? This determines what constitutes a "gap" versus expected behavior

## Procedure

Follow these six steps sequentially. Each step builds on the
previous — IPAM extraction and live discovery feed the diff and
conflict detection, which feeds utilization analysis, culminating
in the reconciliation report.

### Step 1: IPAM Inventory Analysis

Extract authoritative IP allocation data from the IPAM system to
build a complete picture of intended address space usage.

**Prefix Hierarchy Review** — Export the prefix hierarchy for in-scope
VRFs. Verify supernet/subnet containment: every child prefix must be
within its parent aggregate. Identify orphaned prefixes (no parent)
and overlapping definitions (same address space in same VRF). See
`references/cli-reference.md` for IPAM API patterns (NetBox, Infoblox,
BlueCat).

**VLAN-to-Subnet Mapping** — Cross-reference VLAN assignments with
prefix VLAN fields. Flag VLANs with no subnet (unused or misconfigured)
and subnets with no VLAN association (missing metadata).

**IP Reservation Audit** — Categorize IPs by status: static, DHCP pool,
reserved (gateways, HSRP/VRRP VIPs), and available. Verify gateway IPs
are marked reserved. Check for IPs marked "Active" with no device or
interface record — orphaned allocations.

**IPv4 Exhaustion Assessment** — Calculate raw utilization per subnet:
assigned addresses / total usable addresses. Flag prefixes above
threshold (typically 80% warning) and identify remaining contiguous
free blocks.

### Step 2: Live Subnet Discovery

Discover actual IP address usage to compare against IPAM records.
No single source captures all active addresses — multiple collection
methods are required.

**ARP Table Analysis** — Collect ARP tables from Layer 3 gateways
for each in-scope subnet. Each ARP entry represents a recently active
IP. On Cisco IOS: `show ip arp vrf <name>`. On Juniper JunOS:
`show arp interface <l3-interface>`. On Arista EOS: `show ip arp vrf <name>`.

**DHCP Lease Correlation** — Extract active leases from the DHCP
server. Compare against IPAM DHCP scope definitions to ensure
boundaries match. Identify leases outside defined scopes — these
indicate misconfigured or rogue DHCP servers.

**Ping Sweep Validation** — For subnets where ARP data is incomplete
(routed subnets with no local L3 interface), use ICMP sweeps:
`nmap -sn <prefix>` or `fping -g <prefix>`. Non-responding IPs are
not necessarily unused — firewalls may block ICMP.

**Duplicate IP Detection** — Analyze ARP tables for multiple MAC
addresses on the same IP (gratuitous ARP conflicts). Rapidly
alternating MACs for a single IP indicate active conflicts causing
intermittent connectivity.

### Step 3: DNS Record Audit

Audit DNS records for consistency, accuracy, and hygiene. DNS errors
cause application failures often misdiagnosed as network issues.

**Forward/Reverse Consistency** — For each A record, verify a
corresponding PTR record points back to the same hostname. For each
PTR, verify the referenced hostname has a matching A record. Use
`dig +short <hostname> A` and `dig +short -x <ip>` to test pairs.
Inconsistencies break reverse DNS used by mail servers, logging, and
security tools.

**Stale Record Detection** — Cross-reference A records against IPAM
and live ARP tables. A records pointing to IPs that IPAM shows as
available or decommissioned are stale. Records pointing to IPs with
no ARP activity for 90+ days may reference removed hosts.

**CNAME Chain Validation** — Verify CNAME records resolve to valid
targets. Flag chains longer than two hops (add latency and fragility).
Verify no CNAME exists at a zone apex or alongside MX/NS records
(RFC 1034 prohibition).

**Delegation Chain Integrity** — Verify NS records for delegated zones
point to responding servers. Check MX records resolve to A records
(not CNAMEs, per RFC 2181). Validate SOA serial numbers across primary
and secondary servers for replication currency.

**TTL Review** — Audit TTL appropriateness: infrastructure records
(NS, MX, SOA) should use 3600–86400s; frequently changing records
(load balancers, failover) need 60–300s; static host records
typically use 3600s.

### Step 4: Conflict Detection

Identify conflicts that cause operational problems — higher severity
than record hygiene issues from Step 3.

**Overlapping Subnet Definitions** — Compare all prefix entries within
each VRF for overlaps. Two /24 prefixes covering the same range, or a
/24 outside its documented /16 parent, indicate data entry errors. Use
bitwise comparison to detect non-obvious overlaps (e.g., 10.1.0.0/23
and 10.1.1.0/24).

**Duplicate IP Assignments** — Cross-reference IPAM assignments with
live ARP. Two IPAM records for the same IP in the same VRF is a data
conflict. Two MACs for the same IP in ARP is a live conflict. Either
causes packet loss and needs immediate remediation.

**DNS Record Conflicts** — Multiple A records for the same hostname
(without intentional round-robin) indicate misconfiguration. CNAME
records conflicting with other types at the same name violate
standards. PTR records with no matching forward A record are orphaned.

**Orphaned PTR Records** — Reverse zone entries pointing to hostnames
with no forward A record, or to IPs that IPAM shows unallocated. These
accumulate after decommissions when reverse zones are not cleaned.
Audit by iterating PTR records and performing forward lookups.

### Step 5: Utilization Reporting

Compute utilization metrics for capacity planning, exhaustion risk
identification, and overprovisioning detection.

**Subnet Utilization Calculation** — For each prefix:
`utilization = allocated_addresses / usable_addresses × 100%`.
Usable addresses exclude network and broadcast. Compare IPAM-calculated
vs ARP-based utilization (active IPs vs total) — significant divergence
indicates stale IPAM data.

**Threshold Classification** — Apply standard thresholds: >90% critical
(expand immediately), >80% warning (plan within quarter), 50–80%
healthy, <20% oversized (reclaim candidate). DHCP pools tolerate
higher utilization than static ranges.

**DHCP Scope Exhaustion Projection** — Calculate remaining leases per
scope and project time-to-exhaustion based on lease growth rate. Scopes
with <10% free and growing demand need immediate expansion or lease
time reduction.

**IPv6 Adoption Coverage** — For dual-stack environments, measure the
percentage of subnets with corresponding IPv6 prefixes. Track GUA vs
ULA adoption rates. Identify IPv4-only sites as migration gaps.

### Step 6: Reconciliation Report

Compile findings into a structured report with health scores,
conflict inventory, and actionable remediation.

**IPAM Health Scorecard** — Aggregate subnet utilization distribution,
IPAM-vs-live accuracy, prefix hierarchy integrity, and VLAN mapping
completeness into a composite health score.

**DNS Audit Findings** — Summarize forward/reverse consistency rate,
stale record count, CNAME chain issues, and delegation integrity.
Group by zone for targeted remediation.

**Conflict Inventory** — List conflicts ordered by severity: duplicate
IPs first (packet loss), overlapping subnets second (routing ambiguity),
DNS conflicts third (resolution failures). Include affected hosts and
recommended resolution.

**Capacity Planning Recommendations** — Identify subnets needing
expansion within 90 days, recommend oversized subnet reclamation,
suggest DHCP scope adjustments, and flag IPv6 migration gaps.

## Threshold Tables

| Metric | Good | Warning | Critical | Notes |
|--------|------|---------|----------|-------|
| Subnet utilization | <80% | 80–90% | >90% | Per-prefix allocated/usable ratio |
| DHCP scope free | >20% | 10–20% | <10% | Remaining leases in scope |
| Forward/reverse match | ≥95% | 85–95% | <85% | A records with valid PTR |
| Stale A records | <5% | 5–15% | >15% | A records pointing to inactive IPs |
| IPAM vs ARP accuracy | ≥90% | 80–90% | <80% | IPAM entries confirmed by ARP |
| Duplicate IPs detected | 0 | 1–3 | >3 | Per-VRF duplicate IP count |
| Orphaned PTRs | <5% | 5–15% | >15% | PTR records with no forward match |
| VLAN-subnet mapping | ≥95% | 85–95% | <85% | VLANs with correct subnet association |
| IPv6 dual-stack coverage | ≥80% | 50–80% | <50% | Subnets with IPv6 counterparts |

## Decision Trees

```
Audit Scope Selection:
├─ Full enterprise audit?
│  ├─ >1000 subnets? → Scope by site/region, audit iteratively
│  └─ <1000 subnets? → Full-scope audit feasible in single pass
├─ Targeted investigation?
│  ├─ IP conflict report? → Focus on affected VRF/subnet
│  ├─ DNS resolution failures? → Focus on affected zones
│  └─ Capacity planning? → Focus on high-utilization prefixes
└─ Pre-migration audit? → Scope to migrating subnets and DNS zones

IPAM Data Source Selection:
├─ NetBox IPAM module? → Use /api/ipam/ REST endpoints
├─ Infoblox NIOS? → Use WAPI with network_view filtering
├─ BlueCat Address Manager? → Use REST v2 API
├─ Spreadsheet/manual? → Export to structured format first
└─ Multiple IPAM sources? → Reconcile between sources before live comparison

Duplicate IP Response:
├─ ARP table shows conflicting MACs for same IP?
│  ├─ Both MACs belong to known devices? → IP assignment error — reassign one
│  ├─ One MAC unknown? → Potential rogue device — investigate
│  └─ MACs alternating rapidly? → Active conflict — disable one port immediately
├─ IPAM shows same IP assigned to two records?
│  ├─ One record stale? → Archive stale record, confirm active device
│  └─ Both records active? → Investigate which device is using the IP
└─ Different VRFs? → Verify VRF isolation is intact (expected overlap)

Stale DNS Record Disposition:
├─ A record points to IPAM-available IP? → Delete (confirmed decommissioned)
├─ A record points to IP with no ARP activity?
│  ├─ Device exists in IPAM as active? → Verify device is powered on
│  └─ No device record? → Delete after 30-day notification hold
├─ PTR record with no forward match? → Delete (orphaned reverse entry)
└─ CNAME target unresolvable? → Delete or update to valid target
```

## Report Template

```markdown
# IPAM/DNS Reconciliation Report

## Executive Summary
- **IPAM source:** [NetBox IPAM / Infoblox / BlueCat / other]
- **Scope:** [VRFs/sites] — [prefix count] prefixes, [zone count] DNS zones
- **Audit date:** [date]
- **Composite IPAM Health Score:** [score]%

## Utilization Summary
| Tier | Prefix Count | Avg Utilization | At Risk |
|------|-------------|-----------------|---------|
| Critical (>90%) | | | Expand immediately |
| Warning (80–90%) | | | Plan expansion |
| Healthy (20–80%) | | | Monitor |
| Oversized (<20%) | | | Reclaim candidate |

## DNS Audit Summary
| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Forward/reverse consistency | [%] | ≥95% | |
| Stale A records | [count] | <5% | |
| Orphaned PTR records | [count] | <5% | |
| CNAME chain violations | [count] | 0 | |
| Delegation integrity | [pass/fail] | pass | |

## Conflict Inventory

### Critical — Duplicate IP Assignments
| # | IP Address | VRF | MAC 1 | Device 1 | MAC 2 | Device 2 | Action |
|---|-----------|-----|-------|----------|-------|----------|--------|

### High — Overlapping Subnets
| # | Prefix A | Prefix B | VRF | Overlap Range | Action |
|---|----------|----------|-----|---------------|--------|

### Medium — DNS Record Conflicts
| # | Record | Type | Conflict | Action |
|---|--------|------|----------|--------|

## Capacity Planning
| Subnet | Current Util | Growth Rate | Projected Exhaustion | Recommendation |
|--------|-------------|-------------|---------------------|----------------|

## Remediation Priorities
1. [Immediate — Resolve duplicate IP conflicts]
2. [Short-term — Remove stale DNS records]
3. [Medium-term — Expand critical-utilization subnets]
4. [Ongoing — Reclaim oversized subnets for reallocation]
5. [Strategic — Close IPv6 dual-stack gaps]

## Appendix
- IPAM extraction parameters and query details
- DNS audit methodology (zones, servers, tools)
- ARP collection scope and device list
- Subnet math reference for utilization calculations
```

## Troubleshooting

**ARP tables show fewer IPs than expected** — ARP entries expire
(240s on Cisco, 1200s on Juniper). Collect during peak usage for
maximum coverage. Devices communicating only within the same VLAN
(L2 adjacent) may not appear in router ARP — check switch MAC
tables. Ping sweeps supplement ARP for idle subnets.

**DNS zone transfer (AXFR) denied** — Many servers restrict AXFR
to authorized secondaries. Fall back to individual lookups for
known hostnames using `dig @<auth-server> <name> A`. Slower but
avoids AXFR permissions. Check `allow-transfer` (BIND) or zone
transfer settings (Windows DNS).

**DHCP lease data unavailable** — If the DHCP server is not
directly accessible, check IPAM platforms that sync DHCP natively
(Infoblox manages DHCP; NetBox requires external sync).
Alternatively, analyze relay statistics:
`show ip dhcp relay statistics`.

**Subnet utilization mismatch between IPAM and ARP** — IPAM shows
high allocation but ARP shows few active hosts, indicating stale
records. Cross-reference against device inventory (source-of-truth-audit
skill). Clean stale allocations to restore accurate metrics.

**Overlapping subnets not detected** — Overlap detection requires
VRF-scoped comparison. Multi-VRF environments legitimately overlap
(e.g., 10.0.0.0/8 in multiple VRFs). Verify IPAM VRF assignments
are correct — wrong VRF produces false alerts or misses real overlaps.

**IPv6 utilization always ~0%** — IPv6 /64 subnets have 2^64
addresses, making percentage meaningless. Measure by active host
count instead. Focus audits on prefix hierarchy (/48 per site,
/64 per VLAN) rather than per-subnet exhaustion.
