# Slack Routing Reference

**App name:** `slack`
**Base URL proxied:** `slack.com`

## API Path Pattern

```
/slack/api/{method}
```

## Common Endpoints

### Post Message
```bash
POST /slack/api/chat.postMessage
Content-Type: application/json

{
  "channel": "C0123456789",
  "text": "Hello, world!"
}
```

With blocks:
```bash
POST /slack/api/chat.postMessage
Content-Type: application/json

{
  "channel": "C0123456789",
  "blocks": [
    {"type": "section", "text": {"type": "mrkdwn", "text": "*Bold* and _italic_"}}
  ]
}
```

### List Channels
```bash
GET /slack/api/conversations.list?types=public_channel,private_channel
```

### Get Channel Info
```bash
GET /slack/api/conversations.info?channel=C0123456789
```

### List Messages in Channel
```bash
GET /slack/api/conversations.history?channel=C0123456789&limit=100
```

### Get Thread Replies
```bash
GET /slack/api/conversations.replies?channel=C0123456789&ts=1234567890.123456
```

### List Users
```bash
GET /slack/api/users.list
```

### Get User Info
```bash
GET /slack/api/users.info?user=U0123456789
```

### Search Messages
```bash
GET /slack/api/search.messages?query=keyword
```

### Upload File
```bash
POST /slack/api/files.upload
Content-Type: multipart/form-data

channels=C0123456789
content=file content here
filename=example.txt
```

### Add Reaction
```bash
POST /slack/api/reactions.add
Content-Type: application/json

{
  "channel": "C0123456789",
  "name": "thumbsup",
  "timestamp": "1234567890.123456"
}
```

### Update Message
```bash
POST /slack/api/chat.update
Content-Type: application/json

{
  "channel": "C0123456789",
  "ts": "1234567890.123456",
  "text": "Updated message"
}
```

### Delete Message
```bash
POST /slack/api/chat.delete
Content-Type: application/json

{
  "channel": "C0123456789",
  "ts": "1234567890.123456"
}
```

### Post Thread Reply
```bash
POST /slack/api/chat.postMessage
Content-Type: application/json

{
  "channel": "C0123456789",
  "thread_ts": "1234567890.123456",
  "text": "This is a reply in a thread"
}
```

### Get Channel Members
```bash
GET /slack/api/conversations.members?channel=C0123456789&limit=100
```

### Open DM Conversation
```bash
POST /slack/api/conversations.open
Content-Type: application/json

{
  "users": "U0123456789"
}
```

### Auth Test (get current user/team)
```bash
GET /slack/api/auth.test
```

## Notes

- Authentication is automatic - the router uses the user's OAuth access token
- Channel IDs start with `C` (public), `G` (private/group), or `D` (DM)
- User IDs start with `U`, Team IDs start with `T`
- Message timestamps (`ts`) are used as unique identifiers
- Use `mrkdwn` type for Slack-flavored markdown formatting
- Thread replies use `thread_ts` to reference the parent message

## Resources

- [API Overview](https://api.slack.com/apis)
- [Post Message](https://api.slack.com/methods/chat.postMessage)
- [Update Message](https://api.slack.com/methods/chat.update)
- [Delete Message](https://api.slack.com/methods/chat.delete)
- [List Channels](https://api.slack.com/methods/conversations.list)
- [Get Channel Info](https://api.slack.com/methods/conversations.info)
- [Get Channel Members](https://api.slack.com/methods/conversations.members)
- [Open Conversation](https://api.slack.com/methods/conversations.open)
- [Channel History](https://api.slack.com/methods/conversations.history)
- [Thread Replies](https://api.slack.com/methods/conversations.replies)
- [List Users](https://api.slack.com/methods/users.list)
- [Get User Info](https://api.slack.com/methods/users.info)
- [Auth Test](https://api.slack.com/methods/auth.test)
- [Search Messages](https://api.slack.com/methods/search.messages)
- [Upload File](https://api.slack.com/methods/files.upload)
- [Add Reaction](https://api.slack.com/methods/reactions.add)
- [Block Kit Reference](https://api.slack.com/reference/block-kit)
- [LLM Reference](https://docs.slack.dev/llms.txt)