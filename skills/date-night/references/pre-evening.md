# Pre-Evening Intelligence — Detailed Reference

Gather and present useful information before a date night: menu preview, dress code, parking, drive time, weather, and dessert spots.

Load config: `CONFIG=$(cat ~/.openclaw/skills/date-night/config.json)`

---

## 1. Menu Preview

### From OpenTable Restaurant Page
```bash
playwright-cli -s=intel open "https://www.opentable.com/r/{slug}" --headed
playwright-cli -s=intel snapshot
playwright-cli -s=intel click {menu-tab-ref}
playwright-cli -s=intel snapshot
```

### From Restaurant Website
```bash
web_search "{restaurant name} {city} menu"
web_fetch "https://restaurant-website.com/menu" --maxChars 5000
```

### Presentation Rules

Apply dietary preferences from config when presenting menus:
- If `dietary` includes `"no alcohol"`: do **not** highlight wine lists, cocktail pairings, bar menus, or happy hour specials. Focus on food, signature dishes, chef specialties.
- If `dietary` includes `"vegetarian"`: highlight plant-based options explicitly.
- If allergies in `dietary`: flag any potential allergen in described dishes.

**Example menu summary:**
> *The restaurant is known for their dry-aged steaks — the bone-in NY strip is a signature. Great sides. Entrées run $45–75.*

---

## 2. Dress Code

### Extract from OpenTable
```bash
playwright-cli -s=intel snapshot
playwright-cli -s=intel mousewheel 0 -500  # scroll to Details section
playwright-cli -s=intel snapshot
# Look for "Dress Code" or "Attire" in snapshot
```

### Extract via Web Search
```bash
web_search "{restaurant name} {city} dress code attire"
```

### Inference by Price Range
| Price | Inferred Dress Code |
|-------|---------------------|
| $$$$ | Business casual to smart casual (minimum) |
| $$$ | Smart casual |
| $$ | Casual — no dress code concern |
| $ | Casual |

### Presentation
> *Dress code: business casual — a button-down and nice pants, or a nice dress.*

---

## 3. Parking & Arrival Info

### Extract from OpenTable / Web
```bash
playwright-cli -s=intel snapshot  # look for "Parking", "Valet", "Transportation"
web_search "{restaurant name} {city} parking valet"
```

### For Event Venues
```bash
web_search "{venue name} parking options"
web_search "{venue name} preferred parking lots"
# Many major venues have pre-pay parking: SpotHero, ParkWhiz
```

### Presentation
> *Parking: valet available ($15). There's also a covered garage one block east.*

---

## 4. Drive Time from Home

Use `config.location` as the origin.

### Calculate
```bash
# Via web search
web_search "drive time from {config.location} to {restaurant address}"

# Via goplaces (if address known)
goplaces search "{restaurant name} {city}" --limit 1 --json 2>/dev/null | \
  jq -r '.[0].formattedAddress' 2>/dev/null || true
```

### "Leave By" Calculation
```
Leave time = Reservation time - Drive time - 15 min buffer
```

Include in brief:
> *It's about {X} minutes from {config.location}. I'd suggest leaving by {time} to have time to park and settle in.*

---

## 5. Weather Check

Check forecast for the evening using the wttr.in service.

```bash
# Quick format: temp, conditions, precip, wind
curl -s "wttr.in/{config.location}?format=%l:+%t+%C+💧%p+💨%w" 2>/dev/null || true

# 3-day summary
curl -s "wttr.in/{config.location}?format=3" 2>/dev/null || true

# URL-encode city: spaces → +, commas → %2C
# Example: "Salt Lake City, UT" → "Salt+Lake+City%2C+UT"
```

### Advisories by Condition

| Condition | Advisory |
|-----------|----------|
| Below freezing | Covered parking recommended; note walking distance |
| Rain / snow | Mention umbrella; valet over open lots |
| 60°F+ clear | Mention patio option if restaurant has one |
| Wind > 15 mph | Skip patio recommendation regardless of temp |
| High AQI (inversion) | Briefly note if severe; shorter outdoor exposure |

### Weather Line in Brief

```
🌡️ **Weather:** ~{temp} and {conditions}. {advisory}
```

**Examples:**
> *🌡️ Weather: 29°F with light snow — bundle up. Covered parking is closest, about a half-block walk.*

> *🌡️ Weather: 67°F and clear — beautiful evening. The patio should be great if you want it.*

> *🌡️ Weather: 42°F, partly cloudy. A jacket will do.*

---

## 6. Pre-Evening Brief Template

Assemble all gathered intel into a clean summary:

```
📋 **Evening Brief: {Event/Restaurant}**
📅 {Day, Date} at {Time} — {details}

🍽️ **Menu highlights:** {signature dishes, price range}
      {any dietary-relevant note}
👔 **Dress code:** {recommendation}
🅿️  **Parking:** {valet/garage/street}
🚗 **Drive time:** ~{X} min from home — leave by {time}
🌡️ **Weather:** ~{temp}, {conditions}. {advisory}
📝 **Note:** {cancellation policy, occasion, anything else}
```

---

## 7. Dessert & After Spots

Suggest an optional extension — keep it light, don't make it feel mandatory.

### Find Options Near Venue / Restaurant

```bash
web_search "dessert near {venue or restaurant address} open late"
web_search "ice cream cafe {city} open after 9pm"

goplaces nearby "{address}" --type bakery --open-now --limit 5 2>/dev/null || true
goplaces search "dessert cafe {city}" --min-rating 4.0 --limit 5 2>/dev/null || true
```

### Check Closing Times First

Only suggest spots that close ≥ 60 minutes after the estimated end of the evening:

```bash
web_search "{spot name} {city} hours"
goplaces search "{name}" --limit 1 --json 2>/dev/null | \
  jq '.[0].currentOpeningHours.weekdayDescriptions' 2>/dev/null || true
```

### Dietary Preferences Apply Here Too

If `dietary` includes `"no alcohol"`: recommend dessert cafes, creameries, bakeries — not cocktail bars or wine bars. If `dietary` includes allergy notes, check menu before recommending.

### How to Present

Frame as optional — one concise sentence:

> "Want to keep the evening going? There's a {spot} about {distance} from the restaurant, open until {time} — great for dessert."

Only surface if:
- Evening ends before 9 PM (enough time)
- User seems to be planning a full evening
- User explicitly asks about after-dinner options

---

## 8. Movie / Event Pre-Show Intel

For evenings that include a movie or event:

```bash
# Find venue details
web_search "{venue name} bag policy entry requirements"
web_search "{venue name} parking options prepay"

# For events: check if there's an opener/support act
web_search "{artist/event} {venue} {date} opener doors time"
```

**Pre-show brief additions:**
```
🎤 **Doors:** {doors open time}
🎭 **Show starts:** {start time} (arrive by {doors time} for best experience)
🎒 **Bag policy:** {clear bag required / small clutch / no restrictions}
🅿️  **Parking:** {venue-specific options; pre-pay if available}
```
