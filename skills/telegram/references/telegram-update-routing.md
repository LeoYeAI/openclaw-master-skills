# Telegram Update Routing

## Update normalization
- Normalize inbound updates to a single envelope:
  - `update_id`, `chat_id`, `user_id`, `message_id`, `text`, `callback_data`, `type`
- This makes routing logic consistent across message types.

## Routing rules
- If `callback_query` exists, handle callbacks first.
- Else if `message.text` starts with `/`, treat as command.
- Else fall back to default handler (help or menu).

## Safe defaults
- Unknown command: reply with `/help` guidance.
- Unknown callback: answerCallbackQuery with a short notice.

## Idempotency
- Keep a cache of processed `update_id` in case of retries.
- Ensure handlers can be safely re-run.

## Error handling
- On 429: backoff and retry with jitter.
- On 400: validate payload length and parse mode.
