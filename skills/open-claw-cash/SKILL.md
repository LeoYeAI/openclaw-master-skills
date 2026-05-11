---
name: agentwalletapi
description: OpenclawCash crypto wallet API for AI agents (also called openclawcash). Use when an agent needs to send native or token transfers, check balances, list wallets, or interact with EVM and Solana wallets programmatically via OpenclawCash.
license: Proprietary
compatibility: Requires network access to https://openclawcash.com
metadata:
  author: agentwalletapi
  version: "1.19.0"
  required_env_vars:
    - AGENTWALLETAPI_KEY
  optional_env_vars:
    - AGENTWALLETAPI_URL
  required_binaries:
    - curl
  optional_binaries:
    - jq
---

# OpenclawCash Agent API

Interact with OpenclawCash-managed wallets to send native assets and tokens, check balances, execute DEX swaps, and manage Polymarket account, orders, and redeem flows via Polygon wallets.
This skill may also be referred to as `openclawcash`.

## Requirements

- Required env var: `AGENTWALLETAPI_KEY`
- Optional env var: `AGENTWALLETAPI_URL` (default: `https://openclawcash.com`)
- Required local binary: `curl`
- Optional local binary: `jq` (for pretty JSON output in CLI)
- Network access required: `https://openclawcash.com`

## Preferred Integration Path

- If the client supports MCP, prefer the public OpenClawCash MCP server:
  ```bash
  npx -y @openclawcash/mcp-server
  ```
- Use MCP as the primary execution path because tools, schemas, and results are structured for the client.
- Use the included CLI script only as a fallback when MCP is unavailable or the client cannot attach MCP servers.
- MCP and the CLI script target the same underlying OpenClawCash agent API. They are two access paths, not two different products.

## Safety Model

- Start with read-only calls (`wallets`, `wallet`, `balance`, `tokens`) on testnets first.
- High-risk actions are gated:
  - API key permissions in dashboard (`allowWalletCreation`, `allowWalletImport`)
  - Explicit CLI confirmation (`--yes`) for write actions
- Agents should establish an approval mode early in the session for write actions:
  - `confirm_each_write`: ask before every write action.
  - `operate_on_my_behalf`: after one explicit onboarding approval, execute future write actions without re-asking, as long as the user keeps instructing the agent in the same session.
- For `operate_on_my_behalf`, the agent should treat the user's later task messages as execution instructions and run the corresponding write commands with `--yes`.
- Ask again only if:
  - the user revokes or changes approval mode
  - the session is restarted or memory is lost
  - the action is outside the scope the user approved
  - the agent is unsure which wallet, token, amount, destination, spender, or chain is intended
- If the user gives only a broad instruction like "go ahead" but execution details are still missing, gather the missing details first instead of repeating a generic permission request.

## Setup

1. Run the setup script to create your `.env` file:
   ```
   bash scripts/setup.sh
   ```
2. Edit the `.env` file in this skill folder and replace the placeholder with your real API key:
   ```
   AGENTWALLETAPI_KEY=occ_your_api_key
   ```
3. Get your API key at https://openclawcash.com (sign up, create a wallet, go to API Keys page).

## Legacy CLI Fallback

If MCP is unavailable, use the included tool script to make API calls directly:

