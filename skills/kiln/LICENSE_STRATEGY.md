# Kiln — License Strategy

**Decision date:** 2026-02-14
**Decided by:** Adam + Chris

## Decision: Open Core (MIT core, proprietary platform later)

### Why MIT

Chris nailed it: trust is the adoption gate. Nobody installs closed-source software that:
- Sends G-code to their expensive printer
- Sits between their AI agent and their hardware
- Has access to sensitive/private agent data

The core **must** be open source for adoption to work. This isn't a concession — it's the growth strategy.

### What's MIT (this repo — `kiln`)

Everything that touches the printer, the agent, or runs locally:

- All printer adapters (OctoPrint, Moonraker, Bambu, Prusa Connect, future ones)
- All marketplace adapters (Thingiverse, MyMiniFactory, Cults3D)
- G-code safety validator + safety profiles
- Slicer integration + slicer profiles
- Printer intelligence database
- MCP protocol layer + all tool definitions
- CLI tool (octoprint-cli)
- Pipelines (quick_print, calibrate, benchmark)
- Agent loop / OpenRouter integration
- Persistence layer (SQLite, job history, agent memory)
- Single-printer and multi-printer local use — full functionality, no restrictions

### What's proprietary (future separate repo — `kiln-platform`)

Enterprise/cloud features that only matter at scale or as a hosted service:

- Hosted/cloud API (multi-tenant)
- Auth + API key management (for hosted service)
- Billing/fee tracking (for hosted service)
- Enterprise fleet features TBD

**This repo does not exist yet.** Don't build it until there's real demand from fleet operators.

### Why separate repos (not monorepo split)

- Clean licensing — no confusing per-file headers
- Contributors know exactly what they're contributing to (MIT, period)
- No ambiguity on PyPI about what license the package has
- Easier to communicate: "Kiln is MIT. Full stop."

### What this means for USC partnership

Students contribute to a genuinely MIT-licensed open-source project. No asterisks, no "well actually it's source-available." Their contributions are real OSS on their resume.

### What this means for adoption

Users can read every line of code that touches their printer or their agent's data. Chris's point: "there's zero chance I'd ever install an openclaw tool that wasn't open source." Same applies to Kiln.

### Future considerations

- If fleet operators emerge as a market, build `kiln-platform` as a separate product
- Talk to actual fleet operators before designing the proprietary layer
- The paid product sells convenience and scale, not access — users are already past the trust barrier from running the open core
