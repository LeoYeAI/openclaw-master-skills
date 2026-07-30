# Interface Health CLI Reference

Multi-vendor command reference for interface diagnostics. Organized by
diagnostic category with Cisco IOS-XE/NX-OS, Juniper JunOS, and Arista EOS
commands side by side.

## Interface Status Commands

| Purpose | Cisco IOS-XE | Cisco NX-OS | JunOS | EOS |
|---------|-------------|-------------|-------|-----|
| Interface summary (all) | `show interfaces status` | `show interface status` | `show interfaces terse` | `show interfaces status` |
| Single interface detail | `show interfaces [intf]` | `show interface [intf]` | `show interfaces [intf]` | `show interfaces [intf]` |
| Admin/oper state + speed | `show interfaces [intf] \| include line protocol\|BW\|duplex` | `show interface [intf] \| include "admin\|oper\|speed\|duplex"` | `show interfaces [intf] \| match "Physical\|Speed\|Duplex"` | `show interfaces [intf] \| include line protocol\|BW\|duplex` |
| Interface description | `show interfaces description` | `show interface description` | `show interfaces descriptions` | `show interfaces description` |
| Hardware/media type | `show interfaces [intf] \| include Hardware\|media` | `show interface [intf] \| include "Hardware\|Type"` | `show interfaces [intf] \| match "Link-level type"` | `show interfaces [intf] \| include Hardware\|Type` |

**Interpretation notes:**
- IOS-XE uses `show interfaces` (plural). NX-OS uses `show interface` (singular).
- JunOS `terse` output is a compact table; `detail` and `extensive` add progressively more information.
- EOS syntax closely mirrors IOS-XE in most cases.

## Error Counter Commands

| Purpose | Cisco IOS-XE | Cisco NX-OS | JunOS | EOS |
|---------|-------------|-------------|-------|-----|
| All error counters | `show interfaces [intf] \| include errors\|CRC\|frame\|runts\|giants` | `show interface [intf] \| include "errors\|CRC\|frame\|runts\|giants"` | `show interfaces [intf] extensive \| match "Errors\|CRC\|Framing\|Runts\|Giants"` | `show interfaces [intf] counters errors` |
| Error counter table | `show interfaces [intf] counters errors` | `show interface [intf] counters errors` | N/A (use `extensive`) | `show interfaces [intf] counters errors` |
| Clear counters | `clear counters [intf]` | `clear counters interface [intf]` | `clear interfaces statistics [intf]` | `clear counters [intf]` |
| Counter snapshot (delta) | Take two reads, compute delta | Take two reads, compute delta | `show interfaces [intf] extensive` (includes rate fields) | Take two reads, compute delta |

**Interpretation notes:**
- JunOS `extensive` output includes per-second and per-interval rate fields inline — delta computation is less necessary.
- NX-OS `show interface [intf] counters` provides packet/byte counts; use `counters errors` specifically for error counters.
- Clearing counters affects only the CLI display counters, not SNMP counters or streaming telemetry.

## Discard and Queue Commands

| Purpose | Cisco IOS-XE | Cisco NX-OS | JunOS | EOS |
|---------|-------------|-------------|-------|-----|
| Input/output discards | `show interfaces [intf] \| include drops\|discard` | `show interface [intf] \| include "drops\|discard"` | `show interfaces [intf] extensive \| match "Drops"` | `show interfaces [intf] counters discards` |
| QoS policy stats | `show policy-map interface [intf]` | `show queuing interface [intf]` | `show class-of-service interface [intf]` | `show qos interface [intf]` |
| Queue depth/drops | `show platform hardware qfp active interface [intf] stats` | `show queuing interface [intf] detail` | `show interfaces queue [intf]` | `show interfaces [intf] counters queue` |
| Buffer allocation | `show buffers` | `show hardware internal buffer info` | `show chassis fabric summary` | `show platform trident buffers` |

**Interpretation notes:**
- QoS command structures differ significantly across vendors. Cisco uses `policy-map`, JunOS uses `class-of-service`, EOS uses `qos`.
- NX-OS `show queuing` is the primary QoS monitoring command (not `show policy-map interface`).
- Buffer visibility varies by platform. The commands above are representative; specific models may use different commands.

## Interface Reset and Flap Commands

