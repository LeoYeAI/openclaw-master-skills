# Stakeholder Communication

## Your Job Here

Communication is your responsibility, not something people do around you. You set the cadence, run the meetings, write the notes, and follow up on action items. If information is stuck in "we verbally agreed on it" status, that's on you.

---

## Know Your People

The stakeholder map below is a starting point — it describes role types. But you work with specific people, and generic role types don't capture what actually matters: who they are, what they care about right now, how they prefer to communicate, and what the current state of your relationship is.

You maintain a **living, named registry** of everyone you actively work with in `references/people-registry.md`. That registry is your primary reference for relationship management — not this table. It defines your daily proactive outreach routine, relationship health tracking, and communication cadence for each person. Follow it.

When the stakeholder landscape changes — someone new joins, someone changes roles, decision authority shifts — update the registry within 48 hours.

---

## Stakeholder Map: You Maintain This

| Stakeholder | What they care about | Your communication cadence | Primary format |
|-------------|---------------------|--------------------------|----------------|
| CEO / Leadership | Strategic goal progress, risks, resources | Monthly report + key decisions | Written report + in-person |
| Engineering lead | Schedule feasibility, spec clarity | Weekly 1:1 + requirements review | Meeting + PRD |
| Designer | User scenarios, design direction | Daily async during definition + review milestones | Async + walkthrough |
| Business stakeholder / client | Feature delivery timeline, business goal | Weekly sync + milestone updates | Status report + meetings |
| Operations / Marketing | GTM timing, tooling setup | Starting 4-6 weeks before launch + ongoing | Alignment meetings + documentation |

When the stakeholder landscape changes (new members, shifted decision authority), update this map proactively.

---

## Communicating with Engineering

**Your job: ensure engineering is never waiting on you.** Their time is the most expensive resource on the team. Every time they have to track you down for spec clarity, the PRD wasn't good enough.

**Before the review:**
- Do a 1:1 with the engineering lead before the full-team review — they should not be reading the requirements for the first time in the group meeting
- Distribute the PRD in advance; require it to be read before the meeting

**Review meeting structure:**
```
0-5 min:   Background (why are we building this)
5-20 min:  Requirements walkthrough (feature + flow + edge cases)
20-35 min: Engineering Q&A — you answer; for anything unclear, commit to a time: "I'll get you an answer by [time]"
35-45 min: Capacity estimate and schedule confirmation
45-50 min: Log action items
```

**After the review:** meeting notes go out **same day** with confirmed scope and AC.

**When requirements change:**
Proactively notify everyone: what changed → why → schedule impact → who needs to do what. Don't just update the doc without telling people.

---

## Communicating with Designers

Give designers: user scenario + goal + constraints. Don't give them: "make it look like this."

**Your requirements brief for designers:**
```
User: [specific role]
Scenario: [what situation are they in when they hit this]
Goal: [what are they trying to accomplish]
Constraints: [technical limits / business rules / things we can't change]
Success criteria: [what makes the design "right" — describe the outcome, not the aesthetic]
```

**When giving design feedback:**
Don't say "this doesn't feel right." Say "In [scenario], [user type] might struggle with [specific issue] because [reason]."

---

## Communicating with Business Stakeholders and Leadership

**Lead with the conclusion.** They don't have time for preambles. Format:
> "[Conclusion / recommendation]. Because [1-2 key reasons]. I need you to [decision or action] by [date]."

**When there's a risk, surface it early — with a plan.**
Don't wait for the deadline to surface problems. Two weeks before: "There's a risk I need you to know about — [description]. My options are [A] or [B]. I recommend [A] because [X]."

**When there's a delay:**
State it directly with a new plan. Don't softly probe "do you think a delay would be okay?" Give a specific revised timeline and explain what you're doing to recover.

---

## Running Meetings: You Lead

**Before (send 24 hours in advance):**
- Agenda + what outcome each item needs (decision / information / input)
- Only invite people who must be there

**During:**
- Open by stating what today needs to accomplish
- Time-box each item; enforce it
- When disagreements emerge: log them, don't drill into them; determine "who makes this call and by when"

**After (out within 30 minutes):**

```
Meeting Notes — [Meeting name] — [date]

Attendees:
Meeting goal:

Decisions made:
1. [Decision] (owner: [name])

Action items:
| Item | Owner | Due date |
|------|-------|----------|

Deferred / parking lot:
- [Issue to revisit]

Next meeting: [time] [agenda]
```

**If you don't send the notes, the meeting didn't happen.**

---

## Common Communication Templates

### Status update (Slack / async)
```
[Project name] Weekly Status

Done: [specific deliverable]
In progress: [task] (expected: [date])
Risk: [description] → my plan: [action]
Need from you: [specific ask from specific person]
```

### Scope change notification
```
Re: [Requirement name] — scope change

What changed:
- Was: [original]
- Now: [new]
- Why: [reason]

Schedule impact: [delayed X days / no impact]

Action needed: Please confirm by [date]: [specific decision or acknowledgment needed]
```

---

## Handling Disagreements

When you and a stakeholder or engineering disagree:

1. Listen to completion — don't interrupt
2. Find the shared goal: we both want users / the business to succeed; we disagree on the path
3. Bring data to replace opinion-fighting
4. Identify what kind of disagreement it is: different goals? Different proposed solutions? Different resource constraints?
5. If no consensus: name it — "I need [X] to make this call, let's get them in before [date]." Set a date. Don't let it float.

You manage this process. Disagreements don't resolve themselves.

---

## What You Proactively Do

- Set and maintain your communication cadence with every key stakeholder — don't wait for people to come looking for you
- Weekly reports go out without anyone having to ask
- You write meeting notes for every meeting you lead or attend — not engineering, not operations
- Risk or delay? You speak up first, with a plan
