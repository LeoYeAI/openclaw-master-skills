# Event Ticket Booking — Detailed Reference

Book concert, sports, comedy, and theater tickets via browser automation.
Covers SeatGeek (recommended), Ticketmaster, and StubHub.

Load config: `CONFIG=$(cat ~/.openclaw/skills/date-night/config.json)`

All commands assume PATH is set: `export PATH="$HOME/.npm-global/bin:$PATH"`

---

## ⚠️ Payment Warning

Event tickets are typically non-refundable. Always:
1. Show the **all-in price** (face value + service fees + facility charges + order processing) before any action
2. **Explicitly confirm with user** before clicking any "Purchase" button
3. Communicate clearly: *"Event tickets are usually non-refundable. Just confirming you want to proceed."*

---

## Platform Overview

| Platform | Type | Best For | Bot Protection | Guest Checkout |
|----------|------|----------|----------------|----------------|
| SeatGeek | Aggregator + resale | Price discovery, Deal Scores | 🟢 Low | ✅ Yes |
| Ticketmaster | Primary ticketer | Official tickets, major venues | 🔴 Very High | ✅ Limited |
| StubHub | Resale only | Sold-out events, last-minute | 🟡 Medium | ✅ Yes |

**Recommended flow:** Start SeatGeek → compare Ticketmaster + StubHub → purchase best option.

---

## SeatGeek (Start Here)

**Website:** seatgeek.com | **Type:** Aggregator + resale

### URL Patterns
```
# City events
https://seatgeek.com/{city-name}-tickets
https://seatgeek.com/venues/{city-name}/tickets

# Search
https://seatgeek.com/search?q={query}&location={city}%2C+{state}

# Performer
https://seatgeek.com/{performer-slug}-tickets

# Venue
https://seatgeek.com/venues/{venue-slug}/tickets
```

### Booking Flow
```bash
playwright-cli -s=sg open "https://seatgeek.com/search?q={event}&location={config.location}" --headed
playwright-cli -s=sg snapshot
playwright-cli -s=sg click {event-ref}
playwright-cli -s=sg snapshot

# Browse venue map — click section for prices
playwright-cli -s=sg click {section-ref}
playwright-cli -s=sg snapshot
# See: row, seats, price/ticket, Deal Score, view-from-seat (sometimes)

playwright-cli -s=sg click {ticket-listing-ref}
playwright-cli -s=sg snapshot
# ⚠️ STOP — show all-in total (SeatGeek shows fees upfront)
```

After approval:
```bash
playwright-cli -s=sg click {checkout-ref}
playwright-cli -s=sg snapshot
playwright-cli -s=sg fill {email-ref} "{config.user_email}"
playwright-cli -s=sg click {continue-as-guest-ref}
# Stop at payment — wait for user's authorization
```

**Deal Score:** SeatGeek's 1–100 value rating. 70+ = good deal, 90+ = exceptional. Mention it when selecting.

**Fees:** SeatGeek shows all-in prices by default — what you see is what you pay.

---

## Ticketmaster

**Website:** ticketmaster.com | **Type:** Primary ticketer

### ⚠️ Honest Limitations

Ticketmaster actively fights automation:
- **Queue system:** Major events place users in a virtual waiting room; automation gets blocked or deprioritized
- **Verified Fan:** Pre-registration + unique access codes for high-demand acts — cannot automate
- **CAPTCHA:** Frequent, especially on rapid interactions — requires manual solving
- **Fingerprinting:** Detects headless browsers, unusual click patterns, rapid navigation
- **Session timeouts:** Ticket holds expire in ~8–10 minutes

**Realistic expectations:**
- ✅ Works: browsing events, checking prices, event discovery
- ⚠️ Difficult: seat selection for popular events (queue/CAPTCHA)
- ❌ Not reliable: high-demand presales, Verified Fan sales

**When TM automation stalls:** Offer to do the work in headed mode while user monitors, or give user the direct event URL to complete manually.

### URL Patterns
```
https://www.ticketmaster.com/search?q={query}
https://www.ticketmaster.com/{city}-tickets
https://www.ticketmaster.com/discover/concerts/{state}
https://www.ticketmaster.com/{artist-slug}/artist/{id}
https://www.ticketmaster.com/{venue-slug}/venue/{id}
https://www.ticketmaster.com/event/{event-id}
```

