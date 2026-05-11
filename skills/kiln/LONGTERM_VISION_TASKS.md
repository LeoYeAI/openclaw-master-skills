# Longterm Vision: Multi-Device Manufacturing

> Parked here until 3D printing is fully conquered. These are real opportunities worth pursuing once the core product is stable and generating revenue.

---

## The Thesis

Agents don't care what the machine is. "Turn this design into a physical object" is the same workflow whether it's FDM filament, UV resin, a laser on acrylic, or a CNC bit in aluminum. Kiln already has the adapter abstraction, safety profile system, and fulfillment brokering that generalizes to all of these. Expanding to new device types turns Kiln from "3D printer controller" into "the manufacturing runtime for AI agents" — a much larger market with a real moat.

The moat is the adapter ecosystem. Every new device type creates network effects: agents trained against Kiln's tools work across more machines, more users adopt Kiln, more community adapters get built, and Kiln becomes the default manufacturing abstraction layer. Nobody else is building this.

## Device Types (Priority Order)

### 1. Resin / SLA Printers

**Why first:** Smallest delta from FDM. Same "upload file, start print, monitor, finish" workflow. The adapter pattern ports almost directly.

**Target hardware:**
- Formlabs (Form 3/4) — REST API via Dashboard, fleet management built in
- Prusa SL1S — Prusa Connect support (Kiln already has Prusa Connect adapter for FDM)
- Elegoo Saturn / Anycubic Photon — ChiTuBox or community firmware with network APIs
- Phrozen — Growing market share, USB/network API

**Safety model differences from FDM:**
- UV exposure time validation (under-curing = weak parts, over-curing = brittleness)
- Resin toxicity warnings — agent should flag when ventilation or PPE is needed
- Wash and cure cycle management — post-processing is mandatory, not optional
- Vat level monitoring — resin runs out mid-print = ruined build plate
- Temperature sensitivity — resin viscosity changes with ambient temp, affects print quality
- No thermal runaway risk (no heated bed/nozzle), but UV LED lifespan tracking matters

**Monetization angle:** Resin prints are higher value per-unit (jewelry, dental, miniatures). Fulfillment brokering margins are better. Formlabs materials are expensive — material recommendation and cost optimization tools have real value.

**Estimated effort:** 2-3 weeks for a Formlabs adapter + safety profiles, assuming hardware access. Could ship Prusa SL1 support even faster since the Connect API is already integrated.

---

### 2. Laser Cutters

**Why second:** Different enough from 3D printing to prove the "multi-device" story, but control interfaces are well-documented. Opens flat-stock manufacturing: signage, enclosures, packaging, architectural models.

**Target hardware:**
- Glowforge — Cloud API (controversial, but huge user base)
- Epilog — Serial/Ethernet control, common in makerspaces and universities
- K40 (Chinese CO2 lasers) — K40 Whisperer is open-source, massive hobbyist market
- xTool — Growing consumer brand with network API
- LightBurn-compatible lasers — LightBurn CLI covers dozens of laser brands

**Safety model (significantly different from 3D printing):**
- Material safety database — some materials release toxic fumes when laser-cut (PVC = chlorine gas, polycarbonate = bisphenol A). Agent MUST refuse to cut dangerous materials.
- Ventilation interlock — agent should verify exhaust is running before starting
- Fire risk — laser + flammable material = real fire hazard. Unattended operation needs active monitoring.
- Power/speed validation — too much power = fire, too little = incomplete cut. Per-material profiles are mandatory.
- Focus distance — wrong focal length = poor cuts and wasted material
- Eye safety — no direct safety control, but agent should warn about laser classes

**Monetization angles:**
- Material sourcing — Kiln could broker material orders (acrylic sheets, plywood, leather) alongside cut jobs. Partnership with material suppliers.
- Outsourced cutting — Ponoko, SendCutSend, and OSH Cut all have APIs for outsourced laser/waterjet cutting. Same fulfillment brokering model as 3D printing.
- Design optimization — nesting algorithms to minimize material waste. Real cost savings for production runs.

**Estimated effort:** 3-4 weeks for a LightBurn CLI adapter + material safety database. The safety model is the hard part — the material toxicity database needs to be comprehensive and correct.

---

### 3. CNC Routers / Mills

**Why last:** Highest value but highest complexity. CNC parts are expensive ($50-500+ per part), so fulfillment brokering revenue is significant. But the safety model is the most demanding of any device type.

