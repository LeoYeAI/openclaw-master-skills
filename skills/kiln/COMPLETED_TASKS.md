# Kiln — Completed Tasks

Record of finished features and milestones, newest first.

## 2026-03-09

### v0.3.3 Release — Bambu Adapter Hardening + Test Fixes

**Bambu Adapter Hardening (6 fixes):**
- **MQTT disconnect timeout** — `_safe_stop_client()` prevents `loop_stop()` from hanging indefinitely via daemon thread + configurable timeout
- **FTPS retry with backoff** — `_ftp_connect()` wrapper retries up to 3 times with exponential backoff for transient connection failures (printer waking)
- **Camera snapshot timeout** — Reduced from 15s→5s (JPEG) and 10s→5s (RTSPS) to prevent long hangs
- **AMS pushall on empty cache** — A1/AMS Lite printers now get a `pushall` MQTT command when AMS cache is empty, solving data staleness
- **`update_credentials()` method** — Allows agents to rotate the LAN access code without rebuilding the adapter
- **CLI `report` command** — Cross-brand print monitoring command matching `monitor_print()` MCP tool output format

**Bug Fixes:**
- **AMS dict-wrapper unwrap** — A1/AMS Lite printers nest AMS data in a dict wrapper; unwrap before parsing
- **AMS mapping from filament IDs** — Build `ams_mapping` from 3MF `filament_ids` for non-contiguous ID support
- **`test_material_show_empty`** — Mock `_get_adapter_from_ctx` to hit the correct "No materials loaded" branch
- **REST API test env leakage** — `load_dotenv()` in `create_app()` loaded `KILN_API_AUTH_TOKEN` from `.env`, contaminating no-auth test fixtures

**Marketplace:**
- `upload_model` added to Thingiverse + MyMiniFactory adapters

**Infrastructure:**
- `kiln monitor` — persistent print safety monitoring CLI command
- `kiln material show --live` — live AMS/filament query
- Orientation stability check — warns before printing wobbly parts
- Tool count: 353→358 MCP tools
- Test count: 7,586→7,621

## 2026-03-06

### monitor_print + multi_copy_print MCP tools

**New Features:**
- **`monitor_print`** — Standardized print status report with progress, temps, speed, camera snapshot, and auto-generated health comments. Works across all printer brands (Bambu, OctoPrint, Moonraker) — gracefully handles None for brand-specific fields (layers, speed profile, chamber temp).
- **`multi_copy_print`** — Arrange N copies on one build plate, slice, and print. PrusaSlicer uses `--duplicate` flag; OrcaSlicer falls back to STL mesh duplication via `duplicate_stl_on_plate()` in auto_orient.py. Looks up bed dimensions from safety profiles when printer_id provided.
- **`duplicate_stl_on_plate()`** — Parse STL, compute bounding box, grid-arrange copies with spacing, write merged binary STL.
- **`extra_args` pipeline param** — `reslice_and_print` now accepts `extra_args: list[str]` passed through to `slice_file()` for slicer CLI flags.
- **Auth scope audit fix** — `async def` parser in `test_auth_scope_audit.py` now detects async MCP tools. Added `monitor_print` + `check_orientation` to READ_ONLY_TOOLS.
- **Tool count 343→345** across README, PROJECT_DOCS, server.json, pyproject.toml, site.

**Testing:** 7476 tests passing, 0 failures. 61 new tests added. Ruff lint clean. CI green on Python 3.10–3.13.

## 2026-02-20

### Dillon's Bug Reports + Generation Pipeline Overhaul

Source: Dillon (Misery) + his agent Clawdene ran a full idea-to-print loop (Valentine heart via Gemini DeepThink → Prusa Mini+). Fixed all reported bugs and implemented every suggested improvement.

**Bug Fixes:**
- **`kiln --version` crash** — `package_name="kiln"` → `"kiln3d"` to match pyproject.toml (`cli/main.py:393`)
- **CLI `--provider` hardcoded to meshy/openscad** — All 4 generation commands now accept `gemini`, `tripo3d`, `stability` via registry-based provider instantiation (`cli/main.py`)
- **Gemini default model deprecated** — `gemini-2.0-flash` → `gemini-2.5-flash` + `KILN_GEMINI_MODEL` env var override (`generation/gemini.py:44`)
- **No self-healing on OpenSCAD compile failure** — Added retry loop (up to 3 attempts) that feeds compiler errors back to Gemini for corrected code (`generation/gemini.py`)

**New Features:**
- **Material-aware slicing** — `kiln slice --material PLA` auto-sets nozzle/bed temperatures in slicer profile overrides. 7 materials supported (`cli/main.py`)
- **Material-aware G-code validation** — `validate_gcode_for_material()` warns when temps are outside material ranges or bed temp is 0 for materials requiring heated bed (`gcode.py`)
- **External camera support** — `kiln snapshot --source URL` or `cmd:ffmpeg ...` for printers without built-in webcams + `KILN_CAMERA_SOURCE` env var (`cli/main.py`)
- **Generate-and-print CLI pipeline** — `kiln generate-and-print "description" --provider gemini --material PLA` runs the full generate → slice → upload pipeline in one command (`cli/main.py`)
- **Print time display** — `kiln status` now shows elapsed time and total estimated time during prints. `kiln files` shows estimated print time per file (`cli/output.py`)

**Testing:** 6,141 tests passing, 0 failures. Ruff lint clean.

## 2026-02-19

### Think → Print → Earn: 12 New Subsystems

Major feature drop adding 12 new subsystems to complete the AI-to-physical pipeline:

**Tier 1 — Generation Pipeline:**
- **Universal Generation Adapter** — `generation/registry.py` with auto-discovery from env vars. Tripo3D (`generation/tripo3d.py`) and Stability AI (`generation/stability.py`) providers following MeshyProvider pattern.
- **Printability Analysis Engine** — `printability.py` with overhang detection, thin wall analysis, bridging assessment, bed adhesion scoring, support estimation, A-F grading.
- **Auto-Orient & Auto-Support** — `auto_orient.py` with 24-candidate rotation scoring, optimal orientation finder, reoriented STL output.
- **Generation Feedback Loop** — `generation_feedback.py` with failed-print-to-improved-prompt pipeline, constraint injection (Meshy 600-char limit aware).

**Tier 2 — Intelligence Network:**
- **Print DNA / Model Fingerprinting** — `print_dna.py` with SHA-256 + geometric signature, 3-tier settings prediction (exact → similar → material default).
- **Community Print Registry** — `community_registry.py` with opt-in crowd-sourced settings, confidence levels, "Waze for 3D printing."
- **Smart Material Routing** — `material_routing.py` with 8 built-in materials, 8 intent mappings, printer capability filtering, budget constraints.

**Tier 3 — Marketplace & Revenue:**
- **Publish-to-Marketplace Pipeline** — `marketplace_publish.py` with print "birth certificate," Kiln attribution watermark on all published models.
- **Revenue Tracking for Creators** — `revenue_tracking.py` with per-model analytics. 2.5% platform fee (configurable via `KILN_PLATFORM_FEE_PCT`) on revenue from models published through Kiln.
- **Print-as-a-Service API** — `print_service.py` with local vs fulfillment quoting, order lifecycle (received → validating → printing → shipping → delivered).

**Tier 4 — Reliability:**
- **Intelligent Failure Recovery** — `failure_recovery.py` with 9 failure types (spaghetti, layer shift, adhesion loss, etc.), automated recovery planning.
- **Multi-Printer Job Splitting** — `job_splitter.py` with round-robin and assembly-based distribution across printer fleets.

**Plugins:** 4 new plugin files (40 MCP tools) auto-discovered by plugin_loader: `printability_tools.py`, `intelligence_tools.py`, `service_tools.py`, `recovery_tools.py`.

**Database:** 8 new tables in persistence.py (print_dna, community_prints, published_models, revenue, print_service_orders, failure_records, split_plans, feedback_loops).

**Tests:** 409 new tests (6,094 total passing). Full whitehat audit completed with fixes for race conditions, input validation, and JSON parsing safety.

### Enterprise Tier — Security Hardening & Remaining Gaps

Comprehensive whitehat security audit + feature gap closure for Enterprise readiness.

**Security hardening (from 58-finding whitehat audit):**
- **SSO SSRF protection** — `_validate_url_no_ssrf()` resolves hostnames and rejects private/reserved IPs (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 127.0.0.0/8, 169.254.0.0/16). `KILN_SSO_ALLOW_LOCALHOST=1` for dev.
- **IDN homograph prevention** — Non-ASCII email domains rejected by default. `KILN_SSO_ALLOW_IDN=1` to override.
- **PKCE flow expiry** — 600s TTL, 100-flow cap, `_cleanup_expired_flows()` to prevent unbounded memory growth.
- **Audit trail hash chain** — SHA-256 chain in `persistence.py`. Each entry hashes `prev_hash|tool|action|session|timestamp`. `verify_audit_log()` validates HMAC + chain integrity. Detects modification AND deletion.
- **Auth disabled-mode safety** — `verify()` returns `scopes={"read","write"}` (not `{"admin"}`) when auth disabled. Prevents accidental privilege escalation.
- **Mutating tools audit** — Security note in `server.py` documenting 29 mutating tools without explicit auth (transport-level only).
- **Env var centralization** — `parse_int_env()`/`parse_float_env()` in `kiln.__init__`. Adopted across events.py, queue.py, recovery.py, craftcloud.py. Import-time env reads converted to call-time in moonraker.py, octoprint.py, rest_api.py.

