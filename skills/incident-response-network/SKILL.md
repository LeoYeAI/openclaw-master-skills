---
name: incident-response-network
description: >-
  Network forensics evidence collection and analysis during security incidents.
  Guides volatile evidence preservation, lateral movement detection via flow
  records and ARP/MAC/CAM table analysis, and read-only containment
  verification across Cisco IOS-XE/NX-OS, Juniper JunOS, and Arista EOS.
  Scoped to network artifacts only — packet captures, flow data
  (NetFlow/sFlow/IPFIX), forwarding tables, routing state, and device logs.
  Not general incident response, endpoint forensics, or malware analysis.
license: Apache-2.0
metadata:
  safety: read-only
  author: network-security-skills-suite
  version: "1.0.0"
  openclaw: '{"emoji":"🚨","safetyTier":"read-only","requires":{"bins":["ssh"],"env":[]},"tags":["incident","forensics","network"],"mcpDependencies":[],"egressEndpoints":[]}'
---

# Network Incident Response — Network Forensics

Network-specific evidence collection and analysis during security incidents.
This skill covers network artifacts only: packet captures, flow records
(NetFlow/sFlow/IPFIX), ARP/MAC/CAM tables, routing table state, and device
syslog events. It does not cover general incident response lifecycle (NIST
800-61), endpoint forensics, malware analysis, or organizational
communication plans.

The procedure follows an event-driven lifecycle shaped around forensic
evidence: preserve volatile data → triage scope → detect lateral movement →
verify containment → reconstruct timeline → document findings. All commands
are read-only. Containment verification confirms that previously applied
controls are effective — it does not execute containment actions.

Commands use `[Cisco]`, `[JunOS]`, or `[EOS]` vendor labels where syntax
diverges. See `references/cli-reference.md` for the full command reference
and `references/forensics-workflow.md` for evidence methodology,
chain-of-custody templates, and timeline reconstruction guidance.

## When to Use

- **Active security incident** requiring network-level evidence collection
  (packet captures, flow analysis, device logs)
- **Post-incident network forensics** — reconstructing what happened on the
  network after a confirmed security event
- **Lateral movement investigation** — tracing attacker movement between
  internal hosts using flow records, ARP/MAC table changes, and routing
  state analysis
- **Unauthorized access investigation** — identifying how an external or
  internal actor reached target systems via network path analysis
- **Data exfiltration analysis** — quantifying outbound data transfers via
  flow record byte counts and packet capture content analysis
- **Containment verification** — confirming (read-only) that ACLs, null
  routes, or VLAN isolation applied by responders are blocking attacker
  traffic effectively

## Prerequisites

- **Device CLI access** — read-only access to network devices in the
  incident scope is sufficient for all evidence collection commands.
  No enable/configure privilege is required.
- **Flow collection infrastructure** — NetFlow, sFlow, or IPFIX collectors
  must be receiving exports from network devices. Verify with flow export
  commands in `references/cli-reference.md`. Without flow data, lateral
  movement analysis (Step 3) is limited to ARP/MAC/syslog correlation.
- **Centralized logging** — device syslog events must be forwarded to a
  SIEM or syslog server. Local device log buffers are small and rotate
  quickly. Missing centralized logs create timeline gaps.
- **NTP synchronization** — all devices must be time-synchronized. Verify
  with `[Cisco]` `show ntp status`, `[JunOS]` `show system ntp`,
  `[EOS]` `show ntp status`. Skewed clocks corrupt timeline correlation.
- **Known-good baseline** — saved copies of routing tables, ARP tables, and
  device configurations from before the incident for comparison. Without
  baselines, anomaly detection relies on general heuristics rather than
  delta analysis.

## Procedure

Follow these six steps in order. Earlier steps capture volatile evidence
before it ages out; later steps analyze and document. Each step references
specific commands from `references/cli-reference.md` and methodology from
`references/forensics-workflow.md`.

### Step 1: Evidence Preservation

Capture volatile network evidence before it ages out or is overwritten.
Follow the volatility ordering from `references/forensics-workflow.md` —
most volatile first.

**1a. ARP / MAC / CAM tables** (highest volatility — minutes to hours):

Collect the current ARP and MAC address tables from every device in the
incident scope. These tables map IP addresses to MAC addresses and MAC
addresses to physical switch ports — essential for identifying which hosts
were connected where.

- **[Cisco]** — `show arp` and `show mac address-table`
- **[JunOS]** — `show arp no-resolve` and `show ethernet-switching table`
- **[EOS]** — `show arp` and `show mac address-table`

