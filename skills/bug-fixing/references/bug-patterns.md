# Bug Pattern Library

Cross-project bug patterns, detection methods, and fix strategies.
Updated by extracting patterns from project-level bug records.

---

## Domain-Specific Pattern Indexes

- Frontend common issues: `frontend-patterns.md`
- Backend common issues: `backend-patterns.md`

---

## Category 1: Input Handling Bugs

| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|----------------|-----------|-------------|
| **Format assumption mismatch** | User input doesn't match expected format | Check parser/validator logic | Add input normalization at parse time |
| **Missing input validation** | Boundary input causes crash | Test with empty/null/special chars | Add validation before processing |
| **Encoding issues** | Garbled text, truncation | Check charset handling | Ensure UTF-8 consistency throughout |
| **Unescaped quotes in strings** | Syntax error prevents startup | Check for unescaped quotes in literals | Escape internal quotes or use single quotes |
| **BOM header causes parse failure** | Parser reports missing header marker | Check file header for BOM/hidden bytes | Save as UTF-8 without BOM |
| **Whitespace sensitivity** | Matching fails unexpectedly | Compare against trimmed values | Normalize whitespace on input |

## Category 2: Status/State Bugs

| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|----------------|-----------|-------------|
| **Status mismatch** | UI shows success but operation failed | Check both HTTP and business status | Parse full response body |
| **Stale state** | Shows outdated data after updates | Check state invalidation | Refresh state after mutations |
| **Race condition** | Intermittent failures, order-dependent | Add timing logs, stress test | Add proper synchronization |
| **Orphaned state** | Cleanup not triggered | Check cleanup paths | Ensure all exit paths clean up |
| **Event ID inconsistency** | Preview stuck/state can't complete | Compare IDs across events | Unify IDs or establish mapping |
| **Over-sync overrides user selection** | Refreshing metadata overwrites dropdown | Check effect/subscription triggers | Only sync on critical conditions |
| **Missing event gate** | Normal output triggers side effects | Check if event source has gate | Only process explicit events |

## Category 3: API Integration Bugs

| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|----------------|-----------|-------------|
| **Missing timeout** | Request hangs forever | Check timeout config | Add explicit timeout |
| **No retry logic** | Transient failure causes permanent error | Check retry implementation | Add retry with backoff |
| **Response structure assumption** | Crash on unexpected API response | Check response parsing | Add defensive parsing |
| **Missing error propagation** | Errors silently swallowed | Trace error flow | Ensure errors surface |
| **Model capability mismatch** | Calling unsupported feature returns 400 | Check capability flags | Add capability detection + error message |

## Category 4: Data Flow Bugs

| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|----------------|-----------|-------------|
| **Transformation mismatch** | Data displayed incorrectly | Trace data path end-to-end | Fix transformation logic |
| **Missing null check** | undefined/null crash | Check optional chaining | Add null guards |
| **Off-by-one error** | Pagination/index issues | Check boundary conditions | Validate index calculations |
| **Type coercion** | Unexpected comparison results | Check type handling | Use explicit type conversion |
| **State-display mismatch** | UI doesn't reflect state change | Compare write vs read logic | Align read logic to handle all write formats |
| **Parent-child selection inconsistency** | Parent selected but children not | Trace selection cascade | Read logic must check parent state |

## Category 5: Configuration Bugs

| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|----------------|-----------|-------------|
| **Environment mismatch** | Works in dev, fails in production | Compare env configs | Ensure config consistency |
| **Missing default values** | Crash when config not set | Check fallback values | Add reasonable defaults |
| **Non-critical dependency without degradation** | Logging errors but core works | Check dependency availability | Degrade/skip non-critical paths |
| **Config priority confusion** | Wrong value used | Trace config loading order | Document config priority |
| **Secret exposure** | Secrets in logs/UI | Search for sensitive data | Sanitize before logging |

### Category 5.1: Multi-Environment Config Bugs

| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|----------------|-----------|-------------|
| **Partial env file fix** | Fix works in prod, fails in dev | Check all .env* files | Update all env files |
| **Startup script mismatch** | bat/sh uses different env | Check startup scripts | Verify which env file each script uses |
| **Config loading order** | Wrong value overrides correct one | Trace config loading | Document and fix priority |
| **Missing env variable** | Works locally, fails in CI/CD | Compare local vs CI env | Add variable to all environments |
| **Framework env load priority assumption** | Fix uses wrong priority order | Read framework source code | Verify merge semantics, document in comments |
| **Windows event loop incompatibility** | Subprocess NotImplementedError | Check event loop policy | Add platform compatibility pre-check |

**Environment file checklist** (mandatory for config bugs):

| File | Checked | Updated |
|------|---------|---------|
| `.env` | [ ] | [ ] |
| `.env.local` | [ ] | [ ] |
| `.env.development` | [ ] | [ ] |
| `.env.test` | [ ] | [ ] |
| `.env.staging` | [ ] | [ ] |
| `.env.production` | [ ] | [ ] |

### Category 5.2: JSON/Regex Processing Bugs

| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|----------------|-----------|-------------|
| **Unnecessary JSON preprocessing** | Parsing fails after "fix" | Check if input already valid | Remove unnecessary preprocessing |
| **Backslash double-escaping** | Paths get triple-escaped | Compare input vs processed output | Trust the source, don't over-process |
| **Regex breaks valid escapes** | Valid escapes become invalid | Test with system paths | Verify regex doesn't match already-escaped chars |

## Category 6: Platform-Specific Bugs

| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|----------------|-----------|-------------|
| **API unavailable** | Feature fails in specific env | Check platform compatibility | Add feature detection/fallback |
| **Permission denied** | Operation blocked | Check security config | Configure required permissions |
| **Path handling** | File operations fail cross-OS | Check path separators | Use platform-agnostic paths |
| **Binary vs text** | File corruption | Check read/write modes | Use correct mode for file type |

## Category 7: State-Display Consistency Bugs

| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|----------------|-----------|-------------|
| **Write-read format mismatch** | Operation succeeds but UI doesn't update | Compare storage vs display logic | Align read to handle all write formats |
| **Derived state inconsistency** | Parent/child selection out of sync | Trace derivation chain | Derive child from parent, not vice versa |
| **Implicit vs explicit state** | Selected items show as unselected | Check if read assumes explicit storage | Handle implicit state (e.g. inherited) |
| **Partial update** | Some UI elements update, others don't | Trace all state consumers | Ensure all consumers respond |

**Key detection questions**:
1. What format does the WRITE function store?
2. What format does the READ function expect?
3. Do they match? If not, extend read logic.

## Category 8: Component Integration & Feature Propagation

| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|----------------|-----------|-------------|
| **Incomplete prop propagation** | Feature works in one place, fails elsewhere | grep all component usage | Ensure all parents pass required props |
| **Partial feature release** | New behavior only in some views | Search for old pattern usage | Global search-replace or centralize |
| **Context penetration** | Component needs unavailable data | Check component hierarchy | Lift state or use global Store/Context |
| **Style/theme inconsistency** | Component looks different in contexts | Check CSS inheritance | Standardize styles or use design tokens |

## Category 9: UI Display Completeness Bugs

| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|----------------|-----------|-------------|
| **Missing display component** | Data exists but UI doesn't show it | Compare API fields vs UI elements | Add component for missing fields |
| **Wrong field priority** | Shows irrelevant data | Check field selection logic | Use context-aware field selection |
| **Destructured but unused** | Variable destructured but not rendered | Search for unused destructured vars | Add render logic |
| **Method-agnostic display** | Same logic for all HTTP methods | Check if display considers method | Use method-aware logic |

## Category 10: API Schema Bugs

| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|----------------|-----------|-------------|
| **Update Schema missing field** | Request has field but no update | Compare request vs response | Add field to Update Schema |
| **Create Schema missing field** | Fields ignored during creation | Check if new record has all fields | Add field to Create Schema |
| **Field type mismatch** | Data silently converted or lost | Check Schema type vs DB type | Align type definitions |
| **Pydantic silently drops fields** | Undefined fields ignored | Check model_dump(exclude_unset) | Add field definition to Schema |

