# Kiln — Lessons Learned

Hard-won technical patterns and bug fixes. Consulted when hitting unfamiliar issues. **Append new entries under the relevant section when you learn something new.**

---

## Printer Adapter Patterns
<!-- Patterns related to PrinterAdapter interface, state mapping, data normalization -->

### Temperature validation belongs in the base class
Don't rely on each adapter individually validating temperature bounds — they won't. Put a shared `_validate_temp()` in the abstract `PrinterAdapter` base class and call it from every concrete `set_tool_temp()`/`set_bed_temp()`. The MCP tool layer should ALSO validate, giving defense-in-depth. Same principle applies to any safety-critical operation: validate at every layer, not just one.

### Negative temperatures bypass `temp > limit` checks
The G-code validator originally only checked `temp > MAX_TEMP`. Negative temperatures (e.g., `M104 S-50`) passed right through. Always check `temp < 0` explicitly. This is the kind of bug that's invisible in happy-path testing but catastrophic in adversarial scenarios.

## OctoPrint API Quirks
<!-- Non-obvious behaviors of the OctoPrint REST API -->

## MCP Server Patterns
<!-- FastMCP tool registration, response formatting, error propagation -->

### Never pass `**body` from HTTP requests to tool functions
`func(**body)` lets callers inject arbitrary keyword arguments. Use `inspect.signature()` to filter to only valid parameters and reject unknowns with a 400. This prevents parameter pollution attacks where extra keys override internal defaults.

### Sanitize tool results before feeding to LLM agents
Tool results from MCP tools are untrusted data — printer names, filenames, and API error messages can all contain prompt injection payloads. Always sanitize before passing to the LLM. Add a system prompt warning about untrusted tool results.

### PrusaSlicer has no `--printer` CLI flag — use `--load` only
PrusaSlicer's CLI does NOT have a `--printer` flag. The code assumed it did (like some other tools) and passed `--printer "Original Prusa MINI & MINI+"`, which caused `kiln slice --printer-id X` to fail with "Unknown option --printer". The correct approach: generate a complete `.ini` profile file via `slicer_profiles.py` and pass it with `--load profile.ini`. PrusaSlicer applies all printer settings from the INI file. **Always verify that CLI flags you're generating actually exist in the target tool's documentation.** Mocked tests hide this class of bug entirely since the subprocess never runs.

## CLI / Output Formatting
<!-- Click CLI patterns, JSON output, exit codes, config management -->

### Every CLI command must support `--json` output
Human-readable output is the default, but agents and scripts depend on `--json`. When adding a new command, always include the `json_mode` flag and route through `format_response()` or the appropriate `format_*()` helper in `output.py`. Test both modes.

### Use the standard JSON envelope for all responses
All JSON output follows `{"status": "success|error", "data": {...}, "error": {...}}`. Never return bare data or ad-hoc structures. Agents parse the envelope to determine success/failure.

### Error messages must include what, why, and what-to-try
Bad: `"Error: connection refused"`. Good: `"Failed to connect to printer at http://octopi.local: connection refused. Check that OctoPrint is running and the host is correct."` Include the printer name/host when available.

## Python / Build System
<!-- pyproject.toml, setuptools, import resolution, packaging -->

### Always use `python3` and `pip3` on macOS
`python` may not exist or point to system Python 2. This causes silent import failures or wrong package installations. All scripts, commands, and documentation must use `python3`/`pip3`.

### ALWAYS run Ruff lint before pushing — CI will catch what you don't
CI runs `ruff check` on every push and fails on any violation. The local `py_compile` check only catches syntax errors, NOT lint issues like unused variables (F841) or function-call-in-defaults (B008). **After any Python edits, run `cd kiln && python3 -m ruff check src/kiln/` before committing.** Common gotchas: (1) `except Exception as exc:` where `exc` isn't used after sanitizing error messages — use `except Exception:` instead; (2) FastAPI `Depends()`/`File()` in function param defaults triggers B008 — hoist to module-level singletons like `_auth_dep = Depends(verify_auth)`. Never leave CI red. Fix immediately if it fails.

### `from __future__ import annotations` in every file
This enables PEP 604 union syntax (`X | None`) and forward references. Without it, type hints that reference later-defined classes fail at import time. Add it as the first import in every new file.

## Testing Patterns
<!-- pytest, mocking HTTP calls, mocking hardware, test isolation -->

### Counting CLI commands: walk the Click tree programmatically, count both packages
Never grep `@.*command()` or count function defs to get the CLI command count — these miss subcommands inside groups and overcount helpers. The correct method:
```python
python3 -c "
import click, sys
sys.path.insert(0, 'kiln/src')
from kiln.cli.main import cli
def count(group, prefix=''):
    cmds = []
    for name, cmd in group.commands.items():
        full = f'{prefix} {name}'.strip()
        cmds += count(cmd, full) if isinstance(cmd, click.Group) else [full]
    return cmds
print(len(count(cli)))
"
```
Also count `octoprint-cli` separately — kiln3d exposes **two CLI packages** (`kiln` + `octoprint-cli`). The total is their sum. As of v0.1.0: kiln=89, octoprint-cli=13, total=102.

### Use `responses` library for HTTP mocking, not `unittest.mock.patch` on requests
The `responses` library intercepts at the transport level, catching issues that `mock.patch` misses (like session reuse, header propagation, retry logic). Use `@responses.activate` decorator on each test method. Only use `unittest.mock.patch` for non-HTTP mocking (filesystem, time, env vars).

### Test all enum values — exhaustive coverage prevents state mapping bugs
When testing state mapping (e.g., OctoPrint flags → PrinterStatus), write a test for EVERY enum value. State mapping bugs (like `cancelling` → BUSY instead of CANCELLING) are caught by exhaustive tests, not by testing a few happy paths.

### Test class docstrings list coverage areas; method names are self-documenting
Class-level docstring explains what's being tested and what's covered. Individual test methods don't need docstrings — the name `test_empty_host_raises` is clear enough.

## Release & Publishing

### Version bump requires 3 files, not just pyproject.toml
When bumping the version for a release, update: (1) `kiln/pyproject.toml` → `version`, (2) `server.json` → top-level `version` AND `packages[0].version`, (3) `docs/site/src/layouts/BaseLayout.astro` → `softwareVersion` in the JSON-LD block. The CI workflow auto-syncs `server.json` from the git tag at publish time, but keep the repo in sync too so `main` always reflects the current version.

### PyPI + MCP Registry are both automated on GitHub Release
`publish.yml` triggers on `release: [published]`. It runs tests, validates the tag matches `pyproject.toml`, publishes to PyPI via trusted publishing (OIDC, no token), then publishes to the MCP Registry via `mcp-publisher` with GitHub OIDC. No manual publish commands needed — just `gh release create vX.Y.Z`.

