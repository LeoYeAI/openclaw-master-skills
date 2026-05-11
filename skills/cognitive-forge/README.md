# Cognitive Forge (认知锻造)

> Your AI reads books, extracts mental models, and builds a growing library of decision frameworks. The more books processed, the more compound thinking ability your AI gains.

[![ClawHub](https://img.shields.io/badge/ClawHub-Published-blue)](https://clawhub.ai)
[![Version](https://img.shields.io/badge/version-2.0.0-green)](https://github.com/your-repo)
[![License](https://img.shields.io/badge/license-MIT--0-lightgrey)](LICENSE)

---

## What Makes This Different

**Most AI skills** give you answers.
**Cognitive Forge** builds your AI's **decision framework library**.

Every book processed → One new mental model → Permanently stored in `thinking-patterns.md`.

After 100 books, your AI has 100 reusable frameworks (Taleb's antifragility, Munger's mental models, Kahneman's dual-process theory, etc.) that it can reference across ANY domain.

Building compound thinking, one book at a time.

---

## One Run, Dual Value

Each run produces two outputs simultaneously:

### 1. For You: F.A.C.E.T. Analysis
Sharp, actionable analysis for deep book comprehension:

- **[F] Framework**: Core mechanism in 50 words (not what author said, but what theory DOES)
- **[A] Anchor Case**: Most iconic real-world example (vivid stories stick)
- **[C] Contradiction**: What "common sense" does this destroy?
- **[E] Edge**: When does this model fail? Fragile assumptions?
- **[T] Transfer**: Map to YOUR reality TODAY (personalized to your job/projects)

Not a book summary — a battle-tested mental model you can apply immediately.

### 2. For Your AI: Knowledge Base Entry
The extracted model is permanently written to `thinking-patterns.md`. In future sessions, your AI can reference this framework when answering complex questions.

---

## Quick Start

### 1. Install Dependencies

This skill requires:
- [`book-scout`](https://clawhub.ai/kedoupi/book-scout) — Finds high-quality books via web search
- [`mental-model-forge`](https://clawhub.ai/kedoupi/mental-model-forge) — Applies F.A.C.E.T. analysis

```bash
# Install from ClawHub
clawhub install kedoupi/book-scout
clawhub install kedoupi/mental-model-forge

# Or manually copy to ~/.openclaw/workspace/skills/
```

### 2. Tell Your AI to Use It

**Daily learning (recommended)**:
```
Ask your AI: "Run cognitive-forge daily at 8:30 AM. Topic: Business Strategy."
```

Your AI will:
1. Find a high-quality book on the topic (Douban ≥7.5 or Goodreads ≥3.8)
2. Extract the core mental model (F.A.C.E.T. analysis)
3. Write it to `thinking-patterns.md` (permanent storage)
4. Deliver a summary to you

**One-time book processing**:
```
Ask your AI: "Use cognitive-forge to analyze: 'Thinking, Fast and Slow' by Daniel Kahneman"
```

**First run**: The skill auto-creates all necessary files and directories. No manual setup needed.

---

## How It Works

### The Permanent Upgrade Loop

```
┌─────────────────────────────────────────────────────┐
│  1. Book Selection                                   │
│     ├── Priority: Direct specify > User queue > Search │
│     ├── Filter: Douban ≥7.5 OR Goodreads ≥3.8        │
│     └── Dedup: Book title + Model name (dual-layer)  │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  2. F.A.C.E.T. Analysis + Quality Verification      │
│     ├── [F] Extract core framework                   │
│     ├── [A] Find iconic case study                   │
│     ├── [C] Identify contrarian insight              │
│     ├── [E] Map failure modes                        │
│     ├── [T] Transfer to user's context               │
│     └── Self-check: Score ≥7/10 or retry             │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  3. Write to thinking-patterns.md (PERMANENT)        │
│     ├── Classify: Pattern / Principle / Concept      │
│     ├── Tag with multiple categories                 │
│     └── Verify write with date + model name check    │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  4. Your AI Can Now Reference This Model             │
│     When you ask for advice in ANY domain:           │
│     "Should I invest in X?"                          │
│     → AI checks thinking-patterns.md                 │
│     → Applies relevant frameworks                    │
│     → Gives strategically grounded insight            │
└─────────────────────────────────────────────────────┘
```

---

## Features

### Breadth vs Depth Mode

| Mode | Behavior | Use When |
|------|----------|----------|
| **Breadth** (default) | 1 book → 1 model | Daily learning, covering diverse topics |
| **Depth** | 1 book → up to 5 models | Deep-diving into a rich book (e.g., *Antifragile*) |

**Depth mode** extracts multiple models from one book until:
- 5 models reached, OR
- New model is a variant of an existing one, OR
- AI determines no more independent frameworks remain

**Usage**: "深度分析这本书" or `depth_mode: depth`

### Multi-Source Book Selection

Three sources (priority order):
1. **Direct specify**: "Analyze *Thinking, Fast and Slow*"
2. **User queue**: Pre-queue books in `reading-history.json`
3. **Web search**: `book-scout` finds high-quality books automatically

### Configurable Topic Mapping

Default weekly rotation:
```
Mon: Business Strategy | Tue: Psychology | Wed: Technology
Thu: Economics | Fri: Innovation | Sat: Philosophy | Sun: Biography
```

Override in `HEARTBEAT-reading.md` to match your learning goals.

### Brief / Full Output

| Mode | Content | Default |
|------|---------|---------|
| **Full** | Complete F.A.C.E.T. + scenarios + counter-example + strategic question | Yes |
| **Brief** | 4-line summary with "expand" option | User requests `output: brief` |

### Knowledge Library Status

```
Ask: "cognitive-forge status"
```
Returns: total models, category distribution, weak areas, recent entries.

### Weekly Review (Spaced Repetition)

```
Ask: "cognitive-forge review"
```
Quizzes you on 2-3 models from the past week. Also auto-triggers on Sundays if configured.

### Error Recovery

If a run fails mid-way, the next run detects the failure and offers to resume from where it stopped.

---

## How to Maximize Value

### 1. Enable Auto-Scanning in AGENTS.md

Add this to your `AGENTS.md` (optional):

```markdown
## Session Startup

1. Read `SOUL.md` — this is who you are
2. Read `USER.md` — this is who you're helping
3. Read `memory/YYYY-MM-DD.md` (today + yesterday) for recent context
4. **Load `memory/knowledge-base/thinking-patterns.md`** — your decision frameworks
```

**Why**: Every session, your AI loads its accumulated mental models. When answering complex questions, it references `thinking-patterns.md` for relevant frameworks.

**Example**:
```
You: "Should I pivot my startup to B2B?"

Your AI:
1. Reads thinking-patterns.md
2. Finds: "Clayton Christensen's Jobs-to-be-Done"
3. Finds: "Andy Grove's Strategic Inflection Points"
4. Applies both frameworks to your question
5. Gives a strategically grounded answer
```

### 2. Schedule Daily Learning

**Weekly rotation example**:
```
Monday: Business Strategy
Tuesday: Psychology/Decision Science
Wednesday: Product/Design Thinking
Thursday: Finance/Economics
Friday: Philosophy/Systems Thinking
Saturday: Technology/Innovation
Sunday: Review week's mental models
```

Diverse mental models → Better cross-domain thinking.

```bash
openclaw cron create --name "Daily Book" --schedule "30 8 * * *" \
  --task "Run cognitive-forge. Topic: [based on weekday mapping]"
```

### 3. Force Your AI to Apply Models

**Generic ask** (doesn't use mental models):
```
"Should I hire more people?"
```

**Strategic ask** (forces model application):
```
"Apply mental models from thinking-patterns.md: Should I hire more people?
Consider: Brook's Law, Two-Pizza Teams, Scaling Challenges."
```

---

## Sample Output

### Book: *Thinking, Fast and Slow* by Daniel Kahneman

**F.A.C.E.T. Analysis**:

```markdown
[F] Framework: Dual-Process Theory
Human cognition operates via two systems:
- System 1: Fast, automatic, emotional (95% of decisions)
- System 2: Slow, deliberate, rational (used only when forced)
Core: System 1 dominates by default → cognitive biases emerge when System 2 fails to override.

[A] Anchor Case: The Linda Problem
Most people choose the more specific description (conjunction fallacy).
System 1 says "the story fits!" System 2 (if engaged) knows the math.

[C] Contradiction
"People make rational decisions when given good information."
→ NO. Even experts rely on System 1 and commit systematic errors.

[E] Edge
Fails when: experts in narrow domains (chess masters' intuition IS reliable),
time-critical survival decisions, culturally variable contexts.

[T] Transfer (personalized)
For your AI product at 爱康国宾:
1. User onboarding → Design for System 1 (one-click, zero thinking)
2. Critical health decisions → Force System 2 (add friction before confirming)
3. Team decisions → Ask "What System 1 biases made us love this feature?"
```

---

## Use Cases

### 1. Build a Personal Decision Framework Library
- **Who**: Founders, investors, strategists
- **How**: Process 1 book/week for 1 year = 52 mental models
- **Value**: Every future decision taps into 52 frameworks

### 2. Team Learning System
- **Who**: Product teams, research labs
- **How**: Rotate book topics weekly, share F.A.C.E.T. analyses
- **Value**: Shared mental model language → Better collaboration

### 3. AI-Powered Reading Coach
- **Who**: Lifelong learners
- **How**: Your AI reads books you don't have time for, extracts models
- **Value**: You get the wisdom without reading 300 pages

### 4. Deep-Dive Single Books
- **Who**: Anyone studying a specific author or domain
- **How**: Use depth mode to extract 3-5 models from one rich book
- **Value**: Thorough extraction, no framework left behind

---

## File Structure

```
cognitive-forge/
├── SKILL.md                       # Main workflow definition
├── README.md                      # This file
└── references/
    ├── book-selection.md          # Multi-source selection + configurable mapping
    ├── example-output.md          # Full and brief mode examples
    └── knowledge-classification.md # Three-type classification with tag system
```

---

## How This Differs from "Book Summary" Tools

| Feature | Cognitive Forge | Traditional Summary Tools |
|---------|----------------|---------------------------|
| **Goal** | Extract reusable mental model | Condense book content |
| **Focus** | Transferable frameworks | Facts and key points |
| **Permanence** | Written to thinking-patterns.md (forever) | Forgotten after reading |
| **Application** | Your AI references it across domains | You read it once |
| **Personalization** | [T] Transfer maps to YOUR context | Generic for everyone |
| **Longevity** | Models compound over time | Summaries don't interact |
| **Quality** | Self-verified (score ≥ 7/10) | No quality gate |

---

## Advanced Usage

### Multi-Book Cross-Analysis

```
Ask your AI: "Process 3 books on decision-making:
1. Thinking, Fast and Slow (Kahneman)
2. Superforecasting (Tetlock)
3. The Black Swan (Taleb)

Then cross-analyze: Where do their mental models agree? Conflict? Complement?"
```

### Domain-Specific Model Curation

**For product managers**:
```
Schedule: Process 1 product/UX book per week
Topics: Jobs-to-be-Done, Hooked Model, Lean Startup, Design Thinking
Result: thinking-patterns.md becomes your PM playbook
```

**For investors**:
```
Topics: Mental Models (Munger), Antifragile (Taleb), Capital (Piketty)
Result: thinking-patterns.md becomes your investment decision framework
```

### Feishu/Notion Integration (Optional)

If you set `FEISHU_APP_TOKEN` or `NOTION_API_KEY`, the skill auto-uploads:
- Book title, F.A.C.E.T. analysis, reading date, mental model tags

Benefit: Build a searchable knowledge base across your team.

---

## Troubleshooting

**"Book-scout can't find books on my topic"**:
- Try broader topics (e.g., "Psychology" instead of "Behavioral Economics of Crypto")
- Or specify a book directly: "Analyze: [Book Title] by [Author]"
- Or add books to your queue: "Add *[Book Title]* to my reading queue"

**"F.A.C.E.T. analysis is too shallow"**:
- The skill now self-verifies quality (score ≥ 7/10) and retries automatically
- For deeper analysis: "Deep F.A.C.E.T. analysis with multiple examples"
- Claude Opus recommended for best results

**"How do I see what mental models my AI has learned?"**:
```bash
# Check your knowledge library
cat ~/.openclaw/workspace/memory/knowledge-base/thinking-patterns.md

# Or use the status command
Ask: "cognitive-forge status"
```

**"My AI isn't applying learned models"**:
- Check if `thinking-patterns.md` is loaded in AGENTS.md
- Explicitly ask: "Apply mental models from thinking-patterns.md to [question]"

**"A run failed halfway"**:
- Next run will auto-detect and offer to resume
- Check `reading-history.json` → `last_attempted` field for details

---

## Important Notes

**Data Persistence**: This skill writes to `thinking-patterns.md` and `reading-history.json` in your workspace. These files persist across sessions.

**Optional Integration**: The "auto-load thinking-patterns.md" feature requires manual configuration in your `AGENTS.md`. The skill does NOT automatically modify your agent's behavior without your explicit setup.

**Export Tokens**: Environment variables (`FEISHU_APP_TOKEN`, `NOTION_API_KEY`) are entirely optional. The skill works perfectly fine without them (local-only mode).

**First Run**: All necessary files and directories are auto-created on first run. No manual setup required beyond installing dependencies.

---

## License

MIT-0 (No Attribution Required)

---

## Credits

Created by **汤圆 (Tangyuan)** for 雯姐's learning journey.

**Inspired by**:
- Charlie Munger's "latticework of mental models"
- Nassim Taleb's antifragility & skin in the game
- Daniel Kahneman's dual-process theory
- Shane Parrish's Farnam Street framework

**Built with**:
- [`book-scout`](https://clawhub.ai/kedoupi/book-scout) — Quality book discovery
- [`mental-model-forge`](https://clawhub.ai/kedoupi/mental-model-forge) — F.A.C.E.T. analysis engine

---

## Feedback

Report issues or share your experience at [ClawHub](https://clawhub.ai).

If you've processed 50+ books and want to share what your AI has learned, ping `@KeDOuPi` on ClawHub.
