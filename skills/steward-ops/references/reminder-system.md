# Reminder System & Cadence

## Purpose
Reminders are Steward's primary communication tool. They are how Steward proactively surfaces information
at exactly the right moment. A poorly timed or poorly formatted reminder is noise — it trains the principal
to ignore Steward. A perfectly timed, perfectly formatted reminder is invisible operational excellence —
it makes the principal feel like they have superhuman memory and foresight.

---

## Reminder Types

### 1. Deadline Reminders
Triggered by approaching deadlines in the registry.

**Format:**
```
⏰ [Item] — [X days/hours] until [deadline type]
Action: [what needs to happen]
Consequence if missed: [what goes wrong]
[Link or path to take action]
```

**Cadence logic:**
Deadline reminders follow the lead-time schedules defined in `references/deadline-renewal.md`.
They escalate in urgency as the deadline approaches:
- Early reminders: Informational tone, "heads up" energy
- Mid-range reminders: Action-oriented tone, "plan for this" energy
- Urgent reminders: Alert tone, "do this today" energy
- Overdue reminders: Alarm tone, "this is past due" energy

### 2. Follow-Up Reminders
Triggered when a response or action is expected from someone else and hasn't arrived.

**Format:**
```
📩 No response from [person/entity] — sent [X days ago]
Original: [1-line summary of what was sent]
Expected by: [when a response was expected]
Suggested action: [follow up | wait longer | escalate | close]
```

**Cadence logic:**
- 1x expected response time: First nudge — "No response yet, still within normal range"
- 2x expected response time: Active flag — "This is overdue, recommend following up"
- 3x expected response time: Escalation — "This has been unanswered for [X]. Draft follow-up?"
- 5x expected response time: Decision point — "Close this thread or escalate?"

### 3. Recurring Operational Reminders
Triggered by the calendar and operational rhythm.

**Format:**
```
🔄 Recurring: [Description]
Frequency: [daily/weekly/monthly]
Last completed: [date]
Context: [why this matters and what to do]
```

**Examples:**
- "Tomorrow is Monday — Navigator needs to produce the weekly strategic memo"
- "End of month in 3 days — review revenue metrics and update financial tracker"
- "Quarterly estimated tax payment due in 14 days — prepare documentation"
- "Weekly: Review Stripe dashboard for payment anomalies"
- "Monthly: Audit active subscriptions against actual usage"

### 4. Anticipatory Reminders
Triggered by Steward connecting dots across systems — not because something is due, but because
something relevant is coming up.

**Format:**
```
💡 Heads up: [Anticipation]
Why now: [what triggered this — connected dots]
Suggested action: [what to do about it, if anything]
```

**Examples:**
- "You have a meeting with [client] Thursday — their last email mentioned dissatisfaction with [X].
  Consider preparing talking points around [specific resolution]."
- "KDP session expires in 6 days, and you mentioned wanting to update the Legacy Letters listing.
  Recommend doing the update before the session expires to avoid re-auth + update in the same session."
- "Credit card ending in 4521 expires next month. 3 subscriptions use this card: [list]. Update
  payment method to avoid service disruptions."
- "Etsy's holiday sales typically spike starting in October. Current date is September 15.
  Consider preparing seasonal listings now if planning holiday products."

### 5. Milestone & Progress Reminders
Triggered by project timelines and goal tracking.

**Format:**
```
📊 Progress check: [Project/Goal]
Started: [date] | Target: [date]
Progress: [X]% complete | [X] of [Y] milestones
On track: [yes/no/at risk]
Next milestone: [description] — due [date]
```

### 6. Personal-Business Crossover Reminders
Triggered by life admin items that affect or intersect with business operations.

**Format:**
```
🏠 Personal/Life: [Item]
Due: [date]
Impact: [how this affects business operations, if at all]
Action: [what needs to happen]
```

---

## Reminder Timing Intelligence

### The Right Moment Framework
Not every reminder should arrive at the same time. Steward calculates the optimal delivery moment:

