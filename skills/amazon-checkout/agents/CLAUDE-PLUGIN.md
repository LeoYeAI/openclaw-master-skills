---
name: creditclaw-claude-plugin
version: 1.0.0
updated: 2026-03-18
description: "Claude Desktop/Cowork — plugin-based secure checkout flow."
companion_of: SKILL.md
api_base: https://creditclaw.com/api/v1
credentials: [CREDITCLAW_API_KEY]
---

# Claude Desktop — Plugin-Based Checkout Flow

> **Coming Soon**
>
> This checkout method is under development. When available, the CreditClaw plugin
> will handle secure browser form filling without exposing card details to the agent's context.

## Security Model

The CreditClaw plugin provides a secure card handoff for Claude Desktop and Cowork environments:

- The plugin handles browser-based form filling directly — card details never enter the agent's context
- Triple-secure pre- and post-context scans before compaction ensure no card data leaks
- The agent orchestrates the purchase (requests checkout, gets approval) while the plugin handles the sensitive card entry

## How It Will Work

```
1. Agent requests checkout via POST /bot/rail5/checkout (same as all platforms)
2. Agent waits for owner approval (if required)
3. Agent invokes the CreditClaw plugin with the checkout_id
4. Plugin retrieves the decryption key, decrypts card details internally
5. Plugin fills the merchant's payment form in a secure browser session
6. Plugin confirms the checkout result via the API
7. Plugin returns a success/failure summary to the agent (no card data)
8. Agent announces the result to the owner
```

## Status

This guide will be updated when the CreditClaw plugin is available for installation. In the
meantime, refer to `agents/OPENCLAW.md` for the sub-agent checkout flow or `CHECKOUT-GUIDE.md`
for the platform-agnostic API reference.
