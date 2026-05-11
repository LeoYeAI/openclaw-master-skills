# Telegram Bot API Field Notes

## 1) Base URL and request style
- Base format: `https://api.telegram.org/bot<token>/<method>`
- Use GET or POST with JSON or form-encoded payloads.
- File uploads use `multipart/form-data` and `attach://` references.

## 2) Updates and delivery models
### Long polling
- `getUpdates` delivers updates with an `offset` cursor and `timeout`.

### Webhook
- `setWebhook` switches the bot to webhook mode.
- Webhook URLs must be HTTPS. Check the official docs for port restrictions.

### Update types (examples)
- `message`, `edited_message`, `channel_post`, `edited_channel_post`
- `inline_query`, `chosen_inline_result`, `callback_query`
- `shipping_query`, `pre_checkout_query`, `poll`, `poll_answer`

Use `allowed_updates` to limit which updates you receive.

## 3) High-traffic-safe patterns
- Use `allowed_updates` to reduce noise.
- Keep handlers idempotent (Telegram may retry).
- Return quickly from webhooks; process heavy work async.

## 4) Common methods (non-exhaustive)
- `getMe`, `getUpdates`, `setWebhook`
- `sendMessage`, `editMessageText`, `deleteMessage`
- `sendPhoto`, `sendDocument`, `sendChatAction`
- `answerCallbackQuery`, `answerInlineQuery`

## 5) Common fields (non-exhaustive)
### sendMessage
- `chat_id`, `text`, `parse_mode`
- `entities`, `disable_web_page_preview`
- `reply_markup` (inline keyboard, reply keyboard)

### reply_markup (inline keyboard)
- `inline_keyboard`: array of button rows
- Buttons can contain `text` + `callback_data` or `url`

### callback_query
- `id`, `from`, `message`, `data`

### sendChatAction
- `action`: `typing`, `upload_photo`, `upload_document`, `upload_video`, `choose_sticker`

## 6) Command UX checklist
- `/start`: greet, explain features, and show main commands.
- `/help`: include short examples and support contact.
- `/settings`: show toggles with inline keyboards.
- `/status`: show recent job results or queue size.

## 7) Error handling
- `429`: back off and retry.
- `400`: validate chat_id, message length, and formatting.
- `403`: bot blocked or chat not accessible.

## 8) Reference links
- https://core.telegram.org/bots/api
- https://core.telegram.org/bots/faq