### ClawHub skill must be republished on version bumps
ClawHub doesn't auto-detect updates from the repo. When shipping a new version (new tools, adapters, or SKILL.md changes), republish: `clawhub publish .dev --slug kiln --name "Kiln" --version X.Y.Z --tags "3d-printing,manufacturing,printer,mcp,octoprint,bambu,moonraker,klipper,prusa,ai-agent" --changelog "summary"`. This is part of the release checklist — don't skip it.

## Documentation & Content Updates
<!-- Rules for what to update, what to leave alone -->

### Hardcoded tool/command counts go stale — grep after every feature add
MCP tool counts and CLI command counts are hardcoded in 8+ places: CLAUDE.md, README.md, kiln/README.md, server.json, THREAT_MODEL.md, PROJECT_DOCS.md, GitHub description, SKILL.md. After adding new MCP tools or CLI commands, run `grep -rn "\d\+ MCP tools" . --include="*.md"` to find every stale reference. Also update the GitHub repo description via `gh api`. The count drifted from 273→345 across multiple releases without anyone catching it (2026-03-06).

### Never edit old blog posts to update counts or stats
Blog posts are dated content — they were accurate when published. When updating tool counts, CLI counts, test counts, etc. across the codebase, update README, docs, website components, and marketing pages — but **never** blog posts under `docs/site/src/pages/blog/`. Those are historical records. Only edit blog posts if explicitly told to.

## Project Structure & File Location
<!-- Where files live, directory conventions, common lookup mistakes -->

### Internal docs live in `.dev/`, not the repo root
All internal working documents (`TASKS.md`, `COMPLETED_TASKS.md`, `LESSONS_LEARNED.md`, `LONGTERM_VISION_TASKS.md`, `SWARM_GUIDE.md`, etc.) live in `.dev/`. When the user references a file by name (e.g., "longterm_vision_tasks.md"), check `.dev/` first — don't waste time globbing the entire repo. The Project Structure Quick Reference in `CLAUDE.md` documents this layout. **Read it before searching.**

## Configuration & Environment
<!-- Config precedence, environment variables, credential handling -->

