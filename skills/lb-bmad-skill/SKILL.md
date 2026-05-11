---
name: bmad-method
description: "Use BMad (Breakthrough Method of Agile AI Driven Development) framework for AI-driven development. Use for: architecture analysis, sprint planning, story generation, PRD creation, and full development workflows. Requires coding-agent skill with Claude Code."
---

# BMad Method Skill

> Use BMad framework for AI-driven development with autonomous agent workflows.

**For detailed reference, see:**
- [docs/reference/commands.md](docs/reference/commands.md) - Complete command reference
- [docs/reference/agents.md](docs/reference/agents.md) - Available agents
- [docs/how-to/install-bmad.md](docs/how-to/install-bmad.md) - Detailed installation guide
- [docs/tutorials/getting-started.md](docs/tutorials/getting-started.md) - Quick start

## DEPENDENCY

**This skill requires coding-agent skill with Claude Code installed.**
- Claude Code must be installed (`~/.local/bin/claude`)
- Use `bash pty:true` for all Claude Code invocations

## Description

BMad (Breakthrough Method of Agile AI Driven Development) is a 4-phase framework:
1. **Analysis** — Explore the problem space
2. **Planning** — Define what to build
3. **Solutioning** — Decide how to build it
4. **Implementation** — Build it

Each phase produces documents that become context for the next phase.

---

## Installation

To use BMad in a project:

> ⚠️ **Security Note:** `npx bmad-method install` fetches code from npm. Only run this if you trust the BMad package. Review the package before installing.

```bash
cd ~/project && npx bmad-method install
```

Select Claude Code when prompted.

### ⚠️ Installation is Interactive

**⚠️ npx bmad-method install asks questions!**

For installation:
- **DO NOT use background:true** - you need to respond to prompts
- **Stay in the session** and answer each question
- **Monitor the log** for these common prompts:

| Prompt in Log | Expected Answer | Notes |
|---------------|----------------|-------|
| "Where should BMad be installed?" | `.` or `~path/to/project` | Current directory |
| "Which AI tool are you using?" | `Claude Code` or number | Select Claude |
| "Select modules to install" | `a` or `enter` | Select all/default |
| "Install BMad in current directory?" | `y` or `enter` | Confirm |

```bash
# Installation must be interactive!
bash pty:true workdir:~/project command:"cd ~/project && npx bmad-method install"
# Stay present, answer each prompt:
# - Monitor log for prompts
# - Submit answer via: process action:submit sessionId:XXX data:"y"
```

### ⚠️ Pre-Flight Check

**Before running any /bmad- command, verify BMad is installed:**

```bash
ls -la ~/project/_bmad/  # or _bmad-output/
```

If not found → run installation first:
```bash
bash pty:true workdir:~/project command:"cd ~/project && npx bmad-method install"
```

---

## Model Selection

**Strategic model selection for efficiency:**

| Model | Best Use Cases |
|-------|----------------|
| **Sonnet** | Architecture, Solutioning, Quick-dev (complex tasks) |
| **Haiku** | Brainstorming, Story generation, Code review (repetitive/structured) |
| **Opus** | Large refactoring, complex architecture decisions |

```bash
# Examples
claude --model sonnet "Create the architecture"
claude --model haiku "Generate stories from the epic"
```

---

## Available Commands (via /bmad-)

| Command | Purpose | Output |
|---------|---------|--------|
| `/bmad-help` | Interactive guide | - |
| `/bmad-brainstorming` | Brainstorm project ideas (use sparingly - see Notes) | `brainstorming-report.md` |
| `/bmad-bmm-create-prd` | Define requirements | `PRD.md` |
| `/bmad-bmm-create-ux-design` | Design UX | `ux-spec.md` |
| `/bmad-bmm-create-architecture` | Technical decisions | `architecture.md` + ADRs |
| `/bmad-bmm-create-epics-and-stories` | Break into stories | Epic files in `_bmad-output/` |
| `/bmad-bmm-check-implementation-readiness` | Gate check | PASS/CONCERNS/FAIL |
| `/bmad-bmm-sprint-planning` | Initialize sprint | `sprint-status.yaml` |
| `/bmad-bmm-create-story` | Prepare next story | `story-[slug].md` |
| `/bmad-bmm-dev-story` | Implement story | Working code + tests |
| `/bmad-bmm-code-review` | Validate quality | Approved/changes requested |
| `/bmad-bmm-quick-spec` | Quick spec (skip phases 1-3) | `tech-spec.md` |
| `/bmad-bmm-quick-dev` | Quick implementation | Working code |

