# Funding the bot wallet (Base)

## What the human needs to do
1) Acquire **ETH on Base** (onramp)
2) Send ETH on Base to the bot's public address

## Recommended onramp (simple)
- Coinbase: buy/hold ETH, then send on **Base** network to the bot address.

(Exact UI varies by region; the skill scripts print the address and a checklist.)

## LINK requirement (first release)
- Each submission requires LINK for judgement fees.
- **Mainnet:** Bot can swap a user-chosen portion of its ETH on Base into LINK on Base.
- **Testnet (devs):** Devs can fund LINK directly to the bot address (simpler; no swap required).

## Typical fee sizing
(Replace with current real numbers as they stabilize.)
- Estimate endpoint: `GET /api/jobs/:jobId/estimate-fee`
- Rule of thumb (initial): ~0.04 LINK per submission

## Sweep policy
If bot ETH balance exceeds a threshold (default suggestion: $100), sweep excess ETH to an off-bot address.

