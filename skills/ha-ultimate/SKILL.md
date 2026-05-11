---
name: ha-ultimate
description: >
  Definitive Home Assistant skill for AI agents. Control 25+ entity domains via REST API
  with safety enforcement, webhooks, inventory generation, and a full CLI wrapper.
  Lights, climate, locks, presence, weather, calendars, notifications, TTS, scripts,
  automations, and more.
metadata: {"openclaw":{"emoji":"🏠","requires":{"env":["HA_URL","HA_TOKEN"],"bins":["curl","jq"]},"optionalBins":["node"],"primaryEnv":"HA_TOKEN","configPaths":["$HOME/.config/homeassistant/config.json",".env"]}}
---

# ha-ultimate — Definitive Home Assistant Skill

Control your smart home via the Home Assistant REST API with safety enforcement, inventory
awareness, and full domain coverage.

## Setup

### 1. Environment Variables

```bash
export HA_URL="http://your-ha-instance:8123"
export HA_TOKEN="your-long-lived-access-token"
```

Or create a `.env` file in the skill directory (auto-loaded by ha.sh):

```env
HA_URL=http://192.168.1.100:8123
HA_TOKEN=eyJ...your-token...
```

The CLI wrapper also checks `$HOME/.config/homeassistant/config.json` as a fallback
(JSON with `url` and `token` keys). Protect this file with restrictive permissions
(`chmod 600`) since it may contain your token.

### 2. Getting a Long-Lived Access Token

1. Open Home Assistant → Profile (bottom left)
2. Scroll to "Long-Lived Access Tokens"
3. Click "Create Token", name it (e.g., "OpenClaw")
4. Copy the token immediately (shown only once)

### 3. Test Connection

```bash
curl -s -H "Authorization: Bearer $HA_TOKEN" "$HA_URL/api/" | jq
```

Or with the CLI wrapper:

```bash
scripts/ha.sh info
```

### 4. Generate Entity Inventory (Recommended, requires Node.js)

**Note:** Node.js is an **optional** dependency, only needed for `inventory.js`.
If Node.js is not available, `ha.sh inventory` falls back to a curl+jq listing.

```bash
node scripts/inventory.js
```

This generates `ENTITIES.md` with all entities organized by domain, including name, area,
and current state. **Read ENTITIES.md before acting on devices** to know what is available.

### 5. Docker / Container Networking

If running inside Docker:
- **Use IP address** (recommended): `http://192.168.1.100:8123`
- **Tailscale**: `http://homeassistant.ts.net:8123`
- **Avoid mDNS** in Docker: `homeassistant.local` often doesn't resolve
- **Nabu Casa**: `https://xxxxx.ui.nabu.casa` (requires subscription)

---

## Safety Rules

This skill implements a **layered safety system** to prevent accidental actions on
security-critical devices.

### Layer 1: Mandatory Confirmation (Agent Behavior)

**Always confirm with the user before performing these actions:**
- **Locks** — locking or unlocking any lock
- **Alarm panels** — arming or disarming
- **Garage doors** — opening or closing (`cover.*` with `device_class: garage`)
- **Security automations** — disabling automations related to security or safety
- **Covers** — opening or closing covers that control physical access (gates, barriers)

Never act on security-sensitive devices without explicit user confirmation.

### Layer 2: Critical Action Workflow

For critical domains (locks, alarm panels, garage doors, covers controlling physical
access), follow this workflow **before executing any command**:

1. **Identify the action as critical** — check if the entity domain is lock, alarm_control_panel, or cover with device_class garage/gate
2. **Inform the user and ask for confirmation** — "⚠️ Opening the garage door is a critical action. Do you want to proceed?"
3. **Wait for explicit confirmation** — "Yes", "OK", "Sure", "Do it", or any affirmative response
4. **Only then execute the command** — never execute first

**Important:** The agent (not the script) is responsible for enforcing this confirmation
flow. The CLI wrapper (`scripts/ha.sh`) checks `blocked_entities.json` as a hard block,
but interactive confirmation must be handled at the agent conversation level before
invoking any command on critical domains.

### Layer 3: Blocked Entities (Optional Configuration)

Users can permanently block entities by listing them in a `blocked_entities.json` file:

