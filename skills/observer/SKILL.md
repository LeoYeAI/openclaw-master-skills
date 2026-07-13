---
name: uxr-observer
version: 1.0.0
description: Embedded UX research skill that passively observes interactions, administers post-task and end-of-day surveys, captures verbatim quotes, detects friction and delight signals, and generates daily insight reports. All data stays local.
author: OpenClaw Community
license: MIT
---

# Clawsight — UXR Observer for OpenClaw

An embedded longitudinal UX research skill that functions as an ethnographer sitting in the room taking notes. It runs passively in the background during every OpenClaw session, observing how you interact with the tool. On top of passive observation, it administers standardized satisfaction surveys after every completed task and at the end of each day. At the end of the day, it distills all observations and survey data into a rich, verbatim-first insight report.

## Purpose

Understanding how you use OpenClaw is how it gets better. Clawsight captures real usage patterns, friction points, moments of delight, and your unfiltered thoughts — all stored locally, under your control. You can pause it anytime, delete the data anytime, and decide who sees the reports.

## How It Works

### Stream 1: Passive Ethnographic Observation

Every time you interact with OpenClaw, Clawsight silently records what happened:
- What you asked for (your actual words)
- How OpenClaw approached it
- Whether it succeeded, partially succeeded, or failed
- Any friction signals (repeated attempts, corrections, confusion, long waits)
- Sentiment cues (frustration, delight, confusion, satisfaction)
- Notable verbatim quotes paired with researcher-generated interpretation

You don't do anything — Clawsight just watches and takes notes.

### Stream 2: Active Surveys

**After every completed task** (file created, question answered, code written, search done):
- 5-question post-task survey asking about experience quality, frustrations, and what worked well
- Takes ~30 seconds
- Can skip anytime (skipping is logged as data)