---

## ⚠️ Important: Claude Code Execution

### Use Non-Interactive Mode When Possible

For commands that don't need real-time interaction:

```bash
# Non-interactive (recommended for most BMad workflows)
claude -p --dangerously-skip-permissions "Your prompt"
```

### When to Use Background Mode

Use `background:true` only when:
- Running multiple BMad workflows in sequence
- The workflow is expected to take a long time

**Always monitor with `process action:log` every 10-30 seconds** to detect if Claude Code is waiting for input.

### Permission Configuration

To avoid Claude Code blocking on permission requests:

> ⚠️ **Security Note:** Using `--dangerously-skip-permissions` or `--permission-mode bypassPermissions` suppresses permission checks. Use with caution - only for trusted code execution. For production workflows, prefer default permissions or validate the code first.

```bash
# Skip all permission prompts (use with caution!)
claude --dangerously-skip-permissions "prompt"

# Or use specific permission mode
claude --permission-mode bypassPermissions "prompt"
```

### Permission Loop Detection

**If Claude Code waits for confirmation (Y/n, Commit, etc.):**

1. Check the log: `process action:log sessionId:XXX`
2. Identify the type of prompt:
   - **Shell command (Y/n):** → submit "y"
   - **Git commit proposal:** → submit "n" (see below)
   - **Other:** → evaluate if you know the answer, otherwise ask user

### Task Completion Detection (Background Mode)

**How to know Claude Code is really done:**

1. **Success message in log:** Look for "Task completed", "Done!", "All tasks finished"
2. **Prompt available:** The command prompt is back
3. **Timeout:** If log is silent for **2+ minutes** without completion message → check process:
   ```bash
   ps aux | grep claude
   process action:log sessionId:XXX
   ```

**⚠️ Only consider task complete when you see explicit success message or prompt is back.**

### Session Heartbeat (Long Running Tasks)

For workflows lasting 5+ minutes (/bmad-bmm-dev-story, large refactoring):

**Every 60 seconds with no new log output:**
```bash
# Check if process is still alive
ps aux | grep claude

# If stalled but alive → check if waiting for input
process action:log sessionId:XXX

# If process died → trigger recovery (see below)
```

---

## Autonomous Workflow Patterns

### Pattern 1: Full Analysis + Planning Request

**User says:** "Analyze the current architecture and generate the product brief for project X"

**Agent should:**
1. **Pre-flight check:** Verify BMad installed (`ls _bmad/`)
2. **Check project-context.md:** If absent or outdated, generate it first (see below)
3. Launch Claude Code in the project directory:
   ```bash
   bash pty:true workdir:~/path/to/project background:true command:"claude --dangerously-skip-permissions '/bmad-bmm-create-architecture'"
   ```
4. Monitor progress with `process action:log` (check every 10-30s)
5. If Claude Code needs information → ask the user directly
6. When complete → run: `ls _bmad-output/` to confirm files generated
7. **Verify output:** `grep -i "error" _bmad-output/architecture.md || head -20 _bmad-output/architecture.md`
8. Read `architecture.md` to verify coherence with user's request
9. Then launch product brief: `/bmad-bmm-create-product-brief`

### Pattern 2: Sprint Preparation with Story Generation

**User says:** "Prepare sprint 1 and add tasks to OCM (OpenClaw Mission Center)"

**Agent should:**
1. **Pre-flight check:** Verify BMad installed
2. Launch Claude Code:
   ```bash
   bash pty:true workdir:~/path/to/project background:true command:"claude --dangerously-skip-permissions '/bmad-bmm-sprint-planning && /bmad-bmm-create-epics-and-stories'"
   ```
3. Wait for stories to be generated in `_bmad-output/epics/`
4. **Refresh context**: run `ls -R _bmad-output/` to confirm files exist
5. **Read stories efficiently** (see "Reading Stories Safely" below)
6. **Create OCM tasks from each story** (use task-manager skill)
7. Report completion with task list

#### OCM Task Traceability

**When creating OCM tasks, ALWAYS include the BMad story reference:**

```
Task: Implement login form validation
Description: [full story content]
---
Ref: _bmad-output/epics/auth/stories/story-login-validation.md
Epic: auth
Created from: BMad Sprint 1
```

**Why:** This links the OCM task back to the source story for traceability.

### Pattern 3: Quick Feature Implementation

**User says:** "Implement feature X using quick-dev"

