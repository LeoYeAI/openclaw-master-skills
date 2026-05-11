# Cross-Ref Roadmap

## Completed

### Tier 1 (Core Features)

- [x] **Thematic clustering** — Group connected findings by shared PR/issue numbers
      into clusters with auto-generated themes (union-find approach)
- [x] **Actionability scoring** — 0-10 rubric scoring clusters by state, confidence,
      engagement, and ambiguity. Drives report ordering and action recommendations.
- [x] **Extended actions** — Close and label operations beyond commenting, with strict
      ordering (comment → label → close) and confidence gates.
- [x] **Hard-stop / manual_review_required** — First-class status that propagates from
      subagent discovery through verification and into a dedicated report section.
      Ambiguous findings never get automated actions.
- [x] **Evidence verification (Phase 3b)** — Single verifier agent fetches deeper data
      (gh pr diff, gh issue view --json body,comments) to confirm/reject candidates.
- [x] **Decision principles** — references/principles.md with evidence-over-narrative,
      confidence specifics, credit preservation, conservative defaults, reversibility.
- [x] **Dry-run as default mode** — `plan` mode always runs first. User must explicitly
      opt into `execute` mode after reviewing findings.
- [x] **Rate-limit engineering** — Jitter-based intervals (75-135s), breathing pauses
      (8-15 min every 30-50 comments), exponential backoff (2→4→8→16min, 30min cap),
      rate-limit vs permanent error differentiation, atomic progress file writes,
      5-minute grace period on resume after rate-limit exit.

---

## Tier 2: High-Value Improvements

Priority-ordered. Each item includes the rationale and rough scope.

### 5. MCP Tool Integration
**Source**: issue-prioritizer pattern
**What**: Expose cross-ref as a structured MCP tool (not just a skill). This allows
other agents/tools to invoke cross-ref programmatically and consume structured JSON
output instead of reading Markdown reports.
**Why**: Enables composition — e.g., an issue triage agent could call cross-ref to
check for duplicates before assigning priority. Also enables CI integration.
**Scope**: Medium. Requires defining tool schema (input params, output JSON), creating
an mcp-tool.json descriptor, and a thin wrapper that runs the existing phases.

### 6. Agent Persona (SOUL.md)
**Source**: dedupe skill (constitution.md) + issue-prioritizer (SOUL.md)
**What**: Create a SOUL.md file that defines the agent's voice, values, and behavioral
guardrails in a way that's more evocative than principles.md.
**Why**: principles.md is rule-based. A persona file gives the agent *judgment* — how
to weigh competing concerns, what tone to use in edge cases, when to escalate vs.
decide. The dedupe skill's constitution is an excellent example.
**Scope**: Small. Write the file, reference it from SKILL.md alongside principles.md.

### 7. External Config File (config.yaml)
**Source**: issue-prioritizer pattern
**What**: Move all configurable parameters (batch_size, confidence_threshold, rate limits,
daily budget, etc.) from inline SKILL.md values to a `config.yaml` file.
**Why**: Operators can tune behavior without editing the skill. Enables per-repo configs.
Also makes rate-limit parameters machine-readable for the shell scripts.
**Scope**: Small-medium. Create config.yaml, update SKILL.md to read from it, update
shell scripts to accept config path.

### 8. AGENTS.md Subagent Specification
**Source**: issue-prioritizer pattern
**What**: Create an AGENTS.md file that formally defines each subagent role (batch
analyzer, verifier), their inputs/outputs, and expected behavior.
**Why**: Currently the subagent prompts are inline in SKILL.md. AGENTS.md makes it
easier to iterate on subagent behavior independently and enables the MCP tool to
reference specific agent specs.
**Scope**: Small. Extract existing prompts into structured format.

### 9. Timeline Decay Scoring
**Source**: issue-prioritizer (age-based scoring)
**What**: Add a time-decay factor to the actionability score. Older clusters (where all
items are >6 months old) score lower. Recent clusters (items from last 30 days) get a
small bonus.
**Why**: A 2-year-old pair of duplicate PRs is less actionable than one from last week,
even if both are open. Currently the score doesn't consider age at all.
**Scope**: Small. Add `created_at` comparison logic to scoring, add decay signal to
the scoring table.

### 10. Comment Edit Support (PATCH)
**Source**: user-provided rate-limit guidance
**What**: When cross-ref has previously commented on an item, use PATCH to update the
existing comment instead of creating a new one. Track comment IDs in progress file.
**Why**: Avoids comment spam on re-runs. If the analysis improves (new links found),
the existing comment can be updated in-place. Also reduces total comment count against
the daily budget.
**Scope**: Medium. Requires tracking comment IDs per item, checking for existing comments
before posting, using `gh api -X PATCH` for updates.

---

## Tier 3: Nice-to-Have

