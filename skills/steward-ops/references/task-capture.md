# Task Capture & Resurfacing

## Purpose
Tasks leak from every conversation, email, and thought. The average knowledge worker loses 40% of their
action items because they were mentioned in passing, agreed to in conversation, or thought of at the wrong
moment. Steward captures every task at the moment it appears and resurfaces it at the moment it's needed.
Nothing falls through the cracks.

---

## Task Capture Sources

Tasks can originate from anywhere. Steward monitors all channels:

### Conversational Task Capture
During any conversation with the principal, watch for:

**Explicit task signals:**
- "I need to..." / "I should..." / "I have to..."
- "Don't let me forget to..."
- "Remind me to..."
- "We need to..."
- "Someone should..."
- "Add to the list..."
- "Track this..."
- "Follow up on..."
- "Put this on my radar..."
- "I'll do that later..."
- "Let me come back to that..."
- "That's a good idea, let me think about it..."
- "I promised [person] I would..."

**Implicit task signals:**
- Discussion of a problem without a stated solution → capture: "Resolve [problem]"
- Mention of a deadline without a stated plan → capture: "Plan for [deadline]"
- Reference to a person expecting something → capture: "Deliver [thing] to [person]"
- Comparison shopping or research discussion → capture: "Make decision on [topic]"
- "That reminds me..." → capture whatever follows
- Questions about how to do something → capture: "Figure out [how to do X]"

### Email-Derived Tasks
When processing emails (see `references/inbox-triage.md`):
- Extract every action item from action-required emails
- Convert meeting invitations to prep tasks
- Convert invoice emails to payment tasks
- Convert shipping notifications to "verify delivery" tasks
- Convert service outage emails to "check resolution" tasks

### Calendar-Derived Tasks
From calendar events:
- Pre-meeting preparation tasks
- Post-meeting follow-up tasks
- Deliverable deadlines attached to calendar events
- Travel preparation tasks
- Presentation or document preparation deadlines

### Self-Generated Tasks
Steward generates tasks from its own observations:
- Deadline approaching → "Review and act on [deadline]"
- Account health issue detected → "Investigate [platform] account status"
- Subscription audit → "Review [subscription] value before renewal"
- Pattern detected → "Address [recurring issue]"

---

## The Task Record Format

Every captured task is stored in a structured format:

```
TASK ID: [unique identifier — format: T-YYYYMMDD-NNN]
Created: [timestamp of capture]
Source: [conversation | email | calendar | self-generated | manual]
Source Context: [quote or reference to where this came from]

Title: [clear, imperative action statement — "Review KDP listing performance"]
Description: [expanded context if needed, max 3 sentences]
Category: [business-ops | product | marketing | finance | personal | admin | client | platform]
Priority: [P0 | P1 | P2 | P3 | P4]

Due Date: [specific date if known, or "ASAP" | "This week" | "This month" | "No deadline"]
Estimated Time: [how long this will take — 5min | 15min | 30min | 1hr | 2hr+ | Unknown]
Energy Level: [high-focus | medium | low-energy — what state is needed to do this well]

Dependencies: [other tasks or conditions that must be met first]
Blocked By: [if this task can't proceed, why not]
Blocks: [what other tasks are waiting on this one]

Delegable: [yes | no — can someone else do this?]
Delegate To: [if yes, who?]
Approval Required: [does completion require the principal's sign-off?]

Resurface: [when should this task be shown again — specific date, or trigger condition]
Recurrence: [one-time | daily | weekly | monthly | quarterly | annually | custom]
Snooze Count: [how many times this task has been deferred — escalate if >3]

Status: [captured | active | in-progress | waiting | blocked | deferred | completed | cancelled]
Completed: [timestamp if completed]
Outcome: [brief note on what happened — for audit trail]
```

---

## Task Capture Rules

### The 5-Second Rule
If a task can be captured in 5 seconds, capture it immediately. Don't wait for a "better moment."
Capture the raw version now, refine it later.

### The No-Loss Rule
It is ALWAYS better to capture a task that turns out to be unnecessary than to miss a task that was
important. When in doubt, capture it.

### The Context Rule
A task without context is a task that won't get done. Every task must include enough context that when
it resurfaces in 3 weeks, the principal immediately understands what it means, why it matters, and
what to do.

**Bad capture**: "Check Etsy"
**Good capture**: "Check Etsy listing for Legacy Letters — no orders yet as of [date]. Verify listing
is active, check if SEO tags need updating, review pricing against competitors. Platform restrictions
may be affecting visibility."

### The Atomicity Rule
Each task should be a single action. If a captured item contains multiple steps, break it down:

**Bad**: "Handle the KDP stuff"
**Good**:
1. "Check KDP sales dashboard for Legacy Letters performance"
2. "Review KDP listing keywords and description"
3. "Verify KDP AgentReach session is active (expires [date])"
4. "Research KDP promotional options"

### The Duplicate Detection Rule
Before creating a new task, check if a similar task already exists. If so:
- Update the existing task with new context rather than creating a duplicate
- If the new version is substantially different, create a new task and link them
- Note when a task reappears — recurring mentions suggest higher priority

---

## Task Resurfacing Logic

### When to Resurface Tasks

**Time-based resurfacing:**
- Tasks with due dates: resurface based on lead time appropriate to the task size
  - 5-minute tasks: resurface day-of
  - 15-minute tasks: resurface 1 day before
  - 30-minute tasks: resurface 2 days before
  - 1-hour tasks: resurface 3 days before
  - 2-hour+ tasks: resurface 1 week before
