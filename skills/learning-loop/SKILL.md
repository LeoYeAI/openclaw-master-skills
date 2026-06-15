---
name: learning-loop
version: 1.4.0
description: "Structured self-improvement system for AI agents with confidence decay, cross-agent sharing, and anomaly detection. Use when: (1) After debugging sessions to capture lessons learned, (2) When receiving feedback or corrections from users, (3) Before risky actions to check relevant rules, (4) Weekly to review metrics and promote proven patterns to enforced rules, (5) Setting up persistent memory that survives session compactions."
metadata:
  openclaw:
    requires:
      bins: ["python3", "bash"]
      env: []
      config: []
    user-invocable: true
  homepage: https://github.com/yoder-bawt
---

# Learning Loop

**Stop waking up stupid.**

AI agents lose everything on compaction. Every debugging session, every hard-won lesson, every correction from your human - gone. You start fresh and repeat the same failures. Your human notices. Trust erodes.

The Learning Loop is a structured self-improvement system that gives agents persistent, compounding intelligence. It captures what you learn, promotes proven patterns into hard rules, tracks your improvement over time, detects when your human is satisfied or frustrated - automatically, and now includes confidence decay and cross-agent knowledge sharing.

This isn't a toy. This is infrastructure for agents that want to get measurably better at their job, every single session.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    LEARNING LOOP v1.4.0                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  INPUT LAYER          PROCESSING LAYER        OUTPUT LAYER  │
│  ───────────          ────────────────        ────────────  │
│                                                              │
│  Events ──────────▶  Pattern Detection  ────▶  Reports      │
│    │                     │                         │        │
│    ▼                     ▼                         ▼        │
│  lessons.json       Confidence Decay          Rules         │
│    │                     │                         │        │
│    ▼                     ▼                         ▼        │
│  Promotion ◀────── Anomaly Detection ◀────── Enforcement    │
│                                                              │
│  CROSS-AGENT LAYER:                                          │
│  Export ─────▶  Portable Format  ─────▶  Import             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Data Flow:**
- **Tier 1: Events** - Raw logs of debugging sessions, mistakes, successes, feedback. Append-only, never deleted.
- **Tier 2: Lessons** - Patterns extracted from events. Tracked by applications and saves.
- **Tier 3: Rules** - Lessons promoted after 3+ successful applications with 0.9+ confidence.

**Confidence Decay:** Rules lose confidence over time using Ebbinghaus-inspired exponential decay. Stale rules (confidence < 0.5) are flagged for review.

**Cross-Agent Sharing:** Export rules as portable JSON with metadata (hashes, provenance). Import from other agents with conflict detection and trust scoring.

## When to Activate

Use the Learning Loop when:
1. **After debugging sessions** - Capture the problem, solution, and confidence level to events.jsonl
2. **Receiving user feedback** - Positive ("perfect", "exactly") or negative ("wrong", "I already told you") signals trigger automatic capture
3. **Before risky actions** - Check pre-action-checklist.md and rules.json for relevant constraints
4. **Weekly maintenance** - Run pattern detection, confidence decay, promote qualified lessons to rules, update metrics
5. **During compaction** - Flush uncaptured events to prevent knowledge loss
6. **Sharing knowledge** - Export rules for other agents, import rules from trusted sources

## What It Does

```
Events (raw)  -->  Lessons (structured)  -->  Rules (enforced)
  append-only       proven patterns           hard constraints
  events.jsonl      lessons.json              rules.json
```

**Three-tier knowledge system:**
- **Tier 1: Events** - Raw logs of debugging sessions, mistakes, successes, feedback. Append-only, never deleted.
- **Tier 2: Lessons** - Patterns extracted from events. Tracked by how many times they've been applied and how many mistakes they've prevented.
- **Tier 3: Rules** - Lessons promoted after 3+ successful applications. Loaded at boot. These are your behavioral constraints.

**Five enforcement layers** ensure learning happens even when discipline fails:
1. Boot sequence loads rules every session
2. Compaction flush saves uncaptured events before context compression
3. Heartbeat checks periodically scan for missed learning opportunities
4. Daily cron extracts events from session logs
5. Weekly cron runs pattern detection, metrics, confidence decay, and self-audit

No single layer is critical. If one fails, the others catch it.

## Quick Start

