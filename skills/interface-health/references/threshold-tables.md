# Interface Health Threshold Tables

Detailed severity-tiered thresholds for interface health metrics. All rate
thresholds use per-5-minute intervals (errors/5min) unless noted otherwise.
Adjust thresholds for high-throughput environments or links with known baseline
noise.

## Error Rate Thresholds

### CRC Errors (per 5-minute interval)

| Level | Rate | Meaning | Action |
|-------|------|---------|--------|
| Normal | 0 | Clean signal path | No action |
| Warning | 1–5 | Intermittent physical issue | Monitor trend, check DOM readings |
| Critical | 6–50 | Active physical-layer problem | Inspect cable/fiber, clean connectors, check SFP seating |
| Emergency | >50 | Severe L1 failure | Replace cable and SFP, check patch panel, escalate |

### Frame Errors (per 5-minute interval)

| Level | Rate | Meaning | Action |
|-------|------|---------|--------|
| Normal | 0 | Normal framing | No action |
| Warning | 1–3 | Occasional framing issue | Check duplex settings both ends |
| Critical | 4–25 | Active framing problem | Verify duplex match, check NIC on connected device |
| Emergency | >25 | Severe framing failure | Replace cable, check connected device hardware |

### Input Errors (per 5-minute interval)

Input errors aggregate CRC, frame, overrun, and other receive-path failures.

| Level | Rate | Meaning | Action |
|-------|------|---------|--------|
| Normal | 0–2 | Minimal receive errors | No action |
| Warning | 3–20 | Elevated receive errors | Identify dominant error type (CRC, frame, overrun) |
| Critical | 21–100 | Significant receive-path issue | Investigate physical layer per error subtype |
| Emergency | >100 | Severe receive failure | Immediate physical intervention required |

### Output Errors (per 5-minute interval)

| Level | Rate | Meaning | Action |
|-------|------|---------|--------|
| Normal | 0 | Normal transmission | No action |
| Warning | 1–10 | Occasional transmit failures | Check for congestion, verify interface speed match |
| Critical | 11–50 | Active transmit problem | Investigate interface congestion or hardware fault |
| Emergency | >50 | Severe transmit failure | Check hardware, consider failover to redundant path |

## Discard Rate Thresholds

### Output Discards (per 5-minute interval)

| Level | Rate | Meaning | Action |
|-------|------|---------|--------|
| Normal | 0–10 | Minimal congestion | No action |
| Warning | 11–100 | Moderate congestion or microbursts | Review QoS policy, check bandwidth utilization |
| Critical | 101–1,000 | Significant congestion | Tune QoS scheduling, consider link upgrade |
| Emergency | >1,000 | Severe congestion | Immediate QoS intervention or capacity upgrade |

### Input Discards (per 5-minute interval)

| Level | Rate | Meaning | Action |
|-------|------|---------|--------|
| Normal | 0 | No input drops | No action |
| Warning | 1–10 | Occasional input drops | Check CoPP counters, verify input policer rates |
| Critical | 11–50 | Active input drop issue | Investigate punt rate, input policer configuration |
| Emergency | >50 | Severe input drop rate | Check for traffic flood, review CoPP/input policer |

## Interface Reset/Flap Thresholds

### Resets per Hour

| Level | Rate | Meaning | Action |
|-------|------|---------|--------|
| Normal | 0 | Stable interface | No action |
| Warning | 1–2 | Occasional instability | Monitor, check for transient physical events |
| Critical | 3–10 | Unstable interface | Investigate root cause: physical, STP, auto-neg |
| Emergency | >10 | Rapidly flapping | Shut interface to stop network-wide impact, investigate offline |

### Time Since Last Flap

| Level | Duration | Meaning | Action |
|-------|----------|---------|--------|
| Normal | >7 days | Stable | No action |
| Warning | 1–7 days | Recent flap event | Verify recovery, check error counters post-flap |
| Critical | 1–24 hours | Recent instability | Active investigation required |
| Emergency | <1 hour | Currently unstable | Immediate investigation, consider shutting interface |

## Optical Power Thresholds

Optical thresholds are SFP-type-specific. Always verify against the actual
DOM alarm/warning thresholds embedded in the SFP EEPROM, which reflect the
manufacturer's specifications for that exact part.

### 1G-SX (SFP, 850nm, MMF, max 550m)

| Parameter | Normal | Warning | Critical | Emergency |
|-----------|--------|---------|----------|-----------|
| Tx Power | -2 to -9 dBm | -9 to -9.5 dBm | -9.5 to -10 dBm | < -10 dBm |
| Rx Power | -1 to -17 dBm | -17 to -19 dBm | -19 to -20 dBm | < -20 dBm |
| Laser Bias | 2–15 mA | 15–20 mA | 20–25 mA | >25 mA |
| Temperature | 0–55°C | 55–65°C | 65–70°C | >70°C |