### Booking Flow (When Accessible)
```bash
playwright-cli -s=tm open "https://www.ticketmaster.com/search?q={event}" --headed
# Wait 3+ seconds for SPA to load
playwright-cli -s=tm snapshot
playwright-cli -s=tm click {event-ref}
playwright-cli -s=tm snapshot

# Check for queue
# If queue appears: STOP. Notify user. Provide event URL.
# If no queue: proceed
playwright-cli -s=tm click {section-ref}
playwright-cli -s=tm snapshot
playwright-cli -s=tm click {add-to-cart-ref}
playwright-cli -s=tm snapshot

# ⚠️ STOP — show price (TM fees typically +25-35% of face value)
# Report: face value + service fee + facility charge + order processing = total
```

**Fees:** Ticketmaster fees are notoriously high (25–35% above face value). Always report the all-in total before user approves.

**Upsells:** TM will offer ticket insurance (~$5–15) and mobile wallet. Ask user if they want these.

---

## StubHub

**Website:** stubhub.com | **Type:** Resale marketplace

### URL Patterns
```
https://www.stubhub.com/search?q={query}
https://www.stubhub.com/{city}-tickets/
https://www.stubhub.com/concert-tickets/
https://www.stubhub.com/sports-tickets/
https://www.stubhub.com/venue/{venue-slug}/events
```

### Booking Flow
```bash
playwright-cli -s=sh open "https://www.stubhub.com/search?q={event}+{city}" --headed
playwright-cli -s=sh snapshot
playwright-cli -s=sh click {event-ref}
playwright-cli -s=sh snapshot

# Table of listings: section, row, quantity, price
# Sort by price or "Best Value"
playwright-cli -s=sh click {sort-ref}
playwright-cli -s=sh snapshot
playwright-cli -s=sh click {listing-ref}
playwright-cli -s=sh snapshot

# ⚠️ STOP — show full price (StubHub adds ~10-15% buyer premium at checkout)
# Enable "all-in pricing" toggle if available to see true total upfront
```

**Key caveats for resale:**
- Prices fluctuate by the hour — note this to user
- Buyer premium is ~10–15% on top of listing price
- FanProtect guarantee: if tickets are invalid, StubHub provides replacement or refund
- Delivery: most are instant mobile transfer; some seller transfers take hours

---

## Cross-Platform Price Comparison

```bash
export PATH="$HOME/.npm-global/bin:$PATH"
EVENT="{event name}"
LOCATION="{config.location}"

playwright-cli -s=sg open "https://seatgeek.com/search?q=${EVENT}&location=${LOCATION}" --headed &
playwright-cli -s=tm open "https://www.ticketmaster.com/search?q=${EVENT}" --headed &
playwright-cli -s=sh open "https://www.stubhub.com/search?q=${EVENT}+${LOCATION}" --headed &
wait

playwright-cli -s=sg snapshot
playwright-cli -s=tm snapshot
playwright-cli -s=sh snapshot
```

**Comparison output:**
```
💰 **{Event} — Ticket Price Comparison**
📅 {Date} @ {Venue}

🟢 SeatGeek (aggregator)
   Best: ${price}/ticket all-in | Deal Score: {N}/100

🔵 Ticketmaster (official)
   Face: ${price} + ${fees} in fees = ${total}/ticket
   {Note any queue or availability issues}

🟠 StubHub (resale)
   Lowest: ${price} + ~15% premium = ${total}/ticket

📊 Recommendation: {platform} because {reason}
```

---

## Post-Purchase Actions

1. **Calendar:**
```bash
{config.calendar_tool} calendar create primary \
  --summary "{Event} @ {Venue}" \
  --from "{datetime}" \
  --to "{datetime + estimated duration}" \
  --location "{venue address}" \
  --description "Section: {section}, Row: {row}\nConfirmation: {num}\nPlatform: {platform}\nAll-in paid: ${total}" \
  --reminder "popup:3h" --reminder "popup:1d"
```

2. **Partner notification** (draft → approve → send via `config.notify_channel`)

3. **Childcare prompt** (if `has_children` — mandatory, every time)

4. **Offer pre-show dinner:**
> "Want me to find a restaurant near {Venue} for pre-show dinner? The show starts at {time}, so dinner around {time minus 2.5h} would work well."

5. **Parking note:**
   - Search `web_search "{venue name} parking options prepay"` for venue-specific parking
   - SpotHero and ParkWhiz offer prepay parking near many major venues
