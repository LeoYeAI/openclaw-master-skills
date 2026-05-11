# decision-mental-models

Apply the right mental model to any problem or decision — surfaces non-obvious insights by explicitly selecting and working through 2–3 frameworks per query.

---

## What it does

Given a problem or decision, the agent:

1. Identifies the core tension in the user's situation
2. Selects 2–3 mental models from a library of 20 that are structurally relevant to that specific problem
3. Applies each model explicitly — using the user's actual details, not generic explanations
4. Synthesizes the insights into a single high-leverage takeaway

---

## The 20 Mental Models

| # | Model | Best for |
|---|-------|----------|
| 1 | First Principles Thinking | Breaking inherited assumptions |
| 2 | Inversion | Avoiding failure conditions |
| 3 | Second-Order Thinking | Tracing downstream consequences |
| 4 | Occam's Razor | Cutting unnecessary complexity |
| 5 | The Map Is Not the Territory | Spotting model-reality gaps |
| 6 | Circle of Competence | Calibrating confidence to knowledge |
| 7 | Opportunity Cost | Evaluating the road not taken |
| 8 | Sunk Cost Fallacy | Breaking path dependency |
| 9 | Regret Minimization | Long-arc life decisions |
| 10 | Hanlon's Razor | Interpersonal conflict and attribution |
| 11 | Feedback Loops | Understanding self-perpetuating systems |
| 12 | Probabilistic Thinking | Decisions under uncertainty |
| 13 | Thought Experiments | Stress-testing plans before committing |
| 14 | Pareto Principle (80/20) | Prioritization under constraint |
| 15 | Activation Energy | Behavior change and friction reduction |
| 16 | Dunning-Kruger Effect | Competence calibration |
| 17 | Chesterton's Fence | Before eliminating rules or processes |
| 18 | Availability Heuristic | Correcting for vivid-but-rare thinking |
| 19 | Margin of Safety | Planning for error and uncertainty |
| 20 | Systems Thinking | Recurring organizational problems |

---

## Usage

Just describe your problem or decision. The agent handles model selection and application.

**Example triggers:**
- "I can't decide whether to quit my job and go freelance."
- "Our team keeps making the same mistakes. What are we missing?"
- "Help me think through whether to raise a seed round now."
- "How should I approach this conflict with my co-founder?"

---

## Installation

### OpenClaw / ClawHub

```bash
clawhub skill install arbazex/decision-mental-models
```

### Manual

Copy `SKILL.md` into your agent's skill directory. No environment variables, binaries, or external APIs required.

---

## What this skill does NOT do

- Give direct advice or tell the user what to decide
- Apply models generically — every application uses the user's specific situation
- Replace professional legal, medical, or financial advice
- Apply all 20 models at once (2–3 per query is intentional — depth beats breadth)

---

## License

MIT