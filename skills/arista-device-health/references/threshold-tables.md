# Arista EOS Threshold Tables

Detailed threshold definitions for EOS device health parameters. EOS runs on
Linux — memory thresholds must account for page cache behavior. MLAG and
VXLAN/EVPN thresholds apply only to data center deployments. Adjust thresholds
per device role and traffic profile.

## CPU Thresholds

### System CPU 5-Minute Average

| Level | Range | Meaning | Action |
|-------|-------|---------|--------|
| Normal | 0–40% | Typical operating range | No action |
| Warning | 41–70% | Elevated load | Identify top agent via `show processes top once` |
| Critical | 71–90% | High load, protocol timer risk | Investigate top agents, reduce load |
| Emergency | > 90% | Control plane at risk | Immediate triage, collect `show tech-support` |

### Per-Agent CPU

| Level | Range | Meaning | Action |
|-------|-------|---------|--------|
| Normal | < 30% | Healthy agent | No action |
| Warning | 30–50% | Agent under load | Monitor, identify workload source |
| Critical | 50–80% | Agent overloaded | Investigate protocol/feature causing load |
| Emergency | > 80% | Agent at risk of watchdog timeout | Immediate investigation, may crash |

## Memory Thresholds

### System Memory (Free %)

EOS uses Linux page cache aggressively. "Used" memory includes reclaimable cache.
Use `bash free -m` `available` column for true available memory.

| Level | Free % (show version) | Available % (bash free) | Action |
|-------|----------------------|------------------------|--------|
| Normal | > 40% | > 50% | No action |
| Warning | 20–40% | 30–50% | Monitor trend, identify large consumers |
| Critical | 10–20% | 15–30% | Investigate growth, check for agent leaks |
| Emergency | < 10% | < 15% | Risk of OOM kills, plan reload, open TAC case |

### Flash Storage

| Level | Used % | Meaning | Action |
|-------|--------|---------|--------|
| Normal | 0–70% | Healthy | No action |
| Warning | 71–85% | Filling | Clean old images, archives |
| Critical | 86–95% | Near full | Remove unused files, compress logs |
| Emergency | > 95% | Full — upgrades and configs at risk | Immediate cleanup |

## Agent Health Thresholds

| Level | Condition | Meaning | Action |
|-------|-----------|---------|--------|
| Normal | All agents running, uptimes match device | Healthy | No action |
| Warning | Agent restarted once (uptime < device uptime) | Recovered from crash | Check agent logs for cause |
| Critical | Agent in crashed/not running state | Subsystem down | Collect logs, attempt restart, escalate |
| Emergency | Multiple agents crashed or restart loop | Systemic instability | Collect show tech, open TAC case |

### Agent Restart Frequency

| Level | Restarts/24hr | Meaning | Action |
|-------|---------------|---------|--------|
| Normal | 0 | Stable | No action |
| Warning | 1 | Single incident | Review logs, monitor |
| Critical | 2–3 | Recurring issue | Investigate root cause, consider image upgrade |
| Emergency | > 3 | Persistent instability | Collect diagnostics, open TAC case |

## Interface Thresholds

### Error Rate

| Level | Rate | Meaning | Action |
|-------|------|---------|--------|
| Normal | < 0.001% | Clean | No action |
| Warning | 0.001–0.01% | Low error rate | Monitor, check optics DOM |
| Critical | 0.01–0.1% | Significant errors | Investigate L1: cable, SFP, fiber |
| Emergency | > 0.1% | High error rate | Replace cable/optic, check remote end |

### Output Discards Per Hour

| Level | Range | Meaning | Action |
|-------|-------|---------|--------|
| Normal | 0–50/hr | Minimal | No action |
| Warning | 51–500/hr | Moderate congestion | Review QoS, check bandwidth |
| Critical | 501–5,000/hr | Significant drops | Tune QoS, consider link upgrade |
| Emergency | > 5,000/hr | Severe congestion | Immediate QoS intervention or upgrade |

### CRC Errors Per Hour

