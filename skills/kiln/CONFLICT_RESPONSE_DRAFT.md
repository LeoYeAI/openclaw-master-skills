# Response to 3DOS Conflict Allegations — Factual Record

**Prepared by:** Adam Arreola
**Date:** February 25, 2026
**Status:** DRAFT — Attorney review required before distribution
**Audience:** Roger Lim (NGC), legal counsel, personal advisors
**Classification:** CONFIDENTIAL — Do not distribute beyond intended recipients

---

## Executive Summary

John Dogru's conflict review request to NGC characterizes Kiln as a copy of 3DOS/3DPrinterOS. This document presents the factual record — supported by timestamped code commits, public documentation, and codebase architecture — demonstrating that:

1. **Kiln and 3DOS are fundamentally different products.** Kiln is a local-first CLI tool and MCP server that runs on a user's own machine and talks to their own printers over LAN. 3DOS is a cloud-hosted decentralized manufacturing marketplace/network. They share a vertical (3D printing) but not an architecture, business model, user type, or product category.

2. **Adam proactively sought collaboration with 3DOS, not competition.** Before Kiln launched, Adam messaged John (February 12, 2026) proposing a partnership and requesting API access to integrate 3DOS as a provider within Kiln. Adam built a full 3DOS gateway client into Kiln — 6 MCP tools, 6 CLI commands, 46 tests — designed to route business *to* the 3DOS network.

3. **No confidential 3DOS information was used to build Kiln.** The AI tools used to build Kiln were explicitly and repeatedly instructed not to compete with 3DOS. The codebase contains no 3DOS proprietary code, no references to 3DOS internal documentation, and no features derived from non-public information.

4. **The "overlapping features" cited in John's comparison are industry-standard capabilities** present in OctoPrint (est. 2012), Repetier-Server, AstroPrint, 3DPrinterOS itself, and numerous other tools that predate both Kiln and 3DOS's current product.

---

## Section 1: What Kiln Actually Is (Architecture)

### Local-First, Single-Tenant Software

Kiln is a Python package that installs on a user's own computer via `pip install kiln-server`. It runs as a local process. All data is stored in SQLite at `~/.kiln/kiln.db` on the user's local filesystem. There is no cloud component, no shared database, no multi-user coordination, and no distributed system.

