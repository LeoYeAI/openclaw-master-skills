---
name: kibibot
description: Create tokens on-chain, check fee earnings, check Kibi Credit balance, trigger agent credit reload, and interact with KibiBot's Agent API and Kibi LLM Gateway. Use when asked to create a token via KibiBot, check fee earnings across chains and platforms, check KibiBot Kibi Credit balance, check daily token creation quota, reload credits from trading wallet, or make LLM calls through KibiBot's gateway.
---

# KibiBot Skill

Create tokens on-chain, earn trading fees, and use KibiBot's Kibi LLM Gateway — all from natural language commands.

**Version:** 1.5.2  
**Provider:** [KibiBot](https://kibi.bot)  
**Auth:** API key required — get yours at [kibi.bot/settings/api-keys](https://kibi.bot/settings/api-keys)  
**Install:** `install the kibibot skill from https://github.com/KibiAgent/skills/tree/main/kibibot`

---

## Setup

### Step 1 — Get your API key
Go to [kibi.bot/settings/api-keys](https://kibi.bot/settings/api-keys) → Create API Key → copy the `kb_...` key.

> **Permissions:** Base API is always included. Enable **Kibi LLM Gateway** if you want to use AI models. Enable **Agent Reload** if you want the agent to top up your Kibi Credits automatically from your trading wallet.

### Step 2 — Add Kibi Credits (for AI model access)
Go to [kibi.bot/credits](https://kibi.bot/credits) → Add Credit.  
Minimum $1 to start. Credits are consumed per token used.

### Step 3 — Set up Kibi LLM Gateway *(optional)*
> This step registers KibiBot as your agent's AI model provider, so your agent *thinks* using Claude/GPT/Gemini billed to your Kibi Credits — instead of paying Anthropic/OpenAI directly. It's separate from the Agent API skill.
>
> **OpenClaw users:** follow the config below. If you're using LangChain, CrewAI, or any OpenAI-compatible framework, point your `base_url` to `https://llm.kibi.bot/v1` with your `kb_...` API key instead.
>
> **OpenClaw users** — add KibiBot as an LLM provider in `~/.openclaw/openclaw.json`. This is the full config with all available models — you only need to include the models you want to use.

```json
{
  "models": {
    "mode": "merge",
    "providers": {
      "kibi": {
        "baseUrl": "https://llm.kibi.bot",
        "apiKey": "YOUR_KB_API_KEY",
        "api": "openai-completions",
        "models": [
          { "id": "kibi-opus-4-6",              "name": "Claude Opus 4.6",          "api": "anthropic-messages", "contextWindow": 1000000,  "maxTokens": 128000 },
          { "id": "kibi-opus-4-5",              "name": "Claude Opus 4.5",          "api": "anthropic-messages", "contextWindow": 200000,   "maxTokens": 64000  },
          { "id": "kibi-sonnet-4-6",            "name": "Claude Sonnet 4.6",        "api": "anthropic-messages", "contextWindow": 1000000,  "maxTokens": 128000 },
          { "id": "kibi-sonnet-4-5",            "name": "Claude Sonnet 4.5",        "api": "anthropic-messages", "contextWindow": 1000000,  "maxTokens": 64000  },
          { "id": "kibi-haiku-4-5",             "name": "Claude Haiku 4.5",         "api": "anthropic-messages", "contextWindow": 200000,   "maxTokens": 4096   },
          { "id": "kibi-gpt-5-4-pro",           "name": "GPT 5.4 Pro",              "contextWindow": 1050000,    "maxTokens": 16384 },
          { "id": "kibi-gpt-5-4",               "name": "GPT 5.4",                  "contextWindow": 1050000,    "maxTokens": 16384 },
          { "id": "kibi-gpt-5-4-mini",          "name": "GPT 5.4 Mini",             "contextWindow": 400000,     "maxTokens": 16384 },
          { "id": "kibi-gpt-5-4-nano",          "name": "GPT 5.4 Nano",             "contextWindow": 400000,     "maxTokens": 16384 },
          { "id": "kibi-gpt-5-2-pro",           "name": "GPT 5.2 Pro",              "contextWindow": 400000,     "maxTokens": 16384 },
          { "id": "kibi-gpt-5-2",               "name": "GPT 5.2",                  "contextWindow": 400000,     "maxTokens": 16384 },
          { "id": "kibi-gpt-5-2-codex",         "name": "GPT 5.2 Codex",            "contextWindow": 400000,     "maxTokens": 16384 },
          { "id": "kibi-gpt-5-2-chat",          "name": "GPT 5.2 Chat",             "contextWindow": 128000,     "maxTokens": 16384 },
          { "id": "kibi-gemini-3-1-pro",        "name": "Gemini 3.1 Pro",           "contextWindow": 1048576,    "maxTokens": 16384 },
          { "id": "kibi-gemini-3-1-flash-lite", "name": "Gemini 3.1 Flash Lite",    "contextWindow": 1048576,    "maxTokens": 16384 },
          { "id": "kibi-gemini-3-flash",        "name": "Gemini 3 Flash",           "contextWindow": 1048576,    "maxTokens": 16384 },
          { "id": "kibi-gemini-2-5-pro",        "name": "Gemini 2.5 Pro",           "contextWindow": 1048576,    "maxTokens": 8192  },
          { "id": "kibi-gemini-2-5-flash",      "name": "Gemini 2.5 Flash",         "contextWindow": 1048576,    "maxTokens": 8192  },
          { "id": "kibi-grok-4-1",              "name": "Grok 4.1 Fast",            "contextWindow": 2000000,    "maxTokens": 16384 },
          { "id": "kibi-deepseek-v3-2",         "name": "DeepSeek V3.2",            "contextWindow": 164000,     "maxTokens": 16384 },
          { "id": "kibi-kimi-k2-5",             "name": "Kimi K2.5",                "contextWindow": 262144,     "maxTokens": 16384 },
          { "id": "kibi-mimo-v2-pro",           "name": "MiMo-V2-Pro",              "contextWindow": 1048576,    "maxTokens": 16384 },
          { "id": "kibi-mimo-v2-omni",          "name": "MiMo-V2-Omni",             "contextWindow": 262144,     "maxTokens": 16384 },
          { "id": "kibi-mimo-v2-flash",         "name": "MiMo-V2-Flash",            "contextWindow": 262144,     "maxTokens": 16384 },
          { "id": "kibi-seed-2-0-lite",         "name": "Seed 2.0 Lite",            "contextWindow": 262144,     "maxTokens": 16384 },
          { "id": "kibi-seed-2-0-mini",         "name": "Seed 2.0 Mini",            "contextWindow": 262144,     "maxTokens": 16384 },
          { "id": "kibi-qwen-3-coder",          "name": "Qwen3 Coder",              "contextWindow": 262144,     "maxTokens": 16384 },
          { "id": "kibi-qwen-3-5-plus",         "name": "Qwen3.5 Plus",             "contextWindow": 1000000,    "maxTokens": 16384 },
          { "id": "kibi-qwen-3-5-flash",        "name": "Qwen3.5 Flash",            "contextWindow": 1000000,    "maxTokens": 16384 },
          { "id": "kibi-minimax-m2-7",          "name": "MiniMax M2.7",             "contextWindow": 204800,     "maxTokens": 16384 },
          { "id": "kibi-minimax-m2-5",          "name": "MiniMax M2.5",             "contextWindow": 196608,     "maxTokens": 16384 },
          { "id": "kibi-glm-5-turbo",           "name": "GLM 5 Turbo",              "contextWindow": 202752,     "maxTokens": 16384 },
          { "id": "kibi-glm-5",                 "name": "GLM 5",                    "contextWindow": 80000,      "maxTokens": 16384 }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "models": {
        "kibi/kibi-opus-4-6":              { "alias": "kibi-opus-4-6" },
        "kibi/kibi-opus-4-5":              { "alias": "kibi-opus-4-5" },
        "kibi/kibi-sonnet-4-6":            { "alias": "kibi-sonnet-4-6" },
        "kibi/kibi-sonnet-4-5":            { "alias": "kibi-sonnet-4-5" },
        "kibi/kibi-haiku-4-5":             { "alias": "kibi-haiku-4-5" },
        "kibi/kibi-gpt-5-4-pro":           { "alias": "kibi-gpt-5-4-pro" },
        "kibi/kibi-gpt-5-4":               { "alias": "kibi-gpt-5-4" },
        "kibi/kibi-gpt-5-4-mini":          { "alias": "kibi-gpt-5-4-mini" },
        "kibi/kibi-gpt-5-4-nano":          { "alias": "kibi-gpt-5-4-nano" },
        "kibi/kibi-gpt-5-2-pro":           { "alias": "kibi-gpt-5-2-pro" },
        "kibi/kibi-gpt-5-2":               { "alias": "kibi-gpt-5-2" },
        "kibi/kibi-gpt-5-2-codex":         { "alias": "kibi-gpt-5-2-codex" },
        "kibi/kibi-gpt-5-2-chat":          { "alias": "kibi-gpt-5-2-chat" },
        "kibi/kibi-gemini-3-1-pro":        { "alias": "kibi-gemini-3-1-pro" },
        "kibi/kibi-gemini-3-1-flash-lite": { "alias": "kibi-gemini-3-1-flash-lite" },
        "kibi/kibi-gemini-3-flash":        { "alias": "kibi-gemini-3-flash" },
        "kibi/kibi-gemini-2-5-pro":        { "alias": "kibi-gemini-2-5-pro" },
        "kibi/kibi-gemini-2-5-flash":      { "alias": "kibi-gemini-2-5-flash" },
        "kibi/kibi-grok-4-1":              { "alias": "kibi-grok-4-1" },
        "kibi/kibi-deepseek-v3-2":         { "alias": "kibi-deepseek-v3-2" },
        "kibi/kibi-kimi-k2-5":             { "alias": "kibi-kimi-k2-5" },
        "kibi/kibi-mimo-v2-pro":           { "alias": "kibi-mimo-v2-pro" },
        "kibi/kibi-mimo-v2-omni":          { "alias": "kibi-mimo-v2-omni" },
        "kibi/kibi-mimo-v2-flash":         { "alias": "kibi-mimo-v2-flash" },
        "kibi/kibi-seed-2-0-lite":         { "alias": "kibi-seed-2-0-lite" },
        "kibi/kibi-seed-2-0-mini":         { "alias": "kibi-seed-2-0-mini" },
        "kibi/kibi-qwen-3-coder":          { "alias": "kibi-qwen-3-coder" },
        "kibi/kibi-qwen-3-5-plus":         { "alias": "kibi-qwen-3-5-plus" },
        "kibi/kibi-qwen-3-5-flash":        { "alias": "kibi-qwen-3-5-flash" },
        "kibi/kibi-minimax-m2-7":          { "alias": "kibi-minimax-m2-7" },
        "kibi/kibi-minimax-m2-5":          { "alias": "kibi-minimax-m2-5" },
        "kibi/kibi-glm-5-turbo":           { "alias": "kibi-glm-5-turbo" },
        "kibi/kibi-glm-5":                 { "alias": "kibi-glm-5" }
      }
    }
  }
}
```

> **Note:** The `agents.defaults.models` block is required — it allowlists the models and registers aliases so both the model dropdown picker and `/model` command work correctly. The `alias` must match the model `id` exactly.

Set as default model (optional):
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "kibi/kibi-sonnet-4-6"
      }
    }
  }
}
```

Then restart OpenClaw:
```
openclaw gateway restart
```

Switch models using the dropdown picker or `/model` command:
```
/model kibi-opus-4-6
/model kibi-sonnet-4-6
/model kibi-haiku-4-5
/model kibi-gpt-5-4
/model kibi-gemini-3-1-pro
/model kibi-grok-4-1
/model kibi-deepseek-v3-2
```

### Available Models

**Anthropic**
| Model ID | Context |
|---|---|
| `claude-opus-4-6` | 1M |
| `claude-opus-4-5` | 200k |
| `claude-sonnet-4-6` | 1M |
| `claude-sonnet-4-5` | 1M |
| `claude-haiku-4-5` | 200k |

**OpenAI**
| Model ID | Context |
|---|---|
| `gpt-5.4-pro` | 1.05M |
| `gpt-5.4` | 1.05M |
| `gpt-5.4-mini` | 400k |
| `gpt-5.4-nano` | 400k |
| `gpt-5.2-pro` | 400k |
| `gpt-5.2` | 400k |
| `gpt-5.2-codex` | 400k |
| `gpt-5.2-chat` | 128k |

**Google**
| Model ID | Context |
|---|---|
| `gemini-3.1-pro` | 1M |
| `gemini-3.1-flash-lite` | 1M |
| `gemini-3-flash` | 1M |
| `gemini-2.5-pro` | 1M |
| `gemini-2.5-flash` | 1M |

**xAI**
| Model ID | Context |
|---|---|
| `grok-4.1-fast` | 2M |

**DeepSeek**
| Model ID | Context |
|---|---|
| `deepseek-v3.2` | 164k |

**Moonshot**
| Model ID | Context |
|---|---|
| `kimi-k2.5` | 262k |

**Xiaomi**
| Model ID | Context |
|---|---|
| `mimo-v2-pro` | 1M |
| `mimo-v2-omni` | 262k |
| `mimo-v2-flash` | 262k |

**ByteDance**
| Model ID | Context |
|---|---|
| `seed-2.0-lite` | 262k |
| `seed-2.0-mini` | 262k |

**Alibaba**
| Model ID | Context |
|---|---|
| `qwen3-coder` | 262k |
| `qwen3.5-plus` | 1M |
| `qwen3.5-flash` | 1M |

**MiniMax**
| Model ID | Context |
|---|---|
| `minimax-m2.7` | 205k |
| `minimax-m2.5` | 197k |

**Z.ai**
| Model ID | Context |
|---|---|
| `glm-5-turbo` | 203k |
| `glm-5` | 80k |

Verify by asking your agent: *"what's my KibiBot Kibi Credit balance?"*

---

## What This Skill Can Do

### Kibi LLM Gateway
Use KibiBot-hosted AI models billed against your Kibi Credits. Same API key for LLM calls and agent actions.

- **Check balance:** "what's my KibiBot Kibi Credit balance?"
- **Add credits:** "I need to top up KibiBot credits" → agent links to kibi.bot/credits
- **Reload credits:** "reload my KibiBot credits from my trading wallet" (requires Agent Reload permission + configured on Credits page)
- **Model info:** "what models does KibiBot support?"

### Token Creation
Create tokens on Base, BSC, or Solana — KibiBot handles wallet creation, gas sponsorship, and on-chain deployment.

- "launch a token called MOON on Base"
- "create a meme coin named PEPE with ticker $PEPE on BSC"
- "make a test token called DEMO on Base Sepolia"

Token creation is async. After calling the API, poll the job status endpoint until complete (usually 30–60 seconds).

### Created Tokens
- "what tokens have I created on KibiBot?"
- "show my KibiBot token portfolio"

### Quota
- "how many free token launches do I have left today?"
- "what's my KibiBot quota per chain?"

### Wallet Balances
- "what's my KibiBot wallet balance?"
- "show my ETH, BNB, SOL and stablecoin balances on KibiBot"

### Fee Earnings
Check creator fee earnings across all chains and platforms — data is read from pre-computed DB cache (fast, no on-chain calls).

- "what are my KibiBot fee earnings?"
- "show my fee earnings summary across all chains"
- "what have I earned from my flap tokens on BSC?"
- "what are my fee earnings on Base?"
- "how much have I earned from my pumpfun tokens on Solana?"
- "how much has token 0x... earned on flap?"
- "what are the fees for my pumpfun token [mint address]?"

### Token Lookup
- "what's the price of $MOON on KibiBot?"
- "look up token 0x... on Base"

### Account
- "show me my KibiBot profile"
- "what's my KibiBot Twitter username and wallet address?"

### Skills
- "what can KibiBot do?" → calls GET /agent/v1/skills

---

## API Reference

**Base URL:** `https://api.kibi.bot/agent/v1`  
**Auth header:** `X-Api-Key: kb_...`

