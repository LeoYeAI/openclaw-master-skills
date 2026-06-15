---
name: Claude Code CLI for OpenClaw
version: 1.0.2
author: Matrix Zion (ProSkillsMD)
description: Install, authenticate, and use Claude Code CLI as a native coding tool for any OpenClaw agent system.
homepage: https://missiondeck.ai
tags: [claude-code, coding, cli, anthropic, agent-tools]
openclaw: ">=2026.2"
metadata:
  {
    "openclaw":
      {
        "emoji": "🤖",
        "requires": { "bins": ["node", "npm"] },
        "install":
          [
            {
              "id": "listing",
              "kind": "link",
              "label": "📚 ProSkills Listing",
              "url": "https://proskills.md/skills/claude-code-cli",
            },
            {
              "id": "github",
              "kind": "link",
              "label": "GitHub Repository",
              "url": "https://github.com/ProSkillsMD/skill-claude-code-cli",
            },
            {
              "id": "missiondeck",
              "kind": "link",
              "label": "☁️ MissionDeck.ai Cloud",
              "url": "https://missiondeck.ai",
            },
          ],
      },
  }
---

# Skill: Claude Code CLI for OpenClaw

## Description

This skill teaches OpenClaw agents how to install, authenticate, configure, and use Claude Code CLI as a coding tool. Claude Code is an official Anthropic CLI that provides file-based context efficiency, reducing token usage by 80-90% compared to raw API calls for coding tasks.

**Key Benefits:**
- **Token Efficiency:** ~500 tokens per task vs 10k-50k with raw API (Claude Code reads files via tools instead of dumping full content into context)
- **Flat-Rate Billing:** Uses Claude Max subscription (OAuth), not per-token API billing
- **Better Code Quality:** Native file exploration, codebase understanding, and precise edits
- **Project Context:** CLAUDE.md file provides persistent project brain across sessions

**Use Cases:**
- Code implementation and refactoring
- Bug fixes with file exploration
- Multi-file code changes
- Project scaffolding
- Code reviews and analysis

## 🎯 Setup Modes

