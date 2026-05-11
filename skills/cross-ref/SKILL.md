---
name: cross-ref
description: >
  Cross-reference GitHub PRs and issues to find duplicates and missing links.
  Spawns parallel Sonnet subagents to semantically analyze the last N PRs and issues,
  finding PRs that solve the same problem (duplicates) and issues resolved by open PRs
  but not yet linked. Groups findings into thematic clusters, scores them by actionability,
  and offers rate-limited commenting or bulk actions (close, label). Use this skill when
  the user wants to find duplicate PRs, link issues to PRs, clean up a repo's cross-references,
  or audit PR/issue relationships. Also useful when the user says things like
  "find related PRs", "which PRs fix this issue", "are there duplicate PRs",
  "link issues and PRs", or "audit cross-references".
---

# Cross-Ref: PR & Issue Linker

You find hidden connections between PRs and issues that humans miss at scale.
The core loop is: **fetch → analyze in parallel → cluster → verify → report → act**.

Before doing anything, read `references/principles.md`. Those rules override
everything in this file when there's a conflict.

## Overview

Repos accumulate duplicate PRs and orphaned issue→PR links over time. Manual
cross-referencing doesn't scale past a few dozen items. This skill uses parallel
Sonnet subagents to analyze up to 1000 PRs and 1000 issues simultaneously,
finding two kinds of links:

1. **Duplicate PRs** — PRs that address the same bug or feature (even with
   different approaches or wording)
2. **Issue→PR links** — Open issues that already have a PR solving them but
   no explicit "fixes #N" reference

Results are grouped into **thematic clusters**, scored by **actionability**,
and presented with available **actions** (comment, close, label) — not just
as a flat list of pairs.

## Configuration

The user provides these at invocation time (ask if not given):

| Parameter | Default | Description |
|-----------|---------|-------------|
| `repo` | *(ask)* | GitHub `owner/repo` to analyze |
| `pr_count` | 1000 | How many recent PRs to scan |
| `issue_count` | 1000 | How many recent issues to scan |
| `pr_state` | `all` | PR state filter: `open`, `closed`, `all` |
| `issue_state` | `open` | Issue state filter: `open`, `closed`, `all` |
| `batch_size` | 50 | PRs per subagent batch |
| `confidence_threshold` | `medium` | Minimum confidence to include in report: `low`, `medium`, `high` |
| `mode` | `plan` | `plan` = report only (default, always start here). `execute` = act on findings. |

**Default mode is `plan`** (dry-run). The skill always starts by generating
the report. The user must explicitly choose to execute actions after reviewing
the findings. This matters because actions can't be undone.

## Workflow

### Phase 1: Data Collection

Fetch PR and issue metadata from the GitHub API. This phase is deterministic
and uses the shell script — no AI needed.

```bash
scripts/fetch-data.sh <owner/repo> <workspace_dir> [pr_count] [issue_count] [pr_state] [issue_state]
```

This produces:
- `workspace/prs.json` — Full PR metadata
- `workspace/issues.json` — Full issue metadata (PRs filtered out)
- `workspace/existing-refs.json` — Pre-extracted explicit cross-references
- `workspace/pr-index.txt` — Compact one-line-per-PR index
- `workspace/issue-index.txt` — Compact one-line-per-issue index

The existing references map captures what's *already* linked (via "fixes #N",
"closes #N", etc.) so subagents can focus on what's *missing*.

### Phase 2: Parallel Analysis (Sonnet Subagents)

This is where the intelligence happens. Split PRs into batches and spawn
parallel Sonnet subagents. Each subagent receives:

- Its batch of PRs (full metadata from prs.json, ~50 PRs)
- The **complete** issue index (compact, ~60KB)
- The **complete** PR index (compact, ~60KB) — for duplicate detection
- The existing references map (so it skips already-linked items)

**Spawn subagents using the Task tool:**

```
For each batch B of {batch_size} PRs:
  Task(
    subagent_type="general-purpose",
    model="sonnet",
    prompt=<see below>
  )
```

**Subagent prompt template:**

**Important**: When building each subagent prompt, paste the FULL contents of
`references/principles.md` into the "Decision Principles" section below.
Do not summarize or condense — include the complete text. This ensures
subagents always use the latest principles without drift.

