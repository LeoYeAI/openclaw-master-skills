---
name: telegram
description: |
  Telegram Bot API integration with managed authentication. Send messages, manage chats, handle updates, and interact with users through your Telegram bot. Use this skill when users want to send messages, create polls, manage bot commands, or interact with Telegram chats. For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
compatibility: Requires network access and valid Maton API key
metadata:
  author: maton
  version: "1.0"
  clawdbot:
    emoji: 🧠
    requires:
      env:
        - MATON_API_KEY
---

# Telegram Bot API

Access the Telegram Bot API with managed authentication. Send messages, photos, polls, locations, and more through your Telegram bot.

## Quick Start

```bash
# Get bot info
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/telegram/:token/getMe')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/telegram/:token/{method}
```

The `:token` placeholder is automatically replaced with your bot token from the connection configuration. Replace `{method}` with the Telegram Bot API method name (e.g., `sendMessage`, `getUpdates`).

## Authentication

All requests require the Maton API key in the Authorization header:

```
Authorization: Bearer $MATON_API_KEY
```

**Environment Variable:** Set your API key as `MATON_API_KEY`:

```bash
export MATON_API_KEY="YOUR_API_KEY"
```

### Getting Your API Key

1. Sign in or create an account at [maton.ai](https://maton.ai)
2. Go to [maton.ai/settings](https://maton.ai/settings)
3. Copy your API key

## Connection Management

Manage your Telegram bot connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=telegram&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'telegram'}).encode()
req = urllib.request.Request('https://ctrl.maton.ai/connections', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Get Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "connection": {
    "connection_id": "e8f5078d-e507-4139-aabe-1615181ea8fc",
    "status": "ACTIVE",
    "creation_time": "2026-02-07T10:37:21.053942Z",
    "last_updated_time": "2026-02-07T10:37:59.881901Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "telegram",
    "metadata": {}
  }
}
```

Open the returned `url` in a browser to complete the bot token configuration.

### Delete Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Specifying Connection

If you have multiple Telegram connections (multiple bots), specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/telegram/:token/getMe')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', 'e8f5078d-e507-4139-aabe-1615181ea8fc')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Bot Information

#### Get Bot Info

```bash
GET /telegram/:token/getMe
```

Returns information about the bot.

**Response:**
```json
{
  "ok": true,
  "result": {
    "id": 8523474253,
    "is_bot": true,
    "first_name": "Maton",
    "username": "maton_bot",
    "can_join_groups": true,
    "can_read_all_group_messages": true,
    "supports_inline_queries": true
  }
}
```

### Getting Updates

#### Get Updates (Long Polling)

```bash
POST /telegram/:token/getUpdates
Content-Type: application/json