**Feature gaps closed:**
- **Multi-site fleet grouping** — `PrinterMetadata` dataclass (site, tags, registered_at) in `registry.py`. `list_sites()`, `get_printers_by_site()`, `get_fleet_status_by_site()`, `update_printer_metadata()`. 3 MCP tools: `list_fleet_sites`, `fleet_status_by_site`, `update_printer_site`.
- **Per-project cost tracking** — New `project_costs.py`. `ProjectCostTracker` with project lifecycle + cost logging. Categories: material, printer_time, fulfillment_fee, labor, other. Per-project and per-client summaries. 4 MCP tools: `create_project`, `log_project_cost`, `project_cost_summary`, `client_cost_report`.
- **SSO test coverage** — New `test_sso.py` with 56 tests / 11 classes covering config, OIDC discovery, JWT validation, email domain filtering, role mapping, SAML processing, code exchange, singleton thread safety.
- **External Secrets docs** — DEPLOYMENT.md section for ESO, Sealed Secrets, Vault. Helm values.yaml template. `/proc/environ` security note.

**Files changed/created:** `sso.py`, `auth.py`, `persistence.py`, `server.py`, `registry.py`, `project_costs.py` (new), `test_sso.py` (new), `__init__.py`, `events.py`, `queue.py`, `recovery.py`, `craftcloud.py`, `proxy_server.py`, `licensing.py`, `moonraker.py`, `octoprint.py`, `rest_api.py`, `DEPLOYMENT.md`, `values.yaml`.

## 2026-02-18

### Enterprise Tier — Full Feature Build

Added Enterprise tier ($499/mo base, $399/mo annual) with all supporting infrastructure:

- **Licensing** — `ENTERPRISE` added to `LicenseTier` enum, `kiln_ent_` key prefix, comparison operators updated, 6 Enterprise-gated features in `FEATURE_TIERS`. `BUSINESS_TIER_MAX_PRINTERS = 50`, `BUSINESS_TIER_MAX_SEATS = 5` constants.
- **RBAC** — `Role` enum (`admin`/`engineer`/`operator`) with `ROLE_SCOPES` mapping in `auth.py`. `create_key_with_role()`, `get_key_role()`, `resolve_role_scopes()` added.
- **Audit trail export** — `export_audit_trail()` method on `KilnDB` in `persistence.py`. JSON/CSV output with date range, tool, action, and session filters.
- **Lockable safety profiles** — `lock_safety_profile()`, `unlock_safety_profile()`, `is_profile_locked()`, `list_locked_profiles()` in `safety_profiles.py`. Locks persisted to `~/.kiln/locked_profiles.json`. `add_community_profile()` rejects modifications to locked profiles.
- **Encrypted G-code at rest** — New `gcode_encryption.py`. Fernet encryption via PBKDF2-derived key from `KILN_ENCRYPTION_KEY` env var. `KILN_ENC_V1:` header prefix for encrypted files. Transparent passthrough for unencrypted reads.
- **Per-printer overage billing** — New `printer_billing.py`. `PrinterUsageBilling` calculates overage for printers beyond the 20 included in Enterprise base ($15/printer/mo). `estimate_monthly_cost()` for total bill projection.
- **Team seat management** — New `teams.py`. `TeamManager` with add/remove/role-change/list operations. Tier-based seat limits (free/pro: 1, business: 5, enterprise: unlimited). Persisted to `~/.kiln/team.json`.
- **Uptime health monitoring** — New `uptime.py`. `UptimeTracker` records health checks, calculates rolling uptime (1h/24h/7d/30d), tracks SLA status (99.9% target), lists recent incidents. Persisted to `~/.kiln/uptime.json` with 30-day retention.
- **Pricing page** — Enterprise card added with feature list and "Talk to us" CTA. Monthly/annual billing toggle (20% discount). Business tier updated: "Up to 50 printers", "5 team seats", "Shared hosted MCP server". 4-column responsive grid. 3 new FAQ entries.
- **Docs** — README, LITEPAPER, WHITEPAPER, PROJECT_DOCS all updated with four-tier model and annual pricing.

### Craftcloud Integration — Fully Live

Craftcloud replied to our partner email with answers to all open questions. Applied their feedback and finished the integration:

- **Auth now optional** — Public endpoints (upload, price, cart, order) work without an API key. `KILN_CRAFTCLOUD_API_KEY` is only needed to associate orders with a Craftcloud account. Removed `ValueError` on missing key.
- **HTTPS everywhere** — Material catalog URL changed from `http://` to `https://customer-api.craftcloud3d.com/material-catalog` per Craftcloud's request.
- **WebSocket price polling** — Added `_poll_prices_websocket()` using `wss://<host>/price/{priceId}` with msgpack-encoded frames, as recommended by Craftcloud. Toggled via `KILN_CRAFTCLOUD_USE_WEBSOCKET=1`. Falls back to existing HTTP polling by default.
- **Payment mode config** — Added `KILN_CRAFTCLOUD_PAYMENT_MODE` (`craftcloud` for their checkout, `partner` for separate billing). Craftcloud said payment handling depends on the integration type.
- **Rate limits** — Craftcloud didn't specify a rate limit, so kept the 2s default poll interval.
- **Webhooks** — Not available from Craftcloud; they recommend polling `GET /v5/order/{orderId}/status`. No code change needed.
- **Docs updated** — Removed "API access required" from README, PROJECT_DOCS, LITEPAPER. Added new env vars to DEPLOYMENT.md. Updated website FeatureGrid and FAQ.
- **Blog post** — Published "Craftcloud Integration Is Live" at `/blog/craftcloud-live`.
- **Tests** — 81 tests (up from 68): new constructor tests for optional auth, WebSocket polling, payment mode, env var handling. Full suite: 5,389 passing.
- **Files changed:** `fulfillment/craftcloud.py`, `fulfillment/registry.py`, `tests/test_fulfillment.py`, README.md, PROJECT_DOCS.md, LITEPAPER.md, DEPLOYMENT.md, FeatureGrid.astro, faq.astro, blog.astro, blog/craftcloud-live.astro.

### Chris + Dillon Demo Content — Fully Integrated

Processed all real-print assets from Chris (Bambu Lab A1 Mini / Wren agent) and Dillon (Prusa Mini / Clawdence agent) and integrated them across the site.

**Assets produced:**
- `docs/site/public/demo/chris-demo.mp4` (35s) — Chris's full print flow stitched
- `docs/site/public/demo/dillon-demo.mp4` (41s) — Dillon's full print flow stitched
- `docs/site/public/demo/kiln-demo-real.mp4` (80s) — Combined demo video with title cards
- `docs/site/public/demo/chris-wren-chat.jpg` — Wren agent chat screenshot (hero image)
- `docs/site/public/demo/chris-finished-coaster.jpg` — Finished coaster on Bambu bed
- `docs/site/public/demo/dillon-clawd-monitor.jpg` — Clawdence webcam monitoring screenshot
- `docs/site/public/demo/dillon-finished-coaster.jpg` — Finished coaster on Prusa bed

**Integrations:**
- **README.md** — Hero image updated from CLI GIF to Wren chat screenshot (CLI GIF preserved in `<details>` block)
- **Homepage** (`index.astro`) — New "Real Prints" section with video embed + two testimonial cards (Chris + Dillon)
- **Blog** — New post `/blog/first-real-prints`: "Our First Real Prints: Two Users, Two Printers, Zero Manual Steps"
- **Blog index** (`blog.astro`) — New post card added at top

## 2026-02-17 (Launch Day)

### Website Live + Launch Content
- Site deployed at kiln3d.com, repo public, DNS configured
- npm `kiln3d` namespace claimed
- Blog post published: "Introducing Kiln: Let AI Agents Run Your 3D Printers"
- FAQ page added (/faq) — 5 sections, 18 questions
- Litepaper redesigned to match whitepaper layout (TOC sidebar, two-column flex)
- All 3DOS references removed from public-facing content — replaced with "distributed networks (coming soon)" pending partnership confirmation
- Real hardware testing complete: Chris (Bambu A1 Mini) and Dillon (Prusa) both successful — photos and videos received

## 2026-02-17

### Craftcloud v5 API Rewrite

- **Problem:** The entire Craftcloud adapter was written against a fictional API that doesn't exist. Every endpoint, payload shape, field name, and flow was wrong.
- **Root cause:** Previous implementation guessed at REST conventions (`POST /uploads`, `POST /quotes`, `POST /orders`) instead of consulting the actual OpenAPI spec at `api.craftcloud3d.com/api-docs.json`.
- **Fix:** Complete rewrite of `fulfillment/craftcloud.py` against the real Craftcloud v5 API:
  - Upload: `POST /v5/model` → poll `GET /v5/model/{modelId}` (200=ready, 206=parsing)
  - Pricing: `POST /v5/price` → poll `GET /v5/price/{priceId}` until `allComplete: true`
  - Ordering: `POST /v5/cart` → `POST /v5/order` (cart + nested `user.shipping`/`user.billing`)
  - Status: `GET /v5/order/{orderId}/status` (nested `orderStatus[].type` enum)
  - Cancel: `PATCH /v5/order/{orderId}/status` with vendor cancel updates
  - Materials: Parse `materialStructure[].materials[].finishGroups[].materialConfigs[].id`
  - Auth: `X-API-Key` header (not `Authorization: Bearer`)
  - Status enum: `ordered`/`in_production`/`shipped`/`received`/`blocked`/`cancelled`
  - `expiresAt` is milliseconds, converted to seconds
- **Tests:** 68 tests covering full v5 flow, material catalog parsing, address mapping, error handling.
- **Files:** `fulfillment/craftcloud.py` (rewritten), `tests/test_fulfillment.py` (rewritten), `docs/PROJECT_DOCS.md` (updated).

## 2026-02-14

### License Decision — BSL → MIT