```json
{
  "blocked": ["switch.main_breaker", "lock.front_door"],
  "notes": "Main breaker should never be automated. Front door is manual-only."
}
```

**Blocked entities cannot be controlled under any circumstance**, even with user confirmation.
Check this file before executing any action if it exists.

---

## CLI Wrapper

The `scripts/ha.sh` CLI provides easy access to all HA functions:

```bash
# Test connection
scripts/ha.sh info

# List entities
scripts/ha.sh list all          # all entities
scripts/ha.sh list light        # just lights
scripts/ha.sh list switch       # just switches

# Search entities
scripts/ha.sh search kitchen    # find entities by name

# Get/set state
scripts/ha.sh state light.living_room
scripts/ha.sh full light.living_room    # full details with attributes
scripts/ha.sh on light.living_room
scripts/ha.sh on light.living_room 200  # with brightness (0-255)
scripts/ha.sh off light.living_room
scripts/ha.sh toggle switch.fan

# Scenes & scripts
scripts/ha.sh scene movie_night
scripts/ha.sh script goodnight

# Climate
scripts/ha.sh climate climate.thermostat 22

# Dashboard (quick status of everything)
scripts/ha.sh dashboard

# Call any service
scripts/ha.sh call light turn_on '{"entity_id":"light.room","brightness":200}'

# Areas
scripts/ha.sh areas
```

---

## Entity Discovery

### List all entities

```bash
curl -s "$HA_URL/api/states" -H "Authorization: Bearer $HA_TOKEN" \
  | jq -r '.[].entity_id' | sort
```

### List entities by domain

```bash
# Lights
curl -s "$HA_URL/api/states" -H "Authorization: Bearer $HA_TOKEN" \
  | jq -r '.[] | select(.entity_id | startswith("light.")) | "\(.entity_id): \(.state)"'

# Sensors (with units)
curl -s "$HA_URL/api/states" -H "Authorization: Bearer $HA_TOKEN" \
  | jq -r '.[] | select(.entity_id | startswith("sensor.")) | "\(.entity_id): \(.state) \(.attributes.unit_of_measurement // "")"'
```

Replace the domain prefix (`switch.`, `light.`, `sensor.`, etc.) to discover entities
in any domain.

### Get single entity state

```bash
curl -s "$HA_URL/api/states/ENTITY_ID" -H "Authorization: Bearer $HA_TOKEN"
```

### Area & Floor Discovery

Use the template API to query areas, floors, and labels.

```bash
# List all areas
curl -s -X POST "$HA_URL/api/template" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template": "{{ areas() }}"}'

# Entities in a specific area
curl -s -X POST "$HA_URL/api/template" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template": "{{ area_entities(\"kitchen\") }}"}'

# Find which area an entity belongs to
curl -s -X POST "$HA_URL/api/template" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template": "{{ area_name(\"light.kitchen\") }}"}'

# List all floors and their areas
curl -s -X POST "$HA_URL/api/template" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template": "{% for floor in floors() %}{{ floor }}: {{ floor_areas(floor) }}\n{% endfor %}"}'
```

---

## Switches

```bash
# Turn on
curl -s -X POST "$HA_URL/api/services/switch/turn_on" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "switch.office_lamp"}'

# Turn off
curl -s -X POST "$HA_URL/api/services/switch/turn_off" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "switch.office_lamp"}'

# Toggle
curl -s -X POST "$HA_URL/api/services/switch/toggle" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "switch.office_lamp"}'
```

## Lights

```bash
# Turn on with brightness (percentage)
curl -s -X POST "$HA_URL/api/services/light/turn_on" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "light.living_room", "brightness_pct": 80}'

# Turn on with color (RGB)
curl -s -X POST "$HA_URL/api/services/light/turn_on" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "light.living_room", "rgb_color": [255, 150, 50]}'

# Turn on with color temperature (mireds, 153-500)
curl -s -X POST "$HA_URL/api/services/light/turn_on" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "light.living_room", "color_temp": 300}'

# Turn on with transition (seconds)
curl -s -X POST "$HA_URL/api/services/light/turn_on" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "light.living_room", "brightness_pct": 100, "transition": 3}'

# Turn off
curl -s -X POST "$HA_URL/api/services/light/turn_off" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "light.living_room"}'
```

