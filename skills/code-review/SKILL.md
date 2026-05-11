---
name: code-review
model: reasoning
category: testing
description: Systematic code review patterns covering security, performance, maintainability, correctness, and testing — with severity levels, structured feedback guidance, review process, and anti-patterns to avoid. Use when reviewing PRs, establishing review standards, or improving review quality.
version: 1.0
---

# Code Review Checklist

Thorough, structured approach to reviewing code. Work through each dimension systematically rather than scanning randomly.


## Installation

### OpenClaw / Moltbot / Clawbot

```bash
npx clawhub@latest install code-review
```


---

## Review Dimensions

| Dimension | Focus | Priority |
|-----------|-------|----------|
| Security | Vulnerabilities, auth, data exposure | Critical |
| Performance | Speed, memory, scalability bottlenecks | High |
| Correctness | Logic errors, edge cases, data integrity | High |
| Maintainability | Readability, structure, future-proofing | Medium |
| Testing | Coverage, quality, reliability of tests | Medium |
| Accessibility | WCAG compliance, keyboard nav, screen readers | Medium |
| Documentation | Comments, API docs, changelog entries | Low |

---

## Security Checklist

Review every change for these vulnerabilities:

- [ ] **SQL Injection** — All queries use parameterized statements or an ORM; no string concatenation with user input
- [ ] **XSS** — User-provided content is escaped/sanitized before rendering; `dangerouslySetInnerHTML` or equivalent is justified and safe
- [ ] **CSRF Protection** — State-changing requests require valid CSRF tokens; SameSite cookie attributes are set
- [ ] **Authentication** — Every protected endpoint verifies the user is authenticated before processing
- [ ] **Authorization** — Resource access is scoped to the requesting user's permissions; no IDOR vulnerabilities
- [ ] **Input Validation** — All external input (params, headers, body, files) is validated for type, length, format, and range on the server side
- [ ] **Secrets Management** — No API keys, passwords, tokens, or credentials in source code; secrets come from environment variables or a vault
- [ ] **Dependency Safety** — New dependencies are from trusted sources, actively maintained, and free of known CVEs
- [ ] **Sensitive Data** — PII, tokens, and secrets are never logged, included in error messages, or returned in API responses
- [ ] **Rate Limiting** — Public and auth endpoints have rate limits to prevent brute-force and abuse
- [ ] **File Upload Safety** — Uploaded files are validated for type and size, stored outside the webroot, and served with safe Content-Type headers
- [ ] **HTTP Security Headers** — Content-Security-Policy, X-Content-Type-Options, Strict-Transport-Security are set

---

## Performance Checklist

- [ ] **N+1 Queries** — Database access patterns are batched or joined; no loops issuing individual queries
- [ ] **Unnecessary Re-renders** — Components only re-render when their relevant state/props change; memoization is applied where measurable
- [ ] **Memory Leaks** — Event listeners, subscriptions, timers, and intervals are cleaned up on unmount/disposal
- [ ] **Bundle Size** — New dependencies are tree-shakeable; large libraries are loaded dynamically; no full-library imports for a single function
- [ ] **Lazy Loading** — Heavy components, routes, and below-the-fold content use lazy loading / code splitting
- [ ] **Caching Strategy** — Expensive computations and API responses use appropriate caching (memoization, HTTP cache headers, Redis)
- [ ] **Database Indexing** — Queries filter/sort on indexed columns; new queries have been checked with EXPLAIN
- [ ] **Pagination** — List endpoints and queries use pagination or cursor-based fetching; no unbounded SELECT *
- [ ] **Async Operations** — Long-running tasks are offloaded to background jobs or queues rather than blocking request threads
- [ ] **Image & Asset Optimization** — Images are properly sized, use modern formats (WebP/AVIF), and leverage CDN delivery

---

## Correctness Checklist

- [ ] **Edge Cases** — Empty arrays, empty strings, zero values, negative numbers, and maximum values are handled
- [ ] **Null/Undefined Handling** — Nullable values are checked before access; optional chaining or guards prevent runtime errors
- [ ] **Off-by-One Errors** — Loop bounds, array slicing, pagination offsets, and range calculations are verified
- [ ] **Race Conditions** — Concurrent access to shared state uses locks, transactions, or atomic operations
- [ ] **Timezone Handling** — Dates are stored in UTC; display conversion happens at the presentation layer
- [ ] **Unicode & Encoding** — String operations handle multi-byte characters; text encoding is explicit (UTF-8)
- [ ] **Integer Overflow / Precision** — Arithmetic on large numbers or currency uses appropriate types (BigInt, Decimal)
- [ ] **Error Propagation** — Errors from async calls and external services are caught and handled; promises are never silently swallowed
- [ ] **State Consistency** — Multi-step mutations are transactional; partial failures leave the system in a valid state
- [ ] **Boundary Validation** — Values at the boundaries of valid ranges (min, max, exactly-at-limit) are tested

---

## Maintainability Checklist

- [ ] **Naming Clarity** — Variables, functions, and classes have descriptive names that reveal intent
- [ ] **Single Responsibility** — Each function/class/module does one thing; changes to one concern don't ripple through unrelated code
- [ ] **DRY** — Duplicated logic is extracted into shared utilities; copy-pasted blocks are consolidated
- [ ] **Cyclomatic Complexity** — Functions have low branching complexity; deeply nested chains are refactored
- [ ] **Error Handling** — Errors are caught at appropriate boundaries, logged with context, and surfaced meaningfully
- [ ] **Dead Code Removal** — Commented-out code, unused imports, unreachable branches, and obsolete feature flags are removed
- [ ] **Magic Numbers & Strings** — Literal values are extracted into named constants with clear semantics
- [ ] **Consistent Patterns** — New code follows the conventions already established in the codebase
- [ ] **Function Length** — Functions are short enough to understand at a glance; long functions are decomposed
- [ ] **Dependency Direction** — Dependencies point inward (infrastructure to domain); core logic does not import from UI or framework layers

