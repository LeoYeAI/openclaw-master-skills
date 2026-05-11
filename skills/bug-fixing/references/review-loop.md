# Fix → Regression Verify → Summary → Code Review Loop (MANDATORY)

Goal: Never stop at "works on my machine". Iterate continuously until `code-review` finds no real bugs.

## Loop Contract (MUST follow this order)

1) Fix
- Apply the minimal change that addresses the root cause.
- **Strictly limit modifications to within the Change Blueprint** (from `pre-fix-impact-prediction.md`).
- If additional changes are discovered during the fix → **STOP**, update the Blueprint, re-assess impact.

1.5) Web/PC Bug Extra Gate (MANDATORY when UI is involved)

- Verify UI + API linkage and UI quality:
  - `web-pc-fullstack-quality-gate.md`
  - `web-pc-ui-quality-checklist.md`
- Ensure fix is root-cure oriented (not a quick patch):
  - `root-cure-strategy.md`
- If you modified a method/class used elsewhere, inventory callers and regressions:
  - `caller-impact-protocol.md`

2) 🔴 **Regression Verification (MANDATORY — Cannot Skip)**

After fixing code, **MUST immediately run regression verification** instead of going directly to code review:

### 2.1 Automated Verification (if tests exist)

```bash
# Run tests related to modified files
# Compare test results before and after fix
# Ensure zero new failures
```

### 2.2 Side Effect Verification (Against Impact Prediction)

```markdown
## Side Effect Verification Results

| Predicted Side Effect | Actual Result | Status |
|----------------------|---------------|--------|
| [copied from Impact Prediction] | [actual observation] | ✅/❌ |

| Predicted Edge Case | Test Result | Status |
|--------------------|-------------|--------|
| [copied from Impact Prediction] | [actual result] | ✅/❌ |
```

### 2.3 Consumer Regression Check

```markdown
## Consumer Regression Verification

| Consumer | Verification Method | Result | Status |
|----------|-------------------|--------|--------|
| [copied from Scope Discovery] | [how to verify] | [result] | ✅/❌ |
```

### 2.4 Lint & Build Check

```bash
# Check lint errors on modified files
read_lints(paths: ["<modified_file>"])

# Ensure build passes (if applicable)
```

**⛔ If ANY verification item fails → return to step 1 to fix, do NOT proceed.**

3) Output Bug Summary (only this)

```markdown
## Bug Summary
- Symptom: ...
- Root Cause: ...
- Fix: ... (may include key verification commands)
- Side Effect Prediction: [all verified passed / issue found: ...]
- Time: YYYY-MM-DD HH:mm:ss
- Version: git=abc1234; optional app=1.2.3
```

4) Run `code-review`
- Invoke `code-review` skill (recommended):
  - Claude Code: `/code-review`
  - Other platforms: `skillora read code-review` then follow it
- **Provide Impact Prediction output during code review** so the reviewer can cross-reference.

5) If review finds bugs → treat them as bugs and loop
- Any correctness/security/behavior regression is a bug, must fix.
- If only style/minor issues found, it's not a bug; unless it hides a real bug, leave for later.
- If the bug should have been caught by this workflow, strengthen the gates: `references/skill-feedback-loop.md`
- **🔴 If review finds regression → execute Regression Autopsy**: `references/self-reflection-protocol.md`
- After fixing review-found bugs: return to step 2 (regression verification), step 3 (summary), and step 4 (review) to execute again.

## Stop Condition (Definition of "Clean")

Only stop the loop when:
- `code-review` reports no correctness/security/behavior issues, AND
- **Regression verification all passed (all items in step 2 ✅)**, AND
- Original bug's tests/verification pass.

If there are remaining issues, user must explicitly waive them (no longer "auto-clean").

## How to Fill Time/Version (for summary)

- Time: Use local time, format `YYYY-MM-DD HH:mm:ss`.
- Version:
  - Git: Use current short commit ID (e.g. `git rev-parse --short HEAD`).
  - App version (optional): Use repo's tag version or manifest version (if available).
