# Bug Fix Output Templates

> All mandatory output templates for the bug fixing workflow.

---

## 1. Reproduction Steps Template (Phase 1)

```markdown
## Reproduction Steps
1. [specific action step]
2. [...]

## Evidence
- Error message: [full error]
- Logs: [key log lines]
- Screenshot: [if available]
```

---

## 2. Hypothesis Ladder Template (Phase 2.1)

> **⛔ MUST list 3-5 candidate hypotheses first, then verify each. Do NOT just verify the first one and start fixing.**

```markdown
## Hypothesis Ladder

| # | Hypothesis | Likelihood | Confirmation Test | Rejection Test | Status |
|---|-----------|-----------|-------------------|----------------|--------|
| 1 | [hypothesis description] | High/Med/Low | [how to prove it's this cause] | [how to prove it's NOT this cause] | ☐ |
| 2 | [hypothesis description] | High/Med/Low | [confirmation test] | [rejection test] | ☐ |
| 3 | [hypothesis description] | High/Med/Low | [confirmation test] | [rejection test] | ☐ |
```

**Hypothesis Ladder Rules**:
1. Sort by likelihood from high to low
2. Each hypothesis must have a **falsifiable** test (can prove it wrong)
3. Run rejection tests first (lower cost), then confirmation tests
4. Once a hypothesis is rejected, immediately move to the next — don't dwell

---

## 3. Five Whys Template (Phase 2.2)

```markdown
**Problem**: [description]

**Why 1**: Why [symptom]? → Because [...]
**Why 2**: Why [previous answer]? → Because [...]
**Why 3**: Why [previous answer]? → Because [...]
**Why 4**: Why [previous answer]? → Because [...]
**Why 5**: Why [previous answer]? → Because [...]

**Root Cause**: [one-sentence root cause]
**Evidence**: [file:line] [code snippet]
```

---

## 4. Evidence Bundle Template (Phase 2.3)

> **⛔ Must collect the following evidence for every RCA, otherwise root cause is not credible.**

```markdown
## Evidence Bundle

### Trigger Conditions
- Input/params: [...]
- Environment: [OS/browser/Node version/...]
- Timing: [action sequence/time interval/...]

### Observable Output
- Error message: [full error]
- Logs: [key log lines]
- Screenshot/recording: [if available]
- Network request/response: [if available]

### Correlation IDs
- requestId/traceId: [...]
- sessionId: [...]
- actionId: [...]

### Current State Snapshot
- URL/route: [...]
- Config flags: [...]
- Version/build hash: [...]
```

Detailed template: `evidence-bundle-template.md`

---

## 5. Consumer List Template (Phase 3.1)

> **⛔ Before modifying any shared artifact (API/component/utility/config/cache), MUST fill in the consumer list.**

```markdown
## Consumer List

| Consumer | Layer | Entry Point | Contract Used | Risk | Verification Method |
|----------|-------|-------------|---------------|------|---------------------|
| [who uses it] | [frontend/backend/CLI/test] | [file:line] | [call signature/dependent field] | [H/M/L] | [how to verify not affected] |
```

**Consumer Types**:
- **Direct callers**: Directly import/call the modified symbol
- **Indirect dependents**: Depend on modified behavior through an intermediate layer
- **Config consumers**: Read the modified config/env variable
- **Cache consumers**: Depend on modified cache key/TTL/invalidation logic

---

## 6. Contract & Invariant List Template (Phase 3.2)

> **⛔ Must explicitly list modified contracts and invariants that must hold after the fix.**

```markdown
## Contract List

| Contract Type | Description | Before | After | Compatibility |
|---------------|-------------|--------|-------|---------------|
| API signature | [function/method signature] | [old signature] | [new signature] | ✅/⚠️/❌ |
| Return type | [return value structure] | [old structure] | [new structure] | ✅/⚠️/❌ |
| Error codes | [error code semantics] | [old behavior] | [new behavior] | ✅/⚠️/❌ |
| Side effects | [state changes] | [old behavior] | [new behavior] | ✅/⚠️/❌ |

## Invariant List

| Invariant | Description | Verification Method |
|-----------|-------------|---------------------|
| [INV-1] | [condition that must remain true] | [how to verify] |
| [INV-2] | [condition that must remain true] | [how to verify] |
```