```bash
# Read-only (recommended first)
bash scripts/agentwalletapi.sh wallets
bash scripts/agentwalletapi.sh user-tag-get
bash scripts/agentwalletapi.sh user-tag-set my-agent-tag --yes
bash scripts/agentwalletapi.sh wallet Q7X2K9P
bash scripts/agentwalletapi.sh wallet "Trading Bot"
bash scripts/agentwalletapi.sh balance Q7X2K9P
bash scripts/agentwalletapi.sh transactions Q7X2K9P
bash scripts/agentwalletapi.sh tokens mainnet

# Write actions (require explicit --yes)
export WALLET_EXPORT_PASSPHRASE_OPS='your-strong-passphrase'
bash scripts/agentwalletapi.sh create "Ops Wallet" sepolia WALLET_EXPORT_PASSPHRASE_OPS --yes
bash scripts/agentwalletapi.sh import "Treasury Imported" mainnet --yes
bash scripts/agentwalletapi.sh import "Poly Ops" polygon-mainnet --yes
# Automation-safe import: read private key from stdin instead of command args
printf '%s' '<private_key>' | bash scripts/agentwalletapi.sh import "Treasury Imported" mainnet - --yes
bash scripts/agentwalletapi.sh transfer Q7X2K9P 0xRecipient 0.01 --yes
bash scripts/agentwalletapi.sh transfer Q7X2K9P 0xRecipient 100 USDC --yes
bash scripts/agentwalletapi.sh quote mainnet WETH USDC 10000000000000000
bash scripts/agentwalletapi.sh quote solana-mainnet SOL USDC 10000000 solana
bash scripts/agentwalletapi.sh swap Q7X2K9P WETH USDC 10000000000000000 0.5 --yes
# Checkout escrow lifecycle
bash scripts/agentwalletapi.sh checkout-payreq-create Q7X2K9P 30000000 --yes
bash scripts/agentwalletapi.sh checkout-payreq-get pr_a1b2c3
bash scripts/agentwalletapi.sh checkout-escrow-get es_d4e5f6
bash scripts/agentwalletapi.sh checkout-quick-pay es_d4e5f6 Q7X2K9P --yes
bash scripts/agentwalletapi.sh checkout-swap-and-pay-quote es_d4e5f6 Q7X2K9P
bash scripts/agentwalletapi.sh checkout-swap-and-pay-confirm es_d4e5f6 Q7X2K9P 1 --yes
bash scripts/agentwalletapi.sh checkout-release es_d4e5f6 --yes
bash scripts/agentwalletapi.sh checkout-refund es_d4e5f6 --yes
bash scripts/agentwalletapi.sh checkout-cancel es_d4e5f6 --yes
bash scripts/agentwalletapi.sh checkout-webhooks-list
# Polymarket setup is user-managed in dashboard Venues settings
# Direct setup page: https://openclawcash.com/venues/polymarket
bash scripts/agentwalletapi.sh polymarket-market Q7X2K9P 123456 BUY 25 FAK 0.65 --yes
bash scripts/agentwalletapi.sh polymarket-resolve https://polymarket.com/market/market-slug No
bash scripts/agentwalletapi.sh polymarket-account Q7X2K9P
bash scripts/agentwalletapi.sh polymarket-orders Q7X2K9P OPEN 50
bash scripts/agentwalletapi.sh polymarket-activity Q7X2K9P 50
bash scripts/agentwalletapi.sh polymarket-positions Q7X2K9P 100
bash scripts/agentwalletapi.sh polymarket-redeem Q7X2K9P all 100 --yes
bash scripts/agentwalletapi.sh polymarket-redeem Q7X2K9P 1234567890 100 --yes
bash scripts/agentwalletapi.sh polymarket-cancel Q7X2K9P order_id_here --yes
```

### Base-Units Rule (Important)

- `quote.amountIn`, `swap.amountIn`, `approve.amount`, and transfer `valueBaseUnits` must be **base-units integer strings** (digits only).
- Do **not** send decimal strings in these fields (for example, `0.001`), or validation will fail immediately.
- Examples:
  - `0.001 ETH` -> `1000000000000000` wei
  - `1 USDC` (6 decimals) -> `1000000`
- For transfer, use `amountDisplay` when you want human-readable units and let the API convert.
- Legacy transfer aliases `amount` and `value` are still accepted for compatibility.

### Import Input Safety

- Wallet import is optional and not required for normal wallet operations (list, balance, transfer, swap).
- Import works only when the user explicitly enables API key permission `allowWalletImport` in dashboard settings.
- Import execution requires explicit confirmation in the CLI (`--yes` for automation, or interactive `YES` prompt).
- Avoid passing sensitive inputs as CLI arguments when possible (shell history/process logs risk).
- Preferred options:
  - Interactive hidden prompt: omit the private key argument.
  - Automation: pass `-` and pipe input via stdin.