---

## Testing Checklist

- [ ] **Test Coverage** — New logic paths have corresponding tests; critical paths have both happy-path and failure-case tests
- [ ] **Edge Case Tests** — Tests cover boundary values, empty inputs, nulls, and error conditions
- [ ] **No Flaky Tests** — Tests are deterministic; no reliance on timing, external services, or shared mutable state
- [ ] **Test Independence** — Each test sets up its own state and tears it down; test order does not affect results
- [ ] **Meaningful Assertions** — Tests assert on behavior and outcomes, not implementation details
- [ ] **Test Readability** — Tests follow Arrange-Act-Assert; test names describe the scenario and expected outcome
- [ ] **Mocking Discipline** — Only external boundaries (network, DB, filesystem) are mocked
- [ ] **Regression Tests** — Bug fixes include a test that reproduces the original bug and proves it is resolved

---

## Review Process

Work through the code in three passes. Do not try to catch everything in one read.

| Pass | Focus | Time | What to Look For |
|------|-------|------|------------------|
| First | High-level structure | 2-5 min | Architecture fit, file organization, API design, overall approach |
| Second | Line-by-line detail | Bulk | Logic errors, security issues, performance problems, edge cases |
| Third | Edge cases & hardening | 5 min | Failure modes, concurrency, boundary values, missing tests |

### First Pass (2-5 minutes)

1. Read the PR description and linked issue
2. Scan the file list — does the change scope make sense?
3. Check the overall approach — is this the right solution to the problem?
4. Verify the change does not introduce architectural drift

### Second Pass (bulk of review time)

1. Read each file diff top to bottom
2. Check every function change against the checklists above
3. Verify error handling at every I/O boundary
4. Flag anything that makes you pause — trust your instincts

### Third Pass (5 minutes)

1. Think about what could go wrong in production
2. Check for missing tests on the code paths you flagged
3. Verify rollback safety — can this change be reverted without data loss?
4. Confirm documentation and changelog are updated if needed

---

## Severity Levels

Classify every comment by severity so the author knows what blocks merge.

| Level | Label | Meaning | Blocks Merge? |
|-------|-------|---------|---------------|
| Critical | `[CRITICAL]` | Security vulnerability, data loss, or crash in production | Yes |
| Major | `[MAJOR]` | Bug, logic error, or significant performance regression | Yes |
| Minor | `[MINOR]` | Improvement that would reduce future maintenance cost | No |
| Nitpick | `[NIT]` | Style preference, naming suggestion, or trivial cleanup | No |

Always prefix your review comment with the severity label. This removes ambiguity about what matters.

---

## Giving Feedback

### Principles

- **Be specific** — Point to the exact line and explain the issue, not just "this is wrong"
- **Explain why** — State the risk or consequence, not just the rule
- **Suggest a fix** — Offer a concrete alternative or code snippet when possible
- **Ask, don't demand** — Use questions for subjective points: "What do you think about...?"
- **Acknowledge good work** — Call out clean solutions, clever optimizations, or thorough tests
- **Separate blocking from non-blocking** — Use severity labels so the author knows what matters

### Example Comments

**Bad:**
> This is wrong. Fix it.

**Good:**
> `[MAJOR]` This query interpolates user input directly into the SQL string (line 42), which is vulnerable to SQL injection. Consider using a parameterized query:
> ```sql
> SELECT * FROM users WHERE id = $1
> ```

**Bad:**
> Why didn't you add tests?

**Good:**
> `[MINOR]` The new `calculateDiscount()` function has a few branching paths — could we add tests for the zero-quantity and negative-price edge cases to prevent regressions?

**Bad:**
> I would have done this differently.

**Good:**
> `[NIT]` This works well. An alternative approach could be extracting the retry logic into a shared `withRetry()` wrapper — but that's optional and could be a follow-up.

---

## Review Anti-Patterns

Avoid these common traps that waste time and damage team trust:

| Anti-Pattern | Description |
|--------------|-------------|
| **Rubber-Stamping** | Approving without reading. Creates false confidence and lets bugs through. |
| **Bikeshedding** | Spending 30 minutes debating a variable name while ignoring a race condition. |
| **Blocking on Style** | Refusing to approve over formatting that a linter should enforce automatically. |
| **Gatekeeping** | Requiring your personal preferred approach when the submitted one is correct. |
| **Drive-by Reviews** | Leaving one vague comment and disappearing. Commit to following through. |
| **Scope Creep Reviews** | Requesting unrelated refactors that should be separate PRs. |
| **Stale Reviews** | Letting PRs sit for days. Review within 24 hours or hand off to someone else. |
| **Emotional Language** | "This is terrible" or "obviously wrong." Critique the code, not the person. |

---

## NEVER Do

1. **NEVER approve without reading every changed line** — rubber-stamping is worse than no review
2. **NEVER block a PR solely for style preferences** — use a linter; humans review logic
3. **NEVER leave feedback without a severity level** — ambiguity causes wasted cycles
4. **NEVER request changes without explaining why** — "fix this" teaches nothing
5. **NEVER review more than 400 lines in one sitting** — comprehension drops sharply; break large PRs into sessions
6. **NEVER skip the security checklist** — one missed vulnerability outweighs a hundred style nits
7. **NEVER make it personal** — review the code, never the coder; assume good intent
