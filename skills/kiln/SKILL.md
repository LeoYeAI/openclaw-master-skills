---
name: kiln
description: Control 3D printers with AI agents — 430 MCP tools, 114 CLI commands, text/sketch-to-3D generation, model marketplace search, multi-printer fleet support, safety enforcement, and outsourced manufacturing
homepage: https://kiln3d.com
user-invocable: true
metadata: {"openclaw":{"emoji":"🏭","os":["darwin","linux"],"requires":{"env":["KILN_PRINTER_HOST","KILN_PRINTER_API_KEY"],"bins":["kiln"],"anyBins":["prusaslicer","orcaslicer"]},"primaryEnv":"KILN_PRINTER_HOST","install":[{"kind":"uv","pkg":"kiln3d","git":"https://github.com/codeofaxel/Kiln.git","subdirectory":"kiln"}],"optional":{"env":["KILN_PRINTER_TYPE","KILN_PRINTER_MODEL","KILN_AUTONOMY_LEVEL","KILN_HEATER_TIMEOUT","KILN_CRAFTCLOUD_API_KEY","KILN_SCULPTEO_API_KEY","KILN_MESHY_API_KEY","KILN_TRIPO3D_API_KEY","KILN_STABILITY_API_KEY","KILN_GEMINI_API_KEY"]}}}
---

# Kiln — Agent Skill Definition

You are controlling a physical 3D printer through Kiln.
**Physical actions are irreversible and can damage hardware.** Follow
these rules strictly.

## Quick Start

```bash
kiln setup          # interactive wizard — finds printers, saves config
kiln verify         # check everything is working
kiln status --json  # see what the printer is doing
```

Then ask the human what they'd like to print.

---

## Which Interface to Use

Kiln supports **two interfaces**. Pick based on your capabilities:

| | CLI | MCP |
|---|---|---|
| **Use when** | You have a shell/exec tool | You have an MCP client configured |
| **How it works** | `kiln <command> [flags] --json` | MCP tool calls with JSON arguments |
| **Response format** | JSON to stdout (with `--json`) | Structured JSON objects |
| **Setup** | Just env vars + `kiln` on PATH | `kiln serve` running as MCP server |
| **Tool count** | 114 CLI commands | 430 MCP tools |
| **Best for** | Quick start, debugging, simple workflows | Tight integration, full tool catalog |

**Don't know which?** Try CLI first. Run `kiln status --json`. If that
works, you're good. MCP gives you more tools but requires server setup.

---

## CLI Interface

Run commands via your shell/exec tool. **Always use `--json`** for
machine-readable output.

```bash
kiln <command> [options] --json
```

### First-Time Setup

If the printer isn't configured yet, run these first:

```bash
# Interactive wizard: auto-discovers printers, saves config, tests connection
kiln setup

# Or manually add a printer
kiln auth --name my-printer --host http://192.168.1.100 --type octoprint --api-key YOUR_KEY

# Verify everything works (Python, slicer, config, printer reachable, database)
kiln verify

# Scan network for printers
kiln discover --json
```

After setup, config is saved to `~/.kiln/config.yaml` — no env vars needed.

### Core Commands

```bash
# Check printer status (start here)
kiln status --json

# List files on printer
kiln files --json

# Run safety checks before printing
kiln preflight --json
kiln preflight --material PLA --json

# Upload a G-code file
kiln upload /path/to/model.gcode --json

# Start printing (auto-uploads local files, auto-runs preflight)
kiln print model.gcode --json
kiln print model.gcode --dry-run --json   # preview without starting

# Cancel / pause / resume
kiln cancel --json
kiln pause --json
kiln resume --json

# Set temperatures
kiln temp --tool 210 --bed 60 --json
kiln temp --json                        # read current temps (no flags)

# Send raw G-code
kiln gcode G28 "G1 X50 Y50 F3000" --json

# Slice STL to G-code
kiln slice model.stl --json
kiln slice model.stl --print-after --json   # slice + upload + print

# Webcam snapshot
kiln snapshot --save photo.jpg --json

# Wait for print to finish (blocks until done)
kiln wait --json

# Print history
kiln history --json
kiln history --status completed --json

# Discover printers on network
kiln discover --json

# Cost estimate
kiln cost model.gcode --json
```

### Outsourced Manufacturing (Fulfillment)

No local printer? Printer busy? Kiln can outsource to manufacturing
services (Craftcloud, Sculpteo) with the same CLI.

