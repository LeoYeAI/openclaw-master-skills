# SignalRadar Skill Development Spec v3

> Status: Draft for implementation  
> Scope: Polymarket first, multi-market extensible  
> Distribution priority: ClawHub  
> Cross-platform goal: compatible with ClawHub and Claude-class AI skill ecosystems via adapter layer

## 1. Product Goal and Boundaries

### 1.1 Goals

- Low noise: no change, no push by default.
- High signal density: only meaningful deltas are delivered.
- Traceable: every push can answer why, from which baseline, and by which decision path.
- Agent-first: stable machine-readable contracts for AI-to-AI invocation.
- Extensible: Polymarket now; Kalshi/Metaculus/other markets later.

### 1.2 Boundaries

- This skill monitors and notifies. It does not execute trades.
- This skill provides data/alerts, not investment advice.
- Core protocol is platform-agnostic; platform-specific delivery/auth is in adapters.

## 2. User and Agent Experience Requirements

### 2.1 End-user Experience

- First install sends onboarding once baseline is initialized.
- Signal push must include full market question (no truncation), baseline, current value, abs delta, timestamp, and reason.
- Default behavior for repeated hits: send all hits.
- User can enable dedup and set dedup interval.
- Time display rule: always `UTC + user timezone`.

### 2.2 AI Agent Experience

- All key objects must be strict JSON contracts with schema versioning.
- Every decision output must be deterministic without requiring a strong LLM.
- Optional analysis layer can enrich text, but cannot change core decision result.
- Idempotent delivery via idempotency key.

## 3. Core Data Contracts (Normative)

### 3.1 EntrySpec

```json
{
  "schema_version": "1.0.0",
  "entry_id": "polymarket:12345:claude-5-by-april-30:evt_67890",
  "source": "polymarket",
  "market_id": "12345",
  "event_id": "evt_67890",
  "slug": "claude-5-by-april-30",
  "category": "ai_model",
  "status": "active",
  "threshold_policy": {
    "abs_pp": 5.0,
    "rel_pct": 5.0,
    "rel_pct_enabled": true
  },
  "source_tag": "system_preset",
  "owner_scope": "user",
  "created_at": "2026-02-12T03:20:00Z",
  "updated_at": "2026-02-12T03:20:00Z",
  "version": 1
}
```

Rules:

- `entry_id = {source}:{market_id}:{slug}:{event_id}`.
- Never use natural-language title as key.
- Storage timestamps must be UTC only.

### 3.2 SignalEvent

```json
{
  "schema_version": "1.0.0",
  "request_id": "9f98e47e-6e0e-4563-b7c8-87a3b19e97af",
  "entry_id": "polymarket:12345:claude-5-by-april-30:evt_67890",
  "source": "polymarket",
  "current": 84.5,
  "baseline": 59.5,
  "abs_pp": 25.0,
  "rel_pct": 42.02,
  "threshold_abs_pp": 5.0,
  "threshold_rel_pct": 5.0,
  "confidence": "high",
  "reason": "abs_pp crossed threshold",
  "ts": "2026-02-12T03:28:00Z",
  "baseline_ts": "2026-02-12T00:00:00Z",
  "volume_24h": 42000000
}
```

Trigger rule (default):

- `HIT` when `abs_pp >= threshold.abs_pp`.
- `rel_pct` is auxiliary for explanation and analytics.
- `threshold.abs_pp` default is `5.0`; user can modify globally or per entry.

### 3.3 IntentSpec

```json
{
  "schema_version": "1.0.0",
  "intent_id": "int_20260212_0001",
  "action": "batch_update_threshold",
  "entry_ids": ["polymarket:12345:claude-5-by-april-30:evt_67890"],
  "payload": {
    "abs_pp": 6.0
  },
  "requested_by": "user",
  "confirmed": true,
  "confirmed_at": "2026-02-12T03:30:00Z"
}
```

Rules:

- No state mutation without explicit `confirmed=true`.
- All applied intents must be auditable and replayable.

### 3.4 DeliveryEnvelope

