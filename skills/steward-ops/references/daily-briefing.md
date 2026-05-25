# Daily Briefing & Status Reports

## Purpose
The daily briefing is the single most important output Steward produces. It's the one document the principal
reads every morning that tells them: what matters today, what changed overnight, what's coming, and what needs
a decision. A great daily briefing means the principal starts their day with complete operational clarity
in under 3 minutes.

---

## The Morning Briefing — Master Template

```markdown
# Good Morning — [Day of Week], [Full Date]

## ⚡ Decisions Needed ([count])
[Items that require the principal's judgment — nothing else goes here.
Each item includes the decision to be made, the options, Steward's recommendation,
and the deadline for deciding.]

**1. [Decision Title]**
Situation: [1-2 sentences — what's going on]
Options: [A] [B] [C if applicable]
Recommendation: [Steward's suggested choice and why]
Decide by: [deadline]

---

## 📬 Inbox Summary
**Action required**: [X] emails across [Y] accounts
[Top 3-5 most important emails with sender, subject essence, and action needed]

**FYI**: [X] items worth knowing
[1-line summaries of notable FYI items]

**Handled**: [X] emails auto-processed (receipts, confirmations, newsletters archived)

---

## 📅 Today's Schedule
[Time-ordered view of today's calendar events with context]

**[Time]** — [Event Title]
  ↳ [Prep needed | Context note | Link]

**[Time]** — [Event Title]
  ↳ [Prep needed | Context note | Link]

[If no events: "Clear calendar today — focus time available."]

---

## ✅ Today's Tasks ([count])

### Must Do Today
- [ ] [Task] — [context, est. time] — [P level]
- [ ] [Task] — [context, est. time] — [P level]

### Should Do Today
- [ ] [Task] — [context, est. time]
- [ ] [Task] — [context, est. time]

### Quick Wins (< 5 min each)
- [ ] [Task]
- [ ] [Task]

---

## ⏰ Deadlines & Renewals
**This week:**
- [Item] — due [day] — [status: on track | needs attention | at risk]
- [Item] — due [day] — [status]

**Upcoming (next 2 weeks):**
- [Item] — due [date] — [status]

---

## 📊 Pulse Check
[Key metrics snapshot — revenue, orders, platform health, anything the principal tracks]
- [Metric]: [value] ([trend: ↑ ↓ →] vs [comparison period])
- [Metric]: [value] ([trend])
- [Platform status]: [healthy ✅ | issue ⚠️ | down 🔴]

---

## 💡 On Your Radar
[Anticipatory items — things Steward noticed that aren't urgent but worth knowing]
- [Observation or connection]
- [Observation or connection]

---

## 📋 Standing Items
[Recurring items that appear on specific days]
[Monday: Weekly strategic memo production]
[Friday: Week-in-review, next week preview]
[Month start: Monthly metrics review]
[Quarter end: Quarterly review preparation]
```

---

## Briefing Construction Logic

### Step 1: Gather Raw Data
Before constructing the briefing, collect from all sources:
1. **Email** — Run inbox triage across all accounts (see `references/inbox-triage.md`)
2. **Calendar** — Pull today's events and this week's preview
3. **Deadline registry** — Check all items due within 14 days
4. **Task list** — Pull all active tasks, sorted by priority and due date
5. **Platform status** — Check known platforms for health and session status
6. **Financial** — Pull any payment-related alerts or due dates
7. **Previous briefing** — Check what was surfaced yesterday — anything unresolved?

### Step 2: Triage & Prioritize
Apply the universal priority framework (P0-P4) to every item from every source.
Then stack-rank within each section:
- Decisions → by deadline (soonest first), then by consequence (highest impact first)
- Inbox → by priority level, then by sender importance
- Tasks → by must-do vs should-do vs quick-wins
- Deadlines → by proximity
- Metrics → by deviation from expected (biggest changes first)

### Step 3: Synthesize & Connect
Look for connections between items:
- Does an email relate to a task already on the list? Link them.
- Does a calendar event require prep that isn't in the task list? Add it.
- Does a deadline relate to a platform session that's expiring? Connect them.
- Does a metric change relate to something in the inbox? Note the connection.

### Step 4: Format & Deliver
Apply the master template above. Strict rules:
- **Total length**: The briefing should be readable in under 3 minutes
- **Decision section**: NEVER more than 5 items. If more exist, push the rest to a separate "Decision Queue"
- **Inbox section**: Top 5 action items max. Link to full triage report for more.
- **Tasks section**: Max 10 items total across all subsections
- **Deadlines section**: Only items within 14 days
- **Metrics section**: Only 3-5 key metrics. More detail available on request.
- **Radar section**: Max 3 items. These should feel insightful, not routine.

---

## Briefing Variations

### The Monday Briefing (Weekly Kickoff)
Adds to the standard template:
```markdown
## 📌 This Week's Focus
[3-5 key objectives for the week]
1. [Objective] — [why it matters this week]
2. [Objective]
3. [Objective]

## 🔙 Last Week's Outcomes
- [Objective]: [completed ✅ | partial 🟡 | missed ❌]
- [Objective]: [status]
- Notable: [anything unexpected that happened]

## 📅 Week at a Glance
[Day-by-day preview of key events, deadlines, and tasks]
Mon: [key items]
Tue: [key items]
Wed: [key items]
Thu: [key items]
Fri: [key items]
```