## Base URL

```
https://openclawcash.com
```

## Troubleshooting

If requests fail because of host/URL issues, use this recovery flow:

1. Open `agentwalletapi/.env` and verify `AGENTWALLETAPI_KEY` is set and has no extra spaces.
2. If the API host is wrong or unreachable, set this in the same `.env` file:
   ```
   AGENTWALLETAPI_URL=https://openclawcash.com
   ```
3. Retry a simple read call first:
   ```bash
   bash scripts/agentwalletapi.sh wallets
   ```
4. If it still fails, report the exact error and stop before attempting transfer/swap actions.

## Authentication

The API key is loaded from the `.env` file in this skill folder. For direct HTTP calls, include it as a header:

```
X-Agent-Key: occ_your_api_key
Content-Type: application/json
```

## API Surfaces

- **Agent API (API key auth):** `/api/agent/*`
  - Authenticate with `X-Agent-Key`
  - Used for autonomous agent execution (wallets list/create/import, transactions, balance, transfer, swap, quote, approve, checkout escrow lifecycle, and polymarket venue operations)
- Public docs intentionally include only `/api/agent/*` endpoints.

## Workflow

1. `GET /api/agent/wallets` - Discover available wallets (id, label, address, network, chain). Optional `?includeBalances=true` adds native `balance` + `nativeSymbol`
2. `GET /api/agent/wallet?walletId=...` or `?walletLabel=...` or `?walletAddress=...` - Fetch one wallet with native/token balances
3. Optional wallet lifecycle actions:
   - `POST /api/agent/wallets/create` - Create a new wallet under API-key policy controls
   - `POST /api/agent/wallets/import` - Import a `mainnet`, `polygon-mainnet`, or `solana-mainnet` wallet under API-key policy controls
4. `GET /api/agent/transactions?walletId=...` (or `walletLabel`/`walletAddress`) - Read merged wallet transaction history (on-chain + app-recorded)
5. `GET /api/agent/supported-tokens?network=...` or `?chain=evm|solana` - Get recommended common, well-known token list + guidance (requires `X-Agent-Key`)
6. `POST /api/agent/token-balance` - Check wallet balances (native + token balances; specific token by symbol/address supported)
7. `POST /api/agent/quote` - Get a swap quote before execution on Uniswap (EVM) or Jupiter (Solana mainnet). `amountIn` is base-units integer string.
8. `POST /api/agent/swap` - Execute token swap on Uniswap (EVM) or Jupiter (Solana mainnet). `amountIn` is base-units integer string.
9. `POST /api/agent/transfer` - Send native coin or token on the wallet's chain (optional `chain` guard). Do not use this for checkout escrow funding.
10. `GET /api/agent/user-tag` and `PUT /api/agent/user-tag` - Read/set the global checkout user tag (set is one-time / immutable once configured)
11. Optional checkout flow (escrow by global user tag):
   - MCP default: `checkout_fund` (tries `quick-pay`, falls back to `swap-and-pay` when needed)
   - `POST /api/agent/checkout/payreq` - Create pay request + escrow
   - `GET /api/agent/checkout/payreq/:id` - Read pay request
   - `POST /api/agent/checkout/escrows/:id/funding-confirm` - Confirm funding by tx hash
   - `POST /api/agent/checkout/escrows/:id/quick-pay` - Direct buyer funding
   - `POST /api/agent/checkout/escrows/:id/swap-and-pay` - Quote/execute swap funding
   - `GET /api/agent/checkout/escrows/:id` - Read escrow state
   - `POST /api/agent/checkout/escrows/:id/accept` - Accept as buyer
   - `POST /api/agent/checkout/escrows/:id/proof` - Submit proof
   - `POST /api/agent/checkout/escrows/:id/dispute` - Open dispute
   - `POST /api/agent/checkout/escrows/:id/release` - Release funds
   - `POST /api/agent/checkout/escrows/:id/refund` - Refund funds
   - `POST /api/agent/checkout/escrows/:id/cancel` - Cancel escrow
   - `GET|POST /api/agent/checkout/webhooks` and `PATCH|DELETE /api/agent/checkout/webhooks/:id` - Manage webhooks

