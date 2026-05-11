# Wallet History

Understanding wallet history transaction categories, classifications, and interpretation.

## Transaction Categories

Wallet history categorizes transactions into these main types:

### Native Transfers
- **Received**: Incoming native token transfers (ETH, MATIC, BNB, etc.)
- **Sent**: Outgoing native token transfers
- **Self**: Transactions sent to self (e.g., contract deployment)

### Token Transfers
- **ERC20**: Token transfers and approvals
- **ERC721**: NFT transfers
- **ERC1155**: Multi-token transfers

### Contract Interactions
- **Contract Interaction**: Transactions that interact with smart contracts
- Classified by protocol type (DEX, NFT marketplace, DeFi, etc.)

### Internal Transactions
- **Internal**: Internal value transfers within contract execution

### Classification Types

Each transaction may include:
- **Category**: Broad classification (e.g., "token-transfer", "contract-interaction")
- **Method**: Specific function called (e.g., "transfer", "swap")
- **Protocol**: Protocol name if applicable (e.g., "uniswap", "aave")
- **Direction**: "in" for incoming, "out" for outgoing

## Related Endpoints

- [getWalletHistory](rules/getWalletHistory.md) - Get complete decoded transaction history
- [getWalletTransactions](rules/getWalletTransactions.md) - Get native transactions
- [getWalletTransactionsVerbose](rules/getWalletTransactionsVerbose.md) - Get decoded transactions
- [getWalletTokenTransfers](rules/getWalletTokenTransfers.md) - Get ERC20 token transfers
- [getWalletNFTTransfers](rules/getWalletNFTTransfers.md) - Get NFT transfers

## Performance Characteristics

- Most requests return quickly, but response time depends on wallet activity volume and chain
- Wallets with extensive transaction history (whale wallets, power users) take longer to process
- Use pagination with smaller `limit` values (25–50) for large wallets
- Set client timeout to **30s** to handle edge cases

See [PerformanceAndLatency.md](PerformanceAndLatency.md) for full optimization guidance.

## Documentation

For complete wallet history documentation and examples, see:
[https://docs.moralis.com/web3-data-api/evm/wallet-history](https://docs.moralis.com/web3-data-api/evm/wallet-history)