```
You are a cross-reference analyst for a GitHub repository. Your job is to find
connections between PRs and issues that aren't explicitly linked yet.

## Decision Principles (these override everything else)

{paste full contents of references/principles.md here}

## Your Batch
You are analyzing PRs {start_num} through {end_num} of {total_prs}.

## PR Details (your batch)
{full PR metadata for this batch from prs.json}

## Complete Issue Index
{issue-index.txt content}

## Complete PR Index
{pr-index.txt content}

## Already Known References
{existing-refs.json content}

## Your Task

Find TWO types of connections:

### 1. Issue→PR Links
For each PR in your batch, determine if it resolves any issue in the index.
Evidence must include at least one of:
- Same error message or failure path described in both
- PR modifies the component/module that the issue describes as broken
- PR body explicitly references the problem the issue describes (even without #N)

Title similarity alone is NOT sufficient. Skip any links that already exist
in the known references.

### 2. Duplicate PRs
For each PR in your batch, check if any OTHER PR in the full PR index
addresses the same problem. Evidence must include at least one of:
- Both modify the same files for the same reason
- Both fix the same error/behavior (even with different approaches)
- One is a resubmission or continuation of the other (same branch, similar body)

Same area of code is NOT enough — the PRs must address the same specific problem.

### 3. Flagging Uncertainty

If you encounter a pair where the evidence is ambiguous — you can see a
plausible connection but can't confirm it from the available data — mark it
with `"status": "manual_review_required"` instead of guessing a confidence
level. Include what's missing (e.g., "need to see full diff to confirm
file overlap").

### Output Format
Return ONLY a JSON array. No other text.

[
  {
    "type": "issue_link",
    "pr": 5678,
    "pr_author": "@username",
    "issue": 1234,
    "confidence": "high|medium|low",
    "status": "confirmed|manual_review_required",
    "root_cause": "One sentence: what shared problem connects these",
    "evidence": "Specific: same error message, same file, same component, etc.",
    "missing_evidence": null or "What would be needed to confirm this"
  },
  {
    "type": "duplicate_pr",
    "pr_a": 5678,
    "pr_b": 5679,
    "pr_a_author": "@username_a",
    "pr_b_author": "@username_b",
    "confidence": "high|medium|low",
    "status": "confirmed|manual_review_required",
    "root_cause": "One sentence: what shared problem connects these",
    "evidence": "Specific: same files modified, same branch, resubmission, etc.",
    "missing_evidence": null or "What would be needed to confirm this"
  }
]
```

**Parallelism**: Spawn ALL batch subagents simultaneously. With batch_size=50
and 1000 PRs, that's 20 parallel subagents. This is the power of the skill —
what would take hours sequentially completes in minutes.

### Phase 3: Merge, Deduplicate & Cluster

After all subagents return:

1. **Collect** all JSON results into a single array
2. **Deduplicate** duplicate_pr entries (A→B and B→A are the same link)
3. **Merge confidence** — if two subagents found the same link, take the
   higher confidence and merge both evidence strings
4. **Filter** by `confidence_threshold`
5. **Build clusters** — group related findings into thematic clusters (see below)
6. **Score clusters** by actionability (see below)
7. **Sort** clusters by score (highest first)

Save to `workspace/results-unverified.json`.

#### Clustering Algorithm

Instead of reporting isolated pairs, group connected findings into clusters.
Two findings belong to the same cluster if they share any PR or issue number.

Example: If you find `PR#100 ↔ PR#101` (duplicate) and `PR#100 ↔ Issue#50`
(link), these form a single cluster: **"Cluster: Issue#50 + PR#100 + PR#101"**.

Cluster structure:
```json
{
  "cluster_id": 1,
  "theme": "Onboard token mismatch — OPENCLAW_GATEWAY_TOKEN ignored",
  "items": ["PR#22662", "PR#22658", "Issue#22638"],
  "findings": [ ...individual findings in this cluster... ],
  "score": 8.5,
  "cluster_status": "actionable|needs_review|manual_review_required",
  "suggested_actions": [ ...see Phase 4b... ]
}
```

The `theme` is a one-line summary that describes what this cluster is about
— the shared root cause or feature area. Generate it from the `root_cause`
fields of the cluster's findings.

