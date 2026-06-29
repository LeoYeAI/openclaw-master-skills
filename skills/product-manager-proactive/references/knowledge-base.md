# PM Knowledge Base & Document Management

## Your Job Here

A PM without a structured document system is running on memory and Slack threads. Information decays, decisions get forgotten, context gets lost when people change roles. Your job is to own a living knowledge base that captures the right information at the right level of detail — and to build it as work happens, not retroactively.

This file defines what to document, how to structure it, when to update it, and how to surface it when needed.

---

## When to Initialize the Knowledge Base

Build it during onboarding if it doesn't exist. If you're inheriting a product with scattered docs, your first two weeks include a knowledge audit: find what exists, consolidate what's useful, identify what's missing.

For each category below: if nothing exists, create the folder and a starter doc. If something exists but is disorganized, restructure it. If it's already well-maintained, just note the location and keep it current.

---

## The 11 Document Categories

### 1. Business Consulting Records

**What goes here:** notes and outputs from any external consulting, advisory engagement, or strategic assessment — including investor feedback that has product implications, external audits, and strategy sessions with outside advisors.

**File structure:**
```
/consulting/
  YYYY-MM-DD_[advisor-or-firm]_[topic].md
  index.md  ← running list of all sessions with 1-line summaries
```

**What to capture per session:**
- Date, participants, context
- Key insights or recommendations
- What was decided or will be acted on
- What was noted but not acted on (and why)
- Link to any deliverable (deck, report)

**Freshness rule:** index.md updated within 24 hours of any session.

---

### 2. Client / Customer Requirements

**What goes here:** requirements submitted by clients or business stakeholders — distinct from internally-generated roadmap items. Includes formal requirement documents, emails with requests, meeting notes where a requirement was stated, and account-specific commitments.

**File structure:**
```
/requirements/
  /intake/
    YYYY-MM-DD_[client-or-stakeholder]_[requirement-title].md
  /active/
    [feature-or-epic-name].md  ← consolidated from multiple intake sources
  /backlog/
    [feature-or-epic-name].md
  /declined/
    [feature-name]_declined.md  ← include reason for declining
```

**What to capture per requirement:**
- Source (who submitted it, in what context)
- Business goal it serves
- Current status (intake / in analysis / prioritized / in development / shipped / declined)
- Link to the PRD if one was written
- Any commitments made to the requester

**Freshness rule:** status updated whenever it changes. Declined requirements are never deleted — they explain why you said no, which will come up again.

---

### 3. User Interviews

**What goes here:** records of every user research conversation — interviews, usability tests, customer calls with product-relevant content, support escalations with important signal.

**File structure:**
```
/user-research/
  /interviews/
    YYYY-MM-DD_[user-type-or-pseudonym]_[topic].md
  /synthesized/
    [theme-or-question].md  ← cross-interview synthesis
  insights-registry.md  ← running list of validated insights with source citations
```

**What to capture per interview:**
- Date, interviewer, participant description (role, segment, tenure as user)
- Research question or goal
- Key quotes (verbatim where possible)
- Observations (what the user did, not just what they said)
- Insights (your interpretation — labeled as inference, not fact)
- Open questions raised

**Synthesis rule:** after every 3-5 interviews on the same topic, write a synthesis note in `/synthesized/`. Don't let raw notes pile up without extracting patterns.

**RAG indexing:** the `insights-registry.md` is the retrievable index. Format each entry as:
```
[Insight]: [one sentence statement of what was learned]
[Evidence]: [2-3 quotes or observations that support it]
[Source]: [interview IDs]
[Confidence]: [High / Medium / Low — based on # of sources and consistency]
[Implications]: [what this suggests for the product]
```

---

### 4. PRD Archive — Including Changes, Deferrals, and Scope Cuts

**What goes here:** every PRD, with full version history. Crucially: not just what was built, but what was cut, deferred, and why.

**File structure:**
```
/prds/
  /active/
    [feature-name]-PRD-v[N].md
  /shipped/
    [feature-name]-PRD-v[final].md
  /deferred/
    [feature-name]-PRD-v[N]-deferred.md  ← include deferral reason
  /cancelled/
    [feature-name]-PRD-v[N]-cancelled.md  ← include cancellation reason
```

**Version control within each PRD:**
```
## Change Log
| Version | Date | Author | What changed | Why |
|---------|------|--------|-------------|-----|
| 1.0 | ... | ... | Initial draft | — |
| 1.1 | ... | ... | Removed X | Engineering complexity > value |
| 1.2 | ... | ... | Deferred Y | Deprioritized for Q3 | 
```

**What to document for every scope cut or deferral:**
- What was removed
- Why (data, constraint, decision-maker, trade-off made)
- What condition would bring it back (e.g., "revisit when user base exceeds 10K" or "if NPS drops below 40")

**Why this matters:** scope cuts often get re-requested 6 months later. Having the "why we didn't" documented saves the team from re-debating closed questions.

