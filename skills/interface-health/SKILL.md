---
name: interface-health
description: >-
  Interface and link health assessment with error counter analysis, optical
  power monitoring, discard diagnosis, and utilization trending. Multi-vendor
  coverage for Cisco IOS-XE/NX-OS, Juniper JunOS, and Arista EOS with
  severity-tiered thresholds for physical and data-link layer metrics.
license: Apache-2.0
metadata:
  safety: read-only
  author: network-security-skills-suite
  version: "1.0.0"
  openclaw: '{"emoji":"🔍","safetyTier":"read-only","requires":{"bins":["ssh"],"env":[]},"tags":["interface","errors","optics"],"mcpDependencies":[],"egressEndpoints":[]}'
---

# Interface Health Assessment

Threshold-driven diagnostic skill for interface and link health. Covers the
physical and data-link layers — error counters, optical power levels, discard
rates, interface flaps, and bandwidth utilization. Each metric is evaluated
against four severity tiers (Normal / Warning / Critical / Emergency) with
vendor-specific collection commands.

Commands are labeled **[Cisco]**, **[JunOS]**, or **[EOS]** where syntax
diverges. Unlabeled statements apply to all three vendors. Detailed command
syntax is in `references/cli-reference.md`; full threshold tables with
per-optic-type ranges are in `references/threshold-tables.md`.

## When to Use

- Interface reported down or flapping (repeated up/down transitions)
- Users reporting packet loss or degraded throughput on a link
- Monitoring alerts for CRC errors, input errors, or output drops
- Pre/post maintenance validation of link quality after cable or optic swap
- Optical power alarms from DOM (Digital Optical Monitoring) readings
- Capacity planning — identifying interfaces approaching saturation
- Troubleshooting latency spikes that correlate with interface congestion
- Baseline collection for new link turn-ups or circuit migrations

## Prerequisites

- SSH or console access to the device (read-only privilege sufficient)
- Interfaces to evaluate are identified (specific interfaces or all active)
- Baseline error counts or a prior snapshot for delta comparison — without a
  baseline, only instantaneous rates and absolute counters are available
- Knowledge of expected link parameters: speed, duplex, media type (copper vs
  fiber), SFP model, and cable distance
- For optical checks: SFP/QSFP modules with DOM support installed

## Procedure

Work through each step sequentially. Early steps collect broad status; later
steps drill into specific failure domains identified by prior output.

### Step 1: Interface Status Overview

Collect admin state, operational state, speed, duplex, and media type for all
interfaces under review.

**[Cisco]**
```
show interfaces status
show interfaces [intf] | include line protocol|BW|duplex
```

**[JunOS]**
```
show interfaces terse
show interfaces [intf] | match "Physical|Speed|Duplex|Link-level"
```

**[EOS]**
```
show interfaces status
show interfaces [intf] | include line protocol|BW|duplex
```

Record each interface: name, admin/oper state, speed, duplex, media type. Any
interface that is admin up but operationally down requires immediate
investigation — skip to the Decision Trees section for that interface. Duplex
mismatches (one end full, other half) cause late collisions and must be
resolved before error analysis is meaningful.

### Step 2: Error Counter Analysis

Collect error counters and calculate per-interval rates. Raw counters are
cumulative since last clear — always compute a delta over a known interval
(minimum 5 minutes) for actionable rates.

**[Cisco]**
```
show interfaces [intf] | include CRC|input errors|output errors|frame|runts|giants
show interfaces [intf] counters errors
```

**[JunOS]**
```
show interfaces [intf] extensive | match "CRC|Errors|Framing|Runts|Giants"
```

**[EOS]**
```
show interfaces [intf] counters errors
show interfaces [intf] | include CRC|input errors|output errors|runts|giants
```

Key counters to evaluate:
- **CRC errors** — corrupted frames; indicates physical-layer problems (bad
  cable, dirty fiber, failing SFP, EMI)
