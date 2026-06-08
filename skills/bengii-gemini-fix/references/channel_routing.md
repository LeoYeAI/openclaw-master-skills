# Channel Routing Reference

> Source: https://docs.openclaw.ai/channels/channel-routing

## Key Terms

| Term | Meaning |
|---|---|
| **Channel** | `whatsapp`, `telegram`, `discord`, `slack`, `signal`, `imessage`, `webchat`, `mattermost`, `bluebubbles` |
| **AccountId** | Per-channel account instance (when supported) |
| **AgentId** | Isolated workspace + session store ("brain") |
| **SessionKey** | Bucket key for context and concurrency control |

### Default Account
- `channels.<channel>.defaultAccount` chooses which account is used when outbound path has no `accountId`.
- In multi-account setups: must set explicit default (`defaultAccount` or `accounts.default`).

## Session Key Shapes

| Pattern | Example |
|---|---|
| Main DM | `agent:main:main` |
| Group | `agent:main:whatsapp:group:<id>` |
| Channel/Room | `agent:main:discord:channel:<id>` |
| Slack/Discord thread | `...base:thread:<threadId>` |
| Telegram forum topic | `...group:<id>:topic:<topicId>` |

Examples:
```
agent:main:telegram:group:-1001234567890:topic:42
agent:main:discord:channel:123456:thread:987654
```

## Main DM Route Pinning

- Controlled by `session.dmScope` (default: `main`).
- `lastRoute`: uses last DM route.
- When `allowFrom` has exactly one non-wildcard entry that can be normalized to a concrete sender ID, and the inbound DM sender doesn't match — the DM is pinned to that owner.

## Routing Rules (Agent Selection)

Resolution order (first match wins):

1. **Exact peer match** — `bindings` with `peer.kind` + `peer.id`
2. **Parent peer match** — thread inheritance
3. **Guild + roles match** (Discord) — `guildId` + `roles`
4. **Guild match** (Discord) — `guildId`
5. **Team match** (Slack) — `teamId`
6. **Account match** — `accountId` on the channel
7. **Channel match** — any account on that channel (`accountId: "*"`)
8. **Default agent** — `agents.list[].default`, else first list entry, fallback to `main`

## Broadcast Groups (Multiple Agents)

Run multiple agents for the same conversation:
```json5
{
  broadcast: {
    strategy: "parallel",
    "120363403215116621@g.us": ["alfred", "baerbel"],
    "+15555550123": ["support", "logger"],
  },
}
```

## Mattermost Channel

> Source: https://docs.openclaw.ai/channels/mattermost

### Setup
```bash
openclaw plugins install @openclaw/mattermost
```

```json5
{
  channels: {
    mattermost: {
      enabled: true,
      botToken: "mm-token",
      baseUrl: "https://chat.example.com",
      dmPolicy: "pairing",
    },
  },
}
```

### Features
- Native slash commands via plugin
- Access control for DMs (pairing/allowlist)
- Channel/group support
- Reactions and interactive buttons via message tool
- Directory adapter for user resolution
- Multi-account support

## BlueBubbles (iMessage) Channel

> Source: https://docs.openclaw.ai/channels/bluebubbles

### Overview
- Runs on macOS via BlueBubbles helper app ([bluebubbles.app](https://bluebubbles.app))
- Recommended: macOS Sequoia (15); macOS Tahoe (26) works with known limitations
- Communicates via REST API
- Incoming via webhooks; outgoing via REST calls

### Quick Start
```json5
{
  channels: {
    bluebubbles: {
      enabled: true,
      serverUrl: "http://192.168.1.100:1234",
      password: "example-password",
      webhookPath: "/bluebubbles-webhook",
    },
  },
}
```

Point BlueBubbles webhooks to: `https://your-gateway-host:3000/bluebubbles-webhook?password=<password>`

### Security
- Webhook authentication is always required.
- OpenClaw rejects webhook requests without matching `channels.bluebubbles.password`.
- Password checked before reading/parsing webhook bodies.

### Features
- Typing + read receipts
- Reactions (surfaced as system events)
- Edit, unsend, reply threading
- Message effects
- Group management
- Block streaming support
- Media + limits (per WhatsApp-style pipeline)

## See Also

- [channels.md](channels.md) — All channel setup guides
- [channel_troubleshooting.md](channel_troubleshooting.md) — Per-channel troubleshooting
- [multi_agent.md](multi_agent.md) — Multi-agent routing configuration
