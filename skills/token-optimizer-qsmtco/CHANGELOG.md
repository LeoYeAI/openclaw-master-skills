# Changelog

All notable changes to the Token Optimizer skill are documented here.

## [1.3.0] - 2026-02-15

### Added
- Central configuration via `config.py` (single source of truth for tier model assignments)
- `validate()` function in config to catch misconfiguration early
- Automatic detection of OpenRouter API key from `auth-profiles.json` for `refresh-pricing`
- Weekly cronjob template for pricing refresh

### Changed
- **Model routing**: tier names now Quick/Standard/Deep (previously Haiku/Sonnet/Opus)
- **Pricing**: `token_tracker.py` now filters to only tier-relevant models (minimal cache)
- **OpenRouter integration**: fixed per-token to per-1M conversion; handles string values
- `model_router.py` default model now derives from config (Standard tier)
- Documentation updated across SKILL.md, HEARTBEAT.template.md, cronjob-model-guide.md to use actual model IDs and tier names
- `context_optimizer.py` imports config and generates AGENTS.md with dynamic model overrides
- `refresh-pricing` now more robust with prefix mapping for OpenRouter model IDs

### Fixed
- Pricing cache now correctly reflects only configured tier models (2 vs 345 entries)
- Model ID mapping for OpenRouter (raw IDs like `stepfun/step-3.5-flash:free` map to canonical `openrouter/...`)

### Security & Ops
- SECURITY.md updated to reflect optional network usage for pricing refresh
- README clarified that network use is user-initiated
- Weekly cronjob set up: `0 9 * * 1` → `refresh-pricing` with log rotation ready

[Unreleased]: Placeholder for future changes
