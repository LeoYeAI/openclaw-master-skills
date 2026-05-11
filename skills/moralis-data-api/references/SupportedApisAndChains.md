# Supported APIs and Chains

Complete list of supported Web3 Data APIs and blockchain networks with feature availability per chain.

## API Categories

| API Category              | Field Name       | Description                                  |
| ------------------------- | ---------------- | -------------------------------------------- |
| **Wallet API**            | `walletApi`      | Balances, transactions, history, approvals   |
| **NFT API**               | `nftApi`         | Metadata, transfers, collections             |
| **Token API**             | `tokenApi`       | Prices, metadata, pairs, holders             |
| **DeFi API**              | `defiApi`        | Protocol positions, liquidity                |
| **Entity API**            | `entityApi`      | Labeled addresses (exchanges, funds, whales) |
| **Blockchain API**        | `blockchainApi`  | Blocks, transactions                         |
| **Profitability API**     | `pnlApi`         | Wallet profit/loss analysis                  |
| **Token Prices**          | `tokenPrices`    | ERC20 token price data                       |
| **Internal Transactions** | `internalTxs`    | Internal ETH transfers                       |
| **NFT Trades**            | `nftTrades`      | NFT trade history                            |
| **NFT Prices**            | `nftPrices`      | NFT sale prices                              |
| **NFT Floor Prices**      | `nftFloorPrices` | NFT floor price data                         |

## Support by Chain

Legend: ✅ Supported | ❌ Not Supported | 🔄 Coming Soon

### Major EVM Chains

| Chain                  | Wallet | NFT | Token | DeFi | Entity | Blockchain | PnL | Prices | Internal Tx | NFT Trades | NFT Prices | Floor Prices |
| ---------------------- | ------ | --- | ----- | ---- | ------ | ---------- | --- | ------ | ----------- | ---------- | ---------- | ------------ |
| **Ethereum** (0x1)     | ✅     | ✅  | ✅    | ✅   | ✅     | ✅         | ✅  | ✅     | ✅          | ✅         | ✅         | ✅           |
| **Sepolia** (0xaa36a7) | ✅     | ✅  | ✅    | ❌   | ✅     | ✅         | ❌  | ❌     | ✅          | ❌         | ❌         | ❌           |
| **Holesky** (0x4268)   | ✅     | ✅  | ✅    | ❌   | ✅     | ✅         | ❌  | ❌     | ✅          | ❌         | ❌         | ❌           |
| **Polygon** (0x89)     | ✅     | ✅  | ✅    | ✅   | ✅     | ✅         | ✅  | ✅     | ✅          | ✅         | ✅         | ❌           |
| **Amoy** (0x13882)     | ✅     | ✅  | ✅    | ❌   | ✅     | ✅         | ❌  | ❌     | ✅          | ❌         | ❌         | ❌           |
| **BSC** (0x38)         | ✅     | ✅  | ✅    | ✅   | ✅     | ✅         | ❌  | ✅     | ✅          | ✅         | ✅         | ❌           |
| **BSC Testnet** (0x61) | ✅     | ✅  | ✅    | ❌   | ✅     | ✅         | ❌  | ❌     | ✅          | ❌         | ❌         | ❌           |

### L2 Chains

| Chain                           | Wallet | NFT | Token | DeFi | Entity | Blockchain | PnL | Prices | Internal Tx | NFT Trades | NFT Prices | Floor Prices |
| ------------------------------- | ------ | --- | ----- | ---- | ------ | ---------- | --- | ------ | ----------- | ---------- | ---------- | ------------ |
| **Arbitrum** (0xa4b1)           | ✅     | ✅  | ✅    | ✅   | ✅     | ✅         | ❌  | ✅     | ✅          | ✅         | ✅         | ❌           |
| **Arbitrum Sepolia** (0x66eee)  | ❌     | ❌  | ❌    | ❌   | ❌     | ❌         | ❌  | ❌     | ❌          | ❌         | ❌         | ❌           |
| **Base** (0x2105)               | ✅     | ✅  | ✅    | ✅   | ✅     | ✅         | ✅  | ✅     | ✅          | ✅         | ✅         | ✅           |
| **Base Sepolia** (0x14a34)      | ✅     | ✅  | ✅    | ❌   | ✅     | ✅         | ❌  | ❌     | ✅          | ❌         | ❌         | ❌           |
| **Optimism** (0xa)              | ✅     | ✅  | ✅    | ✅   | ✅     | ✅         | ❌  | ✅     | ✅          | ✅         | ✅         | ❌           |
| **Optimism Sepolia** (0xaa37dc) | ❌     | ❌  | ❌    | ❌   | ❌     | ❌         | ❌  | ❌     | ❌          | ❌         | ❌         | ❌           |

