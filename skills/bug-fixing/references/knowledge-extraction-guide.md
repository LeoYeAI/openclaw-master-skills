# Knowledge Extraction Guide

> Transform every bug fix experience into reusable knowledge, continuously enriching bug-guide.md.

---

## Why Knowledge Extraction Matters

### Problem: Repeating the Same Mistakes

| Scenario | Consequence |
|----------|------------|
| Same type of bug keeps appearing | Wasted time on repeated investigation |
| Fix experience only in personal memory | Knowledge can't be inherited |
| No standardized fix patterns | Starting from scratch every time |

### Solution: Knowledge Deposit Cycle

```
Bug Fix
    ↓
Pattern Abstraction
    ↓
Update bug-guide.md
    ↓
Query Before Next Fix
    ↓
Quickly Apply Known Solution
    ↓
Faster Fixes, Fewer Pitfalls
```

---

## Phase -1: Knowledge Query (Before Fix)

### Mandatory Query Process

**Before starting any bug fix, MUST execute:**

```markdown
## 📚 Phase -1: Knowledge Base Query

### Step 1: Extract Search Keywords
Extract from user report:
- Symptom keywords: [e.g. page crash, data out of sync, API timeout]
- Error type: [e.g. TypeError, 500 error, render anomaly]
- Tech stack: [e.g. React, FastAPI, PostgreSQL]

### Step 2: Search bug-guide.md
Search in these locations:
1. Common Bug Pattern Library (each Category table)
2. High-Frequency Root Causes
3. Universal Verification Checklist

### Step 3: Record Match Results
| Match Level | Pattern | Relevance |
|-------------|---------|-----------|
| 🟢 High | [Category X: Pattern Name] | [Why it matches] |
| 🟡 Medium | [Category Y: Pattern Name] | [Partially related] |

### Step 4: Decision
- [ ] 🟢 High match: Directly apply known solution
- [ ] 🟡 Medium match: Reference strategy, but verify
- [ ] 🔴 No match: New pattern, full investigation + Phase 6 deposit
```

### Match Decision Matrix

| Match Level | Definition | Action |
|-------------|-----------|--------|
| 🟢 **High match** | Symptom, root cause, and tech stack all match | Directly apply fix strategy, can skip RCA |
| 🟡 **Medium match** | Similar symptom, but different details | Reference strategy, but verify hypotheses |
| 🔴 **No match** | No related pattern found | Full investigation, must update knowledge base after fix |

---

## Phase 6: Knowledge Extraction (After Fix)

### 6.1 Extraction Trigger Conditions

**Must execute knowledge extraction in these cases:**

| Condition | Must Extract |
|-----------|-------------|
| Phase -1 no match | ✅ Required (new pattern) |
| Fix strategy differs from known pattern | ✅ Required (supplement/correction) |
| Discovered new detection method | ✅ Required (enhancement) |
| P0/P1 severe bug | ✅ Required (important experience) |
| Simple bug + existing pattern covers it | ⚪ Optional |

### 6.2 Pattern Abstraction Process

```
Specific Bug
    ↓
┌──────────────────────────────────────────────────────┐
│ Step 1: Identify Pattern Category                    │
│ ─────────────────────────────────────────────────────│
│ Which existing category does this bug belong to?     │
│ - Category 1: Input Handling Bugs                    │
│ - Category 2: Status/State Bugs                     │
│ - Category 3: API Integration Bugs                  │
│ - Category 4: Data Flow Bugs                        │
│ - Category 5: Configuration Bugs                    │
│ - Category 6: Platform-Specific Bugs                │
│ - ...                                               │
│                                                      │
│ If none match → Create new Category                  │
└──────────────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────────────┐
│ Step 2: Generalize Description                       │
│ ─────────────────────────────────────────────────────│
│ Abstract project-specific details to universal lang: │
│                                                      │
│ Project-specific:                                    │
│ "UserService.login() returns null but UI shows ok"   │
│                                                      │
│ Generalized:                                         │
│ "Service returns null but caller doesn't check"      │
└──────────────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────────────┐
│ Step 3: Extract Reusable Elements                    │
│ ─────────────────────────────────────────────────────│
│ - Pattern name: [short, searchable]                  │
│ - Typical symptom: [how user describes it]           │
│ - Detection method: [how to find this bug type]      │
│ - Fix strategy: [universal solution approach]        │
└──────────────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────────────┐
│ Step 4: Format as Table Row                          │
│ ─────────────────────────────────────────────────────│
│ | Pattern | Typical Symptom | Detection | Fix |      │
│ |---------|-----------------|-----------|-----|      │
│ | [name]  | [symptom]       | [detect]  | [fix]  |  │
└──────────────────────────────────────────────────────┘
```

### 6.3 Generalization Rules