**How Kiln connects to printers:**
- OctoPrint adapter: HTTP requests to `http://octopi.local` (user's LAN)
- Moonraker/Klipper adapter: HTTP requests to local IP
- Bambu Lab adapter: MQTT over local network
- Prusa Connect adapter: REST API
- Serial adapter: USB cable (`/dev/ttyUSB0`, `COM3`)

Every printer connection is a direct, local network connection between the user's machine and their own printer. Kiln does not broker connections between different users' printers.

**How Kiln stores state:**
- Job queue: local SQLite (`~/.kiln/queue.db`)
- Print history: local SQLite (`~/.kiln/kiln.db`)
- Configuration: local YAML (`~/.kiln/config.yaml`)
- Fleet registry: in-memory Python dictionary with a threading lock

There is no server infrastructure that Kiln operates where multiple users' data commingles.

### What 3DOS Is (For Comparison)

3DOS, per its own public documentation (https://3dos.gitbook.io/why-3dos-matters), is "a global, decentralized manufacturing network for everyone." It is a cloud-hosted platform where printer owners worldwide enroll their printers, and designers/buyers submit orders that are routed across the network to available printers. It includes blockchain/token components and operates as a multi-sided marketplace.

### Side-by-Side Architectural Comparison

| Dimension | Kiln | 3DOS |
|---|---|---|
| **Product category** | Local CLI tool / MCP server | Cloud manufacturing marketplace/network |
| **Runs where** | User's own laptop/server | Cloud-hosted platform |
| **Printer connections** | Direct LAN (HTTP/MQTT to user's own printers) | Global network of enrolled printers worldwide |
| **Job routing** | User's local queue → user's local printers | Platform routes across unrelated printer owners |
| **Multi-tenancy** | Single user, single installation | Multi-sided: designers + print service providers |
| **Data storage** | SQLite on user's local disk | Cloud database |
| **Manufacturing network** | Does not operate one | IS the network |
| **Blockchain/tokens** | None | Part of 3DOS architecture |
| **Peer-to-peer** | None | Core architectural concept |
| **Primary user** | AI agents (via MCP protocol) | Human designers and printer operators |
| **Revenue model** | Open-source; optional paid tiers for fleet features | Marketplace transaction fees |

**The fundamental difference:** Kiln is analogous to a local print spooler that an AI agent can talk to. 3DOS is analogous to Uber for 3D printing. These are not the same product category.

---

## Section 2: Timeline of Events and Intent

### February 11-12, 2026 — 3DOS Integration Built, Collaboration Sought

**Git commit `9de1fd5` (Feb 11):** "Wire 3DOS gateway into MCP tools + CLI with 46 tests"

Adam built a full integration client for the 3DOS API into Kiln. This integration was designed to:
- Allow Kiln users to register their local printers on the 3DOS network (sending business TO 3DOS)
- Allow Kiln users to find printers on the 3DOS network (consuming 3DOS's service)
- Allow Kiln users to submit jobs to the 3DOS network (generating revenue FOR 3DOS)

The integration client (`kiln/src/kiln/gateway/threedos.py`) is a standard REST API wrapper that calls `https://api.3dos.io/v1`. It does not replicate, reverse-engineer, or replace any 3DOS functionality. It is functionally equivalent to any third-party developer using the 3DOS API.

**February 12, 2026 — Message to John Dogru:**

Adam messaged John directly, introducing Kiln and proposing collaboration:

> "I built a 3DOS gateway into it too that I can push at launch. Agents can register printers on the network, find remote printers by material/location, and submit jobs. 6 MCP tools, CLI commands, 46 tests, all wired up. I just need 3DOS API keys to light it up."
>
> "The vision: an agent says 'print this' and Kiln prints it locally on the user's printer(s) or auto-routes it to the best available printer on 3DOS or other fulfillment services."

This message, timestamped before Kiln's public launch, demonstrates:
1. Adam wanted 3DOS integrated as a key partner, not as a competitor
2. Adam needed 3DOS's API keys — he was building a client for their service, not a replacement
3. Adam proposed revenue sharing — he intended to drive paying traffic to 3DOS's network

John did not respond to this message. It was left on read until February 24, 2026 — 12 days later.

### February 17, 2026 — Preemptive De-Branding

Because John had not responded and the partnership was unconfirmed, Adam proactively removed 3DOS branding from all public-facing documentation.

**Git commit `21f655d` (Feb 17):** "Clean up 3DOS references in docs"

The internal task tracker (`.dev/TASKS.md`) explicitly documents the reasoning:

> "All public-facing references to '3DOS' have been replaced with generic 'distributed network (coming soon)' phrasing across README, LITEPAPER, WHITEPAPER, PROJECT_DOCS, THREAT_MODEL, DEPLOYMENT, blog post, and FAQ. Do not restore 3DOS branding until we have the API key and have confirmed the partnership with the 3DOS founder."

Adam replaced specific 3DOS branding with generic placeholders *because he did not want to publicly claim a partnership that wasn't confirmed.* The "coming soon" language was a placeholder pending John's response — not a declaration of intent to build a competing network.

### February 23-24, 2026 — Boundary Clarification

After the hostile phone call with John, Adam immediately took steps to clarify Kiln's positioning:

**Git commit `018046e` (Feb 23):** "docs: clarify product boundary (orchestration layer, not first-party network)"

**Git commit `2121b6a` (Feb 23):** "clarify provider boundary and deprecate network_* naming"

These commits:
- Added a dedicated `/boundary` page to the website explicitly stating: "Kiln does not operate a first-party decentralized manufacturing marketplace/network"
- Added clarification banners to the top of the Whitepaper, Litepaper, and Project Docs
- Deprecated all `network_*` MCP tool names in favor of `provider_*` names (e.g., `network_register_printer` → `connect_provider_account`)
- Updated the FAQ with an explicit question: "How is Kiln different from decentralized manufacturing networks?"
- Updated the blog launch post with a clarification notice

These changes were not an admission of wrongdoing. They were a good-faith effort to remove any possible ambiguity in Kiln's public messaging after learning that John perceived the project as competitive.

---

## Section 3: Addressing John's Specific Accusations

### Accusation 1: "You literally are copying most all aspects of 3DOS"

**Response:** The feature comparison in John's document to Roger compares at the category label level, not at the product level. By John's logic, every email client is a copy of Gmail because they both have "inbox management," "search," and "compose." The features John cites — fleet management, slicing, monitoring, marketplace search, outsourced manufacturing — are industry-standard capabilities present in software that predates both Kiln and 3DOS:

| Feature | Pre-existing in... |
|---|---|
| Fleet/farm management | OctoPrint (2012), Repetier-Server, AstroPrint, 3DPrinterOS (John's own older product) |
| Slicing integration | PrusaSlicer, OrcaSlicer, Cura — all open-source, all predate 3DOS |
| Print monitoring | OctoPrint's webcam plugin (2013), OctoEverywhere, Obico |
| Marketplace/model search | Thingiverse API (public), MyMiniFactory API (public), Thangs API (public) |
| Outsourced manufacturing | Craftcloud by All3DP, Xometry, Hubs (Protolabs), Shapeways — all with public APIs |

Kiln's novel contribution is the **MCP protocol integration** — making these capabilities accessible to AI agents. That is Kiln's core innovation and it has no analog in 3DOS or 3DPrinterOS.

### Accusation 2: "For sure you asked AI to copy our sites"

**Response:** This is false. The AI tools used to build Kiln were explicitly and repeatedly instructed not to compete with 3DOS. The project's own internal instructions (CLAUDE.md, conversation history) contain directives to avoid competing with 3DOS. At no point was any AI tool instructed to visit, scrape, analyze, or copy 3DOS or 3DPrinterOS websites or materials.

The codebase contains zero references to 3DPrinterOS. The only references to 3DOS are in the integration client that was built to *partner with* 3DOS, not replace it.

### Accusation 3: "You're saying you have this idea to include CNC Water Jet — that's literally off all our confidential materials"

**Response:** Adam does not know what a "CNC water jet" is. Expanding manufacturing automation software beyond FDM 3D printing to include CNC, laser cutting, and other fabrication methods is an obvious product direction that multiple public companies have executed for years:

- **Xometry** (XMTR, public company): CNC, 3D printing, sheet metal, injection molding
- **Hubs (Protolabs)**: CNC, 3D printing, sheet metal, injection molding
- **SendCutSend**: Laser, waterjet, CNC, bending — public pricing on their website
- **Shapeways**: 3D printing expanding to CNC

The concept of "multi-method manufacturing" is not proprietary to 3DOS and is publicly practiced by companies worth billions of dollars. On the phone call, Adam mentioned a general vision of Kiln potentially supporting other device types beyond FDM printers in the future — this is a natural product evolution, not derived from any 3DOS confidential material.

### Accusation 4: "You're claiming you are not building a peer to peer manufacturing network... then you are literally writing that from your Twitter"

**Response:** Adam has not built a peer-to-peer manufacturing network. Kiln's architecture (documented above) is a local-first tool with no peer-to-peer component. If any Twitter language was imprecise, it was an error in casual social media communication, not a reflection of the actual product architecture. Adam's Twitter post did not describe a functioning peer-to-peer network because no such network exists in Kiln.

The "coming soon" language about distributed network support referred to the planned 3DOS integration (which Adam was actively trying to partner on) and Craftcloud integration (a public third-party service) — not to Kiln building or operating its own network.

---

## Section 4: Confidential Information

### What Adam Had Access To

As a member of NGC's investment team, Adam participated in routine portfolio monitoring of 3DOS. This included periodic financial updates, fundraising status, and product roadmap discussions — standard for any portfolio company relationship.

### What Adam Did NOT Do

- Did not use 3DOS financial information in building Kiln (Kiln has no financial model derived from 3DOS metrics)
- Did not use 3DOS technical architecture in building Kiln (Kiln's architecture is fundamentally different — local-first vs. distributed cloud)
- Did not use 3DOS proprietary code (Kiln is built from scratch in Python; 3DOS is a separate technology stack)
- Did not instruct any AI tool to reference, analyze, or copy 3DOS or 3DPrinterOS materials
- Did not share 3DOS confidential information with any third party

### What the Codebase Proves

The 3DOS integration in Kiln's codebase (`gateway/threedos.py`) is a standard REST API client that calls 3DOS's public API endpoint (`https://api.3dos.io/v1`). It uses standard HTTP methods (GET, POST) with bearer token authentication. This is the same integration pattern any third-party developer would use. No proprietary 3DOS infrastructure knowledge was required or used.

---

## Section 5: Chris (NGC) Involvement

John apparently speculated that Chris's departure from NGC was related to Kiln. For the record:

- Chris ran a few tests of Kiln on his personal 3D printer. This was informal testing of an open-source tool, equivalent to any developer trying a GitHub project.
- Chris did not contribute code to Kiln.
- Chris's departure from NGC is unrelated to Kiln.
- Chris has no role, equity, or involvement in Hadron Labs Inc. or Kiln.

---

## Section 6: Remaining Public Messaging Issues

An audit of Kiln's current public-facing content (conducted February 25, 2026) identified several items where language could still be misinterpreted. These should be cleaned up regardless of the dispute outcome:

### Items Requiring Immediate Attention

1. **Legacy `network_*` MCP tool names still in README** (lines 588-593) — These are deprecated aliases but their presence in documentation ("network_register_printer," "network_find_printers") implies Kiln operates a network. These should be removed from public docs even if the code aliases remain for backward compatibility.

2. **README line 699:** "Fee tracking for fulfillment and network-routed jobs" — should say "provider-routed jobs"

3. **README line 88:** Mermaid diagram node labeled "Third-Party Network Providers" — should say "Third-Party Providers"

4. **Whitepaper line 301:** "enabling job routing across independent printer operators" — should be reworded to clarify this is via third-party provider APIs, not Kiln's own routing

5. **Blog post `introducing-kiln.astro` line 174:** "Partner-network integrations" in What's Next section — should say "Third-party provider integrations"

6. **Blog post `think-print-earn.astro` line 39:** Section heading "The intelligence network" — could be misread; consider rewording

7. **Whitepaper line 323:** "Federated learning across Kiln instances" — Future work item that implies cross-instance networking; consider removing or clarifying

8. **Twitter** — Has not been audited or cleaned up. Must be reviewed manually for any language that implies Kiln operates a network. The tweet John referenced (https://x.com/adamaarreola/status/2024203275885764893) should be reviewed specifically.

9. **Active 3DOS code in codebase** — `gateway/threedos.py`, `plugins/network_tools.py`, and `tests/test_threedos_gateway.py` still contain full 3DOS integration code including docstrings like "3DOS distributed manufacturing gateway client" and "dispute resolution in the 3DOS network" (`quality.py`). While this code supports Adam's narrative of wanting to partner (not compete), its continued presence should be discussed with counsel.

---

## Appendix A: Key Git Commits (Chronological Evidence)

| Date | Commit | Description |
|---|---|---|
| 2026-02-11 | `9de1fd5` | Built 3DOS integration: 6 MCP tools, 6 CLI commands, 46 tests |
| 2026-02-12 | `e18ba0d` | Added 3DOS to whitepaper fulfillment fee description |
| 2026-02-12 | `97f05e4` | Expanded litepaper with 3DOS distributed manufacturing as a feature |
| 2026-02-12 | — | **DM sent to John proposing collaboration and requesting API keys** |
| 2026-02-17 | `21f655d` | Removed 3DOS branding from docs (partnership unconfirmed) |
| 2026-02-18 | `87398b0` | Fulfillment proxy system noting 3DOS as one integration option |
| 2026-02-23 | `018046e` | Added boundary clarification: "Kiln is not a network" |
| 2026-02-23 | `2121b6a` | Deprecated `network_*` naming, created `/boundary` page |
| 2026-02-24 | — | **John's first reply (hostile message accusing Adam of copying)** |
| 2026-02-24 | — | **John sends formal conflict review request to Roger** |

---

## Appendix B: What Kiln's AI Was Actually Told

Throughout Kiln's development, the AI tools (Claude) were given explicit instructions regarding 3DOS. The project's internal instruction file (CLAUDE.md) and conversation history contain directives to:

- Not compete with 3DOS
- Build Kiln as an orchestration/agent layer, not as a manufacturing network
- Treat 3DOS as a potential partner integration, not a competitor
- Remove 3DOS-specific branding from public docs when the partnership was unconfirmed

These instructions are verifiable in the project's conversation logs and configuration files.

---

*This document presents factual information supported by the Kiln codebase, git history, and timestamped communications. It is prepared for use in legal consultation and internal review. Not for public distribution.*
