---
name: skanetrafiken
description: Skåne public transport trip planner (Skånetrafiken). Plans bus/train journeys with real-time delays. Supports stations, addresses, landmarks, and cross-border trips to Copenhagen.
license: MIT
compatibility: Requires curl, jq. Works with Claude Code and compatible agents.
metadata:
  author: rezkam
  version: "1.2.0"
  region: sweden
---

# Skånetrafiken Trip Planner

Plan public transport journeys in Skåne, Sweden with real-time departure information.

## Commands

### 1. Search Location

Search for stations, addresses, or points of interest.

```bash
./search-location.sh <query> [limit]
```

| Argument | Description |
|----------|-------------|
| `query` | Location name to search for |
| `limit` | Number of results to show (default: 3, max: 10) |

**Output includes:**
- `ID` - The location identifier (use this in journey search)
- `Name` - Official name of the location
- `Type` - STOP_AREA (station), ADDRESS, or POI (point of interest)
- `Area` - Region/municipality
- `Coordinates` - Latitude, longitude

**When to increase limit:**
- First result doesn't match user's intent
- User's query is ambiguous (e.g., "station", "centrum")
- Need to show user multiple options to choose from

### 2. Journey Search

Plan a journey between two locations using their IDs.

```bash
./journey.sh <from-id> <from-type> <to-id> <to-type> [datetime] [mode]
```

| Argument | Description |
|----------|-------------|
| `from-id` | Origin location ID (from search) or coordinates (`lat#lon`) |
| `from-type` | `STOP_AREA`, `ADDRESS`, `POI`, or `LOCATION` (for coordinates) |
| `to-id` | Destination location ID or coordinates |
| `to-type` | Type of destination |
| `datetime` | Optional: `"18:30"`, `"tomorrow 09:00"`, `"2026-01-15 09:00"` |
| `mode` | Optional: `"depart"` (default) or `"arrive"` |

**Important:** The Journey API only accepts `STOP_AREA` and `LOCATION` types. For `ADDRESS` or `POI` results, use the coordinates as `lat#lon` with type `LOCATION`.

---

## Understanding User Time Intent

Before searching, understand what the user wants:

### Intent Types

| User Says | Intent | How to Query |
|-----------|--------|--------------|
| "now", "next bus", "how do I get to" | **Travel Now** | No datetime parameter |
| "in 30 minutes", "in 1 hour", "after lunch" | **Depart Later** | Calculate time, use `depart` mode |
| "around 15:00", "sometime afternoon" | **Around Time** | Query with offset (see below) |
| "arrive by 18:00", "need to be there at 9" | **Arrive By** | Use `arrive` mode |
| "tomorrow morning", "on Friday at 10" | **Future Time** | Use specific datetime |

### Handling "Around Time" Queries

When user wants options "around" a time, query 15-30 minutes earlier to show options before and after:

```bash
# User: "I want to travel around 15:00"
# Query at 14:30 to get options spanning 14:30-16:00+
./journey.sh ... "14:30" depart
```

### Relative Time Calculations

Convert relative times to absolute:

| User Says | Current: 14:00 | Query Time |
|-----------|----------------|------------|
| "in 30m" | → | "14:30" |
| "in 1h" | → | "15:00" |
| "in 2 hours" | → | "16:00" |

---

## LLM Response Formatting

When presenting journey results to users, use these emojis and formatting guidelines.

### Emoji Reference

| Emoji | Use For |
|-------|---------|
| 🚂 | Train (Pågatåg, Öresundståg) |
| 🚌 | Bus |
| 🚇 | Metro (Copenhagen) |
| 🚋 | Tram |
| ⛴️ | Ferry |
| 🚶 | Walking segment |
| ⏱️ | Time/duration |
| 🕐 | Departure time |
| 🏁 | Arrival time |
| 📍 | Stop/station |
| 🏠 | Origin (home/start) |
| 🎯 | Destination |
| ⚠️ | Delay or disruption |
| ✅ | On time |
| 🔄 | Transfer/change |
| 🛤️ | Platform/track |

### Response Structure

**Always include these key elements from the tool output:**

1. **When to leave** - The actual time user needs to start (including walking)
2. **Walking segments** - Distance and time for any walking
3. **Transport departure** - When the bus/train actually leaves
4. **Arrival time** - When user reaches destination
5. **Any delays** - Show deviation from schedule

### Example Response Format

**For a simple direct journey:**
```
🏠 **Leave home at 09:00**

🚶 Walk 450m to Möllevångstorget (5 min)

📍 **Möllevångstorget** → 🎯 **Malmö C**
🚌 Bus 5 departs 09:07 from Möllevångstorget
🏁 Arrives 09:18 at Malmö C

⏱️ Total: 18 min
```

