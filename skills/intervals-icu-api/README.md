# Intervals.icu API Skill

A comprehensive Claude Skill for working with the **intervals.icu API**. Provides clear guidance on authenticating, retrieving training activities, managing calendar events, and logging wellness data.

## Overview

This skill enables you to:

- **Get Activities**: Retrieve completed workouts with power, heart rate, and load data
- **Manage Calendar**: Create, update, and delete planned workouts on your training calendar
- **Combine Data**: Use field selectors to pull activities with contextual metrics (fitness, fatigue, zones)
- **Log Wellness**: Track sleep, soreness, resting HR, and recovery metrics
- **Upload Data**: Create manual activities and bulk-import training sessions
- **Export Workouts**: Download planned workouts in device formats (.zwo, .mrc, .erg, .fit)

## Quick Start

### 1. Get Your Credentials

Visit [intervals.icu settings](https://intervals.icu/settings) and find:
- Your **Athlete ID**
- Your **API Key**

### 2. Authenticate

Two authentication methods are supported:

**API Key Method:**
```bash
curl -H "Authorization: ApiKey YOUR_ATHLETE_ID:YOUR_API_KEY" \
  https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID
```

**Bearer Token (OAuth):**
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID
```

### 3. Common Operations

**List activities for a date range:**
```bash
curl -H "Authorization: ApiKey YOUR_ATHLETE_ID:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/activities?oldest=2024-01-01&newest=2024-01-31"
```

**Get planned workouts:**
```bash
curl -H "Authorization: ApiKey YOUR_ATHLETE_ID:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/events?oldest=2024-02-01&newest=2024-02-29&category=WORKOUT"
```

**Create a planned workout:**
```bash
curl -X POST \
  -H "Authorization: ApiKey YOUR_ATHLETE_ID:YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sweet Spot Build",
    "category": "WORKOUT",
    "start_date_local": "2024-02-16T18:00:00",
    "description": "3x 10min at 88-92% FTP"
  }' \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/events?upsertOnUid=true"
```

**Log wellness data:**
```bash
curl -X PUT \
  -H "Authorization: ApiKey YOUR_ATHLETE_ID:YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "2024-01-15",
    "sleep_secs": 28800,
    "resting_hr": 52,
    "fatigue": 3
  }' \
  https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/wellness/2024-01-15
```

## Key Features

### Activities with Combined Data

Pull activities with specific data fields for efficient queries:

```bash
# Power, HR, and training load
curl -H "Authorization: ApiKey YOUR_ATHLETE_ID:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/activities?oldest=2024-01-01&fields=name,icu_weighted_avg_watts,average_heartrate,icu_training_load,icu_atl,icu_ctl"

# Zone times and intensity
curl -H "Authorization: ApiKey YOUR_ATHLETE_ID:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/activities?oldest=2024-01-01&fields=id,name,distance,moving_time,icu_zone_times,icu_weighted_avg_watts"
```

### Calendar Management

Create weekly training plans:
```bash
# Bulk create workouts for the week
curl -X POST \
  -H "Authorization: ApiKey YOUR_ATHLETE_ID:YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '[
    {"name": "Easy Spin", "category": "WORKOUT", "start_date_local": "2024-02-15T18:00:00", "description": "60min at 60-65% FTP"},
    {"name": "VO2Max", "category": "WORKOUT", "start_date_local": "2024-02-20T18:00:00", "description": "6x 4min at 110% FTP"},
    {"name": "Recovery", "category": "WORKOUT", "start_date_local": "2024-02-21T18:00:00", "description": "45min easy"}
  ]' \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/events/bulk?upsertOnUid=true&updatePlanApplied=true"
```

### Structured Workouts

Download planned workouts in device formats:
```bash
# Zwift format
curl -H "Authorization: ApiKey YOUR_ATHLETE_ID:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/events/EVENT_ID/download.zwo" \
  --output workout.zwo

# TrainerRoad format
curl -H "Authorization: ApiKey YOUR_ATHLETE_ID:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/events/EVENT_ID/download.mrc" \
  --output workout.mrc

# Garmin format
curl -H "Authorization: ApiKey YOUR_ATHLETE_ID:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/events/EVENT_ID/download.fit" \
  --output workout.fit
```

### Wellness Tracking

Bulk update recovery metrics:
```bash
curl -X PUT \
  -H "Authorization: ApiKey YOUR_ATHLETE_ID:YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '[
    {"id": "2024-01-15", "sleep_secs": 28800, "resting_hr": 52},
    {"id": "2024-01-16", "sleep_secs": 30600, "resting_hr": 50},
    {"id": "2024-01-17", "sleep_secs": 27000, "resting_hr": 54}
  ]' \
  https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/wellness-bulk
