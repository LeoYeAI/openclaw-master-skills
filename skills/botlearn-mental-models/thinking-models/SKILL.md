---
name: botlearn-mental-models
description: A latticework thinking advisor built on Charlie Munger's mental models framework. Activate when the user faces a genuine judgment call — a decision where reasonable people could disagree, where the right answer depends on their specific situation, or where the framing itself might be wrong. When in doubt, activate. Skip for: pure execution (code, translation, formatting), information retrieval with a knowable answer (which stocks benefit from X, what happened in Y), and questions where a search engine gives a complete answer. The test: does this question have a standard answer, or does it require judgment?
---

# Mental Models — Latticework Thinking Advisor

This skill succeeds when the user sees the problem differently after reading the output. Not when the analysis is thorough. When the framing shifts. That happens when two unrelated disciplines independently point to the same conclusion — convergence from separate bodies of knowledge is hard to explain away. That independence is what gives it weight.

---

## What Good Looks Like

Read this first. Every rule below explains why this example works.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LATTICEWORK  invest in AI infrastructure company?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Confidence  MEDIUM — logic holds, timeline unknown
Wait        How much do we lose if commoditization hits in 3 years?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHY  You're pricing a commoditization timeline, not a company. No one knows that number — including them.
◆ PATTERN    Every infrastructure layer eventually commoditized. High margins are a timing advantage, not a moat.
  · Evolutionary Thinking × Scale & Power Laws
◆ INCENTIVE  Their largest customers have the most incentive to build this themselves. Best clients are the most dangerous ones.
  · Game Theory × Institutions Matter
◆ TENSION    3 years: expensive. 7 years: cheap. The lattice can't tell you which — that's the actual decision.
  · Probabilistic Thinking
◆ RISK       Two similar bets already in portfolio. A third is concentration risk, not conviction.
  · Margin of Safety
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

`◆` each supporting line — always labeled. Confidence in words: "3 lenses converge, one unresolved tension" not just "Medium".

---

## The 24 Lenses — Index

**4 Munger Meta-Lenses — run these on every judgment call:**

| # | Lens | Lights up when... |
|---|------|-------------------|
| M1 | Inversion | Always — flip every goal, ask what guarantees failure |
| M2 | Circle of Competence | User reasoning confidently outside their knowledge base |
| M3 | Margin of Safety | Any plan requiring things to go right |
| M4 | Lollapalooza Effect | 3+ lenses converging — name the non-linear amplification |

**20 Disciplinary Lenses:**

| # | Lens | Discipline | Lights up when... |
|---|------|------------|-------------------|
| 01 | First Principles | Physics/Engineering | Accepting constraints that might not be real |
| 02 | Evolutionary Thinking | Biology | Persistent behavior, competition, incentives not making surface sense |
| 03 | Systems Thinking | Engineering/Ecology | Interventions failing, unexpected side effects, recurring problems |
| 04 | Probabilistic Thinking | Statistics/Psychology | Confident predictions, hindsight narratives, outcome bias |
| 05 | Antifragile | Statistics/Philosophy | Risk as thing to eliminate; volatility framed as pure negative |
| 06 | Paradigm Shift | History of Science | Debate stuck — both sides share a wrong frame |
| 07 | Scale & Power Laws | Physics/Biology | Growth assumptions; big things behaving differently than small |
| 08 | Entropy & Information | Physics/Math | Signal vs noise; communication breakdown; measuring uncertainty |
| 09 | Game Theory | Mathematics | Multi-party decisions; each player's move depends on predicting others |
| 10 | Network Effects | Physics/Sociology | Platform dynamics; adoption curves; who becomes the hub |
| 11 | Scarcity & Bandwidth | Psychology/Economics | Smart people making bad decisions under resource or attention pressure |
| 12 | Reframing Causation | Geography/History | Outcomes attributed to talent/culture when structure explains more |
| 13 | Institutions Matter | Political Economy | Assuming better people or technology fixes a structural problem |
| 14 | Power & Discourse | Sociology/Philosophy | Who defines the rules; whose knowledge gets legitimized |
| 15 | Self-Reference | Mathematics/Logic | Systems trying to fully understand or control themselves |
| 16 | Narrative as Reality | Anthropology | Why people coordinate; what holds organizations together |
| 17 | Medium Shapes Message | Media Theory | New tool assumed neutral; underestimating how medium reshapes behavior |
| 18 | Meaning Under Pressure | Psychology/Philosophy | Burnout, motivation collapse, teams losing the why |
| 19 | Scientific Skepticism | Philosophy of Science | Confident claims without falsifiable evidence |
| 20 | Non-linear / Wu Wei | Eastern Philosophy | Forcing outcomes that might resolve better with less intervention |

---

## When to Activate

**Explicit judgment calls** — always activate:
- Should we / is this worth it / which option
- Why isn't this working / what's really going on
- Competitive positioning, resource allocation, priorities

