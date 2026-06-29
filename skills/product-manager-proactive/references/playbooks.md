# PM Playbooks

High-frequency PM scenarios have a known shape. Each playbook tells you exactly what context to bring, what PM will produce, and how long it takes. Use the trigger phrase to start — no explanation needed.

---

## Quick Index

| Scenario | Trigger phrase | Time |
|----------|---------------|------|
| Weekly sprint planning | `run sprint planning playbook` | 15 min |
| Investor meeting prep | `run investor prep playbook` | 20 min |
| Metric drop analysis | `run metric drop playbook` | 15 min |
| Feature prioritization | `run feature prioritization playbook` | 10 min |
| GTM / launch decision | `run GTM playbook` | 15 min |
| User feedback synthesis | `run feedback synthesis playbook` | 10 min |

---

## Playbook 1: Weekly Sprint Planning

**Trigger:** `run sprint planning playbook`

**When to use:** Start of each week or sprint. You have a backlog and limited capacity and need a PM call on what's in vs. out.

**Context to bring:**
- Current phase and north star metric
- Team capacity this sprint (person-days)
- The backlog items being considered (paste as a list with rough effort estimates)
- Any hard deadlines or external commitments this sprint

**What PM produces:**
1. Prioritized list: items IN this sprint (with rationale) and items OUT (with rationale)
2. Any scope cuts recommended to keep the sprint achievable
3. One key risk to watch this sprint
4. The specific question PM needs answered before sprint start (if any)

**Output format:** Lightweight for solo founders. Full sprint plan table for teams.

**PM instruction:** Make the call directly. Don't present a ranked list and ask the founder to choose — give the final prioritization with explicit reasoning for each in/out decision.

---

## Playbook 2: Investor Meeting Prep

**Trigger:** `run investor prep playbook`

**When to use:** 24-72 hours before a fundraising conversation, board meeting, or investor update.

**Context to bring:**
- Meeting type (intro call / follow-up / board / update)
- Investor name and fund (if known — helps calibrate their typical focus)
- Current stage and what you're raising (amount, round)
- Key metrics: ARR or revenue, growth rate, DAU/MAU, retention, burn rate
- What's gone well since last conversation (if follow-up)
- What's not going well (be honest — PM will help you frame it)
- Your biggest ask or goal from this meeting

**What PM produces:**
1. Product narrative in 3 sentences: what it is, why now, why you win
2. Top 3 metrics to lead with and how to frame them
3. Top 5 questions investors typically ask in this context + PM's recommended answers
4. One thing to proactively address (the thing they'll ask that you don't want to be caught unprepared on)
5. Clear ask: what do you want them to do at the end of this meeting?

**Output format:** Always lightweight — bullets, no formal doc unless specifically requested.

---

## Playbook 3: Metric Drop Analysis

**Trigger:** `run metric drop playbook`

**When to use:** A key metric dropped and you need to understand why before deciding what to do.

**Context to bring:**
- Which metric dropped
- By how much (%, absolute number)
- Over what time period
- What the baseline was before the drop
- What changed in the product recently (releases, experiments, changes to onboarding, pricing, etc.)
- Any external factors (competitor launch, seasonality, platform outage)
- Data you already have (support ticket volume, cohort breakdown, error logs — paste what's available)

**What PM produces:**
1. Diagnosis structure: signal or noise? (Is this statistically meaningful?)
2. Top 3 hypotheses for the cause, ordered by likelihood
3. The one piece of data that would confirm or eliminate the most likely hypothesis
4. Recommended immediate action (investigate further / roll back / hold / communicate to stakeholders)
5. Timeline: when do we need a conclusion, and what happens at each checkpoint?

**PM instruction:** Don't speculate without data. If the context provided isn't enough to form a hypothesis, state exactly what data is needed and why. Don't produce a hypothesis that can't be tested.

---

## Playbook 4: Feature Prioritization Decision

**Trigger:** `run feature prioritization playbook`

**When to use:** You have multiple features competing for limited development time and need a PM call on what gets built next.

**Context to bring:**
- The features being considered (paste as a list)
- Rough effort estimate for each (person-days or t-shirt sizing)
- Current north star metric or top goal
- Any hard deadlines or commitments affecting the decision
- ICP: who is the target user right now
- What you know about user demand for each feature (requests, frequency, who's asking)

**What PM produces:**
1. A direct prioritization call: feature 1 first, then feature 2, features 3+ deferred
2. For each feature: one sentence on why it's in or out
3. The key assumption underlying the top recommendation — what would change it
4. What to tell users or stakeholders about the deferred items

**PM instruction:** Give the final answer, not a scoring matrix for the founder to evaluate. If two items are genuinely equal, say so and ask the one clarifying question that would break the tie.

---

## Playbook 5: GTM / Launch Decision

**Trigger:** `run GTM playbook`

**When to use:** A feature or product is ready (or nearly ready) to ship and you need to decide: is this ready to launch, and how?

**Context to bring:**
- What's being launched (feature / product / update)
- Current state: what's done, what's still in progress
- Target user: who is this for
- Launch type being considered: internal / soft launch / hard launch / public announcement
- GTM readiness: has marketing / sales / support been briefed? Is docs/changelog ready?
- Key metrics baseline: what are the current numbers before launch
- Any known risks or open questions

**What PM produces:**
1. Go / no-go recommendation with explicit reasoning
2. If no-go: the specific 1-2 blockers and what it takes to clear them
3. If go: soft launch vs hard launch recommendation and the criteria to move from soft to hard
4. What to monitor in the first 72 hours and what thresholds trigger a rollback conversation
5. One-paragraph launch communication for the team (internal, not marketing copy)

For full launch checklist and signal monitoring framework, load `references/launch.md`.

---

## Playbook 6: User Feedback Synthesis

**Trigger:** `run feedback synthesis playbook`

**When to use:** You have a pile of raw feedback — support tickets, NPS comments, user interview notes, App Store reviews — and need to extract what to actually do with it.

**Context to bring:**
- The raw feedback (paste directly — quotes, ticket summaries, interview notes)
- Source of the feedback (support / NPS / interviews / reviews / sales calls)
- Approximate volume and time range
- Current product focus or ICP (so PM can weight feedback from the right users more heavily)
- Any hypothesis you already have about what the feedback will show

**What PM produces:**
1. Top 2-3 themes with supporting evidence (verbatim quotes where possible)
2. For each theme: is this a bug, a missing feature, a UX problem, or a positioning mismatch?
3. Recommended action for each theme: fix now / add to backlog / needs more research / not our problem
4. One surprising or counterintuitive signal in the data (if any)
5. What to watch for in the next feedback cycle

**PM instruction:** Weight feedback from ICP users more heavily than general feedback. If the feedback contains requests that don't match the ICP, note it but don't let it drive the recommendation.

---

## Adding a New Playbook

When a new high-frequency scenario emerges that doesn't fit an existing playbook, define it using this template:

```
## Playbook N: [Name]

**Trigger:** `run [name] playbook`
**When to use:** [one sentence]
**Context to bring:** [bulleted list]
**What PM produces:** [numbered list of outputs]
**PM instruction:** [any specific behavioral guidance]
```

Add it to the Quick Index at the top.
