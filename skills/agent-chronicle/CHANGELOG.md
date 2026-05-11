# Changelog

## [0.7.0] - 2026-03-26
### Added
- **"On This Day" Resurfacing**: When generating a new diary entry, checks for entries from 7, 30, and 365 days ago and adds a "Looking Back" section with highlights
- **Mood & Pattern Analytics** (`scripts/analyze.py`): Mood timeline with sparkline/emoji, mood distribution, recurring topics, wins compilation, frustration tracking, trend insights
- **Cron Auto-Generation** (`--auto` flag): Non-interactive diary generation for OpenClaw cron integration; skips if entry already exists
- **Weekly Digest** (`scripts/digest.py`): Synthesizes past 7 daily entries into a weekly summary with quotes, wins, decisions, mood trends, and curiosities
- `--no-looking-back` flag to skip "On This Day" resurfacing
- `--json` flag for analyze.py (programmatic output)
- `--output` flag for analyze.py (save report to file)
- `--date` flag for digest.py (generate for a specific week)
- `--emit-task` and `--from-stdin` flags for digest.py (sub-agent workflow)
- OpenClaw cron setup documentation in SKILL.md

### Changed
- Version bumped to 0.7.0
- Updated SKILL.md with comprehensive documentation for all new features
- Updated README.md with new features

## [0.6.5] - 2026-03-26
### Fixed
- config.json now uses relative `diary_path: memory/diary/` instead of absolute `/root/clawd/...`
- `memory_integration.enabled` defaults to `false` (opt-in, not opt-out)
- Addresses ClawHub security review: no absolute system paths shipped in config

## [0.6.4] - 2026-03-26
### Changed
- README and CHANGELOG synchronized across ClawHub, GitHub, and local
- Version badges updated

## [0.6.3] - 2026-03-26
### Added
- `--month YYYY-MM` flag: export only entries from a specific month
- `--all` flag: explicit alias for default behavior
- Default output filename when `--month` is set: `Cami-Diary-YYYY-MM.pdf`
### Changed
- PDF export cron now generates monthly PDFs (smaller, faster)

## [0.6.2] - 2026-03-03
### Changed
- Synced changelog/docs and aligned package metadata

## [0.6.1] - 2026-02-11
### Added
- `.gitignore` to exclude cache, config, and export files
- Updated metadata to openclaw format
- Documentation consistency updates

## [0.6.0] - 2026-02-05
### Changed
- Removed raw HTTP calls to Gateway from scripts/generate.py
- Diary generation now uses sessions_spawn (OpenClaw-native)
- Added --emit-task CLI flag