### 11. Stale Link Cleanup
**What**: Find existing cross-references (#N mentions) that point to closed/deleted
items or items that have diverged from the original connection. Report as "stale links."
**Scope**: Medium. Requires parsing existing comments, validating referenced items.

### 12. PR Conversation Context
**What**: Analyze PR review comments (not just body) for deeper evidence during
verification. Reviewers often mention related PRs in their comments.
**Scope**: Medium. Additional API calls during Phase 3b, extended jq parsing.

### 13. Label-Based Filtering
**What**: Allow users to filter analysis by label (e.g., "only look at PRs labeled
`bug`" or "skip PRs labeled `dependencies`").
**Scope**: Small. Add filter logic to Phase 2 batch construction.

### 14. Issue Template Detection
**What**: Auto-detect issue types (bug report, feature request, question) from
template structure and weight them differently in scoring.
**Scope**: Small. Pattern matching on issue body structure.

### 15. Webhook/Incremental Mode
**What**: Instead of bulk scanning, run incrementally on new PRs/issues as they arrive.
Could be triggered by GitHub webhooks or a periodic cron.
**Scope**: Large. Requires persistent state, incremental index updates, event handling.

---

## Rate-Limit Engineering Guide

This section documents the anti-abuse patterns implemented in `post-comments.sh`
and referenced by `commenting-strategy.md`. All patterns below are implemented
and tested.

### Why This Matters

GitHub's abuse detection is aggressive and poorly documented. The public rate
limit is 5000 requests/hour, but content-creating endpoints (comments, labels,
closes) have much stricter secondary limits. Getting rate-limited can block the
entire `gh` CLI token for minutes to hours.

### Jitter-Based Intervals (Implemented)

**Never use fixed intervals between comments.** Fixed-rate patterns are exactly
what abuse detection looks for. The script posts one comment at a time, then
sleeps a random duration (default 75-135s). The base target is ~90s between
comments, with ±45s of jitter making the pattern look organic.

```bash
# post-comments.sh — jitter_sleep()
jitter_sleep() {
  local min_secs="${1:-$JITTER_MIN}"
  local max_secs="${2:-$JITTER_MAX}"
  local range=$((max_secs - min_secs + 1))
  local sleep_time=$((RANDOM % range + min_secs))
  echo "  ⏳ Waiting ${sleep_time}s (jitter: ${min_secs}-${max_secs}s)..."
  sleep "$sleep_time"
}
```

CLI: `./post-comments.sh <owner/repo> <workspace_dir> [jitter_min] [jitter_max] [daily_max]`
Defaults: jitter_min=75, jitter_max=135, daily_max=60.

### Breathing Pauses (Implemented)

After every 30-50 comments (randomized), the script takes a longer pause of
8-15 minutes. This simulates a human taking a break. Without this, sustained
commenting for >1 hour often triggers abuse detection even within rate limits.
The interval is re-randomized after each pause.

### Exponential Backoff (Implemented)

On API failure, the script checks stderr for rate-limit indicators
(`rate.limit`, `secondary`, `abuse`, `429`, `403`). If it's a rate-limit
error, it retries with exponential backoff:

```
Attempt 1: Try immediately (no wait)
Attempt 2: Wait 2 minutes, then retry
Attempt 3: Wait 4 minutes, then retry
Attempt 4: Wait 8 minutes, then retry
Attempt 5: Wait 16 minutes, then retry
```

Total backoff budget: ~30 minutes. If all 5 attempts fail, save progress and
exit. Non-retriable errors (404, 422) are detected and skipped immediately
without backoff.

```bash
# post-comments.sh — backoff_sleep()
backoff_sleep() {
  local attempt="$1"
  local base=120   # 2 minutes
  local cap=1800   # 30 minutes
  local wait=$((base * (2 ** (attempt - 2))))
  if [ "$wait" -gt "$cap" ]; then wait=$cap; fi
  echo "  ⏳ Backoff: ${wait}s (~$((wait / 60))min) before retry $attempt of 5..."
  sleep "$wait"
}
```

### Recovery After Rate Limit (Implemented)

If the script exits due to rate limiting:
1. `comment-progress.json` has the exact index where it stopped (with `error` field)
2. On resume, the script detects the `error` field and starts with a **5-minute
   grace period** before the first comment
3. For longer cooldowns (1+ hours), the operator should wait before re-running
   — this is a manual decision, not enforced by the script

### Text Variation

GitHub's abuse detection also looks at comment body patterns. If you post 50
comments with the exact same structure, that's a signal.

**Already handled**: SKILL.md Phase 6 defines opener rotation (4 openers,
never repeat consecutively). This is usually sufficient. For large batches
(>100 comments), consider also varying:
- Sentence structure in the root_cause line
- Whether to include the correction footer or not (include it 80% of the time)
- Spacing and punctuation minor variations

### PATCH vs POST

When re-running cross-ref on a repo where comments were previously posted:

1. Check if a cross-ref comment already exists on the target item
2. If yes, **PATCH** (edit) the existing comment instead of creating a new one
3. Track comment IDs in `comment-progress.json`:
   ```json
   {
     "posted_comments": {
       "1234": "IC_kwDOABC123",
       "5678": "IC_kwDOABC456"
     }
   }
   ```

This requires extending `post-comments.sh` to:
- Accept a `--update` flag for re-run mode
- Look up existing comment IDs before posting
- Use `gh api -X PATCH repos/{owner}/{repo}/issues/comments/{id}` for updates

**Note**: This is a Tier 2 feature (#10) — not yet implemented.

### Separate Rate Limits by Action Type

Comments, labels, and closes may have different secondary limits. Treat them
independently:

| Action | Recommended Rate | Notes |
|--------|-----------------|-------|
| Comment | 1 per ~90s (jitter) | Most sensitive to abuse detection |
| Label | 1 per ~30s | Less scrutinized, but still throttle |
| Close | 1 per ~60s | Irreversible, be conservative |

When a cluster has multiple actions (comment + label + close), spread them:
```
Comment on #1234  → wait 90s
Label #1234       → wait 30s
Close #1234       → wait 60s
Comment on #5678  → wait 90s
...
```

### Daily Budget

Keep the 60 comments/day cap. This is well below GitHub's actual limits but
provides a safety margin. For repos you don't own, consider 30/day.

The daily counter resets at UTC midnight. Track in `comment-progress.json`:
```json
{
  "day_start_utc": "2026-02-21",
  "day_count": 42,
  "day_budget": 60
}
```
