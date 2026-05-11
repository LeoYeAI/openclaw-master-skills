# Bambu Lab Print Pipeline — Hard-Won Learnings

## Swarm Task Prompt

Use this prompt to have a Claude swarm implement all learnings into Kiln so future Bambu users never face these issues:

---

### Prompt for Claude Swarm

You are improving Kiln's Bambu Lab adapter (`kiln/src/kiln/printers/bambu.py`) and related infrastructure to make printing on Bambu printers as reliable as pressing "Print" on the touchscreen. Below are ALL the hard-won learnings from the first successful end-to-end AI-driven print on a Bambu Lab A1 Combo. Every single one of these caused real failures. Implement fixes for ALL of them.

**Branch:** Create `feature/bambu-print-reliability` from `main`

**Reference files:**
- `kiln/src/kiln/printers/bambu.py` — Bambu MQTT/FTPS adapter
- `kiln/src/kiln/printers/base.py` — Abstract PrinterAdapter
- `kiln/src/kiln/gcode.py` — G-code validation
- `kiln/src/kiln/server.py` — MCP tools (preflight_check, start_print)
- `kiln/src/kiln/slicer.py` — Slicer integration
- `.dev/LESSONS_LEARNED.md` — Append new learnings

---

## 1. FTPS Upload Issues

### 1a. Python 3.14 breaks Bambu FTPS
**Problem:** Python 3.14's `ftplib.FTP_TLS` changed TLS handling. The standard `connect()` method no longer works with Bambu's implicit FTPS (port 990) because it tries to wrap an already-wrapped socket. The `storbinary()` method's `conn.unwrap()` also times out.

**Fix needed:** Create a `BambuFTP(ftplib.FTP_TLS)` subclass in `bambu.py` that:
- Overrides `connect()` to directly create a TLS-wrapped socket via `context.wrap_socket()` instead of connect-then-upgrade
- Overrides `ntransfercmd()` to manually handle passive mode data connections with TLS wrapping
- Overrides `storbinary()` to catch `TimeoutError` and `OSError` on `conn.unwrap()` in the finally block (upload succeeds before unwrap times out)
- Handles the case where data connection may not be an SSL socket: `if hasattr(conn, 'unwrap'): conn.unwrap()`

### 1b. Bambu A1 uses `/model/` not `/sdcard/`
**Problem:** A1 series stores files at `/model/` on FTPS, not `/sdcard/` like X1 series.

**Fix:** The adapter should try `/model/` first, fall back to `/sdcard/` if CWD fails. Detect printer model from MQTT and route accordingly.

### 1c. Must call `prot_p()` after login
**Problem:** Without `ftp.prot_p()`, the data channel isn't encrypted and uploads fail with `BrokenPipeError`.

**Fix:** Always call `prot_p()` immediately after `login()` in the FTPS upload flow.

---

## 2. MQTT Print Command Issues

### 2a. URL format: `file:///sdcard/model/` NOT `ftp:///model/`
**Problem:** This was THE hardest bug. Using `ftp:///model/filename.3mf` in the MQTT print command makes the firmware try to fetch from its own FTP server, triggering HMS error `0500-C010-010800` ("MicroSD Card read/write exception"). This error persisted across TWO different SD cards, making it look like a hardware issue.

**Fix:** The URL in the MQTT `project_file` command MUST be `file:///sdcard/model/filename.3mf`. This reads directly from the filesystem like the touchscreen does. Never use `ftp:///`.

**Proof:** Touchscreen prints worked fine with the same files that failed via MQTT with `ftp:///` URLs.

### 2b. Access code regenerates when LAN Only Mode is toggled
**Problem:** Toggling LAN Only Mode off and back on generates a new access code. FTPS/MQTT auth fails with the old code (530 login failure / MQTT rc=5).

**Fix:** When connection fails with auth error, prompt user to check their access code on the printer (Settings > General > LAN Mode). Consider caching the code with a TTL and re-prompting if auth fails.

### 2c. Developer Mode is required for third-party MQTT commands
**Problem:** Without Developer Mode enabled, MQTT `project_file` commands are silently ignored.

