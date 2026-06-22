# CLI Reference (brainx-v5)

Entry point: `./brainx-v5`

Internally it delegates to `lib/cli.js`.

## Global help

```bash
./brainx-v5 --help
```

## `health`

Runs a database smoke test:

```bash
./brainx-v5 health
```

Checks:

- DB connectivity (`select 1`)
- pgvector installed
- `brainx_*` tables exist

## `add`

Store (upsert) a memory item.

```bash
./brainx-v5 add \
  --type <type> \
  --content <text> \
  [--context <ctx>] \
  [--tier <hot|warm|cold|archive>] \
  [--importance <1-10>] \
  [--tags a,b,c] \
  [--agent <name>] \
  [--id <id>] \
  [--status <pending|in_progress|resolved|promoted|wont_fix>] \
  [--category <learning|error|feature_request|correction|knowledge_gap|best_practice>] \
  [--patternKey <key>] \
  [--recurrenceCount <n>] \
  [--firstSeen <iso>] \
  [--lastSeen <iso>] \
  [--resolvedAt <iso>] \
  [--promotedTo <target>] \
  [--resolutionNotes <text>]
```

Notes:

- If `--id` is omitted, an id like `m_<timestamp>_<rand>` is generated.
- Embedding input is built as:
  - `${type}: ${content} [context: ${context}]`
- Phase 2 store pipeline adds:
  - optional PII scrubbing before embedding/storage (`BRAINX_PII_SCRUB_ENABLED`, `BRAINX_PII_SCRUB_REPLACEMENT`)
  - semantic dedupe merge in recent same `context`/`category` (`BRAINX_DEDUPE_SIM_THRESHOLD`)
  - redaction metadata tags like `pii:redacted`, `pii:email`

## `search`

Semantic search returning JSON.

```bash
./brainx-v5 search \
  --query <text> \
  [--limit <n>] \
  [--minSimilarity <0-1>] \
  [--context <ctx>] \
  [--tier <tier>] \
  [--minImportance <n>]
```

Returned fields include:

- all table columns
- `similarity`
- `score`

## `inject`

Semantic search formatted as a prompt-ready block (plain text).

```bash
./brainx-v5 inject \
  --query <text> \
  [--limit <n>] \
  [--context <ctx>] \
  [--tier <tier>] \
  [--minImportance <n>] \
  [--minScore <n>] \
  [--maxTotalChars <n>] \
  [--maxCharsPerItem <n>] \
  [--maxLinesPerItem <n>]
```

Defaults:

- `BRAINX_INJECT_DEFAULT_TIER=warm_or_hot`
  - if you don’t pass `--tier`, inject searches hot then warm and merges unique ids.
- `BRAINX_INJECT_MIN_SCORE=0.25`
- `BRAINX_INJECT_MAX_TOTAL_CHARS=12000`

Output format:

```
[sim:0.62 imp:9 tier:hot type:decision agent:coder ctx:openclaw]
<content>

---

[sim:0.41 imp:6 tier:warm type:note agent:system ctx:emailbot]
<content>
```

## Environment variables

Required:

- `DATABASE_URL`
- `OPENAI_API_KEY`

Optional:

- `BRAINX_ENV` — load a shared env file from a specific path
- `OPENAI_EMBEDDING_MODEL`
- `OPENAI_EMBEDDING_DIMENSIONS`
- `BRAINX_INJECT_DEFAULT_TIER`
- `BRAINX_INJECT_MAX_CHARS_PER_ITEM`
- `BRAINX_INJECT_MAX_LINES_PER_ITEM`
- `BRAINX_INJECT_MAX_TOTAL_CHARS`
- `BRAINX_INJECT_MIN_SCORE`
- `BRAINX_PII_SCRUB_ENABLED` (default `true`)
- `BRAINX_PII_SCRUB_REPLACEMENT` (default `[REDACTED]`)
- `BRAINX_PII_SCRUB_ALLOWLIST_CONTEXTS` (csv; contexts que NO se redactan)
- `BRAINX_DEDUPE_SIM_THRESHOLD` (default `0.92`)
- `BRAINX_DEDUPE_RECENT_DAYS` (default `30`)
- `BRAINX_LIFECYCLE_PROMOTE_MIN_RECURRENCE` (default `3`)
- `BRAINX_LIFECYCLE_PROMOTE_DAYS` (default `30`)
- `BRAINX_LIFECYCLE_DEGRADE_DAYS` (default `45`)
- `BRAINX_LIFECYCLE_LOW_IMPORTANCE_MAX` (default `3`)
- `BRAINX_LIFECYCLE_LOW_ACCESS_MAX` (default `1`)

