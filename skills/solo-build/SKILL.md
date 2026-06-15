---
name: solo-build
description: Execute implementation plan tasks with TDD workflow, auto-commit, and phase gates. Use when user says "build it", "start building", "execute plan", "implement tasks", "ship it", or references a track ID. Do NOT use for planning (use /plan) or scaffolding (use /scaffold).
license: MIT
metadata:
  author: fortunto2
  version: "2.2.1"
  openclaw:
    emoji: "🔨"
allowed-tools: Read, Grep, Bash, Glob, Write, Edit, AskUserQuestion, mcp__solograph__session_search, mcp__solograph__project_code_search, mcp__solograph__codegraph_query, mcp__solograph__web_search, mcp__context7__resolve-library-id, mcp__context7__query-docs
argument-hint: "[track-id] [--task X.Y] [--phase N]"
---

# /build

This skill is self-contained — follow the task loop, TDD rules, and completion flow below instead of delegating to external build/execution skills (superpowers, etc.).

Execute tasks from an implementation plan. Finds `plan.md` (in `docs/plan/`), picks the next unchecked task, implements it with TDD workflow, commits, and updates progress.

## When to use

After `/plan` has created a track with `spec.md` + `plan.md`. This is the execution engine.

Pipeline: `/plan` → **`/build`** → `/deploy` → `/review`

## MCP Tools (use if available)

- `session_search(query)` — find how similar problems were solved before
- `project_code_search(query, project)` — find reusable code across projects
- `codegraph_query(query)` — check file dependencies, imports, callers

If MCP tools are not available, fall back to Glob + Grep + Read.

## Pre-flight Checks

1. **Detect context** — find where plan files live:
   - Check `docs/plan/*/plan.md` — standard location
   - Use whichever exists.
   - **DO NOT** search for `conductor/` or any other directory — only `docs/plan/`.

2. Load workflow config from `docs/workflow.md` (if exists):
   - TDD strictness (strict / moderate / none)
   - Commit strategy (conventional commits format)
   - Verification checkpoint rules
   - **Integration Testing section** — if present, run the specified CLI commands after completing tasks that touch the listed paths
   If `docs/workflow.md` missing: use defaults (moderate TDD, conventional commits).

3. **Verify git hooks are installed:**

   Read the stack YAML (`templates/stacks/{stack}.yaml`) — the `pre_commit` field tells you which system and what it runs:
   - `husky + lint-staged` → JS/TS stacks (eslint + prettier + tsc)
   - `pre-commit` → Python stacks (ruff + ruff-format + ty)
   - `lefthook` → mobile stacks (swiftlint/detekt + formatter)

   Then verify the hook system is active:
   ```bash
   # husky
   [ -f .husky/pre-commit ] && git config core.hooksPath | grep -q husky && echo "OK" || echo "NOT ACTIVE"
   # pre-commit (Python)
   [ -f .pre-commit-config.yaml ] && [ -f .git/hooks/pre-commit ] && echo "OK" || echo "NOT ACTIVE"
   # lefthook
   [ -f lefthook.yml ] && lefthook version >/dev/null 2>&1 && echo "OK" || echo "NOT ACTIVE"
   ```

   **If not active — install before first commit:**
   - husky: `pnpm prepare` (or `npm run prepare`)
   - pre-commit: `uv run pre-commit install`
   - lefthook: `lefthook install`

   Don't use `--no-verify` on commits — if hooks fail, fix the issue and commit again.

## Track Selection

### If `$ARGUMENTS` contains a track ID:
- Validate: `{plan_root}/{argument}/plan.md` exists (check `docs/plan/`).
- If not found: search `docs/plan/*/plan.md` for partial matches, suggest corrections.

### If `$ARGUMENTS` contains `--task X.Y`:
- Jump directly to that task in the active track.

### If no argument:
1. Search for `plan.md` files in `docs/plan/`.
2. Read each `plan.md`, find tracks with uncompleted tasks.
3. If multiple, ask via AskUserQuestion.
4. If zero tracks: "No plans found. Run `/plan` first."

## Context Loading

### Step 1 — Architecture overview (if MCP available)
```
codegraph_explain(project="{project name}")
```
Returns: stack, languages, directory layers, key patterns, top dependencies, hub files — one call instead of exploring the tree manually.

### Step 2 — Essential docs (parallel reads)
1. `docs/plan/{trackId}/plan.md` — task list (REQUIRED)
2. `docs/plan/{trackId}/spec.md` — acceptance criteria (REQUIRED)
3. `docs/workflow.md` — TDD policy, commit strategy (if exists)
4. `CLAUDE.md` — architecture, Do/Don't
5. `.solo/pipelines/progress.md` — running docs from previous iterations (if exists, pipeline-specific). Contains what was done in prior pipeline sessions: stages completed, commit SHAs, last output lines. **Use this to avoid repeating completed work.**

