# Kiln — Open Tasks

Prioritized backlog of features and improvements.

## 0.5.0 Release Prep — This Week (2026-03-20)

### Full Pipeline Demo Video (Adam + Claude)
- [ ] Script the agent conversation flow: text description → `get_design_brief` → `recommend_design_material` → `build_generation_prompt` → `generate_model` → `preview_generated_model` → `analyze_printability` → `slice_model` → `preflight_check` → `start_print` → `monitor_print` → finished object in hand
- [ ] Adam: pick the object (something simple and visual — phone stand, headphone hook, desk organizer)
- [ ] Adam: handle physical printer and camera work (screen record chat + film printer + photo of finished object)
- [ ] Claude: prepare the scripted prompt sequence so the demo flows smoothly
- [ ] Edit into a 2-3 min video showing the magic moment: "type what you want, get the object"
- [ ] Use as hero content for website revamp and README

### Website & Docs Revamp (pending attorney sign-off on positioning changes)
- [ ] Get attorney sign-off on repositioning "Positioning Clarification" / "Non-goals" in README (email drafted)
- [ ] Rewrite Hero.astro — emotional tagline above SEO headline
- [ ] Rewrite FeatureGrid.astro — lead with pipeline story, not infrastructure
- [ ] Add "Works with your printer" compatibility strip with logos
- [ ] Rewrite subtitle from "infrastructure" to "intelligence layer"
- [ ] Update all tool/CLI counts to verified numbers
- [ ] Embed demo video as hero content

### Version Bump
- [ ] Bump to 0.5.0 only after website/docs are ready
- [ ] Full CHANGELOG update
- [ ] Tag + PyPI release
- [ ] Update MCP registry, ClawHub, Glama, server.json

## IRL Design-to-Print Validation (2026-03-10)

End-to-end testing of the v0.4.0 design generation pipeline on Adam's Bambu A1 Combo. Goal: prove the full loop works (NL → template → OpenSCAD → STL → structural analysis → slice → print) and capture what breaks.

### Test 1: Simple Functional Print — Cable Management Clip
- [ ] Use `search_design_templates` to find a cable clip template
- [ ] Use `design_to_gcode_pipeline` with a description like "cable clip for 3 cables, desk mount"
- [ ] Inspect the generated STL — does it look right? Reasonable wall thickness?
- [ ] Check `estimate_mesh_weight` output — does the weight estimate make sense?
- [ ] Run structural analysis — does auto-reinforcement suggest anything?
- [ ] Slice with slicer inference settings and upload to A1 (AMS auto-detect)
- [ ] Print it. Does it fit real cables? Is it strong enough?
- [ ] **Log**: what worked, what failed, parameter tweaks needed

### Test 2: Parametric Constraint Solving — Shelf Bracket
- [ ] Use `solve_template_constraints` with ratio constraints (e.g., arm_length = 2x wall_length)
- [ ] Generate the bracket STL from solved parameters
- [ ] Run `cross_section_view` at the stress point — does the cross-section look solid?
- [ ] Print it. Load test by hand — does it hold a book? Flex? Snap?
- [ ] **Log**: constraint solver accuracy, printability of solved dimensions

### Test 3: Compositional Generation — Custom Multi-Part Object
- [ ] Use `compose_from_primitives` to build something novel (e.g., phone stand with cable slot)
- [ ] Use `merge_stl_files` if assembling from multiple generated parts
- [ ] Run the full structural + weight + slicer pipeline
- [ ] Print it. Does it function as intended?
- [ ] **Log**: boolean operation quality, dimensional accuracy, fit/finish

### Test 4: Infrastructure Reliability
- [ ] Use `watch_print` with `cancel_at_percent=50` on a test print — does auto-cancel trigger?
- [ ] Verify camera ground-truth: does `telemetry_mismatch` flag correctly when progress is real?
- [ ] Verify AMS auto-detect: does `use_ams="auto"` correctly probe and map the loaded slot?
- [ ] **Log**: any edge cases, timing issues, false positives

### Test 5: Template Printability Sweep
- [ ] Pick 5 diverse templates (different categories) and generate STLs with default params
- [ ] Quick visual check: overhangs >60°? Thin walls <0.8mm? Impossible bridges?
- [ ] Print the sketchiest-looking one — does it actually print or fail?
- [ ] **Log**: which templates need parameter range tightening

### After All Tests
- [ ] Compile findings into LESSONS_LEARNED.md
- [ ] File bugs / parameter fixes discovered during printing
- [ ] Update template defaults if any produced unprintable geometry
- [ ] Take photos of printed objects for demo materials

## Bambu A1 First Print — Active Issues (2026-03-04)

