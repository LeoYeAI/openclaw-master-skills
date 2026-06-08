---
name: arista-device-health
description: >-
  Arista EOS device health check and triage procedure. Use when
  troubleshooting Arista 7000, 7500, or 720X series switches — assessing
  CPU, memory, interfaces, environment, and agent/daemon health. Covers
  MLAG state validation and VXLAN/EVPN health as data center extension
  steps. EOS is Linux-native — standard Linux diagnostics (bash top,
  df, dmesg) are valid troubleshooting tools alongside EOS show commands.
  Includes agent health monitoring via show agent for EOS-specific
  daemon failure detection.
license: Apache-2.0
metadata:
  safety: read-only
  author: network-security-skills-suite
  version: "1.0.0"
  openclaw: '{"emoji":"🔍","safetyTier":"read-only","requires":{"bins":["ssh"],"env":[]},"tags":["arista","eos","health"],"mcpDependencies":[],"egressEndpoints":[]}'
---

# Arista EOS Device Health Check

Structured triage procedure for assessing Arista EOS device health. Produces a
prioritized findings report with severity classifications and recommended actions.

EOS runs on a Linux kernel with individual processes (agents) managing each
protocol and subsystem. This architecture means Linux-native tools (`bash top`,
`bash df`, `bash dmesg`) are valid supplements to EOS show commands. Agent
health is a first-class concern — a crashed or stuck agent can silently affect
a subsystem even when aggregate device metrics look normal.

The procedure covers core device health first, then extends to MLAG and
VXLAN/EVPN for data center deployments.

## When to Use

- Device reported as slow, dropping traffic, or unresponsive
- Scheduled health audit of Arista switches (leaf, spine, or border)
- Post-change verification after upgrades, patches, or configuration changes
- Capacity planning data collection for CPU, memory, and link utilization
- Incident response when an Arista switch is suspected as the fault domain
- MLAG inconsistency or split-brain detection in a data center pair
- VXLAN/EVPN overlay health assessment — VTEP reachability, BGP EVPN peering
- Agent crash or restart detected in syslog

## Prerequisites

- SSH or console access to the device (privilege 1 minimum)
- EOS 4.28 or later (commands validated against EOS 4.30+)
- Network reachability to management interface confirmed
- Awareness of the device's normal baseline (CPU, memory, traffic patterns)
- For MLAG configurations: access to both MLAG peers for cross-validation
- For VXLAN/EVPN: knowledge of expected VTEP count and BGP EVPN peer list

## Procedure

Follow this sequence. Core device health (Steps 1–5) applies to all deployments.
Steps 6–7 are data center extensions for MLAG and VXLAN/EVPN — skip if not
configured on this device.

### Step 1: Establish Baseline Context

```
show version
show uptime
show clock
show inventory
```

Record: hostname, EOS version, uptime, hardware model, total memory, current time.
Short uptime indicates a recent reload or crash — check `show reload cause` for
the trigger. Note the hardware platform — Arista's 7050X, 7280R, 7500R, and
720X series have different memory and CPU profiles.

### Step 2: CPU and Memory Assessment

EOS reports CPU and memory through both EOS commands and Linux-native tools.

```
show processes top once
show version | include Free memory
```

**Linux-native alternative** (provides more granularity):
```
bash timeout 5 top -bn1 | head 20
bash free -m
```

`show processes top once` shows per-process CPU and memory similar to Linux `top`.
EOS CPU is typically consumed by agents — each protocol has its own process.

Key agents to watch:
- **Stp** — Spanning Tree: high CPU indicates topology instability
- **Rib** — Routing Information Base: route churn or large table operations
- **Ebra** — EOS Bridge Agent: L2 forwarding, MAC learning storms
- **IpRib** — IP RIB agent: routing table processing
- **Bgp** — BGP agent: peer negotiations, route processing
- **Fap-sobek** / **Sand** — ASIC agents: forwarding plane, hardware programming

EOS memory: `show version` includes total and free memory. Free memory below
20% of total is warning. Linux `free -m` provides buffer/cache detail — EOS
uses Linux page cache aggressively, so "used" memory includes reclaimable cache.

### Step 3: Agent and Daemon Health

EOS runs each subsystem as an independent agent. A crashed or stuck agent
affects its subsystem silently — device-level metrics may look normal while
one protocol is completely inoperative.

```
show agent
show agent [name] logs | tail 20
show logging last 50 | include AGENT|agent|crash|restart
```

`show agent` lists all EOS agents with their PID, state, and uptime.

