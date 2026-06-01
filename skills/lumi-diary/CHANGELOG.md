# Changelog

All notable changes to Lumi Diary Skill will be documented in this file.

## [0.2.0] — 2026-03-14

### Architecture

- **Adapter Pattern** — core business logic extracted to `src/lumi_core.py` (platform-agnostic). OpenClaw adapter (`src/openclaw_skill.py`) and MCP adapter (`src/mcp_server.py`) are thin wrappers.
- **Environment-based Vault** — vault root configurable via `LUMI_VAULT_PATH` env var (default: `./Lumi_Vault`).

### Data Model

- **Fragment → Annotation → Canvas** — new data philosophy replacing "Rashomon" terminology. Each node has one primary `fragment` and a list of `annotations` (companion perspectives).
- **`lumi.json` v0.2.0 schema** — `timeline` → `node` → `fragment` + `annotations[]`.

### Added

- **Git-style Hash Sharding** — `Assets/` now uses 2-char MD5 prefix subdirectories (e.g., `Assets/a1/a1b2c3d4...jpg`) for scalable media storage. Backward-compatible migration of legacy flat files.
- **Portraits System** (`Portraits.json`) — consolidated `identity.json` + `Circle_Dictionary.json` into a single registry with `milestones`, `evolving_impressions`, and `traits`.
- **`update_portrait()`** — dynamic personality/milestone updates during conversation.
- **`check_time_echoes()`** — scans Portraits for milestone dates matching today (birthday, anniversary) for proactive reminders.
- **Time Echoes Protocol** — system prompt instructs Lumi to check milestones at conversation start and generate exclusive canvases.
- **Keepsakes** (`Keepsakes.json`) — renamed from `Meme_Vault.json` with `save_keepsake()` function.
- **`.lumi` Capsule Export** (`export_capsule()`) — ZIP-based capsule containing `lumi.json`, `index.html`, and copied media files. Replaces the old base64-embedded JSON seed.
- **`.lumi` Capsule Import** (`import_capsule()`) — unzip, merge annotations for existing nodes (no overwrite of local fragments), copy assets into sharded storage.

### Changed

- **Terminology** — `rashomon_perspectives` → `annotations`, `Meme_Vault` → `Keepsakes`, `Circle_Dictionary` → `Portraits`, `rashomon_cards` → `annotation_cards`, `rashomon_stitched` → `annotation_stitched`.
- **Tools renamed** — `update_circle_dictionary` → `update_portrait`, `save_meme` → `save_keepsake`, `export_lumi_scroll` → `export_capsule`.
- **Canvas rendering** — updated to use `annotation_cards` and `keepsakes` in payload. Keepsakes gallery replaces Meme gallery.
- **MCP Server** — rewritten to call `lumi_core` instead of `handlers`.

### Removed

- **`src/handlers.py`** — split into `lumi_core.py` (core) + `openclaw_skill.py` (adapter).
- **`identity.json`** — migrated to `Portraits.json` on first load.
- **`Circle_Dictionary.json`** — migrated to `Portraits.json` on first load.
- **`Meme_Vault.json`** — renamed to `Keepsakes.json`.

## [0.1.5] — 2026-03-15

### Added

- **MCP Server** — `src/mcp_server.py` wraps all 8 tool functions as MCP tools, usable with Claude Desktop, Cursor, VS Code Copilot, and any MCP-compatible client.
- **MCP Prompt** — `lumi_persona` prompt exposes the full Lumi behavioral protocol for clients that support prompt injection.
- **pyproject.toml** — standard Python packaging with `lumi-diary` entry point for MCP server.

## [0.1.4] — 2026-03-15

### Fixed

- **Unicode control characters stripped** — removed all `U+FE0F` (Variation Selector-16) and `U+200D` (Zero Width Joiner) from SKILL.md, README.md, and handlers.py that were triggering ClawHub's prompt-injection scanner.
- **Media source validation** — `_store_media_by_hash` now rejects non-media file extensions and files from sensitive system directories (`/etc`, `/var`, `/sys`, `/proc`, `/Library`, etc.), preventing arbitrary file reads even if the agent is tricked into importing a malicious path.

## [0.1.3] — 2026-03-15

### Changed

- **Metadata alignment** — `name` field in SKILL.md now matches package.json (`lumi-diary`).
- **Removed `cron: enable` permission** — unused; removed from SKILL.md to reduce permission surface.
- **Persona rewrite** — replaced "De-robotify: Never say I'm an AI" with natural persona voice guidance; no identity concealment.
- **Consent-first group recording** — Circle Mode now requires explicit user invitation; removed "silent/invisible" language throughout SKILL.md and README.md.
- **Shadow Mode removed** — Multi-Agent Etiquette rewritten as cooperative deference with independent local journaling.
- **Prompt hygiene** — removed all hard-negation override patterns (`Never`, `forbidden`, `绝对禁止`) that triggered prompt-injection detection.

## [0.1.2] — 2026-03-15

### Security

- **Path Traversal Prevention** — all user-supplied path components (`event_name`, `group_id`, project names) sanitized via `_sanitize_path_component` and validated with `_validate_within_vault` to prevent reads/writes outside `Lumi_Vault/`.
- **HTML Injection Guard** — `_render_media_embed` rejects absolute paths, `file://` URLs, and traversal sequences; malicious paths render as safe text labels.
- **Playwright Sandbox** — screenshot browser context runs with JavaScript disabled and a route filter that blocks all requests outside the vault directory.
- **Base64 Embed Guard** — `_embed_media_base64` validates files are within the vault before reading, preventing arbitrary file exfiltration into `.lumi` seeds.

## [0.1.0] — 2026-03-14

### Added

- **Three-Context Architecture** — Solo / Circle / Event routing with isolated vault directories (`Solo/Daily`, `Solo/Projects`, `Circles/`, `Events/`).
- **Fragment Recording** (`record_group_fragment`) — capture life fragments with emotion tags, media attachments, and Rashomon stitching (multi-perspective node grouping).
- **Node Deduplication** — merge fragments from the same sender + story node instead of creating duplicates.
- **Content-Addressed Media** — MD5-hashed filenames in `Assets/` for automatic image/video/audio dedup.
- **Event Lifecycle** (`manage_event`) — start / stop / query temporary events with collision-free group namespacing (`_g{group_id}`).
- **Circle Dictionary** (`update_circle_dictionary`) — maintain group member profiles in `Brain/Circle_Dictionary.json`.
- **Meme Vault** (`save_meme`) — archive legendary moments with context tags and media.
- **Fragment CRUD** (`manage_fragment`) — search, get, update, and delete recorded fragments through dialogue.
- **Interactive HTML Canvas** (`render_lumi_canvas`) — self-contained star-trail timeline with flip cards (Rashomon), meme gallery, and dynamic emotion-based theming.
- **Social Sharing Export** (`export_lumi_scroll`) — produces HTML scroll, `.lumi` seed file (base64-embedded media), and optional PNG long image via Playwright screenshot.
- **Identity System** (`manage_identity`) — owner name setup, auto-registration of group contacts by `sender_id`, and rename binding.
- **Multi-language Support** — English and Chinese (`locale: "en" | "zh"`) for all HTML canvas UI text, CTA banners, and flip card labels.
- **Emotion Palette** — 50+ emotion-to-color mappings for visual theming.