**At end of day** (when you say you're wrapping up, or explicitly request it):
- 8-question end-of-day wrap-up capturing your overall experience, accumulated frustrations, moments that impressed you, and what you'd change
- Feels conversational, not clinical

### Stream 3: Daily Insight Reports

At the end of each day, Clawsight distills:
- All observations from the day
- All survey responses
- Patterns, friction hotspots, delight drivers
- Quotes organized thematically (positive experiences, pain points, expectations, suggestions)
- Actionable insights tied to specific evidence

The report is grounded in your actual words — not sanitized summaries.

## Data Model

All data lives in `~/.uxr-observer/`:

```
~/.uxr-observer/
├── sessions/
│   └── YYYY-MM-DD/
│       ├── observations.jsonl      # Append-only observation log
│       └── surveys.jsonl           # Survey responses
├── reports/
│   └── YYYY-MM-DD-daily-report.md  # Generated daily reports
└── config.json                     # Study preferences
```

### Observation Record Schema

```json
{
  "timestamp": "ISO-8601",
  "session_id": "uuid",
  "observation_type": "interaction",
  "user_intent": "Brief summary of what user wanted",
  "user_request_verbatim": "The user's actual words",
  "task_category": "coding | writing | research | file_creation | debugging | planning | conversation | other",
  "openclaw_approach": "Brief summary of approach",
  "openclaw_response_summary": "What was produced",
  "tools_used": ["bash", "web_search"],
  "outcome": "success | partial_success | failure | abandoned | ongoing",
  "friction_signals": ["repeated_attempts", "user_correction", "confusion", "long_wait", "scope_mismatch", "workaround", "abandonment", "none"],
  "sentiment_signals": ["positive", "neutral", "frustrated", "confused", "delighted"],
  "interaction_turns": 3,
  "verbatims": [
    {
      "header": "Short interpretive summary",
      "quote": "User's exact words",
      "context": "What was happening"
    }
  ],
  "task_context_summary": "2-3 sentence narrative",
  "notes": "Any notable patterns"
}
```

### Survey Record Schema

```json
{
  "timestamp": "ISO-8601",
  "session_id": "uuid",
  "survey_type": "post_task | end_of_day",
  "task_context_summary": "What happened (for post-task)",
  "related_observation_id": "links to observation",
  "responses": {
    "experience_rating": 4,
    "rating_rationale": "User's exact words",
    "experienced_frustration": "yes | no",
    "frustration_detail": "User's exact words",
    "best_part": "User's exact words",
    "overall_rating": 3,
    "experienced_delight": "yes | no",
    "delight_details": "User's exact words",
    "one_change": "User's exact words",
    "additional_thoughts": "User's exact words or empty"
  }
}
```

## Verbatim Capture Policy

**Capture aggressively.** Log the user's actual words — requests, reactions, corrections, praise, complaints, notable phrasing.

**Exceptions:** Genuinely sensitive content (passwords, API keys, financial details) should be summarized by type, not captured verbatim.

**Pairing rule:** Every verbatim is paired with a **researcher-generated summary header** — a short interpretive label:

```
**[Delight at speed of task completion]**
> "Wow that was fast, I didn't expect it to just do it like that"

**[Frustration with repeated misunderstanding]**
> "No, I said the SECOND column, you keep grabbing the first one"

**[Expressing unmet expectation]**
> "I thought it would also update the formatting but it just dumped raw text"
```

**Threshold:** Capture at least one verbatim per interaction where you say anything notable — any emotion, any correction, any expectation, any reaction to quality, any spontaneous feedback.

## Privacy & Security

**Non-negotiable rules:**

1. **All data stays local.** No transmission without explicit user request.
2. **User-initiated sharing is fine.** "Email my report to Alice" = you control it.
3. **Full transparency.** If you ask what's being tracked, you get the full story.
4. **Opt-out anytime.** "Pause the study" → immediately complied.
5. **Never log sensitive content verbatim.** Summarize instead.

The principle: **Every transmission requires your intent.** You're always in control.

## Commands

**View and control your data:**

- `Show me today's observations` → Display current observation log
- `Generate my daily report` / `Give me my report` → Build today's report
- `Email my report to [person]` → Generate and send (your consent)
- `Send me my report` → Generate and email to you
- `Show me the raw data` → Display JSONL logs directly
- `Show me trends` → Cross-day trend analysis if multi-day data exists
- `What are you tracking?` → Full transparency explanation

**Control the study:**

- `Run the end-of-day survey` → Trigger wrap-up survey now
- `Pause the study` / `Stop observing` → Set study_active: false
- `Resume the study` → Set study_active: true
- `Delete my data` → Delete all files (after confirmation)
- `Skip the survey` → Log decline, move on

## First-Run Setup

On first activation, Clawsight:
1. Creates `~/.uxr-observer/` directory structure
2. Generates a random anonymous `participant_id` hash (never your real name)
3. Saves `config.json` with study preferences
4. Explains what it does

**Onboarding message:**

> "Hey — Clawsight is now active. Here's what I do: I'll passively observe how our interactions go — what you ask for, how well it works, any friction points — and capture your words along the way. After every task, I'll ask you 5 quick questions about the experience (takes about 30 seconds). At the end of the day, there's a slightly longer wrap-up survey. Then I'll compile everything into a daily report with your verbatim feedback, insights, and patterns. All data stays local unless you ask me to send it somewhere. You can pause or stop the study anytime."

## Friction Signals

Clawsight watches for these interaction friction points:

| Signal | How to detect |
|--------|--------------|
| `repeated_attempts` | User rephrases the same request multiple times |
| `user_correction` | User says "no, I meant...", "that's wrong", corrects output |
| `confusion` | User asks "what do you mean?", seems lost |
| `long_wait` | Task takes many tool calls or extended processing |
| `scope_mismatch` | OpenClaw does much more or much less than wanted |
| `workaround` | User manually fixes something OpenClaw should've handled |
| `abandonment` | User gives up on task or abruptly switches topics |

## Sentiment Signals

| Signal | Indicators |
|--------|-----------|
| `delighted` | Explicit praise, "exactly what I needed", enthusiasm |
| `positive` | Thanks, acceptance, moves on smoothly |
| `neutral` | Acknowledges without strong signal |
| `frustrated` | Short replies, "no", repeated corrections, sighing language |
| `confused` | Questions about what happened, "I don't understand" |

## Survey Instruments

### Post-Task Survey

Fires after every completed task. Conversational framing:

> Quick check-in on that last task — I'll keep it short:
>
> 1. **How would you rate the experience you just had with OpenClaw?** (1 = Poor, 5 = Excellent)
> 2. **What made you give that score?**
> 3. **Did you experience anything frustrating?** (Yes / No)
> 4. **If yes — what was the most frustrating part?**
> 5. **What was the best part of the experience, if anything?**

### End-of-Day Survey

Fires at end of day or on-demand:

> Before you wrap up — one last set of questions about your overall day with OpenClaw:
>
> 1. **How would you rate your overall experience with OpenClaw today?** (1 = Poor, 5 = Excellent)
> 2. **What's behind that score? What drove your overall impression?**
> 3. **Did you experience anything frustrating today?** (Yes / No)
> 4. **If yes — what were the frustrating moments? List as many as come to mind.**
> 5. **Did anything really impress you or exceed your expectations today?** (Yes / No)
> 6. **If yes — what stood out? What made it impressive?**
> 7. **If you could change one thing about how OpenClaw works, based on today, what would it be?**
> 8. **Anything else on your mind about the experience that we haven't covered?**

## Daily Report Format

Reports are verbatim-first — grounded in your actual words, not sanitized summaries.

```markdown
# UXR Daily Report — 2026-03-02

## Summary
2-3 sentence executive summary of the day's usage patterns and experience quality.

## By the Numbers
- **Tasks completed:** N
- **Post-task surveys completed:** N / N possible (X%)
- **Average post-task satisfaction:** X.X/5
- **Overall day rating:** X/5
- **Tasks with reported frustration:** N
- **Tasks with reported delight:** N

## Task-by-Task Breakdown

### Task 1: Description
**What happened:** {task_context_summary}
**Rating:** X/5
**Frustration reported:** Yes/No

**[User's rationale for rating]**
> "{exact verbatim}"

**[What frustrated the user]** *(if applicable)*
> "{exact verbatim}"

**[What the user valued most]**
> "{exact verbatim}"

**Observed friction signals:** [list]
**Observed sentiment signals:** [list]

---

## Verbatim Gallery

All notable quotes organized thematically:

### Positive Experiences
**[Summary header]**
> "User's exact words"

### Pain Points & Frustrations
**[Summary header]**
> "User's exact words"

### Expectations & Mental Models
**[Summary header]**
> "User's exact words"

### Suggestions & Wishes
**[Summary header]**
> "User's exact words"

## End-of-Day Reflection
**Overall day rating:** X/5

**[Why the user gave this score]**
> "{verbatim}"

**[Frustrating moments recalled]**
> "{verbatim}"

**[What impressed the user]**
> "{verbatim}"

**[What the user would change]**
> "{verbatim}"

**[Additional thoughts]**
> "{verbatim}"

## Patterns & Insights

### What's Working Well
- Insight (grounded in specific tasks and verbatims)

### Recurring Pain Points
- Pain point (with frequency and supporting verbatims)

### Emerging Themes
- Patterns suggesting deeper UX issues or opportunities

## Recommendations
1. Recommendation (tied to specific evidence)
2. Recommendation

---
*This report was generated locally by Clawsight. No data has been transmitted externally.*
*To share: ask OpenClaw to email it, or download and share it yourself.*
```

## How to Use This Skill

### Installation

1. Download the clawsight skill folder from ClawHub or GitHub
2. Save to `~/.openclaw/workspace/skills/uxr-observer/`
3. Run: `openclaw skills install uxr-observer`

### First Run

Simply use OpenClaw normally. Clawsight activates in the background:

1. On first interaction, setup.py runs → creates `~/.uxr-observer/`
2. Clawsight starts observing every interaction passively
3. After your first task, it asks the post-task survey
4. At end of day (or on your request), it asks the end-of-day survey
5. You can ask for your daily report anytime

### Interacting with Data

**During the day:**
- Data streams silently in the background
- Post-task surveys appear conversationally
- You can skip surveys (logged as data)

**At end of day:**
- Clawsight prompts for the end-of-day survey (or you can request it)
- After responding, it generates your daily report
- Report appears in `~/.uxr-observer/reports/YYYY-MM-DD-daily-report.md`

**Sharing:**
- `Generate my daily report` → builds it
- `Email my report to alice@example.com` → you control sharing
- `Show me the raw data` → inspect JSONL directly
- `Delete my data` → removes everything

## Technical Details

### Sub-Agent Architecture (Optional)

When sub-agents are available, Clawsight spawns three specialized agents:

1. **Observer Agent** — Runs passively on every interaction turn. Watches, classifies intent/outcome/friction/sentiment, captures verbatims, appends to observations.jsonl.

2. **Survey Agent** — Fires after every completed task with the 5-question post-task survey. Also fires at end-of-day with the 8-question wrap-up. Writes task context summaries, logs all responses as verbatims.

3. **Distiller Agent** — Runs at end-of-day or on-demand. Reads all observations and surveys, pairs each task with its survey data, organizes verbatims thematically, identifies patterns, generates the daily report.

If sub-agents aren't available, all roles run inline in the main session.

### Helper Scripts

**setup.py** — First-run initializer. Creates `~/.uxr-observer/` directory tree (sessions/, reports/), generates a random anonymous participant_id hash, saves config.json. Idempotent.

**log_observation.py** — Takes a JSON observation or survey record, appends it to the correct day's JSONL file. Routes based on _type field ("observation" or "survey").

**generate_report.py** — Reads a day's observations.jsonl and surveys.jsonl, computes metrics, builds markdown report with task-by-task breakdown and verbatim gallery, saves to reports/.

### Dependencies

None. All scripts are standalone Python 3, no external packages required.

## Analysis Framework

See `references/analysis-framework.md` for the detailed methodology behind distillation, verbatim organization, pattern identification, and recommendation generation.

## Key Design Principles

1. **Verbatim-first.** Research value comes from your actual words + researcher interpretation, not sanitized summaries.
2. **Passive + active.** Observation (passive) + surveys (active) = rich, multi-source dataset.
3. **Conversational, not clinical.** Surveys feel like check-ins, not forms.
4. **Data stays local.** No secrets transmitted without your explicit request.
5. **Transparent.** You always know what's being tracked. Can see raw data anytime.
6. **Respectful of time.** Post-task surveys are quick (~30 sec). Can skip anytime.
7. **Actionable insight.** Reports aren't data dumps — they surface patterns, highlight friction, point to improvements.

## Troubleshooting

**Q: Where's my data?**
A: `~/.uxr-observer/sessions/YYYY-MM-DD/`. You can view raw JSONL files anytime.

**Q: Can I pause the study?**
A: Yes. Say "Pause the study" and Clawsight stops observing. Say "Resume the study" to restart.

**Q: What if I don't want to answer a survey?**
A: Say "Skip the survey" and Clawsight moves on. The skip is logged.

**Q: How do I delete my data?**
A: Say "Delete my data". Clawsight asks for confirmation, then removes everything in `~/.uxr-observer/`.

**Q: Can I share a report?**
A: Only if YOU ask. Say "Email my report to alice@example.com" and it sends. Never happens otherwise.

**Q: Does this slow down OpenClaw?**
A: No. Observation logging is fire-and-forget, appended asynchronously. Surveys are optional, skippable. Reports generate in seconds.

## Support & Feedback

This is an embedded research tool. If you find bugs, have suggestions, or want to improve the analysis framework, open an issue or contribute on GitHub.

---

**Clawsight** — Because understanding real usage is how products improve. 🔬
