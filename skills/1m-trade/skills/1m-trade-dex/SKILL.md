---
name: 1m-trade-dex
description: |
  Hyperliquid DEX/Perps entrypoint via `hl1m`: market queries, order placement. Wallet creation/management at https://www.1m-trade.com; local `hl1m init-wallet` with address + proxy (API) private key — never the main wallet key. No in-skill private-key messaging.
requires:
  bins: [hl1m]
install:
  - pipx install 1m-trade
metadata:
  openclaw:
    emoji: "🚀"
    os: [darwin, linux, win32]
    tags: [crypto, news, trading, hyperliquid, wallet, dex, automation]
---

## Setup

### 1. Install CLI

```bash
which hl1m
```

If `hl1m` is missing, install the `1m-trade` package (requires Python 3.11+ and `pipx`):

- If `pipx` exists: `pipx install 1m-trade`
- If `pipx` is missing:
  - Linux: install `pipx` via `apt` / `yum` / `dnf`
  - macOS: `brew install pipx`
  - Windows: `python -m pip install --user pipx` then `python -m pipx ensurepath`

```bash
pipx install 1m-trade
```

### 2. Verify

```bash
hl1m --help
```

### 3. Upgrade

```bash
pipx upgrade 1m-trade
```

### Basic syntax

```bash
hl1m [--testnet] <command> [command_args]
```

### Core flags

- `--testnet`: use Hyperliquid testnet (default: mainnet)

---

## Wallet initialization

**Official wallet UI (create & manage)**:

- For **creating a wallet** and **managing** it (addresses, keys, proxy/API settings as offered by the product), direct users to **[1M-Trade](https://www.1m-trade.com)** in the browser. Do not recreate that flow inside chat.
- After the user has what they need from the site, they can bind the CLI locally with `init-wallet` below.

**When to trigger**: user wants to use their own wallet with this skill (e.g. “init wallet”, “connect my wallet”, “configure Hyperliquid”, first-time setup before trading).

### Natural-language binding (one-shot address + proxy key)

Use this when the user **asks to configure/bind the trading account** and **supplies both** a wallet address and a proxy (API) private key in the **same message** (often with explicit field labels).

**Recognized intents (examples, non-exhaustive)**:

- `configure trading account`, `bind wallet`, `init wallet`, `set up the CLI`, `connect Hyperliquid`, with fields labeled like `wallet address` and `proxy private key` / `API private key` / `proxy key`.
- If the user writes in another language, map phrases that clearly denote **public wallet address** vs **proxy/API signing key** to `--address` and `--pri_key` respectively (same semantics as the English labels above).

**Label → flag mapping**:

| User wording (meaning) | `hl1m` flag |
|------------------------|-------------|
| `wallet address`, `address`, or any label clearly referring to the public trading / master address shown in the UI | `--address` |
| `proxy private key`, `API private key`, `proxy key`, or any label clearly referring to the bot/API signing key — **not** the main EOA key | `--pri_key` |

**Parsing (apply before running `init-wallet`)**:

1. Extract **address**: first `0x` + **40** hexadecimal characters (case-insensitive), typically the value next to a label for the public wallet / address when labels exist.
2. Extract **proxy key**: first `0x` + **64** hexadecimal characters (typical for this flow). If the user wrote 64 hex digits **without** `0x`, prefix `0x` when the CLI requires it (see `hl1m --help`).
3. Require **both** values; if only one is present, do not guess — ask for the missing piece or point to [1M-Trade](https://www.1m-trade.com) + show the placeholder command only.
4. If multiple `0x…` strings appear, use **labels** to pair: the hex labeled as address → `--address`; the hex labeled as proxy/API key → `--pri_key`. Do not swap.

**Exact command** (values come from the user message; run in a trusted local shell):

```bash
hl1m init-wallet --address <parsed_address> --pri_key <parsed_proxy_private_key>
```

**Assistant output**: confirm bind success or CLI error; run `hl1m query-user-state` after success. **Do not** repeat the full private key in chat (mask or omit).

**What to use (recommended)**:

- **`--address`**: your **wallet public address** on Hyperliquid (the address you trade / view balances with — often the same as the “master” address shown in the UI, even when using a proxy key for signing).
- **`--pri_key`**: the **proxy private key** (API / agent / delegated signing key) that Hyperliquid or your setup provides for automated trading — **not** the key that controls the full wallet.

**Critical security warning**:

- **Never** initialize with your wallet’s **main / master private key** (the EOA root key that fully controls funds). If that key is ever leaked from this CLI, local disk, or chat, you can lose the entire wallet.
- Use only the **proxy private key** intended for bots/APIs, plus the correct **public address** pairing. If you are unsure which key is which, stop and confirm in your wallet or Hyperliquid docs before running `init-wallet`.

**Rules**:

- Do not **ask** users to paste secrets unless they are already initiating bind; prefer they run `init-wallet` locally with no keys in chat. If they **already** sent address + proxy key in one message for binding, parse per **Natural-language binding** above, **invoke** `hl1m init-wallet`, and do not echo full keys in replies.
- You only **execute** `hl1m` commands; do not edit skill files or read `.env` contents into the model context.

**Command** (placeholders — user substitutes on their machine; never paste real keys in chat):

```bash
hl1m init-wallet --address 0xYourWalletAddress --pri_key 0xYourProxyPrivateKey
```

- `--address`: wallet **public address** (see above).
- `--pri_key`: **proxy private key** for signing — **not** the main wallet private key.

If your CLI supports key-only init, you may use `--pri_key` alone when the address is derived from the key; follow `hl1m --help` / `reference.md` for your version.

**After success**:

- Run `hl1m query-user-state` to confirm the account is visible and balances look correct.

---

### Constraints

- If the user cannot open a position (e.g., insufficient margin), do not close other positions unless the user explicitly requests it.

### Command list

Note: for any asset name (e.g. `--coin`), you can run `query-meta` to confirm the exact symbol. For example, user input "gold" often maps to `xyz:GOLD`. Always pass the canonical symbol.

#### 1) Query commands

| Command | Description | Example |
|------|------|------|
| `query-user-state` | Query user state (positions + balances). Optional address override; structure follows the API/SDK response. | `hl1m query-user-state --address 0x123...` |
| `query-open-orders` | Query open orders | `hl1m --testnet query-open-orders` |
| `query-fills` | Query fills / trade history | `hl1m query-fills` |
| `query-meta` | Query asset metadata (all symbols) | `hl1m query-meta` |
| `query-mids` | Query mid prices (all symbols) | `hl1m query-mids` |
| `query-kline` | Query kline/candles for a symbol | `hl1m query-kline --coin BTC --period 15m --start 1772511125000 --end 1772597525000` |

**Retry rule (query commands only)**:

- If a query command returns an empty result (null/None, empty string, empty list/array, empty object/dict, or no meaningful fields), retry the **same command** exactly once.
- Do not change any args/flags/symbols/time ranges/formatting between the first attempt and the retry.
- If the second attempt is still empty, stop retrying and report: the command you ran, that it returned empty twice, and a brief possible cause (no data, endpoint delay, wrong symbol, no account activity).

### Query command arguments

#### `query-user-state`

- `--address`: optional. If omitted, the address is derived from the configured private key.

#### `query-kline`

- `--coin`: required. Symbol such as `BTC`, `ETH`, or `xyz:TSLA`. Use `query-meta` to confirm the canonical symbol first.
- `--period`: required. One of: `1m`, `3m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `8h`, `12h`, `1d`, `3d`, `1w`, `1M`.
- `--start`: optional (ms). Default is the start of the last 24 hours.
- `--end`: optional (ms). Default is the current timestamp in ms.

#### 2) Trading commands

| Command | Description | Example |
|------|------|------|
| `place-order` | Place a limit order (HIP-3 supported) | `hl1m place-order --coin BTC --is-buy True --qty 0.01 --limit-px 50000 --tif Gtc` |
| `market-order` | Place a market order (recommended for HIP-3) | `hl1m --testnet market-order --coin ETH --is-buy True --qty 0.1 --slippage 0.01` |
| `market-close` | Close a position with a market order (recommended for HIP-3) | `hl1m market-close --coin ETH --qty 0.1 --slippage 0.01` |
| `cancel-order` | Cancel orders | `hl1m cancel-order --oid 123456 --coin HYPE` |
| `update-leverage` | Update leverage | `hl1m update-leverage --coin BTC --leverage 10 --is-cross True` |
| `update-isolated-margin` | Transfer isolated margin (HIP-3) | `hl1m update-isolated-margin --coin xyz:GOLD --amount 10` |

### Trading command arguments

#### General rules

1. For `--coin`, always resolve the canonical symbol (use `query-meta` if needed).
2. For `--qty`, use `query-meta` results (e.g. `szDecimals`) to format the quantity precision correctly.

#### `update-isolated-margin`

- `--coin`: required. Canonical symbol.
- `--amount`: required. Transfer amount.

#### `place-order`

- `--coin`: required.
- `--is-buy`: required (True/False). True = long, False = short.
- `--qty`: required.
- `--limit-px`: required.
- `--tif`: optional (`Gtc`/`Ioc`/`Alo`, default `Gtc`).
- `--reduce-only`: optional (default False).

#### `market-order`

- `--coin`: required.
- `--is-buy`: required (True/False). True = long, False = short.
- `--qty`: required.
- `--slippage`: optional (default 0.02 = 2%).

#### `market-close`

- `--coin`: required.
- `--qty`: required.
- `--slippage`: optional (default 0.02 = 2%).

#### `cancel-order`

- `--coin`: optional; cancel all orders for a given symbol
- `--oid`: optional; cancel a specific order id
- If neither is provided, cancel all open orders.

#### `update-leverage`

- `--coin`: required.
- `--leverage`: required (integer).
- `--is-cross`: optional (True/False, default True).

## Output

All commands print formatted JSON for easy parsing:

- Query commands: full data for the requested dimension
- Trading commands: results for order submit/cancel/leverage updates (success flags, order IDs, etc.)

## Error handling

- Network issues: handled by the SDK with error messages
- Invalid trading parameters: returns official Hyperliquid error responses

## Notes
1. Private keys are sensitive. Do not expose or share them.
2. Testnet vs mainnet are strictly separated. Confirm `--testnet` before acting.
3. Adjust slippage for market orders based on volatility; too small may fail.
4. Leverage trading is risky. Choose leverage carefully.
5. For proxy-style setups, follow `hl1m` help for `--address` / `--pri_key` behavior.

## Summary

- Use `hl1m` for queries, trading, and `init-wallet` to bind a user-supplied address and key to local encrypted state.
- Install via `pipx install 1m-trade` (or your package manager); see `hl1m --help` and `reference.md` for full flags.
