# Network Forensics Workflow

Evidence collection methodology, chain-of-custody documentation, artifact
classification, and timeline reconstruction for network-based incident
response. This reference supports the main skill procedure by providing
detailed methodology that would exceed the SKILL.md word budget.

## Evidence Volatility Ordering

Collect evidence in order of volatility — most volatile data disappears
first. This ordering determines the sequence in Step 1 (Evidence
Preservation) of the main procedure.

| Priority | Evidence Type | Volatility | Typical Lifespan | Rationale |
|----------|--------------|------------|------------------|-----------|
| 1 | ARP / MAC / CAM tables | Very High | Minutes to hours (aging timers) | ARP entries age out in 4 hours (default); CAM entries in 5 minutes. Overwritten continuously. |
| 2 | Active packet captures | Very High | Real-time only | Live traffic exists only while flowing. Must capture during the incident window or it is lost forever. |
| 3 | Routing table state | High | Hours (convergence events) | Route changes overwrite previous state. OSPF/BGP convergence can alter tables within seconds of a topology change. |
| 4 | Flow records (NetFlow/sFlow/IPFIX) | Medium | Hours to days (collector retention) | Collector retention varies — 24 hours to 30 days depending on infrastructure. Export gaps are permanent. |
| 5 | Device running configuration | Low | Until next change | Running config persists until modified. Changes overwrite previous state without version history unless archival is configured. |
| 6 | Syslog messages | Low | Days to months (server retention) | Centralized syslog servers retain messages per policy. Local device buffers are small and rotate quickly. |
| 7 | SNMP trap history | Low | Days (trap receiver retention) | Trap receivers retain events per retention policy. |
| 8 | Saved configurations / archives | Very Low | Persistent | Startup configs and config archives are persistent until explicitly deleted. |

## Network Artifact Types and Forensic Value

Each artifact type provides different forensic insight. Collecting multiple
types provides complementary evidence that strengthens investigation
conclusions through cross-correlation.

### Packet Captures (Full Content)

- **What it provides:** Complete payload content of network communications
- **Forensic value:** Highest — enables reconstruction of exact data transferred,
  protocol analysis, malware payload extraction, credential harvesting evidence
- **Limitations:** High storage requirements, potential performance impact during
  capture, encrypted traffic limits payload visibility
- **Collection method:** On-device capture (`monitor capture`, `monitor traffic`,
  `tcpdump`) or span/mirror port to external capture appliance
- **Best for:** Confirming data exfiltration content, protocol-level attack
  analysis, C2 communication reconstruction

### NetFlow / sFlow / IPFIX (Metadata)

- **What it provides:** Connection metadata — source/destination IPs, ports,
  byte counts, timing, protocol numbers
- **Forensic value:** High — reveals communication patterns, lateral movement
  paths, data volume anomalies, timing correlations without full payload
- **Limitations:** No payload content, sampling (sFlow) may miss low-volume
  flows, unidirectional records require stitching for session reconstruction
- **Collection method:** Already exported to collector if configured; verify
  with flow export verification commands in cli-reference.md
- **Best for:** Lateral movement mapping, communication pattern analysis,
  bandwidth anomaly detection, long-duration investigations

### ARP / MAC / CAM Tables (Layer 2 Mapping)

- **What it provides:** IP-to-MAC (ARP) and MAC-to-port (CAM) mappings at
  the time of collection
- **Forensic value:** Medium-High — establishes which physical host was
  connected to which switch port and had which IP address
- **Limitations:** Point-in-time snapshot only, aging timers mean historical
  data is lost rapidly, dynamic entries are overwritten
- **Collection method:** `show arp`, `show mac address-table` per vendor
- **Best for:** Identifying rogue devices, confirming host identity behind
  an IP address, detecting MAC spoofing

### Routing Tables (Path Analysis)

- **What it provides:** The forwarding path traffic follows through the network
- **Forensic value:** Medium — shows whether traffic was routed as expected,
  reveals unauthorized route injections, identifies asymmetric routing
- **Limitations:** Shows current state only (unless snapshots were taken at
  multiple points), convergence events overwrite previous state
- **Collection method:** `show ip route` / `show route` per vendor
- **Best for:** Verifying containment effectiveness (null routes, route
  changes), detecting route hijacking, path analysis for exfiltration

### Syslog Messages (Event Timeline)

- **What it provides:** Timestamped event records from network devices —
  interface state changes, authentication events, configuration changes,
  firewall actions, protocol state transitions
- **Forensic value:** Medium-High — provides the chronological narrative of
  device-level events surrounding the incident
- **Limitations:** Depends on logging level configuration (informational
  vs. debug), local buffers are small, gaps if syslog forwarding fails
- **Collection method:** Query centralized syslog server / SIEM; verify
  forwarding with `show logging` per vendor
- **Best for:** Timeline reconstruction, event correlation, identifying
  the initial indicator and subsequent spread

### SNMP Traps (State Changes)

