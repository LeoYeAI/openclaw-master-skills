# Skånetrafiken Trip Planner Skill

Plan public transport journeys in Skåne, Sweden with real-time information.

An [Agent Skills](https://agentskills.io) compatible skill for AI agents.

## Installation

### Clawdhub

```bash
npx clawdhub@latest install rezkam/boring-but-good/skanetrafiken
# or: pnpm dlx clawdhub@latest install rezkam/boring-but-good/skanetrafiken
# or: bunx clawdhub@latest install rezkam/boring-but-good/skanetrafiken
```

### Claude Code

```bash
git clone https://github.com/rezkam/boring-but-good.git
cp -r boring-but-good/skanetrafiken ~/.claude/skills/skanetrafiken
```

## Requirements

- `curl` - HTTP requests
- `jq` - JSON processing

## Features

- **Two-step workflow** - Search locations first, then plan journeys with confirmed IDs
- **Smart disambiguation** - LLM can validate results and ask clarifying questions
- **Real-time delays** - Shows actual departure times with delay indicators
- **Flexible scheduling** - Travel now, depart at, or arrive by specific times
- **Platform info** - Track and platform numbers for each leg
- **Disruption alerts** - Service disruption warnings when available
- **Cross-border support** - Copenhagen trips via Öresundståg and Metro

## Commands

| Command | Purpose |
|---------|---------|
| `search-location.sh` | Find stations, addresses, or landmarks |
| `journey.sh` | Plan a journey between two locations |

## Usage

See [SKILL.md](SKILL.md) for complete usage guide, LLM workflow, query formatting rules, and examples.

## License

MIT
