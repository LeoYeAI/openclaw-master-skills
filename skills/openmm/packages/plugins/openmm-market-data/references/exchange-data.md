# Exchange Data Reference

Exchange-specific notes for market data queries and portfolio tracking.

## MEXC

- **Minimum order:** 1 USDT
- **Credentials:** `MEXC_API_KEY`, `MEXC_SECRET`
- **Supported Cardano tokens:** SNEK/USDT, INDY/USDT, NIGHT/USDT
- **Symbol format:** `BASE/QUOTE` (e.g., `BTC/USDT`, `ETH/USDT`)
- **Notes:** Most Cardano native tokens are listed here. Good source for CEX price comparison against DEX.

## Gate.io

- **Minimum order:** 1 USDT
- **Credentials:** `GATEIO_API_KEY`, `GATEIO_SECRET`
- **Symbol format:** `BASE/QUOTE` (e.g., `BTC/USDT`, `ETH/USDT`)
- **Notes:** Wide range of altcoin listings. Standard USDT pairs.

## Kraken

- **Minimum order:** 5 EUR/USD
- **Credentials:** `KRAKEN_API_KEY`, `KRAKEN_SECRET`
- **Supported fiat pairs:** EUR, USD, GBP
- **Notable pairs:** ADA/EUR, BTC/USD, ETH/EUR
- **Symbol format:** `BASE/QUOTE` (e.g., `ADA/EUR`, `BTC/USD`)
- **Notes:** Supports major fiat currency pairs. Higher minimum order value compared to other exchanges. Useful for fiat on/off ramp pricing and ADA/EUR quotes.

## Bitget

- **Minimum order:** 1 USDT
- **Credentials:** `BITGET_API_KEY`, `BITGET_SECRET`, `BITGET_PASSPHRASE`
- **Price precision:** 6 decimal places for SNEK/USDT and NIGHT/USDT pairs
- **Symbol format:** `BASE/QUOTE` (e.g., `SNEK/USDT`, `BTC/USDT`)
- **Notes:** Requires a passphrase in addition to API key and secret (set when creating the API key on Bitget). The 6 decimal price precision for SNEK and NIGHT is important for accurate orderbook and ticker data interpretation.

## Common Notes

- All exchanges use `BASE/QUOTE` symbol format (e.g., `BTC/USDT`, `ADA/EUR`)
- The CLI automatically converts to exchange-specific internal formats
- Query each exchange separately — there is no cross-exchange aggregate command
- Use `--json` flag for structured output on all commands
- Credentials are set via environment variables and stored locally
