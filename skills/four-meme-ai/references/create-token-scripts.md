# Create Token Scripts (Four.meme)

**Recommended:** Use `fourmeme create-instant` for one-shot token creation (API + on-chain in one command). Use the step-by-step flow only when you need to inspect or modify the API output before submitting on-chain.

## One-shot (create-instant) — recommended

**create-token-instant.ts** runs API create + on-chain submit in one command. Same args as create-token-api; on success submits createToken and outputs `txHash`.

- All options as `--key=value`; no positionals.
- **Required**: `--image=`, `--name=`, `--short-name=`, `--desc=`, `--label=`.
- **Optional**: `--web-url=`, `--twitter-url=`, `--telegram-url=` (only sent when non-empty); `--pre-sale=0` (**presale in ether units**, e.g. `0.001` for 0.001 BNB, not wei); `--fee-plan=false`, `--tax-options=<path>`; `--value=<wei>` (default to be auto calculated, override BNB value sent; otherwise API output `creationFeeWei` is used).
- **Tax token**: `--tax-options=tax.json` or `--tax-token` with `--tax-fee-rate=5` `--tax-burn-rate=0` `--tax-divide-rate=0` `--tax-liquidity-rate=100` `--tax-recipient-rate=0` `--tax-recipient-address=` `--tax-min-sharing=100000` (burn+divide+liquidity+recipient=100).
- **Label** (exactly one): `Meme` | `AI` | `Defi` | `Games` | `Infra` | `De-Sci` | `Social` | `Depin` | `Charity` | `Others`.
- **Env**: `PRIVATE_KEY`; RPC via `BSC_RPC_URL`.
- **Flow**: nonce → login → upload image → GET public config → POST create → submit `TokenManager2.createToken` on BSC.
- **Output**: JSON `{ "txHash" }`.

```bash
# Via CLI (recommended)
fourmeme create-instant --image=./logo.png --name=MyToken --short-name=MTK --desc="My desc" --label=AI

# With presale (BNB, ether units)
fourmeme create-instant --image=./logo.png --name=MyToken --short-name=MTK --desc="My desc" --label=AI --pre-sale=0.001

# Tax token
fourmeme create-instant --image=./logo.png --name=TaxToken --short-name=TAX --desc="Tax" --label=Meme --tax-options=tax.json
```

---

## Step-by-step flow (create-api → create-chain)

1. **get-public-config.ts** (optional)  
   Fetches `raisedToken` from `https://four.meme/meme-api/v1/public/config`. Use when building the create body manually.

2. **create-token-api.ts**  
   - All options as `--key=value`; no positionals.  
   - Required: `--image=`, `--name=`, `--short-name=`, `--desc=`, `--label=`.  
   - Optional: `--web-url=`, `--twitter-url=`, `--telegram-url=` (only sent when non-empty); `--pre-sale=0` (**presale in ether units**, e.g. `0.001` for 0.001 BNB, not wei); `--fee-plan=false`, `--tax-options=<path>`.  
   - Tax token: `--tax-options=tax.json` or `--tax-token` with `--tax-fee-rate=5` etc. (burn+divide+liquidity+recipient=100).  
   - Env: `PRIVATE_KEY`; RPC via `BSC_RPC_URL`.  
   - Flow: nonce → login → upload image → GET public config → POST create.  
   - Output: JSON `{ "createArg", "signature", "creationFeeWei" }`; script hints required value for chain step.

3. **create-token-chain.ts**  
   - Env: `PRIVATE_KEY`.  
   - Input: `createArg`, `signature` (positional or stdin JSON with `--`).  
   - Optional (CLI overrides env): `--value=<wei>` (env `CREATION_FEE_WEI`). RPC via env `BSC_RPC_URL`.  
   - Calls `TokenManager2.createToken(createArg, sign)`; excess BNB is refunded by the contract.

## createToken value (CREATION_FEE_WEI) formula

**Formula**

- **No presale (or quote is ERC20)**  
  `value = launch_fee`  
  `launch_fee`: read from TokenManager2 `_launchFee()` (wei).

- **With presale and quote is BNB**  
  `value = launch_fee + presale_wei + trading_fee`  
  - `presale_wei`: presale amount in wei (API sends preSale in BNB/ether; script converts to wei for value).  
  - `trading_fee`: see below.

**How to compute trading_fee**

- Contract uses basis-point rate: `trading_fee = presale_wei × fee_rate / 10000` (integer division).  
- `fee_rate` from TokenManager2 `_tradingFeeRate()` (basis points).  
- If the contract enforces a minimum fee per trade, use `max(computed trading_fee, minimum_fee)`.

## Example (instant, recommended)

```bash
export PRIVATE_KEY=your_hex_private_key
fourmeme create-instant --image=./logo.png --name=MyToken --short-name=MTK --desc="My desc" --label=AI
```

## Example (piped)

```bash
export PRIVATE_KEY=your_hex_private_key
npx tsx skills/four-meme-integration/scripts/create-token-api.ts --image=./logo.png --name=MyToken --short-name=MTK --desc="My desc" --label=AI \
  | npx tsx skills/four-meme-integration/scripts/create-token-chain.ts --
```

The chain script reads `creationFeeWei` from stdin JSON when present; you can also pass `--value=<wei>` explicitly.

## Example (two steps)

```bash
export PRIVATE_KEY=your_hex_private_key
npx tsx skills/four-meme-integration/scripts/create-token-api.ts --image=./logo.png --name=MyToken --short-name=MTK --desc="My desc" --label=AI > create-out.json
npx tsx skills/four-meme-integration/scripts/create-token-chain.ts "$(jq -r .createArg create-out.json)" "$(jq -r .signature create-out.json)" --value=$(jq -r .creationFeeWei create-out.json)
```

## Example (with presale)

`--pre-sale` is in **ether units** (e.g. `0.001` = 0.001 BNB; do not pass wei).

```bash
npx tsx .../create-token-api.ts --image=./logo.png --name=MyToken --short-name=MTK --desc="My desc" --label=AI --pre-sale=0.01
```

## Tax token

Tax options file must contain `tokenTaxInfo`. Example **tax-options.json**:

```json
{
  "tokenTaxInfo": {
    "feeRate": 5,
    "burnRate": 20,
    "divideRate": 30,
    "liquidityRate": 40,
    "recipientRate": 10,
    "recipientAddress": "0x1234567890123456789012345678901234567890",
    "minSharing": 100000
  }
}
```

`feeRate` must be 1, 3, 5, or 10; burn+divide+liquidity+recipient=100. See [token-tax-info.md](token-tax-info.md).

```bash
# Option A: --tax-options= path to JSON file
npx tsx .../create-token-api.ts --image=./logo.png --name=TaxToken --short-name=TAX --desc="Tax token" --label=AI --tax-options=tax-options.json

# Option B: --tax-token with rate args
npx tsx .../create-token-api.ts --image=./logo.png --name=TaxToken --short-name=TAX --desc="Tax token" --label=AI --tax-token --tax-fee-rate=5 --tax-burn-rate=20 --tax-divide-rate=30 --tax-liquidity-rate=40 --tax-recipient-rate=10 --tax-recipient-address=0x... --tax-min-sharing=100000
```

Chain and Labels: see [SKILL.md](../SKILL.md) or [api-create-token.md](api-create-token.md).