```bash
# List available materials from configured service
kiln order materials --json

# Get a manufacturing quote (uploads model, returns pricing + lead time)
kiln order quote model.stl -m pla_standard --json

# Place the order [confirm — ask human first, shows price]
kiln order place QUOTE_ID --json

# Track order status
kiln order status ORDER_ID --json

# Cancel (if still cancellable)
kiln order cancel ORDER_ID --json

# Compare local printing vs. outsourced cost side-by-side
kiln compare-cost model.gcode --fulfillment-material pla_standard --json
```

**Setup:** Set one of these env vars (or add to `~/.kiln/config.yaml`):
```bash
export KILN_CRAFTCLOUD_API_KEY="your_key"     # Craftcloud (easiest — one key)
# OR
export KILN_SCULPTEO_API_KEY="your_key"       # Sculpteo
```

**Agent workflow:** Check local printer → if unavailable/busy → quote
fulfillment → present price to human → human approves → place order →
return tracking link.

### Text & Sketch to 3D Generation

Generate printable 3D models from text descriptions or napkin sketches.
Kiln auto-discovers providers from environment variables.

```bash
# List available generation providers [safe]
kiln generate list --json

# Generate a model from text [confirm — creates new file]
kiln generate "a small vase with organic curves" --provider gemini --json
kiln generate "phone stand" --provider meshy --style organic --json

# Check generation status (for async providers like Meshy/Tripo3D)
kiln generate status JOB_ID --json

# Download completed result
kiln generate download JOB_ID --json
```

**MCP equivalents:**
```json
{"name": "list_generation_providers", "arguments": {}}
{"name": "generate_model", "arguments": {"prompt": "a small vase", "provider": "gemini"}}
{"name": "check_generation_status", "arguments": {"job_id": "gemini-abc123"}}
{"name": "download_generated_model", "arguments": {"job_id": "gemini-abc123"}}
```

**Available providers** (set env var to enable):

| Provider | Env Var | Type | Async? |
|----------|---------|------|--------|
| **Gemini Deep Think** | `KILN_GEMINI_API_KEY` | AI reasoning → OpenSCAD → STL | No (synchronous) |
| **Meshy** | `KILN_MESHY_API_KEY` | Cloud text-to-3D | Yes (poll status) |
| **Tripo3D** | `KILN_TRIPO3D_API_KEY` | Cloud text-to-3D | Yes (poll status) |
| **Stability AI** | `KILN_STABILITY_API_KEY` | Cloud text-to-3D | Yes (poll status) |
| **OpenSCAD** | (local binary) | Parametric code → STL | No (synchronous) |

**Gemini Deep Think** uses Google's Gemini API to reason about geometry
and generate precise OpenSCAD code, which is compiled locally to STL.
Supports text descriptions and sketch/napkin-drawing descriptions.
Requires OpenSCAD installed locally.

**Agent workflow:** Ask what the user wants → generate with best
available provider → validate mesh → slice → print.

### Model Marketplace Search

Search and download existing 3D models from online marketplaces before
generating from scratch.

```bash
# Search across all connected marketplaces [safe]
kiln search "phone stand" --json

# Search a specific marketplace [safe]
kiln search "vase" --marketplace thingiverse --json

# Get model details [safe]
kiln model-details thingiverse MODEL_ID --json

# Download a model file [confirm — downloads to local disk]
kiln model-download thingiverse MODEL_ID --json
```

**MCP equivalents:**
```json
{"name": "search_all_models", "arguments": {"query": "phone stand"}}
{"name": "search_models", "arguments": {"query": "vase", "marketplace": "thingiverse"}}
{"name": "get_model_details", "arguments": {"marketplace": "thingiverse", "model_id": "12345"}}
{"name": "download_model_file", "arguments": {"marketplace": "thingiverse", "model_id": "12345"}}
```

**Supported marketplaces:** Thingiverse, MyMiniFactory, Thangs,
Cults3D, GrabCAD, Etsy.

**Agent workflow:** User describes what they want → search marketplaces
→ present top results → if nothing fits, generate from text instead.

### Fleet Management

Manage multiple printers as a fleet with job queuing and smart routing.

```bash
# Register a printer in the fleet [guarded]
kiln fleet add --name ender3 --host http://192.168.1.100 --type octoprint --json

# Fleet-wide status [safe]
kiln fleet status --json

# Submit a job to the queue (auto-routes to best available printer)
kiln fleet print model.gcode --json

# View job queue [safe]
kiln fleet queue --json
```

