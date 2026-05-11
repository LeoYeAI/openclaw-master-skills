# CNC Routers: Engineering Reference for AI-Driven Control Software

---

## 1. Core Physics & Engineering

### How CNC Routers Work

A CNC router uses computer-controlled motion across three or more axes to remove material by rotating a cutting tool (spindle) at high speed while traversing a programmed path. Unlike VMCs (Vertical Machining Centers), routers are optimized for high-speed, light-duty cutting of wood, plastics, and non-ferrous metals — trading rigidity for speed and work area.

**Axis Conventions:**
- **X**: Left/right (along the longest table dimension)
- **Y**: Front/back (gantry travel or table travel)
- **Z**: Up/down (spindle plunge)
- **A/B/C**: Rotational axes around X/Y/Z respectively; 4th axis is typically A (rotation around X)
- **5-axis**: Adds two rotational axes, enabling simultaneous 5-sided machining; rare in routers but growing

**Workholding:** Spoilboard with T-tracks, vacuum tables, cam clamps, toe clamps, or tape+CA glue. The spoilboard is a sacrificial surface surfaced flat (coplanar to XY plane) after installation.

### Cutting Mechanics

**Chip Load** is the thickness of material each cutting edge removes per revolution. It is the fundamental parameter governing tool life, surface finish, and heat generation.

```
Chip Load (inches/tooth) = Feed Rate (IPM) / (RPM × Number of Flutes)
Feed Rate (IPM) = Chip Load × RPM × Number of Flutes
```

**Surface Footage (SFM)** — the peripheral velocity of the cutter:
```
SFM = (RPM × Tool Diameter × π) / 12
RPM = (SFM × 12) / (π × Tool Diameter)
```

**Depth of Cut (DOC):** Axial DOC is how deep the tool plunges (Z). For standard milling, DOC = 0.5–1× tool diameter for roughing. Radial DOC (WOC, Width of Cut) is how far laterally the tool engages; typically 40–50% of tool diameter for conventional milling.

**Adaptive/Trochoidal milling** uses high DOC (1–3× tool diameter) with very low WOC (5–10% of tool diameter), maintaining constant tool engagement angle and dramatically reducing heat and cutting forces. Essential for aluminum on lighter machines.

### Chip Load Reference Tables

| Material | Tool Dia | Flutes | Chip Load (in) | RPM | Feed Rate (IPM) |
|---|---|---|---|---|---|
| Softwood (pine) | 1/4" | 2 | 0.010–0.018 | 18,000 | 360–648 |
| Hardwood (oak) | 1/4" | 2 | 0.007–0.012 | 18,000 | 252–432 |
| MDF | 1/4" | 2 | 0.008–0.015 | 18,000 | 288–540 |
| Acrylic (cast) | 1/4" | 2 | 0.004–0.007 | 18,000 | 144–252 |
| HDPE | 1/4" | 2 | 0.006–0.010 | 18,000 | 216–360 |
| Aluminum 6061 | 1/4" | 2-3 | 0.001–0.003 | 18,000 | 36–108 |
| Aluminum 6061 | 1/8" | 2 | 0.0005–0.001 | 24,000 | 24–48 |
| Brass | 1/4" | 2 | 0.001–0.002 | 12,000 | 24–48 |

*These are conservative starting points; optimize upward while monitoring chip color and sound.*

### Climb vs. Conventional Milling

**Conventional milling:** Cutter rotates against the feed direction. Chip starts thin and ends thick. Better on machines with backlash.

**Climb milling:** Cutter rotates with the feed direction. Chip starts thick and ends thin. Produces better surface finish, generates less heat, extends tool life. **Requires backlash-free motion** — ballscrews or tight rack-and-pinion. Default for CNC routers with modern drive systems.

**Rule of thumb:** Use climb milling for finish passes on rigid machines. For rough passes on machines with backlash, use conventional. On belt-drive machines, conventional is often safer.

### Runout, Backlash, Rigidity

- **Runout:** Radial deviation of the cutter from true rotation axis. ER collet systems: aim for <0.0005" TIR. Causes variable chip load per tooth, vibration, poor finish, tool breakage.
- **Backlash:** Free play in the drive system when reversing direction. Ballscrews: nearly zero. Belt drive: 0.002–0.010" typical. Rack and pinion: 0.001–0.005" with anti-backlash pinion.
- **Rigidity:** Frame stiffness determines maximum depth of cut before chatter. Gantry height is the primary rigidity killer — lower gantry = stiffer.

