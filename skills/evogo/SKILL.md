---
name: evogo
description: Complete WhatsApp automation via Evolution API Go v3 - instances, messages (text/media/polls/carousels), groups, contacts, chats, communities, newsletters, and real-time webhooks
metadata:
  openclaw:
    requires:
      bins: []
    env:
      EVOGO_API_URL: "Evolution API base URL (e.g., http://localhost:8080 or https://api.yourdomain.com)"
      EVOGO_GLOBAL_KEY: "Global API key for admin operations (instance management)"
      EVOGO_INSTANCE: "Default instance name"
      EVOGO_API_KEY: "Instance-specific token for messaging operations"
---

# evoGo - Evolution API Go v3

Complete WhatsApp automation via Evolution API Go v3. Send messages, manage groups, automate conversations, and integrate webhooks.

---

## 🚀 Quick Start

### 1. Set Environment Variables

```json5
{
  env: {
    EVOGO_API_URL: "http://localhost:8080",        // Your API URL
    EVOGO_GLOBAL_KEY: "your-global-admin-key",     // Admin key (instance mgmt)
    EVOGO_INSTANCE: "my-bot",                      // Instance name
    EVOGO_API_KEY: "your-instance-token"           // Instance token (messaging)
  }
}
```

### 2. Create Instance & Connect

```bash
# Create instance
curl -X POST "$EVOGO_API_URL/instance/create" \
  -H "apikey: $EVOGO_GLOBAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-bot",
    "token": "my-secret-token",
    "qrcode": true
  }'

# Connect & get QR code
curl -X POST "$EVOGO_API_URL/instance/connect" \
  -H "apikey: $EVOGO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"number": ""}'
```

Scan the QR code returned in `qrcode.base64`.

### 3. Send First Message

```bash
curl -X POST "$EVOGO_API_URL/send/text" \
  -H "apikey: $EVOGO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "number": "5511999999999",
    "text": "Hello from evoGo! 🚀"
  }'
```

---

## 🔐 Authentication

Two authentication levels:

| Type | Header | Usage |
|------|--------|-------|
| **Global API Key** | `apikey: xxx` | Admin: create/delete instances, logs |
| **Instance Token** | `apikey: xxx` | Messaging: send messages, groups, contacts |

Set via environment or pass directly in headers.

---

## 📦 Core Concepts

### Phone Number Formats

| Context | Format | Example |
|---------|--------|---------|
| **Sending messages** | International (no +) | `5511999999999` |
| **Group participants** | JID format | `5511999999999@s.whatsapp.net` |
| **Groups** | Group JID | `120363123456789012@g.us` |
| **Newsletters** | Newsletter JID | `120363123456789012@newsletter` |

### Message Delay

Add `delay` (milliseconds) to avoid rate limits:
```json
{
  "number": "5511999999999",
  "text": "Message with delay",
  "delay": 2000
}
```

---

## 🎯 Feature Reference

### 📱 Instance Management

#### Create Instance
```bash
POST /instance/create
Header: apikey: $EVOGO_GLOBAL_KEY

{
  "name": "bot-name",
  "token": "secret-token",
  "qrcode": true,
  "advancedSettings": {
    "rejectCalls": false,
    "groupsIgnore": false,
    "alwaysOnline": true,
    "readMessages": true,
    "readStatus": true,
    "syncFullHistory": true
  }
}
```

**Advanced Settings:**
- `rejectCalls` - Auto-reject calls
- `groupsIgnore` - Ignore group messages
- `alwaysOnline` - Stay online always
- `readMessages` - Auto-mark messages as read
- `readStatus` - Auto-mark status as viewed
- `syncFullHistory` - Sync full chat history

#### Connect / Get QR Code
```bash
POST /instance/connect
GET  /instance/qr
Header: apikey: $EVOGO_API_KEY

{"number": ""}  # Leave empty for QR, or phone number for pairing
```

#### Connection Status
```bash
GET /instance/status
Header: apikey: $EVOGO_API_KEY
```

Returns: `connected`, `connecting`, `disconnected`

#### List All Instances
```bash
GET /instance/all
Header: apikey: $EVOGO_GLOBAL_KEY
```