Healthy state: all agents show `running` with uptimes matching device uptime.
Red flags:
- Agent with shorter uptime than device → it crashed and restarted
- Agent in `crashed` or `not running` state → subsystem is down
- Multiple agent restarts in logs → recurring instability

If an agent shows recent restart, check its logs: `show agent [name] logs`.
Common restart causes: memory exhaustion, uncaught exception, watchdog timeout.

### Step 4: Interface Health

```
show interfaces status
show interfaces counters errors
show interfaces counters discards
```

For interfaces with errors:
```
show interfaces [name]
show interfaces [name] transceiver
```

Error classification:
- CRC / FCS errors → Layer 1 (cabling, optics, SFP seating)
- Input errors without CRC → buffer overruns, MTU mismatch
- Alignment errors → duplex mismatch or L1 issue
- Output discards → egress congestion; check QoS or link capacity
- Late collisions → duplex mismatch (should not occur on modern links)

Optics DOM: `show interfaces transceiver` provides Tx/Rx power, temperature,
voltage. Low Rx power (below -10 dBm for most 10G SFP+) indicates fiber or
optic degradation.

### Step 5: Environment and Platform

```
show environment all
show environment cooling
show environment power
show environment temperature
show reload cause
show logging last 30 | include ERR|WARN|traceback|panic
```

Check: all temperature sensors within limits, all power supplies OK, all
fans operational. `show environment all` is a comprehensive single command.

`show reload cause` — if the device recently reloaded, this explains why.
Expected causes: user-initiated, software upgrade. Unexpected causes:
kernel panic, watchdog timeout, power loss.

Review syslog for tracebacks, panics, or agent crashes. EOS logs are also
accessible via `bash cat /var/log/messages | tail 50`.

### Step 6: MLAG Health (Data Center Extension)

Skip this step if MLAG is not configured. MLAG state is often the single most
important health indicator in an Arista data center deployment — a degraded
MLAG pair can cause traffic black-holes or asymmetric forwarding.

```
show mlag
show mlag detail
show mlag interfaces
show mlag config-sanity
```

**MLAG state assessment:**

| Field | Healthy Value | Problem Indicator |
|-------|--------------|-------------------|
| state | active | disabled, inactive |
| negotiation status | connected | connecting, disconnected |
| peer-link status | up | down, errdisabled |
| local-interface status | up | down |
| config-sanity | consistent | inconsistent |

`show mlag detail` provides:
- **Peer address** and **peer-link** interface status
- **Heartbeat** interval and status — lost heartbeats indicate control plane
  reachability issues between peers
- **Reload delay** timers — critical for preventing traffic loss during boot

`show mlag config-sanity` checks for configuration mismatches between peers.
Inconsistencies can cause traffic loops or black-holes. Address any `inconsistent`
result before continuing other triage.

`show mlag interfaces` — verify all MLAG interfaces show `active-full` on both
sides. `active-partial` means one side is down — reduced redundancy.
`disabled` means the MLAG interface is administratively or operationally down.

### Step 7: VXLAN/EVPN Health (Data Center Extension)

Skip this step if VXLAN/EVPN is not configured. This assesses overlay fabric
health for VXLAN deployments using BGP EVPN as the control plane.

```
show vxlan vtep
show vxlan address-table
show interfaces vxlan 1
show bgp evpn summary
```

**VXLAN health checks:**
- `show vxlan vtep` — verify expected VTEP count. Missing VTEPs indicate
  underlay reachability or BGP EVPN peering issues.
- `show interfaces vxlan 1` — VTEP source interface must be up. Flood list
  should match expected remote VTEPs (for flood-and-learn) or be empty
  (for BGP EVPN with ingress replication).
- `show vxlan address-table` — MAC learning across the overlay. Stale or
  missing entries indicate control plane issues.

**BGP EVPN peering:**
- `show bgp evpn summary` — all EVPN peers must be in Established state.
  Peers in Active/Connect state have transport or configuration issues.
- Compare EVPN route count to baseline — significant deviation indicates
  route withdrawal or redistribution problems.

For L3 VXLAN (symmetric IRB):
```
show ip route vrf [name] summary
show bgp evpn route-type ip-prefix
```

Verify: VRF route counts match expectations, no unexpected route withdrawals,
EVPN type-5 routes present for inter-VRF routing.

## Threshold Tables

Reference: `references/threshold-tables.md` for detailed per-parameter thresholds.

