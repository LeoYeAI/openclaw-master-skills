# KibiBot Agent API — Quick Reference

**Base URL:** `https://api.kibi.bot/agent/v1`  
**Auth:** `X-Api-Key: kb_...` header on all requests

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/me` | User profile & wallet addresses |
| GET | `/skills` | List all agent capabilities (no auth required) |
| POST | `/token/create` | Create token on-chain (async) |
| GET | `/jobs/{job_id}` | Poll token creation status |
| GET | `/token/{address}` | Token price & info (`?chain=base`) |
| GET | `/tokens/created` | Paginated list of tokens you created |
| GET | `/balance/credits` | Kibi Credit balance + agent reload config |
| POST | `/balance/credits/reload` | Reload Kibi Credits from trading wallet |
| POST | `/balance/credits/reload/disable` | Emergency disable agent reload (irreversible by agent) |
| GET | `/balance/wallet` | On-chain wallet balances (main + trading, all chains) |
| GET | `/quota` | Daily token creation quota per chain |

---

## POST /token/create

```json
{
  "name": "MOON",
  "symbol": "MOON",
  "chain": "base",
  "description": "...",
  "image_url": "https://...",
  "platform": "basememe"
}
```

Chains: `base` · `bsc` · `solana` · `base-sepolia`  
Platform (optional): `basememe` · `flap` · `pumpfun` · `clanker`  
Returns (`202`): `{ "job_id": 12345, "status": "pending", "chain": "base", "quota": {...} }`  
Poll `/jobs/{job_id}` until `status` is `completed` or `failed`.

---

## GET /jobs/{job_id}

```json
{
  "job_id": 12345,
  "status": "completed",
  "chain": "base",
  "token_address": "0x...",
  "error": null,
  "created_at": "...",
  "completed_at": "..."
}
```

Status: `pending` | `processing` | `completed` | `failed`

---

## GET /balance/credits

```json
{
  "balance_usd": "4.92",
  "balance_usd_cents": 492,
  "agent_reload": {
    "enabled": true,
    "amount_usd": 5.0,
    "daily_limit_usd": 100.0,
    "chains": ["base"]
  }
}
```

`agent_reload` is `null` if not configured by the user.

---

## POST /balance/credits/reload

Manually reload Kibi Credits from trading wallet. Agent-triggered only (no auto-polling).  
Requires: user has Agent Reload enabled at kibi.bot/credits + key has `reload_enabled`.

```json
{
  "success": true,
  "amount_usd": "5.00",
  "tx_hash": "0x...",
  "new_balance_usd": "9.92",
  "daily_used_usd": "5.00",
  "daily_remaining_usd": "95.00"
}
```

---

## GET /balance/wallet

```json
{
  "evm_main":    { "address": "0x...", "balance_eth": "0.05", "balance_bnb": "0.1", "balance_usdc_base": "10.0", "balance_usdt_bsc": "5.0" },
  "evm_trading": { "address": "0x...", "balance_eth": "0.01", "balance_bnb": "0.0", "balance_usdc_base": "0.0",  "balance_usdt_bsc": "0.0" },
  "solana_main":    { "address": "...", "balance_sol": "0.5",  "balance_usdc_solana": "5.0" },
  "solana_trading": { "address": "...", "balance_sol": "0.05", "balance_usdc_solana": "0.0" }
}
```

Fields are `null` if wallet not set up or RPC unavailable. Check `*_error` fields.

---

## GET /quota

```json
{
  "chains": [
    {
      "chain": "base",
      "free_used_today": 1,
      "free_limit": 3,
      "sponsored_remaining": 2,
      "can_create_paid": true,
      "trading_wallet_balance": "0.01 ETH",
      "trading_wallet_address": "0x..."
    }
  ]
}
```

---

## Kibi LLM Gateway

**Base URL:** `https://llm.kibi.bot`  
Same `X-Api-Key` header. Requires `llm_enabled` on API key.

- `POST /v1/messages` — Anthropic format (Claude models)
- `POST /v1/chat/completions` — OpenAI format (all models)
- `GET /v1/models` — list models
- `GET /v1/models/openclaw` — ready-to-paste OpenClaw config (no auth)

---

## Error Codes

| Code | Meaning |
|------|---------|
| 401 | Missing or invalid API key |
| 402 | Insufficient Kibi Credits or trading wallet balance |
| 403 | Feature not enabled for this key or user |
| 404 | Resource not found |
| 422 | Validation error |
| 429 | Rate limited or daily cap exceeded |
| 500 | Server error — retry |
