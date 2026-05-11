---
name: intervals-icu-api
description: Complete guide for accessing and managing training data with the intervals.icu API. Use when working with Intervals.icu athlete profiles, activities, workouts, events, wellness data, and training plans. Covers authentication, retrieving activities with combined data fields, managing calendar events with planned workouts, and creating/updating training data. Includes curl examples for all major operations.
---

# Intervals.icu API Skill

Comprehensive guide for interacting with the intervals.icu API to manage athlete training data, activities, workouts, and calendar events.

## Authentication

### API Key Method

Get your Athlete ID and API Key from [intervals.icu settings page](https://intervals.icu/settings).

```bash
# Using API Key header
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID
```

### Bearer Token Method (OAuth)

```bash
# Using Bearer token
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID
```

**Base URL:** `https://intervals.icu/api/v1`

**Date Format:** ISO-8601 (e.g., `2024-01-15` or `2024-01-15T10:30:00`)

---

## Core Concepts

### Athlete ID

Your unique identifier in Intervals.icu. Used in all API endpoints as `{id}` path parameter.

### Activities vs Events

- **Activities**: Completed workouts with actual data (GPS, power, HR). Retrieved from `/athlete/{id}/activities`
- **Events**: Planned workouts on your calendar. Retrieved from `/athlete/{id}/events`

### Data Fields

Activities and events can return different fields. Use the `fields` query parameter to include/exclude specific data points for more efficient queries.

---

## Getting Activities (Completed Workouts)

### List Activities for Date Range

Retrieve all activities between two dates, sorted newest to oldest.

```bash
# Basic activity list
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/activities?oldest=2024-01-01&newest=2024-01-31"

# With limit
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/activities?oldest=2024-01-01&limit=10"

# Specific fields only (more efficient)
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/activities?oldest=2024-01-01&fields=id,name,start_date_local,type,distance,moving_time,icu_training_load"

# For specific activity type (Ride, Run, Swim, etc.)
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/activities?oldest=2024-01-01&newest=2024-01-31" | jq '.[] | select(.type == "Ride")'
```

### Combine Activities with External Data

Use `fields` parameter to combine activity data with contextual information:

```bash
# Power, HR, and load data
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/activities?oldest=2024-01-01&fields=name,icu_weighted_avg_watts,average_heartrate,icu_training_load,icu_atl,icu_ctl"

# Include fatigue and fitness metrics
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/activities?oldest=2024-01-01&fields=id,name,type,icu_training_load,icu_atl,icu_ctl,perceived_exertion"

# Combine power zones and zone times
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/activities?oldest=2024-01-01&fields=id,name,distance,moving_time,icu_zone_times,icu_weighted_avg_watts"

# HR zones + intensity data
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/activities?oldest=2024-01-01&fields=id,name,type,average_heartrate,max_heartrate,icu_hr_zone_times,trimp"
```

### Get Single Activity with Full Details

```bash
# Get activity by ID with all data
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/activity/ACTIVITY_ID"

# Get activity with intervals
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/activity/ACTIVITY_ID?intervals=true"
```

### Export Activity Streams (CSV or JSON)

```bash
# Get activity streams as JSON
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/activity/ACTIVITY_ID/streams.json"

# Get activity streams as CSV (includes time, power, heart_rate, cadence, etc.)
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/activity/ACTIVITY_ID/streams.csv" \
  --output activity_streams.csv

# Get specific stream types
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/activity/ACTIVITY_ID/streams.json?types=watts,heart_rate,cadence"
```

---

## Calendar & Planned Workouts

### List Calendar Events (Planned Workouts)

Retrieve planned workouts, notes, and training targets from your calendar.

```bash
# Get all events in date range
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/events?oldest=2024-02-01&newest=2024-02-29"

# Get with specific fields
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/events?oldest=2024-02-01&newest=2024-02-29&fields=id,name,category,start_date_local,description"

# Filter by category (WORKOUT, NOTE, TARGET, FITNESS_DAYS, etc.)
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/events?oldest=2024-02-01&category=WORKOUT"

# Get workout targets for date range
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/events?oldest=2024-02-01&category=TARGET"
```

### Get Single Event Details

```bash
# Get specific planned workout
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/events/EVENT_ID"
```

### Download Planned Workout File

Export planned workouts in various formats for your training device.

```bash
# Download as .zwo (Zwift format)
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/events/EVENT_ID/download.zwo" \
  --output workout.zwo

# Download as .mrc (TrainerRoad format)
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/events/EVENT_ID/download.mrc" \
  --output workout.mrc

# Download as .erg (Wahoo format)
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/events/EVENT_ID/download.erg" \
  --output workout.erg

# Download as .fit (Garmin format)
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/events/EVENT_ID/download.fit" \
  --output workout.fit

# Download multiple workouts as zip
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/workouts.zip?oldest=2024-02-01&newest=2024-02-29&ext=zwo" \
  --output workouts.zip
```

---

## Creating & Writing Data

### Create Manual Activity

Add a manually-logged activity to your training history.

```bash
# Basic manual activity
curl -X POST \
  -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Morning Run",
    "type": "Run",
    "start_date_local": "2024-01-15T06:00:00",
    "distance": 10000,
    "moving_time": 3600,
    "description": "Easy morning run"
  }' \
  https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/activities/manual

# With power (cycling activity)
curl -X POST \
  -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Indoor Zwift",
    "type": "Ride",
    "start_date_local": "2024-01-15T18:00:00",
    "moving_time": 3600,
    "icu_joules": 900000,
    "icu_weighted_avg_watts": 250,
    "average_heartrate": 155,
    "trainer": true
  }' \
  https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/activities/manual

# With external ID (for syncing with external systems)
curl -X POST \
  -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Strava Activity",
    "type": "Run",
    "start_date_local": "2024-01-15T07:00:00",
    "distance": 5000,
    "moving_time": 1800,
    "external_id": "strava_12345"
  }' \
  https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/activities/manual
```

### Create Multiple Activities (Bulk)

```bash
# Bulk create activities
curl -X POST \
  -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "name": "Monday Easy Run",
      "type": "Run",
      "start_date_local": "2024-01-15T06:00:00",
      "distance": 10000,
      "moving_time": 3600
    },
    {
      "name": "Tuesday Interval Ride",
      "type": "Ride",
      "start_date_local": "2024-01-16T18:00:00",
      "moving_time": 5400,
      "icu_weighted_avg_watts": 280
    }
  ]' \
  https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/activities/manual/bulk
```

### Create Planned Workout (Event on Calendar)

Add a scheduled workout to your calendar for future training.

```bash
# Basic planned workout
curl -X POST \
  -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Vo2Max Intervals",
    "category": "WORKOUT",
    "start_date_local": "2024-02-15T18:00:00",
    "description": "6x 4min at 110% FTP with 3min recovery"
  }' \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/events?upsertOnUid=true"

# Planned workout with Intervals.icu format description
curl -X POST \
  -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sweet Spot Build",
    "category": "WORKOUT",
    "start_date_local": "2024-02-16T18:00:00",
    "description": "[Workout \"Sweet Spot\" \"\" Bike 300\n  [SteadyState 600 88 92 \"\"]\n  [SteadyState 600 88 92 \"\"]\n  [SteadyState 600 88 92 \"\"]\n]"
  }' \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/events?upsertOnUid=true"

# Create workout from .zwo file contents
curl -X POST \
  -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Zwift Structured Workout",
    "category": "WORKOUT",
    "start_date_local": "2024-02-17T19:00:00",
    "file_contents": "<Workout_Instruction version=\"1\">\n<author></author>\n<name>My Workout</name>\n<description></description>\n<sportType>Bike</sportType>\n<tags></tags>\n<workout>\n<Warmup Duration=\"600\" PowerLow=\"0.5\" PowerHigh=\"0.75\"/>\n<SteadyState Duration=\"1200\" Power=\"0.85\"/>\n</workout>\n</Workout_Instruction>"
  }' \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/events?upsertOnUid=true"
```

### Create Multiple Events (Bulk)

```bash
# Bulk create planned workouts
curl -X POST \
  -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "name": "Easy Spin",
      "category": "WORKOUT",
      "start_date_local": "2024-02-15T18:00:00",
      "description": "60min at 60-65% FTP"
    },
    {
      "name": "Threshold Work",
      "category": "WORKOUT",
      "start_date_local": "2024-02-17T19:00:00",
      "description": "3x 10min at 95-105% FTP"
    },
    {
      "name": "Long Run",
      "category": "WORKOUT",
      "start_date_local": "2024-02-18T07:00:00",
      "description": "90min easy run at conversational pace"
    }
  ]' \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/events/bulk?upsertOnUid=true&updatePlanApplied=true"
```

### Create Training Target (Goal for Date)

Set a specific training target for a date.

```bash
# Create power target
curl -X POST \
  -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "FTP Test Target",
    "category": "TARGET",
    "start_date_local": "2024-02-20T18:00:00",
    "description": "Target power: 300W"
  }' \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/events?upsertOnUid=true"

# Create duration target
curl -X POST \
  -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily Volume Target",
    "category": "TARGET",
    "start_date_local": "2024-02-21T00:00:00",
    "description": "Target: 2 hours training"
  }' \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/events?upsertOnUid=true"
```

---

## Updating Data

### Update Activity

Modify an existing completed activity.

```bash
# Update activity notes and tags
curl -X PUT \
  -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Recovery Ride - Updated",
    "description": "Felt great, good recovery",
    "commute": false
  }' \
  https://intervals.icu/api/v1/activity/ACTIVITY_ID

# Update activity perceived exertion and feel
curl -X PUT \
  -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "perceived_exertion": 7,
    "feel": 8,
    "description": "Good session, felt strong"
  }' \
  https://intervals.icu/api/v1/activity/ACTIVITY_ID
```

### Update Planned Workout (Event)

Modify a scheduled event on your calendar.

```bash
# Update workout details
curl -X PUT \
  -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Modified VO2Max Session",
    "description": "8x 3min at 130% FTP with 2min recovery - UPDATED"
  }' \
  https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/events/EVENT_ID

# Hide event from athlete view
curl -X PUT \
  -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "hide_from_athlete": true
  }' \
  https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/events/EVENT_ID

# Prevent athlete from editing event
curl -X PUT \
  -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "athlete_cannot_edit": true
  }' \
  https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/events/EVENT_ID
```

### Update Multiple Events (Date Range)

```bash
# Hide all workouts for a week
curl -X PUT \
  -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "hide_from_athlete": true
  }' \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/events?oldest=2024-02-15&newest=2024-02-22"
```

---

## Wellness & Recovery Data

### Get Wellness Records

Track sleep, fatigue, resting HR, and other wellness metrics.

```bash
# Get wellness data for date range
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/wellness?oldest=2024-01-01&newest=2024-01-31"

# Get wellness data as CSV
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/wellness.csv?oldest=2024-01-01&newest=2024-01-31" \
  --output wellness.csv

# Get specific wellness fields
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/wellness?oldest=2024-01-01&fields=id,sleep_secs,soreness,fatigue,resting_hr,notes"
```

### Update Wellness Record

Log wellness data for a specific date.

```bash
# Add sleep, HRV, and fatigue
curl -X PUT \
  -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "2024-01-15",
    "sleep_secs": 28800,
    "resting_hr": 52,
    "fatigue": 3,
    "soreness": 2
  }' \
  https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/wellness/2024-01-15

# Add notes
curl -X PUT \
  -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "2024-01-15",
    "notes": "Great sleep, feeling recovered"
  }' \
  https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/wellness/2024-01-15
```

### Bulk Update Wellness Records

```bash
# Update multiple wellness days at once
curl -X PUT \
  -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "id": "2024-01-15",
      "sleep_secs": 28800,
      "resting_hr": 52
    },
    {
      "id": "2024-01-16",
      "sleep_secs": 30600,
      "resting_hr": 50
    },
    {
      "id": "2024-01-17",
      "sleep_secs": 27000,
      "resting_hr": 54
    }
  ]' \
  https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/wellness-bulk
```

---

## Sport Settings & Zones

### Get Sport Settings

Retrieve power zones, HR zones, and FTP settings for a sport.

```bash
# Get Ride settings
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/sport-settings/Ride"

# Get Run settings
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/sport-settings/Run"

# List all sport settings
curl -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/sport-settings"
```

### Update Sport Settings

Modify power zones, FTP, or HR zones.

```bash
# Update FTP and power zones
curl -X PUT \
  -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "ftp": 310,
    "power_zones": [0, 114, 152, 191, 229, 267, 310]
  }' \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/sport-settings/Ride?recalcHrZones=false"

# Update LTHR and HR zones
curl -X PUT \
  -H "Authorization: ApiKey API_KEY:YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "lthr": 165,
    "hr_zones": [0, 123, 142, 160, 178, 197, 220]
  }' \
  "https://intervals.icu/api/v1/athlete/YOUR_ATHLETE_ID/sport-settings/Ride?recalcHrZones=true"
```

---

## Common Use Cases

### Workflow: Sync Training Data with External System

```bash
#!/bin/bash

ATHLETE_ID="YOUR_ATHLETE_ID"
API_KEY="YOUR_API_KEY"
DATE="2024-01-15"

# 1. Get completed activities
ACTIVITIES=$(curl -s -H "Authorization: ApiKey $ATHLETE_ID:$API_KEY" \
  "https://intervals.icu/api/v1/athlete/$ATHLETE_ID/activities?oldest=$DATE&newest=$DATE&fields=id,name,type,distance,icu_training_load")

# 2. Get planned workouts for today
EVENTS=$(curl -s -H "Authorization: ApiKey $ATHLETE_ID:$API_KEY" \
  "https://intervals.icu/api/v1/athlete/$ATHLETE_ID/events?oldest=$DATE&newest=$DATE&category=WORKOUT")

# 3. Get wellness data
WELLNESS=$(curl -s -H "Authorization: ApiKey $ATHLETE_ID:$API_KEY" \
  "https://intervals.icu/api/v1/athlete/$ATHLETE_ID/wellness/$DATE")

echo "Activities: $ACTIVITIES"
echo "Events: $EVENTS"
echo "Wellness: $WELLNESS"
```

### Workflow: Create Weekly Training Plan

```bash
#!/bin/bash

ATHLETE_ID="YOUR_ATHLETE_ID"
API_KEY="YOUR_API_KEY"

# Define workouts for the week
WORKOUTS='[
  {
    "name": "Monday - Easy Spin",
    "category": "WORKOUT",
    "start_date_local": "2024-02-19T18:00:00",
    "description": "60min at 60-65% FTP"
  },
  {
    "name": "Tuesday - VO2Max",
    "category": "WORKOUT",
    "start_date_local": "2024-02-20T18:00:00",
    "description": "6x 4min at 110% FTP with 3min recovery"
  },
  {
    "name": "Wednesday - Recovery",
    "category": "WORKOUT",
    "start_date_local": "2024-02-21T18:00:00",
    "description": "45min easy"
  },
  {
    "name": "Thursday - Threshold",
    "category": "WORKOUT",
    "start_date_local": "2024-02-22T19:00:00",
    "description": "2x 15min at 95-105% FTP"
  },
  {
    "name": "Friday - Rest Day",
    "category": "NOTE",
    "start_date_local": "2024-02-23T00:00:00",
    "description": "Rest and recovery"
  },
  {
    "name": "Saturday - Long Ride",
    "category": "WORKOUT",
    "start_date_local": "2024-02-24T09:00:00",
    "description": "150min at Zone 2"
  },
  {
    "name": "Sunday - Easy Recovery",
    "category": "WORKOUT",
    "start_date_local": "2024-02-25T10:00:00",
    "description": "60min easy spin"
  }
]'

# Create all workouts at once
curl -X POST \
  -H "Authorization: ApiKey $ATHLETE_ID:$API_KEY" \
  -H "Content-Type: application/json" \
  -d "$WORKOUTS" \
  "https://intervals.icu/api/v1/athlete/$ATHLETE_ID/events/bulk?upsertOnUid=true&updatePlanApplied=true"
```

### Workflow: Analyze Week Data

```bash
#!/bin/bash

ATHLETE_ID="YOUR_ATHLETE_ID"
API_KEY="YOUR_API_KEY"

# Get activities with load and zone data for the week
curl -s -H "Authorization: ApiKey $ATHLETE_ID:$API_KEY" \
  "https://intervals.icu/api/v1/athlete/$ATHLETE_ID/activities?oldest=2024-01-08&newest=2024-01-14&fields=name,type,distance,icu_training_load,icu_zone_times,average_heartrate" | \
  jq '[.[] | {name: .name, load: .icu_training_load, zones: .icu_zone_times, hr: .average_heartrate}]'
```

---

## Important Notes

### Rate Limiting

Be respectful with API calls. Don't hammer the API with rapid successive requests.

### Field Selection

Use the `fields` parameter to request only the data you need. This improves performance and reduces payload size.

### Date Formats

Always use ISO-8601 format: `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SS`

### Upsert Parameter

When creating events, use `upsertOnUid=true` to update existing events with matching UIDs instead of creating duplicates.

### External IDs

Use `external_id` when syncing data from other systems to avoid duplicates on re-sync.

### Forum Discussion

For more detailed API information, see: [API Access Forum Post](https://forum.intervals.icu/t/api-access-to-intervals-icu/609)

---

## Response Status Codes

- **200**: Success
- **201**: Created successfully (activities, events)
- **400**: Bad request (invalid parameters)
- **401**: Unauthorized (invalid API key or token)
- **404**: Not found (invalid IDs)
- **429**: Rate limited (too many requests)
- **500**: Server error

Check response headers for error details and rate limit information.
