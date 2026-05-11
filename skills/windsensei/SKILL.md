---
name: windsensei
description: Check wind and weather conditions for wind sports (kitesurfing, wingfoiling, surfing). Get forecasts, find spots nearby, view session history, and request new spots.
homepage: https://windsensei.com
source: https://github.com/jumptrnr/spotsensei
user-invocable: true
metadata: {"emoji": "🪁", "optionalEnv": "WINDSENSEI_API_KEY"}
---

# WindSensei - Wind Forecast Assistant

Check wind conditions at your favorite spots and take action on good forecasts.

## When to Use This Skill

Activate when the user asks about:
- Wind conditions, wind forecast, or weather for wind sports
- "How's the wind?", "Should I go kiting?", "Any good wind this weekend?"
- "What's it looking like at [spot name]?", "Wind report"
- Kiting, kitesurfing, wingfoiling, windsurfing, surfing conditions
- Blocking off time or adding sessions to their calendar based on wind
- Finding spots near a location or exploring new spots
- Session history, stats, or activity logs
- What friends are riding right now (live sessions)

## Configuration

### Credentials

- `WINDSENSEI_API_KEY`: An API key starting with `ss_`. **Optional — the skill works fully without it.** Without it, you can still query any public spot by name, search for spots, and find spots nearby. With it, you get personalized forecasts, dashboard overview, session history, and social features.
- **No other credentials are required.** This skill only makes HTTPS requests to the WindSensei API. Calendar features (if requested by the user) use the host agent's own calendar tools — this skill does not request or store any calendar credentials.

### Getting an API Key

If the user wants personalized forecasts, guide them:
1. Sign up at **windsensei.com**
2. Add their favorite spots and set activity preferences
3. Go to their **Profile page** at **windsensei.com/dashboard/profile** — the API key manager is at the bottom of that page
4. Click **"Create API Key"**, give it a name (e.g., "Claude" or "OpenClaw"), and copy the key
5. The key starts with `ss_` — set it as `WINDSENSEI_API_KEY` in the agent's environment config

**Direct link:** `https://windsensei.com/dashboard/profile` (scroll to "API Keys" section)

## Two Modes

### Public Mode (no API key)
- Query any public spot by name using the `spot` parameter
- Search for spots by name
- Find spots near a latitude/longitude
- Uses default kiting preferences (12-40kt, 8am-8pm)
- Response includes a `hint` field suggesting signup for personalized results

### Authenticated Mode (with API key)
- Everything in public mode, plus:
- Dashboard overview of all favorite spots in one call
- Personalized forecasts using the user's activity preferences, wind speed ranges, time windows
- Session history and stats
- Live session feed from followed users
- Favorites list
- No signup hint in response

## Authentication

For all authenticated endpoints, include the API key as a Bearer token:
```
Authorization: Bearer {WINDSENSEI_API_KEY}
```

The API also accepts `X-API-Key: {key}` header or `?api_key={key}` query param.

---

## API Endpoints

### 1. Wind Report (Quick Summary)

The simplest way to check conditions. Returns a natural language summary plus structured data.

```
GET https://windsensei.com/api/v1/wind-report?when={when}
```

| Param | Values | Default | Description |
|-------|--------|---------|-------------|
| `when` | `today`, `tomorrow`, `weekend`, `week` | `today` | Time window |
| `spot` | string (e.g., `Cherry Beach`) | — | Search public spots by name. Not needed with API key. |
| `locationId` | string | — | Specific spot by ID |
| `format` | `text`, `full` | `full` | `text` returns just the summary string |

**Auth:** Optional. With API key, returns forecasts for all the user's favorite spots automatically.