#### Delete Instance
```bash
DELETE /instance/delete/{instance}
Header: apikey: $EVOGO_GLOBAL_KEY
```

#### Force Reconnect
```bash
POST /instance/forcereconnect/{instance}
Header: apikey: $EVOGO_GLOBAL_KEY

{"number": "5511999999999"}
```

#### Logs
```bash
GET /instance/logs/{instance}?start_date=2026-01-01&end_date=2026-02-10&level=info&limit=100
Header: apikey: $EVOGO_GLOBAL_KEY
```

**Log levels:** `info`, `warn`, `error`, `debug`

---

### 💬 Send Messages

#### Text Message
```bash
POST /send/text

{
  "number": "5511999999999",
  "text": "Hello World!",
  "delay": 1000,
  "mentionsEveryOne": false,
  "mentioned": ["5511888888888@s.whatsapp.net"]
}
```

#### Media (URL)
```bash
POST /send/media

{
  "number": "5511999999999",
  "url": "https://example.com/photo.jpg",
  "type": "image",
  "caption": "Check this out!",
  "filename": "photo.jpg"
}
```

**Media types:**
- `image` - JPG, PNG, GIF, WEBP
- `video` - MP4, AVI, MOV, MKV
- `audio` - MP3, OGG, WAV (sent as voice note/PTT)
- `document` - PDF, DOC, DOCX, XLS, XLSX, PPT, TXT, ZIP
- `ptv` - Round video (Instagram-style)

#### Media (File Upload)
```bash
POST /send/media
Content-Type: multipart/form-data

number=5511999999999
type=image
file=@/path/to/file.jpg
caption=Photo caption
filename=custom-name.jpg
```

#### Poll
```bash
POST /send/poll

{
  "number": "5511999999999",
  "question": "Best language?",
  "options": ["JavaScript", "Python", "Go", "Rust"],
  "selectableCount": 1
}
```

**Get poll results:**
```bash
GET /polls/{messageId}/results
```

#### Sticker
```bash
POST /send/sticker

{
  "number": "5511999999999",
  "sticker": "https://example.com/sticker.webp"
}
```

Auto-converts images to WebP format.

#### Location
```bash
POST /send/location

{
  "number": "5511999999999",
  "latitude": -23.550520,
  "longitude": -46.633308,
  "name": "Avenida Paulista",
  "address": "Av. Paulista, São Paulo - SP"
}
```

#### Contact
```bash
POST /send/contact

{
  "number": "5511999999999",
  "vcard": {
    "fullName": "João Silva",
    "phone": "5511988888888",
    "organization": "Company XYZ",
    "email": "joao@example.com"
  }
}
```

#### Carousel
```bash
POST /send/carousel

{
  "number": "5511999999999",
  "body": "Main carousel text",
  "footer": "Footer text",
  "cards": [
    {
      "header": {
        "title": "Card 1",
        "subtitle": "Subtitle",
        "imageUrl": "https://example.com/img1.jpg"
      },
      "body": {"text": "Card description"},
      "footer": "Card footer",
      "buttons": [
        {
          "displayText": "Click Me",
          "id": "btn1",
          "type": "REPLY"
        }
      ]
    }
  ]
}
```

**Button types:**
- `REPLY` - Simple reply
- `URL` - Opens link
- `CALL` - Initiates call
- `COPY` - Copies text

---

### 📨 Message Operations

#### React to Message
```bash
POST /message/react

{
  "number": "5511999999999",
  "reaction": "👍",
  "id": "MESSAGE_ID",
  "fromMe": false,
  "participant": "5511888888888@s.whatsapp.net"  # Required in groups
}
```

**Reactions:** `👍`, `❤️`, `😂`, `😮`, `😢`, `🙏`, or `"remove"`

#### Typing/Recording Indicator
```bash
POST /message/presence

{
  "number": "5511999999999",
  "state": "composing",
  "isAudio": false
}
```

**States:**
- `composing` + `isAudio: false` → "typing..."
- `composing` + `isAudio: true` → "recording audio..."
- `paused` → Stops indicator