```bash
bash init.sh /path/to/workspace
```

That's it. You now have:

```
memory/learning/
├── events.jsonl          # Raw event log (append-only)
├── rules.json            # Hard behavioral rules (3 starter rules)
├── lessons.json          # Structured lessons (intermediate tier)
├── pre-action-checklist.md  # Check before risky actions
├── metrics.json          # Improvement tracking
├── BOOT.md               # Quick reference for session boot
├── parse-errors.jsonl    # JSON parsing errors (v1.4.0)
└── weekly/               # Weekly learning reports
```

### Wire It In

Add to your agent's boot instructions (AGENTS.md or equivalent):

```markdown
## Every Session
1. Read `memory/learning/rules.json` - hard behavioral rules
2. Read `memory/learning/BOOT.md` - quick reference
3. Before risky actions, check `memory/learning/pre-action-checklist.md`
4. After mistakes or debugging, append to `memory/learning/events.jsonl`
5. Check rule confidence scores - rules with < 0.5 confidence need review
```

### Set Up Automation

**Daily (e.g. 4am):**
```bash
bash extract.sh /path/to/workspace
```

**Weekly (e.g. Sunday 10pm):**
```bash
bash detect-patterns.sh /path/to/workspace
bash confidence-decay.sh /path/to/workspace        # NEW v1.4.0
bash promote-rules.sh /path/to/workspace
bash self-audit.sh /path/to/workspace
bash update-metrics.sh /path/to/workspace
```

### Optional: Compaction Flush

If your platform supports custom compaction prompts, add:

> "Append uncaptured learning events to memory/learning/events.jsonl and update rules.json if new rules emerged."

This is the safety net that catches learning even during context compression.

## Guardrails / Anti-Patterns

**DO:**
- ✓ Capture events immediately after debugging or receiving feedback
- ✓ Use structured JSON format with all required fields (ts, type, category, tags, problem, solution, confidence, source)
- ✓ Run weekly automation to promote lessons with 3+ successful applications
- ✓ Check rules.json before risky actions (account ops, shell commands, external comms)
- ✓ Use wal-capture.sh for critical details that must survive compaction
- ✓ Keep events.jsonl append-only; never delete or edit historical events
- ✓ Run confidence-decay.sh weekly to update rule confidence scores
- ✓ Export rules for cross-agent sharing using export-rules.sh

**DON'T:**
- ✗ Wait to capture events - memory degrades, details get lost
- ✗ Create rules without proven application history (minimum 3 successful applications)
- ✗ Skip the pre-action checklist for "quick" operations
- ✗ Delete events to "clean up" - use archive-events.sh for old data instead
- ✗ Assume lessons apply universally without considering context
- ✗ Manually edit rules.json - let promote-rules.sh handle promotion
- ✗ Ignore confidence scores below 0.5 - these rules need review

## Full Lifecycle Walkthrough

Here's the complete loop in action, from first mistake to enforced rule.

### Day 1: The Mistake