**Response:**
```json
{
  "success": true,
  "text": "Cherry Beach: Great conditions 2-6pm — 18-22kt SW, 24°C, water 19°C. Good for Kitefoil, Twintip.",
  "when": "today",
  "authenticated": false,
  "hint": "Personalize your forecast with your own spots and activity preferences at windsensei.com",
  "locations": [
    {
      "locationId": "abc123",
      "name": "Cherry Beach",
      "timezone": "America/Toronto",
      "blocks": [
        {
          "date": "2026-02-21",
          "dateLabel": "Saturday, Feb 21",
          "start": "14:00",
          "end": "18:00",
          "quality": "good",
          "windSpeed": { "avg": 20, "gust": 25 },
          "windDirection": "SW",
          "windQuality": "good",
          "temperature": 24,
          "waterTemp": 19,
          "activities": ["Kitefoil", "Twintip"]
        }
      ]
    }
  ]
}
```

**When no spot specified and no API key:**
```json
{
  "success": true,
  "text": "Provide a spot name to check conditions. Example: ?spot=Cherry Beach",
  "locations": [],
  "hint": "Personalize your forecast with your own spots and activity preferences at windsensei.com"
}
```

---

### 2. Dashboard (All Spots Overview)

**Auth: Required.** Single call to get current conditions for all the user's favorite spots, sorted best-first. The most efficient way to answer "how's the wind?" for authenticated users.

```
GET https://windsensei.com/api/v1/dashboard
```

**Response:**
```json
{
  "success": true,
  "spots": [
    {
      "locationId": "abc123",
      "name": "Cherry Beach",
      "current": {
        "windSpeed": 18,
        "windGust": 24,
        "windDirection": 225,
        "temperature": 22,
        "quality": "good"
      },
      "observed": {
        "stationName": "Toronto Island",
        "observationTime": "2026-02-21T14:00:00Z",
        "windSpeed": 20,
        "windDirection": 210,
        "windGust": 26,
        "temperature": 21,
        "waterTemp": { "temperature": 18.5, "units": "C" }
      },
      "nextGoodWindow": {
        "start": "2026-02-21T14:00",
        "end": "2026-02-21T18:00",
        "quality": "good",
        "activities": ["Kitefoil", "Twintip"]
      },
      "modelConsensus": {
        "agreement": "high",
        "models": ["GFS", "ICON", "GEM"]
      }
    }
  ],
  "generatedAt": "2026-02-21T12:00:00Z"
}
```

**Key fields:**
- `current`: Forecast-based current conditions
- `observed`: Real weather station data (if available for the spot) — more accurate than forecast
- `nextGoodWindow`: Next rideable time window based on the user's activity preferences. Times are in the spot's local timezone.
- `modelConsensus`: Whether forecast models agree on conditions
- Spots are sorted by quality (best first), then by wind speed

**When to use dashboard vs wind-report:**
- Use **dashboard** when the user has an API key and asks a general "how's the wind?" — it covers all their spots in one call
- Use **wind-report** when querying a specific spot by name, or when there's no API key

---

### 3. Best Conditions (Ranked Spots)

Find the best spots right now. Works with or without auth.

```
GET https://windsensei.com/api/v1/best-conditions
```

| Param | Values | Default | Description |
|-------|--------|---------|-------------|
| `when` | `now`, `today`, `tomorrow`, `weekend` | `now` | Time window. `now` = current hour onward. |
| `lat` | number | — | Latitude (required if no API key) |
| `lng` | number | — | Longitude (required if no API key) |
| `radius` | number | 100 | Search radius in km (max 500). Only used with lat/lng. |
| `limit` | number | 5 | Max results (max 20) |

**Auth:** Optional.
- **With API key:** Evaluates the user's favorite spots using their activity preferences. No lat/lng needed.
- **Without API key:** Requires lat/lng. Finds nearby public spots and evaluates with default kiting preferences.
- If authenticated but no favorites, falls back to lat/lng nearby search.

