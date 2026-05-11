# Telegram Command Playbook

## Command set (professional baseline)
- `/start`: greet, set expectations, and show main actions.
- `/help`: short help + examples.
- `/status`: show last job result, queue length, or uptime.
- `/settings`: show toggles via inline keyboard.
- `/about`: short bot description and support contact.

## Command UX patterns
- Acknowledge fast, then do heavy work asynchronously.
- Prefer short replies with a single call-to-action.
- Always include “what next?” in `/start` and `/help`.

## Inline keyboard patterns
- Use stable callback_data names (e.g., `settings:notifications:on`).
- Keep callbacks idempotent.

## Message style guidelines
- Use MarkdownV2 or HTML consistently; avoid mixing.
- If using MarkdownV2, escape reserved characters.
- Keep single message length under safe limits; split when needed.

## Examples (short)
- `/start` reply: “Hi! I can publish posts and send alerts. Try /help.”
- `/status` reply: “Queue: 2 jobs. Last run: success 2m ago.”
