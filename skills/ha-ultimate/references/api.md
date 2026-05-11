# Home Assistant REST API Reference

## Authentication

All requests require the `Authorization` header:

```
Authorization: Bearer <long-lived-access-token>
```

## Base Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/` | GET | API status and HA version |
| `/api/config` | GET | Current configuration |
| `/api/states` | GET | All entity states |
| `/api/states/<entity_id>` | GET | Single entity state |
| `/api/states/<entity_id>` | POST | Set entity state |
| `/api/services` | GET | Available services |
| `/api/services/<domain>/<service>` | POST | Call a service |
| `/api/events` | GET | Available events |
| `/api/events/<event_type>` | POST | Fire an event |
| `/api/history/period/<timestamp>` | GET | State history |
| `/api/logbook/<timestamp>` | GET | Logbook entries |
| `/api/template` | POST | Evaluate Jinja2 template |
| `/api/calendars` | GET | List calendars |
| `/api/calendars/<entity_id>` | GET | Calendar events (with start/end params) |

## Service Call Pattern

```bash
curl -s -X POST "$HA_URL/api/services/{domain}/{service}" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "domain.entity_name", ...additional_params}'
```

## Common Services

### Lights

```bash
# Turn on with all options
POST /api/services/light/turn_on
{
  "entity_id": "light.living_room",
  "brightness": 255,           # 0-255 (absolute)
  "brightness_pct": 100,       # 0-100 (percentage)
  "color_temp": 370,           # Mireds (153=cold, 500=warm)
  "rgb_color": [255, 0, 0],   # RGB array
  "transition": 2              # Seconds for gradual change
}
```

### Climate

```bash
POST /api/services/climate/set_temperature
{
  "entity_id": "climate.thermostat",
  "temperature": 22,
  "hvac_mode": "heat"  # heat, cool, auto, off
}

POST /api/services/climate/set_preset_mode
{
  "entity_id": "climate.thermostat",
  "preset_mode": "away"  # away, home, sleep
}
```

### Media Player

```bash
POST /api/services/media_player/volume_set
{"entity_id": "media_player.tv", "volume_level": 0.5}

POST /api/services/media_player/play_media
{
  "entity_id": "media_player.tv",
  "media_content_id": "https://example.com/stream",
  "media_content_type": "music"
}
```

### Covers

```bash
POST /api/services/cover/set_cover_position
{"entity_id": "cover.blinds", "position": 50}  # 0=closed, 100=open
```

## Template API

The template endpoint evaluates Jinja2 templates server-side:

```bash
POST /api/template
{"template": "{{ states('light.living_room') }}"}
```

### Available Template Functions

| Function | Description |
|----------|-------------|
| `states()` | Get entity state |
| `is_state(entity, value)` | Check if entity is in state |
| `state_attr(entity, attr)` | Get entity attribute |
| `areas()` | List all area IDs |
| `area_entities(area)` | Entities in an area |
| `area_name(entity)` | Area name for an entity |
| `floors()` | List all floor IDs |
| `floor_areas(floor)` | Areas on a floor |
| `labels()` | List all labels |
| `label_entities(label)` | Entities with a label |
| `devices()` | List all device IDs |
| `device_entities(device)` | Entities for a device |
| `now()` | Current datetime |
| `relative_time(timestamp)` | Human-readable relative time |

## Batch Operations

Control multiple entities in one call:

```json
{"entity_id": ["light.room1", "light.room2", "light.room3"]}
```

## State Object Structure

```json
{
  "entity_id": "light.living_room",
  "state": "on",
  "attributes": {
    "friendly_name": "Living Room Light",
    "brightness": 254,
    "color_temp": 370,
    "supported_features": 44
  },
  "last_changed": "2025-01-15T10:30:00.000Z",
  "last_updated": "2025-01-15T10:30:00.000Z"
}
```