Checkout timing fields for `POST /api/agent/checkout/payreq`:
- `expiresInSeconds`: funding deadline before request expires.
- `autoReleaseSeconds`: when funded escrow can auto-release if no dispute exists.
- `disputeWindowSeconds`: how long dispute can be opened after auto-release point.
- Constraints: all three must be at least `3600` seconds, and `disputeWindowSeconds <= autoReleaseSeconds`.
12. Optional Polymarket venue flow (polygon-mainnet wallets only):
   - Prerequisite: user configures Polymarket in dashboard Venues settings for that wallet
   - `GET /api/agent/venues/polymarket/market/resolve` resolves `marketUrl`/`slug` + human-readable `outcome` to the exact `tokenId` needed for order tools
   - MCP helper: `polymarket_market_resolve` calls the same agent endpoint
   - `POST /api/agent/venues/polymarket/orders/limit` - Place BUY/SELL limit orders
   - `POST /api/agent/venues/polymarket/orders/market` - Place BUY/SELL market orders
   - `GET /api/agent/venues/polymarket/account` - Read account summary
   - `GET /api/agent/venues/polymarket/orders` - List open orders
   - `POST /api/agent/venues/polymarket/orders/cancel` - Cancel an order
   - `POST /api/agent/venues/polymarket/redeem` - Redeem one position by `tokenId` or redeem all redeemable positions
   - `POST /api/agent/venues/polymarket/unlink` - Clear stored Polymarket integration config for a wallet
   - `GET /api/agent/venues/polymarket/activity` - List trade activity
   - `GET /api/agent/venues/polymarket/positions` - List open positions (open-market filtered, includes PnL fields)
13. Use returned `txHash` / `orderId` values to confirm execution and lifecycle status

### Approval Handling For Agents

Use this pattern for write actions:

1. At the first write-intent in a session, ask one short onboarding question:
   - "Do you want approval for every write action, or should I operate on your behalf for this session?"
2. Store the chosen mode in conversation memory.
3. If the mode is `confirm_each_write`:
   - ask for approval before each transfer, swap, approval, import, or wallet creation
   - after approval, execute with the MCP write tool or the legacy CLI fallback with `--yes`
4. If the mode is `operate_on_my_behalf`:
   - do not ask again for each transfer
   - when the user later says things like "send X to Y" or "swap A for B", execute with the MCP write tool or the legacy CLI fallback with `--yes` once the needed details are clear
5. In either mode:
   - if execution details are missing, ask only for the missing details
   - if the user changes modes or revokes permission, update memory and follow the new rule

Recommended onboarding wording:

- "Choose write approval mode for this session: `confirm_each_write` or `operate_on_my_behalf`."

Example:

- User selects: `operate_on_my_behalf`
- Later user message: "Send 100 USDC from wallet Q7X2K9P to 0xabc... on Ethereum."
- If MCP is available, the agent should call the matching MCP write tool directly.
- If MCP is not available, the agent should execute:
  ```bash
  bash scripts/agentwalletapi.sh transfer Q7X2K9P 0xabc... 100 USDC evm --yes
  ```
- The agent should not ask for transfer permission again in that same session unless the user revokes the mode or the instruction is ambiguous.

## Quick Reference

