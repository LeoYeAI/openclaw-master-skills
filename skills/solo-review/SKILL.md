---
name: solo-review
description: Final code review and quality gate — run tests, check coverage, audit security, verify acceptance criteria from spec, and generate ship-ready report. Use when user says "review code", "quality check", "is it ready to ship", "final review", or after /deploy completes. Do NOT use for planning (use /plan) or building (use /build).
license: MIT
metadata:
  author: fortunto2
  version: "1.1.1"
  openclaw:
    emoji: "🔎"
allowed-tools: Read, Grep, Bash, Glob, Write, Edit, mcp__solograph__session_search, mcp__solograph__project_code_search, mcp__solograph__codegraph_query, mcp__solograph__codegraph_explain, mcp__solograph__web_search, mcp__context7__resolve-library-id, mcp__context7__query-docs
argument-hint: "[focus-area]"
---

# /review

This skill is self-contained — follow the instructions below instead of delegating to external review skills (superpowers, etc.) or spawning Task subagents. Run all checks directly.

Final quality gate before shipping. Runs tests, checks security, verifies acceptance criteria from spec.md, audits code quality, and generates a ship-ready report with go/no-go verdict.

## When to use

After `/deploy` (or `/build` if deploying manually). This is the quality gate.

Pipeline: `/deploy` → **`/review`**

Can also be used standalone: `/review` on any project to audit code quality.

## MCP Tools (use if available)

- `session_search(query)` — find past review patterns and common issues
- `project_code_search(query, project)` — find similar code patterns across projects
- `codegraph_query(query)` — check dependencies, imports, unused code

If MCP tools are not available, fall back to Glob + Grep + Read.

## Pre-flight Checks

### 1. Architecture overview (if MCP available)
```
codegraph_explain(project="{project name}")
```
Returns: stack, languages, directory layers, key patterns, top dependencies, hub files. Use this to detect stack and understand project structure.

### 2. Essential docs (parallel reads)
- `CLAUDE.md` — architecture, Do/Don't rules
- `docs/plan/*/spec.md` — acceptance criteria to verify (REQUIRED)
- `docs/plan/*/plan.md` — task completion status (REQUIRED)
- `docs/workflow.md` — TDD policy, quality standards, **integration testing commands** (if exists)

**Do NOT read source code at this stage.** Only docs.

### 3. Detect stack
Use stack from `codegraph_explain` response (or `CLAUDE.md` if no MCP) to choose tools:
- Next.js → `npm run build`, `npm test`, `npx next lint`
- Python → `uv run pytest`, `uv run ruff check`
- Swift → `swift test`, `swiftlint`
- Kotlin → `./gradlew test`, `./gradlew lint`

### 4. Smart source code loading (for code quality spot check)

**Do NOT read random source files.** Use the graph to find the most important code:

```
codegraph_query("MATCH (f:File {project: '{name}'})-[e]-() RETURN f.path, COUNT(e) AS edges ORDER BY edges DESC LIMIT 5")
```

Read only the top 3-5 hub files (most connected = most impactful). For security checks, use Grep with narrow patterns (`sk_live`, `password\s*=`) — not full file reads.

## Review Dimensions

**Makefile convention:** If `Makefile` exists in project root, **always prefer `make` targets** over raw commands. Use `make test` instead of `npm test`, `make lint` instead of `pnpm lint`, `make build` instead of `pnpm build`. Run `make help` (or read Makefile) to discover available targets including integration tests.

Run all 12 dimensions in sequence. Report findings per dimension.

### 1. Test Suite

Run the full test suite (prefer `make test` if Makefile exists):
```bash
# If Makefile exists — use it
make test 2>&1 || true

# Fallback: Next.js / Node
npm test -- --coverage 2>&1 || true

# Python
uv run pytest --tb=short -q 2>&1 || true

# Swift
swift test 2>&1 || true
```

Report:
- Total tests: pass / fail / skip
- Coverage percentage (if available)
- Any failing tests with file:line references

