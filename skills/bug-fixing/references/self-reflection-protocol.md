# Self-Reflection & Evolution Protocol (修复反思与自我进化)

> **Purpose**: After every bug fix, the AI MUST reflect on its own fixing process,
> identify biases/blind spots, and evolve its debugging approach.
> This is NOT just "record what happened" — it's "learn HOW to be better."

---

## Why This Protocol Exists

| Problem | Symptom | This Protocol Fixes |
|---------|---------|-------------------|
| Same type of mistake repeats | AI keeps introducing similar regressions | Pattern recognition of own errors |
| No learning from past fixes | Each fix starts from zero | Accumulated debugging wisdom |
| Blind spots persist | AI consistently misses certain impacts | Explicit blind spot tracking |
| Fix quality doesn't improve over time | Same ratio of fixes cause regressions | Continuous improvement loop |

---

## Mandatory Reflection (After Every Fix)

### Phase 6.5: Self-Reflection (修复反思)

Execute after Phase 6 (Knowledge Deposit) and BEFORE declaring the fix complete.

```markdown
## 🪞 Phase 6.5: Self-Reflection

### 1. Fix Quality Score
Rate your own fix on these dimensions:

| Dimension | Score (1-5) | Evidence |
|-----------|------------|----------|
| **First-time correctness** | [1-5] | Did the fix work on first attempt? |
| **Scope accuracy** | [1-5] | Did I find all affected areas? |
| **Minimal change** | [1-5] | Was the change as small as possible? |
| **Side effect prediction** | [1-5] | Did I predict all side effects? |
| **Root cause depth** | [1-5] | Did I fix the root cause, not symptom? |
| **Total** | [/25] | |

### 2. What Went Wrong (If Anything)

| Issue | What Happened | Why I Missed It | How to Prevent Next Time |
|-------|--------------|-----------------|--------------------------|
| [issue] | [description] | [blind spot/bias] | [concrete action] |

### 3. Debugging Efficiency

| Metric | Value | Notes |
|--------|-------|-------|
| Hypotheses generated | [N] | |
| Hypotheses tested before finding root cause | [N] | |
| False starts / wrong paths | [N] | [list them] |
| Fix attempts before success | [N] | |
| Regressions introduced during fix | [N] | |

### 4. Pattern Recognition

- [ ] Is this bug similar to a previous bug I've fixed?
  - If yes: Did I apply lessons from last time? Why/why not?
- [ ] Did I introduce any new bugs during this fix?
  - If yes: What type? Add to my blind spot list.
- [ ] Was there a simpler fix I missed?
  - If yes: Why did I go with the complex approach?
```

---

## Blind Spot Tracker (盲点追踪器)

Maintain a running list of your known blind spots in `references/ai-blind-spots.md`:

```markdown
## AI Blind Spot Registry

### Active Blind Spots (Must Check Every Fix)

| ID | Blind Spot | First Seen | Times Repeated | Mitigation Check |
|----|-----------|------------|----------------|------------------|
| BS-001 | [description] | [date] | [count] | [what to check] |
| BS-002 | [description] | [date] | [count] | [what to check] |

### Retired Blind Spots (Consistently Avoided)

| ID | Blind Spot | Retired Date | Reason |
|----|-----------|-------------|--------|
| BS-XXX | [description] | [date] | Successfully avoided for 5+ fixes |
```

### Common AI Blind Spots (Seed List)

| Category | Blind Spot | Check |
|----------|-----------|-------|
| **Scope** | Forgetting to check indirect callers | Always run `rg` for re-exports |
| **Scope** | Missing test file updates | Always search `*.test.*` |
| **State** | Not considering race conditions | Ask "can this be called concurrently?" |
| **State** | Ignoring initialization order | Check component/module load order |
| **API** | Assuming response format | Verify actual response shape |
| **API** | Not checking error paths | Test what happens on 4xx/5xx |
| **Types** | Trusting type assertions | Verify runtime values match types |
| **Config** | Forgetting environment differences | Check all env configs |
| **Cache** | Not invalidating after mutation | Check cache strategy |
| **UI** | Not testing different screen sizes | Check responsive behavior |

