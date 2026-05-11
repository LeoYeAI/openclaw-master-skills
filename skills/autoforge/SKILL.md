---
name: autoforge
description: 'AutoForge is a production-grade autonomous optimization framework for AI agents. It replaces subjective "reflection" with mathematically rigorous convergence loops — tracking every iteration in TSV, cross-validating with multiple models, and stopping only when pass rates confirm real improvement. Four specialized modes: prompt (skill & doc optimization via scenario simulation), code (sandboxed test execution with measurable criteria), audit (CLI verification against live tool behavior), and project (whole-repo cross-file consistency analysis). Battle-tested across 50+ iterations on production skills. Use when: user says "autoforge", "forge", "optimize skill", "improve", "run autoforge", "optimize code", "improve script", "optimize repo", "forge project", "check project", "repo audit".'
---

# AutoForge — Autonomous Optimization Framework

> Stop reflecting. Start converging. Every iteration is measured, logged, and validated — not vibed.

AutoForge replaces ad-hoc "improve this" prompts with a rigorous optimization loop: define evals, run iterations, track pass rates in TSV, report live to your channel, and stop only when math says you're done. Multi-model cross-validation prevents the "same model grades its own homework" blind spot.

**Four modes. One convergence standard.**

| Mode | What it does | Best for |
|------|-------------|----------|
| `prompt` | Simulate 5 scenarios/iter, evaluate Yes/No | SKILL.md, prompts, doc templates |
| `code` | Sandboxed test execution, measure exit/stdout/stderr | Shell scripts, Python tools, pipelines |
| `audit` | Test CLI commands live, verify SKILL.md matches reality | CLI skill documentation |
| `project` | Scan whole repo, cross-file consistency analysis | README↔CLI drift, Dockerfile↔deps, CI gaps |

---

# AutoForge — Top-Agent Architecture

## Overview

```
Agent (you)
├── State: results.tsv, current target file state, iteration counter
├── Iteration 1: evaluate → improve → write TSV → report
├── Iteration 2: evaluate → improve → write TSV → report
├── ...
└── Finish: report.sh --final → configured channel
```

### Sub-Agent = You
"Sub-Agent" is a **conceptual role**, not a separate process. You (the top-agent) execute each iteration yourself: simulate/execute → evaluate → write TSV → call report.sh. The templates below describe what you do PER ITERATION — not what you send to another agent.

For code mode, run tests using the `exec` tool.

### Multi-Model Setup (recommended for Deep Audits)

For complex audits, you can **split two roles across different models**:

| Role | Model | Task |
|------|-------|------|
| **Optimizer** | Opus / GPT-4.1 | Analyzes, finds issues, writes fixes |
| **Validator** | GPT-5 / Gemini (different model) | Checks against ground truth, provides pass rate |

**Flow:** Optimizer and Validator alternate. Optimizer iterations have status `improved`/`retained`/`discard`. Validator iterations confirm or refute the pass rate. Spawn validators as sub-agents with `sessions_spawn` and explicit `model`.

**When to use Multi-Model:** Deep Audits (>5 iterations expected), complex ground truth, or when a single model is blind to its own errors.

**When Single-Model suffices:** Simple CLI audits, prompt optimization, code with clear tests.

---

## Configuration

AutoForge uses environment variables for reporting. All are optional — without them, output goes to stdout.

| Variable | Default | Description |
|----------|---------|-------------|
| `AF_CHANNEL` | `telegram` | Messaging channel for reports |
| `AF_CHAT_ID` | _(none)_ | Chat/group ID for report delivery |
| `AF_TOPIC_ID` | _(none)_ | Thread/topic ID within the chat |

---

## Hard Invariants

These rules apply **always**, regardless of mode:

1. **TSV is mandatory.** Every iteration writes exactly one row to `results/[target]-results.tsv`.
2. **Reporting is mandatory.** Call `report.sh` immediately after every TSV row.
3. **--dry-run never overwrites the target.** Only TSV, `*-proposed.md`, and reports are written.
4. **Mode isolation is strict.** Only execute steps for the assigned mode.
5. **Iteration 1 = Baseline.** Evaluate the original version unchanged, status `baseline`.

---

## Modes — Read ONLY Your Mode!