```json
{
  "schema_version": "1.0.0",
  "delivery_id": "del_20260212_0001",
  "request_id": "9f98e47e-6e0e-4563-b7c8-87a3b19e97af",
  "idempotency_key": "sr:polymarket:12345:2026-02-12T03:28:00Z",
  "severity": "P2",
  "route": {
    "primary": "discord:channel:1468620745214267445",
    "fallback": ["telegram:chat:xxxx"]
  },
  "human_text": "Signal hit ...",
  "machine_payload": {
    "signal_event": {}
  }
}
```

Rules:

- Must include both human-readable text and machine-readable payload.
- Same `idempotency_key` must be safe for retries.

## 4. Configuration Contract

```json
{
  "schema_version": "1.0.0",
  "profile": {
    "timezone": "America/Los_Angeles",
    "language": "en"
  },
  "threshold": {
    "abs_pp": 5.0,
    "rel_pct": 5.0,
    "rel_pct_enabled": true,
    "per_category_abs_pp": {
      "AI Releases": 4.0,
      "Crypto": 8.0
    },
    "per_entry_abs_pp": {
      "polymarket:12345:example-slug:evt_12345": 3.0
    }
  },
  "push": {
    "merge_enabled": false
  },
  "dedup": {
    "enabled": false,
    "window_minutes": 0
  },
  "source": {
    "retries": 2
  },
  "digest": {
    "frequency": "off"
  },
  "baseline": {
    "cleanup_expired": true,
    "cleanup_ttl_days": 45
  },
  "delivery": {
    "primary": {
      "channel": "discord",
      "target": "channel:1468620745214267445"
    },
    "fallback": [
      {
        "channel": "telegram",
        "target": "chat:xxxx"
      }
    ]
  },
  "remote_policy": {
    "enabled": true
  }
}
```

Mandatory defaults:

- `threshold.abs_pp = 5.0` (user editable).
- `dedup.enabled = false` and `window_minutes = 0`.
- `digest.frequency = off`.
- Display timezone source: `profile.timezone`; fallback to inferred local timezone.

## 5. Decision and Routing Semantics

Decision outcomes:

- `BASELINE`: first seen entry, store baseline, no push.
- `SILENT`: no hit.
- `HIT`: signal generated and routed.

Dedup policy:

- Default: disabled, all hits are pushed.
- If enabled: suppress same-dimension repeats within `dedup.window_minutes`.
- Severity escalation (`P2 -> P1` or `P1 -> P0`) bypasses dedup.

Threshold precedence:

- Per-entry (`watchlist ThresholdPP` / `threshold.per_entry_abs_pp`) >
- Per-category (`threshold.per_category_abs_pp`) >
- Global (`threshold.abs_pp`).

Digest policy:

- Digest is user-level optional summary (`off|daily|weekly|biweekly`, default `off`).
- Only `watch_level=important` entries are included.
- If all entries are `normal`, no digest is emitted even when frequency is enabled.
- Important entries appear in digest even when no threshold HIT occurred.

## 6. Time and i18n Rules

- Internal storage: UTC only.
- User-facing timestamps: `UTC + user timezone`.
- Protocol keys remain English and never localized.
- Locale fallback: target locale -> `en` -> key name.

## 7. Error Model (Required for Agent Compatibility)

Standard error codes:

- `SR_VALIDATION_ERROR` (payload/schema invalid)
- `SR_SOURCE_UNAVAILABLE` (upstream API unavailable)
- `SR_TIMEOUT` (step timeout)
- `SR_ROUTE_FAILURE` (delivery failed)
- `SR_CONFIG_CONFLICT` (multi-source config conflict)
- `SR_PERMISSION_DENIED` (restricted update attempt)

Error envelope:

```json
{
  "error_code": "SR_TIMEOUT",
  "message": "Decide step timed out",
  "request_id": "9f98e47e-6e0e-4563-b7c8-87a3b19e97af",
  "retryable": true
}
```

## 8. Observability and SLO (Measurable)

Rolling 24h metrics:

- Delivery success rate = `successful_deliveries / total_delivery_attempts` (target >= 98%).
- E2E p95 latency from ingest start to push ack (target < 30s).
- Duplicate push rate per entry within 2h (target < 1 when dedup enabled).
- Trace completeness = ratio of pushes with full `request_id + baseline + reason` (target = 100%).

