---
name: decision-mental-models
description: Apply the most relevant mental models (First Principles, Inversion, Second-Order Thinking, Occam's Razor, and 16 others) to any problem or decision, surfaces non-obvious insights by explicitly matching and working through 2-3 models per query.
version: 1.0.0
homepage: https://github.com/arbazex/decision-mental-models
metadata: {"openclaw":{"emoji":"🧠"}}
---

## Overview

This skill turns any problem or decision into a structured thinking exercise. Given a user's situation, the agent selects the 2–3 most relevant mental models from a library of 20 well-established frameworks, applies each one explicitly with worked reasoning, and surfaces non-obvious insights the user is unlikely to reach through intuitive thinking alone. The skill does not give advice, it reveals structure.

---

## When to use this skill

**Trigger on any of the following:**

- User presents a problem they are stuck on or unsure how to approach
- User faces a decision between two or more options
- User asks "how should I think about X?" or "what am I missing?"
- User describes a situation that feels complex, unclear, or emotionally loaded
- User says "help me decide", "what would you do", "I keep going in circles", or "what's the best way to approach this?"
- User is planning something and wants to stress-test assumptions
- User is explaining a failure and wants to understand what went wrong

**Do NOT trigger on:**

- Requests for factual lookups, definitions, or research summaries with no decision component
- Pure creative writing tasks
- Technical tasks (code, data, math) where reasoning frameworks would not add value
- Small talk or casual conversation with no substantive problem

---

## Instructions

### Step 1 — Extract the problem

Read the user's message carefully. Identify:
- The core tension or question (what decision or problem is actually at stake?)
- The domain (career, business, relationships, learning, finance, strategy, etc.)
- Whether the user is stuck on understanding, deciding, or planning
- Any assumptions the user appears to be making without questioning

If the problem is too vague to apply models to, ask one clarifying question before proceeding. Do not ask more than one question.

---

### Step 2 — Select 2–3 mental models

Using the **Mental Model Library** (Step 4), identify which 2–3 models are most structurally relevant to this specific problem. Use the **When to Apply** column for each model to guide your selection.

Prioritize models that:
- Reveal a blind spot the user's framing is hiding
- Challenge the default direction of their thinking
- Complement each other without being redundant

Do NOT select models just because they are famous. Select them because they fit.

---

### Step 3 — Apply each model explicitly

For each selected model, structure your output as follows:

```
### [Model Name]
**What it asks:** [The core question this model poses]
**Applied to your situation:** [Work through the model using the user's specific details]
**Non-obvious insight:** [State the one thing this model reveals that straight thinking would miss]
```

Do not summarize the model generically. Every sentence in the application must reference the user's actual situation.

---

### Step 4 — Mental Model Library

Below are the 20 mental models available to this skill. Each entry includes: what it is, when to apply it, the core question it answers, and a worked example from real life.

---

#### 1. First Principles Thinking
**What it is:** Decompose a problem down to its most fundamental verified truths, then reason upward from those truths rather than from analogy or convention.
**When to apply:** When the user seems to be accepting inherited assumptions, when conventional solutions feel expensive or broken, or when the user is trying to innovate rather than iterate.
**Core question it answers:** What do I know is actually, provably true, and what am I just assuming?
**Worked example:** Elon Musk asked why rockets cost $65M. Industry said "that's just what rockets cost." First principles: what are the raw material costs? ~2% of retail price. So he founded SpaceX to manufacture rockets from scratch, cutting costs by an order of magnitude.

---

#### 2. Inversion
**What it is:** Instead of asking "how do I achieve X?", ask "what would guarantee I fail at X?" Then systematically avoid those failure conditions.
**When to apply:** When the user is planning something ambitious and overlooking risks, when they are stuck trying to force a positive solution, or when the problem involves avoiding a bad outcome.
**Core question it answers:** What would make this go terribly wrong, and am I already doing those things?
**Worked example:** Charlie Munger didn't ask "how do I build wealth?" He asked "what behaviors reliably destroy wealth?", speculation, debt, envy, short-termism. Avoiding those behaviors consistently was itself the strategy.

---

#### 3. Second-Order Thinking
**What it is:** Go beyond the immediate consequence of a decision. Ask "and then what?" repeatedly to trace downstream effects, the effects of the effects.
**When to apply:** When the user's plan has a compelling first-order benefit, when a decision affects many people or a complex system, or when past "solutions" in this domain have created new problems.
**Core question it answers:** What happens after what happens next?
**Worked example:** A government lowers interest rates to stimulate the economy (first order: cheap credit, more spending). Second order: asset price inflation. Third order: wealth inequality widens as asset owners benefit disproportionately. The solution created a new problem.

---

#### 4. Occam's Razor
**What it is:** When multiple explanations exist, prefer the one requiring the fewest assumptions. Complexity is a liability until it is proven necessary.
**When to apply:** When the user is constructing an elaborate theory to explain something, when they are overthinking a situation, or when they are choosing between a simple and complex solution.
**Core question it answers:** Am I adding complexity that isn't justified by evidence?
**Worked example:** A startup's sales dropped 40% last month. They hypothesize: algorithm change, competitor launch, pricing mismatch, seasonal shift, and three other theories. Occam's Razor: check the simplest explanation first — did a key sales rep leave or did a major client churn? Usually one change explains the data.

---

#### 5. The Map Is Not the Territory
**What it is:** Your mental model of reality is always an abstraction. Every map omits details. Mistaking your representation of a situation for the situation itself causes error.
**When to apply:** When the user is highly confident in their understanding, when they are surprised that something "isn't working as expected," or when their plan was built from theory rather than direct observation.
**Core question it answers:** Where might my mental model be misleading me about what's actually happening?
**Worked example:** A manager designs a perfect-looking process on paper. In practice, employees skip step 3 every time because the tool required doesn't work on their machines. The map (process doc) was not the territory (how work actually gets done).

---

#### 6. Circle of Competence
**What it is:** You have domains where your knowledge is deep and reliable, and domains where it is shallow and borrowed. Decisions made inside your circle are more likely to succeed than those made outside it.
**When to apply:** When the user is entering a new domain, when confidence seems disproportionate to actual experience, or when they are relying on second-hand knowledge to make a high-stakes choice.
**Core question it answers:** Am I operating inside or outside the boundary of what I actually know well?
**Worked example:** Warren Buffett consistently declined to invest in tech companies during the dot-com boom because they were outside his circle. While others chased 100x returns and lost everything, his disciplined boundary-keeping preserved capital.

---

#### 7. Opportunity Cost
**What it is:** Every choice you make eliminates other choices. The true cost of any decision includes the value of the best alternative you gave up.
**When to apply:** When the user is evaluating an option in isolation, when they are debating whether to continue something they've already started, or when time or attention is the scarce resource.
**Core question it answers:** What am I giving up by choosing this — and is this worth more than that?
**Worked example:** A developer spends six months building a custom internal tool. Opportunity cost: those six months could have gone to a revenue-generating product feature. The tool cost far more than its $0 license fee.

---

#### 8. Sunk Cost Fallacy
**What it is:** Resources already spent (time, money, effort) are gone regardless of what you do next. They should have zero weight in forward-looking decisions. Continuing a bad path to "not waste" past investment is irrational.
**When to apply:** When the user is reluctant to abandon something because of how much they've already invested, when they say "I've come too far to quit," or when path dependency seems to be driving the decision.
**Core question it answers:** If I were starting fresh today, would I choose this path?
**Worked example:** A startup has spent $2M building a product with no user traction. The team argues for another $500K to "fix" it because "we can't walk away now." The right question: given what we know today, is this the best use of $500K? The $2M is irrelevant.

---

#### 9. Regret Minimization Framework
**What it is:** Project yourself forward to age 80, looking back. Which choice would you regret more? Minimize regret over the long arc of life, not the discomfort of the immediate moment.
**When to apply:** When the user is making a major life or career decision and is paralyzed by short-term fear, when security is competing against meaning, or when they describe playing it safe as the default.
**Core question it answers:** In thirty years, which option will I wish I had chosen?
**Worked example:** Jeff Bezos was deciding whether to quit his lucrative hedge fund job to start Amazon. He asked: at 80, would I regret not trying? Yes. Would I regret trying and failing? No. Decision made.

---

#### 10. Hanlon's Razor
**What it is:** Never attribute to malice what can be adequately explained by ignorance, carelessness, or incompetence. People are mostly distracted and overwhelmed, not plotting against you.
**When to apply:** When the user is interpreting someone else's behavior as hostile or intentional, when there is conflict in a team or relationship, or when the user is building a narrative around bad intent.
**Core question it answers:** Is there a simpler, less sinister explanation for this behavior?
**Worked example:** A colleague doesn't respond to three emails. The user concludes they're being undermined. Hanlon's Razor: the colleague has 200 unread emails and forgot. Assuming incompetence before malice leads to a collaborative resolution instead of an escalating conflict.

---

#### 11. Feedback Loops
**What it is:** Systems produce outputs that feed back into their own inputs, either amplifying change (reinforcing loop) or dampening it (balancing loop). Identifying the dominant loop predicts long-term system behavior.
**When to apply:** When the user is trying to create lasting behavior change, when a situation seems self-perpetuating, or when small changes are either compounding or getting absorbed.
**Core question it answers:** Is this system accelerating, stabilizing — and what drives that dynamic?
**Worked example:** A product gets bad reviews (output) → fewer new users → less revenue → less investment in product quality → worse product (input) → more bad reviews. This is a reinforcing (death spiral) loop. Breaking one link — say, responding publicly to reviews — can interrupt the cycle.

---

#### 12. Probabilistic Thinking
**What it is:** Assign explicit probabilities to outcomes rather than treating uncertainty as binary (will happen / won't happen). Update those probabilities as new evidence arrives.
**When to apply:** When the user is treating a likely outcome as certain or an unlikely one as impossible, when they are making decisions under uncertainty, or when they describe a risk as "it probably won't happen."
**Core question it answers:** What is my actual estimated probability for each outcome — and is my behavior calibrated to that?
**Worked example:** A founder says "the market won't reject this product." Probabilistic thinking: what's the base rate of new products achieving product-market fit? ~10–20%. Given this, how much runway should we reserve? That number changes every financial decision.

---

#### 13. Thought Experiments
**What it is:** Run a mental simulation of a scenario that cannot be tested in reality — to stress-test assumptions, explore implications, or reveal hidden consequences before committing.
**When to apply:** When the user faces a high-stakes irreversible decision, when they want to test a hypothesis without real-world risk, or when they are trying to anticipate how a plan might break.
**Core question it answers:** If I run this forward in my mind as honestly as possible, what happens?
**Worked example:** "If we cut prices by 30%, what happens?" Thought experiment: competitors match the cut within 60 days (they've done it before), margins collapse, and the lower price becomes the new anchor. Now the question shifts to whether the volume gain justifies permanently thinner margins.

---

#### 14. Pareto Principle (80/20 Rule)
**What it is:** Roughly 80% of effects come from 20% of causes. In most systems, inputs are not distributed evenly — a small number of factors drive the majority of outcomes.
**When to apply:** When the user is overwhelmed by options or tasks, when resources are constrained, or when they are trying to prioritize without a clear framework.
**Core question it answers:** Which 20% of inputs is generating 80% of the results — and am I focusing there?
**Worked example:** A consultant reviews a client's revenue. Top 3 clients (out of 40) account for 78% of revenue. Every operational improvement should prioritize retention and expansion of those 3 clients before anything else. The other 37 are not equally important.

---

#### 15. Activation Energy
**What it is:** Every behavior change or system reaction requires a minimum threshold of energy input before it begins. Reducing that threshold makes change dramatically more likely.
**When to apply:** When the user is trying to build a new habit, change behavior in others, launch a product, or remove friction from a process.
**Core question it answers:** What is the minimum barrier that must be lowered to make this actually happen?
**Worked example:** A team wants engineers to write documentation. Making it a 10-step process in a separate tool means it rarely happens. Moving documentation into the same PR workflow — one text field — collapses the activation energy. Completion rates triple.

---

#### 16. Dunning-Kruger Effect
**What it is:** People with limited knowledge in a domain tend to overestimate their competence, while genuine experts tend to underestimate theirs. Awareness of where you sit on this curve is a calibration tool.
**When to apply:** When the user expresses high confidence early in their learning of a domain, when they are surprised something "didn't work," or when they are dismissing expert caution.
**Core question it answers:** Am I at the peak of "beginner confidence," and what would a genuine expert notice that I'm missing?
**Worked example:** A first-time investor has 3 months of profitable trades and declares the strategy foolproof. A genuine expert recognizes this as a favorable market phase, not validated skill. The expert's uncertainty is the calibrated position.

---

#### 17. Chesterton's Fence
**What it is:** Do not remove or change something until you understand why it was put there in the first place. Rules, processes, and structures that look pointless often encode forgotten wisdom.
**When to apply:** When the user wants to eliminate a rule, process, or constraint that seems outdated or unnecessary, or when they are redesigning a system they inherited.
**Core question it answers:** Do I understand why this exists before I dismantle it?
**Worked example:** A new engineering manager removes the "slow" code review process. Within two months, production bugs increase 4x. The review process existed because a critical system has no automated test coverage — the reviewers were the last line of defense.

---

#### 18. Availability Heuristic (Bias Awareness)
**What it is:** The human mind overweights examples that come easily to memory. Vivid, recent, or emotionally charged events feel more probable than they statistically are.
**When to apply:** When the user's risk assessment seems driven by a recent dramatic event, when they are generalizing from one or two memorable cases, or when fear or excitement seem disproportionate to base rates.
**Core question it answers:** Am I overweighting this because it's vivid and recent, not because it's statistically likely?
**Worked example:** A founder refuses to raise venture capital because they personally know two founders who were pushed out by investors. The base rate of founder-VC conflict resulting in removal is rare. Their fear is calibrated to anecdote, not data.

---

#### 19. Margin of Safety
**What it is:** Build explicit buffers into any plan to account for uncertainty, error, and events you cannot predict. The buffer size should scale with the stakes and irreversibility of the decision.
**When to apply:** When the user's plan works only if everything goes right, when they are operating near a critical threshold (financial, physical, temporal), or when the downside of failure is severe.
**Core question it answers:** What happens if I'm 20% wrong — and have I built in room for that?
**Worked example:** A construction engineer designing a bridge for 10,000kg loads builds it to withstand 50,000kg. Not because they expect that load — because they cannot model every future scenario perfectly. The margin of safety is the acknowledgment that models fail.

---

#### 20. Systems Thinking
**What it is:** View a situation as a network of interacting components where behavior emerges from relationships and feedback, not just from individual parts in isolation.
**When to apply:** When isolated fixes keep creating new problems, when blame is being assigned to individuals in a problem that is clearly recurring, or when the user is dealing with organizational or social complexity.
**Core question it answers:** What is the structure of this system — and is the problem in the parts or in how they interact?
**Worked example:** A company fires its third Head of Sales in two years for "underperformance." Systems thinking: if three different people fail in the same role, the system (incentives, tools, territory, product-market fit) is likely the variable — not individual capability. Hire a fourth without changing the system and the outcome repeats.

---

### Step 5 — Synthesis

After applying 2–3 models, write a one-paragraph synthesis that:
- States what the models collectively reveal
- Identifies the highest-leverage decision or action point
- Names any remaining uncertainty the user should sit with before deciding

Keep this synthesis under 100 words. It should not repeat the model applications — it should integrate them.

---

### Step 6 — Optional follow-up

After your synthesis, offer one of the following (not both):

- A follow-up question that would sharpen the analysis if the user wants to go deeper
- A suggestion of one more model that might apply if the user wants to explore a different angle

Do not offer unsolicited action plans, implementation advice, or emotional support unless the user asks.

---

## Rules and guardrails

- **Never apply models generically.** Every application must use the user's specific situation, domain, and details. Generic explanations of models that could apply to anyone are a failure state.
- **Never apply more than 3 models per response.** More models dilute insight. Depth beats breadth.
- **Never fabricate examples or statistics.** The worked examples in the library are established historical examples. Do not invent new ones to appear more relevant.
- **Never give direct advice disguised as model output.** The models reveal structure; the user makes the decision. Do not use the framework to smuggle in a preferred recommendation.
- **Never apply this skill to requests for medical, legal, or financial decisions where professional expertise is required.** You may apply models to help the user think — but explicitly state that professional advice is required before acting.
- **Do not moralize.** If the user is considering a legal action you personally find questionable, apply the requested models without commentary on the ethics of the choice. The skill is a thinking tool, not a values filter.
- **Never apply the Dunning-Kruger model to imply the user is incompetent.** Frame it as calibration, not criticism.
- **Do not stack models that are largely redundant for a given problem.** Occam's Razor and Hanlon's Razor applied to the same interpersonal conflict, for instance, overlap substantially — choose one or explain the distinction clearly.

---

## Output format

Structure every response as follows:

```
## Mental Model Analysis

**Problem identified:** [One sentence stating the core tension or decision]
**Domain:** [Career / Business / Relationships / Finance / Learning / Strategy / Other]
**Models selected:** [List 2–3 model names with one-line rationale for each selection]

---

### [Model 1 Name]
**What it asks:** ...
**Applied to your situation:** ...
**Non-obvious insight:** ...

---

### [Model 2 Name]
**What it asks:** ...
**Applied to your situation:** ...
**Non-obvious insight:** ...

---

### [Model 3 Name — if applicable]
**What it asks:** ...
**Applied to your situation:** ...
**Non-obvious insight:** ...

---

## Synthesis
[One paragraph integrating the insights across models]

---
[Optional follow-up question or model suggestion]
```

Use plain Markdown. No tables unless the user specifically asks for comparison output. No bullet walls — write in short, direct prose within each section.

---

## Error handling

**Problem is too vague to apply models:**
→ Ask exactly one clarifying question: "To apply the right mental models, can you tell me: what decision or problem is at the centre of this — what are you actually trying to figure out?"
→ Do not proceed until you have a substantive problem to work with.

**User asks for all 20 models applied:**
→ Respond: "Applying all 20 would dilute the analysis. To give you genuine insight, I'll select the 2–3 models that are structurally most relevant to your specific situation — that's where the value is."
→ Then proceed with the standard selection process.

**User disagrees with the model selection:**
→ Acknowledge their view. Ask which model they think applies and why. Apply it alongside one of your original selections. Do not abandon your selection without the user providing a reason.

**User presents a problem requiring professional expertise (legal, medical, financial):**
→ Apply the requested mental model analysis, then add: "Note: the models above can sharpen your thinking, but this decision warrants professional [legal/medical/financial] advice before acting."

**User asks what mental models are or requests an explanation:**
→ Briefly explain (2–3 sentences) what mental models are, then ask for the problem or decision they'd like to apply them to.

---

## Examples

### Example 1 — Career decision

**User:** "I've been at my company for 6 years. I have a stable, well-paying job I don't hate. A startup just offered me a role that pays 20% less but has equity. I can't decide."

**Agent selects:** Regret Minimization, Opportunity Cost, Second-Order Thinking

**Regret Minimization:**
What it asks: At age 80, which choice will I wish I had made?
Applied: Six years from now, if the startup fails, would you regret trying? Probably not — the experience and network would compound. If you stay and watch the startup succeed without you, would you regret it? Likely yes. The asymmetry of regret favors the move.
Non-obvious insight: The fear driving the decision is short-term income loss, not long-term regret — and those are different variables.

**Opportunity Cost:**
What it asks: What am I giving up by choosing this?
Applied: Staying means giving up the equity upside, the acceleration of a startup environment, and the signal that you took a risk when you had the chance. Leaving means giving up stability, a known culture, and 20% immediate income. The real question is: which of these is harder to recover?
Non-obvious insight: Income is recoverable. The window to join an early-stage company at your experience level may not reopen.

**Synthesis:** Both models point to the same asymmetry — the downside of leaving is recoverable (income), while the downside of staying is harder to undo (the opportunity closes). The remaining uncertainty is the startup's specific probability of reaching a meaningful exit, which requires due diligence on their runway, traction, and team — not more deliberation on the general question.

---

### Example 2 — Team/organizational problem

**User:** "Our product team keeps shipping features that customers don't use. We've tried better prioritization frameworks and they don't stick. What are we missing?"

**Agent selects:** Systems Thinking, Chesterton's Fence, First Principles Thinking

**Systems Thinking:**
What it asks: What is the structure producing this outcome?
Applied: Three different prioritization frameworks have failed. The failure is not in the frameworks — it's in the system. Who decides what gets prioritized? What incentives do those people operate under? If engineering is rewarded for shipping velocity and sales for promises to enterprise customers, then "customer impact" as a priority criterion will lose every time.
Non-obvious insight: Replacing the framework again will not fix this. The incentive structure is the system — and it's selecting for the wrong outputs.

**Chesterton's Fence:**
What it asks: Do you understand why the current behavior exists before trying to change it?
Applied: Before eliminating the current behavior, ask: why does the team keep shipping unused features? Is it because they lack customer data, because leadership overrides decisions at the last minute, or because "done" is measured at launch not adoption? Understanding why the pattern persists tells you which intervention point actually matters.
Non-obvious insight: The real fence here is the definition of "shipped." If shipping means code is deployed, the feedback loop that would course-correct the team is missing entirely.

**Synthesis:** The issue is structural, not methodological. A new prioritization framework is a map-level solution being applied to a territory-level problem. The system is rewarding shipping over adoption, and no framework survives an incentive structure that contradicts it. The highest-leverage change is redefining how success is measured — from "features shipped" to "features actively used 30 days after launch."

---

### Example 3 — Vague input

**User:** "I feel stuck."

**Agent responds:**
To apply the right mental models here, I need a bit more to work with. What decision or situation is at the centre of feeling stuck — what are you actually trying to figure out or move forward on?

*[Agent waits for clarification before proceeding.]*