- **Input errors** — superset including CRC, frame, overrun; aggregate
  indicator of receive-path health
- **Output errors** — transmission failures; often buffer exhaustion or
  interface congestion
- **Frame errors** — non-integer-octet frames; typically duplex mismatch or
  bad NIC
- **Runts** — undersized frames (<64 bytes); usually collision fragments or
  bad NIC
- **Giants** — oversized frames; MTU mismatch between endpoints

Compare rates against thresholds in `references/threshold-tables.md`. Any
counter incrementing steadily (not a stale historical value) at Warning level
or above warrants investigation.

### Step 3: Discard Analysis

Evaluate input and output discards separately — they have different root
causes.

**[Cisco]**
```
show interfaces [intf] | include drops|discard|queue
show policy-map interface [intf]
```

**[JunOS]**
```
show interfaces queue [intf]
show class-of-service interface [intf]
```

**[EOS]**
```
show interfaces [intf] counters discards
show qos interface [intf]
```

- **Output discards** — interface transmit ring full. Causes: sustained
  congestion (traffic exceeds link capacity), inadequate QoS scheduling,
  microbursts overwhelming shallow buffers.
- **Input discards** — receive ring full. Causes: CPU unable to process at
  line rate (control plane punt), input QoS policer drops, or receive buffer
  exhaustion.
- **Queue drops** — per-queue drops visible in QoS policy output. Identify
  which traffic class is affected to prioritize remediation.

High output discards with low utilization suggests microburst activity —
short-duration traffic spikes that don't appear in 5-minute utilization
averages but overflow interface buffers.

### Step 4: Interface Reset and Flap Detection

Identify interfaces with recent or recurring resets.

**[Cisco]**
```
show interfaces [intf] | include resets|Last input|Last output|last change
```

**[JunOS]**
```
show interfaces [intf] extensive | match "Last flapped|Resets"
```

**[EOS]**
```
show interfaces [intf] | include resets|Last input|Last output
show logging | include [intf].*up|[intf].*down
```

Record reset counts and last-flap timestamps. Correlate flap events with error
counter spikes — a link that flaps and accumulates CRC errors on recovery
likely has a physical-layer issue (loose cable, marginal SFP). Frequent resets
without errors may indicate auto-negotiation failures or spanning-tree
reconvergence triggers.

Threshold: >3 resets/hour is Critical; >10 resets/hour is Emergency. See
`references/threshold-tables.md` for full severity tiers.

### Step 5: Optical Power Monitoring

For fiber interfaces with DOM-capable SFPs, collect Tx power, Rx power, laser
bias current, and module temperature.

**[Cisco]**
```
show interfaces [intf] transceiver detail
```

**[JunOS]**
```
show interfaces diagnostics optics [intf]
```

**[EOS]**
```
show interfaces [intf] transceiver detail
```

Key readings:
- **Tx Power (dBm)** — transmit optical power. Out-of-range indicates SFP
  degradation or failure.
- **Rx Power (dBm)** — received optical power. Low Rx with normal Tx on the
  remote end indicates fiber attenuation (dirty connector, bend loss, distance
  exceeded, bad splice).
- **Laser Bias Current (mA)** — current driving the laser. Rising bias over
  time indicates SFP aging; high bias with low Tx power means the SFP is
  compensating for degradation.
- **Temperature (°C)** — module operating temperature. Elevated temperature
  accelerates SFP aging and can cause transmission errors.

Compare readings against the per-optic-type tables in
`references/threshold-tables.md`. The tables provide manufacturer spec ranges
for common SFP types (1G-SX, 10G-SR, 10G-LR, 25G-SR, 100G-SR4).

### Step 6: Utilization Assessment

Measure bandwidth usage to identify congested or underutilized links.

**[Cisco]**
```
show interfaces [intf] | include input rate|output rate|reliability
show interfaces [intf] summary
```

