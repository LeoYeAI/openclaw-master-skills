# Verification Gates

> This file consolidates the core content from fix-completeness-checklist, zero-regression-matrix, and code-review-gate.

---

## 1. Fix Completeness Check

### 1.1 Control Flow Completeness

| Fix Pattern | Potential Issue | Correct Approach |
|------------|-----------------|------------------|
| Adding `if condition: return` | Function may silently return empty | Return meaningful value or throw exception |
| Adding `if condition: break` | No handling for break outside loop | Set state/output before break |
| Adding `try-except: pass` | Exception silently swallowed | Log + return/throw |

### 1.2 Boundary Condition Coverage

| Scenario | Must Test |
|----------|----------|
| Resource limits | Low memory, large data volume |
| Empty/abnormal input | null, empty string, very long text |
| Concurrency | Multiple users operating simultaneously |
| Timeout | External service slow or unavailable |

### 1.3 Degradation Strategy

```python
# ❌ Wrong fix
if current_tokens > max_tokens:
    logger.warning("Token limit exceeded")
    return  # Returns nothing, user gets no response

# ✅ Correct fix
if current_tokens > max_tokens:
    logger.warning("Token limit exceeded, applying degradation")
    context = truncate_context(context)  # Degradation strategy
    return generate_with_constraints()   # Still produce output
```

### 1.4 User Visibility Guarantee

| Scenario | Must Guarantee |
|----------|---------------|
| Streaming output | At least one output chunk |
| API response | Non-empty response body |
| UI feedback | Visual/text indicator |

---

## 2. Zero-Regression Verification Matrix

### Section A: Pre-Fix Baseline

| # | Check | Method | Pass |
|---|-------|--------|------|
| A1 | Bug reproduced | Follow repro steps | ☐ |
| A2 | Test baseline saved | Run full test suite | ☐ |
| A3 | Affected files identified | Impact analysis Layer 0-2 | ☐ |
| A4 | Working features listed | Manual check near bug area | ☐ |
| A5 | Root cause identified | Five Whys / Data Flow | ☐ |

**⛔ If any A check fails, do NOT start fixing.**

### Section B: Fix Quality

| # | Check | Criteria | Pass |
|---|-------|----------|------|
| B1 | Minimal LOC | ≤20 lines (ideal), ≤50 lines (max) | ☐ |
| B2 | Single concern | Only fix the bug, no refactoring | ☐ |
| B3 | No new dependencies | Don't add new packages | ☐ |
| B4 | API contract unchanged | Existing callers unaffected | ☐ |

### Section C: Correctness Verification

| # | Check | Method | Pass |
|---|-------|--------|------|
| C1 | Bug fixed | Reproduce original steps | ☐ |
| C2 | Root cause addressed | Code review against RCA | ☐ |
| C3 | Null case | null/undefined input test | ☐ |
| C4 | Empty case | Empty string/array test | ☐ |
| C5 | Boundary case | min/max/edge value test | ☐ |
| C6 | Error case | Simulate network/DB failure | ☐ |

### Section D: Regression Verification (CRITICAL)

| # | Check | Method | Pass |
|---|-------|--------|------|
| D1 | Layer 1 (direct callers) | Test each function calling fixed code | ☐ |
| D2 | Layer 2 (indirect callers) | Test callers of Layer 1 | ☐ |
| D3 | UI features | Manual test listed features | ☐ |
| D4 | Baseline comparison | Run full test suite again | ☐ |

**⛔ D4 is the final gate. If tests regress, the fix is NOT ready.**

### Section E: Code Quality Verification

| # | Check | Command | Pass |
|---|-------|---------|------|
| E1 | Linter clean | Run `ReadLints` on modified files | ☐ |
| E2 | Type check | Language-specific typecheck | ☐ |
| E3 | Build succeeds | Full build command | ☐ |
| E4 | Unit tests | Run affected test files | ☐ |

### Section F: Completeness Check

| # | Check | Method | Pass |
|---|-------|--------|------|
| F1 | Similar bugs searched | IDE search or `rg -n` | ☐ |
| F2 | Bug test added | New test prevents recurrence | ☐ |
| F3 | Commit message clear | Includes bug ID and root cause | ☐ |

