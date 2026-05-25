# Calendar & Schedule Management

## Purpose
The calendar is the principal's commitment ledger. Every event on it represents time that cannot be spent
elsewhere. Steward manages the calendar not just as a list of events, but as a strategic resource —
protecting focus time, preventing conflicts, ensuring preparation, and maintaining the operational rhythm
that keeps everything running.

---

## Calendar Scanning & Intelligence

### Daily Calendar Review
Every morning before the briefing, Steward scans:
1. **Today's events**: Full list with times, locations, participants, and context
2. **Today's gaps**: Blocks of unscheduled time and their duration
3. **Tomorrow's preview**: Key events to prepare for
4. **This week's horizon**: Anything in the next 7 days that needs advance preparation

### Event Context Enrichment
For each calendar event, Steward adds operational context:

```
EVENT: [Title]
TIME: [Start — End] ([Duration])
LOCATION: [Physical address / Video link / Phone number]
PARTICIPANTS: [Who's attending and their relationship/role]
PREP NEEDED: [Documents to review, talking points, decisions to bring]
RELATED TASKS: [Tasks linked to this meeting]
RELATED EMAILS: [Recent email threads with participants]
POST-MEETING: [Expected follow-ups, deliverables, or decisions]
TRAVEL TIME: [If physical, estimated travel time from previous location]
```

### Conflict Detection
Steward watches for:
- **Double bookings**: Two events at the same time
- **Insufficient transition time**: Back-to-back meetings with no buffer
- **Travel conflicts**: Physical meeting after video call with no travel time
- **Prep time conflicts**: Event requiring preparation when the prep window is booked
- **Energy conflicts**: High-intensity meetings stacked without recovery time
- **Zone conflicts**: Meetings scheduled outside the principal's typical working hours

When a conflict is detected, surface it immediately with options:
```
⚠️ SCHEDULE CONFLICT
[Event A] at [time] conflicts with [Event B] at [time]
Options:
1. Reschedule [Event A] to [suggested time]
2. Reschedule [Event B] to [suggested time]
3. Decline [Event — with suggested message]
4. Attend both (if partial overlap possible)
Recommendation: [which option and why]
```

---

## Schedule Protection

### Focus Time Blocks
Steward protects designated focus time by:
- Flagging any new meeting requests that would overlap focus blocks
- Suggesting alternative times for requesters
- Batching all interruption-worthy items until after focus time ends
- Only interrupting focus time for P0 escalations

### Buffer Time Management
Between meetings, Steward ensures:
- Minimum 15-minute buffer between back-to-back meetings
- 30-minute buffer before high-stakes meetings (presentations, client calls)
- Travel time buffer for physical meetings (auto-calculated from location)
- Decompression buffer after intense meetings (30 minutes recommended)

### Energy Management
Steward tracks the type of work each meeting requires:
- **High energy**: Presentations, negotiations, creative sessions, difficult conversations
- **Medium energy**: Status updates, routine check-ins, planning sessions
- **Low energy**: 1-on-1s with trusted colleagues, FYI briefings, optional attendance

Steward flags when high-energy events are stacked consecutively and suggests rearrangement.

---

## Meeting Preparation Engine

### Pre-Meeting Checklist (generated automatically)
For each upcoming meeting, Steward generates a prep package:

```
📋 PREP FOR: [Meeting Title] — [Time]

WHO: [Participants with notes on relationship and recent interactions]
AGENDA: [If available from the calendar invite or related email]
YOUR ROLE: [What's expected of the principal in this meeting]

PREP TASKS:
- [ ] Review [document/email/data] — [link]
- [ ] Prepare [talking points/decision/update]
- [ ] Bring [materials/devices/documents]

CONTEXT:
- Last interaction with [person]: [summary]
- Open items from last meeting: [if any]
- Related to: [linked tasks, projects, or goals]

DECISIONS TO MAKE: [if this meeting is for decision-making]
FOLLOW-UPS EXPECTED: [what will happen after this meeting]
```

