# FFF/FDM 3D Printer Engineering Reference

## AI-Driven Manufacturing Control — Internal Technical Reference

---

## 1. Core Physics and Process Engineering

### The FFF/FDM Process

Fused Filament Fabrication (FFF) — commercially branded as Fused Deposition Modeling (FDM) by Stratasys — deposits thermoplastic material in a layer-by-layer fashion by melting filament through a heated nozzle and depositing it onto a build surface. The process chain is:

1. **Filament feed**: Stepper-driven extruder pushes 1.75 mm or 2.85 mm filament into hotend
2. **Melt zone**: Heater block (typically 200–500°C) raises polymer above its glass transition temperature (Tg) or melt temperature (Tm)
3. **Extrusion**: Molten polymer is pushed through nozzle orifice (0.1–1.2 mm), deposited as a bead
4. **Layer adhesion**: Interlayer bonding occurs by thermal diffusion and polymer chain entanglement — bond strength is 40–60% of bulk material in Z-axis due to partial remelting
5. **Cooling and solidification**: Part cooling fans solidify the extrudate; amorphous polymers (PLA, ABS, PETG) solidify through Tg crossing; semi-crystalline (PEEK, Nylon) solidify through nucleation and crystal growth

### Crystallization and Anisotropy

Semi-crystalline polymers form crystalline domains during cooling. Crystallinity degree determines mechanical properties:
- **PEEK**: Amorphous if quenched, 30–35% crystallinity with controlled cooling at 150–200°C bed; chamber at 90–120°C increases crystallinity and impact resistance
- **Nylon PA12**: ~30% crystallinity typical; higher crystallinity improves fatigue resistance
- **PLA**: Semi-crystalline but kinetically slow to crystallize; functionally amorphous at standard print speeds

Anisotropy is inherent: Z-axis tensile strength is typically 40–65% of XY strength due to poor interlayer fusion. Key mitigation strategies:
- Increase layer overlap (negative air gap in slicers)
- Optimize print temperature (higher promotes chain diffusion)
- Anneal post-print for semi-crystalline polymers
- Reduce layer height to increase interlayer contact area

---

## 2. Motion Systems

### Cartesian (Bed-Slinger)

**Architecture**: Bed moves in Y, toolhead in X and Z (e.g., Prusa MK4, Ender 3).

- **Moving mass**: Bed + print (~500–1500 g moving in Y) limits acceleration; momentum shifts cause ringing artifacts at >150 mm/s
- **Acceleration capability**: 2,000–5,000 mm/s²
- **Advantages**: Mechanically simple, low cost, well-understood, easy calibration
- **Disadvantages**: Bed inertia limits speed; tall prints suffer from oscillation at top of stack; bed flex with large/heavy prints
- **Representative machines**: Prusa MK4, Ender 3 V3 SE, Bambu A1 series

### CoreXY

**Architecture**: Two motors cooperate to drive both X and Y motion through a crossed belt path. The toolhead is the only moving element in XY.

**Kinematic equations**:
```
Motor A = X + Y
Motor B = X - Y
```
When moving in pure X: both motors spin same direction. When moving in pure Y: motors spin opposite directions.

- **Moving mass**: Only toolhead (~100–250 g); enables 10,000–20,000 mm/s² acceleration
- **Top print speeds**: 300–600+ mm/s sustained with input shaping
- **Advantages**: High speed, stable at velocity, no bed inertia, enclosed chambers practical
- **Disadvantages**: Belt tension coupling (both axes affect each other), longer belt paths introduce compliance, mechanical complexity, squaring/tramming more involved
- **Common belt configurations**: Standard CoreXY, CoreXZ, HBot (inferior due to racking moments)
- **Representative machines**: Bambu X1C/P1S/H2D, Voron 2.4, Voron Trident, Creality K1/K2, Qidi X-Max 3, RatRig V-Core

### Delta

**Architecture**: Three vertical towers with parallel arms connecting to a floating effector (toolhead). All three motors collaborate for all motion.

- **Moving mass**: Only lightweight effector moves (~80–150 g)
- **Advantages**: Extremely fast Z motion, tall builds, fast small prints, low moving inertia
- **Disadvantages**: Complex kinematics (calibration requires arm length, tower position, endstop height), cylindrical build volume, difficult to enclose, non-linear motion requires dense calculation
- **Use case**: Tall, narrow parts; dental/jewelry; farms of fast small-part printers
- **Representative machines**: Anycubic Kossel, FLSUN V400 (claimed 400 mm/s max)

### IDEX (Independent Dual Extrusion)

**Architecture**: Two independent toolheads on the same X gantry, each with its own motor.

- **Modes**: Duplication (mirror two identical parts simultaneously), mirror mode, standard dual material
- **Advantages**: True simultaneous multi-material without purge tower; copy mode doubles throughput
- **Disadvantages**: X axis shared, toolhead collision possible, ooze management from inactive nozzle, mechanical complexity
- **Representative machines**: Bambu X1E, Ultimaker S5, Raise3D Pro3 Plus, BCN3D Sigma

---

## 3. Hotend Design

### Thermal Zones

| Zone | Component | Function |
|------|-----------|----------|
| Cold zone | Heat sink / cold block | Keeps filament solid; active or passive cooling |
| Heat break | Thin-walled tube | Thermal choke; high resistance to conduction |
| Heater block | Aluminum or copper block | Hosts cartridge heater and thermistor |
| Nozzle | Brass, hardened steel, ruby-tipped | Final orifice; determines diameter and abrasion resistance |

### Heat Creep

Heat creep occurs when heat migrates up the heat break into the cold zone, softening filament above the intended melt zone. Consequences: filament buckles in heat break, causing partial clog or inconsistent extrusion. Causes:
- Insufficient cold-side cooling (hot ambient, blocked fan)
- Printing at low speeds (low filament throughput = higher dwell time = more heat soak)
- PTFE-lined heat breaks tolerating less heat than all-metal designs