**[JunOS]**
```
show interfaces [intf] traffic
show interfaces [intf] statistics traffic
```

**[EOS]**
```
show interfaces [intf] | include input rate|output rate
show interfaces [intf] counters rates
```

Calculate utilization as a percentage of interface speed. Note that CLI
"input/output rate" values are typically 5-minute weighted averages — they
smooth out microbursts. For burst detection, correlate with output discards
(Step 3) and use streaming telemetry or shorter polling intervals if available.

## Threshold Tables

Summary of key thresholds used in this skill. Full per-optic-type tables and
detailed severity definitions are in `references/threshold-tables.md`.

| Metric | Normal | Warning | Critical | Emergency |
|--------|--------|---------|----------|-----------|
| CRC errors/5min | 0 | 1–5 | 6–50 | >50 |
| Input errors/5min | 0–2 | 3–20 | 21–100 | >100 |
| Output discards/5min | 0–10 | 11–100 | 101–1000 | >1000 |
| Interface resets/hr | 0 | 1–2 | 3–10 | >10 |
| Rx Power vs low-warn | >3 dBm margin | 1–3 dBm margin | 0–1 dBm margin | Below low-alarm |
| Utilization % | 0–50% | 51–75% | 76–90% | >90% |

## Decision Trees

### High Error Rate

```
Errors incrementing (CRC, input, frame)
├── Single interface affected?
│   ├── Yes → Physical layer issue
│   │   ├── Fiber interface?
│   │   │   ├── Check Rx power → Low? → Clean connectors, check fiber run
│   │   │   ├── Rx power normal? → Check SFP seating, try reseat
│   │   │   └── SFP temperature high? → Check airflow, replace SFP
│   │   └── Copper interface?
│   │       ├── Check cable length (<100m for Cat6)
│   │       ├── Check for EMI sources near cable run
│   │       └── Swap cable, test with known-good
│   └── No → Multiple interfaces affected
│       ├── Same line card/module? → Suspect line card hardware
│       ├── Same patch panel? → Suspect patch panel or cable tray
│       └── All interfaces? → Upstream power or grounding issue
├── Frame errors specifically?
│   └── Check duplex settings both ends → Mismatch causes late collisions
├── Giants specifically?
│   └── Check MTU both ends → Must match; check for jumbo frame config
└── Runts specifically?
    └── Check for collision domain issues or bad NIC on connected device
```

### High Discards

```
Discards incrementing
├── Output discards?
│   ├── Utilization >75%? → Congestion — consider link upgrade or ECMP
│   ├── Utilization <50% but discards high? → Microburst activity
│   │   ├── Check per-queue drops → Identify affected traffic class
│   │   └── Increase interface buffer or tune QoS scheduling
│   └── QoS policy applied?
│       ├── Check policer/shaper rates → May be too restrictive
│       └── Check queue allocation → Priority queue starving best-effort
├── Input discards?
│   ├── CPU-bound traffic? → Check CoPP counters for punt drops
│   ├── Input policer configured? → Check rate vs actual traffic
│   └── Receive buffer exhaustion → Rare; check for flood traffic
└── Intermittent vs sustained?
    ├── Sustained → Capacity issue; plan upgrade
    └── Intermittent → Burst-driven; tune buffers or QoS
```

### Optical Power Out of Range

```
Optical reading outside normal range
├── Rx power low?
│   ├── Remote Tx power normal? → Fiber path issue
│   │   ├── Clean both connectors (IPA wipes, not compressed air alone)
│   │   ├── Check for fiber bends exceeding minimum bend radius
│   │   ├── Verify distance within SFP spec (e.g., 10G-SR max 300m OM3)
│   │   └── Test with OTDR if available → Locate fault point
│   └── Remote Tx power also low? → Remote SFP failing
├── Tx power low?
│   ├── Laser bias current high? → SFP degrading, plan replacement
│   ├── Laser bias current normal? → SFP may be misconfigured
│   └── Temperature elevated? → Fix cooling, then recheck Tx power
├── Rx power high?
│   └── Short fiber run without attenuator → Add inline attenuator
└── Temperature alarm?
    ├── Ambient temp normal? → SFP internal issue, replace
    └── Ambient temp high? → Fix chassis/room cooling first
```

