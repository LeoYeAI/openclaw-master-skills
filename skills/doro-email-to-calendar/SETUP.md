# Email-to-Calendar Setup Guide

This skill uses **smart onboarding** - it auto-detects your Gmail accounts and calendars, then presents sensible defaults. You can accept all defaults with one click or customize specific settings.

> **Tool Flexibility:** This guide uses `gog` CLI as the reference implementation for
> Gmail and Google Calendar access. If your agent has alternative tools (MCP servers,
> other CLIs, or direct API access), those can be used instead - the workflow and
> configuration concepts remain the same.

## Quick Start

On first use, the skill will:

1. **Detect your Gmail accounts** via `gog auth status`
2. **List available calendars** via `gog calendar list`
3. **Suggest smart defaults** based on your email pattern

You'll see something like:

```
Here's my suggested configuration (change any you disagree with):

1. Gmail Account: toni@gmail.com ← (detected)
2. Calendar: primary ← (detected)
3. Email Mode: Direct (scan your inbox) ← (guessed: personal email)
4. Attendees: Disabled
5. Whole-day events: Timed (9 AM - 5 PM)
6. Multi-day events: Daily recurring
7. Ignore patterns: (none)
8. Auto-create patterns: (none)
9. Email handling: Mark as read and archive (recommended)
   Also auto-process calendar replies? (Y/n)

Type numbers to change (e.g., "3, 7") or press Enter to accept all defaults.
```

**Just press Enter** to accept all defaults, or type numbers to change specific settings.

## Configuration File

The skill stores settings in `~/.config/email-to-calendar/config.json`.

### Full Schema

```json
{
  "provider": "gog",
  "email_mode": "direct",
  "gmail_account": "your-email@gmail.com",
  "calendar_id": "primary",
  "attendees": {
    "enabled": true,
    "emails": ["user1@gmail.com", "user2@gmail.com"]
  },
  "whole_day_events": {
    "style": "timed",
    "start_time": "09:00",
    "end_time": "17:00"
  },
  "multi_day_events": {
    "style": "daily_recurring"
  },
  "event_rules": {
    "ignore_patterns": ["fundraiser", "meeting"],
    "auto_create_patterns": ["holiday", "No School"]
  },
  "email_handling": {
    "mark_read": true,
    "archive": false
  },
  "deadline_notifications": {
    "enabled": true,
    "email_recipient": "your-email@gmail.com"
  }
}
```

### Configuration Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `provider` | string | `"gog"` | Email/calendar provider backend (currently only "gog" supported) |
| `email_mode` | `"direct"` / `"forwarded"` | `"direct"` | Direct scans your inbox; Forwarded only processes forwarded emails |
| `gmail_account` | string | (auto-detected) | Gmail account to monitor |
| `calendar_id` | string | `"primary"` | Calendar to create events in |
| `attendees.enabled` | boolean | `false` | Whether to add attendees to events |
| `attendees.emails` | string[] | `[]` | Email addresses to invite |
| `whole_day_events.style` | `"timed"` / `"all_day"` | `"timed"` | How to create whole-day events |
| `whole_day_events.start_time` | string | `"09:00"` | Start time for timed events |
| `whole_day_events.end_time` | string | `"17:00"` | End time for timed events |
| `multi_day_events.style` | `"daily_recurring"` / `"all_day_span"` | `"daily_recurring"` | How to handle multi-day events |
| `event_rules.ignore_patterns` | string[] | `[]` | Event types to always skip |
| `event_rules.auto_create_patterns` | string[] | `[]` | Event types to auto-create |
| `email_handling.mark_read` | boolean | `true` | Mark processed emails as read |
| `email_handling.archive` | boolean | `true` | Archive processed emails |
| `email_handling.auto_dispose_calendar_replies` | boolean | `true` | Auto-process calendar reply emails (accepts, declines, tentatives) |
| `deadline_notifications.enabled` | boolean | `false` | Send email notifications for events with deadlines |
| `deadline_notifications.email_recipient` | string | (gmail_account) | Email address to send notifications to |
| `agent_name` | string | `"Ripurapu"` | Agent name shown in event descriptions ("Created by X") |

### Email Mode Detection

The skill guesses the best mode based on your email pattern:

| Email Pattern | Suggested Mode | Reason |
|---------------|----------------|--------|
| `firstname.lastname@gmail.com` | Direct | Personal inbox |
| `firstname@gmail.com` | Direct | Personal inbox |
| `service@*`, `bot@*`, `agent@*` | Forwarded | Service/agent account |

### Event Style Options

**Whole-day Events:**
- `"timed"`: Creates events 9 AM - 5 PM (or custom times)
- `"all_day"`: Creates Google Calendar all-day events