---

## 3. Code Review Gate

### 3.1 When to Run

After verification steps (test/lint/build) pass, before declaring the bug "done".

### 3.2 Code Review Checklist (Bug Fix Specific)

#### Correctness & Edge Cases

- [ ] Fix targets **root cause**, not just symptom?
- [ ] Edge cases handled? (empty input, missing data, null, timeout)
- [ ] Error messages actionable?

#### Contract Compatibility (Common Regression Source)

- [ ] API shape: No unexpected breaking changes (renamed fields, removed keys, changed types)
- [ ] Default values: Distinguish **omitted** vs **null** vs **empty**
- [ ] Backward compatibility: Old paths don't overwrite new settings

#### Reference Safety (Impact Scope Control)

- [ ] Modified function/class has references elsewhere: updated or preserved callers?
- [ ] Shared config/mapping affects multiple consumers: verified list + detail + selection UI?

#### Security & Privacy

- [ ] No secrets in logs/errors
- [ ] Auth/permissions still enforced on all paths

#### Performance & Failure Modes

- [ ] No N+1 behavior introduced
- [ ] Timeouts explicit; retries bounded
- [ ] Cache/invalidation still correct

---

## 4. Fix-Review Loop

### 4.1 Loop Contract (Must Follow This Order)

```
1. Fix
   └─ Apply minimal change to resolve root cause
   └─ Run minimal verification to prove bug is fixed

2. Output Bug Summary (only this)
   ┌─────────────────────────────────────┐
   │ ## Bug Summary                      │
   │ - Symptom: ...                      │
   │ - Root Cause: ...                   │
   │ - Fix: ...                          │
   │ - Time: YYYY-MM-DD HH:mm:ss        │
   │ - Version: git=abc1234              │
   └─────────────────────────────────────┘

3. Run code-review
   └─ Invoke /code-review or read code-review SKILL.md

4. If review finds issues → treat as bugs and loop
   └─ Correctness/security/behavior regression = Bug, must fix
   └─ Style/minor issues only = Not a bug, can address later
   └─ After fixing review-found bugs → return to step 2
```

### 4.2 Stop Condition (Definition of "Clean")

Only stop the loop when:
1. `code-review` reports no correctness/security/behavior issues
2. Original bug's tests/verification pass

---

## 5. Quick Verification Commands

### Frontend (React/Vue/TypeScript)

```bash
npm run lint
npm run typecheck  # or: npx tsc --noEmit
npm run build
npm test -- --coverage
```

### Backend (Python)

```bash
ruff check .
mypy .
pytest --cov=src
```

### Backend (Node.js)

```bash
npm run lint
npm run build
npm test
```

---

## 6. Verification Report Template

```markdown
## Bug Fix Verification Report

**Bug ID**: BUG-XXXX
**Date**: YYYY-MM-DD

### Summary
- **Root Cause**: [one sentence]
- **Fix Approach**: [one sentence]
- **Files Changed**: [count] files, [LOC] lines

### Matrix Results

| Section | Checks | Passed | Notes |
|---------|--------|--------|-------|
| A: Pre-Fix Baseline | 5 | 5/5 | |
| B: Fix Quality | 4 | 4/4 | |
| C: Correctness | 6 | 6/6 | |
| D: Regression | 4 | 4/4 | |
| E: Code Quality | 4 | 4/4 | |
| F: Completeness | 3 | 3/3 | |
| **Total** | **26** | **26/26** | ✅ Ready to merge |

### Sign-off
- [ ] All matrix checks pass
- [ ] No new lint errors
- [ ] Test suite green
- [ ] Ready for review
```

---

## 7. Detailed Reference Files

For more detailed information, refer to the original files:

| Original File | Content |
|---------------|---------|
| `fix-completeness-checklist.md` | Incremental fix protocol, static analysis gates |
| `zero-regression-matrix.md` | Complete 34-item matrix, recovery guide |
| `code-review-gate.md` | Complete code review checklist |