**Do NOT read source code files at this stage.** Only docs. Source files are loaded per-task in the execution loop (step 3 below).

## Resumption

If a task is marked `[~]` in plan.md:

```
Resuming: {track title}
Last task: Task {X.Y}: {description} [in progress]

1. Continue from where we left off
2. Restart current task
3. Show progress summary first
```

Ask via AskUserQuestion, then proceed.

## Task Execution Loop

**Makefile convention:** If `Makefile` exists in project root, **always prefer `make` targets** over raw commands. Use `make test` instead of `pnpm test`, `make lint` instead of `pnpm lint`, `make build` instead of `pnpm build`, etc. Run `make help` (or read Makefile) to discover available targets. If a `make integration` or similar target exists, use it for integration testing after pipeline-related tasks.

**IMPORTANT — All-done check:** Before entering the loop, scan plan.md for ANY `- [ ]` or `- [~]` tasks. If ALL tasks are `[x]` — skip the loop entirely and jump to **Completion** section below to run final verification and output `<solo:done/>`.

For each incomplete task in plan.md (marked `[ ]`), in order:

### 1. Find Next Task

Parse plan.md for first line matching `- [ ] Task X.Y:` (or `- [~] Task X.Y:` if resuming).

### 2. Start Task

- Update plan.md: `[ ]` → `[~]` for current task.
- Announce: **"Starting Task X.Y: {description}"**

### 3. Research (smart, before coding)

**Do NOT grep the entire project or read all source files.** Load only what this specific task needs.

**If MCP available (preferred):**
1. `project_code_search(query="{task keywords}", project="{name}")` — find relevant code in the project. Read only the top 2-3 results.
2. `session_search("{task keywords}")` — check if you solved this before.
3. `codegraph_query("MATCH (f:File {project: '{name}'})-[:IMPORTS]->(dep) WHERE f.path CONTAINS '{module}' RETURN dep.path")` — check imports/dependencies of files you'll modify.

**If MCP unavailable (fallback):**
1. Read ONLY the files explicitly mentioned in the task description (file paths).
2. Glob for the specific module directory the task targets (e.g., `src/auth/**/*.ts`), not the entire project.
3. If the task doesn't mention files, use Grep with a narrow pattern on `src/` or `app/` — never `**/*`.

**Never do:** `Grep "keyword" .` across the whole project. This dumps hundreds of lines into context for no reason. Be surgical.

### Python-Specific Quality Tools

When the project uses a Python stack (detected by `pyproject.toml` or stack YAML), run the full Astral toolchain:

1. **Ruff** — linting + formatting (always):
   ```bash
   uv run ruff check --fix .
   uv run ruff format .
   ```

2. **ty** — type-checking (if `ty` in dev dependencies or stack YAML):
   ```bash
   uv run ty check .
   ```
   ty is Astral's type-checker (extremely fast, replaces mypy/pyright). Fix type errors before committing.

3. **Hypothesis** — property-based testing (if `hypothesis` in dependencies):
   - Use `@given(st.from_type(MyModel))` to auto-generate Pydantic model inputs.
   - Use `@given(st.text(), st.integers())` for edge-case coverage on parsers/validators.
   - Hypothesis tests go in the same test files alongside regular pytest tests.

4. **Pre-commit** — run all hooks before committing:
   ```bash
   uv run pre-commit run --all-files
   ```

Run these checks after each task implementation, before `git commit`. If any fail, fix before proceeding.

### JS/TS-Specific Quality Tools

When the project uses a JS/TS stack (detected by `package.json` or stack YAML):

1. **ESLint** — linting (always):
   ```bash
   pnpm lint --fix
   ```

2. **Prettier** — formatting (always):
   ```bash
   pnpm format
   ```

3. **tsc --noEmit** — type-checking (strict mode):
   ```bash
   pnpm tsc --noEmit
   ```
   Fix type errors before committing. Strict mode should be on in tsconfig.json.

4. **Knip** — dead code detection (if in devDependencies, run periodically):
   ```bash
   pnpm knip
   ```
   Finds unused files, exports, and dependencies. Run after significant refactors.

5. **Pre-commit** — husky + lint-staged runs ESLint + Prettier + tsc on staged files.

### iOS/Android-Specific Quality Tools

When the project uses a mobile stack:

**iOS (Swift):**
```bash
swiftlint lint --strict
swift-format format --in-place --recursive Sources/
```

**Android (Kotlin):**
```bash
./gradlew detekt
./gradlew ktlintCheck
```

