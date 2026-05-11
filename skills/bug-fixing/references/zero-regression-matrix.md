# Zero-Regression Verification Matrix

> The definitive checklist to ensure bug fixes don't break existing functionality or introduce new bugs.

## Why This Matrix Exists

| Problem | Impact | This Matrix Prevents |
|---------|--------|---------------------|
| Fix breaks other feature | User loses functionality | Regression verification |
| Fix introduces new bug | Two bugs instead of one | Systematic validation |
| Fix only addresses symptom | Bug returns later | Root cause verification |
| Fix scope creeps | Unnecessary changes | Minimal change enforcement |

---

## The Complete Matrix

### Section A: Pre-Fix Baseline (BEFORE writing any fix code)

| # | Check | How | Evidence Required | Pass? |
|---|-------|-----|-------------------|-------|
| A1 | Bug reproduced | Follow exact repro steps | Screenshot/video/log | ☐ |
| A2 | Test baseline captured | Run full test suite | Test output saved | ☐ |
| A3 | Affected files identified | Impact analysis Layer 0-2 | File list (<5 ideal) | ☐ |
| A4 | Working features listed | Manual check near bug area | Feature checklist | ☐ |
| A5 | Root cause identified | 5 Whys / Data Flow / Timeline | One-sentence statement | ☐ |

**STOP if any A-check fails. You are not ready to fix.**

---

### Section B: Fix Quality (DURING fix implementation)

| # | Check | Criteria | Pass? |
|---|-------|----------|-------|
| B1 | Minimal LOC | ≤ 20 lines changed (ideal), ≤ 50 lines (max) | ☐ |
| B2 | Single concern | Only the bug fixed, no refactoring | ☐ |
| B3 | No new dependencies | No new packages added | ☐ |
| B4 | No API contract changes | Existing callers unchanged | ☐ |
| B5 | Config over hardcode | Used solution hierarchy correctly | ☐ |
| B6 | Old path preserved | For critical: feature flag exists | ☐ |

**If B4 fails (API change needed), document and get explicit approval.**

---

### Section C: Correctness Verification (AFTER fix, BEFORE commit)

| # | Check | How | Expected | Pass? |
|---|-------|-----|----------|-------|
| C1 | Bug fixed | Reproduce original steps | Bug no longer occurs | ☐ |
| C2 | Root cause addressed | Code review against RCA | Fix targets root cause | ☐ |
| C3 | Null case | Test with null/undefined input | Handled gracefully | ☐ |
| C4 | Empty case | Test with empty string/array | Handled gracefully | ☐ |
| C5 | Boundary case | Test min/max/edge values | Handled gracefully | ☐ |
| C6 | Error case | Simulate network/DB failure | Fails gracefully | ☐ |

---

### Section D: Regression Verification (CRITICAL — FROM IMPACT ANALYSIS)

| # | Check | How | Expected | Pass? |
|---|-------|-----|----------|-------|
| D1 | Layer 1 (Direct callers) | Test each function calling fixed code | All still work | ☐ |
| D2 | Layer 2 (Indirect callers) | Test callers of Layer 1 | All still work | ☐ |
| D3 | Layer 3 (Cross-module) | Verify other modules | No breakage | ☐ |
| D4 | Layer 4 (API surface) | Test API endpoints | Responses unchanged | ☐ |
| D5 | Layer 5 (Data flow) | Verify data integrity | No corruption | ☐ |
| D6 | UI Features | Manual test listed features | All still work | ☐ |
| D7 | Baseline comparison | Run full test suite again | Same or better than A2 | ☐ |

**D7 is the final gate. If tests regress, fix is not ready.**

UI check guidance: for Web/PC bug fixes, enforce the UI + API linkage gate:
`web-pc-fullstack-quality-gate.md`

---

### Section E: Code Quality Verification

| # | Check | Command | Expected | Pass? |
|---|-------|---------|----------|-------|
| E1 | Linter clean | `read_lints` on modified files | Zero new errors | ☐ |
| E2 | Type check | Language-specific typecheck | Pass | ☐ |
| E3 | Build succeeds | Full build command | Success | ☐ |
| E4 | Unit tests | Run affected test files | All pass | ☐ |
| E5 | Integration tests | Run integration suite | All pass | ☐ |
| E6 | E2E tests (if applicable) | Run E2E suite | All pass | ☐ |