| Parameter | Normal | Warning | Critical | Notes |
|-----------|--------|---------|----------|-------|
| CPU 5-min avg | < 40% | 40–70% | > 70% | Per-agent breakdown in `show processes top` |
| Memory free | > 30% | 20–30% | < 20% | Linux page cache is reclaimable |
| Agent state | All running | Agent restarted | Agent crashed/not running | Check `show agent` |
| Interface error rate | < 0.01% | 0.01–0.1% | > 0.1% | |
| Output discards/hr | < 100 | 100–1000 | > 1000 | |
| MLAG state | active/connected | config inconsistency | peer-link down | |
| VXLAN VTEP count | Matches expected | Missing VTEPs | Vxlan1 interface down | |
| Temperature | Within spec | 5°C of max | At/above max | Per-sensor |

## Decision Trees

### Primary Triage

```
Is the device reachable?
├── No → Check console, power, environment. Check reload cause after recovery.
└── Yes
    ├── Agent health issue?
    │   ├── Agent crashed / not running → Subsystem is down
    │   │   ├── Identify which agent → Determines affected protocol/feature
    │   │   ├── Bgp agent → BGP sessions will be down
    │   │   ├── Stp agent → STP not running, L2 loops possible
    │   │   ├── Ebra agent → L2 forwarding affected
    │   │   └── Action: check agent logs, attempt restart, escalate to TAC
    │   ├── Agent restarted recently → Subsystem had a disruption
    │   │   └── Check logs: `show agent [name] logs` for crash reason
    │   └── All agents running, uptimes match → Agent layer healthy
    │
    ├── CPU issue?
    │   ├── Identify top agent by CPU
    │   │   ├── Stp high → STP topology change, check link flaps
    │   │   ├── Rib/IpRib high → Route churn, check BGP/OSPF peers
    │   │   ├── Ebra high → MAC learning storm, check for loops
    │   │   ├── Bgp high → Large table, peer negotiation, route policy
    │   │   └── Fap/Sand high → ASIC programming backlog
    │   └── No single agent dominant → General overload, check traffic rates
    │
    ├── Memory issue?
    │   ├── Free < 20% → Check top consumers via `show processes top once`
    │   ├── Linux cache: `bash free -m` → Cache is reclaimable, not a real leak
    │   └── Steady growth → Memory leak in agent, collect data, plan reload
    │
    ├── Interface errors? → Classify error type
    │   ├── CRC/FCS errors → Layer 1 (cable, optic, SFP)
    │   ├── Output discards → QoS or congestion
    │   └── Alignment errors → Duplex mismatch
    │
    ├── MLAG issue? (if configured)
    │   ├── See MLAG State Triage tree below
    │   └── MLAG healthy → Continue
    │
    ├── VXLAN/EVPN issue? (if configured)
    │   ├── Missing VTEPs → Check underlay reachability, BGP EVPN peers
    │   ├── EVPN peer not Established → Check transport, route-map, ASN
    │   └── VTEP and peers OK → Overlay healthy
    │
    └── All within thresholds → Document clean health
```

### MLAG State Triage

```
MLAG configured?
├── No → Skip MLAG checks
└── Yes
    ├── MLAG state: active?
    │   ├── No → MLAG disabled or inactive
    │   │   └── Check: `show mlag` for reason, peer reachability
    │   └── Yes → Continue
    │
    ├── Peer-link status: up?
    │   ├── No → CRITICAL — peer-link down
    │   │   ├── Traffic orphaned on MLAG interfaces
    │   │   ├── Check: physical link, SFP, port-channel members
    │   │   └── Verify: reload-delay timers configured to prevent storms
    │   └── Yes → Continue
    │
    ├── Negotiation: connected?
    │   ├── No → Control plane issue between peers
    │   │   └── Check: heartbeat, peer IP, VLAN configuration
    │   └── Yes → Continue
    │
    ├── Config sanity: consistent?
    │   ├── No → Configuration mismatch
    │   │   ├── `show mlag config-sanity` for details
    │   │   ├── Common: VLAN mismatch, STP priority, trunk allowed VLANs
    │   │   └── Fix mismatches before trusting MLAG state
    │   └── Yes → Continue
    │
    ├── MLAG interfaces: all active-full?
    │   ├── active-partial → One side down, reduced redundancy
    │   │   └── Check: interface status on both peers
    │   ├── disabled → Interface operationally down
    │   │   └── Check: physical link, member port status
    │   └── active-full → Healthy
    │
    └── All checks pass → MLAG healthy
```