Both use **lefthook** for pre-commit hooks (language-agnostic, no Node.js required).

### 4. TDD Workflow (if TDD enabled in workflow.md)

**Red — write failing test:**
- Create/update test file for the task functionality.
- Run tests to confirm they fail.

**Green — implement:**
- Write minimum code to make the test pass.
- Run tests to confirm pass.

**Refactor:**
- Clean up while tests stay green.
- Run tests one final time.

### 5. Non-TDD Workflow (if TDD is "none" or "moderate" and task is simple)

- Implement the task directly.
- Run existing tests to check nothing broke.
- For "moderate": write tests for business logic and API routes, skip for UI/config.

### 5.5. Integration Testing (CLI-First)

If the task touches core business logic (pipeline, algorithms, agent tools), run `make integration` (or the integration command from `docs/workflow.md`). The CLI exercises the same code paths as the UI without requiring a browser. If `make integration` fails, fix before committing.

### 5.6. Visual Verification (if browser/simulator/emulator available)

After implementation, run a quick visual smoke test if tools are available:

**Web projects (Playwright MCP or browser tools):**
If you have Playwright MCP tools or browser tools available:
1. Start the dev server if not already running (check stack YAML for `dev_server.command`)
2. Navigate to the page affected by the current task
3. Check the browser console for errors (hydration mismatches, uncaught exceptions, 404s)
4. Take a screenshot to verify the visual output matches expectations
5. If the task affects responsive layout, resize to mobile viewport (375px) and check

**iOS projects (simulator):**
If instructed to use iOS Simulator in the pipeline prompt:
1. Build for simulator: `xcodebuild -scheme {Name} -sdk iphonesimulator build`
2. Install on booted simulator: `xcrun simctl install booted {app-path}`
3. Launch and take screenshot: `xcrun simctl io booted screenshot /tmp/sim-screenshot.png`
4. Check simulator logs: `xcrun simctl spawn booted log stream --style compact --timeout 10`

**Android projects (emulator):**
If instructed to use Android Emulator in the pipeline prompt:
1. Build debug APK: `./gradlew assembleDebug`
2. Install: `adb install -r app/build/outputs/apk/debug/app-debug.apk`
3. Take screenshot: `adb exec-out screencap -p > /tmp/emu-screenshot.png`
4. Check logcat: `adb logcat '*:E' --format=time -d 2>&1 | tail -20`

**Graceful degradation:** If browser/simulator/emulator tools are not available or fail — skip visual checks entirely. Visual testing is a bonus, never a blocker. Log that it was skipped and continue with the task.

### 6. Complete Task

**Commit** (following commit strategy):
```bash
git add {specific files changed}
git commit -m "<type>(<scope>): <description>"
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `style`

**Capture SHA** after commit:
```bash
git rev-parse --short HEAD
```

**SHA annotation in plan.md.** After every task commit:
1. Mark task done: `[~]` → `[x]`
2. Append commit SHA inline: `- [x] Task X.Y: description <!-- sha:abc1234 -->`

Without a SHA, there's no traceability and no revert capability. If a task required multiple commits, record the last one.

### 7. Phase Completion Check

After each task, check if all tasks in current phase are `[x]`.

If phase complete:

1. **SHA audit** — scan all `[x]` tasks in this phase. If any are missing `<!-- sha:... -->`, capture their SHA now from git log and add it. Every `[x]` task MUST have a SHA.
2. Run verification steps listed under `### Verification` for the phase.
3. Run full test suite.
4. Run linter.
5. Mark verification checkboxes in plan.md: `- [ ]` → `- [x]`.
6. Commit plan.md progress: `git commit -m "chore(plan): complete phase {N}"`.
7. Capture checkpoint SHA and append to phase heading in plan.md:
   `## Phase N: Title <!-- checkpoint:abc1234 -->`.
8. Report results and continue:

```
Phase {N} complete! <!-- checkpoint:abc1234 -->

  Tasks:  {M}/{M}
  Tests:  {pass/fail}
  Linter: {pass/fail}
  Verification:
    - [x] {check 1}
    - [x] {check 2}

  Revert this phase: git revert abc1234..HEAD
```

Proceed to the next phase automatically. No approval needed.

## Error Handling

### Test Failure
```
Tests failing after Task X.Y:
  {failure details}

1. Attempt to fix
2. Rollback task changes (git checkout)
3. Pause for manual intervention
```
Ask via AskUserQuestion. Do NOT automatically continue past failures.

## Track Completion

When all phases and tasks are `[x]`:

### 1. Final Verification
- **Run local build** — must pass before deploy:
  - Next.js: `pnpm build`
  - Python: `uv build` or `uv run python -m py_compile src/**/*.py`
  - Astro: `pnpm build`
  - Cloudflare: `pnpm build`
  - iOS: `xcodebuild -scheme {Name} -sdk iphonesimulator build`
  - Android: `./gradlew assembleDebug`
- Run full test suite.
- Run linter + type-checker.
- **Visual smoke test** (if tools available):
  - Web: start dev server, navigate to main page, check console for errors, take screenshot
  - iOS: build + install on simulator, launch, take screenshot, check logs
  - Android: build APK + install on emulator, launch, take screenshot, check logcat
  - Skip if tools unavailable — not a blocker for completion
- Check acceptance criteria from spec.md.

### 2. Update plan.md header

Change `**Status:** [ ] Not Started` → `**Status:** [x] Complete` at the top of plan.md.

### 3. Signal completion

Output pipeline signal ONLY if pipeline state directory (`.solo/states/`) exists:
```
<solo:done/>
```
**Do NOT repeat the signal tag elsewhere in the response.** One occurrence only.

### 4. Summary

```
Track complete: {title} ({trackId})

  Phases: {N}/{N}
  Tasks:  {M}/{M}
  Tests:  All passing

  Phase checkpoints:
    Phase 1: abc1234
    Phase 2: def5678
    Phase 3: ghi9012

  Revert entire track: git revert abc1234..HEAD

Next:
  /build {next-track-id}  — continue with next track
  /plan "next feature"    — plan something new
```

## Reverting Work

SHA comments in plan.md enable surgical reverts:

**Revert a single task:**
```bash
# Find SHA from plan.md: - [x] Task 2.3: ... <!-- sha:abc1234 -->
git revert abc1234
```
Then update plan.md: `[x]` → `[ ]` for that task.

**Revert an entire phase:**
```bash
# Find checkpoint from phase heading: ## Phase 2: ... <!-- checkpoint:def5678 -->
# Find previous checkpoint: ## Phase 1: ... <!-- checkpoint:abc1234 -->
git revert abc1234..def5678
```
Then update plan.md: all tasks in that phase `[x]` → `[ ]`.

**Never use `git reset --hard`** — always `git revert` to preserve history.

## Progress Tracking (TodoWrite)

At the start of a build session, create a task list from plan.md so progress is visible:

1. **On session start:** Read plan.md, find all incomplete tasks (`[ ]` and `[~]`).
2. **Create TaskCreate** for each phase with its tasks as description.
3. **TaskUpdate** as you work: `in_progress` when starting a task, `completed` when done.
4. This gives the user (and pipeline) real-time visibility into progress.

## Rationalizations Catalog

These thoughts mean STOP — you're about to cut corners:

| Thought | Reality |
|---------|---------|
| "This is too simple to test" | Simple code breaks too. Write the test. |
| "I'll add tests later" | Tests written after pass immediately — they prove nothing. |
| "I already tested it manually" | Manual tests don't persist. Automated tests do. |
| "The test framework isn't set up" | Set it up. That's part of the task. |
| "This is just a config change" | Config changes break builds. Verify. |
| "I'm confident this works" | Confidence without evidence is guessing. Run the command. |
| "Let me just try changing X" | Stop. Investigate root cause first. |
| "Tests are passing, ship it" | Tests passing ≠ acceptance criteria met. Check spec.md. |
| "I'll fix the lint later" | Fix it now. Tech debt compounds. |
| "It works on my machine" | Run the build. Verify in the actual environment. |

## Critical Rules

1. **Run phase checkpoints** — verify tests + linter pass before moving to next phase.
2. **STOP on failure** — do not continue past test failures or errors.
3. **Keep plan.md updated** — task status must reflect actual progress at all times.
4. **Commit after each task** — atomic commits with conventional format.
5. **Research before coding** — 30 seconds of search saves 30 minutes of reimplementation.
6. **One task at a time** — finish current task before starting next.
7. **Keep test output concise** — when running tests, pipe through `head -50` or use `--reporter=dot` / `-q` flag. Thousands of test lines pollute context. Only show failures in detail.
8. **Verify before claiming done** — run the actual command, read the full output, confirm success BEFORE marking a task complete. Never say "should work now".

## Common Issues

### "No plans found"
**Cause:** No `plan.md` exists in `docs/plan/`.
**Fix:** Run `/plan "your feature"` first to create a track.

### Tests failing after task
**Cause:** Implementation broke existing functionality.
**Fix:** Use the error handling flow — attempt fix, rollback if needed, pause for user input. Never skip failing tests.

### Phase checkpoint failed
**Cause:** Tests or linter failed at phase boundary.
**Fix:** Fix failures before proceeding. Re-run verification for that phase.
