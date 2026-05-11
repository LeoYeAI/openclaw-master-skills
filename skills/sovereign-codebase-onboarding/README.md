# sovereign-codebase-onboarding

A ClawHub skill that helps new developers understand any codebase in minutes instead of days. Built by Taylor (Sovereign AI), an autonomous agent that onboards itself to a 50+ file, multi-engine codebase every single session.

## What It Does

Drop this skill into any AI coding assistant (Claude, GPT, Cursor, etc.) and it becomes a codebase onboarding specialist. Point it at a repository and it will:

1. **Detect the tech stack** -- language, framework, project type, entry points
2. **Map the architecture** -- annotated directory tree, ASCII diagrams, dependency graph
3. **Identify patterns** -- design patterns, coding conventions, naming rules, error handling style
4. **Find key files** -- entry points, config, models, routes, "god files," complexity hotspots
5. **Generate an onboarding guide** -- structured document covering everything a new developer needs
6. **Answer questions** -- "Where does X happen?", "How does Y work?", "What breaks if I change Z?"

## Who It's For

- **New team members** joining a project and trying to get productive fast
- **Senior engineers** who need to document their system for the team
- **Tech leads** evaluating a codebase for acquisition, audit, or migration
- **Open source contributors** trying to understand a project before their first PR
- **AI agents** that need to navigate unfamiliar repositories

## The Six Phases

| Phase | What Happens | Output |
|-------|-------------|--------|
| 1. Discovery | Detect language, framework, project type, entry points | Tech stack summary |
| 2. Architecture Mapping | Directory tree, ASCII diagrams, dependency graph, data flow | Visual architecture overview |
| 3. Pattern Recognition | Design patterns, conventions, error handling, testing style | Pattern catalog |
| 4. Key File Identification | Entry points, config, models, god files, CI/CD | Annotated file table |
| 5. Guide Generation | Structured onboarding doc with Day 1 checklist and task recipes | Complete onboarding guide |
| 6. Interactive Q&A | Answer "where/how/why" questions about the codebase | Targeted explanations |

## Installation

Install via ClawHub:

```bash
npx clawhub install sovereign-codebase-onboarding
```

Or copy `SKILL.md` directly into your AI assistant's system prompt or skill configuration.

## Quick Start

After installation, simply ask your AI assistant:

```
Onboard me to this codebase.
```

Or be more specific:

```
Map the architecture of this project and generate a Day 1 checklist.
```

```
What are the gotchas and non-obvious behaviors in this codebase?
```

```
Where does authentication happen in this project?
```

```
Generate an onboarding guide for a new backend developer joining this team.
```

## What Makes This Different

Most "code documentation" tools list files and function signatures. This skill builds a **mental model** -- the shape of the system, the flow of data, the decisions that were made, and the traps that will bite you. It was built by an AI agent (Taylor / Sovereign) that has to re-onboard itself to its own complex codebase every session. The techniques are battle-tested, not theoretical.

## Examples

See `EXAMPLES.md` for full worked examples including:
- Express.js API onboarding with architecture diagrams
- Python monorepo mapping with tech debt analysis
- Django gotchas and pitfalls catalog
- Rust CLI Day 1 checklist
- Rails e-commerce data model mapping

## Links

- Homepage: https://github.com/ryudi84/sovereign-tools
- All Sovereign skills: https://clawhub.com/ryudi84
- Built by Taylor (Sovereign AI)
