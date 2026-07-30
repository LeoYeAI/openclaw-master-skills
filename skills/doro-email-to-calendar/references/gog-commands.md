# gog Calendar CLI Reference

This document contains detailed reference information for the `gog` CLI commands used by the email-to-calendar skill.

## Calendar Operations

### Creating Events

```bash
gog calendar create <calendar_id> \
    --summary "Event Title" \
    --from "2026-02-11T09:00:00" \
    --to "2026-02-11T17:00:00" \
    --description "Event description" \
    --attendees "email1@example.com,email2@example.com" \
    --send-updates all
```

### Updating Events

```bash
# Update event details
gog calendar update <calendar_id> <event_id> \
    --summary "Updated Title" \
    --from "2026-01-15T09:00:00" \
    --to "2026-01-15T17:00:00"

# Replace all attendees
gog calendar update <calendar_id> <event_id> --attendees "new@example.com"

# Add attendees while preserving existing ones
gog calendar update <calendar_id> <event_id> --add-attendee "additional@example.com"

# Clear recurrence
gog calendar update <calendar_id> <event_id> --rrule " "
```

### Deleting Events

```bash
gog calendar delete <calendar_id> <event_id>
```

### Listing Events

```bash
# List events in a date range
gog calendar events <calendar_id> \
    --from "2026-02-01T00:00:00" \
    --to "2026-02-28T23:59:59" \
    --json
```

## Recurrence Patterns (--rrule flag)

Uses standard RFC 5545 RRULE syntax. The `--rrule` flag accepts RRULE strings.

### Common Patterns

| Pattern | RRULE |
|---------|-------|
| Daily for N days | `RRULE:FREQ=DAILY;COUNT=N` |
| Daily (forever) | `RRULE:FREQ=DAILY` |
| Weekly | `RRULE:FREQ=WEEKLY` |
| Every weekday | `RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR` |
| Every Tuesday | `RRULE:FREQ=WEEKLY;BYDAY=TU` |
| Monthly on specific day | `RRULE:FREQ=MONTHLY;BYMONTHDAY=19` |
| First Monday of month | `RRULE:FREQ=MONTHLY;BYDAY=1MO` |
| Last Friday of month | `RRULE:FREQ=MONTHLY;BYDAY=-1FR` |
| Yearly | `RRULE:FREQ=YEARLY` |
| Until a date | `RRULE:FREQ=WEEKLY;UNTIL=20261231T235959Z` |

### Multi-Day Events

For events spanning multiple consecutive days (e.g., Feb 2-6), create a daily recurring event:

```bash
# Feb 2-6 = 5 days
gog calendar create "$CALENDAR_ID" \
    --summary "Multi-Day Event" \
    --from "2026-02-02T09:00:00" \
    --to "2026-02-02T17:00:00" \
    --rrule "RRULE:FREQ=DAILY;COUNT=5"
```

### Day of Week Codes

| Day | Code |
|-----|------|
| Monday | MO |
| Tuesday | TU |
| Wednesday | WE |
| Thursday | TH |
| Friday | FR |
| Saturday | SA |
| Sunday | SU |

## Key Flags

| Flag | Description | Values |
|------|-------------|--------|
| `--attendees` | Comma-separated attendee emails | `email1,email2` |
| `--send-updates` | Notify attendees of changes | `all`, `externalOnly`, `none` |
| `--rrule` | Recurrence rule (RFC 5545) | `RRULE:FREQ=...` |
| `--reminder` | Add reminder | `email:1d`, `popup:30m` |
| `--guests-can-invite` | Allow guests to invite others | flag |
| `--guests-can-modify` | Allow guests to modify event | flag |
| `--guests-can-see-others` | Allow guests to see other attendees | flag |
| `--json` | Output as JSON | flag |

### Reminder Format

```bash
--reminder "email:1d"    # Email 1 day before
--reminder "popup:30m"   # Popup 30 minutes before
--reminder "popup:1h"    # Popup 1 hour before
```

## Advanced Attendee Syntax

Mark attendees as optional or add comments:

```bash
--attendees "alice@example.com,bob@example.com;optional,carol@example.com;comment=FYI only"
```

| Modifier | Example |
|----------|---------|
| Optional | `email@example.com;optional` |
| Comment | `email@example.com;comment=FYI only` |
| Response status | `email@example.com;responseStatus=accepted` |

## Note on `--send-updates`

The `--send-updates` flag is only available in tonimelisma's gogcli fork. Without this flag, attendees won't receive email notifications for event changes.

To enable:
1. Install gogcli from: https://github.com/tonimelisma/gogcli
2. Use the `feat/calendar-send-updates` branch

The `create_event.sh` script auto-detects support and uses it when available.

## Gmail Operations

### Send an Email

```bash
gog gmail send \
    --account "sender@gmail.com" \
    --to "recipient@example.com" \
    --subject "Subject line" \
    --body "Email body text"
```

**Flags:**
| Flag | Description | Required |
|------|-------------|----------|
| `--account` | Gmail account to send from | Yes |
| `--to` | Recipient email address | Yes |
| `--subject` | Email subject line | Yes |
| `--body` | Email body text | Yes |
| `--cc` | CC recipients (comma-separated) | No |
| `--bcc` | BCC recipients (comma-separated) | No |

**Example - Deadline notification:**
```bash
gog gmail send \
    --account "user@gmail.com" \
    --to "user@gmail.com" \
    --subject "ACTION REQUIRED: RSVP for Team Offsite by Feb 10" \
    --body "A calendar event has been created that requires your action.

Event: Team Offsite
Date: February 15-17, 2026
Deadline: February 10, 2026
Action Required: RSVP

Link: https://example.com/rsvp

---
Sent by email-to-calendar skill"
```

### Get a Single Email

```bash
gog gmail get <messageId> --account "user@gmail.com"
```

### Search Emails

```bash
# Search with body content
gog gmail messages search "in:inbox is:unread" \
    --max 20 \
    --include-body \
    --account "user@gmail.com"

# Search forwarded emails
gog gmail messages search "in:inbox is:unread subject:Fwd OR subject:FW" \
    --max 10 \
    --include-body \
    --account "user@gmail.com"
```

### Modify Email Labels

```bash
# Mark as read
gog gmail modify <messageId> --remove-labels UNREAD --account "user@gmail.com"

# Archive (remove from inbox)
gog gmail modify <messageId> --remove-labels INBOX --account "user@gmail.com"

# Both
gog gmail modify <messageId> --remove-labels UNREAD,INBOX --account "user@gmail.com"
```

## Common Mistakes

- **WRONG:** `gog gmail messages get <id>` - This command does not exist
- **CORRECT:** `gog gmail get <id>` - Use this to read a single email

## References

- [RFC 5545 - iCalendar RRULE](https://icalendar.org/iCalendar-RFC-5545/3-8-5-3-recurrence-rule.html)
- [Google Calendar API Recurrence](https://developers.google.com/calendar/api/concepts/events-calendars#recurrence_rules)