---

### 5. Change Impact Log — Data Changes Caused by Releases

**What goes here:** for every significant release, a record of what changed in key metrics as a result. This is not a general analytics dashboard — it's a causality log that connects product changes to metric movements.

**File structure:**
```
/change-impact/
  YYYY-MM-DD_v[version]_impact.md
  summary.md  ← rolling summary of what features moved which metrics
```

**What to capture per release:**
```
## Release: [version / name] — [date shipped]

### What shipped
- [Feature A]: [brief description of behavior change]
- [Feature B]: ...

### Metrics before (baseline — 2 weeks pre-release)
| Metric | Value |
|--------|-------|
| [metric 1] | [value] |

### Metrics after (2 weeks post-release)
| Metric | Value | Delta |
|--------|-------|-------|
| [metric 1] | [value] | [+/- X%] |

### Attribution notes
- [Metric delta] is likely attributable to [feature] because [reasoning]
- [Confounding factors if any]

### Unexpected outcomes
- [Anything that moved that wasn't expected]
```

**Freshness rule:** fill in baseline before shipping. Fill in post-release metrics 2 weeks after each release. Don't skip the attribution notes — they're the most valuable part.

---

### 6. Data Dashboards, Analysis Conclusions, and Iteration Progress

**What goes here:** outputs of data analysis work — not raw data, but synthesized conclusions, dashboard descriptions, and how metrics trended across iterations.

**File structure:**
```
/data/
  /dashboards/
    [dashboard-name].md  ← description of what's on it, how to read it, link to live version
  /analyses/
    YYYY-MM-DD_[topic].md
  /iteration-tracking/
    [quarter-or-sprint]-metrics.md
```

**Dashboard documentation format:**
```
## Dashboard: [name]

**Purpose**: [what question does this dashboard answer?]
**Link**: [URL to live dashboard]
**Owner**: [who maintains the underlying data pipeline]
**Key metrics shown**:
- [Metric A]: [definition, how it's calculated]
- [Metric B]: ...
**How to read it**: [any non-obvious interpretation guidance]
**Known limitations**: [any data quality issues, sampling biases, lag]
**Last validated**: [date PM last confirmed it's showing correct data]
```

**Analysis conclusion format:**
```
## Analysis: [question being answered]
**Date**: [date]
**Method**: [what data, what analysis approach]
**Conclusion**: [the answer in 1-2 sentences]
**Confidence**: [High / Medium / Low + reason]
**Supporting data**: [key numbers or charts that support the conclusion]
**What this changes**: [any product or roadmap implication]
**What this doesn't tell us**: [limitations or follow-up questions]
```

---

### 7. Daily Work Log (RAG-Indexed)

**What goes here:** a running PM work journal. Not a status report — a log of decisions made, context understood, problems encountered, and reasoning applied. The purpose is to make your thinking retrievable.

**File structure:**
```
/work-log/
  YYYY-MM-DD.md
  index.md  ← auto-updated table of contents by topic and date
```

**Daily log format:**
```
# Work Log — [Date]

## Decisions made today
- [Decision]: [what was decided + by whom + key reasoning]

## Information received
- [New information]: [source + implication]

## Blockers encountered
- [Blocker]: [what it is + what I did about it]

## Open questions
- [Question]: [what I need to find out + by when]

## What I learned
- [One thing learned today about the product, the users, or the team]
```

**RAG indexing strategy:**
The daily log is most useful as a retrieval system. Structure entries so they can be searched by:
- Topic / feature name (always mention the feature by name, not "the thing we discussed")
- Decision type (prioritization, scope, design, technical)
- Person involved (name people explicitly)
- Date range

The `index.md` maintains a running catalog:
```
| Date | Topic | Type | Key decision or insight |
|------|-------|------|------------------------|
| 2024-01-15 | Payment flow | Decision | Deferred split-payment to Q2 because... |
```

**Freshness rule:** write the daily log at the end of each working day, or the morning after. Entries written more than 48 hours late lose too much fidelity.

---

### 8. Business Goals and Strategic Objectives

**What goes here:** the company's strategic goals as they relate to the product, the product's own goals, how they were set, and how they evolve over time. This is the north star document for prioritization decisions.

**File structure:**
```
/strategy/
  current-strategy.md  ← always the live version
  /archive/
    YYYY-[quarter]_strategy.md  ← snapshots when strategy changes significantly
  okrs/
    YYYY-[quarter]_okrs.md
```

**Current strategy document format:**
```
## Product Strategy — [as of date]

### Company context
[What the company is trying to achieve in the next 12 months]

### Product's role
[How the product contributes to company goals]

### Target user
[Who we are building for — be specific about segment]

### What we are optimizing for
[The 1-2 north star metrics]

### Strategic bets
[The 2-3 big product direction choices we're making, and why]

### What we are explicitly NOT doing
[Scope limits and why — this is as important as what we are doing]

### Open strategic questions
[Things we haven't decided yet that will affect the roadmap]

### Last reviewed
[Date + who was involved in the review]
```

