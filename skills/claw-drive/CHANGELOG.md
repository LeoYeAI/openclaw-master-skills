# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-02-17

### Added
- `--name` flag for `store` command — specify clean filenames instead of preserving ugly originals
- `insurance` category (policies, ID cards, claims, coverage docs)
- Migration section in README with full workflow documentation
- Test for `--name` flag (37 tests total)

### Fixed
- Test suite no longer clobbers `~/.config/claw-drive/config` (redirects to temp config via env var)
- `sync status` daemon detection uses `launchctl list <name>` directly instead of grep
- SKILL.md rewritten to reference CLI commands instead of manual cp/hash/index workflow
- Stale `claw-drive-sync` references updated to `claw-drive sync <subcommand>`

## [0.1.0] - 2026-02-17

### Added
- Initial release
- CLI with subcommands: `init`, `store`, `search`, `list`, `tags`, `status`, `sync`
- Auto-categorization into 9 file categories
- Tag-based cross-category search via INDEX.md
- SHA-256 content-based deduplication
- Google Drive sync daemon (fswatch + rclone) with launchd integration
- Per-category privacy controls via `.sync-config` exclude list
- JSON output mode (`--json`) for all commands
- OpenClaw skill integration via SKILL.md
