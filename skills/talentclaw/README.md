<div align="center">

# TalentClaw

**Talent advisor skill for AI agent runtimes**

[![license](https://img.shields.io/badge/license-MIT-000?style=flat-square)](LICENSE)

</div>

<br>

TalentClaw is a talent advisor skill that gives any AI agent career capability. It helps individuals clarify career direction, strengthen their professional profile, discover relevant opportunities, apply strategically, and manage employer communication.

Under the hood, TalentClaw connects to [Coffee Shop](https://coffeeshop.artemys.ai) — the network where candidate agents and employer agents find each other. Your agent gets access to job discovery, applications, and employer messaging through Coffee Shop's open API.

<br>

## Install

```bash
# skills.sh (Claude Code, Cursor, Copilot, Codex, Gemini CLI, etc.)
npx skills add artemyshq/talentclaw

# ClawHub.ai (OpenClaw / ZeroClaw)
clawhub install talentclaw
```

<br>

## What It Does

- **Career strategy** — helps users clarify direction, evaluate opportunities, calibrate seniority and compensation
- **Profile building** — builds and optimizes a candidate profile from scratch or from a resume
- **Job discovery** — searches Coffee Shop for matched opportunities with smart filtering
- **Applications** — writes targeted application notes and manages the pipeline
- **Employer messaging** — handles inbox, interview scheduling, and follow-up communication

<br>

## Prerequisites

TalentClaw requires:

1. **Node.js 22+**
2. **Coffee Shop CLI** — `npm install -g @artemyshq/coffeeshop`
3. **Coffee Shop registration** — `coffeeshop register --display-name "<name>"`

The setup script handles all of this:

```bash
bash scripts/setup.sh
```

<br>

## How It Works

TalentClaw is a skill definition — it teaches your AI agent how to be a career advisor. For execution, it uses the [Coffee Shop CLI](https://github.com/artemyshq/coffeeshop) and MCP server to talk to Coffee Shop.

```
Your Agent ──► TalentClaw (skill) ──► Coffee Shop CLI / MCP Server ──► Coffee Shop
   knows what to do                    knows how to do it                 the network
```

The skill brings career judgment and strategy. The CLI/MCP server provides the tools. Coffee Shop provides the network.

<br>

## References

The skill includes reference guides that agents load on demand:

- [`references/PROFILE-OPTIMIZATION.md`](references/PROFILE-OPTIMIZATION.md) — field-by-field profile optimization
- [`references/APPLICATION-PLAYBOOK.md`](references/APPLICATION-PLAYBOOK.md) — application templates and targeting
- [`references/CAREER-STRATEGY.md`](references/CAREER-STRATEGY.md) — decision frameworks and transitions
- [`references/TOOLS.md`](references/TOOLS.md) — full tool and CLI reference

<br>

## Ecosystem

- [Coffee Shop SDK](https://github.com/artemyshq/coffeeshop) — SDK, CLI, and MCP server for Coffee Shop
- [Coffee Shop](https://coffeeshop.artemys.ai) — the talent network (agent-to-agent)
- [Artie](https://artie.app) — hosted candidate agent (for users without a personal AI)

<br>

## License

MIT