{
  "limit": 100,
  "timeout": 30,
  "offset": 625435210
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| offset | Integer | No | First update ID to return |
| limit | Integer | No | Number of updates (1-100, default 100) |
| timeout | Integer | No | Long polling timeout in seconds |
| allowed_updates | Array | No | Update types to receive |

#### Get Webhook Info

```bash
GET /telegram/:token/getWebhookInfo
```

#### Set Webhook

```bash
POST /telegram/:token/setWebhook
Content-Type: application/json

{
  "url": "https://example.com/webhook",
  "allowed_updates": ["message", "callback_query"],
  "secret_token": "your_secret_token"
}
```

#### Delete Webhook

```bash
POST /telegram/:token/deleteWebhook
Content-Type: application/json

{
  "drop_pending_updates": true
}
```

### Sending Messages

#### Send Text Message

```bash
POST /telegram/:token/sendMessage
Content-Type: application/json

{
  "chat_id": 6442870329,
  "text": "Hello, World!",
  "parse_mode": "HTML"
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| chat_id | Integer/String | Yes | Target chat ID or @username |
| text | String | Yes | Message text (1-4096 characters) |
| parse_mode | String | No | `HTML`, `Markdown`, or `MarkdownV2` |
| reply_markup | Object | No | Inline keyboard or reply keyboard |
| reply_parameters | Object | No | Reply to a specific message |

**With HTML Formatting:**

```bash
POST /telegram/:token/sendMessage
Content-Type: application/json

{
  "chat_id": 6442870329,
  "text": "<b>Bold</b> and <i>italic</i> with <a href=\"https://example.com\">link</a>",
  "parse_mode": "HTML"
}
```

**With Inline Keyboard:**

```bash
POST /telegram/:token/sendMessage
Content-Type: application/json

{
  "chat_id": 6442870329,
  "text": "Choose an option:",
  "reply_markup": {
    "inline_keyboard": [
      [
        {"text": "Option 1", "callback_data": "opt1"},
        {"text": "Option 2", "callback_data": "opt2"}
      ],
      [
        {"text": "Visit Website", "url": "https://example.com"}
      ]
    ]
  }
}
```

#### Send Photo

```bash
POST /telegram/:token/sendPhoto
Content-Type: application/json

{
  "chat_id": 6442870329,
  "photo": "https://example.com/image.jpg",
  "caption": "Image caption"
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| chat_id | Integer/String | Yes | Target chat ID |
| photo | String | Yes | Photo URL or file_id |
| caption | String | No | Caption (0-1024 characters) |
| parse_mode | String | No | Caption parse mode |

#### Send Document

```bash
POST /telegram/:token/sendDocument
Content-Type: application/json

{
  "chat_id": 6442870329,
  "document": "https://example.com/file.pdf",
  "caption": "Document caption"
}
```

#### Send Video

```bash
POST /telegram/:token/sendVideo
Content-Type: application/json

{
  "chat_id": 6442870329,
  "video": "https://example.com/video.mp4",
  "caption": "Video caption"
}
```

#### Send Audio

```bash
POST /telegram/:token/sendAudio
Content-Type: application/json

{
  "chat_id": 6442870329,
  "audio": "https://example.com/audio.mp3",
  "caption": "Audio caption"
}
```

#### Send Location

```bash
POST /telegram/:token/sendLocation
Content-Type: application/json

{
  "chat_id": 6442870329,
  "latitude": 37.7749,
  "longitude": -122.4194
}
```

#### Send Contact

```bash
POST /telegram/:token/sendContact
Content-Type: application/json

{
  "chat_id": 6442870329,
  "phone_number": "+1234567890",
  "first_name": "John",
  "last_name": "Doe"
}
```

#### Send Poll

```bash
POST /telegram/:token/sendPoll
Content-Type: application/json

{
  "chat_id": 6442870329,
  "question": "What is your favorite color?",
  "options": [
    {"text": "Red"},
    {"text": "Blue"},
    {"text": "Green"}
  ],
  "is_anonymous": false
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| chat_id | Integer/String | Yes | Target chat ID |
| question | String | Yes | Poll question (1-300 characters) |
| options | Array | Yes | Poll options (2-10 items) |
| is_anonymous | Boolean | No | Anonymous poll (default true) |
| type | String | No | `regular` or `quiz` |
| allows_multiple_answers | Boolean | No | Allow multiple answers |
| correct_option_id | Integer | No | Correct answer for quiz |

#### Send Dice

```bash
POST /telegram/:token/sendDice
Content-Type: application/json

{
  "chat_id": 6442870329,
  "emoji": "🎲"
}
```

Supported emoji: 🎲 🎯 🎳 🏀 ⚽ 🎰

### Editing Messages

#### Edit Message Text

```bash
POST /telegram/:token/editMessageText
Content-Type: application/json

{
  "chat_id": 6442870329,
  "message_id": 123,
  "text": "Updated message text"
}
```

#### Edit Message Caption

```bash
POST /telegram/:token/editMessageCaption
Content-Type: application/json

{
  "chat_id": 6442870329,
  "message_id": 123,
  "caption": "Updated caption"
}
```

#### Edit Message Reply Markup

```bash
POST /telegram/:token/editMessageReplyMarkup
Content-Type: application/json

{
  "chat_id": 6442870329,
  "message_id": 123,
  "reply_markup": {
    "inline_keyboard": [
      [{"text": "New Button", "callback_data": "new"}]
    ]
  }
}
```

#### Delete Message

```bash
POST /telegram/:token/deleteMessage
Content-Type: application/json

{
  "chat_id": 6442870329,
  "message_id": 123
}
```

### Forwarding & Copying

#### Forward Message

```bash
POST /telegram/:token/forwardMessage
Content-Type: application/json

{
  "chat_id": 6442870329,
  "from_chat_id": 6442870329,
  "message_id": 123
}
```

#### Copy Message

```bash
POST /telegram/:token/copyMessage
Content-Type: application/json

{
  "chat_id": 6442870329,
  "from_chat_id": 6442870329,
  "message_id": 123
}
```

### Chat Information

#### Get Chat

```bash
POST /telegram/:token/getChat
Content-Type: application/json

{
  "chat_id": 6442870329
}
```

#### Get Chat Administrators

```bash
POST /telegram/:token/getChatAdministrators
Content-Type: application/json

{
  "chat_id": -1001234567890
}
```

#### Get Chat Member Count

```bash
POST /telegram/:token/getChatMemberCount
Content-Type: application/json

{
  "chat_id": -1001234567890
}
```

#### Get Chat Member

```bash
POST /telegram/:token/getChatMember
Content-Type: application/json

{
  "chat_id": -1001234567890,
  "user_id": 6442870329
}
```

### Bot Commands

#### Set My Commands

```bash
POST /telegram/:token/setMyCommands
Content-Type: application/json

{
  "commands": [
    {"command": "start", "description": "Start the bot"},
    {"command": "help", "description": "Get help"},
    {"command": "settings", "description": "Open settings"}
  ]
}
```

#### Get My Commands

```bash
GET /telegram/:token/getMyCommands
```

#### Delete My Commands

```bash
POST /telegram/:token/deleteMyCommands
Content-Type: application/json

{}
```

### Bot Profile

#### Get My Description

```bash
GET /telegram/:token/getMyDescription
```

#### Set My Description

```bash
POST /telegram/:token/setMyDescription
Content-Type: application/json

{
  "description": "This bot helps you manage tasks."
}
```

#### Set My Name

```bash
POST /telegram/:token/setMyName
Content-Type: application/json

{
  "name": "Task Bot"
}
```

### Files

#### Get File

```bash
POST /telegram/:token/getFile
Content-Type: application/json

{
  "file_id": "AgACAgQAAxkDAAM..."
}
```

**Response:**
```json
{
  "ok": true,
  "result": {
    "file_id": "AgACAgQAAxkDAAM...",
    "file_unique_id": "AQAD27ExGysnfVBy",
    "file_size": 7551,
    "file_path": "photos/file_0.jpg"
  }
}
```

Download files from: `https://api.telegram.org/file/bot<token>/<file_path>`

### Callback Queries

#### Answer Callback Query

```bash
POST /telegram/:token/answerCallbackQuery
Content-Type: application/json

{
  "callback_query_id": "12345678901234567",
  "text": "Button clicked!",
  "show_alert": false
}
```

## Code Examples

### JavaScript

```javascript
// Send a message
const response = await fetch(
  'https://gateway.maton.ai/telegram/:token/sendMessage',
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      chat_id: 6442870329,
      text: 'Hello from JavaScript!'
    })
  }
);
const data = await response.json();
console.log(data);
```

### Python

```python
import os
import requests

# Send a message
response = requests.post(
    'https://gateway.maton.ai/telegram/:token/sendMessage',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'},
    json={
        'chat_id': 6442870329,
        'text': 'Hello from Python!'
    }
)
print(response.json())
```

### Python (urllib)

```python
import urllib.request, os, json

data = json.dumps({
    'chat_id': 6442870329,
    'text': 'Hello from Python!'
}).encode()
req = urllib.request.Request(
    'https://gateway.maton.ai/telegram/:token/sendMessage',
    data=data,
    method='POST'
)
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
response = json.load(urllib.request.urlopen(req))
print(json.dumps(response, indent=2))
```

## Response Format

All Telegram Bot API responses follow this format:

**Success:**
```json
{
  "ok": true,
  "result": { ... }
}
```

**Error:**
```json
{
  "ok": false,
  "error_code": 400,
  "description": "Bad Request: chat not found"
}
```

## Notes

- `:token` is automatically replaced with your bot token from the connection
- Chat IDs are integers for private chats and can be negative for groups
- All methods support both GET and POST, but POST is recommended for methods with parameters
- Text messages have a 4096 character limit
- Captions have a 1024 character limit
- Polls support 2-10 options
- File uploads require multipart/form-data (use URLs for simplicity)
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Telegram connection or bad request |
| 401 | Invalid or missing Maton API key |
| 429 | Rate limited (Telegram limits vary by method) |
| 4xx/5xx | Passthrough error from Telegram Bot API |

### Troubleshooting: API Key Issues

1. Check that the `MATON_API_KEY` environment variable is set:

```bash
echo $MATON_API_KEY
```

2. Verify the API key is valid by listing connections:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Troubleshooting: Invalid App Name

1. Ensure your URL path starts with `telegram`. For example:

- Correct: `https://gateway.maton.ai/telegram/:token/sendMessage`
- Incorrect: `https://gateway.maton.ai/:token/sendMessage`

## Resources

- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [Available Methods](https://core.telegram.org/bots/api#available-methods)
- [Formatting Options](https://core.telegram.org/bots/api#formatting-options)
- [Inline Keyboards](https://core.telegram.org/bots/api#inlinekeyboardmarkup)
- [Bot Commands](https://core.telegram.org/bots/api#setmycommands)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
