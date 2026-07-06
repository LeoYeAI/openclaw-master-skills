---
name: eval-skills
description: >-
  AI Agent Skill unit testing framework. A framework-agnostic toolkit for
  discovering, scaffolding, selecting, evaluating, and reporting on AI skills.
  Use this skill to assess skill quality before production, compare candidate
  skills on the same benchmark, enforce quality gates in CI/CD, and generate
  human-readable evaluation reports.
version: 0.1.0
---

# eval-skills

AI Agent Skill unit testing framework — a framework-agnostic toolkit for discovering, scaffolding, selecting, evaluating, and reporting on AI skills.

This skill fills the **L1 (Skill Unit Test)** gap that LangSmith / DeepEval leave open: while those platforms focus on agent-level and trajectory-level evaluation (L2-L3), eval-skills targets the individual skill level, ensuring each building block meets quality standards before it ever enters an agent pipeline.

## When to Use This Skill

- **Before deploying a new skill to production** — run `eval` to verify it meets your quality gate.
- **When choosing between multiple candidate skills** — run `select` to rank them on the same benchmark.
- **When a skill is upgraded** — run `report diff` to detect regressions.
- **In CI/CD** — use `--exit-on-fail` to block merges that degrade skill quality.
- **When bootstrapping a new skill** — run `create` to generate a ready-to-fill skeleton.

## Capabilities

### 1. Find Skills

Search for existing skills by keyword, tag, or adapter type.

```bash
eval-skills find \
  --query "web search" \
  --tag retrieval api \
  --adapter http \
  --min-completion 0.8 \
  --skills-dir ./skills \
  --limit 10
```

| Option | Description | Default |
|--------|-------------|---------|
| `-q, --query <string>` | Keyword search (matches name, description, tags) | — |
| `-t, --tag <tags...>` | Filter by tags (intersection: skill must have ALL specified tags) | — |
| `-a, --adapter <type>` | Filter by adapter type (`http`, `subprocess`, `mcp`) | — |
| `--min-completion <rate>` | Minimum historical completion rate (0.0 ~ 1.0) | — |
| `--skills-dir <dir>` | Directory to scan for `skill.json` files | `./skills` |
| `--limit <n>` | Maximum number of results | `20` |

Results are ranked by search relevance (when `--query` is provided) or by historical completion rate (descending).

### 2. Create Skills

Generate a skill skeleton from a template to bootstrap development.

```bash
eval-skills create \
  --name my_api_skill \
  --from-template http_request \
  --output-dir ./skills \
  --description "Fetches weather data from OpenWeather API"
```

| Option | Description | Default |
|--------|-------------|---------|
| `--name <name>` | **Required.** Skill name | — |
| `--from-template <tpl>` | Template type: `http_request`, `python_script`, `mcp_tool` | `http_request` |
| `--output-dir <dir>` | Output directory | `./skills` |
| `--description <text>` | Human-readable description embedded in `skill.json` | — |

Generated file structure:

```
skills/my_api_skill/
  skill.json            # Skill metadata (id, schemas, adapter config)
  adapter.config.json   # Adapter-specific configuration
  tests/
    basic.eval.json     # A starter benchmark with one sample task
  skill.py              # (python_script template only) JSON-RPC entrypoint
```

### 3. Evaluate Skills

Run benchmark evaluations against one or more skills. This is the core command.

```bash
eval-skills eval \
  --skills ./skills/calculator/skill.json ./skills/search/ \
  --benchmark coding-easy \
  --concurrency 4 \
  --timeout 30000 \
  --retries 2 \
  --runs 3 \
  --evaluator exact \
  --format json markdown html \
  --output-dir ./reports \
  --exit-on-fail --min-completion 0.8 \
  --store ./eval-skills.db
```