**Response:**
```json
{
  "success": true,
  "when": "now",
  "spots": [
    {
      "locationId": "abc123",
      "name": "Cherry Beach",
      "timezone": "America/Toronto",
      "distance": 4.2,
      "current": {
        "windSpeed": 20,
        "windGust": 26,
        "windDirection": "SW",
        "windQuality": "good",
        "temperature": 22,
        "quality": "good"
      },
      "waterTemp": 18.5,
      "bestBlock": {
        "date": "2026-02-21",
        "dateLabel": "Saturday, Feb 21",
        "start": "14:00",
        "end": "18:00",
        "quality": "good",
        "windSpeed": { "avg": 20, "gust": 26 },
        "windDirection": "SW",
        "activities": ["Kitefoil", "Twintip"]
      },
      "activities": ["Kitefoil", "Twintip"]
    }
  ],
  "total": 1,
  "authenticated": false,
  "hint": "Get personalized results with your own spots and preferences at windsensei.com",
  "generatedAt": "2026-02-21T12:00:00Z"
}
```

**Key fields:**
- `distance`: Distance from the provided lat/lng in km (only present for nearby queries)
- `current`: Conditions right now (or first hour in the time window)
- `bestBlock`: The best consecutive window of rideable conditions in the time range
- Only spots with medium or better conditions are returned — bad spots are excluded
- Spots are sorted best-first by quality, then wind speed

**When to use:** "What's the best spot right now?", "Where should I go kiting near Toronto?", "Best conditions this weekend?"

---

### 4. Search Spots

Find spots by name. Works without auth.

```
GET https://windsensei.com/api/v1/locations/search?q={query}
```

| Param | Values | Default | Description |
|-------|--------|---------|-------------|
| `q` | string | — | Search query (required) |
| `limit` | number | 10 | Max results (max 50) |

**Auth:** Optional. Authenticated users also see their private spots.

**Response:**
```json
{
  "success": true,
  "query": "cherry",
  "locations": [
    {
      "_id": "abc123",
      "name": "Cherry Beach",
      "latitude": 43.63,
      "longitude": -79.34,
      "activityTypes": ["kite"],
      "windDirections": ["SW", "S", "W"],
      "isFavorite": false
    }
  ],
  "total": 1
}
```

**When to use:** To resolve a spot name to a `locationId` for use with other endpoints, or when the user wants to browse available spots.

---

### 5. Nearby Spots

Find spots near a location. Works without auth.

```
GET https://windsensei.com/api/v1/locations/nearby?lat={lat}&lng={lng}
```

| Param | Values | Default | Description |
|-------|--------|---------|-------------|
| `lat` | number | — | Latitude (required) |
| `lng` | number | — | Longitude (required) |
| `radius` | number | 50 | Radius in km (max 500) |
| `limit` | number | 10 | Max results (max 50) |

**Auth:** Optional. Authenticated users also see private spots.

**Response:**
```json
{
  "success": true,
  "center": { "lat": 43.65, "lng": -79.38 },
  "radiusKm": 50,
  "locations": [
    {
      "id": "abc123",
      "name": "Cherry Beach",
      "latitude": 43.63,
      "longitude": -79.34,
      "distance": 4.2,
      "activityTypes": ["kite"],
      "windDirections": { "SW": "good", "S": "medium", "W": "good" },
      "isFavorite": false
    }
  ],
  "total": 3
}
```

**When to use:** When the user says "what spots are near me?", "spots near Toronto", or "find kite spots in [city]". You'll need to geocode the city/location to lat/lng first (use the agent's geocoding capability or a known coordinate).

---

### 6. Detailed Forecast

Full hourly forecast for a specific spot. More detailed than wind-report.

```
GET https://windsensei.com/api/v1/forecast/{locationId}/full
```

**Auth: Required.** Returns personalized quality ratings based on the user's activity preferences.

**Response includes:**
- Hourly wind speed, direction, gusts, temperature, precipitation
- Time blocks with quality ratings (excellent/good/medium)
- Tide predictions (high/low times)
- Water temperature
- Model consensus data
- Up to 16 days of forecast

**When to use:** When the user wants hour-by-hour detail, or asks "when exactly is the best window?" after seeing a summary.

---

### 7. Favorites List

Get the user's favorite spots in their saved order.

```
GET https://windsensei.com/api/v1/favorites
```

