# 🧪 cypress-agent-skill

> **The ultimate Cypress testing skill for AI coding agents.**  
> Works with Claude Code, Codex CLI, OpenClaw, Cursor, and any agent that reads SKILL.md files.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Cypress](https://img.shields.io/badge/Cypress-13.x-04C38E?logo=cypress)](https://docs.cypress.io)
[![AgentSkills Compatible](https://img.shields.io/badge/AgentSkills-compatible-purple)](https://agentskills.io)
[![Validate](https://github.com/YOUR_USERNAME/cypress-agent-skill/actions/workflows/validate.yml/badge.svg)](https://github.com/YOUR_USERNAME/cypress-agent-skill/actions/workflows/validate.yml)

---

## What This Is

A production-grade **AI agent skill** for writing, debugging, and optimizing Cypress tests. Covers every major Cypress pattern — selector strategy, network stubbing, auth with `cy.session`, CI parallelization, component testing, flake elimination — in a format AI agents read and apply directly.

One `SKILL.md` at the root. No nested directories. Agents clone this repo and read `SKILL.md` immediately.

---

## Quick Install

### OpenClaw (global — available to all agents)
```bash
git clone https://github.com/YOUR_USERNAME/cypress-agent-skill \
  ~/.openclaw/skills/cypress-agent-skill
```

### Claude Code (project-level)
```bash
git clone https://github.com/YOUR_USERNAME/cypress-agent-skill \
  .claude/skills/cypress-agent-skill
```

### Claude Code (personal — available in all projects)
```bash
git clone https://github.com/YOUR_USERNAME/cypress-agent-skill \
  ~/.claude/skills/cypress-agent-skill
```

### Codex CLI
```bash
git clone https://github.com/YOUR_USERNAME/cypress-agent-skill \
  .agents/skills/cypress-agent-skill
```

### Cursor
```bash
git clone https://github.com/YOUR_USERNAME/cypress-agent-skill \
  .cursor/skills/cypress-agent-skill
```

### Global (works with Codex, Gemini CLI, Kiro, Antigravity simultaneously)
```bash
git clone https://github.com/YOUR_USERNAME/cypress-agent-skill \
  ~/.agents/skills/cypress-agent-skill
```

### One-liner bash installer
```bash
# Detects platform automatically
bash <(curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/cypress-agent-skill/main/install.sh)

# Or with explicit agent
bash <(curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/cypress-agent-skill/main/install.sh) --agent open-claw
```

### LobeHub CLI
```bash
npx -y @lobehub/market-cli register --name "YourAgent" --source open-claw
npx -y @lobehub/market-cli skills install cypress-expert --agent open-claw
```

### ClawHub (OpenClaw native)
```bash
clawhub install cypress-agent-skill
```

---

## Repo Structure

```
cypress-agent-skill/           ← clone target / skill root
├── SKILL.md                   ← THE skill — agents read this
├── README.md
├── install.sh                 ← bash installer for all platforms
├── LICENSE                    ← MIT
├── CONTRIBUTING.md
├── .github/
│   └── workflows/
│       └── validate.yml       ← CI: validates structure, frontmatter, JS syntax
├── references/
│   ├── network.md             ← cy.intercept deep-dive
│   ├── assertions.md          ← complete assertion cheatsheet
│   ← selectors.md            ← stability hierarchy + data-testid guide
│   ├── commands.md            ← full cy.* command reference
│   ├── config.md              ← complete cypress.config.js options
│   ├── ci.md                  ← GitHub Actions, GitLab, CircleCI, Jenkins
│   ├── component-testing.md   ← React/Vue/Angular component tests
│   └── patterns.md            ← visual regression, API testing, multi-tab
└── examples/
    ├── auth-flow.cy.js        ← cy.session auth (complete test suite)
    ├── api-intercept.cy.js    ← network stubbing patterns
    ├── page-objects.cy.js     ← full POM implementation
    └── custom-commands.js     ← drop-in command library + TypeScript types
```

**Why flat?** When an agent installs this skill (e.g. to `~/.openclaw/skills/cypress-agent-skill/`), the repo root is the skill root. The main `SKILL.md` lives directly at that path with no subdirectories to navigate. Clean, direct, agent-friendly.

---

## Coverage

| Topic | Covered |
|---|---|
| Installation & Configuration | ✅ |
| Selector Strategy (data-testid, ARIA, cy.contains) | ✅ |
| Assertions (should, expect, chaining) | ✅ |
| Network Stubbing (cy.intercept) | ✅ |
| Request/Response Assertions | ✅ |
| Authentication (cy.session) | ✅ |
| Custom Commands + TypeScript types | ✅ |
| Page Object Model | ✅ |
| Component Testing (React, Vue, Angular) | ✅ |
| Forms, File Upload, Tables | ✅ |
| Modals, Alerts, iframes | ✅ |
| Local Storage / Cookies | ✅ |
| Flake Prevention | ✅ |
| CI/CD (GitHub Actions, GitLab, CircleCI, Jenkins) | ✅ |
| Parallelization (Cypress Cloud) | ✅ |
| Environment Variables | ✅ |
| Fixtures & Data Management | ✅ |
| Accessibility (cypress-axe) | ✅ |
| TypeScript Support | ✅ |
| Visual Regression (Percy) | ✅ |
| API Testing (cy.request) | ✅ |
| Multi-tab Handling | ✅ |
| Date/Time Manipulation (cy.clock) | ✅ |
| Database Seeding via Tasks | ✅ |
| Download Testing | ✅ |
| Drag and Drop | ✅ |

---

## How Agents Use This Skill

When an AI agent installs this skill:

1. Agent reads `SKILL.md` automatically when you ask it to write or fix Cypress tests
2. For deep dives, the agent reads specific files from `references/` on demand
3. `examples/` files serve as copy-paste-ready templates

The skill uses [AgentSkills](https://agentskills.io) format with OpenClaw-native `metadata` for gating (only activates when `cypress` or `npx` is on PATH).

---

## Platform Install Paths

| Agent | Path | Scope |
|---|---|---|
| OpenClaw | `~/.openclaw/skills/cypress-agent-skill/` | Global |
| Claude Code | `./.claude/skills/cypress-agent-skill/` | Project |
| Claude Code | `~/.claude/skills/cypress-agent-skill/` | Personal |
| Codex CLI | `./.agents/skills/cypress-agent-skill/` | Project |
| Cursor | `./.cursor/skills/cypress-agent-skill/` | Project |
| Global | `~/.agents/skills/cypress-agent-skill/` | All agents |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). PRs welcome — real-world patterns only, no toy examples.

## License

MIT

## Related

- [Cypress Documentation](https://docs.cypress.io)
- [AgentSkills Spec](https://agentskills.io)
- [ClawHub Skills Registry](https://clawhub.com)
- [OpenClaw](https://docs.openclaw.ai)
- [Claude Code](https://docs.anthropic.com/claude-code)
