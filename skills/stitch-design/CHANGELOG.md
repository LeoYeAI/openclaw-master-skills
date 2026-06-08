# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.2.3] - 2026-03-29

### Changed
- Published under new slug `google-stitch-design`.
- No functional changes since 1.2.2.

## [1.2.2] - 2026-03-29

### Changed
- Clarified runtime scope in SKILL.md and README: requires only `STITCH_API_KEY`, talks only to Google Stitch endpoints needed for generation and screenshot delivery, and stores local artifacts in `runs/`, `state/`, and `latest-screen.json`.
- Simplified setup guidance to recommend OpenClaw skill env settings or shell env configuration for `STITCH_API_KEY`.
- Documented install scope more explicitly for the bundled Node CLI dependency flow.

## [1.2.1] - 2026-03-29

### Changed
- `--design-system` now accepts only a design system name/slug and loads `design-systems/<name>.md` from a local allowlisted registry
- CLI help, README, and SKILL docs updated to describe the registry-based design system workflow more clearly
- Package and skill descriptions tightened to highlight the official Google Stitch SDK integration and the end-to-end agent workflow

### Added
- `design-systems/README.md` with the local registry convention for design system files

### Fixed
- Removed arbitrary local file path reads from the design system workflow, reducing security risk for ClawHub distribution

## [1.2.0] - 2026-03-29

### Added
- **Design System Injection** — `--design-system <name>` flag for generate/edit/variants appends `design-systems/<name>.md` from a local allowlisted registry (workaround until SDK supports design_system_id linking)
- **Device Type Inheritance** — Edit and variants automatically inherit deviceType from the source screen via `get_screen` when `--device` is not specified
- **Desktop Default** — `generate` defaults to DESKTOP when no `--device` flag is given
- **Screenshot URL Validation** — `show` validates screenshot URLs with a HEAD request and auto-refreshes expired URLs via `get_screen`
- **Variant Screenshot URLs** — `variants` result.json now includes `screenshotUrl` per variant
- **Multi-Screen Consistency Guide** — SKILL.md workflow for hub-first design, generate vs edit distinction
- **Screen Review Loop** — 4-step review/iterate workflow in SKILL.md with decision tree for edit vs post-export fix
- **Feature Coverage Planning** — SKILL.md section for feature matrix before generating
- **`inheritDeviceType()` helper** — Shared device inheritance logic for edit and variants

### Changed
- `callToolRobust()` refactored from positional parameters to Options-Object with `knownIds` for delta-based recovery
- `downloadFile()` validates Content-Type and magic bytes (PNG signature check), with `expectImage` parameter for HTML-aware downloads
- `design-system.mjs` extracted as separate module for allowlisted design system loading from `design-systems/`
- `HIRES_SUFFIX` exported as constant from `download.mjs` (was hardcoded in 4 places)
- SKILL.md fully in English (previously had mixed German/English sections)

### Fixed
- **Edit recovery picked wrong screen** — `cmdEdit` and `cmdGenerate` now snapshot screen IDs before API call; recovery accepts only new IDs (T-005)
- **Download saved HTML instead of PNG** — Content-Type + magic byte validation prevents saving error pages as images (T-006)
- **Screenshot URL token expiry** — Fresh URL fetched via `get_screen` instead of retrying expired URL (T-007)
- **Variants generated Desktop instead of Mobile** — Device type inherited from source screen (T-008)
- **Edit did not inherit device type** — Same fix as variants, discovered during review (T-008 follow-up)

## [1.1.0] - 2026-03-25

### Added
- **Screen Names** — Alias registry for human-readable screen references (`name`, `unname`, `rename`, `resolve`, `names`, `show`)
- **Event Log** — Append-only JSONL log tracking every generate/edit/variants operation with parent/child lineage
- **History & Lineage** — `history <alias>` and `lineage <alias|screenId>` commands to trace design evolution
- **Rebuild** — `rebuild` command reconstructs `names.json` from event log
- **`--name` flag** — Assign an alias inline during generate/edit/variants
- **`show` accepts screen IDs** — Preview any screen without requiring an alias first
- **Hi-res image delivery** — `show` returns Google CDN URLs; append `=w780` for full resolution
- **Variants recovery** — Delta-based recovery (screen list diff) for connection drops during variant generation
- **Corrupt state detection** — `loadNames()` throws with clear error + rebuild hint instead of silently returning empty state
- **Test suites** — 28 alias registry tests + 29 event log tests

### Changed
- `download.mjs` extracted from `artifacts.mjs` — separates HTTP download logic from local file management
- SKILL.md overhauled — image delivery workflow, architecture section, troubleshooting, updated core rules
- README rewritten with full documentation of all new features

### Fixed
- Cleaner module boundaries: file I/O (artifacts.mjs) and HTTP downloads (download.mjs) are now separate concerns

## [1.0.3] - 2026-03-24

### Fixed
- `info` command returned 0 screens — `get_project` doesn't include screen data, now correctly uses `list_screens` to fetch screens separately

## [1.0.2] - 2026-03-24

### Changed
- Extracted file I/O into dedicated `scripts/artifacts.mjs` module (separation of concerns)
- `stitch.mjs` now imports artifact helpers instead of using `node:fs` directly
- Cleaner architecture: API logic separated from local storage

### Fixed
- Module boundaries: file I/O separated from network logic for better testability

## [1.0.1] - 2026-03-23

### Fixed
- Input validation for `--count` flag (NaN guard, range 1-5)
- `slugify()` fallback to 'unnamed' on empty/special-char-only input
- Model/device default documentation aligned with SDK behavior
- State awareness rule made explicit (read `latest-screen.json` before asking)

### Added
- Root `package.json` for ClawHub publish compatibility
- `.clawhubignore` (excludes node_modules, runs, .env, latest-screen.json)
- `engines.node >= 18` in scripts/package.json
- `references/sdk-api.md` referenced in SKILL.md Core Rules

## [1.0.0] - 2026-03-23

### Added
- CLI wrapper (`scripts/stitch.mjs`) with 9 commands: `projects`, `create`, `info`, `generate`, `edit`, `variants`, `html`, `image`, `export`
- Comprehensive prompt guide (`references/prompt-guide.md`) — 4-layer framework, aesthetic vocabulary, patterns/anti-patterns, iteration loop
- SDK API reference (`references/sdk-api.md`)
- Automatic artifact saving to `runs/` with `latest-screen.json` state tracking
- Connection-drop recovery via polling for long-running operations (2-5 min)
- Support for Gemini 3.1 Pro and Gemini 3.0 Flash models
- Variant generation with refine/explore/reimagine creative ranges
- Aspect-targeted variants (layout, color scheme, images, fonts, text content)
- OpenClaw skill integration with YAML frontmatter and env gating
- SKILL.md with visual review, sketch-to-design, and component isolation workflows