### Save irrecoverable secrets BEFORE any subsequent operations
When a setup script generates and registers a secret with an external service (e.g., Circle entity secret), save it to disk **immediately** after the registration API call succeeds — before attempting any further operations. The original `circle_setup.py` registered the entity secret with Circle, then tried to create a wallet (which failed because TEST_API_KEY can't use mainnet chains). The script exited on error without saving the secret. Circle doesn't store entity secrets and has no reset path without the recovery file. Result: permanently locked out of the account. **Pattern:** Any time you generate a secret and send it to a remote service, the very next line must persist it locally. Never gate secret persistence on downstream operations succeeding.

### Circle Programmable Wallets: TEST_API_KEY requires testnet blockchains
Circle TEST_API_KEY keys can only create wallets on testnet blockchains (e.g., `SOL-DEVNET`, `ETH-SEPOLIA`), not mainnet (`SOL`, `ETH`). The API returns HTTP 400 with code 156006. Always check `api_key.startswith("TEST_API_KEY")` and use the corresponding testnet chain. LIVE_API_KEY uses mainnet chains.

### Circle W3S: Destination wallets need an ATA for USDC transfers
When transferring USDC on Solana via Circle W3S, the destination wallet must have an Associated Token Account (ATA) for the USDC token. If it doesn't, Circle's paymaster may refuse with `PAYMASTER_SOL_ATA_CREATION_NOT_ALLOWED`. Fix: fund the destination address with SOL + USDC via faucet (testnet) or ensure it has received USDC before. The `_resolve_chain()` method should auto-map to testnet chains for TEST_API_KEY.

### Bambu access_code vs api_key env vars
Bambu printers use an `access_code` (not the same as an API key). When building env-var config fast paths, don't reuse the same env var (`KILN_PRINTER_API_KEY`) for both `api_key` and `access_code` fields. Use `KILN_PRINTER_ACCESS_CODE` for Bambu access codes. DO NOT fall back to `KILN_PRINTER_API_KEY` — these are semantically different credential types and cross-contamination can cause auth failures or send wrong credentials to wrong backends.

## Hardware / Safety
<!-- Physical printer safety, G-code validation, temperature limits, destructive operations -->

### Preflight checks must be enforced, not optional
If `start_print()` doesn't call `preflight_check()` internally, agents WILL skip it. Safety-critical validation must be mandatory with NO opt-out. The original `skip_preflight=True` parameter was removed entirely — even an "advanced user" bypass is a security hole because agents will discover and use it.

### Path traversal in save/write operations
Any function that accepts a file path from an agent/user and writes to disk is a path traversal risk. Always resolve to absolute path (`os.path.realpath()`), then check it starts with an allowed prefix (home dir, temp dir). Use `tempfile.gettempdir()` resolved through `os.path.realpath()` for cross-platform temp dir detection — macOS `/tmp` resolves to `/private/tmp` and pytest fixtures use `/private/var/folders/`.

### Lock ordering prevents deadlocks
Never emit events (which trigger callbacks) while holding a lock. Callbacks may try to acquire the same lock → deadlock. Pattern: collect event data inside the lock, release the lock, THEN publish events. Applied to `materials.py:deduct_usage()` where `_emit_spool_warnings()` was called inside `with self._lock`.

### Bambu A-series sends UPPERCASE state values
A1/A1 mini printers send `gcode_state` as "RUNNING", "IDLE", "PAUSE" (all caps), unlike X1C/P1S which send lowercase. Always `.lower()` normalize `gcode_state` before matching. Also applies to MQTT `command` field — use case-insensitive comparison for all Bambu string enums.

### `package_name` in `click.version_option` must match `pyproject.toml`'s `name`
Click's `version_option(package_name=...)` uses `importlib.metadata` to look up the version. If the package name doesn't match the `name` in `pyproject.toml`, it crashes with `RuntimeError: 'X' is not installed`. Our package is `kiln3d` (not `kiln`) on PyPI. **Always verify the `package_name` matches the actual installed package name, not the repo or CLI name.**

### CLI choice lists must match the full provider registry
Hardcoded `click.Choice(["meshy", "openscad"])` silently rejected valid providers like `gemini`, `tripo3d`, `stability`. When new providers are added to `generation/registry.py`, the CLI choices must be updated in ALL commands: `generate`, `generate-status`, `generate-download`, and `generate-and-print`. **Better pattern:** use the same list constant across all commands so it's one change.

### Updating default model versions breaks existing tests
When changing a provider's `_DEFAULT_MODEL` (e.g., `gemini-2.0-flash` → `gemini-2.5-flash`), `responses`-mocked tests that build URLs from the model name will fail silently with connection errors. The test constant (`TEST_MODEL`) must match the actual default used at runtime. **After changing any default model, grep tests for the old model string and update.**

### Every code path that calls `adapter.start_print()` must run preflight
The `start_print()` MCP tool correctly enforces `preflight_check()`, but composite tools (`slice_and_print`, `download_and_upload`, `generate_and_print`) were calling `adapter.start_print()` directly — bypassing preflight entirely. Always route through the safety gate, even in convenience/shortcut tools. If you add a new tool that starts a print, search for "adapter.start_print" and ensure every call site has a preceding `preflight_check()`.

### Bambu `cancelling` should map to CANCELLING not BUSY
The Bambu adapter mapped `"cancelling"` gcode_state to `PrinterStatus.BUSY` instead of `PrinterStatus.CANCELLING`. Since OctoPrint correctly maps to `CANCELLING`, agents checking for the cancel state got inconsistent behavior across adapters. Always check that new state values map to the most specific enum variant available.

### REST API tier filtering must happen at both listing AND execution
The REST API `_list_tool_schemas()` accepted a `tier` parameter but never used it — all tools were returned regardless. Worse, the tool execution endpoint had no tier check at all. Tier filtering must happen at both the discovery layer (what tools the client sees) AND the execution layer (what tools the client can call). Otherwise tier restrictions are purely cosmetic.

### Use timing-safe comparison for auth tokens
Bearer token comparison in REST API used `!=` which is vulnerable to timing side-channel attacks. Always use `hmac.compare_digest()` for secret/token comparisons. This is a one-line fix that prevents byte-by-byte brute-force attacks.

### Bambu A-series uses implicit FTPS (port 990), not STARTTLS
A1/A1 mini requires implicit TLS on port 990 — the socket must be wrapped in TLS immediately on connect, before the FTP greeting. Standard `ftplib.FTP_TLS` uses explicit STARTTLS (connect plain, then upgrade). Requires a custom `_ImplicitFTP_TLS` subclass that wraps the socket in `connect()` and reuses the TLS session on data channels via `ntransfercmd()`.

### Never auto-print generated or unverified models
3D printers are delicate hardware. Misconfigured or malformed models (especially AI-generated ones) can cause physical damage — jammed nozzles, broken beds, stripped gears. Default to uploading only, require explicit `start_print` call. Provide opt-in toggles (`KILN_AUTO_PRINT_MARKETPLACE`, `KILN_AUTO_PRINT_GENERATED`) rather than opt-out. Surface these settings early in setup so users make a conscious decision.

### Print confirmation requires MQTT polling, not just command success
Sending a print command to Bambu via MQTT succeeds even if the printer doesn't actually start (e.g., wrong file path, lid open). Must poll `gcode_state` via MQTT to confirm the printer transitions to an active state. Without this, `start_print()` returns success while the printer sits idle.

### Auto-recorded outcomes must never overwrite agent-curated data
The scheduler auto-records outcomes on job completion/failure to grow the learning DB passively. Critical design: always check `get_print_outcome(job_id)` before saving — if an agent already recorded a curated outcome (with quality_grade, failure_mode, settings), the auto-recorded version (which lacks these) must not overwrite it. Set `agent_id="scheduler"` to distinguish auto vs curated data. The entire auto-record path must be wrapped in try/except — a persistence failure must never crash the scheduler.

### Preflight advisory checks must never block prints
Learning-database-driven warnings in `preflight_check()` must always set `"passed": True`. If outcome data says a material has 0% success rate on a printer, that's valuable information for the agent — but the decision to proceed must remain with the agent. Mark advisory checks with `"advisory": True` so agents/UIs can distinguish warnings from blocking failures. Also: wrap the entire learning query in try/except so a DB error doesn't break preflight for printers without outcome history.

### Bambu A1 Combo uses `/model/` for FTPS storage, not `/sdcard/`
The X1C and P1 series use `/sdcard/` as the FTPS root for file uploads. The A1 series uses `/model/`. CWD to `/sdcard/` returns 550 on A1. The Bambu adapter must detect the printer model and use the correct path. When listing files, `/model/` is the correct root on A1/A1 mini.

### Bambu printers ship with preloaded sample 3MF files — don't assume all files are user prints
Files on a Bambu printer's storage are NOT all user prints. Bambu ships printers with preloaded sample files using the naming pattern `"Name by Creator.gcode.3mf"` (e.g., "Panda by Flexi Factory.gcode.3mf", "3DBenchy by Creative Tool.gcode.3mf"). When reporting print history or file listings, distinguish preloaded samples from user-uploaded files. The naming convention is the key signal.

### Bambu printers require Developer Mode for third-party MQTT print commands
Bambu firmware (01.08.03.00+) includes authorization/authentication that rejects print commands from non-Bambu-Studio sources. Error code `84033543` (0x05024007) = "MQTT Command verification failed." Fix: enable **Developer Mode** on the printer (requires LAN Only Mode first). `kiln auth` and `kiln doctor` must check for this and guide users through enabling it during initial Bambu setup — don't let users discover this after hours of debugging.

### Python 3.14 breaks FTPS data channel TLS with Bambu printers
Python 3.14's stricter `ssl` module rejects empty `server_hostname` in `wrap_socket()`, which `ftplib.FTP_TLS.ntransfercmd()` passes for data channels. Fix: subclass `FTP_TLS` and override `ntransfercmd()` to pass `server_hostname=self.host`. The data channel TLS `unwrap()` also times out on Bambu firmware — catch `TimeoutError` and ignore it; the file transfer completes before the timeout.

### Bambu 3MF files require full metadata structure — not just gcode in a zip
A Bambu-compatible 3MF needs: `Metadata/plate_1.gcode`, `Metadata/plate_1.gcode.md5`, `Metadata/plate_1.json`, `Metadata/slice_info.config`, `Metadata/model_settings.config`, `Metadata/machine_settings_1.config`, `Metadata/filament_settings_1.config`, `Metadata/project_settings.config`, `3D/3dmodel.model`, `[Content_Types].xml`, `_rels/.rels`. Just wrapping gcode in a zip with only `Metadata/plate_1.gcode` is insufficient. Best approach: clone a known-working 3MF from the printer and swap the gcode + update the MD5.

### Bambu MQTT print commands accepted ≠ print actually starts
The `project_file` command can return `err_code: 0` but the printer may still show an HMS error and fail to start. Monitor `gcode_state` — if it goes IDLE → FAILED → IDLE, the print was rejected during execution, not at command validation. Causes include: SD card write failures during pre-flight (logging, calibration data), incompatible gcode content, or missing firmware-specific gcode headers.

### Bambu A1 stock SD cards are unreliable — guide users to replace
The stock SanDisk Edge 32GB card shipped with A1 printers is known to fail with "microSD card read/write exception" (HMS 0500-C010). Files upload and verify fine via FTPS, but firmware-level writes during print startup fail. Touchscreen-initiated prints may work because they skip SD write pre-flight checks that MQTT-triggered prints require. `kiln doctor` should check SD card health and recommend replacement with SanDisk Ultra 32GB if errors are detected.

### Bambu FTPS format wipes /model/ directory — must recreate
Formatting the SD card from the printer's touchscreen wipes everything including the `/model/` directory. After format, FTPS CWD to `/model/` returns 550. Must `MKD /model` before uploading files. Kiln's upload flow should handle this automatically.

### Bambu `gcode_line` command: works for individual commands, not full prints
The `gcode_line` MQTT command successfully executes homing (G28) and temperature commands (M104/M109/M140/M190), but the firmware blocks movement/extrusion commands when the printer is not in an active print job. Cannot stream an entire print via gcode_line — it's for manual control only.

### Bambu MQTT print URL: use `file:///sdcard/model/` not `ftp:///model/`
The MQTT `project_file` command's `url` field determines how the firmware accesses the 3MF. Using `ftp:///model/filename.3mf` causes the firmware to try to fetch from its own FTP server, which triggers HMS 0500-C010 "MicroSD Card read/write exception" on A1 printers — even though the SD card is perfectly fine and FTPS uploads/reads work. The correct URL for files already on the SD card is `file:///sdcard/model/filename.3mf`. This makes the firmware read directly from the filesystem (like the touchscreen does) instead of routing through FTP. This was the root cause of persistent "SD card errors" that appeared with multiple SD cards and even in Bambu Studio.

### Bambu 3MF must reference the correct printer model in metadata
A 3MF cloned from a preloaded file may reference a different printer (e.g., "Bambu Lab N1" or "A1 mini" instead of "Bambu Lab A1"). The `machine_settings_1.config` must have the correct `printer_model`, `printer_variant`, and `printable_area`/`printable_height` for the target printer. Nozzle diameter mismatches cause Bambu Handy/Studio to block the print. The `machine_start_gcode` and `machine_end_gcode` are machine-specific and must come from the correct profile templates (e.g., "Bambu Lab A1 0.4 nozzle template machine_start_gcode.json" from BambuStudio's bundled profiles).

### Bambu access code regenerates when LAN Only Mode is toggled
Toggling LAN Only Mode off and back on regenerates the access code. FTPS login returns 530, MQTT connects but commands fail. `kiln doctor` should detect auth failures and prompt users to re-check their access code. The Kiln config must be updated whenever this happens.

### Bambu Studio cannot view printer storage in LAN Only Mode
Bambu Studio's "Storage" tab doesn't work when the printer is in LAN Only Mode. The app connects and shows status but can't browse files. Bambu Handy (mobile) can still see files and interact with the printer in LAN Only Mode. This is relevant for troubleshooting — don't assume Bambu Studio's inability to see storage means the SD card is broken.

### Bambu gcode requires HEADER_BLOCK metadata for progress tracking
PrusaSlicer gcode works for basic printing but the A1 firmware shows 0% progress and 0h0m time estimate without Bambu-specific metadata. The firmware expects a `;HEADER_BLOCK_START` / `;HEADER_BLOCK_END` section near the top of the gcode containing `; total layer number: N` and `; total estimated time: S` (in seconds). Without this, the printer may enter RUNNING state and heat up but show no progress and potentially not extrude. When using non-BambuStudio slicers, always inject this header block before packaging into 3MF.

### Bambu gcode temperature commands must NOT be stripped
When building 3MF from PrusaSlicer gcode, ensure M104/M109 (nozzle) and M140/M190 (bed) commands are preserved. If gcode is processed/cleaned and these are stripped, the printer enters PREPARE state but never heats — nozzle target stays at 0°C. Always verify temperature commands exist in the final gcode before packaging.

### PrusaSlicer gcode with floating geometry causes PREPARE hang on Bambu
If PrusaSlicer warns about "Floating object part" or "Floating bridge anchors," the resulting gcode may cause the Bambu A1 to enter PREPARE state and never start printing. The printer goes through homing and bed leveling but never starts extruding. Ensure 3D models have solid contact with the build plate or enable supports.

## PrusaSlicer Speed Settings for Bambu A1 (2026-03-04)

**Problem:** PrusaSlicer defaults (60mm/s) produce 10+ hour print time estimates for models that BambuStudio would estimate at 2-3 hours on the A1.

**Fix:** When slicing for A1 with PrusaSlicer CLI, override speeds to match A1 capabilities:
- `--perimeter-speed 200` (A1 does 200mm/s outer walls)
- `--external-perimeter-speed 150`
- `--infill-speed 250`
- `--solid-infill-speed 200`
- `--top-solid-infill-speed 150`
- `--travel-speed 400` (A1 can do 500mm/s travel)
- `--first-layer-speed 50`
- `--max-print-speed 300`

**Note:** Even with fast speeds, PrusaSlicer time estimates are pessimistic vs actual A1 print time because PrusaSlicer doesn't account for A1's 10,000mm/s² acceleration capability. Actual prints run 30-50% faster than PrusaSlicer estimates on A1.

## BambuStudio CLI Slicing Bug (2026-03-04)

**Problem:** BambuStudio CLI v02.05.00.66 `--slice --export-3mf` reports "total N models, 0 objects" for ALL inputs (STL, 3MF). Models load but never get assigned to plates. Affects both binary/ASCII STL and proper 3MF files.

**Workaround:** Use PrusaSlicer CLI for slicing, then package gcode into a Bambu 3MF with proper metadata (`Metadata/slice_info.config`, `Metadata/project_settings.config`). Replace PrusaSlicer start/end gcode with resolved BambuStudio A1 official start/end gcode templates.

## Bambu 3MF Metadata Structure (2026-03-04)

**Problem:** Bambu A1 firmware requires `Metadata/slice_info.config` in the 3MF for layer tracking. Without it, display shows 0/0 layers and the printer goes through init (home, level, heat) but never starts extruding filament.

**Required 3MF structure:**
```
[Content_Types].xml
_rels/.rels
3D/3dmodel.model
Metadata/plate_1.gcode          ← actual gcode
Metadata/slice_info.config      ← KEY: prediction, weight, filament info
Metadata/project_settings.config ← printer model, settings
Metadata/model_settings.config  ← object names
```

**slice_info.config format:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<config>
  <header>
    <header_item key="X-BBL-Client-Type" value="slicer"/>
    <header_item key="X-BBL-Client-Version" value="02.05.00.66"/>
  </header>
  <plate>
    <metadata key="index" value="1"/>
    <metadata key="prediction" value="SECONDS"/>
    <metadata key="weight" value="GRAMS"/>
    <metadata key="outside" value="0"/>
    <metadata key="support_used" value="0"/>
    <metadata key="label_object_enabled" value="0"/>
    <metadata key="timelapse_type" value="0"/>
    <filament id="1" type="PLA" color="#FFFFFF" used_m="METERS" used_g="GRAMS"/>
  </plate>
</config>
```

**Key insight:** T1000 in start gcode IS expected for A1 firmware (it's in the official BambuStudio A1 start gcode template). The 0/0 layer bug is purely a metadata issue.

## MakerWorld Cloudflare Protection (2026-03-04)

**Problem:** MakerWorld API (`makerworld.com`) is behind Cloudflare challenge pages. All programmatic access (curl, WebFetch, Python requests) returns 403 Cloudflare challenge. Cannot download models or query API directly.

**Impact:** Kiln cannot offer true MakerWorld integration without a Cloudflare bypass strategy (browser automation, session tokens, or official API partnership).

## M82/M83 Extrusion Mode Mismatch — Bambu A1 + PrusaSlicer (2026-03-04)

**Problem:** Bambu A1 start gcode sets `M83` (relative extrusion) at end of init sequence. PrusaSlicer generates gcode body with `M82` (absolute extrusion). Without explicitly switching modes, firmware interprets PrusaSlicer's absolute E values as relative — each move tries to push ~2mm of filament instead of incremental 0.06mm. Clog detection triggers and silently stops extrusion while head keeps moving.

**Symptom:** Printer goes through full init (home, level, heat, flush, wipe), nozzle reaches print temp (220°C), head moves in correct print paths, but ZERO filament extrudes. Display shows 0% progress.

**Fix:** Insert `M82` + `G92 E0` between the end of the Bambu start gcode and the start of the PrusaSlicer body gcode:
```
G29.4              ← end of Bambu start gcode
M82                ← switch to absolute extrusion (PrusaSlicer mode)
G92 E0             ← reset extruder position
;LAYER_CHANGE      ← start of PrusaSlicer body
```

**Key Rule:** When combining start gcode from one slicer with body gcode from another, ALWAYS verify the extrusion mode (M82 vs M83) matches at the transition point. Bambu firmware uses M83, PrusaSlicer defaults to M82.

## Bambu Firmware Progress Tracking — M73 and Layer Comments (2026-03-04)

**Problem:** Bambu firmware displays 0/0 steps (layers) and 0% progress when gcode lacks specific markers.

**Fix:** Add these to the gcode:
1. Header: `; total layer count : 244` — firmware reads this for total layer display
2. Per-layer: `M73 P{percent} R{remaining_minutes}` after each `;LAYER_CHANGE` — firmware updates progress bar and remaining time
3. `Metadata/slice_info.config` with `<metadata key="prediction" value="SECONDS"/>` — provides time estimate

Without these, the printer still prints correctly but shows no progress/layer info on the display.

## Filament Prime Required After Stop Commands — Bambu A1 (2026-03-04)

**Problem:** After stopping a print on Bambu A1, the end gcode runs the "pull back filament to AMS" sequence (`T255`, `M620 S255`/`M621 S255`). Even without AMS, this partially retracts filament from the hotend. After multiple stop commands, the filament tip is above the melt zone. Subsequent prints move the head correctly but extrude no filament.

**Symptom:** Printhead moves in correct paths, nozzle at correct temperature, progress increases, but zero filament deposits on the bed. Looks like it's "printing air."

**Fix:** Add a filament prime sequence after the nozzle heats up and BEFORE the first layer:
```gcode
G1 Z5 F3000        ; lift nozzle for prime
G1 X128 Y128 F6000 ; move to center of bed
M83                 ; relative extrusion
G1 E30 F300         ; push 30mm filament
G1 E20 F200         ; push 20mm more slowly
G1 E10 F100         ; final 10mm very slow to ensure flow
G1 E-1 F300         ; small retract to prevent ooze
G92 E0              ; reset E
G1 Z0.3 F3000       ; drop to first layer height
```

**Key Rule:** BambuStudio's official start gcode pushes ~65mm of filament (flush + prime). Any custom start gcode for Bambu MUST include a filament prime of at least 30mm, especially after stop commands. Without it, the printer will "print air."

## Bambu A1 Camera RTSP Access (2026-03-04)

**Problem:** A1 Combo camera RTSP stream on port 322 returns "Connection refused." Port 6000 times out with TLS error.

**Status:** Unresolved. May need to be enabled via BambuStudio or printer settings. Format should be `rtsps://bblp:{access_code}@{ip}:322/streaming/live/1`. Adding to backlog for investigation.

## Bambu A1 Developer Mode + LAN Only Mode Can Require Re-Toggling After Power Cycle (2026-03-04)

**Problem:** MQTT print commands suddenly rejected with HMS 0500-0500-0001-0007 "MQTT Command verification failed" after printer reboot, even though Developer Mode and LAN Only Mode appeared to still be on.

**Root cause:** After a power cycle, LAN Only Mode and Developer Mode may visually show as "on" but the MQTT auth state can be stale. Toggling LAN Only Mode off and back on, then re-enabling Developer Mode, forces the firmware to regenerate the MQTT auth context and a fresh access code. Without Developer Mode active, the firmware requires cryptographically signed MQTT commands (using Bambu Connect's X.509 certificate), which third-party clients cannot provide.

**Fix:** If MQTT commands fail after a printer power cycle:
1. Toggle LAN Only Mode OFF then back ON
2. Re-enable Developer Mode
3. Note the NEW access code (it regenerates on LAN Only toggle)
4. Update the access code in Kiln config / env var before retrying

**Note:** The access code regenerates whenever LAN Only Mode is toggled. Always re-read the access code from the printer's LAN settings screen after toggling.

## Bambu A1 Proprietary Start Gcode — Critical Commands for Extrusion (2026-03-04)

**Problem:** PrusaSlicer-generated gcode uploads and "prints" on the A1 — head moves, nozzle heats, progress tracks — but **no filament ever extrudes**. Tested with M82, M83, filament priming, simple start gcode, Bambu start gcode. None worked.

**Root cause:** The Bambu A1 firmware requires a specific proprietary initialization sequence before the extruder motor will respond to E commands. Without these, G1 E commands are silently ignored. The critical sequence from BambuStudio-resolved gcode:

1. `M620 M` — **Enable extruder motor remapping** (required for AMS routing)
2. `M620 S0A` — Switch to AMS slot 0 (tells firmware which filament source)
3. `T0` — Select physical extruder 0 (loads filament from AMS to hotend)
4. `M621 S0A` — Confirm AMS material switch completed
5. Flush sequence: `G1 E50 F200` at 250°C — pushes old material out, primes nozzle
6. `M983`/`M984` — Dynamic extrusion calibration (cali paint test line)
7. `M975 S1` — Enable mech mode suppression
8. `M1007 S1` — Enable mass estimation (may gate E-step execution)
9. `T1000` — Select Bambu virtual tool (used with M83 relative extrusion)
10. `M412 S1` — Enable filament runout detection
11. `M620.3 W1` — Enable filament tangle detection
12. `M981 S1 P20000` — Enable spaghetti detector
13. `M991 S0 P0` — Layer change notification (must appear at EVERY layer change)
14. `G29.4` — Unknown but appears right before print body

**Solution:** Use the complete BambuStudio-resolved start/end gcode (~600 lines start, ~140 lines end) as a wrapper around PrusaSlicer print body. The start gcode contains concrete temperature values for PLA on A1 (140°C preheat → 250°C flush → 220°C print, 65°C bed).

**Key architectural insight:** You CANNOT simplify the Bambu start gcode. Minimal start sequences (G28 + M104 + M140) will never work because the extruder motor is gated behind the M620/T0/M621 AMS initialization sequence. Even priming (G1 E60) won't work because the motor literally doesn't turn without M620 M.

## Bambu A1 Print Body Requirements — Layer Tracking (2026-03-04)

**Problem:** PrusaSlicer gcode plays correctly but the Bambu firmware shows 0/0 layers.

**Solution:** Each layer change in the print body must include these Bambu-specific commands:
```gcode
; layer num/total_layer_count: N/TOTAL
; update layer progress
M73 LN            ; layer number for firmware display
M991 S0 P0        ; notify firmware of layer change
M73 P<pct> R<min> ; progress percentage and remaining minutes
```

PrusaSlicer uses `;LAYER_CHANGE` as its layer marker — inject the Bambu commands after each one.

## Bambu MQTT ams_mapping Must Match Filament Slot Count (2026-03-04)

**Problem:** Sending `"ams_mapping":[0]` for a BambuStudio 3MF that has 3 filament slots configured causes an "SD card error" on the printer.

**Solution:** The `ams_mapping` array in the MQTT print command must match the number of filament slots in the 3MF's slice_info.config. For a 3-slot project using only slot 0: `"ams_mapping":[0,0,0]`. For a single-filament PrusaSlicer project: `"ams_mapping":[0]`.

## PrusaSlicer Needs Brim/Raft for Small or Lattice Models on Bambu A1 (2026-03-04)

**Problem:** 60% scale airless tennis ball (lattice/honeycomb structure) started printing correctly but detached from the bed mid-print, creating a spaghetti mess. Benchy printed perfectly the day before on the same printer.

**Root cause:** The airless tennis ball has tiny lattice contact points at its base. At 60% scale, those contact points are even smaller, providing insufficient bed adhesion on the textured PEI plate. BambuStudio auto-adds adhesion helpers (brim/raft) for models with small contact areas, but PrusaSlicer with empty start-gcode and default settings does not.

**Fix:** When slicing with PrusaSlicer for Bambu printers, add `--brim-width 5` (or `--skirt-distance 0 --skirts 3` for a brim-like effect) for models with:
- Small base contact area (lattice, organic shapes, spheres)
- Scaled-down models (contact area shrinks quadratically with scale)
- Tall/narrow prints with high center of gravity

BambuStudio's auto-brim logic should be replicated in Kiln's slicer pipeline for Bambu targets.

## Bambu Multi-Plate 3MF — Print Plate 2+ via MQTT (2026-03-05)

**Problem:** BambuStudio exports multi-plate 3MF files (e.g., a 2-color bucket with plate 1 = white frame, plate 2 = gray mesh). Kiln's `print` CLI command always prints plate 1. There's no CLI flag to select a different plate. Exporting plate 2 as a standalone 3MF from BambuStudio causes firmware error `0500-4003-010800` ("unable to parse file"). Uploading raw extracted gcode fails because: (a) `start_print()` sends `/sdcard/{name}` but A1 stores files at `/model/`, and (b) the `gcode_file` MQTT command doesn't support `use_ams`/`ams_mapping` parameters.

**Solution:** Upload the **original multi-plate 3MF** (containing all plates) and start print with `plate_number=2`:
```python
adapter.upload_file('original_multiplate.gcode.3mf')
adapter.start_print(
    'original_multiplate.gcode.3mf',
    plate_number=2,
    use_ams=True,
    ams_mapping=[0, 1],  # map to actual AMS slots
)
```
The MQTT `project_file` command uses `"param": "Metadata/plate_2.gcode"` to select the plate's gcode from inside the 3MF. The firmware thumbnail/preview on the LCD may still show plate 1's image — this is cosmetic. Verify the correct plate by checking `total_layers` (plate 1 had 184, plate 2 had 270).

**Bugs to fix in Kiln:**
1. **CLI needs `--plate` flag** — `kiln print --plate 2 file.3mf` should select the plate
2. **CLI needs `--use-ams` and `--ams-mapping` flags** — multi-filament prints need AMS slot control from the CLI
3. **Raw gcode path wrong on A1** — `start_print()` line 1390 sends `/sdcard/{name}` but A1 uses `/model/`. Should use `_detect_storage_path()` result
4. **`gcode_file` command lacks AMS params** — raw gcode prints on multi-filament setups need `use_ams`/`ams_mapping` in the MQTT payload
5. **Auto-detect filament count from gcode header** — parse `; filament: N` and `; filament_density:` lines to auto-set `ams_mapping` size instead of defaulting to `[0]`

## Bambu AMS Color Mismatch Warning (2026-03-05)

**Problem:** User's gcode specified gray filament (`#808080`) in slot 2, but AMS actually had black filament loaded in that slot. Kiln sent the print without any warning. The user expected gray but got black.

**Solution:** Before starting a multi-filament print, Kiln should:
1. Read the loaded AMS filament colors from MQTT status (`ams.ams[N].tray[M].tray_color`)
2. Compare against the 3MF's `plate_N.json` → `filament_colors` array
3. If colors don't match, warn the user: *"Plate 2 expects gray (#808080) in slot 2, but AMS slot 2 has black (#000000). Continue anyway?"*
4. Allow override (the user may not care about exact color), but surface the mismatch so they can make an informed choice

This is especially important for agents — an AI agent told to "print in gray" should notice the AMS has black and flag it before wasting filament/time.

## Bambu Stale Access Code After Power Cycle (2026-03-05)

**Problem:** After the printer is turned off and back on, ALL MQTT print commands fail with `err_code: 84033543` (hex `0502-4007` — "MQTT command verification failed"). Even known-working files that printed successfully minutes ago fail with the same error. The access code may LOOK the same on the printer screen, but the MQTT auth state is stale.

**Root cause:** Bambu firmware resets its internal MQTT auth context on power cycle. Even though Developer Mode and LAN Only Mode show as "enabled" on the touchscreen, the auth tokens are invalidated. The old access code is displayed but no longer valid for third-party MQTT commands.

**Fix for the user:** On the printer touchscreen: Settings → Network → turn LAN Only Mode OFF then ON → toggle Developer Mode OFF then ON → copy the NEW access code (it may be the same string or different, but the internal auth context is now fresh). Update Kiln config with the new code.

**Fix in Kiln (implemented):** `_wait_for_print_start()` now checks the `print_error` MQTT field during polling. If the printer reports error 84033543 while still in IDLE state, Kiln immediately returns a failure with the exact fix instructions instead of timing out with a generic "didn't transition" message. Unknown error codes are also surfaced with their hex value for wiki lookup.

**Key rule:** After any printer restart, assume the access code is stale until proven otherwise. Kiln should eventually detect this proactively (e.g., via a lightweight auth check before attempting a print command).

## Bambu 3MF filament_ids vs AMS Slot Count (2026-03-05)

**Problem:** BambuStudio sliced a single-filament model but wrote `filament_ids: [7]` in the 3MF metadata — meaning the 8th filament profile in the slicer project. The user's A1 Combo AMS only has 4 slots (indices 0-3). While `filament_ids` is a slicer-internal index (NOT a physical AMS slot), it signals a mismatch between the slicer project configuration and the printer's actual hardware.

**Fix in Kiln (implemented):** `_validate_3mf_filament_ids()` reads `filament_ids` from the 3MF plate metadata, queries the AMS tray count via MQTT, and blocks the print with a clear error if any filament_id index exceeds the AMS capacity. The error message tells the user to re-slice with only their installed filaments or provide explicit `--ams-mapping`.

**Key rule:** Validate 3MF metadata against actual printer hardware BEFORE sending the print command. Catching mismatches early saves the user from cryptic firmware errors or wasted prints.

## MQTT Telemetry Cannot Detect Print Failures — Use the Camera (2026-03-05)

**Problem:** Print completely failed (first-layer adhesion failure, printing in air from early on) but MQTT telemetry reported everything as normal — temperatures on target, layers progressing, completion % increasing, `print_error: 0`. Monitoring only the numbers led to reporting "printing smoothly" while the actual print was garbage.

**Root cause:** Bambu firmware tracks progress by gcode line execution, not by actual material deposition. If the print detaches from the bed, the nozzle keeps moving and the firmware keeps counting layers/progress as if nothing is wrong. There is no sensor feedback for adhesion failure, under-extrusion, or spaghetti.

**Key rule:** When monitoring a print, ALWAYS take periodic `kiln snapshot` camera images and visually inspect them — don't just watch the numbers. Telemetry alone gives a false sense of confidence. Check the camera at minimum: (1) after first few layers to confirm adhesion, (2) at ~25% as a mid-early check, (3) periodically every 15-20% thereafter. A 2-second snapshot is worth more than perfect temperature readings.

## Bambu MQTT Single-Client Limitation — Connection Reset by Peer (2026-03-05)

**Problem:** MQTT connection to Bambu printer fails with `[Errno 54] Connection reset by peer` during TLS handshake. TCP connects fine (port 8883 open), RTSPS camera works (port 322), FTPS works (port 990), but MQTT specifically gets RST at the TLS level.

**Root cause:** Bambu printers only allow **one LAN MQTT client** at a time. If BambuStudio, Bambu Handy, or a previous Kiln session already holds the MQTT connection, new clients get their TLS handshake reset. This also happens after calibration commands that crash/restart the MQTT service.

**Diagnosis checklist:**
1. `nc -z -w 3 <host> 8883` → succeeds (port open) but TLS wrapping fails → single-client lock
2. Camera snapshot still works → printer is fine, MQTT specifically is blocked
3. Check if BambuStudio is connected (it auto-connects on launch)

**Fix:** Close BambuStudio / Bambu Handy, or power-cycle the printer to reset MQTT. Kiln should detect this pattern and surface a clear error: "Another MQTT client may be connected. Close BambuStudio and retry."

**Kiln improvement needed:** Add specific error handling in `_ensure_mqtt()` for `ConnectionResetError` / errno 54 with a user-friendly message about single-client limitation.

## Bambu A1 Error 0300 8014 — Nozzle Clumping Detection, NOT Lidar (2026-03-05)

**Problem:** Print repeatedly fails with HMS error `0300 8014` ("nozzle is covered or build plate installed incorrectly") on a specific model. Setting `layer_inspect=False` in the MQTT `project_file` command does NOT fix it.

**Root cause:** Error 0300 8014 is triggered by the **nozzle clumping detection** system — completely separate from the lidar first-layer inspection. The A1 has THREE independent detection systems:

1. **`layer_inspect`** (MQTT `project_file` param) → Lidar visual first-layer scan. Error codes: `0C00-0300-xxxx`.
2. **`nozzle_blob_detect`** (MQTT `print_option` command) → General nozzle blob detection. Error codes: `0300-1A00-xxxx`.
3. **Nozzle clumping detection by probing** → Uses eddy current/force sensor to physically probe the nozzle at layers 4, 11, and 20. This is **hardcoded into the timelapse G-code** in BambuStudio. Error codes: `0300-8014`.

**How clumping detection works on A1:**
- At layers 4, 11, 20, the toolhead moves to the back of the build plate
- Nozzle lowers outside the heat bed and performs a probing motion
- Eddy current sensor checks if nozzle has a filament blob
- If detected → pauses print with 0300 8014

**Why specific models trigger it:**
- Model geometry near the probe zone
- Thin first-layer features that leave strands near the detection area
- Certain purge patterns that leave residual filament in the probe path
- Third-party plate aligners blocking the probe motion (common cause)

**How to ACTUALLY disable it (4 methods, use all for belt-and-suspenders):**

1. **MQTT `print_option` command** (before or during print):
```json
{"print": {"sequence_id": "0", "command": "print_option", "nozzle_blob_detect": false}}
```

2. **MQTT `xcam_control_set`** command:
```json
{"xcam": {"sequence_id": "0", "command": "xcam_control_set", "module_name": "clump_detector", "control": false, "print_halt": false}}
```

3. **Slicer G-code edit:** In BambuStudio printer settings → Machine G-code → Timelapse section, change `{if layer_num == 2}` to `{if layer_num == 20000}` (or delete the entire timelapse gcode section).

4. **Printer touchscreen:** Settings → Printing Options → disable nozzle clumping detection (unreliable — firmware sometimes ignores this setting).

**Key lesson:** `layer_inspect` and `nozzle_blob_detect` / clump detection are DIFFERENT systems. When diagnosing print failures, check the error code prefix to determine which system triggered:
- `0C00` prefix → lidar/xcam → `layer_inspect=False` fixes it
- `0300-8014` → nozzle clumping → `nozzle_blob_detect=False` + xcam clump_detector off
- `0300-1A00` → nozzle wrapped in filament → physical nozzle cleaning needed

**Kiln improvement (DONE):** Added `nozzle_clog_detect` parameter to `start_print()`, `--no-nozzle-check` CLI flag, and MCP tool parameter. `_disable_nozzle_detection()` sends both `print_option` and `xcam_control_set` commands before the print command. Tested with 3 unit tests.

## Bambu FTPS LIST Returns 550 on A1 — Use NLST Instead (2026-03-05)

**Problem:** `list_files()` fails with `ftplib.error_perm: 550` when using `LIST /sdcard/` or `LIST /model/` on the A1 Combo. Upload (`STOR`) works fine through the same connection. The 550 occurs at the data channel command level, not during the TLS handshake.

**Root cause:** The Bambu A1 FTP server's `LIST` implementation is broken or unsupported for certain paths. `NLST` (name list) works where `LIST` (detailed list) doesn't.

**Fix needed in Kiln:** `_list_via_list()` in bambu.py should fall back to `NLST` when `LIST` returns 550. NLST returns just filenames (no size/date metadata), but that's sufficient for most operations.

## Bambu FTPS Single-Client Limitation — Same as MQTT (2026-03-05)

**Problem:** FTPS upload to Bambu A1 times out on TLS handshake when BambuStudio is open. After closing BambuStudio, FTPS connects and uploads immediately. Same symptom as the MQTT single-client limitation.

**Root cause:** Bambu printers only allow one FTPS client AND one MQTT client at a time. BambuStudio holds both connections while open. FTPS timeout manifests at the TLS handshake level — TCP port 990 is "open" (accepts SYN) but the TLS negotiation hangs because the server won't accept a second concurrent session.

**Also:** A stale/hanging FTPS connection (e.g., from a killed Python process) blocks subsequent uploads. Always ensure background FTP processes are killed before retrying.

**Fix needed in Kiln:** Detect TLS handshake timeout on FTPS and surface a clear error: "FTPS connection timed out — BambuStudio or another client may be holding the connection. Close it and retry."

## Layer Delamination on Thin-Walled Prints — Slicer Fix (2026-03-05)

**Problem:** Grip extension model printed with default BambuStudio settings (2 wall loops, 200mm/s outer wall, 215°C nozzle) had vertical walls delaminate mid-print. Base adhesion was perfect. Audible cracking during print.

**Root cause:** Thin vertical walls (2 perimeters) cool too fast between layers on the A1's aggressive cooling + high speed. Poor inter-layer bonding causes the layers to separate under internal stress.

**Slicer fix:**
- Wall loops: 2 → 4 (thicker walls retain heat longer)
- Nozzle temp: 215 → 220°C (hotter = better layer fusion)
- Outer wall speed: 200 → 150 mm/s (slower = more heat per layer)
- MQTT Silent speed mode (level 1) as additional safety

**Key insight:** Wall loops DON'T change the outer dimensions — they add perimeters inward, eating into infill space. Safe to increase without affecting fitment.

### Print failure diagnosis: fix orientation before tweaking parameters

**Problem:** Grip extension failed at 70% due to wobble on a tall, narrow part. AI response was to add wider brim, lower acceleration, reduce speed — all parameter band-aids.

**Actual fix:** Lay the part flat (rotate 90° on X/Y). Tall + tiny footprint is inherently unstable. No amount of brim or speed reduction fixes bad orientation. Laying it flat gives massive bed contact, eliminates wobble, removes the need for supports, and prints faster.

**Rule:** When a print fails due to mechanical instability (wobble, detachment, layer shift on tall parts), **always consider reorientation first**. Parameter tweaks (brim, accel, speed) are secondary. Don't reach for slicer overrides when the geometry is fighting gravity.

**Bias to watch for:** Don't favor tool-based solutions just because the tools exist. The simplest physical fix beats the cleverest software fix.

## Agent Behavior Across Context Rotations

### Always check for existing MCP tools before writing ad-hoc scripts

**Problem:** During a long print monitoring session, context window rotated multiple times. Each time, the agent lost knowledge that `monitor_print()` existed in `server.py` and reinvented the monitoring format with ad-hoc Python scripts — producing inconsistent output and wasting effort.

**Root cause:** Existing tools aren't discoverable across context resets. CLAUDE.md had reference patterns for _building_ tools but no inventory of _existing_ tools to use. The agent's default behavior was to write code rather than grep for existing tools first.

**Fix:** Added "Use Existing Tools — Never Reinvent" table to CLAUDE.md with the most common operations and their corresponding MCP tools. This table survives context rotations because CLAUDE.md is loaded at session start.

**Rule:** Before writing ANY printer interaction script, run `grep "^def \|^async def " src/kiln/server.py | grep -i "<keyword>"` to check if a tool already exists. If it does, use it. If it doesn't, build it as a proper MCP tool — never ship a one-off script.

### Always grep server.py before declaring a task impossible

**Problem:** User asked to print 2 copies of a pre-sliced `.gcode.3mf`. Agent assumed it was impossible because the file had baked G-code, without checking if Kiln had tools to handle this. Kiln already had `multi_copy_print()` (arranges N copies on plate, slices, prints) and `reslice_with_overrides()` (re-slices 3MF/STL with custom params).

**Root cause:** Agent skipped the mandatory grep step from CLAUDE.md and assumed the pre-sliced file was a dead end. The "Use Existing Tools" table didn't list `multi_copy_print` or `reslice_with_overrides`, so the agent had no reminder they existed.

**Fix:** Added these tools to the CLAUDE.md lookup table. But the real fix is discipline — always run the grep before saying "can't do that."

**Rule:** When a user asks for ANY printer operation and your first instinct is "that's not possible," STOP. Run `grep "^def \|^async def " src/kiln/server.py | grep -i "<keyword>"` with multiple keywords. Kiln has 350+ tools. The answer is almost always "yes, a tool exists."

### Test ad-hoc monitoring scripts before trusting them — and use the camera

**Problem:** User asked to auto-cancel a print at 65%. Agent wrote a bash polling script that parsed `data.progress.completion` from `kiln status --json`, but the actual field path is `data.job.completion`. The script read 0% for 70+ minutes while the print was actually progressing. User had to cancel it manually.

**Compounding failure:** Agent had camera access via `camera_snapshot()` but never used it to visually verify print progress. A single snapshot would have revealed the print was well past 0%. Also, the progress jumping from 16% (known earlier) to 0% for an hour should have been an obvious red flag that the script was broken.

**Fix:** (1) Always test JSON parsing against actual output before deploying a monitoring script — run `kiln status --json | python3 -c "..."` once and verify the value is sane. (2) When monitoring prints, periodically use `camera_snapshot()` as a ground-truth check. (3) If a monitored value contradicts known state (was 16%, now showing 0%), investigate immediately — don't blindly trust the script.

**Rule:** Never deploy a background monitoring script without first verifying it produces correct output on a live run. And always use the camera — it's the most reliable indicator of what's actually happening on the printer.