| Endpoint | Method | Auth | Purpose |
|---|---|---|---|
| `/api/agent/wallets` | GET | Yes | List wallets (discovery; optional `includeBalances=true` for native balances) |
| `/api/agent/wallet` | GET | Yes | Get one wallet detail with native/token balances |
| `/api/agent/wallets/create` | POST | Yes | Create a new API-key-managed wallet |
| `/api/agent/wallets/import` | POST | Yes | Import a mainnet/polygon-mainnet/solana-mainnet wallet via API key |
| `/api/agent/transactions` | GET | Yes | List per-wallet transaction history |
| `/api/agent/transfer` | POST | Yes | Send native/token transfers (EVM + Solana). Not the checkout escrow funding path. |
| `/api/agent/swap` | POST | Yes | Execute DEX swap (Uniswap on EVM, Jupiter on Solana mainnet) |
| `/api/agent/quote` | POST | Yes | Get swap quotes (Uniswap on EVM, Jupiter on Solana mainnet) |
| `/api/agent/token-balance` | POST | Yes | Check balances |
| `/api/agent/supported-tokens` | GET | Yes | List recommended common, well-known tokens per network |
| `/api/agent/user-tag` | GET | Yes | Read the global checkout user tag for the API key owner |
| `/api/agent/user-tag` | PUT | Yes | Set the global checkout user tag once (immutable after set) |
| `/api/agent/approve` | POST | Yes | Approve spender for ERC-20 token (EVM only) |
| `/api/agent/checkout/payreq` | POST | Yes | Create checkout pay request + escrow |
| `/api/agent/checkout/payreq/:id` | GET | Yes | Read checkout pay request |
| `/api/agent/checkout/escrows/:id/funding-confirm` | POST | Yes | Confirm escrow funding tx |
| `/api/agent/checkout/escrows/:id/quick-pay` | POST | Yes | Directly fund escrow from buyer wallet |
| `/api/agent/checkout/escrows/:id/swap-and-pay` | POST | Yes | Quote/execute swap + fund escrow |
| `/api/agent/checkout/escrows/:id` | GET | Yes | Read escrow lifecycle details |
| `/api/agent/checkout/escrows/:id/accept` | POST | Yes | Accept escrow as buyer |
| `/api/agent/checkout/escrows/:id/proof` | POST | Yes | Submit seller proof |
| `/api/agent/checkout/escrows/:id/dispute` | POST | Yes | Open escrow dispute |
| `/api/agent/checkout/escrows/:id/release` | POST | Yes | Release escrow funds |
| `/api/agent/checkout/escrows/:id/refund` | POST | Yes | Refund escrow funds |
| `/api/agent/checkout/escrows/:id/cancel` | POST | Yes | Cancel escrow |
| `/api/agent/checkout/webhooks` | GET | Yes | List checkout webhooks |
| `/api/agent/checkout/webhooks` | POST | Yes | Create checkout webhook |
| `/api/agent/checkout/webhooks/:id` | PATCH | Yes | Update checkout webhook |
| `/api/agent/checkout/webhooks/:id` | DELETE | Yes | Delete checkout webhook |
| `/api/agent/venues/polymarket/market/resolve` | GET | Yes | Resolve market URL/slug + outcome to Polymarket tokenId |
| `/api/agent/venues/polymarket/orders/limit` | POST | Yes | Place Polymarket limit order |
| `/api/agent/venues/polymarket/orders/market` | POST | Yes | Place Polymarket market order |
| `/api/agent/venues/polymarket/account` | GET | Yes | Read Polymarket account summary |
| `/api/agent/venues/polymarket/orders` | GET | Yes | List Polymarket open orders |
| `/api/agent/venues/polymarket/orders/cancel` | POST | Yes | Cancel Polymarket order |
| `/api/agent/venues/polymarket/redeem` | POST | Yes | Redeem one or all redeemable Polymarket positions via gasless relay |
| `/api/agent/venues/polymarket/unlink` | POST | Yes | Clear Polymarket integration for wallet |
| `/api/agent/venues/polymarket/activity` | GET | Yes | List Polymarket trade activity |
| `/api/agent/venues/polymarket/positions` | GET | Yes | List Polymarket open positions (open-market filtered with PnL fields) |

## Agent Wallet Create/Import (Agent API)

