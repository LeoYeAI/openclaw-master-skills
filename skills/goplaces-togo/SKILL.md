---
name: goplaces-togo
description: Ask the user for their Google saved places list, look up each place with goplaces, and recommend the single best one to visit today based on their preferences and visit history.
---

# goplaces-togo

## Goal

Help the user pick one place to visit from their saved Google Places list by fetching live details (rating, hours, reviews) via the `goplaces` CLI, incorporating the user's own notes, their stated cuisine and location preferences, and their visit history — then making a clear, opinionated recommendation.

## Prerequisites

- `goplaces` binary is installed and on PATH.
- `GOOGLE_PLACES_API_KEY` environment variable is set.
- **Google Takeout saved places CSV** — export once from [https://takeout.google.com](https://takeout.google.com):
  1. Click "Deselect all", then check only **"Saved"**
  2. Click "Next step" → "Export once" → "Create export"
  3. Download the zip and find the CSV at `Takeout/Saved/Saved Places.csv`
  4. Give the agent the file path — it will import and remember it automatically
- A local data file at `skills/goplaces-togo/goplaces-visits.json` persists the imported list and visit history (created automatically on first use).

## Data file schema

`skills/goplaces-togo/goplaces-visits.json` is the single source of truth for all persistent state:

```json
{
  "savedList": [
    {
      "name": "string",
      "mapsUrl": "string | null",
      "placeId": "string | null",
      "city": "string | null",
      "userComment": "string | null",
      "addedAt": "YYYY-MM-DD"
    }
  ],
  "places": {
    "<place_id>": {
      "name": "string",
      "city": "string | null",
      "visits": [
        { "date": "YYYY-MM-DD", "time": "HH:MM", "note": "string | null" }
      ]
    }
  }
}
```

- `savedList` — the user's saved places, persisted so they don't have to paste it again.
- `savedList[].city` — normalised city name resolved via the Places API; used to filter by city before scoring.
- `places` — keyed by `place_id`, holds visit history for recording and recency scoring.

## Steps

### 1. Load or ask for the saved list

Read `skills/goplaces-togo/goplaces-visits.json`. Check whether `savedList` exists and has at least one entry.

**If a saved list exists**, show it to the user and ask:

> I have your saved list from last time:
> 1. <name> — <userComment or "(no note)">
> 2. ...
>
> Use this list, or provide a new CSV to replace it? (Press Enter to use the existing list.)

- If the user presses Enter or says "use it" / "yes" / similar affirmation → keep `savedList` as-is and proceed.
- If the user provides a new CSV file path or pastes CSV content → replace `savedList` with the newly parsed entries (see Step 2), write to disk, then proceed.
- If the user says "add" or "update" followed by a new CSV → merge: add new entries, keep existing ones that are not duplicates (match on `name` case-insensitively or `mapsUrl`). Write merged list to disk.

**If no saved list exists**, say exactly:

> I need your Google saved places list. Here's how to get it:
>
> 1. Go to https://takeout.google.com
> 2. Click "Deselect all", then scroll down and check only **"Saved"**
> 3. Click "Next step" → "Export once" → "Create export"
> 4. Download the zip, open it, and find the CSV file inside the **Saved/** folder (e.g. `Saved Places.csv`)
> 5. Share the file path or paste its contents here

Wait for the user to provide the CSV before proceeding to Step 2.

### 2. Parse the CSV and extract user comments

The CSV exported from Google Takeout has this header and format:

```
Title,Note,URL,Tags,Comment
Gochi Cupertino,,https://www.google.com/maps/place/Gochi+Cupertino/data=!4m2!3m1!1s0x808fb5c78e1841e7:0xf8efac3fb5ce0b40,,
Kunjip Tofu,Fine and good for date,https://www.google.com/maps/place/Kunjip+Tofu/data=!4m2!3m1!1s0x808fb10003a9a597:0xe41f61b5ba1b2f19,,
```

For each non-empty data row (skip the header and blank rows):

- `Title` → `name`
- `Note` → `userComment` (use `null` if empty)
- `URL` → `mapsUrl` — store as-is for reference; do **not** attempt to extract a place ID from the URL path, as the hex values in `data=!4m2!3m1!1s<hex>` are Google's internal CID format, not Places API IDs
- `Tags`, `Comment` → ignore for now
- Set `addedAt` to today's date
- Store `{ name, mapsUrl, userComment, addedAt, placeId: null }`

After parsing, write the resulting array to `savedList` in `skills/goplaces-togo/goplaces-visits.json` immediately, before doing any API calls. This ensures the list is never lost even if the session ends early.

### 3. Classify each place by city

For every entry in `savedList` where `city` is `null`, resolve the place name to get its city:

```bash
goplaces resolve "<place name>" --limit 1 --json
```

From the result, extract the city using this priority order:
1. `candidates[0].addressComponents` — find the component with `types` containing `"locality"` → use its `longText`
2. Fall back to the component with `types` containing `"administrative_area_level_2"` → use its `longText`
3. Fall back to parsing the city token from `candidates[0].formattedAddress` (typically the second comma-separated segment, e.g. `"Gochi, Cupertino, CA 95014"` → `"Cupertino"`)
4. If all fail, set `city` to `null` and note the entry as unclassified

Normalise city names to title case (e.g. `"cupertino"` → `"Cupertino"`). Store `placeId` from `candidates[0].place_id` at the same time — no need to re-resolve in Step 4.

After classifying all entries, write the updated `savedList` (with `city` and `placeId` filled in) back to disk.

Show the user a summary grouped by city:

> Found N places across X cities:
> - **Cupertino** (3): Gochi Cupertino, Eilleen's Kitchen, ...
> - **Santa Clara** (2): Pho to Chau 999, ...
> - **Unclassified** (1): Some Place Name

### 4. Ask which city they are in today

Say exactly:

> Which city are you in today? (or press Enter to search all cities)

- If the user names a city → filter `savedList` to entries where `city` matches (case-insensitive). Use only these for scoring. If the city has zero matches, say so and ask again or offer to search all.
- If the user presses Enter or says "all" / "anywhere" → use the full `savedList`.
- Store the chosen city as `currentCity` (or `null` for all) in memory for this session.

### 5. Ask for cuisine and location preferences

Say exactly:

> What cuisine or type of food are you in the mood for today? And do you have a preferred neighbourhood or area? (Press Enter to skip either.)

Wait for the user's response. Parse two optional values:
- `cuisinePreference` — e.g. "Japanese", "Italian", "anything spicy", `null` if skipped.
- `locationPreference` — e.g. "Shibuya", "within 2km of Shinjuku Station", `null` if skipped.

If the user skips both, proceed without preference filtering.

### 6. Resolve any remaining unresolved place IDs

Step 3 already resolved and stored `placeId` for newly imported entries. Only re-run resolve for entries that still have `placeId: null` (e.g. manually added entries):

```bash
goplaces resolve "<place name>" --limit 1 --json
```

Parse the JSON. Take `candidates[0].place_id`. Also backfill `city` if it is still `null`. If the result is empty, mark the entry as unresolvable and skip it (report at the end).

### 7. Fetch details for each place ID

```bash
goplaces details <place_id> --reviews --json
```

Collect the following fields for each place:
- `displayName.text` — human name
- `currentOpeningHours.openNow` — is it open right now?
- `rating` — overall rating (0–5)
- `userRatingCount` — number of reviews
- `priceLevel` — 0 (free) to 4 (very expensive)
- `primaryType` or `types[]` — cuisine/category tags
- `location` — `{ latitude, longitude }` for distance scoring
- `reviews[0].text.text` — top review snippet (first 150 chars)
- `editorialSummary.text` — one-line editorial blurb if present

### 8. Load visit history

The `places` section of `skills/goplaces-togo/goplaces-visits.json` was already read in Step 1. For each place in the working list, look up its `place_id` in `places` and derive:
- `visitCount` — length of the `visits` array (0 if the key is absent).
- `daysSinceLastVisit` — days between today and `visits[last].date` (`null` if never visited).

### 9. Score and rank

Compute a score for each resolved place. All bonus terms are additive.

```
base  = rating * log10(max(userRatingCount, 1))
open  = openNow ? +1.0 : -2.0

# Cuisine preference bonus (apply if cuisinePreference is set)
# Check if place types or editorial summary contain the preference keyword (case-insensitive)
cuisine = cuisineMatch ? +2.0 : 0.0

# Location preference bonus (apply if locationPreference is set)
# Resolve locationPreference to lat/lng via: goplaces resolve "<locationPreference>" --limit 1 --json
# Compute haversine distance in km between place.location and preference location
# distance_km = haversine(place.lat, place.lng, pref.lat, pref.lng)
location = distance_km <= 1  ? +2.0
         : distance_km <= 3  ? +1.0
         : distance_km <= 10 ? +0.0
         :                     -1.0
# If locationPreference is null, location bonus = 0

# User comment sentiment bonus
# If userComment is not null, read it holistically:
#   - Positive signals (e.g. "great", "love", "best", "go often") → +1.5
#   - Negative signals (e.g. "meh", "overrated", "avoid", "disappointing") → -1.5
#   - Conditional signals (e.g. "only on weekdays", "good for lunch") →
#       evaluate against current day/time; match → +0.5, mismatch → -0.5
#   - No clear signal → 0
comment = <sentiment score from userComment>

# Recency penalty — discourage going to the same place too soon
recency = visitCount == 0              ? +0.5   # never visited bonus
        : daysSinceLastVisit <= 7      ? -2.0
        : daysSinceLastVisit <= 30     ? -0.5
        :                                 0.0

score = base + open + cuisine + location + comment + recency
```

Rank places by `score` descending. Exclude unresolvable entries from the ranking but list them at the end.

### 10. Recommend exactly one place

Present the top-ranked place as your recommendation using this format:

---

**Recommended: <Place Name>**

- Open now: Yes / No
- Rating: X.X / 5 (N reviews)
- Price: $ / $$ / $$$ / $$$$ (omit if unavailable)
- Your note: "<userComment>" (omit if null)
- Visits: N times (last: YYYY-MM-DD) / Never visited
- Why: <one or two sentences drawing on editorial summary, top review, user comment, and how it matches their preferences>

```bash
goplaces details <place_id> --reviews
```
*(Run the above to see full hours, phone, and website.)*

---

Then list the remaining resolved places as a ranked table:

| Rank | Place | Rating | Open | Visits | Score |
|------|-------|--------|------|--------|-------|
| 2 | ... | | | | |

Finish with any unresolvable entries: "Could not look up: X, Y — please check the spelling or paste Google Maps URLs."

If only one place was provided, still confirm it looks good (or flag if it is closed, poorly rated, or visited very recently).

### 11. Confirm selection and record the visit

After showing the recommendation, ask:

> Are you going to <Place Name>? Say "yes" to log this visit, or tell me which place from the list you picked instead.

Wait for the user's response.

- If the user confirms a place (by saying yes or naming one), record the visit:
  1. Read `skills/goplaces-togo/goplaces-visits.json` (already loaded; use in-memory copy).
  2. Ensure `places["<place_id>"]` exists; create it with `{ name, visits: [] }` if not.
  3. Append a new visit entry:
     ```json
     { "date": "YYYY-MM-DD", "time": "HH:MM", "note": null }
     ```
     Use today's date and the current local time (24-hour format). Do not touch `savedList`.
  4. Write the full updated object (both `savedList` and `places`) back to `skills/goplaces-togo/goplaces-visits.json`.
  5. Confirm: "Logged your visit to <Place Name> on <date> at <time>. Have a great time!"

- If the user says no or skips, say "No worries — enjoy your day!" and do nothing.

### 12. Handle edge cases

- **No places resolved**: Tell the user none of the entries could be matched and ask them to double-check names or paste Google Maps URLs instead.
- **All places closed**: State that all options appear closed right now, rank by score anyway, and caveat the recommendation.
- **Location resolution fails**: Skip the location bonus for all places and note that the area could not be resolved.
- **API error**: Surface the error message and ask the user to verify `GOOGLE_PLACES_API_KEY`.
- **History file corrupt**: Warn the user, treat both `savedList` and `places` as empty, and do not overwrite until the user provides a list or confirms a visit.
- **User wants to clear the list**: If the user says "clear my list" or "forget my places", set `savedList` to `[]` in `skills/goplaces-togo/goplaces-visits.json` (keep `places` history intact) and confirm: "Your saved list has been cleared. Paste a new list whenever you're ready."
- **User wants to remove one entry**: If the user says "remove <name>", delete the matching entry from `savedList` by name (case-insensitive), write to disk, confirm removal. Leave `places` history for that place_id untouched.
- **City classification fails for some entries**: Proceed normally; list unclassified entries under "Unclassified" in the city summary. If the user picks a city, exclude unclassified entries from that city's pool but offer: "I also have N unclassified places — include them?"
- **User's city has only one place**: Recommend it directly (skip scoring), but flag if it is closed or poorly rated.

## Capture behavior

These phrases can be said at any point — not just during the recommendation flow. Detect the intent and act immediately without requiring the user to be in a specific step.

### Retroactive visit logging

| User says | Action |
|-----------|--------|
| "I went to Nobu last night" | Resolve "Nobu" against `savedList` (or run `goplaces resolve`). Ask: "Got it — what time did you go? (or press Enter to skip)". Log visit with yesterday's date and provided time (or `null`). |
| "We ended up going to that ramen place on Saturday" | Identify the place (clarify if ambiguous). Ask for time, then log with the Saturday date. |
| "Just got back from Trattoria Roma" | Log visit with today's date and current time. |
| "I visited 3 places this week: X, Y, Z" | Log all three sequentially. For each, ask "What day and time for X?" then record. |

### Post-visit feedback

| User says | Action |
|-----------|--------|
| "It was amazing" / "Loved it" | Find the most recently logged place (today or last visit). Set `note` on that visit entry to a positive summary. Update `userComment` in `savedList` entry to reflect the positive sentiment. |
| "It was just okay" / "Nothing special" | Same as above but neutral note. |
| "Disappointing, won't go back" | Log negative note on that visit. Update `userComment` in `savedList` to "disappointing — avoid". This will feed a -1.5 comment penalty in future scoring. |
| "Great for lunch but too loud for dinner" | Log as conditional note. Update `userComment` to "good for lunch, too loud for dinner". Future scoring will match against time-of-day. |
| "The omakase was worth it, go on weekdays" | Update `userComment` in `savedList` to the verbatim advice. Confirm: "Updated your note for <Place>." |

### City browsing

| User says | Action |
|-----------|--------|
| "What cities do I have?" | Group `savedList` by `city` and print each city with the count and names of places in it. |
| "Show me my Tokyo places" | Filter `savedList` to `city == "Tokyo"` and list them with userComment and visit count. |
| "I'm in San Jose today" | Set `currentCity = "San Jose"` for this session, filter the working list accordingly, and jump straight to Step 5. |
| "Show places near Cupertino" | Resolve "Cupertino" to lat/lng, then re-score using location bonus for all places regardless of city. |

### List management

| User says | Action |
|-----------|--------|
| "Add Sukiyabashi Jiro to my list" | Append `{ name: "Sukiyabashi Jiro", mapsUrl: null, placeId: null, userComment: null, addedAt: today }` to `savedList`. Confirm: "Added Sukiyabashi Jiro to your list." |
| "Add Pizza Pilgrims — good for groups" | Parse name + comment from the phrase. Append with `userComment: "good for groups"`, `mapsUrl: null`. |
| "Here's my updated Takeout CSV: <path>" | Re-parse the CSV and merge into `savedList`: add new entries, update `userComment` for existing names, preserve visit history. |
| "Remove Shake Shack from my list" | Delete matching `savedList` entry (case-insensitive). Confirm removal. |
| "Show me my list" | Print all `savedList` entries: index, name, userComment, visit count from `places`. |
| "How many times have I been to Nobu?" | Look up the place in `places`, count `visits`. Reply: "You've been to Nobu 4 times. Last visit: 2025-11-03." |
| "What did I think of Trattoria Roma?" | Find the entry's `userComment` and the `note` fields on its visits. Summarise them. |

### Preference shortcuts

| User says | Action |
|-----------|--------|
| "Surprise me" | Skip Step 3 entirely (no preference). Run full scoring and recommend top result. |
| "Something near me" | Ask "What's your current neighbourhood or landmark?" then use that as `locationPreference`. |
| "I want Japanese, anywhere is fine" | Set `cuisinePreference = "Japanese"`, `locationPreference = null`. Jump straight to scoring. |
| "Same as last time" | Reuse the `cuisinePreference` and `locationPreference` from the previous session if stored; otherwise ask again. Store last-used preferences under `"lastPreferences": { cuisine, location }` in `skills/goplaces-togo/goplaces-visits.json`. |