**Multi-day Events (e.g., Feb 2-6):**
- `"daily_recurring"`: Creates separate 9-5 events for each day
- `"all_day_span"`: Creates a single event spanning all days

## Example Configurations

### Family Calendar (School Events)

```json
{
  "provider": "gog",
  "email_mode": "direct",
  "gmail_account": "family@gmail.com",
  "calendar_id": "primary",
  "attendees": {
    "enabled": true,
    "emails": ["parent1@gmail.com", "parent2@gmail.com"]
  },
  "whole_day_events": {
    "style": "timed",
    "start_time": "09:00",
    "end_time": "17:00"
  },
  "multi_day_events": {
    "style": "daily_recurring"
  },
  "event_rules": {
    "ignore_patterns": ["fundraiser", "PTA meeting", "volunteer request"],
    "auto_create_patterns": ["No School", "holiday", "Staff Development Day"]
  },
  "email_handling": {
    "mark_read": true,
    "archive": true,
    "auto_dispose_calendar_replies": true
  },
  "deadline_notifications": {
    "enabled": true,
    "email_recipient": "parent1@gmail.com"
  }
}
```

### Work Calendar

```json
{
  "provider": "gog",
  "email_mode": "direct",
  "gmail_account": "work@company.com",
  "calendar_id": "primary",
  "attendees": {
    "enabled": false,
    "emails": []
  },
  "whole_day_events": {
    "style": "timed",
    "start_time": "08:00",
    "end_time": "18:00"
  },
  "multi_day_events": {
    "style": "all_day_span"
  },
  "event_rules": {
    "ignore_patterns": ["newsletter", "announcement"],
    "auto_create_patterns": ["deadline", "review"]
  },
  "email_handling": {
    "mark_read": true,
    "archive": true,
    "auto_dispose_calendar_replies": true
  },
  "deadline_notifications": {
    "enabled": true,
    "email_recipient": "work@company.com"
  }
}
```

### Personal Calendar (Minimal)

```json
{
  "provider": "gog",
  "email_mode": "direct",
  "gmail_account": "personal@gmail.com",
  "calendar_id": "primary",
  "attendees": {
    "enabled": false,
    "emails": []
  },
  "whole_day_events": {
    "style": "all_day"
  },
  "multi_day_events": {
    "style": "all_day_span"
  },
  "event_rules": {
    "ignore_patterns": [],
    "auto_create_patterns": []
  },
  "email_handling": {
    "mark_read": true,
    "archive": true,
    "auto_dispose_calendar_replies": true
  }
}
```

## Manual Configuration

If you prefer to skip the interactive setup:

```bash
mkdir -p ~/.config/email-to-calendar
cat > ~/.config/email-to-calendar/config.json << 'EOF'
{
  "provider": "gog",
  "email_mode": "direct",
  "gmail_account": "your-email@gmail.com",
  "calendar_id": "primary",
  "attendees": {
    "enabled": false,
    "emails": []
  },
  "whole_day_events": {
    "style": "timed",
    "start_time": "09:00",
    "end_time": "17:00"
  },
  "multi_day_events": {
    "style": "daily_recurring"
  },
  "event_rules": {
    "ignore_patterns": [],
    "auto_create_patterns": []
  },
  "email_handling": {
    "mark_read": true,
    "archive": true,
    "auto_dispose_calendar_replies": true
  },
  "deadline_notifications": {
    "enabled": false,
    "email_recipient": "your-email@gmail.com"
  }
}
EOF
```

## Prerequisites

This skill requires:
- **Email access** - ability to read unread emails and get message bodies
- **Calendar access** - ability to create, update, and delete calendar events
- `jq` for JSON parsing
- `python3` for date parsing and scripts
- `bash` for shell scripts

**Reference implementation:** The `gog` CLI tool provides Gmail and Google Calendar
access. Other tools (MCP servers, direct API) work equally well if they provide
the same capabilities.

## Troubleshooting

### Config not found
The skill will auto-detect and suggest defaults. Just accept or customize.

### Events not being created
1. Check that `gog` is authenticated: `gog auth status`
2. Verify calendar ID is correct: `gog calendar list`
3. Check config file: `cat ~/.config/email-to-calendar/config.json`

### Wrong calendar
List available calendars:
```bash
gog calendar list
```
Update `calendar_id` in config to use a specific calendar.

### See what was processed
```bash
~/.openclaw/workspace/skills/email-to-calendar/scripts/activity_log.sh show --last 5
```

### Undo a recent event
```bash
~/.openclaw/workspace/skills/email-to-calendar/scripts/undo.sh list
~/.openclaw/workspace/skills/email-to-calendar/scripts/undo.sh last
```
