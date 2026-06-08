# Movie Ticket Booking — Detailed Reference

Book movie tickets via browser automation using `playwright-cli`.
Covers the major national chains; use `config.preferred_theater` as the default starting point.

Load config: `CONFIG=$(cat ~/.openclaw/skills/date-night/config.json)`

All commands assume PATH is set: `export PATH="$HOME/.npm-global/bin:$PATH"`

---

## ⚠️ Payment Warning

Always:
1. Show the **full all-in price** (tickets + booking fees + taxes) before proceeding
2. **Explicitly confirm with user** before clicking any "Purchase" / "Place Order" button
3. Never auto-complete a ticket purchase

---

## Finding Your Local Theater

Use `config.preferred_theater` and `config.zip` to determine where to start:

```bash
ZIP=$(cat ~/.openclaw/skills/date-night/config.json | jq -r '.zip')
PREF=$(cat ~/.openclaw/skills/date-night/config.json | jq -r '.preferred_theater // "none"')
```

If no preference set:
```bash
web_search "movie theaters near {config.zip} showtimes"
playwright-cli -s=fd open "https://www.fandango.com/movies-in-theaters?location=${ZIP}" --headed
playwright-cli -s=fd snapshot
```

Fandango is the best aggregator for finding all theaters near a zip code.

---

## Common Theater Chains

### Megaplex Theatres (Utah / Nevada)
- **Website:** megaplex.com
- **Loyalty:** MegaClub (free, earns free tickets)
- **Guest checkout:** ✅ Available; account recommended for points
- **Theater URL pattern:** `megaplex.com/{theater-slug}` (e.g., `megaplex.com/legacycrossing`)
- **Find locations:** `megaplex.com/theatres/locations`

```bash
playwright-cli -s=movies open "https://megaplex.com/{theater-slug}" --headed
playwright-cli -s=movies snapshot
# Click movie → click showtime → seat map → checkout
```

### AMC Theatres (National)
- **Website:** amctheatres.com
- **Loyalty:** AMC Stubs (free) / A-List ($25/mo, 3 movies/week)
- **Guest checkout:** Limited — account preferred for seat selection
- **Showtimes:** `amctheatres.com/theatres/{theater-slug}/showtimes`
- **Find nearby:** `amctheatres.com/movies` → select theater

```bash
playwright-cli -s=amc open "https://www.amctheatres.com/movies" --headed
playwright-cli -s=amc snapshot
playwright-cli -s=amc click {movie-ref}
playwright-cli -s=amc click {showtime-ref}
# Ticket type selection (adult/child/senior) → seat map → checkout
```

AMC charges a per-ticket online booking fee (~$1.50–2.50/ticket). Always include in price shown to user.

### Cinemark (National)
- **Website:** cinemark.com
- **Loyalty:** Movie Club ($8.99/mo, 1 ticket/month)
- **Guest checkout:** ✅ Best guest checkout of major chains
- **Showtimes:** Theater finder on homepage → select by zip

```bash
playwright-cli -s=cin open "https://www.cinemark.com" --headed
playwright-cli -s=cin snapshot
# Theater search by zip → movie → showtime → ticket count → seat map → guest checkout
playwright-cli -s=cin fill {email-ref} "{config.user_email}"
playwright-cli -s=cin click {guest-checkout-ref}
```

### Regal Cinemas (National)
- **Website:** regmovies.com
- **Loyalty:** Regal Crown Club (free) / Unlimited ($20+/mo)
- **Guest checkout:** ✅ Available
- **Showtimes near zip:** `regmovies.com/movies/now-playing?distance=25&zip={zip}`

```bash
playwright-cli -s=reg open "https://www.regmovies.com/movies/now-playing?distance=25&zip={config.zip}" --headed
playwright-cli -s=reg snapshot
playwright-cli -s=reg click {movie-ref}
playwright-cli -s=reg click {showtime-ref}
# Seat selection → checkout
```

---

## Generic Booking Flow

Works for all chains with minor variation:

**Step 1: Navigate to theater / showtime**
```bash
playwright-cli -s=movies open "{theater-url}" --headed
playwright-cli -s=movies snapshot
```

**Step 2: Select movie and showtime**
```bash
playwright-cli -s=movies click {movie-ref}
playwright-cli -s=movies snapshot
playwright-cli -s=movies click {showtime-ref}
playwright-cli -s=movies snapshot
```

**Step 3: Seat selection (interactive map)**
```bash
playwright-cli -s=movies snapshot
# Seat map: green=available, gray=taken, yellow=selected
playwright-cli -s=movies click {seat-ref}     # first seat
playwright-cli -s=movies click {seat-ref-2}   # second seat (party of 2)
playwright-cli -s=movies snapshot             # verify selection
playwright-cli -s=movies click {continue-ref}
```

**Seat map troubleshooting:**
- SVG/canvas seats may not expose aria refs — try coordinate clicking:
  ```bash
  playwright-cli mousemove {x} {y}
  playwright-cli mousedown
  playwright-cli mouseup
  ```
- If map doesn't render: `playwright-cli screenshot` to diagnose
- Query seat count: `playwright-cli eval "document.querySelectorAll('[data-seat-status=available]').length"`

**Step 4: ⚠️ STOP — Confirm price before checkout**

```bash
playwright-cli -s=movies snapshot
# Capture: ticket count, price per ticket, booking fee, tax, total
```

Present to user:
> "2 tickets to {Movie} on {Date} at {Time}, {Theater}. Total: ${amount} (includes ${fee} booking fee). Shall I proceed?"

**Step 5: Complete checkout (after approval)**
```bash
playwright-cli -s=movies fill {email-ref} "{config.user_email}"
playwright-cli -s=movies click {place-order-ref}
playwright-cli -s=movies snapshot
# Capture confirmation number
```

---

## Seat Selection Guide

| Location | Best For |
|----------|----------|
| Center, rows 7–12 of ~20 | Ideal date night — balanced view, good audio |
| Upper-center | Premium formats (IMAX/PLF) — avoid front rows |
| Aisle | Good for restroom access |
| Row 1–3 | Avoid — neck strain, especially in IMAX |

**For a date night:** Center-middle, slightly upper. Avoid splitting into separated seats.

---

## Post-Purchase Actions

1. **Calendar:**
```bash
{config.calendar_tool} calendar create primary \
  --summary "{Movie} @ {Theater}" \
  --from "{datetime}" \
  --to "{datetime + runtime + 30min}" \
  --location "{theater name and address}" \
  --description "Seats: {section/row/numbers}\nConfirmation: {num}\nFormat: {standard/IMAX}" \
  --reminder "popup:2h"
```

2. **Partner notification** (draft → approve → send via `config.notify_channel`)

3. **Childcare prompt** (if `config.has_children: true` — mandatory):
> "Do you have childcare sorted for that evening? {N} kid(s) to account for."

4. **Offer dinner near theater:**
> "Want me to find a restaurant near {Theater} for before the movie?"
