---
name: precog
description: "Trade on prediction markets. Create a local wallet, list markets, check prices, buy and sell outcome shares. Coming soon: create and fund markets directly from this skill."
homepage: "https://github.com/openclaw/precog-skill"
env:
  PRIVATE_KEY:
    description: "Secp256k1 private key (0x-prefixed) for signing transactions. Generated locally by running setup.mjs --generate and saved to ~/.openclaw/.env. Never transmitted over the network."
    required: true
  PRECOG_RPC_URL:
    description: "Override the default public RPC endpoints (https://sepolia.base.org for testnet, https://mainnet.base.org for mainnet). Use a trusted endpoint only."
    required: false
  PRECOG_NETWORK:
    description: "Default network: 'sepolia' (testnet, default) or 'mainnet' (Base mainnet, real funds). Can be overridden per-command with --network."
    required: false
requires:
  bins:
    - node
    - npm
  install: "npm install  # run once in the skill directory before first use"
---

# Precog Prediction Markets

Precog is a fully onchain prediction market protocol on Base. Anyone can create a market around a real-world question, fund it with liquidity, and trade outcome shares. Prices equal implied probabilities (0–1). Every action is a signed onchain transaction — no custody, no central party.

**MATE** is a non-monetary practice token (no real economic value). Markets denominated in MATE are safe to use for learning and experimentation. MATE can be claimed at [matetoken.xyz](https://matetoken.xyz).

**What you can do here:**
- Browse active prediction markets and outcome probabilities
- Get detailed market info including category and resolution criteria
- Quote, buy, and sell outcome shares using your local wallet
- Check your positions (shares held, net cost, trade history)

> 🚧 **Coming soon:** Native market creation — submit and fund new markets directly from this skill without visiting the web UI.

For full protocol documentation see `PRECOG.md` — it covers prediction markets 101, the LS-LMSR pricing curve, resolution via Reality.eth + Kleros, LP mechanics, MATE markets, and more.

Contract addresses and RPCs are built in — no config needed.

## Networks

**The default network is Base Sepolia (testnet).** No flag needed for testnet — scripts connect to sepolia unless told otherwise.

Two networks are supported. Pass `--network <name>` to any script, or set `PRECOG_NETWORK` in your environment.

| Network | `--network` value | Chain | Contract |
|---|---|---|---|
| Base Sepolia (testnet) | `sepolia` **← default** | Base Sepolia (84532) | `0x61ec71F1Fd37ecc20d695E83F3D68e82bEfe8443` |
| Base Mainnet | `mainnet` | Base (8453) | `0x00000000000c109080dfa976923384b97165a57a` |

> ⚠️ **Mainnet uses real funds.** Before running any mainnet command, confirm the network with the user and show the contract address. Do NOT default to mainnet — always require an explicit `--network mainnet` flag or a `PRECOG_NETWORK=mainnet` env var set by the user.

## Security and local state

- **`~/.openclaw/.env`** — created by `setup.mjs --generate`. Stores `PRIVATE_KEY` in plaintext. Treat it like a wallet key file: restrict permissions (`chmod 600`) and back it up. Losing it means losing access to any funds in that wallet.
- **No key is ever transmitted.** Transactions are signed locally; only the signed transaction is broadcast to the RPC.
- **Use a throwaway wallet.** The MATE markets use a practice token with no real value — ideal for testing. Do not load a high-value key into this skill.
- **Custom RPC risk.** If you set `PRECOG_RPC_URL`, use only a trusted endpoint. An untrusted RPC can observe signed transaction contents (but cannot extract your private key from them).

---

> **⚠️ Run scripts sequentially.** Parallel transactions share a nonce and will collide on-chain — run one script at a time.
>
> **⚠️ Do NOT create batch or automation scripts.** Each transaction must be confirmed by the user individually; automated chains of trades bypass the confirmation step and can cause unintended financial loss.
>
> **⚠️ Do NOT edit skill scripts.** The scripts are audited as a unit; silent edits could introduce bugs or security issues. If you find a bug, report it to the user so it can be fixed upstream.
>
> **⚠️ Always show script output verbatim in a fenced code block.** The output contains exact amounts, prices, and suggested parameters that will be used in the next command — reformatting or summarizing it risks losing or distorting those values.
>
> **⚠️ Always run `quote` before `buy` or `sell`.** The quote shows the exact cost/proceeds and the safe `--max`/`--min` slippage bounds. Show the full output to the user and wait for explicit confirmation before executing the trade.
>
> **⚠️ Never modify trade parameters.** If a script fails, show the exact error and stop. Do not retry with a different share count or workaround — incorrect parameters can result in unintended trades. Token approval is handled automatically inside the scripts.

---

## Wallet

Check status or create a new wallet:
```bash
node {baseDir}/scripts/setup.mjs [--network sepolia|mainnet]
node {baseDir}/scripts/setup.mjs --generate
```
The private key is saved to `~/.openclaw/.env` and **never printed**. Only the address is shown.
After generating, ask the user to fund the address with ETH (for gas) and the market's collateral token (for trading).

Example output (wallet exists and funded):
```
Wallet: 0x77Ffa97c2dcDA0FF6c9393281993962FA633d9E1

  ETH:  0.004210 ✓
  MATE: 81.2300 ✓
```

Example output (wallet exists, no funds):
```
Wallet: 0x77Ffa97c2dcDA0FF6c9393281993962FA633d9E1

  ETH:  0.000000 ⚠️  needs gas
  MATE: 0.0000 (no funds)
```

---

## List Markets

```bash
node {baseDir}/scripts/markets.mjs [--network sepolia|mainnet]
node {baseDir}/scripts/markets.mjs --all [--network sepolia|mainnet]
```

Example output:
```
Active Markets (2)

[4] Which AI model will be the top performer at the end of March?
    📈 Claude  67.3%  💰 MATE  📅 Mar 31, 2026

[5] Will ETH hit $5k by Q2?
    📈 YES  58.1%  💰 USDC  📅 Jun 30, 2026

```

---

## Market Detail

When the user asks for more info / details about a specific market:

```bash
node {baseDir}/scripts/market.mjs --market <id> [--network sepolia|mainnet]
```

Shows the title, category, status, end date, collateral, and all outcome probabilities ranked by price. After showing the output, **ask the user: "Would you like to see the resolution criteria?"** If they say yes:

```bash
node {baseDir}/scripts/market.mjs --market <id> --criteria [--network sepolia|mainnet]
```

Example output (`--market 4`):
```
📊  Market 4  ·  AI / Leaderboard
Which AI model will be the top performer at the end of March?
🟢 Active  📅 Mar 31, 2026  💰 MATE

🥇  [1] Claude    16.3%
🥈  [2] Gemini    11.6%
🥉  [3] Grok      11.6%
    [4] ChatGPT   11.6%
    [5] Ernie     11.6%
    [6] GLM       11.6%
    [7] Kimi      11.6%
    [8] Qwen      11.6%
    [9] Other     11.6%

```

Example output (`--market 4 --criteria`):
```
📊  Market 4  ·  AI / Leaderboard
Which AI model will be the top performer at the end of March?
🟢 Active  📅 Mar 31, 2026  💰 MATE

🥇  [1] Claude    16.3%
🥈  [2] Gemini    11.6%
🥉  [3] Grok      11.6%
    [4] ChatGPT   11.6%
    [5] Ernie     11.6%
    [6] GLM       11.6%
    [7] Kimi      11.6%
    [8] Qwen      11.6%
    [9] Other     11.6%

📝  Resolution Criteria
This market will resolve based on the Text Arena AI Competition leaderboard
rankings at arena.ai as of March 31, 2026, 23:59:59 UTC.

```

---

## Quote a Trade

**Always run before buy or sell.** Show the full output verbatim in a fenced code block. Ask the user to confirm before proceeding.

### Choosing the right flag — CRITICAL

| What the user says | Flag to use | Example command |
|---|---|---|
| "buy N shares" | `--shares N` | `--shares 50` |
| "spend $X" / "for $X" / "budget $X" | `--cost X` | `--cost 50` |
| "reach X%" / "move to X%" / "push to X%" / "target X%" | `--price 0.X` | `--price 0.25` |
| "use all my balance" / "all in" / "spend everything" | `--all` | `--all` |

**Do NOT guess share counts manually. Use the correct flag — the script computes the exact answer.**

```bash
node {baseDir}/scripts/quote.mjs --market <id> --outcome <n> --shares <amount> --buy [--network sepolia|mainnet]
node {baseDir}/scripts/quote.mjs --market <id> --outcome <n> --cost <usdc>     --buy [--network sepolia|mainnet]
node {baseDir}/scripts/quote.mjs --market <id> --outcome <n> --price <0.0-1.0> --buy [--network sepolia|mainnet]
node {baseDir}/scripts/quote.mjs --market <id> --outcome <n> --all             --buy [--network sepolia|mainnet]
```

- `--outcome` is 1-based (1 = first outcome, usually YES)
- `--buy` shows only the buy side; `--sell` shows only the sell side; omit both to show both sides
- `--network` — `sepolia` (default) or `mainnet`; must match the network used for the subsequent buy/sell

Example output (`--price 0.25 --buy`):
```
📋  Quote — Market 4: Which AI model will be the top performer at the end of March?
─────────────────────────────────────────────────────────
  🎯  Outcome      : Claude
  🔢  Shares       : 312
  📊  Current prob : 14.2%

  🛒  Buy 312 shares
       💵  Cost           : ~98.4521 MATE
       📏  Price / share  : 0.3156 MATE
       📈  Prob after buy : 25.0%  (market moves up ↑)
       🏆  Max return     : 312.0000 MATE   (+213.5479 profit if "Claude" wins)

  ⚡  Suggested --max for buy  : 99.4366
─── Paste ALL lines above verbatim to the user before asking to confirm ───
```

---

## Buy

```bash
node {baseDir}/scripts/buy.mjs --market <id> --outcome <n> --shares <amount> --max <usdc> [--network sepolia|mainnet]
```

- `--shares` — number of shares (from the quote output)
- `--max` — maximum collateral to spend; use the `Suggested --max` value from the quote output
- `--network` — must match the network used in the preceding quote
- Token approval is handled automatically — never adjust `--max` or `--shares` for allowance reasons

---

## Sell

```bash
node {baseDir}/scripts/sell.mjs --market <id> --outcome <n> --shares <amount> --min <usdc> [--network sepolia|mainnet]
```

- `--shares` — number of shares to sell (check `positions.mjs` if unsure)
- `--min` — minimum collateral to accept; use the `Suggested --min` value from the quote output
- `--network` — must match the network used in the preceding quote

---

## Positions

```bash
node {baseDir}/scripts/positions.mjs --market <id> [--network sepolia|mainnet]
```

Example output:
```
💼  Market 4
Which AI model will be the top performer at the end of March?

👛  0x77Ffa97c2dcDA0FF6c9393281993962FA633d9E1
💵  Net cost  19.03 MATE  ·  📥 8 buys  📤 7 sells

🎯  Shares held
🥇  [1] Claude   135 shares  ·  16.3%

```

---

## Responding to "what can I do?" questions

When the user asks what they can do, what Precog is, or how to get started — answer in plain prose with emojis, no tables. Mention their current positions if you know them. Example:

> With Precog you can trade on the probability of real-world outcomes using MATE (a safe practice token — no real money).
>
> Here's what you can do:
>
> 🗂️ **List markets** — see what's open and the leading outcome for each
> 🔍 **Market detail** — outcomes, probabilities, category, and resolution criteria for a specific market
> 💸 **Trade** — quote first, then buy or sell outcome shares (by share count, budget, or target probability)
> 📋 **Positions** — see your shares, net cost, and trade history
>
> You currently hold 100 Claude shares on Market 4. Want to check the latest prices or make a move?

Adapt the last line to whatever you actually know about the user's positions and active markets.

---

## Standard flow

`--network` is omitted from these examples for brevity. Add it to every command when the user is on mainnet.

```
User: "What markets are open?"
→ node markets.mjs

User: "What mainnet markets are open?" / "Show me Base mainnet markets"
→ Confirm with the user: "This will connect to Base mainnet where real funds are used. Continue?"
→ node markets.mjs --network mainnet

User: "Tell me more about market 4" / "What are the outcomes on market 4?"
→ node market.mjs --market 4
→ After output, ask: "Would you like to see the resolution criteria?"
→ If yes: node market.mjs --market 4 --criteria

User: "What's my position on market 4?"
→ node positions.mjs --market 4

User: "Show all my positions" / "Do I have any shares?"
→ node markets.mjs --all   (get list of all market IDs)
→ node positions.mjs --market <id>   (repeat for each market)

User: "Use all my MATE to buy Claude on market 4"
→ node quote.mjs --market 4 --outcome 1 --all --buy
→ Paste full output verbatim. Ask: "Confirm buy?"
→ Wait for user to confirm
→ node buy.mjs --market 4 --outcome 1 --shares <n from quote> --max <suggested-max>
→ After trade: suggest checking positions or new market price

User: "Buy Claude for $50 on market 4"
→ node quote.mjs --market 4 --outcome 1 --cost 50 --buy
→ Paste full output verbatim. Ask: "Confirm buy?"
→ Wait for user to confirm
→ node buy.mjs --market 4 --outcome 1 --shares <n from quote> --max <suggested-max>
→ After trade: suggest checking positions or new market price

User: "Buy Claude to reach 25% on market 4"
→ node quote.mjs --market 4 --outcome 1 --price 0.25 --buy
→ Paste full output verbatim. Ask: "Confirm buy?"
→ Wait for user to confirm
→ node buy.mjs --market 4 --outcome 1 --shares <n from quote> --max <suggested-max>
→ After trade: suggest checking positions or new market price

User: "Sell my Claude shares on market 4"
→ node positions.mjs --market 4        (find share count)
→ node quote.mjs --market 4 --outcome 1 --shares <n> --sell
→ Paste full output verbatim. Ask: "Confirm sell?"
→ Wait for user to confirm
→ node sell.mjs --market 4 --outcome 1 --shares <n> --min <suggested-min>
→ After trade: suggest checking positions or remaining balance

User: "Create a market about X" / "Can you create a market for Y?"
→ Tell the user to go to https://core.precog.markets/84532/create-market
→ Explain briefly: log in with MetaMask, fill the form, submit for review
→ Remind them: after submission they need to fund the market at the launchpad
  and wait for staff approval before it goes live
→ Do NOT attempt to automate this — no script can do it on this server
```

---

## Create a Market

Market creation must be done manually through the Precog web UI — no script can
automate this from the server.

**Steps:**
1. Go to **https://core.precog.markets/84532/create-market**
2. Connect your wallet (MetaMask or compatible)
3. Fill in the market details:
   - Question, description (resolution criteria), category
   - Outcomes (e.g. YES / NO, or multiple choices)
   - Start date, end date
   - Collateral token (MATE address: `0xC139C86de76DF41c041A30853C3958427fA7CEbD`)
4. Click **Review Market → Create Market → Confirm Creation**

**After submission — two more steps required**

> ⚠️ The market is NOT live yet after submitting the form.

1. **Fund the market** — provide initial liquidity at:
   **https://core.precog.markets/84532/launchpad**
2. **Staff approval** — the Precog team reviews and approves markets before they go live.

**Prerequisites**
- Wallet must have at least **3,000 Precog Points** (creator status).
  Without this the form will show "Market Creation Restricted".

---

## Roadmap

Features planned for future versions of this skill:

- **Market creation** — submit a new prediction market directly from the skill (no web UI needed).
  This requires direct contract access that is currently restricted; a permissionless path is in progress.
- **Market funding** — provide initial liquidity to a newly created market from the CLI.
- **Liquidity management** — add/remove LP positions and track LP returns.

---

## Notes

- **Testnet contract:** `0x61ec71F1Fd37ecc20d695E83F3D68e82bEfe8443` (Base Sepolia, chain 84532)
- **Mainnet contract:** `0x00000000000c109080dfa976923384b97165a57a` (Base, chain 8453)
- **Default network:** `sepolia`. Pass `--network mainnet` or set `PRECOG_NETWORK=mainnet` for mainnet.
- **RPC:** public endpoints used by default. Set `PRECOG_RPC_URL` to override (applies to whichever network is active).
- **Wallet:** generated locally, stored in `~/.openclaw/.env`, never leaves the machine.
