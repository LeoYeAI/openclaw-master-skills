# Resy Booking Flow — Detailed Reference

Step-by-step browser automation for booking on Resy using `playwright-cli`.

Before starting, load config: `cat ~/.openclaw/skills/date-night/config.json`

All commands assume PATH is set: `export PATH="$HOME/.npm-global/bin:$PATH"`

---

## Key Differences from OpenTable

| Aspect | OpenTable | Resy |
|--------|-----------|------|
| Guest checkout | ✅ Yes | ❌ No — account required |
| Auth method | Phone verification per booking | Login (email+password or phone+SMS) |
| URL structure | `/r/{slug}` | `/cities/{city}/{slug}` |
| Availability widget | Modal popup | Inline on restaurant page |
| Deposit / prepayment | Rare | Common at premium restaurants |
| Modification | Direct | Cancel + rebook only |

## Important: Resy Requires Authentication

Resy **requires a user account** to complete a booking. Options:

1. **Has Resy account** → login and proceed
2. **No account** → create one, or suggest OpenTable instead
3. **Saved auth state** → load to skip login

```bash
playwright-cli state-load ~/.openclaw/skills/date-night/state/resy-auth.json 2>/dev/null
```

---

## 1. Restaurant Page URL

```
https://resy.com/cities/{city-slug}/{restaurant-slug}
```

City slug format: `{city}-{state-abbrev}` (lowercase, hyphenated). Examples:
- `salt-lake-city-ut`, `new-york-ny`, `los-angeles-ca`, `chicago-il`

Search: `https://resy.com/cities/{city-slug}/search?query={name}`

## 2. Open & Initial Snapshot

```bash
playwright-cli -s=resy open "https://resy.com/cities/{city-slug}/{restaurant-slug}" --headed
playwright-cli -s=resy snapshot
```

Page shows: restaurant info, inline reservation widget (date picker, party size, time slots).

## 3. Set Reservation Parameters

### Party Size
```bash
playwright-cli -s=resy click {party-size-ref}
playwright-cli -s=resy snapshot
playwright-cli -s=resy click {size-option-ref}
```

### Date Selection
```bash
playwright-cli -s=resy click {date-picker-ref}
playwright-cli -s=resy snapshot
playwright-cli -s=resy click {next-month-ref}  # if needed
playwright-cli -s=resy click {date-ref}
```

### Time / Seating Type
```bash
playwright-cli -s=resy snapshot
# Each button shows time + seating type
# Prefer: Dining Room, Patio, Chef's Table
# Avoid: Bar, Lounge (unless clearly food-focused)
# Apply dietary config: if no alcohol preference, avoid bar-adjacent seating
playwright-cli -s=resy click {time-slot-ref}
```

## 4. Authentication

Clicking a time slot triggers the auth check if not logged in.

### Email + Password Login
```bash
playwright-cli -s=resy fill {email-ref} "{config.user_email}"
playwright-cli -s=resy fill {password-ref} "{user_resy_password}"  # ask user
playwright-cli -s=resy click {login-button-ref}
```

### Phone + SMS Login
```bash
playwright-cli -s=resy fill {phone-ref} "{config.user_phone}"
playwright-cli -s=resy click {send-code-ref}
sleep 5
# Find Resy SMS code — see sms-codes.md for discovering Resy chat ID
playwright-cli -s=resy fill {code-ref} "{code}"
# Or use press if code field is in iframe:
playwright-cli -s=resy press {d}  # each digit
```

### Save Auth State After Login
```bash
mkdir -p ~/.openclaw/skills/date-night/state
playwright-cli -s=resy state-save ~/.openclaw/skills/date-night/state/resy-auth.json
```

## 5. Confirm Reservation

After authentication:
```bash
playwright-cli -s=resy snapshot
playwright-cli -s=resy fill {special-requests-ref} "{dietary note or seating preference}"
playwright-cli -s=resy click {confirm-button-ref}
```

⚠️ **Deposit / prepayment:** Some Resy restaurants require a deposit or full prepayment. If payment form appears — **STOP**. Show total to user, get explicit approval before entering any payment info.

## 6. Confirmation Page

```bash
playwright-cli -s=resy snapshot
```

Capture: restaurant, date, time, party, confirmation number, cancellation policy deadline.

**Always note the cancellation deadline** to the user:
> "This reservation has a 48-hour cancellation policy. You'll need to cancel by {datetime} to avoid a fee."

---

## Resy Quirks

- **SPA (Angular):** Pages take longer to load/stabilize. Snapshot may return sparse content initially — wait and retry.
- **Seating types:** Multiple options per time slot; always choose Dining Room over Bar/Lounge.
- **No modification:** To change details, cancel + rebook. Warn user about resale risk at popular restaurants.
- **Cancellation fees:** Many Resy restaurants charge $25–100+/person for no-shows. Always communicate this.

## Resy SMS Discovery

Resy's SMS sender is different from OpenTable's. On first use:
```bash
# After triggering Resy SMS, search recent messages broadly
imsg history --limit 10 2>/dev/null | grep -i "resy\|verification\|code" || true
# Note the chat ID once found, add to sms-codes.md
```