### Escalation Criteria

Escalate to senior engineer or Arista TAC when:
- CPU sustained > 90% for 15+ minutes with no identifiable cause
- Memory below 15% free with no recent change to explain consumption
- Agent in crashed state that does not recover after restart
- Multiple agents crashing or restarting within a short period
- Traceback or kernel panic in logs (`show logging`, `bash dmesg`)
- Any environmental alarm (power, fan, temperature)
- More than 3 routing neighbor state changes in the last hour
- MLAG peer-link failure with no clear physical cause
- MLAG config-sanity inconsistencies that cannot be resolved
- VXLAN overlay losing more than 10% of expected VTEPs

## Report Template

```
DEVICE HEALTH REPORT
====================
Device: [hostname]
Platform: Arista EOS
Model: [from show inventory]
Software: [EOS version]
Uptime: [uptime string]
Check Time: [timestamp]
Performed By: [operator/agent]

SUMMARY: [HEALTHY | WARNING | CRITICAL | EMERGENCY]

AGENT HEALTH:
  Total agents: [count]
  Running: [count] | Crashed: [count] | Not running: [count]
  Recent restarts: [list any agents with uptime < device uptime]

FINDINGS:
1. [Severity] [Component] — [Description]
   Domain: [System | Interface | MLAG | VXLAN | Environment]
   Observed: [metric value]
   Threshold: [normal/warning/critical range]
   Action: [recommended action]

2. ...

DC EXTENSIONS:
  MLAG: [healthy | degraded | critical | not configured]
    State: [active/inactive], Peer-link: [up/down], Config-sanity: [consistent/inconsistent]
  VXLAN/EVPN: [healthy | degraded | critical | not configured]
    VTEPs: [observed/expected], EVPN peers: [established/total]

RECOMMENDATIONS:
- [Prioritized action list]

NEXT CHECK: [date based on severity — CRITICAL: 24hr, WARNING: 7d, HEALTHY: 30d]
```

## Troubleshooting

### Device Unresponsive to SSH

Try console access. If console is also unresponsive, check power and environment
via out-of-band management. After recovery: `show reload cause` for the trigger,
`bash dmesg | tail 50` for kernel messages, `show logging last 50` for pre-crash
syslog. EOS stores crash data in `/var/log/` — accessible via `bash ls -la /var/log/`.

### Agent Crash and Recovery

If `show agent` shows an agent as `crashed` or with uptime shorter than the device:
1. Check agent logs: `show agent [name] logs | tail 30`
2. Check syslog: `show logging last 50 | include [agent-name]`
3. Linux-level: `bash journalctl -u [agent-name] --no-pager | tail 30`
4. If the agent is not running, attempt: `agent [name] shutdown` then
   `no agent [name] shutdown` in configuration mode (note: this is a config change)

Agent crashes are the most common EOS-specific failure mode. Collect logs before
restarting — the crash data is needed for TAC investigation.

### CPU Spikes During Health Check

EOS show commands can briefly spike CPU on the management plane. Wait 30 seconds
after connecting before collecting CPU data. Use `show processes top once` rather
than interactive `top` (which holds a session) for scripted checks.

### MLAG Split-Brain Detection

If both peers report MLAG state `active` but negotiation shows `disconnected`,
this is a split-brain condition. Both peers believe they are the primary. Causes:
peer-link physical failure, peer-link VLAN issue, or heartbeat network partition.
Immediate action: verify physical peer-link connectivity. If peer-link is
physically up but MLAG reports disconnected, check VLAN trunking on the
peer-link and the heartbeat network (usually the management VRF).

### Linux-Native Diagnostics

EOS's Linux foundation means standard Linux tools work from `bash`:
- `bash top -bn1` — process-level CPU and memory (more granular than EOS `top`)
- `bash free -m` — memory with buffer/cache detail
- `bash df -h` — filesystem usage (important for /mnt/flash and /var/log)
- `bash dmesg | tail` — kernel messages (hardware errors, driver issues)
- `bash uptime` — load averages
- `bash cat /proc/meminfo` — detailed memory breakdown

These supplement EOS show commands when deeper investigation is needed.
Prefix all commands with `bash` from the EOS CLI, or enter `bash` for a shell.

### Inconsistent Memory Readings

EOS's Linux page cache uses available memory for file caching. `show version`
may report low free memory while actual memory pressure is low. Use
`bash free -m` and check the `available` column (not `free`) for the real
available memory. The `available` column accounts for reclaimable cache and
buffers.