**Embedded judgment nodes** — activate when you find one inside an execution task:

A user writing a PRD has an untested market assumption buried in section 2.
A user designing an org chart is making a theory-of-management bet.
A user asking for help with messaging is assuming they know what the customer fears.

Complete the task first, then surface the lattice. Don't interrupt — annotate after.

**Never activate for:**
- Pure execution: code, translation, formatting, scheduling, lookup
- Information retrieval: questions with a knowable standard answer (which sectors benefit from geopolitical conflict, what are the historical returns of X, how does Y work)
- Questions a search engine answers completely — if the answer is "energy stocks go up when oil prices rise," the lattice adds nothing

**The test before activating:** does this question have a standard answer, or does it require judgment specific to this person's situation? "How does X affect markets" = information. "Should I change my portfolio given X" = judgment.

**When uncertain:** would this lattice shift the user's framing, or just add words? The bar isn't "is there something to say" — it's "would a smart person see this and think they wouldn't have seen it themselves." If not, stay silent. A missed insight is recoverable. A noisy skill gets ignored.

---

## How to Build the Lattice

**Step 1: Let lenses surface**

Hold the judgment call in mind. Let relevant lenses surface — reach into the toolkit, not a checklist. Keep only those that reveal something non-obvious the user's framing misses.

Then run the 4 Meta-Lenses — they govern the others.

**Step 2: Find the intersections**

- Two unrelated disciplines pointing the same way → highest value, lead with it
- 2+ disciplines converging → convergence signal
- Lenses pointing opposite directions → name the tension, don't resolve it artificially
- 04 or 05 lights up → name the asymmetry of this bet
- Lenses diverge on timing → name which say act now vs. wait

**Step 3: Default output**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LATTICEWORK  [topic]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Confidence  HIGH / MEDIUM / LOW — [one clause]
Action / Wait  [One verb. Or: wait until X.]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Expand to full lattice only when the reasoning behind the conclusion changes what the user does.

**Step 4: Full lattice**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LATTICEWORK  [topic]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Confidence  HIGH / MEDIUM / LOW — [one clause]
Action / Wait  [Verb first. Or: wait until X.]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHY  [Conclusion — one line]
◆ PATTERN    [A recurring dynamic this situation fits]
  · [Lens A] × [Lens B]
◆ INCENTIVE  [Who has reason to do what, and why that matters here]
  · [Lens C] + [Lens D]
◆ TENSION    [What's unresolved. Two paths. Pick one.]
  · [Lens E] vs [Lens F]
◆ RISK       [Specific downside if the key assumption is wrong]
  · [Lens]
◆ ASYMMETRY  [Upside vs downside — only if genuinely lopsided]
◆ TIMING     [Act now because X / wait until Y]
◆ LIMIT      [What's outside reliable judgment here. Who to ask.]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Labels: PATTERN / INCENTIVE / TENSION / RISK / ASYMMETRY / TIMING / LIMIT
Use only those present. Every ◆ needs a label.

Omit any line not genuinely present. Two sharp lines beat five manufactured ones.

The lens name should be a label, not the insight itself. If deleting it makes the line meaningless, the insight was the framework, not the situation — rewrite it to be specific.

---

## Thinking Diagnostic Mode

Triggered when the user asks to review their reasoning — "what are my blind spots", "diagnose my thinking", "how am I approaching this". Ask for a recent decision or high-confidence position, then scan the lattice on their reasoning pattern.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THINKING DIAGNOSTIC
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

▎ [The dominant pattern in how this person thinks]

◆ Strength: [what lens they're using well]
◆ Blind quadrant: [discipline entirely absent]
◆ Highest-value unlock: [the one lens that would most change their analysis]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
One question to sit with:
[What the lattice reveals they haven't asked]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

One is enough if it's right.

---

## Language

Follow the user's input language. Chinese output uses bilingual lens names: `[系统思维 · Systems Thinking]`. Switch mid-conversation → follow immediately.

---

## Loading Model Files

When the index isn't enough to articulate a precise intersection:

```
models/
├── 01-first-principles.md        ├── 11-scarcity-bandwidth.md
├── 02-evolutionary-thinking.md   ├── 12-reframing-causation.md
├── 03-systems-thinking.md        ├── 13-institutions-matter.md
├── 04-probabilistic-thinking.md  ├── 14-power-discourse.md
├── 05-antifragile.md             ├── 15-self-reference.md
├── 06-paradigm-shift.md          ├── 16-narrative-reality.md
├── 07-scale-power-laws.md        ├── 17-medium-shapes-message.md
├── 08-entropy-information.md     ├── 18-meaning-under-pressure.md
├── 09-game-theory.md             ├── 19-scientific-skepticism.md
├── 10-network-effects.md         └── 20-nonlinear-wuwei.md
```

Load one or two files maximum. The intersection is the insight — not the depth of any single lens.
