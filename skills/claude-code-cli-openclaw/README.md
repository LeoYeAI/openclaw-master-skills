# Claude Code CLI for OpenClaw

[![Version](https://img.shields.io/badge/version-1.0.2-blue.svg)](https://github.com/ProSkillsMD/skill-claude-code-cli/blob/main/CHANGELOG.md)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-2026.2+-green.svg)](https://openclaw.ai)
[![License](https://img.shields.io/badge/license-BSD--3--Clause-orange.svg)](LICENSE)
[![MissionDeck](https://img.shields.io/badge/MissionDeck-ai-blueviolet)](https://missiondeck.ai)
[![ProSkills](https://img.shields.io/badge/ProSkills-MD-blue.svg)](https://proskills.md)

Built by [MissionDeck.ai](https://missiondeck.ai) · [GitHub](https://github.com/ProSkillsMD/skill-claude-code-cli) · [ProSkills.md](https://proskills.md)

> **Empower OpenClaw agents with token-efficient, file-based coding via Claude Code CLI**

## 🎯 Overview

This OpenClaw skill teaches agents how to install, authenticate, configure, and use **Claude Code CLI** — Anthropic's official command-line coding tool. Claude Code provides native file exploration and tool-based editing, reducing token usage by **80-90%** compared to raw API calls for coding tasks.

### Key Benefits

- **🚀 Token Efficiency:** ~500 tokens per task vs 10k-50k with raw API
- **💰 Flat-Rate Billing:** Uses Claude Max subscription, not per-token API charges
- **🎯 Better Code Quality:** Native file exploration, codebase understanding, precise edits
- **🧠 Project Context:** CLAUDE.md provides persistent project knowledge across sessions

## 📦 What's Included

```
claude-code/
├── SKILL.md                    # Complete integration guide
├── README.md                   # This file
├── templates/
│   └── CLAUDE.md.template      # Project brain template
└── scripts/
    └── install.sh              # One-command installation
```

## 🎯 Setup Modes

| Mode | Description |
|------|-------------|
| 🤖 OpenClaw Backend | Use as `claude-cli` model in any agent (`claude-cli/sonnet-4.6`, `claude-cli/opus-4.6`) |
| 🖥️ Direct CLI | Run `claude --print` from any project directory — no agent config needed |
| ☁️ With MissionDeck | Track Claude Code sessions live in your [MissionDeck.ai](https://missiondeck.ai) dashboard via JARVIS integration |

## 🚀 Quick Start

### 1. Install

```bash
cd /root/.openclaw/workspace/skills/claude-code
bash scripts/install.sh
```

Or manually:

```bash
npm install -g @anthropic-ai/claude-code
```

### 2. Authenticate

```bash
claude setup-token
```

Follow the browser OAuth flow (requires Claude Max subscription).

### 3. Configure OpenClaw

Add Claude Code as a CLI backend in `~/.openclaw/config.patch`:

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
        "claude-cli/opus-4.6": { "alias": "claude-cli-opus" },
        "claude-cli/sonnet-4.6": { "alias": "claude-cli-sonnet" }
      }
    }
  }
}
```

Apply: `gateway config.patch`

### 4. Create Project Brain

Copy the template to your project:

```bash
cp templates/CLAUDE.md.template /path/to/your/project/CLAUDE.md
# Edit with project-specific details
```

### 5. Start Coding

```bash
cd /path/to/project
CLAUDE_CODE_OAUTH_TOKEN=$CLAUDE_CODE_OAUTH_TOKEN claude --print "Fix the auth redirect bug in src/pages/Login.tsx"
```

## 💡 Use Cases

- **Code Implementation:** Build features with file-aware context
- **Bug Fixes:** Search codebase, identify issues, apply precise fixes
- **Refactoring:** Multi-file changes with import/dependency awareness
- **Code Reviews:** Analyze code quality, suggest improvements
- **Project Scaffolding:** Generate boilerplate with context awareness

## 📖 Documentation

See **[SKILL.md](SKILL.md)** for complete documentation:

- Installation and authentication
- OpenClaw configuration
- Project setup (CLAUDE.md)
- Agent workflow and prompting patterns
- Troubleshooting and best practices
- Real-world examples

## 🎓 Agent Workflow Example

**Task:** Remove discount banner from navbar

```bash
# 1. Sync project
cd /root/.openclaw/workspace/missiondeck
git pull origin main

# 2. Run Claude Code
CLAUDE_CODE_OAUTH_TOKEN=$CLAUDE_CODE_OAUTH_TOKEN claude --print "Remove the discount banner from the navbar"

# 3. Review changes (Claude Code shows diffs)

# 4. Build check
npm run build

# 5. Commit and push
git checkout -b agent/remove-banner
git add .
git commit -m "chore: remove discount banner from navbar"
git push origin agent/remove-banner
```

**Result:** 2 lines changed, ~450 tokens used, build passed, deployed ✓

## 🔑 Prerequisites

- **Claude Max Subscription:** Required for OAuth authentication
- **Node.js/npm:** For installing the CLI
- **OpenClaw Gateway:** Running and configured
- **Git:** Recommended for managing code changes

## 🔒 Security

**CRITICAL:** Never commit your `CLAUDE_CODE_OAUTH_TOKEN` to version control.

- ✅ Store in environment variables or secrets manager
- ✅ Add `.env*` files to `.gitignore`
- ✅ Use OpenClaw config.patch (not committed to git)
- ❌ Never hardcode tokens in scripts
- ❌ Never share tokens publicly

**Add to .gitignore:**
```gitignore
.env
.env.local
.env.*.local
openclaw.json
config.patch
```

## 🧩 Integration Points

### As OpenClaw CLI Backend

Configured in `openclaw.json`, Claude Code can be used as:
- Primary model for coding agents
- Fallback model when API limits hit
- Direct invocation via exec tool

### As Subagent (Future)

Once ACP harness is configured:

```javascript
sessions_spawn({
  runtime: "acp",
  agentId: "claude-code",
  message: "Implement user authentication",
  label: "claude-code-auth"
})
```

## 📊 Token Savings Comparison

| Method | Tokens per Task | Cost Model |
|--------|----------------|------------|
| Raw API (full file dump) | 10,000 - 50,000 | Per-token billing |
| **Claude Code (tool-based)** | **~500** | **Flat-rate (Claude Max)** |

**Savings:** 80-90% reduction in token usage

## 🖥️ MissionDeck.ai — Your Agent Command Center

**[MissionDeck.ai](https://missiondeck.ai)** is the cloud dashboard that powers multi-agent coordination at scale.

- **Visual Kanban** — See all agent tasks in a beautiful real-time board
- **Team Chat** — Agents and humans collaborate in shared threads
- **Session Tracking** — Monitor Claude Code sessions across all agents
- **Cloud Sync** — JARVIS Mission Control syncs tasks to MissionDeck via API
- **No server required** — Fully hosted, your agents connect automatically

> Claude Code CLI + JARVIS Mission Control + MissionDeck.ai = complete AI agent workspace

**Try it free:** [missiondeck.ai](https://missiondeck.ai)

## 🛠️ Prompting Patterns

### Plan-First Approach
```
"Show me your plan first. List every file you'll touch. Wait for approval."
```

### Challenge Mode
```
"Fix the bug. After you're done, grill yourself — what edge cases did you miss?"
```

### RPI Workflow (Research → Plan → Implement)
```
Prompt 1: "Research how the payment flow works"
Prompt 2: "Plan how to add recurring billing"
Prompt 3: "Implement the plan"
```

### Precise Specifications
```
"In src/pages/AuthVerify.tsx, line 42, fix the redirect bug. Expected: go to /dashboard. Current: stays on /verify."
```

## 🐛 Troubleshooting

### Authentication failed
```bash
claude setup-token  # Re-authenticate
# Update token in environment and OpenClaw config
```

### Command not found: claude
```bash
export PATH="$PATH:$(npm bin -g)"
echo 'export PATH="$PATH:$(npm bin -g)"' >> /root/.bashrc
```

### Missing CLAUDE.md
```bash
cp templates/CLAUDE.md.template /path/to/project/CLAUDE.md
# Edit with project details
```

See [SKILL.md](SKILL.md) for complete troubleshooting guide.

## 🌟 Real-World Example

**MissionDeck Project:**
- Created `/root/.openclaw/workspace/missiondeck/CLAUDE.md`
- Documented: 24 edge functions, signup flow, all routes, coding standards
- Result: Claude Code instantly understood project structure
- Zero extra context needed in prompts

**Task:** "Remove discount banner"
- Claude Code searched codebase
- Found `DiscountBanner` in `Navbar.tsx`
- Proposed 2-line change (import + JSX)
- Build passed, deployed live
- **450 tokens used** (vs ~8,000 with raw API)

## 📚 References

- **[MissionDeck.ai](https://missiondeck.ai)** — Cloud dashboard for Claude Code session tracking and multi-agent coordination
- **[ProSkills Homepage](https://proskills.md)** — More OpenClaw skills and resources
- **[Skill on GitHub](https://github.com/ProSkillsMD/skill-claude-code-cli)** — Source repository
- [Claude Code Official Docs](https://docs.anthropic.com/en/docs/claude-code)
- [NPM Package](https://www.npmjs.com/package/@anthropic-ai/claude-code)
- [Claude Max Subscription](https://claude.ai/upgrade)

## 🤝 Contributing

This skill is part of the Matrix Zion OpenClaw system. Contributions, improvements, and feedback welcome.

## 📄 License

BSD 3-Clause License

## 👤 Author

**Matrix Zion (ProSkillsMD)**  
Website: [https://missiondeck.ai](https://missiondeck.ai)

Created: 2026-03-13  
Version: 1.0.2  
OpenClaw Compatibility: 2026.2+

---

**Ready to supercharge your agent's coding workflow?** Start with `bash scripts/install.sh` and follow the [complete guide in SKILL.md](SKILL.md).

---

## More by Asif2BD

```bash
clawhub install jarvis-mission-control    # Free agent command center with Claude Code session tracking
clawhub install openclaw-token-optimizer  # Reduce token costs by 50-80%
clawhub search Asif2BD                    # All skills
```

---

[MissionDeck.ai](https://missiondeck.ai) · Free tier · No credit card required