### Alternative Chains

| Chain                      | Wallet | NFT | Token | DeFi | Entity | Blockchain | PnL | Prices | Internal Tx | NFT Trades | NFT Prices | Floor Prices |
| -------------------------- | ------ | --- | ----- | ---- | ------ | ---------- | --- | ------ | ----------- | ---------- | ---------- | ------------ |
| **Avalanche** (0xa86a)     | ✅     | ✅  | ✅    | ✅   | ✅     | ✅         | ❌  | ✅     | ✅          | ✅         | ✅         | ❌           |
| **Fantom** (0xfa)          | ✅     | ✅  | ✅    | ❌   | ✅     | ✅         | ❌  | ❌     | ✅          | ❌         | ❌         | ❌           |
| **Fantom Testnet** (0xfa2) | ❌     | ❌  | ❌    | ❌   | ❌     | ❌         | ❌  | ❌     | ❌          | ❌         | ❌         | ❌           |
| **Cronos** (0x19)          | ✅     | ✅  | ✅    | ❌   | ✅     | ✅         | ❌  | ❌     | ❌          | ❌         | ❌         | ❌           |
| **Gnosis** (0x64)          | ✅     | ❌  | ✅    | ❌   | ✅     | ✅         | ❌  | ✅     | ❌          | ❌         | ❌         | ❌           |
| **Gnosis Chiado** (0x27d8) | ✅     | ❌  | ✅    | ❌   | ✅     | ✅         | ❌  | ❌     | ❌          | ❌         | ❌         | ❌           |
| **Linea** (0xe708)         | ✅     | ✅  | ✅    | ✅   | ✅     | ✅         | ❌  | ✅     | ✅          | ❌         | ❌         | ❌           |
| **Linea Sepolia** (0xe705) | ✅     | ✅  | ✅    | ❌   | ✅     | ✅         | ❌  | ❌     | ✅          | ❌         | ❌         | ❌           |

### Additional Chains

| Chain                        | Wallet | NFT | Token | DeFi | Entity | Blockchain | PnL | Prices | Internal Tx | NFT Trades | NFT Prices | Floor Prices |
| ---------------------------- | ------ | --- | ----- | ---- | ------ | ---------- | --- | ------ | ----------- | ---------- | ---------- | ------------ |
| **Chiliz** (0x15b38)         | ✅     | ✅  | ✅    | ❌   | ✅     | ✅         | ❌  | ❌     | ✅          | ❌         | ❌         | ❌           |
| **Chiliz Testnet** (0x15b32) | ✅     | ✅  | ✅    | ❌   | ✅     | ✅         | ❌  | ❌     | ✅          | ❌         | ❌         | ❌           |
| **Moonbeam** (0x504)         | ✅     | ✅  | ✅    | ❌   | ✅     | ✅         | ❌  | ✅     | ❌          | ❌         | ❌         | ❌           |
| **Moonriver** (0x505)        | ✅     | ✅  | ✅    | ❌   | ✅     | ✅         | ❌  | ❌     | ❌          | ❌         | ❌         | ❌           |
| **Moonbase** (0x507)         | ✅     | ✅  | ✅    | ❌   | ✅     | ✅         | ❌  | ❌     | ❌          | ❌         | ❌         | ❌           |
| **Flow** (0x2eb)             | ✅     | ✅  | ✅    | ❌   | ✅     | ✅         | ❌  | ❌     | ❌          | ❌         | ❌         | ❌           |
| **Flow Testnet** (0x221)     | ✅     | ✅  | ✅    | ❌   | ✅     | ✅         | ❌  | ❌     | ❌          | ❌         | ❌         | ❌           |
| **Ronin** (0x7e4)            | ✅     | ✅  | ✅    | ❌   | ✅     | ✅         | ❌  | ✅     | ✅          | ❌         | ❌         | ❌           |
| **Ronin Saigon** (0x7e5)     | ✅     | ✅  | ✅    | ❌   | ✅     | ✅         | ❌  | ❌     | ✅          | ❌         | ❌         | ❌           |
| **Lisk** (0x46f)             | ✅     | ✅  | ✅    | ❌   | ✅     | ✅         | ❌  | ❌     | ✅          | ❌         | ❌         | ❌           |
| **Lisk Sepolia** (0x106a)    | ✅     | ✅  | ✅    | ❌   | ✅     | ✅         | ❌  | ❌     | ✅          | ❌         | ❌         | ❌           |
| **Pulse** (0x171)            | ✅     | ❌  | ✅    | ❌   | ✅     | ✅         | ❌  | ✅     | ✅          | ❌         | ❌         | ❌           |
| **Sei** (0x531)              | ✅     | ✅  | ✅    | ✅   | ✅     | ✅         | ❌  | ✅     | ✅          | ✅         | ✅         | ✅           |
| **Sei Testnet** (0x530)      | ✅     | ✅  | ✅    | ✅   | ✅     | ✅         | ❌  | ❌     | ✅          | ❌         | ❌         | ❌           |
| **Monad** (0x8f)             | ✅     | ✅  | ✅    | ✅   | ✅     | ✅         | ❌  | ✅     | ✅          | ✅         | ✅         | ❌           |