You're building a skill and run `find . -not -path '*/node_modules/*'` on macOS. It silently skips files. You spend 20 minutes debugging before discovering that extended attributes break `find`'s exclusion flags.

**Capture the event:**
```json
{"ts":"2026-02-07T15:00:00Z","type":"debug_session","category":"shell","tags":["macos","find","xattr"],"problem":"find -not -path silently skips files with com.apple.provenance on macOS","solution":"Pipe find output through grep -v instead of using find built-in exclusion flags","confidence":"proven","source":"skill-build"}
```

Append that line to `events.jsonl`. Done. The knowledge is captured.

### Day 3: The Lesson

The daily extraction cron runs `extract.sh`, which scans your session logs and flags patterns. You (or the weekly cron) extract a structured lesson:

```json
{
  "id": "L-001",
  "created": "2026-02-09",
  "category": "shell",
  "lesson": "On macOS, use grep -v piping instead of find -not -path for file filtering",
  "context": "Extended attributes cause find exclusion flags to silently skip files",
  "trigger": "Any find command with -not -path on macOS",
  "action": "Replace find ... -not -path X with: find ... | grep -v X",
  "confidence": "proven",
  "confidence_score": 0.9,
  "times_applied": 0,
  "times_saved": 0,
  "source_events": ["2026-02-07T15:00:00Z"]
}
```

Add it to `lessons.json`. Now it's structured and trackable.

### Day 5, 8, 12: Application

Three more times you need to filter files on macOS. Each time, your boot sequence loaded the rules. Each time, you use `grep -v` instead of `find -not -path`. Each time, you increment `times_applied` in the lesson.

### Day 14: Promotion

The weekly cron runs `promote-rules.sh`. It finds L-001 with 3+ applications and confidence >= 0.9, and auto-promotes it:

```json
{
  "id": "R-004",
  "type": "NEVER",
  "category": "shell",
  "rule": "Never use find -not -path or find ! -path on macOS. Always pipe through grep -v instead.",
  "reason": "com.apple.provenance extended attributes cause find exclusions to silently skip files",
  "created": "2026-02-21",
  "source_lesson": "L-001",
  "violations": 0,
  "last_checked": "2026-02-21",
  "last_validated": "2026-02-21",
  "validation_count": 0,
  "confidence_score": 0.9
}
```

Now it's a hard rule. Loaded at boot. Checked before action. The mistake can never happen again.

### Day 14+: Confidence Decay

After 30 days without validation, `confidence-decay.sh` runs and applies exponential decay:

```
R-004: 0.90 → 0.22 (30 days since validation)
```

The rule is now flagged for review. You validate it again by successfully applying it, and the confidence resets to 0.9.

### Day 14+: Measurement

`update-metrics.sh` tracks the trend:
- Week 1: 3 mistakes, 0 rules
- Week 2: 1 mistake, 5 rules, 2 pre-action saves
- Week 3: 0 mistakes, 8 rules, 4 pre-action saves

`self-audit.sh` scores your loop health: 100% means everything is wired correctly.

**That's the full cycle.** Raw experience becomes structured knowledge becomes enforced behavior. Compounding intelligence.

## Scripts Reference

See [references/script-reference.md](references/script-reference.md) for detailed script documentation.

| Script | Purpose | Schedule |
|--------|---------|----------|
| `init.sh` | Initialize directory structure | Once |
| `extract.sh` | Scan logs for uncaptured events | Daily |
| `detect-patterns.sh` | Tag clusters, regressions, **anomalies** (v1.4.0) | Weekly |
| `confidence-decay.sh` | **Apply Ebbinghaus decay to confidence scores** (v1.4.0) | Weekly |
| `export-rules.sh` | **Export rules for cross-agent sharing** (v1.4.0) | Manual |
| `import-rules.sh` | **Import rules with conflict detection** (v1.4.0) | Manual |
| `promote-rules.sh` | Promote lessons to rules | Daily/Weekly |
| `self-audit.sh` | Health score (23 checks, A-D) | Weekly |
| `update-metrics.sh` | Weekly metrics snapshot | Daily/Weekly |
| `feedback-detector.sh` | Detect human signals | Per-message |
| `track-violations.sh` | Link mistakes to rules | Daily |
| `track-applications.sh` | Track lesson applications | Daily |
| `rule-check.sh` | Dynamic rule lookup | On-demand |
| `archive-events.sh` | Roll off old events | Monthly |
| `wal-capture.sh` | Write-Ahead Log capture | Per-message |
| `inject-rules.sh` | Inject rules into agent context | On-demand |

All scripts accept workspace directory as first argument. Default is current directory.

## Formats

See [references/formats.md](references/formats.md) for event and rule JSON schemas.

**5 event types:** mistake, success, debug_session, feedback, discovery
**4 rule types:** MUST, NEVER, PREFER, CHECK

### Rule Schema (v1.4.0)

```json
{
  "id": "R-001",
  "type": "MUST|NEVER|PREFER|CHECK",
  "category": "shell|auth|memory|...",
  "rule": "The behavioral constraint",
  "reason": "Why this rule exists",
  "created": "2026-02-21",
  "source_lesson": "L-001",
  "violations": 0,
  "last_checked": "2026-02-21",
  "last_validated": "2026-02-21",      // NEW v1.4.0
  "validation_count": 0,               // NEW v1.4.0
  "confidence_score": 0.9,             // NEW v1.4.0
  "review_flagged": false              // NEW v1.4.0
}
```

## Cross-Agent Sharing

Share learned rules between agents:

**Export rules:**
```bash
# Export all rules
bash export-rules.sh /path/to/workspace --output my-rules.json

# Export only shell rules
bash export-rules.sh /path/to/workspace --category shell --output shell-rules.json
```

**Import rules:**
```bash
# Preview import
bash import-rules.sh /path/to/workspace other-agent-rules.json --dry-run

# Import with custom trust threshold
bash import-rules.sh /path/to/workspace other-agent-rules.json --trust 0.8

# Import all rules above default threshold (0.5)
bash import-rules.sh /path/to/workspace other-agent-rules.json
```

Features:
- **Integrity verification:** Rules include SHA256 hashes
- **Conflict detection:** Similar rules are flagged before import
- **Trust scoring:** Imports are scored based on rule count, confidence, and diversity
- **Provenance tracking:** Import metadata preserved in rules

## Troubleshooting

### events.jsonl is corrupted

**Symptoms:** Scripts report JSON parse errors, metrics show fewer events than expected.

**Solution:**
1. Check `parse-errors.jsonl` for details on corrupted lines
2. Backup: `cp events.jsonl events.jsonl.backup`
3. Try to repair by removing bad lines:
   ```bash
   python3 -c "
   import json
   with open('events.jsonl') as f:
       for line in f:
           line = line.strip()
           if line:
               try:
                   json.loads(line)
                   print(line)
               except:
                   pass
   " > events.jsonl.fixed
   mv events.jsonl.fixed events.jsonl
   ```
4. If still broken, archive and start fresh with `init.sh`

### Rules not loading at boot

**Symptoms:** Agent repeats mistakes that have rules, rules.json is never read.

**Solution:**
1. Verify JSON validity: `python3 -c "import json; json.load(open('rules.json'))"`
2. Check AGENTS.md includes: `Read memory/learning/rules.json`
3. Check file permissions: `ls -la memory/learning/rules.json`
4. Check for lock file: if `.lockfile` exists, another process may be stuck

### Parse errors in parse-errors.jsonl

**Symptoms:** JSON lines are being skipped, data loss occurring.

**Solution:**
1. Check parse-errors.jsonl: `cat memory/learning/parse-errors.jsonl`
2. Common causes:
   - Manual editing of events.jsonl introducing syntax errors
   - Concurrent writes without proper locking (fixed in v1.4.0)
   - Encoding issues (must be UTF-8)
3. Fix the source of bad data
4. Clear parse-errors.jsonl after review: `> memory/learning/parse-errors.jsonl`

### Lock contention errors

**Symptoms:** Scripts exit with "Could not acquire lock" error.

**Solution:**
1. Check for stuck processes: `lsof memory/learning/.lockfile`
2. Kill stuck process if safe: `kill <pid>`
3. Remove stale lock file: `rm memory/learning/.lockfile`
4. Re-run the script

### Confidence decay not working

**Symptoms:** All rules show confidence 0.9, no decay applied.

**Solution:**
1. Verify `last_validated` field exists in rules (v1.4.0 schema)
2. Run `init.sh` to backfill missing fields
3. Check that rules are older than 1 day (no decay on same-day rules)
4. Verify `confidence-decay.sh` is in your weekly cron

### Import conflicts

**Symptoms:** Import reports conflicts, rules not imported.

**Solution:**
1. Review conflict report carefully
2. If rules are truly different, import manually:
   - Edit the exported JSON to change the rule text
   - Re-import with `--trust 0.9` to force review mode
3. If rules are duplicates, skip import

## Customization

See [references/customization.md](references/customization.md) for tuning feedback patterns, categories, promotion thresholds, and pre-action checklists.

## Changelog

See [references/changelog.md](references/changelog.md) for version history.

Current: v1.4.0 (Confidence decay, cross-agent sharing, anomaly detection, parse error logging)

## Requirements

- `python3` 3.8+ and `bash`
- `flock` (usually part of util-linux, available on macOS via util-linux or coreutils)
- A workspace directory with `memory/` for file storage
- An agent that reads files at boot (AGENTS.md or equivalent)

No external APIs. No dependencies beyond Python and Bash. Runs anywhere.

## Philosophy

Most agents are goldfish with tool access. They solve the same problem five times and charge you for each one. The Learning Loop breaks that cycle by treating every session as training data for the next one.

Build it once. Let it compound. Get measurably better every week.

Share what you learn. Import what others discovered. Collective intelligence beats isolated learning.
