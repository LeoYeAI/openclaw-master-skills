# Token Search

Understanding token search functionality and how to find tokens by various criteria.

## Search Capabilities

The token search API allows you to find tokens using multiple search criteria:

### Search By
- **Contract Address**: Exact match for token contract
- **Pair Address**: DEX pair address
- **Token Name**: Partial or exact name match
- **Token Symbol**: Partial or exact symbol match

### Filtering Options

- **Chains**: Filter by specific blockchain(s)
- **Token Types**: Filter by token type (ERC20, etc.)
- **Categories**: Filter by token category
- **Market Cap**: Filter by market cap range
- **Volume**: Filter by trading volume

## Response Fields

Search results include:
- Token contract address
- Token name and symbol
- Decimals
- Logo/thumbnail URLs
- Chain information
- Market data (price, market cap, volume)
- Pair information (for DEX listings)

## Related Endpoints

- [searchTokens](rules/searchTokens.md) - Search for tokens by multiple criteria
- [getTokenMetadata](rules/getTokenMetadata__evm.md) - Get token metadata by contract
- [getTokenPairs](rules/getTokenPairs__evm.md) - Get token pairs by address

## Documentation

For complete token search documentation and examples, see:
[https://docs.moralis.com/web3-data-api/evm/token-search](https://docs.moralis.com/web3-data-api/evm/token-search)
