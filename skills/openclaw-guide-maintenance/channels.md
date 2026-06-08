# OpenClaw Channel Reference

## Table of Contents

- [Supported Channels](#supported-channels)
- [WhatsApp](#whatsapp)
- [Telegram](#telegram)
- [Discord](#discord)
- [Slack](#slack)
- [Signal](#signal)
- [iMessage / BlueBubbles](#imessage--bluebubbles)
- [Google Chat](#google-chat)
- [Microsoft Teams](#microsoft-teams)
- [Matrix](#matrix)
- [LINE](#line)
- [Other Channels (Plugins)](#other-channels-plugins)
- [Channel CLI Commands](#channel-cli-commands)
- [Group Chat Configuration](#group-chat-configuration)
- [DM Access Policies](#dm-access-policies)
- [Multi-Account Channels](#multi-account-channels)
- [Troubleshooting](#troubleshooting)

## Supported Channels

### Built-in (core)

| Channel | Library | Auth Method | Notes |
|---|---|---|---|
| WhatsApp | Baileys (WhatsApp Web) | QR pairing | Most popular; stores state on disk |
| Telegram | grammY (Bot API) | Bot token | Fastest setup; supports groups |
| Discord | discord.js | Bot token + Gateway | Servers, channels, DMs |
| IRC | irc-framework | Server config | Channels + DMs |
| Slack | Bolt SDK | Workspace app | Workspace apps |
| Signal | signal-cli | signal-cli setup | Privacy-focused |
| BlueBubbles | REST API | macOS server | Recommended for iMessage |
| iMessage (legacy) | imsg CLI | macOS only | Deprecated — use BlueBubbles |

### Plugins (installed separately)

Feishu/Lark, Google Chat, Mattermost, Microsoft Teams, Synology Chat, LINE, Nextcloud Talk, Matrix, IRC, Nostr, Tlon, Twitch, Zalo, Zalo Personal.

Install plugins: `openclaw plugins install <name>`.

## WhatsApp

```bash
# Pair via QR code
openclaw channels login --channel whatsapp

# Check status
openclaw channels status --probe

# Logout
openclaw channels logout --channel whatsapp
```

Config:

```json5
{
  channels: {
    whatsapp: {
      enabled: true,
      allowFrom: ["+15555550123"],       // Phone numbers
      groups: {
        "*": { requireMention: true },   // Mention gating for all groups
      },
    },
  },
}
```

Key notes:
- Only one WhatsApp session per Gateway (Baileys constraint)
- QR pairing required; re-pair if session expires
- WhatsApp stores significant state on disk
- Group messages require mention by default (`requireMention`)

## Telegram

```bash
# Add bot with token
openclaw channels add --channel telegram --token <BOT_TOKEN>

# Or interactive
openclaw channels add --channel telegram
```

Config:

```json5
{
  channels: {
    telegram: {
      enabled: true,
      botToken: "123:abc",
      dmPolicy: "pairing",           // pairing | allowlist | open | disabled
      allowFrom: ["tg:123"],         // Telegram user IDs
      streaming: "partial",          // off | partial | block | progress
      inlineButtons: "dm",           // off | dm | group | all | allowlist
      reactions: "own",              // off | own | all
      webhook: {                     // Optional webhook mode (default: long-polling)
        enabled: false,
        url: "https://example.com/tg",
      },
    },
  },
}
```

Get token from [@BotFather](https://t.me/BotFather).

Features:
- **Live stream preview modes**: `off | partial | block | progress` — controls how partial responses are shown while generating
- **HTML formatting** with automatic Markdown conversion
- **Native commands** via `setMyCommands` — registers bot commands with BotFather automatically
- **Inline buttons**: `off | dm | group | all | allowlist` — attach interactive buttons to messages
- **Forum topics** with per-topic agent routing
- **Audio/video/sticker support** — send and receive media
- **Reaction notifications**: `off | own | all` — control when reactions trigger events
- **Exec approvals** with button-based workflows — approve or deny tool executions via inline buttons
- **Webhook mode** configuration — alternative to default long-polling

Limits:
- `textChunkLimit`: 4000 characters per message
- `mediaMaxMb`: 100 MB max upload
- `historyLimit`: 50 messages context

## Discord

```bash
openclaw channels add --channel discord --token <BOT_TOKEN>
```

Config:

```json5
{
  channels: {
    discord: {
      enabled: true,
      botToken: "your-bot-token",
      dmPolicy: "pairing",
    },
  },
}
```

Requirements:
- Create bot at [Discord Developer Portal](https://discord.com/developers/applications)
- Enable **Message Content Intent**
- Invite bot with proper permissions

Features:
- **Interactive components** — buttons, select menus, and modals
- **Forum channels** with auto-thread creation
- **Voice channel support** with TTS
- **Thread binding** — bind agent conversations to Discord threads
- **Role-based routing** — route messages to different agents based on Discord roles
- **PluralKit support** — recognize and handle PluralKit proxied messages
- **Auto presence** — automatically set bot status/activity

## Slack

```json5
{
  channels: {
    slack: {
      enabled: true,
      botToken: "xoxb-...",
      appToken: "xapp-...",            // Required for Socket Mode (default)
      signingSecret: "...",
      slashCommands: false,            // Native slash commands (disabled by default)
      streaming: "partial",            // off | partial | block | progress
      channelPolicy: "open",          // open | allowlist | disabled
    },
  },
}
```

Uses Bolt SDK with **Socket Mode** as the default connection method. HTTP Events API is available as an alternative.

- **App Token** (`xapp-...`) is required for Socket Mode
- **Native slash commands** — disabled by default; enable to register commands with Slack
- **Interactive replies** — buttons and selects via Block Kit
- **Ack reactions** — adds a reaction emoji during processing to indicate the bot is working
- **Text streaming modes**: `off | partial | block | progress`
- **Channel Policy**: `open` (respond in any channel), `allowlist` (specified channels only), `disabled`

## Signal

Uses `signal-cli`. Requires separate signal-cli setup and registration.

## iMessage / BlueBubbles

**Recommended: BlueBubbles** (full feature support via REST API on macOS server).

Legacy iMessage via `imsg` CLI is deprecated.

## Google Chat

Plugin: `openclaw plugins install @openclaw/googlechat`

Connects via the Google Chat API with HTTP webhooks.

Requirements:
- Google Cloud project with the Chat API enabled
- Service account with appropriate permissions
- Public HTTPS endpoint for receiving webhook events

## Microsoft Teams

```bash
openclaw plugins install @openclaw/msteams
```

Requirements:
- Azure Bot resource with App ID, Client secret, and Tenant ID
- Messaging endpoint must be publicly accessible via HTTPS

## Matrix

```bash
openclaw plugins install @openclaw/matrix
```

Features:
- **E2EE support** with cross-signing
- **Thread support**: `off | inbound | always`
- **Multi-account** — run multiple Matrix bot accounts
- **Bot-to-bot** communication
- **autoJoin** — automatically accept room invitations

## LINE

```bash
openclaw plugins install @openclaw/line
```

Features:
- **Flex cards** — rich interactive message layouts
- **Streaming** with loading animations during generation
- Text chunking: 5000 characters per message
- Media limit: 10 MB

## Other Channels (Plugins)

```bash
openclaw plugins list               # List available plugins
openclaw plugins install <name>     # Install a plugin
openclaw plugins info <name>        # Plugin details
openclaw plugins enable <name>      # Enable plugin
openclaw plugins disable <name>     # Disable plugin
openclaw plugins doctor             # Check plugin health
```

## Channel CLI Commands

```bash
openclaw channels list              # Show configured channels + auth
openclaw channels status            # Channel health (add --probe for extra checks)
openclaw channels logs              # Recent channel logs from gateway
openclaw channels add               # Wizard-style setup
openclaw channels remove            # Disable (--delete to remove config)
openclaw channels login             # Interactive login (WhatsApp)
openclaw channels logout            # Log out of channel
```

Flags:
- `--channel <name>`: whatsapp|telegram|discord|slack|signal|imessage|googlechat|mattermost|msteams
- `--account <id>`: Account ID (default: "default")
- `--name <label>`: Display name

## Group Chat Configuration

```json5
{
  agents: {
    list: [{
      id: "main",
      groupChat: {
        mentionPatterns: ["@openclaw", "openclaw"],
      },
    }],
  },
  channels: {
    whatsapp: {
      groups: {
        "*": { requireMention: true },              // All groups
        "specific-group-id": { requireMention: false }, // Override
      },
    },
  },
}
```

### Per-Group Tool Restrictions

Restrict which tools are available on a per-group (and per-sender) basis:

```json5
{
  channels: {
    telegram: {
      groups: {
        "*": { tools: { deny: ["exec"] } },
        "-1001234567890": {
          tools: { deny: ["exec", "read", "write"] },
          toolsBySender: { "id:123456789": { alsoAllow: ["exec"] } },
        },
      },
    },
  },
}
```

- `tools.deny` — list of tools to block in a group
- `toolsBySender` — override tool restrictions for specific senders (by ID)
- `alsoAllow` — re-enable specific denied tools for a sender

## DM Access Policies

Set per-channel `dmPolicy`:

| Policy | Behavior |
|---|---|
| `"pairing"` (default) | Unknown senders get one-time pairing code |
| `"allowlist"` | Only senders in `allowFrom` |
| `"open"` | Allow all DMs (requires `allowFrom: ["*"]`) |
| `"disabled"` | Ignore all DMs |

Manage pairings:

```bash
openclaw pairing list --channel <channel>
openclaw pairing approve <id>
```

## Multi-Account Channels

Channels like Discord and Telegram support multiple bot accounts:

```bash
openclaw channels add --channel telegram --account alerts --name "Alerts Bot" --token $TOKEN
openclaw channels add --channel discord --account work --name "Work Bot" --token $TOKEN
openclaw channels remove --channel discord --account work --delete
```

When adding a non-default account to a channel using single-account config, OpenClaw auto-migrates to multi-account structure.

## Troubleshooting

### Messages Not Flowing

```bash
openclaw channels status --probe
openclaw pairing list --channel <channel>
openclaw config get channels
openclaw logs --follow
```

Check for:
- `mention required` — group mention policy filtering
- `pairing` / `pending approval` — sender not approved
- `missing_scope`, `Forbidden`, `401/403` — channel auth/permissions issue

### WhatsApp QR Issues

Re-pair: `openclaw channels login --channel whatsapp --verbose`

### Channels Run Simultaneously

All configured channels run at once; OpenClaw routes per chat automatically.