**Target hardware:**
- Grbl-based machines — Shapeoko, X-Carve, Onefinity. Grbl is open-source, serial protocol, huge hobbyist base.
- LinuxCNC — Professional-grade open-source CNC controller. Well-documented API.
- Carbide Motion (Carbide 3D) — Integrated controller for Shapeoko/Nomad. Less API access but huge market.
- Masso — Growing in prosumer CNC. Ethernet control.
- Haas (longterm) — Industrial CNC with well-documented API. The "enterprise" play.

**Safety model (most complex):**
- Feeds and speeds validation — wrong parameters = tool breakage, workpiece damage, or machine damage. Per-material, per-tool, per-machine limits are critical.
- Tool breakage detection — vibration/current monitoring if hardware supports it, or vision-based detection
- Workholding verification — loose workpiece = projectile. Agent should confirm workholding before spindle start.
- Spindle speed limits — per-material RPM ranges. Aluminum vs. wood vs. plastics are completely different.
- Depth of cut limits — too aggressive = stalled spindle or broken tool
- Coolant/chip evacuation — dry cutting aluminum = fire risk. Agent should verify coolant system is active for metals.
- Emergency stop integration — CNC failures are more dangerous than 3D print failures. E-stop must be wired into the safety system, not just software.
- Tool length offset verification — wrong tool offset = crashed spindle into workpiece/table

**Monetization angles:**
- Fulfillment brokering is the big one. CNC parts through Xometry, Protolabs, or Fictiv are $50-500+. 5% of a $200 CNC order is $10 per job vs. $0.50 on a typical FDM fulfillment order.
- Toolpath optimization — CAM is hard. If Kiln can recommend feeds/speeds or optimize toolpaths, that's real value.
- Tool wear tracking — predict when tools need replacement based on cut history. Saves money on broken tools and scrapped parts.

**Estimated effort:** 6-8 weeks for a Grbl adapter + safety profiles + feeds/speeds database. The safety model alone is probably 3 weeks. This one should not be rushed.

---

## The Compound Play

Once all four device types are supported, Kiln can do something nobody else offers: **multi-device job decomposition.** An agent that needs to build an enclosure can:

- Laser-cut the flat panels from acrylic
- CNC the aluminum mounting brackets
- FDM the internal cable guides and spacers
- SLA the light pipes and cosmetic parts

All routed to the right machines, with material-appropriate safety checks, sliced/CAM'd correctly, and tracked through a single job queue. That's a manufacturing workflow that currently requires a human project manager coordinating across multiple tools and services.

## Testing Strategy

Hardware access is the main blocker. Realistic paths:

### USC Baum Family Maker Space (BFMS) — Primary Target

BFMS covers **every device category** in this roadmap with exact target hardware. Full equipment inventory verified Feb 2025:

