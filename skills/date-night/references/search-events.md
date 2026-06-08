# Finding Events — Detailed Reference

How to discover concerts, sports, comedy, theater, and festivals near you.

Load config: `CONFIG=$(cat ~/.openclaw/skills/date-night/config.json)`

---

## Quick Discovery

### Web Search (Fastest)
```bash
web_search "concerts near {config.location} {month} {year}"
web_search "events near {config.zip} this weekend"
web_search "comedy shows near {config.location} 2026"
web_search "Broadway shows {config.location} 2026 season"
```

### SeatGeek Browse (Best UX for Discovery)
```bash
playwright-cli -s=sg open "https://seatgeek.com/{config.city}-tickets" --headed
playwright-cli -s=sg snapshot
# Filter by: category (Concerts, Sports, Theater, Comedy), date range, price
```

### Ticketmaster Browse
```bash
playwright-cli -s=tm open "https://www.ticketmaster.com/{config.city}-tickets" --headed
playwright-cli -s=tm snapshot
```

---

## By Category

### Concerts / Music
SeatGeek → Concerts category in your city. Or:
```bash
playwright-cli -s=sg open "https://seatgeek.com/concerts/{config.city}-tickets" --headed
web_search "{artist name} {config.location} {year} tour dates"
```

### Sports
```bash
# General
web_search "sports events near {config.location} this month"
# Specific team schedule
web_search "{team name} home games {month} {year} schedule"
playwright-cli -s=tm open "https://www.ticketmaster.com/{team-slug}/artist/{id}" --headed
```

Find your local teams: `web_search "professional sports teams near {config.location}"`

### Comedy
```bash
web_search "comedy shows {config.location} 2026"
web_search "comedy clubs near {config.zip}"
# Many local comedy clubs sell tickets directly on their website
playwright-cli -s=comedy open "{local-comedy-club-url}" --headed
```

### Broadway / Touring Shows
```bash
web_search "Broadway touring shows {config.location} 2026 season"
web_search "{show name} touring schedule {config.location}"
# Check your city's main performing arts center
```

### Festivals / Outdoor Events
```bash
web_search "festivals near {config.location} {season} {year}"
web_search "outdoor events {config.city} {month} {year}"
```

---

## Date-Range Search

When looking for something on a specific date or weekend:

```bash
# SeatGeek with date filter
playwright-cli -s=sg open "https://seatgeek.com/{config.city}-tickets" --headed
playwright-cli -s=sg snapshot
# Apply date filter via UI: click date picker, set range
playwright-cli -s=sg click {date-filter-ref}
playwright-cli -s=sg click {start-date-ref}
playwright-cli -s=sg click {end-date-ref}
playwright-cli -s=sg click {apply-ref}
playwright-cli -s=sg snapshot

# Web fallback
web_search "events {config.location} {specific date}"
```

---

## Cross-Platform Price Check

```bash
export PATH="$HOME/.npm-global/bin:$PATH"
EVENT="{event name}"
CITY="{config.location}"

playwright-cli -s=sg open "https://seatgeek.com/search?q=${EVENT}&location=${CITY}" --headed &
playwright-cli -s=tm open "https://www.ticketmaster.com/search?q=${EVENT}" --headed &
playwright-cli -s=sh open "https://www.stubhub.com/search?q=${EVENT}+${CITY}" --headed &
wait

playwright-cli -s=sg snapshot
playwright-cli -s=tm snapshot
playwright-cli -s=sh snapshot
```

See [event-tickets.md](event-tickets.md) for the full comparison presentation format.

---

## Local / Niche Ticketing

Some smaller venues sell tickets directly. Find them:

```bash
web_search "{venue name} {city} tickets buy"
playwright-cli -s=venue open "{venue-website}" --headed
playwright-cli -s=venue snapshot
```

For local venues, skip the major platforms and book direct — lower fees, often easier checkout.

---

## Event Discovery Output Format

```
🎵 **Events Near {config.location} — {Month Year}**

1. 🎤 **{Artist / Show}**
   📅 {Date}, {Time}
   📍 {Venue} (~{drive time} from home)
   💰 From ${lowest} all-in | SeatGeek Deal Score: {N}/100
   🔗 Cheapest on {platform}

2. 🏀 **{Team} vs. {Opponent}**
   📅 {Date}, {Time}
   📍 {Arena} (~{drive time} from home)
   💰 From ${price} on Ticketmaster
```

**Notes:**
- Always show drive time from `config.location`
- Show all-in price when available
- Flag high-demand events: *"This one is moving fast — prices may increase"*
- Apply dietary preferences: if `"no alcohol"`, present alcohol-centric events neutrally (brewfests, wine events) — let user decide

---

## Plan Around an Event (Full Date Night Pattern)

```
1. Find event → compare prices → confirm with user → purchase tickets
2. Note: venue address + show start time
3. Search restaurants within 0.5 mi of venue, open for dinner
4. Calculate dinner window: show start - 1.5h = dinner end time
5. Suggest 2-3 dinner options with OpenTable availability
6. Book dinner (approval required)
7. Weather check for that evening
8. Calculate timeline: leave home → dinner → venue
9. Add both events to calendar
10. Draft partner notification → send with approval
11. Childcare prompt if has_children
12. Budget estimate: dinner + tickets + babysitter
13. Optional: dessert spot near venue for after
```
