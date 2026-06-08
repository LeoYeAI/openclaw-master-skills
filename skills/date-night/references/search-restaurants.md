# Restaurant Search — Detailed Reference

How to find and evaluate restaurants by name, cuisine, location, or occasion.

Load config: `CONFIG=$(cat ~/.openclaw/skills/date-night/config.json)`

**Dietary preferences:** Apply `config.dietary` to all searches and recommendations. If `"no alcohol"` is set, never highlight wine lists, cocktail programs, or bar features.

---

## Method A: Web Search

```bash
# General discovery
web_search "best Italian restaurants {config.location} 2026"
web_search "romantic dinner restaurants {config.location} date night"
web_search "fine dining {config.location} OpenTable available"

# Find OpenTable slug
web_search "{restaurant name} {city} OpenTable"
# → URL gives slug: opentable.com/r/{slug}

# Find platform
web_search "{restaurant name} {city} reservations"
# → Shows whether it's OpenTable, Resy, Yelp, or phone-only
```

---

## Method B: Google Places (goplaces CLI)

```bash
# Text search
goplaces search "Italian restaurants {config.location}" --type restaurant --limit 5

# Filter by rating
goplaces search "fine dining {config.location}" --type restaurant --min-rating 4.5 --limit 5

# Filter by price level (1=cheap, 2=moderate, 3=expensive, 4=very expensive)
goplaces search "dinner {config.location}" --type restaurant --price-level 3 --price-level 4 --limit 5

# Nearby a location
goplaces nearby "{config.location}" --type restaurant --open-now --limit 10

# Full details for a specific restaurant
goplaces search "{restaurant name} {city}" --limit 1 --json | jq '.[0]' 2>/dev/null || true
```

---

## Method C: OpenTable Search URL

```
https://www.opentable.com/s?term={query}&covers={N}&dateTime={YYYY-MM-DDTHH:MM}&metroId={metro_id}
```

Metro IDs: NYC=1, LA=4, Chicago=5, Dallas=9, SF=13, SLC=72, Denver=6, Seattle=15, Boston=2, Miami=29.

```bash
playwright-cli -s=search open "https://www.opentable.com/s?term=Italian&covers=2&dateTime=2026-03-07T18:30&metroId={metro}" --headed
playwright-cli -s=search snapshot
```

---

## Method D: Resy Browse

```bash
# Browse all Resy restaurants in a city
playwright-cli -s=resy open "https://resy.com/cities/{city-slug}" --headed
playwright-cli -s=resy snapshot

# Search
playwright-cli -s=resy open "https://resy.com/cities/{city-slug}/search?query={term}" --headed
```

---

## Building a Recommendation

### Questions to Consider

1. **Cuisine preference?** (Italian, steak, sushi, American, Mexican, etc.)
2. **Occasion?** (Casual date, anniversary, birthday, celebration)
3. **Budget?** (Casual, upscale casual, fine dining)
4. **Location?** (Downtown, near a theater/venue, near home)
5. **Date / time?** (Check availability before recommending)

### Review Aggregation

Pull from multiple sources for a confident recommendation:

| Source | Tool | Notes |
|--------|------|-------|
| OpenTable | playwright snapshot or web_fetch | Verified diners — most reliable |
| Google | `goplaces details` | High volume |
| Yelp | `web_search` | Good signal, can be noisy |

```bash
# Google rating
goplaces search "{restaurant name} {city}" --limit 1 --json 2>/dev/null | \
  jq -r '.[] | "\(.name): \(.rating)/5 (\(.userRatingCount) reviews)"' 2>/dev/null || true

# OpenTable rating (from page snapshot or web_fetch)
web_fetch "https://www.opentable.com/r/{slug}" --maxChars 2000 2>/dev/null | \
  grep -i "rating\|reviews" | head -3 || true

# Yelp (web search)
web_search "{restaurant name} {city} Yelp rating reviews"
```

**Consolidated display:**
```
⭐ {Restaurant}: 4.9 OpenTable (813) · 4.6 Google (1.2K) · 4.5 Yelp (213)
```

**Weighting:** Prioritize review count. A 4.7 with 500 reviews beats a 4.9 with 12. If Yelp is significantly lower, flag it: *"Yelp is more mixed at 3.8 — worth checking recent reviews."*

---

## Recommendation Format

Present 2–4 options max (decision fatigue above 4):

```
🍽️ **{Restaurant Name}** — {Cuisine}
📍 {Neighborhood}, {City}
⭐ {rating} OpenTable ({N} reviews) · {rating} Google ({N})
💰 {$-$$$$} (~${est}/person before tip)
🎯 Why it fits: {one-sentence reason}
📅 Available: {times on target date}
```

**Include:**
- Signature dishes, food highlights
- Ambiance / atmosphere
- Dress code
- Parking availability

**Apply dietary filter:** If `dietary` contains `"no alcohol"`, omit wine lists, cocktail highlights, and bar descriptions entirely. If vegetarian, note plant-based options.

---

## Near-Venue Search

When the user wants dinner close to an event venue:

```bash
# Get venue address first
web_search "{venue name} {city} address"

# Find nearby restaurants
goplaces nearby "{venue address}" --type restaurant --limit 10 2>/dev/null || true
web_search "restaurants near {venue name} {city} open for dinner"
```

Filter by: closing time (must be open 2–3 hrs before show), walking distance (ideally < 0.5 mi from venue), price range from config.

---

## Past Dining History (Anti-Repeat)

Before recommending, check history to avoid obvious repeats:

```bash
cat ~/.openclaw/skills/date-night/history.jsonl 2>/dev/null | \
  jq -r '.restaurant' 2>/dev/null | sort -u || true
```

Then:
- Exclude recently visited restaurants (last 60 days)
- Suggest revisiting high-rated restaurants from history
- Track cuisine gaps: "You haven't tried Thai yet"