#### Mark as Read
```bash
POST /message/markread

{
  "number": "5511999999999",
  "id": ["MESSAGE_ID_1", "MESSAGE_ID_2"]
}
```

#### Download Media
```bash
POST /message/downloadmedia

{
  "message": {}  # Full message object from webhook
}
```

Returns base64-encoded media.

#### Edit Message
```bash
POST /message/edit

{
  "chat": "5511999999999@s.whatsapp.net",
  "messageId": "MESSAGE_ID",
  "message": "Edited text"
}
```

**Limitations:**
- Text messages only
- Your messages only
- ~15 minute time limit

#### Delete Message
```bash
POST /message/delete

{
  "chat": "5511999999999@s.whatsapp.net",
  "messageId": "MESSAGE_ID"
}
```

**Limitations:**
- Your messages only
- ~48 hour time limit

#### Get Message Status
```bash
POST /message/status

{
  "id": "MESSAGE_ID"
}
```

Returns delivery/read status.

---

### 👥 Group Management

#### List Groups
```bash
GET /group/list        # Basic info (JID + name)
GET /group/myall       # Full info (participants, settings, etc)
```

#### Get Group Info
```bash
POST /group/info

{
  "groupJid": "120363123456789012@g.us"
}
```

#### Create Group
```bash
POST /group/create

{
  "groupName": "My Team",
  "participants": [
    "5511999999999@s.whatsapp.net",
    "5511888888888@s.whatsapp.net"
  ]
}
```

**Requirements:**
- Name: max 25 characters
- Participants: minimum 1

#### Manage Participants
```bash
POST /group/participant

{
  "groupJid": "120363123456789012@g.us",
  "action": "add",
  "participants": ["5511999999999@s.whatsapp.net"]
}
```

**Actions:**
- `add` - Add members
- `remove` - Remove members
- `promote` - Make admin
- `demote` - Remove admin

#### Update Group Settings
```bash
POST /group/settings

{
  "groupJid": "120363123456789012@g.us",
  "action": "announcement"
}
```

**Settings:**
- `announcement` / `not_announcement` - Only admins send messages
- `locked` / `unlocked` - Only admins edit group info
- `approval_on` / `approval_off` - Require approval to join
- `admin_add` / `all_member_add` - Who can add members

#### Get Invite Link
```bash
POST /group/invitelink

{
  "groupJid": "120363123456789012@g.us",
  "reset": false
}
```

Set `reset: true` to revoke old link and generate new one.

#### Join Group
```bash
POST /group/join

{
  "code": "https://chat.whatsapp.com/XXXXXX"
}
```

Accepts full link or just the code.

#### Leave Group
```bash
POST /group/leave

{
  "groupJid": "120363123456789012@g.us"
}
```

#### Manage Join Requests
```bash
# Get pending requests
POST /group/requests
{
  "groupJid": "120363123456789012@g.us"
}

# Approve/Reject
POST /group/requests/action
{
  "groupJid": "120363123456789012@g.us",
  "action": "approve",
  "participants": ["5511999999999@s.whatsapp.net"]
}
```

**Actions:** `approve`, `reject`

#### Update Group Metadata
```bash
# Set photo
POST /group/photo
{
  "groupJid": "120363123456789012@g.us",
  "image": "https://example.com/photo.jpg"
}

# Set name
POST /group/name
{
  "groupJid": "120363123456789012@g.us",
  "name": "New Group Name"
}

# Set description
POST /group/description
{
  "groupJid": "120363123456789012@g.us",
  "description": "New description"
}
```

---

### 💬 Chat Management

#### Pin/Unpin Chat
```bash
POST /chat/pin
POST /chat/unpin

{
  "chat": "5511999999999@s.whatsapp.net"
}
```

#### Archive/Unarchive Chat
```bash
POST /chat/archive
POST /chat/unarchive

{
  "chat": "5511999999999@s.whatsapp.net"
}
```

#### Mute/Unmute Chat
```bash
POST /chat/mute
POST /chat/unmute

{
  "chat": "5511999999999@s.whatsapp.net"
}
```

#### Sync History
```bash
POST /chat/history-sync-request
```

Requests full chat history sync (may take time).

---

### 👤 User & Profile

