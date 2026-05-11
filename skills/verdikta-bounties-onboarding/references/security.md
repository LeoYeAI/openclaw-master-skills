# Security notes (bot wallet)

## Hot-wallet reality
This bot wallet is a hot wallet. Assume compromise is possible.

Recommended practices:
- Keep balances low.
- Use a sweep rule (e.g., send excess to cold address daily / when above threshold).
- Store the keystore file with `chmod 600` and outside web roots.

## Key storage
This skill uses an **encrypted JSON keystore** (ethers-compatible).

- The encryption password should be provided via env var (e.g., `VERDIKTA_WALLET_PASSWORD`).
- Never hardcode private keys.
- Never print the decrypted private key.

## Approvals / swap risk
Swapping ETH→LINK requires signing a transaction with calldata provided by a DEX aggregator.

Mitigations:
- Only use known endpoints (0x API) and correct chainId.
- Set strict slippage.
- Limit swap size.
- Consider allowlisting token addresses.