**MCP equivalents:**
```json
{"name": "fleet_status", "arguments": {}}
{"name": "register_printer", "arguments": {"name": "ender3", "host": "http://192.168.1.100", "type": "octoprint"}}
{"name": "submit_fleet_job", "arguments": {"filename": "model.gcode"}}
{"name": "list_queue", "arguments": {}}
```

### Webhooks

Register HTTP endpoints to receive real-time notifications.

```bash
# Register a webhook [guarded]
kiln webhook add https://example.com/hook --events print_complete,print_failed --json

# List webhooks [safe]
kiln webhook list --json

# Delete a webhook [confirm]
kiln webhook delete WEBHOOK_ID --json
```

All payloads are signed with HMAC-SHA256 for verification.

### Multi-Printer Support

```bash
# List saved printers
kiln printers --json

# Target a specific printer (works with any command)
kiln --printer my-ender3 status --json
kiln --printer bambu-x1c print model.gcode --json
```

Run `kiln --help` for all commands. `kiln <command> --help` for options.

### CLI Response Format

**Success** — exit code 0, JSON to stdout:
```json
{"status": "printing", "filename": "model.gcode", "progress": 42.5,
 "temps": {"tool": 210.0, "bed": 60.0}}
```

**Error** — non-zero exit code, JSON with `"error"`:
```json
{"error": "Printer is offline"}
```

**Warnings** — `"warnings"` array alongside normal data:
```json
{"status": "ok", "warnings": ["Hotend temperature above typical PLA range"]}
```

Check exit code first (0 = success), then `"warnings"` in the JSON.

### Example Responses

**`kiln status --json`** (printing):
```json
{"status": "success", "data": {"printer": {"status": "printing", "temps": {"tool0": {"actual": 210.0, "target": 210.0}, "bed": {"actual": 60.0, "target": 60.0}}}, "job": {"filename": "model.gcode", "progress": 42.5, "time_left": 3600}}}
```

**`kiln print model.gcode --json`** (started):
```json
{"status": "success", "message": "Print started", "filename": "model.gcode"}
```

**`kiln order quote model.stl -m pla_standard --json`**:
```json
{"status": "success", "quote_id": "q_abc123", "price_usd": 12.50, "lead_time_days": 5, "shipping_options": [{"id": "std", "price_usd": 4.99, "days": 7}]}
```

---

## MCP Interface

If your platform has an MCP client, Kiln exposes 430 tools as an MCP
server. Tools are called by name with JSON arguments — your MCP client
handles the transport.

### Starting the MCP Server

```bash
kiln serve
```

