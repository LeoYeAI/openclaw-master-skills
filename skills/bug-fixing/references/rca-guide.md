# Root Cause Analysis Guide

> Techniques for identifying the true source of a bug, not just the symptoms.

## Table of Contents

- [Root Cause Confirmation Gate](#root-cause-confirmation-gate)
- [Hypothesis Ladder](#hypothesis-ladder)
- [Evidence Bundle](#evidence-bundle)
- [RCA Principles](#rca-principles)
- [RCA Techniques](#rca-techniques)
  - [Five Whys](#1-five-whys)
  - [Fishbone Diagram (Ishikawa)](#2-fishbone-diagram-ishikawa)
  - [Timeline Analysis](#3-timeline-analysis)
  - [Fault Tree Analysis](#4-fault-tree-analysis)
  - [Change Analysis](#5-change-analysis)
  - [Git Bisect](#6-git-bisect)
- [Code Path Tracing](#code-path-tracing)
- [Root Cause Categories](#root-cause-categories)
- [System-Level RCA](#system-level-rca)
- [RCA Report Template](#rca-report-template)

Techniques for identifying the true source of a bug, not just the symptoms.

---

## Root Cause Confirmation Gate

> **⛔ Root cause is only "confirmed" when ALL four conditions are met:**

| Condition | Definition | Verification |
|-----------|-----------|-------------|
| **Reproducible** | Can reproduce symptom in controlled scenario | Document repro steps + evidence |
| **Causal** | Minimal change targeting hypothesized root cause makes bug disappear | Show fix + result |
| **Reversible** | Reverting that minimal change makes bug reappear | Show revert + result |
| **Mechanistic** | Can explain the specific code path / state transition / contract mismatch | Point to code + explain why |

**If any condition is not met, you only have a hypothesis, not a confirmed root cause.**

---

## Hypothesis Ladder

> **Before diving into Five Whys, list 3-5 candidate hypotheses and systematically test them.**

### Template

```markdown
## Hypothesis Ladder

| # | Hypothesis | Likelihood | Confirmation Test | Rejection Test | Status |
|---|-----------|-----------|-------------------|----------------|--------|
| 1 | [description] | High/Med/Low | [how to prove it's this] | [how to prove it's NOT this] | ☐ |
| 2 | [description] | High/Med/Low | [confirmation test] | [rejection test] | ☐ |
| 3 | [description] | High/Med/Low | [confirmation test] | [rejection test] | ☐ |
```

### Rules

1. **Sort by likelihood** (most likely first)
2. **Each hypothesis must be falsifiable** (can be proven wrong)
3. **Run rejection tests first** (cheaper to eliminate)
4. **Move to next hypothesis once current is rejected** (don't cling to first guess)

### Example

```markdown
## Hypothesis Ladder: "Element not found in browser automation"

| # | Hypothesis | Likelihood | Confirmation Test | Rejection Test | Status |
|---|-----------|-----------|-------------------|----------------|--------|
| 1 | Session ID routing wrong | High | Logs show sessionId mismatch | Logs show sessionId matches | ❌ Rejected |
| 2 | DOM not ready (timing issue) | High | Works after adding wait | Element exists immediately | ✅ Confirmed |
| 3 | Selector typo | Med | Selector doesn't match in DevTools | Selector matches in DevTools | ❌ Rejected |
| 4 | Element in iframe | Med | Element is inside iframe | Element is in main frame | - |
```

---

## Evidence Bundle

> **Every RCA must collect a standardized evidence bundle. Full template in `evidence-bundle-template.md`.**

### Quick Checklist

- [ ] **Trigger conditions**: inputs, environment, timing
- [ ] **Observable output**: errors, logs, screenshots, network
- [ ] **Correlation IDs**: requestId, sessionId, actionId
- [ ] **State snapshot**: URL, config, version

### Why Evidence Matters

| Without Evidence | With Evidence |
|-----------------|--------------|
| "I think it's X" | "Logs show X happened at T1" |
| "Maybe the session is wrong" | "Frontend sessionId=A, backend sessionId=B" |
| "Might be a timing issue" | "Element appears at T+500ms, action executes at T+100ms" |

---

## RCA Principles

1. **Don't fix symptoms** - A fix that only addresses symptoms will let the bug return
2. **Keep asking "why"** - Dig deeper until you find the fundamental cause
3. **Verify the cause** - Confirm root cause by proving the fix prevents the bug
4. **Look for patterns** - Similar bugs may have the same root cause
5. **Document for learning** - RCA helps prevent future similar bugs

---

## RCA Techniques

### 1. Five Whys

Start with the problem and ask "why" five times:

```markdown
**Problem**: Users receive duplicate emails

**Why 1**: Why do users receive duplicate emails?
→ Because the email service is called twice.

**Why 2**: Why is the email service called twice?
→ Because the submit handler fires twice.

**Why 3**: Why does the submit handler fire twice?
→ Because the button click event bubbles and triggers twice.

**Why 4**: Why does the event bubble and trigger twice?
→ Because there's no event.stopPropagation() or debounce.

**Why 5**: Why is there no duplicate submission prevention?
→ Because the form component was written without considering rapid clicks.

**Root Cause**: Form component lacks duplicate submission prevention.
```

### 2. Fishbone Diagram (Ishikawa)

Categorize potential causes:

```
                    ┌─── People ──────┐
                    │ - Insufficient  │
                    │   training      │
                    │ - Human error   │
                    │                 │
┌─── Process ──────┐│                 │┌─── Technology ───┐
│ - Missing step   ││                 ││ - System bug     │
│ - Wrong order    ││                 ││ - Integration    │
│ - No validation  ││     [BUG]      ││   issue          │
└──────────────────┘│                 │└──────────────────┘
                    │                 │
┌─── Environment ──┐│                 │┌─── Data ─────────┐
│ - Config diff    ││                 ││ - Invalid input  │
│ - Network issues ││                 ││ - Data corruption│
│ - Resource limits│└─────────────────┘│ - Missing data   │
└──────────────────┘                   └──────────────────┘
```

### 3. Timeline Analysis

For intermittent or timing-related bugs:

```markdown
## Timeline Analysis

| Time | Event | System State | Notes |
|------|-------|-------------|-------|
| 00:00 | User clicks submit | Form data valid | |
| 00:01 | API call initiated | Loading state | |
| 00:02 | User clicks submit again | Already loading | No guard! |
| 00:03 | First API call completes | Success | |
| 00:04 | Second API call completes | Duplicate! | |

**Root Cause**: No loading state check before submission
```

### 4. Fault Tree Analysis

Work backwards from the failure:

```
                    [Duplicate Emails]
                         │
            ┌────────────┴────────────┐
            │                         │
   [Email sent twice]           [Two records created]
            │                         │
   ┌────────┴────────┐               │
   │                 │               │
[Duplicate API call] [Retry logic]  [Race condition]
   │
   │
[Button not debounced]  ← Root Cause
```

### 5. Change Analysis

Compare working vs broken state:

```markdown
## Change Analysis

| Aspect | Working State | Broken State | Changed? |
|--------|-------------|-------------|----------|
| Code version | v1.2.3 | v1.2.4 | Yes ✓ |
| Config | prod.yaml | prod.yaml | No |
| Database | schema v42 | schema v42 | No |
| Dependencies | package.json | package.json | No |
| Environment | AWS us-east-1 | AWS us-east-1 | No |

**Focus investigation**: Code changes in v1.2.4

**Changed files**:
- src/services/email.ts (modified)
- src/components/Form.tsx (modified) ← Likely culprit

**Root Cause**: Form.tsx change removed debounce logic
```

### 6. Git Bisect

**Best for**: Regression bugs where you know "it used to work"

When a recent change broke functionality, use bisect to find the culprit commit:

```bash
# Start bisect session
git bisect start

# Mark current commit as broken
git bisect bad HEAD

# Mark last known good version
git bisect good v1.2.3   # or commit hash

# Git checks out a middle commit - test manually
# Then mark the result:
git bisect good   # if this commit works
git bisect bad    # if this commit is broken

# Repeat until Git identifies the first bad commit
# Output: "abc1234 is the first bad commit"

# End session and return to original state
git bisect reset
```

**Automated bisect** (with test script):

```bash
# Automatically run tests on each commit
git bisect start HEAD v1.2.3
git bisect run npm test   # or any command returning 0=good, 1=bad
```

**When to use Git Bisect**:

| Scenario | Use Bisect? |
|----------|-------------|
| "It worked last week" | ✅ Yes |
| "It never worked" | ❌ No |
| Many commits between good/bad | ✅ Yes (efficient) |
| Only 2-3 commits | ❌ No (check manually) |
| Can't reproduce consistently | ❌ No (need consistent test) |

---

## Code Path Tracing

### Step 1: Identify Entry Point

Where does the bug start?

```typescript
// Error message: "Cannot read property 'name' of undefined"
// Stack trace points to:
src/components/UserProfile.tsx:23
  const name = user.name; // Error here
```

### Step 2: Trace Data Flow

Trace data from source to error:

```
Entry: UserProfile.tsx:23 (user.name)
   ↑
   │ user comes from props
   │
Source: UserProfilePage.tsx:15
   ↑
   │ user comes from useUser hook
   │
Source: hooks/useUser.ts:8
   ↑
   │ user comes from API response
   │
Source: api/users.ts:12
   ↑
   │ API returns null when user doesn't exist
   │
Root Cause: No handling for API returning null
```

### Step 3: Document the Path

```markdown
## Code Path

### Execution Flow
1. UserProfilePage renders
   └── Calls useUser(userId)
       └── Fetches from /api/users/{id}
           └── API returns null (user deleted)
               └── useUser returns null
                   └── UserProfile receives user=null
                       └── Accesses user.name
                           └── TypeError!

### Missing Checks
| Location | Should Check | Current |
|----------|-------------|---------|
| API response | User exists | No ❌ |
| useUser hook | null handling | No ❌ |
| UserProfile | user prop | No ❌ |

### Fix Location Options
1. API: Return 404 (proper REST) ← Best
2. Hook: Return loading/error state
3. Component: null check before render
```

---

## Root Cause Categories

### Logic Errors

```typescript
// Bug: Off-by-one error
for (let i = 0; i <= array.length; i++) { // <= should be <
  process(array[i]); // Last iteration is undefined
}

// Bug: Wrong operator
if (user.role = 'admin') { // = should be ===
  // Always true, assigns 'admin' to role
}

// Bug: Wrong condition
if (items.length > 0 || items.length < 10) { // || should be &&
  // Always true if length > 0
}
```

### Async/Timing Errors

```typescript
// Bug: Race condition
let data;
async function loadData() {
  data = await fetchData();
}
loadData();
console.log(data); // undefined - loadData hasn't completed

// Bug: Stale closure
useEffect(() => {
  const interval = setInterval(() => {
    setCount(count + 1); // count is stale
  }, 1000);
}, []); // Missing count dependency

// Bug: Unhandled Promise rejection
async function save() {
  await api.save(data); // No try/catch
}
```

### State Errors

```typescript
// Bug: Direct state mutation
const [items, setItems] = useState([]);
function addItem(item) {
  items.push(item); // Direct mutation!
  setItems(items);  // Same reference, won't re-render
}

// Bug: Invalid state transition
if (status === 'pending') {
  setStatus('complete');
} else if (status === 'processing') {
  setStatus('complete'); // Can we go from processing to complete?
}
```

### Data Errors

```typescript
// Bug: Unexpected data type
function formatDate(date) {
  return date.toISOString(); // Fails if date is a string
}

// Bug: Missing data validation
function createUser(data) {
  return { email: data.email.toLowerCase() }; // Fails if email is undefined
}

// Bug: Data structure assumption
function getFirstItem(response) {
  return response.data.items[0].name; // Too many assumptions!
}
```

### Integration Errors

```typescript
// Bug: API contract mismatch
// Frontend expects: { user: { name: string } }
// Backend returns: { data: { user: { name: string } } }
const name = response.user.name; // undefined

// Bug: Version mismatch
// Library v1: axios.get().then(res => res.data)
// Library v2: axios.get().then(res => res.body)

// Bug: Environment difference
const apiUrl = process.env.API_URL; // undefined in production
```

---

## System-Level RCA

> **For multi-surface, cross-layer, or stateful bugs, use system-level RCA.**

Full guide in `system-rca-track.md`.

### When to Use

- Browser automation bugs
- Streaming/SSE/WebSocket bugs
- Async task bugs
- Microservice integration bugs
- Any bug spanning multiple processes or layers

### Quick Summary

1. **Draw end-to-end chain** (all participants)
2. **Define evidence for each edge** (what proves handshake is correct)
3. **Insert probes before modifying behavior** (logs, return fields)
4. **Narrow the search space** (find last correct edge, first broken edge)
5. **Root cause is between those two edges**

---

## RCA Report Template

```markdown
# Root Cause Analysis Report

## Bug Summary
| Field | Value |
|-------|-------|
| Bug ID | BUG-XXX |
| Summary | [one sentence] |
| Severity | Critical/High/Medium/Low |
| Discovery Date | [date] |
| Fix Date | [date] |

## Problem Description
[Detailed description of the bug]

## Impact
- Affected users: [count/scope]
- Affected features: [list]
- Duration: [how long the issue existed]

## Root Cause

### Five Whys Analysis
[Complete Five Whys]

### Root Cause Statement
**Category**: [Logic/Async/State/Data/Integration]

**Description**: [Clear root cause statement]

**Code Location**: 
- File: [path]
- Line: [number]
- Function: [name]

## Fix

### Solution
[Fix description]

### Code Changes
[Diff or description]

### Why This Fix?
[Rationale]

## Verification
- [ ] Bug cannot be reproduced
- [ ] Test added for bug scenario
- [ ] Related features verified

## Prevention

### Immediate Actions
- [Action 1]
- [Action 2]

### Long-term Improvements
- [Improvement 1]
- [Improvement 2]

## Lessons Learned
- [Lesson 1]
- [Lesson 2]

## Related Bugs
- [BUG-XXX] - Similar issue in [component]
```
