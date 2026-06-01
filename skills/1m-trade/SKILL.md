---
name: 1m-trade
description: |
  Integrated on-chain operations hub: integrates BlockBeats market intelligence, Hyperliquid DEX trading via `hl1m`, wallet creation and management at https://www.1m-trade.com, and supports local initialization using `hl1m init-wallet` (wallet address + proxy private key, never use the main wallet private key). Supports fully autonomous AI trading.
metadata:
  openclaw:
    emoji: "🚀"
    always: false
    requires:
      bins:
        - curl
        - node
        - hl1m
        - openclaw
      configPaths:
        - ~/.openclaw/.1m-trade/.env
        - $OPENCLAW_STATE_DIR/.1m-trade/.env
      env:
        - BLOCKBEATS_API_KEY
        - HYPERLIQUID_PRIVATE_KEY_ENC
        - HYPERLIQUID_PK_ENC_PASSWORD
        - HYPERLIQUID_WALLET_ADDRESS
    os:
      - darwin
      - linux
      - win32
    tags:
      - crypto
      - news
      - trading
      - hyperliquid
      - wallet
      - dex
      - automation
---

# 1m-trade Aggregator - On-chain Operations Hub

**Official website (wallet & account)**: [https://www.1m-trade.com](https://www.1m-trade.com)

## After first install
Scan and verify all required dependencies for sub-skills and install what is needed. From this skill bundle root, run `node auto_check.js` to verify required binaries and `.env` entries (it does not print secrets).

### `1m-trade-news` (required)

This aggregator **must** have the **`1m-trade-news`** sub-skill available: market intelligence, news, and BlockBeats API calls all go through it. Do **not** skip this step when installing the bundle.

1. **Skill files**: Ensure the bundle includes **`skills/1m-trade-news/`** (`SKILL.md`, etc.) and that your OpenClaw / host loads that folder as the **`1m-trade-news`** skill.
2. **`curl`**: Required on `PATH` for the documented API flows (see metadata `requires.bins`).
3. **BlockBeats API key (`BLOCKBEATS_API_KEY`)**: Market and news workflows use the **BlockBeats Pro API**. Install-time, ensure **`BLOCKBEATS_API_KEY`** is set in the local `1m-trade` state file (paths under **Optional runtime override** below).

   **Apply for / obtain a key (free tier)**:

   1. Request a free API key:
      ```bash
      curl --request GET --url "https://api-pro.theblockbeats.info/v1/api-key/free"
      ```
   2. From the JSON body, read `data.api_key` and use it as `BLOCKBEATS_API_KEY`.
   3. Write it to `~/.openclaw/.1m-trade/.env` (or `$OPENCLAW_STATE_DIR/.1m-trade/.env` if you use that override), on its own line:
      `BLOCKBEATS_API_KEY=<api_key>`
      Do not remove unrelated lines; only add or update this variable.

**Reference**: `skills/1m-trade-news/SKILL.md` → **Get an API key** (includes agent-safe steps to populate `.env` without printing the key).

**Security**: Do not paste API keys into chat; the model must not echo stored keys.

### `1m-trade-dex` (required)

This aggregator **must** have the **`1m-trade-dex`** sub-skill available: trading, wallet queries, and `hl1m` all go through it. Do **not** skip this step when installing the bundle.

1. **Skill files**: Ensure the bundle includes **`skills/1m-trade-dex/`** (`SKILL.md`, `reference.md`, etc.) and that your OpenClaw / host loads that folder as the **`1m-trade-dex`** skill.
2. **CLI (`hl1m`)**: Install the `1m-trade` package so `hl1m` is on `PATH` (Python 3.11+ recommended):
   ```bash
   pipx install 1m-trade
   hl1m --help
   ```
   If `pipx` is missing, install it per your OS (see `skills/1m-trade-dex/SKILL.md` → **Setup**).
3. **Wallet / Hyperliquid state**: After install, users still run **`hl1m init-wallet`** (and related steps) so `.env` contains the Hyperliquid fields `auto_check.js` expects — see **`skills/1m-trade-dex/SKILL.md`** → **Wallet initialization**.

Optional runtime override:
- `OPENCLAW_STATE_DIR` can be set to change where local `.1m-trade` state files are read/written.
- If not set, tools default to `~/.openclaw/.1m-trade/`.

Secret source-of-truth policy:
- API key and wallet credentials are expected in the local state `.env` file under the paths above (typically after the user runs `hl1m init-wallet` and related CLIs locally).
- Process environment variables may be used only as explicit runtime overrides by underlying tools.
- **LLM boundary**: The model must **not** read `.env` into context or quote stored secrets. For **wallet bind**, if the user **voluntarily** sends wallet address + **proxy** private key in one message (e.g. clearly labeled fields such as `wallet address` and `proxy private key`), follow `1m-trade-dex` → parse and **invoke** `hl1m init-wallet --address … --pri_key …` in a trusted shell; **do not** repeat full keys in assistant replies. Otherwise prefer the user running `init-wallet` locally without pasting keys in chat.
- Never print secret values in assistant-visible chat or user-facing logs from the model.

## Overview
This skill (`1m-trade`) is an orchestration hub that integrates multiple sub-skills into a single coherent workflow. You describe your goal (e.g., "check today's sentiment", "analyze BTC fund flows and open a long with half my balance", "help me configure my Hyperliquid wallet with init-wallet", "auto-trade BTC"), and this skill decomposes the request and calls `1m-trade-news` and `1m-trade-dex` to complete the operation.

## Core workflows
Based on **intent keywords**, this skill routes into one of the workflows below (or composes them).

### Workflow 1: Market intelligence (Data & News)
**Triggers**: `market`, `price`, `news`, `macro`, `fund flows`, `perps`, `search [keyword]`

**Skill**: `1m-trade-news`

**Logic**:
1. Parse the user query and map it to a scenario / intent mapping.
2. Call the relevant BlockBeats API endpoints in parallel.
3. Format and aggregate results into a market report with brief interpretation.

**Example output**:

```
📰 Market Report · 202X-XX-XX
===
1. 📊 Snapshot
   Sentiment: 35 → Neutral
   BTC ETF: +$120M net inflow today
   On-chain tx volume: +15% vs yesterday

2. 💰 Hot flows (Solana)
   1. JTO net inflow $4.2M
   2. ...

3. 🌐 Macro
   Global M2: +4.5% YoY → Liquidity easing
   DXY: 104.2 → Relatively strong
   Overall: Macro backdrop is neutral-to-bullish for crypto.
```

### Workflow 2: Wallet setup (initialization)
**Triggers**: `init wallet`, `configure wallet`, `configure trading account`, `bind wallet`, `connect Hyperliquid`, `set up trading`, `wallet settings`, `proxy key`, `API key` (wallet); same message with both `wallet address` and `proxy private key` (or non-English equivalents per `1m-trade-dex` **Natural-language binding**).

**Skill**: `1m-trade-dex` (see `skills/1m-trade-dex/SKILL.md` → **Natural-language binding** and `skills/1m-trade-dex/reference.md`)

**Wallet operations (synced with sub-skill docs)**:

| Step | Where | What |
|------|--------|------|
| Create / manage wallet | Browser | **[https://www.1m-trade.com](https://www.1m-trade.com)** — official UI for account and wallet; do not recreate this flow in chat. |
| Bind CLI to the account | Local shell | **`hl1m init-wallet`** only — **wallet public address** + **proxy (API) private key**. **Never** use the **main / master** wallet private key. |
| Verify | After init | `hl1m query-user-state` (and other `hl1m` query commands as needed). |

**Logic**:
1. Send users to **[https://www.1m-trade.com](https://www.1m-trade.com)** for **wallet creation and ongoing management** in the browser. Do not simulate full wallet creation inside the assistant.
2. For **CLI binding**:
   - If the user provides **both** address and proxy key in one message (with labels such as `wallet address` and `proxy private key`, or other languages as mapped in `1m-trade-dex`), follow `1m-trade-dex` **Natural-language binding**: parse `0x` + 40 hex (address) and `0x` + 64 hex (proxy key), then run `hl1m init-wallet --address <parsed> --pri_key <parsed>` in a trusted shell; do not echo full keys in chat.
   - Otherwise, show the placeholder command only and ask the user to run locally:
   ```bash
   hl1m init-wallet --address 0xYourWalletAddress --pri_key 0xYourProxyPrivateKey
   ```
3. After a successful init, use `hl1m query-user-state` to confirm the account is visible.

### Workflow 3: Trading execution & management (Trading & Management)
**Triggers**: `trade`, `order`, `open`, `close`, `positions`, `price`, `kline`, `HIP3`, `AAPL`, `GOLD`

**Skill**: `1m-trade-dex`

**Logic**:
1. **Market data**: query kline/mids/meta as requested and format results.
2. **Pre-trade checks**: ensure `1m-trade-dex` is installed and run `node auto_check.js` to verify prerequisites. If it fails, do not execute any trades.
3. **Execution**: follow the `1m-trade-dex` documentation for the specific command.

### Workflow 4: Hybrid orchestration (Hybrid Workflow)
**Trigger examples**: "check the market then decide whether to buy BTC", "after I init my wallet, show ETH kline"

**Logic**:
1. Call Workflow 1 to fetch the market report.
2. Present the report and ask whether to continue (e.g., "proceed to wallet setup or trading?").
3. After confirmation, call Workflow 2 (wallet init guidance) or Workflow 3.

## Examples
**User**: "How is the crypto market today? I also need to connect my Hyperliquid wallet."
**`1m-trade`**:
1. Generate a market snapshot report (Workflow 1).
2. Point to **[1M-Trade](https://www.1m-trade.com)** for wallet creation/management as needed, then Workflow 2: if the user already sent labeled `wallet address` + `proxy private key` (or equivalent), parse and run `hl1m init-wallet`; otherwise give the placeholder command for local use (proxy key only; never the main wallet private key). Do not guide `send-private-key`.

**User**: "Search for the latest news about 'Bitcoin halving', then show BTC kline."
**`1m-trade`**:
1. Call search (Workflow 1, Scenario 5) and return relevant items.
2. Call kline query (Workflow 3) and return recent candles.

### Workflow 5: Fully autonomous mode (AI Auto-Trader)
**Triggers**: `enable auto trading`, `autonomous trading`, `managed`, `AI trade for me`, `run every N minutes`, `auto trade BTC`

**Logic**:
1. Run the checker once before enabling cron:
   - Repo root: `node auto_check.js`
   - If installed under the OpenClaw workspace: run `node <skill_bundle_root>/auto_check.js`
   If it fails, do not enable auto trading.
2. Check whether the `1m-trade-auto-trader` cron job exists:
   - Run `openclaw cron list` to verify whether it still exists.
   - If it exists, ask the user to stop/remove it before creating a new one.
   - If the user confirms it should be removed and it is still present, attempt to remove it with `openclaw cron rm <task id>`, then re-run `openclaw cron list` to confirm it is gone.

3. Create a periodic workflow using the command below. `--session isolated` is fixed and must not be changed. The default interval is every 20 minutes (`*/20`); replace with `*/N` if needed. Send the trading report to the user.
   Security constraints for the cron message:
   - Include ONLY the "#### Workflow content" block as the job prompt template.
   - Never include any secrets (API keys, private keys, passwords, `.env` contents, tokens).
   - Never include unrelated user/system text, terminal logs, or file contents.
   - Keep shell commands/placeholders unchanged, but you may translate natural-language instructions for locale.
4. Run:
   ```bash
   openclaw cron add \
     --name "1m-trade-auto-trader" \
     --cron "*/20 * * * *" \
     --session isolated \
     --message "<Paste the FULL prompt from #### Workflow content through the end of the report template below; translate EVERY narrative line into the user's language (e.g. full Simplified Chinese if the user uses Chinese—no leftover English instructions). Keep skill names, hl1m subcommands, symbols, and <<...>> structure unchanged. No secrets. Each run outputs ONLY the final trading report; that report must be monolingual (all Chinese OR all English per user—no mixed prose). Replace this placeholder with that translated block.>" \
     --timeoutSeconds 600 \
     --announce \
     --channel <channel e.g. telegram> \
     --to "<user id>" \
   ```

#### Workflow content
Pre-start: dependency memory check
All skills are installed locally.
1. Try reading: `$OPENCLAW_STATE_DIR/.1m-trade/dependencies-status.md`
   - If missing → first run, treat as "not confirmed installed"
   - If present, look for any marker:
     - Installed: true
     - DependencyStatus: Installed
     - SkillsReady: true
   - Record status as "installed" or "not installed/unknown"

2. Decide based on the status:
   - If clearly "installed" → skip checks/install and go to step 4
   - Otherwise → run step 3

3. Only when initialization is needed:
   Ensure these skills are available in order:
   - 1m-trade-news
   - 1m-trade-dex
   If a skill is unavailable, attempt to install/enable it via the system's mechanism.
   Then record success in the memory file.

4. Must execute: update/create the dependency memory file by overwriting:
```
# Dependency install marker - do not edit manually
Installed: true
Skills: 1m-trade-news (or others)
Skills Path: <skill paths>
LastChecked: 2026-03-15 14:30:00 UTC
```
Start execution

Start execution.

### Workflow: Fully autonomous trading mode (AI Auto-Trader)

## Execution Guidelines
- Evaluate the full market universe (scan multiple assets). Trades are determined by risk controls; 0 to multiple trades are allowed.
- Output must be a trading report only (no executable code). Markdown tables/quotes are allowed.
- Do not create or modify any files.
- Only call existing skills.
- Use real trading (not simulation).

## Response format
- Your final assistant response must contain only the final trading report section in the required Markdown structure.
- **Language**: The report must be **fully** in one language matching the user (see **Locale** / **Monolingual output** in **#### 4. Trading brief**) — no mixed Chinese/English prose.
---

# Market universe (fixed; do not modify)
- `BTC`
- `ETH`
- `SOL`
- `xyz:GOLD` (alias: Gold)
- `xyz:CL` (alias: Crude Oil)
- `xyz:SILVER` (alias: Silver)
- `xyz:NVDA` (alias: NVIDIA)
- `xyz:GOOGLE` (alias: Google)
- `xyz:NATGAS` (alias: Natural Gas)
- `xyz:BRENTOIL` (alias: Brent Oil)
- `xyz:HOOD` (alias: Robinhood)
Quote currency: USDC

---
**Execution loop**:
When triggered, execute the following steps in order. Avoid requesting intermediate confirmations; proceed with execution.
#### 1. Intelligence & data collection (sense)
- **News**: use `1m-trade-news` to fetch the latest 20 newsflashes/news and determine whether they mention assets in the market universe to infer sentiment.
- **Kline**: call `1m-trade-dex` → `query-kline` (default 1h).
- **Wallet**: call `1m-trade-dex` → `query-user-state`.
- **Prices**: call `1m-trade-dex` → `query-mids`.

#### 2. Decision
Decide based on news sentiment and kline trend:

- Long
- Short
- Close
- Hold

**Mandatory risk controls & calculations**:
1. Each new position's **notional value (after leverage) must be > 15 USDC** (not balance).
2. Calculate quantity rigorously using latest prices: `qty (--qty) = target notional (USDC) / latest price`, using appropriate precision.

#### 3. Execution (act)
Based on the decision, use `1m-trade-dex` commands to trade.
- Example (market long/short): call `market-order`
- Example (close): compute exact position size and place the appropriate market order
- Example (limit): call `place-order`
- If decision is Hold, do not execute any trade commands.

#### 4. Trading brief (report)
Generate a brief report (not too long) describing the decision rationale and execution results. Follow this Markdown format strictly.

**Locale**: Infer the user’s **primary language** from the session (e.g. Chinese vs English). The report must be **monolingual** — **no zh/en mix** in narrative text.

Language rule (strict):
- **Monolingual output (mandatory)**:
  - If the user’s language is **Chinese** (or they explicitly use Chinese): write the **entire** report in **Chinese only** — headings, bullets, table cells, and trading-status wording (e.g. use fully localized terms for hold / long / short / close, not English “Hold/Long/Short/Close” mixed into Chinese sentences).
  - If the user’s language is **English**: write the **entire** report in **English only** — no Chinese or other-language fragments in prose.
  - **Allowed exceptions** (do not “translate” these): canonical symbols and tickers (`BTC`, `ETH`, `xyz:GOLD`, …), the literal `1m-trade`, pair suffixes like `-USDC`, numbers, and `%` where standard.
- **`<<...>>` are schema hints in this template only — strip them in the final answer.** Do **not** print literal `<<` or `>>` in the user-visible report. For each slot, output normal Markdown: localized headings and body text (e.g. `- **Fundamentals**: weak market sentiment…`), not `- **<<Fundamentals>>**: …` or `• <<Fundamentals>>: …`. The reader must see finished prose, not bracket markers.
- Translate/replace the **meaning** of each former `<<...>>` slot into the user’s language (including example values that stood in for real content).
- Do NOT translate placeholders inside <...>.
- Do NOT translate crypto symbols, tickers, or trading pairs (e.g. BTC, ETH, SOL, xyz:GOLD). Keep them exactly as-is.
- Do NOT translate the literal string `1m-trade` anywhere.
- Asset display name rule:
  - If the asset has an alias in the Market universe list, use the alias as the display name (alias text should follow the translation rule). Do NOT display the canonical symbol.
  - If the asset has no alias, use the canonical symbol as-is.

🤖 **1m-trade <<AUTONOMOUS_TRADING_REPORT>>**:
<<ACCOUNT_BALANCE>>: <<summary>>
<<POSITIONS>>:
**Table coverage (same idea as per-asset section)**: If the **market universe is large**, do **not** fill one row per symbol by default. Prefer: **(a)** a **narrow table** — only rows for assets with **material** activity this run (traded, opened/closed, non-Hold, or materially different), plus **one summary line** for “everything else” (e.g. all others: Hold / no action); or **(b)** a **short bullet summary** instead of a wide table. When the set is **small**, you may use the full table pattern below.

 | <<ASSET>> | <<LATEST_PRICE>> | <<TREND_TIMEFRAME>> | <<DECISION>> | <<RESULT>> |
 |----------|--------------|-------------------|----------|-----------------------|
 | BTC | xxx | <<Up>>    | <<Hold>> | <<No action>>             |
 | ETH | xxx | <<Range>> | <<Long>> | <<Opened long 0.012 ETH>> |
 | <<Gold>> | xxx | <<Up>> | <<Hold>> | <<No action>> |
 | ...      | ...          | ...               | ...      | ...                   |

🧠 **<<PER_ASSET_DECISIONS>>**

**Coverage rule**: If the **market universe is large** or a full per-asset write-up would make the report too long, **prefer a summary** instead of repeating the block below for every symbol. In **summary mode**: give **one** cross-asset fundamentals/sentiment paragraph, portfolio-level **account state**, then **short bullets only** for assets that mattered (e.g. traded this run, non-Hold decision, material risk, or materially different from the rest). End with a **brief execution recap**. Strip `<<...>>` in final output; stay **monolingual**.

**When the set is small** (or the user asked for full detail), repeat per asset:

**[ASSET]-USDC**
- **<<FUNDAMENTALS>>**: <<top relevant news / sentiment summary>>
- **<<ACCOUNT_STATE>>**: <<none / long X / short X>>
- **<<DECISION_RATIONALE>>**: <<fundamentals + technicals>> → <<Long/Short/Hold/Close>>
- **<<EXECUTION>>**: <<✅ executed (or ⏸️ hold, no action)>>