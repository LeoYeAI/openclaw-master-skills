# Spam Detection

Understanding how Moralis detects and handles spam tokens and NFTs.

## How Spam Detection Works

Moralis uses multiple heuristics to identify potential spam:

### Token Spam Indicators
- Suspicious token names/symbols (mimicking legitimate projects)
- Low or no liquidity
- High supply held by few addresses
- Recent contract deployment
- No verified contract code
- Suspicious transaction patterns

### NFT Spam Indicators
- Bulk transfers to many wallets
- Hidden/delayed reveal
- Low or zero floor prices
- Suspicious metadata
- Known spam collections

## Spam Criteria

### Likely Spam
- Tokens with multiple red flags
- Unsolicited NFT airdrops
- Collections with no trading activity

### Possible Spam
- Tokens with some risk indicators
- Low-volume collections
- Recently deployed contracts

## Using Spam Detection

### Filter Results
Many endpoints support spam filtering:
- `excludeSpam=true` parameter filters out known spam
- Default behavior varies by endpoint

### Token and NFT Balances
- Wallet endpoints may flag spam tokens/NFTs
- Check token/contract metadata for spam indicators

## Related Endpoints

- [getWalletTokenBalancesPrice](rules/getWalletTokenBalancesPrice.md) - Get ERC20 balances with prices (supports spam filtering)
- [getWalletNFTs](rules/getWalletNFTs.md) - Get NFTs by wallet (supports spam filtering)
- [getTokenMetadata](rules/getTokenMetadata__evm.md) - Get token metadata (includes spam flags)
- [getNFTMetadata](rules/getNFTMetadata__evm.md) - Get NFT metadata (includes spam flags)
- [getTokenScore](rules/getTokenScore.md) - Get token security score (includes spam analysis)

## Documentation

For complete spam detection documentation, see:
[https://docs.moralis.com/web3-data-api/evm/spam-detection](https://docs.moralis.com/web3-data-api/evm/spam-detection)