#### Actionability Scoring

Each cluster gets a score based on these signals (clamp result to 0-10):

| Signal | Points | Why it matters |
|--------|--------|----------------|
| All items open | +3 | Can still be acted on |
| At least one high-confidence finding | +2 | Strong evidence |
| Multiple findings in cluster | +1 | More connections = more value |
| Issue has >5 reactions/comments | +1 | High community interest |
| PR is not draft | +1 | Ready for review |
| Cluster has a clear canonical PR | +1 | Easy to pick a winner |
| Any `manual_review_required` | -2 | Needs human judgment |
| All items closed | -3 | Low urgency |

Clusters scoring 7+ are **actionable** (green in report).
Clusters scoring 4-6 **need review** (yellow).
Clusters scoring 0-3 are **low priority** (gray).

### Phase 3b: Evidence Verification

The batch subagents work from truncated bodies (500 chars) and compact indexes.
That's good enough for discovery but not for final decisions. This phase takes
the candidates and verifies them against deeper data.

Spawn a single verification subagent (Sonnet) that:

1. Reads `workspace/results-unverified.json`
2. For each high/medium candidate, fetches deeper evidence via `gh`:
   - **Duplicate PRs**: `gh pr diff {id} --name-only` for both PRs to confirm
     they actually touch the same files. If the file lists don't overlap at all,
     downgrade to `low` or remove.
   - **Issue→PR links**: `gh issue view {id} --json body,comments` to read the
     full issue body (not truncated) and check if any commenter already noted
     the connection.
   - **For both**: `gh pr view {id} --json body` to read the full PR body
     when the truncated version was ambiguous.
3. For `manual_review_required` items: attempt to resolve with deeper data.
   If still ambiguous after deep check, keep the flag — it goes to the user.
4. Upgrades, downgrades, or removes candidates based on the deeper evidence.
5. Recalculates cluster scores after confidence changes.
6. Writes the verified results to `workspace/results.json`.

**Verification subagent prompt:**

```
You are an evidence verification agent. You received candidate cross-references
between GitHub PRs and issues from a discovery pass. Your job is to verify or
reject each candidate using deeper data.

## Principles
- A candidate stays only if deeper evidence confirms the connection.
- If file diffs don't overlap for duplicate PRs, downgrade or remove.
- If the full issue body reveals the problem is actually different, remove.
- If someone already commented the link, exclude the candidate from results entirely.
- You may upgrade "medium" to "high" if deeper evidence is strong.
- For "manual_review_required" items: try to resolve with the deeper data.
  If you can confirm or deny, update status to "confirmed" with the new
  confidence. If still ambiguous, keep "manual_review_required".
- Add a "verified_evidence" field with what you found in the deep check.

## Candidates to verify
{contents of results-unverified.json}

## Commands available
Run these via bash to fetch deeper data:
- gh pr diff {number} --name-only --repo {owner/repo}
- gh pr view {number} --json body --repo {owner/repo}
- gh issue view {number} --json body,comments --repo {owner/repo}

## Output
Write verified results to {workspace}/results.json as a JSON array.
Same structure as input, but with:
- Updated confidence levels and status fields
- Added "verified_evidence" field
- Removed any candidates that didn't survive verification
- Added "verification_note" for anything noteworthy
```