**Integration tests** — if `docs/workflow.md` has an "Integration Testing" section, run the specified commands:
- Execute the CLI/integration commands listed there
- Verify exit code 0 and expected output format
- Report: command run, exit code, pass/fail

### 2. Linter & Type Check

```bash
# Next.js
pnpm lint 2>&1 || true
pnpm tsc --noEmit 2>&1 || true

# Python
uv run ruff check . 2>&1 || true
uv run ty check . 2>&1 || true

# Swift
swiftlint lint --strict 2>&1 || true

# Kotlin
./gradlew detekt 2>&1 || true
./gradlew ktlintCheck 2>&1 || true
```

Report: warnings count, errors count, top issues.

### 3. Build Verification

```bash
# Next.js
npm run build 2>&1 || true

# Python
uv run python -m py_compile src/**/*.py 2>&1 || true

# Astro
npm run build 2>&1 || true
```

Report: build success/failure, any warnings.

### 4. Security Audit

**Dependency vulnerabilities:**
```bash
# Node
npm audit --audit-level=moderate 2>&1 || true

# Python
uv run pip-audit 2>&1 || true
```

**Code-level checks** (Grep for common issues):
- Hardcoded secrets: `grep -rn "sk_live\|sk_test\|password\s*=\s*['\"]" src/ app/ lib/`
- SQL injection: look for string concatenation in queries
- XSS: look for `dangerouslySetInnerHTML` without sanitization
- Exposed env vars: check `.gitignore` includes `.env*`

Report: vulnerabilities found, severity levels.

### 5. Acceptance Criteria Verification

Read `docs/plan/*/spec.md` and check each acceptance criterion:

For each `- [ ]` criterion in spec.md:
1. Search codebase for evidence it was implemented.
2. Check if related tests exist.
3. Mark as verified or flag as missing.

**Update spec.md checkboxes.** After verifying each criterion, use Edit tool to change `- [ ]` to `- [x]` in spec.md. Leaving verified criteria unchecked causes staleness across pipeline runs — check them off as you go.

```
Acceptance Criteria:
  - [x] User can sign up with email — found in app/auth/signup/page.tsx + test
  - [x] Dashboard shows project list — found in app/dashboard/page.tsx
  - [ ] Stripe checkout works — route exists but no test coverage
```

After updating checkboxes, commit: `git add docs/plan/*/spec.md && git commit -m "docs: update spec checkboxes (verified by review)"`

### 6. Code Quality Spot Check

Read 3-5 key files (entry points, API routes, main components):
- Check for TODO/FIXME/HACK comments that should be resolved
- Check for console.log/print statements left in production code
- Check for proper error handling (try/catch, error boundaries)
- Check for proper loading/error states in UI components

Report specific file:line references for any issues found.

### 7. Plan Completion Check

Read `docs/plan/*/plan.md`:
- Count completed tasks `[x]` vs total tasks
- Flag any `[ ]` or `[~]` tasks still remaining
- Verify all phase checkpoints have SHAs

### 8. Production Logs (if deployed)

If the project has been deployed (deploy URL in CLAUDE.md, or `.solo/states/deploy` exists if pipeline state directory is present), **check production logs for runtime errors**.

Read the `logs` field from the stack YAML (`templates/stacks/{stack}.yaml`) to get platform-specific commands.

**Vercel (Next.js):**
```bash
vercel logs --output=short 2>&1 | tail -50
```
Look for: `Error`, `FUNCTION_INVOCATION_FAILED`, `504`, unhandled rejections, hydration mismatches.

**Cloudflare Workers:**
```bash
wrangler tail --format=pretty 2>&1 | head -50
```
Look for: uncaught exceptions, D1 errors, R2 access failures.

**Fly.io (Python API):**
```bash
fly logs --app {name} 2>&1 | tail -50
```
Look for: `ERROR`, `CRITICAL`, OOM, connection refused, unhealthy instances.

