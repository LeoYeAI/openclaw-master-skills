---
name: buffy-reminder-dispatch
description: "Dispatch Buffy reminders to Clawbot or other chat channels when they fire"
metadata: {"openclaw":{"emoji":"⏰","events":["reminder:sent"]}}
---

# Buffy Reminder Dispatch Hook

Routes due Buffy reminders into Clawbot (or another chat channel) so users receive announcements
at the scheduled time.

## What It Does

- Listens for Buffy backend `reminder:sent` events.
- Reads the reminder payload (activity title, type, user ID, and any channel identifiers such as
  Telegram chat ID or Clawbot user handle).
- Sends a user-facing notification through the configured channel (for example, posting a message
  via Clawbot) with a concise reminder like:

  > "⏰ Reminder: Time for your run."  
  > "⏰ Reminder: 7pm meeting is starting."

## Expected Event Payload

Implementations should expect the `payload` field of the event to mirror Buffy’s
`ReminderMessage` structure:

- `activity_id: string`
- `user_id: string`
- `type: string` (activity type, e.g. `habit`, `task`, or `routine`)
- `title: string` (human-readable activity title)
- Optional channel identifiers, such as:
  - `telegram_chat_id: string`
  - `clawbot_user_id: string` (if your integration adds this)

Gateways or OpenClaw glue code can map `user_id` to the appropriate downstream channel identifiers.

## Suggested Behavior

An implementation of this hook can:

1. Inspect the event payload to determine which channel(s) to use (Clawbot, Telegram, etc.).
2. Construct a short, friendly reminder message, for example:

   - `⏰ Buffy reminder: {{title}} ({{type}})`

3. Call the appropriate channel API or tool (for example, Clawbot’s send-message endpoint) with:

   - Target user or chat ID.
   - The formatted reminder text.

4. Optionally log dispatch results for observability (success/failure per channel).

## Enabling

In your OpenClaw project (where the Buffy skill is installed), place this file in the hooks
directory (for example `.openclaw/hooks/buffy-reminder-dispatch.md`) and run:

```bash
openclaw hooks enable buffy-reminder-dispatch
```