| Level | Range | Meaning | Action |
|-------|-------|---------|--------|
| Normal | 0 | Clean signal | No action |
| Warning | 1–10/hr | Intermittent L1 issue | Monitor, check SFP DOM readings |
| Critical | 11–100/hr | Active L1 problem | Replace cable, clean fiber, reseat SFP |
| Emergency | > 100/hr | Severe L1 failure | Replace cable and SFP, check patch panel |

## MLAG Thresholds

### MLAG Overall State

| Level | Condition | Meaning | Action |
|-------|-----------|---------|--------|
| Normal | Active, connected, peer-link up, consistent | Fully healthy | No action |
| Warning | Config-sanity inconsistency | Mismatch risk | Resolve config differences |
| Critical | Peer-link down or negotiation disconnected | MLAG degraded | Investigate physical link, check heartbeat |
| Emergency | Split-brain (both active, disconnected) | Traffic duplication/loops possible | Emergency: restore peer-link connectivity |

### MLAG Interface State

| Level | Condition | Meaning | Action |
|-------|-----------|---------|--------|
| Normal | active-full | Both peers have member up | No action |
| Warning | active-partial | One peer's member is down | Investigate down member |
| Critical | disabled | MLAG interface down | Check physical interface, port-channel |
| Emergency | Multiple interfaces in disabled state | Widespread MLAG failure | Investigate common cause |

### MLAG Heartbeat

| Level | Condition | Meaning | Action |
|-------|-----------|---------|--------|
| Normal | Heartbeats received on schedule | Healthy control plane | No action |
| Warning | Occasional missed heartbeats | Intermittent issue | Check management network |
| Critical | Sustained heartbeat loss | Control plane risk | Verify management VRF, peer IP |
| Emergency | Complete heartbeat loss with peer-link up | Split-brain risk | Immediate investigation |

## VXLAN/EVPN Thresholds

### VTEP Reachability

| Level | Condition | Meaning | Action |
|-------|-----------|---------|--------|
| Normal | All expected VTEPs present | Full fabric connectivity | No action |
| Warning | 1–2 VTEPs missing | Partial fabric degradation | Check missing VTEP underlay and EVPN |
| Critical | > 10% of VTEPs missing | Significant fabric issue | Check underlay IGP, spine connectivity |
| Emergency | Vxlan1 interface down | Overlay completely down | Check source interface, underlay routing |

### BGP EVPN Peer Health

| Level | Condition | Meaning | Action |
|-------|-----------|---------|--------|
| Normal | All peers Established, stable route count | Healthy control plane | No action |
| Warning | Route count deviation > 10% | Route churn | Investigate upstream changes |
| Critical | Peer not Established | EVPN peering broken | Check transport, ASN, route-map |
| Emergency | Multiple peers down | Fabric control plane failure | Check spine, underlay, BGP config |

## Environment Thresholds

### Temperature

| Level | Condition | Meaning | Action |
|-------|-----------|---------|--------|
| Normal | Below warning threshold | Within operating spec | No action |
| Warning | Above warning, below critical | Approaching limit | Check fans, airflow, ambient cooling |
| Critical | Above critical, below shutdown | Thermal stress | Fix cooling immediately |
| Emergency | At shutdown threshold | Imminent shutdown | Emergency cooling, power off non-essential |

### Power Supply

| Level | Condition | Meaning | Action |
|-------|-----------|---------|--------|
| Normal | All PSUs OK, redundancy active | Fully protected | No action |
| Warning | Single PSU, no redundancy | Unprotected | Plan PSU installation |
| Critical | Redundant PSU failed | Lost redundancy | RMA failed PSU |
| Emergency | Single PSU degraded | Power loss risk | Emergency maintenance |

### Fan/Cooling

| Level | Condition | Meaning | Action |
|-------|-----------|---------|--------|
| Normal | All fans OK, airflow correct | Adequate cooling | No action |
| Warning | Fan speed elevated or airflow mismatch in rack | Reduced efficiency | Check ambient, correct airflow |
| Critical | One fan failed | Thermal risk | RMA fan, monitor temperature |
| Emergency | Multiple fans failed | Thermal shutdown risk | Reduce load, emergency service |