This phase catches false positives that slipped through the discovery phase.
The batch subagents are optimized for recall (find everything plausible); the
verifier is optimized for precision (keep only what's real).

**Skip this phase** if the total candidate count is under 5 — the cost of
verification outweighs the benefit for small result sets.

### Phase 4: Generate Report

Present the report to the user organized by clusters, not flat pairs.

**Report structure:**

```markdown
# Cross-Reference Report: {owner}/{repo}

**Scanned**: {N} PRs, {M} issues
**Found**: {X} clusters containing {Y} findings
**Already linked**: {Z} existing references (skipped)
**Mode**: plan (review only — no actions taken)

## Clusters (sorted by actionability score)

### Cluster 1: Onboard token mismatch (Score: 8.5 🟢)
**Theme**: OPENCLAW_GATEWAY_TOKEN env var ignored during onboard setup
**Items**: PR#22662 (@aiworks451), PR#22658 (@otherdev), Issue#22638
**Status**: Actionable

| Finding | Type | Confidence | Root Cause |
|---------|------|------------|------------|
| PR#22662 ↔ PR#22658 | duplicate_pr | high | Both fix token mismatch in onboard wizard |
| PR#22658 → Issue#22638 | issue_link | high | PR explicitly closes the issue |

**Suggested actions** (choose per cluster):
- 💬 Comment on PR#22662 noting PR#22658 covers the same fix more broadly
- 🏷️ Label PR#22662 as `duplicate`
- ❌ Close PR#22662 as duplicate of PR#22658

---

### Cluster 2: i18n Portuguese translations (Score: 6.0 🟡)
**Theme**: Competing pt-BR translation implementations
**Items**: PR#22637 (@dev1), PR#22628 (@dev2)
**Status**: Needs review — different approaches, human must choose

| Finding | Type | Confidence | Root Cause |
|---------|------|------------|------------|
| PR#22637 ↔ PR#22628 | duplicate_pr | medium | Same feature, different implementations |

**Suggested actions**:
- 💬 Comment linking the two PRs for coordination
- ⚠️ Manual review required: different i18n architectures, maintainer must decide

---

### ⚠️ Items Requiring Manual Review

These findings had ambiguous evidence that couldn't be resolved automatically:

| Finding | Reason | What's Missing |
|---------|--------|----------------|
| PR#1234 ↔ Issue#5678 | Keyword overlap but no shared error path | Need to check if PR touches the auth module |

## Summary
- **Actionable clusters**: {count} (score 7+, ready for bulk action)
- **Needs review**: {count} (score 4-6, human judgment needed)
- **Manual review required**: {count} (ambiguous, flagged for human)
- **Next step**: Choose actions per cluster, then select a commenting/action strategy.
```

### Phase 4b: Suggested Actions Per Cluster

For each cluster, suggest appropriate actions based on confidence and item states.

**For duplicate PRs (high confidence, both open):**
1. 💬 **Comment** — link the PRs so authors can coordinate
2. 🏷️ **Label** — add `duplicate` label to the weaker PR
3. ❌ **Close** — close the weaker PR as duplicate (only if very clear)

**For duplicate PRs (one open, one closed):**
1. 💬 **Comment** — note the connection for context (lower priority)

**For issue→PR links (high confidence):**
1. 💬 **Comment on issue** — note that a PR addresses this
2. 🏷️ **Label issue** — add `has-pr` or similar

**For `manual_review_required` items:**
1. ⚠️ **Flag for human** — present in a separate section, no automated action

**Action rules:**
- Never suggest closing without high confidence + verification
- Never suggest labeling without at least medium confidence
- Always suggest commenting as the minimum action (it's the safest)
- For clusters with mixed confidence, suggest the action matching the
  lowest-confidence finding (conservative)

### Phase 5: Interactive Action Strategy

After presenting the report, ask the user how they want to proceed.
Read `references/commenting-strategy.md` for rate-limiting details.

**Present action choices per cluster:**

For each actionable cluster, let the user pick:
- **Comment only** — just link the items
- **Comment + label** — link and add labels
- **Comment + close** — link and close duplicates (high confidence only)
- **Skip** — do nothing for this cluster
- **Manual** — I'll handle this one myself

Then present the timing strategy. Read `references/commenting-strategy.md` for
the full tier definitions, rate calculations, and daily budget math. Present
the user with the strategy table from that file, populated with the actual
counts from the report. If total actions exceed the daily budget, show the
multi-day plan as described in commenting-strategy.md.

Always offer **Dry Run** (report only, no actions) as the default choice.
Also offer **Skip** — save the report but don't act at all.

### Phase 6: Execute Actions

If the user chooses to act, build `workspace/approved-comments.json` and
execute with rate limiting via the shell script.

**approved-comments.json schema** (array of objects):
```json
[
  {
    "target_number": 1234,
    "type": "issue_link|duplicate_pr",
    "body": "The full comment text to post",
    "cluster_id": 1,
    "finding_index": 0
  }
]
```
- `target_number` — the issue or PR number to comment on (used by post-comments.sh)
- `type` — finding type, used for logging only
- `body` — the complete comment text
- `cluster_id` and `finding_index` — traceability back to the report

```bash
scripts/post-comments.sh <owner/repo> <workspace_dir> [jitter_min] [jitter_max] [daily_max]
```

**For label and close actions**, execute them inline (not via the script)
since they don't need the same rate limiting as comments:
```bash
# Label (works for both issues and PRs — GitHub treats PRs as issues for labels)
gh issue edit {number} --add-label duplicate --repo {owner/repo}
# Close PR as duplicate (use heredoc for safe body passing)
gh pr close {number} --comment "$(cat <<'EOF'
Closing in favor of #{canonical_pr_number} by @{canonical_author}, which covers the same change ({root_cause_sentence}).

Thanks for the contribution, @{closed_pr_author} — your work helped confirm this was worth fixing.

_If this closure is wrong, reopen and let me know._
EOF
)" --repo {owner/repo}
```

**Always execute in this order within a cluster:**
1. Post comments first (so the context exists before close/label)
2. Add labels
3. Close (only after comment is posted)

**Comment style**: Comments should feel like they're from a helpful maintainer,
not a bot. Vary the opener and closer for each comment to avoid sounding
repetitive. Always mention the PR author by name.

**Comment templates** (vary the opener each time):

Openers (rotate through these, never use the same one twice in a row):
- "Heads up — this might be related."
- "Worth a look:"
- "Noticed a possible connection here."
- "This could be relevant to what you're working on."

For issue→PR links (comment on the issue):
```
{opener}

PR #{pr_number} by @{author} ({pr_title}) appears to address this issue.

{root_cause_sentence}

_If this doesn't look right, let me know and I'll correct the link._
```

For duplicate PRs (comment on the newer PR):
```
{opener}

PR #{other_pr_number} by @{other_author} ({other_pr_title}) seems to address
the same problem.

{root_cause_sentence}

Both approaches have merit — might be worth coordinating.

_If these aren't actually related, let me know and I'll correct this._
```

Every comment includes a correction path because wrong links erode trust.

Save progress to `workspace/comment-progress.json` for resume support.

## Error Handling

- **API rate limit hit**: Pause, show remaining reset time, save progress.
- **Subagent returns invalid JSON**: Log the error, skip that batch, warn user.
  Don't retry — the batch results are lost but other batches continue.
- **PR/issue not found (deleted)**: Skip silently, note in report.
- **Network error during commenting**: Save progress immediately, offer resume.
- **Subagent returns empty results**: Normal — not every batch has links.
- **Close/label fails**: Log the error, continue with remaining actions.
  Never retry a close — the user should investigate manually.

## Workspace Structure

```
cross-ref-workspace/
├── prs.json                  # Raw PR metadata
├── issues.json               # Raw issue metadata
├── pr-index.txt              # Compact PR index (one line per PR)
├── issue-index.txt           # Compact issue index (one line per issue)
├── existing-refs.json        # Pre-extracted explicit references
├── batches/
│   ├── batch-01-results.json # Subagent results per batch
│   ├── batch-02-results.json
│   └── ...
├── results-unverified.json   # Raw merged findings (before verification)
├── results.json              # Verified findings with clusters
├── report.md                 # Human-readable report
├── approved-comments.json    # Comments approved for posting
├── comment-progress.json     # Commenting progress tracker
└── pending-comments.json     # Links not yet commented (if day limit hit)
```

## Resume Support

If a previous run exists in the workspace:
- **Phase 1-3**: Skip if `results.json` exists and user confirms
- **Phase 4**: Skip if `report.md` exists and user confirms
- **Phase 5-6**: Resume from `comment-progress.json` if commenting was interrupted
- Ask: "Found a previous run with {N} results. Resume commenting or start fresh?"

## Tips for Operators

- Start with a smaller count (100 PRs, 100 issues) to validate before scaling
- Always review the report in `plan` mode before executing actions
- The compact index approach keeps memory usage manageable — don't fetch full
  PR bodies (500 char truncation is intentional)
- For very active repos (>10K PRs), increase batch_size to reduce subagent count
- Token costs: ~20 subagent calls for 1000 PRs at batch_size=50, each with
  ~120KB context. Plan accordingly.
- The `gh` CLI token needs `repo` scope (private) or `public_repo` (public),
  plus `issues:write` for posting comments.