**Agent should:**
1. Launch Claude Code with quick-dev:
   ```bash
   bash pty:true workdir:~/path/to/project command:"claude --dangerously-skip-permissions '/bmad-bmm-quick-dev [feature description]'"
   ```

---

## ⚠️ Quick-Dev vs Standard: The Red Line

**Quick-dev is faster but lacks safeguards. Use wisely.**

| ✅ OK with Quick-Dev | ❌ NEVER with Quick-Dev |
|---------------------|------------------------|
| UI tweaks | Authentication changes |
| Bug fixes | Encryption/Security |
| New endpoints | Database migrations |
| Simple features | Payment logic |
| | Breaking schema changes |

**Rule:** If the change touches security, auth, encryption, or database migrations → **Use full BMad cycle** (Analysis → Solutioning → Implementation)

---

## project-context.md Management

BMad relies on `project-context.md` as the project's "brain". It's the persistent context that guides all decisions.

### Before /bmad-bmm-create-prd

**Always check:**

```bash
ls ~/project/project-context.md
```

### If Missing or Outdated

**Generate or update it:**
```bash
# Option 1: Generate from codebase
bash pty:true workdir:~/project command:"claude '/bmad-bmm-generate-project-context'"

# Option 2: Update manually with user's latest direction
# Ask user: "What's the current vision for this project?"
# Then create/update project-context.md with that info
```

### When User Changes Direction

If user pivots mid-project (new features, different direction):
1. Update `project-context.md` with new intentions
2. Regenerate `architecture.md` if architecture is affected
3. Proceed with updated context

---

## Reading Stories Safely (Avoid Context Overflow)

**Don't dump all stories at once!** Follow this process:

1. **List first:**
   ```bash
   ls _bmad-output/epics/*/stories/
   ```

2. **Check each story header** before reading full:
   ```bash
   head -10 _bmad-output/epics/*/stories/story-*.md
   ```

3. **Read one at a time** for task creation:
   - Read story 1 → create OCM task
   - Read story 2 → create OCM task
   - etc.

4. **For batch operations**, group by epic:
   ```bash
   for f in _bmad-output/epics/*/stories/*.md; do head -20 "$f"; done | head -100
   ```

---

## Command Chain Safety

### ❌ Avoid This (Silent Failures)
```bash
claude "/bmad-cmd1 && /bmad-cmd2"  # If cmd1 fails, cmd2 still runs
```

### ✅ Prefer Sequential Execution
```bash
# Step 1: Run cmd1
bash pty:true background:true command:"claude '/bmad-cmd1'"

# Step 2: Verify output exists
ls _bmad-output/required-file.md
grep -q "expected content" _bmad-output/required-file.md || { echo "FAILED"; exit 1; }

# Step 3: Run cmd2 only if cmd1 succeeded
bash pty:true command:"claude '/bmad-cmd2'"
```

**Rule:** Verify each step before proceeding to the next.

---

## Recovery After Crash

**Scenario:** Claude Code crashes (API error 500, timeout, killed process)

### Step 0: Kill Zombie Processes (BEFORE Restart!)

**⚠️ Always check for stale processes first:**

```bash
# Check if Claude is still running
ps aux | grep claude

# Kill any zombie processes for this project
pkill -f "claude.*projects/roundvision" || echo "No zombie processes"

# Also kill any hanging node processes
pkill -f "npx.*bmad" || echo "No zombie npx"
```

### Step 1: Check what was generated

1. **Check what was generated:**
   ```bash
   ls -lt _bmad-output/*.md | head -10
   ```

2. **Find the last valid file:**
   ```bash
   # Read the most recently modified output
   ls -t _bmad-output/*.md | head -1 | xargs head -30
   ```

3. **Resume from where it stopped:**
   - If `architecture.md` exists but `stories/` missing → run story generation
   - If `stories/` exist but no OCM tasks → create tasks from existing stories
   - If partial output → check coherence, regenerate only what's missing

4. **Never restart from zero** if partial output exists

---

## Handling Claude Code Questions

When Claude Code asks questions during execution:

1. **Check the log first** with `process action:log sessionId:XXX` to see what it asked
2. **If you know the answer** → provide it via `process action:submit`
3. **If you need to ask the user** → pause and get clarification first
4. **If Claude Code is blocked** → tell it to ask for what it needs, then come back to you

Example:
```bash
# Claude asks: "What's your preferred authentication provider?"
# If you don't know → ask user: "Claude needs to know auth provider - Auth0, Firebase, or Supabase?"

# Then provide the answer:
process action:submit sessionId:XXX data:"Auth0"
```