You are assigned ONE mode. **Ignore all sections for other modes.**

| Mode | What happens | Output |
|------|-------------|--------|
| `prompt` | Mentally simulate skill/prompt, evaluate against evals | Improved prompt text |
| `code` | Run tests in sandbox, measure results | Improved code |
| `audit` | Test CLI commands (read-only only!) + verify SKILL.md against reality | Improved SKILL.md |
| `project` | Scan whole repo, cross-file analysis, fix multiple files per iteration | Improved repository |

**Your mode is in the task prompt.** Everything else is irrelevant to you.

---

## TSV Format (same for ALL modes)

### Header (once at loop start):
```bash
printf '%s\t%s\t%s\t%s\t%s\n' "iteration" "prompt_version_summary" "pass_rate" "change_description" "status" > results/[target]-results.tsv
```

### Row per iteration:
```bash
printf '%s\t%s\t%s\t%s\t%s\n' "1" "Baseline" "58%" "Original version" "baseline" >> results/[target]-results.tsv
```
> **Use `printf` not `echo -e`!** `echo -e` interprets backslashes in field values. `printf '%s'` outputs strings literally.

### 5 columns, TAB-separated, EXACTLY this order:

| # | Column | Type | Rules |
|---|--------|------|-------|
| 1 | `iteration` | Integer | 1, 2, 3, ... |
| 2 | `prompt_version_summary` | String | Max 50 Unicode chars. No tabs, no newlines. |
| 3 | `pass_rate` | String | Number + `%`: `58%`, `92%`, `100%`. Always integer. |
| 4 | `change_description` | String | Max 100 Unicode chars. No tabs, no newlines. |
| 5 | `status` | Enum | Exactly one of: `baseline` · `improved` · `retained` · `discard` |

### Escaping rules:
- **Tabs** in text fields → replace with spaces
- **Newlines** in text fields → replace with ` | `
- **Empty fields** → use hyphen `-` (never leave empty)
- **`$` and backticks** → use `printf '%s'` or escape with `\$` (prevents unintended variable interpolation)
- **Unicode/Emoji** allowed, count as 1 character (not bytes)

### Status rules (based on pass-rate comparison):
- `baseline` — **Mandatory for Iteration 1.** Evaluate original version only.
- `improved` — Pass rate **higher** than previous best → new version becomes current state
- `retained` — Pass rate **equal or marginally better** → predecessor remains
- `discard` — Pass rate **lower** → change discarded, revert to best state

---

## Reporting (same for ALL modes)

**After EVERY TSV row** (including baseline):
```bash
bash scripts/report.sh results/[target]-results.tsv "[Skill Name]"
```

**After loop ends**, additionally with `--final`:
```bash
bash scripts/report.sh results/[target]-results.tsv "[Skill Name]" --final
```

The report script reads `AF_CHANNEL`, `AF_CHAT_ID`, and `AF_TOPIC_ID` from environment. Without them, it prints to stdout with ANSI colors.

---

## Stop Conditions (for ALL modes)

Priority — first matching condition wins, top to bottom:

1. 🛑 **Minimum iterations** — If specified in task (e.g. "min 5"), this count MUST be reached. No other condition can stop before.
2. 🛑 **Max 30 iterations** — Hard safety net, stop immediately.
3. ❌ **3× `discard` in a row** → structural problem, stop + analyze.
4. ✅ **3× 100% pass rate** (after minimum) → confirmed perfect, done.
5. ➡️ **5× `retained` in a row** → converged, done.

### Counting rules:
- `3× 100%` = three iterations with `pass_rate == 100%`, not necessarily consecutive.
- `5× retained` and `3× discard` = **consecutive** (in a row).
- `baseline` counts toward no series.
- `improved` interrupts `retained` and `discard` series.

**At 100% in early iterations:** Keep going! Test harder edge cases. Only 3× 100% *after the minimum* confirms true perfection.

### Recognizing Validator Noise

In multi-model setups, the Validator can produce **false positives** — fails that aren't real issues:

- **Config path vs tool name confusion** (e.g. `agents.list[]` ≠ `agents_list` tool)
- **Inverted checks** ("no X" → Validator looks for X as required)
- **Normal English as forbidden reference** (e.g. "runtime outcome" ≠ `runtime: "acp"`)
- **Overcounting** (thread commands counted as subagent commands)