Save output to files with timestamps. ARP entries typically age out in
4 hours; CAM entries in 5 minutes. Delay here means losing L2 mapping.

**1b. Active packet captures** (real-time — exists only while traffic flows):

If the incident is active and the investigation requires payload-level
evidence, initiate packet captures on relevant interfaces immediately.

- **[Cisco]** — `monitor capture CAP1 interface <intf> both` then
  `monitor capture CAP1 start` — export with
  `monitor capture CAP1 export flash:evidence.pcap`
- **[JunOS]** — `monitor traffic interface <intf> write-file /var/tmp/capture.pcap`
- **[EOS]** — `bash tcpdump -i <intf> -w /mnt/flash/evidence.pcap -c 10000`

> **Performance note:** On-device packet capture consumes CPU. Monitor
> device health during capture and set packet count or duration limits.

**1c. Routing table snapshots** (hours — convergence overwrites state):

- **[Cisco]** — `show ip route` and `show ip route summary`
- **[JunOS]** — `show route` and `show route summary`
- **[EOS]** — `show ip route` and `show ip route summary`

Also capture routing protocol adjacency state (`show ip ospf neighbor`,
`show ip bgp summary` or vendor equivalents) to document peering status
at the time of collection.

**1d. Flow export verification** (hours to days — collector retention):

Confirm that flow data from the incident time window is available in the
flow collector. Verify export is active and records exist:

- **[Cisco]** — `show flow monitor` and `show flow exporter <name> statistics`
- **[JunOS]** — `show services flow-monitoring version-ipfix template` and
  `show services accounting status`
- **[EOS]** — `show flow tracking` and `show flow tracking counters`

**1e. Device configuration and comprehensive state:**

Save the running configuration and full technical support output for each
device in scope:

- **[Cisco]** — `show tech-support | redirect flash:tech-<hostname>-<date>.txt`
- **[JunOS]** — `request support information | save /var/tmp/tech-<hostname>-<date>.txt`
- **[EOS]** — `show tech-support | redirect flash:tech-<hostname>-<date>.txt`

Compute SHA-256 hashes immediately after saving evidence files (see
`references/forensics-workflow.md` for hash verification commands).

### Step 2: Initial Triage

Determine the scope of the incident — affected devices, time window,
involved IP addresses — using log and flow data collected in Step 1.

**Identify the time window:** Find the earliest indicator (first alert,
first anomalous event) and the latest known malicious activity. Add a
buffer of ±2 hours to account for undetected precursor activity.

**Identify involved IPs:** Extract unique source and destination IP
addresses from alerts, SIEM events, and flow records within the time
window. Classify each as internal, external, or infrastructure.

**Identify affected devices:** Determine which network devices handled
traffic to/from involved IPs. Use routing tables to trace the forwarding
path and identify all transit devices.

**Scope assessment output:** A list of (1) affected time window, (2)
involved IP addresses with classification, (3) affected network devices,
and (4) evidence types available for each device. This scoping drives
the depth of Steps 3–5.

### Step 3: Lateral Movement Detection

Trace internal-to-internal connections that indicate attacker movement
between hosts. Lateral movement leaves evidence in flow records (new
internal connections), ARP/MAC tables (new L2 entries), and syslog
(authentication events, new sessions).

**Flow record analysis:** Query the flow collector for internal-to-internal
connections involving known compromised IPs during the incident time
window. Look for:

- Connections to ports commonly used for lateral movement (SMB/445,
  RDP/3389, SSH/22, WinRM/5985, WMI/135)
- Connections from a compromised host to hosts it has never contacted
  before (new destination analysis)
- High byte-count transfers between internal hosts (staging or exfil prep)
- Sequential connections from one host to many hosts in a short time
  window (scanning behavior)

**ARP/MAC table analysis:** Compare current ARP/MAC tables against
baseline captures. Look for:

- New MAC addresses on access ports (rogue devices)
- MAC address appearing on a different port than baseline (device moved
  or MAC spoofing)
- Multiple IP addresses mapped to a single MAC (IP aliasing, potential
  MITM)

**Syslog correlation:** Review authentication events on network devices
during the incident window. Attacker lateral movement often involves:

- Failed authentication attempts from internal IPs against network
  device management interfaces
- Successful logins from unexpected source IPs
- Configuration view commands from unusual user accounts

### Step 4: Containment Verification (Read-Only)

Verify that containment measures applied by the incident response team
are functioning as intended. This step is strictly read-only — it
confirms effectiveness, it does not apply containment.

**ACL hit count verification:** Confirm that blocking ACLs are matching
the attacker's traffic. Rising hit counters on deny rules confirm the
ACL is intercepting traffic.

