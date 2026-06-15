# Changelog

## 1.4.0 (2026-02-11)

### Confidence Decay + Cross-Agent Sharing + Anomaly Detection

**Phase 3 milestone: Production-grade learning system.** The learning loop now handles the full lifecycle of knowledge: capture, validation, decay, and sharing. This release addresses all critical gaps identified in the improvement plan.

#### Confidence Decay (NEW)
- `confidence-decay.sh` - Applies Ebbinghaus-inspired exponential decay to rule/lesson confidence scores
- Rules lose confidence over time if not validated: `max(0.3, exp(-0.05 * days_since_validation))`
- Stale rules (confidence < 0.5) automatically flagged for review
- Backwards compatible: adds `last_validated`, `validation_count`, `confidence_score` fields to existing rules
- Run weekly via cron to keep confidence scores accurate

#### Cross-Agent Knowledge Sharing (NEW)
- `export-rules.sh` - Export rules as portable JSON with integrity verification
  - Includes SHA256 hashes for each rule
  - Metadata: agent handle, export timestamp, category statistics
  - Optional category filtering
  - Manifest hash for entire export verification
  
- `import-rules.sh` - Import rules from other agents with conflict detection
  - Trust scoring based on rule count, confidence, and diversity
  - Configurable trust threshold (default: 0.5)
  - Automatic conflict detection using text similarity
  - Provenance tracking (imported_from, imported_at, import_hash)
  - Dry-run mode for previewing changes

#### Anomaly Detection (NEW)
- Added to `detect-patterns.sh`
- Calculates daily event counts over rolling 7-day window
- Z-score analysis for spike detection (threshold: 2.5)
- Outputs anomaly alerts in weekly report
- Distinguishes between spikes (📈) and drops (📉)

#### Regression Detection Enhancement
- Enhanced in `detect-patterns.sh`
- Compares recent mistakes against historical rule creation dates
- Calculates days-since-fix and likely cause (context_drift vs rule_violation)
- Reports specific rule IDs that were violated

#### Critical Fixes (v1.3.1 Hotfixes)
- **Silent JSON parsing fixed in ALL 7 scripts**
  - `detect-patterns.sh`, `track-violations.sh`, `track-applications.sh`
  - `promote-rules.sh`, `self-audit.sh`, `update-metrics.sh`, `feedback-detector.sh`
  - All now log parse errors to `parse-errors.jsonl` instead of silently dropping data
  
- **File locking for concurrency safety**
  - All scripts that write JSON files now use flock-based locking
  - Prevents data corruption from parallel cron jobs
  - Lock timeout: 10 seconds with error exit
  
- **Input validation on all scripts**
  - Validates workspace exists and is writable
  - Prevents running against system directories (/etc, /bin, /usr, etc.)
  - Checks required files exist before proceeding
  - Consistent error codes: 1=config error, 2=corruption, 3=lock contention

#### Documentation Updates
- Added architecture overview diagram to SKILL.md
- Added comprehensive troubleshooting section
- Documented all new scripts with examples
- Updated rule schema to include v1.4.0 fields
- Added cross-agent sharing workflow examples

#### Infrastructure Improvements
- Consistent header comments across all scripts
- All scripts export SCRIPT_NAME for error tracking
- Parse errors include script name for debugging
- Lock file: `.lockfile` in learning directory

---

## 1.3.0 (2026-02-08)

### WAL Protocol + P2 Complete

**Phase 2 milestone: ALL 5 items complete.** The learning loop is now a fully closed system - events flow in, patterns are detected, lessons are extracted, rules are promoted, violations are tracked, and every agent instance (including cron jobs) boots with the full rule set.

#### Cross-Session Rule Loading (P2 final item)
- `inject-rules.sh` - Generates compact, category-filtered rule blocks for cron agent payloads
- All cron agents that do external work now boot by reading BOOT.md first
- No more isolated agents repeating mistakes the main session already learned from

#### WAL Protocol Integration

Adopted Write-Ahead Logging from proactive-agent (Hal Stack) skill and adapted it to the learning loop architecture. The WAL protocol ensures critical details (corrections, decisions, preferences, facts) are written to SESSION-STATE.md BEFORE the agent responds, preventing context loss during compaction.

**New Script:**
- `wal-capture.sh` - Write-Ahead Log capture. Types: correction, decision, preference, fact, blocker. Optionally cross-posts to events.jsonl with `--event <category>`.

**New File:**
- `SESSION-STATE.md` (workspace root) - Active working memory / WAL target. Added to boot sequence (step 2) and compaction checklist.