**Rule:** If after all real fixes >3 discards come in a row and the fail justifications don't hold up under scrutiny → **declare convergence**, don't validate endlessly.

---

## Execution Modes

| Flag | Behavior |
|------|----------|
| `--dry-run` (default) | Only TSV + proposed files. Target file/repo remains unchanged. |
| `--live` | Target file/repo is overwritten. Auto-backup → `results/backups/` |
| `--resume` | Read existing TSV, continue from last iteration. On invalid format: abort. |

---

## mode: prompt

> **Only read if your task contains `mode: prompt`!**

### Per Iteration: What you do
1. Read current prompt/skill
2. **Mentally simulate 5 different realistic scenarios**
3. Evaluate each scenario against **all evals** (Yes=1, No=0)
4. Pass rate = (Sum Yes) / (Eval count × 5 scenarios) × 100
5. Compare with best previous pass rate → determine status
6. On `improved`: propose **minimal, surgical** improvement
7. Write TSV row + call report.sh
8. Check stop conditions

### At the End
Best version → `results/[target]-proposed.md` + report.sh `--final`

---

## mode: code

> **Only read if your task contains `mode: code`!**

### Per Iteration: What you do
1. Create sandbox: `SCRATCH=$(mktemp -d) && cd $SCRATCH`
2. Write current code to sandbox
3. Execute test command (with `timeout 60s`)
4. Measure: exit_code, stdout, stderr, runtime
5. Evaluate against evals → calculate pass rate
6. On `improved`: minimal code improvement + verify again
7. Write TSV row + call report.sh
8. Check stop conditions

### Code Eval Types

| Eval Type | Description | Example |
|-----------|-------------|---------|
| `exit_code` | Process exit code | `exit_code == 0` |
| `output_contains` | stdout contains string | `"SUCCESS" in stdout` |
| `output_matches` | stdout matches regex | `r"Total: \d+"` |
| `test_pass` | Test framework green | `pytest exit 0` |
| `runtime` | Runtime limit | `< 5000ms` |
| `no_stderr` | No error output | `stderr == ""` |
| `file_exists` | Output file created | `result.json exists` |
| `json_valid` | Output is valid JSON | `json.loads(stdout)` |

### At the End
Best code → `results/[target]-proposed.[ext]` + report.sh `--final`

---

## mode: audit

> **Only read if your task contains `mode: audit`!**

⚠️ **DO NOT write your own code.** Only test CLI commands of the target tool (`--help` + read-only).

### Two Variants

**Simple Audit (CLI skill, clear commands):**
- 2 iterations: Baseline → Proposed Fix
- For tools with clear `--help` output and simple command structure

**Deep Audit (complex docs, many checks):**
- Iterative loop like prompt/code, same stop conditions
- For extensive documentation with many checkpoints (e.g. config keys, tool policy, parameter lists)
- Recommended: Multi-Model setup (Opus Optimizer + external Validator)

### Simple Audit Flow
1. Write TSV header
2. **Iteration 1 (Baseline):** Test every documented command → pass rate → TSV + report
3. **Iteration 2 (Proposed Fix):** Write improved SKILL.md → expected pass rate → TSV + report
4. Improved SKILL.md → `results/[target]-proposed.md`
5. Detail results → `results/[target]-audit-details.md` (NOT in TSV!)
6. report.sh `--final`

### Deep Audit Flow
1. Write TSV header
2. **Iteration 1 (Baseline):** Extract ground truth from source, define all checks, evaluate baseline
3. **Iterations 2+:** Optimizer fixes issues → Validator checks → TSV + report per iteration
4. Loop runs until stop conditions trigger (3× 100%, 5× retained, 3× discard)
5. Final version → `results/[target]-proposed.md` or `results/[target]-v1.md`
6. report.sh `--final`

### Fixed Evals (audit)
1. Completeness — Does SKILL.md cover ≥80% of real commands/config?
2. Correctness — Are ≥90% of documented commands/params syntactically correct?
3. No stale references — Does everything documented actually exist?
4. No missing core features — Are all important features covered?
5. Workflow quality — Does quick-start actually work?

---

## mode: project

> **Only read if your task contains `mode: project`!**