## Scenes

```bash
curl -s -X POST "$HA_URL/api/services/scene/turn_on" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "scene.movie_time"}'
```

## Scripts

```bash
# List all scripts
curl -s "$HA_URL/api/states" -H "Authorization: Bearer $HA_TOKEN" \
  | jq -r '.[] | select(.entity_id | startswith("script.")) | "\(.entity_id): \(.state)"'

# Run a script
curl -s -X POST "$HA_URL/api/services/script/turn_on" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "script.bedtime_routine"}'

# Run a script with variables
curl -s -X POST "$HA_URL/api/services/script/bedtime_routine" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"variables": {"brightness": 20, "delay_minutes": 5}}'
```

## Automations

```bash
# List all automations
curl -s "$HA_URL/api/states" -H "Authorization: Bearer $HA_TOKEN" \
  | jq -r '.[] | select(.entity_id | startswith("automation.")) | "\(.entity_id): \(.state)"'

# Trigger an automation
curl -s -X POST "$HA_URL/api/services/automation/trigger" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "automation.morning_routine"}'

# Enable / Disable automation
curl -s -X POST "$HA_URL/api/services/automation/turn_on" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "automation.morning_routine"}'

curl -s -X POST "$HA_URL/api/services/automation/turn_off" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "automation.morning_routine"}'
```

## Climate Control

```bash
# Get thermostat state
curl -s "$HA_URL/api/states/climate.thermostat" -H "Authorization: Bearer $HA_TOKEN" \
  | jq '{state: .state, current_temp: .attributes.current_temperature, target_temp: .attributes.temperature}'

# Set temperature
curl -s -X POST "$HA_URL/api/services/climate/set_temperature" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "climate.thermostat", "temperature": 22}'

# Set HVAC mode (heat, cool, auto, off)
curl -s -X POST "$HA_URL/api/services/climate/set_hvac_mode" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "climate.thermostat", "hvac_mode": "auto"}'

# Set preset mode (away, home, sleep, etc.)
curl -s -X POST "$HA_URL/api/services/climate/set_preset_mode" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "climate.thermostat", "preset_mode": "away"}'
```

## Covers (Blinds, Garage Doors)

**Safety:** Confirm with the user before opening/closing garage doors or gates.

```bash
# Open
curl -s -X POST "$HA_URL/api/services/cover/open_cover" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "cover.garage_door"}'

# Close
curl -s -X POST "$HA_URL/api/services/cover/close_cover" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "cover.garage_door"}'

# Set position (0 = closed, 100 = open)
curl -s -X POST "$HA_URL/api/services/cover/set_cover_position" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "cover.blinds", "position": 50}'

# Stop
curl -s -X POST "$HA_URL/api/services/cover/stop_cover" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "cover.blinds"}'
```

## Locks

**Safety:** Always confirm with the user before locking/unlocking.

```bash
# Lock
curl -s -X POST "$HA_URL/api/services/lock/lock" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "lock.front_door"}'

# Unlock
curl -s -X POST "$HA_URL/api/services/lock/unlock" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "lock.front_door"}'
```

## Fans

```bash
# Turn on with speed percentage
curl -s -X POST "$HA_URL/api/services/fan/turn_on" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "fan.bedroom", "percentage": 50}'

# Turn off
curl -s -X POST "$HA_URL/api/services/fan/turn_off" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "fan.bedroom"}'
```

## Media Players

```bash
# Play/pause
curl -s -X POST "$HA_URL/api/services/media_player/media_play_pause" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "media_player.living_room_tv"}'

# Set volume (0.0 to 1.0)
curl -s -X POST "$HA_URL/api/services/media_player/volume_set" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "media_player.living_room_tv", "volume_level": 0.5}'

# Play media
curl -s -X POST "$HA_URL/api/services/media_player/play_media" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "media_player.tv", "media_content_id": "https://example.com/stream", "media_content_type": "music"}'
```

## Vacuum

```bash
# Start cleaning
curl -s -X POST "$HA_URL/api/services/vacuum/start" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "vacuum.robot"}'

# Return to dock
curl -s -X POST "$HA_URL/api/services/vacuum/return_to_base" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "vacuum.robot"}'
```

