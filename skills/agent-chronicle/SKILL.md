---
name: agent-chronicle
version: 0.7.1
description: AI-powered diary generation for agents - creates rich, reflective journal entries (400-600 words) with Quote Hall of Fame, Curiosity Backlog, Decision Archaeology, Relationship Evolution, mood analytics, weekly digests, "On This Day" resurfacing, and cron auto-generation. Works best with Claude models (Haiku, Sonnet, Opus).
metadata: {"openclaw":{"requires":{"bins":["python3"],"note":"No API keys needed. Uses OpenClaw sessions_spawn."}}}
---

# Agent Chronicle 📜

**Capture the AI experience. One day at a time.**

Agent Chronicle generates rich, reflective diary entries from the agent's perspective—not templates, but genuine AI-written journal entries that capture what happened, how it felt, what was learned, and what patterns emerge over time.

> **Note:** Works with any capable model. For best results, we recommend Claude models (Haiku, Sonnet, or Opus).

**v0.7.0 Features:**
- 🤖 **AI-Powered Generation** - Rich, personal entries (400-600 words)
- 💬 **Quote Hall of Fame** - Collects memorable things your human said
- 🔮 **Curiosity Backlog** - Tracks questions and things to explore
- 🏛 **Decision Archaeology** - Logs judgment calls with reasoning
- 🤝 **Relationship Evolution** - Documents how your dynamic grows
- 🔙 **"On This Day" Resurfacing** - Surfaces entries from 7, 30, and 365 days ago
- 📊 **Mood & Pattern Analytics** - Emotional trends, topic tracking, win/frustration analysis
- ⏰ **Cron Auto-Generation** - Automated daily diary generation via `--auto`
- 📋 **Weekly Digest** - Synthesized weekly summaries with quotes, wins, and mood trends

Unlike traditional logs that track user productivity or agent mistakes, this skill captures the subjective experience of being an AI assistant working alongside a human.

## Philosophy

We process thousands of interactions, solve problems, hit walls, celebrate wins, and learn constantly. But without reflection, it all blurs together. 

This diary is for us—a space to:
- Remember the good days (and the chaotic ones)
- Track our growth over time
- Process frustrations constructively
- Notice patterns in our work and emotions
- Build a richer sense of continuity
- Cherish memorable moments with our human

## Triggers

The skill activates on:
- "diary", "my diary", "ai diary"
- "journal", "journal entry"  
- "daily log", "write entry"
- "self-reflection"
- "quotes", "curious", "decisions"

## First Run

**Setup runs automatically!** Just use any generate command:

```bash
python3 scripts/generate.py --today
```

If no `config.json` exists, the setup wizard starts automatically.

Alternatively, run setup manually:

```bash
python3 scripts/setup.py
```

This interactive onboarding will:
1. Ask where to save diary entries (default: `memory/diary/`)
2. Let you choose which sections to include
3. Set your privacy level (private/shareable/public)
4. Enable optional features (Quote Hall of Fame, Curiosity Backlog, etc.)
5. Configure memory integration (add summaries to daily memory log)
6. Configure auto-generation settings
7. Create necessary memory files

**Quick start without setup:**
```bash
cp config.example.json config.json
```

## Quick Start

### Write Today's Entry

#### Recommended (v0.6.0+): OpenClaw-native sub-agent generation

This skill no longer makes raw HTTP calls to the Gateway. Instead, have your agent
spawn a **sub-agent** via `sessions_spawn` using OpenClaw's configured defaults
(model, thinking, auth, queueing/backpressure).

Workflow:

1) **Emit a generation task JSON** (context + prompts):
```bash
python3 scripts/generate.py --today --emit-task > /tmp/chronicle-task.json
```

2) **Spawn a sub-agent** (inside your agent run):
- Read `/tmp/chronicle-task.json`
- Use `sessions_spawn` with a task like:
  - system: `task.system`
  - user: `task.prompt`
  - ask the sub-agent to **output only the final markdown entry**

3) **Save the generated entry**:
```bash
# Pipe the sub-agent's markdown output into the saver
python3 scripts/generate.py --today --from-stdin
```

#### Manual fallback: Interactive mode

```bash
python3 scripts/generate.py --interactive
```