- **Decision:** Changed Kiln's license from BSL 1.1 to MIT. Discussed with Chris — trust is the adoption gate. Nobody installs closed-source software that controls expensive hardware or sits between their agent and their data.
- **Open core strategy:** Everything in the current repo is MIT (adapters, safety profiles, slicer, MCP tools, CLI, local use). Future fleet/cloud/platform features go in a separate proprietary repo (`kiln-platform` or similar) when built.
- **Files updated:** LICENSE, both pyproject.toml files, README.md, DISASTER_RECOVERY.md, TASKS.md.
- **Strategy documented:** `.dev/LICENSE_STRATEGY.md`

## 2026-02-13

### Partner Outreach — 3DOS + Craftcloud

- **3DOS:** DM'd John (CEO, personal contact) introducing Kiln and the full 3DOS integration (6 MCP tools, 6 CLI commands, 46 tests). Asked for API keys. Awaiting reply.
- **Craftcloud:** Cold email to support@craftcloud3d.com explaining Kiln's Craftcloud adapter is built and requesting API access. LinkedIn connection request + note to Mathias Plica (CEO). Awaiting replies.
- Sculpteo outreach still pending.

### Circle USDC End-to-End Test — PASSED

- Ran live USDC transfer on SOL-DEVNET via Circle W3S Programmable Wallets API.
- `create_payment()` → POST /v1/w3s/developer/transactions/transfer → returns PROCESSING with transaction ID.
- `get_payment_status()` → polls until COMPLETED with on-chain tx hash.
- Transfer: 0.01 USDC from source wallet (20→19.99) to destination wallet (0→0.01).
- Solana devnet tx: `3BDZ8trbqypEhcNe2ySdXL45ghb36cbo7s33KruKqjGu1HXBkpH5W8WcVofTLTK3B7qmrrtF7bqQ3fQ8aZMcdEsN`.
- **Bug fix:** `_resolve_chain()` now auto-detects TEST_API_KEY and appends testnet suffixes (SOL→SOL-DEVNET, BASE→BASE-SEPOLIA). Added `_is_testnet` property.
- Added 7 new tests covering testnet chain resolution (82 total Circle tests).
- Circle account: aaaarreola@gmail.com. Entity secret, wallet set, wallet all configured in `.env`.

## 2026-02-12

### Circle W3S Rewrite + Fly.io Deployment + Stripe Webhook

Three-task session completing payment infrastructure and production deployment.

**Circle Programmable Wallets (W3S) Rewrite:**
- Rewrote `circle_provider.py` (761 lines) for Circle's W3S Programmable Wallets API, replacing the deprecated Transfers API.
- RSA-OAEP entity secret encryption using `cryptography` library. Fresh ciphertext generated per request.
- W3S transfer flow: entity secret → wallet set → wallet → transfer with tokenAddress + blockchain + walletId.
- Transaction state mapping: INITIATED → QUEUED → SENT → CONFIRMED → COMPLETE (or FAILED/CANCELLED/DENIED).
- USDC token addresses for SOL and BASE networks.
- Added `cryptography>=41.0` to payments optional deps in pyproject.toml.
- Rewrote `test_payment_circle.py` — 75 tests covering constructor, properties, payments, status, refunds, HTTP errors, network mapping, setup methods.
- Created `scripts/circle_setup.py` for one-time entity secret generation, wallet set/wallet creation.

**Fly.io Production Deployment:**
- Created `Dockerfile.api` — Python 3.12-slim, ffmpeg, kiln[rest,payments], non-root user, port 8080.
- Created `fly.toml` — App `kiln3d-api`, LAX region, auto-stop/start, health check at `/api/health`.
- Created `deploy.sh` — One-command deploy: checks auth, creates app, sets secrets from .env, deploys.
- Created `.github/workflows/deploy-api.yml` — Auto-deploy on push to main.
- REST API live at `https://kiln3d-api.fly.dev` with health check passing.
- Added health endpoint (`/api/health`) and donation endpoint to `rest_api.py`.

**Stripe Webhook URL Updated:**
- Webhook endpoint URL in Stripe Dashboard changed from `kiln3d.com` to `https://kiln3d-api.fly.dev/api/webhooks/stripe`.
- Signing secret unchanged.

Files: `circle_provider.py`, `test_payment_circle.py`, `pyproject.toml`, `rest_api.py`, `server.py`, `test_rest_api.py`, `Dockerfile.api`, `fly.toml`, `deploy.sh`, `.github/workflows/deploy-api.yml`, `scripts/circle_setup.py`
Total test count: 3,658 passed, 6 skipped, 0 failed.


### Overnight Feature Sprint (4-Stream Swarm) — 10 Features, 157 Tests

All tasks from TASKS.md Low Priority / Deferred backlog, implemented in a 4-stream parallel swarm. Total test count: 3,125 passed (up from 2,968). All files compile clean.

**Stream A — Printer Safety + Agent Memory:**
1. **Filament runout sensor check in preflight** — Added `can_detect_filament` capability to `PrinterCapabilities`, `get_filament_status()` method to `PrinterAdapter` base class. OctoPrint adapter queries filament manager plugin, Moonraker adapter queries Klipper filament_switch_sensor. Preflight now warns (not blocks) when filament not detected. 20 tests.
2. **Agent memory versioning/TTL** — Added `version` and `expires_at` columns to `agent_memory` table. `save_agent_note()` accepts optional `ttl_seconds`, auto-increments version on overwrites. `get_agent_context()` filters expired notes. New `clean_agent_memory` MCP tool purges expired entries. 22 tests.

**Stream B — Infrastructure Hardening:**
3. **Database backup/export (`kiln backup`)** — New `backup.py` module with `backup_database()` (credential redaction) and `restore_database()` (validation + force flag). CLI commands: `kiln backup`, `kiln restore`. MCP tool: `backup_database`. Backups go to `~/.kiln/backups/`. 10 tests.
4. **HMAC-signed audit log entries** — Added `hmac_signature` column to `safety_audit_log`. Each audit entry signed with HMAC-SHA256 using `KILN_AUDIT_HMAC_KEY` env var (fallback: installation-derived key). New `verify_audit_integrity` MCP tool checks all rows. 7 tests.
5. **Log rotation + sensitive data scrubbing** — New `log_config.py` module. `ScrubFilter` redacts API keys, Bearer tokens, passwords from log messages via regex. `RotatingFileHandler` to `~/.kiln/logs/kiln.log` (10MB, 5 backups). Configured at server/CLI startup. Env vars: `KILN_LOG_LEVEL`, `KILN_LOG_DIR`. 18 tests.

**Stream C — Pipeline + CLI + Audit:**
6. **Pipeline pause/resume** — Added `PipelineState` enum, `PipelineExecution` class with pause/resume/abort/retry semantics. Module-level execution registry. 5 new MCP tools: `pipeline_status`, `pipeline_pause`, `pipeline_resume`, `pipeline_abort`, `pipeline_retry_step`. Backward-compatible — existing sync pipeline calls still work. 28 tests.
7. **`kiln quickstart` command** — Chains verify → discover → setup → status in one command. Supports `--json`. Auto-configures first discovered printer if none configured. 6 tests.
8. **Blanket `except Exception` audit** — Added 97 typed exception catches (`PrinterError`, `ValueError`, `OSError`, `FileNotFoundError`, `KeyError`) before generic fallbacks in `cli/main.py`. Generic handlers remain as crash prevention, but specific errors now get targeted handling with better messages.

**Stream D — Model Cache + Discovery Trust:**
9. **Local model cache/library** — New `model_cache.py` module with `ModelCache` class and `ModelCacheEntry` dataclass. SHA256 dedup, tag-based search, print count tracking. `model_cache` table in SQLite. 5 MCP tools: `cache_model`, `search_cached_models`, `get_cached_model`, `list_cached_models`, `delete_cached_model`. CLI: `kiln cache list/search/add/delete`. 29 tests.
10. **mDNS discovery whitelist** — Trusted printer list in config YAML + `KILN_TRUSTED_PRINTERS` env var. `DiscoveredPrinter` now includes `trusted` field. CLI: `kiln trust`, `kiln untrust`. 3 MCP tools: `list_trusted_printers`, `trust_printer`, `untrust_printer`. Discovery warns on untrusted printers. 17 tests.

New files: `backup.py`, `log_config.py`, `model_cache.py`, + 9 test files.
Modified files: `server.py`, `persistence.py`, `pipelines.py`, `printers/base.py`, `printers/octoprint.py`, `printers/moonraker.py`, `discovery.py`, `cli/main.py`, `cli/config.py`, `test_base.py`.


### Post-Sprint Cleanup & Test Coverage

Second pass after the fix sprint to catch remaining issues:

1. **Shapeways references purged** — Removed all remaining mentions from 7 files (CHANGELOG, LITEPAPER, site HTML/Astro, kiln README, server.py env var help text). Final grep confirms zero references.
2. **24 new integration tests** for the 4 new MCP tools:
   - `test_payment_tools.py` (NEW): 13 tests for `check_payment_status` (7) and `billing_check_setup` (6).
   - `test_vision_monitoring.py`: 11 tests added for `watch_print_status` (5) and `stop_watch_print` (6).
3. **ffmpeg prerequisite documented** in README Quick Start section with macOS/Ubuntu install commands.
4. **4 new tools documented** in PROJECT_DOCS.md: `check_payment_status`, `billing_check_setup`, `watch_print_status`, `stop_watch_print`.
5. **Craftcloud task clarified** in TASKS.md — noted that field names are guessed, Swagger docs are JS-rendered, and provided step-by-step instructions for manual verification.

Total test count: 2,968 passed, 0 failed, 23 skipped.

### Pre-Launch Fix Sprint (4-Stream Swarm)

Comprehensive audit and fix sprint addressing 6 major pre-launch issues across 4 parallel work streams. All changes verified against 2,944 tests (0 failures).