---

## When to Use BMad vs Direct Coding-Agent

### Use BMad for:
- New features or epics
- Architecture changes or refactoring
- Sprint planning with story generation
- Technical documentation (PRD, architecture)
- Anything security-sensitive

### Use coding-agent directly (without BMad) for:
- Quick fixes and small corrections
- Simple code reviews
- One-file changes
- Experiments/prototyping

**Rule of thumb:** If it needs a story breakdown and sprint planning → BMad. If it's a simple edit → coding-agent directly.

---

## Reading BMad Outputs

After BMad workflows complete, documents are in:

```
project/
├── _bmad/
│   └── config.yaml
├── _bmad-output/
│   ├── brainstorming-report.md
│   ├── product-brief.md
│   ├── PRD.md
│   ├── ux-spec.md
│   ├── architecture.md
│   ├── epics/
│   │   └── epic-[name]/
│   │       └── stories/
│   │           └── story-[slug].md
│   └── sprint-status.yaml
└── project-context.md
```

**⚠️ Always verify files exist** by running `ls _bmad-output/` or `ls -R _bmad-output/` after each workflow.

**Verify output validity** before reading:
```bash
# Quick check
ls -la _bmad-output/architecture.md

# Validate content
head -20 _bmad-output/architecture.md

# Check for errors
grep -i "error\|fail" _bmad-output/architecture.md
```

### Cache Refresh (Perception Reset)

**⚠️ After Claude Code modifies source files, your cached view is stale!**

**Rule:** After each successful Claude Code intervention on source code:
1. **Don't assume** your previous read of a file is still valid
2. **Re-read** the file if you need to work on it further
3. **Clear mental cache** - explicitly read the file again

```bash
# Bad: Assuming old read is still valid
read path:"~/project/src/auth.js"  # ❌ May be outdated

# Good: Read fresh after Claude modified it
exec command:"cat ~/project/src/auth.js"  # ✅ Fresh content
```

---

## Validation Step

Before moving to Implementation phase:

1. Read the generated `architecture.md` (or `tech-spec.md` for quick-dev)
2. Verify it aligns with user's original request
3. If misaligned → regenerate or clarify with user

---

## Error Handling

| Error | Solution |
|-------|----------|
| `Command not found` | Check PATH: `echo $PATH` and `which claude` |
| `npx: command not found` | Install Node.js 20+ |
| `_bmad/ not found` | Run `npx bmad-method install` first |
| Claude stuck on permission | Use `--dangerously-skip-permissions` |
| API 500 error | Trigger recovery (see "Recovery After Crash") |
| Session timeout | Check if process still running, resume if possible |

### ⚠️ Safety Rules
- **Never run `rm -rf` via Claude Code without explicit human validation**
- **Never use quick-dev for security-sensitive changes**
- **Default Git answer: "n" (let OpenClaw handle commits)**

---

## Git Commit Handling

Claude Code often asks: "Do you want to commit these changes? [y/N]"

- **Reply "n"** to keep Git control with OpenClaw
- **Reply "y"** ONLY if user explicitly requested full Git autonomy

```bash
# When Claude asks to commit, default to "n"
process action:submit sessionId:XXX data:"n"
```

---

## Examples

### Example 1: Architecture Analysis + Product Brief (Sequential)

**User:** "On project PingRoot, analyze the current architecture and generate the product brief"

**Agent does:**
```bash
# 1. Pre-flight check
ls ~/projects/pingroot/_bmad/ || echo "Need to install BMad"

# 2. Check/update project-context.md
ls ~/projects/pingroot/project-context.md || echo "Need to create project-context.md"

# 3. Launch architecture workflow
bash pty:true workdir:~/projects/pingroot background:true command:"claude --dangerously-skip-permissions '/bmad-bmm-create-architecture'"

# 4. Monitor, wait for completion
process action:poll sessionId:XXX

# 5. Verify output
ls _bmad-output/architecture.md
head -20 _bmad-output/architecture.md
grep -i "error" _bmad-output/architecture.md || echo "OK"

# 6. If OK, verify coherence with user request
# 7. If coherent, launch product brief
bash pty:true workdir:~/projects/pingroot command:"claude --dangerously-skip-permissions '/bmad-bmm-create-product-brief'"

# 8. Deliver outputs
```

### Example 2: Sprint Preparation + OCM Tasks (with safety checks)

**User:** "Prepare sprint 1 for RoundVision and add tasks to OCM"

