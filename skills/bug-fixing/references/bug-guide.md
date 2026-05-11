# Bug Fixing Universal Guide

This document provides cross-project bug patterns, detection methods, and fix strategies. Updated periodically by extracting patterns from project-level bug records.

---

## Common Bug Pattern Library

### Frontend/Backend High-Frequency Issue Index

- Frontend common issues and fixes: `frontend-common-issues.md`
- Backend common issues and fixes: `backend-common-issues.md`
- Web/PC fullstack quality gate (UI + API integration): `web-pc-fullstack-quality-gate.md`

### Category 1: Input Handling Bugs

| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|----------------|-----------|-------------|
| **Format assumption mismatch** | User input doesn't match expected format | Check parser/validator logic | Add input normalization at parse time |
| **Missing input validation** | Boundary input causes crash or abnormal behavior | Test with empty/null/special chars | Add validation before processing |
| **Encoding issues** | Garbled text, truncation | Check charset handling | Ensure UTF-8 consistency throughout |
| **Unescaped quotes in strings** | Syntax error prevents app from starting | Check for unescaped quotes in string literals | Escape internal quotes or use single quotes |
| **BOM header causes parse failure** | Parser reports missing frontmatter/header marker | Check file header for BOM/hidden bytes | Save as UTF-8 without BOM |
| **Whitespace sensitivity** | Matching fails unexpectedly | Compare against trimmed values | Normalize whitespace on input |

### Category 2: Status/State Bugs

| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|----------------|-----------|-------------|
| **Status mismatch** | UI shows success but operation failed | Check both HTTP and business status | Parse full response body |
| **Stale state** | Shows outdated data after updates | Check state invalidation | Refresh state after mutations |
| **Race condition** | Intermittent failures, order-dependent | Add timing logs, stress test | Add proper synchronization |
| **Fallback stream conflicts with real stream** | Preview content duplicated or jumps | Check if fallback/typewriter syncs applied length | Sync applied length during fallback append or align to current length |
| **Orphaned state** | Cleanup not triggered | Check cleanup paths | Ensure all exit paths clean up |
| **Event ID inconsistency** | Preview stuck/state can't complete | Compare `tool_call_id` across multiple events | Unify IDs or establish mapping |
| **Over-sync overrides user selection** | Switching model/refreshing metadata auto-overwrites dropdown selection | Check effect/subscription trigger conditions | Only sync on critical conditions (e.g. session switch), avoid overriding manual selections |
| **Missing event gate** | Normal output triggers preview/side effects | Check if event source has explicit gate | Only process events from explicit tool calls or user actions |

### Category 3: API Integration Bugs

| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|----------------|-----------|-------------|
| **Missing timeout** | Request hangs forever | Check timeout config | Add explicit timeout |
| **No retry logic** | Transient failure causes permanent error | Check retry implementation | Add retry with backoff |
| **Response structure assumption** | Crash on unexpected API response | Check response parsing | Add defensive parsing |
| **Missing error propagation** | Errors silently swallowed | Trace error flow | Ensure errors surface |
| **Model capability assumption mismatch** | Calling unsupported feature (e.g. Function Call or chat messages) returns 400 | Check model capability flags/pattern matching lists, watch for 20015/20037 error codes | Add capability detection + user-friendly error message |

### Category 4: Data Flow Bugs

| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|----------------|-----------|-------------|
| **Transformation mismatch** | Data displayed incorrectly | Trace data path end-to-end | Fix transformation logic |
| **Missing null check** | undefined/null crash | Check optional chaining | Add null guards |
| **Off-by-one error** | Pagination/index issues | Check boundary conditions | Validate index calculations |
| **Type coercion** | Unexpected comparison results | Check type handling | Use explicit type conversion |
| **State-display mismatch** | UI doesn't reflect state change | Compare write format vs read logic | Ensure read logic handles all write formats |
| **Parent-child selection inconsistency** | Parent selected but children not | Trace selection cascade logic | Read logic must check parent state |
| **Stream buffer reset** | Streaming content only shows first segment | Check buffer lifecycle/dependencies | Use `ref` to persist buffer or use external cache |