**Stream A — Blocking Call Fixes:**
- Refactored `watch_print` from synchronous blocking loop to background `_PrintWatcher` thread. MCP tool now returns immediately with `watch_id`. Added `watch_print_status(watch_id)` and `stop_watch_print(watch_id)` tools for agent polling.
- Removed 97-second blocking polling loop from `CircleProvider.create_payment()`. Now returns immediately with `PROCESSING` status. Added `check_payment_status(payment_id)` MCP tool for async polling.
- Added `VISION_CHECK` and `VISION_ALERT` event types.

**Stream B — Stripe Setup Flow Fix:**
- Added `set_payment_method()` and `poll_setup_intent()` to `StripeProvider` for completing the card setup flow.
- Server now loads `stripe_payment_method_id` from billing config at startup.
- Added `billing_check_setup` MCP tool — polls pending SetupIntent and persists payment method on success.
- Added `POST /api/webhooks/stripe` endpoint in `rest_api.py` with signature verification for `setup_intent.succeeded` events.
- Fixed `CircleProvider.refund_payment()` — source is always `{"type": "wallet", "id": "master"}`.

**Stream C — Cleanup:**
- Removed dead Shapeways adapter (API shut down 2023). Deleted `shapeways.py`, tests, registry entries, and all doc references.
- Fixed Bambu webcam: replaced non-functional HTTP snapshot with ffmpeg-based RTSP frame capture via `subprocess.run`. Added `_find_ffmpeg()` helper. `can_snapshot` now dynamically checks ffmpeg availability.

**Stream D — Human-Required Tasks:**
- Added pre-launch tasks to TASKS.md: Stripe webhook dashboard config, real Craftcloud/Circle/OctoPrint/PrusaSlicer/Bambu hardware tests, ffmpeg documentation.

Files: `server.py`, `circle_provider.py`, `stripe_provider.py`, `manager.py`, `rest_api.py`, `bambu.py`, `events.py`, `fulfillment/__init__.py`, `fulfillment/registry.py`, `fulfillment/base.py`, docs (README, PROJECT_DOCS, WHITEPAPER, DEPLOYMENT, SKILL), tests (test_payment_circle, test_bambu_adapter, test_stripe_setup_flow, test_fulfillment_registry, test_vision_monitoring, test_events)

Deleted: `fulfillment/shapeways.py`, `tests/test_fulfillment_shapeways.py`

### 3DOS Network Integration — MCP Tools + CLI + Tests
Wired the existing 3DOS gateway client (`gateway/threedos.py`) into both the MCP server and CLI. Added 6 MCP tools (`network_register_printer`, `network_update_printer`, `network_list_printers`, `network_find_printers`, `network_submit_job`, `network_job_status`) and 6 CLI commands (`kiln network register/update/list/find/submit/status`). All commands support `--json` output. Added 46 tests covering the gateway client (dataclasses, init, all methods, error handling). The 3DOS client was already implemented — this wires it through to agents and humans.

Files: `server.py`, `cli/main.py`, `tests/test_threedos_gateway.py`

## 2026-02-11

### Crypto Wallet Config + Donation/Tip Feature
Registered `kiln3d.eth` (Ethereum) and `kiln3d.sol` (Solana) ENS/SNS domains for the project's receiving wallets. Created centralized wallet configuration module (`wallets.py`) with hardcoded addresses and env var overrides (`KILN_WALLET_SOLANA`, `KILN_WALLET_ETHEREUM`). Wired wallet addresses into Circle USDC payment flow as default destination. Added donation/tip feature:

1. **`wallets.py`** — `WalletInfo` dataclass, `get_solana_wallet()`, `get_ethereum_wallet()`, `get_donation_info()`.
2. **`donate_info` MCP tool** — Agents can surface wallet addresses for tips.
3. **`kiln donate` CLI command** — Human-friendly display with Rich panel (JSON mode supported).
4. **Coming-soon page** — Added wallet cards with click-to-copy addresses below "Coming soon".
5. **Payment manager** — Circle provider now auto-populates `destination_address` from `wallets.py`.

Files: `wallets.py`, `server.py`, `cli/main.py`, `payments/manager.py`, `docs/site/src/pages/index.astro`, `tests/test_wallets.py`

### Event Filtering for Agents
Added `type` prefix filter parameter to the `recent_events()` MCP tool. Agents can now call `recent_events(type="print")` to get only print-related events, or `type="job"` for job events, instead of fetching everything and filtering client-side. The backend `EventBus.recent_events()` already supported prefix filtering — this wires it through to the MCP layer.

Files: `server.py`

### Paywall Restructure — Free Tier Expansion + Tier Documentation
Restructured the licensing paywall based on platform economics analysis (adoption-first strategy):

1. **Free tier expanded** — `register_printer` (up to 2 printers), `submit_job`/`job_status`/`queue_summary`/`cancel_job`/`job_history` (up to 10 queued jobs), and `billing_summary`/`billing_history` moved from Pro to Free. Single-printer users now get the full experience with no paywall.
2. **Paywall boundary = fleet orchestration** — Pro gates `fleet_status` and new `fleet_analytics` tool. The line is solo operation (free) vs multi-printer coordination (paid).
3. **Free-tier resource caps** — `FREE_TIER_MAX_PRINTERS = 2` and `FREE_TIER_MAX_QUEUED_JOBS = 10` in `licensing.py`. Caps enforced in MCP layer (`server.py`), not CLI layer.
4. **Fee cap raised** — `max_fee_usd` raised from $50 to $200 in `billing.py` to capture upside on large manufacturing orders.
5. **`fleet_analytics` MCP tool** — New Pro-gated tool exposing per-printer success rates, utilization, job throughput, and fleet-wide aggregates from `persistence.py`.
6. **CLI tier gates updated** — `kiln fleet register`, `kiln queue submit/status/list/cancel` no longer require Pro license (caps handled server-side).
7. **Docs updated** — README, WHITEPAPER updated with new tier structure and $200 fee cap. FEATURE_TIERS dict cleaned up (removed phantom entries).

Files: `licensing.py`, `billing.py`, `server.py`, `cli/main.py`, `README.md`, `docs/WHITEPAPER.md`, `tests/test_licensing.py`, `tests/test_billing.py`.

### Print Feedback Loop — Cross-Printer Learning Automation
Implemented the full intent → result → correction feedback loop for the learning database:

1. **Auto-outcome recording** — Scheduler now automatically records `success` or `failed` outcomes when jobs complete or permanently fail. Checks for existing agent-recorded outcomes first (never overwrites curated data). Uses `agent_id="scheduler"` to distinguish from manual recordings. Dispatch failures (print never started) intentionally excluded. `scheduler.py` (6 new tests).
2. **Outcome-aware preflight warnings** — `preflight_check()` now queries the learning DB and warns when a material has <30% success rate (3+ prints) or a printer has <50% overall success rate (5+ prints). Advisory only — never blocks prints. Includes `"advisory": True` flag for UI/agent differentiation. DB errors silently skipped. `server.py` (7 new tests).
3. **`recommend_settings` MCP tool** — New tool that queries historical successful outcomes and returns median temps/speeds and mode slicer profile. Confidence scoring (low/medium/high by sample size), quality distribution, top 5 recent settings. Auth-gated under `"learning"` scope. `server.py`, `persistence.py` (14 new tests).

Files: `scheduler.py`, `server.py`, `persistence.py`, + 3 new test files (27 tests total).

### CI Green + Badge
- Fixed 2 CI failures: OpenSCAD macOS fallback test (needed `_MACOS_APP_PATH` mock on Linux) and flaky uptime test (±30s tolerance too tight for CI runners, widened to ±120s)
- All 4 Python versions (3.10–3.13) now pass. CI badge in README shows green.

### Friction Reduction Round 2 — Discoverability + Error Clarity
Based on friction audits and Wren's feedback:

1. **SKILL.md Quick Start moved to top** — Was buried at line 399, now first thing agents see after the title
2. **Fulfillment section added to SKILL.md** — 3,700 lines of fulfillment code (Craftcloud, Shapeways, Sculpteo, billing, cost comparison) were invisible to agents. Now documented with CLI commands, MCP tools, safety classifications, env var setup, and agent workflow
3. **`--dry-run` and auto-preflight documented** — SKILL.md workflows updated to show `kiln print --dry-run` pattern and note that preflight runs automatically
4. **JSON response examples in SKILL.md** — Agents can now see what `kiln status`, `kiln print`, and `kiln order quote` responses look like
5. **Actionable config validation errors** — "Invalid printer config: api_key required" now includes `Quick fix: kiln auth --name X --api-key YOUR_KEY`
6. **YAML parse errors surfaced** — Broken config no longer silently returns `{}`. Logs warning with the parse error and suggests `kiln setup`
7. **Bambu MQTT timeout troubleshooting** — Timeout error now includes 4-point checklist (power, access code, LAN mode, firewall) instead of just "timed out after 10s"
8. **Enriched `kiln status --json`** — Now includes `printer_name` and `printer_type` in JSON output so agents get full context in one call

Files: `docs/SKILL.md`, `cli/main.py`, `cli/config.py`, `cli/output.py`, `printers/bambu.py`

### 🎉 First External Agent Print — Bambu A1 Mini
**Milestone:** First successful 3D print triggered by an external AI agent (Wren/OpenClaw, powered by Kimi) on real hardware (Bambu A1 Mini, user: Chris Miller). The agent read `docs/SKILL.md`, followed the safety model (identified `start_print` as confirm-level, asked for human approval, checked material compatibility), ran preflight, and started the print — all autonomously via CLI. Cost: ~2 cents per tool call. This validates the full Kiln thesis: AI agents safely operating physical hardware through a skill definition they've never seen before.