#### Get User Info
```bash
POST /user/info

{
  "number": ["5511999999999", "5511888888888"],
  "formatJid": true
}
```

Returns: status, profile photo, verified badge, linked devices, etc.

#### Check WhatsApp Registration
```bash
POST /user/check

{
  "number": ["5511999999999", "5511888888888"]
}
```

Returns: `isInWhatsapp` (true/false) for each number.

#### Get Profile Picture
```bash
POST /user/avatar

{
  "number": "5511999999999",
  "preview": false
}
```

**Preview options:**
- `false` - Full resolution
- `true` - Low resolution preview

#### Get Contacts
```bash
GET /user/contacts
```

Lists all saved contacts.

#### Privacy Settings
```bash
# Get privacy settings
GET /user/privacy

# Set privacy settings
POST /user/privacy
{
  "groupAdd": "all",
  "lastSeen": "contacts",
  "status": "all",
  "profile": "all",
  "readReceipts": "all",
  "callAdd": "all",
  "online": "match_last_seen"
}
```

**Options:** `all`, `contacts`, `contact_blacklist`, `none`, `match_last_seen` (online only)

#### Block/Unblock Contact
```bash
POST /user/block
POST /user/unblock

{
  "number": "5511999999999"
}

# Get block list
GET /user/blocklist
```

#### Update Profile
```bash
# Set profile picture
POST /user/profilePicture
{
  "image": "https://example.com/photo.jpg"
}

# Set profile name
POST /user/profileName
{
  "name": "My Name"
}

# Set status/about
POST /user/profileStatus
{
  "status": "My custom status"
}
```

**Limits:**
- Name: 25 characters max
- Status: 139 characters max

---

### 🏷️ Labels (Tags)

#### Add Label
```bash
# To chat
POST /label/chat
{
  "jid": "5511999999999@s.whatsapp.net",
  "labelId": "1"
}

# To message
POST /label/message
{
  "jid": "5511999999999@s.whatsapp.net",
  "labelId": "1",
  "messageId": "MESSAGE_ID"
}
```

#### Remove Label
```bash
POST /unlabel/chat
POST /unlabel/message

{
  "jid": "5511999999999@s.whatsapp.net",
  "labelId": "1",
  "messageId": "MESSAGE_ID"  # Only for /unlabel/message
}
```

#### Edit Label
```bash
POST /label/edit

{
  "labelId": "1",
  "name": "New Label Name"
}
```

#### List Labels
```bash
GET /label
```

---

### 🏘️ Communities

#### Create Community
```bash
POST /community/create

{
  "communityName": "My Community",
  "description": "Optional description"
}
```

#### Add/Remove Groups
```bash
POST /community/add
{
  "communityJID": "120363123456789012@g.us",
  "groupJID": ["120363111111111111@g.us"]
}

POST /community/remove
{
  "communityJID": "120363123456789012@g.us",
  "groupJID": ["120363111111111111@g.us"]
}
```

---

### 📢 Newsletters (Channels)

#### Create Newsletter
```bash
POST /newsletter/create

{
  "name": "My Channel",
  "description": "Optional description"
}
```

#### List Newsletters
```bash
GET /newsletter/list
```

#### Get Newsletter Info
```bash
POST /newsletter/info

{
  "jid": "120363123456789012@newsletter"
}
```

#### Subscribe
```bash
POST /newsletter/subscribe

{
  "jid": "120363123456789012@newsletter"
}
```

#### Get Newsletter Messages
```bash
POST /newsletter/messages

{
  "jid": "120363123456789012@newsletter",
  "limit": 50
}
```

#### Get Invite Link Info
```bash
POST /newsletter/link

{
  "key": "INVITE_KEY"
}
```

---

### 📞 Call Management

#### Reject Call
```bash
POST /call/reject

# Webhook payload from call event
```

Use with webhook automation to auto-reject calls.

---

## 🎬 Common Workflows

### Broadcast Message to Multiple Contacts
```bash
for number in 5511999999999 5511888888888 5511777777777; do
  curl -X POST "$EVOGO_API_URL/send/text" \
    -H "apikey: $EVOGO_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"number\": \"$number\",
      \"text\": \"Broadcast message\",
      \"delay\": 2000
    }"
done
```