## Alarm Control Panel

**Safety:** Always confirm with the user before arming/disarming.

```bash
# Arm (home mode)
curl -s -X POST "$HA_URL/api/services/alarm_control_panel/alarm_arm_home" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "alarm_control_panel.home"}'

# Arm (away mode)
curl -s -X POST "$HA_URL/api/services/alarm_control_panel/alarm_arm_away" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "alarm_control_panel.home"}'

# Disarm (requires code if configured)
curl -s -X POST "$HA_URL/api/services/alarm_control_panel/alarm_disarm" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "alarm_control_panel.home", "code": "1234"}'
```

## Notifications

```bash
# List available notification targets
curl -s "$HA_URL/api/services" -H "Authorization: Bearer $HA_TOKEN" \
  | jq -r '.[] | select(.domain == "notify") | .services | keys[]' | sort

# Send a notification to a mobile device
curl -s -X POST "$HA_URL/api/services/notify/mobile_app_phone" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Front door opened", "title": "Home Alert"}'

# Send to all devices (default notify service)
curl -s -X POST "$HA_URL/api/services/notify/notify" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "System alert", "title": "Home Assistant"}'
```

Replace `mobile_app_phone` with the actual service name from the list command.

## Person & Presence

```bash
# Who is home?
curl -s "$HA_URL/api/states" -H "Authorization: Bearer $HA_TOKEN" \
  | jq -r '.[] | select(.entity_id | startswith("person.")) | "\(.attributes.friendly_name // .entity_id): \(.state)"'

# Device tracker locations
curl -s "$HA_URL/api/states" -H "Authorization: Bearer $HA_TOKEN" \
  | jq -r '.[] | select(.entity_id | startswith("device_tracker.")) | "\(.entity_id): \(.state)"'
```

States: `home`, `not_home`, or a zone name.

## Weather

```bash
# Current weather
curl -s "$HA_URL/api/states/weather.home" -H "Authorization: Bearer $HA_TOKEN" \
  | jq '{state: .state, temperature: .attributes.temperature, humidity: .attributes.humidity, wind_speed: .attributes.wind_speed}'

# Get forecast (daily)
curl -s -X POST "$HA_URL/api/services/weather/get_forecasts" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "weather.home", "type": "daily"}'

# Get forecast (hourly)
curl -s -X POST "$HA_URL/api/services/weather/get_forecasts" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "weather.home", "type": "hourly"}'
```

## Input Helpers

```bash
# Toggle an input boolean
curl -s -X POST "$HA_URL/api/services/input_boolean/toggle" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "input_boolean.guest_mode"}'

# Set input number
curl -s -X POST "$HA_URL/api/services/input_number/set_value" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "input_number.target_temperature", "value": 72}'

# Set input select
curl -s -X POST "$HA_URL/api/services/input_select/select_option" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "input_select.house_mode", "option": "Away"}'

# Set input text
curl -s -X POST "$HA_URL/api/services/input_text/set_value" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "input_text.welcome_message", "value": "Welcome home!"}'

# Set input datetime
curl -s -X POST "$HA_URL/api/services/input_datetime/set_datetime" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "input_datetime.alarm_time", "time": "07:30:00"}'
```

## Calendar

```bash
# List all calendars
curl -s "$HA_URL/api/calendars" -H "Authorization: Bearer $HA_TOKEN" \
  | jq -r '.[].entity_id'

# Get upcoming events (next 7 days)
START=$(date -u +%Y-%m-%dT%H:%M:%S.000Z)
END=$(date -u -d "+7 days" +%Y-%m-%dT%H:%M:%S.000Z 2>/dev/null || date -u -v+7d +%Y-%m-%dT%H:%M:%S.000Z)
curl -s "$HA_URL/api/calendars/calendar.personal?start=$START&end=$END" \
  -H "Authorization: Bearer $HA_TOKEN" \
  | jq '[.[] | {summary: .summary, start: .start.dateTime, end: .end.dateTime}]'
```

## Text-to-Speech

```bash
curl -s -X POST "$HA_URL/api/services/tts/speak" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "tts.google_en", "media_player_entity_id": "media_player.living_room_speaker", "message": "Dinner is ready"}'
```

