# email-to-calendar Skill Bootstrap

This file contains instructions for self-bootstrapping the skill when installed via ClawHub.

## On First Activation

When this skill is first used:

### 1. Verify Capabilities

Verify the agent can:
- Read emails (list unread, get message body)
- Create calendar events
- Update/delete calendar events

If any capability is missing, inform the user:
> "This skill requires email and calendar access. Please ensure you have
> the necessary tools configured (e.g., gog CLI, or an MCP server)."

### 2. Critical Operating Rules

**NEVER call `gog` or other CLI tools directly.** Always use the wrapper scripts:
- `create_event.sh` - Create/update events (handles tracking, changelog, attribution)
- `email_read.sh` - Read email content
- `email_search.sh` - Search emails
- `email_modify.sh` - Modify email labels
- `disposition_email.sh` - Mark read and/or archive
- `process_calendar_replies.sh` - Auto-archive calendar notifications

Direct CLI calls bypass event tracking and cause duplicate events.

**IGNORE calendar notification emails** from `calendar-notification@google.com`:
- Subject patterns: "Accepted:", "Declined:", "Tentative:", "Updated invitation:", "Cancelled:"
- These are responses to existing invites, NOT new events to create
- Run `process_calendar_replies.sh` to auto-archive them

### 3. Check Heartbeat Integration

Read `~/.openclaw/workspace/HEARTBEAT.md` and ensure it contains:
- "Email Check" or "Email Scanning" section with calendar notification exclusion
- "Pending Calendar Invites" section

## Heartbeat Sections to Add

If the following sections are not present in HEARTBEAT.md, add them:

```markdown
## Email Scanning (email-to-calendar skill)
During email check cycle:
1. **IGNORE calendar notification emails** - DO NOT process emails from `calendar-notification@google.com`
   - These include: "Accepted:", "Declined:", "Tentative:", "Updated invitation:", "Cancelled:"
   - These are just notifications about responses to existing invites, NOT new events
   - Run `~/.openclaw/workspace/skills/email-to-calendar/scripts/process_calendar_replies.sh` to auto-archive them
2. Check for other unread emails with event indicators (dates, times, meeting keywords)
3. If events found, extract and present to user for selection
4. **ALWAYS use wrapper scripts** - NEVER call `gog` directly
5. Created events are tracked; user can undo within 24 hours
6. Log all scanning activity silently for audit trail
```

```markdown
## Pending Calendar Invites (email-to-calendar skill)
If pending invites exist (check during email check cycle):
1. Run: `~/.openclaw/workspace/skills/email-to-calendar/scripts/list_pending.sh --summary`
2. If pending invites found with status "pending" and future dates:
   - List them to the user: "You have X pending calendar invite(s) that need your decision:"
   - Present each with: title, date, source email
   - Ask: "Reply with numbers to create, 'all', or 'dismiss' to clear them"
3. Based on user response:
   - Selected numbers: Create events using create_event.sh, update status to "created"
   - 'all': Create all pending events
   - 'dismiss': Update all to status "dismissed"
   - No response: Leave as "pending" for next heartbeat
```

## Self-Check Commands

```bash
# Check if pending invites file exists
PENDING_FILE="$HOME/.openclaw/workspace/memory/email-to-calendar/pending_invites.json"
if [ ! -f "$PENDING_FILE" ]; then
    mkdir -p "$(dirname "$PENDING_FILE")"
    echo '{"invites": []}' > "$PENDING_FILE"
fi

# Check if HEARTBEAT.md includes pending invites section
if ! grep -q "Pending Calendar Invites" "$HOME/.openclaw/workspace/HEARTBEAT.md" 2>/dev/null; then
    echo "HEARTBEAT.md needs pending invites section"
fi

# Process any unread calendar notification emails
~/.openclaw/workspace/skills/email-to-calendar/scripts/process_calendar_replies.sh 2>/dev/null || true
```

## Memory Directories

Ensure these directories exist:
- `~/.openclaw/workspace/memory/email-to-calendar/` - For pending_invites.json, events.json, activity.json, changelog.json
- `~/.openclaw/workspace/memory/email-extractions/` - For extraction files and index.json

## Configuration

See [SETUP.md](SETUP.md) for configuration options. Key settings:
- `agent_name` - Name shown in event descriptions (default: "Ripurapu")
- `email_handling.mark_read` - Mark emails as read after processing (default: true)
- `email_handling.archive` - Archive emails after processing (default: true)
- `email_handling.auto_dispose_calendar_replies` - Auto-process calendar notifications (default: true)