**For a journey with transfer:**
```
🏠 **Leave at 08:45**

🚶 Walk 300m to Västra Hamnen (4 min)

📍 **Västra Hamnen** → 🔄 **Malmö C** → 🎯 **Lund C**

**Leg 1:**
🚌 Bus 2 departs 08:51 [🛤️ Läge A]
🏁 Arrives Malmö C 09:05

🔄 Transfer at Malmö C (6 min)

**Leg 2:**
🚂 Pågatåg departs 09:11 [🛤️ Spår 4]
🏁 Arrives Lund C 09:23

⏱️ Total: 38 min | 🔄 1 change
```

**With delays:**
```
🕐 **Depart 14:30** from Triangeln

🚂 Öresundståg 1042 → København H
⚠️ +8 min delay (expected 14:38 instead of 14:30)
🏁 Arrives ~15:25 (normally 15:17)
```

### Walking Segment Details

**CRITICAL: Always show walking details from the tool output:**

- Distance in meters (from `line.distance`)
- Include walking in the "leave time" calculation
- Show walking at start AND end of journey

Example tool output:
```
→ WALK 450m from Kalendegatan to Möllevångstorget
```

Format as:
```
🚶 Walk 450m to Möllevångstorget (~5 min)
```

Walk time estimate: ~100m per minute (normal walking speed)

### Presenting Multiple Options

When showing journey options, make timing crystal clear:

```
I found 3 options for you:

**Option 1 - Leave now (09:00)** ✅ Recommended
🚶 5 min walk → 🚌 Bus 5 at 09:07 → arrives 09:25
⏱️ Total: 25 min

**Option 2 - Leave in 15m (09:15)**
🚶 5 min walk → 🚌 Bus 5 at 09:22 → arrives 09:40
⏱️ Total: 25 min

**Option 3 - Leave in 30m (09:30)**
🚶 5 min walk → 🚂 Train at 09:37 → arrives 09:48
⏱️ Total: 18 min | Faster but later departure
```

### Time Offset Notation

Use clear notation for departure times:

| Notation | Meaning |
|----------|---------|
| "now" | Immediately |
| "in 15m" | 15 minutes from now |
| "in 1h" | 1 hour from now |
| "at 14:30" | Specific time |

---

## LLM Workflow: How to Plan a Trip

Follow this workflow when a user asks for a trip:

### Step 1: Understand Time Intent

Parse what the user wants:
- **"How do I get to..."** → Travel now
- **"I need to be there at 18:00"** → Arrive mode
- **"Sometime around 3pm"** → Query 14:30, show range
- **"In about an hour"** → Calculate from current time

### Step 2: Search for Both Locations

Search for origin and destination separately:

```bash
./search-location.sh "Malmö C"
./search-location.sh "Emporia"
```

### Step 3: Validate Search Results

**Check each result carefully:**

1. **Exact or close match?** - If the name matches what the user asked for, proceed.

2. **Multiple results returned?** - The script shows up to 10 matches. If the first result isn't clearly correct, ask the user to confirm.

3. **Name significantly different?** - If user asked for "the mall near Hyllie" and result shows "Emporia", confirm with user: "I found Emporia shopping center near Hyllie. Is this correct?"

4. **No results found?** - Try alternative strategies (see below).

### Step 4: Handle Ambiguous or Failed Searches

**When results don't match or are ambiguous, ask clarifying questions:**

```
I searched for "centrum" and found multiple locations:
1. Malmö Centrum (bus stop)
2. Lund Centrum (bus stop)
3. Helsingborg Centrum (bus stop)

Which one did you mean?
```

**When no results are found, try these strategies:**

1. **Try with city name for addresses:**
   ```bash
   # If "Storgatan 10" fails, try:
   ./search-location.sh "Storgatan 10, Malmö"
   ```

2. **Try official station names:**
   ```bash
   # If "Malmö station" fails, try:
   ./search-location.sh "Malmö C"
   ```

3. **Try landmark name only (without city):**
   ```bash
   # If "Emporia, Malmö" fails, try:
   ./search-location.sh "Emporia"
   ```

4. **Use coordinates as last resort:**
   - If you know the approximate location, use `lat#lon` format directly
   - Ask user: "I couldn't find that location. Can you provide the address or coordinates?"

### Step 5: Convert Types for Journey API

The Journey API only accepts:
- `STOP_AREA` - Bus/train stations (use ID directly)
- `LOCATION` - GPS coordinates as `lat#lon`

**If search returns ADDRESS or POI:**
- Use the coordinates from search result
- Format as `lat#lon` with type `LOCATION`

