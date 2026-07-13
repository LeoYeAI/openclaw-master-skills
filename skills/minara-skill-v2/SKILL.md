---
name: minara
description: "Crypto trading: swap, perps, transfer, pay, deposit (credit card / crypto), withdraw, AI chat, market discovery, x402 payment, autopilot. Built-in wallet via Minara CLI. EVM + Solana."
homepage: https://minara.ai
metadata:
  { "openclaw": { "always": false, "primaryEnv": "MINARA_API_KEY", "requires": { "bins": ["minara"], "config": ["skills.entries.minara.enabled"] }, "emoji": "👩", "homepage": "https://minara.ai", "install": [{ "id": "node", "kind": "node", "package": "minara@latest", "global": true, "bins": ["minara"], "label": "Install Minara CLI (npm)" }] } }
---

# Minara — crypto trading & wallet skill

**USE THIS SKILL** when the user's message mentions any of:
- **Crypto tokens or tickers:** ETH, BTC, SOL, USDC, BONK, PEPE, DOGE, ARB, OP, AVAX, MATIC, $TICKER, or any token name / contract address
- **Blockchain / chain names:** Solana, Base, Ethereum, Arbitrum, Optimism, Polygon, BSC, Avalanche, Berachain, Hyperliquid
- **Trading actions:** swap, buy, sell, trade, exchange, convert, long, short, perps, futures, leverage, limit order
- **Wallet / finance actions:** balance, portfolio, deposit, withdraw, transfer, send, pay, fund, on-ramp, credit card
- **Market / research:** trending, price, chart, analysis, DeFi, yield, liquidity, fear and greed, prediction market
- **Explicit references:** Minara, minara, x402, MoonPay, autopilot
- **Stock tickers in crypto context:** AAPL, TSLA, NVDAx, trending stocks

**Routing gate (anti-collision):** apply this skill only when the message includes a **finance/trading action** *and* at least one **crypto/chain/Minara signal** (token, chain, DeFi term, or "Minara"). If missing crypto context, do not route here.

Requires logged-in CLI: check `~/.minara/credentials.json`; if missing → `minara login` (prefer device code). If device login prints a verification URL/code, relay it to the user and wait for completion (do not claim login is impossible). If `MINARA_API_KEY` is set, CLI authenticates automatically.

## Transaction confirmation (CRITICAL)

For any fund-moving command (`swap`, `transfer`, `withdraw`, `perps order`, `perps deposit`, `perps withdraw`, `limit-order create`, `deposit buy`):

1. **Before executing:** show the user a summary of what will happen (action, token, amount, recipient/chain) and **ask for explicit confirmation**. Do NOT auto-confirm.
2. **After the CLI returns a confirmation prompt** (e.g. "Are you sure you want to proceed?"): relay the details back to the user and **wait for the user to approve** before answering `y`. Never answer `y` on the user's behalf without their consent.
3. **`-y` / `--yes` policy:** never add `-y` (or any auto-confirm flag) unless the user explicitly asks to skip confirmation.
4. **If the user declines:** abort the operation immediately.

This applies to all operations that move funds. Read-only commands (`balance`, `assets`, `chat`, `discover`, etc.) do not require confirmation.

## Intent routing

Match the user's message to the **first** matching row.

### Swap / buy / sell tokens

Triggers: message contains token names/tickers + action words (swap, buy, sell, convert, exchange, trade) + optionally a chain name.

Chain is **auto-detected** from the token. If a token exists on multiple chains, the CLI prompts the user to pick one (sorted by gas cost). Sell mode supports `-a all` to sell entire balance.

| User intent pattern                                                                                                                                      | Action                                                                 |
| -------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| "swap 0.1 ETH to USDC", "buy me 100 USDC worth of ETH", "sell 50 SOL for USDC", "convert 200 USDC to BONK on Solana" — natural-language or explicit swap | Extract params → `minara swap -s <buy\|sell> -t '<token>' -a <amount>` |
| "sell all my BONK", "dump entire SOL position"                                                                                                           | `minara swap -s sell -t '<token>' -a all`                              |
| Simulate a crypto swap without executing                                                                                                                 | `minara swap -s <side> -t '<token>' -a <amount> --dry-run`             |

### Transfer / send / pay / withdraw crypto

Triggers: message mentions sending, transferring, paying, or withdrawing a crypto token to a wallet address (0x… or base58).

