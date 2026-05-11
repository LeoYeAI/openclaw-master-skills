# Query Tax Token fee/tax info

Only for **TaxToken** (creatorType 5). The token contract address is the TaxToken contract; call view functions on that address.

## On-chain view functions (TaxToken.abi)

| Function / variable | Description | Unit / meaning |
|---------------------|-------------|----------------|
| **feeRate** | Trading fee rate | Basis points; 10000 = 100%, e.g. 500 = 5% |
| **rateFounder** | Founder allocation share | Percent; 100 = 100%, e.g. 10 = 10% |
| **rateHolder** | Holder dividend share | Same |
| **rateBurn** | Burn share | Same |
| **rateLiquidity** | Liquidity add share | Same; rateFounder + rateHolder + rateBurn + rateLiquidity = 100 |
| **minDispatch** | Cumulative fee threshold to trigger distribution | Token units |
| **minShare** | Min balance to participate in dividends | Token units (ether); below this, no dividend |
| **quote** | Quote token address | 0 = BNB/ETH |
| **founder** | Founder address | Receives founder allocation |

See also **claimableFee(account)**, **claimedFee(account)**, **userInfo(account)** for claimable/claimed fees and user info in the [official API/Contract docs](https://four-meme.gitbook.io/four.meme/brand/protocol-integration) (e.g. API-Contract-TaxToken).

## Script

```bash
npx fourmeme tax-info <tokenAddress>
```

Or run: `npx tsx .../get-tax-token-info.ts <tokenAddress>`. BSC only.

Example output (JSON): `feeRateBps`, `feeRatePercent`, `rateFounder`, `rateHolder`, `rateBurn`, `rateLiquidity`, `minDispatch`, `minShare`, `quote`, `founder`.

## How to identify a TaxToken

- **Off-chain**: Call four.meme API `GET /v1/private/token/get?address=<token>`; if response `data` contains `taxInfo`, it is a TaxToken.
- **On-chain**: In TokenManager2, `(template >> 10) & 0x3F === 5` means TaxToken. Or run `get-tax-token-info`; if it succeeds and e.g. `feeRateBps > 0`, treat as TaxToken.

## References

- [Protocol Integration](https://four-meme.gitbook.io/four.meme/brand/protocol-integration) – API documents (API-Contract-TaxToken, etc.) and ABIs (TaxToken.abi)