**Fix:** Add a preflight check that verifies Developer Mode is on. The MQTT info report includes device capabilities — check for the dev mode flag. If not on, provide clear instructions to enable it.

---

## 3. 3MF Packaging Issues

### 3a. 3MF metadata must reference the correct printer model
**Problem:** A cloned 3MF had `printer_model: "Bambu Lab N1"` instead of `"Bambu Lab A1"`. This caused Bambu Handy to show "nozzle diameter does not match" and blocked printing.

**Fix:** In `machine_settings_1.config`, always set:
- `printer_model` matching the target printer exactly ("Bambu Lab A1", "Bambu Lab A1 mini", "Bambu Lab X1 Carbon", etc.)
- `printable_area` matching the printer (A1: 256x256, A1 mini: 180x180, X1: 256x256)
- `printable_height` matching (A1: 256, A1 mini: 180, X1: 256)
- `nozzle_diameter` matching the installed nozzle (0.4mm default)

### 3b. Temperature commands MUST be in the gcode
**Problem:** Gcode that was cleaned/stripped lost M104/M109/M140/M190 commands. Printer entered PREPARE state, moved around (homing), but nozzle target stayed 0°C. Never heated, never printed.

**Fix:** In `gcode.py`, add a validation function `validate_bambu_gcode()` that checks:
- At least one M140 or M190 (bed temp) command exists
- At least one M104 or M109 (nozzle temp) command exists
- Temperature values are reasonable (150-300°C nozzle, 40-110°C bed for PLA/PETG/ABS)
- Run this check BEFORE uploading to the printer. Fail loudly if missing.

### 3c. Bambu firmware requires proper start gcode for full functionality
**Problem:** Simple start gcode (`G28; G1 Z5 F5000`) causes the printer to show 0h0m time estimate and 0% progress. While printing eventually works, the firmware can't track progress or provide time estimates.

**Full A1 start gcode** is ~400 lines of proprietary commands including:
- `M1002 gcode_claim_action` state markers (2=heating, 24=material prep, 1=bed leveling, 0=printing)
- `G392`, `M9833.2` (machine init)
- `G380` (endstop avoidance)
- `M960` (laser/logo control)
- `M982.2` (noise reduction)
- `G29 A1` (auto bed leveling)
- `G2814` (nozzle height)
- `M1007` (mass estimation)
- `M73 P{pct} R{remaining}` (progress tracking at each layer change)
- `M412` (filament runout detection)
- `M620.3` (filament tangle detection)

**Fix:** Create a `BambuGcodeBuilder` class that:
1. Stores the full A1 start/end gcode templates with resolved variables
2. Has methods like `build_start_gcode(nozzle_temp, bed_temp, filament_type, bed_type)`
3. Injects M73 progress markers at every `;LAYER_CHANGE`
4. Adds a `; HEADER_BLOCK_START` / `; HEADER_BLOCK_END` section with `; total layer number:` and `; total estimated time:`
5. Ships templates for each supported printer (A1, A1 mini, X1C, P1S, etc.)
6. Falls back to simple gcode if the printer model is unknown

### 3d. Required 3MF structure
A valid Bambu 3MF must contain:
```
[Content_Types].xml
_rels/.rels
3D/3dmodel.model
Metadata/plate_1.gcode          ← The actual gcode
Metadata/plate_1.json           ← Plate metadata (nozzle_diameter, bed_type)
Metadata/machine_settings_1.config  ← Printer model, printable area, nozzle size
Metadata/model_settings.config  ← Per-object settings
Metadata/slice_info.config      ← Time estimate, filament usage
Metadata/project_settings.config ← Version info
```

---

## 4. Preflight / Safety Issues

### 4a. Temperature preflight check needed
**Problem:** When gcode had temperature commands stripped, the printer entered PREPARE and moved around but never heated. Kiln should have caught this before sending the print.

**Fix:** In `preflight_check()` MCP tool, add:
- Parse the gcode and verify nozzle/bed temperature commands exist
- Verify temperature targets are non-zero and reasonable
- After sending print command, monitor MQTT for 60 seconds and verify both nozzle_target_temper and bed_target_temper are non-zero
- If targets stay at 0 after 30 seconds, auto-cancel and report the issue

