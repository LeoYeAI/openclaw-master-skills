# Meta Facebook Inbox

Check Facebook page inbox messages via Meta Business Suite browser automation.

## Features

- ✅ Check inbox messages and unread status
- ✅ Reply to customer messages
- ✅ Get direct conversation URLs for fast access
- ✅ Manage labels (tags) for each conversation
- ✅ Manage notes (internal memos) for each contact
- ✅ Extract messages with images
- ✅ Support multiple Facebook pages with custom aliases

## Installation

### 1. Install the skill

If using ClawHub:
```bash
clawhub install meta-fb-inbox
```

Or clone manually:
```bash
git clone <repo> ~/.openclaw/workspace/skills/meta-fb-inbox
```

### 2. Run setup

```bash
cd ~/.openclaw/workspace/skills/meta-fb-inbox
node scripts/setup.js
```

The setup wizard will:
1. Open https://business.facebook.com/ in your browser
2. Guide you to log in and navigate to your inbox
3. Ask you to copy and paste the inbox URL
4. Save the configuration to `config.json`

### 3. Start using

Tell your OpenClaw agent:
- "Check Facebook inbox"
- "Check FB messages"
- "Reply to [customer name] on Facebook"
- "Add note to [customer name] conversation: [note text]"
- "Get conversation URLs for unread messages"

## Manual Configuration

If you prefer to configure manually, create `config.json`:

```json
{
  "pages": [
    {
      "alias": "fb fanpage",
      "url": "https://business.facebook.com/latest/inbox/all/?&asset_id=123456789012345"
    }
  ]
}
```

To find your inbox URL:
1. Visit https://business.facebook.com/
2. Go to Inbox section
3. Select "All messages"
4. Copy the full URL from the browser address bar (should contain `asset_id`)

### Multiple Pages

To manage multiple Facebook pages, add more entries to the `pages` array:

```json
{
  "pages": [
    {
      "alias": "main page",
      "url": "https://business.facebook.com/latest/inbox/all/?&asset_id=111111111111111"
    },
    {
      "alias": "support page",
      "url": "https://business.facebook.com/latest/inbox/all/?&asset_id=222222222222222"
    }
  ]
}
```

When you ask to check messages without specifying an alias, the agent will use the first page in the array.

## Reconfiguration

To change your Facebook page or add more pages:
```bash
cd ~/.openclaw/workspace/skills/meta-fb-inbox
node scripts/setup.js
```

The wizard will detect existing config and ask if you want to add a new page or overwrite.

## Conversation URLs

One powerful feature of this skill is getting direct conversation URLs. When you ask the agent to check messages, it can optionally retrieve the direct URL for each conversation.

With a conversation URL, you can:
- Jump directly to a conversation without searching
- Save frequently-accessed conversations for instant access
- Reduce API calls and improve response time

Example conversation URL:
```
https://business.facebook.com/latest/inbox/all/?&asset_id=123456789012345&selected_item_id=9876543210&thread_type=FB_MESSAGE
```

The agent can store these URLs and reuse them for fast access later.

## Troubleshooting

**"config.json not found"**
- Run `node scripts/setup.js` in the skill directory

**"Session expired" or login required**
- Meta Business Suite sessions expire periodically
- The skill will detect this and guide you through re-login

**Browser control issues**
- Make sure OpenClaw browser service is running
- The skill uses `profile:"openclaw"` (isolated browser)
- Never use Chrome relay for Meta Business Suite

**Conversation not found**
- Make sure the customer name is spelled correctly
- The skill searches by exact text match in the conversation list
- Try using a direct conversation URL if you have it

**Image download location**
- Images are downloaded to `~/Downloads` by default
- Named with timestamp: `fb-message-YYYYMMDD-HHMMSS.jpg`

## Notes

- This skill uses browser automation (no official Facebook API)
- Sessions may expire; re-login required periodically
- Multi-page management is supported
- All operations are performed through the OpenClaw isolated browser
- Labels and Notes are internal to Meta Business Suite (not visible to customers)

## License

MIT