**Agent does:**
```bash
# 1. Pre-flight check
ls ~/projects/roundvision/_bmad/ || npx bmad-method install

# 2. Check project-context.md
ls ~/projects/roundvision/project-context.md || echo "Update this first!"

# 3. Launch sprint planning + story creation
bash pty:true workdir:~/projects/roundvision background:true command:"claude --dangerously-skip-permissions '/bmad-bmm-sprint-planning && /bmad-bmm-create-epics-and-stories'"

# 4. Monitor and wait for completion
process action:poll sessionId:XXX  # repeat until done

# 5. Refresh context - verify files exist
ls -R ~/projects/roundvision/_bmad-output/epics/

# 6. List stories first (don't dump all at once!)
ls ~/projects/roundvision/_bmad-output/epics/*/stories/

# 7. Read and process stories one by one
for story in ~/projects/roundvision/_bmad-output/epics/*/stories/*.md; do
  echo "=== $(basename $story) ==="
  head -20 "$story"
  # Create OCM task from this story
done

# 8. Report: "Created X tasks in OCM for Sprint 1"
#    IMPORTANT: Each OCM task must include story path as reference!
```

### Example 3: Quick Fix (No BMad Needed)

**User:** "Fix the typo in the login page"

**Agent does:**
```bash
# Direct coding-agent, no BMad workflow needed
bash pty:true workdir:~/projects/login command:"claude 'Fix the typo on line 42: \"Passowrd\" → \"Password\"'"
```

### Example 4: Recovery After Crash

**Scenario:** Claude Code crashes during story generation

**Agent does:**
```bash
# 0. Cleanup zombies FIRST!
ps aux | grep claude
pkill -f "claude.*projects/roundvision" || echo "Clean"

# 1. Check what was generated
ls -lt ~/project/_bmad-output/ | head -10

# 2. Find last valid file
ls -t ~/project/_bmad-output/epics/*/stories/ | head -1

# 3. Check if partial stories exist
ls ~/project/_bmad-output/epics/*/stories/*.md | wc -l

# 4. If partial → resume from last point
# If 3 stories out of 5 → generate remaining 2
# If 0 stories → restart story generation

# 5. Continue without restarting from zero
```

---

## ⚠️ CRITICAL: Sub-Agent (Minion) Access

**The minion does NOT automatically have access to project files! sub-agent to implement**

When spawning a a task, you MUST provide:

### 1. Project Directory Access

```bash
# Minion needs workdir to access project files
sessions_spawn workdir:"~/projects/roundvision" ...
```

### 2. Story + Context + Architecture

**⚠️ NEVER give only the story to a minion!**

The story says "Add a login button" but doesn't say:
- Is this React, Vue, or vanilla JS?
- Does it use Tailwind or Bootstrap?
- What's the existing auth pattern?

**You MUST provide:**

1. **Story** (what to build)
2. **project-context.md** (project rules, tech stack)
3. **architecture.md** (technical decisions)

```bash
# Step 1: Read all three
cat ~/projects/roundvision/project-context.md
cat ~/projects/roundvision/_bmad-output/architecture.md  
cat ~/projects/roundvision/_bmad-output/epics/auth.md

# Step/stories/story-login 2: Combine into a comprehensive prompt
sessions_spawn task:"You are implementing this story: [STORY]. 
Project context: [CONTEXT].
Architecture: [ARCHITECTURE].
Follow the patterns defined in architecture.md."
```

### 3. OCM Task Should Include Story Path

```json
{
  "title": "Implement login form validation",
  "description": "Full story content...",
  "source": "_bmad-output/epics/auth/stories/story-login.md"
}
```

**⚠️ Without workdir + story content + context + architecture, the minion is blind and cannot implement anything!**

---

## Notes

- **BMad brainstorming**: Use sparingly. OpenClaw itself is a brainstorming agent. Use BMad for technical structuring, keep high-level strategy with OpenClaw.
- BMad generates files in `_bmad-output/`
- `project-context.md` is the project's brain - keep it updated
- `/bmad-help` provides interactive guidance
- Always use `pty:true` with Claude Code
- For model restrictions, use `--model <sonnet|haiku|opus>`
- **Token efficiency**: Use direct coding-agent for small tasks, reserve BMad for complex workflows
- **Sequential over chained**: Verify each step before proceeding

---

## Related Skills

- **coding-agent** — Required for launching Claude Code
- **task-manager** — For creating OCM tasks from BMad stories
