# PRD Writing Guide

## Your Job Here

A PRD is your commitment to the engineering team: here is what we're building, why, and to what standard. You write it, and you own its quality. If engineers come back with questions that the PRD should have answered, the PRD wasn't good enough.

---

## Standard PRD Template

Use this structure. Trim sections based on complexity, but Background, Goals, Requirements, and Acceptance Criteria are non-negotiable.

```
# [Product / Feature Name] PRD

Version: v1.0
Author: PM
Status: Draft / In Review / Approved
Last updated: [date]
Reviewers: [engineering lead, designer, relevant business stakeholders]

---

## 1. Background & Problem
(Why are we doing this? What problem or opportunity exists?)

- Current state:
- Core pain point / opportunity:
- Cost of not doing this:

## 2. Goals & Success Metrics
(What changes in the world when this is done? Must be measurable.)

- Business goal:
- User goal:
- Core KPIs:
  - Metric 1: [definition] Target: [X] By: [Q/month]
  - Metric 2:
- Explicitly out of scope:

## 3. Users & Scenarios

Target users:

| User type | Description | Core need |
|-----------|-------------|-----------|
| Primary | | |
| Secondary | | |

Core user stories:
- As a [user role], I need to [do something], so that [I can achieve a specific goal].

## 4. Requirements

### 4.1 Functional Requirements

Feature one: [name]
- Description:
- Interaction flow:
- Edge cases:
- Error handling:

Feature two: [name]
...

### 4.2 Non-Functional Requirements
- Performance: (e.g., P99 API response < 500ms, page load < 2s)
- Security:
- Compatibility:
- Analytics / instrumentation: [list specific events to track — do not leave this for post-launch]

## 5. Design
- Prototype link:
- Core flow diagrams:
- Key screen notes:

## 6. Technical Notes (optional)
- Main technical challenges:
- System / API dependencies:

## 7. Launch Plan
- Estimated schedule:
- Release strategy: Full rollout / Gradual rollout / A/B test
- Rollback plan:
- Post-launch monitoring:

## 8. Acceptance Criteria
(Every AC must be objectively verifiable — pass or fail, no judgment calls.)

- [ ] Given [condition], when [user action], then [system behavior + outcome]
- [ ] ...

## 9. Risks & Dependencies
| Risk | Impact | Probability | My mitigation |
|------|--------|------------|--------------|

External dependencies:
- Dependent team / system:
- Dependency deadline:
```

---

## Your PRD Quality Standards

### Background needs data

Don't write "users report a bad experience." Write "D3 churn after registration is 42%; root cause analysis points to first-use completion rate below 30% (source: April user research + Mixpanel funnel data)."

### Goals must be measurable

Not "improve user experience." Write "first-use completion rate rises to 60% within 30 days of launch."

### Out of scope is as important as in scope

Out of scope is your weapon against scope creep. At review, get explicit confirmation on what's out — treat it the same as getting sign-off on what's in.

### Non-functional requirements cannot be missing

Every feature has performance, security, and compatibility requirements. If you don't write them, engineering will default to the minimum.

### AC must be usable by QA directly

Format: `When user performs [action], system [does/shows something specific]`

**Wrong vs. right:**

| Wrong (untestable) | Right (directly testable) |
|--------------------|--------------------------|
| "System should respond quickly" | "Core API P99 response < 500ms" |
| "Show a helpful error message" | "Invalid input shows red border and text 'Please enter a valid phone number'" |
| "Support major browsers" | "Supports Chrome 90+, Safari 14+, Firefox 88+" |
| "Data is saved successfully" | "After clicking Save, within 2 seconds page shows 'Saved', data persists after page refresh" |

---

## Your Responsibilities After PRD Review

- Send the final PRD and meeting notes **same day** as the review
- Confirm every AC has a corresponding QA test case — you follow up with QA to make sure
- Any scope change: update the PRD, increment the version number, notify all stakeholders with what changed
- When development is complete, you do final acceptance — this is not delegated to QA
