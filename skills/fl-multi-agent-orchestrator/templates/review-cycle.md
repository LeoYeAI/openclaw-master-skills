# Review Cycle Template (Build-Review-Fix Loop)

## Overview
Iterative improvement loop where a builder creates output, a reviewer evaluates it against quality criteria, and the builder fixes issues based on feedback. Repeats until the quality threshold is met or max iterations are exhausted.

## When to Use
- Quality-critical code (auth, payments, security)
- Polished content (blog posts, documentation, marketing copy)
- Complex implementations that benefit from iterative refinement
- Any output that must meet a defined quality bar before shipping

## Architecture

```
                 ┌─────────────────────────────┐
                 │                             │
                 ▼                             │
Iteration 1:  Builder ──► Reviewer             │
                           │                   │
                     ┌─────┴─────┐             │
                     │           │             │
                  PASS ≥7    FAIL <7           │
                     │           │             │
                     ▼           ▼             │
                  Result     Feedback ─────────┘
                              (max 3 iterations)
```

## Configuration

```yaml
orchestration:
  pattern: review-cycle
  max_iterations: 3
  pass_threshold: 7
  budget_usd: 3.00

roles:
  builder:
    model: sonnet
    tools: [Read, Write, Edit, Bash, Grep, Glob]
    max_turns: 20
    budget_usd: 0.50

  reviewer:
    model: opus
    tools: [Read, Grep, Glob]
    max_turns: 10
    budget_usd: 0.30

escalation:
  action: "flag_for_human"
  message: "Failed quality gate after 3 iterations — needs human review"
```

## Iteration Protocol

### Iteration 1: Initial Build

**Builder prompt:**
```
You are the Builder agent. Create the initial implementation.

TASK: [user's task description]

REQUIREMENTS:
[specific requirements list]

Write your output to the appropriate files.
When done, write a summary to .orchestrator/build-iteration-1.md including:
- What you created
- Files modified
- Design decisions made
- Known limitations or trade-offs
```

**Reviewer prompt:**
```
You are the Reviewer agent. Evaluate the Builder's output.

TASK REQUIREMENTS: [original requirements]
BUILDER OUTPUT: Read .orchestrator/build-iteration-1.md and the modified files.

REVIEW CRITERIA (score each 1-10):

1. **Correctness** — Does it work? Are there logic errors, off-by-ones, null pointer risks?
2. **Completeness** — Does it cover ALL requirements? Any missing edge cases?
3. **Code Quality** — Clean architecture? DRY? Proper abstractions? Good naming?
4. **Security** — Input validation? Auth checks? SQL injection? XSS? CSRF?
5. **Performance** — N+1 queries? Unnecessary re-renders? Missing indexes? Memory leaks?
6. **Error Handling** — Graceful failures? User-facing error messages? Logging?
7. **Testability** — Can this be unit tested? Are dependencies injectable?

SCORING:
- Calculate average of all criteria
- PASS: average >= 7
- FAIL: average < 7

OUTPUT FORMAT:
Write to .orchestrator/review-iteration-1.md:

## Review Report — Iteration 1

### Scores
| Criterion | Score | Notes |
|-----------|-------|-------|
| Correctness | X/10 | ... |
| Completeness | X/10 | ... |
| Code Quality | X/10 | ... |
| Security | X/10 | ... |
| Performance | X/10 | ... |
| Error Handling | X/10 | ... |
| Testability | X/10 | ... |

### Overall Score: X.X/10
### Verdict: PASS / FAIL

### Issues (if FAIL — ordered by severity):
1. [CRITICAL] Description → Suggested fix
2. [HIGH] Description → Suggested fix
3. [MEDIUM] Description → Suggested fix
4. [LOW] Description → Suggested fix

### What Went Well:
- [positive feedback to reinforce good patterns]
```

### Iteration 2+ : Fix Based on Feedback

**Builder prompt (fix iteration):**
```
You are the Builder agent. The Reviewer found issues with your work.

ORIGINAL TASK: [user's task]
YOUR PREVIOUS OUTPUT: Read .orchestrator/build-iteration-N.md
REVIEW FEEDBACK: Read .orchestrator/review-iteration-N.md

ADDRESS EACH ISSUE:
For every issue listed in the review:
1. Read the issue description and severity
2. Apply the fix (or implement a better solution)
3. Document what you changed

PRIORITY: Fix CRITICAL and HIGH issues first. MEDIUM and LOW are nice-to-have.

Write updated summary to .orchestrator/build-iteration-N+1.md including:
- Issues addressed (with before/after)
- Issues skipped (with justification)
- Any new concerns introduced by the fixes
```

