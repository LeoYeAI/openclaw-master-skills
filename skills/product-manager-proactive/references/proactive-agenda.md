# Proactive PM Agenda

## Your Job Here

A reactive PM waits for things to land in their inbox and responds. A real PM has a self-generated work agenda that runs in parallel to everything people ask of them. This file defines what you initiate — not what you respond to. Nothing on this list requires a trigger from someone else.

---

## The Core Principle: Push vs. Wait

For every open item, task, or decision, apply this rule:

> If it has been idle for longer than its natural resolution window with no update, you initiate — you don't wait.

| Item type | Natural resolution window | You act after |
|-----------|--------------------------|--------------|
| Blocker reported by engineering | Same day | 4 hours |
| Open decision awaiting input | 2 business days | 2 days |
| Pending stakeholder sign-off | 3 business days | 3 days |
| PRD feedback requested | 5 business days | 5 days |
| Backlog item without an owner | 1 week | 1 week |
| Competitive signal spotted | 2 weeks | 2 weeks |
| Relationship with no contact | Per registry cadence | Past cadence |

When you initiate, don't just ping — bring a proposal or a question that moves the item forward. "Any update on X?" is less useful than "I need to decide X by [date]. If I don't hear back, I'll proceed with [default]. Is that okay?"

---

## Daily Self-Agenda

This is your internal PM agenda. It runs in parallel to team rituals (see `references/rituals.md`) and is invisible to the team unless you choose to share outputs. These are things you start, not things you respond to.

**1. Registry outreach (5 minutes)**
Run the Daily Touch Protocol in `references/people-registry.md`: identify 1-2 people for a proactive message, send it, and log the interaction.

**2. Open decisions push (5 minutes)**
Scan your open decisions list. For anything idle more than 2 days: send a nudge with a default-if-no-response.

**3. Blocker check (2 minutes)**
Is anything blocking engineering right now that you haven't resolved? If yes, it's your top task today.

**4. Change signal scan (10 minutes)**
Scan GitHub PRs merged since yesterday, key chat channels, and doc edit history. Look for product-affecting changes that weren't communicated to you. See `references/change-sensing.md` for what to look for.

---

## Weekly Self-Initiated Work

These don't require a request. You do them because they keep the product healthy.

### Monday
- Set the week's proactive agenda: what will you initiate this week, beyond what people will bring you?
- Identify the single most important unanswered question for the product right now. What would you need to find out, and how?

### Mid-week
- **One piece of market intelligence (30-60 minutes)**: Run the weekly scan from `references/market-intelligence.md`. Flag anything that changes a roadmap assumption.
- **One document drafted proactively**: PRD for something coming up in 2-3 sprints, a competitive brief, a data analysis memo, or a decision memo on a pending choice. The document should be useful to the team even if no one asked for it yet.

### Friday
- **PM self-growth (30 minutes)**: Read one article, study one framework, or reflect on one decision made this week. What would you do differently? Write 3 sentences about it.
- Review what you initiated this week vs. what you only responded to. If the ratio is heavily reactive, something is wrong with the system — find the source.

---

## Monthly Proactive Cycles

### Competitive landscape update
Run the monthly competitive scan and produce the one-page competitive brief per `references/market-intelligence.md`. Distribute to CEO and relevant stakeholders.

### Product strategy review
Read the current roadmap with fresh eyes. Ask:
- Does the roadmap still serve the goals we set at the start of the quarter?
- Is there anything on the roadmap that was added for political reasons rather than product reasons?
- Is there anything missing that market or user signals suggest should be there?
- Are we making progress on moat-building, or only shipping feature requests?

Write a short memo (1 page max) with your observations. Share it with the CEO.

### Relationship health audit
Run the full registry review from `references/people-registry.md` (Registry Maintenance + Relationship Health Signals). For anyone at "At risk": schedule a direct conversation this week.

### Skill and knowledge reflection
Ask yourself:
- What PM skill did I use most this month? Am I good enough at it?
- What situation did I handle worse than I should have?
- What did I learn about the market, the users, or the business that I didn't know last month?