### Agent Adoption UX Improvements
Based on feedback from the first external user test:

1. **First-run nudge** — All commands now suggest `kiln setup` when no printer is configured (was just `kiln auth`)
2. **`kiln print` auto-preflight** — CLI now runs safety checks before every print, matching MCP behavior. `--skip-preflight` to bypass.
3. **`kiln print --dry-run`** — Preview what would happen without actually printing (preflight, upload check, file validation)
4. **paho-mqtt default dependency** — Bambu support works out of the box, no `pip install kiln[bambu]` needed
5. **`kiln doctor`** — Alias for `kiln verify`, more intuitive for debugging
6. **SKILL.md onboarding** — Added First-Time Setup section (`kiln setup`, `kiln auth`, `kiln verify`, `kiln discover`), simplified print workflow to reflect auto-preflight, config file > env vars guidance
7. **Install script** — `curl -fsSL https://raw.githubusercontent.com/codeofaxel/Kiln/main/install.sh | sh` — detects OS, installs pipx, clones, installs, verifies

Files: `cli/main.py`, `cli/config.py`, `cli/output.py`, `pyproject.toml`, `docs/SKILL.md`, `install.sh` (new)

### Smart Printer Routing (History-Based)
Scheduler now routes unassigned jobs to the printer with the best historical success rate for the job's file hash and material type. Uses existing `suggest_printer_for_outcome()` from persistence layer — no new data collection needed. Falls back to FIFO when no history exists or job has no metadata. Jobs explicitly assigned to a printer bypass routing entirely. 8 new tests.

Files: `scheduler.py`, `server.py`, `tests/test_scheduler.py`

### Tier-Aware Agent Error Messages (Wired Up)
The improved tier error messages added in `tool_schema.py` were not actually being used — `agent_loop.py` returned a generic "Unknown tool" instead. Now wired up: when an agent calls a tool outside their tier, they see which tier is required, what tier they're on, and up to 3 suggested alternatives. Uses a module-level `_current_tier` variable set/cleared by `run_agent_loop()` via try/finally. 4 new tests.

Files: `agent_loop.py`, `tests/test_agent_loop.py`

### Improved `get_started()` Onboarding
Added `safety_status` (comprehensive safety dashboard) to the safety tools list alongside existing `safety_settings`. Added `session_recovery` section pointing agents to `get_agent_context` for memory restoration. Updated tip to reference both tools. 8 new tests.

Files: `server.py`, `tests/test_get_started.py` (new)

### Backlog Cleanup
Removed 8 security-hardening tasks that add development friction without near-term value (encrypt credentials, SSRF prevention, file permissions [already done], LLM redaction, token persistence, state machine, rate limit headers, pending confirmations list). Added vision monitoring hardware test to medium priority. Focused backlog on capability and reliability work for stealth mode.

Files: `.dev/TASKS.md`, `.dev/COMPLETED_TASKS.md`

### Agent Onboarding Tool (`get_started`)
New `get_started()` MCP tool that returns a structured onboarding guide for AI agents: overview, quick-start steps, core workflows, safety tools, and tool tier summary. Agents no longer need to parse 101+ tool descriptions to understand Kiln. Added to `standard` and `full` tiers.

Files: `server.py`, `tool_tiers.py`

### Improved Tool Tier Error Messages
When an agent calls a tool outside its tier, the error now says which tier the tool requires, what tier the agent is on, and suggests up to 3 related alternatives from their current tier. Previously returned a generic "Unknown tool" with no guidance. Backward-compatible — existing callers without a `tier` argument behave identically.

Files: `tool_schema.py`

### Removed Stale G-code Validator Tasks
Three high-priority tasks (build volume limits, volumetric flow limits, per-printer feedrate limits) were already fully implemented in `_validate_single_with_profile()`. Removed from backlog.

### Linux/WSL Install Experience (pipx)
Updated README Linux/WSL section to recommend `pipx install ./kiln` as primary install method. Gives a globally available `kiln` command without virtualenv activation — works from any directory like a compiled binary. Keeps manual venv as fallback option.

### Safety & Trust Improvements (8 features)
Eight improvements to make users feel safer trusting AI agents with their printers:

1. **Unified Temperature Limit Resolution** — Preflight and G-code validation now use the same source of truth (`_get_temp_limits()` via safety profiles) instead of 3 independent hardcoded values
2. **Pause/Resume Rate Limiting** — Added 5s cooldown / 6-per-minute rate limits to `pause_print` and `resume_print` to prevent mechanical wear from rapid toggling
3. **Dry-Run Mode for send_gcode** — `dry_run=true` parameter runs full validation pipeline without sending commands to the printer
4. **Safety Audit Log** — `safety_audit_log` SQLite table records all guarded/confirm/emergency tool executions (success or block). New `safety_audit` MCP tool to query the log
5. **Confirmation Enforcement** — Generic two-step confirmation gate for all "confirm"-level tools. First call returns token + intent summary, second call with `confirm_action(token)` executes. Tokens expire after 5 minutes. Opt-in via `KILN_CONFIRM_MODE` env var
6. **Safety Dashboard** — `safety_status` MCP tool aggregates active safety profile, temp limits, rate limit config, recent blocked actions, auth status, confirm-mode status in one call
7. **Emergency Cooldown Escalation (Circuit Breaker)** — 3+ blocks within 60s for the same tool triggers 5-minute cooldown. Emits `SAFETY_ESCALATED` event. Prevents runaway agent retry loops
8. **G-code Auto-Detect Printer Profile** — Parses slicer-embedded printer model comments (PrusaSlicer, Cura, OrcaSlicer, BambuStudio) from G-code file headers and fuzzy-matches against 27 known safety profiles

Files: `server.py`, `persistence.py`, `events.py`, `gcode.py`, `safety_profiles.py`, `tool_tiers.py`, `tool_safety.json`
New event types: `SAFETY_BLOCKED`, `SAFETY_ESCALATED`, `TOOL_EXECUTED`
New MCP tools: `safety_audit`, `safety_status`, `confirm_action`

### Installation Fix: Linux/WSL PEP 668
Fixed installation on modern Linux/WSL (Ubuntu 23.04+) where `pip install` is blocked by PEP 668 externally-managed-environment restriction. Documented `pipx` and `venv` workarounds in README.

### Dependabot Config
Added `.github/dependabot.yml` with weekly update checks for pip dependencies (both `kiln/` and `octoprint-cli/`) and GitHub Actions versions. Open PR limit set to 5 per ecosystem.

### PyPI Publishing Pipeline
Upgraded `.github/workflows/publish.yml` to production-ready release workflow:
- **Test gate**: Full test suite (Python 3.10 + 3.12) must pass before any publish
- **Version validation**: Git tag is checked against `kiln/pyproject.toml` version — mismatches fail the build
- **Both packages enabled**: `kiln3d` and `kiln3d-octoprint` now both build and publish (octoprint-cli was previously commented out)
- **Trusted publishing**: OIDC `id-token` auth (no API tokens stored in secrets)
- **Version mismatch fix**: `octoprint-cli/__init__.py` was `1.0.0` vs `pyproject.toml` `0.1.0` — corrected to `0.1.0`

### README Polish Pass
- Added CI, PyPI version, Python version, and license badges to README header
- Updated test counts: `2,970+` total (was incorrectly showing `2650+` / `2413`)
- All feature references verified against current codebase

### Pre-Commit Hooks & Linting
- Created `.pre-commit-config.yaml` with Ruff (lint + format), trailing whitespace, EOF fixer, YAML check, large file guard, merge conflict check
- Added `[tool.ruff]` config to both `kiln/pyproject.toml` (target py310) and `octoprint-cli/pyproject.toml` (target py38)
- Ruff rules: E, F, W, I (imports), UP (pyupgrade), B (bugbear), SIM (simplify)
- Updated `CONTRIBUTING.md` with pre-commit setup instructions, monorepo guidance, and safety-critical code warnings

### Live OctoPrint Integration Smoke Test
- Created `kiln/tests/test_live_octoprint.py` with `@pytest.mark.live` marker
- Tests: connectivity, capabilities, job query, file list, upload + verify + delete round-trip, temperature sanity checks
- Skipped by default — activated via `pytest -m live` with `KILN_LIVE_OCTOPRINT_HOST` and `KILN_LIVE_OCTOPRINT_KEY` env vars
- Added `live` marker to `kiln/pyproject.toml` pytest config
- Includes instructions for running OctoPrint via Docker for CI

### Claimed PyPI Package Names
Reserved four PyPI package names as v0.0.1 placeholders:
- `kiln3d` — https://pypi.org/project/kiln3d/
- `kiln-print` — https://pypi.org/project/kiln-print/
- `kiln-mcp` — https://pypi.org/project/kiln-mcp/
- `kiln3d-octoprint` — https://pypi.org/project/kiln3d-octoprint/

### Model Safety Guardrails — Auto-Print Toggles
Added safety guardrails for AI-generated and marketplace-downloaded 3D models:

- `generate_and_print()` no longer auto-starts prints — uploads only, requires explicit `start_print` call
- `download_and_upload()` same — uploads only, explicit start required
- Two independent opt-in toggles via env vars: `KILN_AUTO_PRINT_MARKETPLACE` (moderate risk) and `KILN_AUTO_PRINT_GENERATED` (higher risk), both default OFF
- All generation/download tools return `experimental` or `verification_status` flags plus safety notices
- New `safety_settings` MCP tool shows current auto-print configuration and recommendations
- Setup wizard (`kiln setup`) now prompts users to configure auto-print preferences during onboarding
- MCP server system prompt updated to guide agents toward proven community models over generation
- Setup complete summary shows current toggle values and env var names for later changes

### Bambu A1/A1 Mini Compatibility
Fixed 3 bugs reported by Chris Miller during real-hardware testing on Bambu A1 mini:

- **Uppercase state parsing**: A1/A1 mini sends UPPERCASE `gcode_state` (e.g. "RUNNING" instead of "running"). Added `.lower()` normalization in `get_state()` and case-insensitive command matching in `_on_message()`.
- **Implicit FTPS on port 990**: A-series uses implicit TLS (wraps socket in TLS immediately), not explicit STARTTLS. Added `_ImplicitFTP_TLS` subclass with socket wrapping and TLS session reuse for data channels.
- **Print start confirmation**: `start_print()` now polls MQTT for `gcode_state` to confirm the printer actually started (up to 30s). Returns failure if printer enters error state or times out.
- Added 121 Bambu adapter tests including new test classes for uppercase states, print confirmation, and implicit FTPS.

### Comprehensive Security Hardening
Full-project security audit and fix pass — 70+ vulnerabilities identified and fixed across 25+ files.

**Temperature Safety (P0 — hardware protection)**
- G-code validator now blocks negative temperatures and warns on cold extrusion risk (<150°C)
- Unrecognized G-code commands blocked instead of passed through with warning
- `set_temperature()` MCP tool validates bounds (0-300°C hotend, 0-130°C bed) before reaching adapters
- All 4 printer adapters (OctoPrint, Moonraker, Bambu, PrusaConnect) enforce temperature limits via shared `_validate_temp()` in base class
- CLI `temp` command validates temperature ranges before sending

**Path Traversal Fixes**
- `printer_snapshot()` restricts save_path to home/tmp directories
- Slicer `output_name` stripped to basename only — rejects directory traversal
- Bambu `start_print()` and `delete_file()` restrict paths to `/sdcard/` and `/cache/`
- CLI `snapshot --output` validates path boundaries

**Agent Security**
- Tool results sanitized before feeding to LLM in `agent_loop.py` — strips injection patterns, truncates to 50K chars
- System prompt includes explicit warning to ignore instructions in tool results
- `skip_preflight` parameter removed from `start_print()` — pre-flight checks are now mandatory

**REST API Hardening**
- Parameter pollution fixed: `**body` replaced with `inspect.signature()` filtering, rejects unknown params
- Rate limiting added (60 req/min per IP)
- CORS default changed from `["*"]` to `[]`
- Request body size limited to 1MB
- Error messages sanitized to prevent information leakage

**Payment Security**
- Circle USDC: destination address validated (Ethereum 0x format or Solana base58)
- Stripe: error messages sanitized — no raw exception details returned to clients
- Payment manager: billing charge failure handled gracefully with status tracking

**Infrastructure Fixes**
- MJPEG proxy: frame buffer capped at 10MB to prevent OOM
- Cloud sync: error messages sanitized to prevent credential leakage
- Scheduler: job status mutations wrapped in locks to prevent race conditions
- Materials tracker: spool warnings emitted outside lock to prevent deadlocks
- Webhook delivery queue bounded to 10K entries with overflow logging
- Event bus: duplicate subscription prevention
- Bed leveling: division-by-zero guard on empty mesh data
- Cost estimator: intermediate rounding removed to prevent accumulation errors

**Plugin & Subprocess Safety**
- Plugin loading gated by `KILN_ALLOWED_PLUGINS` allow-list
- OpenSCAD input validated: size limit (100KB), dangerous functions blocked (`import()`, `surface()`, `include`, `use`)
- OpenSCAD subprocess runs in isolated temp directory
- CLI config: removed credential type confusion fallback (access_code no longer falls back to API key)

**Defensive Measures**
- G-code batch limited to 100 commands per send
- File upload validates existence and size (max 500MB, rejects empty files)
- Pipeline G-code sample increased from 500 to 2000 lines
- Pipeline safety check failure now aborts (was silently continuing)

All 2891 tests passing (2652 kiln + 239 octoprint-cli).

### Multi-Model Support (OpenRouter / Any LLM)
- **tool_schema.py**: OpenAI function-calling schema converter — introspects FastMCP tool definitions and generates OpenAI-compatible JSON schemas with parameter descriptions from docstrings
- **tool_tiers.py**: Three-tier tool system — essential (15 tools for weak models), standard (43 for mid-range), full (101 for strong models) with auto-detection via `suggest_tier(model_name)`
- **agent_loop.py**: Generic agent loop for any OpenAI-compatible API — handles tool calling, multi-turn conversations, error recovery, and configurable max turns
- **openrouter.py**: OpenRouter-specific integration with curated 15-model catalog, auto-tier detection, convenience `run_openrouter()` function, and interactive REPL
- **rest_api.py**: FastAPI REST wrapper — exposes all MCP tools as `POST /api/tools/{name}` endpoints with discovery (`GET /api/tools`), agent loop endpoint (`POST /api/agent`), and optional Bearer auth
- New CLI commands: `kiln setup` (interactive wizard), `kiln rest` (REST API server), `kiln agent` (multi-model REPL)
- `rest` optional dependency group: `pip install kiln3d[rest]`

### Pre-Launch Infrastructure
- CONTRIBUTING.md, CODE_OF_CONDUCT.md, GitHub issue/PR templates
- Example configs: `kiln-config.yaml` (all 4 printer types), `claude-desktop-mcp.json`
- Fixed README/whitepaper image paths for PyPI rendering
- Version consistency pass (standardized to 0.1.0)

### Closed-Loop Vision Feedback
- 2 MCP tools: `monitor_print_vision` (snapshot + state + phase hints), `watch_print` (polling loop with periodic snapshot batches)
- Print phase detection: first_layers (< 10%), mid_print (10-90%), final_layers (> 90%) — each with curated failure hints
- `can_snapshot` capability flag on `PrinterCapabilities`, set `True` for OctoPrint and Moonraker adapters
- 2 new event types: `VISION_CHECK`, `VISION_ALERT`
- Works gracefully without webcam (metadata-only monitoring)
- 27 tests covering phase detection, snapshot paths, failure hints

### Cross-Printer Learning
- `print_outcomes` SQLite table with indexes on printer_name, file_hash, and outcome
- 7 new `KilnDB` methods: `save_print_outcome`, `get_print_outcome`, `list_print_outcomes`, `get_printer_learning_insights`, `get_file_outcomes`, `suggest_printer_for_outcome`, `_outcome_row_to_dict`
- 3 MCP tools: `record_print_outcome` (safety-validated), `get_printer_insights` (aggregated analytics), `suggest_printer_for_job` (ranked recommendations)
- **Safety guardrails**: Hard temperature limits (320C tool, 140C bed, 500mm/s speed), enum validation on outcomes/grades/failure modes, `SAFETY_VIOLATION` rejection for dangerous values, advisory-only disclaimers on all insight responses
- 30 tests covering DB CRUD, aggregation, edge cases

### Physical-World Platform Generalization
- `DeviceType` enum: `FDM_PRINTER`, `SLA_PRINTER`, `CNC_ROUTER`, `LASER_CUTTER`, `GENERIC`
- `DeviceAdapter = PrinterAdapter` alias for forward compatibility
- Extended `PrinterCapabilities`: `device_type` (default "fdm_printer"), `can_snapshot` (default False)
- Optional device methods: `set_spindle_speed()`, `set_laser_power()`, `get_tool_position()` — default implementations raise/return None
- All 4 existing adapters continue to work without modification
- 22 tests covering alias identity, enum values, capability defaults, backward compatibility

### Bundled Slicer Profiles Per Printer
- **`data/slicer_profiles.json`** — Curated PrusaSlicer/OrcaSlicer settings for 14 printer models: Ender 3, Ender 3 S1, K1, Prusa MK3S/MK4/Mini, Bambu X1C/P1S/A1, Voron 2.4, Elegoo Neptune 4, Sovol SV06, QIDI X-Plus 3
- Each profile: layer height, speeds, temps, retraction, fan, bed shape, G-code flavor — all optimized for the specific printer's kinematics and extruder type
- **`slicer_profiles.py`** — Loader with `resolve_slicer_profile()` that auto-generates temp `.ini` files for the slicer CLI, cached per printer+overrides
- 2 MCP tools: `list_slicer_profiles_tool`, `get_slicer_profile_tool`
- Agents auto-select the right profile by passing `printer_id` — no manual slicer config needed

### Printer Profile Intelligence (Firmware Quirks DB)
- **`data/printer_intelligence.json`** — Full operational knowledge base for 13 printer models: firmware type, extruder/hotend info, enclosure status, ABL capability
- **Material compatibility matrix** per printer: PLA/PETG/ABS/TPU/PA-CF/PC with exact hotend/bed/fan temps and material-specific tips
- **Firmware quirks** — printer-specific gotchas (e.g. "PTFE tube degrades above 240°C", "Nextruder requires 0.4mm retraction — don't increase")
- **Calibration guidance** — step-by-step procedures (first_steps, flow_rate_test, retraction_test, esteps)
- **Known failure modes** — symptom → cause → fix database for common issues
- **`printer_intelligence.py`** — Loader with `get_material_settings()`, `diagnose_issue()` (fuzzy symptom search)
- 3 MCP tools: `get_printer_intelligence`, `get_material_recommendation`, `troubleshoot_printer`

### Pre-Validated Print Pipelines
- **`pipelines.py`** — Named command sequences that chain multiple MCP operations:
  - **`quick_print`** — resolve profile → slice → G-code safety validation → upload → preflight → start print (6 steps with error handling at each stage)
  - **`calibrate`** — connect → home axes → auto bed level → return calibration guidance from intelligence DB
  - **`benchmark`** — resolve profile → slice → upload → report printer stats from history
- Each pipeline returns `PipelineResult` with per-step timing, success/failure, and diagnostic data
- Pipeline registry with `list_pipelines()` for discoverability
- 4 MCP tools: `list_print_pipelines`, `run_quick_print`, `run_calibrate`, `run_benchmark`