| Option | Description | Default |
|--------|-------------|---------|
| `--skills <paths...>` | **Required.** Skill file(s) or directory(ies) | — |
| `--benchmark <id\|path>` | Built-in benchmark ID or path to `benchmark.json` | `coding-easy` |
| `--tasks <file>` | Custom tasks JSON file (replaces benchmark) | — |
| `--concurrency <n>` | Number of parallel task executions | `4` |
| `--timeout <ms>` | Per-task timeout in milliseconds | `30000` |
| `--retries <n>` | Retry count on task failure (with incremental backoff) | `0` |
| `--runs <n>` | Repeat evaluation N times for consistency scoring | `1` |
| `--evaluator <type>` | Default scorer type (see Scorer Types below) | `exact` |
| `--format <formats...>` | Output formats: `json`, `markdown`, `html` | `json markdown` |
| `--output-dir <dir>` | Report output directory | `./reports` |
| `--exit-on-fail` | Exit with code 1 if any skill falls below threshold | disabled |
| `--min-completion <rate>` | Threshold for `--exit-on-fail` | `0.7` |
| `--dry-run` | Validate configuration only; do not execute tasks | disabled |
| `--benchmarks-dir <dir>` | Directory containing built-in benchmarks | `./benchmarks` |
| `--store <path>` | SQLite database path for persistent result storage | `./eval-skills.db` |
| `-c, --config <path>` | Path to `eval-skills.config.yaml` | auto-detected |

**Evaluation flow:**

1. Load skills from `--skills` paths (supports both single `skill.json` and directories)
2. Load benchmark tasks from `--benchmark` or `--tasks`
3. Build the cartesian product: `skills x tasks x runs`
4. Execute all task items concurrently (controlled by `--concurrency`, with timeout and retry)
5. Score each result using the appropriate scorer
6. Aggregate into `SkillCompletionReport` per skill
7. Write reports to `--output-dir`

### 4. Select Skills

Filter and rank skills based on evaluation reports using a multi-dimensional strategy.

```bash
eval-skills select \
  --from ./skills \
  --reports ./reports/eval-result.json \
  --strategy ./strategy.yaml \
  --min-completion 0.8 \
  --top-k 5 \
  --output ./selected.json
```

| Option | Description | Default |
|--------|-------------|---------|
| `--from <path>` | **Required.** Candidate skills directory or JSON file | — |
| `--reports <file>` | Evaluation reports JSON file | — |
| `--strategy <file>` | SelectStrategy YAML/JSON file | built-in default |
| `--min-completion <rate>` | Override minimum completion rate filter | — |
| `--top-k <n>` | Return only the top K results | all |
| `--output <file>` | Write selected skills to file | stdout |

**Selection pipeline:** Filter (by completion rate, error rate, latency, adapter type, required tags) -> Score -> Rank (by compositeScore, completionRate, latency, or tokenCost) -> TopK

Example `strategy.yaml`:

```yaml
filters:
  minCompletionRate: 0.8
  maxErrorRate: 0.1
  maxLatencyP95Ms: 5000
  adapterTypes: [http, subprocess]
  requiredTags: [production-ready]
sortBy: compositeScore
order: desc
topK: 5
```

### 5. Run Pipeline

Execute the full end-to-end pipeline: **Find -> Eval -> Select -> Report** in a single command.

```bash
eval-skills run \
  --query "math" \
  --benchmark coding-easy \
  --skills-dir ./skills \
  --top-k 3 \
  --min-completion 0.7 \
  --format json markdown \
  --output-dir ./reports
```

This command automates the entire process:
1. **Find** — scans `--skills-dir` and optionally filters by `--query`
2. **Eval** — evaluates all candidate skills against `--benchmark`
3. **Select** — filters and ranks results using `--min-completion`, `--top-k`, and optional `--strategy`
4. **Report** — generates output files in all requested `--format`s

### 6. Generate & Compare Reports

#### Convert report format

```bash
eval-skills report convert \
  --input ./reports/eval-result.json \
  --format html \
  --output ./reports/eval-result.html
```

Supported output formats: `markdown`, `html`.

#### Diff two reports (regression detection)

```bash
eval-skills report diff \
  ./reports/v1.json ./reports/v2.json \
  --label-a "v1.0" --label-b "v2.0" \
  --output ./reports/diff.md
```

Generates a side-by-side delta table per skill showing changes in completion rate, error rate, P95 latency, and composite score with directional arrows.

### 7. Initialize Project

```bash
eval-skills init --dir .
```

Creates the project scaffold:
- `eval-skills.config.yaml` — global configuration
- `skills/` — directory for skill definitions
- `benchmarks/` — directory for benchmark files
- `reports/` — directory for evaluation output

### 8. Manage Configuration

```bash
# List all current configuration values
eval-skills config list

# Get a specific value (supports dot notation)
eval-skills config get llm.model

# Set a value (persisted to ~/.eval-skills/config.yaml)
eval-skills config set concurrency 8
eval-skills config set llm.model gpt-4o
eval-skills config set llm.temperature 0
```