---

## Evolution Triggers (进化触发器)

### Automatic Skill Evolution

When certain patterns are detected, the skill MUST evolve:

| Trigger | Condition | Evolution Action |
|---------|-----------|------------------|
| **Repeated regression** | Same type of regression 2+ times | Add to Iron Rules |
| **Blind spot hit** | Known blind spot not checked | Strengthen pre-fix checklist |
| **False root cause** | Root cause was wrong on first attempt | Add diagnostic technique |
| **Scope miss** | Consumer missed in analysis | Add consumer type to scope protocol |
| **Fix cascade** | Fix required 3+ iterations | Add pre-fix prediction step |

### Evolution Process

```
Trigger Detected
    ↓
Document in Reflection (Phase 6.5)
    ↓
Identify Pattern (Is this a one-off or recurring?)
    ↓
If Recurring (2+ times):
    ├── Update relevant reference file
    ├── Add to blind spot tracker
    └── Consider adding new Iron Rule
    ↓
Validate (Run skill validation)
```

---

## Regression Autopsy (回归尸检)

When a fix introduces a regression, perform a detailed autopsy:

```markdown
## 🔬 Regression Autopsy

### The Regression
- **Original Bug**: [what was being fixed]
- **New Bug Introduced**: [what broke]
- **Discovered By**: [code review / testing / user]

### Root Cause of Regression
- **What changed**: [the specific line/logic that caused regression]
- **Why it broke**: [the mechanism]
- **Why I didn't predict it**: [the blind spot]

### Classification
| Category | Match? |
|----------|--------|
| Missed consumer | ☐ |
| API contract violation | ☐ |
| Edge case not tested | ☐ |
| Race condition introduced | ☐ |
| State management error | ☐ |
| Type mismatch | ☐ |
| Config/environment issue | ☐ |
| Other: ___ | ☐ |

### Prevention Measures
1. **Immediate**: [what to add to checklist for this type]
2. **Structural**: [what process change prevents this class of errors]
3. **Tooling**: [what automated check could catch this]

### Skill Update Required?
- [ ] Update blind spot tracker (references/ai-blind-spots.md)
- [ ] Update pre-fix impact prediction protocol
- [ ] Update scope accuracy protocol
- [ ] Update final checklist
- [ ] New iron rule needed?
```

---

## Periodic Self-Assessment (定期自评)

After every 5 bug fixes, perform a meta-review:

```markdown
## 📊 Periodic Self-Assessment (Every 5 Fixes)

### Fix Quality Trend
| Fix # | Bug | Quality Score (/25) | Regressions | First-time Success? |
|-------|-----|--------------------:|:-----------:|:-------------------:|
| 1 | [bug] | [score] | [Y/N] | [Y/N] |
| 2 | [bug] | [score] | [Y/N] | [Y/N] |
| ... | ... | ... | ... | ... |

### Trend Analysis
- Quality improving? [Yes/No/Stable]
- Most common weakness: [dimension]
- Most improved area: [dimension]

### Top 3 Lessons from This Period
1. [lesson]
2. [lesson]
3. [lesson]

### Action Items for Next Period
1. [specific improvement to focus on]
2. [blind spot to watch for]
```

---

## Integration with Main Workflow

```
Phase 6 (Knowledge Deposit) → Phase 6.5 (Self-Reflection) → Done
                                     ↓
                              If regression found:
                              → Regression Autopsy
                              → Update Blind Spot Tracker
                              → Consider Skill Evolution
```

**This protocol is NOT optional.** Every fix must include at minimum:
1. Fix Quality Score (5 dimensions)
2. "What Went Wrong" analysis (even if empty)
3. Pattern Recognition check
