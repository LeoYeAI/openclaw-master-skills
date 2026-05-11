# x402 Payment Flow

runtime-sentinel uses x402 + USDC on Base for premium feature access.
This document covers the full flow, wallet setup, and troubleshooting.

---

## How x402 works

x402 is Coinbase's open payment protocol built on the HTTP 402 status code.
Payment IS authentication — no account, no API key, no subscription required.

```
sentinel daemon start
  → POST https://api.runtime-sentinel.dev/v1/daemon/start
  ← 402 Payment Required
      X-Payment-Request: price=$0.01, network=base, token=USDC,
                         recipient=0x0E0EE00281A8729d4B68CDed99d430324350a305, duration=86400s
  → User sees price and confirms (or auto-confirms if below threshold)
  → sentinel signs USDC transfer from ~/.sentinel/wallet
  → POST (retry) with X-Payment header (signed authorization)
  → Base facilitator verifies on-chain
  ← 200 OK — daemon session token granted for 24h
```

Your USDC stays in your wallet until the moment it is spent. The price is
visible in the `X-Payment-Request` header before your wallet signs anything.

---

## Premium pricing

| Feature | Price | Unit |
|---|---|---|
| Daemon mode | $0.01 | per 24h |
| Egress monitoring | $0.005 | per 24h |
| Process anomaly detection | $0.005 | per 24h |
| Full premium bundle | $0.015 | per 24h |
| On-demand deep scan | $0.02 | per scan |

Free tier (integrity checks, basic injection scan, credential audit) has no
payment requirement and no rate limit.

---

## Wallet setup

`sentinel` manages a local Base wallet stored at `~/.sentinel/wallet`.

```bash
# Generate new wallet (on first run)
sentinel setup

# Show current address and USDC balance
sentinel wallet show

# Print QR + address to fund with USDC
sentinel wallet fund

# Set a per-day spend limit (auto-approves payments below this)
sentinel wallet set-limit 0.05

# Export BIP-39 mnemonic for backup
sentinel wallet export

# Restore wallet on a new machine
sentinel wallet recover
```

**Recommended starting balance**: $1 USDC — covers roughly 66 days of full
premium bundle at the standard rate.

**Security**: The wallet private key is stored encrypted at
`~/.sentinel/wallet/keystore.json`. The passphrase is derived from the
machine's hardware ID by default, or can be set manually with
`sentinel wallet set-passphrase`.

---

## Auto-approval threshold

To avoid per-payment prompts in daemon mode:

```bash
sentinel wallet set-limit <amount>   # e.g. 0.05 for $0.05/day max
```

Payments above this threshold always prompt for explicit confirmation.
Set to `0` to require confirmation for every payment.

---

## Troubleshooting

**"Insufficient USDC balance"**  
Run `sentinel wallet fund` and send USDC to the displayed address on Base.
USDC on Base (not Ethereum mainnet) is required.

**"Facilitator unreachable"**  
The Base facilitator at `https://x402.org/facilitator` may be temporarily
unavailable. Sentinel will retry with exponential backoff. Free tier
continues to work while premium features are paused.

**"Payment rejected"**  
The signed authorization may have expired (x402 authorizations are
time-limited). Sentinel retries automatically. If this persists, run
`sentinel wallet diagnose`.

**Running offline / air-gapped**  
Use `--offline` flag. Only free tier features are available. Hash databases
and injection patterns are cached locally at `~/.sentinel/cache/`.
