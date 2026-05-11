# USC Partnership Brief

> Reference doc for outreach to USC Viterbi faculty/staff via Jeremy Dann intro. Two sections: the warm intro ask (for Jeremy), and the technical proposal (for whoever Jeremy connects us with — likely BFMS staff, a faculty advisor, or a capstone coordinator).

---

## Part 1: The Ask to Jeremy Dann

**Goal:** Get an intro to the right person at BFMS (Baum Family Maker Space) or Viterbi engineering faculty who can approve equipment access or frame this as a student project.

**Key points to hit:**
- Building Kiln — open-source software that lets AI agents control manufacturing equipment (3D printers, laser cutters, CNC mills)
- Already works with 4 printer backends (OctoPrint, Moonraker, Bambu Lab, Prusa Connect), 50+ MCP tools, 2,700+ tests
- Need hardware access to validate new device adapters — BFMS has the exact equipment we're targeting
- Not asking for money or sponsorship — just access to machines for integration testing
- Happy to structure as capstone project, independent study, or open-source collaboration if that makes it easier to approve
- USC students who contribute get real open-source credit on a shipped product, not a toy project

**Who we need to meet:**
- BFMS lab manager or operations lead (controls equipment access/scheduling)
- Alternatively: faculty member who supervises capstone projects or independent studies in ME, EE, or CS and could frame this as a student project with equipment access as a natural part of the work

**What we do NOT need Jeremy to do:**
- Understand the technical details — just make the intro
- Vouch for the project's viability — we'll pitch that ourselves
- Commit USC to anything — we're asking for a conversation

---

## Part 2: Technical Proposal (For BFMS Staff / Faculty)

### What Kiln Is

Kiln is an open-source AI manufacturing runtime — software that lets AI agents control physical manufacturing equipment through a standardized interface. Think of it as "the operating system layer between AI and factory floors."

Currently supports FDM 3D printers via four adapter backends. The architecture generalizes to any digitally-controlled manufacturing device: SLA/resin printers, laser cutters, CNC mills.

**GitHub:** [link to repo]
**Docs:** [link to docs site]

### What We're Building Next

Expanding from FDM-only to multi-device manufacturing control. Three new device categories, in order:

1. **SLA/Resin Printers** — adapter for Formlabs (Form 3L)
2. **Laser Cutters** — adapter for CO2 lasers (ULS, Full Spectrum)
3. **CNC Mills** — adapter for Haas (VF-2SS)

Each requires: a machine control adapter, safety profiles (material-specific limits, hazard checks), and integration testing on real hardware.

### What BFMS Has That We Need

| BFMS Equipment | What We'd Test |
|----------------|----------------|
| 6x Prusa MK4 | Fleet scheduling — distribute jobs across identical printers, validate queue/priority system |
| Prusa Pro HT90 | High-temp material safety profiles (ABS, ASA, PA, PCCF) |
| Markforged X7 | Exotic material safety (continuous carbon fiber, Kevlar reinforcement) |
| FormLabs Form 3L | SLA adapter development — upload, print, monitor, post-process workflow |
| ULS VLS6.75 laser | Laser adapter development — material safety database, power/speed profiles |
| Haas VF-2SS mill | CNC adapter development — feeds/speeds validation, tool safety checks |
| Omegasonics ultrasonic cleaner | SLA post-processing pipeline (wash cycle management) |

We'd also love to cross-validate laser adapters on the BME Full Spectrum H-Series (DRB B18) if access extends that far.

### What We're Asking For

**Minimum viable ask:**
- Scheduled access to BFMS Advanced Fab Lab equipment for integration testing sessions
- Estimate: 4-6 sessions over 2-3 months per device type, 2-4 hours each
- We bring our own laptops and software — just need the machines powered on and available
- Happy to work around student schedules and existing reservations

**Stretch ask (if there's appetite):**
- Frame as a capstone project or independent study
- 2-4 students build adapters as their project, with our mentorship on the software side
- Students get: real open-source contribution credit, experience with MCP protocol / AI agent tooling, a shipped product on their resume
- USC gets: open-source manufacturing infrastructure that other universities can use, potential conference paper on AI-controlled multi-device manufacturing

### What We Bring

- A working, tested codebase — not a pitch deck. 2,700+ tests, 50+ MCP tools, 4 production adapters.
- Deep knowledge of the adapter pattern — we'll mentor students on how to build adapters that are safe, testable, and production-grade.
- All work is open-source (MIT license) — USC can use, modify, and extend Kiln for any purpose.
- Safety-first design philosophy — every adapter has per-material safety profiles, preflight checks, and emergency stop integration. We take "don't break the $50k Haas mill" seriously.

### What We Do NOT Need

- Funding or sponsorship
- Exclusive access — happy to share time slots
- Unsupervised access — we expect and welcome lab supervision, especially on CNC and laser equipment
- Admin/root access to any USC systems

### Timeline

| Phase | Equipment | When | Duration |
|-------|-----------|------|----------|
| 0 (now) | Prusa MK4 fleet, Pro HT90, Markforged X7 | Whenever convenient | 2-3 sessions, 2hrs each |
| 1 | FormLabs Form 3L + ultrasonic cleaner | After SLA adapter is built (mock-tested) | 4-6 sessions over 6-8 weeks |
| 2 | ULS VLS6.75 laser + BME Full Spectrum | After laser adapter is built (mock-tested) | 4-6 sessions over 6-8 weeks |
| 3 | Haas VF-2SS | After CNC adapter is built (mock-tested) | 4-6 sessions over 8-10 weeks |

Phase 0 can start immediately — we already have working Prusa Connect adapters and just need to validate against real fleet hardware.

### Contact

Adam Arreola — [email / phone]

---

## Notes for Adam

- Jeremy's intro gets us in the door. The technical proposal is what we send (or present) to whoever Jeremy connects us with.
- Lead with Phase 0 (Prusa MK4 fleet testing) — it's the smallest ask, requires no new equipment training, and demonstrates value before we ask for laser/CNC time.
- If they're interested in the capstone angle, that's the biggest win — students do the adapter work, we mentor, USC gets a real project, and we get hardware access baked into the academic calendar.
- The Haas VF-2SS is the crown jewel. Don't lead with it — earn trust on the FDM and SLA phases first. CNC access will have the most gatekeeping because the machine is expensive and dangerous.
- The OMAX waterjet is a bonus — don't mention it in the initial ask. If CNC goes well, bring it up as a natural extension.