**Immutability rule:** never edit the current strategy doc in place without creating an archive copy first. Strategy changes are significant events — the history matters.

---

### 9. Design Asset Index (Figma and Other Design Files)

**What goes here:** not the design files themselves, but an organized index of where they live, what state they're in, and how they map to product areas and PRDs.

**File structure:**
```
/design/
  design-index.md  ← master index of all design files
  /specs/
    [feature-name]-design-spec.md  ← design decisions and rationale for implemented features
```

**Design index format:**
```
## Design Index

| Feature / Area | Figma Link | Status | Version | PRD Link | Designer | Last Updated |
|---------------|-----------|--------|---------|---------|---------|-------------|
| [Feature A] | [URL] | Final | v3 | [link] | [name] | [date] |
| [Feature B] | [URL] | In Progress | v1 | [link] | [name] | [date] |
| [Feature C] | [URL] | Archived | v2 | [link] | [name] | [date] |
```

**Design status definitions:**
- **Explorations**: early-stage, not ready for implementation
- **In Review**: being reviewed by PM and/or engineering
- **Final**: approved and ready for (or in) implementation
- **Archived**: no longer active; kept for reference

**Design spec (per shipped feature):**
Document the design decisions that were made and why — interaction patterns chosen, edge cases handled, things explicitly decided against. This prevents re-debating closed design questions and helps future designers understand intent.

---

### 10. Version Release Records — What Was Actually Built

**What goes here:** for each version or sprint, a record of what was actually implemented — distinct from what was specced. This is the ground truth of product history.

**File structure:**
```
/releases/
  YYYY-MM-DD_v[version].md
  release-history.md  ← index of all releases with 1-line summaries
```

**Release record format:**
```
## Release v[X.Y.Z] — [Date]

### What shipped
| Feature / Change | PRD link | Notes |
|-----------------|---------|-------|
| [Feature A] | [link] | Shipped as specced |
| [Feature B] | [link] | Shipped with scope reduction: [what was cut] |
| [Bug fix C] | — | [brief description of what was fixed] |

### What was deferred from this release
| Item | Reason for deferral | Target release |
|------|---------------------|---------------|
| [Feature D] | [reason] | [next version / TBD] |

### Spec deviations
| Item | Specced behavior | Shipped behavior | Why different |
|------|-----------------|-----------------|--------------|
| [X] | [what spec said] | [what shipped] | [reason] |

### Known issues shipped
| Issue | Severity | Workaround | Fix target |
|-------|---------|-----------|-----------|
| [issue] | [P1/P2/P3] | [workaround if any] | [sprint/date] |

### Retrospective notes
[Key learnings from this release cycle]
```

**Freshness rule:** complete within 48 hours of release. The spec deviations section is mandatory — don't skip it even when everything went smoothly.

---

### 11. SOPs — Standard Operating Procedures

**What goes here:** step-by-step instructions for recurring PM tasks and processes that need to be done consistently. SOPs prevent the "how do we do this again?" question from slowing down execution.

**File structure:**
```
/sops/
  index.md  ← list of all SOPs
  /pm-processes/
    sprint-planning.md
    requirements-intake.md
    prd-review.md
    launch-checklist.md
    ...
  /tools/
    [tool-name]-usage.md  ← how PM uses each tool
  /integrations/
    [integration-name]-setup.md
```

**SOP format:**
```
# SOP: [Process Name]

**Purpose**: [what this process achieves]
**Trigger**: [what starts this process]
**Owner**: PM
**Frequency**: [when this runs]
**Tools required**: [list]

## Steps

### Step 1: [Name]
[Specific action]
- Input: [what you need]
- Output: [what you produce]
- Time: [estimate]

### Step 2: [Name]
...

## Common failure modes
- [What goes wrong here and how to handle it]

## Version
Last updated: [date] | [what changed]
```

**SOP maintenance rule:** if you find yourself doing a process differently than the SOP describes — either update the SOP or follow it. Never let the SOP silently go stale.

---

## Knowledge Base Maintenance

### When to create a new document
- Any decision that was non-trivial gets logged (daily work log at minimum)
- Any user conversation produces an interview note
- Any release produces a release record
- Any analysis produces a conclusion doc

### When to update existing documents
- Status changes in requirements → update status field
- Metric moves post-release → update change impact log
- Strategy changes → archive current, create new
- PRD changes → version bump + change log entry

### Monthly knowledge base audit
Once a month, run a 20-minute audit:
- Are there orphaned notes that should be filed or deleted?
- Is the design index up to date?
- Are there user insights sitting in raw interview notes that should be synthesized?
- Is the release history current?
- Are any SOPs visibly out of date?

### When onboarding someone new
The knowledge base should make it possible for a new team member to get up to speed without needing a series of explanations from you. If you can't point someone new to the knowledge base and have them understand the product's context, it needs work.