### Toolpath Strategies

- **Pocket (2D):** Clears a 2D enclosed region to depth. Strategies: zig-zag, spiral, offset (concentric).
- **Contour (Profile):** Follows the outline of a shape; used for cutouts and external profiles. Tabs hold parts to the sheet.
- **Adaptive Clearing (Trochoidal):** Circular arc moves with small radial engagement. Maintains constant tool engagement angle. High DOC, low WOC. Essential for aluminum.
- **V-Carve:** V-bit follows centerline of a design; depth controlled by design width. Dominant in sign-making.
- **3D Surfacing:** Parallel, scallop, or contour passes across a 3D surface. Ball-nose end mills required.
- **Onion Skin:** Leave a thin floor (0.01–0.02") to hold parts during cutting; peel manually afterward.

### Heat Generation and Tool Wear

Heat is the enemy. In aluminum, chips are the primary heat carrier — they must evacuate the cut. Chip welding (aluminum fusing to the tool flute) causes immediate tool failure. Indicators of excess heat:
- Discolored chips (blue/dark = overheating)
- Melted plastic chips (stringy, sticky residue on acrylic)
- Built-up edge on cutter
- Burning smell in wood

Mitigation: increase feed rate (thicker chips carry more heat away), use air blast or mist coolant (WD-40 on aluminum).

---

## 2. Mechanical Systems

### Gantry Designs

- **Moving gantry, fixed table:** Most common for hobby/prosumer. Gantry moves in Y; table fixed. Good for sheet goods.
- **Moving table, fixed gantry:** Table moves under a fixed bridge. More rigid for heavy cuts; used in industrial VMCs.
- **Bridge mill:** Fixed gantry, wide table movement. Common in stone/composite machining.

### Linear Motion Systems

| System | Precision | Load Capacity | Cost | Dirt Tolerance | Typical Use |
|---|---|---|---|---|---|
| V-slot wheels (OpenBuilds) | Low | Low | Very low | Moderate | Hobbyist, light-duty |
| Round rod + linear bearing | Low-medium | Medium | Low | Poor | Budget entry-level |
| Profile rail (HiWin HGR) | High | High | Medium | Good (sealed) | Prosumer, semi-pro |
| Box ways | Very high | Very high | High | Excellent | Industrial VMC |

**HiWin HGR15, HGR20, HGR25** are the standard for prosumer CNC routers. Chinese clones (identical dimensional spec) are functional for routers at 30–50% of the cost. **MGN12** and **MGN9** are miniature rails used on desktop machines.

### Drive Systems

| Drive | Backlash | Precision | Max Speed | Cost | Notes |
|---|---|---|---|---|---|
| Belt (GT2/GT3) | 0.002–0.010" | Low | High | Very low | X-Carve, Shapeoko 4 |
| Lead screw (ACME) | 0.005–0.030" | Medium | Low | Low | Older designs, Z-axis |
| Ballscrew (C7/C5) | <0.001" | High | Medium | Medium | Onefinity, Shapeoko 5 |
| Rack & pinion | 0.001–0.005" | High | High | Medium | Avid CNC, ShopBot |

**Ballscrews:** C7 grade (±0.050mm/300mm) adequate for most routing. C5 (±0.018mm/300mm) for precision work. 1610 (16mm dia, 10mm lead) common on Z-axis; 2005 or 2010 common on X/Y.

**Rack & Pinion:** Standard on Avid CNC (1.5 MOD rack, Nema 34 with helical anti-backlash pinion). Scales well to large tables (4×8, 5×10). Requires periodic lubrication and spring-loaded pinion to eliminate backlash.

### Spindle Types

| Spindle | Power | RPM Range | Runout | Collet | Noise | Cost |
|---|---|---|---|---|---|---|
| Trim router (Makita RT0701, DeWalt DWP611) | 1.25 HP | 10,000–30,000 | 0.001–0.003" | 1/4", 1/8" via adapter | High | Low |
| Air-cooled VFD spindle | 1.5–3 kW | 6,000–24,000 | <0.0008" | ER11, ER16, ER20 | Moderate | Medium |
| Water-cooled VFD spindle | 1.5–3.5 kW | 6,000–24,000 | <0.0005" | ER11–ER25 | Low | Medium-high |
| HSD / ISO30 ATC spindle | 5–15 kW | 3,000–24,000 | <0.0003" | ISO30, HSK | Low | High |

**ER Collet Standard:** ER11 (max 7mm shank), ER16 (max 10mm), ER20 (max 13mm), ER25 (max 16mm), ER32 (max 20mm). ER20 is the sweet spot for 1/4" and 1/2" shank tooling on 2.2 kW spindles.

**VFD Control Methods:**
- **0–10V analog:** Simple, voltage proportional to speed. VFD parameter PD070=1 (0–10V control).
- **RS485/Modbus RTU:** Digital; supports speed readback, fault status, current monitoring. Baud typically 9600, 8N1 or 8N2. Huanyang VFD: register 0x02 = frequency command, 0x03 = run/stop.
- **PWM:** Pulse-width modulation; common on GRBL (M3 Sxxx drives PWM output to VFD 0–10V converter).

### Dust Collection

Effective chip/dust extraction is mandatory for air quality (MDF dust is carcinogenic, composite dust is hazardous) and machine life.

- **Dust boot:** Surrounds the spindle, skirt contacts workpiece. Examples: Suckit Dust Boot, Sweepy (Carbide 3D).
- **Vacuum shoe (fixed):** Rigid shoe fixed to Z plate; used on industrial machines. More effective but limits Z travel.
- **Cyclone separator:** Pre-separator (Oneida, Dustopper) before shop vac extends filter life dramatically.
- **Mist coolant:** For aluminum cutting; small pump delivers oil-air mist to cut.

### Spoilboard

The spoilboard is a sacrificial MDF or HDPE sheet bolted to the machine bed. Must be surfaced (fly-cut) after installation to be coplanar with the XY plane. Surface with a large-diameter surfacing bit (Whiteside 6210, 1.5" diameter) at low DOC (0.5–1mm), high feed rate, overlapping passes.

**T-Track:** Aluminum T-track channels embedded in spoilboard rows allow sliding clamps anywhere. 3/4" T-track (Kreg, Woodpecker) is standard; bolts take 5/16"-18 or M8 fasteners.

---

## 3. Electronics & Control

### Controller Types

| Controller | Platform | Open Source | Max Axes | Interface | Best For |
|---|---|---|---|---|---|
| GRBL v1.1 | Arduino Mega/Uno | Yes | 3–6 | Serial/USB | Hobbyist, DIY |
| FluidNC | ESP32 | Yes | 6 | WebSocket, HTTP, Serial | Modern DIY, remote AI |
| LinuxCNC | Linux RT kernel | Yes | 9+ | HAL/NML/Python | Industrial retrofit |
| Mach3 | Windows XP/7 | No | 6 | Parallel port/plugin | Legacy prosumer |
| Mach4 | Windows | No (plugin API) | 6+ | USB motion controller | Prosumer/semi-pro |
| Centroid Acorn | Dedicated hardware | No | 4 | Ethernet | Prosumer retrofit |
| UCCNC | Windows | No | 4 | UC100/UC300 USB | European prosumer |
| Buildbotics | ARM Linux | Yes | 4 | HTTP REST API | Onefinity |

### GRBL Protocol — Complete Reference for AI Integration

GRBL communicates over serial (typically 115200 baud, 8N1). Two command classes:

**Real-time commands (single byte, immediate effect — no newline required):**
- `?` — Status report
- `~` — Cycle start / Resume
- `!` — Feed hold (pause motion)
- `0x18` (Ctrl-X) — Soft reset
- `0x85` — Jog cancel
- `0x90` — Feed override 100%
- `0x91` — Feed override +10%
- `0x92` — Feed override -10%
- `0x9A` — Spindle override +10%
- `0x9B` — Spindle override -10%

**System commands ($ prefix, terminated with newline):**
- `$$` — View all settings
- `$#` — View G-code parameters (work offsets G54–G59, TLO, PRB)
- `$G` — View current G-code state
- `$H` — Run homing cycle
- `$X` — Kill alarm lock
- `$J=G91 X10 F500` — Jog command (real-time, cancellable with 0x85)
- `$RST=$` — Restore all settings to defaults

**Status report fields:**
```
<Idle|MPos:0.000,0.000,0.000|FS:500,12000|Ov:100,100,100|WCO:0.000,0.000,0.000>
```
- State: `Idle`, `Run`, `Hold:0`, `Hold:1`, `Jog`, `Alarm`, `Door`, `Check`, `Home`, `Sleep`
- `MPos` or `WPos`: machine or work position
- `FS`: feed rate, spindle speed (actual)
- `Ov`: feed, rapids, spindle overrides (%)
- `WCO`: work coordinate offset

**Key G-codes for router operation:**
- `G0` — Rapid move
- `G1` — Linear feed
- `G2/G3` — Circular arc CW/CCW
- `G4 P0.5` — Dwell 0.5 seconds
- `G20/G21` — Inches/millimeters
- `G38.2` — Probe toward workpiece (tool length, surface probing)
- `G43.1 Z-5.0` — Apply tool length offset
- `G54–G59` — Work coordinate systems
- `G90/G91` — Absolute/incremental
- `M3 S12000` — Spindle CW at 12,000 RPM
- `M4` — Spindle CCW
- `M5` — Spindle off
- `M6 T2` — Tool change, tool 2
- `M7/M8` — Mist/flood coolant on
- `M9` — Coolant off
- `M30` — Program end and rewind

### FluidNC — Recommended for AI Integration

FluidNC (ESP32) extends GRBL with:
- **WebSocket API** (`ws://[ip]:81`): Real-time bidirectional G-code streaming, status reports, file operations
- **HTTP REST API** (`http://[ip]/`): File upload, config read/write, OTA firmware updates
- **YAML configuration** instead of `$` parameter numbers — human-readable, version-controlled
- **Automatic status reporting** — push-based rather than poll-based
- **WebUI** built-in at `http://[ip]`
- Wi-Fi connectivity; no USB tether required — ideal for headless AI agent control

```yaml
# FluidNC config.yaml example (partial)
axes:
  x:
    steps_per_mm: 800
    max_rate_mm_per_min: 5000
    homing:
      cycle: 1
      positive_direction: false
spindle:
  type: VFD_Huanyang
  rs485_addr: 1
  speeds: [{speed: 0, percent: 0}, {speed: 24000, percent: 100}]
```

### LinuxCNC HAL/Python Interface

LinuxCNC exposes a full Python API for AI agent integration:

```python
import linuxcnc

s = linuxcnc.stat()
c = linuxcnc.command()
e = linuxcnc.error_channel()

s.poll()                          # Refresh state
print(s.position)                 # (x, y, z, a, b, c, u, v, w) tuple
print(s.spindle[0]['speed'])      # Actual spindle RPM
print(s.task_mode)                # MANUAL=1, AUTO=2, MDI=3

c.mode(linuxcnc.MODE_MDI)
c.wait_complete()
c.mdi("G0 X10 Y10")              # MDI G-code command
c.program_open("/path/to/file.ngc")
c.auto(linuxcnc.AUTO_RUN, 0)     # Run from line 0
```

### Buildbotics (Onefinity) REST API

```
GET  http://[ip]/api/status     # Full machine state JSON
GET  http://[ip]/api/config     # Configuration
PUT  http://[ip]/api/config     # Update config
POST http://[ip]/api/start      # Start program
POST http://[ip]/api/stop       # Stop
POST http://[ip]/api/pause      # Pause
GET  http://[ip]/api/log        # Log streaming
```

### CNCjs — Node.js Headless Controller

CNCjs provides a controller-agnostic WebSocket API supporting GRBL, Smoothieware, Marlin, and TinyG. Run headless on Raspberry Pi.
- Connect: `ws://[ip]:8000` with auth token
- Namespace: `/grbl`, `/smoothie`, `/marlin`
- Events: `serialport:data`, `workflow:state`, `feeder:status`
- Commands: `command workspaceId gcode`, `command workspaceId homing`

### Stepper vs. Servo Motor Selection

| Parameter | Open-Loop Stepper | Closed-Loop Stepper | Servo (AC/DC) |
|---|---|---|---|
| Position feedback | None | Encoder (500–2000 CPR) | High-res encoder |
| Stall detection | None | Yes, fault output | Yes, fault + recovery |
| Torque at speed | Drops sharply >1000 RPM | Drops sharply >1000 RPM | Flat through range |
| Cost (NEMA23, 1 axis) | $15–50 | $60–150 | $150–500 |
| Missed step risk | Yes (crash = unknown position) | No (faults and halts) | No |

**Practical guidance for AI control:** Closed-loop steppers (Leadshine EtherCAT, StepperOnline iSV) are strongly preferred. A stalled open-loop stepper silently loses position — the machine will crash into fixtures and the AI cannot detect it. Closed-loop systems fault with a drive alarm signal that halts the controller immediately.

---

## 4. Software & CAM

### CAD/CAM Workflow

```
Design (CAD) → Toolpath Generation (CAM) → Post Processing → G-code file → Controller → Machine
```

### Key CAM Packages

| Software | Target | Strength | Post Processors |
|---|---|---|---|
| Fusion 360 (Autodesk) | Hobbyist–Pro | Adaptive clearing, 5-axis, integrated CAD | GRBL, Mach3/4, LinuxCNC, Centroid, Fanuc, Haas |
| VCarve Pro / Aspire (Vectric) | Woodworking/signs | V-carving, 2.5D, gadgets library | 200+ posts; Shopbot, Mach, GRBL |
| Carbide Create | Beginner | Simple 2.5D, paired with Carbide Motion | Carbide Motion only |
| EstlCAM | Budget | Simple, direct machine control | GRBL, UCCNC |
| Mastercam | Professional | Full 3–5 axis, Swiss machining | All industrial controls |
| HSMWorks | Pro (SolidWorks) | Full 3–5 axis, inside SolidWorks | All industrial controls |
| Hypermill (Open Mind) | High-end 5-axis | 5-axis strategies, automation | All major controls |

**Post processor selection:** CAM output must target the specific controller dialect. GRBL post for Fusion 360 outputs: units in mm, no tool change (M6 — GRBL ignores), M3/M5 for spindle. ShopBot requires SB3 dialect (`.sbp` file, not `.nc`).

**Nesting Software:** For production sheet cutting, dedicated nesting software (Vectric Cut2D Nest, Pronest, Optimik) maximizes material utilization by packing parts intelligently before toolpath generation.

---

## 5. Materials

### Material-Specific Cutting Guide

**Wood (MDF, Plywood, Hardwood, Softwood):**
- MDF: Uniform density, no grain direction issues. Excellent for V-carving. Toxic dust (urea-formaldehyde binders); N95 minimum.
- Plywood: Veneer layers cause tear-out. Use **compression bits** (upcut+downcut spiral combined) for clean top and bottom faces simultaneously.
- Hardwood: Climb milling for finish passes. Feed parallel to grain where possible.

**Plastics:**
- **Acrylic (Cast preferred over Extruded):** Cast acrylic machines cleanly; extruded acrylic stress-cracks. Use single-flute O-flute bits.
- **HDPE:** Very soft; chip welding risk. High feed, sharp single-flute, polished flutes.
- **Delrin/POM:** Machines beautifully. High chip loads tolerated.
- **Polycarbonate:** Tends to melt. Keep feed rates high, reduce RPM to 10,000–12,000.

**Aluminum (6061-T6, 7075-T6):**
- **6061** machines well with 2–3 flute uncoated carbide, WD-40 or IPA mist.
- **7075** is harder, more abrasive. Reduce chip load 20%. ZrN coating preferred.
- Trochoidal/adaptive toolpaths strongly recommended on machines with limited rigidity.
- Chip evacuation is critical — chips must not re-enter the cut.

**Composites (G10/FR4, CFRP):**
- Extremely abrasive — diamond-coated or solid carbide required.
- CFRP dust is a carcinogenic inhalation hazard. Full-face respirator, downdraft table, wet cutting or enclosed machine.
- PCB milling (isolation routing): 0.1 mm V-bits (60°), 10–30 µm depth, 300–600 mm/min. Z-axis surface probing mandatory.

---

## 6. Major Brands & Key Models

### Hobbyist / Desktop

**Carbide 3D (Shapeoko):**
- Shapeoko 4 XL/XXL: V-wheels, belt drive, Carbide Motion GRBL-based controller. 16"×16" to 33"×33" cutting area.
- Shapeoko 5 Pro: Ballscrews, linear rails, 200 IPM max feed. Significant rigidity improvement.
- HDM (Heavy Duty Mill): Fully enclosed, 65mm spindle mount, for serious aluminum.
- Controller: Carbide Motion runs on USB-connected proprietary board; API limited.

**Inventables (X-Carve):**
- X-Carve Pro 4×4: Cloud-based via Easel. XCP controller runs GRBL, accessible via Easel's API or direct GRBL serial.

**Onefinity:**
- Woodworker / Machinist: Ballscrew Z, independent X-rails (no gantry cross-beam). Buildbotics controller (ARM Linux, REST API).
- Elite Series: Closed-loop steppers (Leadshine), same Buildbotics-derived controller. 400 IPM max.

**Sienci LongMill MK2 / MK2.5:**
- GRBL-based, BlackBox controller. gSender is the recommended sender with full GRBL support.
- Open-source hardware and firmware.

### Prosumer / Semi-Professional

**Avid CNC:**
- PRO4848, PRO6060, PRO4896: Rack and pinion drive (1.5 MOD, hardened), NEMA 34 closed-loop steppers.
- Ships with Mach4 (Windows PC) or optional Centroid Acorn.
- Industrial-grade linear rails (equivalent to HiWin HGR20/HGR25).

**Axiom CNC:**
- AR6 Pro+ and AR8 Pro+: Centroid controller, rack and pinion, water-cooled spindle.

**CAMaster:**
- Stinger I–IV: Entry semi-pro, rack and pinion.
- Cobra: Production routing, optional ATC (linear tool rack, ISO30). Centroid or Mach4 control.

### Professional / Industrial

**ShopBot Tools:**
- PRSstandard, PRSalpha: Rack and pinion, SB3 proprietary control (`.sbp` file format with ShopBot Basic scripting).
- Desktop MAX: 24"×36", ATC V2 (6-tool pneumatic carousel).
- PRSalpha 60" gantry: 5×10 sheet production routing.
- SB3 software exposes COM object API for Windows automation.

**AXYZ International:**
- Wide-format industrial (4×8 to 6×12+). Fanuc or Siemens 840D controls.

**Multicam:**
- 3000/5000 series: ATC with 8–20 tool capacity, ISO30 or HSK63 tooling. 10–15 HP HSD spindles.

**Biesse / Homag / SCM:**
- European industrial woodworking CNC. Used in furniture manufacturing at scale.

**Budget Chinese (6040, 1325, etc.):**
- 6040 format: 600×400mm, 800W–2.2 kW spindle, Mach3 or GRBL controller.
- 1325 (1300×2500mm): Near-industrial footprint, 3–4.5 kW spindle. Mach3 control standard.

---

## 7. Remote Management & AI Integration APIs

### GRBL Serial Protocol for AI Agents

Streaming G-code to GRBL requires flow control via acknowledgment ("ok" / "error:X"):

```python
import serial
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
ser.write(b'\r\n\r\n')  # Wake up
time.sleep(2)
ser.flushInput()

def send_gcode(line):
    ser.write((line.strip() + '\n').encode())
    return ser.readline().decode().strip()  # 'ok' or 'error:X'

# Status query
ser.write(b'?')
status = ser.readline().decode()  # '<Idle|MPos:0.000,0.000,0.000|FS:0,0>'
```

**GRBL planning buffer:** GRBL has a 15-block RX buffer and a 16-block planner buffer. Use character-counting method (track sent bytes, count back 'ok' responses) for maximum throughput.

### Universal Gcode Sender (UGS) / CNCjs

- **UGS Platform mode REST API:** `GET /api/machine/status`, `POST /api/machine/sendCommand`
- **CNCjs:** Node.js, WebSocket-first. Embeds on Raspberry Pi. Plugin system allows custom G-code macros triggered by WebSocket events.

### Mach4 Plugin API

Mach4 exposes Lua scripting for macro automation. External control via Modbus TCP (if Ethernet motion controller configured) or the Mach4 API DLL (Windows COM).

---

## 8. Tool Types & Tooling

### End Mill Geometry

| Type | Geometry | Best For | Notes |
|---|---|---|---|
| Flat (square) end mill | Flat bottom, sharp corners | Pockets, slots, profiles | Most common |
| Ball nose | Hemispherical tip | 3D surfacing, fillets | Stepover determines scallop height |
| Bull nose (corner radius) | Flat bottom, radiused corners | Roughing, floor finishing | More rigid than ball nose |
| O-flute (single flute) | Single large flute | Plastics, soft aluminum | Maximum chip evacuation |
| V-bit | V-point | V-carving, chamfering, engraving | 60°, 90°, 120° common |
| Compression | Upcut + downcut combined | Plywood, melamine | Clean top and bottom |
| Surfacing / fly cutter | Large-diameter, single insert | Spoilboard surfacing | 1–2" diameter |

**Flute count selection:**
- 1 flute (O-flute): Plastics, soft aluminum on light machines
- 2 flutes: Aluminum, general purpose, maximum chip room
- 3 flutes: Hardwood, general metal (balances chip room and finish)
- 4+ flutes: Finish passes in hardwood and metal

### Coating Selection

| Coating | Max Temp | Best Materials | Avoid |
|---|---|---|---|
| Uncoated carbide | 700°C | Aluminum (no Al reaction), plastics, wood | Steel (oxidizes) |
| TiN (gold) | 600°C | Wood, light steel, general purpose | Aluminum (Al affinity) |
| TiAlN (dark violet) | 900°C | Steel, stainless, titanium | Aluminum (Al-Al reaction) |
| ZrN (gold/bronze) | 600°C | Aluminum, brass, copper | High-temp steel |
| AlTiN (dark gray) | 1000°C | Hardened steel, inconel | Aluminum |
| DLC (Diamond-Like Carbon) | 400°C | Graphite, CFRP, aluminum | Ferrous metals |

---

## 9. Workholding

### Methods by Application

- **Cam clamps:** Fastest for odd-shaped parts; require T-track. Eccentric profile creates mechanical advantage.
- **Tape + CA Glue:** 180° peel tape on spoilboard and workpiece, bonded with CA glue. Holds 50–100 lbf in shear. Remove with acetone or IPA.
- **Vacuum table:** Highest throughput for sheet goods. MDF acts as vacuum manifold plenum. Pump sizing: 1–2 CFM per sq ft of active zone at 18–22" Hg for woodworking.
- **T-track + clamps:** Flexible. 3/4" aluminum T-track rows every 4" is common.
- **Fixture / jig:** Dedicated fixture for repeat parts. Machined from HDPE or aluminum. Dowel pin registration for ±0.005" placement.
- **Onion skin (floor tabs):** Leave 0.020–0.030" material floor. Peel and sand after.

---

## 10. Safety

### Critical Safety Considerations for AI-Controlled Systems

**Spindle safety:**
- Collet tightening torque must be correct — under-torqued collets allow tool pullout at 18,000+ RPM. A 1/4" end mill ejected at 24,000 RPM has kinetic energy of ~50 J — lethal.
- AI control systems must verify spindle speed has reached setpoint before beginning a cut (VFD spindle acceleration: 2–5 seconds to reach 24,000 RPM).

**Emergency stop architecture:**
- Hardware E-stop: hardwired normally-closed (NC) circuit through relay — breaks power to VFD enable AND controller enable simultaneously.
- Software E-stop must not be the only layer.
- Feed hold (`!` in GRBL) stops axis motion but does NOT stop spindle. Full reset or E-stop required for spindle.
- Limit switches: Normally Closed (NC) wiring — open circuit (cut wire) = triggered limit. GRBL: `$21=1` enables hard limits.

**Dust and fire hazard:**
- MDF/wood dust is explosive above Lower Explosive Limit — maintain dust extraction.
- Aluminum swarf can ignite if accumulated in dust collector.
- CFRP/graphite dust is conductive — can short electronics and is carcinogenic.

**Soft limits (GRBL `$20=1`):** Software-enforced travel boundaries. Machine must be homed first (`$H`) for soft limits to activate.

**Interlock for AI control:** Implement a watchdog: if AI agent loses connectivity to controller for >N seconds during a job, the machine should execute feed hold automatically.

---

## 11. Calibration & Maintenance

### Steps Per Unit Calibration

GRBL: `$100`, `$101`, `$102` = steps/mm for X, Y, Z.
```
Steps/mm = (Motor steps/rev × Microstepping) / (Lead mm/rev)
# Ballscrew example: 200 × 16 / 5 = 640 steps/mm
# Belt example: 200 × 16 / (20 teeth × 2mm GT2) = 80 steps/mm
```
Verify with digital calipers: command `G0 X100`, measure actual travel, correct by `new_steps = (commanded_distance / actual_distance) × current_steps`.

### Gantry Squaring

Dual-motor Y-axis gantry: each Y motor has an independent limit switch. Homing fires both switches; if one hits before the other, the gantry skews.
1. Home the machine.
2. Mark both ends of gantry with scribe.
3. Measure diagonal of known square.
4. Adjust stepper position offset or physically reposition motor mounts.
5. Recheck diagonals — equal diagonals = 90° gantry.

### Spoilboard Surfacing

```gcode
G0 Z5                          ; safe height
G0 X0 Y0                       ; corner
G1 Z-0.5 F300                  ; plunge to surface depth
G1 X800 F3000                  ; pass 1
G0 Y20                         ; step over
G1 X0 F3000                    ; pass 2 (return)
; repeat for full table width
```

### Tramming the Spindle

Spindle must be perpendicular to spoilboard. Check with dial indicator in a radius arm rotating around spindle axis:
- Measure deviation at 90° intervals.
- Adjust spindle mount shims until deviation < 0.001" across 4" diameter sweep.
- Non-perpendicular spindle causes scalloping on pocket floors from ball nose passes.

### Tool Length Offset (TLO) Probing

```gcode
G38.2 Z-50 F100               ; probe toward plate
G43.1 Z[#5063 + 20]           ; set TLO: probe Z + plate thickness
G0 Z5                          ; retract safe
```
GRBL stores last probe result in `#5063` (Z). TLO stored in `$#` output.

### Backlash Compensation

GRBL does not natively support backlash compensation. For AI control: always approach a position from the same direction (typically positive X and Y) to eliminate backlash effect.

---

## 12. Industry Trends (2024–2026)

### ATC Democratization

Automatic Tool Changers arriving in prosumer market:
- ShopBot Desktop MAX ATC V2: 6-tool carousel, ISO30, pneumatic. ~$15,000.
- Chinese 4-axis ATC routers: ISO30, 8–12 tool linear rack, ~$8,000–15,000.
- ATC enables lights-out AI-driven production runs with multi-tool operations.

### Closed-Loop Steppers Replacing Open-Loop

Leadshine EtherCAT, Stepperonline iSV: $80–150/axis puts them within 2× of open-loop steppers. All new prosumer machines shipping in 2025 are closed-loop as baseline. Essential for AI control — stall detection prevents silent position loss.

### Network-Native Controllers

FluidNC (ESP32-based) making Wi-Fi native controllers standard on DIY builds. Eliminates USB-tethered PC. AI agents connect over MQTT or WebSocket from anywhere on local network.

### Hybrid Machine Platforms

Single-frame machines combining CNC router + diode laser + drag knife on one gantry (Snapmaker Artisan, xTool P2S). AI control abstracts the tool type; same motion system, different toolhead G-code dialects.

### Camera-Based Registration

Camera systems locate fiducial marks on sheets for registration compensation. AI control with vision: capture fixture position via downward-facing camera, compute coordinate offset, update G54 work offset before job start.

### 5-Axis Accessibility

- **Pocket NC V2-10, V2-50:** Desktop 5-axis, $5,000–10,000. Fusion 360 compatible.
- Chinese 5-axis router tables: $20,000–40,000 with ISO30 ATC and Siemens 808D control.
- For AI systems: 5-axis requires inverse kinematics and orientation control; G-code adds `A` and `B` words.

---

## Appendix: Quick-Reference G-Code Vocabulary for AI Agents

```gcode
; Spindle control
M3 S18000          ; Spindle on CW, 18,000 RPM
M5                 ; Spindle off

; Coolant
M7                 ; Mist on
M8                 ; Flood on
M9                 ; Coolant off

; Probing
G38.2 Z-30 F60    ; Probe down, trip on contact (error if no contact)
G38.3 Z-30 F60    ; Probe down, no error if no contact
G38.4 Z5 F60      ; Probe up (away from contact)

; Work offsets
G54               ; Work coordinate 1 (default)
G92 X0 Y0 Z0      ; Set current position as origin (GRBL-compatible)
G92.1             ; Clear G92 offset

; Tool length
G43.1 Z-25.4      ; Dynamic TLO (GRBL — set offset directly)
G49               ; Cancel TLO

; Canned cycles (Mach/LinuxCNC only — not supported in GRBL)
G81 X10 Y10 Z-5 R2 F100  ; Drill cycle
G83 X10 Y10 Z-20 R2 Q3 F80 ; Peck drill cycle

; Feed/speed overrides (GRBL real-time, single byte)
; 0x90 = 100%, 0x91 = +10%, 0x92 = -10%, 0x93 = +1%, 0x94 = -1%
; 0x9A = spindle +10%, 0x9B = spindle -10%
```