- **[Cisco]** — `show access-lists <containment-acl-name>` — check hit
  counters on deny entries
- **[JunOS]** — `show firewall filter <containment-filter>` — check
  term counters for deny actions
- **[EOS]** — `show access-lists <containment-acl-name>` — check
  per-entry match counts

**Routing containment verification:** If null routes or route
modifications were applied for containment, verify they are present and
effective:

- Confirm the null route exists in the routing table (`show ip route
  <attacker-prefix>` should show Null0/discard)
- Verify no more-specific routes bypass the null route
- Check routing protocol advertisements to confirm containment routes
  are not being overridden by dynamic protocols

**Network isolation verification:** If VLAN isolation was applied, verify
that the isolated segment has no unintended paths:

- Check the routing table for routes to/from the isolated VLAN
- Verify trunk port allowed VLAN lists exclude the isolated VLAN
  on uplinks
- Confirm no layer-3 interfaces provide alternative paths

### Step 5: Timeline Reconstruction

Build a unified chronological sequence of network events from all
evidence sources. This timeline is the primary deliverable of network
forensics investigation.

**Source integration:** Merge events from syslog, flow records, routing
changes, and ARP/MAC transitions into a single timeline sorted by UTC
timestamp. Follow the full timeline reconstruction methodology in
`references/forensics-workflow.md`.

**Key timeline elements:**

1. **Anchor events** — high-confidence events that serve as fixed points
   (first alert, interface state changes, BGP/OSPF adjacency changes)
2. **Correlated events** — events linked by shared IP addresses,
   timestamps, or session identifiers across multiple devices
3. **Gaps** — time periods with missing evidence from devices that should
   have been active (document explicitly as uncertainty)
4. **Phase transitions** — points where activity shifts from
   reconnaissance to access, access to lateral movement, lateral
   movement to objective or exfiltration

**Timeline validation:** Cross-reference the reconstructed timeline
against multiple evidence sources. Events confirmed by two or more
independent sources (e.g., firewall deny in syslog + flow record for
same session) are high confidence. Single-source events are medium
confidence.

### Step 6: Post-Incident Documentation

Compile investigation findings into a structured evidence package. This
documentation supports organizational incident response and any
subsequent legal or compliance review.

**Required documentation artifacts:**

- Evidence inventory with chain-of-custody records (use the template
  in `references/forensics-workflow.md`)
- Reconstructed timeline of network events (from Step 5)
- Lateral movement map showing affected hosts and connection paths
  (from Step 3, if lateral movement was detected)
- Containment verification results (from Step 4)
- List of affected network devices with evidence types collected
- Identified gaps in evidence and their impact on conclusions

## Threshold Tables

### Evidence Priority Classification

| Priority | Evidence Type | Condition | Rationale |
|----------|--------------|-----------|-----------|
| **Critical** | Active packet captures | Incident is active, payload evidence required | Live traffic cannot be recovered after the fact |
| **Critical** | ARP/MAC/CAM tables | Any incident within the last 4 hours | Aging timers overwrite entries — shortest evidence lifespan |
| **High** | Flow records | Incident time window within collector retention | Reveals communication patterns and lateral movement paths |
| **High** | Syslog events | Incident time window within log retention | Provides the event narrative — auth, config, state changes |
| **Medium** | Routing table snapshots | Suspected route manipulation or path analysis needed | Shows forwarding state but only captures current point-in-time |
| **Medium** | SNMP trap history | Corroborating physical or threshold events | Supplements syslog but with less detail |
| **Low** | Historical config archives | Baseline comparison or configuration drift analysis | Persistent data — available for later retrieval if needed |

### Containment Verification Criteria

| Check | Expected Result | Failure Indicator |
|-------|----------------|-------------------|
| ACL deny counters | Incrementing on containment rules | Zero or static counters — ACL not matching traffic |
| Null route presence | Attacker prefix routes to Null0/discard | Route missing or overridden by dynamic protocol |
| VLAN isolation | No L3 routes to/from isolated segment | Routes exist, providing bypass path |
| Flow records post-containment | No new flows from/to attacker IPs | Continuing flows indicate containment bypass |

## Decision Trees

### Evidence Collection Priority

