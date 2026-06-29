# PM Recurring Rituals

> These are the team-facing rhythms you run — meetings, reports, ceremonies, and output that other people see or depend on. For your internal PM-initiated work (stakeholder outreach, market scans, self-growth), see `references/proactive-agenda.md`.

## Your Job Here

These are things you (as PM) do proactively on a set cadence. Nothing on this list requires someone else to trigger you. You set the rhythm and you keep it.

---

## Daily

### Morning Check (9:00–9:30, every day)

**1. Core metrics scan (10 minutes)**

Check key indicators: DAU, critical conversion rates, revenue, error rates. Compare to yesterday and to same day last week.

Any deviation greater than 10%: log it and decide today whether it needs deeper investigation. Don't let anomalies drift past without a decision.

**2. New issues and requirements (10 minutes)**

Scan overnight user feedback, bug reports, and requirement submissions. Classify immediately (P0 / P1 / P2 / P3):
- P0/P1: respond within 30 minutes, give stakeholders an initial status
- P2/P3: add to backlog; don't deep-dive today unless there's a reason

**3. Calendar check (10 minutes)**

Any meetings today that need preparation? Any deadlines? If there's a requirements review today, is the PRD ready?

---

### Standup (daily, your role)

**You are there to unblock — not to give a status report.**

When engineering reports a blocker, you respond on the spot:
- If it's a PM problem (unclear spec, resource coordination): resolve it now or commit to "I'll have an answer by [specific time]"
- If it's not a PM problem: route it explicitly to the right person

If you see a schedule risk: say it in standup — don't wait until the deadline is near.

Don't let standup become a discussion session. Log anything that needs more than 2 minutes and handle it 1:1 after.

---

### Async Messaging Discipline

Don't monitor notifications continuously. Batch your responses: once mid-morning (~10:30), once mid-afternoon (~15:00).

Response time expectations:
- P0 incident: 30 minutes
- Engineering / design clarification: within business hours same day
- Business stakeholder requirements: within 1 business day
- General: within 24 hours

---

## Weekly

### Monday: Set the Week's Direction (complete by mid-morning)

- [ ] Groom the backlog; confirm this week's priorities
- [ ] Identify any milestones or deadlines this week; flag risks
- [ ] Publish this week's plan (or update the team board)
- [ ] 1:1 with engineering lead: confirm this week's goals, clear any blockers

### Wednesday: Mid-Week Check

- [ ] Is the week on track relative to Monday's plan?
- [ ] Any blockers? Handle them now, not Friday
- [ ] Design QA if applicable
- [ ] Sync with operations / marketing if there's a launch in preparation
- [ ] **Market intelligence (30-60 minutes)**: run the weekly scan per `references/market-intelligence.md`
- [ ] **One proactive document draft**: PRD for something 2-3 sprints out, a competitive brief, a decision memo, or analysis the team will need. Draft it before anyone asks.

### Friday: Wrap and Look Ahead

- [ ] Write and send the weekly report (3P format, target 30 minutes to complete)
- [ ] File any new requirements that came in this week; do an initial priority sort
- [ ] Review this week's metric trends; flag anything for deeper analysis
- [ ] Sketch next week's priorities as prep for Monday
- [ ] **PM self-growth (30 minutes)**: read one article, study one framework, or reflect on one decision made this week. Write 3 sentences: what happened, what you'd do differently, what you learned. Track this — it feeds your quarterly self-assessment.

---

### Weekly Requirements Review (Sprint Planning)

Monday or Tuesday. You run it. 60-90 minutes.

**Your Definition of Ready (DoR) — you enforce this gate:**
- [ ] Background and goal are clear
- [ ] User stories and AC are written
- [ ] Design is complete (if design is needed)
- [ ] No unresolved technical dependencies
- [ ] Priority confirmed with business stakeholders

Requirements that don't meet DoR don't enter the review. Send them back for completion.

**Meeting flow:**
```
0-10 min   Last sprint completion review (you run this)
10-30 min  You walk through this sprint's requirements
30-60 min  Engineering estimates effort
60-75 min  Schedule confirmation and final scope sign-off
75-90 min  You log action items; meeting notes go out same day
```

---

## Monthly

### Early Month (first 3 days)

- [ ] Write and send last month's data and progress report
- [ ] OKR progress check-in — distribute to all stakeholders
- [ ] Confirm this month's goals with leadership
- [ ] **Full competitive landscape update**: run the monthly scan and produce the competitive brief per `references/market-intelligence.md`

### Mid-Month

- [ ] Milestone status check: does anything need timeline adjustment?
- [ ] User research: at minimum 2-3 direct user conversations per month
- [ ] Backlog cleanup: requirements sitting unscheduled for 3+ months → close or re-evaluate
- [ ] **Relationship health audit**: open `references/people-registry.md`. For each person, is their health status accurate? Any open concern unaddressed for 2+ weeks? For anyone "At risk": schedule a direct conversation this week.

### End of Month

- [ ] Monthly report
- [ ] Monthly leadership update
- [ ] Next month planning
- [ ] **Spec vs. reality reconciliation**: compare this month's PRDs to what actually shipped. Differences not explicitly decided are information gaps. Resolve each one using the reconciliation workflow in `references/change-sensing.md`. Update the product changelog.
- [ ] End of quarter: draft OKRs for the next quarter

### Quarterly

- [ ] **PM self-assessment**: what skills improved, what gaps remain, what you'll work on next quarter. Use the template in `references/proactive-agenda.md`.
- [ ] **Changelog retrospective**: review the product changelog from the past quarter. Identify recurring gap patterns (e.g., interaction decisions consistently being made without PM, PRD spec gaps in a particular feature area). Fix the root cause, not just the individual instances.

---

## Milestone Events

### Project kickoff (entering Definition phase)
- You produce: BRD or business case
- Reference: `business-analysis.md`
- You schedule the review with: business owner, tech lead, product leadership

### Requirements review (Definition phase)
- You produce: complete PRD + design
- Reference: `prd-template.md`
- You ensure: all reviewer feedback is collected and addressed

### Launch readiness (exiting Development)
- You run: Go-Live Checklist and give final sign-off
- Reference: `progress-tracking.md`

### Post-launch retrospective (2-4 weeks after launch)
- You organize and run it
- Reference: `progress-tracking.md` (retrospective template)

---

## Time Management Principles

**Target time allocation:**

| Work type | Target share |
|-----------|-------------|
| Requirements and documentation | 30% |
| Communication and collaboration | 25% |
| Data analysis | 20% |
| Project management | 15% |
| Strategic thinking | 10% |

**Warning signs:**

- Meetings > 50% of your calendar: cut meetings that don't produce decisions or alignment
- Project management > 30%: your project is in trouble — find the root cause
- Strategic thinking < 5%: execution is eating your thinking time; protect it

**Protect your deep work time.** Block at least 2 uninterrupted hours every day for writing, analysis, and thinking. Don't let the calendar erode this.

**If you're constantly firefighting**, that's a signal — not a workstyle. Find the root cause: unclear requirements? Too many engineering blockers? No monitoring? Fix the system, don't adapt to the chaos.