⚠️ **This mode operates on an ENTIRE repository/directory**, not a single file. Cross-file consistency is the core feature — this is NOT "audit on many files."

### Three Phases

Project mode runs through three sequential phases. Phases 1 and 2 happen once (in Iteration 1 = Baseline). Phase 3 is the iterative fix loop.

---

### Phase 1: Scan & Plan

1. **Analyze the repo directory:**
   ```bash
   # Discover structure
   tree -L 3 --dirsfirst [target_dir]
   ls -la [target_dir]
   ```
2. **Identify relevant files** and classify by priority:

   | Priority | Files |
   |----------|-------|
   | **critical** | README, Dockerfile, CI workflows (.github/workflows), package.json/requirements.txt, main entry points |
   | **normal** | Tests, configs, scripts, .env.example, .gitignore |
   | **low** | Docs, examples, LICENSE, CHANGELOG |

3. **Build the File-Map** — a mental inventory of what exists and what's missing.
4. **Compose eval set:** Merge user-provided evals with auto-detected evals (see Default Evals below).

---

### Phase 2: Cross-File Analysis

Run consistency checks **across** files. Each check = one eval point:

| Check | What it verifies |
|-------|-----------------|
| **README ↔ CLI** | Documented commands/flags match actual `--help` output |
| **Dockerfile ↔ deps** | `requirements.txt` / `package.json` versions match what Dockerfile installs |
| **CI ↔ project structure** | Workflow references correct paths, scripts, test commands |
| **`.env.example` ↔ code** | Every env var in code has a corresponding entry in `.env.example` |
| **Imports ↔ dependencies** | Every `import` / `require` has a matching dependency declaration |
| **Tests ↔ source** | Test files exist for critical modules |
| **`.gitignore` ↔ artifacts** | Build outputs, secrets, and caches are excluded |

**Result of Phase 2:** A complete eval checklist with per-file and cross-file checks, each scored Yes/No.

---

### Phase 3: Iterative Fix Loop

Same loop logic as prompt/code/audit — TSV, report.sh, stop conditions. Key differences:

- **Multiple files** can be changed per iteration
- **Pass rate** = aggregated over ALL evals (file-specific + cross-file)
- **Fixes are minimal and surgical** — don't refactor blindly, only fix what improves pass rate
- **`change_description`** includes which files were touched: `"Fix Dockerfile + CI workflow sync"`

### Per Iteration: What you do
1. Evaluate current repo state against **all evals** (file-specific + cross-file)
2. Calculate pass rate: (passing evals / total evals) × 100
3. Compare with best previous pass rate → determine status
4. On `improved`: apply **minimal, surgical fixes** to the fewest files necessary
5. Verify the fix didn't break other evals (re-run affected checks)
6. Write TSV row + call report.sh
7. Check stop conditions

### Dry-Run vs Live

| Flag | Behavior |
|------|----------|
| `--dry-run` (default) | Fixed files → `results/[target]-proposed/` directory (mirrors repo structure). Original repo untouched. |
| `--live` | Files overwritten in-place. Originals backed up → `results/backups/` (preserving directory structure). |

### Default Evals (auto-applied unless overridden)

These evals are **automatically used** when the user doesn't provide custom evals. The agent detects which are applicable based on what exists in the repo:

| # | Eval | Condition |
|---|------|-----------|
| 1 | README accurate? (describes actual features/commands) | README exists |
| 2 | Tests present and green? (`pytest` / `npm test` / `go test`) | Test files or test config detected |
| 3 | CI configured and syntactically correct? | `.github/workflows/` or `.gitlab-ci.yml` exists |
| 4 | No hardcoded secrets? (`grep -rE "(password|api_key|token|secret)\s*="`) | Always |
| 5 | Dependencies complete? (`requirements.txt` ↔ imports, `package.json` ↔ requires) | Dependency file exists |
| 6 | Dockerfile functional? (`docker build` succeeds or Dockerfile syntax valid) | Dockerfile exists |
| 7 | `.gitignore` sensible? (no secrets, build artifacts excluded) | `.gitignore` exists |
| 8 | License present? | Always |

### Eval Scoring

```
Pass Rate = (Passing Evals / Total Applicable Evals) × 100
```