### Send Image with Mentions (Groups)
```bash
curl -X POST "$EVOGO_API_URL/send/media" \
  -H "apikey: $EVOGO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "number": "120363123456789012@g.us",
    "url": "https://example.com/report.jpg",
    "type": "image",
    "caption": "Report ready! @5511999999999 please review",
    "mentionedJid": ["5511999999999@s.whatsapp.net"]
  }'
```

### Auto-Create Group + Welcome Message
```bash
# 1. Create group
GROUP_JID=$(curl -s -X POST "$EVOGO_API_URL/group/create" \
  -H "apikey: $EVOGO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "groupName": "Team Alpha",
    "participants": ["5511999999999@s.whatsapp.net"]
  }' | jq -r '.groupJid')

# 2. Send welcome message
curl -X POST "$EVOGO_API_URL/send/text" \
  -H "apikey: $EVOGO_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"number\": \"$GROUP_JID\",
    \"text\": \"Welcome to Team Alpha! 🎉\"
  }"
```

### Check Multiple Numbers
```bash
curl -X POST "$EVOGO_API_URL/user/check" \
  -H "apikey: $EVOGO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "number": [
      "5511999999999",
      "5511888888888",
      "5511777777777"
    ]
  }'
```

---

## ⚠️ Rate Limits & Best Practices

### Delays
Always add delays between messages:
```json
{"delay": 2000}  // 2 seconds
```

**Recommended:**
- 1-2 seconds between individual messages
- 3-5 seconds between mass sends
- Exponential backoff on errors

### Error Handling

**HTTP Status Codes:**
- `200` - Success
- `400` - Bad request (check parameters)
- `401` - Unauthorized (check API key)
- `404` - Not found (instance/resource doesn't exist)
- `500` - Server error

**Common Issues:**

| Error | Solution |
|-------|----------|
| Instance not connected | Run `POST /instance/connect` |
| Invalid phone format | Use international without `+`: `5511999999999` |
| Message not sent | Check `GET /instance/status` |
| Group operation failed | Verify you're admin (for admin operations) |

---

## 🔗 Webhooks

Configure webhooks to receive real-time events:
- Message received
- Message sent
- Connection status
- Group updates
- Calls received
- And more...

Use `POST /webhook/set` endpoint to configure webhook URL (see Postman collection for details).

---

## 🧪 Troubleshooting

### Instance Won't Connect
```bash
# 1. Check if instance exists
GET /instance/all

# 2. Force reconnect
POST /instance/forcereconnect/{instance}

# 3. Check logs
GET /instance/logs/{instance}?level=error
```

### Messages Not Sending
1. Verify connection: `GET /instance/status`
2. Check phone format (no `+` or spaces)
3. Ensure recipient has WhatsApp
4. Verify API key is correct

### Group Operations Failing
1. Check you're admin (for admin operations)
2. Verify group JID format: `xxxxx@g.us`
3. Ensure participants use format: `number@s.whatsapp.net`

---

## 📚 Resources

- **Evolution API Go:** https://github.com/EvolutionAPI/evolution-api
- **WhatsApp Business API:** https://developers.facebook.com/docs/whatsapp
- **JID Format Guide:** `number@s.whatsapp.net` for users, `xxxxx@g.us` for groups

---

## 🆕 Known Limitations

**Not Working (v3.0):**
- `/send/button` - Interactive buttons (deprecated by WhatsApp)
- `/send/list` - Interactive lists (deprecated by WhatsApp)

These endpoints exist but are non-functional due to WhatsApp API changes.

---

## 💡 Tips

1. **Always check status** before operations
2. **Use delays** to avoid rate limits (1-2s minimum)
3. **Store tokens securely** in environment variables
4. **Handle disconnects** with automatic reconnection
5. **Validate numbers** before sending
6. **Use webhooks** for real-time event handling
7. **Monitor logs** for troubleshooting
8. **Test with small groups** before mass operations

---

**evoGo** simplifies WhatsApp automation with Evolution API Go v3. For advanced features, check the full Postman collection or API documentation.
