# Non-Technical Methodology Research

> Merged guide for researching judgment-heavy, non-technical domains
> (writing, communication, hiring, negotiation, decision-making, etc.)
> and a seed database of experts/frameworks to start from.

---

## When to Use

When creating or optimizing a skill for a domain where quality depends on
subjective judgment rather than technical correctness:

- Writing and communication
- User research and interviews
- Product decisions and discovery
- Negotiation and persuasion
- Hiring and evaluation
- Retrospectives and improvement

---

## Why This Protocol Exists

Non-technical skill quality varies wildly. The root cause is usually not
formatting, but:

- Whether the right authoritative methodology was chosen
- Whether "golden examples" define the quality ceiling
- Whether anti-patterns are written into quality gates
- Whether cross-validation was performed across experts
- Whether test scenarios were designed upfront

---

## Minimum Research Deliverables

Complete all 5 before writing the skill:

1. **Expert and framework list** (2-3 experts minimum)
2. **Golden examples** (>= 2)
3. **Anti-patterns / common failures** (>= 3)
4. **Cross-validation matrix** (agreements / disagreements / context conditions)
5. **Test scenarios** (typical / boundary / failure mode, at least 1 each)

---

## Three-Layer Research Path

### Layer 1: Baseline (your current knowledge)

Write 10-20 lines of "what you currently believe are best practices."
Mark uncertain points for later research.

### Layer 2: Locate Authoritative Experts

Minimum requirements:
- 2-3 experts/institutions that are widely cited in the industry
- Each with at least 1 named framework or methodology
- Record source type + traceable info (book, article, talk + date)

### Layer 3: Read Primary Sources

Priority order:
1. Books / official articles / course materials
2. Talk transcripts / interview transcripts (with context)
3. High-quality secondary summaries (must note this)

---

## Methodology Seed Database

Starting points when you don't know which experts to research.

### Writing and Communication

| Expert | Framework | Use When | Primary Source |
|--------|-----------|----------|---------------|
| Barbara Minto | Pyramid Principle (MECE/SCQ) | Business writing, structured expression | "The Pyramid Principle" |
| William Zinsser | Simplicity/Clarity | Removing verbosity, clear writing | "On Writing Well" |
| Amazon | Narrative memo / Working Backwards | Alignment docs, resource requests | Bezos letters, "Working Backwards" |
| Nancy Duarte | Sparkline (is vs could be) | Presentations, storytelling | "Resonate" |

### User Research

| Expert | Framework | Use When | Primary Source |
|--------|-----------|----------|---------------|
| Rob Fitzpatrick | The Mom Test | User interviews, avoiding false data | "The Mom Test" |
| Steve Portigal | Interviewing Users | Interview structure, follow-up strategy | "Interviewing Users" |
| Nielsen Norman Group | Research -> Findings -> Insights | Research writing, usability | nngroup.com |
| Clayton Christensen | Jobs To Be Done | Understanding user motivation | "Competing Against Luck" |

### Product and Decision-Making

| Expert | Framework | Use When | Primary Source |
|--------|-----------|----------|---------------|
| Marty Cagan / SVPG | Problem-first / Empowered teams | PRD, product decisions | "Inspired", "Empowered" |
| Teresa Torres | Continuous Discovery Habits | Ongoing discovery, opportunity trees | "Continuous Discovery Habits" |
| Annie Duke | Decision hygiene | Decision review, reducing outcome bias | "Thinking in Bets" |

### Negotiation and Persuasion

| Expert | Framework | Use When | Primary Source |
|--------|-----------|----------|---------------|
| Chris Voss | Tactical Empathy | High-pressure negotiation | "Never Split the Difference" |
| Fisher & Ury | Principled Negotiation (BATNA) | Collaborative negotiation | "Getting to Yes" |
| Robert Cialdini | Six Principles of Influence | Persuasion structure | "Influence" |

### Hiring and Evaluation

| Expert | Framework | Use When | Primary Source |
|--------|-----------|----------|---------------|
| Geoff Smart | Topgrading / WHO | Structured interviews, A-player ID | "Who" |
| Laszlo Bock | Structured Interviews | Interview structure and scoring | "Work Rules!" |

### Retrospectives and Improvement

| Expert | Framework | Use When | Primary Source |
|--------|-----------|----------|---------------|
| Google SRE | Blameless Postmortem | Incident review, systemic improvement | "Site Reliability Engineering" |
| Toyota | 5 Whys | Root cause tracing | Lean/Toyota Production System |

---

## Research Record Templates

### Methodology Card (one per expert)

```markdown
## Methodology Card: [Expert] - [Framework]

- **Domain**: [writing/hiring/negotiation/...]
- **Applicable context**: [B2B/startup/enterprise/...]
- **Core claim (one sentence)**: [...]
- **Key steps/principles**:
  1) ...
  2) ...
- **Common failures/anti-patterns**:
  - ...
- **Source**: [book/article/talk], [title/URL], [date], credibility: [S/A/B/C]
```

### Cross-Validation Matrix

```markdown
| Principle/Step | Expert A | Expert B | Expert C | Conclusion |
|---------------|----------|----------|----------|------------|
| [principle 1] | agree/disagree | agree/disagree | agree/disagree | [consensus or context-dependent] |
```

### Test Scenarios

```markdown
## Test Scenarios

1) **Typical**: [description]
2) **Boundary**: [description]
3) **Failure mode**: [e.g., missing input, conflicting goals, hostile audience]
```

---

## Stop Condition

All must be true before proceeding to write the skill:

- [ ] Key terms/steps have consistent meaning across sources (or disagreements documented)
- [ ] Can write 3-5 checkable, actionable quality criteria
- [ ] Golden examples exist that can reverse-engineer a quality checklist
- [ ] Know 3+ anti-patterns that can be written into quality gates
- [ ] Can provide 3 test scenarios covering typical/boundary/failure modes
