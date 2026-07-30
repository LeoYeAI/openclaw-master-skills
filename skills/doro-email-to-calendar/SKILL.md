---
name: doro-email-to-calendar
version: 1.13.1
version: 1.0.0
description: Extract calendar events from emails and create calendar entries. Supports two modes: (1) Direct inbox monitoring - scans all emails for events, or (2) Forwarded emails - processes emails you forward to a dedicated address. Features smart onboarding, event tracking, pending invite reminders, undo support, silent activity logging, deadline detection with separate reminder events, email notifications for action-required items, and provider abstraction for future extensibility.
---

> **CRITICAL RULES - READ BEFORE PROCESSING ANY EMAIL**
>
> 1. **NEVER CALL `gog` DIRECTLY** - ALWAYS use wrapper scripts (`create_event.sh`, `email_read.sh`, etc.). Direct `gog` calls bypass tracking and cause duplicates. THIS IS NON-NEGOTIABLE.
> 2. **IGNORE CALENDAR NOTIFICATIONS** - DO NOT process emails from `calendar-notification@google.com` (Accepted:, Declined:, Tentative:, etc.). These are responses to existing invites, NOT new events. Run `process_calendar_replies.sh` to archive them.
> 3. **ALWAYS ASK BEFORE CREATING** - Never create calendar events without explicit user confirmation in the current conversation
> 4. **CHECK IF ALREADY PROCESSED** - Before processing any email, check `processed_emails` in index.json
> 5. **READ CONFIG FIRST** - Load and apply `ignore_patterns` and `auto_create_patterns` before presenting events
> 6. **READ MEMORY.MD** - Check for user preferences stored from previous sessions
> 7. **INCLUDE ALL CONFIGURED ATTENDEES** - When creating/updating/deleting events, always include attendees from config with `--attendees` flag (and `--send-updates all` if supported)
> 8. **CHECK TRACKED EVENTS FIRST** - Use `lookup_event.sh --email-id` to find existing events before calendar search (faster, more reliable)
> 9. **TRACK ALL CREATED EVENTS** - The `create_event.sh` script automatically tracks events; use tracked IDs for updates/deletions
> 10. **SHOW DAY-OF-WEEK** - Always include the day of week when presenting events for user verification

> ⛔ **FORBIDDEN: DO NOT USE `gog` COMMANDS DIRECTLY** ⛔
>
> **WRONG:** `gog calendar create ...` or `gog gmail ...`
> **RIGHT:** `"$SCRIPTS_DIR/create_event.sh" ...` or `"$SCRIPTS_DIR/email_read.sh" ...`
>
> Direct CLI calls bypass event tracking, break duplicate detection, and cause duplicate events.
> ALL operations MUST go through the wrapper scripts in `scripts/`.

# Email to Calendar Skill

Extract calendar events and action items from emails, present them for review, and create/update calendar events with duplicate detection and undo support.

**First-time setup:** See [SETUP.md](SETUP.md) for configuration options and smart onboarding.

## Reading Email Content

**IMPORTANT:** Before you can extract events, you must read the email body. Use the wrapper scripts.

```bash
SCRIPTS_DIR="$HOME/.openclaw/workspace/skills/email-to-calendar/scripts"

# Get a single email by ID (PREFERRED)
"$SCRIPTS_DIR/email_read.sh" --email-id "<messageId>"

# Search with body content included
"$SCRIPTS_DIR/email_search.sh" --query "in:inbox is:unread" --max 20 --include-body
```

**Note on stale forwards:** Don't use `newer_than:1d` because it checks the email's original date header, not when it was received. Process all UNREAD emails and rely on the "already processed" check.

## Workflow

### 0. Pre-Processing Checks (MANDATORY)

```bash
SCRIPTS_DIR="$HOME/.openclaw/workspace/skills/email-to-calendar/scripts"
CONFIG_FILE="$HOME/.config/email-to-calendar/config.json"
INDEX_FILE="$HOME/.openclaw/workspace/memory/email-extractions/index.json"

# Start activity logging
"$SCRIPTS_DIR/activity_log.sh" start-session

# Check email mode
EMAIL_MODE=$(jq -r '.email_mode // "forwarded"' "$CONFIG_FILE")

# Check if email was already processed
EMAIL_ID="<the email message ID>"
if jq -e ".extractions[] | select(.email_id == \"$EMAIL_ID\")" "$INDEX_FILE" > /dev/null 2>&1; then
    "$SCRIPTS_DIR/activity_log.sh" log-skip --email-id "$EMAIL_ID" --subject "Subject" --reason "Already processed"
    exit 0
fi

# Load ignore/auto-create patterns
IGNORE_PATTERNS=$(jq -r '.event_rules.ignore_patterns[]' "$CONFIG_FILE")
AUTO_CREATE_PATTERNS=$(jq -r '.event_rules.auto_create_patterns[]' "$CONFIG_FILE")
```