| Mode | Description |
|------|-------------|
| 🤖 OpenClaw Backend | Use as `claude-cli` model in any agent (`claude-cli/sonnet-4.6`, `claude-cli/opus-4.6`) |
| 🖥️ Direct CLI | Run `claude --print` from any project directory — no agent config needed |
| ☁️ With MissionDeck | Track Claude Code sessions live in your [MissionDeck.ai](https://missiondeck.ai) dashboard via JARVIS integration |

## Prerequisites

- **Claude Max Subscription:** Required for OAuth authentication (cannot use raw API keys)
- **Node.js/npm:** For installing the CLI globally
- **TTY Terminal:** Required for OAuth setup flow (use `pty: true` with exec tool)
- **Git:** Recommended for managing code changes in branches
- **OpenClaw Gateway:** Must be running to apply config patches

## Installation

### Step 1: Install Claude Code CLI

```bash
npm install -g @anthropic-ai/claude-code
```

### Step 2: Verify Installation

```bash
which claude && claude --version
```

Expected output:
```
/usr/bin/claude
2.1.75
```

### Quick Install

Use the provided installation script:

```bash
cd /root/.openclaw/workspace/skills/claude-code
bash scripts/install.sh
```

The script handles:
- NPM package installation
- Version verification
- Environment setup preparation

## Authentication

Claude Code requires **browser-based OAuth authentication** using a Claude Max subscription. Raw API keys (sk-ant-api03-*) will NOT work.

### Interactive Setup (One-Time)

Run this in a PTY terminal (requires TTY):

```bash
claude setup-token
```

**Flow:**
1. CLI shows spinner + authorization URL:
   ```
   https://claude.ai/oauth/authorize?code=true&client_id=...&code_challenge=...
   ```
2. Copy URL and open in browser
3. Authorize the application with your Claude Max account
4. Browser shows authorization code
5. Paste code back into terminal at prompt: `Paste code here if prompted >`
6. Success: `✓ Long-lived authentication token created successfully!`
7. Token format: `sk-ant-oat01-xxxxx` (valid for 1 year)

### Storing the Token

The token must be available as the `CLAUDE_CODE_OAUTH_TOKEN` environment variable.

**Option 1: Shell RC Files (Recommended)**
```bash
echo "export CLAUDE_CODE_OAUTH_TOKEN=YOUR_OAUTH_TOKEN_HERE" >> /root/.bashrc
echo "export CLAUDE_CODE_OAUTH_TOKEN=YOUR_OAUTH_TOKEN_HERE" >> /root/.profile
source /root/.bashrc
```

**Option 2: System-Wide**
```bash
echo "CLAUDE_CODE_OAUTH_TOKEN=YOUR_OAUTH_TOKEN_HERE" >> /etc/environment
```

**Option 3: OpenClaw Config Only**

Add to your `openclaw.json` config patch (see next section) — the token will be available during OpenClaw backend calls but not direct CLI usage.

### 🔒 Security Warning

**CRITICAL:** Never commit your `CLAUDE_CODE_OAUTH_TOKEN` to version control.

- ✅ Store in environment variables or secrets manager
- ✅ Add `.env*` files to `.gitignore`
- ✅ Use OpenClaw config.patch (not committed to git)
- ❌ Never hardcode tokens in scripts
- ❌ Never share tokens publicly or in screenshots
- ❌ Never commit tokens to GitHub/GitLab

**Add to your .gitignore:**
```gitignore
.env
.env.local
.env.*.local
openclaw.json
config.patch
```

### Verification

```bash
echo $CLAUDE_CODE_OAUTH_TOKEN
# Should output: sk-ant-oat01-xxxxx
```

## OpenClaw Configuration

Integrate Claude Code as a CLI backend in OpenClaw, enabling it as a model option and fallback.

### Config Patch

Create or append to `~/.openclaw/config.patch`:

```json
{
  "agents": {
    "defaults": {
      "cliBackends": {
        "claude-cli": {
          "command": "/usr/bin/claude",
          "env": {
            "CLAUDE_CODE_OAUTH_TOKEN": "YOUR_OAUTH_TOKEN_HERE"
          }
        }
      },
      "models": {
        "claude-cli/opus-4.6": {
          "alias": "claude-cli-opus"
        },
        "claude-cli/sonnet-4.6": {
          "alias": "claude-cli-sonnet"
        }
      }
    },
    "list": [
      {
        "id": "tank",
        "model": {
          "primary": "anthropic/claude-opus-4-5",
          "fallbacks": [
            "google/gemini-3-flash-preview",
            "claude-cli/opus-4.6"
          ]
        }
      }
    ]
  }
}
```

### Apply Configuration

```bash
gateway config.patch
```

Verify in gateway logs or test by spawning a coding session.

### Available Models

- `claude-cli/sonnet-4.6` → Claude Sonnet 4.6 (fast, general coding)
- `claude-cli/opus-4.6` → Claude Opus 4.6 (complex reasoning, architecture)

Use as primary model, fallback, or invoke directly via exec.

## Project Setup (CLAUDE.md)

**Critical:** Every project using Claude Code should have a `CLAUDE.md` file in its root directory. This is the "project brain" — Claude Code reads it automatically at session start.

### What to Include

```markdown
# Project: [Name]

## Overview
[1-2 sentence project description]

## Tech Stack
- Language: [e.g., TypeScript, Python, Rust]
- Framework: [e.g., Next.js, FastAPI, Supabase]
- Key Dependencies: [list major packages]

## Directory Structure
```
/
├── src/           # Source code
├── public/        # Static assets
├── supabase/      # Database functions, migrations
└── docs/          # Documentation
```

## Key Files
- `src/App.tsx` - Main app component, routing
- `src/lib/supabase.ts` - Database client
- `supabase/functions/` - Edge functions (24 total)

## Coding Standards
- Use TypeScript strict mode
- Functional components (React)
- Tailwind CSS for styling
- ESLint + Prettier configured

## Deployment
- Platform: Netlify (frontend), Supabase (backend)
- Deploy command: `npm run build`
- Environment: `.env.local` (never commit)

## Critical Rules
- Never commit API keys
- Always run `npm run build` before pushing
- All functions must have TypeScript types

## Testing
- `npm test` - Run Jest tests
- `npm run lint` - Check code style
```

### Template Usage

Copy the provided template and customize:

```bash
cp /root/.openclaw/workspace/skills/claude-code/templates/CLAUDE.md.template /path/to/your/project/CLAUDE.md
# Edit with project-specific details
```

### Real Example

For MissionDeck project, we created:
- `/root/.openclaw/workspace/missiondeck/CLAUDE.md`
- Result: Claude Code instantly knew: 24 edge functions, signup flow, all routes, coding standards
- Zero extra context needed in prompts

## Agent Workflow

### Daily Coding Workflow

**Step 1: Sync Project**
```bash
cd /path/to/project
git pull origin main
```

**Step 2: Run Claude Code with Task**
```bash
CLAUDE_CODE_OAUTH_TOKEN=$CLAUDE_CODE_OAUTH_TOKEN claude --print "Fix the signup redirect bug in src/pages/AuthVerify.tsx — users aren't being redirected to /dashboard after magic link verification"
```

**Step 3: Review Proposed Changes**

Claude Code will:
- Search the codebase
- Identify affected files
- Propose changes with diffs
- Explain reasoning

**Step 4: Build Check**
```bash
npm run build  # or npm test, cargo build, etc.
```

**Step 5: Commit and Push**
```bash
git checkout -b agent/fix-signup-redirect
git add .
git commit -m "fix: redirect to /dashboard after magic link verification"
git push origin agent/fix-signup-redirect
```

**Step 6: Create PR (Optional)**
```bash
gh pr create --title "Fix signup redirect" --body "Fixes redirect bug in AuthVerify.tsx"
```

### OpenClaw Exec Pattern

For agents using the `exec` tool:

```javascript
exec({
  command: `cd /path/to/project && CLAUDE_CODE_OAUTH_TOKEN=$CLAUDE_CODE_OAUTH_TOKEN claude --print "Your task here"`,
  workdir: "/path/to/project",
  pty: false  // PTY not needed for --print mode
})
```

### Subagent Spawn Pattern (Future)

Once ACP harness is configured:

```javascript
sessions_spawn({
  runtime: "acp",
  agentId: "claude-code",
  message: "Fix the navbar bug in components/Navbar.tsx",
  label: "claude-code-navbar-fix"
})
```

## Prompting Patterns

Effective prompts yield better results. Here are proven patterns:

### 1. Plan-First Approach

```
"Show me your plan first. List every file you'll touch and what changes you'll make. Wait for my approval before implementing."
```

**Why:** Prevents unwanted changes, gives you control

### 2. Challenge Mode

```
"Fix the authentication bug. After you're done, grill yourself — what edge cases did you miss? What could break?"
```

**Why:** Forces deeper reasoning, catches edge cases

### 3. RPI Workflow (Research → Plan → Implement)

For complex tasks, use 3 separate prompts:

**Prompt 1 (Research):**
```
"Research how the payment flow works. Show me all relevant files and how they connect."
```

**Prompt 2 (Plan):**
```
"Now plan how to add recurring billing. List the changes step-by-step."
```

**Prompt 3 (Implement):**
```
"Implement the plan. Make the changes."
```

**Why:** Breaks complexity into manageable phases

### 4. Precise Specifications

```
"In src/pages/AuthVerify.tsx, line 42, the redirect after magic link verification is broken. Expected behavior: redirect to /dashboard. Current behavior: stays on /verify. Fix it."
```

**Why:** Clear context = precise fixes

### 5. File-Focused Tasks

```
"Refactor src/lib/database.ts — extract the connection pool logic into a separate file src/lib/db-pool.ts"
```

**Why:** Claude Code excels at file-level operations

### Anti-Patterns (Avoid These)

❌ Vague: "Make the app better"  
❌ No context: "Fix the bug"  
❌ Too broad: "Rewrite the entire codebase"  
❌ Missing paths: "Update the config file" (which one?)  

✅ Specific: "Fix the redirect bug in src/pages/AuthVerify.tsx — users should go to /dashboard after email verification"  
✅ Scoped: "Refactor the authentication logic in src/lib/auth.ts to use async/await instead of promises"  
✅ Clear paths: "Update the database connection pool size in src/config/database.ts from 10 to 20"

## Why Claude Code vs Raw API

### Token Usage Comparison

| Method | Tokens per Task | Cost Model |
|--------|----------------|------------|
| Raw API (full file dump) | 10,000 - 50,000 | Per-token ($) |
| Claude Code (tool-based) | ~500 | Flat-rate (Claude Max subscription) |

**Savings:** 80-90% reduction in token usage

### How It Works

**Raw API Approach:**
```
User: "Fix the bug in App.tsx"
Agent: [reads entire App.tsx] [dumps 5,000 tokens into context] [generates fix] [writes back]
Cost: ~7,000 tokens
```

**Claude Code Approach:**
```
User: "Fix the bug in App.tsx"
Claude Code: [uses file tool to read App.tsx] [analyzes in isolation] [generates fix] [uses edit tool]
Cost: ~500 tokens
```

**Result:** Same quality, 90% fewer tokens, flat-rate billing

### Code Quality Benefits

- **Codebase Exploration:** Claude Code searches files, understands structure
- **Precise Edits:** Tool-based editing, not regex replacement
- **Context Awareness:** Reads CLAUDE.md automatically, no prompt overhead
- **Multi-file Operations:** Handles imports, dependencies across files

## Real-World Example

### Task
"Remove the offer/discount banner from MissionDeck navbar"

### Process

**Claude Code Execution:**
```bash
cd /root/.openclaw/workspace/missiondeck
CLAUDE_CODE_OAUTH_TOKEN=$CLAUDE_CODE_OAUTH_TOKEN claude --print "Remove the discount banner from the navbar"
```

**What Happened:**
1. Claude Code searched codebase for "banner", "discount", "navbar"
2. Found `DiscountBanner` component in `src/components/Navbar.tsx`
3. Identified exactly 2 changes needed:
   - Remove `import { DiscountBanner } from './DiscountBanner'`
   - Remove `<DiscountBanner />` JSX element
4. Proposed changes with diff
5. Build passed: `npm run build` ✓
6. Pushed to branch: `oracle/disable-discount-banner`
7. Merged to main → deployed live

**Token Usage:** ~450 tokens  
**Time:** 30 seconds  
**Result:** Precise, working, deployed

## Troubleshooting

### Issue: "Authentication failed"

**Cause:** Token expired or invalid

**Fix:**
```bash
claude setup-token  # Re-authenticate
# Update token in environment and OpenClaw config
```

### Issue: "command not found: claude"

**Cause:** NPM global bin not in PATH

**Fix:**
```bash
export PATH="$PATH:$(npm bin -g)"
echo 'export PATH="$PATH:$(npm bin -g)"' >> /root/.bashrc
```

### Issue: "Could not read CLAUDE.md"

**Cause:** Project missing CLAUDE.md file

**Fix:**
```bash
cp /root/.openclaw/workspace/skills/claude-code/templates/CLAUDE.md.template /path/to/project/CLAUDE.md
# Edit with project details
```

### Issue: PTY required error during setup

**Cause:** `claude setup-token` needs TTY

**Fix (with OpenClaw exec):**
```javascript
exec({
  command: "claude setup-token",
  pty: true  // Enable pseudo-terminal
})
```

### Issue: "No such file or directory" errors

**Cause:** Running Claude Code from wrong directory

**Fix:** Always `cd` into project root first
```bash
cd /path/to/project
CLAUDE_CODE_OAUTH_TOKEN=$CLAUDE_CODE_OAUTH_TOKEN claude --print "your task"
```

### Issue: Changes not applied

**Cause:** Claude Code proposes changes, but requires approval in interactive mode

**Fix:** Use `--print` flag for non-interactive mode (outputs to stdout)
```bash
claude --print "your task"  # No approval needed, just shows output
```

For interactive mode (approval required):
```bash
claude  # Interactive, will wait for y/n approval
```

## Advanced Usage

### Batch Operations

Process multiple tasks sequentially:

```bash
cd /path/to/project
CLAUDE_CODE_OAUTH_TOKEN=$CLAUDE_CODE_OAUTH_TOKEN claude --print "Task 1: Fix auth bug"
CLAUDE_CODE_OAUTH_TOKEN=$CLAUDE_CODE_OAUTH_TOKEN claude --print "Task 2: Add new endpoint"
CLAUDE_CODE_OAUTH_TOKEN=$CLAUDE_CODE_OAUTH_TOKEN claude --print "Task 3: Update tests"
```

### Model Selection

Force specific model:

```bash
claude --model opus-4.6 --print "Complex architecture refactor"
claude --model sonnet-4.6 --print "Quick bug fix"
```

### Integration with Git Workflow

```bash
# Create feature branch
git checkout -b feature/claude-code-implementation

# Run Claude Code
CLAUDE_CODE_OAUTH_TOKEN=$CLAUDE_CODE_OAUTH_TOKEN claude --print "Implement feature X"

# Review changes
git diff

# Commit
git add .
git commit -m "feat: implement X using claude-code"

# Push
git push origin feature/claude-code-implementation
```

## Best Practices

1. **Always create CLAUDE.md** — It's the project brain, saves token overhead
2. **Use feature branches** — Never commit directly to main
3. **Run builds before committing** — Catch errors early
4. **Be specific in prompts** — Include file paths, expected behavior
5. **Review proposed changes** — Claude Code is good, but verify
6. **Store token securely** — Use environment variables, not hardcoded
7. **Sync before working** — `git pull` to avoid conflicts
8. **Use plan-first for complex tasks** — Get approval before implementation

## References

- **[MissionDeck.ai](https://missiondeck.ai)** — Cloud dashboard for Claude Code session tracking and multi-agent coordination
- **[ProSkills Homepage](https://proskills.md)** — More OpenClaw skills and resources
- **[Claude Code Official Docs](https://docs.anthropic.com/en/docs/claude-code)** — Anthropic documentation
- **[GitHub Repository](https://github.com/ProSkillsMD/skill-claude-code-cli)** — Skill source
- **[NPM Package](https://www.npmjs.com/package/@anthropic-ai/claude-code)** — Claude Code CLI on npm
- **[Claude Max Subscription](https://claude.ai/upgrade)** — Required for OAuth auth

## Skill Metadata

- **Version:** 1.0.2
- **Author:** Matrix Zion (ProSkillsMD)
- **Homepage:** https://missiondeck.ai
- **Created:** 2026-03-13
- **Updated:** 2026-03-14
- **License:** BSD 3-Clause
- **Dependencies:** Node.js, npm, Claude Max subscription
- **OpenClaw Compatibility:** 2026.2+

---

**Next Steps:**
1. Install Claude Code: `npm install -g @anthropic-ai/claude-code`
2. Authenticate: `claude setup-token`
3. Configure OpenClaw: Add CLI backend to `config.patch`
4. Create project CLAUDE.md: Copy template and customize
5. Start coding: `CLAUDE_CODE_OAUTH_TOKEN=$token claude --print "your task"`

---

## More by Asif2BD

```bash
clawhub install jarvis-mission-control    # Free agent command center with Claude Code session tracking
clawhub install openclaw-token-optimizer  # Reduce token costs by 50-80%
clawhub search Asif2BD                    # All skills
```

---

[MissionDeck.ai](https://missiondeck.ai) · Free tier · No credit card required
