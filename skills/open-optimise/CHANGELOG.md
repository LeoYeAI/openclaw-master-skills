# Changelog

## 7.0.0 — 2026-03-15

### Added
- **GUIDE.md** — Complete user guide with requirements, installation, example outputs from every script (captured from a live instance), and common workflows.
- **Chapter 14: Scripts Reference** in SKILL.md — Full script listing with usage syntax so the agent knows how to invoke every tool.
- **Quick Start section** in SKILL.md frontmatter — Requirements, install commands, first run.

### Improved
- SKILL.md frontmatter now includes version, expanded description, and tags.
- SKILL.md now has a "What's Included" table summarizing all 40 files.
- Every script's usage, arguments, and expected output documented in GUIDE.md with real examples.

## 6.0.0 — 2026-03-15

### Added
- **Fallback chain validator** — `fallback-validator.sh`. Tests every model in order, catches bricking before production.
- **Token budget enforcer** — `token-enforcer.sh`. Sets maxTokens presets (strict/moderate/normal/generous/unlimited).
- **Session replay analyzer** — `session-replay.sh`. Exchange-by-exchange cost breakdown for any session.
- **Provider cost comparison** — `provider-compare.sh`. Finds same model across providers, catches "paying for free stuff."
- **System prompt tracker** — `prompt-tracker.sh`. Snapshots prompt size over time, shows growth and cost impact.
- **Idle detection** — `idle-sleep.sh`. Extends heartbeat when user is inactive, restores on wake.
- **Webhook cost reports** — `webhook-report.sh`. Sends daily summaries to Discord, Slack, or any webhook.
- **Deduplication detector** — `dedup-detector.sh`. Finds redundant tool calls and repeated requests.
- **Multi-instance aggregator** — `multi-instance.sh`. Combines costs across multiple OpenClaw instances.
- **Preset manager** — `preset-manager.sh`. Export/import/list named config presets.
- **5 community presets** — solo-coder, writer, researcher, zero-budget, agency-team.

## 5.0.0 — 2026-03-15

### Added
- **Config backup & rollback** — `backup-config.sh` + `restore-config.sh`. Auto-backup before preset applies.
- **Heartbeat cost isolator** — `heartbeat-cost.sh`. Shows exact heartbeat spending vs what-if on other models.
- **Cost history analysis** — `cost-history.sh`. Recalculates past usage across all model tiers.
- **Provider health check** — `provider-health.sh`. Tests all models for UP/DOWN/SLOW status with latency.
- **Tool call audit** — `tool-audit.sh`. Finds unused tools, duplicates, and waste from logs.
- **Context growth monitor** — `context-monitor.sh`. Tracks context bloat and predicts compaction.
- **Config diff viewer** — `config-diff.sh`. Side-by-side current vs recommended with per-item savings.
- **Model quick-switcher** — `model-switcher.sh`. All models with status, cost, and strengths at a glance.
- **Compaction event logger** — `compaction-log.sh`. Tracks compaction and memory flush events.
- **VERSION file** — Semver tracking for update detection.
- **CHANGELOG.md** — This file.

### Improved
- `apply-preset.sh` now auto-backs-up config before applying changes
- `parse-config.js` handles JSON5/JS object literal configs (unquoted keys, trailing commas)
- `cost-audit.sh` rewritten to use parse-config.js for reliable config parsing
- `cost-dashboard.js` fixed JSON5 parsing

## 4.0.0 — 2026-03-15

### Initial Release
- SKILL.md with 13 chapters, setup flow, commands, installation guide, and principles
- Model tier reference card (`references/model-tiers.md`)
- Config templates (`references/setup-config.md`)
- Cost audit script (`scripts/cost-audit.sh`)
- Cost monitor (`scripts/cost-monitor.sh`)
- Token counter (`scripts/token-counter.sh`)
- Model availability test (`scripts/model-test.sh`)
- Preset applier (`scripts/apply-preset.sh`) — free, budget, balanced, quality
- OpenRouter setup generator (`scripts/setup-openrouter.sh`)
- HTML cost dashboard (`scripts/cost-dashboard.js`)
- Cron job templates (`scripts/cron-setup.sh`)
- JSON5 config parser (`scripts/parse-config.js`)
