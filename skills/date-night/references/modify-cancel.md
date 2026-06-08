# Modify & Cancel Reservations — Detailed Reference

How to modify or cancel existing reservations on OpenTable and Resy.

Load config: `CONFIG=$(cat ~/.openclaw/skills/date-night/config.json)`

All commands assume PATH is set: `export PATH="$HOME/.npm-global/bin:$PATH"`

---

## OpenTable: Modify Reservation

### Via Confirmation Email (Easiest)
OpenTable sends a confirmation email with direct "Modify" and "Cancel" links:
```bash
# Search for confirmation email (if using gog/Gmail)
gog gmail search "from:opentable reservation confirmed" --max 5 2>/dev/null || true
```

### Via Website
```bash
playwright-cli -s=modify open "https://www.opentable.com/my/reservations" --headed
playwright-cli -s=modify snapshot
# Find reservation by confirmation # + last name (no login required):
playwright-cli -s=modify click {find-reservation-ref}
playwright-cli -s=modify fill {confirmation-ref} "{confirmation_number}"
playwright-cli -s=modify fill {last-name-ref} "{config.last_name}"
playwright-cli -s=modify click {find-ref}
```

### Modification Steps
```bash
playwright-cli -s=modify click {modify-ref}
playwright-cli -s=modify snapshot
# Change: date, time, or party size
playwright-cli -s=modify click {new-date-ref}
playwright-cli -s=modify click {new-time-ref}
playwright-cli -s=modify click {save-changes-ref}
```

**After modifying:**
1. Update the calendar event
2. Notify partner of the change (draft → approve → send)

---

## OpenTable: Cancel Reservation

```bash
playwright-cli -s=cancel open "https://www.opentable.com/my/reservations" --headed
playwright-cli -s=cancel snapshot
playwright-cli -s=cancel click {cancel-ref}
playwright-cli -s=cancel click {confirm-cancel-ref}
```

**Post-cancellation:**
1. Delete the calendar event
2. Notify partner if they were told about it (draft → approve → send)
3. Update history entry: set `"cancelled": true`

---

## Resy: Cancel Reservation

Resy requires login. Load saved auth if available:
```bash
playwright-cli -s=resy-cancel state-load ~/.openclaw/skills/date-night/state/resy-auth.json 2>/dev/null
playwright-cli -s=resy-cancel open "https://resy.com/account/reservations" --headed
playwright-cli -s=resy-cancel snapshot
playwright-cli -s=resy-cancel click {reservation-ref}
playwright-cli -s=resy-cancel click {cancel-ref}
playwright-cli -s=resy-cancel click {confirm-ref}
```

**⚠️ Resy Cancellation Policies:**
Many Resy restaurants have strict policies:
- 24–48 hour cancellation windows
- No-show fees: $25–100+ per person
- Prepaid/ticketed reservations may be non-refundable

Always check the policy and remind user of the deadline:
> "This reservation has a 24-hour cancellation policy. You need to cancel by {deadline} to avoid a fee."

## Resy: "Modify" (Cancel + Rebook)

Resy does not support direct modification. To change details:
1. Book new reservation first (if possible)
2. Cancel original after new one is confirmed
3. **Warn user:** popular restaurants may not have availability for new time

---

## Finding Reservation Details

If user doesn't have confirmation number:

```bash
# Check history file
cat ~/.openclaw/skills/date-night/history.jsonl 2>/dev/null | \
  jq -s 'sort_by(.date) | reverse | .[0:5]' 2>/dev/null || true

# Search email — targeted to booking senders only
gog gmail search "from:opentable OR from:resy subject:reservation confirmed" --max 5 2>/dev/null || true
```

---

## Movie / Event Ticket Cancellations

**Important:** Movie and event tickets are generally **non-refundable**. Always communicate this before purchase.

**Exceptions to check:**
- Some chains (Cinemark, Fandango) allow cancellation up to 1 hour before showtime for a partial refund
- SeatGeek / StubHub FanProtect covers invalid tickets but not buyer's remorse
- Ticketmaster "ticket insurance" (sold at checkout) may cover cancellation — check if user purchased it

To check cancellation options:
```bash
web_search "{platform} cancel movie tickets policy"
web_search "{chain} refund policy online tickets"
# Then navigate to the platform's order management page
```