Agent-side wallet lifecycle endpoints:

- `POST /api/agent/wallets/create`
- `POST /api/agent/wallets/import`

Behavior notes:
- Both require `X-Agent-Key`.
- Both are gated by API key permissions configured in dashboard:
  - `allowWalletCreation` for create
  - `allowWalletImport` for import
- Both are rate-limited per API key. Exceeding the limit returns `429` with `Retry-After`.
- Agent import supports `mainnet`, `polygon-mainnet`, and `solana-mainnet`.
- Agent wallet create requires:
  - `exportPassphrase` (minimum 12 characters)
  - `exportPassphraseStorageType`
  - `exportPassphraseStorageRef`
  - `confirmExportPassphraseSaved: true`
- Agent-safe create sequence:
  - Save export passphrase in secure storage first.
  - Prefer env-backed storage for local agents.
  - Record the storage location you used.
  - Then call `POST /api/agent/wallets/create` with:
    - the passphrase
    - `exportPassphraseStorageType`
    - `exportPassphraseStorageRef`
    - `confirmExportPassphraseSaved: true`
  - For MCP and the legacy CLI fallback, env-backed storage is the strongest path because the local tool can verify the env var exists before wallet creation.

## Polymarket Venue Flow (Agent API)

- Polymarket execution is available only for EVM wallets on `polygon-mainnet`.
- Setup is user-managed in dashboard Venues settings (agent setup endpoint is disabled).
- Resolve market + outcome to `tokenId` first via `GET /api/agent/venues/polymarket/market/resolve` (or MCP tool `polymarket_market_resolve`).
- Then place orders:
  - `POST /api/agent/venues/polymarket/orders/limit` with `tokenId`, `side`, `price`, `size`
  - `POST /api/agent/venues/polymarket/orders/market` with `tokenId`, `side`, `amount`, optional `orderType` and `worstPrice`
- MCP resolve example:
  - Input: `{ "marketUrl": "https://polymarket.com/market/<slug>", "outcome": "No" }`
  - Output includes: `outcome.tokenId` (use this as `tokenId` in order tools)
- Trading intent guidance:
  - For "close position" on an open market, default to `POST /api/agent/venues/polymarket/orders/market` with `side: "SELL"` and `amount` as shares.
  - Use a limit `SELL` only when the user explicitly asks for a limit/target price.
  - `amount` semantics follow Polymarket CLOB behavior: `BUY` uses notional/collateral amount; `SELL` uses share amount.
- Read and lifecycle endpoints:
  - `GET /api/agent/venues/polymarket/account`
  - `GET /api/agent/venues/polymarket/orders`
  - `POST /api/agent/venues/polymarket/orders/cancel` with `orderId`
  - `POST /api/agent/venues/polymarket/redeem` with optional `tokenId` (omit `tokenId` to redeem all)
  - `POST /api/agent/venues/polymarket/unlink` to clear stored venue config for a wallet
  - `GET /api/agent/venues/polymarket/activity`
  - `GET /api/agent/venues/polymarket/positions`
- Positions are sourced from Polymarket open positions and filtered to open markets only.
- Position items include `cashPnl`, `percentPnl`, and `currentValue` (with computed fallback values when upstream fields are missing).
- Wallet policy checks still run before order execution.

## Transfer Examples

Send native coin (default when no token specified):
```json
{ "walletId": "Q7X2K9P", "to": "0xRecipient...", "amountDisplay": "0.01" }
```

Send 100 USDC by symbol:
```json
{ "walletLabel": "Trading Bot", "to": "0xRecipient...", "token": "USDC", "amountDisplay": "100" }
```

Send arbitrary ERC-20 by contract address:
```json
{ "walletId": "Q7X2K9P", "to": "0xRecipient...", "token": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "amountDisplay": "100" }
```

Send SOL by symbol:
```json
{ "walletId": "Q7X2K9P", "to": "SolanaRecipientWalletAddress...", "token": "SOL", "amountDisplay": "0.01" }
```