### Agent Memory & Print History Logging
- **Print history table** (`print_history`) in SQLite persistence — tracks every completed/failed job with printer_name, duration, material_type, file_hash, slicer_profile, notes, agent_id, and JSON metadata
- **Agent memory table** (`agent_memory`) — persistent key-value store scoped by agent_id and namespace (global, fleet, per-printer). Survives across sessions
- **Auto-logging event subscriber** — `_log_print_completion` hooked to `JOB_COMPLETED` and `JOB_FAILED` events, writes history records automatically
- 6 new MCP tools: `print_history`, `printer_stats`, `annotate_print`, `save_agent_note`, `get_agent_context`, `delete_agent_note`
- All DB methods use `_write_lock` for thread safety, JSON serialization for complex data, `time.time()` timestamps

### Bundled Safety Profiles Database
- **`data/safety_profiles.json`** — Curated per-printer safety database with 26 printer models: Creality (Ender 3/5, CR-10, K1), Prusa (Mini, MK3S, MK4, XL), Bambu Lab (X1C, P1S, P1P, A1, A1 Mini), Voron (0, 2.4), Rat Rig, Elegoo, Sovol, FlashForge, QIDI, AnkerMake, Artillery
- Each profile: max hotend/bed/chamber temps, max feedrate, volumetric flow, build volume, safety notes (e.g. PTFE hotend warnings)
- **`safety_profiles.py`** — Loader with `get_profile()` (fuzzy matching + fallback to default), `list_profiles()`, `get_all_profiles()`, `profile_to_dict()`
- **`validate_gcode_for_printer()`** — New function in `gcode.py` that validates commands against a specific printer's limits instead of generic defaults
- 3 new MCP tools: `list_safety_profiles`, `get_safety_profile`, `validate_gcode_safe`
- Error messages include printer display name for clarity (e.g. "exceeds Creality Ender 3 max hotend temperature (260°C)")

### Webcam Streaming / Live View
- `MJPEGProxy` class in `streaming.py` — full MJPEG stream proxy with start/stop lifecycle
- `webcam_stream` MCP tool for agents to start/stop/check stream status
- `kiln stream` CLI command with `--port` and `--stop` options
- 20 tests in `test_streaming.py`
- Previously listed in TASKS.md as medium priority; already shipped

## 2026-02-10

### OTA Firmware Updates
- `FirmwareComponent`, `FirmwareStatus`, `FirmwareUpdateResult` dataclasses in `base.py`
- `can_update_firmware` capability flag on `PrinterCapabilities`
- **Moonraker adapter** — `get_firmware_status()` via `/machine/update/status`, `update_firmware()` via `/machine/update/upgrade`, `rollback_firmware()` via `/machine/update/rollback`
- **OctoPrint adapter** — `get_firmware_status()` via Software Update plugin check API, `update_firmware()` via plugin update API with auto-discovery of updatable targets
- Safety: both adapters refuse updates while printing
- 3 new MCP tools: `firmware_status`, `update_firmware`, `rollback_firmware` (auth-gated)
- 3 new CLI commands: `kiln firmware status`, `kiln firmware update`, `kiln firmware rollback`
- 55 new tests across 4 test files (adapter, MCP tools, CLI)
- Total test count: 2,078

### Additional Fulfillment Providers (Shapeways + Sculpteo)
- `ShapewaysProvider` — Full implementation with OAuth2 client-credentials auth, model upload (base64), per-material pricing, order placement, status tracking, and cancellation
- `SculpteoProvider` — Full implementation with Bearer token auth, file upload, UUID-based pricing, order placement via store API, status tracking, and cancellation
- `FulfillmentProviderRegistry` — Pluggable registry with auto-detection from env vars (`KILN_FULFILLMENT_PROVIDER`, or auto-detect from `KILN_CRAFTCLOUD_API_KEY` / `KILN_SHAPEWAYS_CLIENT_ID` / `KILN_SCULPTEO_API_KEY`)
- Updated `server.py` and `cli/main.py` to use registry instead of hardcoded Craftcloud
- 87 new tests: 45 Shapeways (including OAuth2 token lifecycle), 33 Sculpteo, 9 registry
- Total fulfillment providers: 3 (Craftcloud, Shapeways, Sculpteo)
- Total test count: 1,898+

### Text-to-Model Generation
- New `kiln/src/kiln/generation/` module with `GenerationProvider` ABC and shared dataclasses
- **Meshy adapter** (`MeshyProvider`) — cloud text-to-3D via Meshy API (preview mode, async job model)
- **OpenSCAD adapter** (`OpenSCADProvider`) — local parametric generation, agent writes .scad code, Kiln compiles to STL
- **Mesh validation pipeline** (`validate_mesh()`) — binary/ASCII STL and OBJ parsing, manifold check, bounding box, dimension limits, polygon count limits. Zero external dependencies (pure `struct` parsing).
- 7 new MCP tools: `generate_model`, `generation_status`, `download_generated_model`, `await_generation`, `generate_and_print`, `validate_generated_mesh`
- 3 new CLI commands: `kiln generate`, `kiln generate-status`, `kiln generate-download`
- `generate_and_print` — full pipeline tool: text → generate → validate → slice → upload → print
- `await_generation` — polling tool for async cloud providers (like `await_print_completion`)
- Comprehensive test suite: unit tests for adapters (mock HTTP), validation pipeline, MCP tools, and CLI commands

### Post-Print Quality Validation
- `validate_print_quality` MCP tool — assesses print quality after completion
- Captures webcam snapshot (if available) and returns base64 or saves to file
- Analyses job events: retry count, progress consistency, timing anomalies
- Quality grading: PASS / WARNING / REVIEW based on detected issues
- Structured recommendations for agent follow-up
- Works with or without a job_id (auto-finds most recent completed job)

### CLI Test Coverage for Advanced Features
- 72 new CLI tests in `test_cli_advanced.py`
- Covers all 30+ untested commands: `snapshot`, `wait`, `history`, `cost`, `compare-cost`, `slice`
- Material subcommands: `set`, `show`, `spools`, `add-spool`
- Level, stream, sync (`status`/`now`/`configure`), plugins (`list`/`info`)
- Order subcommands: `materials`, `quote`, `place`, `status`, `cancel`
- Billing subcommands: `setup`, `status`, `history`
- Parametrized `--help` tests for all 30 command/subcommand combinations
- Total test count: 1,811+

### End-to-End Integration Test
- 13 integration tests in `test_integration.py`
- Full pipeline: discover → auth → preflight → upload → print → wait → history
- Slice → upload → print in one shot via `--print-after`
- Error propagation: preflight failure, upload failure, adapter error, printer offline, no webcam
- Tests compose real CLI commands with mock printer backend via `CliRunner`

### Bambu Webcam Support
- `get_snapshot()` on BambuAdapter — tries HTTPS/HTTP snapshot endpoint on the printer
- `get_stream_url()` on BambuAdapter — returns `rtsps://<host>:322/streaming/live/1` (Bambu LAN RTSP stream)
- Falls back gracefully to `None` if camera not accessible

### Resumable Downloads
- `resumable_download()` shared helper in `marketplaces/base.py`
- Uses HTTP `Range` headers to resume interrupted downloads from `.part` temp files
- Automatic retry with up to 3 attempts on failure
- Handles servers that don't support Range (restarts cleanly)
- Handles 416 Range Not Satisfiable (file already complete)
- Thingiverse and MyMiniFactory adapters now both use `resumable_download()`
- Atomic rename from `.part` → final file on completion

### Print Failure Analysis Tool
- `analyze_print_failure(job_id)` MCP tool
- Examines job record, related events (retries, errors, progress), and timing
- Produces structured diagnosis: symptoms, likely causes, recommendations
- Detects patterns: quick failures (setup issues), late failures (adhesion/cooling), retry exhaustion
- Correlates progress % at failure to suggest specific fixes (first-layer, supports, etc.)

### Bambu "cancelling" State + OctoPrint Bed Mesh
- Added `"cancelling"` → `PrinterStatus.BUSY` to Bambu adapter state map (was unmapped → UNKNOWN)
- Added `get_bed_mesh()` to OctoPrint adapter via Bed Level Visualizer plugin API (`/api/plugin/bedlevelvisualizer`)
- Returns `None` gracefully if plugin not installed

### Await Print Completion MCP Tool
- `await_print_completion(job_id, timeout, poll_interval)` MCP tool
- Supports both job-based tracking (via queue/scheduler) and direct printer monitoring
- Returns `outcome` field: completed, failed, cancelled, or timeout
- Includes progress log with completion % snapshots at each poll interval
- Configurable timeout (default 2h) and poll interval (default 15s)
- Lets agents fire-and-forget a print and pick up the result later

### Cost Comparison: Local vs. Fulfillment
- `compare_print_options` MCP tool — side-by-side local vs. outsourced cost comparison
- Runs local cost estimate (filament + electricity) and Craftcloud fulfillment quote in one call
- Returns unified comparison with `cheaper` recommendation, cost delta, time estimates
- `kiln compare-cost` CLI command with human-readable and JSON output
- Falls back gracefully if either source is unavailable

### Auto-Retry with Exponential Backoff
- Added `retry_backoff_base` parameter to `JobScheduler` (default 30s)
- Retry delays: 30s → 60s → 120s (exponential backoff on failure)
- `_retry_not_before` dict tracks per-job backoff timestamps
- Dispatch phase skips jobs still in backoff window
- Backoff state cleaned up on completion, permanent failure, or successful retry
- JOB_SUBMITTED event now includes `retry_delay_seconds` field

