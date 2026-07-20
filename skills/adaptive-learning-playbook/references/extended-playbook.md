# Extended Playbook — Adaptability & Learning

## Table of Contents
1. [Tools & Technology Stack](#tools--technology-stack)
2. [Case Studies & Reference Models](#case-studies--reference-models)
3. [Advanced Frameworks](#advanced-frameworks)
4. [Templates](#templates)
5. [Recommended Reading & Sources](#recommended-reading--sources)

---

## Tools & Technology Stack

### By Capability

| Capability | Recommended Tools | Budget Alternative |
|---|---|---|
| Market Trends | Feedly, Google Alerts, ITONICS Radar, Exploding Topics | Google Alerts + RSS + AI synthesis |
| Org Agility | Linear, Notion, Jira, Miro | GitHub Projects + Notion free |
| Kaizen | Notion (PDCA templates), Loom (Gemba recordings), Retrium | Notion + retrospective template |
| Experimentation | LaunchDarkly, Optimizely, Statsig | Feature flags in code + spreadsheet |
| Knowledge Mgmt | Notion, Confluence, Slite, GitBook | Notion + SKILL.md architecture |
| Competitive Intel | RivalSense, Crayon, Klue, Visualping | Google Alerts + Visualping + Similarweb free |
| Pivoting | Strategyzer (BMC), Miro, FigJam | BMC template + decision log |

### AI-Augmented Workflow

For a lean team, AI multiplies CI and KM capabilities:
- **Signal synthesis:** Feed trend data to Claude → structured weekly digest
- **Competitive analysis:** Crawl competitor sites → AI-generated battlecard updates
- **Knowledge Q&A:** Index Notion/docs → AI-powered internal search
- **Experiment design:** Describe the assumption → AI generates MVE framework
- **Decision support:** Feed decision log context → AI surfaces relevant precedents
- **SKILL.md architecture:** Encode institutional knowledge into reusable AI instruction files deployable across Claude.ai, Claude Code, Codex CLI

---

## Case Studies & Reference Models

### Amazon → AWS: Intelligence-Driven Market Creation
Amazon identified a customer segment before those customers identified themselves. By 2025,
AWS reached 32% global cloud infrastructure market share — ahead of Azure (20%) and Google
Cloud (13%). The CI that enabled AWS was not a report on existing competitors. It was a
forward-looking read on indirect competitors and market opportunities not yet materialised.

**Lesson:** The highest form of competitive intelligence creates markets, not just responds to them.

### Netflix: The Multi-Stage Pivot
Netflix pivoted DVD-by-mail → streaming → original content production — each time preserving
the core insight (people want convenient, personalised entertainment) while fundamentally
changing delivery, technology, and business model. Blockbuster had abundant CI but failed
to act on it.

**Lesson:** CI without decision architecture is worthless. Pivoting ability requires both
intelligence AND organisational willingness to cannibalise existing revenue.

### Toyota: Kaizen as Sustainable Competitive Advantage
Toyota's production system built on Kaizen created advantages competitors spent decades trying
to replicate. While individual improvements are small, the culture of continual aligned
improvements + standardisation yields massive cumulative productivity gains. This differs
fundamentally from command-and-control improvement programmes.

**Lesson:** Kaizen is a compounding function. Small daily improvements > periodic big-bang
transformations. The culture is the moat.

### NSF I-Corps: Systematic Pivoting in Deep Tech (230 Startups)
Analysis of 230 early-stage deep tech startups found 95% adjusted at least one business model
component, with 66% making changes to four or more components. Most altered: value propositions
and customer segments. This confirms product-market fit is iterative and experimentation-driven.

**Lesson:** Pivoting is the norm, not the exception. Build for it structurally and culturally.

### Ford: Kaizen-Driven Turnaround Under Alan Mulally
When Mulally became CEO in 2006, Ford was near bankruptcy. Using Kaizen principles and radical
transparency (red/yellow/green meeting charts), he executed one of the most celebrated turnarounds
in history — without government bailout.

**Lesson:** Kaizen applies at the highest strategic level, not just manufacturing floors.
Transparency is the enabler.

### Pixar: Quality Through Iteration
Pixar applied continuous improvement to reduce risks of expensive movie failures using quality
control checks and iterative creative processes. Every film goes through systematic review
cycles where candid feedback drives improvement.

**Lesson:** Creative industries benefit from structured improvement processes just as much as
manufacturing. The key is psychological safety in feedback.

---

## Advanced Frameworks

### Three Learning Loops (Lean Startup × Organisational Learning)

| Loop | Type | Trigger | Action |
|---|---|---|---|
| Single-loop | Iteration | Minor deviations from plan | Small product/process tweaks. Adjust tactics. |
| Double-loop | Pivot | Fundamental assumption invalidated | Change strategy, business model component, or target market. |
| Triple-loop | Transformation | Core identity/vision questioned | Redefine organisational purpose, industry, or operating model. |

The lean startup's Build-Measure-Learn cycle primarily operates in single-loop. Pivots are
double-loop. Rare transformations (e.g., Nokia, Fujifilm) require triple-loop learning.

### Hoshin Kanri (Policy Deployment) + Kaizen Alignment

Hoshin Kanri aligns strategic priorities with daily Kaizen:
1. **Breakthrough objectives** (3–5 year) cascade to...
2. **Annual objectives** which decompose to...
3. **Quarterly targets** delivered through...
4. **Daily Kaizen** at the team level.

This ensures small improvements move enterprise metrics, not just local optima.

### The Agility Diagnostic (Worley & Lawler)

14 dimensions across four features:
- **Robust Strategy:** Shared purpose, flexible strategic intent, strong future focus
- **Adaptable Design:** Structural flexibility, resource flexibility, development orientation,
  information transparency, shared power, flexible rewards
- **Shared Leadership:** Change-friendly identity, distributed leadership
- **Change Capability:** Change capability, learning capability, innovation capability

Use as a self-assessment diagnostic quarterly.

### McKinsey Influence Model for Kaizen Success
Kaizen sustainability depends on four conditions:
1. **Conviction** (understanding why we improve)
2. **Role modelling** (leaders at the Gemba)
3. **Capability** (problem-solving skills)
4. **Reinforcement** (KPIs, incentives, recognition)

If any element is missing, Kaizen devolves into "tool-of-the-month."

### Experimentation Programme Design (Academy of Management)

Two critical dimensions:
- **Number of experiments** — More is not always better
- **Pivot threshold** — How much negative evidence triggers a pivot

Key finding: Programmes generating frequent early pivots impede learning. An effectively
designed programme can also partially remedy entrepreneur behavioural biases (e.g., overconfidence).

Recommended approach:
- Conservative early threshold (resist premature pivoting)
- Increase sensitivity as evidence accumulates
- Use pre-registered criteria to prevent emotional pivoting
- Combine theorisation (articulating explicit hypotheses) with experimentation for purposeful pivots

### Pivot Enablers (Research-Backed)

Three factors most strongly associated with willingness to pivot:
1. **Entrepreneurial experience** — Prior startup experience broadens perspective
2. **Startup mentoring** — External advisors provide cognitive diversity
3. **Team size** — Larger teams have broader collective perspective

Founders resist pivoting value propositions most, even with negative feedback. These enablers
help overcome identity-based resistance to change.

---

## Templates

### Weekly Trend Digest Template

```markdown
# Trend Digest — Week of [DATE]

## Top Signals This Week
1. [Signal] — Source: [X] — Impact: High/Med/Low — Action: [None/Monitor/Investigate/Act]
2. ...
3. ...

## Regulatory Updates
- [Jurisdiction]: [Update summary]

## Technology Watch
- [Notable development]

## Competitive Moves
- [Competitor]: [Action observed]

## Recommended Actions
- [ ] [Specific action item with owner]
```

### Experiment Log Template

```markdown
# Experiment: [EXP-NNN] [Title]

## Hypothesis
We believe [customer segment] will [take action] because [reason].

## Success Criteria (Pre-registered)
- Primary: [Metric] reaches [threshold] within [timeframe]
- Secondary: [Metric]

## Design
- Type: [Smoke test / A-B / Concierge / Wizard of Oz / Pilot]
- Duration: [Timeframe]
- Sample: [Size/segment]
- Variables: [What we're changing vs control]

## Results
- Primary metric: [Actual] vs [Target]
- Secondary: [Actual]
- Unexpected observations:

## Decision
- [ ] Persevere — Scale this approach
- [ ] Pivot — Change direction based on evidence
- [ ] Kill — Stop investing

## Key Learnings
- [What we now know that we didn't before]
- [How this changes our assumptions]
```

### Competitive Battlecard Template

```markdown
# Battlecard: [Competitor Name]

## Overview
- Founded: | HQ: | Funding: | Est. ARR:
- Primary market: | Target customer:

## Their Strengths
- [What they do well — be honest]

## Their Weaknesses
- [Where they fall short]

## How We Win Against Them
- [Specific advantages with evidence]

## Common Objections & Responses
| Prospect Says | We Respond |
|---|---|
| "[Objection]" | "[Response with evidence]" |

## Pricing Comparison
| Feature | Us | Them |
|---|---|---|

## Recent Moves
- [Date]: [What they did and what it means]

## Last Updated: [DATE]
```

### After-Action Review (AAR) Template

```markdown
# After-Action Review: [Project/Incident Name]

## Date: [DATE]
## Participants: [Names]

## What Was Expected
- [Planned outcome]

## What Actually Happened
- [Actual outcome]

## Why the Difference
- Root causes (use 5 Whys if needed):
  1. Why? →
  2. Why? →
  3. Why? →

## What We Will Do Differently
- [ ] [Action item — Owner — Deadline]

## What We Will Keep Doing
- [What worked well]

## Knowledge to Capture
- [Insight to add to knowledge base]
```

---

## Recommended Reading & Sources

### Books
- **The Lean Startup** — Eric Ries (experimentation, MVP, pivoting)
- **Kaizen: The Key to Japan's Competitive Success** — Masaaki Imai (foundational Kaizen text)
- **The Toyota Way** — Jeffrey Liker (Kaizen in practice, 14 principles)
- **Built to Change** — Worley & Lawler (agility diagnostic framework)
- **The Fifth Discipline** — Peter Senge (learning organisations)
- **Competitive Strategy** — Michael Porter (Five Forces, competitive positioning)
- **The Art of Action** — Stephen Bungay (strategy execution under uncertainty)
- **Thinking in Bets** — Annie Duke (decision-making under uncertainty)
- **The Mom Test** — Rob Fitzpatrick (customer research/validation)

### Frameworks & Models
- Scaled Agile Framework (SAFe) — Organisational agility dimensions
- World Economic Forum — Continuous adaptation model
- Prosci ADKAR — Change management methodology
- Business Model Canvas — Osterwalder (pivot framework)
- OODA Loop — Boyd (Observe-Orient-Decide-Act for competitive response)

### Research
- Burnell et al. (2023) — "Early-stage business model experimentation and pivoting"
- Camuffo et al. (2020) — Scientific approach to entrepreneurship (theory-based view)
- Gans, Stern & Wu (2019) — "Programs of Experimentation and Pivoting"
- Bellavitis et al. (2025) — "Strategic Pivoting in Deep Tech" (NSF I-Corps)
- Springer (2025) — "Multidimensional concept of organisational agility" (SLR of 110 articles)

---

**This reference document supports the main SKILL.md. Return to the main skill for
quick-reference frameworks and decision-making guidance.**