**Supabase Edge Functions:**
```bash
supabase functions logs --scroll 2>&1 | tail -30
```

**iOS (TestFlight):**
- Check App Store Connect → TestFlight → Crashes
- If local device: `log stream --predicate 'subsystem == "com.{org}.{name}"'`

**Android:**
```bash
adb logcat '*:E' --format=time 2>&1 | tail -30
```
- Check Google Play Console → Android vitals → Crashes & ANRs

**If no deploy yet:** skip this dimension, note in report as "N/A — not deployed".

**If logs show errors:**
- Classify: startup crash vs runtime error vs intermittent
- Add as FIX FIRST issues in the report
- Include exact log lines as evidence

Report:
- Log source checked (platform, command used)
- Errors found: count + severity
- Error patterns (recurring vs one-off)
- Status: CLEAN / WARN / ERRORS

### 9. Dev Principles Compliance

Check adherence to dev principles. Look for `templates/principles/dev-principles.md` (bundled with this skill), or check CLAUDE.md or project docs for architecture and coding conventions.

Read the dev principles file, then spot-check 3-5 key source files for violations:

**SOLID:**
- **SRP** — any god-class/god-module doing auth + profile + email + notifications? Flag bloated files (>300 LOC with mixed responsibilities).
- **DIP** — are services injected or hardcoded? Look for `new ConcreteService()` inside business logic instead of dependency injection.

**DRY vs Rule of Three:**
- Search for duplicated logic blocks (Grep for identical function signatures across files).
- But don't flag 2-3 similar lines — duplication is OK until a pattern emerges.

**KISS:**
- Over-engineered abstractions for one-time operations?
- Feature flags or backward-compat shims where a simple change would do?
- Helpers/utilities used only once?

**Schemas-First (SGR):**
- Are Pydantic/Zod schemas defined before logic? Or is raw data passed around?
- Are API responses typed (not `any` / `dict`)?
- Validation at boundaries (user input, external APIs)?

**Clean Architecture:**
- Do dependencies point inward? Business logic should not import from UI/framework layer.
- Is business logic framework-independent?

**Error Handling:**
- Fail-fast on invalid inputs? Or silent swallowing of errors?
- User-facing errors are friendly? Internal errors have stack traces?

Report:
- Principles followed: list key ones observed
- Violations found: with file:line references
- Severity: MINOR (style) / MAJOR (architecture) / CRITICAL (data loss risk)

### 10. Commit Quality

Check git history for the current track/feature:

```bash
git log --oneline --since="1 week ago" 2>&1 | head -30
```

**Conventional commits format:**
- Each commit follows `<type>(<scope>): <description>` pattern
- Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `style`
- Flag: generic messages ("fix", "update", "wip", "changes"), missing type prefix, too-long titles (>72 chars)

**Atomicity:**
- Each commit = one logical change? Or monster commits with 20 files across unrelated features?
- Revert-friendly? Could you `git revert` a single commit without side effects?

**SHAs in plan.md:**
- Check that completed tasks have `<!-- sha:abc1234 -->` comments
- Check that phase checkpoints have `<!-- checkpoint:abc1234 -->`

```bash
grep -c "sha:" docs/plan/*/plan.md 2>/dev/null || echo "No SHAs found"
```

**Pre-commit hooks:**

Read the stack YAML `pre_commit` field to know what system is expected (husky/pre-commit/lefthook) and what it should run (linter + formatter + type-checker). Then verify:

```bash
# Detect what's configured
[ -f .husky/pre-commit ] && echo "husky" || [ -f .pre-commit-config.yaml ] && echo "pre-commit" || [ -f lefthook.yml ] && echo "lefthook" || echo "none"
```