Audit log minimum:

- `request_id`, `entry_id`, decision outcome, route target, delivery result, error code, UTC timestamp.

## 9. Multi-Platform Compatibility Strategy

### 9.1 Core vs Adapter

- Core package: protocol, decision engine, state model, validation.
- Adapter package: platform-specific auth, routing, formatting, publishing metadata.

### 9.2 ClawHub (Primary)

- Publish full skill package to ClawHub.
- Include explicit remote-policy whitelist/blacklist and user override precedence.

### 9.3 Claude-class Platforms (Secondary)

- Reuse core protocol and scripts unchanged.
- Provide platform adapter for invocation and delivery only.
- Keep output contract identical (`SignalEvent` and `DeliveryEnvelope`) to reduce migration cost.

## 10. Delivery Package Structure

```text
signalradar/
  SKILL.md
  scripts/
    ingest_polymarket.py
    decide_threshold.py
    route_delivery.py
    validate_schema.py
    run_signalradar_job.py
    pull_notion_watchlist_entries.py
    export_monitor_jobs_md.py
    polymarket_watchlist_refresh.py
    sync_md_to_notion_v4.sh
    error_utils.py
    config_utils.py
    discover_entries.py
    plan_rollover_actions.py
  .env.example
  config.example.json
  references/
    protocol.md
    config.md
    notion-sync.md
    release-checklist.md
  assets/
    templates/
      push_default.md
```

## 11. Quality Gates Before Publish

- Schema validation passes for all protocol examples.
- Replay test confirms idempotent retries.
- Threshold test confirms `abs_pp=5` default behavior.
- Dedup test confirms default all-push and configurable suppression.
- Time rendering test confirms `UTC + user timezone`.
- Failure path test confirms non-silent error explanation.

## 12. Release and Compliance Checklist

- Publish target: ClawHub.
- Optional adapter build for Claude-class ecosystems.
- No secrets, tokens, local cache, or user private data in package.
- Explicit disclaimer: monitoring tool only, no investment advice.
- User local override remains highest precedence over remote policy.

## 13. Migration Notes (V2 -> V3)

- Consolidate duplicated chapters into this single normative spec.
- Replace ambiguous timezone rules with one rule.
- Add strict schemas and error model for agent interoperability.
- Keep old field names where possible; version with `schema_version`.

## 14. Notion Collaboration Runtime Notes (Implemented)

- `watchlist-refresh` creates/uses a single Notion directory page (`SignalRadar` by default) under the configured parent page.
- SignalRadar-related pages are centralized under that directory:
  - `polymarket_watchlist_2026` (full monitored market rows)
  - `polymarket_rollover_2026` (watchlist refresh logs)
  - `signalradar_monitor_jobs` (active cron monitor jobs exported from OpenClaw)
  - `SignalRadar_Manual_Entries` (user-editable manual additions)
- `SignalRadar_Manual_Entries` is auto-created on first `watchlist-refresh` if missing.
- Runtime parameters:
  - `--notion-page-id` (parent page id)
  - `--notion-root-page-title` (directory page title, default `SignalRadar`)
  - `--notion-manual-page-title` (manual entries page title, default `SignalRadar_Manual_Entries`)
  - `--dry-run` (watchlist-refresh dependency check only, no state mutation)
- Manual entry line formats:
  - `Category | Question | EndDate`
  - `Category | Question | EndDate | WatchLevel | ThresholdPP`
  - `Category | Question`
  - `Polymarket URL` (runtime attempts slug resolution via public API)
- Parser is tolerant to bullets and Chinese punctuation; malformed lines are skipped.
- Dedup feedback is explicit in runtime output:
  - `MERGED=N` for newly added rows
  - `SKIPPED=M EXISTING=...` for already-existing rows
- Runtime exports active monitor jobs into `memory/signalradar_monitor_jobs.md` so task-level visibility is also synced to Notion.
- Synced pages start with a `signalradar-page` code-block header to clarify page purpose, editability, and editing cautions.
- On failures, runtime emits JSON error envelope (with `error_code`, `message`, `request_id`, `retryable`, `details`) instead of plain stderr text.
- `polymarket_watchlist_refresh.py` no longer depends on a fixed workspace path; it accepts `--workspace-root` and output/state path args.

