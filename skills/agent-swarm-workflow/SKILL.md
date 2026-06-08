---
name: agent-swarm-workflow
description: "Jeffrey Emanuel's multi-agent implementation workflow using NTM, Agent Mail, Beads, and BV. The execution phase that follows planning and bead creation. Includes exact prompts used."
---

# Agent Swarm Workflow — Parallel Implementation

> **Core Insight:** Every agent is fungible and a generalist. They all use the same base model and read the same AGENTS.md. Simply telling one it's a "frontend agent" doesn't make it better at frontend.
>
> The swarm is distributed, robust, and self-organizing through Agent Mail and Beads.

---

## Prerequisites

Before starting a swarm:

1. **Comprehensive plan** created (see `planning-workflow` skill)
2. **Polished beads** ready (see `beads-workflow` skill)
3. **AGENTS.md** configured with all tool blurbs
4. **Agent Mail server** running (`am` or `~/projects/mcp_agent_mail/scripts/run_server_with_token.sh`)
5. **NTM** available for session management

---

## The Swarm Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         BEADS                               │
│     (Task graph with dependencies, priorities, status)      │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
┌─────────────────────────────┐  ┌─────────────────────────┐
│        BV                   │  │     AGENT MAIL          │
│  (What to work on)          │  │  (Coordination layer)   │
└─────────────────────────────┘  └─────────────────────────┘
         │                            │
         └──────────────┬─────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    NTM + AGENTS                             │
│  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐     │
│  │ CC  │  │ CC  │  │ Cod │  │ Gmi │  │ CC  │  │ Cod │     │
│  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## Starting the Swarm

### Using NTM (Named Tmux Manager)

```bash
# Spawn a swarm with multiple agents
ntm spawn myproject --cc=3 --cod=2 --gmi=1

# Send initial prompt to all Claude Code agents
ntm send myproject --cc "$(cat initial_prompt.txt)"

# Or send to all agents
ntm send myproject --all "$(cat initial_prompt.txt)"
```

### Manual Setup

Create tmux sessions/panes for each agent in your project folder.

---

## THE EXACT PROMPT — Initial Agent Marching Orders

Give each agent this EXACT prompt to start:

```
First read ALL of the AGENTS dot md file and README dot md file super carefully and understand ALL of both! Then use your code investigation agent mode to fully understand the code, and technical architecture and purpose of the project. Then register with MCP Agent Mail and introduce yourself to the other agents.

Be sure to check your agent mail and to promptly respond if needed to any messages; then proceed meticulously with your next assigned beads, working on the tasks systematically and meticulously and tracking your progress via beads and agent mail messages.

Don't get stuck in "communication purgatory" where nothing is getting done; be proactive about starting tasks that need to be done, but inform your fellow agents via messages when you do so and mark beads appropriately.

When you're not sure what to do next, use the bv tool mentioned in AGENTS dot md to prioritize the best beads to work on next; pick the next one that you can usefully work on and get started. Make sure to acknowledge all communication requests from other agents and that you are aware of all active agents and their names.  Use ultrathink.
```

---

## The Implementation Loop

### THE EXACT PROMPT — Move to Next Bead

Once agents complete a bead, use this prompt to keep them moving:

```
Reread AGENTS dot md so it's still fresh in your mind.   Use ultrathink.   Use bv with the robot flags (see AGENTS dot md for info on this) to find the most impactful bead(s) to work on next and then start on it. Remember to mark the beads appropriately and communicate with your fellow agents. Pick the next bead you can actually do usefully now and start coding on it immediately; communicate what you're working on to your fellow agents and mark beads appropriately as you work. And respond to any agent mail messages you've received.
```

### THE EXACT PROMPT — Self-Review After Bead Completion

Have agents review their work before moving on:

```
Great, now I want you to carefully read over all of the new code you just wrote and other existing code you just modified with "fresh eyes" looking super carefully for any obvious bugs, errors, problems, issues, confusion, etc. Carefully fix anything you uncover. Use ultrathink.
```

**Keep running this until they stop finding bugs.**

---

## Handling Context Compaction

### THE EXACT PROMPT — Post-Compaction

When an agent does a compaction, immediately follow up with:

```
Reread AGENTS dot md so it's still fresh in your mind.   Use ultrathink.
```

This re-establishes the critical context about tools and workflows.

---

## Quality Review Prompts

### THE EXACT PROMPT — Cross-Agent Review

Periodically have agents review each other's work:

```
Ok can you now turn your attention to reviewing the code written by your fellow agents and checking for any issues, bugs, errors, problems, inefficiencies, security problems, reliability issues, etc. and carefully diagnose their underlying root causes using first-principle analysis and then fix or revise them if necessary? Don't restrict yourself to the latest commits, cast a wider net and go super deep! Use ultrathink.
```

### THE EXACT PROMPT — Random Code Exploration

For deep quality checks:

```
I want you to sort of randomly explore the code files in this project, choosing code files to deeply investigate and understand and trace their functionality and execution flows through the related code files which they import or which they are imported by.

Once you understand the purpose of the code in the larger context of the workflows, I want you to do a super careful, methodical, and critical check with "fresh eyes" to find any obvious bugs, problems, errors, issues, silly mistakes, etc. and then systematically and meticulously and intelligently correct them.

Be sure to comply with ALL rules in AGENTS dot md and ensure that any code you write or revise conforms to the best practice guides referenced in the AGENTS dot md file. Use ultrathink.
```

---

## Committing Work

### THE EXACT PROMPT — Commit Changes

Have agents commit logically grouped changes:

```
Now, based on your knowledge of the project, commit all changed files now in a series of logically connected groupings with super detailed commit messages for each and then push. Take your time to do it right. Don't edit the code at all. Don't commit obviously ephemeral files. Use ultrathink.
```

---

## Post-Bead Completion Prompts

### THE EXACT PROMPT — Add Test Coverage

```
Do we have full unit test coverage without using mocks/fake stuff? What about complete e2e integration test scripts with great, detailed logging? If not, then create a comprehensive and granular set of beads for all this with tasks, subtasks, and dependency structure overlaid with detailed comments.
```

### THE EXACT PROMPT — UI/UX Scrutiny

```
Great, now I want you to super carefully scrutinize every aspect of the application workflow and implementation and look for things that just seem sub-optimal or even wrong/mistaken to you, things that could very obviously be improved from a user-friendliness and intuitiveness standpoint, places where our UI/UX could be improved and polished to be slicker, more visually appealing, and more premium feeling and just ultra high quality, like Stripe-level apps.
```

### THE EXACT PROMPT — Deep UI/UX Enhancement

```
I still think there are strong opportunities to enhance the UI/UX look and feel and to make everything work better and be more intuitive, user-friendly, visually appealing, polished, slick, and world class in terms of following UI/UX best practices like those used by Stripe, don't you agree? And I want you to carefully consider desktop UI/UX and mobile UI/UX separately while doing this and hyper-optimize for both separately to play to the specifics of each modality. I'm looking for true world-class visual appeal, polish, slickness, etc. that makes people gasp at how stunning and perfect it is in every way.  Use ultrathink.
```

---

## Agent Mail Integration

### How Agents Coordinate

Each agent:
1. **Registers** with Agent Mail at session start
2. **Reserves files** before editing (`file_reservation_paths`)
3. **Announces work** via messages with bead ID in `thread_id`
4. **Checks inbox** between tasks
5. **Releases reservations** when done

### File Reservation Pattern

```python
# Before starting work on a bead
file_reservation_paths(
    project_key="/path/to/project",
    agent_name="GreenCastle",
    paths=["src/auth/**/*.ts"],
    ttl_seconds=3600,
    exclusive=True,
    reason="bd-123"
)

# After completing work
release_file_reservations(project_key, agent_name)
```

### Communication Pattern

```python
# Announce starting a bead
send_message(
    project_key, agent_name,
    to=["BlueLake", "RedMountain"],  # Other active agents
    subject="[bd-123] Starting auth module",
    body_md="I'm taking bd-123. Reserved src/auth/**.",
    thread_id="bd-123"
)

# Update on completion
send_message(
    project_key, agent_name,
    to=["BlueLake", "RedMountain"],
    subject="[bd-123] Completed",
    body_md="Auth module done and tested. Released file reservations.",
    thread_id="bd-123"
)
```

---

## Using BV for Task Selection

### Key Commands

```bash
# THE MEGA-COMMAND: Start here
bv --robot-triage

# Just get the single top pick
bv --robot-next

# Get parallel execution tracks (for multi-agent)
bv --robot-plan

# Check for cycles (MUST FIX if found)
bv --robot-insights | jq '.Cycles'

# Find bottlenecks
bv --robot-insights | jq '.bottlenecks'
```

**CRITICAL:** Never run bare `bv` — it launches interactive TUI that blocks the session.

---

## Quality Loops

### Run Until Clean

Keep running these prompts in rounds until they consistently come back with no changes:

1. **Self-review** — Agent reviews own code
2. **Cross-review** — Agent reviews other agents' code
3. **Random exploration** — Deep dive into random code paths

### The Steady-State Signal

When all three types of reviews return clean (no bugs found, no changes made), the code is likely solid.

---

## Complete Prompt Reference

### Initial Marching Orders
```
First read ALL of the AGENTS dot md file and README dot md file super carefully and understand ALL of both! Then use your code investigation agent mode to fully understand the code, and technical architecture and purpose of the project. Then register with MCP Agent Mail and introduce yourself to the other agents.

Be sure to check your agent mail and to promptly respond if needed to any messages; then proceed meticulously with your next assigned beads, working on the tasks systematically and meticulously and tracking your progress via beads and agent mail messages.

Don't get stuck in "communication purgatory" where nothing is getting done; be proactive about starting tasks that need to be done, but inform your fellow agents via messages when you do so and mark beads appropriately.

When you're not sure what to do next, use the bv tool mentioned in AGENTS dot md to prioritize the best beads to work on next; pick the next one that you can usefully work on and get started. Make sure to acknowledge all communication requests from other agents and that you are aware of all active agents and their names.  Use ultrathink.
```

