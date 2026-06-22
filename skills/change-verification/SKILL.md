---
name: change-verification
description: >-
  Pre/post change verification with baseline capture, diff analysis, and
  rollback decision guidance across Cisco IOS-XE/NX-OS, Juniper JunOS, and
  Arista EOS. Structured around a single change event lifecycle — before,
  during, and after — with impact classification and rollback criteria.
license: Apache-2.0
metadata:
  safety: read-write
  author: network-security-skills-suite
  version: "1.0.0"
  openclaw: '{"emoji":"🔧","safetyTier":"read-write","requires":{"bins":["ssh"],"env":[]},"tags":["change","verification","rollback"],"mcpDependencies":["git-netops-mcp"],"egressEndpoints":[]}'
---

# Change Verification

Event-driven change verification skill for structured change windows. Guides
baseline capture before a change, provides change execution safety patterns,
performs post-change diff analysis, and supports rollback decision-making when
unexpected deviations are detected.

This skill covers a **single change event lifecycle** (before → during →
after). For ongoing configuration drift detection and compliance auditing, use
the `config-management` skill instead.

Commands are labeled **[Cisco]**, **[JunOS]**, or **[EOS]** where syntax
diverges. Unlabeled statements apply to all three vendors.

> **Safety Note — Read-Write Operations:** This skill includes procedures that
> modify device state during change execution and rollback phases. Steps that
> write to devices are marked with ⚠️ **WRITE**. Always confirm authorization,
> change ticket approval, and maintenance window status before executing write
> operations. Baseline capture and post-change verification steps are read-only
> and safe to run at any time.

## When to Use

- Planned maintenance window requiring structured pre/post verification
- Configuration change (routing policy, ACLs, interface config) with rollback plan
- Software upgrade or patch requiring before/after state comparison
- Hardware replacement (linecard, SFP, PSU) with service validation
- Circuit turn-up or decommission with adjacency and traffic verification
- Emergency change requiring rapid baseline capture and rollback readiness
- Post-change soak period with periodic re-verification against baselines

## Prerequisites

- SSH or console access to all devices in the change scope (read-only for
  baselines; enable/configure privilege for change execution and rollback)
- Approved change ticket with documented scope, expected impact, and rollback
  plan including timing criteria
- Pre-identified list of devices and interfaces in the change scope
- Knowledge of expected state changes: which routes will move, which interfaces
  will bounce, which adjacencies will flap
- Access to a file store (flash, SCP server, or local disk) for baseline
  archival
- Contact information for escalation if rollback criteria are met
- See `references/checklist-templates.md` for per-change-type prerequisites

## Procedure

Follow these steps sequentially for each change event. Steps 1–2 are
always read-only. Steps 3–4 include write operations. Steps 5–6 are
analytical and drive the rollback decision.

### Step 1: Pre-Change Baseline Capture

Capture device state snapshots before any changes. Store outputs with
timestamps for post-change comparison.

**Routing state:**

**[Cisco]**
```
show ip route summary
show ip bgp summary
show ip ospf neighbor
```

**[JunOS]**
```
show route summary
show bgp summary
show ospf neighbor
```

**[EOS]**
```
show ip route summary
show ip bgp summary
show ip ospf neighbor
```

**Interface and adjacency state:**

All vendors — capture interface status, error counters, and neighbor tables:

**[Cisco]**
```
show interfaces summary
show cdp neighbors
show ip arp
```

**[JunOS]**
```
show interfaces terse
show lldp neighbors
show arp no-resolve
```

**[EOS]**
```
show interfaces status
show lldp neighbors
show ip arp
```

**Configuration and hardware:**

**[Cisco]**
```
show running-config
show environment all
show inventory
```

**[JunOS]**
```
show configuration
show chassis environment
show chassis hardware
```

**[EOS]**
```
show running-config
show environment all
show inventory
```

⚠️ **WRITE** — Archive baseline config to persistent storage:

**[Cisco]** `copy running-config flash:pre-change-[ticket]-[date].cfg`
**[JunOS]** `request system configuration save /var/tmp/pre-change-[ticket].conf`
**[EOS]** `copy running-config flash:pre-change-[ticket]-[date].cfg`