Configuration is resolved in priority order:
1. CLI flags (highest priority)
2. `eval-skills.config.yaml` in current directory
3. `~/.eval-skills/config.yaml`
4. Built-in defaults (`concurrency: 4`, `timeoutMs: 30000`, `outputDir: ./reports`)

## Scorer Types

Each task in a benchmark specifies an evaluator type. The scorer compares the skill's actual output against the expected output.

| Type | Aliases | Description | Score Range |
|------|---------|-------------|-------------|
| `exact_match` | `exact` | Strict equality comparison. Supports `caseSensitive` option. | 0 or 1 |
| `contains` | — | Checks for the presence of all specified keywords in the output. Partial credit: `matched_keywords / total_keywords`. | 0.0 ~ 1.0 |
| `json_schema` | `schema` | Validates output against a JSON Schema (using Ajv). | 0 or 1 |
| `llm_judge` | — | Sends the output + expected rubric to an LLM (configurable model) for quality rating. | 0.0 ~ 1.0 |
| `custom` | — | Loads a custom scorer from `expectedOutput.customScorerPath`. | 0.0 ~ 1.0 |

## Evaluation Metrics

Every evaluation produces a `SkillCompletionReport` with these metrics:

| Metric | Description | Formula |
|--------|-------------|---------|
| **Completion Rate** | Fraction of tasks that passed | `pass_count / total_count` |
| **Partial Score** | Mean score across all tasks | `mean(task_scores)` |
| **Error Rate** | Fraction of tasks that errored or timed out | `(error_count + timeout_count) / total_count` |
| **Consistency Score** | Stability across multiple runs (requires `--runs >= 2`) | `1 - stddev(per_run_completion_rates)` |
| **P50 / P95 / P99 Latency** | Response time percentiles | Sorted percentile of `latencyMs` |
| **Composite Score** | Weighted overall quality score | `0.5 * CR + 0.2 * (1 - latP95_norm) + 0.3 * (1 - ER)` |

## Built-in Benchmarks

| ID | Domain | Tasks | Scoring | Description |
|----|--------|------:|---------|-------------|
| `coding-easy` | coding | 20 | mean / exact_match | Math expressions, string reversal, palindrome detection |
| `skill-quality` | tool-use | 5 | mean / contains | Metadata completeness, description quality, structure checks |
| `web-search-basic` | web | 8 | mean / contains + schema | Factual queries, keyword verification, structured output validation |
| `gaia-v1` | general | — | mean | Placeholder for GAIA benchmark Level 1 tasks |
| `toolbench-lite` | tool-use | — | mean | Placeholder for ToolBench single-tool scenarios |

### Custom Benchmark

Create a `benchmark.json` file:

```json
{
  "id": "my-benchmark",
  "name": "My Custom Benchmark",
  "version": "1.0.0",
  "domain": "general",
  "scoringMethod": "mean",
  "maxLatencyMs": 30000,
  "metadata": { "source": "internal", "lastUpdated": "2026-02-28" },
  "tasks": [
    {
      "id": "task_001",
      "description": "Test basic addition",
      "inputData": { "expression": "2+3" },
      "expectedOutput": { "type": "exact", "value": "5" },
      "evaluator": { "type": "exact" },
      "timeoutMs": 10000,
      "tags": ["math"]
    },
    {
      "id": "task_002",
      "description": "Test keyword presence",
      "inputData": { "query": "TypeScript" },
      "expectedOutput": { "type": "contains", "keywords": ["JavaScript", "Microsoft"] },
      "evaluator": { "type": "contains", "caseSensitive": false },
      "timeoutMs": 15000,
      "tags": ["search"]
    }
  ]
}
```

```bash
eval-skills eval --skills ./my-skill/ --benchmark ./my-benchmark.json
```

## Adapter Types

Skills communicate through adapters. The adapter type is specified in `skill.json` via `adapterType`.

| Adapter | Protocol | How it works | Key config |
|---------|----------|-------------|------------|
| `http` | REST POST | Sends `POST { skillId, version, input }` to `skill.entrypoint`. Supports Bearer / API-Key auth via env vars. | `baseUrl`, `authType`, `authTokenEnvKey` |
| `subprocess` | JSON-RPC 2.0 over stdin/stdout | Spawns `skill.entrypoint` (e.g. `python3 skill.py`), writes JSON-RPC request to stdin, reads response from stdout. | `command`, `args` |
| `mcp` | MCP Protocol | *(Phase 2)* Native Model Context Protocol integration via `@modelcontextprotocol/sdk`. | — |

