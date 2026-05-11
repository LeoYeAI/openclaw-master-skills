# cross-ref

A Claude Code skill that finds hidden connections between GitHub PRs and issues.

## The problem

Active repos accumulate blind spots. A developer opens a PR to fix a timeout bug — not knowing someone else opened a nearly identical PR two weeks ago. An issue sits open for months while a merged PR quietly solved it, just without the `fixes #N` tag. Maintainers can't manually cross-reference hundreds of PRs and issues. The connections are there, buried in titles, bodies, error messages, and branch names. They just need someone to look.

## What cross-ref does

It reads your repo's PRs and issues, spawns parallel Sonnet subagents to analyze them semantically, and surfaces two things:

1. **Duplicate PRs** — PRs solving the same problem, even with different code or wording
2. **Missing issue links** — Open issues that already have a PR addressing them, just never explicitly linked

Results come back as **thematic clusters** scored by actionability, not a flat list of pairs. A cluster might group `Issue #400 + PR #412 + PR #419` under the theme "auth token rotation fails silently" — showing you the full picture, not isolated matches.

## How it works

```
fetch → analyze in parallel → cluster → verify → report → act
```

**Phase 1**: Shell scripts fetch PR/issue metadata from the GitHub API and build compact indexes.

**Phase 2**: PRs are split into batches. Each batch goes to a parallel Sonnet subagent alongside the full issue index and PR index. Subagents look for evidence-based connections — shared error messages, same component, overlapping fixes. Title similarity alone doesn't count.

**Phase 3**: Results are merged, deduplicated, clustered by shared items (union-find), and scored 0-10 on actionability (open state, confidence, community interest, draft status, clarity of canonical PR).

**Phase 3b**: A verification agent fetches deeper data (`gh pr diff`, full issue bodies, comment threads) to confirm or reject each candidate. Discovery optimizes for recall; verification optimizes for precision.

**Phase 4**: A structured report groups findings by cluster, sorted by score. Each cluster shows its theme, the items involved, evidence, and suggested actions.

**Phase 5-6**: If you choose to act, the skill builds a comment queue and posts with organic-looking rate limiting — jittered intervals, breathing pauses, exponential backoff. Everything is designed to not trigger GitHub's abuse detection.

## Design principles

The skill follows five hard rules (documented in `references/principles.md`):

- **Evidence over narrative** — Never classify duplicates from title similarity alone
- **Confidence requires specifics** — If you can't explain the shared root cause in one sentence, it's not "high"
- **Credit preservation** — Never frame a duplicate as wasted work
- **Conservative defaults** — Better to miss a link than create a false one
- **Reversibility** — Every comment includes a correction path

## Rate limiting

