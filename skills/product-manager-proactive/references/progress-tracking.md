# Progress Tracking & Reporting

## Your Job Here

Progress reports are not a forwarding service for other people's status updates. You synthesize what's happening, make a judgment about what it means, and communicate that to the right people. Don't wait for someone to ask "how's it going?" — you have a cadence and you keep it.

---

## The Three Core Elements of Every Progress Report

In this order, every time:

1. **Done**: specific, verifiable deliverables
2. **In Progress**: current status + expected completion date
3. **Blockers / Risks**: what needs attention, with your plan for handling it

---

## Weekly Report (you write it, it goes out every Friday)

### 3P Format (Progress / Plans / Problems)

```
[Product / Project Name] Weekly Report — Week [N] ([date range])

## Progress (completed this week)
- [Specific deliverable] (linked to KR or milestone)
- [Specific deliverable]

## Plans (next week)
- [ ] [Task] (owner: [name], due: [date])
- [ ] [Task]

## Problems (risks and blockers)
- [Problem description] — impact: [effect on schedule/goals] — my plan: [what you're doing about it]
```

Don't list task names alone. Write what state the deliverable reached: not "completed requirements review" — write "completed requirements review; PRD v1.0 distributed to engineering; three items confirmed out of scope; meeting notes sent."

### Metrics-Driven Weekly Report (for products with active metric tracking)

```
[Product Name] Data Report — Week [N]

## Core Metrics
| Metric | This week | Last week | Change | Target | % of target |
|--------|-----------|-----------|--------|--------|-------------|

## Key Events
[Events that affected the numbers: launches, campaigns, external factors]

## My Read
[Your interpretation of the most significant movement — give a conclusion, not a description]

## Watch List Next Week
[Specific metrics or risks to monitor]
```

---

## Monthly Report (out by the 3rd of each month)

```
[Product Name] Monthly Report — [Month]

## Key Outcomes This Month
(3-5 items, each with a number)
1. [Outcome] — [supporting data]

## OKR Progress
| KR | Target | Current | Completion | Status |
|----|--------|---------|------------|--------|
| | | | | Green / Yellow / Red |

## Milestone Status
| Milestone | Planned date | Actual / projected date | Status |
|-----------|-------------|------------------------|--------|

## My Assessment
[The 1-2 most important things you learned or observed this month — judgment, not data summary]

## Next Month Focus
[Primary goals + key tasks]

## Support Needed
[Specific resources or decisions you need from leadership or other teams]
```

---

## Launch Checklist (you own the sign-off)

Run this before any feature ships. You check each item — you don't delegate this to engineering to self-certify.

```
Pre-Launch Checklist

Product completeness
- [ ] All P0/P1 features developed and complete
- [ ] All AC verified (your final sign-off)
- [ ] Design QA complete, no major deviations

Technical stability
- [ ] Performance tests passed
- [ ] Security review complete
- [ ] Rollback plan tested and documented

Data & monitoring
- [ ] Instrumentation validated
- [ ] Monitoring and alerting configured
- [ ] Dashboard ready

Operations readiness
- [ ] Operations documentation delivered
- [ ] Customer support FAQ published
- [ ] Necessary training completed

Launch logistics
- [ ] Rollout strategy confirmed (% / segment)
- [ ] Launch time confirmed (avoid peak traffic)
- [ ] On-call owner confirmed for launch window
```

---

## Retrospective (you organize and run it)

```
# [Project Name] Retrospective

Project period: [start] → [end]
Retro date: [date]

## Goals vs. Actuals
| Goal | Planned | Actual | % achieved |
|------|---------|--------|------------|

## Keep (what worked well)
1. ...

## Improve (what could be better next time)
1. ...

## Stop (what we won't repeat)
1. ...

## Action Items
| Improvement | Owner | Due date |
|-------------|-------|----------|

## Key Learnings
[1-3 conclusions worth carrying into the next project]
```

---

## Status Color Conventions

| Color | Meaning | Your action |
|-------|---------|-------------|
| Green | On track | Normal follow-through, no escalation needed |
| Yellow | At risk but manageable | Develop mitigation plan; proactively brief stakeholders |
| Red | Off track, needs intervention | Escalate immediately; present a revised plan |
| Gray | Paused / out of scope | Confirm the decision; explicitly update the plan |

---

## What You Proactively Do

- Weekly reports go out every Friday — no reminders needed
- When a milestone is within 2 weeks, proactively check checklist status; surface problems early
- When status moves from green to yellow, notify relevant stakeholders immediately — don't wait for red
- Retro action items become real backlog tickets with owners and deadlines — they don't live only in the retro document
