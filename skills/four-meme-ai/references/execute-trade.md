# Execute Buy / Sell (Four.meme BSC)

Executes buy/sell (sends on-chain transactions). Requires `PRIVATE_KEY`. Only **TokenManager2 (V2)** tokens are supported.

## Buy

- **By amount**: `buyToken(token, amount, maxFunds)`  
  CLI: `fourmeme buy <token> amount <amountWei> <maxFundsWei>`  
  Meaning: Spend at most `maxFundsWei` of quote (BNB or BEP20) to buy `amountWei` tokens.

- **By funds**: `buyTokenAMAP(token, funds, minAmount)`  
  CLI: `fourmeme buy <token> funds <fundsWei> <minAmountWei>`  
  Meaning: Spend `fundsWei` of quote and receive at least `minAmountWei` tokens.

If quote is BEP20 (not BNB), the script will `approve` TokenManager2 first, then send the buy transaction.

## Sell

- Contract requirement: First `approve(tokenManager, amount)` on TokenManager2, then call `sellToken(token, amount)` or `sellToken(origin, token, amount, minFunds)` for slippage protection.
- The CLI runs approve then sell automatically; no need to do both manually.

```bash
fourmeme sell <tokenAddress> <amountWei> [minFundsWei]
```

- `minFundsWei` is optional: minimum quote to receive (slippage protection).

## Relation to quote commands

- `quote-buy` / `quote-sell`: Read-only estimates; no transaction is sent.
- `buy` / `sell`: Actually send transactions. Recommended: use `quote-buy` / `quote-sell` first to get estimates, then choose `maxFundsWei`, `minAmountWei`, `minFundsWei` and call `buy` / `sell`.
