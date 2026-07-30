# Email-to-Calendar Workflow Example

## Scenario: User Forwards an Email

**User sends:**
```
---------- Forwarded message ----------
From: Sarah <sarah@client.com>
Date: Mon, Feb 2, 2026 at 10:00 AM
Subject: Project kickoff meeting
To: team@company.com

Hi everyone,

Let's schedule a kickoff meeting for the new website project on Thursday February 5 at 3:00 PM in Conference Room B.

Action items before the meeting:
- Review the requirements document
- Prepare your team's capacity estimates
- Submit any questions by Wednesday

Thanks!
Sarah
```

## Step 1: Detect Forwarded Email

You recognize the forwarded email patterns:
- Subject starts with "Fwd:" (implied)
- Contains "---------- Forwarded message ----------"
- Has email headers (From:, Date:, Subject:, To:)

## Step 2: Extract Items

Run extraction:
```bash
python3 scripts/extract_events.py email.txt
```

**Result:**
```json
{
  "events": [
    {
      "type": "event",
      "title": "kickoff meeting for the new website project",
      "date": {"month": "February", "day": 5, "year": 2026, "month_num": 2},
      "time": {"hour": 15, "minute": 0},
      "is_full_day": false
    }
  ],
  "actions": [
    {
      "type": "action",
      "text": "Review the requirements document",
      "deadline": null
    },
    {
      "type": "action",
      "text": "Prepare your team's capacity estimates",
      "deadline": null
    },
    {
      "type": "action",
      "text": "Submit any questions by Wednesday",
      "deadline": {"month": "February", "day": 4, "year": 2026, "month_num": 2}
    }
  ]
}
```

## Step 3: Store to Memory

Save to dated file:
```bash
EXTRACTION_FILE="memory/email-extractions/2026-02-02-143022.json"
python3 scripts/extract_events.py email.txt > "$EXTRACTION_FILE"
```

Update index:
```json
{
  "extractions": [
    {
      "file": "memory/email-extractions/2026-02-02-143022.json",
      "date": "2026-02-02T14:30:22",
      "status": "pending_review"
    }
  ]
}
```

## Step 4: Present to User

**Your response:**
> I found 1 event and 3 action items in that email:
>
> **Events:**
> 1. **Kickoff meeting for the new website project** - Thursday February 5 at 3:00 PM - Conference Room B
>
> **Action Items:**
> 1. **Review the requirements document** - No deadline
> 2. **Prepare your team's capacity estimates** - No deadline
> 3. **Submit any questions by Wednesday** - Due February 4
>
> Which events should I create calendar entries for? Reply with numbers (e.g., "1") or "all" or "none".

## Step 5: User Responds

**User replies:** "1"

## Step 6: Check for Duplicates

```bash
bash scripts/check_duplicate.sh "$CALENDAR_ID" \
  "kickoff meeting for the new website project" \
  "February 5, 2026" \
  "3:00 PM"
```

**Result:** `null` (no duplicate found)

## Step 7: Create Calendar Event

```bash
# Read attendees from config
CONFIG_FILE="$HOME/.config/email-to-calendar/config.json"
ATTENDEE_EMAILS=$(jq -r '.attendees.emails | join(",")' "$CONFIG_FILE")
CALENDAR_ID=$(jq -r '.calendar_id' "$CONFIG_FILE")

gog calendar create "$CALENDAR_ID" \
  --summary "Kickoff meeting - Website Project" \
  --from "2026-02-05T15:00:00" \
  --to "2026-02-05T16:00:00" \
  --description "Kickoff meeting for the new website project

Location: Conference Room B
From: Sarah <sarah@client.com>

Action items to complete before meeting:
- Review the requirements document
- Prepare your team's capacity estimates
- Submit any questions by Wednesday February 4" \
  --attendees "$ATTENDEE_EMAILS" \
  --send-updates all
```

## Step 8: Confirm and Update Status

**Your response:**
> Created calendar event:
> - **Title:** Kickoff meeting - Website Project
> - **Date:** Thursday, February 5, 2026
> - **Time:** 3:00 PM - 4:00 PM
> - **Description:** Full details including location and action items
> - **Attendees:** Invited as configured

Update extraction status:
```json
{
  "file": "memory/email-extractions/2026-02-02-143022.json",
  "date": "2026-02-02T14:30:22",
  "status": "processed",
  "events_created": ["event_id_123"]
}
```

## Alternative: Duplicate Found

If check_duplicate.sh returns an existing event:

```json
{
  "id": "abc123xyz",
  "summary": "Website Project Kickoff",
  "start": {"dateTime": "2026-02-05T15:00:00"}
}
```

**Your response:**
> I found an existing event "Website Project Kickoff" on February 5 at 3:00 PM. Should I:
> 1. Update it with new information from this email
> 2. Skip (keep existing event as-is)
> 3. Create a separate event anyway

If user chooses "1", update the existing event with the new event ID.

## Reviewing Pending Items

Later, user asks: "What emails do I need to review?"

Check index file and present any pending extractions:

> You have 1 pending email extraction from February 2:
>
> **Events:**
> 1. **Kickoff meeting** - February 5 at 3:00 PM
>
> **Action Items:**
> 1. Review requirements document
> 2. Prepare capacity estimates
> 3. Submit questions by Wednesday
>
> Should I create the calendar event for item 1?