Record baseline metrics for comparison: total route count, BGP peer count
(Established), OSPF neighbor count (Full), interface error counters, and
hardware sensor readings.

### Step 2: Change Scope Documentation

Before executing any changes, document:

1. **Change description** — what configuration lines are being added, modified,
   or removed
2. **Expected impact** — which peers will flap, which routes will shift, which
   interfaces will bounce, expected duration of disruption
3. **Rollback trigger criteria** — specific thresholds that mandate rollback
   (see Threshold Tables below)
4. **Rollback procedure** — exact commands to revert (see
   `references/cli-reference.md` for vendor-specific rollback commands)
5. **Success criteria** — what "done" looks like: all baselines restored,
   intended changes visible, no unexpected deviations
6. **Soak period** — how long to monitor after change before declaring success

### Step 3: Change Execution

⚠️ **WRITE** — Apply changes using commit-confirm patterns when available.

**[Cisco]** — No native commit-confirm. Apply changes in config mode and
immediately verify. For bulk changes, use `configure replace` with a prepared
config file.

**[JunOS]** — Use `commit confirmed [minutes]` to auto-rollback if not
confirmed within the timer window. Confirm with `commit` after verification.
```
configure
# ... apply changes ...
commit confirmed 5
# ... verify ...
commit
```

**[EOS]** — Use `configure session` for atomic staged changes. Review before
committing.
```
configure session change-[ticket]
# ... apply changes ...
show session-config
commit
```

**Staged rollout for multi-device changes:** Apply to one device first, verify
post-change state (Step 4), then proceed to remaining devices only after the
first device passes all checks.

### Step 4: Post-Change Verification

Re-capture all baseline metrics from Step 1 using identical commands. Perform
a structured diff against pre-change baselines.

**Key comparisons:**

| Metric | Compare Against | Expected Outcome |
|--------|----------------|------------------|
| Route count | Pre-change summary | Within deviation threshold |
| BGP peers Established | Pre-change peer list | All peers restored (or changed per plan) |
| OSPF neighbors Full | Pre-change neighbor list | All adjacencies restored |
| Interface errors | Pre-change counters | No new sustained errors |
| Config diff | Archived pre-change config | Only intended lines changed |

**Config diff verification:**

**[Cisco]**
```
show archive config differences flash:pre-change-[ticket]-[date].cfg system:running-config
```

**[JunOS]**
```
show | compare rollback 1
```

**[EOS]**
```
diff running-config flash:pre-change-[ticket]-[date].cfg
```

Review every line in the diff output. Classify each changed line as **expected**
(directly part of the change plan) or **unexpected** (not in the change scope).

### Step 5: Impact Assessment

Classify all deviations from baseline into categories:

1. **Expected — Intended:** Changes that are the direct goal of the change
   window (e.g., new BGP peer appearing, old ACL removed). No action needed.
2. **Expected — Side Effect:** Changes caused by the intended change but not
   the primary goal (e.g., route count increase because a new peer is now
   advertising). Verify they are benign.
3. **Unexpected — Minor:** Deviations not related to the change scope but low
   severity (e.g., a single interface counter increment). Investigate but do
   not necessarily roll back.
4. **Unexpected — Critical:** Deviations indicating collateral damage (e.g.,
   adjacency loss on an unrelated interface, route withdrawal not in change
   scope). Evaluate rollback immediately.

If any deviation is classified as **Unexpected — Critical**, proceed directly
to Step 6 rollback evaluation.

### Step 6: Rollback Decision

Evaluate whether to accept the change or roll back using the criteria below.

**Rollback if ANY of these conditions are true:**

- Service-affecting outage on interfaces/peers outside the change scope
- Route count deviation exceeds threshold AND routes are not accounted for in
  the change plan
- Adjacency loss persists beyond the expected convergence window
- Hardware errors (PSU, fan, temperature) emerged that were not present in
  baseline
- The change did not achieve its intended effect (success criteria from Step 2
  not met)

**Accept if ALL of these conditions are true:**