**Common Invariant Types**:
- **API invariants**: Response structure unchanged, error code semantics unchanged
- **State invariants**: State transition paths unchanged (loading→success)
- **Routing invariants**: Session/request routing consistency
- **Cache invariants**: Side-effect operations not cached

---

## 7. Call Site List Template (Phase 3.3)

> **⛔ When modifying shared symbols, MUST enumerate all call sites and classify them.**

```bash
# 1. Find all direct calls
rg -n "symbol_name" . --glob "*.{ts,tsx,py,go,java}"

# 2. Find all indirect references (re-export/alias)
rg -n "export.*symbol_name|import.*symbol_name" . --glob "*.{ts,tsx,py}"
```

```markdown
## Call Site List

| File:Line | Call Type | Classification | Needs Update | Update Content |
|-----------|----------|----------------|--------------|----------------|
| file1.ts:23 | Direct call | Runtime critical | ☐ | [if needed] |
| file2.ts:45 | Indirect call | Runtime critical | ☐ | [if needed] |
| test.ts:100 | Test call | Test only | ☐ | [if needed] |
| dev.ts:50 | Dev tool | Dev only | ☐ | [if needed] |
```

**Classification Rules**:
- **Runtime critical**: Production code path, must verify
- **Test only**: Test code, need to update tests
- **Dev only**: Dev tools/scripts, low priority

---

## 8. Regression Matrix Template (Phase 4.3)

> **⛔ After fixing, MUST define a minimal verification matrix for each consumer.**

```markdown
## Regression Matrix

| Consumer | Normal Flow | Critical Boundary | Verification Status |
|----------|------------|-------------------|---------------------|
| [consumer 1] | [normal flow test] | [boundary condition test] | ☐ |
| [consumer 2] | [normal flow test] | [boundary condition test] | ☐ |
```

**Matrix Rules**:
- Each consumer needs at least 1 normal flow + 1 critical boundary
- Prioritize coverage of "runtime critical" consumers
- At least 1 automated guard at the root cause location (test/assertion/log alert)

---

## 9. Request-Response Consistency Check Template (API Bug)

> **⛔ For CRUD API bugs, MUST compare request params vs response output!**

```markdown
## Request-Response Comparison
- Request URL: PUT /api/v1/xxx/{id}
- Request Body: {"field_a": "new_value", "field_b": 123}
- Response Body: {"field_a": "???", "field_b": ???}  // ← Updated correctly?

## Consistency Check
| Field | Request Value | Response Value | Consistent? |
|-------|--------------|----------------|-------------|
| field_a | "new_value" | ? | ☐ |
| field_b | 123 | ? | ☐ |
```

**⚠️ Lesson learned**: If a field is in the request but not updated in the response, it likely means the **Update Schema is missing that field definition**!

---

## 10. Bug Summary Template (Phase 5)

> **⛔ After fix, MUST output the following format, otherwise the fix is considered incomplete.**

```markdown
## Bug Summary [BUG-XXX]
- **Symptom**: [one-sentence description of user-visible problem]
- **Root Cause**: [one-sentence description of actual cause]
- **Fix**: [one-sentence description of fix]
- **Files Modified**: [file1.py, file2.ts]
- **Time**: [YYYY-MM-DD HH:mm:ss]
- **Severity**: [P0/P1/P2]
```

---

## 11. Bug Record Template (Phase 6)

**Add to project-level `references/bug-records.md`**:

```markdown
### [BUG-XXX] Brief Description
**Date**: YYYY-MM-DD
**Severity**: P0/P1/P2

**Root Cause**:
[1-2 sentences explaining why this bug occurred]

**Fix**:
[How this bug was fixed]

**Files Modified**:
- `path/to/file1.ts`
```