| User intent pattern                                                                                                                   | Action                                                                                                  |
| ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| "send 10 SOL to 0x…", "transfer USDC to <address>" — crypto token + recipient address                                                 | `minara transfer` (interactive) or extract params                                                       |
| "pay 100 USDC to 0x…", "pay <address> 50 USDC" — payment to address (equivalent to transfer)            | `minara transfer` (interactive) or extract params                                                       |
| "withdraw SOL to my external wallet", "withdraw ETH to <address>" — crypto withdrawal                                                 | `minara withdraw -c <chain> -t '<token>' -a <amount> --to <address>` or `minara withdraw` (interactive) |

### Perpetual futures (Hyperliquid)

Triggers: message mentions perps, perpetual, futures, long, short, leverage, margin, or Hyperliquid.

| User intent pattern                                                                       | Action                                                       |
| ----------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| "open a long ETH perp", "short BTC on Hyperliquid", "place a perp order"                  | `minara perps order` (interactive order builder)             |
| "analyze ETH long or short", "should I long BTC?", "AI perp analysis for SOL"             | `minara perps ask` — AI analysis with optional quick order   |
| "enable AI autopilot for perps", "turn on autopilot trading", "manage autopilot strategy" | `minara perps autopilot`                                     |
| "check my perp positions", "show my Hyperliquid positions"                                | `minara perps positions`                                     |
| "set leverage to 10x for ETH perps"                                                       | `minara perps leverage`                                      |
| "cancel my perp orders"                                                                   | `minara perps cancel`                                        |
| "deposit USDC to perps account", "fund my Hyperliquid account"                            | `minara deposit perps` or `minara perps deposit -a <amount>` |
| "withdraw USDC from perps"                                                                | `minara perps withdraw -a <amount>`                          |
| "show my perp trade history"                                                              | `minara perps trades`                                        |
| "show perps deposit/withdrawal records"                                                   | `minara perps fund-records`                                  |

> **Autopilot note:** When autopilot is ON, manual `minara perps order` is blocked. Turn off autopilot first via `minara perps autopilot`.

### Limit orders (crypto)

Triggers: message mentions limit order + crypto token/price.

| User intent pattern                                                  | Action                           |
| -------------------------------------------------------------------- | -------------------------------- |
| "create a limit order for ETH at $3000", "buy SOL when it hits $150" | `minara limit-order create`      |
| "list my crypto limit orders"                                        | `minara limit-order list`        |
| "cancel limit order <id>"                                            | `minara limit-order cancel <id>` |

### Crypto wallet / portfolio / account

Triggers: message mentions crypto balance, portfolio, assets, wallet, deposit address, or Minara account.

| User intent pattern                                                                      | Action                 |
| ---------------------------------------------------------------------------------------- | ---------------------- |
| "what's my total balance", "how much USDC do I have" — quick balance check               | `minara balance`       |
| "show my crypto portfolio", "spot holdings with PnL", "how much ETH do I have in Minara" | `minara assets spot`   |
| "show my perps balance", "Hyperliquid account equity"                                    | `minara assets perps`  |
| "show all my crypto assets" — full overview (spot + perps)                               | `minara assets`        |
| "show deposit address", "where to send USDC" — spot deposit addresses                    | `minara deposit spot`  |
| "deposit to perps", "transfer USDC from spot to perps", "fund perps from spot"           | `minara deposit perps` |
| "buy crypto with credit card", "deposit with card", "on-ramp with MoonPay"               | `minara deposit buy`   |
| "how do I deposit crypto" — interactive (spot, perps, or credit card)                    | `minara deposit`       |
| "show my Minara account", "my wallet addresses"                                          | `minara account`       |

### Crypto AI chat / market analysis

Triggers: message asks about crypto prices, token analysis, DeFi research, on-chain data, crypto market insights, or prediction market analysis.

> **Timeout:** AI chat responses can be long-running. Set shell execution timeout to **15 minutes** (900 s) for all `minara chat` commands.