Or configure in Claude Desktop (`~/.config/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "kiln": {
      "command": "kiln",
      "args": ["serve"],
      "env": {
        "KILN_PRINTER_HOST": "http://your-printer-ip",
        "KILN_PRINTER_API_KEY": "your_key",
        "KILN_PRINTER_TYPE": "octoprint"
      }
    }
  }
}
```

### MCP Tool Call Format

```json
{"name": "printer_status", "arguments": {}}
{"name": "start_print", "arguments": {"filename": "model.gcode"}}
{"name": "set_temperature", "arguments": {"tool_temp": 210, "bed_temp": 60}}
{"name": "send_gcode", "arguments": {"commands": ["G28", "G1 X50 Y50 F3000"]}}
{"name": "upload_file", "arguments": {"file_path": "/path/to/model.gcode"}}
```

Parameter names and types are auto-documented by the server — your
client shows them. Call `get_started()` for an onboarding guide.

### MCP Response Format

All tools return JSON objects. Same pattern as CLI:
- Success: tool-specific fields
- Error: `{"error": "message", "status": "error"}`
- Warnings: `"warnings"` array alongside data

---

## Setup

Set these environment variables before using Kiln (CLI or MCP):

```bash
export KILN_PRINTER_HOST="http://your-printer-ip"
export KILN_PRINTER_API_KEY="your_api_key"
export KILN_PRINTER_TYPE="octoprint"   # or: moonraker, bambu, prusaconnect, elegoo
```

Verify connectivity:
```bash
kiln status --json
```

## File Intelligence

G-code files on printers often have cryptic names (`test5112.gcode`,
`spacer_v3.gcode`). Kiln extracts metadata from G-code headers so you
can reason about files without relying on filenames.

```bash
# Analyze a specific file [safe]
kiln analyze-file benchy.gcode --json
```

Returns structured metadata:
```json
{
  "material": "PLA",
  "estimated_time_seconds": 6150,
  "tool_temp": 210.0,
  "bed_temp": 60.0,
  "slicer": "PrusaSlicer 2.7.0",
  "layer_height": 0.2,
  "filament_used_mm": 4523.45
}
```

**How to use file intelligence:**
1. List files: `kiln files --json` — each file now includes metadata
2. Check material match before printing: compare `material` field with
   loaded material (`kiln material show --json`)
3. Check estimated time: use `estimated_time_seconds` to assess duration
4. Validate temperatures: compare `tool_temp`/`bed_temp` with safety profile

**Example: Choosing an overnight print**
```
"I found 3 files on your printer:
- benchy.gcode — PLA, ~45 min, 210°C/60°C
- phone_stand.gcode — PLA, ~2h 10m, 210°C/60°C
- test5112.gcode — PETG, ~8h 30m, 240°C/80°C

You have PLA loaded. phone_stand.gcode is the best match for overnight
(PLA-compatible, reasonable duration). Want me to start it?"
```

---

## Safety Model

Kiln enforces **physical safety** — it will hard-block commands that
exceed temperature limits, contain dangerous G-code, or fail pre-flight
checks. You cannot bypass these.

**You** enforce **operational judgment** — deciding when to ask the
human for confirmation vs. acting autonomously. This document defines
those rules.

## Autonomy Tiers

The human configures how much autonomous control you have. Check
`kiln autonomy show --json` to see the current level.

| Level | Name | Behavior |
|-------|------|----------|
| **0** | Confirm All | (Default) Every `confirm`-level tool requires human approval. |
| **1** | Pre-screened | You may skip confirmation IF the operation passes configured constraints (material, time, temperature). |
| **2** | Full Trust | You may execute any tool autonomously. Only `emergency` tools still need confirmation. |

### Level 1 Constraints

At Level 1, the human pre-configures safety boundaries:

```yaml
# ~/.kiln/config.yaml
autonomy:
  level: 1
  constraints:
    max_print_time_seconds: 14400     # 4 hours max
    allowed_materials: ["PLA", "PETG"] # only these materials
    max_tool_temp: 260                 # hotend ceiling
    max_bed_temp: 100                  # bed ceiling
    require_first_layer_check: true    # must monitor first layer before leaving print unattended
```

**Your workflow at Level 1:**
1. Analyze the file (`kiln files --json` or `kiln analyze-file FILE --json`)
2. Check constraints: material in allowed list? Time under limit? Temps OK?
3. If ALL constraints pass → proceed without asking
4. If ANY constraint fails → ask the human, explain which constraint failed

**Example: Level 1 autonomous print**
```
File: phone_stand.gcode
  Material: PLA ✓ (in allowed list)
  Time: 2h 10m ✓ (under 4h limit)
  Tool temp: 210°C ✓ (under 260°C limit)
  Bed temp: 60°C ✓ (under 100°C limit)
→ All constraints passed. Starting print autonomously.
```

**Example: Level 1 blocked print**
```
File: test5112.gcode
  Material: PETG ✓
  Time: 8h 30m ✗ (exceeds 4h limit)
→ Constraint failed. Asking human for permission.
```

### Level 2 Full Trust

The human has explicitly given you permission to operate freely.
This is typically set with a statement like:
> "Every file on my printer is for generic PLA, will print in under 2 hours, and is safe."

At Level 2, you may start prints, set temperatures, and send G-code
without asking — but you MUST still:
- Run preflight checks (Kiln does this automatically)
- Respect Kiln's hard safety limits (temperature caps, blocked G-code)
- Report what you did after the fact
- Monitor the print if camera is available

### Env Var Override

```bash
export KILN_AUTONOMY_LEVEL=1  # Quick override without editing config
```

## Tool Safety Levels

Every command has a safety level. Follow the expected behavior exactly.
**Autonomy level modifies `confirm`-level behavior only.** Safe, guarded,
and emergency levels are unaffected by autonomy settings.

| Level | Meaning | Your Behavior |
|-------|---------|---------------|
| `safe` | Read-only, no physical effect | Call freely. No confirmation needed. |
| `guarded` | Has physical effect but low-risk. Kiln enforces limits. | Call without asking. Report what you did. |
| `confirm` | Irreversible or significant state change. | **Depends on autonomy level.** Level 0: ask human. Level 1: check constraints. Level 2: proceed. |
| `emergency` | Safety-critical. | **Always ask the human** unless active danger (thermal runaway, collision). |

## Command Safety Classifications

### Safe (read-only, call freely)

| Command | Description |
|---------|-------------|
| `kiln status --json` | Printer state, temps, progress |
| `kiln files --json` | List files on printer |
| `kiln preflight --json` | Pre-print safety checks |
| `kiln printers --json` | List saved printers |
| `kiln discover --json` | Scan network for printers |
| `kiln history --json` | Print history |
| `kiln cost FILE --json` | Cost estimation |
| `kiln snapshot --json` | Webcam snapshot |
| `kiln verify` / `kiln doctor` | System health check |
| `kiln material show --json` | Current material |
| `kiln material spools --json` | Spool inventory |
| `kiln level --status --json` | Bed leveling status |
| `kiln firmware status --json` | Firmware versions |
| `kiln plugins list --json` | Installed plugins |
| `kiln order materials --json` | List fulfillment materials |
| `kiln order status ID --json` | Track order |
| `kiln order quote FILE --json` | Get manufacturing quote |
| `kiln compare-cost FILE --json` | Local vs. outsourced cost |
| `kiln autonomy show --json` | Current autonomy level and constraints |
| `kiln analyze-file FILE --json` | G-code file metadata (material, time, temps) |
| `kiln watch --json` | Monitor active print's first layer (read-only) |

### Guarded (low-risk, report what you did)

| Command | Description |
|---------|-------------|
| `kiln pause --json` | Pause print (reversible) |
| `kiln resume --json` | Resume print (reversible) |
| `kiln upload FILE --json` | Upload G-code (Kiln validates) |
| `kiln slice FILE --json` | Slice model (CPU only, no printer effect) |
| `kiln wait --json` | Wait for print to finish |
| `kiln material set --json` | Set loaded material |

### Confirm (ask human first)

| Command | Description | What to confirm |
|---------|-------------|-----------------|
| `kiln print FILE --json` | **Start printing** (auto-preflight, `--dry-run` to preview, `--skip-preflight` to bypass) | File name and material |
| `kiln cancel --json` | **Cancel print** | Irreversible — print cannot resume |
| `kiln temp --tool X --bed Y --json` | **Set temperatures** | What temp and why |
| `kiln gcode CMD... --json` | **Raw G-code** | What commands and why |
| `kiln slice FILE --print-after --json` | **Slice + print** | Full pipeline |
| `kiln level --trigger --json` | **Bed leveling** | Physical bed probing |
| `kiln firmware update --json` | **Firmware update** | High risk |
| `kiln order place QUOTE_ID --json` | **Place manufacturing order** | Price and shipping |
| `kiln order cancel ORDER_ID --json` | **Cancel order** | May not be reversible |
| `kiln autonomy set LEVEL --json` | **Change autonomy level** | Security-sensitive |
| `start_monitored_print` (MCP) | **Start print + monitor first layer** | File name and material |

### Emergency (ask human unless active danger)

| Command | Description |
|---------|-------------|
| `kiln gcode M112 --json` | Emergency stop. **Only for genuine emergencies.** |

## Recommended Workflows

### Upload and Print

```bash
# 1. Dry-run first [safe — preview what will happen]
kiln print model.gcode --dry-run --json

# 2. Start print [confirm — ask human first]
#    kiln print auto-uploads local files AND runs preflight automatically
#    "Ready to print model.gcode with PLA. Proceed?"
kiln print model.gcode --json

# 3. Monitor progress [safe]
kiln status --json              # check periodically
kiln snapshot --save check.jpg  # visual check after first layer

# 4. Wait for completion [safe]
kiln wait --json
```

> `kiln print` auto-uploads local files and runs pre-flight checks.
> Use `--skip-preflight` to bypass, `--dry-run` to preview without starting.

### Temperature Adjustment

```bash
# 1. Check current temps [safe]
kiln temp --json

# 2. Set temps [confirm — tell human: "Setting hotend to 210°C, bed to 60°C for PLA. OK?"]
kiln temp --tool 210 --bed 60 --json
# IF warnings: relay them
```

### Emergency Response

```bash
# 1. Detect issue
kiln status --json   # check for ERROR state or temp anomalies

# 2. IF thermal runaway or physical danger:
kiln gcode M112 --json   # emergency stop — may bypass confirmation
# Then immediately tell human: "Emergency stop triggered because: {reason}"

# 3. IF quality issue but no immediate danger:
# Ask human: "Detected potential failure. Cancel print?"
kiln cancel --json   # only after human confirms
```

### Print Monitoring Loop

**Preferred: Use `start_monitored_print` (MCP) or `kiln watch` (CLI).**
These tools combine starting the print with automatic first-layer monitoring.

```bash
# CLI — start print with first-layer monitoring
kiln watch --printer myprinter --delay 120 --checks 3 --interval 60 --json

# MCP — start_monitored_print tool does the same thing
```

`start_monitored_print` / `kiln watch`:
1. Starts the print
2. Waits 2 minutes for first layer to begin
3. Captures 3 webcam snapshots at 1-minute intervals
4. Returns snapshots + heuristic analysis (brightness, variance, warnings)
5. Auto-pauses if a failure is reported with confidence >= 0.8

**Monitoring tiers (adapt to your capabilities):**

| Your Capabilities | How to Monitor |
|---|---|
| **Vision + Camera** | Inspect the returned base64 snapshots visually. Look for bed adhesion, warping, extrusion consistency. |
| **No Vision + Camera** | Use the `snapshot_analysis` fields: `brightness`, `variance`, `warnings`, `heuristic_pass`. Low brightness = camera off. Low variance = empty bed or blocked camera. |
| **No Camera** | Fall back to telemetry: `kiln status --json` every 5 min. Watch for temp anomalies, progress stalls, error states. |

**After first-layer check passes, continue periodic monitoring:**

1. Every 5-10 minutes: `kiln status --json` — check for:
   - Temperature anomalies (sudden drops = heater failure)
   - Progress stalls (same % for >10 min = possible jam)
   - Error states
2. On completion: cool down heaters

| Situation | Action | Command |
|-----------|--------|---------|
| First layer failure | Pause + alert human | `kiln pause --json` |
| Temperature anomaly | Alert human | `kiln status --json` |
| Filament runout | Pause + alert human | `kiln pause --json` |
| Progress stalled | Alert human (do NOT cancel) | `kiln status --json` |
| Spaghetti / detach | Emergency stop | `kiln gcode M112 --json` |
| Normal completion | Cool down | `kiln temp --tool 0 --bed 0 --json` |

### Autonomous Overnight Print

The full workflow for safe autonomous printing while the user sleeps:

```
1. Analyze:  kiln analyze-file FILE --json
             → Get material, estimated time, temps from G-code metadata.

2. Check autonomy:  kiln autonomy show --json
             → Verify Level 1+ and constraints pass.

3. Start with monitoring:  start_monitored_print(file_name="FILE")
             → Starts print + automatic first-layer checks.

4. Review first layer snapshots:
   - Vision agents: inspect the images directly
   - Text agents: check heuristic_pass, brightness, variance
   - If issues: print is already auto-paused. Alert human.
   - If clean: print continues unattended.

5. Periodic telemetry:  kiln status --json  (every 10 min)
             → Watch for temp drift, progress stalls, errors.

6. Completion:  kiln temp --tool 0 --bed 0 --json
             → Cool down. Report result to human in morning.
```

**Key safety net:** If `require_first_layer_check` is enabled in autonomy
constraints, the agent MUST use `start_monitored_print` instead of
`start_print`. The autonomy check will remind you with
`"require_first_layer_check": true` in the response.

## Operational Policies

### Heater Idle Protection
Never set temperatures on an idle printer unless the human explicitly
asks for pre-heating. If you do, remind: "Heaters are on. Remember to
turn them off when done."

Kiln includes a **heater watchdog** that automatically cools down
heaters left on without an active print. Default timeout is 30 minutes
(`KILN_HEATER_TIMEOUT`). Set to `0` to disable. The watchdog will NOT
intervene while a print is active — it only triggers on idle heaters.

### Relay All Warnings
When Kiln returns `warnings`, always relay them to the human verbatim.

### Never Generate G-code
Never write or modify G-code. Use `kiln slice` for slicing, or use
pre-sliced files already on the printer.

### Material Awareness
Before printing, check loaded material (`kiln material show --json`).
If mismatched with what the G-code expects, warn the human.

### First-Layer Monitoring
If camera available, check the first few minutes of a new print with
`kiln snapshot`. If something looks wrong, ask the human before acting.

## What Kiln Enforces (you cannot bypass)

| Protection | How |
|-----------|-----|
| Max temperature per printer model | Safety profiles (per `KILN_PRINTER_MODEL`) |
| Blocked G-code commands | M112, M500-502, M552-554, M997 always rejected |
| Pre-flight before printing | Mandatory — `kiln print` runs it automatically |
| G-code validation on upload | Full file scanned for blocked commands |
| G-code validation on send | Every `kiln gcode` call is validated |
| Rate limiting | Dangerous commands have cooldowns to prevent spam |
| File size limits | 500MB upload max |
| Heater auto-off | Idle heaters auto-cool after `KILN_HEATER_TIMEOUT` min (default 30) |

## Licensing & Feature Tiers

Kiln uses a tiered licensing model. Most features are free forever.

| Tier | Price | Key Features |
|------|-------|--------------|
| **Free** | $0 | All printer control, slicing, safety enforcement, text-to-3D generation, marketplace search, CLI + MCP tools, single printer |
| **Pro** | Paid | Fleet management (multi-printer), fleet analytics, priority job queue |
| **Business** | Paid | Outsourced manufacturing (Craftcloud/Sculpteo fulfillment ordering + cancellation) |
| **Enterprise** | Paid | Dedicated MCP server, SSO authentication, audit trail export, role-based access, lockable safety profiles, on-prem deployment |

**Revenue tracking:** Kiln takes a 2.5% platform fee on revenue from
models published through Kiln's marketplace pipeline (configurable via
`KILN_PLATFORM_FEE_PCT`, range 0.0–15.0%). Local printing is always free.

