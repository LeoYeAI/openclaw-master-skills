# Laser Cutters & Laser Engravers: Engineering Reference

---

## 1. Core Physics & Laser Science

### How Laser Cutting Works

Laser cutting is a subtractive thermal process. A focused, high-intensity beam deposits energy into a small spot on the material. The interaction mechanism depends on material type and power density:

- **Thermal ablation**: Material heats rapidly, sublimating directly from solid to vapor. Common in organic materials (wood, acrylic).
- **Melt + blow**: Material melts and is ejected by assist gas pressure. Dominant in metal cutting.
- **Vaporization**: At extreme power densities (fiber on thin metal), material vaporizes nearly instantaneously — minimal melt zone.
- **Photon absorption**: Absorption coefficient is wavelength-dependent — the root reason different laser types suit different materials.

### Laser Types

#### CO2 Lasers (10,600nm)

CO2 lasers use an electrically stimulated gas mixture — typically CO2, N2, and He — to generate photons at 10,600nm (far infrared). Two resonator designs:

| Property | DC Glass Tube | RF Metal Tube |
|---|---|---|
| Excitation | Direct current, high-voltage electrodes | Radio frequency (13.56 MHz or 27.12 MHz) |
| Cooling | Water-cooled (mandatory) | Air-cooled (lower wattages) or water-cooled |
| Lifespan | 1,500–3,000 hours | 20,000–50,000 hours |
| Refillable | Sometimes (specialized shops) | Yes, by manufacturer |
| Cost | Low ($100–$400 replacement) | High ($1,000–$10,000+) |
| Pulse quality | Lower repetition rate | Excellent, high-frequency PWM |
| Applications | Desktop/prosumer machines | Trotec, Epilog, ULS professional machines |

Glass tubes use a water jacket — distilled or deionized water circulated by a chiller (CW-3000 for <60W, CW-5200 for 60–150W). RF tubes have sealed gas cavities in metal/ceramic housings.

#### Diode Lasers (400–450nm blue; 808nm, 940nm infrared variants)

Diode lasers use semiconductor junctions (GaN for blue; GaAs for IR). Desktop machines use:

- **Single emitter stacks**: Multiple discrete emitters combined via micro-optics (beam combining or polarization multiplexing) — Nichia NUBM/NUGM series.
- **Multi-diode combiner modules**: xTool, Sculpfun, and Ortur stacking multiple 5–10W diodes to reach "20W," "40W," or higher.
- **Marketing dishonesty**: Manufacturers frequently conflate **electrical input watts** with **optical output watts**. A "20W" module may have 20W electrical input but only 5–10W optical output. Always verify optical watt specs.

Diode lasers at 450nm have poor absorption in transparent and reflective materials. Clear acrylic passes most of the beam; bare aluminum reflects it. They excel at anodized aluminum, wood, leather, dark polymers.

#### Fiber Lasers (1,064nm)

Fiber lasers use a rare-earth-doped optical fiber (typically Ytterbium, Yb) as the gain medium, pumped by diode bars. Two delivery modes:

- **Gantry delivery**: Fiber beam delivered to a moving head — large-format sheet metal cutting (Trumpf, Bystronic).
- **Galvo scanning**: Fixed fiber source, beam steered by two high-speed galvanometer mirrors + F-theta lens. Fast marking speeds (up to 10,000mm/s), small work area (110×110mm to 300×300mm typical).

**MOPA (Master Oscillator Power Amplifier)**: Pulse width (1–500ns) and repetition rate (1–4000kHz) are independently adjustable. Required for color marking on stainless steel and titanium — oxide layer thickness is tuned by varying pulse parameters to produce structural color.

#### Nd:YAG (1,064nm, pulsed)

Older solid-state laser, largely replaced by fiber lasers. Lamp-pumped Nd:YAG: lamp replacement every 500–1,000 hours. Still found in legacy industrial marking systems.

### Wavelength and Material Absorption

| Wavelength | Best materials | Poor materials |
|---|---|---|
| 10,600nm (CO2) | Wood, MDF, acrylic, glass, leather, rubber, fabric, stone | Bare metals (high reflectivity), clear thin films |
| 1,064nm (fiber) | Metals (steel, aluminum, copper, brass, gold), ceramics | Most organics (pass-through), acrylic |
| 450nm (diode blue) | Dark/opaque organics, anodized aluminum, powder coat | Clear acrylic, transparent materials, bare metal |

### Beam Quality: M² Factor

M² quantifies departure from an ideal Gaussian (TEM00) beam:

- **M² = 1.0**: Perfect Gaussian — theoretical minimum spot size.
- **M² = 1.05–1.2**: Single-mode fiber laser — near-perfect.
- **M² = 1.2–1.8**: Well-designed CO2 with metal RF tube.
- **M² = 2–5**: Typical CO2 glass tube machines — multi-mode.
- **M² > 5**: Multi-mode diode, especially combined emitter stacks.

Minimum spot diameter: `d = (4λ/π) × M² × f / D` where f is focal length and D is beam diameter at lens. Higher M² forces a larger minimum spot — less peak intensity, reducing cutting ability.

### Focus, Spot Size, and Depth of Field

- **Focal length**: Shorter FL (1.5") gives smaller spot, shallower depth of field. Longer FL (2.5" or 4") gives larger spot but deeper DOF — useful for thick material cuts.
- **Spot size**: CO2 at 1.5" FL typically 0.1–0.3mm. Fiber galvo with F-theta: 0.02–0.05mm.
- **Depth of field (Rayleigh range)**: Axial range over which the beam remains near-focused. Important when cutting thick material.

### Kerf Width

Kerf is the material removed by the cutting beam. Design files must compensate for kerf or the part will be undersized:

- CO2, wood/acrylic: 0.1–0.3mm kerf typical
- CO2, thin metal with assist gas: 0.05–0.2mm
- Fiber galvo, metal marking: 0.03–0.1mm
- Diode, wood: 0.15–0.4mm

LightBurn has a built-in **kerf offset** setting to compensate at the toolpath level.

### Heat Affected Zone (HAZ)

HAZ is thermally altered material adjacent to the cut — charring on wood, microcracks in glass, discoloration on metal. Minimized by:
- Higher speed (less dwell time per unit area)
- Assist gas (carries away heat and combustion products)
- Nitrogen assist (inert, no oxidation — cleaner cut edge on acrylic and stainless)
- Pulsed operation (high peak power with low average power)
- Air assist (even simple compressed air reduces char on wood)

---

## 2. Cutting vs Engraving vs Marking

### Cutting (Vector)

Full material penetration along vector paths. Parameters: power (%), speed (mm/s or mm/min), passes, Z offset per pass. Multi-pass with Z-follow extends effective cutting depth.

### Raster Engraving

Laser scans back and forth in horizontal lines while modulating power per pixel:

- **Grayscale mode**: Power varies proportionally to pixel brightness.
- **Dithering**: Converts grayscale to binary (on/off) patterns simulating tonal variation through dot density.
  - **Floyd-Steinberg**: Error-diffusion, propagates quantization error to neighboring pixels (7/16 right, 3/16 lower-left, 5/16 below, 1/16 lower-right). Good for detailed images.
  - **Jarvis (Jarvis-Judice-Ninke)**: Distributes error across a 3×5 pixel neighborhood — smoother results, better for faces and gradients.
  - **Stucki**: Similar to Jarvis but different weighting — slightly sharper.
  - **Newsprint / halftone**: Ordered dithering — less natural for photos, good for stylized looks.
- **Line interval / DPI**: 0.1mm (254 DPI) is common for wood engraving. 0.05mm (508 DPI) for fine detail on anodized aluminum.

### Vector Engraving

Laser follows vector paths at reduced power — outlines, text, fine linework. Not raster scanning. Fast for line art.

### Marking

Surface change without material removal:

- **Anodized aluminum**: Laser vaporizes dye in anodize layer, revealing bright aluminum beneath.
- **Stainless steel (chemical)**: Cermark or Thermark spray applied, laser fuses ceramic powder to metal — black, permanent, dishwasher-safe.
- **Stainless steel (MOPA fiber)**: Structural color via controlled oxide layer thickness — no consumables, JPT MOPA source required.
- **Powder coat**: Laser ablates powder coat to reveal bare metal beneath.

### 3D Engraving

Variable power mapped to grayscale depth image — creates relief sculptures in wood or foam. Some controllers support Z-axis follow during a single pass.

---

## 3. Optical & Mechanical Systems

### Beam Delivery Architectures

| Architecture | Description | Machines |
|---|---|---|
| Flying optics | Gantry moves mirrors, bed is fixed | Most CO2 desktop/mid-range |
| Moving head | Entire laser module moves | xTool D1 Pro, Sculpfun, Ortur |
| Galvo scanning | Fixed source, mirrors deflect beam at high speed | Fiber galvo markers, xTool F1 |

**Flying optics** uses three mirrors: Mirror 1 fixed to frame, Mirror 2 on X-carriage, Mirror 3 at focus head. Mirror materials: Silicon (Si) with gold coating (highest reflectivity at 10,600nm), Molybdenum (Mo) — both must stay clean and aligned.

### Focus Optics

- **ZnSe lens**: Standard for CO2 — transmits 10,600nm, anti-reflection coated. Available in 1.5", 2.0", 2.5", 4" focal lengths. Fragile, expensive ($30–$150), requires careful cleaning.
- **F-theta lens**: Used with galvo systems — ensures constant focal plane across the scan field.
- **Meniscus vs plano-convex**: Meniscus produces smaller spot with less spherical aberration — preferred for high-quality engraving.

### Assist Gas Systems

- **Air assist**: Shop compressor or aquarium pump, 5–30 PSI, delivered coaxially through focus head nozzle. Prevents char, blows sparks, extends lens life, reduces fire risk. Mandatory for serious cutting.
- **Nitrogen (N2)**: Inert, no oxidation — bright, oxide-free edges on stainless steel and acrylic. Requires high pressure (150–400 PSI for metal cutting).
- **Oxygen (O2)**: Exothermic reaction with steel — accelerates cutting speed. Produces oxide layer on cut edge. Standard for mild steel fiber laser cutting.
- **Compressed air**: Adequate for most non-metal cutting. Moisture trap/dryer required.

### Motion Systems

**Gantry architectures for laser:**

| Type | Belt Routing | Torque | Vibration | Complexity |
|---|---|---|---|---|
| Standard Cartesian | Separate X and Y motors | Good | Moderate | Low |
| H-Bot | Single belt, both motors | Racking tendency | Higher (shear force) | Medium |
| CoreXY | Two crossed belts, both motors | Balanced force | Lower | Higher (belt tension critical) |

For laser machines, **CoreXY** is preferred in high-performance machines — both stepper motors are fixed to frame, minimizing moving mass.

**Stepper vs servo:** Belt-driven steppers at 400–800mm/s adequate for most laser work. Closed-loop servos (Trotec, Epilog) allow 3,000–5,000mm/s with position verification.

### Rotary Attachments

- **Chuck rotary**: Grips cylindrical objects with 3-jaw chuck. Accurate center registration. Best for wine glasses, pens, tumblers.
- **Roller rotary**: Object rests on driven rollers. Accommodates irregular diameters.

Both replace the Y-axis motion — connected to Y-axis stepper output. LightBurn and RDWorks support rotary mode with object diameter and steps/rotation calibration.

### Work Surface Types

| Surface | Best for |
|---|---|
| Honeycomb aluminum | Most flat materials — allows smoke below, minimal back-reflection |
| Knife bed (blade supports) | Sheet metal, materials prone to warping |
| Pin bed | Irregular or small parts |
| Pass-through slot | Materials longer than bed (Glowforge, xTool P2 conveyor option) |

---

## 4. Electronics, Controllers & Firmware

### CO2 Laser Power Supply (LPS)

The LPS converts mains AC to high-voltage DC (typically 20–30kV) to excite the CO2 tube:

- **PWM input**: Controller sends 0–5V PWM signal to LPS IN pin — duty cycle maps to power percentage.
- **mA meter**: Inline current meter on LPS output — crucial for monitoring tube health. K40 machines ship without one — adding an mA meter is standard first mod.
- **Interlock circuit**: Lid switches open the interlock line, cutting power to the LPS.
- **Water protect**: Flow sensor wired to WP pin on LPS — LPS disables if coolant flow stops.

Typical tube current ranges: 40W tube, max 18–20mA; 80W tube, max 25–28mA; 130W tube, max 28–32mA. Running above rated mA dramatically shortens tube life.

### Controller Boards

| Controller | Protocol | Machines | Software |
|---|---|---|---|
| Ruida RDC6442G | Proprietary binary (UDP/Ethernet, USB) | OMTech, most Chinese CO2, Thunder Laser | RDWorks, LightBurn |
| Ruida RDC6445G | As above, enhanced | Mid-range CO2 | RDWorks, LightBurn |
| Trocen AWC708C | Proprietary | Some Chinese CO2 | LaserWorks, LightBurn |
| GRBL (ATmega328P, ESP32) | G-code (serial/USB) | Sculpfun, Ortur, Atomstack, K40 conversions | LightBurn, LaserGRBL |
| Cohesion3D (Smoothieware) | G-code + Smoothie config | K40 replacement board | LightBurn |
| xTool proprietary | Vendor protocol | xTool D1 Pro, S1, P2 | xTool Creative Space, LightBurn (GRBL mode on some) |
| EZCad2 / EZCad3 | JCZ/BJJCZ board protocol | Galvo fiber markers | EZCad2 (Windows only), EZCad3 |

**Ruida protocol note**: Ruida uses UDP — inherently unreliable over Wi-Fi. The LightBurn Bridge (Raspberry Pi-based relay) converts UDP to TCP for reliable wireless transmission.

**GRBL specifics**: `M3 Sxxx` sets laser power (0–1000 in GRBL 1.1), `M5` disables laser. Dynamic laser power mode (`$32=1`) enables power to scale with feed rate — critical for consistent engraving at varying speeds around curves.

### Water Cooling Systems

| Model | Capacity | Suitable for | Notes |
|---|---|---|---|
| CW-3000 | Passive radiator, no compressor | Up to 60W glass tube | Raises water temp over long sessions |
| CW-5000 | Compressor-based chiller | 60–150W | Maintains setpoint (typically 15–20°C) |
| CW-5200 | Higher capacity compressor chiller | 100–150W+ | Better thermal headroom |

Use **distilled water** only. Add algaecide to prevent biofilm. Change water every 3–6 months.

### Safety Interlocks

- **Lid switch**: Opens LPS interlock on CO2 machines; disables PWM on diode machines.
- **Flame sensor**: Optical or thermal sensor — triggers E-stop if sustained flame detected.
- **Flow sensor**: Hall effect or paddle-type in coolant line — required for glass tube CO2 protection.
- **E-stop button**: Normally closed relay in series with interlock chain.
- **Current limit pot**: Some LPS units have a physical trim pot to hard-limit maximum mA.

---

## 5. Software Ecosystem

### LightBurn

The de facto standard laser design and control software. Supports Windows, macOS, Linux (x86 and ARM).

**Key capabilities:**
- Vector and raster operations in a single UI
- Native SVG, AI, DXF, PDF, PNG, JPG import
- Node editing — full vector manipulation
- **Material Library**: Named speed/power/pass presets per material, portable across machines
- **Camera registration**: Overhead USB camera captures workspace — design overlaid on photo of actual material
- **LightBurn Bridge**: Raspberry Pi relay for reliable Wi-Fi to Ruida controllers (UDP → TCP)
- **Cut planner**: Optimizes cut order to minimize travel and reduce thermal buildup
- **Tabs**: Automatic bridge tabs in cut paths to prevent parts falling through

**Controller support**: Ruida (RDC6442G, RDC6445G, RDC6332G, RDLC-320A, R5-DSP), Trocen (AWC708C, AWC606), TopWisdom, GRBL, Smoothieware, Marlin, EZCad2/3 galvo.

**Pricing (2025)**: $60 one-time (GRBL/Marlin tier) or $80 (DSP/Ruida tier). Annual update subscription optional after first year.

### LaserGRBL

Free, Windows-only. Focused on GRBL machines and image engraving. Excellent for photo engraving workflows. Built-in dithering previews.

### RDWorks (RDCam)

Ruida's native software. Functional but dated UI. Ships free with Chinese CO2 machines. Most users migrate to LightBurn quickly.

### xTool Creative Space

Proprietary to xTool. Cloud-assisted processing. Some xTool machines expose GRBL serial and can be run with LightBurn in G-code mode.

### EZCad2 / EZCad3

Standard for galvo fiber laser markers with JCZ/BJJCZ control boards. Windows-only. No public API. Supports hatch fill, mark-on-the-fly, array marking. **No Linux/macOS support** — significant limitation for headless deployments.

### Other Tools

| Tool | Use case |
|---|---|
| K40 Whisperer | Open-source K40-specific alternative |
| Inkscape + J-Tech plugin | SVG preparation → GRBL G-code export |
| LaserWeb | Browser-based, GRBL/Smoothie, open source — declining maintenance |

---

## 6. Materials Reference

### Safe Materials

#### Wood

| Material | CO2 | Diode | Notes |
|---|---|---|---|
| Baltic birch plywood | Excellent | Good | Preferred for craft — consistent glue layers, minimal voids |
| MDF | Excellent | Good | Formaldehyde fumes — ventilation mandatory |
| Hardwood (oak, walnut, maple) | Excellent | Good | Variable density affects cut consistency |
| Balsa | Excellent | Excellent | Very low power required, fire risk |
| Pine/spruce | Good | Fair | Resin deposits on lens, variable grain |

#### Plastics

| Material | CO2 | Diode | Notes |
|---|---|---|---|
| Cast acrylic | Excellent | Poor | CO2 only. Clean cuts, flame-polished edges. Engraves frosted. |
| Extruded acrylic | Fair | Poor | Flames during cutting, stress cracks. Avoid for cutting. |
| Delrin (POM) | Good | Fair | Clean cuts, slight odor |
| PETG | Fair | Poor | Tends to melt and string |
| ABS | Poor | Poor | Produces styrene gas — avoid |
| Polycarbonate | Poor | Poor | Discolors, cracks, hazardous fumes |

#### Other

| Material | CO2 | Diode | Notes |
|---|---|---|---|
| Leather (vegetable-tanned) | Excellent | Good | Clean cuts, branded marks |
| Cotton/felt | Good | Good | Low power, fringe-free cuts |
| Paper/cardboard | Excellent | Good | Very low power, fire watch required |
| Anodized aluminum | Good (marking) | Excellent (marking) | Diode excels here |
| Slate/granite | Good (engrave only) | Good (engrave only) | Ablates surface for frosted marks |
| Glass | Good (engrave only) | Poor | CO2 required. Surface frosting. |
| Cermark-coated stainless | Good | Good | Black permanent bond after marking |

### DANGEROUS Materials — AI Control Systems Must Block These

**These must be flagged as absolute blocks in any AI control system:**

| Material | Hazard | Notes |
|---|---|---|
| **PVC (polyvinyl chloride)** | **Hydrochloric acid + chlorine gas** | Corrosive to lungs AND laser optics within minutes |
| **Vinyl** | Same as PVC | Most decorative vinyl is PVC-based |
| **Faux leather / pleather** | Chlorine gas if PVC-based | Must verify material spec before processing |
| **Chrome-tanned leather** | Chromium compounds, carcinogenic | Vegetable-tanned only |
| **Fiberglass (GFRP, PCB)** | Epoxy resin + glass fiber aerosol — silica dust | Never cut |
| **Carbon fiber (CFRP)** | Carcinogenic fiber aerosol, conductive dust | Never cut |
| **Beryllium copper** | Beryllium oxide — extremely toxic | Industrial context only |
| **Bare aluminum (CO2)** | Specular reflection — can destroy tube and optics | Anodized is OK |
| **Bare copper/brass (CO2)** | High reflectivity at CO2 wavelength | Same reflection risk |

---

## 7. Major Brands & Key Models

### Diode Laser (Desktop/Hobbyist)

| Brand / Model | Optical Power | Work Area | Controller | Software | Price (USD) |
|---|---|---|---|---|---|
| xTool D1 Pro 10W | 10W | 430×390mm | xTool proprietary / GRBL-compatible | XCS, LightBurn | ~$500 |
| xTool D1 Pro 20W | 20W | 430×390mm | Same | XCS, LightBurn | ~$700 |
| xTool D1 Pro 2 40W | 40W (stacked) | 430×390mm | Same | XCS, LightBurn | ~$1,200 |
| xTool S1 | 20W | 498×319mm | Proprietary (enclosed) | XCS | ~$1,200 |
| xTool F1 | 10W IR + 2W blue | 115×115mm galvo | Proprietary | XCS | ~$1,200 |
| xTool M1 | 10W laser + blade | 385×300mm | Proprietary | XCS | ~$800 |
| Sculpfun S30 Pro | 10W | 400×400mm | GRBL (ESP32) | LightBurn, LaserGRBL | ~$300 |
| Sculpfun S30 Pro Max | 20W | 400×400mm | GRBL (ESP32) | LightBurn, LaserGRBL | ~$450 |
| Ortur Laser Master 3 | 20W | 400×400mm | GRBL | LightBurn, LaserGRBL | ~$450 |
| Atomstack X20 Pro | 20W | 400×400mm | GRBL | LightBurn, LaserGRBL | ~$400 |
| Bambu Lab Laser Module | ~10W | A1/P1/X1 bed | Bambu proprietary | Bambu Studio | Add-on |

**xTool vs Sculpfun**: xTool targets polished UX, enclosed models, proprietary features (camera, auto-focus). Sculpfun/Ortur target GRBL-compatible open ecosystem — LightBurn compatible without workarounds, better for developer/maker integration.

### CO2 — Entry Level

| Brand / Model | Tube Power | Work Area | Controller | Notes |
|---|---|---|---|---|
| K40 (generic) | 40W nominal (~30W real) | 300×200mm | M2 Nano / various | Massive upgrade ecosystem — mA meter mod, LightBurn board swap, air assist |
| Glowforge Plus | 45W | 495×279mm | Glowforge proprietary | **All processing cloud-side.** No offline operation. No LightBurn support. |
| Glowforge Pro | 45W | 495×279mm passthrough | Glowforge proprietary | Same cloud dependency |
| xTool P2 | 55W CO2 | 600×318mm | xTool proprietary | Enclosed, camera, optional conveyor — Glowforge competitor, no cloud dependency |
| Flux Beamo | 30W CO2 | 300×210mm | Flux proprietary | FLUX Studio software, Taiwanese manufacturer |
| Flux Beambox Pro | 50W CO2 | 600×375mm | Flux proprietary | Larger bed, pass-through |

**Glowforge cloud dependency warning**: Glowforge machines cannot operate without internet connectivity. All design processing occurs on Glowforge's servers. If the company discontinues service, the machine becomes non-functional. **Critical architectural limitation for any integration work.**

### CO2 — Mid-Range / Semi-Pro

| Brand / Model | Tube Power | Work Area | Controller | Price (USD) |
|---|---|---|---|---|
| OMTech 60W | 60W | 500×300mm | Ruida RDC6442G | ~$1,000 |
| OMTech 80W | 80W | 600×400mm | Ruida RDC6442G | ~$1,300 |
| OMTech 100W | 100W | 900×600mm | Ruida RDC6445G | ~$2,200 |
| OMTech 130W | 130W | 1300×900mm | Ruida RDC6445G | ~$3,500 |
| Thunder Laser Nova 35 | 80W | 900×600mm | Ruida | ~$4,500 |
| Thunder Laser Nova 51 | 100W | 1300×900mm | Ruida | ~$6,500 |
| Boss Laser LS-2440 | 80–150W | 610×1016mm | Ruida | ~$7,000+ |
| Monport GP 60W | 60W | 500×300mm | Ruida | ~$900 |

**OMTech**: Rebranded Chinese CO2 machines sold with US-based customer support. Ruida controller ensures LightBurn compatibility.

**Thunder Laser**: Better factory QC, steel frame construction, better stock bed flatness. Ruida controller, full LightBurn compatibility.

### CO2 — Professional

| Brand / Model | Power Range | Speed | Controller/Software | Notes |
|---|---|---|---|---|
| Epilog Zing 16 | 30–50W RF | 750mm/s | Epilog driver (print driver model) | Entry professional, air-cooled RF tube |
| Epilog Fusion Edge 36 | 50–120W RF | 3,500mm/s | Epilog Job Manager | Mid-tier professional |
| Epilog Fusion Pro 48 | 80–120W RF | 3,500mm/s | Epilog Job Manager + camera | Top-tier, overhead camera |
| Trotec Speedy 300 | 30–120W RF | 3,800mm/s | Trotec Ruby | Widely used in schools, sign shops |
| Trotec Speedy 400 | 60–170W RF | 4,300mm/s | Trotec Ruby | Speedy 400 flexx: dual CO2+fiber |
| Trotec Speedy 700 | 80–400W RF | 4,300mm/s | Trotec Ruby | Large format |
| ULS VLS4.60 | 30–75W RF | — | UCP (Universal Control Panel) | Modular laser cartridge system |
| ULS ILS12.150D | 150W RF | — | UCP | Industrial, dual-source capable |

Professional machines use **metal RF tubes** — 20,000–50,000 hour lifespan vs 1,500–3,000 hours for glass tubes. Epilog and Trotec use a **printer driver model** — the laser appears as a system printer, jobs sent from CorelDraw, Illustrator, or any print-capable application.

### Fiber Laser — Desktop / Galvo

| Brand / Model | Power | Source | Work Area | Notes |
|---|---|---|---|---|
| xTool F1 | 10W IR + 2W blue diode | Fiber IR | 115×115mm | Portable, enclosed, both wavelengths |
| ComMarker B4 | 20W–60W | JPT MOPA or Raycus | 110×110mm (extendable) | Desktop fiber galvo, MOPA for color |
| Atomstack Puck | 2W fiber | Fiber | 70×70mm | Ultra-portable, very limited power |
| Monport Galvo 30W | 30W | Raycus or JPT | 110×110mm | Desktop, EZCad2 |

### Industrial

| Brand | Systems | Notes |
|---|---|---|
| Trumpf | TruLaser 3030, 5030, 8000 series | Gold standard; fiber and CO2; up to 20kW |
| Bystronic | ByStar Fiber series | Swiss; high automation options |
| Mazak Photonics | Optiplex Nexus fiber | Japanese; high speed/precision |
| Han's Laser | Smart series | Major Chinese industrial manufacturer |
| Bodor | T series fiber | Chinese, widely exported |
| Prima Power | Platino, Laser Next | Italian; high-end automation |

---

## 8. Remote Management & APIs

### LightBurn

- **LightBurn Bridge**: Raspberry Pi device creating a reliable TCP relay to Ruida controllers (UDP → TCP). Enables Wi-Fi operation.
- **No public REST API**: LightBurn does not expose an HTTP API for programmatic job submission as of early 2025.

### GRBL-Based Machines

GRBL machines (Sculpfun, Ortur, Atomstack, K40 with replacement board) communicate via **USB serial (115200 baud)**:

```python
import serial
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

# Laser-specific G-codes
# M3 Sxxx — Laser on with power 0-1000
# M5      — Laser off
# $32=1   — Enable laser mode (dynamic power scaling with speed)
# G1 X100 F1000 S500  — Move with 50% laser power
```

### Ruida Protocol

Ruida uses **proprietary binary protocol** over USB HID or UDP/Ethernet (port 50200). Partially reverse-engineered. **Not suitable for direct integration without significant reverse-engineering work.** Route through LightBurn Bridge or USB connection.

### Glowforge

- **No local API** — all communication routes through Glowforge cloud servers.
- Exposes a cloud API (`api.glowforge.com`) but not officially documented for third-party use.
- Machine cannot operate without internet. **Offline operation is not achievable.**

### EZCad2 / EZCad3 (Fiber Galvo)

- **Windows only.** No public API. No Linux/macOS support.
- Some integration via Windows COM automation or AHK scripting documented in community.
- For headless fiber galvo control: consider BJJCZ board SDK (limited availability) or open controller conversion.

### Summary API Integration Table

| Machine Type | Protocol | Ease of Integration | Notes |
|---|---|---|---|
| GRBL (any) | Serial G-code | Excellent | Best choice for AI control |
| Ruida (via LightBurn Bridge) | TCP (bridged) | Good | Route through LightBurn |
| Ruida (direct) | Binary UDP/USB | Hard | Reverse-engineered only |
| Glowforge | Cloud HTTP | Poor | Internet-dependent, no official public API |
| xTool (D1 Pro) | GRBL serial | Good | Confirm model-specific |
| Galvo fiber (EZCad) | None / Windows-only | Poor | No practical headless path |

---

## 9. Ventilation & Safety

### Fume Extraction

- **Minimum**: Inline centrifugal fan (4" or 6" inline blower, 200–400 CFM) exhausting outside via duct.
- **Activated carbon filter**: Removes VOCs and odors — required if exhausting indoors.
- **HEPA filter**: Captures fine particulate — downstream of carbon for recirculating systems.
- **Commercial filtration units**: Fumex, UAS Laser Filter, Bofa AD Oracle. Cost: $1,500–$8,000.

**Key principle**: Air flow must maintain **negative pressure** inside the enclosure — smoke moves toward the exhaust, not toward the operator.

### Fire Safety

- **Never leave the machine unattended** during a cut — the primary safety rule.
- **Air assist** is the first line of fire defense.
- **Flame sensor (recommended)**: Triggers E-stop relay if sustained flame detected.
- **CO2 fire extinguisher** within arm's reach — not water, not Halon.
- **Honeycomb bed clearance**: Debris buildup is a fire hazard — clean regularly.

### Eye Safety

| Laser type | Wavelength | Required OD | Notes |
|---|---|---|---|
| CO2 | 10,600nm | OD 5+ at 10,600nm | Acrylic viewing windows are opaque to CO2 — safe |
| Diode (blue) | 445–450nm | OD 4–6+ at 450nm | Visible but dangerous — triggers blink reflex too slowly |
| Fiber IR | 1,064nm | OD 5+ at 1,064nm | **Invisible** — NO indication of exposure. Specialized glasses required. |

**Critical**: CO2 viewing windows in cheap enclosures may be acrylic — safe for CO2 wavelength. However, **diode laser enclosures require OD4+ filtered polycarbonate or glass** — regular acrylic is partially transparent at 450nm.

### Enclosure Interlock Design for AI-Controlled Systems

Hardware-enforced interlock chain — not software-dependent:

```
Lid switch(es) → E-stop relay → LPS interlock IN pin
                              → GRBL Enable pin (inverted)
```

Software should never be the only barrier between an open lid and an active laser. Hardware normally-closed relays in series ensure no firmware bug or API call can fire the laser with an open enclosure.

---

## 10. Calibration & Maintenance

### CO2 Mirror Alignment (Flying Optics)

Three-mirror chain must be aligned to maintain beam centering through all gantry positions:

1. **Mirror 1** (fixed, near tube exit): Align tube output to hit Mirror 1 center.
2. **Mirror 2** (X-carriage): Align Mirror 1 reflection to hit Mirror 2 center at X-near and X-far.
3. **Mirror 3** (focus head): Align Mirror 2 reflection to hit Mirror 3 center at Y-near and Y-far.

**Method**: Use thermal paper or acrylic with protective film taped to mirror backs. Brief low-power pulse (5–10% for <0.5 seconds) burns a dot showing beam position. Adjust mirror set screws to center the dot. Work from tube toward workpiece.

### Focus Calibration

- **Focus gauge/ruler**: Acrylic or metal gauge with stepped thickness. Place on material, lower head until tabs touch.
- **Auto-focus**: Some machines (OMTech autofocus, xTool P2) include a probe that touches material surface.
- **Ramp test**: Engrave a line across a ramp — narrowest engraved line indicates optimal focal height.

### Power Calibration

- **mA meter reading**: Actual tube current is the ground truth. 60W machine should draw ~22–26mA at 100% power — not 30+, which burns the tube.
- **Tube aging**: Glass tubes lose power over time. When maximum current is reached at maximum software power, replacement is due.
- **Power curve mapping**: Map software % to mA readings in 10% increments. Build a correction table.

### Lens Cleaning (ZnSe)

- Clean with **isopropyl alcohol (99%)** and **lint-free cotton swabs** — never paper towels.
- Clean in a single direction — don't scrub back and forth.
- ZnSe is soft — scratches easily. Replace rather than over-clean.
- Clean after every 4–8 hours of cutting (more frequently with MDF, rubber, or resin-heavy materials).

### Water Cooling Maintenance

- Water temp setpoint: **15–20°C** for optimal tube performance.
- **Never run without flow**: Wire the WP interlock before first use.
- Replace distilled water every 3–6 months — algae growth will clog pump and tubing.
- Check coolant hose connections monthly — water near high-voltage LPS is dangerous.

### Belt and Mechanical Maintenance

- Check belt tension monthly — a loose belt causes positioning error and ringing artifacts in engraving.
- **Tension test**: Pluck the belt — should produce a consistent tone. Both belts in CoreXY must match.
- Clean V-slot wheels or linear rails with IPA.
- Re-tighten eccentric spacers on V-slot wheels when carriage develops play.

---

## 11. Industry Trends (2024–2026)

### Diode Laser Power Race

- 2021: "10W" (often 5–6W optical) dominated
- 2022–2023: True 20W optical modules became common
- 2024–2025: 40W+ optical modules via beam combining (xTool D1 Pro 2, multiple competitors)
- Theoretical ceiling for stacked diode approaching practical limits of thermal management and beam combining optics

### Galvo Systems at Desktop Prices

Galvo fiber markers that cost $3,000–$5,000 in 2020 are now $600–$1,500 (ComMarker B4, xTool F1, Monport Galvo series). The xTool F1 combines 10W fiber IR and 2W blue diode in a portable enclosed enclosure.

### MOPA Color Marking Going Mainstream

JPT MOPA sources at 20–30W now in consumer-accessible machines. Color marking of stainless steel — previously a niche industrial application — accessible to small shops and hobbyists. Parameter databases for specific colors (pulse width, frequency, hatch spacing) actively shared in communities.

### AI Image Processing for Engraving

LightBurn and xTool Creative Space include AI-driven image optimization tools for photo engraving — automatic contrast enhancement, dithering algorithm selection, tone-curve adjustment based on material type.

### Camera-Based Registration

Overhead cameras for material placement (LightBurn Camera, Glowforge's built-in camera, xTool camera on S1 and P2) becoming standard even in mid-tier machines. Enables cut-from-photo workflows.

### Cloud Dependency as Risk Factor

The Glowforge situation crystallized a key concern: **a machine that requires vendor cloud connectivity to operate is a machine that stops working when the vendor changes terms, raises prices, or shuts down**. For production or commercial deployment, this is an unacceptable single point of failure. Preference for GRBL-based or Ruida-based machines with fully local operation is well-founded from a business continuity perspective.

### Industrial Fiber Speed Escalation

Industrial fiber laser systems shipping with 20–30kW sources and cutting speeds exceeding 100m/min on thin sheet metal. Dynamic beam shaping (Trumpf BrightLine, Bystronic Dynamic Beam) adjusts beam profile in real time — round spot for cutting, ring mode for thick plate.

---

*Document compiled from manufacturer specifications, community knowledge bases (LightBurn forums, r/lasercutting, r/lasercutter), engineering literature, and vendor documentation.*