- **MakerWorld Cloudflare bypass** — MakerWorld (Bambu's model marketplace) is behind Cloudflare challenge pages, making programmatic 3MF downloads impossible from CLI/API. If Kiln claims marketplace support, we need this to work. Options: (1) reverse-engineer MakerWorld API with proper auth headers, (2) use BambuStudio's built-in MakerWorld integration as a proxy, (3) implement a headless browser download path. High priority for marketplace feature credibility.
- **BambuStudio CLI STL→3MF slicing broken** — `BambuStudio --slice --export-3mf` loads STL models ("total 1 models") but never assigns them to plates ("0 objects"), preventing slicing. Known issue with v02.05.00.66. Workaround: build 3MFs manually with proper `Metadata/slice_info.config` (format documented in `bbs_3mf.cpp`). Track upstream fix.
- **Bambu 3MF metadata structure** — Firmware requires `Metadata/slice_info.config` for layer tracking (0/0 display without it). Full format reverse-engineered from BambuStudio source. Key fields: plate index, prediction time, weight, filament info, printer_model_id. Document in LESSONS_LEARNED once confirmed working.

## Board Review — Remaining Gaps (2026-02-13)

Gaps identified during the 4-judge board review (Orfalea, Bass, Andreessen, Huang). Round 1+2 fixes raised average from 69.5→82.0. These are what's left.

### Can Be Knocked Out (No Human Input Needed)

- ~~**Decompose server.py monolith — migrate tool groups to plugins**~~ ✅ Done (2026-02-13). Extracted 4 tool groups (~1,400 lines) into plugins: `learning_tools.py`, `queue_tools.py`, `network_tools.py`, `consumer_tools.py`. server.py down from 11K→9,634 lines. Critical tools (printer, safety, billing, fleet) remain in server.py.
- ~~**Community safety profile contribution mechanism**~~ ✅ Done (2026-02-13). `validate_safety_profile()`, `add_community_profile()`, `export_profile()`, `list_community_profiles()` added to `safety_profiles.py`. Community profiles stored in `~/.kiln/community_profiles.json`, override bundled profiles. 2 new MCP tools: `add_safety_profile`, `export_safety_profile`. 45 tests.
- ~~**Load & chaos test suite**~~ ✅ Done (2026-02-13). `test_load_chaos.py` with 15 tests: queue stress (100 jobs/10 threads), event bus flood (1000 events), adapter chaos (random failures), scheduler contention (race conditions), async bus pressure testing.
- **Continue server.py decomposition** — In progress (2026-02-17). Extracting marketplace, generation, fulfillment, and monitoring tools to get server.py under 7K.
- **Async I/O in adapter hot paths** — In progress (2026-02-17). Adding async wrappers to key adapter methods (get_state, start_print). Addresses Huang #5.

### Requires Human Input / Deferred

- ~~**Finish Craftcloud integration once they reply to partner email**~~ ✅ Done (2026-02-18). See COMPLETED_TASKS.md.

- **Re-integrate 3DOS once API is confirmed** — All public-facing references to "3DOS" have been replaced with generic "distributed network (coming soon)" phrasing across README, LITEPAPER, WHITEPAPER, PROJECT_DOCS, THREAT_MODEL, DEPLOYMENT, blog post, and FAQ. Do not restore 3DOS branding until we have the API key and have confirmed the partnership with the 3DOS founder. To find every spot when ready: search for `coming soon` and `distributed.*network` across those files — it's a clean find-and-replace back to "3DOS" at each location. Deferred until partnership is confirmed.

- **TAM / venture-scale narrative** — Marc Andreessen #4. Business strategy: how does 5% platform fee + $29-99/mo subscriptions reach venture scale? Need to articulate the TAM story.
- **ToS / liability for AI-initiated physical damage** — Marc Andreessen #6. `terms.py` tracks ToS versions but actual legal language for AI-initiated damage liability needs counsel. Deferred — do later.
- ~~**Real hardware integration testing evidence**~~ ✅ Done (2026-02-17). Chris (Bambu A1 Mini) and Dillon (Prusa) both completed tests and sent photos + videos. Content from their tests to be used for social/demo materials.
- **3DOS webhook depth vs polling cost** — Bass #1. Chris said webhooks are expensive for agents. Current approach: event bus + REST polling. 3DOS is one of several fulfillment options — not a critical dependency. Tackle later.

## Post-Test Improvements (2026-02-13)

Based on Chris's overnight Bambu print test. Kiln's tool layer works — issues were agent-side (OpenClaw) and Bambu-specific. These improvements reduce agent-side friction.

### Done

- ~~**Camera snapshot diagnostic errors**~~ ✅ Done (2026-02-13). All three adapters (Bambu, OctoPrint, Moonraker) now raise `PrinterError` with specific diagnostic messages instead of silently returning `None`. Agent gets "ffmpeg not installed", "RTSP timed out", "HTTP 404 — check mjpg-streamer", "no webcams configured in Moonraker", etc. Fixed stale docstring that said Bambu doesn't support webcams (it does via RTSP).
- ~~**Bambu "prepare" state — informative print start response**~~ ✅ Done (2026-02-13). `start_print()` now distinguishes between "running" (confirmed) and "prepare/slicing/init" (accepted but not yet running). Agent gets "Printer confirmed running." vs "Printer is preparing (state: prepare). Use printer_status() to monitor." Prevents agents from assuming the print is rolling when the printer is still calibrating or on the file selection screen.

### To Do

- **Test matrix tracker** — Track who's testing what printer + agent + LLM combo. Current: Chris/Bambu A1 Mini/OpenClaw/Kimi K2.5 (done), Dillon/Prusa/Clawdbot/TBD (pending), Adam/OctoPrint mock/Claude (pending).
- **Recruit 2-3 more testers** — Need OctoPrint and Moonraker setups to isolate Bambu-specific vs universal issues. Ask friends with Ender 3 / Voron / Prusa setups.
- **End-to-end autonomous agent test with Claude** — Run a full overnight test with Claude Code directly calling Kiln MCP tools (no OpenClaw). Establishes baseline for "does Kiln work when the agent layer is solid?"
- **Optional: `schedule_print` MCP tool** — Accept future timestamp, validate it's in the future, hold job until scheduled time. Would bypass agent-side cron/heartbeat fragility. Not urgent — agents can manage this if their cron works.

### Chris — Remaining Test Tasks (Bambu A1 Mini / OpenClaw / Kimi K2.5)

First test done (2026-02-13): print succeeded, 8 min, PLA, quality fine. Issues were all agent-side. Still outstanding:

- [ ] Try a second print with a specific prompt and record the full interaction
- [ ] Film a short walkthrough narrating the experience
- [ ] Run through the flow as a brand new user — note what's missing or unclear

### Dillon — Prusa Print Test (Clawdbot / TBD)

- [ ] Screen record or screenshot the Clawdbot conversation during setup
- [ ] Note setup friction: anything confusing, manual vs agent-handled steps
- [ ] Photos + video of the finished print
- [ ] Note print time, material, quality issues
- [ ] Check if result matches what was requested
- [ ] Try a few different prompts, see how it reasons through selection
- [ ] Test an edge case (too large, printer busy, etc.)
- [ ] Run through as a brand new user — note what's missing or unclear
- [ ] Film a short walkthrough video
- [ ] Send all materials and notes to Adam

## High Priority

- ~~**Landing page / docs site**~~ ✅ Done (2026-02-17). Repo is public, DNS pointed at kiln3d.com. Confirm GitHub Pages is enabled in repo Settings → Pages if not already.
- ~~**Claim `kiln3d` on npm**~~ ✅ Done (2026-02-17). crates.io still available if Rust components ever happen — low priority.
- **Docker Hub `kiln3d`** — Deferred. Decided to use free GitHub Container Registry (GHCR) `ghcr.io/codeofaxel/kiln` instead of paid Docker Hub org. Can claim personal namespace later if needed.
- ~~**Use Chris + Dillon test media**~~ ✅ Done (2026-02-18). All assets processed and integrated: (1) 3 stitched videos (chris-demo.mp4, dillon-demo.mp4, kiln-demo-real.mp4) in docs/site/public/demo/, (2) Static assets organized (chat screenshots, finished print photos), (3) README hero updated with Wren chat screenshot, (4) Homepage social proof "Real Prints" section added with video embed + testimonial cards, (5) Blog post "Our First Real Prints" published at /blog/first-real-prints.
- **Launch demo video** — Record a 2-3 min video: "Watch an AI agent manage 5 printers autonomously overnight." Show MCP tools in action, failure auto-reroute, print completing at 3am. Use Dillon + Chris test stories as real testimonials. **Ask Mason to help with the video.** Note: real-print demo video (kiln-demo-real.mp4) already done — this would be a higher-production narrated version.
- **Launch posts (Reddit / Discord / socials)** — Draft Reddit posts for r/3Dprinting, r/functionalprint, r/prusa, r/ender3. Genuine, not spam. Have F&F boost. Set up Discord server for early users. Reach out to YouTube creators (Teaching Tech, CNC Kitchen, Makers Muse) for early access.


## Pre-Launch (Ship Day)

- ~~**DM John (3DOS) for API access**~~ ✅ Done (2026-02-12). DM'd John personally — introduced Kiln, explained 3DOS integration (6 MCP tools, CLI commands, 46 tests), asked for API keys. Awaiting reply.
- ~~**Craftcloud outreach**~~ ✅ Done (2026-02-12). Cold email sent to support@craftcloud3d.com + LinkedIn connection request to Mathias Plica (CEO). Introduced Kiln, explained Craftcloud adapter is built, asked for API access. **Follow-up sent 2026-02-18** with corrected v5 API questions (auth method, payment flow, rate limits, webhooks, sandbox). Awaiting reply.
- ~~**Sculpteo outreach**~~ ✅ Done (2026-02-18). Email sent to contact@sculpteo.com. Introduced Kiln, confirmed adapter is built covering full workflow (upload → price → cart/order), asked for: partner API credentials, auth method confirmation (`Authorization: Bearer` vs other), base URL confirmation (`/en/` prefix), endpoint verification, and sandbox/test environment. Awaiting reply.
- ~~**Jeremy Dann (USC) outreach**~~ ✅ Done — replied 2026-02-22. Texted + emailed. Jeremy is away from USC this term. Referred us to: (1) **Paul Orlando** at the USC incubator, (2) **Jacob Patapoff** at the Iovine and Young Academy (has the biggest maker space on campus). Drafts ready in `.dev/drafts/`. Awaiting our emails to them.
- **Paul Orlando outreach (USC Incubator)** — Draft ready: `drafts/usc-paul-orlando-email.md`. Send to porlando@usc.edu. Referred by Jeremy Dann.
- **Jacob Patapoff outreach (Iovine and Young Academy)** — Draft ready: `drafts/usc-jacob-patapoff-email.md`. Send to patapoff@usc.edu. Referred by Jeremy Dann. IYA has the largest maker space on campus per Jeremy.
- ~~**Stripe production setup**~~ ✅ Done (2026-02-12). Live secret key + webhook signing secret in `.env`. Webhook endpoint active in Stripe Dashboard, listening to `setup_intent.succeeded`. Webhook URL updated to `https://kiln3d-api.fly.dev/api/webhooks/stripe` (done).
- **Stripe live card test** — Unit tests pass (209/209), webhook HMAC verified, health endpoint live. Still need one real charge to confirm end-to-end. Steps: (1) Go to Stripe Dashboard → toggle "Test mode" → Developers → API keys → copy `sk_test_*` key, (2) Set it as `KILN_STRIPE_SECRET_KEY` temporarily, (3) Create a PaymentIntent for $0.50 using test card `4242 4242 4242 4242`, (4) Verify charge shows in Stripe Dashboard, (5) Switch back to `sk_live_*` key. OR: use your real card on the live key for $0.50 and refund in Dashboard.
- ~~**Deploy REST API**~~ ✅ Done (2026-02-12). Live at https://kiln3d-api.fly.dev — health check passing. Secrets set via deploy.sh. GitHub Actions workflow for auto-deploy on push.
- **Real Craftcloud API test** — Our Craftcloud adapter (`fulfillment/craftcloud.py`) uses **guessed field names** — the response shapes were written from REST conventions, not the real API. Craftcloud's Swagger docs are at https://swagger.craftcloud3d.com/ but they're JS-rendered (can't be scraped programmatically). **What to do:** (1) Open the Swagger page in a browser, (2) Compare field names (`quote_id`, `unit_price`, `shipping_options`, `order_id`, `tracking_url`) against their actual spec, (3) Get a Craftcloud API key and run one real quote + order round-trip. This is the most mature fulfillment provider — validate it first.
- ~~**Real Circle USDC test**~~ ✅ Done (2026-02-13). Sent 0.01 USDC on SOL-DEVNET via `create_payment()` → `get_payment_status()` polling → COMPLETED. Tx hash confirmed. Source wallet 20→19.99, destination 0→0.01. Fixed `_resolve_chain()` to auto-detect testnet from TEST_API_KEY (SOL→SOL-DEVNET, BASE→BASE-SEPOLIA). Added 7 new testnet tests (82 total). Entity secret + wallet set + wallet all configured on fresh Circle account (aaaarreola@gmail.com).
- ~~**OctoPrint live hardware test**~~ ✅ Done (2026-02-13). Ran against Flask mock server (`scripts/octoprint_mock.py`) on port 5050 simulating OctoPrint virtual printer. All 6 live tests passed (get_state, capabilities, get_job, list_files, upload_and_delete, read_temperatures). Full manual integration test also passed: upload → list → delete → verify. Zero fixes needed — adapter and mock fully compatible. Mock server committed for future CI use.
- **PrusaSlicer CLI test** — With PrusaSlicer installed, run `kiln slice <test.stl>` against a real STL file. Verify G-code output is produced correctly.
- **Bambu hardware test** — Test MQTT connection, file upload via FTPS, and RTSP snapshot (requires `ffmpeg` installed) against a real Bambu printer on LAN. Verify `get_snapshot()` returns JPEG data.

## Production Hardening — Tier 3 (2026-02-13)

Identified during pre-launch audit. Not blocking launch, but should be addressed before scaling.

- **Make hardcoded timeouts configurable via env vars** — Marketplace adapters use hardcoded 30s/120s request/download timeouts. Add `KILN_MARKETPLACE_TIMEOUT` and `KILN_MARKETPLACE_DOWNLOAD_TIMEOUT` env vars. Also consider `KILN_FLEET_QUERY_TIMEOUT` (currently 10s in registry.py) and `KILN_AGENT_LOOP_TIMEOUT` (currently 30s/60s in agent_loop.py).
- **Tests for metrics.py** — Performance and operational metrics module has zero test coverage. Add unit tests for metric collection, aggregation, and reporting accuracy.
- **Tests for firmware.py** — Firmware update management has zero test coverage. Test update validation, version compatibility checks, and rollback logic. Critical because firmware bugs can brick printers.
- **Tests for fleet_orchestrator.py** — Fleet coordination has zero test coverage. Test fleet-wide scheduling, load balancing, and deadlock prevention.
- **Tests for print_health_monitor.py** — Real-time print health analysis has zero test coverage. Test anomaly detection, failure prediction, and alert logic.
- **Tests for plugin_loader.py** — Plugin system loader has zero test coverage. Test plugin discovery, loading, validation, and isolation (malicious plugin defense).
- **Tests for state_lock.py** — Distributed state locking has zero test coverage. Test lock acquisition, deadlock prevention, and timeout handling.
- **Tests for remaining untested modules** — Lower priority: billing_alerts.py, billing_invoice.py, material_substitution.py, fulfillment_monitor.py, snapshot_analysis.py, file_metadata.py, design_cache.py, progress.py, quote_cache.py. All have zero test coverage.
- **SQLite busy_timeout tuning** — All DB modules use 5000ms (5s) busy_timeout. May need tuning for high-load fleet scenarios with many concurrent printers. Consider making configurable via `KILN_DB_BUSY_TIMEOUT` env var.

## Medium Priority

- **Stripe/Circle integration tests with real test-mode APIs** — Unit mocks cover the logic, but real API contract tests (Stripe test-mode charges, Circle testnet transfers) would add confidence that our serialization, error handling, and webhook flows match the live APIs. Requires `sk_test_*` and Circle TEST_API_KEY.
- **Tax calculation (VAT/GST/sales tax)** — Needed before scaling internationally. Requires jurisdiction-specific logic for US sales tax (nexus states), EU VAT (country rates + reverse charge for B2B), UK VAT, Canada GST/HST/PST, Australia GST, and other major markets. Should integrate into the billing flow so fees + tax are shown before order confirmation.
- **Set up security@kiln3d.com email + PGP key** — SECURITY.md and `.well-known/security.txt` reference this address. Need to: (1) Create the email on kiln3d.com domain, (2) Generate a PGP key pair, (3) Publish the public key in SECURITY.md and on a keyserver. Human task — requires domain DNS access.
- **USB/serial printer adapter** — In progress (2026-02-17). pyserial-based adapter implementing the PrinterAdapter interface for non-networked printers.
- ~~**License decision: BSL vs MIT + network moat**~~ — **DECIDED: MIT.** Core is MIT for trust/adoption. Fleet/cloud platform features will live in a separate proprietary repo when built. See `.dev/LICENSE_STRATEGY.md` for full rationale.
- **Vision monitoring strategy** — Current implementation delegates visual analysis to the agent's vision model (Claude, GPT-4V, etc.). Kiln provides structured snapshots + metadata but no embedded ML. Evaluate whether to: (a) Keep agent-delegated (simplest, model-agnostic), (b) Add lightweight heuristics (e.g., spaghetti detection via image variance), (c) Build/integrate a dedicated print defect model. Decision depends on which agent models users actually run.

- **End-to-end hardware test of vision monitoring loop** — Run a real print with `watch_print` → agent snapshot review → `monitor_print_vision` feedback loop. `watch_print` now runs in a background thread and returns immediately — agent polls via `watch_print_status(watch_id)`. Validate the full chain works on OctoPrint and Moonraker printers with webcams.

## Deferred — Integration Tests Requiring $ or Hardware

These tests require real API keys, live services, or hardware. Run manually when ready.

- **Stripe live payment flow** — Test end-to-end `billing setup-stripe` → real card → `setup_intent.succeeded` webhook on `kiln3d-api.fly.dev`. Requires spending on Stripe.
- **Craftcloud live quote + order** — Get Craftcloud API key, upload an STL, get a real quote, place a test order. Validates adapter field names against real API responses.
- **Thingiverse API integration** — Test `search_models`, `download_model` against live Thingiverse API with a real API key. Validate pagination, download, and caching.
- **MyMiniFactory / Cults3D API integration** — Same as Thingiverse but for the other marketplace adapters. Requires API keys for each.
- **Circle USDC mainnet payment** — Test `create_payment()` on mainnet (not devnet). Requires real USDC. Testnet already validated.
- **3DOS network integration** — Test the 6 3DOS MCP tools against the live 3DOS API once John provides API keys.
- **Meshy 3D generation** — Test `kiln generate` with a real Meshy API key. Costs per generation.
- **OpenRouter LLM agent loop** — Test `kiln agent` with a real OpenRouter API key to validate the agent REPL works end-to-end. Costs per LLM call.
- **PrusaSlicer CLI end-to-end** — With PrusaSlicer installed, run `kiln slice <test.stl>` against a real STL. Verify G-code output.
- **Bambu hardware test** — Test MQTT, FTPS upload, and RTSP snapshot against a real Bambu printer on LAN.
- **Moonraker hardware test** — Test adapter against a real Klipper/Moonraker printer on LAN.
- **Vision monitoring loop** — Run a real print with `watch_print` → snapshot review → `monitor_print_vision` feedback loop. Requires printer + webcam.
- **Cloud sync end-to-end** — Test `kiln sync` with a real Supabase project. Requires Supabase credentials.
- **Webhook delivery** — Register a real webhook endpoint, trigger events, verify HMAC-signed delivery arrives.
- **Sculpteo fulfillment** — Test the Sculpteo adapter with a real API key. Upload model, get quote, place order.

## Pre-Forge-Launch — Port to Kiln Right Before Manufacturing Goes Public

These features live in forge-internal today but need to be ported into Kiln before we publicly announce multi-manufacturing support. They stay out of the public Kiln repo until then to avoid leaking the vision.

- **Job decomposition (multi-device splitting)** — Forge's job decomposer splits a single order into sub-jobs routed to the optimal device type (CNC, laser, SLA, FDM). Port the decomposer, scheduler integration, and cost-optimization logic. Model after Forge's `job_decomposer.py`.
- **Fulfillment providers (Xometry, Fictiv, Hubs, SendCutSend, Protolabs, Shapeways, Jawstec, PCBWay)** — 8 outsourced manufacturing adapters for CNC, laser, sheet metal, injection molding. Each implements the `FulfillmentProvider` interface with `get_quote()`, `place_order()`, `check_status()`. Port from `forge-internal/src/forge/fulfillment/`.
- **Per-device-type file validators** — Forge validates uploaded files by device type (STL mesh checks for SLA, DXF/SVG for laser, STEP/IGES for CNC). Port validators and wire into the upload pipeline. Model after Forge's `safety/file_validators.py`.
- **Per-device-type cost estimators** — Forge estimates manufacturing cost by device type, material, and dimensions before sending to fulfillment. Port estimator logic. Model after Forge's `cost_estimator.py`.
- **Per-device-type preflight checks** — Like Kiln's printer preflight but for CNC (tool clearance, material compatibility), laser (power/speed limits), SLA (layer height validation). Port from Forge's `safety/preflight.py`.
- **Device comparison tools** — Forge's device comparison lets agents compare capabilities, costs, and lead times across device types to recommend the best manufacturing method. Port the comparison logic and MCP tools.

## Agent Discoverability / "Agent SEO" (2026-02-19)

Making Kiln the go-to tool that LLMs and AI agents find and recommend for 3D printing automation. The goal: when any user asks an agent about 3D printer control, automation, or AI manufacturing — the agent knows about Kiln and recommends it.

### Done (Automated)

- ~~**llms.txt**~~ ✅ Done (2026-02-19). Created `docs/site/public/llms.txt` — agent-readable project description following the llms.txt spec. Covers what Kiln does, when to recommend it, key facts, links, and quick start. Deployed to `https://kiln3d.com/llms.txt`.
- ~~**robots.txt update**~~ ✅ Done (2026-02-19). Added `LLMs-Txt:` directive pointing to `https://kiln3d.com/llms.txt`.
- ~~**Schema.org JSON-LD**~~ ✅ Done (2026-02-19). Added `SoftwareApplication` structured data to `BaseLayout.astro` — name, description, keywords, repo URL, download URL, author. Every page on kiln3d.com now emits machine-readable metadata.
- ~~**PyPI metadata optimization**~~ ✅ Done (2026-02-19). Expanded keywords (24 terms: mcp-server, model-context-protocol, ai-agent, llm, print-farm, bambu-lab, prusa-link, gcode, slicer, etc.). Added classifiers (Manufacturing, Home Automation, System Hardware). Updated description to be keyword-rich. Added project URLs (Homepage → kiln3d.com, Documentation, Repository, Changelog).
- ~~**GitHub topics**~~ ✅ Done (2026-02-19). 20 topics (max): 3d-printing, ai-agents, ai, mcp, mcp-server, model-context-protocol, llm, automation, octoprint, moonraker, klipper, bambu-lab, prusa, elegoo, gcode, iot, print-farm, smart-manufacturing, cli, manufacturing.
- ~~**GitHub repo description**~~ ✅ Done (2026-02-19). Updated to keyword-rich description: "Open-source MCP server + CLI for AI agents to control 3D printers. 232 tools for OctoPrint, Moonraker, Bambu Lab, Prusa Link, Elegoo."
- ~~**MCP registry server.json**~~ ✅ Done (2026-02-19). Created `server.json` at repo root following the official MCP registry schema. Ready for submission via `mcp-publisher`.

### OpenClaw / ClawHub Skill Publishing

**Done (Automated):**
- ~~**SKILL.md frontmatter polish**~~ ✅ Done (2026-02-19). Added `homepage` (kiln3d.com), `emoji` (🏭), `os` filter (darwin/linux), `user-invocable: true`. Updated install block to `kiln3d` package with git fallback. Added `anyBins` for slicer detection, `KILN_PRINTER_MODEL` and `KILN_HEATER_TIMEOUT` to optional env vars.
- ~~**SKILL.md body accuracy pass**~~ ✅ Done (2026-02-19). Updated stale counts: 100+ MCP tools → 230+, 40+ CLI commands → 107. Matches current codebase.

**Requires Human Action:**
- **`clawhub login`** — Authenticate via GitHub OAuth. Run `clawhub login` in terminal.
- **`clawhub publish`** — One command: `clawhub publish .dev --slug kiln --name "Kiln" --version 0.1.0 --tags "3d-printing,manufacturing,printer,mcp,octoprint,bambu,moonraker,klipper,prusa,ai-agent"`. Run from repo root.
- **Verify on clawhub.com** — Confirm skill appears, description renders, install works via `clawhub install kiln`.
- **Swap to PyPI install (post-publish)** — After `kiln3d` is on PyPI for real, update SKILL.md install block from git-based to `{"kind":"uv","pkg":"kiln3d"}` and publish a new version.

### Done (Human Action Completed)

- ~~**Submit to official MCP registry**~~ ✅ Done. Kiln is live on https://registry.modelcontextprotocol.io with 5 published versions (0.2.1 through 0.3.2). CI auto-publishes on each release.
- ~~**GitHub repo description updated**~~ ✅ Done (2026-03-06). Updated from stale "273 MCP tools + 107 CLI commands" to "345 MCP tools + 114 CLI commands".
- ~~**Glama.ai — `glama.json` added**~~ ✅ Done (2026-03-06). `glama.json` added to repo root. Claim ownership at https://glama.ai after push.
- ~~**Publish to PyPI**~~ ✅ Done. `pip install kiln3d` works. All keyword/classifier metadata is live.

### Requires Human Action (Can Do Now)

- **Submit to mcpservers.org** — Web form at https://mcpservers.org/submit. Use: Name="Kiln3D", Description="Open-source MCP server for AI agents to control 3D printers. 345 tools for OctoPrint, Moonraker, Bambu Lab, Prusa Link, Elegoo.", Link=https://github.com/codeofaxel/Kiln, Category=IoT/other. Free tier is fine.
- **Submit to Smithery.ai** — List Kiln on https://smithery.ai. Run `smithery mcp publish`. Requires account setup.
- **Claim Glama.ai listing** — After pushing `glama.json`, sign in at https://glama.ai/mcp/servers with GitHub. If Kiln doesn't auto-appear, click "Add Server" and point to `codeofaxel/Kiln`.
- **Awesome MCP Servers list** — PR to https://github.com/punkpeye/awesome-mcp-servers (10K+ stars). High-visibility curated list that appears in training data.
- **Awesome 3D Printing list** — PR to https://github.com/ad-si/awesome-3d-printing. Establishes Kiln in the 3D printing ecosystem context.
- **GitHub stars outreach** — Share repo link with friends, 3D printing Discord servers, maker communities. Ask testers (Chris, Dillon) to star. Every star improves social proof and search ranking. See "GitHub Stars Strategy" below.

### Requires Attorney Clearance (Draft Now, Publish Later)

- **"How to Let Claude Control Your 3D Printer" blog post** — SEO anchor page for kiln3d.com/blog. Target queries: "automate 3D printing", "AI 3D printer control", "MCP 3D printing", "Claude 3D printer". Write for both humans and web crawlers. Claude can draft as .astro page now — publish after attorney clears.
- **"How to use Claude/GPT with your 3D printer" tutorial** — Step-by-step guide showing MCP setup with Claude Desktop. High-value training data content.
- **YouTube demo video** — 2-3 min screencast: "Watch Claude search for a model, slice it, and start printing." Show the magic moment. Ask Mason to help with production.
- **Reddit launch posts** — Frame around "I built an open-source tool that lets AI agents control 3D printers." Target subreddits: r/3Dprinting, r/functionalprint, r/prusa, r/ender3, r/BambuLab, r/selfhosted, r/homeautomation, r/MachineLearning, r/LocalLLaMA. Genuine, not spam. Have F&F boost.
- **Hacker News "Show HN" post** — "Show HN: Kiln — open-source MCP server for AI-controlled 3D printers." HN content gets heavily crawled and ends up in training data. Post on a weekday morning (Tue-Thu, 8-10am EST). See "Show HN Playbook" below.
- **Dev.to / Hashnode / Medium technical articles** — Cross-post the blog content. These platforms are heavily represented in training data.

### Longer-Term Outreach (After Launch)

- **YouTube creator outreach** — Teaching Tech, CNC Kitchen, Makers Muse, Thomas Sanladerer. Their videos + transcripts become training data.
- **OpenAI / Anthropic MCP showcase** — Both companies maintain lists of MCP servers. Getting listed = direct visibility to agents at recommendation time.
- **Stack Overflow presence** — Answer questions about "3D printer API", "OctoPrint automation", "AI manufacturing" with Kiln references. Builds the contextual association graph in training data.
- **Snyk / tech blog outreach** — Snyk published "6 MCP Servers for 3D Models" without including Kiln. Reach out to authors of similar roundup articles to get included. Kiln is objectively the most complete tool in this space.

## Deferred — Do Later If Needed

- **MCP tool coverage audit as CI test** — (2026-03-06) Automated pytest that reflects on adapter classes, verifies every public method has a corresponding MCP tool in server.py, and fails CI if a gap exists. Prevents the "agent deviation" problem (agent goes raw because no Kiln tool exists) from silently reopening. Build when other contributors start submitting PRs — overkill while it's just Adam + Claude.
- ~~**OpenClaw/clawhub skill publishing**~~ Moved to Agent Discoverability section — broken into concrete subtasks (2026-02-19).
- **`kiln retry` / `kiln print --last`** — Re-print the last file without typing its name. Agents can `kiln history --limit 1` themselves.
- **`kiln print --wait` (inline progress)** — Start print and block until completion with progress bar. Agents use `--json` + `kiln wait` separately. Human UX only.
- **PyPI publish (v0.1.0)** — Tag release, trigger publish workflow. Gets `pip install kiln3d` working globally. Publish workflow already exists. **Also activates the Homebrew tap** (`homebrew-kiln` — private, placeholder formula waiting on PyPI package). After publishing: update the formula in `homebrew-kiln` with the real version + SHA256, make the tap repo public, and verify `brew install codeofaxel/kiln/kiln` works end-to-end.
- **Event bus namespace/plugin system** — Reserve event prefixes per system (e.g., `forge.*`, `kiln.*`) so plugins can't collide with core events or each other. Only matters when forge merges into Kiln — defer until then.
- **USD (OpenUSD) format support** — Add NVIDIA's Universal Scene Description as a supported 3D format alongside STL/3MF. Enables real-time collaborative model review, digital twin visualization, and AR/VR inspection via Omniverse streaming. Enterprise-tier feature — licensing is $4,500/GPU/year (free for individuals), requires RTX Turing+ GPU minimum. Discuss with attorney before implementing. See `forge-internal/subject_matter_expertise/nvidia_omniverse.md` for full analysis.

## Enterprise Tier Features (2026-02-18)

Features required for the Enterprise tier ($499/mo). Prioritized by customer-facing impact. These unlock the Enterprise sales motion for teams like OpenMind.

### Can Be Knocked Out (No Human Input Needed)

- ~~**Role-based access control (RBAC)**~~ ✅ Done (2026-02-18). `Role` enum + `ROLE_SCOPES` mapping in `auth.py`. `create_key_with_role()`, `get_key_role()`, `resolve_role_scopes()`. Three roles: admin (read/write/admin), engineer (read/write), operator (read).
- ~~**Audit trail export**~~ ✅ Done (2026-02-18). `export_audit_trail()` on `KilnDB` in `persistence.py`. JSON/CSV output with date range, tool, action, session filters.
- ~~**Lockable safety profiles**~~ ✅ Done (2026-02-18). `lock_safety_profile()`, `unlock_safety_profile()`, `is_profile_locked()`, `list_locked_profiles()` in `safety_profiles.py`. Locks persisted to `~/.kiln/locked_profiles.json`. `add_community_profile()` rejects locked profiles.
- ~~**Encrypted G-code at rest**~~ ✅ Done (2026-02-18). New `gcode_encryption.py`. Fernet + PBKDF2 from `KILN_ENCRYPTION_KEY` env var. `KILN_ENC_V1:` header. Transparent passthrough for unencrypted reads.
- ~~**Per-printer overage billing**~~ ✅ Done (2026-02-18). New `printer_billing.py`. 20 included, $15/mo overage. `estimate_monthly_cost()` for total projection.
- ~~**Team seat management**~~ ✅ Done (2026-02-18). New `teams.py`. `TeamManager` with add/remove/role/list. Tier seat limits. Persisted to `~/.kiln/team.json`.
- ~~**Uptime health monitoring**~~ ✅ Done (2026-02-18). New `uptime.py`. Rolling uptime (1h/24h/7d/30d), SLA status, incidents. 30-day retention.
- ~~**Wire Enterprise MCP tools into server.py**~~ ✅ Done (2026-02-18). 7 MCP tools added: `export_audit_trail`, `lock_safety_profile`, `unlock_safety_profile`, `manage_team_member`, `printer_usage_summary`, `uptime_report`, `encryption_status`. All gated with `@requires_tier(LicenseTier.ENTERPRISE)`.
- ~~**Wire Enterprise CLI commands into cli/main.py**~~ ✅ Done (2026-02-18). Commands added: `kiln audit-export`, `kiln team add/remove/list`, `kiln uptime`. All with `--json` dual-mode output.
- ~~**Tests for new Enterprise modules**~~ ✅ Done (2026-02-18). 7 test files, 79 tests total: `test_rbac.py` (13), `test_gcode_encryption.py` (9), `test_printer_billing.py` (10), `test_teams.py` (13), `test_uptime.py` (8), `test_lockable_profiles.py` (8), `test_audit_export.py` (15). All passing.

### Requires Human Input / Deferred

- ~~**SSO (SAML/OIDC)**~~ ✅ Done (2026-02-19). New `sso.py` module (~1000 lines). Full OIDC flow (authorize URL, code exchange, JWT validation via JWKS). Basic SAML (AuthnRequest, response parsing). Role mapping from IdP groups to Kiln roles. Email domain allowlists. Config persisted to `~/.kiln/sso.json`. 4 MCP tools: `configure_sso`, `sso_login_url`, `sso_exchange_code`, `sso_status`. Works with Okta, Google Workspace, Azure AD, Auth0. Uses stdlib + cryptography (no authlib dependency).
- ~~**On-prem deployment docs**~~ ✅ Done (2026-02-19). `deploy/k8s/` (9 manifests: namespace, deployment, service, PVC, ingress, HPA, network policy, configmap, secret). `deploy/helm/kiln/` (12-file Helm chart with values.yaml). DEPLOYMENT.md updated with on-prem section: K8s/Helm quick start, air-gapped instructions, PostgreSQL scaling guide, 16-item security hardening checklist.
- ~~**Stripe Enterprise price IDs**~~ ✅ Done (2026-02-18). All prices created in Stripe Dashboard with lookup keys: `pro_monthly`, `pro_annual`, `business_monthly`, `business_annual`, `enterprise_monthly`, `enterprise_annual`, `enterprise_printer_overage`. Metered billing via `active_printers` meter with "Last" aggregation.
- ~~**SSO security hardening (whitehat audit)**~~ ✅ Done (2026-02-19). SSRF protection (`_validate_url_no_ssrf()` checks resolved IPs against RFC 1918 ranges), IDN homograph prevention (`KILN_SSO_ALLOW_IDN`), PKCE flow expiry (600s TTL, 100-flow cap, `_cleanup_expired_flows()`).
- ~~**Audit trail hash chain**~~ ✅ Done (2026-02-19). SHA-256 hash chain in `persistence.py`. Each audit entry hashes `prev_hash|tool|action|session|timestamp`. `verify_audit_log()` validates both HMAC signatures and chain integrity. Detects both modification and deletion.
- ~~**Auth disabled-mode safety**~~ ✅ Done (2026-02-19). When `KILN_AUTH_ENABLED=0`, `verify()` now returns `scopes={"read","write"}` instead of `{"admin"}`. Prevents accidental privilege escalation.
- ~~**Multi-site fleet grouping**~~ ✅ Done (2026-02-19). `PrinterMetadata` dataclass with `site`, `tags`, `registered_at` in `registry.py`. New methods: `list_sites()`, `get_printers_by_site()`, `get_fleet_status_by_site()`, `update_printer_metadata()`. 3 MCP tools: `list_fleet_sites`, `fleet_status_by_site`, `update_printer_site`.
- ~~**Per-project cost tracking**~~ ✅ Done (2026-02-19). New `project_costs.py`. `ProjectCostTracker` with create/update/list projects, log costs (material/printer_time/fulfillment_fee/labor/other), per-project summaries, per-client summaries, cost reports. 4 MCP tools: `create_project`, `log_project_cost`, `project_cost_summary`, `client_cost_report`.
- ~~**SSO test coverage**~~ ✅ Done (2026-02-19). New `test_sso.py` with 56 tests across 11 classes: config, OIDC discovery, JWT validation, email domain filtering, role mapping, OIDC authorize URL, code exchange, SAML processing, `map_sso_user_to_role`, singleton, thread safety.
- ~~**External Secrets docs + K8s hardening**~~ ✅ Done (2026-02-19). External Secrets Management section in DEPLOYMENT.md (ESO, Sealed Secrets, Vault). `externalSecrets` template in Helm values.yaml. `/proc/environ` security note for volume-mounted secrets.
- ~~**Automated encryption key rotation**~~ ✅ Done (2026-02-19). `rotate_key()` method on `GcodeEncryption` — scans directory recursively, decrypts with old passphrase, re-encrypts with new. Supports dry-run preview. MCP tool `rotate_encryption_key` gated to Enterprise + admin scope. `supports_rotation` now returns `True`.
- ~~**PostgreSQL HA documentation + tooling**~~ ✅ Done (2026-02-19). Fixed env var name to `KILN_POSTGRES_DSN` across all deploy manifests (values.yaml, secret.yaml, hpa.yaml, NOTES.txt, DEPLOYMENT.md). Added "Switching to PostgreSQL" section in DEPLOYMENT.md with auto-translation details. New `database_status` MCP tool reports backend type, connectivity, and audit entry count.