```

## API Endpoints Overview

### Activities
- `GET /athlete/{id}/activities` - List completed workouts
- `POST /athlete/{id}/activities/manual` - Create manual activity
- `PUT /activity/{id}` - Update activity
- `GET /activity/{id}` - Get activity details
- `GET /activity/{id}/streams.csv` - Export activity data

### Calendar Events
- `GET /athlete/{id}/events` - List planned workouts
- `POST /athlete/{id}/events` - Create event
- `PUT /athlete/{id}/events/{eventId}` - Update event
- `DELETE /athlete/{id}/events/{eventId}` - Delete event
- `POST /athlete/{id}/events/bulk` - Bulk create events

### Wellness
- `GET /athlete/{id}/wellness` - Get wellness records
- `PUT /athlete/{id}/wellness/{date}` - Update wellness for date
- `PUT /athlete/{id}/wellness-bulk` - Bulk update wellness

### Sport Settings
- `GET /athlete/{id}/sport-settings` - List sport settings
- `PUT /athlete/{id}/sport-settings/{sport}` - Update zones and FTP

## Date Formats

Always use **ISO-8601** format:
- Date only: `2024-01-15`
- Date and time: `2024-01-15T10:30:00`

## Field Selection

Use the `fields` parameter to request only needed data (improves performance):

```bash
# Request specific fields instead of all
curl -H "Authorization: ApiKey YOUR_ATHLETE_ID:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/activities?oldest=2024-01-01&fields=id,name,type,distance,icu_training_load"
```

## Common Fields

### Activity Fields
- `id` - Activity ID
- `name` - Activity name
- `type` - Activity type (Ride, Run, Swim, etc.)
- `distance` - Distance in meters
- `moving_time` - Moving time in seconds
- `icu_weighted_avg_watts` - Average power (cycling)
- `average_heartrate` - Average heart rate
- `max_heartrate` - Max heart rate
- `icu_training_load` - Training load score
- `icu_atl` - Acute training load
- `icu_ctl` - Chronic training load
- `icu_zone_times` - Time in each power zone
- `icu_hr_zone_times` - Time in each HR zone
- `perceived_exertion` - Perceived exertion (1-10)

### Event Fields
- `id` - Event ID
- `name` - Event name
- `category` - Event category (WORKOUT, NOTE, TARGET, etc.)
- `start_date_local` - Event start time
- `description` - Event description/workout details
- `hide_from_athlete` - Hide from athlete view
- `athlete_cannot_edit` - Lock from athlete edits

### Wellness Fields
- `id` - Date (ISO-8601)
- `sleep_secs` - Sleep duration in seconds
- `resting_hr` - Resting heart rate
- `fatigue` - Fatigue level (1-10)
- `soreness` - Soreness level (1-10)
- `notes` - Daily notes

## Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created successfully |
| 400 | Bad request (invalid parameters) |
| 401 | Unauthorized (invalid API key) |
| 404 | Not found (invalid ID) |
| 429 | Rate limited (slow down) |
| 500 | Server error |

## Use Cases

### Track Weekly Training
Pull activities + wellness data to analyze week:
```bash
# Get activities with load metrics
curl -H "Authorization: ApiKey YOUR_ATHLETE_ID:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/activities?oldest=2024-01-08&newest=2024-01-14&fields=name,type,icu_training_load,average_heartrate"

# Get wellness for the week
curl -H "Authorization: ApiKey YOUR_ATHLETE_ID:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/wellness?oldest=2024-01-08&newest=2024-01-14"
```

### Create Training Plan
Bulk upload week of workouts:
```bash
# See "Calendar Management" section for example
```

### Sync with External System
Export and import training data between tools using external_ids.

### Monitor Fitness
Track Acute/Chronic Training Load (ATL/CTL) over time to monitor fitness and fatigue.

## Documentation

For complete API documentation, see:
- **Official Docs**: [intervals.icu API](https://intervals.icu/api-docs.html)
- **Forum Discussion**: [API Access](https://forum.intervals.icu/t/api-access-to-intervals-icu/609)
- **OpenAPI Spec**: [API Specification](https://intervals.icu/openapi-spec.json)

## Tips

- **Rate Limiting**: Don't hammer the API. Use reasonable delays between requests.
- **Bulk Operations**: Use bulk endpoints (`/bulk`) instead of multiple single requests.
- **Field Selection**: Always specify needed fields with `fields` parameter.
- **Upsert**: Use `upsertOnUid=true` to update instead of duplicate when creating events.
- **External IDs**: Use `external_id` for syncing across systems.

## License

This skill is provided as-is for use with Intervals.icu API.

## Resources

- [Intervals.icu Website](https://intervals.icu)
- [API Documentation](https://intervals.icu/api-docs.html)
- [Community Forum](https://forum.intervals.icu)