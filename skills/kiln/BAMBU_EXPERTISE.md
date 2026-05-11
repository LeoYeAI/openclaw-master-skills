# Bambu Lab Subject Matter Expertise

> Internal reference for maximizing Kiln + Bambu integration quality.
> Last updated: 2026-03-04

---

## Table of Contents
1. [Company & Product Line](#company--product-line)
2. [A1 Combo Deep Dive (Adam's Printer)](#a1-combo-deep-dive)
3. [MQTT Protocol Reference](#mqtt-protocol-reference)
4. [FTPS File Transfer](#ftps-file-transfer)
5. [AMS System](#ams-system)
6. [Material System](#material-system)
7. [Print Quality & Speed Profiles](#print-quality--speed-profiles)
8. [Firmware & Ecosystem](#firmware--ecosystem)
9. [Common Issues & Fixes](#common-issues--fixes)
10. [Gap Analysis: Kiln vs Bambu Capabilities](#gap-analysis)
11. [Improvement Proposals](#improvement-proposals)

---

## Company & Product Line

**Bambu Lab** was founded in 2020 in Shenzhen by Dr. Ye Tao (ex-DJI) and three other engineers. Their thesis: consumer 3D printers were too hard to use. They automated away calibration, leveling, and tuning — making printing as close to "push button, get part" as possible.

### Product Lineup (2026)

| Model | Type | Build Volume | Max Speed | Enclosure | Key Feature | Price |
|-------|------|-------------|-----------|-----------|-------------|-------|
| **A1 mini** | Bed slinger | 180x180x180mm | 500mm/s | No | Compact entry-level | ~$249/$399 combo |
| **A1** | Bed slinger | 256x256x256mm | 500mm/s | No | Full-size open frame | ~$399/$559 combo |
| **P1S** | CoreXY | 256x256x256mm | 500mm/s | Yes | Enclosed workhorse | ~$699 |
| **P2S** | CoreXY | 256x256x256mm | 600mm/s | Yes | Next-gen, PMSM motor, dual WiFi | ~$549/$799 combo |
| **X1 Carbon** | CoreXY | 256x256x256mm | 500mm/s | Yes | LiDAR + AI spaghetti detection | ~$1,199 |
| **H2S** | Industrial | 340x320x340mm | 1000mm/s | Yes | 65C heated chamber, laser option | ~$1,499 |
| **H2D** | Industrial | 350x320x325mm | 1000mm/s | Yes | Dual nozzle | ~$1,749 |
| **H2C** | Industrial | Varies | 1000mm/s | Yes | 6-tool changer (Vortek) | ~$2,399 |

### Key Differentiators

| Feature | A1/A1 mini | P1S/P2S | X1 Carbon | H2 Series |
|---------|-----------|---------|-----------|-----------|
| Enclosure | No | Yes | Yes | Yes + active heating |
| LiDAR | No | No | Yes | Yes |
| AI spaghetti detection | No | No | Yes | Yes |
| Max bed temp | 80-100C | 100-120C | 120C | Higher |
| Heated chamber | No | Passive only | Passive only | Active 65C |
| WiFi | 2.4GHz only | 2.4 (P1S), dual (P2S) | 2.4GHz | Dual |
| AMS type | AMS Lite | AMS/AMS 2 Pro | AMS/AMS 2 Pro | AMS/AMS 2 Pro |
| Engineering materials | Limited (PLA/PETG/TPU) | Full range | Full range | Full + high-temp |

---

## A1 Combo Deep Dive

> Adam's printer: IP `192.168.1.6`, Access code `26509325`, Serial `03900D5C2513213`

### Specifications

| Spec | Value |
|------|-------|
| Build volume | 256 x 256 x 256 mm |
| Max toolhead speed | 500 mm/s |
| Max acceleration | 10,000 mm/s^2 |
| Max nozzle temp | 300C |
| Max bed temp | 100C |
| Layer height (0.4mm nozzle) | 0.08 - 0.28mm |
| Extruder | All-metal direct drive, quick-swap hotend |
| Bed surface | PEI-coated flexible steel plate |
| Camera | 1080p, ~1 FPS streaming |
| Connectivity | WiFi 2.4GHz, microSD, Bambu Cloud, LAN mode |
| Noise | <48 dB in silent mode |
| Power | 100-240 VAC, ~350W at 110V |
| Weight | 8.3 kg |

### Nozzle Options (single-clip toolless swap)
- 0.2mm stainless steel
- **0.4mm stainless steel** (default)
- 0.4mm hardened steel (for CF/GF filaments)
- 0.6mm hardened steel
- 0.8mm hardened steel

### AMS Lite (Included in Combo)
- **Capacity**: 4 spools (up to 4-color printing)
- **Mechanism**: Each slot has its own motor. A filament hub merges 4 paths into 1 using a brushless motor with hall sensors and magnetic rotary encoder.
- **Buffer system**: Spring-loaded buffer at back monitors filament tension so extruder can pull without resistance.
- **RFID**: Reads Bambu-branded spool tags to auto-configure print settings. Third-party filament works but requires manual profile entry.
- **Humidity**: Open-air design — NO humidity seal (unlike AMS 2 Pro). Use an external filament dryer in humid environments.
- **Limitations**:
  - Only 1 AMS Lite per A1 (no daisy-chaining)
  - NOT designed for TPU, TPE, or abrasive filaments
  - PTFE tubes are consumables — replace periodically under heavy use

### Auto-Calibration System (runs before every print)
1. **Z-offset**: Strain-based — uses nozzle tip as contact sensor (no separate probe)
2. **Bed leveling**: Automatic mesh leveling via strain gauge
3. **Vibration compensation**: Measures resonant frequencies with built-in accelerometers, adjusts motion to cancel ringing
4. **Pressure advance**: Compensates for filament compression hysteresis in hotend
5. **Flow calibration**: Measures dynamic extrusion response at different flow rates for real-time compensation

### Camera System
- 1080p built-in camera
- ~1 FPS refresh rate (not smooth video)
- RTSP stream: `rtsps://{host}:322/streaming/live/1`
- **No native AI features** — spaghetti detection and LiDAR are X1 Carbon exclusive
- Third-party tools (Obico) can add AI failure detection via external camera

### What the A1 Does NOT Have (vs X1 Carbon)
- No LiDAR first-layer inspection
- No AI spaghetti detection
- No enclosed build chamber (can't reliably print ABS/ASA/PC)
- No heated chamber
- No 5GHz WiFi
- No AMS daisy-chaining
- Max bed temp 100C (vs 120C on X1C)

### Best Practices for Great Prints
1. **Bed maintenance**: Wash PEI plate with hot water + dish soap (not just IPA). Never touch print surface with fingers.
2. **Keep auto-calibration ON** for every print — don't skip it to save time.
3. **Brims for small objects** to prevent warping/detachment on bed-slinger.
4. **Dry filament** before use, especially PETG. AMS Lite has no humidity control.
5. **Line width 0.5mm / layer height 0.25mm** for first-layer adhesion issues.
6. **Replace PTFE tubes** regularly if using AMS Lite heavily.
7. **Manual feed for TPU** — don't use AMS Lite for flexible filaments.
8. **Standard materials only on open frame**: PLA, PETG, PLA-CF, PLA Silk, TPU. Skip ABS/ASA/PA/PC without an aftermarket enclosure.

---

## MQTT Protocol Reference

### Connection Parameters

**Local LAN (Kiln uses this):**
- Host: `{PRINTER_IP}:8883`
- TLS: Required (TLS 1.2)
- Username: `bblp`
- Password: LAN access code (from printer screen > WiFi settings)
- Protocol: MQTTv3.1.1

**Cloud (not currently supported in Kiln):**
- Host: `us.mqtt.bambulab.com:8883`
- Username: `u_{USER_ID}`
- Password: Full access token from Bambu account

### Topics
- **Subscribe (printer reports):** `device/{SERIAL}/report`
- **Publish (commands):** `device/{SERIAL}/request`

All messages are JSON. Every command includes `"sequence_id": "N"` (incrementing string).

### Getting Full Status
```json
{"pushing": {"sequence_id": "0", "command": "pushall"}}
```
**IMPORTANT**: On A1 and P1 series, printers send **delta updates only** (only changed values). Use `pushall` to get complete state, but rate-limit to once every 5 minutes max. Only one local MQTT client is reliably supported at a time.

### Status Report Fields (from `push_status`)

| Category | Fields |
|----------|--------|
| **Temperatures** | `nozzle_temper`, `nozzle_target_temper`, `bed_temper`, `bed_target_temper`, `chamber_temper` |
| **State** | `gcode_state`: `IDLE`, `RUNNING`, `PAUSE`, `FINISH`, `FAILED`, `PREPARE`, `SLICING`, `INIT`, `CANCELLING` |
| **Progress** | `mc_percent` (0-100), `mc_remaining_time` (minutes), `layer_num`, `total_layer_num` |
| **Fans** | `cooling_fan_speed`, `big_fan1_speed` (aux), `big_fan2_speed` (chamber), `heatbreak_fan_speed` |
| **Speed** | `spd_lvl` (1-4), `spd_mag` (actual multiplier %) |
| **AMS** | Array of AMS units → trays with: `tray_id`, `tray_type`, `tray_color`, `remain`, `tag_uid`, temps, humidity |
| **Lights** | `lights_report` array |
| **Hardware** | `home_flag`, `hw_switch_state`, `sdcard`, `wifi_signal` |
| **Print info** | `gcode_file`, `subtask_name`, `print_type` (`idle`, `local`, `cloud`) |
| **HMS errors** | `hms_*` fields with structured error codes |
| **Print errors** | `print_error` field when `gcode_state == "FAILED"` |

### Command Reference

#### Print Control
```json
{"print": {"sequence_id": "0", "command": "pause"}}
{"print": {"sequence_id": "0", "command": "resume"}}
{"print": {"sequence_id": "0", "command": "stop"}}
```

#### Start Print (3MF)
```json
{"print": {
  "sequence_id": "0",
  "command": "project_file",
  "param": "Metadata/plate_1.gcode",
  "project_id": "0",
  "profile_id": "0",
  "task_id": "0",
  "subtask_id": "0",
  "subtask_name": "",
  "bed_leveling": true,
  "flow_cali": true,
  "vibration_cali": true,
  "layer_inspect": false,
  "ams_mapping": [0],
  "use_ams": true,
  "timelapse": false,
  "bed_type": "auto"
}}
```

#### Start Print (G-code)
```json
{"print": {"sequence_id": "0", "command": "gcode_file", "param": "filename.gcode"}}
```

#### Speed Profiles
```json
{"print": {"sequence_id": "0", "command": "print_speed", "param": "2"}}
```
| Value | Mode | Multiplier |
|-------|------|------------|
| `"1"` | Silent | 50% |
| `"2"` | Standard | 100% |
| `"3"` | Sport | 124% |
| `"4"` | Ludicrous | 166% |

Sport and Ludicrous auto-increase nozzle temp to prevent under-extrusion.

#### LED Control
```json
{"system": {"sequence_id": "0", "command": "ledctrl", "led_node": "chamber_light", "led_mode": "on"}}
```
Nodes: `chamber_light`, `work_light`. Modes: `on`, `off`, `flashing`.

#### Send G-code
```json
{"print": {"sequence_id": "0", "command": "gcode_line", "param": "G28\nM104 S200\n"}}
```
Supports `\n`-separated multiple lines.

#### AMS Control
```json
{"print": {"sequence_id": "0", "command": "ams_change_filament", "target": 0, "curr_temp": 220, "tar_temp": 220}}
{"print": {"sequence_id": "0", "command": "ams_filament_setting", "ams_id": 0, "tray_id": 0, "tray_color": "FF0000FF", "nozzle_temp_min": 190, "nozzle_temp_max": 230, "tray_type": "PLA"}}
```

#### Camera
```json
{"camera": {"sequence_id": "0", "command": "ipcam_record_set", "control": "enable"}}
{"camera": {"sequence_id": "0", "command": "ipcam_timelapse", "control": "enable"}}
```

#### Print Options
```json
{"print": {"sequence_id": "0", "command": "print_option", "auto_recovery": true}}
```

#### Skip Objects (mid-print)
```json
{"print": {"sequence_id": "0", "command": "skip_objects", "obj_list": [1, 3]}}
```

#### Set Nozzle Type
```json
{"system": {"sequence_id": "0", "command": "set_accessories", "accessory_type": "nozzle", "nozzle_diameter": "0.4", "nozzle_type": "stainless_steel"}}
```

#### Get Version Info
```json
{"info": {"sequence_id": "0", "command": "get_version"}}
```

---

## FTPS File Transfer

- Protocol: **Implicit FTPS** (FTP over TLS), NOT SFTP
- Port: **990**
- Username: `bblp`
- Password: Same LAN access code as MQTT
- Upload path: `/sdcard/{filename}`
- Supports `.gcode` and `.3mf` files
- TLS session reuse required on data channels (Bambu-specific requirement)
- Works in both Cloud and LAN-only modes

---

## AMS System

### AMS Lite (A1 / A1 mini)
- 4 spool slots, single unit (no chaining)
- Open-air (no humidity seal)
- RFID reader for Bambu filaments
- Spring-loaded buffer monitors tension
- Each slot has independent feed motor

### AMS / AMS 2 Pro (P series, X1 Carbon)
- 4 spool slots, up to 4 units = 16 colors
- AMS: Sealed chamber with desiccant
- AMS 2 Pro: Active drying with heated venting + built-in humidity sensor
- Full RFID support

### MQTT AMS Data Structure
Each AMS unit reports an array of trays:
```
ams[unit_id].tray[slot_id]:
  tray_id, tray_type, tray_color (hex RRGGBBAA),
  tray_weight, remain (%), tag_uid (RFID),
  nozzle_temp_min, nozzle_temp_max, bed_temp,
  drying_temp, drying_time, humidity
```

### AMS Mapping for Print Jobs
- 5-element array with reverse indexing
- `-1` = unused slot
- Example: `[0, 1, -1, -1]` maps first two filaments to AMS slots 0 and 1

---

## Material System

### Materials by Printer Type

**A1 / A1 mini (no enclosure) — RECOMMENDED:**
- PLA, PLA+, PLA Silk, PLA-CF
- PETG, PETG-CF
- TPU (manual feed, NOT through AMS Lite)

**A1 / A1 mini — NOT RECOMMENDED (no enclosure):**
- ABS, ASA (warp badly without enclosure)
- PA/Nylon (moisture-sensitive, needs enclosure)
- PC (needs high chamber temp)

**P1S / P2S / X1 Carbon (enclosed):**
- Full range: PLA, PETG, ABS, ASA, PA, PC, PVA, TPU, PET, PP, POM, HIPS
- With hardened nozzle: PLA-CF, PAHT-CF, PETG-CF, PA-CF/GF, PET-CF

### RFID System
- Bambu-branded spools contain RFID tags
- Auto-configures: filament type, color, temperature ranges, print profile
- Third-party filament: works fine, but requires manual profile entry in slicer
- Some community tools can write RFID tags for third-party spools

### Temperature Reference (common materials on A1)

| Material | Nozzle (C) | Bed (C) | Notes |
|----------|-----------|---------|-------|
| PLA | 200-220 | 55-65 | Default, easiest |
| PETG | 230-250 | 70-80 | Dry before use, can string |
| PLA-CF | 220-240 | 55-65 | Needs hardened nozzle |
| TPU | 220-240 | 50-60 | Manual feed only, slow speeds |
| PLA Silk | 200-220 | 55-65 | Lower speeds for shine |

---

## Print Quality & Speed Profiles

### Speed Modes
| Mode | Multiplier | MQTT Value | Best For |
|------|-----------|------------|----------|
| Silent | 50% | `"1"` | Overnight, noise-sensitive |
| Standard | 100% | `"2"` | Balanced quality/speed (default) |
| Sport | 124% | `"3"` | Faster, still good quality |
| Ludicrous | 166% | `"4"` | Maximum speed, quality tradeoffs |

### Quality Features (all automatic on A1)
- **Input shaping**: Cancels resonant frequencies to eliminate ringing/ghosting at high speeds
- **Pressure advance**: Compensates for filament lag during acceleration/deceleration
- **Flow calibration**: Real-time extrusion compensation based on measured flow response
- **Auto bed leveling**: Strain-gauge mesh leveling every print

### Multi-Color Workflow (AMS Lite)
1. Assign colors in Bambu Studio (paint tool or multi-part)
2. Load 4 filaments in AMS Lite slots
3. Slicer generates purge tower + color-change G-code
4. During print: AMS retracts old filament → feeds new → purges at nozzle
5. **Waste tips**: Use "flush into infill" to reduce purge tower waste; tune flush volumes per color pair; dark-to-light transitions waste the most

---

## Firmware & Ecosystem

### Bambu Studio
- Based on PrusaSlicer, deeply integrated with Bambu hardware
- Multi-plate system, AMS mapping, calibration toggles, speed profiles
- Multi-color painting and splitting tools
- Exports .3mf project files (richer than raw .gcode)
- Free, open-source (GitHub)

### OrcaSlicer (Community Alternative)
- Fork of Bambu Studio by SoftFever
- Supports non-Bambu printers
- More granular speed/acceleration settings
- "Sandwich mode" wall ordering
- Popular in the community, widely used with Bambu printers

### Cloud vs LAN Mode

| Feature | Cloud Mode | LAN-Only Mode |
|---------|-----------|---------------|
| Remote access | Yes (Bambu Handy) | No |
| Print history | Yes | No |
| Firmware OTA | Yes | SD card only |
| Data routing | Through Bambu servers | Local network only |
| Auth | Bambu account | Printer access code |
| MQTT/FTPS | Both work | Both work |
| Privacy | Shared with Bambu | Fully local |

**Kiln uses LAN mode** — all communication stays local.

### 2025 Authorization Controversy
- Firmware update required authorization for critical operations
- Community backlash over third-party slicer restrictions
- Bambu added "Developer Mode" under LAN mode in response
- Community researchers extracted TLS certificates for local auth

---

## Common Issues & Fixes

### A1 Combo Specific

| Issue | Cause | Fix |
|-------|-------|-----|
| **PTFE tube loosening** in AMS Lite hub | Wear from repeated load/unload | Replace PTFE tubes; check 4-in-1 adapter seating |
| **AMS extrusion failures** | Clog, worn tube, or tangled filament | Clean path, replace tube, check spool |
| **WiFi disconnects** | 2.4GHz only, special chars in password | Use simple password, set up dedicated 2.4GHz network |
| **Poor bed adhesion** | Oil contamination on PEI | Wash with hot water + dish soap (NOT just IPA) |
| **First layer issues** | Dirty nozzle during calibration | Clean nozzle before starting, keep auto-calibration on |
| **Parts detaching mid-print** | Bed-slinger motion shaking loose small parts | Add brims, increase bed temp slightly, clean bed |
| **No spaghetti detection** | A1 doesn't have AI camera features | Use third-party (Obico) or check periodically |

### General Bambu Issues

| Issue | Fix |
|-------|-----|
| MQTT connection refused | Check: LAN mode enabled, access code correct, port 8883, TLS enabled |
| Only one client connects | Bambu supports ~1 local MQTT client at a time; close Bambu Studio |
| FTPS upload fails | Verify port 990, TLS session reuse, correct access code |
| 3MF won't start | Check `ams_mapping` array, verify file path starts with `Metadata/plate_1.gcode` |
| Status shows stale data | A1/P1 send delta updates; use `pushall` (max once per 5 min) |

---

## Gap Analysis

### What Kiln Does Well Today (Bambu)

Kiln has a **solid, production-quality Bambu adapter** (`bambu.py`, 1,367 lines, excellent test coverage). The fundamentals are strong:

- Full MQTT lifecycle with exponential backoff and stale-message rejection
- TOFU TLS pinning (unique security feature most tools don't have)
- Complete print control (start, cancel, pause, resume, emergency stop)
- File management via FTPS with multi-strategy fallback (MLSD → NLST → LIST)
- Temperature control with safety profile validation
- Camera snapshot/stream via RTSP
- G-code validation with Bambu-specific dialect (blocks M600)
- Printer intelligence for 5 Bambu models (materials, quirks, failure modes)
- 100+ tests covering edge cases, error paths, and interface compliance

### What's Missing — Categorized by Impact

#### HIGH IMPACT (Would meaningfully improve daily use)

1. **AMS Status & Control** — The AMS Lite is half the value of the "Combo" but Kiln can't see what's loaded, can't select filaments, and hardcodes `use_ams: False`. For Adam's multi-color prints, this is the #1 gap.

2. **Speed Profile Control** — Can't switch between Silent/Standard/Sport/Ludicrous via Kiln. During a long print, switching to Silent mode at night or Sport during the day is a common workflow.

3. **Print Start Options** — `start_print` hardcodes 8 parameters that should be configurable: AMS mapping, calibration toggles, timelapse, bed type, layer inspect, and multi-plate selection.

4. **HMS Error Code Parsing** — When a print fails, Bambu sends structured error codes with detailed diagnostics. Kiln currently just shows "FAILED" with no explanation.

5. **Richer Print Status** — Layer count, fan speeds, nozzle type, print weight, filament used — all available in MQTT but not extracted. These are valuable for monitoring and agent decision-making.

#### MEDIUM IMPACT (Nice quality-of-life features)

6. **LED/Light Control** — Toggle chamber light and work light on/off. Simple MQTT command, useful for camera visibility and workshop lighting.

7. **Skip Objects Mid-Print** — Bambu supports skipping failed objects without canceling the whole print. Powerful for batch prints.

8. **Print Error Details** — When `gcode_state == "FAILED"`, extract the `print_error` field for actionable diagnostics.

9. **WiFi Signal Strength** — Available in MQTT push, useful for diagnosing connection issues in fleet setups.

10. **RTSP Authentication** — Some firmware versions require the access code for camera streams. Current implementation doesn't pass credentials.

#### LOWER IMPACT (Advanced/niche)

11. **Multi-Plate 3MF Support** — Select which plate to print in a multi-plate 3MF. Niche but useful for batch workflows.

12. **Filament Sensor Status** — Programmatic query of filament runout sensor state.

13. **Bed Mesh Data** — Access auto-leveling mesh data for diagnostics.

14. **Chamber Temperature Target** — Set/read chamber temp target (mostly relevant for enclosed printers, less so for A1).

15. **Cloud API Integration** — Enable remote access without LAN. Low priority since Kiln targets local networks.

16. **Firmware Update Support** — Push firmware updates via Kiln. Risky, low priority.

---

## Improvement Proposals

> For Adam to vote on. Each proposal is self-contained with effort estimate and value assessment.

### Proposal 1: AMS Intelligence
**Value**: HIGH | **Effort**: Medium (2-3 hours)
**What**: Add MCP tools to query AMS status (what's loaded in each slot: filament type, color, remaining %, humidity) and control AMS (load/unload filament, set slot configuration). Make `start_print` AMS-aware with configurable `use_ams` and `ams_mapping`.
**Why**: The AMS Lite is the defining feature of the A1 Combo. Without AMS support, agents can't make material-aware decisions, can't set up multi-color prints, and can't monitor filament levels.
**Scope**: Modify `bambu.py` (extract AMS data from MQTT cache, add AMS control commands), add MCP tools in `server.py`, update `start_print` parameters.

### Proposal 2: Speed Profile Control
**Value**: HIGH | **Effort**: Small (30-60 min)
**What**: Add `set_speed_profile(level)` to the Bambu adapter and expose as an MCP tool. Read current speed level from MQTT status. Support: silent, standard, sport, ludicrous.
**Why**: Common workflow is switching to Silent at night, Sport during the day. Currently requires touching the printer screen or using Bambu Studio. Single MQTT command, very little code.
**Scope**: Add method to `bambu.py`, add MCP tool, add to `base.py` optional interface.

### Proposal 3: Enhanced Print Start
**Value**: HIGH | **Effort**: Small (30-60 min)
**What**: Make `start_print` configurable: `use_ams`, `ams_mapping`, `timelapse`, `bed_leveling`, `flow_cali`, `vibration_cali`, `layer_inspect`, `bed_type`, `plate_number`.
**Why**: Currently everything is hardcoded. Agents can't disable calibration for reprints (saves 2+ min), can't enable timelapse, can't select plates in multi-plate 3MF files.
**Scope**: Add keyword args to `start_print()` in `bambu.py`, update `server.py` MCP tool parameters.

### Proposal 4: Rich Print Monitoring
**Value**: MEDIUM-HIGH | **Effort**: Small (30-60 min)
**What**: Extract additional MQTT fields into `PrinterState` and `JobProgress`: layer_num/total_layers, fan speeds (cooling, aux, chamber), nozzle type/diameter, filament used weight, wifi_signal.
**Why**: Richer data = better agent decisions. Knowing you're on layer 50/200 is more useful than just "62%". Fan speeds help diagnose cooling issues. WiFi signal helps debug connectivity.
**Scope**: Extend dataclasses in `base.py`, update parsing in `bambu.py`, update serialization.

### Proposal 5: HMS Error Intelligence
**Value**: MEDIUM-HIGH | **Effort**: Medium (1-2 hours)
**What**: Parse Bambu HMS (Health Management System) error codes from MQTT. Map codes to human-readable descriptions and fix suggestions. Surface in printer state and as events.
**Why**: When a print fails, Bambu sends detailed diagnostics that currently get ignored. Turning "FAILED" into "Nozzle clog detected during filament change — try cleaning the hotend" is a huge UX win.
**Scope**: Add HMS parsing to `bambu.py`, create HMS error code database (JSON data file), integrate with event bus.

### Proposal 6: LED/Light Control
**Value**: MEDIUM | **Effort**: Tiny (15-30 min)
**What**: Add `set_light(node, mode)` to Bambu adapter. Nodes: chamber_light, work_light. Modes: on, off, flashing. Expose as MCP tool.
**Why**: Simple command, immediate visual feedback. Useful for camera visibility control and "signal" functionality (flash light when print is done).
**Scope**: Add method to `bambu.py`, add MCP tool. ~20 lines of code.

### Proposal 7: Skip Objects Mid-Print
**Value**: MEDIUM | **Effort**: Small (30-60 min)
**What**: Add `skip_objects(obj_list)` command. Requires knowing which objects are in the print (from 3MF metadata or slicer output).
**Why**: When one object in a batch print fails, you can skip it without canceling everything. Saves time and filament on multi-object plates.
**Scope**: Add command to `bambu.py`, add MCP tool. May need object enumeration from print metadata.

### Proposal 8: Print Error Diagnostics
**Value**: MEDIUM | **Effort**: Tiny (15-30 min)
**What**: When `gcode_state == "FAILED"`, extract the `print_error` field and include it in the `PrinterState` response.
**Why**: Currently a failed print just shows "ERROR" status with no explanation. The printer already provides the reason — we just need to surface it.
**Scope**: Add `error_code` and `error_message` fields to `PrinterState`, parse from MQTT.

### Proposal 9: RTSP Camera Auth Fix
**Value**: LOW-MEDIUM | **Effort**: Tiny (15 min)
**What**: Pass access code to ffmpeg RTSP call and include in stream URL for authenticated camera access.
**Why**: Some firmware versions require auth for camera streams. Current implementation may fail silently.
**Scope**: Update ffmpeg args and stream URL in `bambu.py`.

### Proposal 10: A1 Combo Intelligence Enrichment
**Value**: MEDIUM | **Effort**: Small (30-60 min)
**What**: Beef up the `bambu_a1` entry in `printer_intelligence.json` — currently has 3 material profiles and 1 failure mode. Add: all recommended materials with detailed profiles, more failure modes (PTFE wear, AMS jams, WiFi issues, bed adhesion), and A1-specific optimization tips.
**Why**: The intelligence data drives agent recommendations. More complete data = better advice for Adam's specific printer.
**Scope**: Update `printer_intelligence.json` only.

---

### Recommended Priority Order (for maximum impact tomorrow)

**Quick Wins (ship in < 1 hour each):**
1. Proposal 2: Speed Profile Control
2. Proposal 6: LED/Light Control
3. Proposal 8: Print Error Diagnostics
4. Proposal 9: RTSP Camera Auth Fix

**High Value (1-2 hours each):**
5. Proposal 3: Enhanced Print Start
6. Proposal 4: Rich Print Monitoring
7. Proposal 10: A1 Combo Intelligence Enrichment

**Bigger Lifts (2-3 hours):**
8. Proposal 1: AMS Intelligence
9. Proposal 5: HMS Error Intelligence

**Nice to Have:**
10. Proposal 7: Skip Objects Mid-Print