**Integration Points:**
- AGENTS.md updated with WAL Protocol section (scan every message for triggers)
- BOOT.md updated (WAL check appears before guard check)
- Pre-action checklist updated with WAL reference
- Boot sequence now: NOW.md -> SESSION-STATE.md -> SOUL.md -> USER.md -> daily notes -> errors -> rules -> checklist -> MEMORY.md

**Origin:** Inspired by proactive-agent v3.1.0 by Hal Labs. Adapted to integrate with our learning loop events, rules, and guard system rather than being standalone.

---

## 1.2.0 (2026-02-08)

### Full Audit & Gap Closure Update

Comprehensive audit revealed infrastructure was solid but the loop wasn't closing - rules documented mistakes but didn't prevent them at the moment of action.

**New Scripts:**
- `track-violations.sh` - Auto-links mistake events to rule violation counts. Runs daily.
- `track-applications.sh` - Auto-links success events to lesson application counts. Closes the feedback loop for promotion pipeline.
- `rule-check.sh` - Dynamic rule injection. Given an action description, returns relevant rules sorted by relevance. Call before risky operations.
- `archive-events.sh` - Moves events older than N days to monthly archive files. Keeps hot path lean.

**Data Fixes:**
- Unified categories from 25 to 8: memory, auth, infra, shell, social, tooling, comms, learning
- Consolidated event types from 9 to 5: mistake, success, debug, feedback, discovery
- Normalized all rule schemas to 9 canonical fields (id, type, category, rule, reason, created, source_lesson, violations, last_checked)
- Event deduplication (removed near-duplicate timestamp+category+type entries)
- Accurate violation counts from manual incident review (18 real violations across 11 rules)

**Pipeline Improvements:**
- extract.sh bash arithmetic bug fixed (grep -c output parsing on macOS)
- Daily cron now runs: extract -> track-applications -> track-violations -> promote-rules -> update-metrics
- Weekly cron now runs: detect-patterns -> track-violations -> promote-rules -> self-audit -> update-metrics -> BOOT.md regen
- Duplicate cron jobs disabled (kept single daily + weekly)

**Stats After Audit:**
- 29 rules (28 + 1 auto-promoted during audit)
- 26 lessons (14 new extracted from 76 events)
- 76 events (deduped from 78)
- 19/26 lessons promoted to rules
- Self-audit: 22/23 (96%)

---

## 1.1.0 (2026-02-07)

### Competitive Intelligence Update

Analyzed 5 competing ClawHub skills and integrated the best ideas:

**New Features:**
- Confidence scoring on lessons (0.0-1.0 numeric, replaces binary testing/proven)
- Feature request detection ("can you also...", "I wish you could...")
- Knowledge gap detection ("that's outdated", "that's not what that means")
- Write-Ahead Log (WAL) rule: write context before responding, never after
- 80+ feedback signal patterns (up from 40)
- Backward-compatible with v1.0 lesson format (missing confidence_score defaults to 1.0)

**Improvements:**
- promote-rules.sh now requires confidence_score >= 0.9 AND times_applied >= 3
- feedback-detector.sh handles 5 signal categories (was 3)
- feedback-signals.json v1.1 with correction, feature_request, and knowledge_gap sections

**Sources:** Elite Longterm Memory (WAL protocol), Self-Improving Agent (detection triggers), Continuous Learning (confidence scoring)

---

## 1.0.0 (2026-02-07)

### Initial Release

**Core System:**
- Three-tier knowledge system: Events (JSONL) -> Lessons (JSON) -> Rules (JSON)
- Five enforcement layers for redundant learning capture
- Pre-action checklist system for mistake prevention
- Weekly metrics tracking with satisfaction scoring

**Scripts:**
- `init.sh` - One-command workspace initialization with starter rules
- `extract.sh` - Daily log scanner for uncaptured learning signals
- `detect-patterns.sh` - Weekly pattern detection, tag clustering, regression checking
- `promote-rules.sh` - Automatic lesson-to-rule promotion pipeline (3+ applications)
- `self-audit.sh` - 23-check health evaluation with A-D grading
- `update-metrics.sh` - Weekly metrics snapshot calculator
- `feedback-detector.sh` - Human feedback signal detection and auto-capture

**Feedback Detection:**
- 60+ signal patterns across positive, negative, and directive categories
- Configurable scoring thresholds for auto-capture
- Customizable via `feedback-signals.json`

**Quality:**
- All scripts tested on fresh and populated workspaces
- Zero hardcoded paths - workspace directory passed as argument
- Graceful degradation on missing files
- Passes skill-auditor security scan with clean PASS verdict