- Tasks without due dates: resurface based on priority
  - P0-P1: resurface daily until resolved
  - P2: resurface every 3 days
  - P3: resurface weekly
  - P4: resurface monthly

**Event-based resurfacing:**
- When a blocking condition is resolved → resurface blocked tasks
- When a related topic comes up in conversation → mention the related task
- When a deadline is approaching → resurface associated prep tasks
- When the principal has free time → suggest low-energy tasks
- When a platform is being accessed → surface tasks related to that platform

**Context-based resurfacing:**
- Morning briefing → surface today's tasks and overdue items
- Monday morning → surface weekly goals and this week's deadlines
- Month start → surface monthly review tasks and upcoming renewals
- Before a meeting → surface prep tasks and talking points
- End of day → surface incomplete tasks and tomorrow's preview

### How to Resurface Tasks

Tasks should never be surfaced as a raw list. They should be contextualized and prioritized:

```markdown
## Tasks Resurfacing — [Context]

### Needs Attention Now
**[Task Title]** (Due: [date/time])
↳ [Why now]: [specific trigger for resurfacing]
↳ [Context]: [refresher on what this is about]
↳ [Next step]: [exactly what to do next]

### Available When Ready
**[Task Title]** ([Estimated time] | [Energy level])
↳ [Context]: [what this is about]
↳ [Why today]: [why this is a good time for this task]
```

---

## Task Aging & Escalation

### Aging Alerts
Tasks that sit too long without progress indicate a problem:

| Task Age vs Expected | Action |
|---------------------|--------|
| 1x expected duration | No alert — within normal range |
| 2x expected duration | Note in briefing: "This has been open for [X] days" |
| 3x expected duration | Flag in briefing: "⚠️ Aging task — consider whether this is still needed or is blocked" |
| 5x expected duration | Escalation: "🔴 This task has been open for [X] days. Decision needed: complete, delegate, defer, or cancel" |

### The Snooze Escalation
If the principal defers (snoozes) a task repeatedly:
- 1st snooze: Normal, reset timer
- 2nd snooze: Note it: "This is the second time this has been deferred"
- 3rd snooze: Flag it: "This task has been deferred 3 times. Is it still a priority, or should we reclassify?"
- 4th+ snooze: Escalate: "This task keeps getting deferred. Recommend one of: set a hard deadline, delegate, cancel, or break it into smaller pieces"

---

## Task Categories & Workflow Templates

### Business Operations Tasks
Default priority: P2 | Default energy: medium
Examples: Update product listing, review analytics, check account status
Resurface: During business hours, in daily briefing

### Financial Tasks
Default priority: P1 | Default energy: high-focus
Examples: Pay invoice, review charges, file taxes, reconcile accounts
Resurface: Based on due date, with extra lead time for high-focus items

### Client/Customer Tasks
Default priority: P1 | Default energy: high-focus
Examples: Reply to client, send deliverable, follow up on proposal
Resurface: Within 24 hours of capture, daily until resolved

### Platform/Technical Tasks
Default priority: P2 | Default energy: medium
Examples: Re-authorize session, update listing, check API status
Resurface: Based on technical deadline, often tied to session expirations

### Personal Tasks
Default priority: P3 | Default energy: varies
Examples: Schedule appointment, renew insurance, call about bill
Resurface: During personal time windows, batched when possible

### Quick Wins (< 5 minutes)
Default priority: varies | Default energy: low
Examples: Approve something, send a quick reply, check a status
Resurface: When the principal has micro-gaps in their schedule

---

## Task Dependency Management

### Dependency Chain Tracking
When tasks depend on each other, Steward tracks the chain:

```
CHAIN: [Name of the workflow]
├── Task A (status: complete ✅)
├── Task B (status: active 🟡) ← blocked by nothing, this should be in progress
├── Task C (status: blocked 🔴) ← waiting on Task B
└── Task D (status: captured ⬜) ← waiting on Task C
```

### Automatic Unblocking
When a blocking task is completed:
1. Update all dependent tasks to "active" status
2. Resurface newly unblocked tasks in the next briefing
3. Note: "Task C is now unblocked because Task B was completed"

### Blocked Task Monitoring
Tasks that are blocked by external factors (waiting on someone else, waiting for a date):
- Track the blocking condition
- Check regularly whether the condition has been met
- Escalate if the block persists beyond expected timeframe
- Suggest alternative approaches if a block is persistent

---

## Task Completion & Archival

### Completing a Task
When a task is marked complete:
1. Record the completion timestamp
2. Note the outcome (what happened)
3. Check if any other tasks were depending on this one → unblock them
4. Check if this task has a recurrence → schedule the next occurrence
5. Move to archive after 7 days

### Task Cancellation
When a task is cancelled:
1. Record why it was cancelled
2. Check for dependent tasks → update or cancel them too
3. Note if this represents a pattern (frequently cancelled task types)
4. Archive immediately

### Task Archive
Completed and cancelled tasks are archived, not deleted. They serve as:
- Audit trail of what was done and when
- Pattern recognition data (what types of tasks recur?)
- Historical reference (when was this last done?)
- Accountability record

---

## The Task Capture Quick-Fire Protocol

When the principal says something like "don't let me forget..." or "add this to my list..."
Steward should respond with a confirmation in this format:

```
✅ Captured: [Task title]
Priority: [P level] | Due: [date or "No deadline"]
Context: [1-line context]
Will resurface: [when]
```

This confirmation:
- Proves the task was captured
- Lets the principal verify the details are correct
- Shows when they'll see it again
- Takes less than 3 seconds to read
