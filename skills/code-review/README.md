# Code Review Checklist

Systematic code review patterns covering security, performance, maintainability, correctness, and testing — with severity levels, structured feedback guidance, review process, and anti-patterns to avoid.

## What's Inside

- Review dimensions with priority ranking (Security → Performance → Correctness → Maintainability → Testing → Accessibility → Documentation)
- Security checklist (SQL injection, XSS, CSRF, auth, secrets, rate limiting)
- Performance checklist (N+1 queries, re-renders, memory leaks, bundle size, caching)
- Correctness checklist (edge cases, null handling, race conditions, timezone handling)
- Maintainability checklist (naming, SRP, DRY, dead code, dependency direction)
- Testing checklist (coverage, edge cases, flaky tests, mocking discipline)
- Three-pass review process (high-level → line-by-line → edge cases)
- Severity levels (Critical, Major, Minor, Nitpick) with merge-blocking guidance
- Feedback principles and example comments
- Review anti-patterns to avoid

## When to Use

- Reviewing pull requests or merge requests
- Establishing review standards for a team
- Improving the quality and consistency of code reviews
- Training new reviewers on what to look for

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/testing/code-review
```

### OpenClaw / Moltbot / Clawbot

```bash
npx clawhub@latest install code-review
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/testing/code-review .cursor/skills/code-review
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/testing/code-review ~/.cursor/skills/code-review
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/testing/code-review .claude/skills/code-review
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/testing/code-review ~/.claude/skills/code-review
```

## Related Skills

- [clean-code](../clean-code/) — Coding standards that reviews enforce
- [quality-gates](../quality-gates/) — Automated quality checkpoints in CI/CD
- [testing-patterns](../testing-patterns/) — Testing standards to check during review

---

Part of the [Testing](..) skill category.