| Purpose | Cisco IOS-XE | Cisco NX-OS | JunOS | EOS |
|---------|-------------|-------------|-------|-----|
| Reset count | `show interfaces [intf] \| include resets` | `show interface [intf] \| include "resets"` | `show interfaces [intf] extensive \| match "Resets"` | `show interfaces [intf] \| include resets` |
| Last state change | `show interfaces [intf] \| include "Last input\|Last output\|last change"` | `show interface [intf] \| include "Last link"` | `show interfaces [intf] extensive \| match "Last flapped"` | `show interfaces [intf] \| include "Last input\|Last output"` |
| Flap history from logs | `show logging \| include [intf].*UPDOWN` | `show logging logfile \| include [intf].*UPDOWN` | `show log messages \| match [intf].*UP\|[intf].*DOWN` | `show logging \| include [intf].*up\|[intf].*down` |
| Error-disable status | `show interfaces status err-disabled` | `show interface status err-disabled` | N/A (JunOS does not use error-disable) | `show errdisable status` |

**Interpretation notes:**
- JunOS does not have an "error-disable" concept — ports are administratively disabled or operationally down, but there is no automatic error-disable mechanism like Cisco/EOS.
- IOS-XE "resets" counter in `show interfaces` includes both carrier transitions and software resets. NX-OS separates them in detailed output.
- EOS flap history is best checked via `show logging` filtered for the interface name.

## Optical/Transceiver Commands

| Purpose | Cisco IOS-XE | Cisco NX-OS | JunOS | EOS |
|---------|-------------|-------------|-------|-----|
| DOM readings (all optics) | `show interfaces transceiver` | `show interface transceiver details` | `show interfaces diagnostics optics` | `show interfaces transceiver` |
| Single interface DOM | `show interfaces [intf] transceiver detail` | `show interface [intf] transceiver details` | `show interfaces diagnostics optics [intf]` | `show interfaces [intf] transceiver detail` |
| SFP inventory/type | `show interfaces [intf] transceiver \| include type\|vendor\|serial` | `show interface [intf] transceiver \| include "type\|vendor\|serial"` | `show chassis hardware \| match "Xcvr"` | `show inventory \| include [intf]` |
| Alarm thresholds | `show interfaces [intf] transceiver detail` (includes thresholds) | `show interface [intf] transceiver details` (includes thresholds) | `show interfaces diagnostics optics [intf]` (includes thresholds) | `show interfaces [intf] transceiver threshold` |

**Interpretation notes:**
- DOM output format differs: Cisco shows Tx/Rx power in dBm and mW. JunOS shows dBm only. EOS shows dBm with alarm/warning flags.
- NX-OS uses `transceiver details` (plural). IOS-XE uses `transceiver detail` (singular).
- All three vendors embed the SFP's alarm and warning thresholds in the DOM output — compare actual readings against these thresholds, not just the generic thresholds in the skill's threshold tables.
- JunOS uses `diagnostics optics` (not `transceiver`) as the primary DOM command.

## Utilization Commands

| Purpose | Cisco IOS-XE | Cisco NX-OS | JunOS | EOS |
|---------|-------------|-------------|-------|-----|
| Input/output rate | `show interfaces [intf] \| include "input rate\|output rate"` | `show interface [intf] \| include "input rate\|output rate"` | `show interfaces [intf] traffic` | `show interfaces [intf] \| include "input rate\|output rate"` |
| Counter-based rates | `show interfaces [intf] summary` | `show interface [intf] counters` | `show interfaces [intf] statistics traffic` | `show interfaces [intf] counters rates` |
| Reliability metric | `show interfaces [intf] \| include reliability` | N/A (NX-OS does not report reliability) | N/A | N/A |
| Interface load (fraction) | `show interfaces [intf] \| include "load\|reliability"` | N/A | N/A | N/A |

**Interpretation notes:**
- IOS-XE reports "reliability" as a fraction of 255 (255/255 = 100% reliable) and "load" as txload/rxload fractions of 255. These are unique to IOS-XE.
- All vendors report input/output rates as bits per second. The averaging interval is typically 5 minutes (configurable via `load-interval` on Cisco).
- JunOS `show interfaces [intf] traffic` provides rate data including peak rates. The `statistics traffic` variant provides accumulated counters.
- To calculate utilization percentage: (rate in bps / interface speed in bps) × 100.