### 4b. Model geometry validation
**Problem:** PrusaSlicer warned about "Floating object part" and "Floating bridge anchors." This model caused the printer to do init sequence but never start actual extrusion because sliced gcode had unsupported geometry.

**Fix:** After slicing, check PrusaSlicer/slicer warnings. If "floating" or "empty layer" warnings appear, warn the user and suggest enabling supports or reorienting the model.

---

## 5. Monitoring Issues

### 5a. Python socket sandbox blocking
**Problem:** In some environments (Claude Code sandbox), Python's `socket.create_connection()` is blocked for TCP connections to local network devices, even though `ping` and `nc` work. This makes `paho.mqtt.client` and `ftplib` fail.

**Fix:** Add a fallback path in the Bambu adapter:
- Try Python sockets first (paho-mqtt, ftplib)
- If connection fails with `OSError: [Errno 65] No route to host`, fall back to `mosquitto_pub`/`mosquitto_sub` CLI tools for MQTT and `curl` for FTPS
- Detect environment at adapter initialization and choose the appropriate transport

### 5b. MQTT state reporting is sparse
**Problem:** The A1 doesn't always include `gcode_state` in every MQTT report. Many reports only contain temperature data. Progress (`mc_percent`, `mc_remaining_time`) only appears after the start gcode sequence completes.

**Fix:** Don't treat missing `gcode_state` as an error. Cache the last known state and only update when a new state is reported. Don't timeout waiting for a state if temperatures are changing (printer is active).

---

## 6. Network / Connectivity Issues

### 6a. Bambu Studio cannot view storage in LAN Only Mode
**Problem:** When LAN Only Mode is enabled, Bambu Studio's "Storage" tab doesn't work. This made it look like the SD card was broken when it was actually fine.

**Fix:** Document this limitation. When users report SD card issues, first check if LAN Only Mode is causing Bambu Studio to not see files. Bambu Handy (mobile app) CAN still see files in LAN Only Mode.

### 6b. Router/firewall can block LAN traffic
**Problem:** Some routers block device-to-device LAN communication. FTPS/MQTT connections fail even when the printer is on the same subnet.

**Fix:** In `kiln doctor --deep`, check for:
- ICMP ping to printer
- TCP connectivity to port 990 (FTPS) and 8883 (MQTT)
- If ping works but TCP fails, suggest checking router's AP isolation / client isolation settings

---

## 7. Implementation Checklist

For the swarm, implement in this order:
1. **BambuFTP subclass** — Fix Python 3.14 FTPS issues (bambu.py)
2. **MQTT URL fix** — Change `ftp:///` to `file:///sdcard/` (bambu.py start_print)
3. **BambuGcodeBuilder** — Start/end gcode templates with M73 progress (new file or in bambu.py)
4. **3MF Builder** — Proper 3MF packaging with correct metadata (new file or in bambu.py)
5. **Temperature preflight** — Validate temp commands exist before upload (gcode.py)
6. **Slicer warning parser** — Check for floating/unsupported geometry warnings (slicer.py)
7. **Transport fallback** — curl/mosquitto fallback for sandboxed environments (bambu.py)
8. **Access code handling** — Re-prompt on auth failure with clear instructions (bambu.py)
9. **Developer Mode check** — Verify dev mode before attempting MQTT commands (bambu.py)
10. **Tests** — Add tests for all new functionality following test patterns in tests/

**Test count target:** Add 50+ tests covering:
- BambuFTP connect/upload/download
- MQTT URL format validation
- 3MF structure validation
- Gcode temperature validation
- Start gcode template rendering
- M73 progress marker injection
- Access code auth failure handling
- Developer Mode detection

---

## Key Principle

The goal: **Kiln should be easier than pressing print on the touchscreen.** Every manual step the user has to do (toggle LAN mode, check access code, verify gcode, check temperatures) should be automated or pre-validated by Kiln. If something will fail, Kiln should tell the user BEFORE wasting their time.
