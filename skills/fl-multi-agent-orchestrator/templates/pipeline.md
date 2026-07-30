# Sequential Pipeline Template

## Overview
Chain agents in sequence where each stage's output feeds into the next stage's input. Assembly-line processing with quality gates between stages.

## When to Use
- Content creation workflows (research, write, review, publish)
- Code generation with validation (generate, lint, test, review)
- Data processing (extract, transform, validate, load)
- Any workflow with strict ordering requirements

## Configuration

```yaml
orchestration:
  pattern: pipeline
  budget_usd: 3.00
  timeout_minutes: 20
  abort_on_stage_failure: true

stages:
  - name: generate
    model: sonnet
    tools: [Read, Write, Edit, Bash, Grep, Glob]
    max_turns: 20
    budget_usd: 0.50

  - name: review
    model: opus
    tools: [Read, Grep, Glob]
    max_turns: 10
    budget_usd: 0.30

  - name: fix
    model: sonnet
    tools: [Read, Write, Edit]
    max_turns: 15
    budget_usd: 0.40
    condition: "review.verdict == 'FAIL'"

  - name: test
    model: haiku
    tools: [Read, Write, Bash]
    max_turns: 10
    budget_usd: 0.20
```

## Stage Contract

Every stage must define its input/output contract:

```yaml
stage:
  name: [stage-name]
  input:
    type: [file|text|structured]
    source: [previous stage output or user input]
    path: ".orchestrator/stage-N-output.md"   # if file-based
  output:
    type: [file|text|structured]
    path: ".orchestrator/stage-N+1-output.md"
    format: |
      ## Stage Output: [stage-name]
      ### Status: [SUCCESS|FAIL]
      ### Data:
      [structured output here]
  validation:
    required_fields: [list of fields that must be present]
    max_size_kb: 100
  on_failure:
    action: [retry|abort|skip]
    max_retries: 2
```

## Context Passing Protocol

Agents pass context via intermediate files to avoid token bloat:

```
.orchestrator/
  pipeline-config.json        # Pipeline definition
  stage-1-generate-output.md  # Stage 1 output
  stage-2-review-output.md    # Stage 2 output
  stage-3-fix-output.md       # Stage 3 output (if needed)
  stage-4-test-output.md      # Stage 4 output
  pipeline-report.md          # Final aggregated report
```

Each agent's prompt includes:
```
Read the previous stage output at: .orchestrator/stage-N-output.md
Write your output to: .orchestrator/stage-N+1-output.md
```

## Agent Prompts by Stage

### Stage 1: Generate
```
You are the Generator agent in a sequential pipeline.

INPUT: [user requirements]
YOUR TASK: [generate the initial deliverable]

Write your output to .orchestrator/stage-1-generate-output.md

Requirements:
- [specific requirements]
- Follow the output format exactly
- Include metadata (timestamp, files modified, confidence level)
```

### Stage 2: Review
```
You are the Reviewer agent in a sequential pipeline.

INPUT: Read .orchestrator/stage-1-generate-output.md
YOUR TASK: Review the generated output against these criteria:

1. Correctness (1-10)
2. Completeness (1-10)
3. Code quality (1-10)
4. Security (1-10)
5. Performance (1-10)

Write your review to .orchestrator/stage-2-review-output.md

Format:
## Review Report
### Scores: [table]
### Overall: [N/10]
### Verdict: [PASS if >= 7, FAIL if < 7]
### Issues (if FAIL):
- Issue 1: [description] -> [fix suggestion]
- Issue 2: [description] -> [fix suggestion]
```

### Stage 3: Fix (Conditional)
```
You are the Fixer agent in a sequential pipeline.
This stage only runs if the review verdict was FAIL.

INPUT:
- Original output: .orchestrator/stage-1-generate-output.md
- Review feedback: .orchestrator/stage-2-review-output.md

YOUR TASK: Address every issue listed in the review.

Write the fixed output to .orchestrator/stage-3-fix-output.md

For each issue:
1. Read the issue description
2. Apply the suggested fix (or a better one)
3. Document what you changed and why
```

### Stage 4: Test
```
You are the Tester agent in a sequential pipeline.

INPUT: Read the latest output (.orchestrator/stage-3-fix-output.md or stage-1 if no fix was needed)
YOUR TASK: Validate the output works correctly.

1. Write tests for the generated code
2. Run the tests
3. Report pass/fail with details

Write results to .orchestrator/stage-4-test-output.md
```

## Error Handling

### Stage Failure Flow
```
Stage N fails
  ├── retry_count < max_retries?
  │     YES → Retry stage N with same input
  │     NO  → abort_on_stage_failure?
  │            YES → Cancel pipeline, report partial results
  │            NO  → Skip stage N, continue to N+1 (mark gap)
  └── Final report includes failure details
```

### Conditional Stages
Some stages only run under certain conditions:
```yaml
- name: fix
  condition: "review.verdict == 'FAIL'"

- name: deploy
  condition: "test.pass_rate >= 0.95"

- name: rollback
  condition: "deploy.status == 'FAIL'"
```

## Cost Estimate
- Generator (Sonnet): $0.10-0.30
- Reviewer (Opus): $0.15-0.40
- Fixer (Sonnet, conditional): $0.05-0.20
- Tester (Haiku): $0.02-0.10
- **Total: $0.30-1.00** per pipeline run

## Real-World Example: API Endpoint Creation

```yaml
pipeline:
  task: "Create a REST API endpoint for user profiles with CRUD operations"

  stages:
    - name: generate
      prompt: "Create the API routes, controllers, and models for user profiles CRUD"
      output_files: [src/routes/users.ts, src/controllers/users.ts, src/models/user.ts]

    - name: review
      prompt: "Review for security (SQL injection, auth), error handling, and REST conventions"

    - name: fix
      condition: "review.verdict == FAIL"
      prompt: "Fix all issues from the review"

    - name: test
      prompt: "Write integration tests with supertest, covering happy path and edge cases"
      output_files: [tests/users.test.ts]

    - name: document
      prompt: "Generate OpenAPI spec and update README with the new endpoints"
      output_files: [docs/openapi.yaml, README.md]
```