### Coming Soon / Unsupported

| Chain                             | Status         |
| --------------------------------- | -------------- |
| **Blast** (0x13e31)               | 🔄 Coming Soon |
| **Blast Sepolia** (0xa0c71fd)     | 🔄 Coming Soon |
| **zkSync** (0x144)                | 🔄 Coming Soon |
| **zkSync Sepolia** (0x12c)        | 🔄 Coming Soon |
| **Mantle** (0x1388)               | 🔄 Coming Soon |
| **Mantle Sepolia** (0x138b)       | 🔄 Coming Soon |
| **opBNB** (0xcc)                  | 🔄 Coming Soon |
| **Polygon zkEVM** (0x44d)         | 🔄 Coming Soon |
| **Polygon zkEVM Cardona** (0x98a) | 🔄 Coming Soon |
| **Zetachain** (0x1b58)            | 🔄 Coming Soon |
| **Zetachain Testnet** (0x1b59)    | 🔄 Coming Soon |
| **HyperEVM** (0x3e7)              | ❌ Unsupported |

### Solana

Solana uses a separate base URL (`https://solana-gateway.moralis.io`) and dedicated endpoints with the `__solana` suffix.

| Network | Wallet | NFT | Token | Token Price | SPL |
| ------- | ------ | --- | ----- | ----------- | --- |
| **Mainnet** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Devnet** | ✅ | ✅ | ✅ | ❌ | ✅ |

**Supported Solana APIs:**
- **Wallet**: Native balance (`balance__solana`), portfolio (`getPortfolio__solana`)
- **Token**: Metadata (`getTokenMetadata__solana`), prices (`getTokenPrice__solana`, `getMultipleTokenPrices__solana`)
- **NFT**: Metadata (`getNFTMetadata__solana`), owned NFTs (`getNFTs__solana`)
- **SPL**: SPL token balances (`getSPL__solana`)
- **Analytics**: Token scores, trending tokens, volume stats, candlesticks, pair stats

**Limitations:**
- No DeFi position tracking on Solana
- No profitability/PnL analysis
- No floor price data
- Price data only available on Mainnet

## Key Insights

### Full API Coverage

Only **Ethereum (0x1)** and **Base (0x2105)** have complete coverage of all APIs including floor prices.

### Strong Coverage (Most APIs)

- **Polygon** - Missing only floor prices
- **BSC** - Missing only profitability and floor prices
- **Arbitrum** - Missing profitability and floor prices
- **Avalanche** - Missing profitability and floor prices
- **Sei** - Missing profitability (new chain)

### Common Limitations

- **Profitability API**: Only supported on Ethereum, Polygon, Base
- **Internal Transactions**: Not available on most sidechains (Gnosis, Moonbeam family, Flow)
- **NFT Floor Prices**: Only Ethereum, Base, and Sei support this
- **DeFi API**: Testnets generally don't support DeFi protocol data

### Chain Query Params

When using the API, you can specify chains using:

- Hex format: `0x1`, `0x89`, `0x38`
- String format: `eth`, `polygon`, `bsc`

## Documentation

For complete and up-to-date support matrix:

- [Supported Web3 Data APIs](https://docs.moralis.com/supported-web3data-apis) - Interactive support table
- [Supported Chains for Web3 API](https://docs.moralis.com/supported-chains?service=web3api) - Chain-specific details