**FDM Printers (immediate Kiln testing):**
| Device | Count | Kiln Value |
|--------|-------|------------|
| Prusa MK4 | 6 | Fleet/queue testing — 6 identical printers for multi-printer scheduling, Prusa Connect adapter validation |
| Prusa Pro HT90 | 1 | High-temp material profiles (ABS, ASA, PCCF, PA), delta kinematic edge cases |
| Markforged X7 | 1 | Continuous fiber reinforcement (Onyx, carbon fiber, Kevlar) — exotic material safety profiles |
| Stratasys F900 | 1 | Industrial FDM (36"x24"x36" build volume) — tests slicing pipeline at extreme scale |
| Stratasys F370 | 1 | Mid-size industrial FDM — ABS/PC/Nylon materials |

**SLA/Resin (longterm priority #1):**
| Device | Kiln Value |
|--------|------------|
| FormLabs Form 3L | Named target hardware — large-format SLA, REST API via Dashboard, resin safety profile development |

**Laser Cutters (longterm priority #2):**
| Device | Location | Kiln Value |
|--------|----------|------------|
| Universal Laser Systems VLS6.75 | BFMS Advanced Fab Lab | CO2 laser, 18"x32" cut area — material safety database testing, power/speed profile development |
| Full Spectrum H-Series 20x12 | BME Innovation Space (DRB B18) | Second laser brand — cross-vendor adapter validation, 45W |

**CNC / Subtractive (longterm priority #3):**
| Device | Kiln Value |
|--------|------------|
| Haas VF-2SS milling center | Named target hardware ("the enterprise play") — industrial CNC with documented API, feeds/speeds validation |
| OMAX 5555 waterjet | Not in current plan but extends multi-device decomposition — cuts metal/stone that CNC and laser can't |
| 3x Bridgeport mills + 3x lathes | Manual machines, less automatable, but useful for understanding CNC workflows and safety models |

**Support Equipment:**
| Device | Kiln Value |
|--------|------------|
| Omegasonics OMG-4030 ultrasonic cleaner | Post-processing pipeline for SLA — wash/cure cycle management testing |

**Why BFMS is the single best testing partner:** One location, one relationship, covers all four device categories with the exact brands named in this roadmap. The six Prusa MK4s alone are a fleet-testing goldmine. No other single facility maps this cleanly to the Kiln hardware roadmap.

### USC BME Innovation Space (DRB B14)

Secondary facility, useful for cross-validation:
- **Ultimaker S5** (dual extruder) + **Ultimaker 2+** — different firmware ecosystem from Prusa/Stratasys, dual-extruder testing
- **Full Spectrum H-Series laser** (DRB B18) — second laser brand for adapter portability testing

### USC Smaller Labs (Niche Value)

- **SMRL** — Formlabs Form 1, MakerBot Replicator 2X, Longer Orange 10 (DLP). Older gear but useful for testing adapter backward-compatibility with legacy hardware and budget DLP printers.
- **Keck 3D Printing Lab** (medical school) — biomedical printing. Niche, but if Kiln ever targets dental/medical verticals, this is the access point.

### USC Iovine and Young Academy
More product/design focused, but has similar equipment and students who'd appreciate shipping real software.

### Other LA Universities
- **UCLA, CalTech, ArtCenter** — all have fabrication labs with equipment access for collaborative projects. Secondary targets if USC partnership doesn't materialize.

### Makerspaces
- **Maker City LA, Crashspace (Culver City), CRASH Space** — Monthly memberships ($50-150/mo). A month or two during active development gets hands-on testing time. Cheaper than buying hardware.

### Remote / API-First Testing
- For SLA and CNC, the **fulfillment adapter path** (Craftcloud, Sculpteo, Xometry) can be developed and tested purely via API — no hardware needed. Only the local machine control adapter needs physical access.
- **Simulation-first development** — Build adapters against mock backends (like the existing test suite does for OctoPrint/Moonraker). The adapter interface, safety profiles, and MCP tools can all be developed and tested without hardware. ~80% of the work can happen before touching a real machine.

### Manufacturer Dev Programs
- **Formlabs** — Has developer relations. Pitch Kiln as open-source fleet management integration. Possible loaner hardware.
- **Carbide 3D** — Small company, responsive to community. Shapeoko/Nomad are popular in the maker space.
- **xTool** — Actively building developer ecosystem for their laser cutters.

### Sequencing
1. Build adapters against simulated backends (no hardware needed)
2. Test fulfillment/brokering path via existing APIs (no hardware needed)
3. Get hardware access for final integration testing (university, makerspace, or loaner)
4. Ship adapter as "beta" with community testing before marking stable

### USC-Specific Testing Phases

**Phase 0 — Now (FDM, no new adapters needed):**
- Test Prusa Connect adapter against the 6x Prusa MK4 fleet at BFMS
- Validate fleet scheduling, queue management, and multi-printer job distribution
- Test high-temp safety profiles on Prusa Pro HT90 (ABS, ASA, PA, PCCF)
- Test exotic material safety on Markforged X7 (carbon fiber, Kevlar reinforcement)
- Stress-test slicing pipeline with large-format Stratasys F900 builds

**Phase 1 — SLA (first new device type):**
- Build Formlabs adapter against simulated backend
- Integration test on BFMS Form 3L — the exact hardware listed as target
- Develop resin safety profiles (UV exposure, toxicity warnings, wash/cure cycles)
- Test post-processing pipeline using the Omegasonics ultrasonic cleaner

**Phase 2 — Laser Cutters (second device type):**
- Build LightBurn CLI or ULS-native adapter against simulated backend
- Integration test on BFMS VLS6.75 (CO2 laser)
- Cross-validate on BME Full Spectrum H-Series (different brand, same adapter interface)
- Build and validate material toxicity database — this is the hard part and needs real-world testing

**Phase 3 — CNC (third device type):**
- Build Haas adapter against simulated backend (Haas API is well-documented)
- Integration test on BFMS Haas VF-2SS — the exact machine called out as "enterprise play"
- Develop feeds/speeds database with real cutting tests
- Explore OMAX 5555 waterjet as bonus device type for multi-device decomposition demo

---

## When to Start

**Not yet.** Prerequisites before expanding to new device types:

- [ ] Kiln 3D printing is stable with paying Pro/Business users
- [ ] Safety system is battle-tested (no incidents, guardrails proven in production)
- [ ] Adapter pattern is validated across all four 3D printer backends (OctoPrint, Moonraker, Bambu, Prusa Connect)
- [ ] Community is active enough to contribute adapters and test on diverse hardware
- [ ] Revenue from 3D printing fulfillment brokering validates the business model

Once those boxes are checked, SLA is the natural next step — smallest risk, closest to existing code, highest overlap with current users.
