# OpenClaw Channel Troubleshooting Reference

Per-channel deep diagnostics and failure signatures. Use this when messages aren't flowing or channels behave unexpectedly.

## Table of Contents

- [Universal Command Ladder](#universal-command-ladder)
- [WhatsApp Deep Troubleshooting](#whatsapp-deep-troubleshooting)
- [Telegram Deep Troubleshooting](#telegram-deep-troubleshooting)
- [Discord Deep Troubleshooting](#discord-deep-troubleshooting)
- [Slack Deep Troubleshooting](#slack-deep-troubleshooting)
- [Pairing System](#pairing-system)
- [Group Chat Troubleshooting](#group-chat-troubleshooting)

## Universal Command Ladder

Always start here:

```bash
openclaw status                    # 1. Quick overview
openclaw gateway status            # 2. Daemon running? RPC ok?
openclaw logs --follow             # 3. Watch for errors
openclaw doctor                    # 4. Config/service diagnostics
openclaw channels status --probe   # 5. Per-channel probes
```

Expected healthy output:
- `Runtime: running`
- `RPC probe: ok`
- Channel probes show `connected/ready`

## WhatsApp Deep Troubleshooting

### Setup

```bash
# Step 1: Configure access policy
openclaw config set channels.whatsapp.dmPolicy '"pairing"'
openclaw config set channels.whatsapp.allowFrom '["+15551234567"]' --json

# Step 2: Link via QR
openclaw channels login --channel whatsapp
# For specific account:
openclaw channels login --channel whatsapp --account work

# Step 3: Start and approve
openclaw gateway
openclaw pairing list whatsapp
openclaw pairing approve whatsapp <CODE>
```

### Deployment Patterns

| Pattern | Config | Notes |
|---|---|---|
| Dedicated number (recommended) | `dmPolicy: "allowlist"` | Separate WhatsApp identity |
| Personal number | `dmPolicy: "allowlist"`, `selfChatMode: true` | Add your own number to `allowFrom` |

### Failure Signatures

| Symptom | Log Hint | Fix |
|---|---|---|
| Not linked / QR required | No creds on disk | `openclaw channels login --channel whatsapp` |
| Linked but disconnected / reconnect loop | Connection drops | `openclaw doctor`, check logs, try re-login |
| No replies to DMs | `pairing request` | Check `openclaw pairing list whatsapp`, approve sender |
| Group messages ignored | `drop guild message (mention required)` | Check `requireMention`, `groupPolicy`, `groupAllowFrom`, `groups` allowlist |
| No active listener when sending | Outbound send fails | Ensure gateway is running and WhatsApp socket is active |
| Self-chat confusion | Messages to yourself loop | Use dedicated number, or set `selfChatMode: true` |

### WhatsApp Config Keys

- Access: `dmPolicy`, `allowFrom`, `groupPolicy`, `groupAllowFrom`, `groups`
- Delivery: `textChunkLimit`, `chunkMode`, `mediaMaxMb`, `sendReadReceipts`, `ackReaction`
- Multi-account: `accounts.<id>.enabled`, `accounts.<id>.authDir`
- Operations: `configWrites`, `debounceMs`
- Credential path: `~/.openclaw/credentials/whatsapp/<accountId>/creds.json`

### Runtime Model

- Gateway owns the WhatsApp socket and reconnect loop
- Only one session per Gateway (Baileys constraint)
- Status and broadcast chats (`@status`, `@broadcast`) are ignored
- Use Bun runtime with caution — Node.js recommended for WhatsApp

## Telegram Deep Troubleshooting

### Setup

```bash
# Step 1: Create bot with @BotFather
# /newbot → get token

# Step 2: Configure
openclaw config set channels.telegram.enabled true --json
openclaw config set channels.telegram.botToken '"123:abc"' --json
# Or use env: TELEGRAM_BOT_TOKEN=...

# Step 3: BotFather settings
# /setprivacy → Disable (for group messages without @mention)
# /setjoingroups → Allow (for group adds)

# Step 4: Start and approve
openclaw gateway
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

### Finding User IDs

Telegram user IDs are numeric. Find yours:
- Forward a message from yourself to @userinfobot
- Or use `openclaw pairing list telegram` to see pending IDs

### Failure Signatures

| Symptom | Log Hint | Fix |
|---|---|---|
| Bot doesn't respond to group messages | `mention required` | `requireMention=false` + BotFather `/setprivacy` → Disable, then remove+re-add bot to group |
| Bot not seeing messages at all | No inbound logs | Check `channels.telegram.groups` has `"*"`, verify bot in group |
| `/start` gets no reply | `pairing request` | `openclaw pairing list telegram`, approve sender |
| Commands partially work | `pairing` / `allowFrom` | Authorize sender identity even when `groupPolicy: "open"` |
| `setMyCommands failed` | DNS/HTTPS error | Check outbound access to `api.telegram.org` |
| `TypeError: fetch failed` | Network error | Recoverable — OpenClaw retries. If persistent, use proxy |
| IPv6 connectivity issues | Intermittent failures | Set `OPENCLAW_TELEGRAM_DISABLE_AUTO_SELECT_FAMILY=1` |
| Allowlist with `@username` not working | Username mismatch | Use numeric ID, not `@username`. Run `openclaw doctor --fix` |

### Telegram Proxy

For VPS with unstable egress:

```json5
{
  channels: {
    telegram: {
      proxy: "socks5://user:pass@proxy-host:1080",
    },
  },
}
```

### Telegram Network Env Overrides

```bash
OPENCLAW_TELEGRAM_DISABLE_AUTO_SELECT_FAMILY=1  # Force IPv4
OPENCLAW_TELEGRAM_DNS_RESULT_ORDER=ipv4first     # IPv4 preference
```

Validate DNS: `dig +short api.telegram.org A && dig +short api.telegram.org AAAA`

### Telegram Features

- Streaming: `channels.telegram.streaming` → `off | partial | block | progress`
- Custom commands via `channels.telegram.customCommands`
- Native commands: `commands.native: "auto"` (default for Telegram)
- Forum topics isolate sessions with `:topic:<threadId>`

## Discord Deep Troubleshooting

### Setup

```bash
# Step 1: Create Discord app
# Discord Developer Portal → New Application → Bot → Message Content Intent

# Step 2: Enable required intents
# - Message Content Intent (REQUIRED)
# - Server Members Intent (recommended)

# Step 3: Generate invite URL with scopes: bot, applications.commands
# Permissions: View Channels, Send Messages, Read Message History, Embed Links, Attach Files

# Step 4: Enable Developer Mode
# User Settings → Advanced → Developer Mode → On
# Right-click server → Copy Server ID
# Right-click avatar → Copy User ID

# Step 5: Configure OpenClaw
openclaw config set channels.discord.token '"YOUR_BOT_TOKEN"' --json
openclaw config set channels.discord.enabled true --json
openclaw gateway restart

# Step 6: Approve pairing
openclaw pairing list discord
openclaw pairing approve discord <CODE>
```

### Guild Workspace Setup

```json5
{
  channels: {
    discord: {
      groupPolicy: "allowlist",
      guilds: {
        YOUR_SERVER_ID: {
          requireMention: true,          // false to respond to all messages
          users: ["YOUR_USER_ID"],       // Who can interact
        },
      },
    },
  },
}
```

### Failure Signatures

| Symptom | Log Hint | Fix |
|---|---|---|
| Bot offline in Discord | No connection | Check token, verify `enabled: true` |
| Bot ignores guild messages | `mention required` | Set `requireMention: false` for the guild |
| Bot ignores DMs | `pairing request` | `openclaw pairing list discord`, approve |
| Group DMs ignored | `groupEnabled=false` | Default behavior — group DMs aren't supported by default |
| Slash commands not registered | `commands.native` mismatch | Ensure `commands.native: "auto"` |
| Commands visible but "not authorized" | Auth policy | Expected — commands enforce OpenClaw auth even when visible in UI |
| Missing Message Content | No content in logs | Enable **Message Content Intent** in Developer Portal |

### Discord Runtime Model

- Reply routing is deterministic: Discord in → Discord out
- Guild channels isolated: `agent:<agentId>:discord:channel:<channelId>`
- DMs share main session by default (`session.dmScope=main`)
- Native slash commands: isolated sessions with `CommandTargetSessionKey`

## Slack Deep Troubleshooting

### Setup (Socket Mode)

```bash
# Step 1: Create Slack app
# Enable Socket Mode
# Create App Token (xapp-...) with connections:write
# Install app → copy Bot Token (xoxb-...)

# Step 2: Subscribe events
# app_mention, message.channels, message.groups, message.im, message.mpim
# reaction_added, reaction_removed, member_joined_channel, etc.

# Step 3: Configure
```

```json5
{
  channels: {
    slack: {
      enabled: true,
      mode: "socket",      // or "http"
      appToken: "xapp-...",
      botToken: "xoxb-...",
    },
  },
}
```

### Slack App Manifest

Copy-paste ready manifest for quick setup — see the full manifest in the Slack section of the OpenClaw docs.

Key scopes needed:
- `chat:write`, `channels:history`, `channels:read`
- `groups:history`, `im:history`, `mpim:history`
- `users:read`, `app_mentions:read`, `assistant:write`
- `reactions:read`, `reactions:write`, `pins:read`, `pins:write`
- `emoji:read`, `commands`, `files:read`, `files:write`

### Failure Signatures

| Symptom | Log Hint | Fix |
|---|---|---|
| No replies in channels | `groupPolicy` | Check channel allowlist, `requireMention`, per-channel users |
| DMs ignored | `dm.enabled`, `dmPolicy` | Check `channels.slack.dm.enabled`, pairing/allowlist |
| Socket mode not connecting | Connection error | Verify `appToken`, check network |
| HTTP mode not receiving | Webhook error | Check signing secret, webhook path, Slack Request URLs |
| Slash commands not firing | `commands.native` | Enable `channels.slack.commands.native: true` or `slashCommand.enabled: true` |

## Pairing System

### DM Pairing

When `dmPolicy: "pairing"` (default), unknown senders receive a one-time code:

- 8 characters, uppercase, no ambiguous chars (0O1I)
- Expires after 1 hour
- Max 3 pending requests per channel (additional requests ignored)
- Bot only sends pairing message once per ~hour per sender

```bash
openclaw pairing list --channel <channel>
openclaw pairing approve <channel> <CODE>
```

### Node Device Pairing

For iOS/Android/macOS/headless nodes:

```bash
# Via Telegram (recommended for iOS)
# Send pairing command to bot

# Approve
openclaw pairing list --channel <channel> --type node
openclaw pairing approve --type node <CODE>
```

### Pairing State

- DM pairings stored in channel allow-store
- Merged with configured `allowFrom`
- If no allowlist configured, linked self number is allowed by default
- Outbound `fromMe` DMs are never auto-paired

## Group Chat Troubleshooting

### Message Flow Decision Tree

```
groupPolicy? disabled → DROP
groupPolicy? allowlist → group in allowlist? NO → DROP
requireMention? YES → mentioned? NO → store for context only
OTHERWISE → REPLY
```

### Common Issues

| Issue | Check | Fix |
|---|---|---|
| All group messages ignored | `groupPolicy: "disabled"` | Change to `"allowlist"` or `"open"` |
| Specific group ignored | Missing from `groups` allowlist | Add group ID or use `"*"` |
| Only mentioned messages get replies | `requireMention: true` | Set `false` or use `/activation always` |
| Sender blocked in group | `groupAllowFrom` / `groupPolicy: "allowlist"` | Add sender to `groupAllowFrom` |

### Mention Gating Config

```json5
{
  channels: {
    whatsapp: {
      groups: {
        "*": { requireMention: true },
        "123@g.us": { requireMention: false },  // Specific group override
      },
    },
  },
  agents: {
    list: [{
      id: "main",
      groupChat: {
        mentionPatterns: ["@openclaw", "openclaw"],
        historyLimit: 50,
      },
    }],
  },
}
```

### Per-Group Tool Restrictions

```json5
{
  channels: {
    telegram: {
      groups: {
        "*": { tools: { deny: ["exec"] } },
        "-1001234567890": {
          tools: { deny: ["exec", "read", "write"] },
          toolsBySender: {
            "id:123456789": { alsoAllow: ["exec"] },  // Admin override
          },
        },
      },
    },
  },
}
```
