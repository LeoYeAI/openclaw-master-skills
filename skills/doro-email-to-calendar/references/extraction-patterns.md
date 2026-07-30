# Email Extraction Patterns

This document describes the patterns used for extracting calendar events and action items from forwarded emails.

## Event Detection Patterns

The extraction script looks for these patterns to identify potential calendar events:

### Primary Event Keywords
- meeting, call, sync, standup, review, demo, interview
- appointment, event, conference, workshop, webinar, training
- meet (as a verb)

### Event Phrases
- "Meeting on [date] at [time]"
- "Let's meet [date] at [time]"
- "Join us on [date] for [purpose]"
- "You are invited to [event] on [date]"
- "Please attend [event] on [date]"
- "Mark your calendar for [date]"
- "Save the date: [date]"
- "When: [date]" / "Date: [date]" / "Time: [time]"

## Date Parsing

The script recognizes these date formats:

### With Year
- January 15, 2026
- 15 January 2026
- 01/15/2026 (US format)
- 15/01/2026 (EU format)
- 2026-01-15 (ISO format)

### Without Year (defaults to current year)
- Wednesday January 15
- January 15
- Next Tuesday
- This Friday

### Relative Dates
- Today, Tomorrow
- Next week, Next Monday
- In 3 days

## Time Parsing

### 12-hour format
- 2:30 PM, 2:30 pm
- 2 PM, 2pm
- 9:00 AM - 5:00 PM (ranges)

### 24-hour format
- 14:30
- 09:00-17:00

### Full Day Indicators
- "all day", "full day", "whole day"
- "9am to 5pm", "9:00-17:00"
- "business hours", "work day"

## Action Item Detection

### Action Keywords
- Action:, Task:, Todo:, To-do:, Follow-up:, Followup:
- Please [do something]
- Kindly [do something]
- Need to, Needs to, We need to
- Should, Must, Will need to

### Bullet Points
- `- [ ] Task description`
- `* Task description`
- `• Task description`

### Deadline Detection
Action items are checked for associated deadlines:
- "by [date]"
- "due [date]"
- "before [date]"
- "deadline: [date]"

## Header Filtering

The script automatically filters out email headers to focus on actual content:

### Filtered Headers
- From:, Date:, Subject:, To:, Cc:, Bcc:
- "---------- Forwarded message ----------"
- "---------- Original message ----------"
- "On [date] [person] wrote:"
- "Sent from my [device]"

## Duplicate Detection

When checking for existing calendar events, duplicates are identified by:

1. **Same Date**: Events on the same calendar day
2. **Similar Title**: 2+ keywords match between titles
3. **Overlapping Time**: Within 1 hour of each other

If a duplicate is found, the existing event is updated rather than creating a new one.

## Edge Cases

### Cancellations
If an email contains cancellation language:
- "Cancelled", "Canceled", "Postponed", "Rescheduled"
- "No longer happening", "Won't take place"

The script should:
1. Search for the existing event
2. Either delete it or update title with "CANCELLED" prefix

### Recurring Events
Currently, the script extracts each occurrence as a separate event. Recurring patterns ("every Monday", "weekly") are noted but not expanded.

### Time Zones
The script assumes all times are in the user's local timezone. Time zone information in emails is noted in the description but not used for conversion.

### All-Day Events
When detected, all-day events are created with:
- Start: 9:00 AM
- End: 5:00 PM
- Duration: 8 hours

This provides a visual block in the calendar while maintaining flexibility.

## Output Format

### Event Object
```json
{
  "type": "event",
  "title": "Meeting title",
  "date": {
    "month": "January",
    "day": 15,
    "year": 2026,
    "month_num": 1
  },
  "time": {
    "hour": 14,
    "minute": 30
  },
  "is_full_day": false,
  "source_text": "Original text that matched",
  "context": "Surrounding text for reference",
  "raw_line": "The exact line from the email"
}
```

### Action Object
```json
{
  "type": "action",
  "text": "Action description",
  "deadline": {
    "month": "January",
    "day": 17,
    "year": 2026,
    "month_num": 1
  },
  "source_line": "The exact line from the email"
}
```

## Testing

To test extraction on a sample email:

```bash
echo 'Your email content here' | python3 scripts/extract_events.py -
```

Or from a file:

```bash
python3 scripts/extract_events.py email.txt
```