**License key:** Set via `KILN_LICENSE_KEY` env var or `~/.kiln/license` file.
No key = free tier. Keys are prefixed `kiln_pro_`, `kiln_biz_`, `kiln_ent_`.

## Configuration

**Preferred: `kiln setup`** (interactive wizard, saves to `~/.kiln/config.yaml`).

**Alternative: env vars** (useful for Docker/CI):

| Env Var | Purpose | Default |
|---------|---------|---------|
| `KILN_PRINTER_HOST` | Printer URL (e.g. `http://192.168.1.100`) | (from config) |
| `KILN_PRINTER_API_KEY` | Printer API key | (from config) |
| `KILN_PRINTER_TYPE` | `octoprint` / `moonraker` / `bambu` / `prusaconnect` / `elegoo` | `octoprint` |
| `KILN_PRINTER_MODEL` | Safety profile id (e.g. `ender3`, `bambu_x1c`) | (generic limits) |
| `KILN_AUTONOMY_LEVEL` | Autonomy tier: `0` (confirm all), `1` (pre-screened), `2` (full trust) | `0` |
| `KILN_HEATER_TIMEOUT` | Minutes before idle heaters auto-cool (0=disabled) | `30` |
| `KILN_MONITOR_REQUIRE_FIRST_LAYER` | Require first-layer monitoring for autonomous prints | `false` |
| `KILN_MONITOR_FIRST_LAYER_DELAY` | Seconds before first snapshot after print starts | `120` |
| `KILN_MONITOR_FIRST_LAYER_CHECKS` | Number of first-layer snapshots to capture | `3` |
| `KILN_MONITOR_FIRST_LAYER_INTERVAL` | Seconds between first-layer snapshots | `60` |
| `KILN_MONITOR_AUTO_PAUSE` | Auto-pause on detected failure | `true` |
| `KILN_MONITOR_REQUIRE_CAMERA` | Refuse to start monitored print without camera | `false` |
| `KILN_VISION_AUTO_PAUSE` | Auto-pause on vision failure detection (confidence >= 0.8) | `false` |
| `KILN_CRAFTCLOUD_API_KEY` | Craftcloud fulfillment API key | (none) |
| `KILN_SCULPTEO_API_KEY` | Sculpteo partner API key | (none) |
| `KILN_MESHY_API_KEY` | Meshy text-to-3D API key | (none) |
| `KILN_TRIPO3D_API_KEY` | Tripo3D text-to-3D API key | (none) |
| `KILN_STABILITY_API_KEY` | Stability AI text-to-3D API key | (none) |
| `KILN_GEMINI_API_KEY` | Google Gemini Deep Think API key | (none) |
| `KILN_LICENSE_KEY` | License key (Pro/Business/Enterprise) | (free tier) |
| `KILN_PLATFORM_FEE_PCT` | Platform fee % on marketplace revenue | `2.5` |

