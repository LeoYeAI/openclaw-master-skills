# Requirement Elicitation and Scope Narrowing

> Merged guide for gathering explicit/implicit requirements and narrowing
> broad requests into actionable Skill definitions.

---

## Table of Contents

- [1. Pre-Check: Need Scope Narrowing?](#1-pre-check-need-scope-narrowing)
- [2. Scope Narrowing Framework](#2-scope-narrowing-framework)
- [3. Three-Stage Requirement Elicitation](#3-three-stage-requirement-elicitation)
- [4. Final Skill Definition Template](#4-final-skill-definition-template)
- [5. Common Anti-Patterns](#5-common-anti-patterns)

---

## 1. Pre-Check: Need Scope Narrowing?

Narrow scope first if ANY of these apply:

- Request is a broad noun: "writing", "decision-making", "communication"
- No clear audience: unknown who uses it or judges quality
- No clear output: undefined deliverable (document, checklist, plan?)
- No quality criteria: no measurable definition of "good"
- No boundaries: unclear what is in/out of scope

If scope is clear, skip to Stage 1 of requirement elicitation.

Also check: does an existing skill already cover this? See `skill-discovery.md`.

---

## 2. Scope Narrowing Framework

Use these five layers to narrow from "broad" to "actionable":

### Layer 1: Domain Identification

Ask 2-4 options:
```
"[X] means very different things in different contexts. Which is closest?
1) [Domain A - one-line explanation]
2) [Domain B - one-line explanation]
3) [Domain C - one-line explanation]
4) Other (please describe in one sentence)"
```

### Layer 2: Context Constraints (5W1H)

Ask 2-3 at a time (avoid interrogation):

| Dimension | Question |
|-----------|----------|
| WHO | Who uses this? What is their role/expertise? |
| WHAT | What is the deliverable? (format, length, medium) |
| WHERE | What is the org/industry context? (startup, enterprise, B2B) |
| WHEN | When is this used? (trigger, frequency) |
| WHY | What is the goal? (align, persuade, execute, learn) |
| HOW | What constraints exist? (time, process, tools, data) |

### Layer 3: Comparative Narrowing

Present 2-3 similar but distinct scenarios:
```
"To avoid going off track, which is more common for you?
1) [Scenario A]
2) [Scenario B]
3) Mix (please describe ratio)"
```

### Layer 4: Boundary Confirmation (Via Negativa)

Lock boundaries by confirming includes/excludes:
```
"Let me confirm scope:
- Includes: [X], [Y]
- Excludes: [A], [B]
Correct?"
```

### Layer 5: Concrete Case Anchoring

Ask for a recent real example:
- What was the input? (context, data, constraints)
- What output did you need? For whom?
- What was the hard part / time sink?
- What improvement would make it worthwhile?

### Narrowing Stop Condition

All must be true before proceeding:

- [ ] Clear primary scenario (specific audience + specific trigger)
- [ ] Clear output (at least 1 constraint on format/length/structure)
- [ ] Checkable quality criteria (at least 3 items)
- [ ] Boundaries defined (at least 2 "excludes")
- [ ] One real case usable as test input

---

## 3. Three-Stage Requirement Elicitation

```
Stage 1: Explicit requirements (what user said)
    |
Stage 2: Implicit requirements (what user needs but didn't say)
    |
Stage 3: Validation (confirm understanding is correct)
```

### Stage 1: Explicit Requirements

Use 5W1H framework:

| Dimension | Question | Purpose |
|-----------|----------|---------|
| What | What skill to create/optimize? | Define target |
| Why | Why is this skill needed? | Understand motivation |
| Who | Who will use it? | Determine audience |
| When | What scenarios trigger it? | Define trigger conditions |
| Where | What environment/project? | Establish context |
| How | How should it work? | Understand expected behavior |

Key clarification questions:
1. Core functionality?
2. Must-support scenarios?
3. Explicitly unsupported scenarios?
4. Trigger phrases (what would users say)?
5. Expected output format?
6. Quality standards?

### Stage 2: Implicit Requirements

Four methods to uncover hidden requirements:

**Scenario Walkthrough**: User scenario -> possible actions -> possible
problems -> implied requirements.

**Pain Point Analysis**: What problems exist today? What are industry-wide
issues? What cognitive gaps might users have?

**Best Practice Comparison**: Compare against industry best practices to
find gaps that imply requirements.

**Boundary Case Analysis**: Consider edge cases for inputs (empty, huge,
malformed), environment (offline, no permissions), and business logic
(first use, concurrent operations, recovery from interruption).

### Stage 3: Validation

Check three dimensions:

- **Completeness**: All core functions identified? All triggers covered?
  All output formats defined? All error cases considered?
- **Consistency**: No conflicting requirements? Compatible with existing
  system? Aligned with technical constraints?
- **Feasibility**: Required tools available? Technical approach verified?
  Risks identified with mitigation plans?

---

## 4. Final Skill Definition Template

Output after narrowing + elicitation:

```markdown
### Final Skill Definition

- **Core task**: [one sentence]
- **Typical user**: [role/expertise]
- **Typical context**: [industry/org/constraints]
- **Trigger scenarios**: [3-5 items]
- **Input**: [required/optional inputs]
- **Output**: [deliverable type + structure/length constraints]
- **Quality criteria**:
  1) [checkable criterion]
  2) [checkable criterion]
  3) [checkable criterion]
- **Explicitly excludes**:
  - [exclusion A]
  - [exclusion B]
- **Test cases (minimum 3)**:
  - Case 1 (typical): [...]
  - Case 2 (boundary): [...]
  - Case 3 (failure mode): [...]
```

This definition feeds directly into:
1. `description` trigger conditions
2. Decision tree branches
3. Output contract
4. Test case design

---

## 5. Common Anti-Patterns

| Anti-pattern | Consequence |
|-------------|-------------|
| Writing "do X" without specifying who/when/output | Untriggerable skill |
| Cramming multiple tasks into one skill | Trigger conflicts, unstable output |
| No "excludes" boundary | Unlimited scope creep |
| No real example case | Cannot write test cases or acceptance criteria |
| Asking too many questions at once | Overwhelms user, reduces quality |