### Category 5: Configuration Bugs

| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|----------------|-----------|-------------|
| **Environment mismatch** | Works in dev, fails in production | Compare env configs | Ensure config consistency |
| **Missing default values** | Crash when config not set | Check fallback values | Add reasonable defaults |
| **Non-critical dependency without degradation** | Logging/metrics errors but core functions work | Check dependency availability and error level | Degrade/skip non-critical paths and lower log level |
| **Config priority confusion** | Wrong value used | Trace config loading order | Document config priority |
| **Secret exposure** | Secrets in logs/UI | Search for sensitive data | Sanitize before logging |

### Category 5.1: 🔴 Multi-Environment Config Bugs (CRITICAL)

> **This is the #1 cause of "fix doesn't take effect" scenarios!**

| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|----------------|-----------|-------------|
| **Partial env file fix** | Fix works in prod, fails in dev | Check all .env* files | Update all env files |
| **Startup script mismatch** | bat/sh uses different env | Check startup scripts | Verify which env file each script uses |
| **Config loading order** | Wrong value overrides correct one | Trace config loading | Document and fix priority |
| **Missing env variable** | Works locally, fails in CI/CD | Compare local vs CI env | Add variable to all environments |
| **Framework env load priority assumption** | Fix uses wrong priority order (e.g. "first file wins" but actually last wins) | 🔴 Read framework source code to understand actual loading logic (e.g. pydantic-settings uses dict.update()) | Verify dict.update/merge semantics before ordering files, document verified priority direction in code comments |
| **Windows event loop incompatibility** | Subprocess creation raises NotImplementedError | Check if event loop policy supports subprocess | Add platform compatibility pre-check, graceful degradation |

**Real Case Study:**
```
Problem: User's bat script uses dev env file, but bug fix only added prod config
Result: Bug persists when running in dev mode

Root Cause Analysis:
- dev.bat → loads .env.development
- npm run start → loads .env.production
- Fix only updated .env.production
- Dev mode never got the fix!

Correct Fix:
1. Identify all env files: .env, .env.development, .env.production, .env.test
2. Identify all startup scripts: dev.bat, start.bat, npm scripts
3. Map: script → env file → variables
4. Apply fix to ALL relevant env files
5. Verify in all modes
```

**Environment File Checklist (MANDATORY for config bugs):**

| File | Checked | Updated |
|------|---------|---------|
| `.env` | [ ] | [ ] |
| `.env.local` | [ ] | [ ] |
| `.env.development` | [ ] | [ ] |
| `.env.development.local` | [ ] | [ ] |
| `.env.test` | [ ] | [ ] |
| `.env.staging` | [ ] | [ ] |
| `.env.production` | [ ] | [ ] |
| `.env.production.local` | [ ] | [ ] |

**Startup Script Checklist:**

| Script | Mode | Env File Used | Verified |
|--------|------|---------------|---------|
| `npm run dev` | Development | ? | [ ] |
| `npm run start` | Production | ? | [ ] |
| `dev.bat` / `dev.sh` | Development | ? | [ ] |
| `start.bat` / `start.sh` | Production | ? | [ ] |
| Docker Compose | Various | ? | [ ] |

**Quick Detection Commands:**
```bash
# Find all env files
find . -name ".env*" -o -name "*.env" 2>/dev/null

# Search config key across all files
grep -rn "YOUR_CONFIG_KEY" . --include="*.env*" --include="*.yml" --include="*.json"

# Find startup scripts
grep -rn "NODE_ENV\|VITE_\|REACT_APP_" . --include="*.sh" --include="*.bat" --include="package.json"
```

### Category 5.2: 🔴 JSON/Regex Processing Bugs (CRITICAL)

> **This is a common cause of "hook error" or "parse failure" scenarios!**