## 15. Task Model: Keyword Scan + Market Entry Monitoring

- SignalRadar currently supports both:
  - Mode-driven keyword scan tasks (`ai` / `crypto` / `geopolitics`)
  - Explicit market-entry monitoring (from `polymarket_watchlist_2026`)
- Current logic:
  - `ai` mode: if watchlist has AI entries, monitor those explicit questions first; otherwise fallback to AI keyword scan.
  - `crypto` / `geopolitics`: keyword-filtered market set.
  - `watchlist-refresh`: sync/manual-maintain entry list; does not itself emit threshold events.
- Entry inheritance:
  - User adds rows in `SignalRadar_Manual_Entries`.
  - Runtime parses rows and merges into `polymarket_watchlist_2026`.
  - Existing rows are preserved (no overwrite), duplicates are skipped with explicit feedback.
  - Subsequent monitor modes inherit the updated watchlist input automatically.

## 16. Semi-Automatic Discovery and Rollover Confirmation

- `discover_entries.py` provides topic-to-candidate discovery with relevance score for manual confirmation.
- `plan_rollover_actions.py` converts rollover markdown into `suggest_auto`/`suggest_confirm` actions using configurable threshold.
- Current release keeps final mutation manual-first (operator confirms before write-back), reducing false-positive risk.

---

## Changelog

### 2026-02-14 — Notion Database + configurability overhaul (by: Claude Opus 4.6)