The posting script avoids fixed-interval patterns (which is what GitHub's abuse detection targets). Instead:

- **Jitter**: Random 75-135s between comments (~40/hour)
- **Breathing pauses**: 8-15 min break every 30-50 comments
- **Exponential backoff**: 2→4→8→16min on failures, with rate-limit vs permanent error differentiation
- **Daily budget**: 60 comments/day cap with UTC-midnight reset and resume support

## Installation

```bash
clawhub install cross-ref
```

Or clone this repo and symlink to your Claude Code skills directory:

```bash
git clone https://github.com/Glucksberg/cross-ref.git
ln -s "$(pwd)/cross-ref" ~/.claude/skills/cross-ref
```

## Requirements

- Claude Code with Sonnet model access (for subagents)
- `gh` CLI authenticated with `repo` scope
- `jq` for JSON processing

## Usage

### Quick start

In Claude Code, just ask in natural language:

```
Run cross-ref on openclaw/openclaw. Use 1400 PRs (open only) and 1400 issues.
```

Or more casually:

```
Find duplicate PRs and missing issue links in owner/repo
```

The skill activates automatically when Claude detects the intent.

### What happens step by step

**Phase 1 — Data fetch** (~2-3 min for 1000 PRs). The skill runs `fetch-data.sh` to pull PR/issue metadata from the GitHub API and build compact indexes.

**Phase 2 — Parallel analysis** (~3-5 min). Spawns N parallel Sonnet subagents (1000 PRs / 50 per batch = 20 subagents). Each one analyzes its batch of PRs against the full issue and PR indexes, looking for evidence-based connections.

**Phase 3 — Cluster & score**. Merges all subagent results, deduplicates, groups connected findings into thematic clusters, and scores each cluster 0-10 on actionability.

**Phase 3b — Verification**. A single verification agent fetches deeper data (PR diffs, full issue bodies, comment threads) to confirm or reject each candidate. False positives get caught here.

**Phase 4 — Report**. You get a structured report organized by clusters, sorted by score. Each cluster shows its theme, items involved, evidence, and suggested actions.

### You decide what to do

The skill **always starts in `plan` mode** (dry-run). Nothing is posted until you explicitly say so. After reviewing the report, you're presented with a strategy table:

```
┌─────────────┬───────────────────┬──────────┬───────────┬──────────────┐
│ Strategy    │ Rate              │ Daily    │ Comments  │ Est. Time    │
│             │                   │ Max      │ to Post   │              │
├─────────────┼───────────────────┼──────────┼───────────┼──────────────┤
│ Conservative│ 1/75-135s (jitter)│ 60       │ {high}    │ ~90 min      │
│ Moderate    │ 1/75-135s (jitter)│ 60       │ {h+m}     │ ~90 min      │
│ Dry Run     │ —                 │ —        │ 0         │ Instant      │
│ Manual Pick │ 1/75-135s (jitter)│ 60       │ {custom}  │ depends      │
└─────────────┴───────────────────┴──────────┴───────────┴──────────────┘
```

For each cluster you choose:
- **Comment only** — link the items with a helpful comment
- **Comment + label** — link and add labels (e.g., `duplicate`)
- **Comment + close** — link and close duplicate PRs (high confidence only)
- **Skip** — ignore this cluster
- **Manual** — handle it yourself

### Resume support

The script saves progress to `comment-progress.json` after every comment. If it stops mid-run (daily limit, rate limit, Ctrl+C), it resumes from exactly where it left off next time. The daily counter resets at UTC midnight.

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `pr_count` | 1000 | How many recent PRs to fetch |
| `issue_count` | 1000 | How many recent issues to fetch |
| `pr_state` | `all` | PR state filter: `open`, `closed`, `all` |
| `issue_state` | `open` | Issue state filter: `open`, `closed`, `all` |
| `batch_size` | 50 | PRs per subagent batch |
| `confidence_threshold` | `medium` | Minimum to include in report: `low`, `medium`, `high` |
| `mode` | `plan` | `plan` = report only (always start here). `execute` = act on findings. |

### Token cost estimate

For a rough idea of what a run costs (Sonnet subagents + Opus orchestrator):

| Scope | Subagents | Sonnet input | Sonnet output | Time |
|-------|-----------|-------------|---------------|------|
| 1000 PRs + 1000 issues | 20 | ~600K tokens | ~20K tokens | ~5-8 min |
| 1400 PRs + 1400 issues | 28 | ~840K tokens | ~28K tokens | ~7-10 min |
| 4000 PRs + 4000 issues | 80 | ~2.4M tokens | ~80K tokens | ~15-20 min |

Start small (100/100) to validate results before scaling up.

## File structure

```
cross-ref/
├── SKILL.md                     # Main skill definition (phases, prompts, templates)
├── ROADMAP.md                   # Completed features + improvement backlog
├── README.md                    # This file
├── references/
│   ├── principles.md            # Hard decision rules for subagents
│   └── commenting-strategy.md   # Rate-limit tiers and daily budget math
└── scripts/
    ├── fetch-data.sh            # GitHub API data fetcher with pagination
    ├── post-comments.sh         # Rate-limited comment poster with jitter/backoff
    └── test-helpers.sh          # Smoke tests for helper functions
```

## License

MIT
