---
name: homeassistant-skill
description: >
  Control Home Assistant devices and automations via REST API. 25 entity domains
  including lights, climate, locks, presence, weather, calendars, notifications,
  scripts, and more. Use when the user asks about their smart home, devices, or automations.
license: MIT
homepage: https://github.com/anotb/homeassistant-skill
compatibility: Requires curl and jq. Network access to Home Assistant instance.
metadata: {"author": "anotb", "version": "2.1.0", "openclaw": {"requires": {"env": ["HA_URL", "HA_TOKEN"], "bins": ["curl", "jq"]}, "primaryEnv": "HA_TOKEN"}}
---

# Home Assistant Skill

Control smart home devices via the Home Assistant REST API.

## Setup

Set environment variables:
- `HA_URL` — Your Home Assistant URL (e.g., `http://10.0.0.10:8123`)
- `HA_TOKEN` — Long-lived access token (create in HA → Profile → Long-Lived Access Tokens)

## Safety Rules

**Always confirm with the user before performing these actions:**
- **Locks** — locking or unlocking any lock
- **Alarm panels** — arming or disarming
- **Garage doors** — opening or closing (`cover.*` with `device_class: garage`)
- **Security automations** — disabling automations related to security or safety
- **Covers** — opening or closing covers that control physical access (gates, barriers)

Never act on security-sensitive devices without explicit user confirmation.

## Entity Discovery

### List all entities

```bash
curl -s "$HA_URL/api/states" -H "Authorization: Bearer $HA_TOKEN" \
  | jq -r '.[].entity_id' | sort
```

### List entities by domain

```bash
# Switches
curl -s "$HA_URL/api/states" -H "Authorization: Bearer $HA_TOKEN" \
  | jq -r '.[] | select(.entity_id | startswith("switch.")) | "\(.entity_id): \(.state)"'

# Lights
curl -s "$HA_URL/api/states" -H "Authorization: Bearer $HA_TOKEN" \
  | jq -r '.[] | select(.entity_id | startswith("light.")) | "\(.entity_id): \(.state)"'

# Sensors
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

# Only lights in an area
curl -s -X POST "$HA_URL/api/template" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template": "{{ area_entities(\"kitchen\") | select(\"match\", \"light.\") | list }}"}'

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
# Turn on with brightness
curl -s -X POST "$HA_URL/api/services/light/turn_on" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "light.living_room", "brightness_pct": 80}'

# Turn on with color (RGB)
curl -s -X POST "$HA_URL/api/services/light/turn_on" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "light.living_room", "rgb_color": [255, 150, 50]}'

# Turn on with color temperature (mireds)
curl -s -X POST "$HA_URL/api/services/light/turn_on" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "light.living_room", "color_temp": 300}'

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

# Enable automation
curl -s -X POST "$HA_URL/api/services/automation/turn_on" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "automation.morning_routine"}'

# Disable automation
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
  -d '{"entity_id": "climate.thermostat", "temperature": 72}'

# Set HVAC mode (heat, cool, auto, off)
curl -s -X POST "$HA_URL/api/services/climate/set_hvac_mode" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "climate.thermostat", "hvac_mode": "auto"}'
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
# Turn on
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
curl -s "$HA_URL/api/calendars/calendar.personal?start=$(date -u +%Y-%m-%dT%H:%M:%S.000Z)&end=$(date -u -v+7d +%Y-%m-%dT%H:%M:%S.000Z)" \
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

Replace `tts.google_en` with your TTS entity and `media_player.living_room_speaker` with the target speaker.

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
# Turn off all living room lights at once
curl -s -X POST "$HA_URL/api/services/light/turn_off" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": ["light.living_room", "light.living_room_lamp", "light.living_room_ceiling"]}'
```

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

## Response Format

Service calls return an array of state objects for affected entities:

```json
[{"entity_id": "light.living_room", "state": "on", "attributes": {...}, "last_changed": "..."}]
```

- Successful call with no state change: returns `[]` (empty array)
- State read (`/api/states/...`): returns a single state object
- Errors: returns `{"message": "..."}` with an HTTP error code

## Template Evaluation

The `/api/template` endpoint evaluates Jinja2 templates server-side. Useful for computed queries.

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

# Get entity state in a template
curl -s -X POST "$HA_URL/api/template" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template": "{{ states(\"light.living_room\") }}"}'

# List all entities that are "on"
curl -s -X POST "$HA_URL/api/template" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template": "{{ states | selectattr(\"state\", \"eq\", \"on\") | map(attribute=\"entity_id\") | list }}"}'
```

Available template functions: `states()`, `is_state()`, `state_attr()`, `areas()`, `area_entities()`, `area_name()`, `floors()`, `floor_areas()`, `labels()`, `label_entities()`, `devices()`, `device_entities()`, `now()`, `relative_time()`.

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

# Climate summary (all thermostats)
curl -s "$HA_URL/api/states" -H "Authorization: Bearer $HA_TOKEN" \
  | jq -r '.[] | select(.entity_id | startswith("climate.")) | "\(.attributes.friendly_name // .entity_id): \(.state), current: \(.attributes.current_temperature)°, target: \(.attributes.temperature)°"'

# Lock status
curl -s "$HA_URL/api/states" -H "Authorization: Bearer $HA_TOKEN" \
  | jq -r '.[] | select(.entity_id | startswith("lock.")) | "\(.attributes.friendly_name // .entity_id): \(.state)"'

# Who is home
curl -s "$HA_URL/api/states" -H "Authorization: Bearer $HA_TOKEN" \
  | jq -r '.[] | select(.entity_id | startswith("person.")) | "\(.attributes.friendly_name // .entity_id): \(.state)"'
```

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

## Notes

- API returns JSON by default
- Long-lived tokens don't expire — store securely
- Test entity IDs with the list command first
- For locks, alarms, and garage doors — always confirm actions with the user