### Move to Next Bead
```
Reread AGENTS dot md so it's still fresh in your mind.   Use ultrathink.   Use bv with the robot flags (see AGENTS dot md for info on this) to find the most impactful bead(s) to work on next and then start on it. Remember to mark the beads appropriately and communicate with your fellow agents. Pick the next bead you can actually do usefully now and start coding on it immediately; communicate what you're working on to your fellow agents and mark beads appropriately as you work. And respond to any agent mail messages you've received.
```

### Self-Review
```
Great, now I want you to carefully read over all of the new code you just wrote and other existing code you just modified with "fresh eyes" looking super carefully for any obvious bugs, errors, problems, issues, confusion, etc. Carefully fix anything you uncover. Use ultrathink.
```

### Cross-Review
```
Ok can you now turn your attention to reviewing the code written by your fellow agents and checking for any issues, bugs, errors, problems, inefficiencies, security problems, reliability issues, etc. and carefully diagnose their underlying root causes using first-principle analysis and then fix or revise them if necessary? Don't restrict yourself to the latest commits, cast a wider net and go super deep! Use ultrathink.
```

### Random Exploration
```
I want you to sort of randomly explore the code files in this project, choosing code files to deeply investigate and understand and trace their functionality and execution flows through the related code files which they import or which they are imported by.

Once you understand the purpose of the code in the larger context of the workflows, I want you to do a super careful, methodical, and critical check with "fresh eyes" to find any obvious bugs, problems, errors, issues, silly mistakes, etc. and then systematically and meticulously and intelligently correct them.

Be sure to comply with ALL rules in AGENTS dot md and ensure that any code you write or revises conforms to the best practice guides referenced in the AGENTS dot md file. Use ultrathink.
```

### Post-Compaction
```
Reread AGENTS dot md so it's still fresh in your mind.   Use ultrathink.
```

### Commit Changes
```
Now, based on your knowledge of the project, commit all changed files now in a series of logically connected groupings with super detailed commit messages for each and then push. Take your time to do it right. Don't edit the code at all. Don't commit obviously ephemeral files. Use ultrathink.
```

### Test Coverage
```
Do we have full unit test coverage without using mocks/fake stuff? What about complete e2e integration test scripts with great, detailed logging? If not, then create a comprehensive and granular set of beads for all this with tasks, subtasks, and dependency structure overlaid with detailed comments.
```

### UI/UX Scrutiny
```
Great, now I want you to super carefully scrutinize every aspect of the application workflow and implementation and look for things that just seem sub-optimal or even wrong/mistaken to you, things that could very obviously be improved from a user-friendliness and intuitiveness standpoint, places where our UI/UX could be improved and polished to be slicker, more visually appealing, and more premium feeling and just ultra high quality, like Stripe-level apps.
```

### Deep UI/UX Enhancement
```
I still think there are strong opportunities to enhance the UI/UX look and feel and to make everything work better and be more intuitive, user-friendly, visually appealing, polished, slick, and world class in terms of following UI/UX best practices like those used by Stripe, don't you agree? And I want you to carefully consider desktop UI/UX and mobile UI/UX separately while doing this and hyper-optimize for both separately to play to the specifics of each modality. I'm looking for true world-class visual appeal, polish, slickness, etc. that makes people gasp at how stunning and perfect it is in every way.  Use ultrathink.
```

---

## The Flywheel in Action

```
PLAN ──► BEADS ──► SWARM ──► REVIEW ──► COMMIT
  │                  │          │         │
  │                  │          └────┬────┘
  │                  │               │
  │                  └───── REPEAT ──┘
  │                              │
  │         v2 PLAN ◄────────────┘
  │              │
  └──────────────┘
```

Each cycle improves:
- **CASS** remembers solutions
- **CM** distills patterns
- **UBS** catches more issues
- **BV** shows graph health

---

## FAQ

**Q: How do agents know what to work on?**
A: They use `bv --robot-triage` or `bv --robot-next` to find the highest-impact ready bead.

**Q: How do they avoid conflicts?**
A: File reservations in Agent Mail. Exclusive reservations block others; the pre-commit guard enforces it.

**Q: What if an agent crashes or forgets?**
A: Every agent is fungible. Start a new session, read AGENTS.md, check bead status, continue.

**Q: How many agents should I run?**
A: Depends on project complexity. Start with 3-6. More agents = faster but more coordination overhead.

**Q: What model mix works best?**
A: Mix recommended. Try 3 Claude Code (Opus), 2 Codex (GPT 5.2), 1 Gemini. They have different strengths.

**Q: Do agents need individual areas of expertise?**
A: No, every agent is fungible and a generalist. Simply telling one it's a frontend agent doesn't make it better at frontend.

**Q: Is there traceability between git commit and bead?**
A: Yes, bv automatically does this analysis and links beads to relevant git commits by analyzing the stream of data and making logical deductions.
