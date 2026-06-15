# Scripts Reference

| Script | Purpose | Schedule |
|--------|---------|----------|
| `init.sh` | Initialize learning directory structure | Once at setup |
| `extract.sh` | Scan daily logs for uncaptured events | Daily cron |
| `detect-patterns.sh` | Find tag clusters, check regressions, detect anomalies | Weekly cron |
| `confidence-decay.sh` | Apply Ebbinghaus decay to rule/lesson confidence | Weekly cron |
| `export-rules.sh` | Export rules as portable JSON for sharing | Manual |
| `import-rules.sh` | Import rules from other agents with conflict detection | Manual |
| `promote-rules.sh` | Promote lessons with 3+ applications to rules | Daily/Weekly |
| `self-audit.sh` | Score the loop's health (23 checks, A-D grading) | Weekly cron |
| `update-metrics.sh` | Calculate weekly metrics snapshot | Daily/Weekly |
| `feedback-detector.sh` | Detect human feedback signals in messages | Per-message (inline) |
| `track-violations.sh` | Link mistake events to rule violation counts | Daily cron |
| `track-applications.sh` | Link success events to lesson application counts | Daily cron |
| `rule-check.sh` | Dynamic rule lookup before risky actions | On-demand |
| `archive-events.sh` | Move old events to monthly archive files | Monthly/manual |
| `wal-capture.sh` | Write-Ahead Log - capture critical details before responding | Per-message |
| `inject-rules.sh` | Inject rules into agent context (for cron agents) | On-demand |
| `guard.sh` | Pre-action rule checking with save tracking | Per-action |

All scripts accept a workspace directory as the first argument. Default is current directory.

## Exit Codes

All scripts return consistent exit codes:
- **0** - Success
- **1** - Configuration error (missing files, invalid arguments)
- **2** - Data corruption detected
- **3** - Lock contention (retry suggested)

## extract.sh

Scans daily log files (`memory/YYYY-MM-DD.md`) for signal patterns: debugging mentions, lesson keywords, feedback signals, new capabilities. Outputs relevant sections for agent review.

**Note:** This is a signal scanner, not autonomous extractor. Creating well-structured events requires LLM judgment. Bad events are worse than no events.

## detect-patterns.sh

Comprehensive pattern detection with multiple outputs:
- **Overview:** Event counts by type and category
- **Tag Clusters:** Recurring tags that suggest patterns
- **Promotion Candidates:** Lessons with 3+ applications ready for rule promotion
- **Regression Check:** Mistakes that match existing rule categories
- **Anomaly Detection (v1.4.0):** Z-score analysis of daily event counts
- **Self-Audit Summary:** Quick health checks
- **Recommendations:** Auto-generated action items

## confidence-decay.sh

Applies Ebbinghaus-inspired exponential decay to rule and lesson confidence scores.

**Decay Model:**
- Formula: `max(0.3, confidence * exp(-0.05 * days_since_validation))`
- After 30 days: ~22% of original confidence
- After 60 days: ~5% of original confidence
- Floor at 0.3 to prevent complete loss

**Outputs:**
- List of rules/lessons with updated confidence scores
- Stale rules report (confidence < 0.5)
- Summary statistics

**Usage:**
```bash
bash confidence-decay.sh /path/to/workspace
bash confidence-decay.sh /path/to/workspace --dry-run  # Preview only
```

## export-rules.sh

Export rules as portable JSON for cross-agent sharing.

**Features:**
- SHA256 hashes for integrity verification
- Metadata: agent handle, timestamp, statistics
- Optional category filtering
- Manifest hash for entire export

**Usage:**
```bash
# Export all rules
bash export-rules.sh /path/to/workspace --output rules-export.json

# Export only shell rules
bash export-rules.sh /path/to/workspace --category shell --output shell-rules.json

# Export to stdout
bash export-rules.sh /path/to/workspace
```

## import-rules.sh

Import rules from another agent with conflict detection.

**Features:**
- Trust scoring based on rule count, confidence, diversity
- Conflict detection using text similarity
- Provenance tracking
- Dry-run mode for previewing

**Trust Factors:**
- Number of rules (more = more established)
- Average confidence of imported rules
- Category diversity
- Presence of manifest hash

**Usage:**
```bash
# Preview import
bash import-rules.sh /path/to/workspace other-agent-rules.json --dry-run

# Import with custom trust threshold
bash import-rules.sh /path/to/workspace other-agent-rules.json --trust 0.8

# Import with default threshold (0.5)
bash import-rules.sh /path/to/workspace other-agent-rules.json
```

## feedback-detector.sh

Detects human satisfaction/frustration signals:

```bash
bash feedback-detector.sh /path/to/workspace "this is perfect, exactly what I needed"
# Output: JSON with signal_score: 2.0, auto-captures positive feedback event

bash feedback-detector.sh /path/to/workspace "I already told you not to do that"
# Output: JSON with signal_score: -1.5, auto-captures negative feedback event
```

Patterns defined in `feedback-signals.json` and fully customizable.

## self-audit.sh

Evaluates 23 checks across 6 categories:
- **File health** - required files exist and are populated
- **Event quality** - count, type diversity, category coverage, freshness
- **Rule quality** - count, type variety, lesson traceability, confidence scores
- **Lesson quality** - count, promotion rate, application tracking
- **Enforcement chain** - boot sequence, heartbeat, weekly reports
- **Loop effectiveness** - meta-learning events, no repeated mistakes, guard usage

Outputs letter grade (A-D) and specific improvement recommendations.

## File Locking

All scripts that write to JSON files use flock-based locking:
- Lock file: `.lockfile` in learning directory
- Timeout: 10 seconds
- Shared locks for reading, exclusive locks for writing
- Prevents data corruption from concurrent cron jobs
