# Token Holders API FAQ

Frequently asked questions and important notes about the Token Holders API.

## Key Considerations

### Data Freshness
- Holder data is continuously updated
- May have a slight delay from blockchain state
- Large-cap tokens update more frequently

### Sampling for Large Tokens
- For tokens with many holders (>100,000), data may be sampled
- Provides representative subset rather than complete list
- Ensures API response performance

### Historical Holders
- Current holders: Addresses currently holding the token
- Historical holders: Includes addresses that previously held but no longer do

## Common Questions

**Q: How often is holder data updated?**
A: Continuously, with higher frequency for popular tokens.

**Q: Why do some tokens return fewer holders than expected?**
A: May be due to sampling for very large token sets, or recent transfers not yet indexed.

**Q: Can I get historical holder data?**
A: Yes, use the historical holders endpoints for time-series data.

**Q: What's the difference between holders and owners?**
A: Generally interchangeable, but "holders" typically refers to token balances while "owners" may include NFT ownership.

## Related Endpoints

- [getTokenHolders](rules/getTokenHolders__evm.md) - Get holders summary by token address
- [getHistoricalTokenHolders](rules/getHistoricalTokenHolders__evm.md) - Get time-series holders data
- [getTokenOwners](rules/getTokenOwners.md) - Get ERC20 token owners by contract
- [getTopHolders](rules/getTopHolders__solana.md) - Get top holders for a token (Solana)

## Documentation

For complete FAQ and details, see:
[https://docs.moralis.com/web3-data-api/evm/token-holders-api-faq](https://docs.moralis.com/web3-data-api/evm/token-holders-api-faq)