## Category 11: ORM/SQLAlchemy Bugs

| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|----------------|-----------|-------------|
| **Enum native_enum missing** | LookupError on enum values | Check Enum() for native_enum=False | Add native_enum=False |
| **SQL dialect incompatibility** | Syntax error on specific DB | Check for CAST AS TEXT/ILIKE/::type | Use SQLAlchemy abstractions |
| **Foreign key constraint failure** | IntegrityError on insert | Check ondelete handling | Set ondelete="SET NULL" + nullable |
| **Cached old code (.pyc)** | Fix applied but error persists | Check __pycache__/*.pyc timestamps | Delete .pyc files, restart |
| **Missing migration** | Unknown column error | Check alembic/versions | Create migration file |
| **Field length insufficient** | Data too long for column | Check column vs data length | Create migration to extend |

---

## High-Frequency Root Causes (Top 18)

1. **Unverified assumptions** — assuming API/feature works without checking docs
2. **Incomplete status check** — only checking HTTP status, not business status
3. **Missing edge case handling** — not considering empty/null/boundary input
4. **Stale closure/state** — capturing old values in callbacks/effects
5. **Missing cleanup** — resources not released on error paths
6. **Environment differences** — dev/prod config mismatch
7. **Type misunderstanding** — wrong assumptions about data types
8. **Async ordering** — assuming async operations execute sequentially
9. **Cache invalidation** — serving stale cached data
10. **Error swallowing** — catching errors but not surfacing them
11. **State-display format mismatch** — write stores X, read expects Y
12. **Incomplete prop propagation** — updated base component, missed consumers
13. **Incomplete UI display** — backend returns fields, frontend doesn't render
14. **ORM enum mapping error** — values_callable missing native_enum=False
15. **SQL dialect incompatibility** — DB-specific syntax like CAST AS TEXT
16. **Foreign key constraint not considering deletion** — missing ondelete
17. **Update Schema field omission** — Pydantic silently drops undefined fields
18. **Event loop override** — uvicorn reload mode changes event loop policy

---

## Universal Verification Checklist

### Core Checks

- [ ] Original scenario no longer reproduces
- [ ] Related features still work
- [ ] Error paths handled gracefully
- [ ] No new console errors or warnings
- [ ] Code passes all static checks

### Edge Case Checks

- [ ] Handles empty/null/undefined
- [ ] Handles min/max/zero boundary values
- [ ] No race conditions introduced
- [ ] No resource leaks on any exit path

### Regression Checks

- [ ] All existing tests still pass
- [ ] New test added for bug scenario
- [ ] Similar patterns checked globally
- [ ] All consumers of modified code verified

---

## Pattern Extraction Guide

### When to Extract

| Condition | Required |
|-----------|----------|
| No match found in pre-fix search | Yes (new pattern) |
| Fix strategy differs from known pattern | Yes (supplement) |
| Discovered new detection method | Yes (enhancement) |
| P0/P1 severe bug | Yes (important experience) |
| Simple bug, existing pattern covers it | Optional |

### How to Extract

1. **Identify category** — which category table does this bug belong to?
2. **Generalize** — remove project-specific names, use universal terms
3. **Format as table row** — Pattern | Symptom | Detection | Fix Strategy
4. **Verify searchability** — can it be found with 3 different keyword searches?

### Generalization Rules

| Project-Specific | Generalized |
|-----------------|-------------|
| `UserService.login()` | Service method |
| `React useState` | Frontend state management |
| `/api/v1/users` | API endpoint |
| Specific error message | Error type (TypeError, 500, etc.) |

### Quality Standards

| Standard | Check |
|----------|-------|
| **Generality** | Would someone on a different project understand? |
| **Actionability** | Can someone execute the steps directly? |
| **Searchability** | Can it be found with different keywords? |
| **Completeness** | Has symptom + detection + fix? |