## Report Template

```
INTERFACE HEALTH REPORT
========================
Device: [hostname]
Vendor: [Cisco | JunOS | EOS]
Check Time: [timestamp]
Performed By: [operator/agent]

INTERFACE SUMMARY:
- Total interfaces reviewed: [n]
- Admin Up / Oper Up: [n]
- Admin Up / Oper Down: [n] — [list]
- Interfaces with active errors: [n]
- Interfaces with discards: [n]

FINDINGS:
1. [Severity] [Category] — [Description]
   Interface: [name]
   Observed: [metric value and rate]
   Threshold: [Normal/Warning/Critical/Emergency boundary crossed]
   Root Cause: [diagnosis from decision tree]
   Action: [recommended remediation]

OPTICAL STATUS:
- Interfaces with DOM data: [n]
- Rx power warnings: [list with dBm values]
- Tx power warnings: [list with dBm values]
- SFPs approaching end-of-life (rising bias current): [list]

UTILIZATION SUMMARY:
- Interfaces >75% utilized: [list with peak and average rates]
- Interfaces >90% utilized: [list — immediate attention required]

RECOMMENDATIONS:
- [Prioritized action list]

NEXT CHECK: [EMERGENCY: 1hr, CRITICAL: 4hr, WARNING: 24hr, NORMAL: 7d]
```

## Troubleshooting

### CRC Errors on Fiber with Normal Optical Power

Optical power within spec but CRC errors incrementing. Common causes:
wavelength mismatch between SFP types (e.g., SX connected to LR), dirty
connector on the inside of the SFP cage (not the fiber tip), or SFP
incompatibility with the switch (non-qualified optic). Try: clean the SFP
receptacle, verify both ends use the same SFP type, test with a
vendor-qualified optic.

### Output Discards with Low Utilization

Interface shows <30% average utilization but output discards are climbing. This
is almost always microburst traffic — sub-second spikes that exceed link
capacity during the burst but average out below the utilization threshold.
Diagnose with: per-queue drop counters (shows which traffic class), interface
buffer allocation stats. Remediate with: QoS scheduling adjustments, increased
interface buffer depth, or traffic shaping at the ingress point.

### Interface Stuck in Down/Down After Cable Swap

Admin up, operationally down after replacing a cable or SFP. Check: SFP is
fully seated (push firmly until click), fiber polarity is correct (Tx-to-Rx
crossover), SFP type matches remote end, speed/duplex is set to auto or
matches. On **[Cisco]**, check `show interfaces [intf] | include err-disabled`
— the port may have been error-disabled by a protection feature (BPDU guard,
UDLD, link-flap detection). Recover with `shutdown` / `no shutdown` after
fixing the root cause.

### Flapping Interface with No Errors

Interface cycles up/down every few seconds with zero error counters. This
suggests a negotiation or protocol issue, not a physical fault. Common causes:
auto-negotiation incompatibility (force speed/duplex on both ends), STP
topology changes causing repeated blocking/forwarding transitions, UDLD
aggressive mode detecting unidirectional link. Check spanning-tree state and
UDLD status on the interface.

### Rising Laser Bias with Stable Tx Power

Laser bias current increasing over weeks/months while Tx power remains stable.
The SFP is compensating for laser degradation by driving more current. This is
normal aging but indicates the SFP will eventually fail — Tx power will drop
when the laser can no longer compensate. Plan proactive replacement before the
Tx power begins declining. Track the trend: if bias current exceeds 80% of the
manufacturer's max specification, schedule replacement within 30 days.