### PTFE-Lined vs All-Metal

| Property | PTFE-Lined | All-Metal |
|----------|-----------|-----------|
| Max temp | ~240°C continuous (PTFE degrades >260°C) | 500°C+ |
| Materials | PLA, PETG, TPU, low-temp | ABS, ASA, Nylon, PC, PEEK, PEI |
| Friction | Very low (PTFE's non-stick nature) | Moderate; some designs use textured bore |
| Retraction needed | Less (low friction) | More (no PTFE lubricity) |
| Heat creep risk | Higher at elevated temps | Lower with good thermal mass design |
| Jam risk | Lower for flexible filaments | Higher (filament can buckle without PTFE support) |

### Key Hotend Systems

**E3D V6 / Revo**: Industry standard all-metal. Revo adds tool-free nozzle swap; V6 uses standard M6 nozzles. Max 300°C. Ecosystem: Revo Six, Revo Micro, Revo Hemera (integrated extruder).

**Slice Engineering Mosquito**: Copper alloy + strain-hardened steel heat break conducts 85% less heat than standard designs. Rated to 500°C. Uses precision stainless tubing with tight tolerances. Widely used in high-temp printer builds.

**Phaetus Rapido / Dragon**: Conical heat break geometry, copper alloy heater block, titanium alloy throat on Dragon variant. Rapido HF (High Flow) delivers >30 mm³/s volumetric throughput. Temperature range to 450–500°C.

**Dyze Design Pulsar**: Industrial-grade for pellet or filament; 500°C rating, 100 mm³/s volumetric rate for high-throughput applications.

**Bambu X1C hotend**: Proprietary design with hardened steel nozzle, all-metal heat break, integrated strain relief. Rated to 300°C. Auto-nozzle-wipe dock included on machine.

---

## 4. Extruder Systems

### Bowden vs Direct Drive

| Property | Bowden | Direct Drive |
|----------|--------|--------------|
| Moving mass | Very low (motor on frame) | Higher (motor on toolhead) |
| Retraction distance | 4–8 mm (PTFE tube compresses) | 0.5–2 mm |
| Flexible filament | Difficult (buckling in tube) | Feasible |
| Max speed | Higher (low toolhead inertia) | Limited by motor inertia |
| Pressure advance tuning | Critical; large PA values | Simpler; smaller PA values |

### Key Extruder Designs

**E3D Titan**: Dual-stage gear reduction (3:1), widely compatible, lightweight. Mass production workhorse.

**Bondtech BMG (Bimetal Gearbox)**: Dual-drive with opposing drive gears gripping filament from both sides. 3:1 gear ratio. High grip, reliable retraction. Available in left/right-hand variants. Clone market: LGX, LGX Lite.

**Orbiter v2.0**: Ultra-lightweight direct drive (16.8 g). 7.5:1 planetary gear ratio. Designed for high-acceleration systems (Voron, RatRig). Filament path optimized for flexibles.

**Galileo 2**: Voron community design; Orbiter-class weight, uses industry-standard gears. Standalone and toolhead variants (Stealthburner integration).

**Sherpa Mini/Micro**: Dual-drive, ~17 g, designed for Voron Stealthburner toolhead. 50:10 worm gear variant available (Sherpa Nano) for ultra-compact installs.

**Bambu Lab extruder**: Proprietary all-in-one hotend/extruder unit. Motor integrated into toolhead block. Not field-replaceable in standard sense.

### Stepper Torque and Current

Extruder steppers are typically NEMA 14 (small direct drive) or NEMA 17 pancake. Key parameters:
- **Holding torque**: 40–60 mN·m for NEMA 14; 22–40 mN·m for pancake NEMA 17
- **Run current**: 600–900 mA RMS for small motors; set 10–20% below rated to reduce heat
- **Micro-stepping**: 16 or 32 microsteps standard; with TMC drivers, interpolation to 256 microsteps

---

## 5. Electronics and Firmware

### Controller Boards

| Board | MCU | Key Feature | Common Use |
|-------|-----|-------------|------------|
| BTT SKR Mini E3 v3 | STM32G0B1 | Ender 3 drop-in, 32-bit | Budget Cartesian |
| BTT Octopus Pro | STM32H723 | 8 stepper slots, high power | Large Voron, multi-Z |
| Duet 3 Mini 5+ / Mainboard 6HC | SAME70 / STM32H7 | Ethernet, CAN expansion | RRF professional |
| Einsy Rambo | ATmega2560 | Prusa MK3 OEM board | Legacy Prusa |
| Fysetc Spider v2.2 | STM32F446 | 8 steppers, all-in-one | Mid-range CoreXY |
| BTT Manta M8P | STM32H723 | Designed for CM4/CB1 + Klipper | Modern Voron/CoreXY |

### Stepper Drivers

**A4988**: Legacy 2A peak, 16 microstep, no UART. Loud, basic. Obsolete for new designs.

**DRV8825**: 2.2A peak, 32 microstep. Quieter than A4988 but audible whine. No feedback.

**TMC2208**: 2A RMS, SPI/UART configurable. StealthChop2 for silent operation at low speed. SpreadCycle for higher-speed open-loop control. Interpolation to 256 microsteps internally.

**TMC2209**: 2A RMS continuous (2.8A peak). UART configuration. StallGuard4 for sensorless homing (StealthChop mode only — important limitation). CoolStep energy recovery. Most popular choice for modern printers. Sensorless homing accuracy: reliable to ±0.5 mm.

**TMC5160**: 3.2A RMS with external MOSFETs. StallGuard2 (works in SpreadCycle). Higher current capability for larger NEMA 23 motors or Z axes. Used in high-performance CoreXY machines (Voron with Moons motors, BTT Octopus Pro). SPI interface. StallGuard SGT range: -64 (most sensitive) to +63 (least sensitive).

**Current tuning**: Target RMS current = rated peak × 0.707. Set 10–20% below rated for thermal headroom. Interpolation does not affect physical microstepping; motor noise characteristics depend on native microstep count.

### Firmware Architectures

#### Marlin

- **Language**: C++, Arduino-derived; runs fully on printer MCU
- **Architecture**: Monolithic; all kinematics, planning, G-code parsing on 32-bit MCU
- **Strengths**: Ubiquitous, massive compatibility matrix, well-documented, conservative and stable
- **Weaknesses**: Limited by MCU compute for advanced features; input shaping added in Marlin 2.1+ but less capable than Klipper's; configuration via `#define` in C headers (compile to change settings)
- **Used by**: Prusa (Buddy firmware fork), Creality legacy, most off-the-shelf consumer printers

#### Klipper

- **Language**: Python on host (Raspberry Pi / SBC); C microcode on MCU
- **Architecture**: Distributed; host handles G-code parsing, motion planning, pressure advance, input shaping; MCU handles only step timing and GPIO
- **Strengths**: Runtime configuration via `printer.cfg` (no recompile); superior input shaping (multiple shaper algorithms); scripting via macros; extensive community plugin ecosystem; supports multiple MCUs natively (CAN toolhead boards)
- **Weaknesses**: Requires SBC host; more components = more failure points; learning curve; no official UI (relies on Mainsail/Fluidd/OctoKlipper)
- **Input shaping**: ADXL345 or LIS2DW accelerometers; `SHAPER_CALIBRATE` command sweeps frequencies 5–133 Hz; automatically selects EI, MZV, 2HUMP_EI, ZV, or ZVDD filter; reduces ringing artifacts by 70–90%; allows 40–60% speed increase without quality degradation
- **Pressure advance**: Compensates for pressure buildup in melt zone; typical values: PLA 0.03–0.06, PETG 0.06–0.10, flexible 0.0–0.02. `PRESSURE_ADVANCE_SMOOTH_TIME` (default 0.040 s) governs smoothing window
- **Used by**: Voron, most prosumer DIY, Creality K1/K2, Bambu (heavily modified), Qidi, Sovol SV08

#### RepRapFirmware (RRF)

- **Language**: C++; runs on Duet boards (SAME70 or STM32)
- **Architecture**: Monolithic but high-performance; Duet 3 adds object model for live state query
- **Strengths**: Professional-grade; native Ethernet; CAN bus expansion (Duet 3 ecosystem); tool-based multi-extruder architecture; excellent documentation; time-based motion planning
- **Weaknesses**: Tied to Duet hardware ecosystem; smaller community; less third-party plugin ecosystem
- **G-code flavor**: Close to RepRap standard but adds M-code extensions (M671 for auto-tilt, M558 for probe config)
- **Used by**: Professional/industrial DIY, Jubilee toolchanger, some medical/research printers

### Endstops and Probing

| Type | Mechanism | Accuracy | Notes |
|------|-----------|----------|-------|
| Mechanical switch | Physical contact | ±0.05 mm | Reliable, durable, common |
| Optical (slot/reflective) | IR beam interruption | ±0.01 mm | Cleaner signal, no mechanical wear |
| Hall effect | Magnetic field | ±0.05 mm | Used on Prusa MK3/MINI |
| BLTouch / CR Touch | Servo-deployed pin | ±0.005 mm | Widely used, needs Z offset tuning |
| Klicky probe | Magnetic dock/undock | ±0.004 mm | Popular Voron community design |
| Voron Tap | Nozzle as probe via optical + rail | ±0.0004 mm | Most accurate; nozzle directly senses |
| Beacon (eddy current) | Induction to metal bed | ±0.001 mm | Non-contact, very fast scan, temperature-sensitive |
| PINDA v2 (Prusa) | Inductive, temperature-compensated | ±0.01 mm | Steel sheet trigger |

**Mesh bed leveling**: Samples N×N grid (typically 3×3 to 7×7), applies bilinear or bicubic interpolation to Z offset during print. Klipper's `bed_mesh` and Marlin's UBL (Unified Bed Leveling) are the primary implementations.

---

## 6. Slicers and Software

### Architecture and Lineage

```
Slic3r (original, Alessandro Ranellucci)
  └── PrusaSlicer (Prusa Research fork, C++, LibBGCode backend)
        └── SuperSlicer (community fork, more experimental features)
        └── Bambu Studio (Bambu Lab fork of PrusaSlicer)
              └── OrcaSlicer (SoftFever community fork of Bambu Studio)

Cura (Ultimaker, C++ + Python, own engine "CuraEngine")
  └── ArcWelder, Creality Print (Cura-based variants)
```

### Comparison Table

| Feature | PrusaSlicer | OrcaSlicer | Cura | Bambu Studio |
|---------|-------------|------------|------|--------------|
| Engine | libslic3r | libslic3r (fork) | CuraEngine | libslic3r (fork) |
| Speed | Fast | Faster (GPU-assisted) | Fast | Moderate |
| Multi-material | Yes (wipe tower) | Yes (enhanced) | Yes | Yes (AMS-optimized) |
| Calibration tools | Moderate | Extensive built-in | Plugins | Bambu-specific |
| Profile ecosystem | Prusa-centric | Multi-brand | Very broad | Bambu-centric |
| Pressure advance | Yes | Yes (extended) | Linear Advance (Marlin) | Yes |
| Variable layer height | Yes | Yes | Yes | Yes |
| Ironing | Yes | Yes | Yes | Yes |
| Fuzzy skin | Yes | Yes | Yes | No |
| Network send | Prusa Connect | OctoPrint/Moonraker | OctoPrint | Bambu Cloud/LAN |
| License | AGPLv3 | AGPLv3 | LGPLv3 | Proprietary |

### G-code Dialect Differences

| Firmware | Start G-code Behavior | Pressure Advance | Notes |
|----------|----------------------|------------------|-------|
| Marlin | M190/M109 blocking | `M900 K<value>` (Linear Advance) | M-code heavy |
| Klipper | `PRINT_START` macro | `SET_PRESSURE_ADVANCE ADVANCE=<value>` | Macro-centric |
| RRF | `G29` for mesh, tool T0/T1 | `M572 D0 S<value>` | Tool-indexed |
| Bambu | Custom `{if}` conditionals | Internal (not user-visible) | Proprietary extensions |

**Critical G-code differences for AI control systems**:
- Klipper does not support `M109`/`M190` wait-for-temp semantics by default — requires `TEMPERATURE_WAIT` or custom macros
- Bambu printers reject raw G-code from external senders; control is exclusively via MQTT command messages
- RRF uses `G32` for auto-tramming (not `G28`+`G29`), `M671` for independent Z motor calibration

---

## 7. Materials Science

### Common Thermoplastics — Engineering Parameters

| Material | Print Temp (°C) | Bed Temp (°C) | Chamber | Tg (°C) | Hygroscopic | Notes |
|----------|----------------|---------------|---------|----------|-------------|-------|
| PLA | 180–220 | 60 | No | 55–65 | Low | Brittle, UV-sensitive, easy to print |
| PLA+ / PLA-CF | 200–230 | 60–65 | No | 55–65 | Low | Improved toughness; CF requires hardened nozzle |
| PETG | 230–250 | 70–90 | Optional | 80 | Moderate | Excellent layer adhesion, food-safe variants |
| ABS | 230–250 | 100–110 | Required (~50°C) | 105 | Low | Warps without enclosure, acetone smoothable |
| ASA | 240–260 | 100–110 | Required | 100 | Low | UV-resistant ABS replacement |
| TPU 95A | 210–240 | 30–60 | No | −40 | Low | Flexible; direct drive strongly preferred |
| TPE (Soft) | 200–230 | 40–60 | No | −60 | Low | Shore 60–80A; very flexible |
| Nylon PA6 | 240–260 | 70–90 | Beneficial | 47 | Very high | Absorbs moisture rapidly; critical drying |
| Nylon PA12 | 240–260 | 80–100 | Beneficial | 37 | High | Less hygroscopic than PA6; better for production |
| Nylon PA-CF | 260–280 | 80–100 | Yes | 160+ | High | Continuous or chopped fiber; abrasive |
| Polycarbonate | 270–310 | 110–120 | Required (~70°C) | 147 | Moderate | High impact; very prone to warping |
| PEEK | 400–450 | 120–160 | 90–120°C | 143 | Low | Semi-crystalline; requires all-metal hotend, high-temp chamber |
| PEI (Ultem 1010) | 370–420 | 160 | 90–120°C | 217 | Low | Flame-retardant; superior to PEEK for thermal stability at lower cost |
| PEKK | 360–400 | 150 | 90–120°C | 155–165 | Low | Semi-crystalline variant of PEK; aerospace applications |

### Drying Requirements

| Material | Temperature | Time | Storage |
|----------|-------------|------|---------|
| PLA | 45–50°C | 4–6 h | Sealed bag + desiccant |
| PETG | 65°C | 4–6 h | Sealed bag |
| Nylon PA6/PA12 | 80°C | 8–12 h | Vacuum seal; re-dry after 30 min in open air |
| ABS/ASA | 60–80°C | 4 h | Sealed bag |
| TPU | 65°C | 4–6 h | Dry box printing recommended |
| PC | 80–100°C | 8 h | Critical; any moisture causes steam bubbles |
| PEEK | 150°C | 4 h (or 190°C for 2 h) | Sealed at all times |
| PEI/Ultem | 150°C | 4+ h | Vacuum |

### Composite and Specialty Filaments

**Carbon fiber (chopped)**: 50–200 µm chopped fibers increase stiffness, reduce weight. Abrasive — mandatory hardened steel or ruby nozzle. Reduces elongation at break significantly.

**Glass fiber**: Less abrasive than CF; improves stiffness and temperature resistance with lower anisotropy than CF. PA-GF popular for automotive brackets.

**Kevlar (Aramid)**: Anti-abrasion parts; fibers are less stiff than CF but very tough. Requires hardened nozzle, very slow print speeds (20–30 mm/s for continuous strand).

**Continuous fiber (Markforged)**: In-layer continuous strands of CF, Kevlar, fiberglass, or HSHT fiberglass. Achieves 60–70% of aluminum tensile strength in CF composite. Requires dedicated second extruder for fiber vs matrix material.

**Metal fill (PLA-Bronze, PLA-Steel)**: 30–50% metal powder by weight. Can be polished, machined, electroplated. Very abrasive. Purely cosmetic — not structurally superior to base PLA.

**PVA**: Water-soluble support material; requires dry storage (absorbs moisture in hours at room humidity). Print at 190–210°C. Dissolve in agitated water (4–16 h depending on infill).

**HIPS**: Limonene-soluble; ABS support material. Dissolve in d-Limonene. Less hygroscopic than PVA.

**Conductive PLA**: ~15 Ω·cm resistivity; useful for sensors, capacitive switches. Not suitable for power conduction.

---

## 8. Major Brands and Models

### Prusa Research

| Model | Motion | Extruder | Max Temp | Build Volume | API |
|-------|--------|----------|----------|-------------|-----|
| MK4 | Cartesian | Nextruder (8:1 ratio) | 290°C | 250×210×220 mm | PrusaLink REST |
| MK4S | Cartesian | Nextruder + Input Shaping | 290°C | 250×210×220 mm | PrusaLink REST |
| XL | CoreXY (5-tool option) | Nextruder × 1–5 | 290°C | 360×360×360 mm | PrusaLink REST |
| MINI+ | Cartesian | Nextruder (Bowden) | 280°C | 180×180×180 mm | PrusaLink REST |

**PrusaLink API**: REST API at `http://<ip>/api/v1/` with `X-Api-Key` header authentication. Key endpoints:
- `GET /api/v1/printer` — printer status (state, temperatures, fan speeds)
- `GET /api/v1/job` — current job info (file, progress, time remaining)
- `POST /api/v1/files` — upload G-code
- `PUT /api/v1/job` — start/pause/resume/cancel job

**Prusa Connect**: Cloud relay platform; printers register via token; camera snapshots, remote monitoring, print queue. Mobile API at `connect-mobile-api.prusa3d.com`. OpenAPI spec published on GitHub.

### Bambu Lab

| Model | Motion | Max Speed | Build Volume | Chamber | AMS | API |
|-------|--------|-----------|-------------|---------|-----|-----|
| A1 | Cartesian (bed slinger) | 500 mm/s | 256×256×256 mm | No | Yes (AMS lite 4-color) | MQTT |
| A1 Mini | Cartesian | 500 mm/s | 180×180×180 mm | No | Optional | MQTT |
| P1P | CoreXY | 500 mm/s | 256×256×256 mm | Partial | Yes (4-color) | MQTT |
| P1S | CoreXY | 500 mm/s | 256×256×256 mm | Full, 65°C active | Yes | MQTT |
| X1C | CoreXY + LiDAR | 500 mm/s | 256×256×256 mm | Full, 65°C | Yes | MQTT |
| X1E | CoreXY + IDEX | 500 mm/s | 256×256×220 mm | Full, 65°C | Yes | MQTT |
| H2D | CoreXY, Dual hotend | 600 mm/s | 350×320×325 mm | 65°C active | AMS 2 Pro × 4 (24 slots) | MQTT |

**Bambu MQTT Protocol**:
- Port 8883 (TLS); local LAN access uses per-printer LAN access code as MQTT password
- Username: `bblp`; Password: printer's LAN access code (shown in Settings > Network)
- Topics: `device/<serial>/report` (subscribe for status), `device/<serial>/request` (publish commands)
- As of January 2025 firmware, authentication is mandatory; X.509 certificate extracted from Bambu Connect binary needed for TLS cert bypass in third-party clients
- Community documentation: OpenBambuAPI by Doridian on GitHub

**AMS (Automatic Material System)**:
- AMS 2 Pro: 4 filament slots, brushless servo motors, active drying with sealed system
- AMS HT: High-temperature variant for PA, PC, ABS
- Maximum configuration on H2D: 4× AMS 2 Pro + 8× AMS HT = 24 material slots + 1 external = 25 simultaneous colors
- Filament runout detection, RFID tag reading for Bambu-brand filament parameter auto-load

**X1C LiDAR**: 3D surface scan used for: first-layer calibration (offset correction), spaghetti detection (flow anomaly), nozzle tip inspection, multi-color registration.

### Creality

| Model | Firmware | Max Speed | Build Volume | Key Feature |
|-------|----------|-----------|-------------|-------------|
| Ender 3 V3 KE | Klipper | 500 mm/s | 220×220×250 mm | Budget Klipper entry |
| K1 | Custom Klipper | 600 mm/s | 220×220×250 mm | CoreXY, enclosed |
| K1C | Custom Klipper | 600 mm/s | 220×220×250 mm | Carbon fiber support |
| K1 Max | Custom Klipper | 600 mm/s | 300×300×300 mm | Larger build volume |
| K2 Plus | Custom Klipper | 600 mm/s | 350×350×350 mm | APUS extruder, closed-loop |
| CR-10 Smart Pro | Marlin | 180 mm/s | 300×300×400 mm | Auto-leveling |

**Creality API**: K1/K2 series run a Moonraker-compatible API layer; community projects exist (`moonraker-Creality-K1`). Creality Print software manages fleets of K-series printers natively.

### Voron Design

Community-designed open-source printers; all run Klipper. Sold as kits or self-sourced.

| Model | Kinematics | Build Volume | Key Spec |
|-------|-----------|-------------|----------|
| Voron 0.2 | CoreXY (micro) | 120×120×120 mm | Ultra-compact |
| Voron Trident | CoreXY (fixed bed, 3-point Z) | 250/300/350 mm³ | Excellent rigidity |
| Voron 2.4 | CoreXY (flying gantry, 4-point Z belts) | 250/300/350 mm³ | Gold standard DIY |
| Voron Switchwire | CoreXZ (bed slinger Z) | 250×210×200 mm | Ender 3 form factor |

**Voron 2.4 engineering specifics**:
- 4 independent Z motors belt-driven for gantry tramming (`QUAD_GANTRY_LEVEL`)
- CAN bus toolheads: BTT EBB SB2209, Mellow SB2040, BTT EBB36 via CAN bridge board (BTT U2C or similar)
- Voron Tap: optical switch triggered by entire toolhead deflection on Z probe; accuracy to ±0.4 µm
- Stealthburner toolhead: accommodates most extruder/hotend combinations via modular face plate

### UltiMaker (formerly Ultimaker)

| Model | Technology | Build Volume | Key Spec |
|-------|-----------|-------------|----------|
| S5 | Bowden dual extrusion | 330×240×300 mm | 280°C, 0.25–0.8 mm nozzles |
| S7 | Bowden dual + Air Manager | 330×240×300 mm | Active filtered enclosure |
| Factor 4 | IDEX | 330×240×300 mm | Industrial FDM, 280°C, active chamber |

UltiMaker printers expose a REST API (`/api/v1/`) compatible with OctoPrint-style tooling; Cura natively integrates with UltiMaker fleet via UltiMaker Digital Factory cloud.

### Markforged

| Model | Technology | Max Temp | Key Feature |
|-------|-----------|----------|-------------|
| Onyx One | FFF (Onyx matrix) | 260°C | No fiber; strongest FFF nylon |
| Mark Two | FFF + CFF (Continuous Fiber) | 260°C | CF, Kevlar, fiberglass, HSHT fiberglass |
| X7 | FFF + CFF | 315°C | Industrial CFF |
| FX20 | FFF + CFF | 315°C | Large format industrial |
| Metal X | FFF (bound metal) | 350°C | 17-4PH SS, H13, copper; sinter separately |

**Eiger platform**: Cloud-based slicer + fleet management + file repository. Eiger Fleet API enables ERP/MES integration; G-code generated server-side; printers receive encrypted job packages. No open G-code access — vertically integrated stack.

### Stratasys (Industrial FDM)

Stratasys coined "FDM" — proprietary term. Industrial systems use precision extrusion, heated chambers (45–70°C), and soluble support (SR-35, SR-110):

- **F123 series** (F170/F270/F370): Office-friendly; ASA, ABS-CF10, PLA, PC-ABS; Insight slicer; GrabCAD Print software with fleet management
- **Fortus 380mc / 450mc**: Production-grade; ULTEM 9085, ULTEM 1010, PC, Nylon 12CF; 450mc handles 33 material types
- **API**: GrabCAD Print REST API for job submission, fleet monitoring; requires GrabCAD license

### Other Notable Vendors

**Artillery Sidewinder X4 Pro / Genius Pro**: Budget CoreXY; Klipper; 300 mm/s; dual-Z; popular for upgrades.

**AnkerMake M5C / M5**: Klipper-based; 500 mm/s claimed; AnkerMake app (cloud-centric) + local API; good camera integration.

**Qidi X-Max 3 / X-Plus 3**: Enclosed CoreXY; high-temp chamber (60°C); PA, ABS, PC support; Klipper variant; 600 mm/s.

**Sovol SV08**: Voron-inspired CoreXY; 700 mm/s; Klipper; open community mod ecosystem.

**Elegoo Neptune 4 Pro / Max**: Klipper; 500 mm/s; budget; large community.

### Hotend Ecosystem

| Vendor | Key Products | Temp Rating | Specialty |
|--------|-------------|-------------|----------|
| E3D | V6, Revo Six/Micro/Hemera | 300°C | Universal standard, nozzle ecosystem |
| Slice Engineering | Mosquito, Mosquito Magnum+ | 500°C | Heat creep elimination, industrial |
| Phaetus | Dragon, Dragonfly, Rapido HF | 450–500°C | High flow, popular Voron choice |
| Dyze Design | Pulsar, DyzeXtruder GT | 500°C | Pellet + filament, high-throughput |
| Bondtech | BMG, LGX, LGX Lite, CHT nozzle | 300°C | CHT nozzle splits flow for >3× flow rate |

---

## 9. Remote Management and APIs

### OctoPrint

**REST API** (base path `/api/`):
- Auth: `X-Api-Key` header or `apikey` query param
- `GET /api/version` — server + API version
- `GET /api/printer` — full printer state (temp, flags)
- `GET /api/job` — current job (file, progress, time left, time elapsed)
- `POST /api/job` — start/cancel/pause/restart
- `POST /api/files/local` — upload G-code
- `GET /api/files` — list uploaded files
- `POST /api/printer/command` — send arbitrary G-code (`{"command": "G28"}`)
- `GET /api/printer/tool` — hotend temps
- `POST /api/printer/tool` — set hotend target

**WebSocket** (path `/sockjs/websocket` or `/sockjs/<n>/<token>/websocket`):
- Auth flow: `GET /api/login?passive=true&apikey=...` → get `name` + `session`; send `auth` message to socket
- Event messages: `current` (state + temp updates at ~1 Hz), `history` (initial state dump), `event` (print start/complete/fail), `plugin` (plugin-specific events)
- Throttle control: send `{throttle: N}` where N is multiplier on 500 ms base interval

**Plugin ecosystem**: ~300 plugins; notable for AI control: Obico (failure detection), OctoEverywhere (remote tunnel), BedLevelVisualizer, PrintTimeGenius, MultiCam.

### Moonraker + Klipper

Moonraker is a Python web API server sitting in front of Klipper. Exposes two transports:

**HTTP (REST-ish)**: `http://<host>/` — note: not `/api/` prefix
- `GET /printer/info` — Klipper version, state
- `GET /printer/objects/query?extruder&heater_bed` — query any Klipper object state
- `POST /printer/gcode/script` — send G-code (`{"script": "G28"}`)
- `GET /server/files/list?root=gcodes` — list files
- `POST /server/files/upload` — multipart file upload
- `GET /printer/print/start?filename=<file>` — start print
- `POST /printer/print/pause` / `/printer/print/resume` / `/printer/print/cancel`
- `GET /server/history/list` — print history
- `GET /machine/system_info` — host system info

**WebSocket** (primary): JSON-RPC 2.0 over WebSocket at `ws://<host>/websocket`
- `subscribe_objects` method for live state push at configurable rate
- Real-time G-code console stream via `gcode_response` notifications

Mainsail and Fluidd are Vue.js SPAs that consume only the Moonraker API.

### Bambu Connect

- Protocol: MQTT over TLS port 8883
- **Local mode**: Printer IP as broker; credentials: username `bblp`, password = LAN access code
- **Cloud mode**: Bambu broker (`us.mqtt.bambulab.com`); authentication via user token; all data routed through cloud
- **Key MQTT topics**:
  - `device/<SN>/report` — printer publishes status (JSON with print progress, temps, errors, AMS state)
  - `device/<SN>/request` — client publishes commands (start, stop, pause, change temp)
- **File transfer**: FTPS to printer (`ftp://<ip>:990/`) for G-code upload; printer does not accept raw G-code via MQTT
- **Third-party access**: Bambu Jan 2025 firmware mandated authenticated access; community projects reverse-engineered X.509 client certificates from Bambu Connect binary to restore third-party TLS handshake

### Obico (formerly The Spaghetti Detective)

- Open-source self-hostable + cloud SaaS
- AI model: custom neural network (YOLO-derived) analyzing camera frames at ~1 FPS
- Detection types: spaghetti, warping, blobbing (cloud); layer shift and stringing in development
- Integration: OctoPrint plugin, Moonraker native integration
- Self-hosted: Docker deployment; `docker-compose.yml` provided; NVIDIA GPU optional for inference
- API: REST at `/api/v1/`; WebSocket for real-time alert streaming

### SimplyPrint and OctoFarm

**SimplyPrint**: Cloud fleet management SaaS; supports OctoPrint + Klipper printers; AI failure detection; filament tracking; job queue; custom profiles per printer.

**OctoFarm**: Self-hosted fleet management for OctoPrint instances; open-source Node.js app; centralized job dispatch, monitoring dashboard.

### Duet Web Control (RRF)

Native UI for RepRapFirmware; communicates with Duet 3 boards via HTTP REST (`/rr_<command>` endpoints or modern `GET /machine/` JSON object model). No external dependency — runs on Duet's onboard webserver.

---

## 10. API Integration Quick Reference

| Platform | Protocol | Auth | Port | File Transfer |
|----------|---------|------|------|--------------|
| OctoPrint | REST + WebSocket | `X-Api-Key` header | 5000 (default) | `POST /api/files/local` multipart |
| Moonraker (Klipper) | REST + JSON-RPC WS | API key or no auth (local) | 7125 | `POST /server/files/upload` multipart |
| PrusaLink | REST | `X-Api-Key` header | 80 | `POST /api/v1/files` multipart |
| Bambu (local) | MQTT TLS | LAN access code | 8883 | FTPS port 990 |
| Bambu (cloud) | MQTT TLS | User JWT | 8883 | Via cloud relay |
| Duet RRF | REST (`/rr_*`) | Password (optional) | 80 | `POST /rr_upload?name=<path>` |
| Markforged Eiger | REST (Eiger API) | API key | 443 (cloud) | Cloud-only |
| UltiMaker | REST (`/api/v1/`) | Digest auth | 80 | `POST /api/v1/print_job` |

---

## 11. Calibration and Print Quality

### First Layer Calibration

The single most important calibration step. Nozzle-to-bed distance (Z offset) must be within ±0.05 mm:
- **Live Z adjust**: Fine-tune during first layer print; Prusa MK4 has dedicated Live Adjust Z knob
- **Baby stepping**: Marlin `M290` / Klipper `SET_GCODE_OFFSET Z_ADJUST=0.025` for micro-adjustments
- **Squish targets by material**: PLA 0.1–0.2 mm squish; PETG less squish (tends to stick to nozzle); ABS more squish for adhesion

### Flow Rate Calibration

1. Print single-wall perimeter cube, measure wall thickness with calipers
2. Target: 0.4 mm nozzle → 0.4 mm wall; if measuring 0.42 mm → reduce flow by 5%
3. Extrusion multiplier (slicer) or `M221 S<percent>` (Marlin) / `SET_EXTRUDE_FACTOR` (Klipper)

### Retraction Calibration

Print retraction tower varying retraction distance (0–8 mm Bowden; 0–2 mm direct drive) and speed. Evaluate stringing at temperature towers.

### Dimensional Accuracy

- **XY compensation**: Measure hole diameter vs nominal; apply in-slicer XY size compensation or `M206` offset
- **Elephant foot**: First layer squish causes slight flaring; compensate with positive Z offset or slicer "elephant foot compensation" setting
- **Aspect ratio errors**: Usually belt tension; CoreXY tension imbalance causes 45° rhombus deformation

### Surface Finish Enhancement

- **Ironing**: Flat top surfaces re-melted with low flow nozzle pass; reduces surface roughness from 5–10 µm Ra to ~2 µm Ra
- **Fuzzy skin**: Deliberate surface texture for grip; algorithm adds noise to perimeter paths
- **Post-processing**: ABS — acetone vapor smoothing; PLA — XTC-3D epoxy coat; PETG — sanding + primer

---

## 12. Failure Modes and Diagnostics

### Thermal Runaway

**Definition**: Temperature drops > N°C from target for > T seconds while heater is active → firmware emergency stop, disables all heaters and steppers.

**Marlin**: `THERMAL_PROTECTION_HOTENDS` enabled; default threshold 15°C over 45 seconds.
**Klipper**: `verify_heater` section; `check_gain_time` and `hysteresis` parameters.

**Causes**: Thermistor wire failure (resistance spike → apparent temperature drop → heater commanded full power → fire risk), loose heater block, fan failure cooling heater block, drafts. This is a **fire safety feature** — never disable.

### Heat Creep

**Symptoms**: Gradually increasing under-extrusion over 30–60 minutes; eventually jams completely; filament grinds at extruder.
**Diagnosis**: Remove filament after jam; look for bulge above heat break.
**Fix**: Increase cold-side fan speed, reduce ambient temperature, upgrade to all-metal hotend with better heat break geometry.

### Layer Shifting

**Causes**: Motor skipped steps (current too low, acceleration too high, obstruction), loose belt, print head collision with warp.
**Diagnosis in Klipper**: `DUMP_TMC STEPPER=stepper_x` for StallGuard readings.
**Fix**: Increase motor current (careful of thermal limits), reduce acceleration, enable sensorless homing with proper tuning.

### Stringing

**Causes**: Ooze during travel moves; material-dependent (PETG notorious).
**Fix matrix**:
- Increase retraction distance/speed
- Increase travel speed
- Lower print temperature
- Enable "wipe on retract" / "z-hop"
- Tune pressure advance

### Warping

**Causes**: Differential thermal contraction; ABS, PC, Nylon most susceptible.
**Mitigations**: Heated chamber, PEI build surface, brim/raft, draft shield, eliminate drafts, first layer temperature +5°C.

### Spaghetti Detection (AI)

Spaghetti occurs when print detaches from bed or layer shift causes extrusion in air. AI detection approaches:
- **Frame differencing**: Compare sequential frames; anomalous blobs outside expected build area
- **Neural network (Obico)**: YOLO-style detector trained on labeled failure images; confidence score triggers pause/alert
- **Bambu LiDAR**: Point cloud comparison against expected layer profile; deviation > threshold triggers error
- **Structured light**: Experimental; projects grid pattern to detect surface deviation

---

## 13. Print Farms and Fleet Management

### Job Queuing Strategies

- **FIFO per printer**: Simple; each printer runs its own queue independently
- **Central dispatcher**: Single scheduler evaluates printer availability, material loaded, part size, and dispatches next job
- **Capability matching**: Job requires PA-CF at 280°C → scheduler routes only to enclosed high-temp printers

### Filament Cost and Spool Tracking

- Slicer-reported filament length × material density × $/kg = cost per part
- Spool weight tracking: load cell under spool holder for real-time remaining weight
- RFID-tagged spools (Bambu AMS) enable automatic profile switching and remaining filament tracking

### Automated Bed Clearing

Approaches for lights-out operation:
1. **Gantry purge arm sweep**: Angled wiper mounted at bed edge; gantry sweeps finished part off
2. **Conveyor belt bed**: Kapton-coated belt; at completion, belt advances, drops part into bin
3. **Eject macro**: Klipper macro `PRINT_END` that heats bed slightly to release PEI adhesion, then quick Y-axis move

---

## 14. Industry Trends (2025–2026)

### High-Speed FFF

Consumer printers now routinely achieve 300–600 mm/s with input shaping. Physical limits:
- **Volumetric throughput** is the real bottleneck: standard 0.4 mm nozzle at 0.2 mm layer caps at ~15–20 mm³/s; Bambu/Creality K series use high-flow hotends achieving 35–45 mm³/s
- **Input shaping** enables 20,000–50,000 mm/s² acceleration without ringing
- **Resonance compensation** in Bambu X1C uses LiDAR to indirectly measure resonance; Klipper uses ADXL345 accelerometers directly

### Multi-Material Advancement

- AMS-style buffered filament selectors: Bambu AMS, Prusa MMU3, ERCF (Enraged Rabbit Carrot Feeder — community)
- Color count: 4 (standard AMS) → 16 (two AMS units) → 25 (Bambu H2D maximum)
- Purge volume reduction: slicers increasingly optimize tower purge using color transition matrices

### Metal FFF (Bound Metal)

Three-step process:
1. **Print**: Filament = 85–90% metal powder + 10–15% polymer binder. Print at 160–220°C
2. **Debind**: Chemical (solvent) or catalytic debinding removes primary binder
3. **Sinter**: Furnace at 1300–1400°C; ~20% linear shrinkage (isotropic — predictable; slicers apply scale factor)

Key materials: 316L stainless (BASF Ultrafuse 316L, print at 230–240°C), 17-4PH, copper, H13 tool steel. Final part: ~96% density, 480 MPa UTS for 316L.

### Closed-Loop Control

- **Linear encoders on axes**: Experimental; measures actual position vs commanded
- **Closed-loop extrusion**: Filawatch-style filament diameter sensors (±0.01 mm resolution) feeding back for real-time flow compensation
- **Load cell probing**: Nozzle-as-probe via load cell (Beacon, Voron Tap)

---

## 15. Nozzle Material Selection Guide

| Nozzle Material | Materials Printable | Max Temp | Notes |
|----------------|--------------------|---------|---------|
| Brass (E3D standard) | PLA, PETG, ABS, TPU | 300°C | Best thermal conductivity; not abrasion-resistant |
| Hardened steel | All including CF, GF, Kevlar | 500°C | 3× less conductive than brass; may need +5°C |
| Tungsten carbide | All ultra-abrasive | 500°C | Most durable; very expensive |
| Ruby-tipped | All | 450°C | Sapphire orifice; excellent abrasion resistance; brittle |
| Stainless steel | Food-safe printing | 300°C | No zinc/lead leaching; lower conductivity |
| Copper alloy (NF) | High-flow PLA/PETG | 300°C | Highest thermal conductivity; soft, wears quickly |

---

## 16. Key Engineering Constants

| Parameter | Typical Value | Notes |
|-----------|--------------|-------|
| Filament diameter tolerance | ±0.02 mm (quality) / ±0.05 mm (budget) | Cross-section variation → ±10% flow variation |
| Nozzle orifice diameter | 0.1–1.2 mm | 0.4 mm universal standard |
| Layer height range | 25–75% of nozzle diameter | 0.1–0.3 mm for 0.4 mm nozzle |
| Standard print temp range | 180–350°C | Material dependent |
| Maximum mainstream FFF temp | 500°C (Mosquito/Dragon) | PEEK/Ultem/PEEK-CF |
| Belt pitch (GT2) | 2 mm | 20-tooth pulley = 40 mm/rev |
| Steps/mm (1.8° motor, 16x, GT2/20T) | 80 steps/mm | Standard Cartesian/CoreXY |
| Volumetric flow (standard) | 10–20 mm³/s | 0.4 mm nozzle, 0.2 mm layer, 200 mm/s |
| Volumetric flow (high-flow) | 30–45 mm³/s | Bambu, Rapido HF, CHT nozzle |
| Pressure advance typical range | 0.02–0.10 | Material and hotend dependent |
| Input shaper frequency range | 20–100 Hz | Resonant frequency of printer axis |