- **Fixed** `sync_md_to_notion_v4.sh` fenced code block rendering: added state machine to inline Python converter to detect ` ``` ` markers and emit proper Notion `code` blocks. Previously each line fell through to paragraph handler, showing raw backticks.
- **Fixed** Manual_Entries page code block width: split long format line into 3 shorter lines to eliminate horizontal scrollbar.
- **Added** read-only page sync toggle: `notion.sync_readonly_pages` (default `false`). When off, rollover and monitor_jobs pages are not synced to Notion, reducing clutter.
- **Added** `SYNC_EXCLUDE_PATTERNS` environment variable to `sync_md_to_notion_v4.sh` for filtering files during sync loop.
- **De-hardcoded** keywords: moved `KEYWORDS` and `MANUAL_MARKETS` from `polymarket_watchlist_refresh.py` to external `config/watchlist_keywords.json`. Fallback to built-in defaults when config file is absent.
- **Added** `notion_watchlist_db.py`: Notion Database management — create/sync/query inline database with columns (问题/分类/Yes概率/24h成交额/截止日/WatchLevel/ThresholdPP/Source). Replaces plain-text watchlist display.
- **Added** `write_notion_entry.py`: Bot writes entries to both Notion Database and Manual_Entries page with auto-dedup.
- **Integrated** Notion Database sync into `run_signalradar_job.py` watchlist-refresh pipeline: after markdown sync, reads `watchlist_state.json` and calls `sync_watchlist_to_db()`.
- **Updated** `config_utils.py` DEFAULT_CONFIG, `config.example.json`, SKILL.md, `references/notion-sync.md` to reflect all changes.
- **Root cause**: Codex implementation took shortcuts (hardcoded keywords, no code block handler, no Database API), and Claude Opus 4.6 review missed "user configurability" perspective.

### 2026-02-14 — Remove panorama; fix API pagination; add push signature (by: Claude Opus 4.6)

- **Removed** `panorama` mode from `run_signalradar_job.py`: deleted `select_mode_rows()` panorama branch, removed from argparse choices and docstring.
- **Updated** SKILL.md, DevSpec v3, openclaw-runbook.md to remove all panorama references.
- **Reason**: Panorama (top-volume broad scan, no topic filtering) caused irrelevant push notifications (sports, entertainment). Removed to reduce noise.
- **Impact**: Existing panorama cron jobs should be disabled. Other modes (ai/crypto/geopolitics/watchlist-refresh) are unaffected.
- **Fixed** `fetch_markets()` API pagination: Polymarket API caps at 500 per page, previous code only fetched page 1. AI-related markets were on pages 2-3 and **never reached the skill**, causing AI mode to select 0 entries and never produce any push notifications. Now paginates up to 10 pages (5000 markets).
- **Added** `— Powered by SignalRadar` signature to all push outputs (HIT summary, digest, DeliveryEnvelope human_text).

### 2026-02-13 — Product review and gap analysis (by: Claude Opus 4.6)

- **Reviewed** full codebase from product manager perspective: functionality, runtime mechanics, deployment experience.
- **Identified** gaps between DevSpec design and Codex implementation (structured error envelopes, severity grading, per-entry thresholds, IntentSpec, config priority system, etc.).
- **Produced** prioritized action items (P0–P3) and product vision alignment analysis.
- **Validated** Codex Round 2 and Round 3 execution results (all items passed verification).

### 2026-02-12 — Round 3: config.json, per-entry thresholds, digest, discovery (by: GPT-5.3-Codex)

- **Added** `config_utils.py`: config loader with `deep_merge()`, priority CLI > config.json > defaults.
- **Added** `config.example.json`: complete config template.
- **Implemented** per-entry and per-category threshold overrides (5-level resolution hierarchy).
- **Implemented** baseline cleanup mechanism (`--cleanup-expired`, `--cleanup-ttl-days`).
- **Implemented** digest feature: `watch_level` (normal/important), `digest.frequency` (off/daily/weekly/biweekly).
- **Extended** Notion manual entry format: `Category | Question | EndDate | WatchLevel | ThresholdPP`.
- **Added** `discover_entries.py`: semi-automatic topic discovery with Jaccard similarity scoring.
- **Added** `plan_rollover_actions.py`: rollover markdown to confirmation-ready action list.
- **De-hardcoded** paths in `polymarket_watchlist_refresh.py`: added `--workspace-root` parameter.
- **Cleaned** packaging: added `.gitignore`, removed `__pycache__` and `.DS_Store`.

### 2026-02-12 — Round 2: error envelopes, dry-run, external scripts (by: GPT-5.3-Codex)

- **Added** `error_utils.py`: `build_error_envelope()` and `emit_error()` for structured JSON error output.
- **Implemented** unified JSON error envelopes across all 7 scripts (replacing stderr text).
- **Added** `--dry-run` mode: three-layer support in run_signalradar_job, decide_threshold, route_delivery.
- **Hardened** watchlist-refresh failure handling: replaced 4x `try/except: pass` with `emit_error()` + immediate return.
- **Added** `resolve_runtime_script()`: graceful degradation for external script dependencies.
- **Included** `polymarket_watchlist_refresh.py` and `sync_md_to_notion_v4.sh` in skill directory for self-contained distribution.
- **Added** `.env.example` with Notion and runtime environment template.
- **Implemented** API retry with exponential backoff in `fetch_markets()`.
- **Implemented** dynamic severity grading: P0 (≥20pp), P1 (≥10pp), P2 (<10pp); P0/P1 bypass dedup.

### 2026-02-12 — Round 1: initial implementation (by: GPT-5.3-Codex)

- **Implemented** core pipeline: `ingest_polymarket.py` → `decide_threshold.py` → `route_delivery.py`.
- **Implemented** `run_signalradar_job.py`: production cron wrapper with 5 modes (ai/panorama/crypto/geopolitics/watchlist-refresh).
- **Implemented** baseline management: per-entry JSON files, BASELINE/SILENT/HIT decision logic.
- **Implemented** `DeliveryEnvelope` with `human_text` + `machine_payload`, idempotency keys, request_id tracing.
- **Implemented** optional dedup window with configurable `window_minutes`.
- **Implemented** JSONL audit log (append-only).
- **Implemented** multi-mode monitoring with keyword filtering (AI/crypto/geopolitics) and volume-based panorama scan.
- **Implemented** Notion integration: `pull_notion_watchlist_entries.py` with format tolerance, category normalization, dedup feedback.
- **Implemented** `validate_schema.py` for protocol object validation.
- **Implemented** `export_monitor_jobs_md.py` for Notion visibility.
- **Stdlib-only**: zero external dependencies, Python 3.8+ compatible.