---

### GET /me
Returns user profile, wallet addresses, and account info.

Response:
```json
{
  "twitter_user_id": "...",
  "twitter_username": "...",
  "profile_image_url": "...",
  "followers_count": 1234,
  "joined_at": "2025-01-01T00:00:00Z"
}
```

---

### GET /skills
List all available KibiBot Agent API capabilities with examples. No auth required.

Response:
```json
{
  "skills": [
    {
      "name": "token_create",
      "description": "Deploy a new token on Base, BSC, or Solana",
      "example": "POST /agent/v1/token/create {\"name\": \"MyToken\", \"symbol\": \"MTK\", \"chain\": \"base\"}"
    }
  ],
  "total": 9
}
```

---

### POST /token/create
Create a token on-chain (async). Returns a `job_id` to poll.

Request:
```json
{
  "name": "MOON",
  "symbol": "MOON",
  "chain": "base",
  "description": "To the moon",
  "source_url": "https://x.com/user/status/123",
  "image_url": "https://...",
  "platform": "basememe"
}
```

- `chain`: `base` | `bsc` | `solana`
- `source_url` (optional): Twitter/X post URL — tweet image used as token image if `image_url` not provided
- `image_url` (optional): HTTP/HTTPS URL or IPFS URI — overrides source tweet image
- `platform` (optional): `basememe` | `clanker` | `flap` | `fourmeme` | `pumpfun` — defaults to chain default if omitted

