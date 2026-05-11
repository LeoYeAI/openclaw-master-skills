# Pre-Fix Impact Prediction Protocol (修复前副作用预测)

> **Purpose**: Force the AI to predict ALL possible side effects BEFORE writing any fix code.
> This is the #1 defense against "fixing one bug, creating another."

---

## Why This Protocol Exists

| Problem | Root Cause | This Protocol Prevents |
|---------|-----------|----------------------|
| Fix breaks unrelated feature | Didn't anticipate shared dependency | Forced dependency analysis |
| Fix changes API contract | Didn't check consumers | Forced consumer impact review |
| Fix creates edge case bug | Didn't think about boundaries | Forced edge case prediction |
| Fix introduces race condition | Didn't consider async interactions | Forced concurrency review |

---

## Mandatory Steps (Before Writing Fix Code)

### Step 1: Change Blueprint (修改蓝图)

Document exactly what you plan to change BEFORE touching any code:

```markdown
## 📐 Change Blueprint

### Planned Changes
| # | File | Line(s) | Current Code | Planned Change | Reason |
|---|------|---------|-------------|----------------|--------|
| 1 | [file] | [lines] | [what's there now] | [what you'll change to] | [why] |

### Change Type Assessment
- [ ] Logic change (conditions, calculations)
- [ ] Data flow change (inputs, outputs, transformations)
- [ ] State change (lifecycle, transitions)
- [ ] API/Interface change (signatures, contracts)
- [ ] Configuration change (env, config files)
- [ ] Dependency change (imports, packages)
```

### Step 2: Impact Ripple Analysis (影响涟漪分析)

Think of your change as a stone dropped in water — trace the ripples:

```
Layer 0: The changed code itself
    ↓
Layer 1: Direct callers/consumers of the changed code
    ↓
Layer 2: Callers of Layer 1 (indirect impact)
    ↓
Layer 3: Cross-module/cross-service impact
    ↓
Layer 4: User-facing behavior changes
```

**Template:**

```markdown
## 🌊 Impact Ripple Analysis

### Layer 0: Direct Change
- What: [description of the change]
- Confidence: [High/Medium/Low]

### Layer 1: Direct Consumers
| Consumer | How It Uses Changed Code | Predicted Impact | Risk |
|----------|------------------------|------------------|------|
| [file:function] | [usage pattern] | [what might break] | [H/M/L] |

### Layer 2: Indirect Consumers
| Consumer | Via Which L1 Consumer | Predicted Impact | Risk |
|----------|---------------------|------------------|------|
| [file:function] | [L1 consumer] | [what might break] | [H/M/L] |

### Layer 3-4: Cross-Module / User-Facing
| Impact | Description | Risk |
|--------|-------------|------|
| [module/feature] | [predicted impact] | [H/M/L] |
```

### Step 3: Side Effect Prediction (副作用预测)

Explicitly list what COULD go wrong:

```markdown
## ⚠️ Side Effect Predictions

| # | Predicted Side Effect | Probability | Severity | Mitigation |
|---|----------------------|-------------|----------|------------|
| 1 | [what could break] | [H/M/L] | [P0-P3] | [how to verify/prevent] |
| 2 | ... | ... | ... | ... |

### Edge Cases to Verify After Fix
| # | Edge Case | Test Method | Expected Result |
|---|-----------|-------------|-----------------|
| 1 | [null/empty input] | [how to test] | [expected behavior] |
| 2 | [concurrent access] | [how to test] | [expected behavior] |
| 3 | [boundary values] | [how to test] | [expected behavior] |
```

### Step 4: Go/No-Go Decision (执行决策)

```markdown
## ✅ Go/No-Go Decision

| Criteria | Status | Notes |
|----------|--------|-------|
| All L1 consumers identified | ☐ | |
| No High-Risk side effects without mitigation | ☐ | |
| Edge cases have test plan | ☐ | |
| Change is minimal (≤20 LOC ideal, ≤50 max) | ☐ | |
| No API contract breaking changes | ☐ | |

**Decision**: [ ] ✅ GO — Proceed with fix | [ ] ⛔ STOP — Need to adjust approach
```

---

## Quick Version (for Simple Bugs)

For bugs where the fix is ≤5 LOC and touches only 1 file:

```markdown
## Quick Impact Check
- **Change**: [one-line description]
- **Direct callers**: [list or "none — local function"]
- **Could break**: [prediction or "low risk — isolated change"]
- **Edge cases**: [list 1-2 or "none — straightforward logic fix"]
- **Decision**: ✅ GO
```

---

## Red Flags (Immediate STOP)

If any of these are true, STOP and escalate:

| Red Flag | Why | Action |
|----------|-----|--------|
| Fix requires changing function signature | Breaks all callers | Use scope-accuracy-protocol.md |
| Fix touches shared utility/helper | Many unknown consumers | Full consumer enumeration |
| Fix changes data schema/format | Data corruption risk | Requires migration plan |
| Fix modifies error handling | May swallow real errors | Verify error propagation |
| Fix adds new dependency | Supply chain risk | Justify necessity |
| More than 3 files need changes | Scope creep | Consider splitting |

---

## Integration with Main Workflow

This protocol is **Phase 3.5** in the main workflow:

```
Phase 3 (Scope Discovery) → Phase 3.5 (Impact Prediction) → Phase 4 (Fix)
```

The output from this protocol directly feeds into:
- **Phase 4**: Fix implementation (only touch what's in the Blueprint)
- **Phase 5**: Verification (verify each predicted side effect didn't occur)
- **Phase 5**: Code Review (reviewer checks against predictions)