## Workflow Examples

### Evaluating a Single Skill

```bash
# 1. Create a skill skeleton
eval-skills create --name my_calc --from-template python_script

# 2. Implement your logic in skills/my_calc/skill.py

# 3. Run evaluation against the coding-easy benchmark
eval-skills eval \
  --skills ./skills/my_calc/skill.json \
  --benchmark coding-easy \
  --runs 3 \
  --format json markdown

# 4. Review the report
cat ./reports/eval-result-*.md
```

### Comparing Multiple Candidate Skills

```bash
# 1. Discover candidates
eval-skills find --query "weather" --skills-dir ./skills

# 2. Evaluate all candidates on the same benchmark
eval-skills eval \
  --skills ./skills/weather_v1 ./skills/weather_v2 ./skills/weather_v3 \
  --benchmark web-search-basic \
  --runs 3

# 3. Select the best
eval-skills select \
  --from ./skills \
  --reports ./reports/eval-result-*.json \
  --min-completion 0.8 \
  --top-k 2

# 4. Compare two versions
eval-skills report diff \
  ./reports/v1.json ./reports/v2.json \
  --label-a "weather_v1" --label-b "weather_v2"
```

### Full Pipeline (One Command)

```bash
eval-skills run \
  --skills-dir ./skills \
  --benchmark coding-easy \
  --top-k 3 \
  --min-completion 0.7 \
  --format json markdown html \
  --output-dir ./reports
```

### CI/CD Quality Gate

```bash
# In your CI pipeline — fail the build if completion rate drops below 80%
eval-skills eval \
  --skills ./skills/production_skill \
  --benchmark coding-easy \
  --exit-on-fail \
  --min-completion 0.8 \
  --format json
```

### Regression Detection

```bash
# Compare today's evaluation against the baseline
eval-skills report diff \
  ./reports/baseline.json ./reports/latest.json \
  --label-a "baseline" --label-b "latest" \
  --output ./reports/regression-check.md
```

## Best Practices

1. **Always use `--runs 3` or more** when evaluating for production decisions. Single-run results can be noisy; the consistency score captures stability across runs.

2. **Use `--exit-on-fail` in CI/CD pipelines** to enforce quality gates. Set `--min-completion` to your acceptable threshold (recommended: 0.8 for production skills).

3. **Create domain-specific custom benchmarks** rather than relying solely on built-in ones. Your custom benchmark should reflect real-world inputs your skill will encounter.

4. **Use `report diff` after every skill upgrade** to catch regressions early. Compare the new evaluation against a saved baseline report.

5. **Use `--dry-run` before long evaluations** to validate your configuration (skill paths, benchmark resolution, task count) without actually executing tasks.

6. **Persist results with `--store`** to track skill quality over time. The SQLite store enables historical trend queries.

7. **Start with `--concurrency 1` when debugging** a failing skill, then increase for production benchmarking.

8. **Tag your benchmark tasks** to enable per-category analysis (e.g., filter by `math`, `string`, `edge-case`).

## Skill JSON Schema

Every skill must provide a `skill.json` that conforms to this structure:

```json
{
  "id": "my_skill_v1",
  "name": "My Skill",
  "version": "1.0.0",
  "description": "Does something useful",
  "tags": ["utility", "math"],
  "inputSchema": {
    "type": "object",
    "properties": { "query": { "type": "string" } },
    "required": ["query"]
  },
  "outputSchema": {
    "type": "object",
    "properties": { "result": { "type": "string" } }
  },
  "adapterType": "subprocess",
  "entrypoint": "python3 skill.py",
  "metadata": {
    "author": "Your Name",
    "license": "MIT",
    "homepage": "https://github.com/you/my-skill"
  }
}
```

Validation rules:
- `id`: lowercase alphanumeric with `_` or `-`, non-empty
- `version`: semver format (`X.Y.Z`)
- `adapterType`: one of `http`, `subprocess`, `mcp`, `langchain`, `custom`
- `entrypoint`: non-empty string (URL for http, command for subprocess)

## Global Options

These options are available on all commands:

| Option | Description |
|--------|-------------|
| `-c, --config <path>` | Path to configuration file |
| `--json` | JSON output format (CI-friendly) |
| `--no-color` | Disable colored output |
| `-v, --verbose` | Verbose logging |
| `--version` | Show version |
| `-h, --help` | Show help |