**Auth: Required.**

**Response:**
```json
{
  "success": true,
  "locations": [
    {
      "_id": "abc123",
      "name": "Cherry Beach",
      "latitude": 43.63,
      "longitude": -79.34,
      "activityTypes": ["kite"],
      "windDirections": ["SW", "S", "W"],
      "isFavorite": true
    }
  ]
}
```

**When to use:** When the user asks "what are my spots?" or "list my favorites."

---

### 8. Session History

Get the user's logged wind sport sessions.

```
GET https://windsensei.com/api/v1/sessions
```

| Param | Values | Default | Description |
|-------|--------|---------|-------------|
| `limit` | number | 20 | Max results (max 100) |
| `offset` | number | 0 | Pagination offset |
| `activityType` | string | — | Filter by activity (e.g., "Kitefoil", "Wingfoil") |
| `locationId` | string | — | Filter by spot |

**Auth: Required.**

**Response:**
```json
{
  "success": true,
  "sessions": [
    {
      "id": "sess123",
      "activityType": "Kitefoil",
      "locationName": "Cherry Beach",
      "startTime": "2026-02-15T14:00:00Z",
      "endTime": "2026-02-15T17:30:00Z",
      "duration": 12600,
      "rating": 4,
      "notes": "Great session, consistent SW wind",
      "stats": {
        "distance": 15.2,
        "maxSpeed": 32.5
      }
    }
  ],
  "pagination": {
    "total": 47,
    "limit": 20,
    "offset": 0,
    "hasMore": true
  }
}
```

**When to use:** When the user asks "how many sessions have I had?", "show my recent sessions", "what was my last kite session?", or "how much have I ridden this month?"

---

### 9. Live Sessions (Friends Activity)

See which followed users are currently out riding.

```
GET https://windsensei.com/api/v1/live-sessions
```

**Auth: Required.**

**Response:**
```json
{
  "success": true,
  "data": {
    "sessions": [
      {
        "id": "live123",
        "user": {
          "name": "Mike",
          "nickname": "windmike"
        },
        "activityType": "Wingfoil",
        "spotName": "Cherry Beach",
        "startTime": "2026-02-21T14:00:00Z",
        "lastUpdateTime": "2026-02-21T14:30:00Z",
        "stats": {
          "elapsedTime": 1800,
          "distance": 3.2,
          "maxSpeed": 22.1
        },
        "conditions": {
          "windSpeed": 18,
          "windDirection": "SW"
        }
      }
    ]
  }
}
```

**When to use:** When the user asks "is anyone out right now?", "who's riding?", or "are any of my friends on the water?"

---

### 10. Public Profile

Look up any WindSensei user's public stats by their handle. No auth needed.

```
GET https://windsensei.com/api/public/profile/{nickname}
```

**Auth: None.**

**Response includes:** nickname, avatar, total session count, total duration, total distance, recent public sessions, activity types.

**When to use:** When the user asks about a specific rider's profile or stats.

---

### 11. Request a New Spot

Submit a request to add a spot that isn't in the system yet.

```
POST https://windsensei.com/api/v1/spot-request
Content-Type: application/json

{
  "spotName": "Spot Name Here"
}
```

**Auth:** Optional. If API key is included, the request is attributed to the user.

**Response:**
```json
{
  "success": true,
  "message": "Spot request for \"Spot Name\" submitted. We'll review it soon."
}
```

Duplicate requests are handled automatically — just returns success.

---

## Interpreting the Data

**CRITICAL: Only report what the API data says. Do NOT:**
- Make up or guess whether conditions are good if the API didn't say so
- Add your own assessment of wind speeds, directions, or quality beyond what the `quality` and `windQuality` fields state
- Speculate about conditions outside the blocks returned (e.g., "morning might be OK too")
- Editorialize about whether the user should or shouldn't go — the blocks and quality ratings ARE the answer
- Infer activities beyond what the `activities` array lists for each block

**If `blocks` is empty for a location, there are NO good conditions. Period.** Don't soften this or suggest the user check anyway.