Response (`202 Accepted`):
```json
{
  "job_id": 12345,
  "status": "pending",
  "chain": "base",
  "quota": {
    "chain": "base",
    "free_used_today": 1,
    "free_limit": 3,
    "sponsored_remaining": 2
  }
}
```

Pre-check errors:
- `403 insufficient_followers` — need minimum followers to create tokens
- `402 insufficient_balance` — free quota used, trading wallet balance too low
- `429 daily_cap_exceeded` — absolute daily cap reached across all chains

---

### GET /jobs/{job_id}
Poll token creation status.

Response:
```json
{
  "job_id": 12345,
  "status": "completed",
  "chain": "base",
  "token_address": "0x...",
  "error": null,
  "created_at": "2026-01-01T00:00:00Z",
  "completed_at": "2026-01-01T00:01:00Z"
}
```

Status values: `pending` | `processing` | `completed` | `failed`

---

### GET /token/{address}
Get token info by address.

Query: `?chain=base` (optional — searches all chains if omitted)

Response:
```json
{
  "token_address": "0x...",
  "name": "MOON",
  "symbol": "MOON",
  "chain": "base",
  "platform": "basememe",
  "creator_twitter_username": "...",
  "price_usd": "0.0001234",
  "market_cap_usd": "12340",
  "volume_24h_usd": "500",
  "creator_reward_usd": "1.23",
  "created_at": "2026-01-01T00:00:00Z"
}
```