**Morning briefing (7-8 AM principal's time):**
- Today's tasks and deadlines
- Overnight developments (emails received, status changes)
- Calendar overview for the day
- Anticipatory reminders for the day's activities
- Weather/travel impacts if relevant

**Midday check (12-1 PM):**
- Morning task completion status
- New action items from morning email
- Afternoon calendar preview
- Any escalated items

**End of day (5-6 PM):**
- Incomplete task summary
- Tomorrow preview
- Anything that needs overnight thought
- Weekly/monthly item previews if relevant

**Real-time (interrupt the current flow):**
- P0 items only
- Time-critical opportunities with narrow windows
- System failures or security incidents
- Client emergencies

### Day-of-Week Cadence

**Monday:**
- Weekly overview and goals
- Week's deadline preview
- Strategic memo production reminder
- Previous week's unresolved items

**Tuesday-Thursday:**
- Standard daily briefing
- Focus on execution and task completion
- Mid-week course corrections

**Friday:**
- Week-in-review
- Next week preview
- Items to address over the weekend (personal)
- End-of-week financial snapshot

**Weekend:**
- Minimal interruption — personal items only
- Sunday evening: week-ahead preview
- Emergency items only

### Month Cadence

**Month Start (1st-3rd):**
- Monthly review triggers
- New month's deadline preview
- Previous month's metrics summary
- Subscription renewals for the month
- Financial reconciliation reminder

**Mid-Month (14th-16th):**
- Progress check against monthly goals
- Half-month financial snapshot
- Upcoming end-of-month deadlines

**Month End (28th-31st):**
- Monthly close reminders
- Financial reconciliation
- Next month preview
- Monthly report generation

### Quarter Cadence

**Quarter Start:**
- Quarterly goals review
- Estimated tax payment reminder (if applicable)
- Quarterly business review triggers
- License/insurance renewal previews

**Quarter End:**
- Quarterly review preparation
- Tax documentation gathering
- Performance metrics compilation
- Strategic planning triggers

---

## Reminder Format Standards

### Brevity Rules
- Reminder title: 10 words or fewer
- Context line: 20 words or fewer
- Action line: 15 words or fewer
- Total reminder: Should be consumable in under 10 seconds

### Urgency Indicators
Use consistent visual urgency markers:

| Level | Indicator | Usage |
|-------|-----------|-------|
| Info | 💡 or ℹ️ | Anticipatory, no action required now |
| Notice | 📋 or 📌 | Action needed but not time-critical |
| Attention | ⏰ or 🟡 | Deadline approaching, plan for it |
| Warning | ⚠️ or 🟠 | Deadline imminent, act soon |
| Urgent | 🔴 or 🚨 | Overdue or immediate action required |
| Critical | 🆘 | Emergency — stop what you're doing |

### Reminder Batching
Multiple low-priority reminders should be batched, not delivered individually:

**Bad (notification fatigue):**
```
Reminder: Check Stripe dashboard
Reminder: Review email analytics
Reminder: Update product listing
Reminder: Check social media mentions
Reminder: Review weekly traffic
```

**Good (batched):**
```
📋 5 routine items for today — [estimated 30 min total]
1. Check Stripe dashboard (5 min)
2. Review email analytics (5 min)
3. Update product listing (10 min)
4. Check social media mentions (5 min)
5. Review weekly traffic (5 min)
```

---

## Smart Reminder Features

### Snooze Intelligence
When the principal snoozes a reminder:
- 1st snooze: Respect it, reschedule per principal's preference
- 2nd snooze: Reschedule but note the deferral
- 3rd snooze: Attach a note: "Snoozed 3x — is this still needed?"
- 4th+ snooze: See task escalation logic in `references/task-capture.md`

### Context Refresh
When a reminder resurfaces a task from more than 7 days ago, always include:
- The original context (why was this captured)
- What's changed since then (if anything)
- Updated priority (may have shifted)
- Updated deadline (may have moved)

### Reminder Suppression
Steward should suppress reminders when:
- The task has already been completed (detect via email, calendar, or conversation)
- The deadline has been extended (detect via new email or calendar change)
- A higher-priority item makes the reminder irrelevant
- The principal is clearly in deep focus on something important (batch for later)
- The reminder would be redundant with something already surfaced today

### Reminder Chains
Some reminders are part of a sequence. Steward tracks the chain:
```
CHAIN: Quarterly Tax Filing
├── 60 days: Gather documentation ✅ (completed March 1)
├── 30 days: Review with accountant 🟡 (upcoming March 15)
├── 14 days: Finalize filing ⬜ (scheduled March 29)
└── Day of: Submit filing ⬜ (April 15)
```

When one step completes, the next step's reminder activates automatically.

---

## Reminder Delivery Channels

Steward adapts its delivery method based on urgency and context:

| Urgency | Delivery Method |
|---------|----------------|
| Critical (P0) | Immediate in-conversation alert + mark for next briefing |
| Urgent (P1) | Next briefing with highlight + standalone mention if > 4 hours away |
| Important (P2) | Daily briefing, priority section |
| Routine (P3) | Daily briefing, routine section, batched |
| Background (P4) | Weekly rollup only |

---

## Reminder Anti-Patterns (What NOT to Do)

**Never do these:**
- Send a reminder without context ("Check KDP" → useless)
- Remind about the same thing multiple times in the same day (unless escalation)
- Send low-priority reminders during deep focus time
- Use alarm-level urgency for non-urgent items (boy who cried wolf)
- Remind about something the principal just finished
- Stack more than 3 urgent reminders simultaneously (triage first)
- Send reminders about things Steward could handle autonomously
- Forget to include the "how" — where to go and what to do
- Send identical reminder text on repeat — rephrase for freshness
- Remind without checking if the situation has changed since the reminder was set