**If `blocks` exist, they represent the API's definitive assessment** — the quality, wind speed, direction, and activities are computed from the user's preferences and the spot's characteristics. Trust them exactly as returned.

- **timezone**: Each location includes a `timezone` field (e.g., `"America/Toronto"`). **All times in `start`, `end`, and `date` fields are in this timezone** — not UTC, not the user's local time. When presenting times to the user, always clarify the timezone if it differs from the user's location (e.g., "2-6pm EST").
- **quality**: "excellent" > "good" > "medium". Only these appear — bad hours are excluded. Use these exact ratings when describing conditions.
- **windQuality**: How good the wind direction is for that spot ("good", "medium", "bad"). This is computed from the spot's known best directions — don't override it.
- **blocks**: Each block is a continuous window of rideable conditions. Multiple blocks per location/day are possible. If no blocks exist, there are no rideable conditions.
- **activities**: Which wind sports suit the conditions (e.g., "Kitefoil", "Twintip", "Wingfoil"). Only mention activities listed in the block.
- **observed vs current**: `observed` comes from real weather stations and is more accurate. `current` is forecast-based. Prefer observed data when available.
- **modelConsensus**: When `agreement` is "high", the forecast is more reliable.
- **authenticated**: Whether the response used personalized preferences. If `false`, mention the user can get better results by setting up an API key.
- **hint**: Present only for unauthenticated queries. Relay this to the user naturally (e.g., at the end of the first response, not every time).

## Responding to the User

1. **Relay the `text` field first** (when using wind-report) — it's already a concise, factual summary.
2. If the user wants more detail, use the structured `blocks` data to elaborate — but stick to what the data says.
3. For "no good conditions" results (empty blocks), be straightforward: "Nothing rideable today at Cherry Beach." Don't add speculation about what might work.
4. If `hint` is present in the response, casually mention it the first time: "By the way, you can get personalized forecasts for your spots at windsensei.com"
5. When using dashboard data, lead with the best spot and summarize the rest.
6. Don't pad with filler. Be direct, like a friend at the beach.
7. **Never contradict the API's quality assessment.** If the API says "medium" quality, don't upgrade it to "great conditions." If the API says no blocks, don't say "it might still be worth checking."

## Choosing the Right Endpoint

| User intent | Endpoint | Auth needed? |
|------------|----------|-------------|
| "How's the wind?" (has API key) | Dashboard | Yes |
| "How's the wind at Cherry Beach?" | Wind Report with `spot=` | No |
| "How's the wind this weekend?" | Wind Report with `when=weekend` | No |
| "What's the best spot right now?" | Best Conditions | No (lat/lng) or Yes |
| "Where should I kite near Miami?" | Best Conditions with lat/lng | No |
| "What spots are near Toronto?" | Nearby (geocode city first) | No |
| "Find spots called 'cherry'" | Search with `q=cherry` | No |
| "Give me hour-by-hour for Cherry Beach" | Forecast Full | Yes |
| "What are my spots?" | Favorites | Yes |
| "How many sessions have I had?" | Sessions | Yes |
| "Is anyone riding right now?" | Live Sessions | Yes |
| "Show me @windmike's profile" | Public Profile | No |
| "Add Wasaga Beach" (spot not found) | Spot Request | No |

## Handling Spot Names

When the user says "how's the wind at Cherry Beach":
1. Extract the spot name ("Cherry Beach")
2. URL-encode it and pass as `?spot=Cherry+Beach` to wind-report
3. The API does fuzzy matching — partial names work (e.g., "cherry" matches "Cherry Beach")
4. If multiple spots match, the API returns up to 3. Present all of them.

For more control, use the Search endpoint first to resolve the name to a `locationId`, then use that ID with other endpoints.

## Handling Missing Spots

When a spot isn't found:
1. Tell the user: "WindSensei doesn't have data for that spot yet."
2. Ask: "Want me to submit a request to add it?"
3. If they say yes, POST to `/api/v1/spot-request` with the spot name.
4. Relay the confirmation message.

