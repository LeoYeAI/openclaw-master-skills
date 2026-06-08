# OpenTable Booking Flow — Detailed Reference

Step-by-step browser automation for booking on OpenTable using `playwright-cli`.

Before starting, load config: `cat ~/.openclaw/skills/date-night/config.json`

All commands assume PATH is set: `export PATH="$HOME/.npm-global/bin:$PATH"`

---

## 1. Restaurant Page URL

```
https://www.opentable.com/r/{slug}?covers={party_size}&dateTime={YYYY-MM-DDTHH:MM}
```

**Finding the slug:** Search `https://www.opentable.com/s?term=RESTAURANT+NAME` or web search `site:opentable.com "{restaurant name}" "{city}"`.

## 2. Open & Initial Snapshot

```bash
playwright-cli -s=reservation open "https://www.opentable.com/r/{slug}?covers={N}&dateTime={YYYY-MM-DDTHH:MM}" --headed
playwright-cli -s=reservation snapshot
```

Look for: time slot buttons (pre-filled), "Find a time" / "View full availability" button, or "No availability" message.

## 3. Availability Modal

```bash
playwright-cli -s=reservation click {availability-button-ref}
playwright-cli -s=reservation snapshot
```

Shows: calendar, time slot grid once a date is selected, party size selector.

## 4. Date Selection

```bash
playwright-cli -s=reservation snapshot
# If target month not visible:
playwright-cli -s=reservation click {next-month-arrow-ref}
playwright-cli -s=reservation snapshot
playwright-cli -s=reservation click {date-ref}
```

## 5. Time Selection

Time slots render as `<a>` links, not buttons:

```bash
playwright-cli -s=reservation snapshot
playwright-cli -s=reservation click {time-ref}
```

If exact time unavailable: snapshot shows all available times. Pick nearest, **confirm with user before proceeding**.

## 6. Checkout — Fill Guest Details

```bash
playwright-cli -s=reservation snapshot
playwright-cli -s=reservation fill {phone-ref} "{config.user_phone}"
playwright-cli -s=reservation fill {email-ref} "{config.user_email}"
playwright-cli -s=reservation fill {first-name-ref} "{config.first_name}"
playwright-cli -s=reservation fill {last-name-ref} "{config.last_name}"
```

`fill` handles React controlled inputs natively.

**Dietary preferences:** If config has dietary restrictions, fill the Special Requests field:
```bash
playwright-cli -s=reservation fill {special-requests-ref} "{dietary-note}"
```

## 7. Occasion & Special Requests

**Occasion dropdown** (React custom — use click, not select):
```bash
playwright-cli -s=reservation click {occasion-dropdown-ref}
playwright-cli -s=reservation snapshot
playwright-cli -s=reservation click {option-ref}   # "Date Night", "Anniversary", etc.
```

**Special requests textarea:**
```bash
playwright-cli -s=reservation fill {special-requests-ref} "Booth seating preferred"
```

## 8. Submit Reservation

```bash
playwright-cli -s=reservation click {complete-reservation-ref}
```

Triggers either: phone verification modal, or confirmation page (if phone already verified in session).

## 9. Phone Verification (Cross-Origin Iframe)

The verification input is in a cross-origin iframe — use `press`, not `fill`.

```bash
# Wait for SMS
sleep 5
# Retrieve code — see sms-codes.md for {CHAT_ID}
imsg history --chat-id {OPENTABLE_CHAT_ID} --limit 1 2>/dev/null | grep -oE '[0-9]{6}'

# Type each digit
playwright-cli -s=reservation press {d1}
playwright-cli -s=reservation press {d2}
playwright-cli -s=reservation press {d3}
playwright-cli -s=reservation press {d4}
playwright-cli -s=reservation press {d5}
playwright-cli -s=reservation press {d6}
```

## 10. Post-Verification Phone Fix

**Known OpenTable bug:** Verification often clears the phone field. After verification:

```bash
playwright-cli -s=reservation snapshot
playwright-cli -s=reservation fill {phone-ref} "{config.user_phone}"
playwright-cli -s=reservation click {complete-reservation-ref}
```

## 11. Confirmation

```bash
playwright-cli -s=reservation snapshot
```

Capture: restaurant name, date, time, party size, confirmation number. Then execute Post-Booking Actions in SKILL.md.

---

## Timer Expiry Recovery

OpenTable holds a table for ~**10 minutes** after time slot selection. If expired:
1. Go back to the restaurant URL
2. Reselect a time slot (may no longer be available)
3. Move quickly through checkout — gather all info upfront before starting

**Prevention:** Have phone, email, name ready before opening the page. Don't pause mid-checkout.

---

## Verification Failures

| Issue | Solution |
|-------|----------|
| No code after 30s | Click "Resend code". Wait. Check SMS again. |
| Code expired (10 min) | Click "Resend code" for a fresh one. |
| Wrong code | `press Backspace` × 6, re-enter. |
| Modal disappeared | Snapshot — may need to click "Complete reservation" again. |