- All success criteria from Step 2 are met
- Config diff contains only expected change lines
- All baseline metrics are within acceptable deviation thresholds
- No unexpected critical deviations detected
- Soak period has elapsed without regression

⚠️ **WRITE** — If rolling back:

**[Cisco]** `configure replace flash:pre-change-[ticket]-[date].cfg force`
**[JunOS]** `rollback 1` then `commit`
**[EOS]** `configure replace flash:pre-change-[ticket]-[date].cfg`

After rollback, re-run Step 4 post-change verification to confirm the device
has returned to its pre-change state.

## Threshold Tables

### Acceptable Deviation Thresholds

| Metric | Normal Deviation | Warning | Rollback Trigger |
|--------|-----------------|---------|------------------|
| IPv4 route count | ±2% of baseline | ±5% of baseline | >10% or unplanned loss |
| IPv6 route count | ±2% of baseline | ±5% of baseline | >10% or unplanned loss |
| BGP Established peers | 0 lost (unless planned) | 1 lost (if in scope) | ≥1 lost outside scope |
| OSPF Full adjacencies | 0 lost (unless planned) | Flap then recover <2 min | Lost >2 min |
| Interface errors (new) | 0 new CRC/input errors | <10 in first 5 min | Sustained >10/min |
| Interface flaps | 0 (unless planned bounce) | 1 flap on in-scope intf | Any flap outside scope |

### Rollback Timing Thresholds

| Phase | Maximum Duration | Action if Exceeded |
|-------|-----------------|-------------------|
| Change execution | Per change ticket | Pause and escalate |
| Post-change convergence | 5 minutes | Begin rollback assessment |
| Adjacency re-establishment | 2 minutes per peer | Escalate if critical peer |
| Route table stabilization | 3 minutes | Check for route oscillation |
| Soak period (minor change) | 15 minutes | Declare success or investigate |
| Soak period (major change) | 60 minutes | Declare success or investigate |
| Rollback execution | 5 minutes | Escalate to senior engineer |

## Decision Trees

### Post-Change Diff Contains Unexpected Lines

```
Config diff shows unexpected changes
├── Lines are in sections RELATED to change scope
│   ├── Side effect of intended change (e.g., auto-generated route-map sequence)
│   │   └── Classify as Expected — Side Effect → Document and accept
│   └── Unintended consequence (e.g., wrong interface affected)
│       └── Classify as Unexpected — Critical → Evaluate rollback
└── Lines are in sections UNRELATED to change scope
    ├── Timestamps, counters, or cosmetic changes (e.g., "Last configuration change")
    │   └── Classify as Expected — Side Effect → Ignore
    └── Substantive config changes (e.g., ACL modified, route-map added)
        └── Classify as Unexpected — Critical → Immediate rollback
```

### Adjacency Loss Detected Post-Change

```
Neighbor/peer no longer in expected state
├── Device IS in the change scope
│   ├── Interface was intentionally bounced per change plan
│   │   ├── Adjacency recovers within timing threshold
│   │   │   └── Expected — document recovery time
│   │   └── Adjacency does NOT recover within threshold
│   │       └── Investigate → Check interface state, cable, peer config
│   └── Interface was NOT intentionally bounced
│       └── Unexpected — Critical → Check for config error → Rollback if unresolved
└── Device is NOT in the change scope
    ├── Peer is on a device that IS in scope (far-end impact)
    │   └── Expected side effect → Verify peer recovers within threshold
    └── Peer is on a device NOT in scope (unrelated)
        └── Unexpected — Critical → Unrelated failure, separate investigation
```

### Route Count Deviation Outside Normal Threshold

```
Route count differs from baseline beyond ±2%
├── Change plan includes prefix addition or removal
│   ├── Deviation direction matches plan (added routes = count increase)
│   │   └── Expected — verify exact prefix matches plan
│   └── Deviation direction opposes plan (planned addition but count decreased)
│       └── Unexpected — Critical → Check BGP/OSPF process, peer state
├── Change plan does NOT include routing changes
│   ├── Deviation is <5% and routes are from in-scope device peers
│   │   └── Warning — likely convergence artifact → Monitor for 3 min
│   └── Deviation is >5% OR routes from out-of-scope sources
│       └── Unexpected — Critical → Evaluate rollback
└── Route oscillation detected (count fluctuating)
    └── Unexpected — Critical → Routing loop or flapping → Immediate rollback
```