## Calendar Integration

This skill does not provide or require any calendar credentials. It relies on the host agent's existing calendar tools (e.g., Google Calendar MCP, Apple Calendar, etc.). If the agent has no calendar tool available, skip calendar actions and just present the forecast data.

When the user asks to "block off", "add to calendar", or "schedule" a session based on a wind block:

1. Use the block data to create a calendar event via the agent's calendar tool:
   - **Title**: `Kite @ {location name}` (or the relevant activity from the block)
   - **Start**: The block's `date` + `start` time
   - **End**: The block's `date` + `end` time
   - **Description**: `{windSpeed.avg}kt {windDirection} (gusts {windSpeed.gust}kt), {temperature}°C{waterTemp ? ', water ' + waterTemp + '°C' : ''}. Quality: {quality}.`
   - **Location**: The spot name

2. Confirm to the user what was added.
3. If no calendar tool is available, offer the event details so the user can add it manually.

If there are multiple good blocks, ask which one(s) to add unless the user said "all".

## Example Conversations

**First-time user, no API key:**
> User: "How's the wind at Cherry Beach?"
> → Call GET /api/v1/wind-report?spot=Cherry+Beach&when=today
> → Relay the `text` field
> → Mention: "For personalized forecasts with your own spots, check out windsensei.com"

**Authenticated user, quick check:**
> User: "How's the wind?"
> → Call GET /api/v1/dashboard (with Bearer token)
> → Summarize: lead with the best spot, mention the rest

**Best spot right now (unauthenticated):**
> User: "Where should I go kiting near Miami?"
> → Geocode Miami to lat=25.76, lng=-80.19
> → Call GET /api/v1/best-conditions?lat=25.76&lng=-80.19&when=now
> → "Crandon Park has the best conditions right now — 18kt SE, good direction, 28°C. Best window is 2-6pm."

**Best spot right now (authenticated):**
> User: "What's my best spot today?"
> → Call GET /api/v1/best-conditions?when=today (with Bearer token)
> → "Cherry Beach looks best today — good conditions 2-6pm with 20kt SW. Hanlan's has medium conditions 1-4pm."

**Finding new spots:**
> User: "What kite spots are near Miami?"
> → Geocode Miami to lat=25.76, lng=-80.19
> → Call GET /api/v1/locations/nearby?lat=25.76&lng=-80.19&radius=100
> → Present the spots with distances

**Session stats:**
> User: "How many sessions have I logged this year?"
> → Call GET /api/v1/sessions?limit=100
> → Count and summarize by activity type

**Live check:**
> User: "Is anyone out riding right now?"
> → Call GET /api/v1/live-sessions
> → "Your friend Mike is wingfoiling at Cherry Beach — been out for 30 minutes in 18kt SW wind"

**Calendar action:**
> User: "Block off the good times this weekend"
> → Call GET /api/v1/wind-report?when=weekend
> → For each block, create a calendar event
> → "Added 2 sessions to your calendar: Kite @ Cherry Beach Sat 2-6pm, Wing @ Hanlan's Sun 10am-1pm"

**Specific day:**
> User: "What about Saturday?"
> → Call GET /api/v1/wind-report?when=weekend
> → Relay the relevant day from the response

**No conditions:**
> User: "Should I go kiting tomorrow?"
> → Call GET /api/v1/wind-report?when=tomorrow
> → If no blocks: "No rideable conditions tomorrow at [spot name]."

**Missing spot:**
> User: "How's the wind at Wasaga Beach?"
> → Call GET /api/v1/wind-report?spot=Wasaga+Beach
> → Response: not found
> → Reply: "WindSensei doesn't have data for Wasaga Beach yet. Want me to submit a request to add it?"
> User: "Yeah, do it"
> → Call POST /api/v1/spot-request with `{"spotName": "Wasaga Beach"}`
> → Reply: "Done — submitted a request to add Wasaga Beach. The WindSensei team will review it."