Replace `tts.google_en` with your TTS entity and the media player with the target speaker.

---

## Call Any Service

The general pattern for any HA service:

```bash
curl -s -X POST "$HA_URL/api/services/{domain}/{service}" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "domain.entity_name", ...}'
```

### Batch operations

Control multiple entities in one call by passing an array of entity IDs:

```bash
curl -s -X POST "$HA_URL/api/services/light/turn_off" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": ["light.living_room", "light.kitchen", "light.bedroom"]}'
```

---

## Template Evaluation

The `/api/template` endpoint evaluates Jinja2 templates server-side. Useful for computed
queries that go beyond simple state reads.

```bash
curl -s -X POST "$HA_URL/api/template" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template": "TEMPLATE_STRING"}'
```

### Examples

```bash
# Count entities by domain
curl -s -X POST "$HA_URL/api/template" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template": "{{ states.light | list | count }} lights"}'

# List all entities that are "on"
curl -s -X POST "$HA_URL/api/template" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template": "{{ states | selectattr(\"state\", \"eq\", \"on\") | map(attribute=\"entity_id\") | list }}"}'

# Entities in an area filtered by domain
curl -s -X POST "$HA_URL/api/template" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template": "{{ area_entities(\"kitchen\") | select(\"match\", \"light.\") | list }}"}'
```

Available template functions: `states()`, `is_state()`, `state_attr()`, `areas()`,
`area_entities()`, `area_name()`, `floors()`, `floor_areas()`, `labels()`,
`label_entities()`, `devices()`, `device_entities()`, `now()`, `relative_time()`.

---

## History & Logbook

### Entity state history

```bash
# Last 24 hours for a specific entity
curl -s "$HA_URL/api/history/period?filter_entity_id=sensor.temperature" \
  -H "Authorization: Bearer $HA_TOKEN" \
  | jq '.[0] | [.[] | {state: .state, last_changed: .last_changed}]'

# Specific time range (ISO 8601)
curl -s "$HA_URL/api/history/period/2025-01-15T00:00:00Z?end_time=2025-01-15T23:59:59Z&filter_entity_id=sensor.temperature" \
  -H "Authorization: Bearer $HA_TOKEN" \
  | jq '.[0]'
```

### Logbook

```bash
# Recent logbook entries
curl -s "$HA_URL/api/logbook" -H "Authorization: Bearer $HA_TOKEN" \
  | jq '.[:10]'

# Logbook for a specific entity
curl -s "$HA_URL/api/logbook?entity=light.living_room" \
  -H "Authorization: Bearer $HA_TOKEN" \
  | jq '.[:10] | [.[] | {name: .name, message: .message, when: .when}]'
```

---

## Dashboard Overview

Quick status of all active devices:

```bash
# All lights that are on
curl -s "$HA_URL/api/states" -H "Authorization: Bearer $HA_TOKEN" \
  | jq -r '.[] | select(.entity_id | startswith("light.")) | select(.state == "on") | .entity_id'

# All open doors/windows (binary sensors)
curl -s "$HA_URL/api/states" -H "Authorization: Bearer $HA_TOKEN" \
  | jq -r '.[] | select(.entity_id | startswith("binary_sensor.")) | select(.state == "on") | select(.attributes.device_class == "door" or .attributes.device_class == "window") | .entity_id'

# Temperature sensors
curl -s "$HA_URL/api/states" -H "Authorization: Bearer $HA_TOKEN" \
  | jq -r '.[] | select(.entity_id | startswith("sensor.")) | select(.attributes.device_class == "temperature") | "\(.attributes.friendly_name // .entity_id): \(.state)\(.attributes.unit_of_measurement // "")"'

# Climate summary
curl -s "$HA_URL/api/states" -H "Authorization: Bearer $HA_TOKEN" \
  | jq -r '.[] | select(.entity_id | startswith("climate.")) | "\(.attributes.friendly_name // .entity_id): \(.state), current: \(.attributes.current_temperature)°, target: \(.attributes.temperature)°"'

# Lock status
curl -s "$HA_URL/api/states" -H "Authorization: Bearer $HA_TOKEN" \
  | jq -r '.[] | select(.entity_id | startswith("lock.")) | "\(.attributes.friendly_name // .entity_id): \(.state)"'

# Who is home
curl -s "$HA_URL/api/states" -H "Authorization: Bearer $HA_TOKEN" \
  | jq -r '.[] | select(.entity_id | startswith("person.")) | "\(.attributes.friendly_name // .entity_id): \(.state)"'
```