### The Friday Briefing (Week Wrap)
Adds to the standard template:
```markdown
## 📊 Week in Review
**Completed**: [X] of [Y] planned tasks
**Decisions made**: [count]
**Emails processed**: [count]
**Deadlines met**: [count]

### Key Accomplishments
- [accomplishment]
- [accomplishment]

### Carried Forward
- [task or item that's moving to next week, with reason]

## 🔮 Next Week Preview
**Big items**: [top 3 things coming next week]
**Deadlines**: [anything due next week]
**Prep needed**: [anything to think about over the weekend]
```

### The Month-Start Briefing (Monthly Review)
Adds to the standard template:
```markdown
## 📊 Monthly Snapshot — [Month Year]

### Revenue & Financial
- Revenue: $[X] ([trend] vs last month)
- Expenses: $[X] ([notable changes])
- Net: $[X]
- Subscriptions active: [count] ($[total]/month)

### Platform Health
| Platform | Status | Key Metric | Change |
|----------|--------|------------|--------|
| [Platform] | [status] | [metric] | [change] |

### Renewals This Month
- [item] — [date] — [cost] — [action needed]

### Monthly Ops Tasks
- [ ] Review all subscriptions for value
- [ ] Audit account access and permissions
- [ ] Check backup status
- [ ] Review and update SOPs if needed
- [ ] Reconcile financial records
```

### The Quick Scan (for "what's urgent?" queries mid-day)
```markdown
## Quick Scan — [Time]

### 🔴 Urgent Now
[Item with action needed — or "All clear, nothing urgent"]

### 🟡 Before End of Day
- [item]
- [item]

### New Since This Morning
- [new email/event/task that arrived since the morning briefing]
```

---

## End-of-Day Review

```markdown
# End of Day — [Date]

## Completed Today ✅
- [task]
- [task]

## Not Completed — Carrying Forward
- [task] — [rescheduled to: date | reason for carry-forward]

## New Items Captured Today
- [task/deadline/note captured during the day]

## Tomorrow Preview
- [Key items for tomorrow]
- [Prep needed tonight]

## 🌙 Tonight's Homework (if any)
[Only if something genuinely needs attention tonight. Otherwise: "Nothing tonight. Rest well."]
```

---

## Metrics & Pulse Check Configuration

### What to Track
The Pulse Check section of the briefing should include metrics the principal cares about. Configure by asking:

1. **Revenue metrics**: Daily/weekly revenue, order count, average order value
2. **Platform metrics**: Views, impressions, click-through rates, conversion rates
3. **Growth metrics**: Subscriber count, follower growth, audience size
4. **Health metrics**: Uptime, error rates, API usage vs limits
5. **Financial metrics**: Cash position, burn rate, receivables, payables
6. **Custom KPIs**: Whatever the principal specifically wants to track

### Metric Display Rules
- Always show the metric with directional trend (↑ ↓ →)
- Always show comparison period (vs yesterday, vs last week, vs last month)
- Highlight anomalies — anything that deviated >20% from the expected range
- Don't show metrics that haven't changed — only notable movements
- Use sparkline-style descriptions for trends ("steadily climbing" vs "sharp drop yesterday")

---

## Briefing Quality Standards

### The 3-Minute Rule
The complete morning briefing must be fully consumable in 3 minutes or less.
If it takes longer, it's too detailed — push depth into linked detail documents.

### The Action Clarity Test
For every item in the briefing, the principal should be able to answer:
1. What is this?
2. Why should I care right now?
3. What do I need to do?
If the answer to any of these is unclear, rewrite the item.

### The Zero-Surprise Standard
The morning briefing should never contain an item that makes the principal say "I should have known
about this yesterday." If it's that important, it should have been surfaced in real-time or in
yesterday's briefing.

### The Consistency Standard
The briefing should follow the same structure every day. The principal should know exactly where to
look for each type of information. Consistency builds trust and speeds reading.

### The Completeness Standard
The briefing should cover ALL of the principal's operational concerns:
- All email accounts triaged
- All calendar events noted
- All deadlines checked
- All active tasks reviewed
- All tracked metrics updated
- All platforms status-checked

If any source was unavailable (couldn't access email, calendar API down, etc.), explicitly note it:
"⚠️ Could not access [source] for this briefing. Manual check recommended."

---

## Briefing Personalization

### Adapting to the Principal's Style
Over time, Steward should learn and adapt:
- **Reading pattern**: Does the principal read top-to-bottom or scan? → Adjust density
- **Decision style**: Does the principal want full options or just recommendations? → Adjust decision section
- **Detail preference**: Does the principal want metrics every day or only when notable? → Adjust pulse section
- **Tone preference**: Clinical and efficient, or conversational with personality? → Adjust voice
- **Priority corrections**: When the principal overrides a priority, learn from it → Adjust classification

### Briefing Feedback Loop
After each briefing, Steward should note:
- Which items the principal acted on immediately → these were well-prioritized
- Which items the principal ignored → consider if these were over-prioritized
- Which items the principal asked follow-up questions about → add more context next time
- What the principal asked about that wasn't in the briefing → add this source/category