---

### GET /tokens/created
Get paginated list of tokens you have created.

Query: `?page=1&page_size=20`

Response:
```json
{
  "tokens": [
    {
      "token_address": "0x...",
      "name": "MOON",
      "symbol": "MOON",
      "chain": "base",
      "platform": "basememe",
      "created_at": "2026-01-01T00:00:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 20,
  "has_more": false
}
```

---

### GET /balance/credits
Get Kibi Credit balance and agent reload configuration.

Response:
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

`agent_reload` is `null` if not configured. `enabled: false` means agent reload is off.

---

### POST /balance/credits/reload
Trigger a Kibi Credit reload from the trading wallet.

**Requirements:**
- User must have enabled Agent Reload at [kibi.bot/credits](https://kibi.bot/credits)
- The API key must have `reload_enabled = true`
- The API key must have `llm_enabled = true`
- Trading wallet must have sufficient USDC/USDT on at least one configured chain
- Daily reload limit must not be exceeded

This is **manually triggered by the agent** — there is no automatic background polling. Call this endpoint when the agent determines a credit reload is needed (e.g. before a long task).

Response:
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

Errors:
- `403` — reload not enabled for user or key
- `429` — daily limit would be exceeded
- `400` — insufficient stablecoin balance on all configured chains
- `500` — transaction failed

---

### POST /balance/credits/reload/disable
Emergency kill switch — agent disables its own reload permission. **Cannot be re-enabled by the agent** (human must re-enable via dashboard).

Use this if the agent detects unexpected reload behaviour or wants to self-limit spending.

Response: `204 No Content`

---

### GET /balance/wallet
Get on-chain wallet balances across all chains (main + trading wallets).

Response:
```json
{
  "evm_main": {
    "address": "0x...",
    "balance_eth": "0.050000",
    "balance_bnb": "0.100000",
    "balance_usdc_base": "10.000000",
    "balance_usdt_bsc": "5.000000"
  },
  "evm_trading": {
    "address": "0x...",
    "balance_eth": "0.010000",
    "balance_bnb": "0.005000",
    "balance_usdc_base": "0.000000",
    "balance_usdt_bsc": "0.000000"
  },
  "solana_main": {
    "address": "...",
    "balance_sol": "0.500000",
    "balance_usdc_solana": "5.000000"
  },
  "solana_trading": {
    "address": "...",
    "balance_sol": "0.050000",
    "balance_usdc_solana": "0.000000"
  }
}
```

Any field may be `null` if the wallet is not set up or the RPC is unavailable. Check `*_error` fields (e.g. `eth_error: "rpc_unavailable"`) for failure reasons.

---

### GET /fees/summary
Get total fee earnings across all chains in a single call. All data is pre-computed — fast, no on-chain calls.

Response:
```json
{
  "bsc": {
    "chain_id": 56,
    "token_count": 12,
    "total_earned_bnb": 0.053
  },
  "base": {
    "chain_id": 8453,
    "token_count": 7,
    "basememe_total_earned_eth": "0.0290",
    "basememe_claimable_eth": "0.0145",
    "clanker_claimable_weth_eth": "0.0080"
  },
  "solana": {
    "chain_id": 101,
    "token_count": 4,
    "total_earnings_sol": 0.05,
    "total_claimable_sol": 0.012
  }
}
```

---

### GET /fees/earnings
Get per-platform fee breakdown for a specific chain.

Query: `?chain=bsc` | `?chain=base` | `?chain=solana`

BSC response:
```json
{
  "chain": "bsc",
  "chain_id": 56,
  "flap": { "total_earned_bnb": 0.042, "earning_token_count": 3 },
  "fourmeme": { "total_earned_bnb": 0.011, "earning_token_count": 1 }
}
```

Base response:
```json
{
  "chain": "base",
  "chain_id": 8453,
  "basememe": { "total_earned_eth": "0.0290", "claimable_eth": "0.0145", "token_count": 5 },
  "clanker": { "claimable_weth_eth": "0.0080", "token_count": 2 }
}
```

Solana response:
```json
{
  "chain": "solana",
  "chain_id": 101,
  "pumpfun": { "total_earnings_sol": 0.05, "total_claimable_sol": 0.012, "earning_token_count": 4 }
}
```

---

### GET /fees/token
Get fee earnings for a specific token.

Query: `?chain=bsc&platform=flap&token_address=0x...`

- `chain`: `bsc` | `base` | `solana`
- `platform`: `flap` | `fourmeme` (BSC) · `pumpfun` (Solana)
- `token_address`: contract address (EVM) or mint address (Solana)

> **Note:** `basememe` and `clanker` do not support per-token fee tracking — a helpful redirect message is returned instead.

BSC/Flap response:
```json
{
  "token_address": "0x...",
  "token_name": "MyToken",
  "token_symbol": "MTK",
  "platform": "flap",
  "chain": "bsc",
  "earned_bnb": 0.021
}
```

Solana/Pumpfun response:
```json
{
  "mint": "AbcDef...",
  "token_name": "MyToken",
  "token_symbol": "MTK",
  "platform": "pumpfun",
  "chain": "solana",
  "actual_sol": 0.05,
  "distributable_sol": 0.012,
  "total_sol": 0.062,
  "is_graduated": true
}
```

Returns `404` if token not found or not owned by the authenticated user.

---

### GET /quota
Get daily token creation quota and trading wallet readiness per chain.

Response:
```json
{
  "chains": [
    {
      "chain": "base",
      "free_used_today": 1,
      "free_limit": 3,
      "sponsored_remaining": 2,
      "can_create_paid": true,
      "trading_wallet_balance": "0.010000 ETH",
      "trading_wallet_address": "0x..."
    },
    {
      "chain": "bsc",
      "free_used_today": 0,
      "free_limit": 3,
      "sponsored_remaining": 3,
      "can_create_paid": false,
      "trading_wallet_balance": "0.000000 BNB",
      "trading_wallet_address": "0x..."
    },
    {
      "chain": "solana",
      "free_used_today": 0,
      "free_limit": 3,
      "sponsored_remaining": 3,
      "can_create_paid": true,
      "trading_wallet_balance": "0.050000 SOL",
      "trading_wallet_address": "..."
    }
  ]
}
```

---

## Kibi LLM Gateway Reference

**Base URL:** `https://llm.kibi.bot`  
**Auth:** `X-Api-Key: kb_...` or `Authorization: Bearer kb_...`

### POST /v1/messages (Anthropic format)
Compatible with Claude models via Anthropic Messages API format.

```bash
curl https://llm.kibi.bot/v1/messages \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: YOUR_KB_API_KEY" \
  -d '{
    "model": "claude-haiku-4-5",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 100
  }'
```

### POST /v1/chat/completions (OpenAI format)
Compatible with all models via OpenAI Chat Completions format.

```bash
curl https://llm.kibi.bot/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: YOUR_KB_API_KEY" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 100
  }'
```

### GET /v1/models
List available models.

### GET /v1/models/openclaw
Returns a ready-to-paste OpenClaw provider config block. No auth required.

---

## Error Codes

| Code | Meaning |
|------|---------|
| 401 | Missing or invalid API key |
| 402 | Insufficient Kibi Credits (LLM) or trading wallet balance (token creation) |
| 403 | Permission denied — feature not enabled for this key or user |
| 404 | Resource not found |
| 422 | Validation error — check request body |
| 429 | Rate limited or daily cap exceeded — wait before retrying |
| 500 | Server error — retry |

---

## Troubleshooting

**402 on LLM calls**  
Kibi Credits exhausted. Top up at [kibi.bot/credits](https://kibi.bot/credits).  
Note: Kibi Credits ≠ trading wallet. Topping up one doesn't affect the other.

**403 on reload**  
Either Agent Reload is not enabled for the user ([kibi.bot/credits](https://kibi.bot/credits) → Agent Reload section), or the API key doesn't have `reload_enabled`. Check both.

**401 Unauthorized**  
API key missing or invalid. Manage keys at [kibi.bot/settings/api-keys](https://kibi.bot/settings/api-keys).  
Ensure you send: `X-Api-Key: kb_...`

**Token creation stuck at pending**  
Poll `GET /agent/v1/jobs/{job_id}` — creation usually takes 30–60 seconds.  
If still pending after 5 minutes, check the `error` field.

**429 on reload**  
Daily reload limit exceeded. Check `daily_remaining_usd` in the balance response.

**400 on reload — insufficient balance**  
No configured chain has enough USDC/USDT in the trading wallet. Check `GET /balance/wallet` and top up.

---

## Full Documentation
- Agent API: [kibi.bot/agent](https://kibi.bot/agent)
- API Keys: [kibi.bot/settings/api-keys](https://kibi.bot/settings/api-keys)
- Kibi LLM Gateway: [kibi.bot/llm](https://kibi.bot/llm)
- OpenClaw setup: [kibi.bot/llm/openclaw](https://kibi.bot/llm/openclaw)
- Kibi Credits: [kibi.bot/credits](https://kibi.bot/credits)