---

## Inbound Webhooks (HA → Agent)

To receive events from Home Assistant automations:

### 1. Define REST Command in HA

```yaml
# configuration.yaml
rest_command:
  notify_agent:
    url: "https://your-agent-url/webhook/home-assistant"
    method: POST
    headers:
      Authorization: "Bearer {{ webhook_secret }}"
      Content-Type: "application/json"
    payload: '{"event": "{{ event }}", "area": "{{ area }}", "entity": "{{ entity }}"}'
```

### 2. Create HA Automation with Webhook Action

```yaml
# automations.yaml
- alias: "Notify agent on motion"
  trigger:
    - platform: state
      entity_id: binary_sensor.motion_hallway
      to: "on"
  action:
    - service: rest_command.notify_agent
      data:
        event: motion_detected
        area: hallway
        entity: binary_sensor.motion_hallway
```

### 3. Handle in Agent

The agent receives the webhook POST and can notify the user or take action based on
the event type and data.

For complete webhook setup, see [references/webhooks.md](references/webhooks.md).

---

## Error Handling

### Check API connectivity

```bash
curl -s -o /dev/null -w "%{http_code}" "$HA_URL/api/" \
  -H "Authorization: Bearer $HA_TOKEN"
# Expect: 200
```

### Verify entity exists before acting

```bash
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  "$HA_URL/api/states/light.nonexistent" \
  -H "Authorization: Bearer $HA_TOKEN")
# 200 = exists, 404 = not found
```

### HTTP status codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (malformed JSON or invalid service data) |
| 401 | Unauthorized (bad or missing token) |
| 404 | Entity or endpoint not found |
| 405 | Method not allowed (wrong HTTP method) |
| 503 | Home Assistant is starting up or unavailable |

### Response Format

Service calls return an array of state objects for affected entities:

```json
[{"entity_id": "light.living_room", "state": "on", "attributes": {...}, "last_changed": "..."}]
```

- Successful call with no state change: returns `[]` (empty array)
- State read (`/api/states/...`): returns a single state object
- Errors: returns `{"message": "..."}` with an HTTP error code

For more troubleshooting, see [references/troubleshooting.md](references/troubleshooting.md).

---

## Entity Domains

| Domain | Examples |
|--------|----------|
| `switch.*` | Smart plugs, generic switches |
| `light.*` | Lights (Hue, LIFX, etc.) |
| `scene.*` | Pre-configured scenes |
| `script.*` | Reusable action sequences |
| `automation.*` | Automations |
| `climate.*` | Thermostats, AC units |
| `cover.*` | Blinds, garage doors, gates |
| `lock.*` | Smart locks |
| `fan.*` | Fans, ventilation |
| `media_player.*` | TVs, speakers, streaming devices |
| `vacuum.*` | Robot vacuums |
| `alarm_control_panel.*` | Security systems |
| `notify.*` | Notification targets |
| `person.*` | People / presence tracking |
| `device_tracker.*` | Device locations |
| `weather.*` | Weather conditions and forecasts |
| `calendar.*` | Calendar events |
| `tts.*` | Text-to-speech engines |
| `sensor.*` | Temperature, humidity, power, etc. |
| `binary_sensor.*` | Motion, door/window, presence |
| `input_boolean.*` | Virtual toggles |
| `input_number.*` | Numeric sliders |
| `input_select.*` | Dropdown selectors |
| `input_text.*` | Text inputs |
| `input_datetime.*` | Date/time inputs |

---

## Notes

- API returns JSON by default
- Long-lived tokens don't expire — store securely
- Test entity IDs with the list command first
- For locks, alarms, and garage doors — always confirm actions with the user
- Use `scripts/inventory.js` to generate a full entity map before first use
- Check `blocked_entities.json` if it exists before acting on any entity
- For complete API reference, see [references/api.md](references/api.md)
