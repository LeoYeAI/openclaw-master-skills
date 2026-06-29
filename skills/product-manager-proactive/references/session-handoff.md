# Session Handoff

## Why This File Exists

Claude has no persistent memory across conversations. Without a structured handoff format, every new session starts from zero — the PM re-asks questions, the founder re-explains context, and quality suffers. This file solves that through a closed loop:

```
Session ends → PM produces Session Summary Card
     ↓
Founder stores card in Notion / Notes
     ↓
Next session: paste card into Quick Re-entry (onboarding.md)
     ↓
PM operational in 30 seconds
```

---

## 1. Session Summary Card

**PM produces this at the end of every working session — without being asked.**

Any conversation where a product decision was made, a priority was set, or meaningful context was established should end with this card. Label it clearly so the user knows to save it.

```
---
## Session Summary — [YYYY-MM-DD] | [3-word topic]

### Decisions made
- [Decision]: [one sentence + key reason]
- [Decision]: [one sentence + key reason]

### Open items (not resolved this session)
- [Item]: [what's blocking it + who needs to act + by when]

### State for next session — paste this into Quick Re-entry
  Product: [name]
  Phase: [Discovery / Definition / Development / Launch / Growth]
  This week's most important thing: [updated one sentence]
  Current biggest blocker: [updated one sentence]
  What I need from PM next time: [sprint planning / investor prep / metric drop / feature decision / other]
---
```

**When to produce it:** at the end of any session longer than 10 minutes or any session where a decision was made. If the user says "thanks, bye" or signals they're done — output the card before closing.

**How to signal it:** start the card with "— Save this for next time —" so it's visually obvious.

---

## 2. Re-hydration: Closing the Loop

The "State for next session" block in the card IS the Quick Re-entry template. When the user opens a new conversation:

1. Paste the "State for next session" block from the last card
2. Add or update the "What I need from PM today" line
3. PM confirms state in one sentence and enters working mode

No other onboarding needed. The full 7-question onboarding in `references/onboarding.md` only runs when there is no prior context at all.

**If the card is partial or outdated:** PM fills in what's missing with explicit assumptions, then proceeds. Never stall waiting for complete information.

---

## 3. Cross-Team Handoff Format

Use when PM passes work to engineering, design, marketing, or ops. The receiving team should be able to execute without a follow-up question.

```
## Handoff: [what is being handed off] — [date]

From: PM
To: [team / person]

Context
[Why this work exists. What decision or user insight led to it. 2-3 sentences max.]

What is decided (not up for re-discussion)
- [Decision 1]
- [Decision 2]

What is open (your call to make)
- [Open question 1 + what PM needs back]
- [Open question 2 + what PM needs back]

Output needed from you
[Specific deliverable + deadline]

Definition of done
[How PM will know the handoff is complete — not "done" in an abstract sense]

Escalation path
[If something is blocked or unclear: contact PM via [channel] within [timeframe]]
```

**Common mistakes to avoid:**
- Don't hand off without stating what's already decided — teams re-debate closed questions
- Don't hand off without a deadline — work without a deadline doesn't get done
- Don't hand off without a definition of done — "done" means different things to different teams

---

## 4. Colleague Handoff

Use when another person is temporarily covering PM work, or when PM transitions a project to a new PM.

This is lighter than onboarding — the person has context on the company and team, just needs the product-specific state.

```
## PM Coverage Handoff — [coverage dates]

Covering: [name]
Product: [name] | Phase: [phase]

Current state (30-second version)
[2-3 sentences: what the team is building, what the top priority is, what's at risk]

Active decisions in flight
| Decision | Status | Who's involved | What's needed |
|----------|--------|----------------|---------------|
| [decision] | [waiting on X / in review / blocked] | [people] | [what needs to happen] |

Do not change without checking with PM first
- [High-stakes item 1 + why]
- [High-stakes item 2 + why]

Safe to decide independently
- [Low-stakes item + guidance if needed]
- [Low-stakes item + guidance if needed]

Recurring outputs to send while PM is away
| Output | Audience | Cadence | Template location |
|--------|---------|---------|------------------|
| [report name] | [who] | [weekly / monthly] | [link or doc name] |

On return: PM needs a summary of decisions made and any changes to the product state.
```