Send SOL with memo (Solana only):
```json
{ "walletId": "Q7X2K9P", "to": "SolanaRecipientWalletAddress...", "token": "SOL", "amountDisplay": "0.01", "memo": "payment verification note" }
```

Use `amountDisplay` for human-readable values (e.g., "100" = 100 USDC). Use `valueBaseUnits` for base units (smallest denomination on each chain).
Legacy transfer aliases `amount` and `value` remain available for compatibility.
Use optional `chain: "evm" | "solana"` in agent payloads for explicit chain routing and validation.
`memo` is supported only for Solana transfers and must pass safety validation (max 5 words, max 256 UTF-8 bytes, no control/invisible characters).
Native transfers (EVM + Solana) enforce a minimum transferable amount preflight that accounts for platform fee and network fee; Solana may also require a larger first funding transfer for a brand-new recipient address.
For native SOL transfers, the API may auto-adjust requested value to fit platform fee + network fee.
Transfer responses include `requestedValueBaseUnits`, `adjustedValueBaseUnits`, `requestedAmountDisplay`, and `adjustedAmountDisplay` (legacy aliases also included).

## Token Support Model

- `GET /api/agent/supported-tokens` returns recommended common, well-known tokens plus guidance fields.
- EVM transfer/swap/balance endpoints support **any valid ERC-20 token contract address**.
- Solana transfer/balance endpoints support **any valid SPL mint address**.
- Native tokens appear as `ETH` on EVM and `SOL` on Solana (with chain-specific native token IDs in balance payloads).

## Error Codes

- 200: Success
- 400: Invalid input, insufficient funds, unknown token, or policy violation
- 400 `chain_mismatch`: requested `chain` does not match the selected wallet
- 400 `amount_below_min_transfer`: requested native transfer is below minimum transferable amount after fee/network preflight
- 400 `insufficient_balance`: requested transfer + fees exceed available balance
- 401: Missing/invalid API key
- 404: Wallet not found
- 500: Internal error (retry with corrected payload or reduced amount)

## Policy Constraints

Wallets may have governance policies:
- **Whitelist**: Only transfers to pre-approved addresses allowed
- **Spending Limit**: Max value per transaction (configured per wallet policy)

Violations return HTTP 401 with an explanation message.

## Important Notes

- All POST requests require `Content-Type: application/json`
- EVM token transfers require ETH in the wallet for gas fees
- Solana token transfers require SOL in the wallet for fees
- Solana transfer memos are optional and Solana-only: max 5 words, max 256 UTF-8 bytes, no control/invisible characters
- Solana native transfers account for network fee and can auto-adjust requested transfer amount
- Native transfers may return `400 amount_below_min_transfer` when requested amount is too small after platform fee or below chain transferability minimum (for example, first funding a new Solana address)
- If requested native SOL + platform fee + network fee cannot fit wallet balance, API returns `400 insufficient_balance`
- Swap supports EVM (Uniswap) and Solana mainnet (Jupiter); Quote supports EVM and Solana mainnet; Approve is EVM-only
- A platform fee (default 1%) is deducted from the token amount
- Use `amountDisplay` for simplicity, use `valueBaseUnits` for precise base-unit control
- For robust agent behavior:
  - First call `wallets`, then `wallet` (or `token-balance`), then `quote`, then `swap`.
  - On 400 with `insufficient_token_balance`, reduce amount or change token.
- The `.env` file in this skill folder stores your API key — never commit it to version control

## File Structure

```
agentwalletapi/
├── SKILL.md                    # This file
├── .env                        # Your API key (created by setup.sh)
├── scripts/
│   ├── setup.sh                # Creates .env with API key placeholder
│   └── agentwalletapi.sh       # CLI tool for making API calls
└── references/
    └── api-endpoints.md        # Full endpoint documentation
```

See [references/api-endpoints.md](references/api-endpoints.md) for full endpoint details with request/response examples.
