# LINE Official Account Manager

Operate LINE Official Account Manager (chat.line.biz) via browser automation.

## Features

- ✅ Check unread messages across all chats
- ✅ Reply to customer messages
- ✅ Manage tags and notes for each chat
- ✅ Switch between multiple official accounts

## Installation

### 1. Install the skill

If using ClawHub:
```bash
clawhub install line-oa
```

Or clone manually:
```bash
git clone <repo> ~/.openclaw/workspace/skills/line-oa
```

### 2. Run setup

```bash
cd ~/.openclaw/workspace/skills/line-oa
node scripts/setup.js
```

The setup wizard will:
1. Open https://chat.line.biz/ in your browser
2. Guide you to log in and select your official account
3. Ask you to copy and paste the chat URL
4. Save the configuration to `config.json`

### 3. Start using

Tell your OpenClaw agent:
- "Check LINE for unread messages"
- "Check LINE messages"
- "Reply to [customer name] on LINE"
- "Switch to [LINE Official Account name]"

## Manual Configuration

If you prefer to configure manually, create `config.json`:

```json
{
  "chatUrl": "https://chat.line.biz/U1234567890abcdef1234567890abcdef"
}
```

To find your chat URL:
1. Visit https://manager.line.biz
2. Go to Chat section
3. Copy the full URL from the browser address bar

## Reconfiguration

To change your LINE OA account:
```bash
node scripts/setup.js
```

The wizard will detect existing config and ask if you want to overwrite.

## Troubleshooting

**"config.json not found"**
- Run `node scripts/setup.js` in the skill directory

**"Session expired" or login required**
- LINE OA sessions expire after a few hours
- The skill will automatically guide you through re-login

**Browser control issues**
- Make sure OpenClaw browser service is running
- The skill uses `profile:"openclaw"` (isolated browser)
- Never use Chrome relay for LINE OA

## Notes

- This skill uses browser automation (no official LINE API)
- Sessions may expire; re-login required periodically
- Multi-account switching is supported
- All operations are performed through the OpenClaw isolated browser

## License

MIT