- **Hooks installed?** Check config files exist AND hooks are wired (`core.hooksPath` for husky, `.git/hooks/pre-commit` for pre-commit/lefthook).
- **Hooks match stack?** Compare detected system with stack YAML `pre_commit` field. Flag mismatch.
- **`--no-verify` bypasses?** Check if recent commits show signs of skipped hooks (e.g., lint violations that should've been caught). Flag as WARN.
- **Not configured?** Flag as WARN recommendation — stack YAML expects `{pre_commit}` but nothing found.

Report:
- Total commits: {N}
- Conventional format: {N}/{M} compliant
- Atomic commits: YES / NO (with examples of violations)
- Plan SHAs: {N}/{M} tasks have SHAs
- Pre-commit hooks: {ACTIVE / NOT INSTALLED / NOT CONFIGURED} (expected: {stack pre_commit})

### 11. Documentation Freshness

Check that project documentation is up-to-date with the code.

**Required files check:**
```bash
ls -la CLAUDE.md README.md docs/prd.md docs/workflow.md 2>&1
```

**CLAUDE.md:**
- Does it reflect current tech stack, commands, directory structure?
- Are recently added features/endpoints documented?
- Grep for outdated references (old package names, removed files):
  ```bash
  # Check that files mentioned in CLAUDE.md actually exist
  grep -oP '`[a-zA-Z0-9_./-]+\.(ts|py|swift|kt|md)`' CLAUDE.md | while read f; do [ ! -f "$f" ] && echo "MISSING: $f"; done
  ```

**README.md:**
- Does it have setup/run/test/deploy instructions?
- Are the commands actually runnable?

**docs/prd.md:**
- Do features match what was actually built?
- Are metrics and success criteria defined?

**AICODE- comments:**
```bash
grep -rn "AICODE-TODO" src/ app/ lib/ 2>/dev/null | head -10
grep -rn "AICODE-ASK" src/ app/ lib/ 2>/dev/null | head -10
```
- Flag unresolved `AICODE-TODO` items that were completed but not cleaned up
- Flag unanswered `AICODE-ASK` questions
- Check for `AICODE-NOTE` on complex/non-obvious logic

**Dead code check:**
- Unused imports (linter should catch, but verify)
- Orphaned files not imported anywhere
- If `knip` available (Next.js): `pnpm knip 2>&1 | head -30`

Report:
- CLAUDE.md: CURRENT / STALE / MISSING
- README.md: CURRENT / STALE / MISSING
- docs/prd.md: CURRENT / STALE / MISSING
- docs/workflow.md: CURRENT / STALE / MISSING
- AICODE-TODO unresolved: {N}
- AICODE-ASK unanswered: {N}
- Dead code: {files/exports found}

### 12. Visual/E2E Testing

If browser tools or device tools are available, run a visual smoke test.

**Web projects (Playwright MCP or browser tools):**
1. Start dev server (use `dev_server.command` from stack YAML, e.g. `pnpm dev`)
2. Use Playwright MCP tools (or browser-use skill) to navigate to the main page
3. Verify it loads without console errors, hydration mismatches, or React errors
4. Navigate to 2-3 key pages (based on spec.md features)
5. Take screenshots at desktop (1280px) and mobile (375px) viewports
6. Look for broken images, missing styles, layout overflow

**iOS projects (simulator):**
1. Build for simulator: `xcodebuild -scheme {Name} -sdk iphonesimulator build`
2. Install and launch on booted simulator
3. Take screenshot of main screen
4. Check simulator logs for crashes or assertion failures

**Android projects (emulator):**
1. Build debug APK: `./gradlew assembleDebug`
2. Install and launch on emulator
3. Take screenshot of main activity
4. Check logcat for crashes or ANRs: `adb logcat '*:E' --format=time -d 2>&1 | tail -20`

**If tools are not available:** skip this dimension, note as "N/A — no browser/device tools" in the report. Visual testing is never a blocker for SHIP verdict on its own.

Report:
- Platform tested: {browser / simulator / emulator / N/A}
- Pages/screens checked: {N}
- Console errors: {N}
- Visual issues: {NONE / list}
- Responsive: {PASS / issues found}
- Status: {PASS / WARN / FAIL / N/A}

## Review Report

Generate the final report:

```
Code Review: {project-name}
Date: {YYYY-MM-DD}

## Verdict: {SHIP / FIX FIRST / BLOCK}

### Summary
{1-2 sentence overall assessment}

### Tests
- Total: {N} | Pass: {N} | Fail: {N} | Skip: {N}
- Coverage: {N}%
- Status: {PASS / FAIL}

### Linter
- Errors: {N} | Warnings: {N}
- Status: {PASS / WARN / FAIL}

### Build
- Status: {PASS / FAIL}
- Warnings: {N}

### Security
- Vulnerabilities: {N} (critical: {N}, high: {N}, moderate: {N})
- Hardcoded secrets: {NONE / FOUND}
- Status: {PASS / WARN / FAIL}

### Acceptance Criteria
- Verified: {N}/{M}
- Missing: {list}
- Status: {PASS / PARTIAL / FAIL}

### Plan Progress
- Tasks: {N}/{M} complete
- Phases: {N}/{M} complete
- Status: {COMPLETE / IN PROGRESS}

### Production Logs
- Platform: {Vercel / Cloudflare / Fly.io / N/A}
- Errors: {N} | Warnings: {N}
- Status: {CLEAN / WARN / ERRORS / N/A}

### Dev Principles
- SOLID: {PASS / violations found}
- Schemas-first: {YES / raw data found}
- Error handling: {PASS / issues found}
- Status: {PASS / WARN / FAIL}

### Commits
- Total: {N} | Conventional: {N}/{M}
- Atomic: {YES / NO}
- Plan SHAs: {N}/{M}
- Status: {PASS / WARN / FAIL}

### Documentation
- CLAUDE.md: {CURRENT / STALE / MISSING}
- README.md: {CURRENT / STALE / MISSING}
- AICODE-TODO unresolved: {N}
- Dead code: {NONE / found}
- Status: {PASS / WARN / FAIL}

### Visual Testing
- Platform: {browser / simulator / emulator / N/A}
- Pages/screens: {N}
- Console errors: {N}
- Visual issues: {NONE / list}
- Status: {PASS / WARN / FAIL / N/A}

### Issues Found
1. [{severity}] {description} — {file:line}
2. [{severity}] {description} — {file:line}

### Recommendations
- {actionable recommendation}
- {actionable recommendation}
```

**Verdict logic:**
- **SHIP**: All tests pass, no security issues, acceptance criteria met, build succeeds, production logs clean, docs current, commits atomic, no critical visual issues
- **FIX FIRST**: Minor issues (warnings, partial criteria, low-severity vulns, intermittent log errors, stale docs, non-conventional commits, minor SOLID violations, minor visual issues like layout overflow) — list what to fix
- **BLOCK**: Failing tests, security vulnerabilities, missing critical features, production crashes in logs, missing CLAUDE.md/README.md, critical architecture violations, app crashes on launch (simulator/emulator) — do not ship

## Post-Verdict: CLAUDE.md Revision

After the verdict report, revise the project's CLAUDE.md to keep it lean and useful for future agents.

### Steps:

1. **Read CLAUDE.md** and check size: `wc -c CLAUDE.md`
2. **Add learnings from this review:**
   - New Do/Don't rules discovered during review
   - Updated commands, workflows, or architecture decisions
   - Fixed issues or gotchas worth remembering
   - Stack/dependency changes (new packages, removed deps)
3. **If over 40,000 characters — trim ruthlessly:**
   - Collapse completed phase/milestone histories into one line each
   - Remove verbose explanations — keep terse, actionable notes
   - Remove duplicate info (same thing explained in multiple sections)
   - Remove historical migration notes, old debugging context
   - Remove examples that are obvious from code or covered by skill/doc files
   - Remove outdated troubleshooting for resolved issues
4. **Verify result ≤ 40,000 characters** — if still over, cut least actionable content
5. **Write updated CLAUDE.md**, update "Last updated" date

### Priority (keep → cut):
1. **ALWAYS KEEP:** Tech stack, directory structure, Do/Don't rules, common commands, architecture decisions
2. **KEEP:** Workflow instructions, troubleshooting for active issues, key file references
3. **CONDENSE:** Phase histories (one line each), detailed examples, tool/MCP listings
4. **CUT FIRST:** Historical notes, verbose explanations, duplicated content, resolved issues

### Rules:
- Never remove Do/Don't sections — critical guardrails
- Preserve overall section structure and ordering
- Every line must earn its place: "would a future agent need this to do their job?"
- Commit the update: `git add CLAUDE.md && git commit -m "docs: revise CLAUDE.md (post-review)"`

## AFTER CLAUDE.md revision — output signal EXACTLY ONCE:

Output pipeline signal ONLY if pipeline state directory (`.solo/states/`) exists.

**Output the signal tag ONCE and ONLY ONCE.** Do not repeat it. The pipeline detects the first occurrence.

**If SHIP:** output this exact line (once):
```
<solo:done/>
```

**If FIX FIRST or BLOCK:**
1. Open plan.md and APPEND a new phase with fix tasks (one `- [ ] Task` per issue found)
2. Change plan.md status from `[x] Complete` to `[~] In Progress`
3. Commit: `git add docs/plan/ && git commit -m "fix: add review fix tasks"`
4. Output this exact line (once):
```
<solo:redo/>
```

The pipeline reads these tags and handles all marker files automatically. You do NOT need to create or delete any marker files yourself.
**Output the signal tag once — the pipeline detects the first occurrence.**

## Error Handling

### Tests won't run
**Cause:** Missing dependencies or test config.
**Fix:** Run `npm install` / `uv sync`, check test config exists (jest.config, pytest.ini).

### Linter not configured
**Cause:** No linter config file found.
**Fix:** Note as a recommendation in the report, not a blocker.

### Build fails
**Cause:** Type errors, import issues, missing env vars.
**Fix:** Report specific errors. This is a BLOCK verdict — must fix before shipping.

## Two-Stage Review Pattern

When reviewing significant work, use two stages:

**Stage 1 — Spec Compliance:**
- Does the implementation match spec.md requirements?
- Are all acceptance criteria actually met (not just claimed)?
- Any deviations from the plan? If so, are they justified improvements or problems?

**Stage 2 — Code Quality:**
- Architecture patterns, error handling, type safety
- Test coverage and test quality
- Security and performance
- Code organization and maintainability

## Verification Gate

**No verdict without fresh evidence.**

Before writing any verdict (SHIP/FIX/BLOCK):
1. **Run** the actual test/build/lint commands (not cached results).
2. **Read** full output — exit codes, pass/fail counts, error messages.
3. **Confirm** the output matches your claim.
4. **Only then** write the verdict with evidence.

Never write "tests should pass" — run them and show the output.

## Rationalizations Catalog

| Thought | Reality |
|---------|---------|
| "Tests were passing earlier" | Run them NOW. Code changed since then. |
| "It's just a warning" | Warnings become bugs. Report them. |
| "The build worked locally" | Check the platform too. Environment differences matter. |
| "Security scan is overkill" | One missed secret = data breach. Always scan. |
| "Good enough to ship" | Quantify "good enough". Show the numbers. |
| "I already checked this" | Fresh evidence only. Stale checks are worthless. |

## Critical Rules

1. **Run all checks** — do not skip dimensions even if project seems simple.
2. **Be specific** — always include file:line references for issues.
3. **Verdict must be justified** — every SHIP/FIX/BLOCK needs evidence from actual commands.
4. **Don't auto-fix code** — report issues and add fix tasks to plan.md. Let `/build` fix them. Review only modifies plan.md, never source code.
5. **Check acceptance criteria** — spec.md is the source of truth for "done".
6. **Security is non-negotiable** — any hardcoded secret = BLOCK.
7. **Fresh evidence only** — run commands before making claims. Never rely on memory.
