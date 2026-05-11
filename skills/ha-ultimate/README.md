# 🏠 ha-ultimate — Definitive Home Assistant Skill

The most comprehensive Home Assistant skill for AI agents. Control 25+ entity domains
via REST API with safety enforcement, entity inventory generation, a CLI wrapper,
webhook support, and complete documentation.

[![ClawHub](https://img.shields.io/badge/ClawHub-ha--ultimate-blue)](https://clawhub.ai/skills/ha-ultimate)

Works with [OpenClaw](https://github.com/openclaw/openclaw),
[Claude Code](https://docs.anthropic.com/en/docs/claude-code),
[Cursor](https://cursor.com), and any tool supporting the
[SKILL.md](https://agentskills.io) standard.

## Features

| Category | What you get |
|----------|-------------|
| **25+ domains** | Lights, switches, climate, locks, covers, fans, media, vacuum, alarm, notifications, presence, weather, calendar, TTS, input helpers, sensors, scenes, scripts, automations |
| **Safety system** | Layered: mandatory confirmation rules + blocked entities file |
| **CLI wrapper** | `scripts/ha.sh` — one-liner commands for everything |
| **Entity inventory** | `scripts/inventory.js` — generates full ENTITIES.md with areas |
| **Webhooks** | Bidirectional HA ↔ Agent communication |
| **Dashboard** | Quick status command for presence, lights, temps, locks, doors |
| **Templates** | Jinja2 template evaluation via /api/template |
| **History** | Entity state history and logbook queries |
| **Batch ops** | Control multiple entities in a single API call |
| **Error handling** | HTTP status codes, entity verification, troubleshooting guide |

## Quick Start

```bash
# 1. Set credentials
export HA_URL="http://192.168.1.100:8123"
export HA_TOKEN="your-long-lived-access-token"

# 2. Test connection
scripts/ha.sh info

# 3. Generate entity inventory
node scripts/inventory.js

# 4. Start controlling
scripts/ha.sh on light.living_room
scripts/ha.sh dashboard
```

## File Structure

```
homeassistant/
├── SKILL.md                     # Main skill (read by AI agents)
├── README.md                    # This file
├── _meta.json                   # Skill metadata
├── ENTITIES.md                  # Generated entity inventory (after running inventory.js)
├── blocked_entities.json        # Optional: entities to block from automation
├── .env                         # Optional: HA_URL and HA_TOKEN
├── scripts/
│   ├── ha.sh                    # CLI wrapper for all HA operations
│   └── inventory.js             # Entity inventory generator (Node.js)
└── references/
    ├── api.md                   # REST API reference
    ├── webhooks.md              # Webhook setup guide (HA → Agent)
    └── troubleshooting.md       # Common issues and solutions
```

## Credits & Acknowledgments

This skill was created by analyzing and combining the best features from **four
published ClawHub skills** plus a personal skill. Each brought unique strengths
that made the whole greater than the sum of its parts.

| Skill | Author | Version | Key Contributions |
|-------|--------|---------|-------------------|
| **[home-assistant](https://clawhub.ai)** | `kn739j7n05pt...` | 1.0.0 | CLI wrapper (ha.sh), webhook support (HA → Agent), config file pattern |
| **[homeassistant-cli](https://clawhub.ai)** | `kn76s8zyvh2p...` | 1.0.0 | Event monitoring concepts, output format flexibility, troubleshooting docs, auto-completion reference |
| **[homeassistant-skill](https://clawhub.ai)** | [anotb](https://github.com/anotb/homeassistant-skill) | 2.1.0 | **Primary base** — 25 entity domains, template API, history/logbook, area discovery, batch operations, dashboard overview, safety rules, error handling |
| **[moltbot-ha](https://clawhub.ai)** | [iamvaleriofantozzi](https://github.com/iamvaleriofantozzi/moltbot-ha) | 0.1.1 | Mechanical safety system (3 levels), blocked/allowed entities with wildcards, action logging concept, Docker networking docs |
| **mia personal** | Paco | custom | Entity inventory generator (inventory.js), .env configuration pattern |

### How this skill was built

A detailed feature-by-feature comparison of all five source skills was performed
to identify the strengths and gaps of each. The comparison table is included as
`ha-skills-comparison.html` in the project documentation. From that analysis:

- **S3 (homeassistant-skill by anotb)** was selected as the base due to its
  unmatched domain coverage (25 domains) and comprehensive API documentation
- **S4 (moltbot-ha)** inspired the safety architecture and blocked entities concept
- **S1 (home-assistant)** provided the CLI wrapper pattern and webhook documentation
- **S2 (homeassistant-cli)** contributed troubleshooting patterns and format flexibility
- **S5 (mia personal)** provided the inventory generator and .env configuration approach

## License

MIT — See individual source projects for their respective licenses.

## Links

- [Home Assistant REST API Docs](https://developers.home-assistant.io/docs/api/rest/)
- [OpenClaw](https://github.com/openclaw/openclaw)
- [ClawHub](https://clawhub.ai)
- [SKILL.md Standard](https://agentskills.io)