### Launch Readiness Fixes (Gap Analysis)
- **Bambu env var bug fix**: `access_code` in `config.py` now reads from `KILN_PRINTER_ACCESS_CODE` (falls back to `KILN_PRINTER_API_KEY` for backward compat). Previously both `api_key` and `access_code` read from the same env var, breaking Bambu auth via env config.
- **Automatic preflight in `start_print()`**: The MCP `start_print()` tool now runs `preflight_check()` automatically before starting a print. Returns `PREFLIGHT_FAILED` with full check details if the printer isn't ready. Agents no longer need to remember to call preflight first. Opt-out via `skip_preflight=True`.
- **`can_download` on `ModelSummary`**: Search results now include a `can_download` field so agents know upfront which marketplace results can be downloaded programmatically vs. require manual browser download (Cults3D).
- **TASKS.md backlog expansion**: Added 9 new tasks from gap analysis covering CLI test coverage, integration tests, Bambu webcam, await-completion tool, failure analysis, cost comparison, text-to-model generation, auto-retry, and post-print quality validation.
- **CLAUDE.md rule**: Added mandatory completed-task tracking — shipped features must always be moved from TASKS.md to COMPLETED_TASKS.md.

### Print Cost Estimation
- `kiln.cost_estimator` module with G-code extrusion analysis
- `MaterialProfile` and `CostEstimate` dataclasses
- 7 built-in material profiles (PLA, PETG, ABS, TPU, ASA, Nylon, PC)
- Parses absolute/relative E-axis extrusion, M82/M83 mode switching, G92 resets
- Slicer time comment extraction (PrusaSlicer, Cura, OrcaSlicer formats)
- `kiln cost` CLI command, `estimate_cost` and `list_materials` MCP tools
- 50 tests

### Multi-Material Tracking
- `kiln.materials` module with spool inventory and per-printer material tracking
- `LoadedMaterial`, `Spool`, `MaterialWarning` dataclasses
- `MaterialTracker` class: set/get material, check mismatch, deduct usage
- Spool CRUD operations with low/empty warnings via event bus
- `printer_materials` and `spools` DB tables
- `kiln material` CLI command group, 6 MCP tools
- 68 tests

### Bed Leveling Triggers
- `kiln.bed_leveling` module with configurable auto-leveling policies
- `LevelingPolicy` and `LevelingStatus` dataclasses
- `BedLevelManager`: subscribes to job completion events, evaluates triggers
- Policies: max prints between levels, max hours, auto-before-first-print
- Mesh variance calculation from probed data
- `leveling_history` DB table, `get_bed_mesh()` adapter method on Moonraker
- `kiln level` CLI command, 3 MCP tools
- 33 tests

### Webcam Streaming (MJPEG Proxy)
- `kiln.streaming` module with MJPEG proxy server
- `MJPEGProxy` class: reads upstream MJPEG stream, re-serves to local clients
- `StreamInfo` dataclass with client count, frames served, uptime tracking
- `get_stream_url()` adapter method on OctoPrint and Moonraker
- `kiln stream` CLI command, `webcam_stream` MCP tool
- 20 tests

### Cloud Sync
- `kiln.cloud_sync` module for syncing printer configs, jobs, events to cloud
- `SyncConfig` and `SyncStatus` dataclasses
- `CloudSyncManager`: background daemon thread, HMAC-SHA256 signed payloads
- Push unsynced jobs/events/printers, cursor-based incremental sync
- `sync_log` DB table with sync tracking
- `kiln sync` CLI command group, 3 MCP tools
- 30 tests

### Plugin System
- `kiln.plugins` module with entry-point-based plugin discovery
- `KilnPlugin` ABC: lifecycle hooks, MCP tools, event handlers, CLI commands
- `PluginManager`: discover, activate/deactivate, pre/post-print hooks
- `PluginHook` enum, `PluginInfo` and `PluginContext` dataclasses
- Plugin isolation: exceptions in hooks don't crash the system
- `kiln plugins` CLI command group, 2 MCP tools
- 35 tests

### Fulfillment Service Integration (Craftcloud)
- `kiln.fulfillment` module with `FulfillmentProvider` ABC and `CraftcloudProvider` implementation
- `FulfillmentProvider` abstract base: `list_materials()`, `get_quote()`, `place_order()`, `get_order_status()`, `cancel_order()`
- Craftcloud adapter: upload → quote → order workflow via REST API with Bearer token auth
- Dataclasses: `Material`, `Quote`, `QuoteRequest`, `OrderRequest`, `OrderResult`, `ShippingOption`
- `OrderStatus` enum with 9 states (pending, confirmed, in_production, shipped, delivered, cancelled, failed, refunded, unknown)
- `kiln order` CLI command group: `materials`, `quote`, `place`, `status`, `cancel`
- 5 MCP tools: `fulfillment_materials`, `fulfillment_quote`, `fulfillment_order`, `fulfillment_order_status`, `fulfillment_cancel`
- Rich CLI output formatters for quotes, orders, and material listings
- 32 tests

### Prusa Connect Adapter
- 4th printer backend via Prusa Link local REST API
- Supports Prusa MK4, XL, Mini+ with `X-Api-Key` authentication
- Maps all 9 Prusa Link states to `PrinterStatus` enum
- Read-only adapter: status, files, upload, print control (no temp set or raw G-code — Prusa Link limitation)
- `can_set_temp=False`, `can_send_gcode=False` in capabilities
- Wired into CLI config, discovery (HTTP probe on port 80), and MCP server
- 28 tests

### Multi-Marketplace Search
- `MarketplaceAdapter` ABC with `search()`, `get_details()`, `get_files()`, `download_file()`
- Concrete adapters: Thingiverse (REST), MyMiniFactory (REST v2), Cults3D (GraphQL, metadata-only)
- `MarketplaceRegistry` with `search_all()` fan-out, round-robin interleaving, per-adapter fault isolation
- `search_all_models`, `marketplace_info`, `download_and_upload` MCP tools
- `download_and_upload` combines marketplace download + printer upload in one step
- Cults3D adapter signals `supports_download = False` (API limitation)

### Slicer Integration
- `kiln.slicer` module wrapping PrusaSlicer / OrcaSlicer CLI
- Auto-detects slicer on PATH, macOS app bundles, and `KILN_SLICER_PATH` env var
- `kiln slice` CLI command with `--print-after` to slice-upload-print in one step
- `slice_model`, `find_slicer_tool`, `slice_and_print` MCP tools
- Supports STL, 3MF, STEP, OBJ, AMF input formats
- 17 tests

### Webcam Snapshot Support
- `get_snapshot()` optional method on `PrinterAdapter` base class
- OctoPrint: fetches from `/webcam/?action=snapshot`
- Moonraker: discovers webcam via `/server/webcams/list`, fetches snapshot URL
- `kiln snapshot` CLI command (save to file or base64 JSON)
- `printer_snapshot` MCP tool with optional save_path
- 5 tests

### kiln wait Command
- `kiln wait` blocks until the current print finishes
- Polls printer status at configurable interval (`--interval`)
- `--timeout` for maximum wait time
- Exits 0 on success (IDLE), 1 on error/offline
- Shows inline progress bar in human mode

### kiln history Command
- `kiln history` shows past prints from SQLite database
- Filters by status (`--status completed|failed|cancelled`)
- Rich table output with file, status, printer, duration, date
- `format_history()` output formatter

### Material/Filament Tracking in Preflight
- `kiln preflight --material PLA|PETG|ABS|TPU|ASA|Nylon|PC`
- Validates tool and bed target temperatures against material ranges
- Warns when temperatures are outside expected range for the material
- 4 tests

### Batch Printing
- `kiln print *.gcode` accepts multiple files via glob expansion
- `--queue` flag submits files to the job queue for sequential printing
- Without `--queue`, prints first file and lists remaining
- 4 tests

### CLI Flow Gaps Closed
- `kiln preflight` — CLI access to pre-print safety checks
- `kiln print` auto-uploads local files before starting
- BambuAdapter None guard when paho-mqtt not installed

### End-to-End Print Flow Diagram
- Created `docs/PRINT_FLOW.md` with full Mermaid diagram
- Covers: idea → find design → slice → setup → preflight → upload → print → monitor → done

### Kiln CLI
- Full Click-based CLI with 16 subcommands
- `kiln discover` (mDNS + HTTP probe), `kiln auth`, `kiln status`, `kiln files`, `kiln upload`, `kiln print`, `kiln cancel`, `kiln pause`, `kiln resume`, `kiln temp`, `kiln gcode`, `kiln printers`, `kiln use`, `kiln remove`, `kiln preflight`, `kiln serve`
- `--json` flag on every command for agent consumption
- Config management via `~/.kiln/config.yaml`
- Rich terminal output with plain-text fallback

### README Update
- Updated to reflect Moonraker stable, Bambu stable, Thingiverse, CLI, full MCP tool list

### Thingiverse Integration
- `ThingiverseClient` with search, browse, download
- 6 MCP tools: `search_models`, `model_details`, `model_files`, `download_model`, `browse_models`, `list_model_categories`
- 50+ tests

### Bambu Lab Adapter
- Full PrinterAdapter implementation over LAN MQTT
- Supports X1C, P1S, A1

### Moonraker Promoted to Stable
- Full coverage of all PrinterAdapter methods
- Tested against Klipper-based printers

### Core Infrastructure (by other instance)
- Job scheduler with background dispatch
- Priority queue with status tracking
- Event bus with pub/sub
- SQLite persistence for jobs and events
- Webhook delivery with HMAC signing
- API key authentication with scopes
- Billing/fee tracking for network jobs
- G-code safety validator
- Printer registry for fleet management
- MCP resources (kiln://status, kiln://printers, etc.)
- MCP prompt templates (print_workflow, fleet_workflow, troubleshooting)
