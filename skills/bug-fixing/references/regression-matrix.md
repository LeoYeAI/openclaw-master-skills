# Zero-Regression Verification Matrix

The definitive checklist to ensure bug fixes don't break existing functionality.

---

## Section A: Pre-Fix Baseline (BEFORE writing fix code)

| # | Check | How | Evidence Required | Pass? |
|---|-------|-----|-------------------|-------|
| A1 | Bug reproduced | Follow exact repro steps | Screenshot/video/log | [ ] |
| A2 | Test baseline captured | Run full test suite | Test output saved | [ ] |
| A3 | Affected files identified | Impact analysis L0-L2 | File list (<5 ideal) | [ ] |
| A4 | Working features listed | Manual check near bug | Feature checklist | [ ] |
| A5 | Root cause identified | 5 Whys / Data Flow | One-sentence statement | [ ] |

**STOP if any A-check fails. You are not ready to fix.**

---

## Section B: Fix Quality (DURING implementation)

| # | Check | Criteria | Pass? |
|---|-------|----------|-------|
| B1 | Minimal LOC | <=20 lines ideal, <=50 max | [ ] |
| B2 | Single concern | Only the bug fixed, no refactoring | [ ] |
| B3 | No new dependencies | No new packages added | [ ] |
| B4 | No API contract changes | Existing callers unchanged | [ ] |
| B5 | Config over hardcode | Solution hierarchy correct | [ ] |
| B6 | Old path preserved | Feature flag for critical changes | [ ] |

If B4 fails (API change needed), document and get explicit approval.

---

## Section C: Correctness (AFTER fix, BEFORE commit)

| # | Check | How | Expected | Pass? |
|---|-------|-----|----------|-------|
| C1 | Bug fixed | Original repro steps | Bug gone | [ ] |
| C2 | Root cause addressed | Review against RCA | Targets root cause | [ ] |
| C3 | Null case | null/undefined input | Handled gracefully | [ ] |
| C4 | Empty case | Empty string/array | Handled gracefully | [ ] |
| C5 | Boundary case | min/max/edge values | Handled gracefully | [ ] |
| C6 | Error case | Network/DB failure | Fails gracefully | [ ] |

---

## Section D: Regression (CRITICAL)

| # | Check | How | Expected | Pass? |
|---|-------|-----|----------|-------|
| D1 | L1 Direct callers | Test functions calling fixed code | All work | [ ] |
| D2 | L2 Indirect callers | Test callers of L1 | All work | [ ] |
| D3 | L3 Cross-module | Verify other modules | No breakage | [ ] |
| D4 | L4 API surface | Test API endpoints | Responses unchanged | [ ] |
| D5 | L5 Data flow | Verify data integrity | No corruption | [ ] |
| D6 | UI features | Manual test listed features | All work | [ ] |
| D7 | Baseline comparison | Run full test suite | Same or better than A2 | [ ] |

**D7 is the final gate. If tests regress, fix is NOT ready.**

---

## Section E: Code Quality

| # | Check | Command | Expected | Pass? |
|---|-------|---------|----------|-------|
| E1 | Linter clean | ReadLints on modified files | Zero new errors | [ ] |
| E2 | Type check | Language-specific typecheck | Pass | [ ] |
| E3 | Build succeeds | Full build command | Success | [ ] |
| E4 | Unit tests | Run affected test files | All pass | [ ] |
| E5 | Integration tests | Run integration suite | All pass | [ ] |
| E6 | E2E tests | Run E2E suite (if applicable) | All pass | [ ] |

---

## Section F: Completeness

| # | Check | How | Pass? |
|---|-------|-----|-------|
| F1 | Similar bugs searched | `rg -n` for same pattern | All found fixed | [ ] |
| F2 | Documentation updated | If behavior changed | Docs reflect change | [ ] |
| F3 | Test for bug added | New test prevents recurrence | Test exists | [ ] |
| F4 | Commit message clear | Includes bug ID and root cause | Written | [ ] |

---

## Verification Commands by Stack

### Frontend (React/Vue/TypeScript)

```bash
npm run lint
npm run typecheck
npm run build
npm test -- --coverage
npm run test:e2e
```

### Backend (Python)

```bash
ruff check .
mypy .
pytest --cov=src
pytest tests/integration/
```

### Backend (Node.js)

```bash
npm run lint
npm run build
npm test
npm run test:integration
```

### Backend (Go)

```bash
go vet ./...
golangci-lint run
go build ./...
go test ./... -cover
```

### Backend (Java)

```bash
./gradlew check test integrationTest
# or: mvn verify
```

---

## Verification Report Template

```markdown
## Bug Fix Verification Report

**Bug ID**: BUG-XXXX
**Date**: YYYY-MM-DD

### Summary
- Root Cause: [one sentence]
- Fix Approach: [one sentence]
- Files Changed: [count] files, [LOC] lines

### Matrix Results

| Section | Checks | Passed | Notes |
|---------|--------|--------|-------|
| A: Pre-Fix Baseline | 5 | /5 | |
| B: Fix Quality | 6 | /6 | |
| C: Correctness | 6 | /6 | |
| D: Regression | 7 | /7 | |
| E: Code Quality | 6 | /6 | |
| F: Completeness | 4 | /4 | |
| **TOTAL** | **34** | **/34** | |

### Evidence
- [ ] Screenshot/log of bug fixed
- [ ] Test baseline before: [link]
- [ ] Test baseline after: [link]
- [ ] Similar bugs found and fixed: [count]
```

---

## Common Failures and Recovery

| Failure | Symptom | Recovery |
|---------|---------|----------|
| D7 fails | New test failures | Revert, investigate, re-fix |
| B1 fails | Change >50 lines | Split into smaller changes |
| C1 fails | Bug still occurs | Review RCA, find actual root |
| F1 fails | Pattern found elsewhere | Fix all before declaring done |

---

## The Golden Rule

> **If you cannot pass Section D (Regression), the fix is NOT ready.**
> No exceptions. No "it should be fine". No "I'll fix it later".
> A broken fix is worse than no fix.