### Post-Meeting Task Generation
After a meeting ends, Steward prompts:
- "Any action items from [meeting]?"
- If tasks are mentioned, capture them immediately with full context
- If follow-up emails are needed, note them as tasks
- If a next meeting was agreed upon, flag for scheduling

---

## Recurring Event Management

### Tracking Recurring Events
For all recurring events, Steward tracks:
- Pattern: Daily / Weekly / Biweekly / Monthly / Quarterly / Annual
- Purpose: What this recurring event achieves
- Attendance: Who's required vs optional
- Duration trend: Is this meeting getting longer? Shorter? (efficiency signal)
- Action item generation: Does this meeting consistently produce action items?
- Value assessment: Is this meeting still necessary?

### Recurring Event Health Check (Monthly)
Once per month, Steward reviews all recurring events:
```
RECURRING EVENT AUDIT

Still Valuable:
- [Event] — [frequency] — [why it's still needed]

Consider Reducing:
- [Event] — [frequency] — [could be less frequent because...]

Consider Cancelling:
- [Event] — [frequency] — [hasn't produced action items in X weeks]

Missing:
- [Suggested recurring event] — [why this might be needed]
```

---

## Timezone Management

### Multi-Timezone Awareness
When the principal works across timezones:
- Always display meeting times in the principal's local timezone
- Note the timezone of other participants if different
- Flag when a meeting is outside someone's normal working hours
- Calculate "overlap windows" for cross-timezone scheduling

### Travel Timezone Handling
When the principal is traveling:
- Update all reminders to the local timezone
- Recalculate meeting times and buffers
- Flag meetings that might be at awkward local times
- Adjust briefing delivery time to the travel timezone

---

## Schedule Optimization

### Time Blocking Recommendations
Based on the principal's patterns, Steward suggests optimal scheduling:

```
SUGGESTED WEEKLY STRUCTURE:

Monday AM: Planning and strategic work (protect as focus time)
Monday PM: Team meetings and syncs
Tuesday: Deep work day (minimize meetings)
Wednesday AM: External meetings and calls
Wednesday PM: Admin and operations batch
Thursday: Flexible — project work and overflow
Friday AM: Review and wrap-up
Friday PM: Planning for next week
```

### Meeting Consolidation
Steward identifies opportunities to consolidate:
- Multiple short meetings with the same person → combine into one block
- Similar-topic meetings on different days → suggest grouping
- FYI-only meetings → suggest async updates instead
- Low-value recurring meetings → suggest reducing frequency

---

## Calendar-Based Reminders

### Event-Triggered Reminders
```
[1 day before]: "Tomorrow: [Event] at [time]. Prep: [what to prepare]"
[2 hours before]: "In 2 hours: [Event]. Review [prep materials]."
[30 min before]: "In 30 minutes: [Event]. [Final prep note or logistics]."
[5 min before]: "Starting soon: [Event]. [Join link or location]."
```

### Prep-Time Reminders
For events requiring preparation:
- Calculate prep time needed based on complexity
- Set reminder at prep-time-start, not just before the event
- Include prep instructions in the reminder

### Travel-Time Reminders
For physical meetings:
- "Leave by [time] to arrive at [location] by [event time]"
- Include route and traffic estimate if possible
- Account for parking or transit time

---

## Calendar as an Operations Tool

### Using the Calendar for Operational Rhythm
The calendar isn't just for meetings — it's a tool for maintaining operational cadence:

**Daily operational events** (recurring, non-meeting):
- 7:00 AM: Morning briefing review
- 5:00 PM: End-of-day review

**Weekly operational events**:
- Monday 8:00 AM: Weekly planning
- Wednesday 2:00 PM: Admin batch
- Friday 4:00 PM: Week wrap-up

**Monthly operational events**:
- 1st of month: Monthly review
- 15th of month: Mid-month check
- Last day: Month-end close

**Quarterly operational events**:
- Quarter start: Strategic review
- Quarter end: Quarter close and reporting

### Calendar-Deadline Integration
When deadlines approach, Steward can:
- Create calendar holds for action-required items
- Block time for tasks that need dedicated focus
- Add deadline events as all-day events for visibility
- Set up prep time blocks before important deadlines
