# Four.meme Contract Addresses (BSC only)

This skill supports **BSC only** (chainId 56). Arbitrum and Base are not supported.

## TokenManager (V1)

Used for tokens created **before** September 5, 2024. Only trading (no create).

| Chain | Address |
|-------|---------|
| BSC   | `0xEC4549caDcE5DA21Df6E6422d448034B5233bFbC` |

## TokenManager2 (V2)

Used for tokens created **after** September 5, 2024. Create and trade.

| Chain | Address |
|-------|---------|
| BSC   | `0x5c952063c7fc8610FFDB798152D69F0B9550762b` |

## TokenManagerHelper3 (V3)

Use for **getTokenInfo**, **tryBuy**, **trySell**. Supports both V1 and V2 tokens.

| Chain | Address |
|-------|---------|
| BSC   | `0xF251F83e40a78868FcfA3FA4599Dad6494E46034` |

## AgentIdentifier (BSC)

Used to check if a wallet is an **Agent wallet** (holds an Agent NFT). See [agent-creator-and-wallets.md](agent-creator-and-wallets.md).

| Chain | Address |
|-------|---------|
| BSC   | `0x09B44A633de9F9EBF6FB9Bdd5b5629d3DD2cef13` |

- **Interface**: `isAgent(address wallet)`, `nftCount()`, `nftAt(uint256 index)`.

---

## Usage

1. Call **TokenManagerHelper3.getTokenInfo(token)** to get `version` and `tokenManager`.
2. If `version === 1` → use TokenManager V1 for buy/sell.
3. If `version === 2` → use TokenManager2 for buy/sell (and check X Mode / TaxToken / AntiSniperFeeMode if needed).
4. Token creation is only via **TokenManager2** on BSC after obtaining `createArg` and `signature` from the four.meme API.
5. **Agent Creator**: Token created by agent wallet — on-chain `(template & (1 << 85)) != 0`; off-chain API `data.aiCreator === true`. Agent wallets: call **AgentIdentifier.isAgent(wallet)** on BSC.