## `resolve`

Set lifecycle resolution fields on a single memory (`--id`) or by recurring pattern (`--patternKey`).

```bash
./brainx-v5 resolve \
  (--id <id> | --patternKey <key>) \
  --status <pending|in_progress|resolved|promoted|wont_fix> \
  [--resolvedAt <iso>] \
  [--promotedTo <target>] \
  [--resolutionNotes <text>]
```

Returns JSON with updated rows.

## `promote-candidates`

Lists recurring patterns that meet promotion thresholds. Output is JSON.

```bash
./brainx-v5 promote-candidates \
  [--minRecurrence <n>] \
  [--days <n>] \
  [--limit <n>] \
  [--json]
```

Defaults: `--minRecurrence 3`, `--days 30`, `--limit 50`

## `lifecycle-run`

Automates lifecycle transitions:

- promote recent recurring items to `promoted`
- degrade stale `pending` / `in_progress` items to `pending` or `wont_fix` based on importance/access
- refresh affected `brainx_patterns` aggregate status/recurrence timestamps

```bash
./brainx-v5 lifecycle-run \
  [--promoteMinRecurrence <n>] \
  [--promoteDays <n>] \
  [--degradeDays <n>] \
  [--lowImportanceMax <n>] \
  [--lowAccessMax <n>] \
  [--dryRun] \
  [--json]
```

Defaults (env-overridable): promote `recurrence>=3` within `30` days, degrade stale after `45` days.

## `metrics`

Operational KPIs (JSON):

- counts by status/category/tier
- top recurring patterns
- search/inject query performance from `brainx_query_log`

```bash
./brainx-v5 metrics [--days <n>] [--topPatterns <n>] [--json]
```

## Offline eval harness

Run retrieval quality checks from a JSON/JSONL dataset of `query` + `expected_key` pairs:

```bash
npm run eval:memory-quality -- --json
# or
node ./scripts/eval-memory-quality.js --dataset ./tests/fixtures/memory-eval-sample.jsonl --k 5 --json
```

Outputs proxy metrics including `hit_at_k_proxy`, `avg_top_similarity`, and duplicate reduction by collapsing top-k results on `pattern_key`.

## Exit codes

- `0` on success
- `1` on error (prints message to stderr)

## `doctor`

Diagnose BrainX installation health, schema, cron, and configuration issues.

```bash
./brainx-v5 doctor [--json]
```

## `fix`

Auto-fix issues detected by `doctor`.

```bash
./brainx-v5 fix [--json] [--dry-run]
```

## `fact`

Shortcut to add a fact-type memory (tier: hot, category: infrastructure).

```bash
./brainx-v5 fact --content "Some important fact"
```

## `facts`

List stored facts, optionally filtered by context.

```bash
./brainx-v5 facts [--context <ctx>] [--limit 30]
```

## `promote-candidates`

Promote recurring memories from agent-local to global tier.

```bash
./brainx-v5 promote-candidates [--minRecurrence 3] [--days 30] [--limit 50]
```

## `lifecycle-run`

Run the full memory lifecycle (promote + degrade + archive).

```bash
./brainx-v5 lifecycle-run [--promote-min-recurrence 3] [--promote-days 30] [--degrade-days 45]
```

## `advisory`

Check BrainX advisories before executing a high-risk tool.

```bash
./brainx-v5 advisory --tool <tool> [--args '{}'] [--agent <agent>] [--project <project>] [--json]
```

## `advisory-feedback`

Record whether an advisory was followed.

```bash
./brainx-v5 advisory-feedback --id <advisory_id> --followed yes|no [--outcome "..."]
```

## `eidos`

Behavioral prediction and pattern evaluation engine.

```bash
./brainx-v5 eidos predict|evaluate|distill|stats [options]
```
