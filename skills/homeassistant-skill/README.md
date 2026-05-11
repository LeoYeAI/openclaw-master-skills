# Home Assistant Skill

An AI agent skill for controlling Home Assistant devices and automations through natural language. 25 entity domains including lights, climate, locks, presence, weather, calendars, notifications, and more — all via the HA REST API.

Works with [Claude Code](https://docs.anthropic.com/en/docs/claude-code), [OpenClaw](https://github.com/openclaw/openclaw), [Cursor](https://cursor.com), and any tool supporting the [SKILL.md](https://agentskills.io) standard.

[![ClawHub](https://img.shields.io/badge/ClawHub-homeassistant--skill-blue)](https://clawhub.ai/skills/homeassistant-skill)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Part of [unsol.dev](https://unsol.dev)

## Prerequisites

- Home Assistant instance with API access
- `curl` and `jq` installed

## Installation

### Claude Code

```bash
git clone https://github.com/anotb/homeassistant-skill.git ~/.claude/skills/homeassistant-skill
```

### OpenClaw (via ClawdHub)

```bash
clawhub install homeassistant-skill
```

### Cursor / Other

Clone to your agent's skill directory.

## Configuration

1. Create a long-lived access token in Home Assistant: Profile → Long-Lived Access Tokens
2. Set environment variables:

```bash
export HA_URL=http://10.0.0.10:8123
export HA_TOKEN=your-long-lived-access-token
```

## What You Can Do

| Domain | Actions |
|--------|---------|
| Switches | Turn on, off, toggle |
| Lights | On/off, brightness, color, color temp |
| Scenes | Activate scenes |
| Scripts | List, run, run with variables |
| Automations | Trigger, enable, disable |
| Climate | Set temperature, HVAC mode |
| Covers | Open, close, set position (blinds, garage) |
| Locks | Lock, unlock (with safety confirmation) |
| Fans | On/off, speed |
| Media players | Play, pause, volume |
| Vacuum | Start, return to dock |
| Alarm | Arm, disarm (with safety confirmation) |
| Notifications | Send to mobile devices, list targets |
| Person / Presence | Who is home, device locations |
| Weather | Current conditions, daily/hourly forecast |
| Input helpers | Boolean, number, select, text, datetime |
| Calendar | List calendars, upcoming events |
| Text-to-Speech | Speak messages on media players |
| Sensors | Read temperature, humidity, power, etc. |
| Areas & Floors | Discover areas, floors, entities by area |
| History | Entity state history, logbook |
| Templates | Evaluate Jinja2 templates server-side |

## Usage Examples

```bash
# "Turn on the office light at 80%"
curl -s -X POST "$HA_URL/api/services/light/turn_on" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "light.office", "brightness_pct": 80}'

# "What's the temperature?"
curl -s "$HA_URL/api/states" -H "Authorization: Bearer $HA_TOKEN" \
  | jq '.[] | select(.attributes.device_class == "temperature") | {name: .attributes.friendly_name, temp: .state, unit: .attributes.unit_of_measurement}'
```

## License

MIT