- **What it provides:** Asynchronous notifications of significant state
  changes — link up/down, authentication failures, threshold violations
- **Forensic value:** Low-Medium — provides timestamps of significant
  events but limited detail compared to syslog
- **Limitations:** Unreliable delivery (SNMP v1/v2c uses UDP), limited
  detail per trap, depends on trap receiver configuration
- **Collection method:** Query trap receiver / NMS database
- **Best for:** Corroborating syslog timeline, detecting physical events
  (link state), identifying when thresholds were crossed

## Chain-of-Custody Documentation

Every piece of evidence collected must be documented to maintain forensic
integrity. Use the following template for each evidence item.

### Evidence Collection Record

```
EVIDENCE COLLECTION RECORD
===========================
Evidence ID:          [unique sequential identifier, e.g., NET-INC-2024-001-E01]
Incident Reference:   [incident ticket or tracking number]
Collection Timestamp: [YYYY-MM-DD HH:MM:SS UTC]
Collector:            [name and role of person collecting]
Collection Method:    [command used, tool, or export method]
Source Device:        [hostname, IP, model, serial number]
Source Interface:     [interface name if applicable]
Evidence Type:        [packet capture / flow record / ARP table / etc.]
Time Window:          [start — end of captured data, if applicable]
File Name:            [exact filename of saved evidence]
File Size:            [bytes]
Hash (SHA-256):       [hash of evidence file immediately after collection]
Storage Location:     [where the evidence file is stored]
Chain-of-Custody:     [transfer log — who handled, when, to/from where]
Notes:                [any conditions, limitations, or observations]
```

### Hash Verification

After collecting evidence to a file, immediately compute a SHA-256 hash
to establish integrity. Document the hash in the evidence collection record.

| Platform | Command |
|----------|---------|
| Linux/macOS | `sha256sum <filename>` |
| Network device (Cisco) | `verify /sha256 flash:<filename>` |
| Network device (JunOS) | `file checksum sha-256 /var/tmp/<filename>` |
| Network device (EOS) | `verify /sha256 flash:<filename>` |

## Timeline Reconstruction Methodology

Building a forensic timeline from multiple evidence sources requires
systematic correlation. This methodology produces a unified chronological
narrative from disparate network artifacts.

### Step 1: Establish Anchor Events

Identify high-confidence, timestamped events that serve as fixed points
in the timeline. Good anchor events include:

- First alert or detection event (the trigger)
- Interface state changes (link up/down — recorded by multiple systems)
- BGP/OSPF adjacency changes (logged by both peers)
- Firewall deny events for known-bad indicators
- Configuration changes (logged with user attribution)

### Step 2: Normalize Timestamps

All evidence timestamps must be converted to a single timezone (UTC
recommended) before correlation. Common timestamp issues:

- Device clock skew (check NTP status on each device)
- Timezone inconsistencies (some devices log local time, others UTC)
- Daylight saving time transitions during the incident window
- Syslog timestamp precision (seconds vs. milliseconds)

### Step 3: Correlate by Shared Attributes

Link events across sources using shared attributes:

- **IP address** — same source or destination IP appears in flow records,
  ARP tables, and syslog events
- **Timestamp proximity** — events within a defined window (±60 seconds
  for automated correlation, ±5 minutes for manual review)
- **Session identifier** — VPN tunnel IDs, TCP session hashes, or
  flow record keys
- **Device/interface** — events on the same device or interface

### Step 4: Identify Gaps

After correlation, identify periods with missing evidence:

- Time windows with no events from a device that should be active
- Flow record gaps indicating export or collector issues
- Syslog gaps indicating forwarding failures or device reboot
- ARP/MAC table gaps (evidence was volatile and lost before collection)

Document gaps explicitly — they represent uncertainty in the timeline.

### Step 5: Assemble Chronological Sequence

Merge all correlated events into a single timeline sorted by timestamp.
Annotate each entry with:

- Source (which evidence type and device)
- Confidence (high for multi-source corroborated, medium for single source,
  low for inferred from circumstantial evidence)
- Phase (reconnaissance, initial access, lateral movement, objective,
  exfiltration, containment, recovery)

### Timeline Entry Format

```
| # | Timestamp (UTC) | Source Device | Evidence Type | Event Description | Source/Dest | Confidence | Phase |
|---|-----------------|--------------|---------------|-------------------|-------------|------------|-------|
| 1 | 2024-01-15 14:32:01 | fw-core-01 | Syslog | Firewall deny from external IP | 203.0.113.50 → 10.1.1.100:443 | High | Recon |
| 2 | 2024-01-15 14:32:15 | sw-access-01 | ARP table | New ARP entry for 10.1.1.100 | MAC aa:bb:cc:dd:ee:ff | Medium | Context |
| 3 | 2024-01-15 14:35:00 | rtr-core-01 | NetFlow | High-volume flow to external IP | 10.1.1.100 → 198.51.100.25:8443 | High | Exfil |
```