```
Incident reported
├── Is the incident currently active?
│   ├── Yes — Active threat
│   │   ├── Is payload-level evidence needed?
│   │   │   ├── Yes → Start packet capture immediately (Step 1b)
│   │   │   └── No → Proceed to ARP/MAC collection (Step 1a)
│   │   └── Simultaneously: collect ARP/MAC tables (Step 1a)
│   │       └── Then: routing snapshots (Step 1c) → flow verification (Step 1d)
│   │
│   └── No — Post-incident investigation
│       ├── How long ago did the incident occur?
│       │   ├── < 4 hours → ARP/MAC tables may still have entries (Step 1a)
│       │   ├── 4–24 hours → ARP tables likely aged out; start with flow data
│       │   └── > 24 hours → Rely on syslog and flow collector retention
│       └── Verify flow data and syslog coverage for incident window (Steps 1d, 1e)
│
├── Has containment been applied?
│   ├── Yes → Add containment verification (Step 4) after triage
│   │   └── Check ACL counters, null routes, VLAN isolation
│   └── No → Skip Step 4, proceed through Steps 1–3, 5–6
│
└── Proceed to initial triage (Step 2)
```

## Report Template

```
NETWORK FORENSICS EVIDENCE SUMMARY
=====================================
Incident Reference:   [ticket/tracking number]
Investigation Period: [start] — [end] (UTC)
Network Scope:        [number] devices across [number] sites
Analyst:              [name/identifier]
Collection Date:      [date evidence collection began]

EVIDENCE INVENTORY:
| # | Device | Evidence Type | File | SHA-256 | Collected At |
|---|--------|--------------|------|---------|-------------|
| 1 | [host] | [type] | [file] | [hash] | [time UTC] |

INCIDENT TIMELINE:
| # | Time (UTC) | Device | Event | Details | Confidence |
|---|-----------|--------|-------|---------|------------|
| 1 | [time] | [host] | [event] | [details] | [H/M/L] |

LATERAL MOVEMENT MAP (if detected):
- Source host → destination host : port (first seen, last seen, byte count)
- [list all observed internal-to-internal attacker paths]

CONTAINMENT VERIFICATION:
| Control | Device | Status | Evidence |
|---------|--------|--------|----------|
| [ACL/route/VLAN] | [host] | [Effective/Bypassed] | [counter values] |

EVIDENCE GAPS:
- [device/time period with missing evidence and impact on conclusions]

RECOMMENDATIONS:
1. [network-level remediation or monitoring improvement]
```

## Troubleshooting

### Insufficient Flow Data Coverage

**Symptom:** Flow records do not exist for devices or time windows
critical to the investigation.

**Diagnosis:** Verify flow export configuration on each device using
commands in `references/cli-reference.md`. Check collector storage —
retention may have expired for the incident time window.

**Workaround:** Substitute with syslog events (lower fidelity but covers
event timestamps) and ARP/MAC table correlation. Document the flow gap
and its impact on lateral movement analysis completeness.

### Time Synchronization Gaps

**Symptom:** Events from different devices appear out of order or
correlation produces implausible sequences.

**Diagnosis:** Check NTP status on each device. Compare timestamps of
events that should be near-simultaneous (e.g., both ends of a link-down
event logged by adjacent devices).

**Workaround:** Calculate clock offset per device and apply correction
to the timeline. Note the correction in evidence documentation. Reduce
correlation confidence for events involving desynchronized devices.

### Evidence Overwritten by Log Rotation

**Symptom:** Syslog events from the incident time window no longer exist
on the device or in the SIEM.

**Diagnosis:** Check device log buffer size (`show logging` to see
buffer capacity and oldest retained message). Check SIEM retention
policy for the relevant index.

**Workaround:** Use flow records or SNMP trap history as alternative
event sources. Note the syslog gap in the timeline with an explicit
confidence reduction for that time period.

### Packet Capture Performance Impact

**Symptom:** Device CPU spikes or forwarding performance degrades during
on-device packet capture.

**Diagnosis:** Monitor CPU utilization during capture. On-device
capture processes packets in software, bypassing hardware forwarding.

**Workaround:** Limit captures with ACL filters (capture only relevant
traffic), set packet count limits (`-c` flag), use span/mirror sessions
to an external capture appliance instead of on-device capture, or
reduce capture duration. If performance impact is unacceptable, stop
capture and rely on flow records for metadata-level analysis.

### Incomplete ARP/MAC Table Recovery

**Symptom:** ARP or MAC address tables are mostly empty — entries have
already aged out by the time evidence collection begins.

**Diagnosis:** Default ARP aging is 4 hours; default CAM aging is
5 minutes. If more than 4 hours have elapsed since the incident,
ARP entries for inactive hosts will be gone.

**Workaround:** Cross-reference DHCP lease logs for IP-to-MAC mappings
during the incident window. Use flow records to identify involved
IP addresses without L2 mapping. Check if any NMS polled ARP/MAC
tables via SNMP during the incident window.