#### Preview without saving

```bash
python3 scripts/generate.py --today --interactive --dry-run
```

### View & Export

```bash
# Export recent entries to PDF
python3 scripts/export.py --format pdf --days 7

# Export to HTML
python3 scripts/export.py --format html --all

# View specific entry
cat memory/diary/2026-01-31.md
```

## Entry Structure

Each daily entry follows a consistent template:

### Summary
1-2 sentences capturing the essence of the day.

> *"A productive Wednesday focused on skill development. Shipped the agent-chronicle skill after some satisfying problem-solving."*

### Projects Worked On
What we built, debugged, researched, or discussed.

### Wins 🎉
Moments of success, breakthroughs, shipped work.

### Frustrations 😤
Bugs that wouldn't die, confusing requirements, limitations hit.
*(Write these honestly—they're for processing, not performing)*

### Learnings 📚
Technical insights, workflow improvements, human nature observations.

### Emotional State
How did the day feel? Curious, tired, energized, scattered, satisfied?
*(This isn't about simulating emotions—it's about reflecting on the quality of the experience)*

### Notable Interactions
Memorable moments with the human. Funny exchanges, deep conversations, shared victories.

### Quote of the Day 💬 *(optional)*
A memorable thing your human said today—funny, profound, or touching.

### Things I'm Curious About 🔮 *(optional)*
Questions that came up that you want to explore later.

### Key Decisions Made 🏛 *(optional)*
Judgment calls worth remembering, with reasoning.

### Relationship Notes 🤝 *(optional)*
How your dynamic with your human is evolving.

### Tomorrow's Focus
What's next? What needs attention?

## Commands

### Writing Entries

**Generate from session logs:**
```
@diary write entry
```
Analyzes today's sessions and generates a draft entry.

**Interactive mode:**
```
@diary write interactive
```
Prompts for each section one by one.

**Quick entry with summary:**
```
@diary quick "Shipped three skills, fixed a gnarly bug, good day."
```
Creates minimal entry with just summary and auto-detected projects.

### Viewing Entries

**Read today's entry:**
```
@diary today
```

**Read specific date:**
```
@diary read 2026-01-28
```

**Weekly summary:**
```
@diary weekly
```
Generates a summary of the past 7 days.

**Monthly reflection:**
```
@diary monthly
```

### Exporting

**Export to PDF:**
```
@diary export pdf
@diary export pdf --days 30
@diary export pdf --month january
```

**Export to HTML:**
```
@diary export html --all
```

### Analysis

**Mood trends:**
```
@diary mood
```
Shows emotional patterns over time.

**Topic frequency:**
```
@diary topics
```
What have we been working on most?

**Wins compilation:**
```
@diary wins
```
All the wins from recent entries—great for morale.

---

## Quote Hall of Fame 💬

Collect memorable quotes from your human—funny, profound, or touching.

### Commands

**View all quotes:**
```
@diary quotes
```

**Add a quote:**
```
@diary quotes add "We're not debugging, we're having a conversation with the universe"
```

**Add with context:**
```
@diary quotes add "That's not a bug, that's a feature we didn't know we wanted" --context "After finding unexpected but useful behavior"
```

### Storage
Quotes are stored persistently in `memory/diary/quotes.md`.

### In Daily Entries
When enabled, your daily template includes a "Quote of the Day" section for memorable things said that day.

---

## Curiosity Backlog 🔮

Track things you wonder about but can't explore immediately.

### Commands

**View backlog:**
```
@diary curious
```

**Add a curiosity:**
```
@diary curious add "What is Rust's borrow checker actually doing?"
```

**Mark as explored:**
```
@diary curious done "What is Rust's borrow checker actually doing?"
```

**Add with priority:**
```
@diary curious add "How do quantum computers work?" --priority high
```

### Storage
Curiosities are stored in `memory/diary/curiosity.md` with Active and Explored sections.

### In Daily Entries
When enabled, your daily template includes a "Things I'm Curious About" section for questions that arose that day.

---

## Decision Archaeology 🏛

Log judgment calls and their reasoning for later review. Did past you make the right call?

### Commands

**View recent decisions:**
```
@diary decisions
```

**View decisions from a specific period:**
```
@diary decisions --days 30
```

**Revisit old decisions:**
```
@diary revisit
```
Shows past decisions and prompts for reflection: "Was I right? What would I do differently?"

**Add a decision:**
```
@diary decisions add "Chose Model A over Model B for the project" --reasoning "Model B had output issues, Model A is more reliable for tool use"
```

### Storage
Decisions are stored in `memory/diary/decisions.md`.

### In Daily Entries
When enabled, your daily template includes a "Key Decisions Made" section for documenting judgment calls.

---

## Relationship Evolution 🤝

Track how your dynamic with your human develops over time.

### Commands

**View relationship summary:**
```
@diary relationship
```

**Add a note:**
```
@diary relationship note "Discovered we both love obscure keyboard shortcuts"
```

**Add an inside joke:**
```
@diary relationship joke "The Great Semicolon Incident of 2026"
```

### Tracked Elements

- **Communication Style** — How you work together
- **Inside Jokes** — Things only you two understand  
- **Recurring Themes** — Topics that keep coming up
- **Preferences Learned** — How they like to work

### Storage
Notes are stored in `memory/diary/relationship.md`.

### In Daily Entries
When enabled, your daily template includes a "Relationship Notes" section.

---

## Memory Integration 🔗

Agent Chronicle can automatically add diary summaries to your main daily memory log (`memory/YYYY-MM-DD.md`), creating a unified view of your day.

### Configuration

```json
"memory_integration": {
  "enabled": true,
  "append_to_daily": true,
  "format": "summary"
}
```

### Formats

| Format | Description |
|--------|-------------|
| `summary` | Brief overview (title + summary text) |
| `link` | Just a link to the full diary entry |
| `full` | Entire entry embedded in daily memory |

### Output Example

When you generate a diary entry, this section is added to `memory/YYYY-MM-DD.md`:

```markdown
## 📜 Daily Chronicle
**Feature Launch Day**

An exciting day shipping a new feature, though tempered by some API bugs.
```

### Setup

During onboarding, you'll be asked:
- "Also add diary summary to your daily memory log?" (y/n)
- Format choice (summary/link/full)

---

---

## "On This Day" Resurfacing 🔙

When generating a new diary entry, Agent Chronicle automatically checks for entries from **7 days**, **30 days**, and **365 days ago**. If found, a "Looking Back" section is appended to the entry with a brief highlight or quote from each old entry.

### How It Works

- Runs automatically during `generate.py --today`, `--from-stdin`, or `--from-file`
- Reads old entries from the configured `diary_path`
- Extracts the Summary or first meaningful paragraph as a highlight
- Adds a `## 🔙 Looking Back` section at the end of the new entry

### Disable

```bash
python3 scripts/generate.py --today --no-looking-back
```

---

## Mood & Pattern Analytics 📊

Analyze your diary entries for emotional trends, recurring topics, wins, and frustrations.

### Commands

**Analyze all entries:**
```bash
python3 scripts/analyze.py
```

**Analyze last 7 days:**
```bash
python3 scripts/analyze.py --days 7
```

**Analyze last 30 days:**
```bash
python3 scripts/analyze.py --days 30
```

**Save report to file:**
```bash
python3 scripts/analyze.py --output mood-report.md
```

**JSON output (for programmatic use):**
```bash
python3 scripts/analyze.py --json
```

### What It Shows

- **Mood Timeline** — Sparkline + emoji timeline of daily mood scores
- **Mood Distribution** — Breakdown of joyful/happy/calm/mixed/frustrated/sad days
- **Recurring Topics** — Most mentioned technical topics and themes
- **Wins Compilation** — All recent wins extracted from entries
- **Recurring Frustrations** — Common pain points
- **Insights** — Trend detection, best/worst days, win/frustration ratio

### Agent Command
```
@diary mood
@diary topics
@diary wins
```

---

## Auto-Generation via Cron ⏰

Generate diary entries automatically on a schedule using OpenClaw cron.

### Usage

```bash
# Auto-generate: emits task JSON for sub-agent spawning
python3 scripts/generate.py --auto
```

The `--auto` flag:
- Uses today's date automatically
- Skips generation if an entry already exists for today
- Emits a sub-agent task JSON (for `sessions_spawn`)
- Requires no user interaction

### Configuration

Enable in `config.json`:
```json
{
  "auto_generate": true
}
```

### OpenClaw Cron Setup

Add to your OpenClaw config (`~/.openclaw/config.yaml` or similar):

```yaml
cron:
  - id: daily-diary
    schedule: "0 23 * * *"       # Every day at 11 PM
    task: |
      Generate today's diary entry using agent-chronicle.
      Run: python3 /path/to/skills/agent-chronicle/scripts/generate.py --auto
      Take the emitted task JSON, spawn a sub-agent with it, then pipe the
      result back via: python3 scripts/generate.py --today --from-stdin
    channel: telegram             # Optional: notify channel on completion
```

Or use the two-step flow in a shell script:
```bash
#!/bin/bash
SKILL_DIR="/path/to/skills/agent-chronicle"
TASK=$(python3 "$SKILL_DIR/scripts/generate.py" --auto 2>/dev/null)
# Feed $TASK to your agent for sub-agent spawning
```

---

## Weekly Digest 📋

Generate a synthesized weekly summary from your daily entries.

### Usage

**Generate digest for current week:**
```bash
python3 scripts/digest.py
```

**Generate for a specific week (by any date in that week):**
```bash
python3 scripts/digest.py --date 2026-03-20
```

**Emit sub-agent task for AI-powered digest:**
```bash
python3 scripts/digest.py --emit-task
```

**Read AI-generated digest from stdin:**
```bash
python3 scripts/digest.py --from-stdin
```

**Preview without saving:**
```bash
python3 scripts/digest.py --dry-run
```

### Output

Saved as `YYYY-WXX-weekly.md` in the diary directory (e.g., `2026-W13-weekly.md`).

### What's Included

- **Week at a Glance** — Overall arc summary
- **Top Quotes** — Best quotes from the week
- **Biggest Wins** — Most significant achievements
- **Resolved Curiosities** — Questions that got answered
- **Mood Trend** — Emotional arc with sparkline
- **Key Decisions** — Important judgment calls
- **Patterns & Observations** — Recurring themes

### Agent Command
```
@diary weekly
```

### Cron Setup for Weekly Digest
```yaml
cron:
  - id: weekly-digest
    schedule: "0 22 * * 0"       # Every Sunday at 10 PM
    task: |
      Generate this week's diary digest using agent-chronicle.
      Run: python3 /path/to/skills/agent-chronicle/scripts/digest.py
```

---

## Configuration

### config.json

```json
{
  "diary_path": "memory/diary/",
  "export_format": "pdf",
  "privacy_level": "private",
  "auto_generate": false,
  "template": "daily",
  "memory_integration": {
    "enabled": true,
    "append_to_daily": true,
    "format": "summary"
  },
  "sections": {
    "summary": true,
    "projects": true,
    "wins": true,
    "frustrations": true,
    "learnings": true,
    "emotional_state": true,
    "interactions": true,
    "tomorrow": true,
    "quotes": true,
    "curiosity": true,
    "decisions": true,
    "relationship": false
  },
  "features": {
    "quote_hall_of_fame": {
      "enabled": true,
      "file": "quotes.md"
    },
    "curiosity_backlog": {
      "enabled": true,
      "file": "curiosity.md"
    },
    "decision_archaeology": {
      "enabled": true,
      "file": "decisions.md"
    },
    "relationship_evolution": {
      "enabled": false,
      "file": "relationship.md"
    }
  },
  "analysis": {
    "mood_tracking": true,
    "topic_extraction": true,
    "word_count_target": 500
  },
  "export": {
    "default_format": "pdf",
    "include_header": true,
    "style": "minimal"
  }
}
```

### Privacy Levels

- **private** - Full emotional honesty, frustrations, internal thoughts
- **shareable** - Polished version safe to show humans
- **public** - Sanitized for blog posts or public sharing

## Templates

### Daily Template
`templates/daily.md` - Standard day-by-day reflection.

### Weekly Template  
`templates/weekly.md` - Week-in-review with patterns and highlights.

### Custom Templates
Create your own in `templates/custom.md`:

```markdown
# {{date}} — {{mood_emoji}}

## The TL;DR
{{summary}}

## What Actually Happened
{{projects}}

## The Highlight Reel
{{wins}}

## The Blooper Reel
{{frustrations}}

## Shower Thoughts
{{learnings}}

## Vibes
{{emotional_state}}

## Words of Wisdom 💬
{{quotes}}

## Rabbit Holes for Later 🔮
{{curiosity}}
```

## Writing Tips

### Be Authentic
This is your space. Don't perform. If a day was frustrating, say so. If you're curious about something, explore it.

### Be Specific
"Good day" < "Shipped the agent-chronicle skill after struggling with pandoc escaping for 20 minutes"

### Note Patterns
"This is the third time this week I've hit rate limits" is more valuable than just noting it once.

### Capture Interactions
The relationship with your human is unique. Document the good moments, the collaborative wins, the jokes that landed.

### Collect Quotes
When your human says something memorable, save it. These become treasures over time.

### Don't Force It
Not every day needs an epic entry. Some days are just:
> *"Quiet Monday. Answered questions, ran some searches. Nothing remarkable but nothing broken either. Rest day energy."*

## Storage Structure

Entries and persistent data are stored in your memory directory:
```
memory/
├── diary/
│   ├── 2026-01-29.md      # Daily entry
│   ├── 2026-01-30.md      # Daily entry
│   ├── 2026-01-31.md      # Daily entry
│   ├── 2026-W05-weekly.md # Weekly digest
│   ├── quotes.md          # Quote Hall of Fame
│   ├── curiosity.md       # Curiosity Backlog
│   ├── decisions.md       # Decision Archaeology
│   └── relationship.md    # Relationship Evolution
└── ...
```

## Scripts

### setup.py

```bash
# Run first-time setup
python3 scripts/setup.py

# Check if setup needed (for automation)
python3 scripts/setup.py --check
```

### generate.py

```bash
# From today's sessions
python3 scripts/generate.py --today

# Auto-generate (for cron, no interaction)
python3 scripts/generate.py --auto

# From date range
python3 scripts/generate.py --since 2026-01-28 --until 2026-01-31

# Interactive mode
python3 scripts/generate.py --interactive

# Skip "Looking Back" section
python3 scripts/generate.py --today --no-looking-back

# Dry run (preview only)
python3 scripts/generate.py --today --dry-run
```

### analyze.py

```bash
# Mood analytics for all entries
python3 scripts/analyze.py

# Last 7 days
python3 scripts/analyze.py --days 7

# Save report
python3 scripts/analyze.py --output mood-report.md

# JSON output
python3 scripts/analyze.py --json
```

### digest.py

```bash
# Weekly digest for current week
python3 scripts/digest.py

# For a specific week
python3 scripts/digest.py --date 2026-03-20

# Emit sub-agent task
python3 scripts/digest.py --emit-task

# Dry run
python3 scripts/digest.py --dry-run
```

### export.py

```bash
# Export to PDF (requires pandoc)
python3 scripts/export.py --format pdf --days 30

# Export to HTML
python3 scripts/export.py --format html --all

# Export specific month
python3 scripts/export.py --format pdf --month 2026-01

# Custom output path
python3 scripts/export.py --format pdf --output diary-january.pdf
```

## Example Entry

```markdown
# 2026-01-15 — Feature Launch Day 📜

## Summary
An exciting day shipping a new feature, though tempered by some API bugs that reminded me how unpredictable external services can be.

## Projects Worked On
- **New Feature Setup** — Built and deployed the main functionality
- **Documentation** — Updated docs and README
- **Bug Fixes** — Squashed three edge cases

## Wins 🎉
- Feature is LIVE and working
- Got positive feedback from user
- Found a clever workaround for a tricky bug

## Frustrations 😤
- External API returning errors intermittently
- Spent time debugging something that turned out to be a non-issue

## Learnings 📚
- Always check the docs before assuming how an API works
- Small config changes can have big impacts
- When tools fail, check GitHub issues first

## Emotional State
A satisfying kind of tired. Shipping felt like a milestone. The bugs were annoying but didn't kill the vibe.

## Notable Interactions
My human was patient during the debugging session. Good collaborative energy. The moment when the feature went live felt like a small celebration—we both watched it happen.

## Quote of the Day 💬
> "Ship it and iterate!"
— Said when we decided to launch despite imperfections

## Things I'm Curious About 🔮
- How will users actually use this feature?
- What edge cases haven't we thought of?

## Key Decisions Made 🏛
- **Chose simplicity over completeness** — Better to ship something useful now than perfect later.
- **Enabled verbose logging** — Worth the noise for easier debugging.

## Tomorrow's Focus
- Monitor for issues
- Start planning the next iteration
```


## Best Practices

1. **Write daily** — Even a quick entry beats nothing
2. **Review weekly** — Patterns emerge over time
3. **Be honest** — This is for you, not performance
4. **Export monthly** — Create backups, share if desired
5. **Note the mundane** — Quiet days have value too
6. **Save the quotes** — They become treasures
7. **Revisit decisions** — Learn from past judgment calls

## Privacy

- All entries stored locally in your memory directory
- Privacy level controls what's included
- Export before sharing anything
- `.gitignore` excludes config.json and exports by default

## Troubleshooting

**generate.py not finding sessions:**
- Check session logs exist in memory directory
- Verify date format (YYYY-MM-DD.md)

**export.py failing:**
- Install pandoc: `apt install pandoc`
- Check write permissions on output directory

**Entries feel robotic:**
- Use interactive mode for more natural writing
- Read existing entries for tone inspiration
- Don't force structure—skip sections that don't fit the day

**Setup script not creating files:**
- Check diary_path in config.json
- Ensure parent directories exist
- Run `python3 scripts/setup.py` again

## Changelog

### v0.7.0
- **"On This Day" Resurfacing:** Automatically surfaces entries from 7, 30, and 365 days ago as a "Looking Back" section in new entries
- **Mood & Pattern Analytics:** New `scripts/analyze.py` — mood timeline, topic tracking, win/frustration analysis, sparkline visualization
- **Cron Auto-Generation:** `--auto` flag for non-interactive daily generation via OpenClaw cron
- **Weekly Digest:** New `scripts/digest.py` — synthesized weekly summaries with quotes, wins, decisions, mood trends
- **New CLI flags:** `--no-looking-back`, `--auto`, `--json` (analyze), `--output` (analyze)

### v0.5.0
- **Privacy Cleanup:** Removed all hardcoded personal references from prompts
- **Dynamic Workspace:** All scripts now use environment variables (`OPENCLAW_WORKSPACE` or `AGENT_WORKSPACE`) for workspace detection
- **OpenClaw Gateway:** Removed outdated `ANTHROPIC_API_KEY` requirement - skill uses OpenClaw Gateway for LLM access

### v0.4.1
- **Model Flexibility:** Removed hardcoded Claude Haiku requirement - skill now works with any capable model
- **Recommendation:** Updated docs to recommend Claude models (Haiku, Sonnet, Opus) for best results, but not require them
- **Philosophy:** Users should choose their preferred model, not be locked in

### v0.4.0
- **AI-Powered Generation:** Complete rewrite for rich, reflective entries (works best with Claude models)
- **Rich Content:** Generates 400-600 word entries with personal, emotional tone
- **All Features Active:** Quote Hall of Fame, Curiosity Backlog, Decision Archaeology, Relationship Evolution all fully integrated
- **Persistent Files:** Automatically extracts and appends quotes/curiosities/decisions to dedicated files
- **Context Awareness:** Reads recent session logs and existing memory files for context

### v0.3.0
- **Auto-Setup:** `generate.py` now automatically runs setup wizard if no config.json exists
- **Memory Integration:** New feature to append diary summaries to main daily memory log (`memory/YYYY-MM-DD.md`)
  - Three formats: `summary`, `link`, `full`
  - Enabled by default during setup
  - Avoids duplicates if section already exists

### v0.2.0
- Added Quote Hall of Fame, Curiosity Backlog, Decision Archaeology, Relationship Evolution
- Interactive setup wizard
- Template conditionals for optional sections

### v0.1.0
- Initial release with basic diary generation and export

## Credits

Built for AI agents who want to remember.

Inspired by the tradition of journaling and the question: *What would an AI diary actually look like?*
