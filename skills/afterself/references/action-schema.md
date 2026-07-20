# Action Plan JSON Schema

## Action Plan

```json
{
  "name": "My Final Messages",
  "actions": [
    { ... },
    { ... }
  ]
}
```

When creating a plan via the vault CLI, pass the `name` and `actions` array. The vault auto-generates `id`, `createdAt`, and `updatedAt`.

---

## Action Types

### message

Send a message on a messaging channel.

```json
{
  "type": "message",
  "channel": "whatsapp",
  "to": "+1234567890",
  "content": "Hey, if you're reading this...",
  "attachments": ["photo.jpg"],
  "delay": "0h"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | `"message"` | yes | |
| `channel` | string | yes | whatsapp, telegram, discord, signal, slack, imessage, webchat, email |
| `to` | string | yes | Recipient identifier (phone, username, email) |
| `content` | string | yes | Message body |
| `attachments` | string[] | no | File paths to attach |
| `delay` | string | yes | When to send: "0h" (immediate), "24h", "7d", etc. |

### email

Send an email.

```json
{
  "type": "email",
  "to": "friend@example.com",
  "subject": "Something I wanted you to know",
  "body": "Full email body here...",
  "attachments": ["document.pdf"],
  "delay": "0h"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | `"email"` | yes | |
| `to` | string | yes | Recipient email |
| `subject` | string | yes | Email subject |
| `body` | string | yes | Email body (plain text) |
| `attachments` | string[] | no | File paths to attach |
| `delay` | string | yes | |

### close_account

Close an online account.

```json
{
  "type": "close_account",
  "service": "Twitter",
  "url": "https://twitter.com/settings/deactivate",
  "method": "browser_automation",
  "instructions": "Click 'Deactivate your account', confirm with password",
  "delay": "24h"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | `"close_account"` | yes | |
| `service` | string | yes | Service name (for logging) |
| `url` | string | yes | URL to navigate to, or support email address for email_request method |
| `method` | string | yes | `"browser_automation"`, `"api"`, or `"email_request"` |
| `instructions` | string | no | Natural language instructions for browser automation |
| `delay` | string | yes | |

### social_post

Post on social media.

```json
{
  "type": "social_post",
  "platform": "twitter",
  "content": "A final message to everyone who made this journey worth it.",
  "media": ["farewell-photo.jpg"],
  "delay": "0h"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | `"social_post"` | yes | |
| `platform` | string | yes | `"twitter"`, `"instagram"`, `"facebook"`, `"linkedin"` |
| `content` | string | yes | Post text |
| `media` | string[] | no | Image/video paths |
| `delay` | string | yes | |

### crypto_transfer

Transfer cryptocurrency.

```json
{
  "type": "crypto_transfer",
  "asset": "ETH",
  "amount": 1.5,
  "toWallet": "0xabc123...",
  "useEscrow": true,
  "chain": "ethereum",
  "delay": "0h"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | `"crypto_transfer"` | yes | |
| `asset` | string | yes | Token symbol (ETH, SOL, BTC, etc.) |
| `amount` | number | yes | Amount to transfer |
| `toWallet` | string | yes | Recipient wallet address |
| `useEscrow` | boolean | yes | Use escrow protocol for trustless transfer |
| `chain` | string | yes | ethereum, solana, bitcoin, etc. |
| `delay` | string | yes | |

### custom

Custom action with optional webhook.

```json
{
  "type": "custom",
  "description": "Notify my lawyer to initiate estate proceedings",
  "webhookUrl": "https://api.example.com/notify",
  "webhookPayload": { "event": "estate_trigger", "ref": "case-123" },
  "delay": "48h"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | `"custom"` | yes | |
| `description` | string | yes | What this action does (for logging and review) |
| `webhookUrl` | string | no | URL to POST to |
| `webhookPayload` | object | no | JSON payload for the webhook |
| `delay` | string | yes | |

---

## Delay Format

Delays use a simple format: `<number><unit>`

| Unit | Meaning | Example |
|---|---|---|
| `m` | Minutes | `30m` |
| `h` | Hours | `24h` |
| `d` | Days | `7d` |

Actions are sorted by delay before execution. Immediate actions (`0h`) run first, then delayed actions in order.

---

## Example: Complete Plan

```json
{
  "name": "Final Wishes",
  "actions": [
    {
      "type": "message",
      "channel": "whatsapp",
      "to": "+1555123456",
      "content": "Mom, I love you. I set this up just in case. Everything you need is in the folder on my desk.",
      "delay": "0h"
    },
    {
      "type": "email",
      "to": "lawyer@firm.com",
      "subject": "Estate Activation Notice",
      "body": "This is an automated notice that the digital will protocol has been activated. Please proceed with the instructions in the sealed envelope.",
      "delay": "0h"
    },
    {
      "type": "social_post",
      "platform": "twitter",
      "content": "If you're seeing this, I'm no longer here. Thank you for everything. Take care of each other.",
      "delay": "24h"
    },
    {
      "type": "close_account",
      "service": "Instagram",
      "url": "https://instagram.com/accounts/remove/request/permanent/",
      "method": "browser_automation",
      "instructions": "Click through the account deletion flow, confirm when prompted",
      "delay": "7d"
    }
  ]
}
```