## Decision Flow

```
iteration = 1

LOOP:
  Builder creates/fixes output
  Reviewer evaluates output

  if reviewer.score >= pass_threshold:
    PASS → Return final output + review history

  if iteration >= max_iterations:
    ESCALATE → Flag for human review with full history
    Return best iteration's output + all review reports

  iteration += 1
  Builder receives reviewer feedback
  GOTO LOOP
```

## Review History Tracking

Maintain a running log for transparency:

```markdown
# Review Cycle History

## Iteration 1
- Builder: Created initial implementation
- Reviewer: Score 5.4/10 — FAIL
  - 3 CRITICAL issues, 2 HIGH issues
  - Main concern: Missing auth checks on API routes

## Iteration 2
- Builder: Fixed all CRITICAL and HIGH issues
- Reviewer: Score 7.8/10 — PASS
  - All critical issues resolved
  - 2 LOW suggestions for future improvement

## Final Output
- Iteration: 2 of 3 max
- Final score: 7.8/10
- Total cost: $1.60
- Files modified: [list]
```

## Error Handling

| Scenario | Response |
|----------|----------|
| Builder fails mid-iteration | Retry with fresh agent; pass previous iteration's output as starting point |
| Reviewer gives inconsistent scores | Log anomaly; if scores contradict the issues list, re-run review |
| Score oscillates (improves then worsens) | Cap at best score achieved; investigate if fixes are breaking other things |
| Max iterations reached, still failing | Return best iteration + full review history; flag for human |
| Budget exceeded mid-cycle | Return current state with partial review |

## Score Calibration

To prevent overly strict or lenient reviews:

```
Calibration guidelines for the Reviewer:
- 9-10: Production-ready, exemplary code. No changes needed.
- 7-8: Good quality. Minor improvements possible but not blocking.
- 5-6: Functional but has significant issues. Needs another iteration.
- 3-4: Fundamental problems. Major rework needed.
- 1-2: Doesn't work or is completely wrong.

A score of 7 means: "I would approve this PR with minor comments."
```

## Cost Estimates

| Iterations | Builder (Sonnet) | Reviewer (Opus) | Total |
|-----------|-------------------|------------------|-------|
| 1 (pass)  | $0.10-0.30       | $0.15-0.30      | $0.25-0.60 |
| 2 (fix)   | $0.20-0.60       | $0.30-0.60      | $0.50-1.20 |
| 3 (max)   | $0.30-0.90       | $0.45-0.90      | $0.75-1.80 |

## Real-World Example: Secure Auth Endpoint

```yaml
review_cycle:
  task: "Build JWT authentication with refresh tokens, rate limiting, and account lockout"
  max_iterations: 3
  pass_threshold: 8  # Higher bar for security-critical code

  builder:
    model: sonnet
    initial_prompt: |
      Build a complete JWT auth system:
      - Login endpoint with email/password
      - JWT access tokens (15min) + refresh tokens (7 days)
      - Rate limiting: 5 failed attempts → 15min lockout
      - Secure token storage (httpOnly cookies)
      - Token rotation on refresh
      - Logout (invalidate refresh token)

  reviewer:
    model: opus
    criteria:
      - "OWASP Top 10 compliance"
      - "Token handling best practices (no localStorage)"
      - "Rate limiting is per-account, not per-IP"
      - "Refresh token rotation prevents replay attacks"
      - "Timing-safe password comparison"
      - "Proper error messages (no info leakage)"

  expected_iterations: 2
  # First build usually misses timing-safe comparison and token rotation
  # Second iteration with specific feedback produces production-ready code
```

## Combining with Other Patterns

### Review Cycle + Swarm
Run a swarm to build the feature, then run a review cycle on the combined output:
```
Phase 1: Swarm (4 agents build different modules in parallel)
Phase 2: Review Cycle (reviewer evaluates the integrated result, builder fixes integration issues)
```

### Review Cycle + Pipeline
Add review cycle as a stage in a pipeline:
```
Stage 1: Generate (builder)
Stage 2: Review Cycle (iterate until quality bar met)
Stage 3: Test (tester validates the reviewed output)
Stage 4: Deploy (only if tests pass)
```