---

### Section F: Completeness Check

| # | Check | How | Pass? |
|---|-------|-----|-------|
| F1 | Similar bugs searched | IDE content search or `rg -n` for the same pattern | All found fixed | ☐ |
| F2 | Documentation updated | If behavior changed | Docs reflect change | ☐ |
| F3 | Test for bug added | New test prevents recurrence | Test exists | ☐ |
| F4 | Commit message clear | Includes bug ID and root cause | Message written | ☐ |

---

## Quick Verification Commands by Stack

### Frontend (React/Vue/TypeScript)

```bash
# E1-E3: Code quality
npm run lint
npm run typecheck  # or: npx tsc --noEmit
npm run build

# E4-E6: Tests
npm test -- --coverage
npm run test:e2e
```

### Backend (Python)

```bash
# E1-E3: Code quality
ruff check .
mypy .
pip install -e .  # or poetry install

# E4-E6: Tests
pytest --cov=src
pytest tests/integration/
```

### Backend (Node.js)

```bash
# E1-E3: Code quality
npm run lint
npm run build

# E4-E6: Tests
npm test
npm run test:integration
```

### Backend (Go)

```bash
# E1-E3: Code quality
go vet ./...
golangci-lint run
go build ./...

# E4-E6: Tests
go test ./... -cover
go test ./... -tags=integration
```

### Backend (Java)

```bash
# E1-E6: All in one
./gradlew check test integrationTest
# or
mvn verify
```

---

## Verification Report Template

Copy and fill after completing the matrix:

```markdown
## Bug Fix Verification Report

**Bug ID**: BUG-XXXX
**Date**: YYYY-MM-DD
**Fixed By**: [Name]

### Summary
- **Root Cause**: [One sentence]
- **Fix Approach**: [One sentence]
- **Files Changed**: [Count] files, [LOC] lines

### Matrix Results

| Section | Checks | Passed | Notes |
|---------|--------|--------|-------|
| A: Pre-Fix Baseline | 5 | 5/5 | |
| B: Fix Quality | 6 | 6/6 | |
| C: Correctness | 6 | 6/6 | |
| D: Regression | 7 | 7/7 | |
| E: Code Quality | 6 | 6/6 | |
| F: Completeness | 4 | 4/4 | |
| **TOTAL** | **34** | **34/34** | ✅ Ready to merge |

### Evidence
- [ ] Screenshot/log of bug fixed
- [ ] Test baseline before: [link/output]
- [ ] Test baseline after: [link/output]
- [ ] Similar bugs found and fixed: [count]

### Sign-off
- [ ] All matrix checks pass
- [ ] No new lint errors
- [ ] Test suite green
- [ ] Ready for review
```

---

## When to Use Zero-Risk Protocol Instead

Escalate to `references/zero-risk-protocol.md` if ANY of these apply:

| Condition | Action |
|-----------|--------|
| Production incident | Zero-Risk Protocol |
| Payment/Auth/User data affected | Zero-Risk Protocol |
| Impact analysis reaches Layer 4-5 | Zero-Risk Protocol |
| Team lead requests "zero-risk" | Zero-Risk Protocol |
| >50 LOC change required | Zero-Risk Protocol |
| API contract must change | Zero-Risk Protocol |

---

## Common Failures and How to Recover

| Failure | Symptom | Recovery |
|---------|---------|----------|
| D7 fails (tests regress) | New test failures | Revert, investigate, re-fix |
| B1 fails (too many LOC) | Change >50 lines | Split into smaller changes |
| C1 fails (bug not fixed) | Bug still occurs | Review RCA, find actual root |
| F1 fails (similar bugs) | Pattern found elsewhere | Fix all before declaring done |

---

## The Golden Rule

> **If you cannot pass Section D (Regression), the fix is NOT ready.**
>
> No exceptions. No "it should be fine". No "I'll fix it later".
>
> A broken fix is worse than no fix.