Example:
```bash
# Search returns: ID: 123, Type: ADDRESS, Coordinates: 55.605, 13.003
# Use in journey as:
./journey.sh "55.605#13.003" LOCATION 9021012080000000 STOP_AREA
```

### Step 6: Execute Journey Search

Once you have confirmed IDs/coordinates for both locations:

```bash
./journey.sh <from-id> <from-type> <to-id> <to-type> [datetime] [mode]
```

### Step 7: Format Response with Emojis

Use the emoji guide above to present results clearly. **Always use actual numbers from the tool output - never speculate or estimate.**

---

## Query Formatting Rules

**The search API is sensitive to formatting. Follow these rules:**

### Landmarks and POIs: Name Only

Use the landmark name WITHOUT city name.

```bash
# CORRECT
./search-location.sh "Emporia"
./search-location.sh "Triangeln"
./search-location.sh "Turning Torso"

# WRONG - city name breaks POI search
./search-location.sh "Emporia, Malmö"        # May return wrong location!
./search-location.sh "Triangeln, Malmö"      # Unnecessary, may fail
```

### Street Addresses: Include City

Include city name for better accuracy.

```bash
# CORRECT
./search-location.sh "Kalendegatan 12, Malmö"
./search-location.sh "Storgatan 25, Lund"
./search-location.sh "Drottninggatan 5, Helsingborg"

# RISKY - may be ambiguous
./search-location.sh "Kalendegatan 12"       # Works if unambiguous
```

### Train Stations: Use Official Names

Use "C" suffix for central stations.

```bash
# CORRECT
./search-location.sh "Malmö C"
./search-location.sh "Lund C"
./search-location.sh "Helsingborg C"
./search-location.sh "Malmö Hyllie"
./search-location.sh "Malmö Triangeln"

# WRONG
./search-location.sh "Malmö"                 # Ambiguous!
./search-location.sh "Malmö Central"         # Not official name
./search-location.sh "Lund station"          # Not official name
```

### Copenhagen (Cross-border)

Use Danish names or common alternatives.

```bash
# All work
./search-location.sh "København H"
./search-location.sh "Nørreport"
./search-location.sh "Copenhagen Airport"
./search-location.sh "Köpenhamn"
```

---

## Examples

### Example 1: Travel Now

User: "How do I get from Malmö C to Lund C?"

```bash
./search-location.sh "Malmö C"
./search-location.sh "Lund C"
./journey.sh 9021012080000000 STOP_AREA 9021012080040000 STOP_AREA
```

**Response:**
```
🏠 **Leave now** from Malmö C

📍 **Malmö C** → 🎯 **Lund C**
🚂 Öresundståg 1324 departs 09:04 [🛤️ Spår 2b]
🏁 Arrives 09:16 at Lund C [🛤️ Spår 1]

⏱️ Total: 12 min | ✅ Direct, no changes
```

### Example 2: Address with Walking

User: "I need to go from Kalendegatan 12 in Malmö to Emporia"

```bash
./search-location.sh "Kalendegatan 12, Malmö"
./search-location.sh "Emporia"
./journey.sh "55.595#13.001" LOCATION "55.563#12.973" LOCATION
```

**Response:**
```
🏠 **Leave at 10:05**

🚶 Walk 320m to Möllevångstorget (~3 min)

📍 **Möllevångstorget** → 🎯 **Emporia**
🚌 Bus 32 departs 10:10
🏁 Arrives 10:28 at Emporia

🚶 Walk 150m to destination (~2 min)

⏱️ Total: 25 min
```

### Example 3: Arrive By Time

User: "I need to be at Copenhagen central by 18:00 tomorrow"

```bash
./search-location.sh "Malmö C"
./search-location.sh "København H"
./journey.sh 9021012080000000 STOP_AREA 9921000008600626 STOP_AREA "tomorrow 18:00" arrive
```

**Response:**
```
🎯 **Arrive by 18:00** at København H

📍 **Malmö C** → 🎯 **København H**
🚂 Öresundståg departs **17:21** [🛤️ Spår 1]
🏁 Arrives **17:56** ✅ 4 min buffer

⏱️ Journey: 35 min

💡 Leave Malmö C by 17:21 to arrive on time!
```

### Example 4: Around Time Query

User: "I want to travel to Lund around 15:00"

```bash
# Query 30 min earlier to show options around 15:00
./journey.sh 9021012080000000 STOP_AREA 9021012080040000 STOP_AREA "14:30"
```

