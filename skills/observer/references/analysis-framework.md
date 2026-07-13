# Clawsight Analysis Framework

## Overview

Clawsight distillation is a **verbatim-first, ethnographic approach** to converting raw observation and survey data into actionable daily insights. The goal is to understand not just *what* you did with OpenClaw, but *how it felt*, where friction occurred, what delighted you, and what patterns emerge.

## Data Assembly

1. **Load observations.jsonl** — All interaction observations for the day
2. **Load surveys.jsonl** — Post-task and end-of-day survey responses
3. **Pair observations with surveys** — Link each task observation to its corresponding post-task survey (if exists) via `related_observation_id`
4. **Identify end-of-day survey** — If present, use as capstone reflection

## Task-Level Pairing

For each task (interaction observation), create an atomic record:

```
observation + task_context_summary + post_task_survey (if exists)
```

This ensures the report reader understands:
- What the user asked for (observation)
- What OpenClaw did (task_context_summary)
- How the user felt about it (survey response)

If no survey exists for a task, still include the observation with its friction/sentiment signals.

## Verbatim Organization

### Collection

1. Harvest ALL verbatims from:
   - Observation records (verbatims array)
   - Survey responses (rating_rationale, frustration_detail, best_part, one_change, additional_thoughts)

2. Pair each quote with a **researcher-generated summary header** — your interpretation of what the quote represents

**Good headers:**
- "Frustration with CSS selector matching"
- "Surprise at speed of code generation"
- "Expectation unmet about formatting options"
- "Appreciation for explanatory comments"

**Bad headers:**
- "Feedback" (too generic)
- "User said X" (no interpretation)
- "Good" / "Bad" (not specific)

### Thematic Organization

Bucket verbatims into themes:

| Theme | What goes here |
|-------|---------------|
| **Positive Experiences** | Praise, delight, appreciation, things that worked well |
| **Pain Points & Frustrations** | Complaints, friction, confusion, repeated attempts, workarounds |
| **Expectations & Mental Models** | What the user expected vs. what happened, surprise moments |
| **Suggestions & Wishes** | "I wish...", "It would be nice if...", user-proposed changes |
| **Workflow & Context** | How tasks fit into the user's broader work, integration patterns |

## Quantitative Metrics

Compute once per day:

| Metric | Meaning |
|--------|---------|
| **Total tasks completed** | Number of distinct interaction observations |
| **Post-task surveys completed** | Of those tasks, how many have survey responses? |
| **Survey completion rate** | (surveys completed / tasks) × 100 |
| **Average post-task satisfaction** | Mean of experience_rating across post-task surveys |
| **Frustration frequency** | How many tasks had experienced_frustration == "yes" |
| **Delight frequency** | How many tasks had positive sentiment or delight mention |
| **Overall day rating** | Rating from end-of-day survey (if exists) |

## Cross-Reference Analysis

### Observer vs. Reporter Gap

Compare what the observer **saw** (friction_signals, sentiment_signals) against what the user **reported** (survey ratings):

**Example:**
- Observation: 3 friction signals detected (repeated_attempts, user_correction, confusion)
- Survey: User rates 4/5 "Good"
- Insight: User has high frustration tolerance. They still rate highly despite friction.

**Example:**
- Observation: No friction signals, sentiment = "delighted"
- Survey: User rates 3/5 "Okay"
- Insight: Possible survey fatigue or other context not visible in the interaction

### Divergence Detection

Flag these gaps:
- High friction observed but high satisfaction reported → tolerance/resilience signal
- Low friction but low satisfaction → expectation/context issue
- Repeated corrections but positive rating → task complexity accepted as worth it

## End-of-Day Integration

If end-of-day survey exists:

1. Compare overall day rating with average task rating
   - Is daily reflection higher/lower than task average? Why?
2. Review "frustration moments recalled"
   - Do they match observer-detected frustration, or different patterns?
3. Highlight "one change" response
   - High-signal user suggestion → surfaces priority
4. Note emotional tone of additional_thoughts

## Pattern Identification

### Capability Clusters

Group tasks by category (coding, writing, research, etc.). Detect patterns:
- Highest satisfaction in [category]?
- Most friction in [category]?
- Do patterns suggest strengths/weaknesses?

### Friction Hotspots

Aggregate friction_signals across tasks:
- Which friction type appears most? (repeated_attempts, corrections, long_wait?)
- Are they in specific categories or tools?
- Are they isolated or recurring?

### Delight Drivers

What triggered "delighted" sentiment?
- Specific tools?
- Speed?
- Quality of output?
- Unexpected capability?

### Recovery Patterns

When friction occurred, how did it resolve?
- Did user correct the agent?
- Did user workaround?
- Did user abandon?
- Did follow-up clarification fix it?

### Verbatim Echoes

Watch for the same complaint/praise appearing in multiple forms:
- Multiple observations mention the same friction
- Survey responses echo the same wish
- Pattern = genuine, not one-off

## Trend Analysis (Multi-Day)

If you have 2+ days of data:

1. **Rating trajectories** — Is overall satisfaction trending up/down?
2. **Persistent pain points** — Same friction appearing day-to-day?
3. **Usage evolution** — Task categories / tool usage changing?
4. **Survey fatigue** — Are responses getting shorter/less engaged?
5. **Capability discovery** — New use cases appearing over time?

## Recommendation Generation

Generate 2–4 actionable recommendations:

**Criteria:**
- Tied to specific evidence (cite verbatims, frequencies, observations)
- Prioritized by frequency × severity
- Balance problem/opportunity framing
- Include specificity (not "improve the UI" but "reduce the number of steps to X")

**Format:**
```
[#]. [Specific action] — [evidence]. [Expected impact].

Example:
1. Reduce CSS selector debugging steps — Users reported 3× corrections
   in web scraping tasks. Adding visual selector preview tool could cut
   iteration time by 50%.
```

## Quality Checks

Before finalizing the report:

- [ ] Every insight traceable back to data (cite line numbers in JSONL if needed)
- [ ] Task context summaries are readable by someone who wasn't present
- [ ] Verbatim headers are interpretive, not editorializing
- [ ] Both positive and negative findings represented (not confirmation-biased)
- [ ] Uncertainty flagged ("Small sample size, N=2" etc.)
- [ ] No sensitive data in report (passwords, financial details redacted)
- [ ] All verbatim quotes are user's actual words, not paraphrased
- [ ] Report is scannable (headers, lists, quotes stand out)

## Data Sensitivity

### What NOT to Include Verbatim

- Passwords, API keys, tokens
- Financial details (amounts, account numbers)
- Personal secrets, health info
- Names of people (use initials or "colleague")
- Sensitive project details

**Instead:** Summarize by type. Example:
- Instead of: `"I just created a password-protected database with key xyz..."`
- Write: `User created a password-protected database.`

### What TO Include Verbatim

**Everything else.** The entire value of UX research is understanding the user's voice:
- How they phrase requests
- What they complain about
- How they celebrate wins
- What confuses them
- What they wish existed

## Lifecycle

1. **Post-task** — Observer logs interaction, survey captures immediate response
2. **End-of-day** — Distiller assembles data, generates report
3. **Next day** — You review report, reflect on patterns
4. **Weekly/Monthly** — Cross-day trends analyzed, recommendations accumulated
5. **Quarterly** — Broader patterns emerge, inform product decisions

## Tools & Automation

### Observer Agent (if sub-agents available)

Runs after every interaction:
- Watches exchange
- Classifies user intent, OpenClaw approach, outcome
- Detects friction and sentiment signals
- Captures verbatims with headers
- Appends observation to observations.jsonl

### Survey Agent (if sub-agents available)

Runs after task completion and at end-of-day:
- Writes task context summary
- Presents survey conversationally
- Logs responses as verbatims
- Appends survey to surveys.jsonl

### Distiller Agent (if sub-agents available)

Runs at end-of-day or on-demand:
- Reads observations + surveys
- Computes metrics
- Organizes verbatims thematically
- Identifies patterns
- Generates markdown report
- Saves to reports/

## Example: One Day in Clawsight

### Morning: Coding Task

**Observation:** User asks to refactor Python script. OpenClaw generates refactored version. User says "this is almost right but the error handling is different from my original."

**Friction signals:** user_correction

**Sentiment:** neutral (acceptance, minor fix needed)

**Verbatim captured:** 
- "this is almost right but the error handling is different" → header: "Unmet expectation about function signature compatibility"

**Post-task survey:** Rating 3/5. "It was good but I had to manually review and adjust. Wished it understood my existing error handling pattern."

### Afternoon: Research Task

**Observation:** User asks for market research summary. OpenClaw searches, compiles, provides markdown. User says "wow, that's exactly what I needed."

**Friction signals:** none

**Sentiment:** delighted

**Verbatim captured:**
- "wow, that's exactly what I needed" → header: "Delight at meeting precise information need"

**Post-task survey:** Rating 5/5. "Fast, comprehensive, exactly the format I needed."

### End of Day

**End-of-day survey:** Overall rating 4/5. "Coding task was a bit frustrating with the error handling mismatch, but research task was excellent. If I could change one thing: better learning of user patterns (like my error handling conventions)."

### Report Distillation

**Metrics:**
- 2 tasks, 2 post-task surveys, 1 end-of-day survey (100% completion)
- Avg satisfaction: 4/5
- Frustration: 1 task, Delight: 1 task

**Task-by-Task:**
- Coding: Rating 3/5, friction detected
- Research: Rating 5/5, delighted sentiment

**Verbatim Gallery:**
- Positive: "wow, that's exactly what I needed"
- Expectations: "wished it understood my existing error handling pattern"

**Recommendation:**
"Implement context retention for error handling conventions. Users appreciate OpenClaw's research capabilities but want refactoring to adapt to existing code patterns, not just generic best practices. Learning user conventions could improve coding task satisfaction from 3→4+."

---

This framework turns everyday interactions into structured learning. Over time, patterns emerge that inform improvements to OpenClaw.
