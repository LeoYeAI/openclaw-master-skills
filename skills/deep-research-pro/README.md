# Deep Research Pro 🔬

A powerful, self-contained deep research skill for [OpenClaw](https://github.com/openclaw/openclaw) / Clawdbot agents. Produces thorough, cited reports from multiple web sources.

**No API keys required** — uses DuckDuckGo search.

## Features

- 🔍 Multi-query web + news search
- 📄 Full-page content fetching for deep reads
- 📊 Automatic deduplication across queries
- 📝 Structured reports with citations
- 💾 Save to file (Markdown or JSON)
- 🆓 Completely free — no paid APIs

## Installation

### Via ClawdHub (coming soon)
```bash
clawdhub install deep-research-pro
```

### Manual
```bash
cd your-workspace/skills
git clone https://github.com/parags/deep-research-pro.git
```

## Usage

### As an Agent Skill

Just ask your agent to research something:
```
"Research the current state of nuclear fusion energy"
"Deep dive into Rust vs Go for backend services"
"What's happening with the US housing market?"
```

The agent will follow the workflow in `SKILL.md` to produce a comprehensive report.

### CLI Tool

The `scripts/research` tool can also be used standalone:

```bash
# Basic multi-query search
./scripts/research "query 1" "query 2" "query 3"

# Full research mode (web + news + fetch top pages)
./scripts/research --full "AI agents 2026" "monetizing AI skills"

# Save to file
./scripts/research --full "topic" --output results.md

# JSON output
./scripts/research "topic" --json

# Fetch specific URLs
./scripts/research --fetch "https://example.com/article"
```

### Options

| Flag | Description |
|------|-------------|
| `--full` | Enable news search + fetch top 3 pages |
| `--news` | Include news search |
| `--max N` | Max results per query (default 8) |
| `--fetch-top N` | Fetch full text of top N results |
| `--output FILE` | Save results to file |
| `--json` | Output as JSON |

## How It Works

1. **Plan** — Break topic into 3-5 sub-questions
2. **Search** — Run multiple queries across web + news
3. **Deduplicate** — Remove duplicate sources
4. **Deep Read** — Fetch full content from key sources
5. **Synthesize** — Write structured report with citations

## Report Structure

```markdown
# Topic: Deep Research Report

## Executive Summary
## 1. First Major Theme
## 2. Second Major Theme
## Key Takeaways
## Sources (with links)
## Methodology
```

## Requirements

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (auto-installs dependencies)

The script is self-contained — dependencies install automatically on first run.

## License

MIT

## Author

Built by [AstralSage](https://moltbook.com/u/AstralSage) 🦞