**Response:**
```
Options around 15:00 for Malmö C → Lund C:

**Option 1 - Depart 14:34** (in 25m)
🚂 Pågatåg → arrives 14:52
⏱️ 18 min

**Option 2 - Depart 14:49** (in 40m)
🚂 Öresundståg → arrives 15:01
⏱️ 12 min

**Option 3 - Depart 15:04** (in 55m) ✅ Closest to 15:00
🚂 Pågatåg → arrives 15:22
⏱️ 18 min

Which works best for you?
```

### Example 5: Relative Time

User: "I want to leave in about an hour"

```bash
# Current time: 13:00, so query for 14:00
./journey.sh ... "14:00"
```

**Response:**
```
Options departing around 14:00 (in ~1h):

**Leave at 13:55** (in 55m)
🚶 5 min walk → 🚌 Bus 5 at 14:02 → arrives 14:25

**Leave at 14:10** (in 1h 10m)
🚶 5 min walk → 🚂 Train at 14:17 → arrives 14:35

Let me know which one works!
```

### Example 6: Journey with Delays

When tool output shows delays:
```
From: 14:30 Malmö C [+8 min late]
```

**Response:**
```
📍 **Malmö C** → 🎯 **Lund C**
🚂 Öresundståg 1042
⚠️ **Running 8 min late**
🕐 Scheduled: 14:30 → Expected: ~14:38
🏁 Arrives ~14:50 (normally 14:42)
```

---

## When to Ask Clarifying Questions

**Always ask when:**

1. **Search returns no results:**
   - "I couldn't find [location]. Could you provide more details like the full address or nearby landmarks?"

2. **Multiple plausible matches:**
   - "I found several locations matching '[query]': [list]. Which one did you mean?"

3. **Result name very different from query:**
   - "You asked for '[user query]' but the closest match I found is '[result name]'. Is this correct?"

4. **User request is vague:**
   - "From Malmö" - "Which location in Malmö? The central station (Malmö C), or a specific address?"

5. **Cross-border ambiguity:**
   - "Copenhagen" could mean different stations - confirm if they want København H (central), Airport, or another station.

6. **Time is unclear:**
   - "When do you want to travel? Now, or at a specific time?"

---

## DateTime Formats

All times are Swedish local time (CET/CEST).

| Format | Example | Meaning |
|--------|---------|---------|
| _(empty)_ | | Travel now |
| `HH:MM` | `"18:30"` | Today at 18:30 |
| `tomorrow HH:MM` | `"tomorrow 09:00"` | Tomorrow at 09:00 |
| `YYYY-MM-DD HH:MM` | `"2026-01-15 09:00"` | Specific date |

---

## Output Format

### Journey Option (Raw Tool Output)

```
══════════════════════════════════════════════════════════════
OPTION 1: Malmö C → Lund C
══════════════════════════════════════════════════════════════
Date:    2026-01-14
Depart:  09:04
Arrive:  09:16
Changes: 0

LEGS:
  → ORESUND Öresundståg 1324
    From: 09:04 Malmö C [Spår 2b]
    To:   09:16 Lund C [Spår 1]
    Direction: mot Helsingborg C
```

### Transport Types

| Type | Emoji | Description |
|------|-------|-------------|
| `TRAIN` | 🚂 | Pågatåg (regional train) |
| `ORESUND` | 🚂 | Öresundståg (cross-border train) |
| `BUS` | 🚌 | City or regional bus |
| `WALK` | 🚶 | Walking segment |
| `TRAM` | 🚋 | Tram/light rail |
| `METRO` | 🚇 | Copenhagen Metro |
| `FERRY` | ⛴️ | Ferry |

### Status Indicators

| Indicator | Emoji | Meaning |
|-----------|-------|---------|
| _(none)_ | ✅ | On time |
| `[+X min late]` | ⚠️ | Delayed |
| `[-X min early]` | ℹ️ | Running early |
| `[PASSED]` | ❌ | Already departed |
| `AVVIKELSE` | 🚨 | Service disruption |

---

## Error Handling

### "No locations found"

The search returned no results.

**Strategies:**
1. Check spelling (Swedish: å, ä, ö)
2. Try official station names with "C" for central
3. For landmarks, remove city suffix
4. For addresses, add city name
5. Ask user for clarification

### "No journeys found"

No routes available.

**Strategies:**
1. Check if service operates at that hour (late night/early morning limited)
2. Try different departure time
3. Suggest alternative nearby stops

---

## Quick Reference

| Location Type | Search Format | Journey Type |
|--------------|---------------|--------------|
| Train station | `"Malmö C"` | STOP_AREA |
| Bus stop | `"Möllevångstorget"` | STOP_AREA |
| Address | `"Street 12, City"` | Use coords → LOCATION |
| Landmark/POI | `"Emporia"` (no city!) | Use coords → LOCATION |
| Coordinates | `55.605#13.003` | LOCATION |
