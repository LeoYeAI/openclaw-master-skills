# Final Checklist (Complete Version)

> **⛔ Before declaring "fix complete", MUST confirm ALL of the following check items.**

---

## Basic Checks (ALL Bugs Must Complete)

| # | Check Item | Verification | Status |
|---|-----------|-------------|--------|
| 1 | Output Bug Summary (standard format) | In response | ☐ |
| 2 | Executed code review | In response | ☐ |
| 3 | Review found no P0/P1/P2 issues | In response | ☐ |
| 4 | Updated **project-level** `references/bug-records.md` | File | ☐ |
| 5 | 🔴 **User confirmed bug is fixed** | **User actual testing** | ☐ |
| 6 | If universal pattern found, updated skill-level `bug-guide.md` | File | ☐ |

---

## 🔴 Root Cause Confirmation Checks (Root Cause Gate)

| # | Check Item | Verification | Status |
|---|-----------|-------------|--------|
| R1 | Listed 3-5 candidate hypotheses | Hypothesis ladder table | ☐ |
| R2 | Each hypothesis has confirmation + rejection tests | Hypothesis ladder table | ☐ |
| R3 | Root cause passes 4 gates (reproducible/causal/reversible/mechanistic) | RCA output | ☐ |
| R4 | Collected evidence bundle (triggers/output/correlation IDs/state snapshot) | Evidence bundle output | ☐ |

---

## 🔴 Pre-Fix Impact Prediction Checks (NEW!)

| # | Check Item | Verification | Status |
|---|-----------|-------------|--------|
| P1 | Output Change Blueprint | In response | ☐ |
| P2 | Completed Impact Ripple Analysis | In response | ☐ |
| P3 | Listed side effect predictions and edge cases | In response | ☐ |
| P4 | Go/No-Go decision passed | In response | ☐ |
| P5 | 🔴 Checked active blind spots in AI Blind Spot Registry | Blind spot list | ☐ |

---

## 🔴 Scope Accuracy Checks (Scope Gate)

| # | Check Item | Verification | Status |
|---|-----------|-------------|--------|
| S1 | Filled consumer list when modifying shared artifacts | Consumer list table | ☐ |
| S2 | Listed modified contracts and invariants | Contract/invariant list | ☐ |
| S3 | Enumerated all call sites and classified them | Call site list | ☐ |
| S4 | Defined regression matrix for each consumer | Regression matrix table | ☐ |

---

## 🔴 Regression Verification Checks (NEW!)

| # | Check Item | Verification | Status |
|---|-----------|-------------|--------|
| V1 | Ran related tests (if any) | Test output | ☐ |
| V2 | Verified side effects against Impact Prediction item by item | Side effect verification table | ☐ |
| V3 | Verified all consumers are not broken | Consumer regression table | ☐ |
| V4 | Lint/Build checks passed | Tool output | ☐ |
| V5 | Zero new test failures | Test comparison | ☐ |

---

## 🔴 Self-Reflection Checks (NEW!)

| # | Check Item | Verification | Status |
|---|-----------|-------------|--------|
| E1 | Output Fix Quality Score (5-dimension rating) | In response | ☐ |
| E2 | Completed "What Went Wrong" analysis | In response | ☐ |
| E3 | Completed Pattern Recognition check | In response | ☐ |
| E4 | If regression occurred, executed Regression Autopsy | In response | ☐ |
| E5 | If new blind spot found, updated `ai-blind-spots.md` | File | ☐ |

---

## 🔴 API Bug Extra Checks (MANDATORY for CRUD API bugs)

| # | Check Item | Verification | Status |
|---|-----------|-------------|--------|
| A | Checked full data flow (Frontend→API→Schema→Service→Database) | In RCA | ☐ |
| B | Checked Update/Create Schema field completeness | Code review | ☐ |
| C | Compared request params vs response output consistency | User testing | ☐ |

---

## 🔴 System-Level Bug Extra Checks (MANDATORY for cross-layer/cross-process bugs)

| # | Check Item | Verification | Status |
|---|-----------|-------------|--------|
| X1 | Drew end-to-end chain | System-level RCA | ☐ |
| X2 | Defined "handshake correct" evidence for each edge | System-level RCA | ☐ |
| X3 | Inserted probes to collect evidence (before modifying behavior) | Logs/return fields | ☐ |

---

## Notes

- Item 4 refers to the **project root** `references/bug-records.md`, not the skill directory
- Item 5 **cannot be satisfied by code review alone**, user must actually test and confirm
- Item 6 is only needed when a reusable pattern is discovered
- 🔴 R1-R4 are Root Cause Confirmation gates, must be met before starting fix
- 🔴 P1-P5 are Impact Prediction gates, must be met before starting coding
- 🔴 S1-S4 are Scope Accuracy gates, must be met before entering verification
- 🔴 V1-V5 are Regression Verification gates, must be met before entering code review
- 🔴 E1-E5 are Self-Reflection gates, must be met before declaring complete
- 🔴 API bugs must complete A/B/C check items
- 🔴 Cross-layer/cross-process bugs must complete X1-X3 check items

**If ANY item is ☐, MUST complete it before declaring done.**

---

## Quick Reference: Gate Conditions

### Root Cause Confirmation Gate

| Gate Condition | Meaning | Verification |
|---------------|---------|-------------|
| **Reproducible** | Can reproduce symptom in controlled scenario | Output repro steps + evidence |
| **Causal** | Minimal change targeting hypothesized root cause makes bug disappear | Output change + result |
| **Reversible** | Reverting that minimal change makes bug reappear | Output revert + result |
| **Mechanistic** | Can point to specific code path / state transition / contract mismatch | Output code location + explanation |

### Scope Accuracy Gate

| Gate Condition | Meaning | Verification |
|---------------|---------|-------------|
| **Consumer List** | All consumers (callers/dependents) listed | Output consumer list table |
| **Contract List** | Modified contracts/interfaces/behaviors listed | Output contract list |
| **Invariant Check** | Must-hold invariants listed | Output invariant list |
| **Call Site Enum** | All call sites enumerated and classified | Output call site table |

### 🆕 Impact Prediction Gate

| Gate Condition | Meaning | Verification |
|---------------|---------|-------------|
| **Change Blueprint** | Precisely define what to change and what NOT to change | Output Change Blueprint |
| **Ripple Analysis** | Analyze impact on L0-L4 | Output Impact Ripple |
| **Blind Spot Check** | Check known AI blind spots | Review ai-blind-spots.md item by item |

### 🆕 Regression Verification Gate

| Gate Condition | Meaning | Verification |
|---------------|---------|-------------|
| **Tests Pass** | Zero new test failures in related tests | Test output comparison |
| **Side Effect Verification** | Predicted side effects did not occur | Item-by-item verification |
| **Consumers Intact** | All consumer functions work normally | Regression verification table |

### 🆕 Self-Reflection Gate

| Gate Condition | Meaning | Verification |
|---------------|---------|-------------|
| **Quality Score** | 5-dimension self-rating + total score | Fix Quality Score |
| **Issue Analysis** | Identify issues during the fix | What Went Wrong |
| **Pattern Recognition** | Whether related to past fixes | Pattern Recognition |
