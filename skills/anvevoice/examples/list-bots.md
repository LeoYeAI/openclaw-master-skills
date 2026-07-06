# Example: Listing Bots

## User Prompt
> "Show me all my AnveVoice bots"

## Agent Action

```json
{
  "tool": "list_bots",
  "arguments": { "limit": 10 }
}
```

## Expected Response

```json
{
  "success": true,
  "data": {
    "bots": [
      {
        "id": "abc-123",
        "name": "Support Bot",
        "status": "active",
        "bot_type": "support",
        "created_at": "2025-01-15T10:00:00Z"
      },
      {
        "id": "def-456",
        "name": "Sales Assistant",
        "status": "paused",
        "bot_type": "sales",
        "created_at": "2025-02-01T14:30:00Z"
      }
    ],
    "total": 2
  }
}
```

## Agent Response
> You have 2 bots:
> 1. **Support Bot** — Active, created Jan 15
> 2. **Sales Assistant** — Paused, created Feb 1
>
> Would you like to see analytics for either bot, or activate the Sales Assistant?
