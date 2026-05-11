# Email Draft: Professor Jeremy Dann — USC x Kiln Partnership

**Status:** Ready to send (updated 2026-02-21)
**Date:** February 21, 2026
**To:** Professor Jeremy Dann

---

**Subject: Open-Source AI Manufacturing Project — Student Collaboration at USC**

Professor Dann,

Hope you're doing well. I wanted to reach out about something that connects back to the fabrication lab you brought us to.

I launched an open-source project called **Kiln** — it's infrastructure that lets AI agents (Claude, GPT, etc.) control physical manufacturing equipment. It's live at kiln3d.com and on GitHub. Right now it handles 3D printers (OctoPrint, Klipper, Bambu Lab, Prusa Connect), but the architecture is designed to generalize to any fabrication device: resin printers, laser cutters, and CNC routers.

I was just at ETH Denver and got a chance to demo Kiln to the person running the maker lab they had set up at the conference. He told me it was the coolest thing anyone had shown him in a long time — which felt like a good sign that the direction is right.

The next phase is building adapters for those new device types, and USC's labs have exactly the hardware I need — SLA printers, laser cutters, industrial FDM printers, mills, and CNC equipment across the Baum Family Maker Space, the machine shop, and the Architecture school's digital fabrication lab.

**What I'm exploring:**

I'd love to connect with the right people at USC to set up a student contributor program around Kiln. This isn't just beta testing — students would be building real infrastructure:

- **Resin/SLA adapter** — Build support for SLA printers in the Maker Space, including UV curing safety profiles and resin toxicity handling. Estimated 2-3 week core build, but a full semester allows proper safety validation.

- **Laser cutter adapter** — Build support for the CO2 laser, including a material safety database (some materials release toxic fumes when cut — real safety engineering). This is publishable-quality work.

- **CNC adapter** — The most ambitious: feeds/speeds validation, tool breakage detection, workholding verification. A serious engineering project for advanced students.

- **Fleet testing** — Validate Kiln's multi-printer scheduling across the lab's FDM printers. Build adapters for printer brands Kiln doesn't support yet.

The long-term vision is **multi-device job decomposition** — an agent that can take a product design and automatically route the acrylic panels to the laser cutter, the aluminum brackets to the CNC, the internal parts to FDM, and the cosmetic pieces to SLA. All with per-device safety checks, managed through a single job queue. That's a demo that would be impressive at any showcase or competition.

**What students get:**
- Real open-source contributions on a published MIT-licensed project (PyPI, active GitHub)
- Hands-on experience with AI agent protocols (MCP), hardware-software integration, and safety-critical systems
- Cross-disciplinary work: CS students on adapters and tools, ME students on safety profiles and testing, business students on the marketplace/fulfillment model
- Their names on the contributor list and changelog — meaningful resume differentiation

I think this could work as directed research credit (CSCI 490 or equivalent), a USC Makers project, an Iovine and Young collaboration, or even a Greif Center case study on open-source AI infrastructure.

You're the person I trust most to tell me who the right doors are. Would you be open to a quick conversation about how to explore this?

Project: **github.com/codeofaxel/Kiln**

Best,
Adam