## Report Template

```
# Change Verification Report — [Ticket ID]

## Change Summary
- **Ticket:** [ID]
- **Date/Time:** [Start] — [End]
- **Devices:** [list]
- **Change Type:** [routing | switching | security | upgrade | other]
- **Executed By:** [name/team]

## Pre-Change Baseline
- Route count (IPv4/IPv6): [count]
- BGP peers Established: [count]
- OSPF adjacencies Full: [count]
- Interface errors (notable): [any]
- Config archived to: [location]

## Change Execution
- Method: [manual | commit-confirm | session | replace]
- Duration: [minutes]
- Issues during execution: [none | description]

## Post-Change Verification
- Route count (IPv4/IPv6): [count] (Δ [change])
- BGP peers Established: [count] (Δ [change])
- OSPF adjacencies Full: [count] (Δ [change])
- Interface errors (new): [count]
- Config diff lines: [expected: N, unexpected: N]

## Impact Assessment
- Expected — Intended: [list]
- Expected — Side Effect: [list]
- Unexpected — Minor: [list or none]
- Unexpected — Critical: [list or none]

## Decision
- **Result:** [ACCEPTED | ROLLED BACK | ESCALATED]
- **Rationale:** [reason]
- **Soak period:** [duration, outcome]

## Action Items
- [ ] [any follow-up tasks]
```

## Troubleshooting

### Baseline capture commands fail or return incomplete output

- Verify SSH session stability — long command outputs may be truncated by
  terminal buffer limits. Use `terminal length 0` **[Cisco/EOS]** or
  `set cli screen-length 0` **[JunOS]** before capture.
- Check device CPU — high CPU may cause CLI timeouts. Run `show processes cpu`
  **[Cisco]** / `show system processes extensive` **[JunOS]** /
  `show processes top` **[EOS]** to verify.
- If archival to remote storage fails, save to local flash as fallback and
  note the location for later retrieval.

### Config diff shows excessive noise

- Filter out timestamp and comment lines that change on every config display
  (e.g., `! Last configuration change at ...`).
- On **[JunOS]**, `show | compare rollback 1` gives clean structured diffs. On
  **[Cisco]**, `show archive config differences` may include line-order
  differences that are not real changes — focus on substantive config lines.
- Use `references/checklist-templates.md` checklists to focus verification on
  change-relevant sections rather than full config comparison.

### Adjacency does not recover after expected bounce

- Check interface state: `show interfaces [intf]` — look for `down/down` vs
  `up/down` to distinguish physical vs protocol issues.
- Verify the peer device accepted the change — a mismatched configuration on
  both sides of a link (e.g., mismatched OSPF area, BGP ASN) will prevent
  adjacency formation.
- Check for hold-timer expiry: OSPF default dead interval is 40s; BGP default
  hold time is 180s. Wait at least one full timer cycle before escalating.

### Rollback command fails or produces unexpected state

- **[Cisco]** `configure replace` requires the IOS archive feature to be
  enabled. If unavailable, manually reverse the config changes line by line.
- **[JunOS]** `rollback N` may fail if the commit history has been cleared or
  the device has rebooted since the baseline commit. Use
  `show system commit` to verify available rollback points.
- **[EOS]** `configure replace` requires the replacement file to be a complete
  config, not a partial fragment. Verify the archived file is a full
  `show running-config` capture.
- After any rollback, re-run the full post-change verification (Step 4) to
  confirm the device has returned to its pre-change state.

### Change window time exceeded before verification completes

- Prioritize critical services: check routing adjacencies and interface states
  first, defer detailed config diff analysis to after the window if services
  are healthy.
- If the soak period must be shortened, document the reduced observation window
  and schedule a follow-up verification at the next opportunity.
- Escalate if service impact is detected and the change window has closed —
  do not delay rollback due to window constraints if there is active service
  degradation.
