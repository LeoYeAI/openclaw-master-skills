# Event listening (TokenManager2, V2 only)

Only **TokenManager2 (V2)** is supported. V1 is not supported. Contract address (BSC): `0x5c952063c7fc8610FFDB798152D69F0B9550762b`.

The agent can react to **token creation, buy/sell, and liquidity add** by listening to the events below (e.g. copy-trading).

## Event list

| Event           | Meaning           | Main args                                                                 |
|-----------------|-------------------|---------------------------------------------------------------------------|
| **TokenCreate** | New token created | `creator`, `token`, `requestId`, `name`, `symbol`, `totalSupply`, `launchTime`, `launchFee` |
| **TokenPurchase** | Buy             | `token`, `account`, `price`, `amount`, `cost`, `fee`, `offers`, `funds`   |
| **TokenSale**   | Sell              | `token`, `account`, `price`, `amount`, `cost`, `fee`, `offers`, `funds`   |
| **LiquidityAdded** | Liquidity added | `base`, `offers`, `quote`, `funds`                                        |

- **TokenCreate**: With `token` (new token address) and `requestId`, you can call Helper3 `getTokenInfo(token)` or execute buy/sell immediately.
- **TokenPurchase / TokenSale**: Use for copy-trading, stats, etc.; `token` is the token address, `account` is the buyer/seller.
- **LiquidityAdded**: `base` is the token address; the token has been added to the pool and can be traded on the DEX.

## How to listen (viem)

### Option 1: Poll historical blocks with `getLogs`

```typescript
import { createPublicClient, http, parseAbiItem } from 'viem';
import { bsc } from 'viem/chains';

const TOKEN_MANAGER2 = '0x5c952063c7fc8610FFDB798152D69F0B9550762b';

const client = createPublicClient({
  chain: bsc,
  transport: http(process.env.BSC_RPC_URL || 'https://bsc-dataseed.binance.org'),
});

const logs = await client.getLogs({
  address: TOKEN_MANAGER2,
  events: [
    parseAbiItem('event TokenCreate(address creator, address token, uint256 requestId, string name, string symbol, uint256 totalSupply, uint256 launchTime, uint256 launchFee)'),
    parseAbiItem('event TokenPurchase(address token, address account, uint256 price, uint256 amount, uint256 cost, uint256 fee, uint256 offers, uint256 funds)'),
    parseAbiItem('event TokenSale(address token, address account, uint256 price, uint256 amount, uint256 cost, uint256 fee, uint256 offers, uint256 funds)'),
    parseAbiItem('event LiquidityAdded(address base, uint256 offers, address quote, uint256 funds)'),
  ],
  fromBlock: fromBlockNumber,
  toBlock: toBlockNumber,
});
```

### Option 2: Real-time subscription with `watchContractEvent`

```typescript
import { createPublicClient, http, parseAbiItem } from 'viem';
import { bsc } from 'viem/chains';

const client = createPublicClient({ chain: bsc, transport: http(rpcUrl) });

const unwatch = client.watchContractEvent({
  address: TOKEN_MANAGER2,
  events: [
    parseAbiItem('event TokenCreate(address creator, address token, uint256 requestId, string name, string symbol, uint256 totalSupply, uint256 launchTime, uint256 launchFee)'),
    parseAbiItem('event TokenPurchase(address token, address account, uint256 price, uint256 amount, uint256 cost, uint256 fee, uint256 offers, uint256 funds)'),
    parseAbiItem('event TokenSale(address token, address account, uint256 price, uint256 amount, uint256 cost, uint256 fee, uint256 offers, uint256 funds)'),
    parseAbiItem('event LiquidityAdded(address base, uint256 offers, address quote, uint256 funds)'),
  ],
  onLogs: (logs) => {
    for (const log of logs) {
      console.log(log.eventName, log.args);
    }
  },
});
// To stop: unwatch()
```

## Script

Use `fourmeme events <fromBlock> [toBlock]` (script `get-recent-events.ts`) to fetch the four event types in a block range and output JSON. See the events section in [SKILL.md](../SKILL.md).
