# Polls

> Source: https://docs.openclaw.ai/automation/poll

## Supported Channels

- Telegram
- WhatsApp (web channel)
- Discord
- MS Teams (Adaptive Cards)

## CLI

```bash
# Telegram
openclaw message poll --channel telegram --target 123456789 \
  --poll-question "Ship it?" --poll-option "Yes" --poll-option "No"

openclaw message poll --channel telegram --target -1001234567890:topic:42 \
  --poll-question "Pick a time" --poll-option "10am" --poll-option "2pm" \
  --poll-duration-seconds 300

# WhatsApp
openclaw message poll --target +15555550123 \
  --poll-question "Lunch today?" --poll-option "Yes" --poll-option "No" --poll-option "Maybe"

openclaw message poll --target 123456789@g.us \
  --poll-question "Meeting time?" --poll-option "10am" --poll-option "2pm" --poll-option "4pm" --poll-multi

# Discord
openclaw message poll --channel discord --target channel:123456789 \
  --poll-question "Snack?" --poll-option "Pizza" --poll-option "Sushi"

openclaw message poll --channel discord --target channel:123456789 \
  --poll-question "Plan?" --poll-option "A" --poll-option "B" --poll-duration-hours 48

# MS Teams
openclaw message poll --channel msteams --target conversation:19:abc@thread.tacv2 \
  --poll-question "Lunch?" --poll-option "Pizza" --poll-option "Sushi"
```

## CLI Flags

| Flag | Description |
|---|---|
| `--channel` | `whatsapp` (default), `telegram`, `discord`, or `msteams` |
| `--poll-multi` | Allow selecting multiple options |
| `--poll-duration-hours` | Discord-only (defaults to 24) |
| `--poll-duration-seconds` | Telegram-only (5–600 seconds) |
| `--poll-anonymous` / `--poll-public` | Telegram-only poll visibility |

## Gateway RPC

Method: `poll`

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `to` | string | ✓ | Target ID |
| `question` | string | ✓ | Poll question |
| `options` | string[] | ✓ | Answer options |
| `maxSelections` | number | | Multi-select |
| `durationHours` | number | | Discord-only |
| `durationSeconds` | number | | Telegram-only |
| `isAnonymous` | boolean | | Telegram-only |
| `channel` | string | | Default: `whatsapp` |
| `idempotencyKey` | string | ✓ | Dedup key |

## Agent Tool (Message)

- The message tool can also send polls by including poll parameters in the tool call.