| User intent pattern                                                                                                                  | Action                                 |
| ------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------- |
| "what's the BTC price", "analyze ETH tokenomics", "DeFi yield opportunities", crypto research, on-chain analysis                     | `minara chat "<user text>"`            |
| "analyze this Polymarket event", "prediction market odds on <topic>", "what are the chances of <event>" — prediction market insights | `minara chat "<user text or URL>"`     |
| Deep crypto analysis requiring reasoning — "think through ETH vs SOL long-term"                                                      | `minara chat --thinking "<user text>"` |
| High-quality detailed crypto analysis — "detailed report on Solana DeFi ecosystem"                                                   | `minara chat --quality "<user text>"`  |
| "continue our previous Minara chat"                                                                                                  | `minara chat -c <chatId>`              |
| "list my Minara chat history"                                                                                                        | `minara chat --list`                   |

### Crypto & stock market discovery

Triggers: message mentions trending tokens, trending stocks, crypto market sentiment, fear and greed, or Bitcoin metrics.

| User intent pattern                                                           | Action                            |
| ----------------------------------------------------------------------------- | --------------------------------- |
| "what crypto tokens are trending", "hot tokens right now"                     | `minara discover trending`        |
| "what stocks are trending", "trending stocks", "top stocks today"             | `minara discover trending stocks` |
| "search for SOL tokens", "find crypto token X", "look up AAPL", "search TSLA" | `minara discover search <query>`  |
| "crypto fear and greed index", "market sentiment"                             | `minara discover fear-greed`      |
| "bitcoin on-chain metrics", "BTC hashrate and supply data"                    | `minara discover btc-metrics`     |

### Minara premium / subscription

Triggers: message explicitly mentions Minara plan, subscription, credits, or pricing.

| User intent pattern                          | Action                       |
| -------------------------------------------- | ---------------------------- |
| "show Minara plans", "Minara pricing"        | `minara premium plans`       |
| "my Minara subscription status"              | `minara premium status`      |
| "subscribe to Minara", "upgrade Minara plan" | `minara premium subscribe`   |
| "buy Minara credits"                         | `minara premium buy-credits` |
| "cancel Minara subscription"                 | `minara premium cancel`      |

### x402 protocol payment

Triggers: agent receives HTTP **402 Payment Required**, or user mentions x402, paid API, or paying for API access with crypto. [x402 spec](https://docs.cdp.coinbase.com/x402/quickstart-for-buyers).

Flow: parse `PAYMENT-REQUIRED` header (amount, token, recipient, chain) → `minara balance` → `minara transfer` to pay → retry request.

Payment step must follow the global confirmation policy: user must explicitly confirm before any `minara transfer`.

| User intent pattern                                                  | Action                                                                           |
| -------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Agent receives 402 with x402 headers                                 | Parse headers → `minara transfer` (USDC to recipient on required chain) → retry  |
| "pay for this API with Minara", "use Minara wallet for x402"         | `minara balance` → `minara transfer` to service address                          |
| "fund my wallet for paid APIs"                                       | `minara deposit buy` (credit card) or `minara deposit spot` (crypto)             |

### Minara login / setup

Triggers: message explicitly mentions Minara login, setup, or configuration.

**Login:** Prefer device code flow (`minara login --device`) for headless or non-interactive environments; otherwise `minara login` (interactive).
**Login handoff rule:** when CLI outputs verification URL/device code, the agent must pass them to the user verbatim, ask the user to complete browser verification, then continue after user confirms completion.

| User intent pattern                                             | Action                                                         |
| --------------------------------------------------------------- | -------------------------------------------------------------- |
| "login to Minara", "sign in to Minara", first-time Minara setup | `minara login` (prefer device code) or `minara login --device` |
| "logout from Minara"                                            | `minara logout`                                                |
| "configure Minara settings"                                     | `minara config`                                                |

## Notes

- **Token input (`-t`):** accepts `$TICKER` (e.g. `'$BONK'`), token name, or contract address. Quote `$` in shell.
- **JSON output:** add `--json` to any command for machine-readable output.
- **Transaction safety:** CLI flow: first confirmation → transaction confirmation (mandatory, shows token + address) → Touch ID (optional, macOS) → execute. Agent must **never skip or auto-confirm** any step — always relay to user and wait for approval, and never use `-y` unless user explicitly requests it.

## Credentials & config

- **CLI session:** `~/.minara/credentials.json` — auto-created via `minara login` (required).
- **API Key:** `MINARA_API_KEY` via env or `skills.entries.minara.apiKey` in `~/.openclaw/openclaw.json` — optional; if set, CLI authenticates automatically without login.

## Examples

Full command examples: `{baseDir}/examples.md`