### 1. Find Emails to Process

**DIRECT mode:** Scan all unread emails for event indicators (dates, times, meeting keywords).

**FORWARDED mode:** Only process emails with forwarded indicators (Fwd:, forwarded message headers).

### 2. Extract Events (Agent does this directly)

Read the email and extract events as structured data. Include for each event:
- **title**: Descriptive name (max 80 chars)
- **date**: Event date(s)
- **day_of_week**: For verification
- **time**: Start/end times (default: 9 AM - 5 PM)
- **is_multi_day**: Whether it spans multiple days
- **is_recurring**: Whether it repeats (and pattern)
- **confidence**: high/medium/low
- **urls**: Any URLs found in the email (REQUIRED - always look for registration links, info pages, ticketing sites, etc.)
- **deadline_date**: RSVP/registration/ticket deadline date (if found)
- **deadline_action**: What user needs to do (e.g., "RSVP", "get tickets", "register")
- **deadline_url**: Direct link for taking action (often same as event URL)

**URL Extraction Rule:** ALWAYS scan the email for URLs and include the most relevant one at the BEGINNING of the event description.

### 2.1 Deadline Detection

Scan the email for deadline patterns that indicate action is required before the event:

**Common Deadline Patterns:**
- "RSVP by [date]", "Please RSVP by [date]"
- "Register by [date]", "Registration closes [date]"
- "Tickets available until [date]", "Get tickets by [date]"
- "Early bird ends [date]", "Early registration deadline [date]"
- "Must respond by [date]", "Respond by [date]"
- "Sign up by [date]", "Sign up deadline [date]"
- "Deadline: [date]", "Due by [date]"
- "Last day to [action]: [date]"

When a deadline is found:
1. Extract the deadline date
2. Determine the required action (RSVP, register, buy tickets, etc.)
3. Find the URL for taking that action
4. Flag the event for special handling (see sections below)

### 3. Present Items to User and WAIT

Apply event rules, then present with numbered selection:

```
I found the following potential events:

1. ~~ELAC Meeting (Feb 2, Monday at 8:15 AM)~~ - SKIP (matches ignore pattern)
2. **Team Offsite (Feb 2-6, Sun-Thu)** - PENDING
3. **Staff Development Day (Feb 12, Wednesday)** - AUTO-CREATE

Reply with numbers to create (e.g., '2, 3'), 'all', or 'none'.
```

**STOP AND WAIT for user response.**

After presenting, record pending invites for follow-up reminders:
```bash
# Record pending invites using add_pending.sh
"$SCRIPTS_DIR/add_pending.sh" \
    --email-id "$EMAIL_ID" \
    --email-subject "$EMAIL_SUBJECT" \
    --events-json '[{"title":"Event Name","date":"2026-02-15","time":"14:00","status":"pending"}]'
```

### 4. Check for Duplicates (MANDATORY)

**ALWAYS check before creating any event:**

```bash
# Step 1: Check local tracking first (fast)
TRACKED=$("$SCRIPTS_DIR/lookup_event.sh" --email-id "$EMAIL_ID")
if [ "$(echo "$TRACKED" | jq 'length')" -gt 0 ]; then
    EXISTING_EVENT_ID=$(echo "$TRACKED" | jq -r '.[0].event_id')
fi

# Step 2: If not found, try summary match
if [ -z "$EXISTING_EVENT_ID" ]; then
    TRACKED=$("$SCRIPTS_DIR/lookup_event.sh" --summary "$EVENT_TITLE")
fi

# Step 3: Fall back to calendar search using wrapper script
if [ -z "$EXISTING_EVENT_ID" ]; then
    "$SCRIPTS_DIR/calendar_search.sh" --calendar-id "$CALENDAR_ID" --from "${EVENT_DATE}T00:00:00" --to "${EVENT_DATE}T23:59:59"
fi
```

Use LLM semantic matching for fuzzy duplicates (e.g., "Team Offsite" vs "Team Offsite 5-6pm").

### 5. Create or Update Calendar Events

**Use create_event.sh (recommended)** - handles date parsing, tracking, and changelog:

```bash
# Create new event
"$SCRIPTS_DIR/create_event.sh" \
    "$CALENDAR_ID" \
    "Event Title" \
    "February 11, 2026" \
    "9:00 AM" \
    "5:00 PM" \
    "Description" \
    "$ATTENDEE_EMAILS" \
    "" \
    "$EMAIL_ID"

# Update existing event (pass event_id as 8th parameter)
"$SCRIPTS_DIR/create_event.sh" \
    "$CALENDAR_ID" \
    "Updated Title" \
    "February 11, 2026" \
    "10:00 AM" \
    "6:00 PM" \
    "Updated description" \
    "$ATTENDEE_EMAILS" \
    "$EXISTING_EVENT_ID" \
    "$EMAIL_ID"
```

For direct gog commands and advanced options, see [references/gog-commands.md](references/gog-commands.md).

### 6. Email Disposition (Automatic)

Email disposition (mark as read and/or archive) is handled **automatically** by `create_event.sh` based on config settings. No manual step needed - emails are dispositioned after event creation.

To manually disposition an email:
```bash
"$SCRIPTS_DIR/disposition_email.sh" --email-id "$EMAIL_ID"
```

To process calendar reply emails (accepts, declines, tentatives):
```bash
"$SCRIPTS_DIR/process_calendar_replies.sh"           # Process all
"$SCRIPTS_DIR/process_calendar_replies.sh" --dry-run # Preview only
```

```bash
# End activity session
"$SCRIPTS_DIR/activity_log.sh" end-session
```

## Event Creation Rules

### Date/Time Handling
- **Single-day events**: Default 9:00 AM - 5:00 PM
- **Multi-day events** (e.g., Feb 2-6): Use `--rrule "RRULE:FREQ=DAILY;COUNT=N"`
- **Events with specific times**: Use exact time from email

### Event Descriptions

**Format event descriptions in this order:**

1. **ACTION WARNING** (if deadline exists):
   ```
   *** ACTION REQUIRED: [ACTION] BY [DATE] ***
   ```

2. **Event Link** (if URL found):
   ```
   Event Link: [URL]
   ```

3. **Event Details**: Information extracted from the email

**Example WITH deadline:**
```
*** ACTION REQUIRED: GET TICKETS BY FEB 15 ***

Event Link: https://example.com/tickets

Spring Concert at Downtown Theater
Doors open at 7 PM
VIP meet & greet available
```

**Example WITHOUT deadline:**
```
Event Link: https://example.com/event

Spring Concert at Downtown Theater
Doors open at 7 PM
```

### Duplicate Detection
Consider it a duplicate if:
- Same date AND similar title (semantic matching) AND overlapping time

Always update existing events rather than creating duplicates.

### Creating Deadline Events

When an event has a deadline (RSVP, registration, ticket purchase, etc.), create TWO calendar events:

**1. Main Event** (as normal, but with warning in description):
```bash
"$SCRIPTS_DIR/create_event.sh" \
    "$CALENDAR_ID" \
    "Spring Concert" \
    "March 1, 2026" \
    "7:00 PM" \
    "10:00 PM" \
    "*** ACTION REQUIRED: GET TICKETS BY FEB 15 ***

Event Link: https://example.com/tickets

Spring Concert at Downtown Theater
Doors open at 7 PM" \
    "$ATTENDEE_EMAILS" \
    "" \
    "$EMAIL_ID"
```

**2. Deadline Reminder Event** (separate event on the deadline date):
```bash
# Use create_event.sh for deadline reminders too (ensures tracking)
"$SCRIPTS_DIR/create_event.sh" \
    "$CALENDAR_ID" \
    "DEADLINE: Get tickets for Spring Concert" \
    "2026-02-15" \
    "09:00" \
    "09:30" \
    "Action required: Get tickets

Event Link: https://example.com/tickets

Main event: Spring Concert on March 1, 2026" \
    "" \
    "" \
    "$EMAIL_ID"
```

**Deadline Event Properties:**
- **Title format**: `DEADLINE: [Action] for [Event Name]`
- **Date**: The deadline date
- **Time**: 9:00 AM (30 minute duration)
- **Reminders**: Email 1 day before + popup 1 hour before
- **Description**: Action required, URL, reference to main event

### Email Notifications for Deadlines

When creating events with deadlines, send a notification email to alert the user:

```bash
# Load config
CONFIG_FILE="$HOME/.config/email-to-calendar/config.json"
USER_EMAIL=$(jq -r '.deadline_notifications.email_recipient // .gmail_account' "$CONFIG_FILE")
NOTIFICATIONS_ENABLED=$(jq -r '.deadline_notifications.enabled // false' "$CONFIG_FILE")

# Send notification if enabled (using wrapper script)
if [ "$NOTIFICATIONS_ENABLED" = "true" ]; then
    "$SCRIPTS_DIR/email_send.sh" \
        --to "$USER_EMAIL" \
        --subject "ACTION REQUIRED: Get tickets for Spring Concert by Feb 15" \
        --body "A calendar event has been created that requires your action.

Event: Spring Concert
Date: March 1, 2026
Deadline: February 15, 2026
Action Required: Get tickets

Link: https://example.com/tickets

Calendar events created:
- Main event: Spring Concert (March 1)
- Deadline reminder: DEADLINE: Get tickets for Spring Concert (Feb 15)

---
This notification was sent by the email-to-calendar skill."
fi
```

**When to send notifications:**
- Only when `deadline_notifications.enabled` is `true` in config
- Only for events that have action-required deadlines
- Include the deadline date, action, URL, and event details

## Activity Log

```bash
# Start session
"$SCRIPTS_DIR/activity_log.sh" start-session

# Log skipped emails
"$SCRIPTS_DIR/activity_log.sh" log-skip --email-id "abc" --subject "Newsletter" --reason "No events"

# Log events
"$SCRIPTS_DIR/activity_log.sh" log-event --email-id "def" --title "Meeting" --action created

# End session
"$SCRIPTS_DIR/activity_log.sh" end-session

# Show recent activity
"$SCRIPTS_DIR/activity_log.sh" show --last 3
```

## Changelog and Undo

Changes can be undone within 24 hours:

```bash
# List recent changes
"$SCRIPTS_DIR/changelog.sh" list --last 10

# List undoable changes
"$SCRIPTS_DIR/undo.sh" list

# Undo most recent change
"$SCRIPTS_DIR/undo.sh" last

# Undo specific change
"$SCRIPTS_DIR/undo.sh" --change-id "chg_20260202_143000_001"
```

## Pending Invites

Events not immediately actioned are tracked for reminders:

```bash
# Add pending invites (after presenting events to user)
"$SCRIPTS_DIR/add_pending.sh" \
    --email-id "$EMAIL_ID" \
    --email-subject "Party Invite" \
    --events-json '[{"title":"Birthday Party","date":"2026-02-15","time":"14:00","status":"pending"}]'

# List pending invites (JSON)
"$SCRIPTS_DIR/list_pending.sh"

# Human-readable summary
"$SCRIPTS_DIR/list_pending.sh" --summary

# Update reminder tracking
"$SCRIPTS_DIR/list_pending.sh" --summary --update-reminded

# Auto-dismiss after 3 ignored reminders
"$SCRIPTS_DIR/list_pending.sh" --summary --auto-dismiss
```

## Event Tracking

```bash
# Look up by email ID
"$SCRIPTS_DIR/lookup_event.sh" --email-id "19c1c86dcc389443"

# Look up by summary
"$SCRIPTS_DIR/lookup_event.sh" --summary "Staff Development"

# List all tracked events
"$SCRIPTS_DIR/lookup_event.sh" --list

# Validate events exist (removes orphans)
"$SCRIPTS_DIR/lookup_event.sh" --email-id "abc" --validate
```

## File Locations

| File | Purpose |
|------|---------|
| `~/.config/email-to-calendar/config.json` | User configuration |
| `~/.openclaw/workspace/memory/email-extractions/` | Extracted data |
| `~/.openclaw/workspace/memory/email-extractions/index.json` | Processing index |
| `~/.openclaw/workspace/memory/email-to-calendar/events.json` | Event tracking |
| `~/.openclaw/workspace/memory/email-to-calendar/pending_invites.json` | Pending invites |
| `~/.openclaw/workspace/memory/email-to-calendar/activity.json` | Activity log |
| `~/.openclaw/workspace/memory/email-to-calendar/changelog.json` | Change history |
| `~/.openclaw/workspace/skills/email-to-calendar/scripts/` | Utility scripts |
| `~/.openclaw/workspace/skills/email-to-calendar/MEMORY.md` | User preferences |

## References

- **Setup Guide**: [SETUP.md](SETUP.md) - Configuration and onboarding
- **CLI Reference**: [references/gog-commands.md](references/gog-commands.md) - Detailed gog CLI usage
- **Extraction Patterns**: [references/extraction-patterns.md](references/extraction-patterns.md) - Date/time parsing
- **Workflow Example**: [references/workflow-example.md](references/workflow-example.md) - Complete example

## Notes

### Date Parsing
Handles common formats:
- January 15, 2026, Wednesday January 15
- 01/15/2026, 15/01/2026
- Date ranges like "Feb 2-6"

### Time Zones
All times assumed local timezone. Time zone info preserved in descriptions.