### 10G-SR (SFP+, 850nm, MMF, max 300m OM3 / 400m OM4)

| Parameter | Normal | Warning | Critical | Emergency |
|-----------|--------|---------|----------|-----------|
| Tx Power | -1 to -7.3 dBm | -7.3 to -8 dBm | -8 to -8.5 dBm | < -8.5 dBm |
| Rx Power | 0.5 to -9.9 dBm | -9.9 to -11 dBm | -11 to -12 dBm | < -12 dBm |
| Laser Bias | 2–12 mA | 12–16 mA | 16–20 mA | >20 mA |
| Temperature | 0–70°C | 70–78°C | 78–85°C | >85°C |

### 10G-LR (SFP+, 1310nm, SMF, max 10km)

| Parameter | Normal | Warning | Critical | Emergency |
|-----------|--------|---------|----------|-----------|
| Tx Power | -1 to -6 dBm | -6 to -7 dBm | -7 to -8.2 dBm | < -8.2 dBm |
| Rx Power | 0.5 to -14.4 dBm | -14.4 to -16 dBm | -16 to -18 dBm | < -18 dBm |
| Laser Bias | 5–40 mA | 40–55 mA | 55–70 mA | >70 mA |
| Temperature | -5–75°C | 75–82°C | 82–90°C | >90°C |

### 25G-SR (SFP28, 850nm, MMF, max 100m OM4)

| Parameter | Normal | Warning | Critical | Emergency |
|-----------|--------|---------|----------|-----------|
| Tx Power | -1 to -7 dBm | -7 to -8 dBm | -8 to -8.5 dBm | < -8.5 dBm |
| Rx Power | 0.5 to -10.3 dBm | -10.3 to -12 dBm | -12 to -13 dBm | < -13 dBm |
| Laser Bias | 2–12 mA | 12–16 mA | 16–20 mA | >20 mA |
| Temperature | 0–70°C | 70–78°C | 78–85°C | >85°C |

### 100G-SR4 (QSFP28, 850nm, MMF, max 70m OM3 / 100m OM4)

| Parameter | Normal | Warning | Critical | Emergency |
|-----------|--------|---------|----------|-----------|
| Tx Power (per lane) | -1 to -7.6 dBm | -7.6 to -8.5 dBm | -8.5 to -9 dBm | < -9 dBm |
| Rx Power (per lane) | 0.5 to -9.5 dBm | -9.5 to -11 dBm | -11 to -12 dBm | < -12 dBm |
| Laser Bias (per lane) | 2–12 mA | 12–16 mA | 16–20 mA | >20 mA |
| Temperature | 0–70°C | 70–78°C | 78–85°C | >85°C |

**Notes on multi-lane optics (100G-SR4):**
- 100G-SR4 uses 4 lanes. Each lane has independent Tx/Rx power and laser bias.
  A single degraded lane can cause CRC errors even when aggregate power looks
  acceptable. Check per-lane DOM readings individually.
- Some platforms report only aggregate power. If per-lane data is unavailable,
  use the aggregate thresholds above multiplied by 4 for total power
  assessment, but be aware this masks per-lane problems.

## Utilization Thresholds

### Bandwidth Utilization (5-minute average)

| Level | Utilization | Meaning | Action |
|-------|-------------|---------|--------|
| Normal | 0–50% | Healthy headroom | No action |
| Warning | 51–75% | Elevated usage | Monitor trend, plan capacity if sustained |
| Critical | 76–90% | High utilization | Evaluate upgrade path, optimize traffic distribution |
| Emergency | >90% | Near saturation | Immediate action: upgrade, ECMP, traffic engineering |

### Peak vs Sustained Utilization

Sustained utilization (5-minute average) drives capacity planning. Peak
utilization (1-second or sub-second bursts) drives QoS and buffer tuning.

| Scenario | Sustained | Peak Indicator | Action |
|----------|-----------|----------------|--------|
| Both low | <50% avg | No discards | Healthy — no action |
| Sustained low, peaks high | <50% avg | Output discards present | Microburst activity — tune buffers/QoS |
| Sustained high, peaks low | >75% avg | Minimal discards | Steady load — plan capacity upgrade |
| Both high | >75% avg | High discards | Congested — immediate capacity review |

## Error Rate as Percentage of Traffic

For high-throughput links, absolute error counts may be less meaningful than
error-to-packet ratios. Use this table when an interface processes millions of
packets per 5-minute interval.

| Level | Error Rate | Meaning | Action |
|-------|-----------|---------|--------|
| Normal | < 0.0001% (1 in 1M) | Negligible error rate | No action |
| Warning | 0.0001–0.001% | Low but measurable | Monitor, check DOM if fiber |
| Critical | 0.001–0.01% | Significant error rate | Investigate physical layer |
| Emergency | > 0.01% (1 in 10K) | High error rate | Immediate physical intervention |