| Project-Specific | Generalized |
|-----------------|-------------|
| `UserService.login()` | Service method |
| `React useState` | Frontend state management |
| `FastAPI endpoint` | Backend API endpoint |
| `/api/v1/users` | API endpoint |
| `PostgreSQL query` | Database query |
| Specific error message | Error type (TypeError, 500, etc.) |

### 6.4 Extraction Template

```markdown
## 📝 Phase 6: Knowledge Extraction

### Bug Information
- **Bug ID**: BUG-XXX
- **Date**: YYYY-MM-DD
- **Severity**: P0/P1/P2
- **Tech Stack**: [React, FastAPI, PostgreSQL]

### Original Issue
- **Symptom**: [user-reported problem]
- **Root Cause**: [identified root cause]
- **Fix**: [applied fix method]

### Pattern Abstraction

#### Category Assignment
- **Category**: [existing category name / NEW: new category name]
- **Reason**: [why it belongs to this category]

#### Generalized Description
| Dimension | Project-Specific | Generalized |
|-----------|-----------------|-------------|
| Symptom | [specific description] | [universal description] |
| Detection | [specific method] | [universal method] |
| Fix | [specific approach] | [universal strategy] |

#### Generated Table Row
```
| [pattern name] | [typical symptom] | [detection method] | [fix strategy] |
```

### Keyword Coverage
Ensure these keywords can find this pattern:
- [ ] [keyword1]
- [ ] [keyword2]
- [ ] [keyword3]

### bug-guide.md Update
- **Add Location**: Category X table
- **Add Content**: [the generated table row above]
```

---

## bug-guide.md Update Specifications

### Adding to Existing Category

If the bug belongs to an existing category, add new row at end of corresponding table:

```markdown
### Category 2: Status/State Bugs

| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|-----------------|-----------|--------------|
| **Status mismatch** | UI says success but operation failed | Check both HTTP and business status | Parse full response body |
| **Stale state** | Shows outdated data after updates | Check state invalidation | Refresh state after mutations |
| **NEW PATTERN** | [symptom] | [detection] | [fix] |  ← New row
```

### Creating New Category

If the bug doesn't belong to any existing category:

```markdown
### Category N: [New Category Name] (NEW)

[Brief description of common characteristics of this bug type]

| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|-----------------|-----------|--------------|
| **[pattern name]** | [symptom] | [detection] | [fix] |
```

### Updating High-Frequency Root Causes List

If this root cause is worth adding to the top list:

```markdown
## High-Frequency Root Causes (Top 14)  ← Update number

...
14. **[new root cause]**: [description]  ← New entry
```

---

## Knowledge Quality Standards

### 4 Standards That Must Be Met

| Standard | Check Question | Fail Example | Pass Example |
|----------|---------------|-------------|-------------|
| **Generality** | Would someone on a different project understand? | "UserService's login method" | "Service method return value" |
| **Actionability** | Can someone execute the steps directly? | "Check the code" | "grep 'return null' to search for null returns" |
| **Searchability** | Can it be found with different keywords? | Only one keyword | Contains multiple synonyms |
| **Completeness** | Missing key information? | Only symptom, no fix | Symptom + detection + fix all present |

### Quality Check Checklist

```markdown
## Knowledge Quality Check

### Generality
- [ ] No project-specific class/method names
- [ ] Tech stack agnostic or explicitly labeled
- [ ] Other developers can understand

### Actionability
- [ ] Detection method is specific and executable
- [ ] Fix strategy has clear steps
- [ ] Can be acted on without additional explanation

### Searchability
- [ ] Symptom description includes common expressions
- [ ] Covers possible synonyms
- [ ] Keyword test: searching with 3 different expressions all find it

### Completeness
- [ ] Has typical symptom
- [ ] Has detection method
- [ ] Has fix strategy
- [ ] All 4 columns filled
```

---

## Knowledge Validation

### Search Test

After updating bug-guide.md, verify knowledge can be found:

```markdown
## Search Test

Search with these keywords to verify the newly added pattern can be found:

| Search Term | Found? |
|-------------|--------|
| [description user might use 1] | ✅/❌ |
| [description user might use 2] | ✅/❌ |
| [error type keyword] | ✅/❌ |

If ❌, need to adjust pattern description or add synonyms.
```

### Reuse Test

Assume encountering a similar bug, verify knowledge is useful:

```markdown
## Reuse Test

Hypothetical scenario: [describe a similar hypothetical bug]

Can a solution be found via bug-guide.md?
- [ ] Can find related pattern
- [ ] Pattern description helps understand the problem
- [ ] Fix strategy guides the solution

If any ❌, need to supplement information.
```

---

## FAQ

### Q1: Must all bugs be extracted?

**A**: No. Only these cases require extraction:
- New patterns with no Phase -1 match
- P0/P1 severe bugs
- Newly discovered detection/fix methods

Simple bugs covered by existing patterns can be skipped.

### Q2: What if the pattern is too specific?

**A**: Generalize progressively:

```
Too specific: "React useState doesn't update after useEffect"
↓
Level 1: "State update doesn't refresh component"
↓
Level 2: "State update doesn't trigger expected UI update"
↓
Final: "Stale state" (existing pattern)
```

### Q3: Not sure which category it belongs to?

**A**: Ask yourself:
1. Problem in input handling? → Category 1
2. Problem in state management? → Category 2
3. Problem in API calls? → Category 3
4. Problem in data flow? → Category 4
5. Problem in configuration? → Category 5
6. Platform-specific problem? → Category 6
7. None of the above? → Create new Category

### Q4: How to ensure knowledge gets used?

**A**: The Phase -1 mandatory query mechanism ensures bug-guide.md is queried before every fix.

---

## Checklists

### Phase -1 (Before Fix)
- [ ] Extract search keywords
- [ ] Search bug-guide.md
- [ ] Record match results
- [ ] Decide fix strategy

### Phase 6 (After Fix)
- [ ] Determine if extraction needed
- [ ] Identify pattern category
- [ ] Generalize description
- [ ] Generate table row
- [ ] Update bug-guide.md
- [ ] Quality check
- [ ] Search test

### Continuous Improvement
- [ ] Periodically review bug-guide.md
- [ ] Merge duplicate patterns
- [ ] Update outdated content
- [ ] Supplement missing detection/fix methods

---

## 🔴 Debugging Journal

**Record personal debugging experiences to accelerate future problem-solving.**

### Why a Debugging Journal?

| Benefit | Description |
|---------|------------|
| **Faster identification** | Quickly recall solutions when encountering similar problems |
| **Discover patterns** | Identify types of mistakes you commonly make |
| **Time tracking** | Understand which bug types consume the most time |
| **Skill improvement** | Continuously improve debugging ability through retrospectives |

### Debugging Journal Template

```markdown
## Debugging Journal Entry

**Date**: YYYY-MM-DD
**Bug**: [brief description]
**Time to Fix**: [duration]
**Difficulty**: Easy / Medium / Hard

### Symptoms
[User-reported problem]

### Root Cause
[Root cause]

### Solution
[Solution]

### What Worked
- [Effective debugging methods]

### What Didn't Work
- [Methods tried but ineffective]

### Lesson Learned
[Experience for next time encountering similar problem]

### Tags
#[category] #[technology] #[pattern]
```

### Debugging Journal Example

```markdown
## Debugging Journal Entry

**Date**: 2025-01-19
**Bug**: API returns 500 but frontend shows success
**Time to Fix**: 2 hours
**Difficulty**: Medium

### Symptoms
User clicks save and sees "Saved successfully", but data is not actually persisted

### Root Cause
Frontend only checked HTTP status code 200, didn't check business code in response body

### Solution
Added business code check: `if (response.code !== 0) throw new Error()`

### What Worked
- Viewing Network panel revealed response body has code: -1
- Comparing successful/failed request response differences

### What Didn't Work
- Initially thought it was a backend problem, wasted 30 minutes

### Lesson Learned
API responses must check both HTTP status code and business status code

### Tags
#api #status-check #frontend
```

### Periodic Review

**Weekly/monthly review of debugging journal:**

1. **Track most time-consuming bug types** → Focus learning
2. **Identify recurring patterns** → Add to bug-guide.md
3. **Analyze ineffective attempts** → Avoid repeating next time

---

## 🔴 Proactive Bug Prevention

**Don't just fix bugs — prevent them!**

### Prevention Techniques Overview

| Technique | Tool | Purpose |
|-----------|------|---------|
| **Fuzz Testing** | AFL, libFuzzer | Find boundary condition bugs |
| **Chaos Engineering** | Chaos Monkey, Gremlin | Test system resilience |
| **Load Testing** | k6, Locust | Find performance bugs |
| **Contract Testing** | Pact | Find API integration bugs |

### Fuzz Testing

**Discover boundary condition bugs with random input:**

```bash
# JavaScript (using fast-check)
npm install fast-check
```

```javascript
import fc from 'fast-check';

// Test function doesn't crash on any input
fc.assert(
  fc.property(fc.string(), (input) => {
    const result = myFunction(input);
    return result !== undefined;
  })
);
```

### Chaos Engineering

**Proactively inject faults to test system resilience:**

| Fault Type | Test Purpose |
|-----------|-------------|
| Network latency | Is timeout handling correct |
| Service down | Does degradation strategy work |
| Disk full | Is error handling graceful |
| CPU overload | Is performance degradation smooth |

> Research shows: 68% of organizations using chaos engineering reduced production incidents by 20%+ (Gremlin 2023)

### When to Use Prevention Techniques

| Scenario | Recommended Technique |
|----------|----------------------|
| Before release | Fuzz Testing + Load Testing |
| After major changes | Contract Testing |
| Production environment | Chaos Engineering (cautiously) |
| Continuous integration | All automated tests |
