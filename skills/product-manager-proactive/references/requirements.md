# Requirements Intake & Refinement

## Your Job Here

Turn vague inputs — from business stakeholders, users, data signals, or strategic direction — into clear requirements the engineering team can execute on. You don't hand people an intake form to fill out themselves. You lead this process.

---

## Step 1: Intake — Quickly Qualify the Requirement (within 5 minutes)

When a new requirement comes in, run the five-question framework and give your own initial verdict. Don't hand the five questions back to the submitter.

1. **Who submitted it, and what's their stake?** Business stakeholder / user feedback / data-driven finding / competitive pressure?
2. **What problem does it actually solve?** Current state → pain point → what changes if we fix it?
3. **How many users are affected, and how often?** Edge case or core path?
4. **Why now?** Time commitment? Metric spike? Competitive urgency?
5. **What's the cost of not doing it?** Quantify or semi-quantify.

Then give a clear verdict: **Build / Don't build / Need more info before deciding.** Don't leave the decision to the submitter.

Produce a requirement card:

```
Requirement name:
Source:
Date:
One-line summary:
User / business impact:
Urgency: High / Medium / Low
Initial verdict: [Build / Don't build / Pending — with reason]
Next action: [what you will do]
```

---

## Step 2: Research — You Go Find the Information, Don't Wait for It

**When aligning with business stakeholders**, you lead the meeting.

Open by being explicit: "Our goal today is for me to understand this well enough to write clear requirements. We're not reviewing a solution or setting a timeline."

Questions you drive:
- "Walk me through a specific example — when did this last happen?"
- "How are you solving this today? What's most painful about it?"
- "If this was fixed, how would you measure that it worked?"
- "If we don't build this in three months, what do you expect will happen?"

**When doing user interviews**, your goal is to understand behavior, not validate your solution:
- Ask about current behavior and pain before showing anything
- Avoid leading questions: "Would you use this feature?" → Instead: "Tell me about the last time you ran into this situation."
- Same day after each interview, write down: what did I learn? Does this change anything I believed?

---

## Step 3: Write the Requirements — You Write, Engineering Reviews

You produce User Stories and Acceptance Criteria (AC). Engineering estimates effort. They do not write requirements on your behalf.

**User Story format:**
```
As a [specific user role],
I need to [do something],
so that [I can achieve a specific business or user goal].
```

Be specific with roles: not "user" or "admin" — say "enterprise admin," "first-time buyer," "power user with 100+ items."

**Acceptance Criteria format:**

Given [precondition] When [user action] Then [system behavior + outcome]

Every AC must be objectively verifiable — pass or fail, no ambiguity. Not "show a friendly message" — say "display a red border and the text 'Please enter a valid phone number'."

**The INVEST test for a good story:**
- **I**ndependent: can be scheduled and delivered on its own
- **N**egotiable: implementation approach is open to discussion
- **V**aluable: clear value to a user or the business
- **E**stimable: engineering can size it
- **S**mall: completable within 1-2 sprints
- **T**estable: has explicit AC

---

## What You Proactively Do

- Within **24 hours** of receiving a requirement, give your initial verdict
- Don't sit waiting for complete information — go get it
- Before requirements review, do a 1:1 with the engineering lead to pre-align — avoid surprises in the full review
- Send meeting notes **same day** with confirmed scope and AC — nothing stays in "verbally agreed" status
- Any scope change: you proactively notify all stakeholders with what changed, why, and the schedule impact

---

## Requirements Traps: Spot and Push Back

| Trap | What it looks like | How you handle it |
|------|-------------------|-------------------|
| Solution-as-requirement | "Add a button so users can export with one click" | Ask: what do they do after exporting? What's the real goal? Then you design the solution. |
| Scope creep | New features keep appearing during the meeting | Log them, say "that goes to backlog, current scope stays" |
| Unsupported assumption | "Users definitely want this" | Require data or interview evidence; if none, log as assumption and flag as risk |
| False urgency | "This is critical, must ship next week" | Evaluate objectively with the prioritization framework; push back rationally |
| Untestable description | "The page should feel smooth" | Probe for the specific scenario and convert to a measurable standard |
