# Telegram Request Templates (HTTP)

## sendMessage
POST `/sendMessage`
```json
{
  "chat_id": 123456789,
  "text": "Hello",
  "parse_mode": "HTML",
  "disable_web_page_preview": true
}
```

## editMessageText
POST `/editMessageText`
```json
{
  "chat_id": 123456789,
  "message_id": 42,
  "text": "Updated",
  "parse_mode": "HTML"
}
```

## answerCallbackQuery
POST `/answerCallbackQuery`
```json
{
  "callback_query_id": "1234567890",
  "text": "Saved"
}
```

## setWebhook
POST `/setWebhook`
```json
{
  "url": "https://example.com/telegram/webhook",
  "secret_token": "your-secret",
  "allowed_updates": ["message","callback_query"]
}
```
