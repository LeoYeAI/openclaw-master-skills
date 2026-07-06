# Creating a Custom Benchmark

Benchmarks are standardized test sets for evaluating Skills. This guide shows you how to create your own.

## Benchmark Schema

A benchmark is a JSON file with the following structure:

```json
{
  "id": "my-benchmark",
  "name": "My Custom Benchmark",
  "version": "1.0.0",
  "domain": "custom",
  "scoringMethod": "mean",
  "maxLatencyMs": 30000,
  "metadata": {
    "source": "Internal team",
    "lastUpdated": "2026-01-01"
  },
  "tasks": [...]
}
```

### Fields

| Field | Type | Required | Description |
|:---|:---|:---|:---|
| `id` | string | Yes | Unique benchmark ID |
| `name` | string | Yes | Human-readable name |
| `version` | string | Yes | Semver version |
| `domain` | string | Yes | Domain category (e.g., "coding", "web", "general") |
| `scoringMethod` | string | Yes | `"mean"`, `"weighted_mean"`, or `"pass_at_k"` |
| `maxLatencyMs` | number | No | Maximum expected latency for normalization (default: 30000) |
| `metadata` | object | No | Additional metadata |
| `tasks` | Task[] | Yes | Array of evaluation tasks |

## Task Schema

Each task defines an input, expected output, and scoring method:

```json
{
  "id": "task_001",
  "description": "What this task tests",
  "inputData": {
    "query": "some input"
  },
  "expectedOutput": {
    "type": "exact",
    "value": "expected result"
  },
  "evaluator": {
    "type": "exact"
  },
  "timeoutMs": 10000,
  "tags": ["category"]
}
```

## Evaluator Types

### Exact Match

```json
{
  "expectedOutput": { "type": "exact", "value": "42" },
  "evaluator": { "type": "exact" }
}
```

Score: 1.0 if output === expected, else 0.0.

### Contains Keywords

```json
{
  "expectedOutput": {
    "type": "contains",
    "keywords": ["keyword1", "keyword2"]
  },
  "evaluator": { "type": "contains", "caseSensitive": false }
}
```

Score: matched_count / total_keywords (partial scoring).

### JSON Schema Validation

```json
{
  "expectedOutput": {
    "type": "schema",
    "schema": {
      "type": "object",
      "properties": {
        "result": { "type": "string", "minLength": 1 }
      },
      "required": ["result"]
    }
  },
  "evaluator": { "type": "json_schema" }
}
```

Score: 1.0 if output matches schema, else 0.0.

### LLM Judge

```json
{
  "expectedOutput": {
    "type": "llm_judge",
    "judgePrompt": "Rate the quality of this search result on a scale of 0-10"
  },
  "evaluator": { "type": "llm_judge" }
}
```

Requires `EVAL_SKILLS_LLM_KEY` environment variable.

## Directory Structure

Benchmarks can be organized two ways:

```
benchmarks/
├── simple-bench.json              # Flat file
└── complex-bench/                 # Directory
    ├── benchmark.json             # Required
    └── README.md                  # Optional documentation
```

## Using Your Benchmark

```bash
# By ID (if placed in benchmarks/ directory)
eval-skills eval --skills ./skills/ --benchmark my-benchmark

# By file path
eval-skills eval --skills ./skills/ --benchmark ./path/to/benchmark.json

# With custom benchmarks directory
eval-skills eval --skills ./skills/ --benchmark my-benchmark --benchmarks-dir ./my-benchmarks/
```

## Best Practices

1. **Start small** — 5-10 tasks, then expand based on results
2. **Cover edge cases** — empty input, boundary values, error conditions
3. **Mix evaluator types** — use exact match for deterministic tasks, contains for fuzzy ones
4. **Set appropriate timeouts** — match the expected complexity of the task
5. **Use tags** — categorize tasks for analysis (e.g., "math", "string", "edge-case")
6. **Version your benchmarks** — update the version when adding/changing tasks
7. **Document each task** — clear descriptions help when reviewing results

## Built-in Benchmarks

| ID | Tasks | Domain | Description |
|:---|:---|:---|:---|
| `coding-easy` | 20 | Coding | Basic math and string operations |
| `skill-quality` | 5 | Tool Use | Skill metadata quality checks |
| `web-search-basic` | 8 | Web | Basic web search tasks |