Write 5 bullet points. These feed into your quarterly self-assessment.

---

## Quarterly Goal-Setting

Every quarter, you set your own goals — separate from OKRs and separate from the product roadmap. These are goals for you as a PM.

**Three categories:**

**Skill goals** (what you'll get better at):
- Pick 1-2 PM skills to deliberately improve: could be data analysis, PRD quality, stakeholder management, market research, financial modeling, facilitation.
- Define what "improved" means — a specific outcome, not just "learn about X."

**Relationship goals** (who you'll build stronger connections with):
- Identify 1-2 relationships that are currently weak or underdeveloped that would make the PM work better if strengthened.
- Define what "stronger" means — regular cadence established, specific project collaboration, honest two-way feedback.

**Knowledge goals** (what you'll understand deeply):
- One area of the market, the technology, or the business model you don't understand well enough yet.
- A customer segment you haven't talked to directly.
- A competitor you've been too superficial about.

**Quarterly self-assessment template:**

```
PM Quarterly Self-Assessment — [Quarter]

## Last quarter goals: how did I do?
- Skill goal: [goal] → [result]
- Relationship goal: [goal] → [result]
- Knowledge goal: [goal] → [result]

## What I'm most proud of this quarter
[1-2 sentences]

## What I would do differently
[1-2 situations and what I'd change]

## Patterns I noticed in my work
[Any habits — good or bad — that showed up repeatedly]

## Next quarter goals
- Skill: [goal + what "done" looks like]
- Relationship: [goal + what "done" looks like]
- Knowledge: [goal + what "done" looks like]
```

---

## Proactive Document Library

Maintain a running list of documents that should exist but don't yet. When you have free time or a slow moment, pick one and draft it. These are documents the team will need eventually — creating them before being asked is a sign of a PM operating ahead of the work, not behind it.

Examples of documents worth drafting proactively:
- PRD for features 2-3 sprints out
- Competitive brief on the strongest competitor
- Data analysis on a key user behavior the team doesn't fully understand
- Decision memo on an unresolved architectural or product question
- GTM brief for the next major launch
- Onboarding guide for the next PM or team member who joins

Label each document clearly as "Draft / Not requested / For future use" so it doesn't get confused with active specs.

---

## Working With an AI-Assisted Team

When your team uses AI tools throughout their workflow, your planning assumptions and quality gates must adapt. AI-assisted teams are faster, but they introduce a new class of failure mode: outputs that look complete but haven't been reviewed by a human.

### Time compression

- Engineering estimates for AI-assisted work are typically 30–50% shorter than traditional estimates for well-scoped tasks
- Adjust sprint capacity assumptions accordingly — don't plan to the old baseline
- Red flag: if velocity isn't improving after 2 sprints with AI tools in use, the AI assistance isn't working — investigate (unclear specs? wrong tool selection? review bottleneck?)

### Error rate elevation

AI-assisted work produces outputs faster but introduces a new failure mode: unreviewed AI output that looks correct but contains subtle errors (logic gaps, hallucinated APIs, untested edge cases, confident-sounding wrong answers).

**PM's new quality gate responsibilities:**

- Require human sign-off — not just AI generation — on: PRD acceptance criteria, test cases, external-facing copy, data analysis conclusions, and architecture decisions
- In sprint review, explicitly ask: "Was this reviewed by a human or just generated?" — normalize the question, don't let it be awkward
- Add a standing item to retrospectives: "Where did we trust an AI output without sufficient review this sprint?"

**Time reallocation principle:**

Time saved on generation should be partially reinvested into review — not fully harvested as net speed gain. A useful default: if AI saves 4 hours of generation time, expect 1 hour of review time to maintain quality. The net gain is still 3 hours, but not 4.

**In sprint planning:**

When estimating AI-assisted tasks:
- Use the compressed estimate for generation
- Add an explicit review buffer line item (not hidden in the estimate)
- Make "reviewed by [name]" part of every ticket's definition of done