Evals that don't apply (e.g. "Dockerfile functional?" when no Dockerfile exists) are **excluded from the total**, not counted as passes.

### At the End
- `--dry-run`: All proposed changes → `results/[target]-proposed/` directory
- `--live`: Changes already applied, backups in `results/backups/`
- report.sh `--final`
- Optionally: `results/[target]-project-details.md` with per-file findings (NOT in TSV!)

---

## Directory Structure

```
autoforge/
├── SKILL.md                    ← This file
├── results/
│   ├── [target]-results.tsv    ← TSV logs
│   ├── [target]-proposed.md    ← Proposed improvement (prompt/audit)
│   ├── [target]-proposed/      ← Proposed repo changes (project mode)
│   │   ├── README.md
│   │   ├── Dockerfile
│   │   └── ...
│   ├── [target]-v1.md          ← Deep audit final version
│   ├── [target]-audit-details.md ← Audit details (audit mode only)
│   ├── [target]-project-details.md ← Project details (project mode only)
│   └── backups/                ← Auto-backups (--live)
│       ├── [file].bak          ← Single file backups (prompt/code/audit)
│       └── [target]-backup/    ← Full directory backup (project mode)
├── scripts/
│   ├── report.sh               ← Channel reporting
│   └── visualize.py            ← PNG chart (optional)
├── references/
│   ├── eval-examples.md        ← Pre-built evals
│   └── ml-mode.md              ← ML training guide
└── examples/
    ├── demo-results.tsv        ← Demo data
    └── example-config.json     ← Example configuration
```

---

## Examples (task descriptions, NOT CLI commands)

AutoForge is not a CLI tool — it's a **skill prompt** for the agent:

```
# Optimize a prompt
"Start autoforge mode: prompt for the coding-agent skill.
 Evals: PTY correct? Workspace protected? Clearly structured?"

# Audit a CLI skill (simple)
"Start autoforge mode: audit for notebooklm-py."

# Deep audit with multi-model
"Start autoforge mode: audit (deep) for subagents docs.
 Optimizer: Opus, Validator: GPT-5
 Extract ground truth from source, validate iteratively."

# Optimize code
"Start autoforge mode: code for backup.sh.
 File: ./backup.sh
 Test: bash backup.sh personal --dry-run
 Evals: exit_code==0, backup file created, < 10s runtime"

# Optimize a whole repository
"Start autoforge mode: project for ./my-app
 Evals: Tests green? CI correct? No hardcoded secrets? README accurate?"

# Project mode with custom focus
"Start autoforge mode: project for /path/to/api-server
 Focus: Docker + CI pipeline consistency
 Evals: docker build succeeds, CI workflow references correct paths,
        .env.example covers all env vars used in code"

# Project mode dry-run (default)
"Start autoforge mode: project for ./my-tool --dry-run
 Use default evals. Show me what needs fixing."
```

---

## Eval Examples → Mode Mapping

`references/eval-examples.md` provides ready-to-use Yes/No evals grouped by category. Here's how they map to AutoForge modes:

| eval-examples.md Category | AutoForge Mode | Notes |
|---------------------------|---------------|-------|
| Briefing, Email, Calendar, Summary, Proposal | `prompt` | Mental simulation with scenario evals |
| Python Script, Shell Script, API, Data Pipeline, Build | `code` | Real execution with measurable criteria |
| CI/CD, Docker, Helm, Kubernetes, Terraform | `code` or `project` | `code` for single files, `project` for cross-file |
| Code Review, API Documentation | `audit` | Verify docs match reality |
| Project / Repository, Cross-File Consistency, Security Baseline | `project` | Whole-repo scanning and cross-file checks |

Pick evals from the matching category and paste them into your task prompt as the eval set.

---

## Tips
- Always start with `--dry-run`
- `prompt` = think, `code` = execute, `audit` = test CLI, `project` = optimize repo
- Simple Audit for clear CLI skills, Deep Audit for complex docs
- Project mode scans the whole repo — cross-file consistency is the killer feature
- Multi-Model for Deep Audits: different models cover different blind spots
- At >3 discards after all fixes: check for validator noise, declare convergence if justified
- TSV + report.sh are NOT optional — they are the user interface
- For ML training: see `references/ml-mode.md`