**Symbol note**: In this section, `<BS>` represents a single backslash character (`\`).

| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|----------------|-----------|-------------|
| **Unnecessary JSON preprocessing** | JSON parsing fails after "fix" | Check if input is already valid JSON | Remove unnecessary regex/preprocessing |
| **Backslash double-escaping** | `<BS><BS>path` becomes `<BS><BS><BS>path` | Compare input vs processed output | Trust the source, don't over-process |
| **Regex breaks valid escapes** | Valid `<BS><BS>` becomes invalid `<BS><BS><BS>` | Test with Windows paths containing `<BS>` | Verify regex doesn't match already-escaped chars |

**Real Case Study:**
```
Problem: PowerShell hook script tries to "fix" JSON Windows paths
Result: Valid JSON strings with Windows-style escapes become invalid after "fix"
Example (conceptual): {"cwd":"path<BS><BS>to<BS><BS>file"} becomes {"cwd":"path<BS><BS><BS>to<BS><BS>file"}

Root Cause Analysis:
- Claude Code sends correctly escaped JSON (backslashes already escaped)
- Script uses regex to "fix" unescaped backslashes
- Regex matches already-escaped backslashes and adds another
- Result: Triple-escaped backslashes, which is invalid JSON

Correct Fix:
1. Trust input — Claude Code sends valid JSON
2. Remove unnecessary preprocessing regex
3. Parse JSON directly without modification
```

**JSON Processing Checklist (MANDATORY for hook scripts):**

| Check | Action |
|-------|--------|
| Is input already valid JSON? | Test with `ConvertFrom-Json` directly first |
| Does preprocessing break valid input? | Test with Windows paths like `path<BS>to<BS>file` |
| Is the regex necessary? | Usually not — trust the source |

### Category 6: Platform-Specific Bugs

| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|----------------|-----------|-------------|
| **API unavailable** | Feature fails in specific env | Check platform compatibility | Add feature detection/fallback |
| **Permission denied** | Operation blocked | Check security config | Configure required permissions |
| **Path handling** | File operations fail cross-OS | Check path separators | Use platform-agnostic paths |
| **Local intent falls back to workspace** | User requests local generation but file still lands in workspace | Check relative path resolution in local mode | Specify local default directory for relative paths in local mode |
| **Binary vs text** | File corruption | Check read/write modes | Use correct mode for file type |
| **🔴 uvicorn event loop override** | `asyncio.create_subprocess_exec()` raises `NotImplementedError` on Windows + `--reload` | Check `type(asyncio.get_running_loop()).__name__`, confirm if `SelectorEventLoop` | Add `--loop none` to uvicorn startup params, let Python use default `ProactorEventLoop` |

---

### Category 7: State-Display Consistency Bugs

These bugs occur when the **write path** (how data is stored) and the **read path** (how data is displayed) use inconsistent logic.

| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|----------------|-----------|-------------|
| **Write-read format mismatch** | Operation succeeds but UI doesn't update | Compare storage format vs display query | Align read query to handle all write formats |
| **Derived state inconsistency** | Parent/child selection out of sync | Trace state derivation chain | Derive child state from parent, not vice versa |
| **Implicit vs explicit state** | Selected items show as unselected | Check if read assumes explicit storage | Read must handle implicit state (e.g. inherited from parent) |
| **Partial update** | Some UI elements update, others don't | Trace all consumers of the state | Ensure all consumers respond to state changes |
| **Inconsistent rendering strategy** | Conversation display differs from file preview display | Compare renderer configs/HTML parsing switches | Unify rendering strategy or support common inline tags (e.g. `<br>`) |

**Key Detection Questions:**
1. **What format does the WRITE function store?** (e.g. `{ type: 'folder', id }`)
2. **What format does the READ function expect?** (e.g. `t.type === 'interface'`)
3. **Do they match?** If not, read must be extended to handle write's format.

**Common Scenario (Tree Selection):**
- Write: stores parent selection → `[{ type: 'folder', id: 1 }]`
- Read (buggy): only checks `type === 'interface'` → children show as unselected
- Read (fixed): checks `type === 'interface' || parentIsSelected(id)` → children show as selected

---

### Category 8: Component Integration & Feature Propagation

These bugs occur when shared components are updated or reused, but not all consumers provide the required context or props.

| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|----------------|-----------|-------------|
| **Incomplete prop propagation** | Feature works in one place, fails in others | grep all component usage | Ensure all parents pass required props (or use Context) |
| **Partial feature release** | New behavior only activates in some views | Search for old pattern usage | Global search-replace / centralize logic |
| **Context penetration** | Component needs data unavailable in parent | Check component hierarchy | Lift state or use global Store/Context |
| **Style/theme inconsistency** | Component looks different in different places | Check CSS inheritance/props | Standardize base styles or use design tokens |

**Case Study: Variable Highlighting**
- **Problem**: Added "gray out missing variables" feature to base `Highlight` component.
- **Bug**: Only works in main editor, not in modals/sidebars.
- **Root Cause**: `availableVariables` prop required but not all parent components pass it.
- **Fix**: Create `useAvailableVariables` hook and update all consumers (`BodyEditor`, `ParamEditor`, `HeaderEditor`) to pass data.

---

### Category 9: UI Display Completeness Bugs

These bugs occur when backend returns data fields but frontend doesn't display them, or displays context-inappropriate fields.

| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|----------------|-----------|-------------|
| **Missing display component** | Data exists but UI doesn't show it | Compare API response fields vs UI elements | Add UI component for missing fields |
| **Wrong field priority** | Shows irrelevant data instead of expected | Check field selection logic | Use context-aware field selection |
| **Destructured but unused** | Variable destructured but not rendered | Search for destructured-but-unused variables | Add render logic for all destructured data |
| **Method-agnostic display** | Same logic for all HTTP methods | Check if display considers method type | Use method-aware logic (e.g. POST→body, GET→params) |

**Case Study: Scheduled Task Report**
- **Problem**: Report missing request headers; request body shows wrong data
- **Bug 1**: `request_headers` destructured but no `RequestHeadersBlock` component
- **Bug 2**: `content={request_params || request_body}` always prioritizes params
- **Fix 1**: Add `RequestHeadersBlock` component with table display
- **Fix 2**: Method-aware priority: POST/PUT/PATCH→body first, GET/DELETE→params first

**Display Priority Pattern for HTTP Requests:**
```
Method         Priority Display
----------     ----------------
GET            request_params > request_body
DELETE         request_params > request_body
POST           request_body > request_params
PUT            request_body > request_params
PATCH          request_body > request_params
```

---

### Category 10: 🔴 API Schema Bugs (CRITICAL)

> **These bugs typically manifest as "frontend submitted data but backend didn't update" — root cause is Update/Create Schema missing field definitions**

| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|----------------|-----------|-------------|
| **Update Schema missing field** | Request contains field but response doesn't show update | Compare request params vs response output | Add missing field to `XxxUpdate` Schema |
| **Create Schema missing field** | Some fields ignored during creation | Check if new DB record contains all fields | Add missing field to `XxxCreate` Schema |
| **Field type mismatch** | Data silently converted or lost | Check Schema type definition vs DB type | Align type definitions |
| **Pydantic silently drops fields** | Undefined fields ignored | Check `model_dump(exclude_unset=True)` result | Add field definition to Schema |

**Case Study: Editing embedding model model_name won't update**
```python
# ❌ Wrong: EmbeddingModelUpdate missing model_name and provider_type fields
class EmbeddingModelUpdate(BaseModel):
    name: str | None = None
    base_url: str | None = None
    # ... other fields
    # Missing model_name and provider_type!

# When frontend submits {"model_name": "new_value"}
# Pydantic silently drops model_name field
# Service layer's data.model_dump(exclude_unset=True) doesn't include model_name
# Database won't update!

# ✅ Correct: Add all updatable fields
class EmbeddingModelUpdate(BaseModel):
    name: str | None = None
    provider_type: Literal[...] | None = None  # 🔑 Added
    model_name: str | None = None              # 🔑 Added
    base_url: str | None = None
    # ... other fields
```

**Quick Detection Commands:**
```bash
# Compare Create Schema vs Update Schema field differences
diff <(grep -E "^\s+\w+:" schemas/xxx.py | head -20) \
     <(grep -E "^\s+\w+:" schemas/xxx.py | tail -20)

# Check if Update Schemas are missing common fields
rg "class.*Update.*BaseModel" --glob "*.py" -A 20 | grep -v "model_name\|provider_type"
```

**API Bug Verification Checklist (MANDATORY):**

| Checkpoint | Method | Status |
|-----------|--------|--------|
| Fields in request params | Network panel | ☐ |
| Corresponding fields updated in response | Network panel | ☐ |
| Update Schema includes the field | Code review | ☐ |
| Service layer processes the field | Code review | ☐ |

---

### Category 11: 🔴 ORM/SQLAlchemy Bugs (CRITICAL)

> **These bugs typically surface after deployment, caused by database differences between dev/test and production environments**

| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|----------------|-----------|-------------|
| **Enum native_enum missing** | `LookupError: 'value' is not among the defined enum values` | Check if `Enum()` uses `values_callable` but lacks `native_enum=False` | Add `native_enum=False` parameter |
| **SQL dialect incompatibility** | `ProgrammingError: syntax error` (only on specific DB) | Check raw SQL for `CAST AS TEXT`/`ILIKE`/`::type` | Use SQLAlchemy abstractions or `CAST AS CHAR` |
| **Foreign key constraint failure** | `IntegrityError: foreign key constraint fails` | Check handling after referenced row deletion | Set `ondelete="SET NULL"` + `nullable=True` |
| **Cached old code** | Code is fixed but error persists | Check `__pycache__/*.pyc` file timestamps | Delete `.pyc` files and restart service |

**Case Study 1: Enum Definition Issue**
```python
# ❌ Wrong: values_callable without native_enum=False
engine_type = mapped_column(
    Enum(KBEngineType, values_callable=lambda x: [e.value for e in x])
)
# MySQL stores 'LANGCHAIN', but values_callable expects 'langchain'
# Causes LookupError during query

# ✅ Correct: Add native_enum=False
engine_type = mapped_column(
    Enum(KBEngineType, 
         values_callable=lambda x: [e.value for e in x],
         native_enum=False)  # 🔑 Key
)
```

**Case Study 2: SQL Dialect Incompatibility**
```sql
-- ❌ PostgreSQL syntax, MySQL doesn't support
SELECT CAST(user_id AS TEXT) FROM audit_logs

-- ✅ MySQL-compatible syntax
SELECT CAST(user_id AS CHAR) FROM audit_logs
```

**Case Study 3: Foreign Key Constraint Design**
```python
# ❌ Wrong: Using potentially invalid user_id when auth fails
audit_log = AuditLog(user_id=request.state.user_id)  # User may be deleted

# ✅ Correct: Explicitly set to None, avoid FK constraint
audit_log = AuditLog(
    user_id=None,  # Don't use potentially invalid ID when auth fails
    details={"user_id_raw": request.state.user_id}  # Preserve for debugging
)
```

**Quick Detection Commands:**
```bash
# Detect enums missing native_enum=False
rg "values_callable" --glob "*.py" -A 3 | grep -v "native_enum=False"

# Detect MySQL-incompatible SQL
rg "CAST\(.*AS TEXT\)|ILIKE|::text|::varchar" --glob "*.py"

# Detect foreign keys missing ondelete
rg "ForeignKey\(" --glob "*.py" | grep -v "ondelete"

# Detect pyc cache
find . -name "*.pyc" -newer source_file.py
```

---

## High-Frequency Root Causes (Top 18)

1. **Unverified assumptions**: Assuming API/feature works without checking docs
2. **Incomplete status check**: Only checking HTTP status, not business status
3. **Missing edge case handling**: Not considering empty/null/boundary input
4. **Stale closure/state**: Capturing old values in callbacks/effects
5. **Missing cleanup**: Resources not released on error paths
6. **Environment differences**: Dev/prod config mismatch
7. **Type misunderstanding**: Wrong assumptions about data types
8. **Async ordering**: Assuming async operations execute sequentially
9. **Cache invalidation**: Serving stale cached data
10. **Error swallowing**: Catching errors but not surfacing them
11. **State-display format mismatch**: Write stores X, read expects Y
12. **Incomplete prop propagation**: Updated base component but missed some consumers
13. **Incomplete UI display**: Backend returns fields but frontend doesn't render them
14. **ORM enum mapping error**: `values_callable` missing `native_enum=False`
15. **SQL dialect incompatibility**: Using DB-specific syntax like `CAST AS TEXT`
16. **Foreign key constraint not considering deletion**: Missing `ondelete` policy
17. **🔴 Update Schema field omission**: Pydantic silently drops undefined fields, causing updates to fail
18. **🔴 uvicorn event loop override**: uvicorn 0.36+ on Windows `--reload` explicitly selects SelectorEventLoop, breaking asyncio subprocess

---

## Universal Verification Checklist

Before marking any bug as fixed:

### Core Checks

- [ ] **Original scenario**: Bug no longer reproduces with exact same steps
- [ ] **Related features**: Adjacent features still work
- [ ] **Error paths**: Error cases handled gracefully
- [ ] **Console/logs**: No new errors or warnings
- [ ] **Build/lint**: Code passes all static checks

### Edge Case Checks

- [ ] **Empty input**: Handles empty/null/undefined
- [ ] **Boundary values**: Handles min/max/zero values
- [ ] **Concurrent access**: No race conditions introduced
- [ ] **Resource cleanup**: No leaks on any exit path

### Regression Checks

- [ ] **Existing tests**: All tests still pass
- [ ] **New tests**: Added test for bug scenario
- [ ] **Similar patterns**: Checked for same bug elsewhere (global search)
- [ ] **Prop consistency**: Verified all consumers of modified components

---

## Pattern Extraction Guide

When you have 5-10 bug records in your project `bugRecord.md`, extract common patterns:

### Step 1: Identify Recurring Themes

Group bugs by:
- Root cause type (input handling, state, API, etc.)
- Affected component/module
- Symptom similarity

### Step 2: Abstract to Universal Patterns

Convert project-specific details to universal patterns:

| Project-Specific | Universal Pattern |
|-----------------|------------------|
| "Excel column name ${keywords}" | "Wrapper syntax in user input" |
| "API returns code: -1" | "Business status code in response body" |
| "React state not updating" | "Stale closure in async callback" |

### Step 3: Document in This Guide

Add new patterns to the appropriate category table above:
- Pattern name
- Typical symptom
- Detection method
- Fix strategy

### Step 4: Update Verification Checklist

If a pattern reveals new verification needs, add them to the checklist.

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | Better Approach |
|-------------|-------------|-----------------|
| **Fix the symptom** | Root cause remains, bug will recur | Trace to true root cause |
| **Large-scale refactor** | High regression risk | Minimal surgical fix |
| **Not verifying** | Bug may not be fixed | Always test before declaring fixed |
| **Silent fix** | Lost learning opportunity | Document for future reference |
| **Assumption-based fix** | May introduce new bugs | Verify assumptions first |
| **Partial fix** | Similar bugs still in codebase | Do global search and pattern match |

---

## Quick Reference

### When Bug Recurs After "Fix"

1. Re-read original root cause analysis
2. Check if fix addresses actual root cause
3. Verify fix was applied to correct code path
4. Consider if there are multiple entry points

### When Similar Bugs Appear

1. Check if it's the same pattern as previous bug
2. Look for systematic fix (fix all instances, not just one)
3. Update this guide if it's a new pattern

### When Uncertain About Root Cause

1. Add more logging/tracing
2. Reproduce in debugger
3. Compare working vs broken scenarios
4. Bisect to find the change that introduced the issue
